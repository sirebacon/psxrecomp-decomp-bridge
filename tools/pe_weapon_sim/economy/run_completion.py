"""Corrected Phase 3 experiments; python -m pe_weapon_sim.economy.run_completion."""
import argparse
import hashlib
import json
import multiprocessing as mp
import os
import time
from . import run_phase3 as P, playthrough as PT, policies as PO, surrogate as SG, evaluation as EV

OUT = os.path.join(P.OUT_DIR, 'pe-weapon-p3-completion-2026-10-17.json')


class ObservedPolicy(PO.Policy):
    def maintain(self, run, at_wayne):
        super().maintain(run, at_wayne)
        if not hasattr(run, 'routes'):
            run.routes = {}
        # Observe owned live M10B only; no hypothetical or retroactive upgrades.
        for item in run.items.values():
            if item.iid != P.M10B or not item.alive:
                continue
            for threshold in (0, 8, 12, 16):
                key = 'acquired' if threshold == 0 else 'mag' + str(threshold)
                if item.magazine() >= threshold and key not in run.routes:
                    run.routes[key] = dict(phase=run.phase, battle=run.battle_no,
                        magazine=item.magazine(), equipped=item.uid == run.main,
                        bonus=list(item.bonus), origins=[item.origin_totals(i) for i in range(3)],
                        bp_spent=dict(run.ledger.spent), tools_spent=dict(run.m['tools_spent']),
                        junk_spent=dict(run.m['junk_spent']))


def one(task):
    SG.TIMING = task['timing']
    pol = P.policy_from(task['policy'])
    pol.__class__ = ObservedPolicy
    run = PT.play(P.econ_from(task['econ']), pol, task['profile'], task['seed'], P._camp(), check=True)
    rec = dict(seed=task['seed'], cps={p: P.compact(s) for p, s in run.checkpoints.items()},
               m=run.checkpoints['Disc2']['metrics'], bench={}, routes=run.routes)
    if task['bench']:
        crules = PT.combat_rules(task.get('bench_rules', 'current'))
        for phase in ('D5', 'Disc2'):
            s = run.checkpoints[phase]
            rec['bench'][phase] = P.slim(EV.benchmark(crules, s['_gun'].cfg(), s['_aya'], phase,
                armor=EV.armor_of(s['_armor']), n=10, timing=task['timing']))
            if task.get('close'):
                rec['bench'][phase + '_close'] = P.slim(EV.benchmark(crules, s['_gun'].cfg(), s['_aya'], phase,
                    armor=EV.armor_of(s['_armor']), n=10, timing=task['timing'], policy='close_in'))
            if s['_second']:
                rec['bench'][phase + '_second'] = P.slim(EV.benchmark(crules, s['_second'].cfg(), s['_aya'], phase,
                    armor=EV.armor_of(s['_armor']), n=10, timing=task['timing']))
    return rec


def main():
    ap = argparse.ArgumentParser(__doc__)
    ap.add_argument('--n', type=int, default=100)
    ap.add_argument('--bench', type=int, default=40)
    ap.add_argument('--workers', type=int, default=4)
    a = ap.parse_args()
    if not 2 <= a.bench <= a.n:
        ap.error('require 2 <= bench <= n')
    start = time.time()
    specs = {}
    for timing in ('overlap', 'serial'):
        for pol in ('A', 'C', 'G', 'H', 'I', 'D', 'S_def', 'S_save', 'S_wpn'):
            specs[timing + '|' + pol] = dict(policy=(pol, None), timing=timing)
        # Common optimizer decisions, changing only the class preference.
        for kind in ('handgun', 'shotgun', 'machine', 'rifle', 'grenade'):
            base = PO.policy_set()['C']
            over = dict(base.__dict__)
            over.pop('name'); over.pop('label'); over.pop('fav_kind')
            specs[timing + '|controlled_' + kind] = dict(policy=('B_' + kind, over), timing=timing)
        for profile in ('minimal', 'completionist', 'farmer'):
            specs[timing + '|C_' + profile] = dict(policy=('C', None), timing=timing, profile=profile)
        for variant, econ, over, bench_rules in (
            ('S0', 'current', P.NO_BULLETS, 'current'),
            ('S1', 'current', None, 'current'),
            ('S2', 'current', None, 'exp:C1s_40'),
            ('S3', 'cur:base_delta={"0x6E":[0,0,1]}', P.NO_BULLETS, 'current'),
            ('S4', 'cur:base_delta={"0x6E":[0,0,1]}', None, 'exp:C1s_40')):
            specs[timing + '|' + variant] = dict(policy=('B_shotgun', over), timing=timing,
                econ=econ, bench_rules=bench_rules, close=True)
    # Resource ablations use the corrected checkpoint implementation.
    for code in ('A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7'):
        specs['overlap|' + code] = dict(policy=('C', None), timing='overlap', econ='abl:' + code)
    raw, groups = {}, {}
    for key, spec in specs.items():
        tasks = [dict(econ='current', profile='typical', **{k:v for k,v in spec.items() if k not in ('econ','profile')},
                      seed=s, bench=s <= a.bench) for s in range(1, a.n + 1)]
        for t in tasks:
            t['econ'] = spec.get('econ', 'current'); t['profile'] = spec.get('profile', 'typical')
        with mp.Pool(a.workers) as pool:
            recs = pool.map(one, tasks, chunksize=4)
        raw[key] = recs
        groups[key] = dict(summary=P.summarize_group(recs), prob=P.probabilities(recs))
        print(key, round(time.time()-start, 1), 'seconds', flush=True)
    paired = {}
    for timing in ('overlap', 'serial'):
        for key in [k for k in raw if k.startswith(timing + '|') and k != timing + '|C']:
            base = raw[timing + '|S1'] if key.split('|')[1] in ('S0','S2','S3','S4') else raw[timing + '|C']
            for phase in ('D5', 'Disc2'):
                ds = [r['bench'][phase]['suite_time'] - b['bench'][phase]['suite_time']
                      for r,b in zip(raw[key], base) if phase in r['bench']]
                paired[key + '|' + phase] = P.stats(ds)
    source_hashes = {}
    for name in ('playthrough.py','surrogate.py','evaluation.py','policies.py','run_completion.py'):
        with open(os.path.join(P.HERE,name),'rb') as f:
            source_hashes[name] = hashlib.sha256(f.read()).hexdigest()
    res = dict(meta=dict(n=a.n, bench=a.bench, workers=a.workers, seconds=round(time.time()-start,2),
        source_sha256=source_hashes, specs=specs,
        caveat='S2/S4 proximity is checkpoint-only; campaign feedback remains CURRENT. Profiles are assumptions from one logged run.'),
        groups=groups, paired=paired, raw=raw, validation=P.part_validation())
    with open(OUT,'w',encoding='utf-8') as f:
        json.dump(res,f,indent=1)
    print('wrote',OUT,flush=True)


if __name__ == '__main__':
    main()
