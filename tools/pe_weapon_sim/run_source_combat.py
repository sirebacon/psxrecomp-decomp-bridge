"""Offline encounter benchmarks for the integrated source action backend."""
import json
from pathlib import Path
import random
from . import rules
from .decomp_animation import source_combat_rules
from .economy import evaluation
from .run_benchmark import summarize


def cfg(kind=1,mode=None,rof=3):
    return dict(kind=kind,power=100,range=1500,magazine=5,
        eff=dict(rof=rof,**({'mode':mode} if mode else {})))


def run():
    root=Path(__file__).resolve().parents[2]/'findings'
    profile=source_combat_rules(rules.CURRENT)
    aya=dict(level=30,stat22=79,offense=100)
    results=[];switches=[];count=0
    encounters=('close_normal','groups','keepaway_boss','endurance')
    for kind in range(1,8):
        for mode in (None,'random','burst','all'):
            for encounter in encounters:
                fights=evaluation.run_enc(profile,cfg(kind,mode),aya,encounter,'Disc2',8,
                    source_options=dict(hp=300,reserve_ammo={0:120,1:120,2:120}),time_cap=60)
                assert all(f['ammo_balance']==0 for f in fights)
                results.append(dict(kind=kind,mode=mode,encounter=encounter,summary=summarize(fights)))
                count+=len(fights)
    for strategy in ('primary_only','alternate','distance'):
        for stream in (0,20):
            def choose(state):
                if strategy=='alternate': return 'rifle' if state['turns']%2 else 'primary'
                live=[f for f in state['foes'] if f['cur']>0]
                if strategy=='distance' and live and min(f['dist'] for f in live)>1100: return 'rifle'
                return 'primary'
            fights=evaluation.run_enc(profile,dict(cfg(1),range=1100),aya,'medium_mobile','Disc2',8,
                source_options=dict(hp=300,reserve_ammo={0:120},weapons={'rifle':dict(cfg(4),range=1800)},
                    weapon_policy=choose,menu_updates=6,stream_updates=stream),time_cap=60)
            assert all(f['ammo_balance']==0 for f in fights)
            switches.append(dict(strategy=strategy,stream_updates=stream,summary=summarize(fights),
                total_switches=sum(f.get('switches',0) for f in fights)))
            count+=len(fights)
    raw=dict(profile=profile,fights=count,encounters=results,switching=switches,
        scope='synthetic frozen equipment; modeled enemy AI/status behavior, not retail battle parity')
    (root/'data/pe-source-combat-2026-10-18.json').write_text(json.dumps(raw,indent=2),encoding='utf-8')
    lines=['# Integrated source combat validation — 2026-10-18','',
        f'{count} encounter benchmark calls completed offline. Every result passed ammo conservation.',
        'Endurance calls contain three linked combat segments carrying ammo, gauge and HP.',
        'Synthetic equipment: power100, magazine5, RoF3; Aya stat22=79, HP300.',
        'Source player events are combined with the existing modeled enemy periods/movement/statuses.',
        'No campaign-policy ranking or retail parity is claimed.','',
        'Representative handgun group encounters (8 matched seeds each):','',
        '| Mode | Win fraction | Mean seconds | Mean damage dealt |','|---|---:|---:|---:|']
    for r in results:
        if r['kind']==1 and r['encounter']=='groups':
            s=r['summary'];lines.append(f"| {r['mode'] or 'ordinary'} | {s['win']:.3f} | {s['time_mean']:.3f} | {s.get('damage',0):.1f} |")
    lines+=['','Two-gun medium-mobile scenarios (8 matched seeds each):','',
        '| Policy | Stream wait per switch | Win fraction | Mean seconds | Switches across seeds |',
        '|---|---:|---:|---:|---:|']
    for r in switches:
        s=r['summary'];lines.append(f"| {r['strategy']} | {r['stream_updates']} | {s['win']:.3f} | {s['time_mean']:.3f} | {r['total_switches']} |")
    lines+=['','Times include losses/timeouts: compare win fractions first. Defaults for unspecified enemy',
        'angles are seeded uniform headings; burst occupancy is therefore a geometric scenario assumption.',
        'Switch policies are simple controlled experiments, not optimized strategies. See the integration',
        'notes and raw results for status assumptions, explicit resource budgets and unsupported features.']
    (root/'pe-source-combat-validation-2026-10-18.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'Validated {count} encounter calls (including linked endurance segments).')


if __name__=='__main__': run()
