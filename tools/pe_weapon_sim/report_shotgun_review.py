"""Summaries for current-balance shotgun baselines and paired candidate changes."""
import argparse,csv,json,random,statistics
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
METRICS=('time','won','damage_taken','rounds','reloads','click','damage','turns')

def summarize(rows):
 groups=defaultdict(list)
 for r in rows:groups[(r['stage'],r['gun'],r['profile'],r['scenario_kind'],r['variant'])].append(r)
 out=[]
 for (stage,gun,profile,kind,v),rr in sorted(groups.items()):
  z=dict(stage=stage,gun=gun,profile=profile,scenario_kind=kind,variant=v,kind=rr[0]['kind'],n=len(rr))
  for m in METRICS:z[m]=statistics.mean(r[m] for r in rr)
  wins=[r for r in rr if r['won']];z['clear_time']=statistics.mean(r['time'] for r in wins) if wins else None
  cap=400 if rr[0]['boss'] else 90
  z['penalized_time']=statistics.mean(r['time'] if r['won'] else cap for r in rr)
  out.append(z)
 return out

def paired(rows,variant,profile='attack_only'):
 groups=defaultdict(list)
 for r in rows:
  if r['profile']==profile and r['variant'] in ('current',variant):groups[(r['stage'],r['gun'],r['scenario_kind'])].append(r)
 out=[]
 for (stage,gun,kind),rr in sorted(groups.items()):
  base={(r['seed'],r['case']):r for r in rr if r['variant']=='current'}
  prop={(r['seed'],r['case']):r for r in rr if r['variant']==variant}
  if not prop:continue
  assert set(base)==set(prop)
  ds=defaultdict(list)
  for key in base:
   cap=400 if base[key]['boss'] else 90
   ds[key[1]].append((prop[key]['time'] if prop[key]['won'] else cap)-(base[key]['time'] if base[key]['won'] else cap))
  diffs=[statistics.mean(v) for v in ds.values()];rng=random.Random(26)
  bs=sorted(statistics.mean(rng.choices(diffs,k=len(diffs))) for _ in range(1000))
  out.append(dict(stage=stage,gun=gun,profile=profile,scenario_kind=kind,variant=variant,n=len(base),
   base_time=statistics.mean(r['time'] for r in base.values()),prop_time=statistics.mean(r['time'] for r in prop.values()),
   base_won=statistics.mean(r['won'] for r in base.values()),prop_won=statistics.mean(r['won'] for r in prop.values()),
   penalized_delta=statistics.mean(diffs),delta_ci=[bs[24],bs[974]],
   base_rounds=statistics.mean(r['rounds'] for r in base.values()),prop_rounds=statistics.mean(r['rounds'] for r in prop.values()),
   base_reloads=statistics.mean(r['reloads'] for r in base.values()),prop_reloads=statistics.mean(r['reloads'] for r in prop.values())))
 return out

