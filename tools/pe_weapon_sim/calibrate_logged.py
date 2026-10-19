"""Independent check against captured play: replay every logged won battle and compare
simulated fight time / damage taken with the logged values (pe-campaign-2026-10-17.json).

For each battle: the logged gun (battle 'gun' id) with the bonus / mods of the latest save that
held that gun at or before the battle (else the nearest save with it, labelled), the armor of
that save, Aya's source stats at the logged level, the battle's own enemies (evaluation pool
filters), the normal / boss distance profile, and the options of compare_rules (assumption set
selectable). HP is unbounded so damage taken is not truncated by deaths; time cap 90 s.
python -m pe_weapon_sim.calibrate_logged [--fights 8] [--assumptions default,late,...]
Outputs findings/data/pe-calibration-logged-2026-10-18.json and findings/pe-calibration-logged-2026-10-18.md.
"""
import argparse, json, math, random, statistics, sys, zlib
from pathlib import Path

from . import engine as E, rules as R
from .decomp_animation import source_behavior_rules
from .run_benchmark import PROF
from .compare_rules import ASSUMPTIONS, options_for
from .economy import equipment, evaluation, source_stats, tables

# Marked bosses whose script refills HP at the 1000000 threshold (a second phase): room 188 actor 5
# Entity_SetField 44/45 = 300; the log shows the reset (dmg 999660, left 300). All other marked foes end there.
PHASE2_HP = {('188', '0x021A'): 300}
LOGGED_CAST_SPELLS = {'Heal1', 'Heal2', 'Heal3', 'Detox', 'Haste', 'Barrier', 'Slow', 'Confuse', 'GeneHeal', 'Preraise', 'EnergyShot', 'Liberate'}

ROOT = Path(__file__).resolve().parents[2]


RAW_LOG = Path('D:/Recomp Games/Parasite Eve Project/parasite-eve-recomp/build-release/pe_play_log.csv')


def raw_battles():
    """Battle rows of the raw play log aligned to the campaign battles (map, secs, exp in order).
    The logger's secs field is (frames*10/599 + 5)/10 (pe_loot_logger.c pe_secs), i.e. real
    seconds / 10; real time is frames / 59.9."""
    import csv, re
    if not RAW_LOG.exists(): return None
    with open(RAW_LOG, encoding='utf-8', errors='replace') as fh: allrows = list(csv.DictReader(fh))
    rows = [r for r in allrows if r['kind'] == 'battle']
    kv = lambda s: dict(re.findall(r'(\w+)=([^ ]*)', s))
    camp = json.loads((ROOT / 'findings/data/pe-campaign-2026-10-17.json').read_text(encoding='utf-8'))
    # Per battle row, the enemy rows logged before it (in order) with each slot's hit list, so a
    # foe that only ever took one full-HP hit (a scripted removal) can be recognised.
    enemies_before, hurts_before, pending, hits, hurts = {}, {}, [], {}, []
    for r in allrows:
        if r['kind'] == 'hurt':
            hurts.append((int(r['play_s']), int(kv(r['detail'])['dmg'])))
        elif r['kind'] == 'hit':
            d = kv(r['detail']); hits.setdefault(d['slot'], []).append((int(d['dmg']), int(d['left'])))
        elif r['kind'] == 'enemy':
            d = kv(r['detail']); pending.append(dict(slot=d['slot'], id=d['id'], hp=int(d['hp']), hits=hits.pop(d['slot'], [])))
        elif r['kind'] == 'battle':
            enemies_before[id(r)] = pending; hurts_before[id(r)] = hurts; pending, hits, hurts = [], {}, []
    by_detail = {(r['map'], r['detail']): enemies_before.get(id(r), []) for r in allrows if r['kind'] == 'battle'}
    hurts_by = {(r['map'], r['detail']): hurts_before.get(id(r), []) for r in allrows if r['kind'] == 'battle'}
    out = []; j = 0
    for e in camp['events']:
        if e['type'] != 'battle': continue
        hit = None
        while j < len(rows):
            d = kv(rows[j]['detail']); r = rows[j]; j += 1
            if r['map'] == e['map'] and int(d['secs']) == int(e['secs']) and int(d['exp']) == int(e['exp']):
                hit = dict(d, _enemies=by_detail.get((r['map'], r['detail']), []), _hurts=hurts_by.get((r['map'], r['detail']), [])); break
        out.append((tuple(e['t']), hit))
    return dict(out)


