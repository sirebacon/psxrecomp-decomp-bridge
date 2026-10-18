"""Checkpoint mod ablations, tick-rate sensitivity, and two-weapon screening.

python -m pe_weapon_sim.economy.run_followups --n 40
No game files or historical simulation results are modified.
"""
import argparse
import copy
import hashlib
import json
import math
import os
import time
from .. import engine as E, rules as CR
from . import run_phase3 as P, playthrough as PT, surrogate as SG, policies as PO, evaluation as EV

OUT = os.path.join(P.OUT_DIR, 'pe-weapon-p3-followups-2026-10-17.json')


def remove_effects(cfg, variant):
    cfg = copy.deepcopy(cfg)
    if variant in ('no_commands', 'neither'):
        cfg['eff']['commands'] = 1
    if variant in ('no_quickdraw', 'neither'):
        cfg['eff'].pop('quickdraw', None)
    return cfg


def envelope(primary, secondary, switch_seconds=0):
    """Optimistic per-encounter selection, with a scalar switching-delay screen.

    Not a within-fight switch simulation; no carried state between candidates.
    """
    main = [primary[e]['time_mean'] for e in EV.SCORE_SET]
    choice = [min(primary[e]['time_mean'], secondary[e]['time_mean'] + switch_seconds) for e in EV.SCORE_SET]
    return dict(main=math.exp(sum(math.log(max(.1,x)) for x in main)/len(main)),
                envelope=math.exp(sum(math.log(max(.1,x)) for x in choice)/len(choice)),
                secondary_faster=[e for e in EV.SCORE_SET if secondary[e]['time_mean'] + switch_seconds < primary[e]['time_mean']],
                # Win rates accompany times; never treat a fast loss as a useful option.
                wins={e:[primary[e]['win'],secondary[e]['win']] for e in EV.SCORE_SET})


def main():
    ap = argparse.ArgumentParser(__doc__)
    ap.add_argument('--n',type=int,default=40)
    a=ap.parse_args()
    if a.n < 2: ap.error('n must be at least 2')
    t0=time.time(); raw={}; summary={}; portfolios=[]; rates=[]
    old_tick,old_timing=E.TICK_HZ,SG.TIMING
    try:
        for timing in ('overlap','serial'):
            SG.TIMING=timing
            for label in ('C','G','controlled_shotgun','D'):
                key=timing+'|'+label; recs=[]
                for seed in range(1,a.n+1):
                    if label=='controlled_shotgun':
                        pol=PO.policy_set()['C'].copy('controlled_shotgun',fav_kind=2)
                    else: pol=PO.policy_set()[label]
                    run=PT.play(P.econ_from('current'),pol,'typical',seed,P._camp(),check=True)
                    rec=dict(seed=seed, checkpoints={})
                    for phase in ('D5','Disc2'):
                        s=run.checkpoints[phase]; cfg=s['_gun'].cfg(); armor=EV.armor_of(s['_armor'])
                        variants={}
                        for v in ('baseline','no_commands','no_quickdraw','neither'):
                            b=EV.benchmark(CR.CURRENT,remove_effects(cfg,v),s['_aya'],phase,armor=armor,n=20,timing=timing)
                            variants[v]=P.slim(b)
                        rec['checkpoints'][phase]=dict(gun=s['gun'],mods=s['mods'],variants=variants,
                            commands=cfg['eff'].get('commands',1),quickdraw=bool(cfg['eff'].get('quickdraw')))
                        if phase=='Disc2':
                            # Freeze earned equipment/Aya; only alter the time conversion in combat.
                            for hz in (59.9,94.0):
                                E.TICK_HZ=hz; EV._CACHE.clear()
                                b=EV.benchmark(CR.CURRENT,cfg,s['_aya'],phase,armor=armor,n=20,timing=timing)
                                rates.append(dict(group=key,seed=seed,tick_hz=hz,suite=b['suite_time']))
                            E.TICK_HZ=old_tick; EV._CACHE.clear()
                        if label=='D' and s['_second'] is not None:
                            main=EV.benchmark(CR.CURRENT,cfg,s['_aya'],phase,armor=armor,n=20,timing=timing)
                            second=EV.benchmark(CR.CURRENT,s['_second'].cfg(),s['_aya'],phase,armor=armor,n=20,timing=timing)
                            delay=.5*E.fill_seconds(s['_aya']['stat22'],s['_second'].kind)
                            portfolios.append(dict(group=key,seed=seed,phase=phase,main=s['gun'],
                                second=s['_second'].name,half_fill_delay=delay,
                                free=envelope(main,second),charged=envelope(main,second,delay)))
                    recs.append(rec)
                raw[key]=recs
                summary[key]={}
                for phase in ('D5','Disc2'):
                    cps=[r['checkpoints'][phase] for r in recs]
                    summary[key][phase]=dict(
                        commands_present=sum(c['commands']>1 for c in cps),
                        quickdraw_present=sum(c['quickdraw'] for c in cps),
                        baseline=P.stats([c['variants']['baseline']['suite_time'] for c in cps]),
                        delta={v:P.stats([c['variants'][v]['suite_time']-c['variants']['baseline']['suite_time'] for c in cps])
                               for v in ('no_commands','no_quickdraw','neither')})
                print(key,round(time.time()-t0,1),'seconds',flush=True)
    finally:
        E.TICK_HZ=old_tick; SG.TIMING=old_timing; EV._CACHE.clear()
    hashes={}
    for name in ('run_followups.py','policies.py','playthrough.py','evaluation.py','surrogate.py'):
        with open(os.path.join(P.HERE,name),'rb') as f: hashes[name]=hashlib.sha256(f.read()).hexdigest()
    with open(OUT,'w',encoding='utf-8') as f:
        json.dump(dict(meta=dict(n=a.n,fights=20,seconds=round(time.time()-t0,2),source_sha256=hashes,
            caveats=['Mod removal leaves slots empty; no reinvestment or campaign adaptation.',
                     'Tick-rate alternatives freeze progression; 59.9Hz is a sensitivity case, not a verified gauge tick rate.',
                     'Portfolio envelope uses foreknowledge and scalar delay; not a dynamic switching simulation.']),
            summary=summary,raw=raw,portfolios=portfolios,tick_rates=rates),f,indent=1)
    print('wrote',OUT,flush=True)


if __name__=='__main__': main()
