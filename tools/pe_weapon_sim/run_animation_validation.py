"""Generate durations and a controlled benchmark without running the game."""
import json
from pathlib import Path
from . import data, engine, rules
from .decomp_animation import queued_shot_timeline, source_rules
from .economy import evaluation


def main():
    root=Path(__file__).resolve().parents[2]/'findings'
    profile=source_rules(rules.CURRENT)
    rows=[]
    for costume in (0,1):
        for kind in range(1,9):
            for shots in (1,3,5,10):
                r=queued_shot_timeline(kind,shots,costume=costume)
                r['seconds']=r['update_calls']/(59.9/2)
                rows.append(r)
    benchmarks=[]
    # Same synthetic equipment power/range/magazine and matched seeds, isolating
    # timing model. Not an economy replay or an earned-loadout weapon ranking.
    for kind in range(1,8):
        cfg=dict(kind=kind,power=100,range=1500,magazine=30,eff=dict(rof=3,commands=1))
        aya=dict(level=30,stat22=79,offense=100)
        for label,r in (('legacy',rules.CURRENT),('asset_queue',profile)):
            b=evaluation.benchmark(r,cfg,aya,'Disc2',n=8,timing='overlap')
            benchmarks.append(dict(kind=kind,model=label,suite_time=b['suite_time'],results=b))
    out=dict(profile=profile,durations=rows,benchmarks=benchmarks,
        caveats=['nominal NTSC no-stall update rate', 'ordinary queued shots only',
            'engine still aggregates volley damage at turn time', 'reload seconds remain assumed',
            'no interruptions, target deaths or asynchronous effect waits in animation kernel'])
    (root/'data/pe-animation-validation-2026-10-18.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    lines=['# Extracted animation durations — 2026-10-18','','Ordinary uninterrupted queued shots; bank0, nominal59.9/2 updates/s.',
        'Counts include the initial battle call; reload and input time excluded.','',
        '| Class | Aim frames | Fire frames | 1 shot updates / seconds | 3 shot updates / seconds |',
        '|---|---:|---:|---:|---:|']
    for kind in range(1,9):
        one=queued_shot_timeline(kind,1);three=queued_shot_timeline(kind,3)
        lines.append(f"| {data.KIND[kind]} | {one['aim_frames']} | {one['follow_frames']} | {one['update_calls']} / {one['update_calls']/(59.9/2):.3f} | {three['update_calls']} / {three['update_calls']/(59.9/2):.3f} |")
    lines += ['', 'Synthetic frozen-equipment overlap benchmark, 8 matched seeds per encounter:', '',
        '| Class | Legacy suite score | Asset-queue profile suite score |','|---|---:|---:|']
    for kind in range(1,8):
        pair=[r for r in benchmarks if r['kind']==kind]
        lines.append(f"| {data.KIND[kind]} | {pair[0]['suite_time']:.3f} | {pair[1]['suite_time']:.3f} |")
    lines += ['', 'The benchmark changes both gauge clock/arithmetic and animation timing; it does not',
        'isolate animation-only effects. Suite scores include a 60-second penalty for encounters',
        'with any losses; inspect raw win rates before interpreting them as clear times. It does not',
        'establish policy rankings. The two costumes differ',
        'in grenade/club aiming length. Burst/Random/AttackAll are explicitly rejected by this',
        'profile until their alternate queue branches are reconstructed. Historical defaults',
        'remain available; use decomp_animation.source_rules for this experimental profile.']
    (root/'pe-animation-durations-2026-10-18.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Wrote 64 duration cases and 14 controlled benchmark groups.')


if __name__=='__main__': main()