def battles():
    camp = json.loads((ROOT / 'findings/data/pe-campaign-2026-10-17.json').read_text(encoding='utf-8'))
    saves = sorted([(tuple(e['t']), e) for e in camp['events'] if e['type'] == 'save' and 'gun' in e], key=lambda x: x[0])
    raw = raw_battles() or {}
    out = []
    for e in camp['events']:
        if e['type'] != 'battle' or e['outcome'] != 'win': continue
        gid = int(e['gun'], 16); t = tuple(e['t']); d = raw.get(t) or {}
        prior = [s for tt, s in saves if tt <= t and s['gun']['id'] == gid]
        anyg = [s for tt, s in saves if s['gun']['id'] == gid]
        src = prior[-1] if prior else (min(anyg, key=lambda s: abs(s['t'][0] - t[0])) if anyg else None)
        last = [s for tt, s in saves if tt <= t]
        armor = (last[-1] if last else saves[0][1]).get('armor')
        foes = []
        logged = d.get('_enemies', [])
        logged = logged if [r['id'] for r in logged] == [x['id'] for x in e['enemies']] else [None] * len(e['enemies'])
        boss_battle = any(x['boss'] for x in e['enemies'])
        for x, lr in zip(e['enemies'], logged):
            hp = x['hp'] - 1000000 if x['hp'] > 1000000 else x['hp']
            if hp <= 0: continue
            f = dict(name=x['id'], loc=e['map'], hp=hp, level=max(1, round((x['defense'] - 3) / 1.6)), defense=x['defense'],
                     boss=x['boss'], heat=x['heat'], frost=x['frost'], cyanide=x['cyanide'], acid=x['acid'], tranq=x['tranq'])
            if x['defense'] >= 200 or x['id'] == '0x0200':
                # Never hit by Aya in the log (defense >= 200: room 34 0x0307; the 0x0200 helpers of rooms 156 / 380).
                # Dropped by default; with --controllers they stay as untargetable attackers (foe_for).
                f['_part'] = True
            # Scripted boss HP (used only with --controllers, see foe_for):
            if boss_battle and len(e['enemies']) > 1 and hp <= 10:
                # Boss cores logged at 10 HP (room 123 0x0312, room 273 0x0325): never hit by Aya, the
                # battle ends without (273) or with only a scripted (123: dmg 1000010) death.
                f['_controller'] = True
            elif boss_battle and lr is not None and len(lr['hits']) == 1 and lr['hits'][0] == (x['hp'], 0) and hp >= 100:
                # One hit for the whole HP at the end (e.g. room 269 slots 3-6 at the boss's death):
                # a scripted removal of a part that never engaged.
                f['_unengaged'] = True
            if x['hp'] > 1000000 and (e['map'], x['id']) in PHASE2_HP: f['_phase2_hp'] = PHASE2_HP[e['map'], x['id']]
            foes.append(f)
        if not foes: continue
        out.append(dict(t=t, phase=e['phase'], map=e['map'], level=e['level'], boss=any(f['boss'] for f in foes), foes=foes,
                        gun=gid, gun_source='prior save' if prior else ('nearest save' if anyg else 'no save (base item)'),
                        gun_bonus=(src or {}).get('gun', {}).get('bonus', [0, 0, 0]), gun_mods=(src or {}).get('gun', {}).get('mods', []),
                        armor=armor, logged_secs=int(d['frames']) / 59.9 if d else e['secs'] * 10.0, logged_taken=e['taken'],
                        logged_turns=int(d.get('turns', 0) or 0), logged_dealt=int(d.get('dealt', 0) or 0), logged_shots=int(d.get('shots', 0) or 0),
                        logged_reloads=int(d.get('reloads', 0) or 0), logged_swaps=int(d.get('wswaps', 0) or 0),
                        pe_casts=d.get('casts', ''), acts=d.get('acts', ''), raw=bool(d), hurts=d.get('_hurts', []),
                        pe_start=int(d['pe'].split('->')[0]) if d.get('pe') else None,
                        bag={int(x.split(':')[0], 16): int(x.split(':')[1]) for x in d.get('bag', '').split('/') if ':' in x}, _used=d.get('used', '')))
    for b in out:                                       # the logged bag is the end state: add back what was used
        b['used_items'] = {int(x.split(':')[0], 16): int(x.split(':')[1]) for x in b.get('_used', '').split('/') if ':' in x}
        for x in b.pop('_used', '').split('/'):
            if ':' in x: k = int(x.split(':')[0], 16); b['bag'][k] = b['bag'].get(k, 0) + int(x.split(':')[1])
    known = set()                                       # spells cast so far in the run (known by then)
    for b in out:
        known |= {c.split(':')[0] for c in b['pe_casts'].split('/') if c}
        b['known_spells'] = sorted(known)
    return out


