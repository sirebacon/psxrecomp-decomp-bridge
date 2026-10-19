"""Rebalance comparison workflow (fixed loadouts, matched seeds, assumption sensitivity).

python -m pe_weapon_sim.compare_rules --proposal exp:E1 [--stages D5 Disc2] [--seeds 8]
        [--fights 4] [--assumptions default,late,untimed_long,untimed_hit_low] [--out STEM]

- Builds: the frozen earned campaign builds (8 policy groups x seeds, D5 / Disc2 checkpoints;
  the controlled_* groups are the weapon-class comparison), with Aya's source stats and armor.
- Encounters ('campaign'): each fight replays one logged won battle of the stage, drawn
  uniformly, so enemy groups enter with their campaign frequency; boss battles use the boss
  distance profile. Optional synthetic boss encounters are labelled separately.
- Rules: baseline (rules.CURRENT) vs a proposal: 'exp:E1+E2' (rules.experimental) or
  'module:function' returning (rules, cfg_transform). Every fight is paired: same build,
  encounter, seed and assumption set under both rules.
- Assumption sets vary what the source does not resolve (see ASSUMPTIONS). Results report
  the paired difference per set and whether build rankings change between sets.
- Coverage labels travel with the results: fallback-damage hits, untimed strikes, unresolved
  status types.
Outputs findings/data/<STEM>.json and findings/<STEM>.md; historical outputs are not touched.
"""
import argparse, re, importlib, json, random, statistics, sys, zlib
from pathlib import Path

from . import engine as E, rules as R
from .decomp_animation import source_behavior_rules
from .run_benchmark import PROF
from . import encounters as N

ROOT = Path(__file__).resolve().parents[2]

BASE_OPTIONS = dict(static_enemy_catalog=True, enemy_action_timing='fast', melee_reach=True, effect_actions=True,
                    player_status=True, hp=385, reserve_ammo={0: 999, 1: 999, 2: 999},
                    enemy_defaults=dict(charge_step=90, windup=10, recovery=10, source_action_slot=0))

# Unresolved inputs and their alternatives (each set changes one thing from 'default').
ASSUMPTIONS = {
    'default': dict(contact='early', untimed=(10, 10), hit=0.75, ambiguous='first'),
    'late': dict(contact='late', untimed=(10, 10), hit=0.75, ambiguous='first'),
    'untimed_long': dict(contact='early', untimed=(60, 120), hit=0.75, ambiguous='first'),
    'untimed_hit_low': dict(contact='early', untimed=(10, 10), hit=0.4, ambiguous='first'),
    'ambiguous_uniform': dict(contact='early', untimed=(10, 10), hit=0.75, ambiguous='uniform'),
    'human_reaction': dict(contact='early', untimed=(10, 10), hit=0.75, ambiguous='first', reaction=75),
    'far_player': dict(contact='early', untimed=(10, 10), hit=0.75, ambiguous='first', distance_scale=1.4),
    'geometry_upper': dict(contact='early', untimed=(10, 10), hit=0.75, ambiguous='first', throw_lateral='aimed'),
    # Play-log player: menu reaction 75 updates + 55% of strikes avoided by movement. Fitted to the log's
    # ordinary battles with --atb-guard --logged-charge (pe-calibration-atbguard-2026-10-19.md); behaviour, not source.
    'logged_player': dict(contact='early', untimed=(10, 10), hit=0.75, ambiguous='first', reaction=75, evade=0.55),
    # With --serial (source: game flag 0x100 freezes enemy charge/scripts and Aya's gauge during her action):
    # a 30-update menu reaction in the paused menu, no evasion fit. Matches the log's ordinary damage (1.15x)
    # and time per turn (pe-calibration-serial-2026-10-19.md).
    'logged_player_serial': dict(contact='early', untimed=(10, 10), hit=0.75, ambiguous='first', reaction=30, reaction_paused=True),
}

METRICS = ('won', 'time', 'damage_taken', 'rounds', 'reloads', 'switches', 'death', 'status_total',
           'fallback_hits', 'untimed_strikes', 'strikes', 'hits_taken')


ATB_GUARD = [False]          # set by --atb-guard (module-level so run_fight / secondary_test share it)
LOGGED_CHARGE = [False]      # set by --logged-charge
SERIAL = [False]             # set by --serial
IDENTITY_RANK = [False]      # set by --identity-rank
CALIBRATED = [False]         # set by --calibrated: the play-log-calibrated model (see options_for / campaign_battles)