def write_csv(path,rows):
 if not rows:return
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',default='native-all-shotguns-2026-10-26');p.add_argument('--candidate',nargs='*',default=[])
 a=p.parse_args();d=json.loads((ROOT/'findings/data'/('pe-'+a.tag+'.json')).read_text());ss=summarize(d['rows'])
 records=[];cmeta=[]
 for tag in a.candidate:
  cd=json.loads((ROOT/'findings/data'/('pe-'+tag+'.json')).read_text());cmeta.append(dict(tag=tag,fights=len(cd['rows'])))
  for v in cd['meta']['variants']:
   if v!='current':
    for profile in ('stock','attack_only'):records+=paired(cd['rows'],v,profile)
 out=ROOT/'findings/data'/('pe-'+a.tag+'-summary.json')
 out.write_text(json.dumps(dict(meta=d['meta'],summary=ss,candidate_batches=cmeta,candidates=records),indent=1))
 write_csv(out.with_name('pe-'+a.tag+'-baseline.csv'),ss);write_csv(out.with_name('pe-'+a.tag+'-candidates.csv'),records)
 guns=d['meta']['guns'];shotguns=[g['name'] for g in guns.values() if g['kind']==2]
 lines=['# All shotgun review against current native balance — 2026-10-26','',
  '**Simulation only. No native game code, balance settings, or executable changes.**','',
  f"Baseline: {len(d['rows']):,} fights; all seven shotgun records plus six comparison weapons, four seeds, built-in effects only. Candidate experiments: {sum(c['fights'] for c in cmeta):,} fights.",
  'Current means the native Rebalanced defaults, including the approved M79-2 +20, M203-3 +20, and M79-3 +18. Other existing bonuses remain enabled. Both native defaults and source hashes were checked before and after each batch.',
  'All seven shotgun combat stat records were also verified against the original resident item pack read by the native loader; see `data/pe-shotgun-item-audit-2026-10-26.json`.','',
  '## Coverage and investment','',
  'M870 (also MA10) and M870-2 (MA10-2) were missed by the old name-based availability join. This pass enumerates every kind-2 weapon record. Chrysler weapons tested in story scenarios are counterfactual same-investment comparisons, not claims that they can be acquired then.',
  'Stock: no player investment. attack_only: typical attack/range investment (+18/+12 for D5; +50/+18 for Disc2/EX), zero extra magazine rounds. mag2: the same attack/range with only two additional magazine rounds. Intrinsic starting bonuses are retained.',
  'Campaign tests use the sampled logged Aya/armor/PE/bag. Chrysler stress tests use twelve extracted regular enemy stat blocks spanning the tower, including the highest defense (200), each alone and as a constructed group of three. EX33/EX50 use level 33/50 with logged endgame armor and no PE/items. They are not recorded tower fights, and they exclude scripted Chrysler bosses and True Eve.',
  'Every fight starts with a full magazine and a 999-round reserve. Groups use the existing modeled angular spread for Burst. Fight geometry, EX action fallbacks, player levels, and armor assumptions affect absolute times.','',
  '## Weapon records','',
  '| Weapon | Attack including intrinsic bonus | Range | Stock rounds | Built-in effects |','|---|---:|---:|---:|---|']
 for g in guns.values():
  if g['kind']==2:lines.append(f"| {g['name']} | {g['attack']+g['intrinsic_attack']} | {g['range']} | {g['magazine']} | {', '.join(g['builtin'])} |")
 for profile in ('attack_only','stock'):
  for stage in d['meta']['scenarios']:
   kinds=list(dict.fromkeys(r['scenario_kind'] for r in d['rows'] if r['stage']==stage))
   lines+=['',f'## {stage} / {profile}: current balance','',
    '| Weapon | '+ ' | '.join(k+' seconds / win rate' for k in kinds)+' |','|---|'+'---:|'*len(kinds)]
   rr=[r for r in ss if r['stage']==stage and r['profile']==profile and r['variant']=='current']
   names=shotguns+[g['name'] for g in guns.values() if g['kind']!=2]
   for name in names:
    cells=[]
    for k in kinds:
     r=next(x for x in rr if x['gun']==name and x['scenario_kind']==k)
     cells.append(f"{r['time']:.2f} / {r['won']:.0%}")
    lines.append('| '+name+' | '+' | '.join(cells)+' |')
 lines+=['','## Two-round magazine investment','',
  '| Stage / scenario | Shotgun | No extra rounds → +2 rounds, seconds | Win rate | Reloads |','|---|---|---|---|---|']
 for r in ss:
  if r['profile']!='attack_only' or r['kind']!=2 or r['variant']!='current':continue
  p=next(x for x in ss if (x['stage'],x['gun'],x['profile'],x['scenario_kind'],x['variant'])==(r['stage'],r['gun'],'mag2',r['scenario_kind'],'current'))
  lines.append(f"| {r['stage']} / {r['scenario_kind']} | {r['gun']} | {r['time']:.2f} → {p['time']:.2f} | {r['won']:.0%} → {p['won']:.0%} | {r['reloads']:.2f} → {p['reloads']:.2f} |")
 if records:
  lines+=['','## Individual candidate experiments','',
   'These edits exist only in simulator configurations. Paired intervals resample encounters, grouping the repeated seeds per encounter; they measure model variation, not real-game confidence. Delta uses the fight horizon as a penalty for losses so early deaths are not rewarded as faster clears.','',
   '| Stage / scenario | Weapon | Setup | Candidate | Current → candidate seconds | Win rate | Penalized delta interval |','|---|---|---|---|---|---|---|']
  for r in records:
   if r['profile']!='attack_only':continue
   lines.append(f"| {r['stage']} / {r['scenario_kind']} | {r['gun']} | {r['profile']} | {r['variant']} | {r['base_time']:.2f} → {r['prop_time']:.2f} | {r['base_won']:.0%} → {r['prop_won']:.0%} | [{r['delta_ci'][0]:.2f}, {r['delta_ci'][1]:.2f}] |")
 alignpath=ROOT/'findings/data/pe-native-shotgun-burst-alignment-2026-10-26.json'
 if alignpath.exists():
  ad=json.loads(alignpath.read_text());aligned=summarize(ad['rows'])
  lines+=['','## Burst alignment sensitivity','',
   f"Additional {len(ad['rows']):,} current-balance fights: same EX50 stats, seeds, investment, and built-in effects, but the constructed triples are within the native Burst angular predicate. This is an ideal line-up sensitivity, not measured player behavior. Non-Burst controls retain identical outcomes.", '',
   '| Weapon | Scattered triples: seconds / win rate | Lined-up triples: seconds / win rate | Penalized time, scattered → lined-up |',
   '|---|---:|---:|---:|']
  for r in aligned:
   if r['scenario_kind']!='ex_triple':continue
   b=next(x for x in ss if (x['stage'],x['gun'],x['profile'],x['scenario_kind'],x['variant'])==(r['stage'],r['gun'],r['profile'],r['scenario_kind'],'current'))
   lines.append(f"| {r['gun']} | {b['time']:.2f} / {b['won']:.1%} | {r['time']:.2f} / {r['won']:.1%} | {b['penalized_time']:.2f} → {r['penalized_time']:.2f} |")
  write_csv(out.with_name('pe-'+a.tag+'-alignment.csv'),aligned)
 lines+=['','## Findings for discussion','',
  '**M870-2 (MA10-2): +10 attack is the strongest conservative individual candidate.** At attack/range-only investment, current D5 ordinary fights take 37.06s; +5/+10/+15 all cross the same breakpoint to 27.81s. On Disc2 bosses, current 98.40s falls to 93.57s at +5, 87.37s at +10, and 85.17s at +15. +10 takes its intrinsic attack total from 63 to 73, below M500-2 76 and Maverick 82. It preserves the five-round magazine and single-shot identity. It does not make this lower-power tower pickup an upper-floor endgame replacement.',
  'In EX50 single-enemy stress cases, the same M870-2 +10 raises wins from 89.6% to 91.7%; +15 reaches 93.8%. These are limited constructed stress samples, not proof of tower clear rates. Both +2 and +50% magazine candidates leave its results unchanged across the tested profiles. Its main weakness here is damage/breakpoints, not capacity.',
  '**M870: keep.** It is the lower-power main-game shotgun (called MA10 in the old gear list), not a weapon that should be raised to Wayne/S12 power. **M500: keep.** It improves on that early model without needing Catalog installs.',
  '**M500-2: keep.** The modest Disc2 ordinary-fight regression versus M500 (18.05 vs 17.32s at no magazine investment) is offset by better bosses (87.76 vs 92.80s), higher EX33 solo wins (85.4% vs 75%), and improved EX50 aligned-triple wins (72.9% vs M500 68.8%). Its RoF3 and six-round magazine trade ammo cost and firing commitment for damage against tougher targets.',
  '**Maverick: keep.** It provides a useful single-shot, larger-magazine step above M870-2; S12 is a stronger later-tier stat option. Exact Chrysler pickup floors were not established by the available item-location table. **S12: keep.** Strong ordinary performance and ammunition economy; it needs no buff from this evidence.',
  '**M10B: keep.** Best shotgun in the Disc2 boss benchmark (67.74s versus S12 75.14s) and EX50 solo benchmark (15.48s versus S12 18.39s) at zero magazine investment. Its EX50 constructed-triple win rate improves from 68.8% scattered to 87.5% when lined up. Two extra rounds provide a small Disc2 boss improvement (67.74 → 65.20s), not evidence of a broad capacity defect.',
  'A +10 M870-2 change is a proposal only. No weapon attack, magazine, firing speed, native settings, or game executable was modified in this review.',
  '', '## Limits','',
  'Table times include losses/timeouts; always read win rates alongside them. Successful-clear means and penalized durations are available in the CSV/JSON. Stage averages weight the chosen encounters equally, not by campaign frequency. Source-extracted EX stats do not verify its complete AI, room formations, encounter frequency, pickup floors, or progression economy.',
  'Old early-game shotguns need not match Wayne/S12 on upper tower floors. A Chrysler weapon being tested does not establish where it should rank without its actual acquisition-floor data. No class-wide attack, firing-speed, proximity, or reload change is applied.',
  'The built-in RoF is preserved; installed-RoF bonuses and acceleration never apply to these shotguns. Native hit arithmetic is mirrored, but native RNG sequences, status-floor edge cases, delayed hits, and integer crowd-cap search retain earlier model limitations. Critical conversion now uses native integer 26%, rather than the earlier 26.67% approximation.',
  'Other current-balance comparison weapons can specialize: P90 has Attack All, MAG Critical, M9-3 Commands, and grenade elements. Their results provide context, not a requirement that every shotgun beat every class.']
 lines+=['','## Reproduce','', 'Use the configured Python runtime from the bridge root with PYTHONPATH=tools.','', '```text',
  'python -m unittest pe_weapon_sim.tests.test_shotgun_review pe_weapon_sim.tests.test_native_damage pe_weapon_sim.tests.test_native_c_oracle pe_weapon_sim.tests.test_source_combat',
  'python -m pe_weapon_sim.run_shotgun_review',
  'python -m pe_weapon_sim.run_shotgun_review --only "M870 2" --no-anchors --profiles stock attack_only --variants current attack5 attack10 attack15 mag2 mag50pct --workers 2 --tag native-shotgun-m8702-candidates-2026-10-26',
  'python -m pe_weapon_sim.run_shotgun_review --stages EX50 --profiles attack_only --geometry clustered --workers 2 --tag native-shotgun-burst-alignment-2026-10-26',
  'python -m pe_weapon_sim.report_shotgun_review --candidate native-shotgun-m8702-candidates-2026-10-26','```']
 path=ROOT/'findings'/('pe-'+a.tag+'.md');path.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(path)
if __name__=='__main__':main()
