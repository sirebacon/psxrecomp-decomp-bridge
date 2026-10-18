"""Generate the remaining Phase 3 reports C–L from corrected experiments."""
import json
import os
from .run_completion import OUT
from . import reporting as R, run_phase3 as P

ROOT = os.path.abspath(os.path.join(P.OUT_DIR, '..'))


def table(headers, rows):
    # Group names contain pipes; escape them to preserve Markdown column counts.
    return R.table(headers, [[str(x).replace('|', '\\|') for x in row] for row in rows])


def main():
    with open(OUT, encoding='utf-8') as f:
        data = json.load(f)
    groups, raw = data['groups'], data['raw']
    def s(key, phase='Disc2'):
        return groups[key]['summary'][phase]
    def m(key, metric, phase='Disc2'):
        return R.m(s(key, phase).get(metric), nd=2)
    def final(key, metric):
        return R.m(groups[key]['summary']['final'].get(metric), nd=2)
    def overview(keys, phase='Disc2'):
        return table(['group','suite seconds ±95% CI','BP earned','BP spent','pending BP','AT bought','capacity','main gun'],
            [[k,R.mci(s(k,phase).get('suite_time')),m(k,'bp_earned',phase),m(k,'bp_spent',phase),
              m(k,'bp_pool',phase),m(k,'at_bought',phase),m(k,'capacity',phase),R.top(s(k,phase)['guns'])] for k in keys])
    def paired(keys):
        return table(['comparison group','D5 difference seconds','Disc2 difference seconds'],
            [[k,R.mci(data['paired'].get(k+'|D5')),R.mci(data['paired'].get(k+'|Disc2'))] for k in keys])
    prefix = (
        'Generated from `data/pe-weapon-p3-completion-2026-10-17.json` using corrected checkpoint snapshots '
        'and timing-separated surrogate scores. Original Phase 3 tables and the first continuation '
        'remain historical artifacts; their checkpoint combat results are superseded here.\n\n'
        f"Each group: {data['meta']['n']} matched campaign seeds; first {data['meta']['bench']} seeds "
        'benchmarked at D5 and Disc2, ten fights per encounter. CIs describe Monte Carlo variation '
        'under the model, not confidence in actual game mechanics. Overlap and serial are alternative '
        'ATB assumptions. Fixed pickup timing and exploration profiles remain assumptions derived '
        'from one logged campaign. No gameplay changes were implemented.\n\n')
    files = []
    def write(letter, slug, title, body):
        name = f'pe-weapon-p3-{letter}-{slug}-2026-10-17.md'
        with open(os.path.join(ROOT,name),'w',encoding='utf-8') as f:
            f.write(f'# Phase 3 report {letter}: {title}\n\n'+prefix+body+'\n')
        files.append(name)

    bpkeys = [t+'|'+p for t in ('overlap','serial') for p in ('A','C','G','H','I','S_def','S_save','S_wpn')]
    bp_table = table(['group','attack BP','range BP','bullets BP','AT BP','capacity BP','armor BP','unspent incl. pool'],
        [[k]+[m(k,'bp_'+x) for x in ('attack','range','bullets','active_time','capacity','armor','unspent')] for k in bpkeys])
    write('C','bp-economy','BP economy and opportunity costs',
        overview(bpkeys)+'\n\n'+bp_table+'\n\n'+paired([t+'|G' for t in ('overlap','serial')])+
        '\n\nDifferences above are relative to optimizer C within the same timing model; negative is faster. '
        'These are whole-policy comparisons with combat-feedback earnings, not isolated returns on one BP point. '
        'One weapon stat point costs 100 BP; buying it defers one AT stat level or one capacity stat level. '
        'Capacity stat levels need not grant an inventory slot at every step. Armor defense currently does '
        'not reduce simulated incoming damage, so this model cannot fairly value defense-first investment. '
        'BP after the final level-up remains pending and cannot be spent. Do not convert earned totals '
        'directly into affordable upgrades. The optimizer is a surrogate-guided heuristic, not a proven optimum.')

    keys = ['overlap|'+p for p in ('A','C','G','H','I')]
    resource = table(['group','Tools field','Tools drops','Tools rare','Tools bought','Tools spent','boosters field','boosters rare','overflow events'],
        [[k]+[final(k,x) for x in ('tools_got_field','tools_got_drop','tools_got_rare','tools_got_bought',
                                   'tools_spent_total','boosters_got_field','boosters_got_rare','overflow')] for k in keys])
    rares = table(['group','mean rare rewards per campaign'],[[k,', '.join(f'{n}: {v}' for n,v in groups[k]['summary']['final']['rare_per_run'].items())] for k in keys])
    write('D','rare-drop-economy','Rare rewards and Tool feedback',resource+'\n\n'+rares+
        '\n\nNormal pity starts at 4%, gains one percentage point per dry battle, and guarantees a rare '
        'when dry+1 reaches 25. Lucky Find adds two dry steps on failure, not a new reward table. '
        'Within a rare cascade, the Tool branch rolls at 85/65/40/20/10% for 0/1/2/3/4 Tools held '
        'and skips at 5+ or with a kit. Earlier cascade branches can win first, so those numbers '
        'are conditional branch chances, not per-battle Tool probabilities. Spending Tools raises '
        'later Tool eligibility; hoarding suppresses Tool rewards and allows more later-branch '
        'boosters. Observed differences also include policies buying Tools and wearing economy mods. '
        'The model does not establish that players should waste Tools to manipulate drops.')

    donors = table(['group','gear pickups offered','stat transfers','extracted atk','extracted range','extracted bullets','BP bonus points moved','Tools left','unused gun bonuses'],
        [[k,final(k,'donors_got'),final(k,'donors_harvested')]+[final(k,'extracted_'+x) for x in ('attack','range','bullets')]+
         [final(k,'extracted_bp'),m(k,'tools_left'),m(k,'unused_donor_bonus')] for k in keys])
    write('E','donor-analysis','Donor equipment and transfer costs',donors+'\n\n'+resource+
        '\n\nThe existing metric named donors_got counts offered guns **and armor**, including gear '
        'that can overflow; it is not a count of useful donor guns. Transfer totals count actions, '
        'including switching and armor transfers, rather than distinct harvested weapons. A plain '
        'Tool transfers all three bonus axes and deletes the donor; a Super Tool preserves it with '
        'bonuses removed. Base stats do not transfer. BP-derived bonuses retain provenance and '
        'transfer exactly like other bonuses. Switching preserves investment if a Tool is available, '
        'but consumes the prior weapon under an ordinary Tool. This is not costless switching. '
        'Inventory-focused results describe this inventory policy; consumable reserves are coarse '
        'and armor defense is omitted, so a small simulated capacity benefit is not evidence that '
        'capacity is useless in play.')

    prog = []
    for timing in ('overlap','serial'):
        for pol in ('A','C','I'):
            for phase in P.PHASES:
                k=timing+'|'+pol; row=s(k,phase)
                prog.append([k,phase,m(k,'bp_earned',phase),R.top(row['guns']),
                    '/'.join(m(k,'bonus_'+x,phase) for x in ('attack','range','bullets')),
                    m(k,'magazine',phase),R.mci(row.get('suite_time'))])
    profilekeys = [t+'|C'+suffix for t in ('overlap','serial') for suffix in ('','_minimal','_completionist','_farmer')]
    write('F','integrated-progression','Integrated progression across the story',
        table(['group','phase','BP earned','gun','bonus atk/rng/bul','magazine','suite seconds'],prog)+
        '\n\n## Exploration sensitivity\n\n'+overview(profilekeys)+
        '\n\nD1 and D2–4 resource states are recorded but not combat-benchmarked in this experiment. '
        'A dash is not a zero clear time. Farmers add modeled repeat encounters; this is not a '
        'validated farming route or an estimate of real hours required. Completionist gear and '
        'uniform within-phase pickup timing can bring items earlier than a real route would.')

    route_rows=[]
    for k in [t+'|'+p for t in ('overlap','serial') for p in ('S0','S1','controlled_shotgun')]:
        for threshold in ('acquired','mag8','mag12','mag16'):
            reached=[r['routes'][threshold] for r in raw[k] if threshold in r['routes']]
            phases={ph:sum(x['phase']==ph for x in reached) for ph in P.PHASES}
            bp=[x['bp_spent']['bullets'] for x in reached]
            route_rows.append([k,threshold,f'{len(reached)}/{len(raw[k])}',str(phases),
                R.m(P.stats([x['battle'] for x in reached])),R.m(P.stats(bp))])
    write('G','magazine-breakpoints','M10B acquisition and reachable capacity',
        table(['group','milestone','reached','phase counts','mean battle if reached','cumulative bullet BP if reached'],route_rows)+
        '\n\nMilestones are first observations of a live owned M10B after policy maintenance. '
        'An item can gain several points in one maintenance pass, so this is a conservative observation '
        'time, not the exact transaction time. Counts are conditional on the modeled acquisition '
        'policy and log-derived availability. Cumulative bullet BP includes previous weapons; it '
        'is not the direct cost paid on M10B alone. Raw records retain origins and cumulative Tool/Junk '
        'spending at each milestone.\n\n'
        'A direct Bullet +1 costs 100 spendable BP; a donor route costs one Tool and an available '
        'donor with a Bullet bonus, transferring its other bonuses too. A suitable booster adds '
        'its tier without a Tool, but its acquisition is random. S0 spends no BP on bullets; compare '
        'its milestones with S1 before claiming BP is necessary. None of these routes guarantees '
        'an early pickup. The original fixed-capacity grid remains a controlled mechanical experiment, '
        'not evidence that every grid build is obtainable in a normal campaign.')

    classkeys=[t+'|controlled_'+c for t in ('overlap','serial') for c in ('handgun','shotgun','machine','rifle','grenade')]
    write('H','weapon-reevaluation','Controlled class-policy comparisons',overview(classkeys)+
        '\n\n## Paired differences from unrestricted C\n\n'+paired(classkeys)+
        '\n\nAll controlled class policies inherit C’s BP, mod, donor, purchasing, and switching '
        'decision settings; only preferred class changes. This controls decision logic, not identical '
        'realized earnings, gear, or resource spending. Gear must be acquired through the economy. '
        'The preferred class can be unavailable earlier; inspect checkpoint gun shares before '
        'calling any row a class-specific benchmark. These results cover policies and their chosen '
        'guns, not every individual named gun at equal investment. M500 versus M10B and earlier '
        'individual weapons still need targeted fixed-loadout comparisons if decisions depend on them. '
        'P90/MAG dominance must be conditioned on timing assumptions; no nerf follows from a single model.')

    modrows=[]
    for k in classkeys+['overlap|D','serial|D']:
        modrows.append([k,', '.join(f'{name}: {share:.0%}' for name,share in s(k)['mods_share'].items()),
                        R.mci(s(k).get('second_suite_time'))])
    write('I','build-diversity','Build diversity and two-weapon investment',
        table(['group','final mod frequency','secondary suite seconds'],modrows)+
        '\n\n'+overview(['overlap|C','overlap|D','serial|C','serial|D'])+
        '\n\nFrequent Commands or Quickdraw selections show these policies favor them; they do '
        'not prove either effect is mandatory. Establishing that requires matched mod-removal '
        'experiments at the same legal slot budget. Secondary scores benchmark each gun separately; '
        'the model does not simulate a dynamic two-gun encounter policy with switch time and '
        'shared ammunition. Do not treat the better of the two scores as an achievable free-switch '
        'result. Transferable BP lowers sunk equipment cost, but maintaining two simultaneous '
        'bonus pools still competes for donors and Tools.')

    sgkeys=[t+'|S'+str(i) for t in ('overlap','serial') for i in range(5)]
    closerows=[]
    for k in sgkeys:
        benches=[r['bench']['Disc2_close'] for r in raw[k] if 'Disc2_close' in r['bench']]
        closerows.append([k,R.mci(P.stats([b['suite_time'] for b in benches])),
                          R.mci(P.stats([b['close_normal']['taken'] for b in benches]))])
    write('J','shotgun-proposal','Revised shotgun experiments S0–S4',overview(sgkeys)+
        '\n\n## Paired differences\n\n'+paired([k for k in sgkeys if not k.endswith('S1')])+
        '\n\nS0/S2/S3/S4 differences use S1 as the matched reference. S1 rows elsewhere use C. '
        'S0: no BP bullets; S1: normal specialist; S2: proximity benchmark; S3: base Bullet +1 '
        'without BP bullets; S4: base Bullet +1 plus proximity benchmark.\n\n'+
        table(['group','Disc2 close-in suite seconds','close-normal damage taken'],closerows)+
        '\n\nProximity in S2/S4 is a checkpoint-only combat experiment (+40% within 400 units, '
        'fading to zero at 650). Campaign hit feedback and policy scoring remain CURRENT, so this '
        'does not measure a full-campaign proximity economy. Close-in policy assumes a 350-unit '
        'stopping distance and increased hit risk; real reachability is unmeasured.\n\n'
        'Recommendation: retain stock magazine and CURRENT damage pending runtime measurements. '
        'Progression can solve capacity, while the remaining shotgun clear-time gap warrants '
        'testing an optional proximity mechanic. Avoid treating a faster benchmark as proof that '
        'the proposed coefficient is balanced or needed throughout the campaign.')

    abkeys=['overlap|'+x for x in ('C','A1','A2','A3','A4','A5','A6','A7')]
    write('K','validation','Corrections, sensitivity, and validation',
        '## Corrections\n\nCheckpoint equipment is now deep-copied. Earlier checkpoints previously '
        'referenced live Item objects that could gain later upgrades or be zeroed/deleted by a '
        'transfer. This contaminated combat benchmarks while compact checkpoint summaries retained '
        'the old values. Timing is part of the surrogate cache key. Spearman now uses average '
        'ranks for ties and Pearson correlation of ranks; constant vectors return undefined.\n\n'+
        table(['phase','corrected Spearman','loadouts'],[[k,v['spearman'],v['n']] for k,v in data['validation'].items()])+
        '\n\n## Resource ablations\n\n'+overview(abkeys)+
        '\n\nA1 BP only; A2 donors only; A3 rare only; A4 BP+donors; A5 donors+rare; '
        'A6 BP+rare; A7 all three. Catalog/Junk and fixed pickups remain enabled in these '
        'ablations, so “only” describes the three switched progression systems, not all resources. '
        'These tests include policy adaptation and feedback; they are not additive decompositions.\n\n'
        'All new campaign runs check accounting and inventory invariants. Unit tests cover snapshot '
        'isolation, mixed-timing caching, tied ranks, transfers, loot and ledger behavior. '
        'Combat uses fitted enemy damage, simplified movement, and no armor-defense mitigation. '
        'The random stream is seeded by campaign, but different state-dependent cascade paths '
        'consume different draws. This matches seeds and encounter opportunities, not identical '
        'rewards across policies. Priority runtime measurements: refill while firing, animation '
        'time per shot, real shotgun distance/risk, armor mitigation, and acquisition timing.')

    write('L','conclusions','Integrated conclusions and next decisions',
        overview(['overlap|A','overlap|C','overlap|G','overlap|controlled_shotgun',
                  'serial|C','serial|G','serial|controlled_shotgun'])+
        '\n\nThe corrected optimizer selects MAG in 99/100 overlap campaigns and P90 in all '
        '100 serial campaigns. With the optimizer’s decision rules, the shotgun preference '
        'finishes at 2.73 versus 2.40 seconds under overlap and 5.29 versus 4.19 under serial '
        '(benchmark means over 40 seeds). Its gap is smaller than the older weighted-BP '
        'shotgun specialist’s, so player decision rules explain part of the apparent class deficit. '
        'These comparisons retain differences in earned resources and available gear.\n\n'
        'The no-BP-bullets specialist reaches at least eight M10B rounds in 100/100 seeds '
        'under each timing model, and at least twelve in 99/100. All first M10B observations '
        'are in Disc2 in this acquisition model. This supports later customization availability '
        'but cannot establish early comfort or an early-game need for an extra built-in round. '
        'Conditional checkpoint proximity improves that specialist’s late benchmark by '
        '0.55 ± 0.02 seconds under overlap and 0.68 ± 0.06 under serial, while its progression '
        'feedback remains unchanged.\n\n'
        '\n\n## Decisions supported now\n\n'
        '- Use these corrected checkpoint results in place of the original combat tables.\n'
        '- Preserve the BP, donor, Tool and rare systems; they provide distinct resource routes.\n'
        '- Defer a permanent M10B Bullet +1 until acquisition and opportunity-cost findings are '
        'checked against actual play. Final specialist capacity is not evidence of early comfort.\n'
        '- Defer P90/MAG changes until timing is measured. Their rankings depend on that assumption.\n'
        '- Keep shotgun proximity experimental and measure risk and distance before selecting values.\n\n'
        '## Coverage and unresolved questions\n\n'
        'Reports C–G quantify modeled BP availability, spending competition, capacity behavior, '
        'gear/Tool flows, rare feedback, provenance, and magazine milestones. Reports H–J compare '
        'class preferences, two-weapon components, mod frequency, and S0–S4. Report K documents '
        'correctness checks, ablations and uncertainty.\n\n'
        'The following original questions remain only partially answered: exact useful donor-gun '
        'counts (the inherited counter includes armor/offered gear), mandatory Commands/Quickdraw '
        '(no matched removal experiment), a true two-weapon battle strategy, direct defense/capacity '
        'utility in real play, all individual named-gun rankings, and full-campaign proximity effects. '
        'Simulation does not establish whether rare rewards make experimentation feel affordable '
        'to humans or whether farming is enjoyable. Those require controlled follow-ups and playtests.\n\n'
        '## Reproduce\n\nFrom the repository tools directory, run:\n\n'
        '```powershell\n'
        "$simPython = 'C:\\Users\\maver\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe'\n"
        '& $simPython -m unittest discover -s pe_weapon_sim/tests\n'
        '& $simPython -m pe_weapon_sim.economy.run_completion --n 100 --bench 40 --workers 4\n'
        '& $simPython -m pe_weapon_sim.economy.report_completion\n```\n\n'
        'Raw JSON stores seed-level checkpoint states, benchmarks, milestone provenance, paired '
        'differences, experiment specifications and source hashes. Original results are preserved. '
        'No live game source, binaries or saves were changed.')
    for name in files:
        print('wrote',name)


if __name__ == '__main__':
    main()
