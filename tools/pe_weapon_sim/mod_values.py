"""Single-mod values on the calibrated model (2026-10-19).

python -m pe_weapon_sim.mod_values --stage D5|Disc2 --rules vanilla|current [--seeds 2]

For each class gun at typical investment (compare_rules.INVEST), fight the stage's logged battles with
no mod and with each single mod effect added (data.MODS / data.FLAGS; a RoF / mode / Commands mod
replaces the gun's own value of that kind, as an installed mod does). Same battles and seeds for every
variant, so each mod's value is its paired difference from 'none'. Disc2 uses every boss battle and
every 4th ordinary battle. Calibrated options as compare_rules --calibrated. Writes
findings/data/pe-mod-values-<stage>-<rules>-2026-10-19.json.
"""
import argparse, json, statistics
from pathlib import Path

from . import compare_rules as CR, data as D, rules as R
from .run_benchmark import W, gun_cfg, CLASS_GUNS
from .progression import Gun

ROOT = Path(__file__).resolve().parents[2] / 'findings/data'
EFFECTS = list(D.MODS) + list(D.FLAGS)


def guns(stage):
    g = dict(CLASS_GUNS['Day5' if stage == 'D5' else 'Wayne'])
    if stage == 'Disc2': g.update(CLASS_GUNS.get('WayneRocket', {}))
    return g


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--stage', required=True); ap.add_argument('--rules', required=True)
    ap.add_argument('--seeds', type=int, default=2)
    ap.add_argument('--effects', nargs='*')                  # subset of mods (default all)
    ap.add_argument('--tag', default=None)                   # output name suffix (defaults to --rules)
    a = ap.parse_args()
    from .enemy_identity import FIRST_RUN_SHARED_CELLS as C, MULTI_KIND
    cells = {**C, MULTI_KIND: 1}
    for flag in (CR.ATB_GUARD, CR.LOGGED_CHARGE, CR.SERIAL, CR.IDENTITY_RANK, CR.CALIBRATED): flag[0] = True
    rules = R.VANILLA if a.rules == 'vanilla' else R.CURRENT if a.rules == 'current' else R.experimental(*a.rules[4:].split('+'))
    battles = CR.campaign_battles(a.stage)
    if a.stage == 'Disc2':
        ords = [b for b in battles if not b['boss']]
        battles = [b for b in battles if b['boss']] + ords[::4]
    assumption = CR.ASSUMPTIONS['logged_player_serial']
    ref = {b['seed']: b for b in CR.builds([a.stage], a.seeds, ['C'])}
    out = []
    for cls, wid in guns(a.stage).items():
        for eff in ['none'] + (a.effects or EFFECTS):
            g = Gun(W[wid]); g.invested = list(CR.INVEST[a.stage]['typical'])
            cfg = gun_cfg(g, [] if eff == 'none' else [eff])
            if eff.startswith('RoF'): cfg = dict(cfg, eff=dict(cfg['eff'], rof_mod=True))   # installed RoF (R-E fire speed applies)
            for seed in range(1, a.seeds + 1):
                b = dict(aya=ref[seed]['aya'], armor=ref[seed]['armor'])
                for i, battle in enumerate(battles):
                    r = CR.run_fight(rules, cfg, b, battle, 'logged_player_serial', assumption, seed * 7919 + i, cells)
                    out.append(dict(cls=cls, eff=eff, seed=seed, battle=i, boss=battle['boss'], won=r['won'], time=r['time'],
                                    damage=r['damage_taken'], rounds=r['rounds']))
        print(cls, len(out), flush=True)
    summ = {}
    for cls in guns(a.stage):
        for enc in (False, True):
            base = {(r['seed'], r['battle']): r for r in out if r['cls'] == cls and r['eff'] == 'none' and r['boss'] == enc}
            for eff in (a.effects or EFFECTS):
                rr = [r for r in out if r['cls'] == cls and r['eff'] == eff and r['boss'] == enc]
                if not rr: continue
                pairs = [(r, base[(r['seed'], r['battle'])]) for r in rr]
                summ['%s|%s|%s' % (cls, 'boss' if enc else 'ord', eff)] = dict(
                    n=len(rr), time=statistics.mean(r['time'] for r, _ in pairs), time_none=statistics.mean(b['time'] for _, b in pairs),
                    damage=statistics.mean(r['damage'] for r, _ in pairs), damage_none=statistics.mean(b['damage'] for _, b in pairs),
                    won=statistics.mean(r['won'] for r, _ in pairs), won_none=statistics.mean(b['won'] for _, b in pairs))
    (ROOT / ('pe-mod-values-%s-%s-2026-10-19.json' % (a.stage, a.tag or a.rules))).write_text(json.dumps(dict(summary=summ, stage=a.stage, rules=a.rules, seeds=a.seeds), indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
