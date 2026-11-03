"""Matched comparison of grenade proposals and unchanged M203-2/M203-4."""
import csv,json,statistics
from collections import defaultdict
from pathlib import Path
from .report_native_review import paired
ROOT=Path(__file__).resolve().parents[2]
TAG='native-grenade-progression-2026-10-26'
CASES=[('M203 2','native'),('M79 2','native'),('M79 2','candidate_full'),('M203 3','native'),('M203 3','candidate_full'),('M79 3','native'),('M79 3','attack_plus15'),('M79 3','attack_plus20'),('M203 4','native')]
LABEL={'native':'current','candidate_full':'+20 attack','attack_plus15':'+15 attack','attack_plus20':'+20 attack'}

def main():
 d=json.loads((ROOT/'findings/data'/('pe-'+TAG+'.json')).read_text());groups=defaultdict(list)
 executed=len(d['rows']);cases=list(CASES)
 finepath=ROOT/'findings/data/pe-native-grenade-fine-2026-10-26.json'
 if finepath.exists():
  fine=json.loads(finepath.read_text());executed+=len(fine['rows'])
  cases += [('M79 3','attack_plus%d'%n) for n in (16,17,18,19)]
  d['rows'] += [r for r in fine['rows'] if r['variant'] in {'attack_plus%d'%n for n in (16,17,18,19)}]
  for n in (16,17,18,19):LABEL['attack_plus%d'%n]='+%d attack'%n
 for r in d['rows']:groups[(r['stage'],r['invest'],r['gun'],r['variant'],r['boss'])].append(r)
 records=[]
 for stage in ('D5','Disc2'):
  for invest in ('stock','low','typical','high'):
   for gun,v in cases:
    for boss in (False,True):
     rr=groups[(stage,invest,gun,v,boss)]
     assert rr and all(r['mode']=='builtin' for r in rr)
     row=dict(stage=stage,invest=invest,gun=gun,variant=v,boss=boss,n=len(rr),time=statistics.mean(r['time'] for r in rr),won=statistics.mean(r['won'] for r in rr),damage_taken=statistics.mean(r['damage_taken'] for r in rr),rounds=statistics.mean(r['rounds'] for r in rr),reloads=statistics.mean(r['reloads'] for r in rr))
     for anchor,short in (('M203 2','m203_2'),('M203 4','m203_4')):
      aa=groups[(stage,invest,anchor,'native',boss)]
      key=lambda r:(r['seed'],r['battle'],r['map'])
      am={key(r):r for r in aa};assert set(am)=={key(r) for r in rr}
      row[short+'_ratio']=row['time']/statistics.mean(r['time'] for r in aa)
      row[short+'_delta_ci']=paired(aa,rr)
      row[short+'_faster']=sum(r['time']<am[key(r)]['time']-1e-8 for r in rr)
      row[short+'_tied']=sum(abs(r['time']-am[key(r)]['time'])<=1e-8 for r in rr)
     records.append(row)
 out=ROOT/'findings/data'/('pe-'+TAG+'-comparison.json');out.write_text(json.dumps(dict(meta=d['meta'],rows=records),indent=1))
 with out.with_suffix('.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 lines=['# Grenade progression comparison — 2026-10-26','','**Simulation only; no game balance, settings, or executable changes.**', '',
  f"{executed:,} simulated fights across the main comparison and any fine sweep (including repeated controls); four matched seeds; twelve ordinary encounters and up to four bosses per stage; zero optional installs. Each weapon faces the same sampled battles with the same Aya and investment. Existing M203-2 +15 and M203-4 +15 bonuses remain enabled.",
  'Stock = intrinsic weapon bonuses only, no player investment. Low / typical / high use historical stage investment, including magazine upgrades. D5 is the historical museum-era test pool, not proof that every pickup is available at an exact point on Day 5.', '',
  '## Weapon characteristics','',
  '| Weapon | Recorded pickup area | Attack with intrinsic bonus and current native buff | Proposed attack | Built-in effects | Stock magazine | Slots / cap |',
  '|---|---|---:|---:|---|---:|---|',
  '| M203-2 | Warehouse | 64 | 64 | Heat, RoF2 | 7 | 2 / 5 |',
  '| M79-2 | Chinatown | 46 | 66 (+20) | Acid, RoF3 | 6 | 4 / 4 |',
  '| M203-3 | Chinatown Sewer | 50 | 70 (+20) | Acid, RoF3 | 7 | 4 / 5 |',
  '| M79-3 | Subway | 54 | 69 (+15) or 74 (+20) | Frost, RoF2 | 6 | 3 / 4 |',
  '| M203-4 | Museum | 73 | 73 | Frost, RoF2 | 8 | 5 / 7 |', '',
  'Pickup areas are historical gear-location data, not a verified mandatory acquisition sequence. The M203-4 / M79-3 comparison is the most direct: same built-in effects, different attack, range, ammunition, and slots. M79-3 has range 69 versus M203-4 67, so +20 would exceed its attack and range while losing ammunition and upgrade capacity.', '',
  '## Typical investment','', '| Stage | Weapon | Configuration | Ordinary seconds | Boss seconds | Ordinary ratio vs M203-4 | Boss ratio vs M203-4 |','|---|---|---|---:|---:|---:|---:|']
 for stage in ('D5','Disc2'):
  for gun,v in CASES:
   o=next(r for r in records if (r['stage'],r['invest'],r['gun'],r['variant'],r['boss'])==(stage,'typical',gun,v,False))
   b=next(r for r in records if (r['stage'],r['invest'],r['gun'],r['variant'],r['boss'])==(stage,'typical',gun,v,True))
   lines.append(f"| {stage} | {gun} | {LABEL[v]} | {o['time']:.2f} | {b['time']:.2f} | {o['m203_4_ratio']:.3f} | {b['m203_4_ratio']:.3f} |")
 for stage in ('D5','Disc2'):
  lines += ['',f'## {stage}: investment sensitivity','', '| Investment | Weapon / configuration | Ordinary seconds | Boss seconds | Boss wins | Ordinary ratio vs M203-2 | Ordinary ratio vs M203-4 |','|---|---|---:|---:|---:|---:|---:|']
  for invest in ('stock','low','typical','high'):
   for gun,v in CASES:
    if v=='native' and gun not in ('M203 2','M203 4'):continue
    o=next(r for r in records if (r['stage'],r['invest'],r['gun'],r['variant'],r['boss'])==(stage,invest,gun,v,False))
    b=next(r for r in records if (r['stage'],r['invest'],r['gun'],r['variant'],r['boss'])==(stage,invest,gun,v,True))
    lines.append(f"| {invest} | {gun} {LABEL[v]} | {o['time']:.2f} | {b['time']:.2f} | {b['won']:.3f} | {o['m203_2_ratio']:.3f} | {o['m203_4_ratio']:.3f} |")
 if finepath.exists():
  lines += ['', '## M79-3: smaller attack bonuses','',
   '| Bonus | D5 low ordinary | D5 typical ordinary | D5 high ordinary | D5 stock ordinary | Disc2 typical boss |',
   '|---|---:|---:|---:|---:|---:|']
  for v in ['attack_plus%d'%n for n in (15,16,17,18,19,20)]+['anchor']:
   cells=[]
   for stage,invest,boss in [('D5','low',False),('D5','typical',False),('D5','high',False),('D5','stock',False),('Disc2','typical',True)]:
    r=next(r for r in records if (r['stage'],r['invest'],r['gun'],r['variant'],r['boss'])==(stage,invest,'M203 4' if v=='anchor' else 'M79 3','native' if v=='anchor' else v,boss))
    cells.append(f"{r['time']:.2f}")
   lines.append('| '+('M203-4 current' if v=='anchor' else LABEL[v])+' | '+' | '.join(cells)+' |')
 lines += ['', '## Recommendation for discussion','',
  'Keep M203-2 and M203-4 at their existing +15 native bonuses. M79-2 +20 and M203-3 +20 fit as competitive Acid alternatives: in typical D5 ordinary fights they sit between M203-2 and M203-4, and both remain slower than those anchors on bosses. Heat remains useful, so this is not a universal numerical upgrade chain.',
  'Revise the M79-3 candidate from +20 to +18. +18 is the smallest tested integer bonus that reaches the D5 low-investment breakpoint: 30.97 seconds versus 34.33 at +17 and 30.98 for current M203-4. It produces 72 attack including intrinsic bonuses, versus M203-4 73. M203-4 retains eight versus six stock rounds and five versus three slots (caps seven versus four).',
  'This preserves stat headroom, not a large or statistically established fight-time advantage. At typical investment, M79-3 +18 and M203-4 are effectively tied in D5 fights and Disc2 ordinary fights; the modeled Disc2 boss means are 88.51 versus 86.91 seconds, with a paired interval spanning zero. If M203-4 must feel clearly stronger in immediate combat, +18 alone does not establish that goal. Further identity changes would need a separate discussion.',
  'The initial all-+20 shortlist should therefore remain provisional. No game balance changes were made.',
  '', '## Interpretation limits','',
  'Ratios below 1 mean faster. Ordinary and boss results are separate stratified samples, not a weighted campaign total. Detailed JSON/CSV include matched encounter intervals, sample-level faster/tied counts, win rates, damage taken, ammunition, and reloads.',
  'Some completely uninvested Disc2 controls lose boss fights: current M203-2 wins 87.5%, current M203-3 93.75%, and current M79-3 75% in this sample. Read times alongside win rates; an early death is not a faster clear. The tested +20 grenade proposals win all sampled fights, as does current M203-4.',
  'The source model maps native defaults and integer damage arithmetic; it does not execute the native game. Boss behavior, RNG, status-at-minimum-damage rules, delayed hits, and the crowd-cap heuristic retain the limitations documented in the preceding review. A single logged campaign underlies enemy profiles. Pickup chronology and optional areas are not fully modeled.',
  'No universal weapon ordering is assumed across different elements. Keeping M203-4 worthwhile with built-in effects matters more than preserving its upgrade-slot advantage, because this review explicitly treats Catalog upgrades as optional.', '', '## Reproduce','', '```text',
  'python -m pe_weapon_sim.run_native_review --only "M203 2" "M203 4" "M79 2" "M203 3" "M79 3" --modes builtin --invest stock low typical high --stages D5 Disc2 --seeds 4 --battle-limit 12 --extended --tag native-grenade-progression-2026-10-26',
  'python -m pe_weapon_sim.run_native_review --only "M79 3" --modes builtin --invest stock low typical high --stages D5 Disc2 --seeds 4 --battle-limit 12 --extended --fine --workers 2 --tag native-grenade-fine-2026-10-26',
  'python -m pe_weapon_sim.report_grenade_progression','```']
 path=ROOT/'findings'/('pe-'+TAG+'.md');path.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(path)
if __name__=='__main__':main()