def options_for(a, shared_cells):
    o = json.loads(json.dumps(BASE_OPTIONS))
    o['reserve_ammo'] = {0: 999, 1: 999, 2: 999}
    o.update(shared_cells=shared_cells, contact_timing=a['contact'], melee_window=a['contact'],
             enemy_choice=dict(contact=a['contact'], ambiguous=a['ambiguous'], untimed=a['untimed'], throw_lateral=a.get('throw_lateral', 0)),
             called_slots=dict(contact=a['contact'], untimed=a['untimed'], throw_lateral=a.get('throw_lateral', 0)))
    o['enemy_defaults'].update(hit_probability=a['hit'], windup=a['untimed'][0], recovery=a['untimed'][1])
    from .enemy_identity import MULTI_KIND
    if MULTI_KIND in (shared_cells or {}): o['called_slots']['silent'] = True   # --multi-kind: identity fixes incl. silent actors
    if ATB_GUARD[0]: o['atb_guard'] = True
    if LOGGED_CHARGE[0]: o['logged_charge'] = True
    if a.get('reaction'): o['reaction_updates'] = a['reaction']           # calibrated from the play log (8.2 vs 5.7 s/turn)
    if a.get('evade'): o['player_evade'] = a['evade']
    if a.get('reaction_paused'): o['reaction_paused'] = True
    if IDENTITY_RANK[0]: o['identity_rank'] = True             # source: counter rank from the enemy identity
    if SERIAL[0]: o['serial_action'] = True                    # behaviour, fitted to the play log
    if CALIBRATED[0]:
        # pe-calibration-logged-v7-2026-10-19: body contact (per-room log rate), actor by HP, borrowed plans.
        o['contact_damage'] = dict(ord=0.82, boss=0.89, logged=True)
        o['called_slots'] = dict(o['called_slots'], actor_by_hp=True, borrow=True, silent=True)
    return o


def campaign_battles(phase):
    """Logged won battles of a phase as fight foes (the evaluation pool filters applied). With --calibrated,
    calibrate_logged's battles: scripted boss HP (controllers, phase 2, parts kept as controllers, unengaged
    parts dropped) and each battle's logged bag / known spells for Parasite Energy."""
    if CALIBRATED[0]:
        from .calibrate_logged import battles, foe_for
        out = []
        for b in battles():
            if b['phase'] != phase: continue
            foes = [x for x in (foe_for(f, True) for f in b['foes'] if not f.get('_unengaged')) if x]
            out.append(dict(map=b['map'], boss=b['boss'], foes=foes, logged=dict(secs=b['logged_secs'], taken=b['logged_taken']),
                            bag=dict(b['bag']), known_spells=list(b['known_spells'])))
        return out
    camp = json.loads((ROOT / 'findings/data/pe-campaign-2026-10-17.json').read_text(encoding='utf-8'))
    out = []
    for e in camp['events']:
        if e['type'] != 'battle' or e['outcome'] != 'win' or e['phase'] != phase: continue
        foes = []
        for x in e['enemies']:
            hp = x['hp'] - 1000000 if x['hp'] > 1000000 else x['hp']
            if hp <= 0 or x['defense'] >= 200 or x['id'] == '0x0200': continue
            foes.append(dict(name=x['id'], loc=e['map'], hp=hp, level=max(1, round((x['defense'] - 3) / 1.6)),
                             defense=x['defense'], boss=x['boss'], heat=x['heat'], frost=x['frost'],
                             cyanide=x['cyanide'], acid=x['acid'], tranq=x['tranq']))
        if foes: out.append(dict(map=e['map'], boss=any(f['boss'] for f in foes), foes=foes,
                                 logged=dict(secs=e.get('secs'), taken=e.get('taken'))))
    return out


