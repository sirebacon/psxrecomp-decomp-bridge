"""Current-balance remaining Chrysler weapons and matched candidate experiments."""
import argparse,json
from pathlib import Path
from .report_shotgun_review import summarize,paired,write_csv
ROOT=Path(__file__).resolve().parents[2]
KINDS={1:'Handguns',2:'Shotgun reference',3:'Machine guns',4:'Rifles',5:'Grenade launchers',6:'Rocket launchers',8:'Clubs — damage only'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',default='native-chrysler-weapons-2026-10-26');p.add_argument('--candidate',nargs='*',default=[])
 a=p.parse_args();d=json.loads((ROOT/'findings/data'/('pe-'+a.tag+'.json')).read_text());ss=summarize(d['rows']);cc=[];batches=[]
 for tag in a.candidate:
  cd=json.loads((ROOT/'findings/data'/('pe-'+tag+'.json')).read_text());assert cd['meta']['native_audit']==d['meta']['native_audit']
  batches.append(dict(tag=tag,fights=len(cd['rows'])))
  for v in cd['meta']['variants']:
   if v!='current':
    for profile in ('stock','attack_only'):cc+=paired(cd['rows'],v,profile)
 info=d['meta']['guns'];total=len(d['rows'])+sum(x['fights'] for x in batches)
 summary=ROOT/'findings/data'/('pe-'+a.tag+'-summary.json')
 summary.write_text(json.dumps(dict(meta=d['meta'],summary=ss,candidate_batches=batches,candidates=cc),indent=1))
 write_csv(summary.with_name('pe-'+a.tag+'-baseline.csv'),ss);write_csv(summary.with_name('pe-'+a.tag+'-candidates.csv'),cc)
 lines=['# Remaining Chrysler weapons versus current native balance — 2026-10-26','',
  '**No native game balance, code, saved settings, or executable changes.**','',
  f"{total:,} simulated fights: {len(d['rows']):,} baseline and {sum(x['fights'] for x in batches):,} candidate experiments. All 31 remaining Chrysler weapon records are included, plus 13 current-balance reference weapons. Four matched seeds per configuration. Previously reviewed Chrysler shotguns are not repeated as targets.",
  'Current baseline includes PPK +5, M870-2 +10, M79-2 +20, M203-3 +20, M79-3 +18, and all earlier native bonuses. Both native settings defaults and source hashes were checked before and after each run. Combat stats for all 44 records were verified against the resident item pack used by the native loader (`data/pe-chrysler-items-audit-2026-10-26.json`).','',
  '## Method and coverage','',
  'Built-in effects only. Stock uses intrinsic bonuses and no player investment. attack_only adds the same late-game +50 attack/+18 range to every weapon, with zero magazine investment. Built-in RoF never receives installed-RoF power/animation changes.',
  'Disc2 uses sampled logged campaign enemies, Aya, armor, spells, and bags. EX33/EX50 use twelve extracted Chrysler regular enemy stat blocks (including defense 200) as singles and constructed triples, fixed level 33/50 with logged endgame armor and no spells/items. EX tests are stress scenarios, not actual tower fights. There is no scripted Chrysler boss or True Eve validation, pickup-floor chronology, or complete EX economy replay.',
  'AM444 is mapped to native AM44. Clubs 4–5 are included for damage, Counter, and Quickdraw; stealing/loot utility is not modeled. Rocket benchmarks have 999 reserve rockets and do not establish campaign ammo affordability.',
  'A status-floor simulator correction was made before these runs: Cyanide/Acid/Tranq cannot activate when the native pre-quality damage term is non-positive. Native integer damage checks and the dedicated Cyanide regression pass. Earlier reports remain historical; these new results should be compared within this matched batch.',
  'Times include deaths/timeouts; read the win rates. Full CSV/JSON also include successful-clear times, failure-penalized durations, ammunition, empty clicks and reloads. No weak early pickup is required to match a top Wayne gun at the upper tower.','',
  '## Weapon records','',
  '| Weapon | Class | Base + intrinsic attack | Native attack bonus | Range | Stock rounds | Built-in effects |','|---|---|---:|---:|---:|---:|---|']
 for i,g in info.items():
  if not g['chrysler']:continue
  bonus=d['meta']['bonuses'].get(i,0)
  lines.append(f"| {g['name']} | {KINDS[g['kind']]} | {g['attack']} | {bonus} | {g['range']} | {g['magazine']} | {', '.join(g['builtin']) or 'None'} |")
 if cc:
  proposals=[('M1911A3','attack15',15),('M16A2','attack20',20),('M203 5','attack15',15),('M79 4','attack15',15),('M79 5','attack10',10)]
  lines+=['','## Shortlist for discussion — no changes applied','',
   'These are conservative starting points for playtesting, not proven unique optima. M1911A3 and M16A2 are the clearest weak gun candidates; consider the three non-elemental grenades together to preserve their relative stats. The boss comparisons contain four sampled boss encounters × four seeds, so absolute times and exact bonus choices remain provisional.', '',
   '| Weapon | Candidate flat attack bonus | Attack including intrinsic bonuses, current → proposed | Disc2 boss seconds, current → proposed | EX50 solo wins, current → proposed |',
   '|---|---:|---:|---:|---:|']
  for gun,v,bonus in proposals:
   g=next(g for g in info.values() if g['name']==gun)
   boss=next(r for r in cc if (r['gun'],r['variant'],r['profile'],r['stage'],r['scenario_kind'])==(gun,v,'attack_only','Disc2','campaign_boss'))
   ex=next(r for r in cc if (r['gun'],r['variant'],r['profile'],r['stage'],r['scenario_kind'])==(gun,v,'attack_only','EX50','ex_solo'))
   lines.append(f"| {gun} | +{bonus} | {g['attack']} → {g['attack']+bonus} | {boss['base_time']:.2f} → {boss['prop_time']:.2f} | {ex['base_won']:.1%} → {ex['prop_won']:.1%} |")
  lines += ['',
   '**M1911A3 +15:** preserves its attack below M1911A4 (65 versus 68) while improving its weak built-in RoF5 performance. It still trails the single-shot M1911A4 on bosses (99.18 versus 87.90s); this is a modest repair, not proof that the built-in high-RoF tradeoff is fully solved.',
   '**M16A2 +20:** raises intrinsic attack from 55 to 75, matching PSG-1’s nominal attack but retaining different RoF. It remains a little slower than current G3A3 and PSG-1 on sampled bosses (101.18 versus 96.74 and 92.07s). It does not obsolete either anchor.',
   '**Grenades +15 / +15 / +10:** M79-4 reaches 76 attack with ten stock rounds; M203-5 reaches 83 with seven; M79-5 reaches 85 with eight and more range. M79-6 stays at 94 with eleven rounds, while M203-6 retains Cyanide utility. These choices avoid flattening the whole non-elemental line. They remain slower on the sampled bosses than current M203-4 / M79-3, so elemental launchers retain a role.',
   'Ordinary-fight gains are smaller than boss gains, and larger +20 alternatives exist in the experiment tables. M203-5 and M79-5 boss intervals reach zero because some sampled bosses do not benefit; their recommendations are less strongly supported than the M1911A3/M16A2/M79-4 cases. Exact pickup-floor data and live tests are still needed before treating this as a finished Chrysler progression.',
   'A separate stock-only grenade pass confirms the direction without any player attack/range investment: proposed EX50 solo win rates rise from 79.2% to 87.5% (M203-5), 77.1% to 85.4% (M79-4), and 85.4% to 87.5% (M79-5). Completely uninvested Disc2 boss wins remain 75% for these guns; the proposed bonuses do not turn them into universal boss or tower-clearing weapons.',
   'Adding two magazine rounds has very little benefit for the five tested candidates. There is no evidence here for a general capacity or class-wide attack increase.',
   '**Keep the other 26 targets for now:** the SMGs, M96R, Mark 23, USP-3, stronger rifles, M203-6, M79-6, AT4-1, and Clubs 4–5 have useful damage or built-in-effect roles. Lower-tier single-shot handguns such as P228 and USP-2 are slower, but that alone does not establish a buff when acquisition floors and ammo/utility choices are unresolved. This is a watch list, not a claim that every unmodified gun is equally strong.',
   'Clubs already show strong offensive results; their unmodeled stealing value is additional utility. AT4-1 fits below LAW80 in this ammo-unlimited comparison, but rocket economy and splash geometry need separate validation. No nerfs or balance edits are proposed from these cases.']
 for profile in ('attack_only','stock'):
  for kind,label in KINDS.items():
   guns=[g for g in info.values() if g['kind']==kind]
   if not guns:continue
   guns.sort(key=lambda g:(not g['chrysler'],g['attack'],g['name']))
   lines+=['',f'## {label} / {profile}: current balance','',
    '| Weapon | Chrysler | Disc2 ordinary: s / wins | Disc2 bosses: s / wins | EX50 single: s / wins | EX50 triple: s / wins |',
    '|---|---|---:|---:|---:|---:|']
   for g in guns:
    cells=[]
    for stage,sk in [('Disc2','campaign_ordinary'),('Disc2','campaign_boss'),('EX50','ex_solo'),('EX50','ex_triple')]:
     r=next(r for r in ss if (r['stage'],r['gun'],r['profile'],r['scenario_kind'],r['variant'])==(stage,g['name'],profile,sk,'current'))
     cells.append(f"{r['time']:.2f} / {r['won']:.1%}")
    lines.append('| '+g['name']+' | '+('Yes' if g['chrysler'] else 'Reference')+' | '+' | '.join(cells)+' |')
 if cc:
  lines+=['','## Candidate experiments against current balance','',
   'These changes exist only in simulator configurations. Paired intervals resample encounter-level differences, grouping repeated seeds per encounter. Losses receive the 90/400-second scenario horizon as a penalty; short failed fights are not rewarded. Intervals describe model variation, not real-game confidence. Stock-profile results remain in the full CSV.', '',
   '| Weapon | Scenario | Candidate | Current → candidate seconds | Current → candidate wins | Penalized delta interval, s |',
   '|---|---|---|---|---|---|']
  for r in cc:
   if r['profile']!='attack_only' or r['stage']=='EX33':continue
   lines.append(f"| {r['gun']} | {r['stage']} / {r['scenario_kind']} | {r['variant']} | {r['base_time']:.2f} → {r['prop_time']:.2f} | {r['base_won']:.1%} → {r['prop_won']:.1%} | [{r['delta_ci'][0]:.2f}, {r['delta_ci'][1]:.2f}] |")
 lines+=['','## Limits','']+['- '+x for x in d['meta']['limitations']]
 lines+=['','## Reproduce','', 'From the bridge root with the configured Python runtime and PYTHONPATH=tools:', '', '```text',
  'python -m unittest pe_weapon_sim.tests.test_chrysler_review pe_weapon_sim.tests.test_native_damage pe_weapon_sim.tests.test_native_c_oracle pe_weapon_sim.tests.test_source_combat',
  'python -m pe_weapon_sim.run_chrysler_review',
  'python -m pe_weapon_sim.run_chrysler_review --only M1911A3 M16A2 --no-anchors --profiles stock attack_only --variants current attack5 attack10 attack15 attack20 mag2 --workers 2 --tag native-chrysler-candidates-a-2026-10-26',
  'python -m pe_weapon_sim.run_chrysler_review --only "M203 5" "M79 4" "M79 5" --no-anchors --profiles attack_only --variants current attack5 attack10 attack15 attack20 mag2 --workers 2 --tag native-chrysler-candidates-b-2026-10-26',
  'python -m pe_weapon_sim.run_chrysler_review --only "M203 5" "M79 4" "M79 5" --no-anchors --stages Disc2 EX50 --profiles stock --variants current attack10 attack15 attack20 --workers 4 --tag native-chrysler-candidates-stock-2026-10-26',
  'python -m pe_weapon_sim.report_chrysler_review --candidate native-chrysler-candidates-a-2026-10-26 native-chrysler-candidates-b-2026-10-26 native-chrysler-candidates-stock-2026-10-26','```']
 path=ROOT/'findings'/('pe-'+a.tag+'.md');path.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(path,total)
if __name__=='__main__':main()
