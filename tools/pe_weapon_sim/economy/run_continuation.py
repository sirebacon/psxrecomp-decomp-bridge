"""Independent, auditable continuation; leaves original Phase 3 outputs intact.

Run from tools: python -m pe_weapon_sim.economy.run_continuation --n 80 --bench 40 --workers 4
"""
import argparse
import hashlib
import json
import os
import time
from . import run_phase3 as P


def main():
    ap = argparse.ArgumentParser(__doc__)
    ap.add_argument('--n', type=int, default=80)
    ap.add_argument('--bench', type=int, default=40)
    ap.add_argument('--workers', type=int, default=4)
    a = ap.parse_args()
    if not 2 <= a.bench <= a.n:
        ap.error('require 2 <= bench <= n')
    started = time.time()
    groups, raw = {}, {}
    for timing in ('overlap', 'serial'):
        for pol in ('C', 'G', 'B_shotgun'):
            key = timing + '|' + pol
            tasks = P.tasks_for('current', (pol, None), 'typical', a.n, a.bench,
                                sg_timing=timing, timing=timing,
                                bench_phases=('D5', 'Disc2'))
            records = P.run_many(tasks, a.workers)
            groups[key] = dict(summary=P.summarize_group(records), prob=P.probabilities(records))
            raw[key] = records
            print(key, round(time.time() - started, 1), 'seconds', flush=True)
    paired = {}
    for timing in ('overlap', 'serial'):
        for other in ('G', 'B_shotgun'):
            left = {r['seed']: r for r in raw[timing + '|C']}
            right = {r['seed']: r for r in raw[timing + '|' + other]}
            for phase in ('D5', 'Disc2'):
                deltas = [right[s]['bench'][phase]['suite_time'] - left[s]['bench'][phase]['suite_time']
                          for s in sorted(left) if phase in left[s]['bench'] and phase in right[s]['bench']]
                paired[timing + '|' + other + '-C|' + phase] = P.stats(deltas)
    sources = {}
    for name in ('surrogate.py', 'run_phase3.py', 'evaluation.py', 'run_continuation.py'):
        with open(os.path.join(P.HERE, name), 'rb') as f:
            sources[name] = hashlib.sha256(f.read()).hexdigest()
    result = dict(meta=dict(n=a.n, bench=a.bench, workers=a.workers, seeds=[1, a.n],
                            fights_per_encounter=10, seconds=round(time.time()-started, 2),
                            source_sha256=sources,
                            note='Timing cache correction; original Phase 3 results preserved. CIs use existing normal approximation.'),
                  groups=groups, paired_time_delta_seconds=paired, raw=raw)
    path = os.path.join(P.OUT_DIR, 'pe-weapon-p3-continuation-2026-10-17.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=1)
    print('wrote', path, flush=True)


if __name__ == '__main__':
    main()
