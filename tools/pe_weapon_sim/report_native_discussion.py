"""Curated discussion report from the completed native-default review batches."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
TAGS=['native-review-2026-10-26','native-dropped-buffs-2026-10-26','native-shotgun-capacity-2026-10-26']

def main():
    batches={t:json.loads((ROOT/'findings/data'/('pe-'+t+'-summary.json')).read_text()) for t in TAGS}
    raw={t:json.loads((ROOT/'findings/data'/('pe-'+t+'.json')).read_text()) for t in TAGS}
    total=sum(len(d['rows']) for d in raw.values())
    cand=batches[TAGS[1]]['candidates']
    def pick(gun,variant,mode='builtin',invest='typical',stage='D5',enc='ordinary'):
        return next(r for r in cand if (r['gun'],r['variant'],r['mode'],r['invest'],r['stage'],r['encounter'])==(gun,variant,mode,invest,stage,enc))
    lines=['# Native weapon balance: proposals to discuss — 2026-10-26','',
        '**No game balance changes made.** The native checkout, saved settings, and game executable were not modified. Only the separate bridge simulator, regression tests, and reports changed.','',
        f'{total:,} simulated fights in three completed batches. The screening covers 38 distinct main-campaign guns (18 available in the early-stage pool), at D2–4, museum-era D5, and Disc2. Chrysler-only weapons, clubs, and other special weapons are outside this ladder.',
        'The disputed five weapons were repeated at four seeds and low / typical / high investment, with up to twelve ordinary encounters plus four bosses per stage. M10B also received stock and attack-only investment checks.','',
        '## What changes the earlier conclusion','',
        'The earlier decision to drop buffs relied on each gun receiving favorable Catalog installs. That establishes upgraded potential; it does not establish that the pickup is satisfying with its built-in effects alone. These runs keep those questions separate.',
        'A simulator bug was corrected: the source combat callback reset installed RoF damage to the built-in percentage at each hit. Historical reports remain untouched, but their precise values should not be treated as equivalent to these corrected runs.',
        'The review additionally maps native integer attack scaling, element scaling, defense division, and hit-quality rounding. 2,000 randomized cases matched the native C damage helper compiled unchanged. Twenty focused regression tests passed. Whole-fight behavior remains a model, not execution of the native game.','',
        '## Attack proposals worth discussing','',
        'D5 ordinary fights, typical investment, built-in effects only. Negative time change means faster. These are separate alternatives, not installed changes.','',
        '| Weapon | Candidate | Native setup → candidate | Time change | Catalog time change, same baseline loadout |',
        '|---|---|---|---:|---:|']
    for gun,v,label in [('M79 2','candidate_full','+20 attack'),('M203 3','candidate_full','+20 attack'),('M79 3','attack_plus20','+20 attack'),('PPK','candidate_half','+5 attack')]:
        b=pick(gun,v);c=pick(gun,v,'catalog')
        lines.append(f"| {gun} | {label} | {b['base_time']:.2f}s → {b['prop_time']:.2f}s | {b['change_pct']:+.1f}% | {c['change_pct']:+.1f}% |")
    lines += ['','**M79-2 +20 and M203-3 +20:** reopen these proposals if pickups should stand on their own. The benefit persists across all three investment levels; the Catalog versions are already competitive, so stronger optimized builds are the tradeoff.',
        '**M79-3:** the old +10 is not robust at low investment. +20 crosses the useful breakpoint at all three tested investment levels; +15 misses it at low investment. Discuss it alongside the other two grenades, and compare with M203-4 before approving a package.',
        '**PPK:** +5 is the conservative candidate; do not automatically take +10. The baseline is already near the overall D5 median and has built-in Quickdraw. A buff helps comfort, but it is a lower priority than the grenade progression.','',
        '## Magazine proposals','',
        'The historical low / typical / high profiles already add 10 / 15 / 20 magazine rounds at D5. Their lack of response to a magazine buff cannot establish that the stock M10B is comfortable.',
        'The dedicated checks below remove magazine investment: stock = zero investment in any stat; attack_only = typical attack and range investment but zero magazine investment.','',
        '| Stage | Setup | Investment | Candidate | Ordinary seconds | Boss seconds |',
        '|---|---|---|---|---|---|']
    sc=batches[TAGS[2]]['candidates']
    for r in sc:
        if r['encounter']!='ordinary':continue
        boss=next(x for x in sc if all(x[k]==r[k] for k in ('stage','gun','mode','invest','variant')) and x['encounter']=='boss')
        lines.append(f"| {r['stage']} | {r['mode']} | {r['invest']} | {r['variant']} | {r['base_time']:.2f} → {r['prop_time']:.2f} | {boss['base_time']:.2f} → {boss['prop_time']:.2f} |")
    lines += ['','M10B +1 round has little impact here. A +50% magazine helps the Catalog-equipped Disc2 boss cases with no magazine investment (23.80s → 20.13s stock; 17.75s → 15.47s with attack/range investment), but ordinary-fight gains are small and the effect disappears with the historical magazine investments. This supports a conditional comfort discussion, not a blanket shotgun damage buff.','',
        '## Other guns','',
        'Keep the existing six attack bonuses as the baseline. The broad screen does not justify a blanket buff to older guns simply because Wayne or later pickups beat them. M79 is reasonably close to the early-stage median; its late-game lag is an expected replacement curve. M203-2 already receives +15 and should remain a comparison point when adjusting the later grenades.',
        'Machine guns, rifles, shotguns, and rockets retain different crowd, boss, range, and ammo roles. This screen does not establish a new P90/MAG adjustment. Rocket campaign viability is not tested by unlimited-reserve isolated battles.','',
        '## Limits and discussion','',
        'Results use one historical logged campaign and modeled movement, enemy behavior, and shot scheduling. Boss absolutes are less reliable than paired comparisons. The sample is stratified, so ordinary and boss averages must not be added into an unweighted campaign score. Catalog is an optimistic best-of-tested-loadouts estimate, not guaranteed player ownership.',
        'Native crowd-cap binary-search granularity, delayed hit processing, status-at-minimum-damage behavior, and RNG replay are not reproduced exactly. Critical conversion retains the inherited 26.67% model chance versus native integer 26%. The disputed five weapons have no built-in Critical.',
        'Recommendation for the discussion: decide whether an unmodified pickup should be a useful upgrade, then consider the three grenade +20 proposals together. Treat PPK +5 as optional and discuss M10B capacity separately. Do not install any balance changes from this report automatically.','',
        '## Detailed evidence','']
    for tag in TAGS:lines.append(f'- [{tag}](pe-{tag}.md): full tables; paired boss/ordinary data and intervals in `data/pe-{tag}-candidates.csv`.')
    lines += ['','## Reproduce','', 'From the bridge repository, set PYTHONPATH to tools and run:', '', '```text',
        'python -m unittest pe_weapon_sim.tests.test_native_damage pe_weapon_sim.tests.test_native_c_oracle pe_weapon_sim.tests.test_source_combat pe_weapon_sim.tests.test_compare_rules',
        'python -m pe_weapon_sim.run_native_review --seeds 2 --workers 4',
        'python -m pe_weapon_sim.run_native_review --only "M79 2" "M203 3" "M79 3" PPK M10B --stages D5 Disc2 --invest low typical high --seeds 4 --battle-limit 12 --extended --tag native-dropped-buffs-2026-10-26',
        'python -m pe_weapon_sim.run_native_review --only M10B --stages D5 Disc2 --invest stock attack_only --seeds 4 --battle-limit 12 --workers 2 --tag native-shotgun-capacity-2026-10-26',
        'python -m pe_weapon_sim.report_native_review native-review-2026-10-26',
        'python -m pe_weapon_sim.report_native_review native-dropped-buffs-2026-10-26',
        'python -m pe_weapon_sim.report_native_review native-shotgun-capacity-2026-10-26',
        'python -m pe_weapon_sim.report_native_discussion','```','',
        'Native defaults and source hashes are recorded in `data/pe-native-defaults-audit-2026-10-26.json`; follow-up batches also embed that audit. Historical result files were preserved.']
    path=ROOT/'findings/pe-native-weapon-review-2026-10-26.md';path.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(path,total)
if __name__=='__main__':main()
