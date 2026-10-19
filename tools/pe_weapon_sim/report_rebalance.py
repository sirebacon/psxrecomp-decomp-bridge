"""Three-way rebalance summary (vanilla / current mod / proposal) from compare_rules runs.

python -m pe_weapon_sim.report_rebalance OUT.json
Reads the calibrated comparison runs of 2026-10-19 (vanilla -> current, current -> proposal with
Attack All at 30% / 40%, frozen builds) and writes one JSON with, per assumption set, stage, class
and encounter type (ordinary / boss): win rate, time, damage taken, reloads under each ruleset.
Both runs share builds, battles and seeds, so 'current' is the same simulation in each.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / 'findings/data'
RUNS = dict(vc='pe-compare-cal-vanilla-current-2026-10-19', p30='pe-compare-cal-current-P30-2026-10-19',
            p40='pe-compare-cal-current-P40-2026-10-19', fvc='pe-compare-cal-frozen-vanilla-current-2026-10-19',
            fp30='pe-compare-cal-frozen-current-P30-2026-10-19')
METRICS = ('won', 'time', 'damage_taken', 'reloads', 'death', 'status_total')


def load(stem):
    p = ROOT / (stem + '.json')
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None


def cells(run):
    out = {}
    for k, c in run['summary']['table'].items():
        s, ph, g = k.split('|')
        if '/' not in g: continue
        grp, enc = g.split('/')
        out[(s, ph, grp, enc)] = dict(n=c['n'], **{m: (c[m]['base'], c[m]['prop']) for m in METRICS})
    return out


def main(path):
    runs = {k: load(v) for k, v in RUNS.items()}
    rows = []
    for kind, (vc, p30, p40) in (('class', ('vc', 'p30', 'p40')), ('frozen', ('fvc', 'fp30', None))):
        if not runs.get(vc): continue
        a, b = cells(runs[vc]), cells(runs[p30]) if runs.get(p30) else {}
        c = cells(runs[p40]) if p40 and runs.get(p40) else {}
        for key, va in a.items():
            s, ph, grp, enc = key
            row = dict(builds=kind, assumption=s, stage=ph, group=grp, enc=enc, n=va['n'])
            for m in METRICS:
                row[m] = dict(vanilla=va[m][0], current=va[m][1],
                              p30=b.get(key, {}).get(m, (None, None))[1], p40=c.get(key, {}).get(m, (None, None))[1],
                              current_check=b.get(key, {}).get(m, (None, None))[0])
            rows.append(row)
    guns = {}
    vc = runs.get('vc')
    if vc:
        from .run_benchmark import W, CLASS_GUNS
        for ph, key in (('D5', 'Day5'), ('Disc2', 'Wayne')):
            for cls, wid in CLASS_GUNS[key].items(): guns['%s|class_%s' % (ph, cls)] = W[wid].name
    meta = {k: dict(stages=r['stages'], seeds=r['seeds'], assumptions=list(r['assumptions']), builds=r['builds'],
                    proposal=r['proposal'], base=r.get('base')) for k, r in runs.items() if r}
    Path(path).write_text(json.dumps(dict(meta=meta, guns=guns, rows=rows), indent=1), encoding='utf-8')
    print(len(rows), 'rows')


if __name__ == '__main__':
    main(sys.argv[1])