def cfg_transform(spec):
    """Weapon-table edits, e.g. '4.power+15,5.rof+1,@G3A3.power+45' (kind or @weapon name, spaces as _). This is
    what a mod would change in the weapon data; applied to the proposal side only."""
    edits = []
    for item in spec.split(','):
        m = re.fullmatch(r'(\d+|all|@\w+)\.(\w+)([+*])(-?[\d.]+)', item.strip())
        if not m: raise ValueError('bad cfg edit %r' % item)
        edits.append((m[1], m[2], m[3], float(m[4])))
    def tf(cfg):
        c = dict(cfg); c['eff'] = dict(cfg.get('eff', {}))
        for kind, field, op, v in edits:
            if kind.startswith('@'):
                if getattr(c.get('weapon'), 'name', '').replace(' ', '_') != kind[1:]: continue
            elif kind != 'all' and int(kind) != c['kind']: continue
            box = c if field in c else c['eff']
            old = box.get(field, 0)
            new = old + v if op == '+' else old * v
            box[field] = int(round(new)) if isinstance(old, int) else new
        return c
    return tf


def proposal_from(spec):
    """(rules dict, cfg transform) for a proposal spec; 'exp:A+B|cfg:4.power+15' combines both."""
    if spec in (None, '', 'baseline'): return R.CURRENT, None
    if '|' in spec or spec.startswith('cfg:'):
        rules, tf = R.CURRENT, None
        for part in spec.split('|'):
            if part.startswith('cfg:'): tf = cfg_transform(part[4:])
            else: rules, _ = proposal_from(part)
        return rules, tf
    if spec.startswith('exp:'):
        names = [x for x in spec[4:].split('+') if x]
        unsupported = {k for n in names for k in R.EXPERIMENTS[n]} - R.SOURCE_BACKEND_KEYS
        if unsupported: raise ValueError('experiment keys not honoured by the source backend: %s' % sorted(unsupported))
        return R.experimental(*names), None
    mod, fn = spec.split(':', 1)
    return getattr(importlib.import_module(mod), fn)()


def builds(stages, seeds, groups=None):
    from .audit_fallback_hits import cases
    seen = set()
    for bound, group, phase, enc, seed, cfg, aya, armor, _ in cases(('early',)):
        if phase not in stages or (groups and group not in groups): continue
        key = (group, phase, seed)
        if key in seen: continue
        seen.add(key)
        if len([k for k in seen if k[:2] == (group, phase)]) > seeds: continue
        yield dict(group=group, phase=phase, seed=seed, cfg=cfg, aya=aya, armor=armor)


def class_builds(stages, seeds):
    """Equal-investment class benchmark: each class's representative gun (run_benchmark.CLASS_GUNS:
    Day 5 guns for D5, Wayne guns for Disc2). D5: Day-5 attack investment, built-in effects only;
    Disc2: endgame investment [30, 10, 10] + 2 Commands + Quickdraw (the universal core). Aya (level,
    armor) is the same seed's frozen group-C build, so only the gun differs from the frozen runs."""
    from .run_benchmark import W, gun_cfg, CLASS_GUNS, STAGE_INVEST
    from .progression import Gun
    for ph in stages:
        guns = CLASS_GUNS['Day5' if ph == 'D5' else 'Wayne']
        ref = {b['seed']: b for b in builds([ph], seeds, ['C'])}
        for cls, wid in guns.items():
            g = Gun(W[wid])
            if ph == 'D5': g.invested[0] = STAGE_INVEST['Day5']; mods = []
            else: g.invested = [30, 10, 10]; mods = ['2Cmd', 'Quickdraw']
            cfg = gun_cfg(g, mods)
            for seed in range(1, seeds + 1):
                yield dict(group='class_' + cls, phase=ph, seed=seed, cfg=cfg, aya=ref[seed]['aya'], armor=ref[seed]['armor'], gun=W[wid].name)

