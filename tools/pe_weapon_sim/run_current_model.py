"""Offline current-model rerun of frozen earned loadouts; no campaign reoptimization."""
import hashlib
import json
import statistics
from pathlib import Path
from . import rules
from .decomp_animation import source_behavior_rules
from .economy import equipment, evaluation, tables, source_stats
from .enemy_identity import FIRST_RUN_SHARED_CELLS
from .run_behavior_balance import GROUPS, ENCOUNTERS, config

ROOT = Path(__file__).resolve().parents[2]
STEM = 'pe-current-model-balance-2026-10-18'

def fingerprints():
    paths = list((ROOT/'tools/pe_weapon_sim').rglob('*.py')) + list((ROOT/'findings/data').glob('pe-*.json'))
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.stem != STEM}

def main():
    before = fingerprints()
    history = json.loads((ROOT/'findings/data/pe-weapon-p3-completion-2026-10-17.json').read_text(encoding='utf-8'))
    records=[]; coverage={}; total=0
    profile=source_behavior_rules(rules.CURRENT)
    # Frozen BP purchases are replayed against the source growth thresholds, preserving
    # purchase count rather than the obsolete linear stat22.
    for bound in ('early','late'):
        for group in GROUPS:
            for run in history['raw']['overlap|'+group][:8]:
                for phase in ('D5','Disc2'):
                    cp=run['cps'][phase]; cfg=config(cp)
                    name=cp['armor'].split('#')[0].strip()
                    ids=[i for i,r in tables.ITEMS.items() if r['kind']==9 and r['name'].upper()==name.upper()]
                    if len(ids)!=1: raise ValueError(('ambiguous armor',name,ids))
                    armor_item=equipment.Item(ids[0],'frozen',phase)
                    armor_item.bonus=list(cp['armor_bonus'])
                    inverse={v:k for k,v in tables.ARMOR_FX.items()}
                    armor_item.mods=[inverse[m] for m in cp['armor_mods']]
                    value=source_stats.value_at(cp['level']); purchased=value
                    for _ in range(cp['at_bought']): purchased=source_stats.next_threshold(5,purchased)
                    aya=source_stats.player_inputs(cp['level'],armor_item,at_extra=purchased-value)
                    armor=evaluation.armor_of(armor_item)
                    for enc in ENCOUNTERS:
                        options=dict(static_enemy_catalog=True,shared_cells=FIRST_RUN_SHARED_CELLS,
                            enemy_action_timing='fast',contact_timing=bound,melee_window=bound,
                            melee_reach=True,effect_actions=True,enemy_choice=dict(contact=bound,ambiguous='first'),
                            player_status=True,hp=385,reserve_ammo={0:999,1:999,2:999},
                            enemy_defaults=dict(charge_step=90,windup=10,recovery=10,source_action_slot=0))
                        fights=evaluation.run_enc(profile,cfg,aya,enc,phase,6,seed=run['seed'],armor=armor,
                                                  source_options=options,time_cap=90)
                        assert all(f['ammo_balance']==0 for f in fights)
                        for f in fights:
                            for k,v in f.items():
                                if not k.startswith('_') and isinstance(v,(int,float)) and any(s in k for s in
                                    ('matches','catalog_foes','power_hits','legacy_damage','melee_reach','status_','choice_','unmodeled')):
                                    coverage[k]=coverage.get(k,0)+v
                        records.append(dict(bound=bound,group=group,phase=phase,encounter=enc,seed=run['seed'],
                            gun=cp['gun'],stat22=aya['stat22'],win=statistics.mean(f['won'] for f in fights),
                            time=statistics.mean(f['time'] for f in fights),damage_taken=statistics.mean(f['damage_taken'] for f in fights),
                            rounds=statistics.mean(f['rounds'] for f in fights)))
                        total+=len(fights)
            print(f'Completed {bound}: {group}; {total} fights',flush=True)
    after=fingerprints(); changed=[p for p in before if before[p]!=after.get(p)]
    aggregates=[]
    for bound in ('early','late'):
        for phase in ('D5','Disc2'):
            for group in GROUPS:
                rs=[r for r in records if (r['bound'],r['phase'],r['group'])==(bound,phase,group)]
                aggregates.append(dict(bound=bound,phase=phase,group=group,
                    **{k:statistics.mean(r[k] for r in rs) for k in ('win','time','damage_taken','rounds')}))
    result=dict(meta=dict(total_fights=total,seeds=8,fights_per_encounter=6,hp=385,
        scope='Frozen earned loadouts; source stats and latest opt-in ordinary enemy features; not reoptimized campaigns',
        changed_inputs=changed,input_sha256=before,options=options),coverage=coverage,aggregates=aggregates,records=records)
    (ROOT/f'findings/data/{STEM}.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    lines=['# Current-model simulation — October 18, 2026','',f'{total:,} fights using 8 frozen campaign seeds, 6 fights per encounter, D5 and Disc2, and early/late contact bounds.',
        'User authorized this rerun after Claude’s latest additions. No game interaction. Equipment and BP purchase counts are frozen; source stat tables recalculate Aya’s stats.',
        '','| Contact | Phase | Group | Win % | Mean seconds | Mean damage taken | Mean rounds |','|---|---|---|---:|---:|---:|---:|']
    for r in aggregates:
        lines.append(f"| {r['bound']} | {r['phase']} | {r['group']} | {100*r['win']:.1f} | {r['time']:.2f} | {r['damage_taken']:.1f} | {r['rounds']:.1f} |")
    lines+=['','## Interpretation limits','',
        'These are scenario results, not a final retail balance verdict. HP385 and effectively ample ammunition are controlled inputs. Source max HP is not used because the prior save had an HP bug.',
        'Distance profiles are sampled encounter scenarios, not continuous world navigation. Melee reach uses facing actors on a common floor and captured idle Aya geometry. Early/late timing bounds do not reconstruct per-frame player movement.',
        'Overlapping choice guards select the lowest slot; unknown actions retain approximations. Slot0 is the explicit fallback power selection, not a claim that retail enemies always choose it. Missing source charge/timing uses step90 and windup/recovery10.',
        'Boss encounters retain incomplete generic behavior; the validated beam volley adapter is not a complete boss AI and is not enabled here. Frozen equipment was optimized under earlier rules, so this run does not establish newly optimal campaign policies.',
        '',f'Inputs changed during run: {changed!r}.','', '## Feature counters','', '```json',json.dumps(coverage,indent=2),'```']
    (ROOT/f'findings/{STEM}.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(dict(total_fights=total,changed_inputs=changed,aggregates=aggregates),indent=2),flush=True)

if __name__=='__main__': main()