def foe_for(f, controllers):
    if f.get('_part') and not controllers: return None
    out = {k: v for k, v in f.items() if k not in ('_controller', '_phase2_hp', '_unengaged', '_part')}
    if f.get('_part'): out['controller'] = True
    if controllers and f.get('_controller'): out['controller'] = True
    if controllers and f.get('_phase2_hp'): out['phase2_hp'] = f['_phase2_hp']
    return out


def setup(b):
    item = equipment.Item(b['gun'], 'logged', b['phase']); item.bonus = list(b['gun_bonus']); item.mods = list(b['gun_mods'])
    cfg = item.cfg()
    armor_item = None
    if b['armor']:
        armor_item = equipment.Item(b['armor']['id'], 'logged', b['phase'])
        armor_item.bonus = list(b['armor'].get('bonus', [0, 0, 0])); armor_item.mods = list(b['armor'].get('mods', []))
    aya = source_stats.player_inputs(max(1, b['level']), armor_item)
    return cfg, aya, evaluation.armor_of(armor_item)


def run(b, a_name, fights, cells, policy='stand', reaction=0, log_era=False, atb_guard=False, logged_charge=False, evade=0.0, reaction_paused=False, serial=False, pe=False, evade_melee=0.0, evade_melee_early=0.0, logged_casts=False, boss_cap=90, controllers=False, identity_rank=False, logged_items=False, steals=False, contact=False, actor_by_hp=False, borrow=False):
    cfg, aya, armor = setup(b)
    opts = options_for(ASSUMPTIONS[a_name], cells); opts['hp'] = 10 ** 7
    opts['player_max_hp'] = source_stats.aya_stats(max(1, b['level']))['max_hp']   # HP-share statuses use real HP
    if reaction: opts['reaction_updates'] = reaction
    if atb_guard: opts['atb_guard'] = True
    if logged_charge: opts['logged_charge'] = True    # play-log charge step where scripts give none (logged_charge.py)
    if evade: opts['player_evade'] = evade           # player behaviour assumption (share of strikes avoided)
    if reaction_paused: opts['reaction_paused'] = True  # the reaction time is spent in the paused command menu
    if contact:
        # contact_damage.py: contacts per battle-minute from the play log (hurt == contactDamage, >= 3 s apart).
        opts['contact_damage'] = dict(ord=0.70, boss=0.77, logged=contact == 'logged')   # logged: per-room rate (logged_contact.py)
    if borrow and opts.get('called_slots'):
        opts['called_slots'] = dict(opts['called_slots'], borrow=True)        # enemy_choice.borrowed_plans (labelled)
    if actor_by_hp and opts.get('called_slots'):
        opts['called_slots'] = dict(opts['called_slots'], actor_by_hp=True)   # enemy_choice.unarmed_actor (source)
    if steals: opts['steals'] = True                   # Battle_ApplyEnemyAttack item / ammo steals (source)
    if identity_rank: opts['identity_rank'] = True     # counter rank from the enemy identity (Battle_RollEnemySpawn)
    if serial: opts['serial_action'] = True             # source: enemies freeze (no new attacks) during Aya's action
    if evade_melee: opts['player_evade_melee'] = evade_melee   # behaviour: stepping back from melee swings
    if evade_melee_early and b['phase'] in ('D1', 'D2-4'):
        opts['player_evade_melee'] = evade_melee_early          # the player dodged many melee hits early on (user, 2026-10-19)
    if pe:
        # parasite_energy.py: logged start PE, the spells known by then, vanilla heals (the logged run),
        # heal policy on Aya's source max HP (the fight's hp cap is unbounded here).
        opts['pe'] = dict(spells=b['known_spells'], start=b['pe_start'], heal_rules='vanilla',
                          max_hp=source_stats.aya_stats(max(1, b['level']))['max_hp'], bag=b['bag'])
        if logged_casts:
            # Replay the battle's logged casts (player choices) instead of the generic policy;
            # powers the model has no effect for (Liberate, Scan, Gene Heal, Preraise) are dropped.
            script = {}
            for part in (b['pe_casts'] or '').split('/'):
                if ':' in part and part.split(':')[0] in LOGGED_CAST_SPELLS:
                    script[part.split(':')[0]] = int(part.split(':')[1])
            opts['pe']['script'] = script
        if logged_items:
            # Replay the battle's logged item use (Revive 0x12 is automatic at death, so not scripted).
            opts['pe']['items'] = {k: v for k, v in b['used_items'].items() if k != 0x12}
    if log_era:
        # The logged run used Mod Effects 'Counter chance %' = 500 (REBALANCED default, removed in
        # c7dc04f): the roll's HP level x5, and the HP-level bug froze that level at level 24 (240).
        opts['counter_hp_level'] = 5 * min(10 * max(1, b['level']), 240)
    prof = PROF['boss'] if b['boss'] else PROF['normal']
    res = []
    for i in range(fights):
        st = E.fight(source_behavior_rules(R.CURRENT), cfg, aya, [x for x in (foe_for(f, controllers) for f in b['foes'] if not (controllers and f.get('_unengaged'))) if x], prof,
                     random.Random(zlib.crc32(repr((b['t'], i)).encode())), armor=armor, source_options=opts, time_cap=boss_cap if b['boss'] else 90, policy=policy)
        res.append(st)
    return dict(sim_secs=statistics.mean(s['time'] for s in res), sim_taken=statistics.mean(s['damage_taken'] for s in res),
                sim_turns=statistics.mean(s.get('turns', 0) + s.get('pe_casts', 0) + s.get('items_used', 0) for s in res),   # the log counts casts / items as turns
                sim_rounds=statistics.mean(s['rounds'] for s in res),
                sim_reloads=statistics.mean(s['reloads'] for s in res),
                sim_won=statistics.mean(s['won'] for s in res),
                fallback=sum(s.get('legacy_damage_hits', 0) for s in res), hits=sum(s.get('hits_taken', 0) for s in res),
                sim_casts=statistics.mean(s.get('pe_casts', 0) for s in res), sim_healed=statistics.mean(s.get('healed', 0) for s in res), sim_items=statistics.mean(s.get('items_used', 0) for s in res), pe_sim=pe,
                sim_dealt=statistics.mean(s.get('damage', 0) for s in res), sim_bullets=statistics.mean(s.get('bullets', 0) for s in res))