def run_fight(rules_dict, cfg, b, battle, a_name, a, seed, cells):
    opts = options_for(a, cells)
    # Max HP from the source level table (live-read rows), not the HP-bugged save's 385.
    from .economy.source_stats import aya_stats
    opts['hp'] = aya_stats(b['aya']['level'])['max_hp']
    prof = PROF['boss'] if battle['boss'] else PROF['normal']
    if a.get('distance_scale'): prof = N.Scaled(prof, a['distance_scale'])
    foes = [dict(f) for f in battle['foes']]
    if CALIBRATED[0]:
        # Parasite Energy and items with the generic policy (heal below half, Haste on bosses), the battle's
        # logged bag and spells known by then; vanilla rules: vanilla heals, no half-bar powers / items.
        mode = 'vanilla' if rules_dict['name'] == 'vanilla' else 'current'
        opts['pe'] = dict(spells=battle.get('known_spells', []), rules=mode, heal_rules=mode, max_hp=opts['hp'], bag=dict(battle.get('bag', {})))
        opts['player_max_hp'] = opts['hp']
    st = E.fight(source_behavior_rules(rules_dict), cfg, b['aya'], foes, prof, random.Random(seed),
                 armor=b['armor'], source_options=opts, time_cap=400 if (CALIBRATED[0] and battle['boss']) else 90, policy='walk')
    if st['ammo_balance'] != 0: raise AssertionError('ammo conservation')
    strikes = sum(v for k, v in st.items() if k.startswith('strike_timing_'))
    return dict(won=st['won'], time=st['time'], damage_taken=st['damage_taken'], rounds=st['rounds'],
                reloads=st['reloads'], switches=st.get('switches', 0),
                death=int(not st['won'] and st['damage_taken'] >= opts['hp']),
                status_total=sum(v for k, v in st.items() if k.startswith('status_') and k != 'status_already'),
                fallback_hits=st.get('legacy_damage_hits', 0), untimed_strikes=st.get('strike_timing_untimed', 0),
                strikes=strikes, hits_taken=st.get('hits_taken', 0))


def bootstrap(diffs, n=2000, seed=1):
    if not diffs: return None
    rng = random.Random(seed); m = len(diffs)
    means = sorted(statistics.mean(rng.choice(diffs) for _ in range(m)) for _ in range(n))
    return [means[int(0.025 * n)], means[int(0.975 * n) - 1]]


def spearman(a, b):
    keys = [k for k in a if k in b]
    if len(keys) < 3: return None
    ra = {k: i for i, k in enumerate(sorted(keys, key=a.get))}; rb = {k: i for i, k in enumerate(sorted(keys, key=b.get))}
    n = len(keys)
    return 1 - 6 * sum((ra[k] - rb[k]) ** 2 for k in keys) / (n * (n * n - 1))


