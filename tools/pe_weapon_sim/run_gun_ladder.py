"""Gun ladder: every gun available at a stage, equal (typical) investment, rebalanced rules.

Runs compare_rules' class benchmark with run_benchmark.CLASS_GUNS replaced by every gun the player
can hold at that stage (fixed pickups from the gear-location table, Wayne's crafts from Day 5), so
lesser / in-between guns can be compared with their neighbours. Writes
findings/data/pe-gun-ladder-<stage>.json via compare_rules and a summary table
findings/pe-gun-ladder-2026-10-20.md.

    PYTHONPATH=tools python -m pe_weapon_sim.run_gun_ladder [--seeds 3] [--fights 4] [--stages D2-4 D5 Disc2]
"""
import argparse, json, statistics
from pathlib import Path

from . import run_benchmark as RB
from . import compare_rules as CR
from .economy.tables import GEAR_LOCATIONS, ITEMS, WAYNE_GUNS

ROOT = Path(__file__).resolve().parents[2]
PROPOSAL = 'exp:AAc_75+RoFE|cfg:@G3A3.power+45,@M203_4.power+15'
KINDS = {1: 'handgun', 2: 'shotgun', 3: 'machine', 4: 'rifle', 5: 'grenade', 6: 'rocket'}
ORDER = {'D1': 0, 'D2-4': 1, 'D5': 2, 'Disc2': 3}


def first_seen():
    first = {}
    for iid, ph, area in GEAR_LOCATIONS:
        if 1 <= ITEMS[iid]['kind'] <= 6 and (iid not in first or ORDER[ph] < ORDER[first[iid][0]]):
            first[iid] = (ph, area)
    for w in WAYNE_GUNS: first.setdefault(w, ('D5', 'Wayne'))
    return first


def pool(stage, first):
    """Guns holdable at a stage: D2-4 = Day 1-4 pickups; D5 (museum era) and Disc2 = everything
    from the main game, Wayne's guns included."""
    limit = 1 if stage == 'D2-4' else 3
    return {iid: v for iid, v in first.items() if ORDER[v[0]] <= limit and iid in RB.W}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', type=int, default=3); ap.add_argument('--fights', type=int, default=4)
    ap.add_argument('--stages', nargs='+', default=['D2-4', 'D5', 'Disc2'])
    ap.add_argument('--extra', default='')            # more cfg terms, e.g. @M16A1.power+25
    ap.add_argument('--only', nargs='*')               # gun names to run (default: all)
    ap.add_argument('--tag', default='2026-10-20')
    a = ap.parse_args(argv)
    first = first_seen()
    rows = []
    for stage in a.stages:
        guns = pool(stage, first)
        names = {'g%02X' % iid: iid for iid in guns if not a.only or ITEMS[iid]['name'] in a.only}
        key = 'Day4' if stage == 'D2-4' else 'Day5' if stage == 'D5' else 'Wayne'
        RB.CLASS_GUNS[key] = dict(names); RB.CLASS_GUNS['WayneRocket'] = {}
        stem = 'pe-gun-ladder-%s-%s' % (a.tag, stage)
        CR.main(['--builds', 'classlog', '--calibrated', '--invest', 'typical', '--base', 'current', '--proposal', PROPOSAL + (',' + a.extra if a.extra else ''),
                 '--stages', stage, '--seeds', str(a.seeds), '--fights', str(a.fights), '--assumptions', 'default',
                 '--classes', *names, '--out', stem])
        t = json.loads((ROOT / 'findings/data' / (stem + '.json')).read_text())['summary']['table']
        for n, iid in names.items():
            o = t.get('default|%s|class_%s/ord' % (stage, n)); b = t.get('default|%s|class_%s/boss' % (stage, n))
            r = ITEMS[iid]
            rows.append(dict(stage=stage, gun=r['name'], id=iid, kind=KINDS[r['kind']], found=first[iid][0], where=first[iid][1],
                             base=r['base'], ord=o['time']['prop'] if o else None, ord_win=o['won']['prop'] if o else None,
                             boss=b['time']['prop'] if b else None, boss_win=b['won']['prop'] if b else None))
    (ROOT / ('findings/data/pe-gun-ladder-%s.json' % a.tag)).write_text(json.dumps(rows, indent=1), encoding='utf-8')
    L = ['# Gun ladder (rebalanced rules, typical investment), October 20, 2026', '',
         'Every gun the player can hold at each stage, same investment (`compare_rules` INVEST typical; Disc2 with',
         '2 Commands + Quickdraw), calibrated model, %d seeds x %d fights. Ordinary = mean fight time of ordinary' % (a.seeds, a.fights),
         'battles; x median = the gun against the stage median. Produced by `run_gun_ladder`.', '']
    for stage in a.stages:
        rs = sorted([r for r in rows if r['stage'] == stage and r['ord']], key=lambda r: r['ord'])
        if not rs: continue
        med = statistics.median(r['ord'] for r in rs)
        L += ['## %s (median %.1f s)' % (stage, med), '',
              '| Gun | Kind | Found | Base atk / range / bullets | Ordinary s | x median | Boss s | Boss wins |', '|---|---|---|---|---:|---:|---:|---:|']
        for r in rs:
            L.append('| %s | %s | %s (%s) | %s | %.1f | %.2f | %s | %s |' % (r['gun'], r['kind'], r['found'], r['where'], '/'.join(map(str, r['base'])),
                     r['ord'], r['ord'] / med, '%.1f' % r['boss'] if r['boss'] else '-', '%.2f' % r['boss_win'] if r['boss_win'] is not None else '-'))
        L.append('')
    (ROOT / ('findings/pe-gun-ladder-%s.md' % a.tag)).write_text('\n'.join(L), encoding='utf-8')
    print('done', len(rows))


if __name__ == '__main__':
    main()

