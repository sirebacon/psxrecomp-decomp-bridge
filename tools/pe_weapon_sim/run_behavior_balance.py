"""Rebenchmark frozen earned loadouts with counter/charge-aware combat, offline.

Does not rerun economy decisions with an uncalibrated surrogate. Enemy charge
values are labeled sensitivity scenarios, not invented per-enemy retail data.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import statistics
from . import rules
from .decomp_animation import source_behavior_rules
from .economy import equipment,tables,evaluation


GROUPS=('C','G','D','controlled_handgun','controlled_shotgun','controlled_machine','controlled_rifle','controlled_grenade')
ENCOUNTERS=('close_normal','groups','keepaway_boss','stationary_boss')


def config(cp):
    iid,bonus,mods=cp['cfg_sig']
    item=equipment.Item(iid,'frozen','Disc2');item.bonus=list(bonus);item.mods=list(mods)
    result=item.cfg()
    assert result['magazine']==cp['magazine']
    return result


def main():
    ap=argparse.ArgumentParser(__doc__);ap.add_argument('--seeds',type=int,default=8)
    ap.add_argument('--fights',type=int,default=6);ap.add_argument('--static-catalog',action='store_true');ap.add_argument('--action-timing',choices=('fast','slow'));ap.add_argument('--projectile-height',type=int,choices=(320,640));a=ap.parse_args()
    if a.projectile_height:a.action_timing='fast'
    if a.action_timing:a.static_catalog=True
    if min(a.seeds,a.fights)<2: ap.error('at least two seeds and fights required')
    root=Path(__file__).resolve().parents[2]/'findings'
    path=root/'data/pe-weapon-p3-completion-2026-10-17.json'
    historical=json.loads(path.read_text());records=[];total=0;matched=0;foe_count=0;timed=0;projectile_matches=0;projectiles=0;contacts=0
    stem='pe-static-script-balance-2026-10-18' if a.static_catalog else 'pe-behavior-balance-2026-10-18'
    if a.action_timing:stem=f'pe-action-{a.action_timing}-balance-2026-10-18'
    if a.projectile_height:stem=f'pe-projectile-h{a.projectile_height}-balance-2026-10-18'
    profile=source_behavior_rules(rules.CURRENT)
    for step in (60,90,120):
        for group in GROUPS:
            for run in historical['raw']['overlap|'+group][:a.seeds]:
                for phase in ('D5','Disc2'):
                    cp=run['cps'][phase];baseline=config(cp)
                    variants={'baseline':baseline}
                    if baseline['eff'].get('quickdraw') and not baseline['eff'].get('counter'):
                        swapped=copy.deepcopy(baseline);swapped['eff'].pop('quickdraw');swapped['eff']['counter']=True
                        variants['counter_for_quickdraw']=swapped
                    aya=dict(level=cp['level'],stat22=cp['stat22'],offense=tables.offense_of(cp['level']),
                             hp_level=cp['level']*10)
                    armor=dict(slow_at='SlowAT' in cp['armor_mods'],
                        attack_levels=cp['armor_mods'].count('AttackUp')-cp['armor_mods'].count('AttackDown'))
                    for variant,cfg in variants.items():
                        encounters={};counters=0;rounds=0
                        for enc in ENCOUNTERS:
                            fights=evaluation.run_enc(profile,cfg,aya,enc,phase,a.fights,seed=run['seed'],armor=armor,
                                source_options=dict(projectile_height=a.projectile_height,enemy_action_timing=a.action_timing,static_enemy_catalog=a.static_catalog,hp=385,reserve_ammo={0:999,1:999,2:999},
                                    enemy_defaults=dict(charge_step=step,windup=10,recovery=10)),time_cap=90)
                            assert all(f['ammo_balance']==0 for f in fights)
                            win=statistics.mean(f['won'] for f in fights)
                            mean=statistics.mean(f['time'] for f in fights)
                            counters+=sum(f.get('counters',0) for f in fights)
                            rounds+=sum(f['rounds'] for f in fights)
                            encounters[enc]=dict(win=win,time_mean=mean,
                                damage_taken=statistics.mean(f['damage_taken'] for f in fights))
                            total+=len(fights)
                            projectile_matches+=sum(f.get('projectile_model_matches',0) for f in fights)
                            projectiles+=sum(f.get('projectiles_launched',0) for f in fights)
                            contacts+=sum(f.get('projectile_contacts',0) for f in fights)
                            timed+=sum(f.get('action_timing_matches',0) for f in fights)
                            matched+=sum(f.get('catalog_matches',0) for f in fights)
                            foe_count+=sum(f.get('catalog_foes',0) for f in fights)
                        score=math.exp(statistics.mean(math.log(max(.1,e['time_mean']+60*(1-e['win'])))
                            for e in encounters.values()))
                        records.append(dict(step=step,group=group,seed=run['seed'],phase=phase,variant=variant,
                            gun=cp['gun'],cfg_sig=cp['cfg_sig'],score=score,
                            win=statistics.mean(e['win'] for e in encounters.values()),counters=counters,
                            rounds=rounds,encounters=encounters))
            print(f'Completed charge-step {step}, group {group}.',flush=True)
    aggregates=[]
    for step in (60,90,120):
        for phase in ('D5','Disc2'):
            for group in GROUPS:
                rs=[r for r in records if r['step']==step and r['phase']==phase and r['group']==group and r['variant']=='baseline']
                aggregates.append(dict(step=step,phase=phase,group=group,n=len(rs),
                    score_mean=statistics.mean(r['score'] for r in rs),
                    win=statistics.mean(r['win'] for r in rs),
                    ci95=1.96*statistics.stdev(r['score'] for r in rs)/math.sqrt(len(rs))))
    lookup={(r['step'],r['group'],r['seed'],r['phase']):r for r in records if r['variant']=='baseline'}
    paired=[]
    for r in records:
        if r['variant']=='baseline':continue
        base=lookup[(r['step'],r['group'],r['seed'],r['phase'])]
        paired.append(dict(step=r['step'],group=r['group'],seed=r['seed'],phase=r['phase'],
            score_delta=r['score']-base['score'],win_delta=r['win']-base['win'],counters=r['counters']))
    raw=dict(meta=dict(projectile_height=a.projectile_height,projectile_matches=projectile_matches,projectiles_launched=projectiles,projectile_contacts=contacts,projectile_extract_sha256=hashlib.sha256((root/'data/pe-projectile-extract-2026-10-18.json').read_bytes()).hexdigest() if a.projectile_height else None,seeds=a.seeds,fights_per_encounter=a.fights,total_fights=total,
        action_timing=a.action_timing,action_timing_matches=timed,action_data_sha256=hashlib.sha256((root/'data/pe-enemy-actions-2026-10-18.json').read_bytes()).hexdigest() if a.action_timing else None,
        static_catalog=a.static_catalog,catalog_matches=matched,catalog_foes=foe_count,
        historical_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        scope='frozen earned loadouts; not reoptimized campaigns',profile=profile,
        catalog_sha256=hashlib.sha256((root/'data/pe-enemy-scripts-2026-10-18.json').read_bytes()).hexdigest() if a.static_catalog else None,
        enemy_scenarios=('Exact map + rank/kind static charge/rank/poison declarations override step60/90/120 fallback; windup10/recovery10 and consume-on-action policy remain assumed.' if a.static_catalog else 'steps60/90/120, windup10/recovery10, consume charge on action; assumed script policies'),
        hp=385,reserves={0:999,1:999,2:999},score='geomean(mean time + 60*(1-win))'),
        aggregates=aggregates,paired_counter_replacements=paired,records=records)
    (root/'data'/f'{stem}.json').write_text(json.dumps(raw,indent=2),encoding='utf-8')
    lines=['# Counter and enemy-charge balance rerun — 2026-10-18','',
        f'{total} fights; {a.seeds} matched frozen campaign seeds per group, {a.fights} fights per encounter.',
        'Uses historically earned equipment; campaigns were not reoptimized. Enemy script policies',
        ('use static declarations where matched and charge-step60/90/120 fallback elsewhere; action selection remains assumed.' if a.static_catalog else 'are explicit charge-step60/90/120 sensitivity scenarios, not extracted enemy-specific AI.'),
        'HP385 and reserve budgets999 per pool are controlled inputs.','',
        'Disc2 baseline results (lower score is better; read win fraction first):','',
        '| Charge step | Group | Score ± 95% Monte Carlo interval | Win fraction |',
        '|---|---|---:|---:|']
    for r in aggregates:
        if r['phase']=='Disc2':lines.append(f"| {r['step']} | {r['group']} | {r['score_mean']:.3f} ± {r['ci95']:.3f} | {r['win']:.3f} |")
    lines+=['','Equal-slot intervention: replace an existing Quickdraw with Counter (negative score delta favors Counter):','',
        '| Charge step | Phase | Eligible seed-loadouts | Mean score delta | Mean win delta | Successful counters |',
        '|---|---|---:|---:|---:|---:|']
    for step in (60,90,120):
        for phase in ('D5','Disc2'):
            rs=[r for r in paired if r['step']==step and r['phase']==phase]
            if rs:lines.append(f"| {step} | {phase} | {len(rs)} | {statistics.mean(r['score_delta'] for r in rs):.3f} | {statistics.mean(r['win_delta'] for r in rs):.3f} | {sum(r['counters'] for r in rs)} |")
    if a.static_catalog:
        lines+=['',f'Static declaration scenario: {matched}/{foe_count} enemy instances matched by exact map + rank/kind.',
            'Matched charge/rank/poison literals override sensitivity defaults. Action selection and windup/recovery remain assumed.',
            'Static declarations are not a control-flow or runtime execution proof. Conflicting and missing identities fall back.']
    if a.action_timing:
        lines+=['',f'Action timing scenario: {a.action_timing}; matched {timed}/{foe_count} enemy instances.',
            'Chooses shortest/longest complete extracted melee action per matching identity; this is not decoded retail choice probability.',
            'Verified straight post-command zero-charge setters enable reset at completion; other reset behavior retains the generic assumption.',
            'Unresolved actions, parent animation sharing, interruptions, movement and hit delivery remain assumptions.']
    if a.projectile_height:
        lines+=['',f'Projectile scenario: map156 ID0x0216, launch height{a.projectile_height}; {projectile_matches} matched enemy instances, {projectiles} orbs launched, {contacts} geometry contacts.',
            'Outer chooser gates assumed entered; close distance<1300 selects melee, far path forces slot4. Flat floor, stationary point player, aligned heading; projectile jitter ranges follow source.',
            'Visual tail completion uses an explicit 24-update bound; full effect pool traversal and process ordering remain unresolved.']
    lines+=['','Score is the geometric mean of encounter mean time +60*(1-win fraction).',
        'Intervals measure Monte Carlo variation under the assumptions, not certainty about retail balance.',
        'Counter eligibility/roll/one-command/gauge cost follow source. Idle reaction settling and',
        'enemy-specific AI/action parameters remain approximations. Rank and HP-level fallbacks are',
        'explicitly documented in pe-counter-enemy-derivation-2026-10-18.md.',
        'No gameplay changes or new global balance recommendation are made from this sensitivity rerun.']
    (root/f'{stem}.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'Wrote {total} fights and {len(paired)} paired effect replacements.',flush=True)


if __name__=='__main__':main()