def summary(rows):
    def agg(rr):
        if not rr: return None
        ls = [r['logged_secs'] for r in rr]; ss = [r['sim_secs'] for r in rr]
        lt = [r['logged_taken'] for r in rr]; st = [r['sim_taken'] for r in rr]
        return dict(n=len(rr), logged_secs=statistics.mean(ls), sim_secs=statistics.mean(ss),
                    secs_ratio_median=statistics.median([s / max(l, 1) for s, l in zip(ss, ls)]),
                    logged_taken=statistics.mean(lt), sim_taken=statistics.mean(st),
                    taken_ratio_of_means=statistics.mean(st) / max(1e-9, statistics.mean(lt)),
                    corr_secs=corr(ls, ss), corr_taken=corr(lt, st),
                    logged_turns=statistics.mean(r['logged_turns'] for r in rr), sim_turns=statistics.mean(r['sim_turns'] for r in rr),
                    corr_turns=corr([r['logged_turns'] for r in rr], [r['sim_turns'] for r in rr]),
                    logged_reloads=statistics.mean(r['logged_reloads'] for r in rr), sim_reloads=statistics.mean(r['sim_reloads'] for r in rr),
                    logged_secs_per_turn=slope([r['logged_turns'] for r in rr], ls), sim_secs_per_turn=slope([r['sim_turns'] for r in rr], ss),
                    fallback_share=sum(r['fallback'] for r in rr) / max(1, sum(r['hits'] for r in rr)))
    out = {}
    for a in sorted({r['assumption'] for r in rows}):
        ra = [r for r in rows if r['assumption'] == a]
        ra = [r for r in ra if not r['pe_casts'] or r.get('pe_sim')]   # PE battles only when PE is simulated (--pe)
        out[a] = {'ALL normal': agg([r for r in ra if not r['boss']]), 'ALL boss': agg([r for r in ra if r['boss']])}
        for ph in ('D1', 'D2-4', 'D5', 'Disc2'):
            out[a][ph + ' normal'] = agg([r for r in ra if r['phase'] == ph and not r['boss']])
            out[a][ph + ' boss'] = agg([r for r in ra if r['phase'] == ph and r['boss']])
    return out