def main(argv=None):
    from .enemy_identity import FIRST_RUN_SHARED_CELLS as cells
    ap = argparse.ArgumentParser()
    ap.add_argument('--proposal', default='baseline'); ap.add_argument('--stages', nargs='+', default=['D5', 'Disc2'])
    ap.add_argument('--seeds', type=int, default=8); ap.add_argument('--fights', type=int, default=4)
    ap.add_argument('--groups', nargs='*'); ap.add_argument('--assumptions', default=','.join(ASSUMPTIONS))
    ap.add_argument('--out', default=None); ap.add_argument('--builds', default='frozen', choices=('frozen', 'class'))
    ap.add_argument('--multi-kind', action='store_true')     # opt-in identity fixes: several literal kinds (Disc2 bosses) + silent actors
    ap.add_argument('--atb-guard', action='store_true')      # source: incoming damage halved while the gauge is above 0
    ap.add_argument('--logged-charge', action='store_true')  # play-log charge step where scripts give none
    ap.add_argument('--identity-rank', action='store_true')  # source: Battle_RollEnemySpawn rank = identity low byte
    ap.add_argument('--serial', action='store_true')         # source: flag 0x100 freezes enemies / Aya's gauge during her action
    ap.add_argument('--calibrated', action='store_true')     # full calibrated model (implies --serial --atb-guard --logged-charge --multi-kind --identity-rank)
    ap.add_argument('--base', default='current', choices=('current', 'vanilla'))   # baseline ruleset
    ap.add_argument('--all-battles', action='store_true')    # every logged battle once per build (no battle sampling noise)
    ap.add_argument('--encounters', default='all', choices=('all', 'ordinary', 'boss'))   # boss: enough boss samples per group
    a = ap.parse_args(argv)
    base_rules = R.VANILLA if a.base == 'vanilla' else R.CURRENT
    if a.calibrated: a.serial = a.atb_guard = a.logged_charge = a.multi_kind = a.identity_rank = True
    CALIBRATED[0] = a.calibrated
    ATB_GUARD[0] = a.atb_guard; LOGGED_CHARGE[0] = a.logged_charge; SERIAL[0] = a.serial; IDENTITY_RANK[0] = a.identity_rank
    if a.multi_kind:
        from .enemy_identity import MULTI_KIND
        cells = {**cells, MULTI_KIND: 1}
    prop_rules, cfg_tf = proposal_from(a.proposal)
    sets = a.assumptions.split(',')
    battles = {p: [x for x in campaign_battles(p) if a.encounters == 'all' or x['boss'] == (a.encounters == 'boss')] for p in a.stages}
    rows = []
    for b in (class_builds(a.stages, a.seeds) if a.builds == 'class' else builds(a.stages, a.seeds, a.groups)):
        for i in range(len(battles[b['phase']]) if a.all_battles else a.fights):
            if a.all_battles: battle = battles[b['phase']][i]
            else:
                pick = random.Random(b['seed'] * 1009 + i * 7 + zlib.crc32(b['phase'].encode()) % 97)   # stable across processes
                battle = battles[b['phase']][pick.randrange(len(battles[b['phase']]))]
            fseed = b['seed'] * 7919 + i
            for s in sets:
                base = run_fight(base_rules, b['cfg'], b, battle, s, ASSUMPTIONS[s], fseed, cells)
                pcfg = cfg_tf(b['cfg']) if cfg_tf else b['cfg']
                prop = base if (prop_rules is base_rules and cfg_tf is None) else run_fight(prop_rules, pcfg, b, battle, s, ASSUMPTIONS[s], fseed, cells)
                rows.append(dict(group=b['group'], phase=b['phase'], seed=b['seed'], fight=i, map=battle['map'],
                                 boss=battle['boss'], assumption=s, base=base, prop=prop))
        print(b['group'], b['phase'], b['seed'], len(rows), file=sys.stderr, flush=True)
    summary = summarize(rows, sets, a.stages)
    stem = a.out or 'pe-compare-%s-2026-10-18' % a.proposal.replace(':', '_').replace('+', '_')
    out = dict(proposal=a.proposal, base=a.base, calibrated=a.calibrated, builds=a.builds, multi_kind=a.multi_kind, atb_guard=a.atb_guard, logged_charge=a.logged_charge, serial=a.serial, identity_rank=a.identity_rank, encounters=a.encounters, all_battles=a.all_battles, stages=a.stages, seeds=a.seeds, fights=a.fights, assumptions={s: ASSUMPTIONS[s] for s in sets},
               summary=summary, rows=rows)
    (ROOT / 'findings/data' / (stem + '.json')).write_text(json.dumps(out, indent=1, default=list), encoding='utf-8')
    (ROOT / 'findings' / (stem + '.md')).write_text(report(out), encoding='utf-8')
    print(json.dumps(summary['stability'], indent=1))


def resummarize(stem):
    """Rebuild summary and report from a saved run's rows (no re-simulation)."""
    path = ROOT / 'findings/data' / (stem + '.json'); out = json.loads(path.read_text(encoding='utf-8'))
    out['summary'] = summarize(out['rows'], list(out['assumptions']), out['stages'])
    path.write_text(json.dumps(out, indent=1, default=list), encoding='utf-8')
    (ROOT / 'findings' / (stem + '.md')).write_text(report(out), encoding='utf-8')


def summarize(rows, sets, stages):
    groups = sorted({r['group'] for r in rows})
    table = {}
    for s in sets:
        for ph in stages:
            for g in groups + ['ALL', 'ORDINARY', 'BOSS']:
                rr = [r for r in rows if r['assumption'] == s and r['phase'] == ph and (g == 'ALL' or r['group'] == g or
                      (g == 'ORDINARY' and not r['boss']) or (g == 'BOSS' and r['boss']))]
                if not rr: continue
                cell = dict(n=len(rr))
                for m in METRICS:
                    bm = [r['base'][m] for r in rr]; pm = [r['prop'][m] for r in rr]
                    cell[m] = dict(base=statistics.mean(bm), prop=statistics.mean(pm),
                                   delta=statistics.mean(p - q for p, q in zip(pm, bm)),
                                   ci=bootstrap([p - q for p, q in zip(pm, bm)]))
                table['%s|%s|%s' % (s, ph, g)] = cell
            for g in groups:                                    # per build group, ordinary and boss kept apart
                for enc in ('ord', 'boss'):
                    rr = [r for r in rows if r['assumption'] == s and r['phase'] == ph and r['group'] == g and r['boss'] == (enc == 'boss')]
                    if rr: table['%s|%s|%s/%s' % (s, ph, g, enc)] = {m: dict(base=statistics.mean(r['base'][m] for r in rr),
                                                                             prop=statistics.mean(r['prop'][m] for r in rr)) for m in METRICS} | dict(n=len(rr))
    # Ranking stability: groups ranked by (win rate, -time) under each assumption set.
    stability = {}
    for ph in stages:
        score = {s: {g: table['%s|%s|%s' % (s, ph, g)]['won']['prop'] * 100 - table['%s|%s|%s' % (s, ph, g)]['time']['prop'] / 100
                     for g in groups if '%s|%s|%s' % (s, ph, g) in table} for s in sets}
        ref = score.get('default') or score[sets[0]]
        stability[ph] = {s: dict(spearman_vs_default=spearman(ref, score[s]),
                                 order=sorted(score[s], key=lambda g: -score[s][g])) for s in sets}
        dsign = {s: table.get('%s|%s|ALL' % (s, ph), {}).get('won', {}).get('delta') for s in sets}
        stability[ph]['win_delta_by_set'] = dsign
    return dict(table=table, stability=stability)


