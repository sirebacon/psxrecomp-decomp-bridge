"""Data for the rebalance report page (findings/reports/pe-weapon-rebalance-2026-10-19.html), matching
findings/pe-rebalance-economy-basis.md.

python -m pe_weapon_sim.report_basis OUT.json
- classes: per stage (D2-4, D5, Disc2), investment level and class (incl. catalog Attack All and the
  LAW80), ordinary / boss: vanilla, current mod and the final proposal (AAc_75 + RoFE + G3A3 +45 +
  M203 4 +15). Vanilla -> current and current -> proposal runs share battles, builds and seeds.
- ra_variants: the Attack All rules tried, typical investment.
- mods: single-mod values (vanilla, current, current + R-E).
- pe: the Parasite Energy study.
"""
import json, statistics, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / 'findings/data'
STAGES = {'D2-4': 'd24', 'D5': 'd5', 'Disc2': 'd2'}
METRICS = ('won', 'time', 'damage_taken', 'reloads')
SET = 'logged_player_serial'


def load(stem):
    p = ROOT / (stem + '-2026-10-19.json')
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None


def cells(run, side):
    out = {}
    for k, c in run['summary']['table'].items():
        s, ph, g = k.split('|')
        if s != SET or '/' not in g: continue
        grp, enc = g.split('/')
        out[(grp.replace('class_', ''), enc)] = dict(n=c['n'], **{m: c[m][side] for m in METRICS})
    return out


def classes():
    rows = []
    for stage, tag in STAGES.items():
        for lvl in ('low', 'typical', 'high'):
            fin = load('pe-final-%s-%s' % (tag, lvl))
            van = load('pe-final-%s-%s-vanilla' % (tag, lvl)) or (load('pe-final-d24-vanilla-current') if stage == 'D2-4' and lvl == 'typical' else None)
            if not fin: continue
            cur, prop = cells(fin, 'base'), cells(fin, 'prop')
            vv = cells(van, 'base') if van else {}
            for key in cur:
                rows.append(dict(stage=stage, invest=lvl, cls=key[0], enc=key[1], n=cur[key]['n'],
                                 **{m: dict(vanilla=vv.get(key, {}).get(m), current=cur[key][m], proposal=prop[key][m]) for m in METRICS}))
    return rows


def ra_variants():
    """Ordinary-fight time / damage of the Attack All rules tried (typical investment)."""
    spec = {'D5': [('Power cut 40% (old R-A)', 'pe-sweep-ra2-typical-aa40'), ('After-defense 40%', 'pe-sweep-aad-d5-typical-40'),
                   ('After-defense 60%', 'pe-sweep-aad-d5-typical-60'), ('Crowd-scaled (c 2.0)', 'pe-sweep-aan-d5-typical-20'),
                   ('HP cap 60%', 'pe-sweep-aac_60-d5-typical'), ('HP cap 75% (R-A)', 'pe-sweep-aac_75-d5-typical')],
            'Disc2': [('Power cut 40% (old R-A)', 'pe-sweep-d2-typical-aa40'), ('After-defense 40%', 'pe-sweep-aad-d2-typical-40'),
                      ('After-defense 60%', 'pe-sweep-aad-d2-typical-60'), ('Crowd-scaled (c 2.0)', 'pe-sweep-aan-d2-typical-20'),
                      ('HP cap 60%', 'pe-sweep-aac_60-d2-typical'), ('HP cap 75% (R-A)', 'pe-sweep-aac_75-d2-typical')]}
    out = []
    for stage, items in spec.items():
        for label, stem in items:
            run = load(stem)
            if not run: continue
            cur, prop = cells(run, 'base'), cells(run, 'prop')
            for (cls, enc), c in prop.items():
                if enc != 'ord': continue
                out.append(dict(stage=stage, rule=label, cls=cls, time=c['time'], damage=c['damage_taken'],
                                time_now=cur[(cls, enc)]['time'], damage_now=cur[(cls, enc)]['damage_taken']))
    return out


def mods():
    out = []
    for stage in ('D5', 'Disc2'):
        for tag in ('vanilla', 'current', 'rofe'):
            p = ROOT / ('pe-mod-values-%s-%s-2026-10-19.json' % (stage, tag))
            if not p.exists(): continue
            s = json.loads(p.read_text(encoding='utf-8'))['summary']
            effs = sorted({k.split('|')[2] for k in s})
            for enc in ('ord', 'boss'):
                for e in effs:
                    v = [100 * (c['time'] / c['time_none'] - 1) for k, c in s.items() if k.split('|')[1] == enc and k.split('|')[2] == e]
                    if v: out.append(dict(stage=stage, rules=tag, enc=enc, eff=e, mean=statistics.mean(v), lo=min(v), hi=max(v)))
    return out


def pe():
    out = []
    for label, tag in (('Vanilla PE', 'pev'), ('Heals 10/25/50%', 'peh_10_25_50'), ('Heals 15/30/50%', 'peh_15_30_50'), ('Heals 20/40/65%', 'peh_20_40_65')):
        for stem, stages in (('pe-pestudy-d24-%s' % tag, ('D2-4',)), ('pe-pestudy-d5d2-%s' % tag, ('D5', 'Disc2'))):
            run = load(stem)
            if not run: continue
            for st in stages:
                for enc in (False, True):
                    rr = [r for r in run['rows'] if r['boss'] == enc and r['phase'] == st]
                    if not rr: continue
                    f = lambda m, side: statistics.mean(r[side][m] for r in rr)
                    out.append(dict(variant=label, stage=st, enc='boss' if enc else 'ord', n=len(rr),
                                    time=(f('time', 'base'), f('time', 'prop')), damage=(f('damage_taken', 'base'), f('damage_taken', 'prop')),
                                    deaths=(f('death', 'base'), f('death', 'prop'))))
    return out


def main(path):
    from .run_benchmark import W, CLASS_GUNS
    guns = {}
    for stage, key in (('D2-4', 'Day4'), ('D5', 'Day5'), ('Disc2', 'Wayne')):
        g = dict(CLASS_GUNS[key])
        if stage == 'Disc2': g.update(CLASS_GUNS.get('WayneRocket', {}))
        for cls, wid in g.items(): guns['%s|%s' % (stage, cls)] = W[wid].name
    data = dict(classes=classes(), ra=ra_variants(), mods=mods(), pe=pe(), guns=guns)
    Path(path).write_text(json.dumps(data, separators=(',', ':')), encoding='utf-8')
    print({k: len(v) for k, v in data.items()})


if __name__ == '__main__':
    main(sys.argv[1])
