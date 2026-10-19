"""Investment profiles for the weapon strength sweeps (2026-10-19).

python -m pe_weapon_sim.economy.run_profiles [--n 40] [--workers 6]

For each economy setting x player policy, play N matched campaigns (playthrough.play: BP earned per
enemy minus hits, banked at level-up; hits anchored to the logged run and scaled by gun strength;
Junk economy, rare cascade, Tools, Mod Catalog) and record, at the end of Day 2-4, Day 5 and Disc2,
what the player has invested in the gun they carry: bonus attack / range / bullets, which strong
effects it has (2 / 3 Commands, Attack All, Quickdraw), BP earned / spent / still pending, level,
Tools and Junk.

Economy settings: vanilla (no Junk economy), current mod on its Normal preset, Relaxed (preset 0:
150% Junk, shorter pity, cheaper) and Grind (preset 2: 75% Junk, longer pity, dearer).
Players: policies.policy_set() A casual, C weapon optimizer, I balanced, S_wpn weapon stats only,
S_end BP hoarder (the logged run's habit), and F farmer on the farmer exploration profile.
Calibration: the logged exploration profile with the run's own hits (hits_logged) and the hoarder,
compared with the logged save rows.
Writes findings/data/pe-investment-profiles-2026-10-19.json and findings/pe-investment-profiles-2026-10-19.md.
"""
import argparse, json, os, statistics

from . import run_phase3 as P

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
STEM = 'pe-investment-profiles-2026-10-19'
ECON = {'vanilla': 'vanilla', 'normal': 'current', 'relaxed': 'cur:preset=0', 'grind': 'cur:preset=2'}
POLICIES = ('A', 'C', 'I', 'S_wpn', 'S_end')
STAGES = ('D2-4', 'D5', 'Disc2')
STRONG = ('2Cmd', '3Cmd', 'AttackAll', 'Quickdraw')


def tasks(n):
    out = []
    for e, spec in ECON.items():
        for p in POLICIES:
            for s in range(1, n + 1): out.append(dict(econ=spec, policy=(p, None), profile='typical', seed=s, _tag=(e, p)))
        if e in ('vanilla', 'normal'):
            for s in range(1, n + 1): out.append(dict(econ=spec, policy=('F', None), profile='farmer', seed=s, _tag=(e, 'F')))
    cal = 'cur:hits_logged=true'
    for s in range(1, n + 1): out.append(dict(econ=cal, policy=('S_end', None), profile='logged', seed=s, _tag=('calibration', 'S_end')))
    return out


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, int(round(q * (len(xs) - 1)))))]


def summarize(recs):
    groups = {}
    for r in recs: groups.setdefault(tuple(r['_tag']), []).append(r)
    out = {}
    for tag, rr in groups.items():
        for st in STAGES:
            cps = [r['cps'][st] for r in rr if st in r['cps']]
            if not cps: continue
            att = [c['bonus'][0] for c in cps]
            cell = dict(n=len(cps),
                        attack=dict(mean=statistics.mean(att), p10=pct(att, .1), p50=pct(att, .5), p90=pct(att, .9)),
                        range=statistics.mean(c['bonus'][1] for c in cps), bullets=statistics.mean(c['bonus'][2] for c in cps),
                        level=statistics.mean(c['level'] for c in cps),
                        bp_earned=statistics.mean(c['bp_earned'] for c in cps),
                        bp_spent=statistics.mean(sum(c['bp_spent'].values()) for c in cps),
                        bp_attack=statistics.mean(c['bp_spent']['attack'] for c in cps),
                        bp_pending=statistics.mean(c['bp_banked'] + c['bp_pool'] for c in cps),
                        tools=statistics.mean(c['tools'] for c in cps), junk=statistics.mean(c['junk'] for c in cps),
                        kinds={k: sum(1 for c in cps if c['gun_kind'] == k) / len(cps) for k in sorted({c['gun_kind'] for c in cps})},
                        strong={m: sum(1 for c in cps if m in c['mods']) / len(cps) for m in STRONG},
                        guns=sorted({c['gun'] for c in cps}, key=lambda g: -sum(1 for c in cps if c['gun'] == g))[:4])
            out['%s|%s|%s' % (tag[0], tag[1], st)] = cell
    return out


LOGGED = {'D2-4': dict(level=18, gun='0x7B', bonus=[9, 5, 5]), 'D5': dict(level=21, gun='0x89', bonus=[12, 8, 10]),
          'Disc2': dict(level=33, gun='0x64', bonus=[32, 12, 23], note='+54 attack after a final 4,000 BP spend')}


def report(s):
    L = ['# Investment profiles for the strength sweeps — October 19, 2026', '',
         'Playthrough simulations (economy simulator, BP anchored to the logged hits and scaled by gun strength). '
         'Per economy setting and player policy, %d matched campaigns; the numbers describe the gun carried at the end of each stage.' % s['n'], '',
         'Policies: A casual, C weapon optimizer, I balanced, S_wpn weapon stats only, S_end BP hoarder (the logged habit), F farmer (farmer route).', '',
         '## Logged playthrough (anchor)', '', '| Stage | Level | Gun | Bonus attack / range / bullets |', '|---|---|---|---|']
    for st, v in LOGGED.items():
        L.append('| %s | %d | %s | %s%s |' % (st, v['level'], v['gun'], ' / '.join(map(str, v['bonus'])), (' (' + v['note'] + ')') if v.get('note') else ''))
    L += ['', '## Attack bonus on the carried gun (mean, p10–p90) and strong effects', '',
          '| Economy | Player | Stage | Level | Attack mean | p10–p90 | Range | Bullets | BP earned | BP spent (attack) | BP pending | Tools | 2Cmd | AttackAll |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for k, c in sorted(s['cells'].items()):
        e, p, st = k.split('|')
        L.append('| %s | %s | %s | %.1f | %.1f | %d–%d | %.1f | %.1f | %.0f | %.0f (%.0f) | %.0f | %.1f | %.0f%% | %.0f%% |' % (
            e, p, st, c['level'], c['attack']['mean'], c['attack']['p10'], c['attack']['p90'], c['range'], c['bullets'],
            c['bp_earned'], c['bp_spent'], c['bp_attack'], c['bp_pending'], c['tools'], 100 * c['strong']['2Cmd'], 100 * c['strong']['AttackAll']))
    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=40); ap.add_argument('--workers', type=int, default=6)
    a = ap.parse_args()
    tt = tasks(a.n)
    tags = [t.pop('_tag') for t in tt]
    recs = P.run_many(tt, a.workers)
    for r, tag in zip(recs, tags): r['_tag'] = tag
    s = dict(n=a.n, cells=summarize(recs), logged=LOGGED, econ=ECON)
    with open(os.path.join(ROOT, 'findings', 'data', STEM + '.json'), 'w', encoding='utf-8') as fh: json.dump(s, fh, indent=1)
    with open(os.path.join(ROOT, 'findings', STEM + '.md'), 'w', encoding='utf-8') as fh: fh.write(report(s))
    print(len(recs), 'runs')


if __name__ == '__main__':
    main()