def report(out):
    t = out['summary']['table']; st = out['summary']['stability']
    base_name = 'VANILLA' if out.get('base') == 'vanilla' else 'CURRENT'
    prop_name = 'CURRENT (mod)' if out['proposal'] in (None, '', 'baseline') else out['proposal'] + ' on CURRENT'
    L = ['# Rule comparison: %s → %s%s' % (base_name, prop_name, ' (calibrated model)' if out.get('calibrated') else ''), '',
         ('Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build)' if out.get('builds') == 'class' else 'Fixed frozen builds') + ', campaign-frequency encounters (logged won battles), matched seeds; ' + ('%d seeds x every logged battle%s.' % (out['seeds'], '' if out.get('encounters', 'all') == 'all' else ' (' + out['encounters'] + ' only)') if out.get('all_battles') else '%d seeds x %d fights per build and stage.' % (out['seeds'], out['fights'])),
         'Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).', '',
         ('Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.' if out.get('calibrated') else 'Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).'), '',
         '| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |',
         '|---|---|---|---|---|---|---|---|---|---|---|']
    for k, c in t.items():
        s, ph, g = k.split('|')
        if g not in ('ALL', 'ORDINARY', 'BOSS'): continue
        ci = c['won']['ci']
        fb = c['fallback_hits']['base'] / max(1e-9, c['hits_taken']['base'])
        un = c['untimed_strikes']['base'] / max(1e-9, c['strikes']['base'])
        L.append('| %s | %s | %s | %.3f→%.3f (%+.3f, [%+.3f, %+.3f]) | %.2f→%.2f | %.1f→%.1f | %.1f→%.1f | %.1f→%.1f | %.3f→%.3f | %.2f | %.2f |' % (
            s, ph, g, c['won']['base'], c['won']['prop'], c['won']['delta'], ci[0], ci[1], c['time']['base'], c['time']['prop'],
            c['damage_taken']['base'], c['damage_taken']['prop'], c['rounds']['base'], c['rounds']['prop'],
            c['reloads']['base'], c['reloads']['prop'], c['death']['base'], c['death']['prop'], fb, un))
    L += ['', '## Per build group (ordinary and boss separate)', '',
          '| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |', '|---|---|---|---|---|---|---|---|']
    for k, c in t.items():
        s, ph, g = k.split('|')
        if '/' not in g: continue
        L.append('| %s | %s | %s | %d | %.3f→%.3f | %.2f→%.2f | %.1f→%.1f | %.1f→%.1f |' % (s, ph, g, c['n'], c['won']['base'], c['won']['prop'],
                 c['time']['base'], c['time']['prop'], c['damage_taken']['base'], c['damage_taken']['prop'], c['reloads']['base'], c['reloads']['prop']))
    L += ['', '## Build ranking stability across assumption sets', '']
    for ph, d in st.items():
        L.append('**%s**' % ph)
        for s, v in d.items():
            if s == 'win_delta_by_set': continue
            L.append('- %s: Spearman vs default %s; order %s' % (s, 'n/a' if v['spearman_vs_default'] is None else '%.2f' % v['spearman_vs_default'], ', '.join(v['order'])))
        L.append('- win-rate delta (proposal − baseline) by set: %s' % ', '.join('%s %+.3f' % (s, v) for s, v in d['win_delta_by_set'].items() if v is not None))
        L.append('')
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    main()
