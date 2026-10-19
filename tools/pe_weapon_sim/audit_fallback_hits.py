"""Audit of incoming hits in the current-model run: which enemies / actions used fallback damage.

Replays run_current_model's cases (same groups, seeds, phases, encounters, options) with the
opt-in `hit_trace`, then attributes every landed hit to (map, enemy id, boss, power source,
action slot) and joins the static catalogs to say why power was missing.
python -m pe_weapon_sim.audit_fallback_hits [--bound early|late|both] [--out PATH]
"""
import argparse, collections, json, sys
from pathlib import Path

from . import rules
from .decomp_animation import source_behavior_rules
from .economy import equipment, evaluation, tables, source_stats
from .enemy_identity import FIRST_RUN_SHARED_CELLS
from .run_behavior_balance import GROUPS, ENCOUNTERS, config

ROOT = Path(__file__).resolve().parents[2]


def cases(bounds=('early', 'late')):
    """Yield (bound, group, phase, enc, seed, cfg, aya, armor, options) exactly as run_current_model."""
    history = json.loads((ROOT / 'findings/data/pe-weapon-p3-completion-2026-10-17.json').read_text(encoding='utf-8'))
    for bound in bounds:
        for group in GROUPS:
            for run in history['raw']['overlap|' + group][:8]:
                for phase in ('D5', 'Disc2'):
                    cp = run['cps'][phase]; cfg = config(cp)
                    name = cp['armor'].split('#')[0].strip()
                    ids = [i for i, r in tables.ITEMS.items() if r['kind'] == 9 and r['name'].upper() == name.upper()]
                    armor_item = equipment.Item(ids[0], 'frozen', phase)
                    armor_item.bonus = list(cp['armor_bonus'])
                    inverse = {v: k for k, v in tables.ARMOR_FX.items()}
                    armor_item.mods = [inverse[m] for m in cp['armor_mods']]
                    value = source_stats.value_at(cp['level']); purchased = value
                    for _ in range(cp['at_bought']): purchased = source_stats.next_threshold(5, purchased)
                    aya = source_stats.player_inputs(cp['level'], armor_item, at_extra=purchased - value)
                    armor = evaluation.armor_of(armor_item)
                    for enc in ENCOUNTERS:
                        options = dict(static_enemy_catalog=True, shared_cells=FIRST_RUN_SHARED_CELLS,
                                       enemy_action_timing='fast', contact_timing=bound, melee_window=bound,
                                       melee_reach=True, effect_actions=True, enemy_choice=dict(contact=bound, ambiguous='first'),
                                       player_status=True, hp=385, reserve_ammo={0: 999, 1: 999, 2: 999},
                                       enemy_defaults=dict(charge_step=90, windup=10, recovery=10, source_action_slot=0))
                        yield bound, group, phase, enc, run['seed'], cfg, aya, armor, options


