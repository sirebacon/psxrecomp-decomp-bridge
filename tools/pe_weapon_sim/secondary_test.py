"""Does carrying and switching to a secondary weapon help? (fixed builds, matched seeds)

python -m pe_weapon_sim.secondary_test [--seeds 8] [--fights 6] [--assumptions default,human_reaction]
Pairs each seed's Disc2 MAG build (group C) with the same seed's P90 (group D) and compares:
  mag_only, p90_only, crowd_switch (P90 while >= 2 enemies alive, else MAG),
  boss_switch (MAG when the only living enemy is a boss, else P90).
Switching uses source_combat's switch path (half-bar rule and menu / stream updates). The second
gun's ammo is its own pool. Results: findings/data/pe-secondary-test-2026-10-19.json and .md.
"""
import argparse, json, random, statistics, sys
from pathlib import Path

from . import engine as E, rules as R
from .compare_rules import ASSUMPTIONS, builds, campaign_battles, options_for, proposal_from
from .decomp_animation import source_behavior_rules
from .economy.source_stats import aya_stats
from .run_benchmark import PROF
from . import encounters as N

ROOT = Path(__file__).resolve().parents[2]


def policy(name):
    if name in ('mag_only', 'p90_only'): return None
    def crowd(state):
        alive = [f for f in state['foes'] if f['cur'] > 0]
        return 'p90' if len(alive) >= 2 else 'primary'
    def boss(state):
        alive = [f for f in state['foes'] if f['cur'] > 0]
        return 'primary' if len(alive) == 1 and alive[0]['boss'] else 'p90'
    return {'crowd_switch': crowd, 'boss_switch': boss}[name]


def main(argv=None):
    from .enemy_identity import FIRST_RUN_SHARED_CELLS as cells
    ap = argparse.ArgumentParser(); ap.add_argument('--seeds', type=int, default=8); ap.add_argument('--fights', type=int, default=6)
    ap.add_argument('--assumptions', default='default,human_reaction'); ap.add_argument('--free-switch', action='store_true')
    ap.add_argument('--proposal', default='baseline')
    ap.add_argument('--out', default='pe-secondary-test-2026-10-19'); a = ap.parse_args(argv)
    bs = {(b['group'], b['seed']): b for b in builds(['Disc2'], a.seeds, ['C', 'D'])}
    rules, cfg_tf = proposal_from(a.proposal); tf = cfg_tf or (lambda c: c)
    battles = campaign_battles('Disc2'); rows = []
    for (g, seed), mag in sorted(bs.items()):
        if g != 'C' or ('D', seed) not in bs: continue
        p90 = bs['D', seed]
        for i in range(a.fights):
            battle = battles[random.Random(seed * 1009 + i * 7).randrange(len(battles))]
            for s in a.assumptions.split(','):
                for strat in ('mag_only', 'p90_only', 'crowd_switch', 'boss_switch'):
                    asm = ASSUMPTIONS[s]; o = options_for(asm, cells); o['hp'] = aya_stats(mag['aya']['level'])['max_hp']
                    cfg = tf(p90['cfg'] if strat == 'p90_only' else mag['cfg'])
                    if strat not in ('mag_only', 'p90_only'):
                        o['weapons'] = {'p90': tf(p90['cfg'])}; o['weapon_policy'] = policy(strat)
                        o['reserve_ammo'] = {0: 999, 1: 999, 2: 999}
                        if a.free_switch: o['switch_cost'] = 'free'        # candidate rule: switching costs no gauge
                    prof = PROF['boss'] if battle['boss'] else PROF['normal']
                    if asm.get('distance_scale'): prof = N.Scaled(prof, asm['distance_scale'])
                    st = E.fight(source_behavior_rules(rules), cfg, mag['aya'], [dict(f) for f in battle['foes']], prof,
                                 random.Random(seed * 7919 + i), armor=mag['armor'], source_options=o, time_cap=90, policy='walk')
                    rows.append(dict(seed=seed, fight=i, assumption=s, strategy=strat, boss=battle['boss'], won=st['won'], time=st['time'],
                                     taken=st['damage_taken'], switches=st.get('switches', 0), rounds=st['rounds']))
        print(seed, len(rows), file=sys.stderr, flush=True)
    out = {}
    for s in a.assumptions.split(','):
        for enc in ('ordinary', 'boss'):
            for strat in ('mag_only', 'p90_only', 'crowd_switch', 'boss_switch'):
                rr = [r for r in rows if r['assumption'] == s and r['strategy'] == strat and r['boss'] == (enc == 'boss')]
                if rr: out['%s|%s|%s' % (s, enc, strat)] = dict(n=len(rr), **{k: statistics.mean(r[k] for r in rr) for k in ('won', 'time', 'taken', 'switches', 'rounds')})
    (ROOT / 'findings/data' / (a.out + '.json')).write_text(json.dumps(dict(summary=out, rows=rows), indent=1), encoding='utf-8')
    L = ['# Secondary weapon test (Disc2, MAG + P90%s%s) — October 19, 2026' % (', free switch' if a.free_switch else '', '' if a.proposal == 'baseline' else ', rules ' + a.proposal), '',
         'Matched seeds and logged Disc2 battles; switching through the source switch path (half-bar rule). Bosses are an incomplete scenario.', '',
         '| Assumptions | Encounters | Strategy | n | Win | Time s | Damage taken | Switches | Rounds |', '|---|---|---|---|---|---|---|---|---|']
    for k, v in out.items():
        s, enc, strat = k.split('|')
        L.append('| %s | %s | %s | %d | %.3f | %.2f | %.1f | %.2f | %.1f |' % (s, enc, strat, v['n'], v['won'], v['time'], v['taken'], v['switches'], v['rounds']))
    (ROOT / 'findings' / (a.out + '.md')).write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