def slope(x, y):
    if len(x) < 3: return None
    mx, my = statistics.mean(x), statistics.mean(y); sxx = sum((a - mx) ** 2 for a in x)
    return None if sxx == 0 else sum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx


def corr(x, y):
    if len(x) < 3: return None
    mx, my = statistics.mean(x), statistics.mean(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x)); sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return None if sx == 0 or sy == 0 else sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def main(argv=None):
    from .enemy_identity import FIRST_RUN_SHARED_CELLS as cells
    ap = argparse.ArgumentParser(); ap.add_argument('--fights', type=int, default=8)
    ap.add_argument('--assumptions', default='default'); ap.add_argument('--out', default='pe-calibration-logged-run')
    ap.add_argument('--policy', default='stand'); ap.add_argument('--reaction', type=int, default=0)
    ap.add_argument('--log-era', action='store_true', help='replay with the logged run Counter boost')
    ap.add_argument('--atb-guard', action='store_true', help='halve incoming damage while the gauge is above 0 (source)')
    ap.add_argument('--logged-charge', action='store_true', help='play-log charge step for identities with no literal one')
    ap.add_argument('--evade', type=float, default=0.0, help='share of enemy strikes the player avoids (behaviour assumption)')
    ap.add_argument('--reaction-paused', action='store_true', help='reaction updates pass in the paused menu (enemies frozen)')
    ap.add_argument('--logged-casts', action='store_true', help='with --pe: replay the logged casts of each battle')
    ap.add_argument('--evade-melee-early', type=float, default=0.0, help='melee dodge share in Days 1-4 only (behaviour)')
    ap.add_argument('--evade-melee', type=float, default=0.0, help='share of melee strikes avoided by stepping back (behaviour)')
    ap.add_argument('--pe', action='store_true', help='simulate Parasite Energy (heals / Haste) and include the battles with casts')
    ap.add_argument('--serial', action='store_true', help='game flag 0x100: enemy charge/scripts freeze during Aya''s action')
    ap.add_argument('--boss-cap', type=float, default=90, help='sim time cap (s) for boss battles; long logged boss fights exceed 90')
    ap.add_argument('--controllers', action='store_true', help='scripted boss HP: 10-HP cores untargetable, scripted second phases (PHASE2_HP)')
    ap.add_argument('--logged-items', action='store_true', help='with --pe --logged-casts: replay the logged item use')
    ap.add_argument('--contact', nargs='?', const='global', default=False, help='enemy body-contact damage (source value); rate: global (default) or logged (per room)')
    ap.add_argument('--borrow', action='store_true', help='unresolved room/identity pairs use the agreed plans of the identity from other rooms')
    ap.add_argument('--actor-by-hp', action='store_true', help='resolve the actor of a shared identity by HP; unarmed actors never strike')
    ap.add_argument('--steals', action='store_true', help='enemy item / ammo steals (source)')
    ap.add_argument('--identity-rank', action='store_true', help='counter rank difference from the enemy identity low byte (source)')
    ap.add_argument('--multi-kind', action='store_true', help='resolve kind-switching bosses and silent parts (enemy_identity)')
    a = ap.parse_args(argv)
    if a.multi_kind:
        from .enemy_identity import MULTI_KIND
        cells = {**cells, MULTI_KIND: 1}
    rows = []
    bs = battles()
    for name in a.assumptions.split(','):
        for k, b in enumerate(bs):
            r = run(b, name, a.fights, cells, a.policy, a.reaction, a.log_era, a.atb_guard, a.logged_charge, a.evade, a.reaction_paused, a.serial, a.pe, a.evade_melee, a.evade_melee_early, a.logged_casts, a.boss_cap, a.controllers, a.identity_rank, a.logged_items, a.steals, a.contact, a.actor_by_hp, a.borrow)
            rows.append(dict({x: b[x] for x in ('t', 'phase', 'map', 'level', 'boss', 'gun', 'gun_source', 'logged_secs', 'logged_taken',
                                                'logged_turns', 'logged_dealt', 'logged_shots', 'logged_reloads', 'logged_swaps', 'pe_casts', 'acts')},
                             assumption=name, **r))
            if k % 20 == 0: print(name, k, len(bs), file=sys.stderr, flush=True)
    s = summary(rows)
    (ROOT / 'findings/data' / (a.out + '.json')).write_text(json.dumps(dict(fights=a.fights, policy=a.policy, reaction=a.reaction, summary=s, rows=rows), indent=1, default=list), encoding='utf-8')
    L = ['# Logged-battle calibration — October 18, 2026', '',
         'Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (%d fights each; player policy %s, reaction %d updates, log-era Counter boost %s). HP unbounded; damage is not truncated.' % (a.fights, a.policy, a.reaction, a.log_era), '',
         ('Parasite Energy and items are simulated (parasite_energy.py)' + (', replaying the logged casts' if a.logged_casts else '') + '.' if a.pe else 'Battles with PE casts are excluded (PE abilities are not simulated).') + ' Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.', '',
         '| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |', '|---|---|---|---|---|---|---|---|']
    for name, groups in s.items():
        for g, v in groups.items():
            if not v: continue
            f = lambda x: 'n/a' if x is None else '%.2f' % x
            L.append('| %s | %s | %d | %.2f → %.2f (%s) | %s → %s | %.2f → %.2f | %.1f → %.1f (%.2f, %s) | %.2f |' % (
                name, g, v['n'], v['logged_turns'], v['sim_turns'], f(v['corr_turns']), f(v['logged_secs_per_turn']), f(v['sim_secs_per_turn']),
                v['logged_reloads'], v['sim_reloads'], v['logged_taken'], v['sim_taken'], v['taken_ratio_of_means'], f(v['corr_taken']), v['fallback_share']))
    (ROOT / 'findings' / (a.out + '.md')).write_text('\n'.join(L) + '\n', encoding='utf-8')
    print(json.dumps({n: {g: (v and {k: round(x, 2) if isinstance(x, float) else x for k, x in v.items()}) for g, v in grp.items() if g.startswith('ALL')} for n, grp in s.items()}, indent=1))


if __name__ == '__main__':
    main()
