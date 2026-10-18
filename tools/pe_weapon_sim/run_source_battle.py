"""Offline source-state validation grid; no emulator connection or gameplay."""
from collections import Counter
import json
from pathlib import Path
from .engine import source_sequence
from .source_battle import BattleSession,Gun,ammo_pool


def summary(events):
    counts=Counter(e['event'] for e in events)
    return dict(counts=counts,fire_updates=[e['update'] for e in events if e['event']=='fire'],
        hit_updates=[e['update'] for e in events if e['event']=='hit'])


def main():
    root=Path(__file__).resolve().parents[2]/'findings'
    attacks=[];switches=[]
    for costume in (0,1):
        for kind in range(1,9):
            for mode in (None,'random','burst','all'):
                for label,capacity,loaded,reserve in (('loaded',30,30,0),('reload',2,1,7),('empty',2,0,0)):
                    s=BattleSession({'a':Gun(kind,capacity,loaded)},{ammo_pool(kind):reserve},'a',
                        gauge=9000,costume=costume)
                    r=s.attack(rof=5,mode=mode,targets=(0,1,2),selected=0,
                        target_angles={0:0x800,1:0x400,2:-0x800})
                    counts=summary(r['events'])
                    # Every real gun shot consumes one existing loaded/reserve round.
                    if kind!=8:
                        assert loaded+reserve == s.gun.loaded+sum(s.reserves.values())+counts['counts'].get('fire',0)
                    attacks.append(dict(costume=costume,kind=kind,mode=mode,case=label,
                        capacity=capacity,initial_loaded=loaded,initial_reserve=reserve,**r,**counts))
    for source in range(1,8):
        for dest in range(1,8):
            if source==dest: continue
            for half in (False,True):
                for stream in (0,20):
                    r=source_sequence({'a':Gun(source,10,3),'b':Gun(dest,10,7)},
                        {0:40,1:20,2:20},'a',[
                            dict(op='attack',rof=3),
                            dict(op='switch',destination='b',half_bar=half,stream_updates=stream,menu_updates=6),
                            dict(op='attack',rof=3),
                            dict(op='switch',destination='a',half_bar=half,stream_updates=stream,menu_updates=6),
                            dict(op='attack',rof=3)],gauge=9000)
                    switches.append(dict(source=source,destination=dest,half_bar=half,stream_updates=stream,
                        **r,**summary(r['events'])))
    raw=dict(attacks=attacks,switch_sequences=switches,update_hz=59.9/2,
        scope='deterministic player-action state transitions; no enemy AI or damage-balance ranking')
    (root/'data/pe-source-battle-2026-10-18.json').write_text(json.dumps(raw,indent=2),encoding='utf-8')
    lines=['# Offline reload, firing-mode and switching validation — 2026-10-18','',
        f'{len(attacks)} attack cases and {len(switches)} carried-state switch sequences completed.',
        'Each firearm case asserts conservation of loaded ammo + pooled reserve + rounds fired.',
        'No game process, controller, save load or live scan is used.','',
        'Representative bank0 handgun cases, RoF5, three eligible targets:', '',
        '| Mode | Ammo setup | Updates | Shots | Transfers | Loaded left | Reserve left |',
        '|---|---|---:|---:|---:|---:|---:|']
    for r in attacks:
        if r['costume'] or r['kind']!=1: continue
        lines.append(f"| {r['mode'] or 'ordinary'} | {r['case']} | {r['updates']} | {r['counts'].get('fire',0)} | {r['counts'].get('ammo_transfer',0)} | {r['loaded']} | {sum(r['reserves'].values())} |")
    lines += ['', 'Representative handgun→rifle→handgun sequences (three RoF3 attacks, six menu updates per switch):','',
        '| Gauge cost | Stream wait per switch | Total updates | Nominal seconds | Final loaded a / b |',
        '|---|---:|---:|---:|---|']
    for r in switches:
        if r['source']==1 and r['destination']==4:
            lines.append(f"| {'CURRENT half' if r['half_bar'] else 'retail full'} | {r['stream_updates']} | {r['updates']} | {r['nominal_seconds']:.3f} | {r['loaded']['a']} / {r['loaded']['b']} |")
    lines += ['', 'The all-target partial-magazine path can repeat more than nominal RoF after a reload:',
        'the traced ready branch resets the remaining-shot counter. This literal-source result',
        'is flagged for independent retail validation; do not turn it into a balance recommendation.',
        'Seconds use nominal29.95 updates/s; stream waits are explicit inputs, not predicted disk latency.',
        'See pe-source-battle-derivation-2026-10-18.md for source references and scope.']
    (root/'pe-source-battle-validation-2026-10-18.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'Validated {len(attacks)} attacks and {len(switches)} carried-state sequences.')


if __name__=='__main__': main()
