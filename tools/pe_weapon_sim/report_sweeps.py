"""Tabulate the 2026-10-19 strength sweeps (compare_rules runs pe-sweep-*).

python -m pe_weapon_sim.report_sweeps
Per stage, investment level, assumption set and class: the current mod's mean time / damage / win
for ordinary and boss fights, and each swept strength's value. Writes findings/data/pe-sweeps-2026-10-19.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / 'findings/data'
D5 = {'+35/+15': 'g35m15', '+40/+20': 'g40m20', '+45/+25': 'g45m25'}
D2 = {'35%': 'aa35', '40%': 'aa40', '45%': 'aa45'}


def load(stem):
    p = ROOT / (stem + '-2026-10-19.json')
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None


def main():
    out = []
    for stage, variants, prefix in (('D5', D5, 'pe-sweep-d5'), ('Disc2', D2, 'pe-sweep-d2')):
        for lvl in ('low', 'typical', 'high'):
            runs = {lab: load('%s-%s-%s' % (prefix, lvl, tag)) for lab, tag in variants.items()}
            base_run = next((r for r in runs.values() if r), None)
            if not base_run: continue
            for k, c in base_run['summary']['table'].items():
                s, ph, g = k.split('|')
                if '/' not in g: continue
                grp, enc = g.split('/')
                row = dict(stage=stage, invest=lvl, assumption=s, cls=grp.replace('class_', ''), enc=enc, n=c['n'],
                           current={m: c[m]['base'] for m in ('won', 'time', 'damage_taken')})
                for lab, r in runs.items():
                    if r and k in r['summary']['table']:
                        cc = r['summary']['table'][k]
                        row[lab] = {m: cc[m]['prop'] for m in ('won', 'time', 'damage_taken')}
                out.append(row)
    (ROOT / 'pe-sweeps-2026-10-19.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
    return out


if __name__ == '__main__':
    rows = main()
    for r in rows:
        if r['assumption'] != 'logged_player_serial' or r['enc'] != 'ord': continue
        labs = [k for k in r if k.startswith('+') or k.endswith('%')]
        print(r['stage'], r['invest'], r['cls'], 'cur %.1fs %.1fdmg' % (r['current']['time'], r['current']['damage_taken']),
              ' | '.join('%s %.1fs %.1f' % (l, r[l]['time'], r[l]['damage_taken']) for l in labs))