def why(loc, name, cells=FIRST_RUN_SHARED_CELLS):
    """Static reasons an identity lacks source power: called slots and, per slot, the first
    enemy_power rejection (power_gaps.reasons); overlay-driven when no actor calls a slot."""
    from .enemy_catalog import lookup
    from .enemy_choice import called_slots
    from .power_gaps import reasons
    foe = dict(loc=loc, name=name)
    called = called_slots(foe, cells)
    out = dict(static=bool(lookup(foe, cells)), called_slots={str(k): v for k, v in called.items()})
    if not called:
        out['reason'] = 'no attack calls in the identity scripts (overlay-driven or unresolved identity)'
        return out
    out['slot_reasons'] = {}
    for s in called:
        try:
            from .enemy_power import power_profile
            ok = power_profile(foe, s, cells, scaled_identities=True, default_critical=True)
        except ValueError as exc: ok = None; out['slot_reasons'][str(s)] = 'error: ' + str(exc)
        if ok: out['slot_reasons'][str(s)] = 'resolved (power %d)' % ok['power']
        elif str(s) not in out['slot_reasons']: out['slot_reasons'][str(s)] = reasons(loc, name, s)['reason']
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--bound', default='both'); ap.add_argument('--out'); ap.add_argument('--extra', default='{}', help='JSON options merged into every case')
    a = ap.parse_args()
    bounds = ('early', 'late') if a.bound == 'both' else (a.bound,)
    profile = source_behavior_rules(rules.CURRENT)
    hits = collections.Counter(); dmg = collections.Counter(); where = collections.defaultdict(collections.Counter)
    fights = 0; counters = collections.Counter(); strikes = collections.Counter()
    for bound, group, phase, enc, seed, cfg, aya, armor, options in cases(bounds):
        options['hit_trace'] = True; options.update(json.loads(a.extra.replace('BOUND', bound)) if 'BOUND' in a.extra else json.loads(a.extra))
        for f in evaluation.run_enc(profile, cfg, aya, enc, phase, 6, seed=seed, armor=armor, source_options=options, time_cap=90):
            fights += 1
            for k, v in f.items():
                if isinstance(v, (int, float)) and k.startswith(('strike_timing_', 'called_slot', 'choice_', 'melee_reach', 'legacy_damage', 'explicit_power', 'status_', 'incoming_status')):
                    counters[k] += v
            for k, v in f.items():
                if k.startswith('_hit|'):
                    key = tuple(k.split('|')[1:]); hits[key] += v; where[key][(phase, enc)] += v
                elif k.startswith('_strike|'):
                    strikes[tuple(k.split('|')[1:])] += v
                elif k.startswith('_dmg|'):
                    dmg[tuple(k.split('|')[1:])] += v
        print(bound, group, phase, enc, fights, file=sys.stderr, flush=True)
    total = sum(hits.values()); fb = sum(v for k, v in hits.items() if k[3] == 'fallback')
    per_id = collections.defaultdict(lambda: collections.Counter())
    for (loc, name, boss, src, slot), v in hits.items():
        per_id[loc, name, boss][src] += v
        per_id[loc, name, boss][src + '_damage'] += dmg[loc, name, boss, src, slot]
    rows = []
    for (loc, name, boss), c in sorted(per_id.items(), key=lambda kv: -kv[1]['fallback']):
        rows.append(dict(map=loc, id=name, boss=boss == '1', fallback_hits=c['fallback'], power_hits=c['power'],
                         fallback_damage=round(c['fallback_damage'], 1), power_damage=round(c['power_damage'], 1),
                         share_of_fallback=round(c['fallback'] / fb, 4) if fb else 0,
                         encounters={'%s/%s' % pe: n for pe, n in sorted(where_sum(where, loc, name, boss).items())},
                         **({'why': why(loc, name)} if c['fallback'] else {})))
    out = dict(scope='landed incoming hits in a replay of run_current_model with hit_trace (bounds %s)' % (bounds,), extra=json.loads(a.extra),
               fights=fights, hits=total, fallback_hits=fb, fallback_share=round(fb / total, 4) if total else 0,
               by_group=dict(normal=group_sum(rows, False), boss=group_sum(rows, True)), counters=dict(sorted(counters.items())),
               strikes=[dict(map=k[0], id=k[1], boss=k[2] == '1', timing=k[3], slot=k[4], n=v) for k, v in strikes.most_common()],
               identities=rows)
    path = Path(a.out) if a.out else ROOT / 'findings/data/pe-fallback-hit-audit-2026-10-18.json'
    path.write_text(json.dumps(out, indent=1), encoding='utf-8')
    print(json.dumps({k: out[k] for k in ('fights', 'hits', 'fallback_hits', 'fallback_share', 'by_group')}, indent=1))
    for r in rows[:15]: print(r['map'], r['id'], 'boss' if r['boss'] else 'normal', r['fallback_hits'], r['power_hits'], r['share_of_fallback'])


def where_sum(where, loc, name, boss):
    c = collections.Counter()
    for (l, n, b, src, slot), v in where.items():
        if (l, n, b) == (loc, name, boss) and src == 'fallback': c.update(v)
    return c


def group_sum(rows, boss):
    rr = [r for r in rows if r['boss'] == boss]
    return dict(identities=len(rr), fallback_hits=sum(r['fallback_hits'] for r in rr), power_hits=sum(r['power_hits'] for r in rr))


if __name__ == '__main__':
    main()
