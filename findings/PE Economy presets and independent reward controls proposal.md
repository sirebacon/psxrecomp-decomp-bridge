# PE Economy: playstyle presets and independent reward controls

Status: design proposal; no gameplay or balance changes implemented.

Date: October 30, 2026.

Audience: developers, reviewers, translators, and AI assistants helping implement the native PC mod.

Planning tracker: [Master checklist and document register](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets and Menu Organization - Master Checklist.md>). Use it to track decisions, required documents, implementation, and verification; written proposals are not completed features.

Pre-implementation review: [Open conflicts, missing contracts, and readiness gates](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets and Mod Extensions - Pre-implementation Review.md>). REV-01–12 remain unresolved design work, not accepted implementation policies. Resolve the gates relevant to the selected delivery slice before coding; the proposal is not yet a complete executable specification.

Scoped follow-up drafts now exist: [D2 controls/menu inventory](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Control Inventory and Menu Map.md>), [D3 persistence/migration](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Persistence and Migration Design.md>), and [D6 small API contract](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Mod Extensions - API and Cooperation Contract.md>). They distinguish observed source facts from recommended policies. Proposed refinements include one combined new settings/progress record, restricted initial storage combinations, and explicit redemption/price/queue behavior. These do not silently supersede broader choices here: review/accept them and update the relevant D1 sections before implementation. [D4's scoped validation/playtest plan](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Validation and Playtest Record.md>) is now created, with no executed results. Policy bindings, target hardware/numeric budgets, and host prerequisites remain outstanding.

Scope note: although this document began with Economy, Sections 13–20 cover independent presets, menu organization, a shared extension framework, race-condition protections, low-powered-machine performance, memory/resource leak prevention, small capability APIs with coordinated Randomizer/overhaul support, and custom content with shop contributions for **all current and future mods**. Economy is the proposed first implementation of that framework, not its architectural boundary.

## 1. Confirmed direction

**Enhanced remains the default.** New players enabling the economy should continue to receive the existing enhanced experience unless they select another playstyle. Existing saves must retain their current behavior.

Players should also be able to use the Junk counter and inventory-space convenience while retaining vanilla enemy drops, without the mod's additional battle Junk or bonus rare rewards.

The implementation should expose a few understandable presets and independent controls. Internally, the counter, reward generation, bundle redemption, and menu settings should have separate responsibilities.

This document is an implementation proposal, not authorization to change the code or apply new balance values. Section 4 records provisional starting values for playtesting. Section 12 records the six recommended implementation policies; final balance and the remaining engineering details require review and testing. Workshop visibility is a follow-up, outside the initial scope.

## 2. Player feedback and the problem

A player wanted the Junk economy enabled mainly because Junk no longer occupies inventory slots. They also wanted vanilla enemy drops. They reported finding a Super/Duper Junk item that appeared to give roughly 80 Junk, which felt excessive for their preferred run.

The underlying problem is that the current economy switch groups several different features together:

- Inventory convenience: regular Junk is stored in a counter.
- Additional income: the mod awards extra Junk after battles.
- Additional items: the mod generates bonus rare rewards.
- Bundle redemption: Super Junk and Duper Junk are automatically exchanged for substantial counter amounts.

A player seeking only the first benefit can unintentionally enable the others. The solution is to separate these choices and explain them in ordinary language.

Do not dismiss the feedback on the basis that vanilla Junk is scarce. A player can knowingly prefer slower vanilla progression and still want inventory convenience. This proposal does not assert an exact vanilla Junk drop percentage; that would require a separate review of the native drop tables and encounters.

## 3. Current behavior verified in the native code

The implementation inspected is in `D:/Recomp Games/pe-localization`, on `feat/localization`. Verify the target branch again before coding, because upstream may have moved.

Primary sources:

- `mods/pe_economy/pe_loot.c`: counter, battle income, rare rewards, bundle conversion, settings, and Wayne hand-ins.
- `mods/pe_economy/pe_economy.h`: internal economy calls.
- `mods/host/pe_services.h`: services used by other mods.
- `mods/pe_economy/pe_wayne_refund.c`: separate failed-craft refund feature, currently off by default.
- `mods/host/pe_save.h`: versioned mod-save records and upgrade contracts.

### Ordinary enemy drops

The current reward hook preserves non-Junk entries supplied by the native game. Native Junk is routed into the counter/reward presentation. The mod then adds its own rewards.

Therefore, “vanilla drops enabled” is potentially misleading as a toggle: ordinary native drops are already present. The missing option is **vanilla drops without the added reward systems**.

### Additional battle Junk

With current untouched Normal tuning, the base calculation is:

`1 + floor(battle EXP / 8)`, capped at 12 for ordinary battles or 25 for the mod's boss-fight classification.

Those are caps on the base calculation, not necessarily the final payment. The code then applies a hit-based bonus, the existing difficulty multiplier, and Scavenger where applicable. Native Junk and stolen Junk are accounted for separately.

The current “no-hit” tuning is 25%; the implementation also gives a diminishing bonus for fewer than four recorded hits. If this is exposed more prominently, the description should accurately explain it rather than promise a strictly zero-hit-only condition.

### Bonus rare rewards

The mod has a separate rare-reward roll with increasing chance and a guaranteed-reward mechanism. Its reward selection can produce economy effects, Super Tools, Mod Permits, Super/Duper Junk, Tools, or stat boosters, subject to its existing rules.

Setting only the initial rare percentage to zero does **not** disable this system: chance increases and guarantees can still produce rewards.

### Super Junk and Duper Junk

Current automatic counter values are:

| Item | Junk credited |
| --- | ---: |
| Super Junk | 75 |
| Duper Junk | 150 |

The sweep converts these items from both Aya's inventory and Wayne's storage while the economy is active. Conversion is not limited to bundles generated by the new rare system; it can also affect bundles obtained through native gameplay, including Wayne's crafting results.

The player's reported 80 is not confirmed. Super Junk plus another payment is one possible explanation, but a log or save would be needed to establish what happened. Do not describe 80 as the current configured bundle value.

### Existing difficulty choices

Relaxed, Normal, and Grind currently affect income, rare-reward behavior, and prices together. Normal is the current default. These existing difficulty choices are distinct from the proposed playstyle presets.

## 4. Proposed player-facing presets

The exact labels can be refined during UI review. The following behavior is proposed:

| Playstyle | Regular Junk counter | Extra battle Junk | Bonus rare items | Bonus Super/Duper drops | Super/Duper redemption |
| --- | --- | --- | --- | --- | --- |
| **Enhanced — default** | On | Existing behavior | Existing behavior | Existing behavior | Existing 75 / 150 values |
| **Vanilla drops + inventory QoL** | On | Off | Off | Off | Keep bundles as native items |
| **Light economy** | On | Provisional: 1 ordinary / 3 boss | Off | Off | Provisional: automatically redeem for 10 / 20 Junk |
| **Steady Income** | On | Provisional: 3 ordinary / 10 boss | Off | Off | Off: keep bundles as items |
| **Treasure Hunter** | On | Off | Provisional: 10% per victory, guaranteed by the tenth victory without one | Off | Off: keep bundles as items |
| **Custom** | Player selection | Player selection | Player selection | Player selection | Player selection |

Enhanced remains the confirmed default and its current behavior is unchanged. Light economy, Steady Income, and Treasure Hunter now have suggested starting settings for playtesting. These are not finalized balance values or implemented changes; they remain open to adjustment after discussion and testing.

### Provisional starting values for playtesting

| Setting | Light economy | Steady Income | Treasure Hunter |
| --- | ---: | ---: | ---: |
| Extra Junk per ordinary victory | 1 | 3 | 0 |
| Extra Junk per boss victory | 3 | 10 | 0 |
| Chance of the extra Junk payment | Every victory | Every victory | None |
| Performance bonus | Off | Off | Off |
| Bonus rare-item chance | Off | Off | 10% per victory |
| Increasing chance after a missed roll | Off | Off | Off: the random roll stays at 10% |
| Guaranteed bonus rare item | None | None | By the tenth victory without a bonus |
| Bonus Super Junk drops | Off | Off | Off |
| Bonus Duper Junk drops | Off | Off | Off |
| Automatic Super Junk redemption | On: 10 Junk | Off: keep the item | Off: keep the item |
| Automatic Duper Junk redemption | On: 20 Junk | Off: keep the item | Off: keep the item |
| Empty-steal compensation | Off | Off | Off |

Interpretation and boundaries:

- All native enemy drops remain unchanged. These settings govern additions and conversion, not native drop percentages.
- The boss Junk payment replaces the ordinary payment; the two do not stack. Use the existing boss classification initially and verify its behavior during testing.
- The suggested extra Junk payments are fixed base amounts, not EXP-based calculations. Figures in this table are before equipment modifiers. Apply the recommended Scavenger/Lucky Find policy below; disabled reward systems must remain disabled even with those effects equipped.
- Successful native steals of ordinary Junk still route the actual Junk into the counter. Disabling empty-steal compensation only removes the extra award for stealing from an empty enemy.
- Shop prices remain separate. Do not change Enhanced's prices, difficulty multipliers, guarantees, bundle values, or existing reward calculations to implement these new starting settings.
- Redemption off means the item remains available with its native behavior, not that it is consumed for zero Junk. Applying Steady Income or Treasure Hunter should initialize prospective redemption values to 10/20 while leaving redemption off. Show those inactive values before the player enables Custom redemption. Manual off/on toggles preserve the player's configured values; existing Enhanced settings retain 75/150.

### Equipment modifiers and small payments

Keep equipped effects meaningful within enabled reward systems. Scavenger should retain its 50% increase to extra battle Junk; Lucky Find should retain its effect on bonus-reward guarantee progress. Neither effect should enable rewards that the chosen settings disable. Equipment effects are distinct from the performance bonus, which remains off in the three new playtest configurations.

For the new configurable reward path, carry fractional Scavenger bonuses forward rather than rounding them away on every small payment. For example, a base payment of 1 Junk with a 50% bonus alternates between 1 and 2 Junk, averaging 1.5. Keep this fractional state with the appropriate save and do not let toggling settings replay or manufacture a payment. Enhanced retains its existing calculation and rounding unchanged.

### Light economy

This starting configuration provides a small currency supplement without bonus item drops. At current standard prices, the extra income alone pays for Medicine 1 after six ordinary victories or a common Catalog effect after ten. Automatic Super/Duper redemption at 10/20 is a modest return compared with Enhanced's unchanged 75/150.

These progression examples exclude native drops, other income, spending, and price discounts. They are arithmetic illustrations, not simulation results or evidence that the preset is already balanced.

### Steady Income

For players who want dependable currency progression without large random reward spikes. This preset proposes regular bonus battle Junk while disabling bonus rare items and bonus Super/Duper drops. Native enemy drops remain unchanged.

Start playtesting at 3 extra Junk for an ordinary victory and 10 for a boss victory, with no performance bonus or random bonus rewards. At current standard Catalog prices, this extra income alone pays for a common effect after four ordinary victories, an intermediate effect after ten, or a premium effect after 27, plus any required Tool. The intended distinction is dependable progress without random reward spikes. Revise the amounts after testing rather than treating them as settled.

### Treasure Hunter

For players who enjoy discovering additional items but want to limit extra currency income. The starting proposal has no extra battle Junk, enables bonus rare items, and disables bonus Super/Duper drops. Native enemy drops remain unchanged.

Start with a flat 10% bonus-item roll per victory. If nine consecutive victories award no bonus, the tenth guarantees one; a successful bonus resets that counter. Ordinary and boss victories each count as one victory, with no separate boss-chance increase proposed initially.

Initially retain the existing eligible non-bundle bonus pool and its item eligibility/selection rules rather than inventing another loot table. In the new configurable path, keep the bonus-item roll separate from the bundle roll as described in Section 12. Enhanced continues to use its existing cascade unchanged. The goal is item discovery, not automatically maximizing rare drops.

With a flat 10% roll and the tenth-victory guarantee, the mathematical average is approximately one bonus per 6.5 victories before equipment modifiers. It is not one per ten on average, because the guarantee raises the effective frequency. For reference, the current untouched Enhanced/Normal calculation averages approximately one bonus per 9.8 victories without Lucky Find/charm effects and with eligible rewards; this is a mathematical comparison, not a proposed change to Enhanced or a full gameplay simulation.

Tools, stat boosters, permits, and effect unlocks can accelerate progression even without extra currency. Playtesting must check the pool's indirect value as well as the visible Junk balance.

For both Steady Income and Treasure Hunter, bundle redemption remains independent of bonus bundle generation. The initial suggestion is to keep native Super/Duper items, including Wayne's crafting results, without automatic redemption. Players can choose otherwise through Custom settings. Shop prices remain separate from the reward presets.

“Enhanced” must preserve the current experience, including applicable Relaxed/Normal/Grind settings. Selecting Enhanced must not silently erase a player's previous difficulty choice or hand-in preference.

“Vanilla drops + inventory QoL” describes the reward policy, not a promise that every other mod has been disabled. Weapon balancing, combat changes, combining, and other independently enabled features remain separate choices.

Changing an individual reward setting should make the playstyle read **Custom**. Selecting a preset should explain which settings it will replace. Merely highlighting a preset must not apply it.

## 5. Proposed Economy menu layout

Keep everyday choices on the main Economy page. Put detailed numeric controls in clearly named subpages rather than requiring players to use Debug.

### Main page

- **Playstyle:** Enhanced / Vanilla drops + inventory QoL / Light economy / Steady Income / Treasure Hunter / Custom.
- **Junk balance:** current amount.
- **Junk uses inventory space:** No / Yes, or an equivalent clearly worded counter toggle.
- **Reward settings:** opens the controls below.
- **Wayne hand-in:** preserves the existing next-gun/all-Junk choice.

Show a short summary of the active configuration. For example:

> Vanilla enemy drops. Junk uses the counter. Extra battle Junk and bonus drops are off.

For Enhanced, say that it adds battle Junk and bonus rewards. Do not require players to infer this from the word “economy.”

### Extra battle Junk

- **Extra battle Junk:** Off / Low / Standard / High / Custom, or a comparably simple amount control.
- **Amount:** an understandable amount or multiplier when Custom is selected.
- **Battle-performance bonus:** independently adjustable, with an accurate explanation of the current hit-based calculation.
- Optional advanced settings: minimum payment, EXP contribution, ordinary/boss limits, and empty-steal compensation.

The starting presets use fixed payments on every victory. Any custom bonus-frequency control must describe its percentage as a chance per won battle and must not change native drop tables. Named controls and Advanced numeric controls must edit the same underlying settings.

### Bonus drops

- **Bonus rare items:** On / Off.
- **Bonus rare frequency:** Off / Low / Standard / Frequent / Custom, with the numeric behavior explained.
- **Advanced frequency:** exact chance per won battle, editing the same underlying setting as the named choice.
- **Guaranteed bonus rewards:** show the guarantee interval separately, because it raises effective reward frequency.
- **Super Junk bonus drops:** On / Off, with its own configurable per-victory probability.
- **Duper Junk bonus drops:** On / Off, with its own configurable per-victory probability.

Suggested explanation:

> These are additional mod rewards. Turning them off does not remove normal enemy drops.

“Bonus rare items” should refer to the non-bundle bonus pool. Super/Duper bundle generation should have its own controls, so players do not need to guess which category contains them.

Enhanced keeps its shared cascade. The new configurable path uses independent bonus-item and bundle reward families. Super/Duper outcomes are mutually exclusive within the bundle roll, and their combined probability must not exceed 100%. Disabling a bundle category leaves its probability as “no bundle”; it must not redistribute that probability to another reward. Custom can consequently award one bonus item and one bundle in the same victory. See Section 12 for compatibility and pending-reward requirements.

### Super/Duper redemption

- **Automatically redeem Super/Duper Junk:** On / Off; separate toggles may be preferable if players want different behavior for each.
- **Super Junk value:** adjustable Junk amount.
- **Duper Junk value:** adjustable Junk amount.

Suggested explanation:

> Applies to bundles in your inventory or storage, including Wayne's crafting results. Drop frequency is configured separately.

When redemption is off, keep the actual item and its native behavior. Do not consume it for zero Junk, silently delete it, or treat it as one ordinary Junk.

Keep the basic preview visible: “Super Junk → 75 Junk” or “Super Junk stays as an item.” When redemption is off, also show the prospective value, such as “Off; enabling would redeem for 10 Junk.” Enabling it should mark the configuration Custom and apply the displayed value. Manual toggles must not reset edited amounts.

## 6. Rules that must remain independent

### Native drops versus bonus rewards

Turning off bonus rewards must not remove native Tools, boosters, Junk, or other drops just because an equivalent item also exists in a bonus pool. The implementation must distinguish rewards by origin, not suppress all matching item IDs.

Counter-only mode should move a native Junk unit into the counter as one Junk, without multiplying its value or increasing how often it appears.

### Bonus generation versus redemption

These are separate operations. Disabling new Super/Duper drops must not remove Wayne's native crafting outcomes or prevent the player keeping an existing bundle. Disabling automatic redemption must not automatically disable bundle drops.

### Counter versus additional income

The wallet/counter and Wayne's normal hand-in integration must work when all added reward systems are off. Other mods should not assume that an available `junk` service means bonus battle income or rare rewards are enabled.

Empty-steal compensation is additional income and should be off in the Vanilla-drops, Light economy, Steady Income, and Treasure Hunter presets. A successful native steal of ordinary Junk should still route that actual Junk into the counter.

Scavenger and Lucky Find must not bypass disabled reward systems. Preserve the effects on the equipment, but explain when their corresponding bonus system is inactive.

### Rewards versus shop prices and services

Selecting a reward playstyle should not unexpectedly change shop prices, difficulty, owned effects, recipes, or Workshop availability. Keep Relaxed/Normal/Grind as an advanced legacy option for Enhanced and existing saves, with an explanation that it currently changes income, rare rewards, and prices together. The new presets use their own explicit reward settings; do not apply a legacy income multiplier a second time to their fixed payments. Preserve current shop prices until the player explicitly changes them.

**Workshop-service visibility is a follow-up, outside the initial implementation.** Existing enabled services remain available when a reward preset changes. Describe the Vanilla-drops preset as a reward/storage policy so players do not infer that it also hides shops. A future separate Workshop-services switch may hide added services while retaining the counter and native Wayne hand-ins.

Someone wanting only counter convenience should still be able to use native Wayne hand-ins. Someone enabling Catalog/Dismantle/Rebuild can still deliberately earn or spend Junk through those services; this preset alone is not a claim of completely vanilla progression.

Do not change Dismantle/Rebuild anti-exploit protections as part of this work.

## 7. Disabled systems, guarantees, and pending rewards

Review caveat: the strict policy below is intended for the new configurable path. Preserve legacy Enhanced behavior separately; its carried-effect replacement is an existing exception that must be specified in the transition/lifecycle design. See REV-02 and REV-06 in the linked pre-implementation review. Switching paths, guarantee reset timing, and full-queue handling are not yet finalized.

“Off” must be complete and predictable:

- No new bonus rolls for the disabled system.
- No guaranteed bonus reward leaking through while it is off.
- No previously queued reward being delivered while its category is disabled.
- No accumulation of new disabled-system rewards to pay out when re-enabled.

Recommended policy: freeze existing guarantee progress for a disabled category and preserve an already pending reward, without delivering it until its category is allowed again. Resume that progress when re-enabled. Do not generate new rewards from the disabled category or accumulate a backlog. This avoids deleting earned progress or using toggle changes to reset reward counters.

Apply reward-policy changes between battles. An already generated reward must not be rerolled, duplicated, or silently converted into another reward by a preset change. Preserve its identity when settings change. For the new path, settle a bounded pending-reward capacity and the full-queue behavior during engineering review, including mixed enabled/disabled categories. Enhanced's existing reward-generation and queue behavior remain unchanged; compatibility tests must distinguish that legacy path from the new configurable one.

## 8. Persistence and existing saves

Review caveat: the inspected host may omit carried inactive/unknown records when the save container is full. New records must not rely on unconditional preservation merely because registration succeeds. Normal save and crash-capture coherence also need separate contracts. See REV-01, REV-08, and REV-09 in the pre-implementation review before allocating or migrating state.

- Keep Enhanced as the default for new economy settings.
- An older save without the new settings must reproduce its existing enhanced behavior and difficulty choice.
- Preserve the Junk balance, rare progress, queued rewards, economy-effect progress, Mod Permit progress, and other existing state.
- Keep balances and chosen playstyle with the appropriate playthrough; loading a different save must not inherit another save's reward choices accidentally.
- Keep purely presentational preferences, such as showing the inventory counter, separate from reward rules.
- Applying a preset must not grant Junk, reset a balance, redeem already consumed items, refund previous spending, or replay previous battle rewards.

The current `pe_economy.loot` v1 record is explicitly asserted to be 36 bytes. Do not append fields to it without a versioned upgrade path.

Use a separate versioned reward-settings record to keep the existing wallet/reward state intact, subject to checking the mod-save container's record and byte budgets first. Give any additional configurable-path progress state, such as fractional bonuses and pending rewards, an explicit versioned layout as well. Keep it separate from the legacy Enhanced state. An older save without the new settings record must use its existing Enhanced behavior and difficulty choice; do not reset the wallet or reward progress. If capacity requires a different layout, review that change and its migration before implementation.

## 9. Modular implementation proposal

Use feature ownership rather than one enlarged settings function:

| Responsibility | Owns | Should not own |
| --- | --- | --- |
| Junk wallet | Balance, native Junk collection, spending, storage handling, Wayne hand-ins | Whether a bonus rare item should roll |
| Extra battle Junk | Additional payout calculation and its controls | Native enemy-drop selection |
| Bonus rewards | Allowed categories, probabilities, guarantees, pending rewards | Automatic redemption of collected bundles |
| Bundle redemption | Super/Duper conversion policy, payout, one-time consumption | Whether the bundle should have dropped |
| Presets/settings | Named configurations, Custom detection, persistence, menu summaries | Reimplementing rewards or changing balances directly |
| Presentation | Labels, explanations, source summaries, translation keys | Game rules or saved identifiers |

These can be separate modules inside `pe_economy`; they do not require separate public mods or duplicate counters. Preserve the existing `junk` service contract for consumers unless an explicitly versioned extension is needed.

Add stable localization keys and Latin American Spanish labels alongside the new interface. Do not use translated text as a settings key, saved identifier, or condition in the reward logic.

## 10. Reward feedback

Where practical, identify why the balance changed:

- Native drop: “Junk +1.”
- Additional payout: “Bonus battle Junk +5.”
- Redemption: “Super Junk redeemed: +75 Junk.”

The numbers above illustrate presentation; +5 is not an approved Light-preset reward.

Avoid adding several mandatory popups after every fight. A concise reward breakdown or a single summary is preferable; detailed sources can remain in the log. The menu should let players see bundle values before collecting or redeeming one.

## 11. Validation plan

Keep new tests, fixtures, disposable saves, simulations, logs, and captures local in `D:/Recomp Games/pe-native-debug`. Production modules and documentation belong in the game repository.

Required checks before release:

1. **Enhanced compatibility:** untouched new defaults and migrated saves reproduce the current payout, bonus-reward, bundle-value, price, and hand-in behavior.
2. **Vanilla reward parity:** fixed encounters produce the same native reward items/counts with the Vanilla-drops preset, apart from regular Junk's storage/presentation. No extra rolls, compensation, or modifiers introduce additional rewards.
3. **Counter-only use:** pickups, storage, successful Junk steals, full inventory, save/load, and native Wayne hand-ins work without added battle income or bonus drops.
4. **Independent switches:** rare items, Super Junk, and Duper Junk can be enabled/disabled as advertised. Native rewards of the same IDs are not filtered out.
5. **Guarantees and pending rewards:** disabled categories never leak a reward; paused progress and pending items survive save/load and resume under the documented rules.
6. **Bundle conversion:** inventory/storage conversion consumes each item exactly once and credits the configured amount. Redemption off preserves the item. Changing values does not retroactively change money already credited.
7. **No duplication:** toggling settings, changing presets, loading saves, handing Junk to Wayne, or equipping/unequipping economic effects cannot replay a payment or create an infinite-Junk route.
8. **Existing protections:** Dismantle/Rebuild provenance and anti-refund-exploit behavior remain intact.
9. **Menu clarity:** presets, Custom state, current values, disabled explanations, and summaries are readable in English and Spanish without clipping. Browsing/highlighting settings must not accidentally apply them.
10. **Balance review:** use Section 4's provisional settings as playtest candidates, not final balance. Compare income/progression and reward variability for Light economy, Steady Income, and Treasure Hunter. Verify that Steady Income reduces bonus reward spikes and Treasure Hunter emphasizes item discovery without unintended currency or upgrade inflation. Measure actual bonus intervals and guarantee resets. Enhanced's current settings and 75/150 redemption values must remain unchanged.
11. **New-path modifiers and controls:** verify fractional Scavenger payouts across multiple victories and save/load; Lucky Find affects enabled bonus guarantee progress only. Named and Advanced frequency controls stay synchronized. Enabling redemption uses the displayed inactive value, and manual toggles preserve edits.
12. **Independent reward families:** test simultaneous bonus-item and bundle awards in Custom, mutually exclusive Super/Duper outcomes, probability limits, disabled categories retaining their “no bundle” outcome, bounded pending rewards, and between-battle application of settings. None of these changes may alter Enhanced's existing cascade, rounding, or queue behavior.

## 12. Six implementation recommendations

These recommendations define the proposed first implementation. They do not authorize code changes or make the starting numbers final balance values.

1. **Use the provisional starting settings and preserve meaningful equipment effects.** Begin with Section 4's amounts, disabled performance bonuses and empty-steal compensation, and Treasure Hunter's 10%/tenth-victory settings. Apply Scavenger and Lucky Find only to their enabled systems. Carry fractional Scavenger bonuses forward in the new path, while retaining Enhanced's original rounding. Applying Steady Income or Treasure Hunter sets prospective bundle values to 10/20 with redemption off. Show those values before enabling Custom redemption; manual toggles preserve edits. Enhanced and existing Enhanced saves keep their current values.
2. **Provide named frequencies and an Advanced numeric view.** Offer Off / Low / Standard / Frequent / Custom, explain each profile, and expose exact per-won-battle percentages and guarantee intervals in Advanced. Both views edit one canonical configuration. Guarantees are shown separately because they change effective frequency. Numeric mappings for the additional named profiles still need playtest design; do not invent or hard-code them silently.
3. **Preserve the Enhanced cascade and separate the new reward families.** Enhanced uses its existing generation path unchanged. The configurable path has a bonus-item roll and a separate bundle roll; the latter selects Super, Duper, or neither. Super/Duper probabilities are mutually exclusive and must total at most 100%; disabling either leaves its probability as no bundle. Custom can award one item plus one bundle in a victory. Initially preserve the existing non-bundle pool's item eligibility and selection rules. The three new starting presets disable bonus bundles, so their initial tests produce no simultaneous item/bundle awards.
4. **Retain legacy difficulty as an advanced compatibility option.** Keep Relaxed/Normal/Grind for Enhanced and existing saves, explaining its combined effects. Give the new presets explicit reward settings and keep shop prices separate. Preserve current prices on playstyle changes, and prevent the legacy income multiplier from being applied again to fixed payments. Any intentional change to a legacy difficulty choice must explain its price/reward effects before applying it.
5. **Leave Workshop visibility for a follow-up.** The first implementation changes reward controls, not service visibility. Preserve enabled Workshop services, the counter, and native Wayne hand-ins. A later, independent service-visibility switch can support players who want to hide added shops without losing inventory convenience.
6. **Use versioned settings and freeze disabled progress.** Add a separate per-save settings record after checking capacity; preserve the current wallet/reward record and use legacy Enhanced behavior for older saves with no new settings. Freeze disabled guarantee progress, retain pending reward identities, and resume when allowed. Deliver no disabled-category rewards and accumulate no new disabled rewards. Use bounded pending storage, apply policy changes between battles, and never reroll an already generated reward during a preset change.

### Remaining refinements before coding

- Review the proposed starting values as a playtest baseline; final balancing remains open.
- Specify the numeric mappings for Low / Standard / Frequent and the allowed custom input ranges.
- Verify the existing Scavenger/Lucky Find descriptions and document how actual modifiers affect the displayed base settings.
- Check save-container capacity and finalize the new records' layouts and migration behavior, including fractional progress and pending-reward capacity/full-queue behavior.
- Define and test how advanced legacy tuning and separate shop-price choices are presented and preserved across playstyle changes, without changing untouched Enhanced behavior.

Workshop visibility remains a follow-up. **Enhanced remains the default and unchanged. No game code has been changed by this proposal.**

## 13. Future presets for other mod categories

The following ideas extend the same approach beyond Economy. They are planning proposals, not implemented features or approval to change balance. Each category owns its settings independently. Adding these options must preserve all current defaults and existing player settings; it must not automatically select a new profile on an existing save or installation. Enhanced remains the Economy default.

### Shared behavior and boundaries

- Keep a separate preset selector for each category. A Combat preset must not change Economy, encounters, movement, inventory, or collection preferences. Avoid a global Easy/Hard profile that silently changes several systems.
- A separately selected Randomizer/overhaul package may explicitly coordinate several categories under Section 19's preview, consent, conflict, and save-compatibility rules. This is distinct from an ordinary category preset; it must never be applied implicitly by that preset.
- Show the current settings and a short preview of exactly what selecting a preset will replace. Highlighting or browsing a preset must not apply it.
- Editing an individual setting makes only its own category read **Custom**. Categories without editable combinations do not need a Custom label merely for consistency.
- Treat named presets as convenient configurations of existing controls, not competing sources of settings. Use stable identifiers and translated labels; never save translated names as identifiers.
- Preserve each feature's existing persistence scope. Review save-specific rules separately from installation/profile presentation preferences. Do not move settings between those scopes without an explicit migration plan.
- A preset must not grant or reset possessions, effect unlocks, outfit ownership, Bestiary progress, or other earned state. Keep testing unlock/reset tools separate.
- Missing or newly added preset metadata must leave existing settings intact. Recognize a named configuration only when its owned settings match; otherwise show Custom without rewriting values.
- The new Economy work remains the first scope. These additional categories can be designed and implemented separately after review; none is a prerequisite for counter-only Economy use.

### Combat

Suggested choices: **Original Rules / Rebalanced / Custom**. The current mod already exposes Vanilla/Rebalanced/Custom choices for effect rules and PE balance. Review their exact ownership before grouping them under a clearer Combat page; do not introduce a second conflicting selector or assume that every combat module has identical rules.

| Proposed choice | Intended purpose | Boundary |
| --- | --- | --- |
| Original Rules | Select the available original-rule options for the combat controls explicitly listed in the preview | Does not promise to remove stored weapon upgrades or disable every mod |
| Rebalanced | Coordinate the currently enabled combat rebalance defaults | Preserve current behavior; do not add new buffs, nerfs, or PE-cost changes through this proposal |
| Custom | Let players adjust supported combat controls individually | Changes only the listed combat settings |

Define “Original Rules” carefully before implementation. Weapon attack bonuses or upgrades can already be stored in equipment/save data. Selecting a rules preset must not subtract guessed bonuses, rewrite equipment, or erase earned upgrades. If a balance component cannot be switched safely, explain that limitation and keep it outside the preset until a separate migration design is approved. The Weapon power (DPS) option is a display setting, not a weapon-balance switch, and should remain independent.

A possible future **Assisted Combat** configuration would require a separate balance discussion, concrete settings, and testing. No assistance values are proposed or approved here. Combat presets must not alter random-encounter frequency, enemy-group size, reward income, or shop prices.

### Encounters

Suggested choices: **Story Focus / Original Frequency / More Encounters / Custom**.

| Proposed choice | Intended behavior |
| --- | --- |
| Story Focus | Disable random battles while preserving scripted and required encounters |
| Original Frequency | Use the existing native-frequency option |
| More Encounters | Select a reviewed existing higher-frequency option; determine the exact mapping before implementation |
| Custom | Expose the existing encounter controls and clearly explain any random-battles-off override |

The current implementation has a frequency selector and a separate no-random-battles override. Presets should coordinate those controls without changing encounter logic. More encounters means more frequent random battles, not larger enemy groups, different enemy compositions, or stronger enemies. Keep battle rewards independent even though fighting more often naturally produces more rewards over time. Verify scripted fights and story progression before advertising Story Focus as safe for a complete playthrough.

### Movement

Suggested choices: **Original / Comfort / Fast Exploration / Custom**.

| Proposed choice | Intended behavior |
| --- | --- |
| Original | Use the original values for the movement controls explicitly covered by this preset |
| Comfort | Match the current mod defaults for those controls |
| Fast Exploration | Offer faster field movement and, if appropriate, battle-entry movement while preserving the player's combat-movement setting |
| Custom | Allow individual movement controls to be adjusted |

The existing controls include Always run, Run speed, Walk speed, Combat speed, and Battle start speed. Record their current defaults from the target branch before defining the preset table. Do not invent speed multipliers or change current defaults as part of this proposal. Separate field movement from combat movement in the interface and preview; Fast Exploration must not silently make Aya faster during combat. Decide whether battle-entry speed belongs in that preset only after checking how it behaves.

### Inventory convenience

Suggested choices: **Manual Organization / Convenient Inventory / Custom**.

| Proposed choice | Intended behavior |
| --- | --- |
| Manual Organization | Disable automatic organization while retaining explicitly chosen manual actions |
| Convenient Inventory | Coordinate the current inventory-convenience defaults, with each included feature listed |
| Custom | Let players choose supported convenience options separately |

Start with existing inventory controls, such as remembered automatic sorting and inventory tips; review the precise included features before implementation. Preserve manual sorting and the existing behavior in which manually moving items turns automatic sorting off. A presentation option, such as displaying the Junk count, must not enable bonus income or change rewards.

The Junk storage policy belongs to the independent Economy/counter controls described earlier. An Inventory preset should not duplicate or silently change that policy. If the Inventory page links to the counter control, show that it is the same underlying setting and explain any change explicitly. Any future transition between pocket items and a counter must preserve the full balance and handle a full inventory without loss, duplication, or forced conversion. Ownership and existing equipment must remain unchanged.

### Bestiary presentation

Possible presentation choices: **Spoiler-Free / Standard / Reference**.

| Proposed choice | Intended purpose |
| --- | --- |
| Spoiler-Free | Hide undiscovered identities and details according to a reviewed discovery policy |
| Standard | Preserve the current Bestiary presentation defaults |
| Reference | Make already available reference information easier to browse without granting discovery or ownership |

Define exactly which names, models, descriptions, statistics, and locked entries each choice reveals before implementation. A presentation mode must not mark enemies as met, complete entries, unlock rewards, make purchases, or reset progress. If Reference would reveal undiscovered information, identify that explicitly as a spoiler-view choice and obtain a design decision; do not silently bypass discovery rules. Keep the existing Show all / met / not complete filter independent unless the preview explicitly includes it. Model rotation and animation controls remain ordinary viewer preferences.

### Wardrobe presentation

Phase 1 update, November 2: D8 §12 fixes the standalone split's acquisition boundary. Wardrobe alone makes all installed compatible costumes available for viewing/wearing. Economy owns an optional **Costume unlock rules** toggle, default on, preserving current unlock/purchase behavior; off restores unrestricted access without granting permanent ownership or disabling other Economy features. Ownership, current prices/sources and the no-buying Wardrobe viewer are preserved. Progression/challenge/acquisition presets belong to later separately reviewed Economy improvements, not phase 1. D2 §10, D3 §16.5, D6 §15.5 and D4 PB-17 define controls/state/API/acceptance; payment safety and remaining split gates are still open. No code or balance changes accompany this decision.

Keep this simpler than Combat or Economy. Suggested choices are **Story Appearance / Owned Outfits**, subject to confirming what the current costume system can support safely.

| Proposed choice | Intended purpose |
| --- | --- |
| Story Appearance | Follow the original story-appropriate appearance where supported, without deleting outfit ownership |
| Owned Outfits | Let the player choose from outfits they already own, preserving the existing selection behavior |

Do not automatically switch players away from their currently selected outfit when adding presets. Preserve current defaults and selection until the player explicitly chooses another mode. Review story transitions and model compatibility before promising automatic story appearance. Wardrobe has no buying functionality in this design.

Keep outfit filters, initial model-facing direction, rotation, and animation playback controls separate from outfit ownership. Unlock-all and reset buttons are testing tools, not player presets. Bestiary and Wardrobe use shared collection-profile state (`pe_collection.ini` in the inspected implementation); presentation changes must not grant, reset, or migrate that state accidentally.

### Suggested order and review checks

After the Economy design, prioritize **Combat → Encounters → Movement → Inventory**, with Bestiary and Wardrobe presentation as later, independent work. This is a suggested planning order, not authorization to implement these categories together.

Before implementing each category:

1. Inventory its existing controls, exact defaults, persistence scope, and module ownership on the target branch.
2. Define the preset-to-setting table and confirm that every label accurately describes its effects. Leave unreviewed numeric mappings open rather than silently selecting values.
3. Verify that untouched installations and existing saves retain their behavior, including configurations that match no named preset.
4. Change one category and confirm that every other category retains its settings. Check preview, explicit application, and category-local Custom detection.
5. Verify that preset changes preserve equipment, balances, unlocks, collection progress, and save data, with no replayed rewards or duplicated items.
6. Check readable English and Latin American Spanish labels, controller navigation, and long descriptions. Keep new test suites and fixtures local in `D:/Recomp Games/pe-native-debug`.

**All categories remain independent. Current defaults are preserved. This section adds design ideas only; no game code or balance changes are authorized.**

## 14. Menu organization for presets and individual controls

The proposed controls warrant a menu-organization review before implementation. Players should be able to find a feature by its purpose without knowing which internal mod provides it. Developers should still retain clear module ownership. This section proposes navigation and presentation only: moving a control must not change its value, default, persistence scope, enabled state, or gameplay behavior.

### Separate configuration from in-game actions

Use the mod settings interface (currently reached through F1) for presets and lasting preferences. Keep Aya's in-game menus focused on actions such as installing/removing Catalog effects, viewing the Bestiary, and choosing an owned outfit in Wardrobe. These screens can expose relevant viewer controls, but should not become another copy of the full settings interface.

Keep the Catalog's Tune Up-style presentation and Weapon/Armor selection. Catalog discovery rules still apply: undiscovered effects remain question marks with their details hidden. Reorganizing settings does not authorize exposing those effects, changing purchase/install/remove rules, or adding buying functionality to Wardrobe.

### Proposed player-facing settings order

The following is a starting navigation map, not a requirement to add empty pages. Audit the current menu first, retain unrelated existing settings, and reuse suitable existing pages. Confirm controller and keyboard access before choosing a final layout.

| Order | Category | Contents and ownership |
| --- | --- | --- |
| 1 | Combat | Combat rules preset, supported effect/PE rule controls, and links to advanced combat settings |
| 2 | Encounters | Encounter preset, random-battle frequency, and the random-battles-off control |
| 3 | Movement | Movement preset, field movement, combat movement, and battle-entry movement, clearly distinguished |
| 4 | Inventory | Inventory preset, automatic sorting, tips, and inventory display preferences; link to the Economy counter policy |
| 5 | Economy | Enhanced/default and other reward presets, Junk storage policy, battle income, bonus drops, bundle redemption, and existing Wayne preferences |
| 6 | Collection | Separate Bestiary and Wardrobe presentation pages; keep their choices independent |
| 7 | Language and Display | Language selection and existing display preferences, including the display-only weapon DPS option where appropriate |
| 8 | Manage Mods | Existing mod enable/disable and restart information; preserve access to this page |
| 9 | Developer Tools | Existing testing, logging, unlock/reset, and diagnostic controls, clearly separated from normal play preferences |

This grouping does not introduce a global preset. Combat and Encounters remain separate even though they appear next to each other. Bestiary and Wardrobe remain separate inside Collection. Preserve the current availability of Developer Tools; this proposal does not enable testing tools or authorize new unlock/reset actions.

### Consistent layout within each category

Where supported by that category, use this order:

1. **Current setup:** show the active preset or Custom, followed by a short plain-language summary.
2. **Choose preset:** preview the affected settings and require an explicit Apply action. Merely moving through the choices changes nothing.
3. **Common options:** keep the few frequently used independent controls close at hand.
4. **Advanced settings:** expose detailed values and legacy tuning without making them necessary for ordinary use. Advanced controls edit the same underlying settings as the simpler controls.

Show whether a setting belongs to the loaded save or applies more broadly when that distinction matters. Do not introduce a category-wide Reset that also erases possessions or progress. Any future reset-to-defaults action must list its category-local scope and preserve earned state.

### Economy subpage arrangement

Refine Section 5's layout into a short main page with the preset, active summary, current Junk balance, and links to:

- **Junk Storage:** counter versus inventory policy and its explanation.
- **Battle Income:** ordinary/boss payments, performance bonuses, and related advanced controls.
- **Bonus Drops:** non-bundle bonus items, Super/Duper generation, frequencies, and guarantees.
- **Bundle Redemption:** automatic conversion and the displayed Super/Duper values, including inactive values.
- **Wayne and Pricing:** retain existing Wayne preferences and clearly separate any supported price control from reward settings. Keep the coupled legacy Relaxed/Normal/Grind choice in Advanced with its full explanation; do not invent independent price controls before their behavior is reviewed.

Preserve easy access to the main preset selector. Workshop-service visibility remains a follow-up; no new visibility switch is included in this layout. Enhanced continues to reproduce current behavior.

### One setting, one owner

Each actual setting should have one owning module and one canonical definition. Player-facing categories may assemble controls supplied by different modules without copying their values or business logic into a central menu file. Preset definitions, setting persistence, and translated presentation should remain separate responsibilities as described in Section 9.

Cross-category links should open the owning setting, not create a second independent toggle. For example, Inventory can link to Junk Storage, while the counter policy remains owned by Economy. Inventory's Junk-count display preference remains a separate presentation setting. If two pages deliberately expose the same control, they must use the same backing value and clearly explain the same effect.

Preserve stable setting identifiers and save keys when moving rows. Do not identify controls or route actions solely by their old row numbers. Audit hooks, translations, tests, breadcrumbs, and saved navigation state that may assume a particular order. Preserve valid selection/scroll positions, and fall back safely when a previously selected row no longer exists.

### Navigation and usability review

- Keep category names short, readable, and translated; explain unfamiliar terms in the help area.
- Show a clear page title, selected control, description, and Back action. Returning from a subpage should restore the parent selection and scroll position.
- Keep long descriptions and option lists readable with appropriate scrolling; do not shrink text to fit everything on one page.
- Distinguish a disabled feature from an unavailable dependency. Explain dependencies without silently enabling another mod or changing another category's preset.
- Keep ordinary settings usable without visiting Developer Tools. Place progress-changing test actions away from routine preset selection.
- Verify English and Latin American Spanish layouts, keyboard/controller navigation, long lists, and missing/disabled modules. Reordering must not break Aya's sidebar, Catalog navigation, or collection viewers.

Before implementation, approve a final menu map and a control-ownership inventory against the current branch. The proposed order and subpage names remain open to review. **This is a document-only design extension; existing defaults and independent categories remain unchanged.**

## 15. Mod extension points, hooks, and cooperation between mods

### Purpose and existing foundation

Provide supported extension points so other mods can contribute content, settings, and calculated adjustments without editing PE Enhancements' implementation. Several mods should be able to participate in the same operation with predictable results. This is a proposed extension contract, not a promise that arbitrary mods can modify every internal rule safely.

**The extension framework covers all current and future mods. Economy is only the proposed first implementation.** Combat, Encounters, Movement, Inventory/QoL, Catalog, shops, Wardrobe, Bestiary, localization/presentation, and future content or gameplay mods should use the same shared conventions where they expose extension points. New categories must not require a separate global hook system or depend on Economy merely to register their own extensions.

Framework-wide contracts cover registration identity, service discovery/versioning, lifecycle, deterministic cooperation/conflicts, diagnostics, and save ownership. Each feature module separately owns its typed operations and defines what other mods may observe, register, or influence. Some modules may expose only content registration or notifications; others may support calculation modifiers. Coverage does not mean every module implements every extension type, nor that all modules' APIs are built in the first release. Existing defaults and module independence remain intact.

### Framework-wide coverage and module adoption

The following are candidate extension surfaces to review, not new implemented APIs or authorization to change their rules:

| Module/category | Candidate supported extensions | Owner boundary |
| --- | --- | --- |
| Economy and shops | Reward/price contributions, reward notifications, reward entries, additional presets | Wallet transactions, pricing validation, native-drop eligibility, and disabled-system policy remain owner-controlled |
| Combat and Encounters | Supported combat calculations, encounter-policy contributions, battle notifications, category presets | Preserve combat/encounter separation, required fights, and stored equipment upgrades |
| Movement and Inventory/QoL | Supported movement adjustments, organization policies, action notifications, category presets | Preserve field/combat scope, item integrity, and the canonical owner of each setting |
| Catalog and custom equipment/items | Effect/content registration and supported install/remove notifications or validation | Discovery, stable identities, consumption, provenance, and save/editor compatibility require explicit contracts |
| Wardrobe and Bestiary | Costume/creature registration, viewer contributions, outfit/discovery notifications | Preserve ownership, unlock rules, profile progress, and missing-content behavior; no Wardrobe buying is added |
| Localization and presentation | Registered labels/descriptions, category controls, viewer/display extensions | Keep translation keys separate from saved identifiers and game rules; define provider precedence explicitly |
| Future mods/categories | New owner-published, versioned services and typed extension points using the shared conventions | Declare capabilities and dependencies; no automatic access to unrelated internals or player state |

Track adoption per module: existing interfaces to preserve, proposed extension points, supported versions, dependencies, owner, status, and validation evidence. Reuse existing Bestiary/costume registration rather than replacing working APIs solely to make them look uniform. Economy-specific reward formulas and eligibility rules must stay in Economy; they are examples of the shared cooperation model, not global rules for every mod.

The inspected `pe-localization` checkout already provides a foundation:

- [Host API](<D:/Recomp Games/pe-localization/mods/host/pe_mod_host.h>): `pe_hook_add`, priority-ordered callbacks, named events through `pe_event_id`/`pe_event_emit`, named/versioned services through `pe_service_publish`/`pe_service_get`, and dependency-ordered initialization.
- [Shared services](<D:/Recomp Games/pe-localization/mods/host/pe_services.h>): Junk, Catalog, key items, Wardrobe, Bestiary, and costume interfaces, including creature/costume registration and collection notifications.

These references establish existing mechanisms, not the new extension API described below. Recheck the target branch before implementation. A published service is an interface offered by an owner; supporting multiple contributors requires a registration contract inside that interface, rather than having multiple mods overwrite the same service. Existing hook priority alone does not settle arithmetic, veto, replacement, or notification rules.

### Three distinct extension contracts

| Kind | Examples | Required boundary |
| --- | --- | --- |
| Content/configuration registration | Add an Economy preset, reward-pool entry, costume, or eventually Catalog effect | Validate namespaced IDs, dependencies, limits, and metadata; registration does not grant ownership or automatically select a preset |
| Calculation contributions | Add a battle-Junk amount, multiply an eligible payment, or propose a supported price/chance adjustment | Contribute to an owner-controlled calculation; do not credit the wallet, consume items, or rewrite saved settings from the callback |
| Notifications | Observe a committed reward, outfit change, or successful effect installation | Post-operation observation; cannot alter the completed transaction, replay it, or veto it retroactively |

Keep these contracts separate. A generic mutable “anything changed” event is insufficient. Define typed payloads for each operation, including valid inputs, units, result status, ownership, and lifetime. The same host event machinery may carry them, but notification subscribers should receive an observational contract rather than a mutable reward buffer. This is a cooperation API, not process isolation from arbitrary native code.

### Multiple contributors and a single transaction owner

The owning module remains responsible for the authoritative operation. Economy validates eligibility, computes rewards, and credits its wallet once. A price adjustment does not itself spend money; Catalog installation does not let every listener consume a Tool. Other mods return contributions through the defined extension surface.

Proposed calculation stages for the new configurable Economy path:

1. **Eligibility:** determine the reward's origin and whether its category is enabled. Disabled bonus income remains disabled even if a contributor supplies a positive bonus. Keep native drops separate.
2. **Base calculation:** compute the owner's configured amount, including its documented equipment rules.
3. **External contributions:** gather validated additions and multipliers for that operation. Contributors receive a stable base/context snapshot and submit declared contributions; they do not depend on another contributor's incidental callback execution order.
4. **Resolution:** combine contributions using the published operation-specific formula, perform defined rounding/fraction handling, and apply owner-enforced limits.
5. **Commit:** the owner applies the final transaction exactly once, preserving source/provenance information needed by pending rewards and anti-exploit rules.
6. **Notification:** emit the completed result and source breakdown. Observers cannot restart the same transaction through this notification path.

Illustrative formula only: owner base 10 Junk, mod A adds 2, mod B multiplies by 1.5; an agreed “add, then multiply” policy gives `(10 + 2) × 1.5 = 18`. This is not an approved balance change or a global formula for prices, chances, damage, or equipment bonuses. Each operation needs its own reviewed formula, integer/fixed-point representation, rounding, overflow handling, and bounds. Preserve Section 4's fractional-Scavenger policy and Enhanced's original rounding.

Use a deterministic composition rule for additive/multiplicative contributions. Where a resolver truly needs sequential callbacks, define priority plus a stable tie-breaker, such as contributor ID, rather than relying on registration timing. State which order is observable. Do not let load order silently decide the result.

### Conflict and authority rules

- **Add/multiply:** declare supported contribution types and ranges per operation; reject invalid values, overflow, or unsupported combinations with an attributable diagnostic.
- **Limits:** owner-enforced bounds and player-disabled categories cannot be bypassed by ordinary modifiers. Define any contributor-supplied lower/upper limits and contradictory-limit policy before exposing them; omit that capability from the first version if unresolved.
- **Replacement/exclusive override:** reserve for explicit contracts. Two incompatible replacements must produce a visible conflict and a documented fallback or user choice. Do not silently select the last registered provider.
- **Veto:** restrict to named, documented pre-operation validation points where cancellation is safe. Define who may veto and what the player sees. A completed payment or item consumption cannot be vetoed afterward.
- **Names:** use stable namespaced IDs for providers, registrations, presets, and content. Reject duplicate IDs unless an explicit replacement API and ownership policy allow them.
- **Player authority:** selecting a preset changes only its category's stored settings. A modifier cannot silently switch presets, enable a disabled system, reveal undiscovered content, grant outfits, or reset progress. Deliberate content grants require a separate existing/approved action API.
- **Reentrancy:** prevent callbacks from recursively executing the same reward/spend/installation operation. Notifications do not form an alternate payment route. Specify failure behavior and prohibit side effects in calculation callbacks; a crash in arbitrary native code is outside this contract's protection.

### Presets, menus, and effective values

Keep the player's chosen configuration separate from temporary external contributions. For example, display **“Steady Income · modified by 2 mods”** rather than overwriting the preset or storing the modified amount as its base setting. Manual edits to owned settings still trigger category-local Custom detection. Selecting a preset does not unregister other mods' contributions.

A diagnostic breakdown should identify the owner/base, each contributing mod and operation, rejected/conflicting contributions, and final effective value. Normal menus can show a concise summary and a link to that breakdown. Explain when a contribution is inactive because its reward category is off. Do not expose undiscovered Catalog effects through diagnostics or previews.

Additional presets register against one category with stable IDs, supported setting fields, dependency information, and localized labels/descriptions. Reject cross-category or unsupported fields. Registration does not apply the preset; preview and explicit application remain required. Provider-supplied settings controls belong to that provider and can appear under the relevant category through the menu registration mechanism. Do not duplicate backing values in a central settings module.

### Lifecycle, compatibility, and saves

Version extension services/payloads explicitly. Document required versus optional dependencies, callback/data lifetimes, thread/reentrancy constraints, registration capacity, error returns, and startup/shutdown ownership. Give new interfaces explicit size/capability negotiation where appropriate; do not assume that incrementally appending fields to an existing v1 table is safe for every consumer. Preserve existing public services or introduce a separately versioned extension interface.

Respect the host's actual activation model. An inactive contributor must not continue influencing calculations. If the host does not support safe runtime unloading, require its existing restart flow rather than promising hot removal. Use owner-scoped registrations and cleanup so disabling/restarting cannot leave stale callbacks, pointers, duplicate contributions, or duplicated menu rows. Snapshot the eligible contributors/policy for an in-flight operation; changes take effect at the documented safe boundary.

Save only the state that needs persistence: stable IDs, player settings, and versioned progress, never pointers or callback registration order. Recompute effective values without compounding yesterday's modifiers into today's base. Preserve unknown/absent providers' records according to the current host save contract. A missing registered preset should leave its ID and supported underlying player settings intact, display an unavailable-provider explanation, and avoid silently selecting another preset. Explicitly define how partially applicable presets or missing content are handled before supporting them.

Generated/pending rewards retain their original identity and any needed provider/provenance references. Do not reroll or pay them again after a provider disappears. Define a safe unavailable-content policy and capacity/migration behavior before allowing external custom reward items; freezing an unsupported pending item is a candidate for review, not a finalized rule. Keep ephemeral modifier state distinct from committed reward progress and respect per-save versus collection-profile scope.

### Modular ownership and staged scope

| Module responsibility | Owns |
| --- | --- |
| Mod host | Existing dispatch, service discovery/versioning, provider lifecycle and diagnostics facilities |
| Each feature owner (Economy is the first implementation) | Its own typed extension contracts, eligible operations, aggregation, validation, and authoritative state changes |
| Registration/resolution component | Owner-scoped contributor records, deterministic combination, conflicts, and contribution trace |
| Presets/settings | Category definitions, provider preset registration, preview/apply, and stored player choices |
| Persistence | Versioned saved IDs/progress, unknown-data handling, migration, and capacity checks |
| Presentation/localization | Categories, provider summaries, unavailable/conflict explanations, and translated labels |

These responsibilities can be small modules within the existing structure. Reuse the host rather than building a second global event system or allowing extensions to manipulate unrelated modules' internal state.

Implement shared conventions and only the infrastructure needed by the first adopter, with module-neutral naming and no compulsory Economy dependency. Add other modules' contracts incrementally under the same framework as their designs are reviewed. Framework-wide scope is the long-term design requirement; Economy-first is the rollout order.

Recommended first slice, subject to separate implementation authorization: **new-path bonus battle-Junk modifiers, committed reward notifications, and additional Economy preset registration**. Retain exact existing behavior with no contributors. Enhanced remains unchanged by default: the initial gameplay modifier path should operate only on the new configurable path; report it inactive under legacy Enhanced rather than silently changing that path. Any future support for intentionally modifying Enhanced requires explicit player-facing scope and a separate compatibility decision. Pure notifications must not change legacy outcomes.

External reward-pool items, Catalog effects, Combat calculations, pricing extensions, and broader collection additions are later contracts within this same framework, not implied first-slice support. Movement, Encounters, Inventory/QoL, localization/presentation, and future module adoption likewise remain in architectural scope without being promised in the Economy-first delivery. In particular, custom item/effect registration needs its own stable identity, display, save/editor compatibility, and missing-provider design. Existing costume/Bestiary APIs remain available under their current contracts.

Before coding, produce an extension API specification linked from the master checklist. It must settle payloads, supported first-slice operations, composition/arithmetic, priority tie-breaks, conflicts, registration lifetime, dependency/version negotiation, saved-state policy, effective-value presentation, and examples using at least two simultaneous providers. Validate with local tests for no-provider parity, deterministic multi-provider results, invalid/conflicting contributions, disabled rewards, recursion prevention, activation changes, missing providers, and save/load without compounding or replay.

**This section is a modular extension proposal only. No hooks, APIs, gameplay values, or code have been changed.**

## 16. Race-condition protections and transaction safety

### Scope and threading model

These requirements apply to the shared extension framework and every adopting module. They cover both actual concurrent access from different threads and single-threaded ordering/reentrancy problems. Priority ordering makes execution predictable; it does not provide thread synchronization or make a multi-step operation atomic.

First audit the actual host, game, rendering, save, and asset-loading call paths. This proposal does not establish that the existing engine is single-threaded or that its hooks are already thread-safe. The recommended model is **one designated game thread owns extension-driven gameplay mutations**. Workers may prepare immutable data or submit requests through a synchronized handoff; they must not directly mutate wallet, inventory, equipment, collection progress, settings, or live render resources through these APIs. Mark each entry point as game-thread-only, worker-safe submission, or immutable query, and define enforcement/error behavior.

### Required operation protections

| Hazard | Required design response |
| --- | --- |
| Two requests spend the same balance or consume the same item | The owner validates current funds/items and commits the complete supported operation without interleaving another state-changing callback |
| Settings/contributors change during reward calculation | Capture small operation-specific inputs and a stable contributor generation; defer changes to the documented safe boundary |
| A callback recursively spends, installs, or awards | Reject unsafe reentry; explicitly permitted follow-up requests go into a bounded queue and are revalidated later |
| Registration changes while callbacks are being visited | Defer structural changes and preserve callback/provider lifetime until dispatch finishes; do not invoke unregistered or stale pointers |
| A worker completes an asset load after the player switches outfit/save | Validate request generation, provider lifetime, and current selection before publishing; discard obsolete work safely |
| Renderer uses an asset being replaced | Use the renderer's actual synchronization/lifetime boundary; applying on the game thread alone is not proof that GPU/render-thread use has ended |
| Save captures half of an item/payment transaction | Capture coherent committed state at an owner-defined safe point; serialize an immutable snapshot afterward where supported |

Use the phases **calculate → validate → commit → notify** for extension-driven operations. Calculate from stable inputs without side effects. Before commit, validate authoritative state and request eligibility, including funds, item identity, provider availability, and applicable settings. If preconditions changed, reject or restart the uncommitted calculation under a documented bounded policy; never reroll a reward already generated or committed. Do not hold a lock while calling arbitrary mod callbacks, performing file access, or waiting for a worker.

For operations involving multiple owners, such as paying Junk and installing an effect, define a coordinator and explicit preflight/commit/failure behavior. Use a reservation or equivalent design where needed so a failed install cannot leave money deducted or items consumed without the corresponding result. “One owner” is not sufficient unless the whole supported operation is coherent. Do not promise generic rollback of arbitrary callback side effects; prohibit those effects within the calculation/commit contract instead.

Post-commit notifications describe immutable completed results. Emit them only after all participating owners' state is consistent. They cannot veto the completed transaction or synchronously re-enter it. Use operation identity/provenance where a queued retry or duplicate delivery is possible; define deduplication scope and lifetime without claiming exactly-once behavior across crashes unless persistence actually guarantees it.

### Snapshots, queues, and safe boundaries

Snapshot only relevant settings, IDs, numeric inputs, and provider handles/generations. A snapshot must not contain unprotected pointers to mutable or unloadable content. Hold providers/resources alive for the required lifetime, or require restart-only lifecycle changes where the host cannot support safe removal. Record which facts are frozen for an operation and which must be rechecked at execution.

The game thread drains requests in a documented deterministic order. Define ordering across worker submissions explicitly; wall-clock arrival order alone is not a reproducibility guarantee. Each queued request has an owner/source, intended operation, relevant generation/identity, and observable success/failure result. Recheck affordability and availability when it executes. Do not let listeners create an unbounded chain of new operations in the same dispatch or frame.

Specify separate capacities and overflow behavior for gameplay requests, lifecycle changes, and observational notifications as appropriate. Never silently drop an accepted purchase, consume an item without applying its effect, or lose an earned reward because a queue is full. Reject new requests before side effects, retain committed progress according to the pending-reward policy, or use another explicitly reviewed strategy. Preserve Enhanced's legacy behavior. Diagnostic messages may be coalesced/rate-limited without changing gameplay results.

Apply preset/policy changes between battles for the Economy path, and define equivalent boundaries for other modules. Perform registration updates after active dispatches; model publication requires the renderer's safe boundary; save capture requires a coherent state boundary. Do not use “next frame” as a universal substitute for these different guarantees. Changing saves/New Game invalidates obsolete worker completions and requests according to explicit ownership rules.

### Modular responsibilities and verification

The host/dispatch layer owns execution context, stable callback traversal, lifecycle generations, and common handoff facilities. Feature owners own transaction validation and authoritative mutation. Cross-owner action coordinators own coherent multi-resource actions. Asset/render owners manage publication and resource lifetime; save owners manage coherent capture. Keep these responsibilities separate rather than adding one global lock around all mods.

D6 must specify threading/reentrancy contracts, callback lifetimes, ordering, queue limits, cross-owner actions, and failure policies; D3 must specify save/pending-state boundaries; D4 must record tests. Cover two spends competing for one balance/item, nested notifications, settings changes during dispatch, provider changes, stale asset completions, save capture at each transaction phase, queue saturation, and save/New Game switches. Use controlled interleavings and stress tests; use race-detection tooling where supported, without treating its absence or a clean run as proof of safety.

These protections constrain cooperative API usage. They do not isolate arbitrary native mods or safely preempt a callback that crashes or never returns. **No threading or transaction-safety guarantee is claimed for the current implementation by this proposal.**

## 17. Performance requirements for low-powered machines

### Design targets and implementation rules

The framework must remain practical on low-powered machines. Efficiency is a measured acceptance requirement, not an assumption derived from the small number of example callbacks. Preserve defaults and gameplay results; do not automatically reduce rewards, disable contributors, or change presets to meet a performance target.

- **Event-driven work:** invoke reward, purchase, outfit, and preset extensions when the corresponding operation happens. Do not poll every module or regenerate registration lists each frame. Future genuinely per-frame combat/movement hooks need separate cost review.
- **Cheap empty path:** with no subscribers, skip aggregation and diagnostic construction. Avoid per-call allocation and unnecessary settings snapshots on that path; retain legacy/no-provider results exactly.
- **Cached dispatch:** resolve services/dependencies and sort callbacks when registrations change. Keep per-operation traversal proportional to that operation's participating contributors, not all installed mods or registered content. Invalidate caches on relevant lifecycle/configuration changes; never cache mutable balances as authoritative transaction state.
- **Small stable inputs:** snapshot only the operation's required fields. Reuse bounded scratch buffers/queues with explicit ownership and nesting rules; a single shared scratch buffer must not be overwritten by nested dispatch.
- **No blocking callback work:** calculation/notification callbacks must not perform synchronous disk/network access, asset decoding, worker waits, or lengthy scans. Prepare expensive data separately and publish it safely under Section 16.
- **Measured concurrency:** use workers for work that justifies their overhead, such as substantial asset preparation. Simple reward arithmetic stays on the owning thread. Avoid thread creation per event and unbounded worker queues; support machines with few cores.
- **Bounded workload:** define registration counts, scratch memory, queue capacities, and per-drain work limits. Defer permitted work in a way that preserves operation order and semantics. Reject registrations/requests clearly when limits are exceeded rather than silently losing gameplay state.
- **Optional diagnostics:** build detailed provider traces on demand or when explicitly enabled. Keep essential errors visible but rate-limit repeated messages. Diagnostic history must have a bounded memory policy. Do not format verbose strings on every normal callback.
- **Separate hot-path APIs:** if later modules expose per-hit/per-frame operations, use prevalidated handles and allocation-free dispatch where practical. Do not reuse a heavyweight reward/preset diagnostic path for high-frequency movement or combat calculations.

Single-thread ownership avoids routine contention for gameplay mutation, but one slow callback can still stall the game. Document callback responsibilities and offer opt-in attribution/timing. Do not attempt to interrupt a native callback mid-transaction or silently skip a required contribution when a time budget expires. Budget excess should produce a measured failure/report for review, not nondeterministic gameplay.

### Performance acceptance plan

Before implementation, D4 must identify a representative low-powered target, OS/architecture, CPU/core count, RAM/GPU, build type, resolution/settings, and a supported frame-rate target. Agree numeric budgets for empty-path overhead, representative/worst-supported dispatch cost, frame-time impact, additional memory, startup/registration time, and queue backlog/latency. Exact hardware and numeric limits remain open; do not invent universal millisecond guarantees before establishing the baseline.

| Scenario | Evidence required |
| --- | --- |
| Previous build versus framework build with no contributors | Matched gameplay/native-result parity and measured CPU/frame-time/memory overhead; distinguish engine cost from framework cost |
| A few representative simultaneous providers | Dispatch/aggregation latency, callback attribution, memory/allocations, and unchanged deterministic results |
| Maximum supported contributors/content | Registration/startup time, memory high-water marks, category/menu scrolling, and operation latency |
| Rapid repeated actions/full queues | Drain latency, bounded memory/backlog, clear capacity outcomes, and no dropped state-changing operations or runaway chains |
| Combat/movement/viewer hot paths, if adopted | Frame-time spikes and operation frequency under representative load, including asset publication and callback cost |
| Diagnostics off versus enabled | Cost separation, bounded history, and no gameplay dependence on instrumentation |
| Worker handoffs on few-core hardware | Main-thread stalls, scheduling contention, obsolete-result cleanup, and safe resource lifetime |

Measure average and tail costs (for example p95/p99 frame and dispatch times), worst observed stalls, allocation counts, and memory high-water marks. Record sample counts/duration and distinguish cold asset loading from steady-state gameplay. Use matched builds/settings and repeat runs sufficiently to separate noise from regression. Synthetic many-provider tests supplement real sessions; desktop-only results do not establish low-powered-machine performance. If the agreed hardware is unavailable, record that coverage gap rather than marking it passed.

Keep performance fixtures, benchmark tools, logs, and captures local in `D:/Recomp Games/pe-native-debug`. Summaries and measured budgets belong in D4; module/API limits and callback guidance belong in D6. Each adopting module must record its own relevant results rather than inheriting Economy's performance pass.

### Modular ownership and decisions still open

Dispatch/registration owns the empty path, cached ordering, and contributor bounds. Request handoff owns queue capacity and drain limits. Each feature owns the cost of its calculations and commits. Asset loading/rendering owns expensive preparation/publication. Diagnostics owns optional trace/timing overhead. Benchmarking stays separate from production game rules.

Before coding, settle target hardware/budgets, queue capacities and overflow policies, callback cost guidance, scratch-buffer nesting/lifetimes, and any justified worker usage. Reconcile these with Section 16: an optimization must not introduce unsynchronized access, stale snapshots, silent payment loss, or observable load-order dependence. **Sections 16–17 add design and validation requirements only; no code, defaults, or balance values have changed.**

## 18. Memory and resource leak prevention

### Scope and ownership contracts

Leak prevention is a requirement for the framework and every adopting module, including current and future mods. It includes heap allocations, models/textures and other GPU resources, file/OS handles, worker jobs, event subscriptions, queued payloads, and retained provider references. Bounded caches and intentional lifetime allocations are different from leaks, but must have explicit owners, limits, and release policies.

Every API/resource must document who creates it, who owns it, whether the API borrows or copies it, its valid lifetime, how ownership transfers on success/failure, and the matching release operation. Preserve the inspected APIs' existing lifetime requirements until a versioned contract changes them; do not free registered content while consumers still borrow it. Pair creation/acquisition and cleanup in the owning module and use its allocator/release function across module boundaries where required. Document non-owning handles separately from owning references.

Do not promise automatic recovery from arbitrary native-mod leaks. The host can manage resources registered through its lifecycle contracts and attribute supported allocations; it cannot infer every allocation a third-party callback makes privately. Clear API obligations and measured tests are required.

### Lifecycle and failure-path requirements

| Resource / situation | Required ownership and cleanup behavior |
| --- | --- |
| Provider registrations, callbacks, and menu controls | Owner-scoped records; release copied metadata and references when the registration is safely removed. Prevent duplicate registration and stale subscribers. Respect restart-only lifecycle where required |
| Borrowed strings, content descriptors, and callback contexts | Document exact lifetime; copy temporary inputs when retention is required. Never retain stack pointers or release provider data before all readers finish |
| Menu/viewer sessions | Release session-owned lists, temporary text, model references, and preview state on every close/cancel/error path; keep only documented bounded caches |
| Model/texture swaps | Prepare the replacement without losing ownership of the current resource; on success retire the old one at the render-safe boundary, on failure release partial replacements and retain a valid current view |
| Worker jobs and queued requests | Own each payload until completion, rejection, cancellation, stale-result discard, or shutdown; each path releases it exactly once. Cancellation flags alone do not release resources or prove a worker has stopped using them |
| Pending rewards/save data | Free transient buffers when no longer needed while preserving earned/versioned persistent state under its save policy. Resource cleanup must not delete unknown mod data or silently discard pending rewards |
| Language packs and dynamic descriptions | Release replaced pack/cache storage only after borrowers finish; repeated language/provider changes must not retain obsolete copies |
| Files/OS handles and optional diagnostics | Close handles on early returns as well as success; bound log/trace buffers and release worker/timing resources under their owners |

Failed initialization must unwind completed steps even if the host never calls the normal shutdown path for a failed mod. Specify who performs that unwind. Rejecting a registration, exhausting a queue, failing allocation, or cancelling a load must leave ownership unambiguous and release partial work. Repeated cleanup must be safe under its documented state machine; prevent double-free and use-after-free as well as leaks.

Deactivation/shutdown must stop new submissions, invalidate or cancel obsolete jobs, remove registrations at safe boundaries, let active users finish, and then release owned resources in dependency-safe order. Coordinate with Section 16; freeing everything immediately during a callback or while the renderer/worker still uses it is unsafe. If safe unload is unsupported, use the existing restart flow and still clean up session/replacement/failure resources during normal operation.

Use simple acyclic ownership where possible. Shared assets need a documented reference/handle scheme and eviction policy; provider↔subscriber or job↔owner reference cycles must not keep dead modules/assets alive indefinitely. Scratch arenas/pools need defined reset points and bounds: keeping leaked objects in a growing pool does not solve the leak.

### Bounded retention and allocation failure

Set explicit entry/byte limits and eviction/release rules for content/model caches, language caches, diagnostic history, contributor metadata, and completed job records. Evict only resources no longer in use; track temporary peaks when old/new assets coexist. A bounded count is not a sufficient memory limit if entries have unbounded size. Avoid per-frame allocation where practical without replacing it with unbounded retained storage.

Handle allocation/registration failure before committing gameplay changes. Return an attributable error, release partially built objects, and preserve the previous valid state. Reuse the existing pending-reward/save policy where completion cannot proceed; do not consume an item, charge Junk, or erase progress just to recover memory. Allocation-failure diagnostics should not require another large allocation.

### Modular ownership and documentation

Keep resource management with the module that owns the resource. The host owns its registration/subscription storage and any supported owner-scoped tracking. Feature modules own operation/menu state. Asset/render owners own loaded resources and deferred destruction. Worker/handoff owners own job payloads and cancellation completion. Localization owns pack/cache lifetimes; persistence owns transient serialization buffers and preserved records. Optional diagnostics provide attribution and counters without becoming a second unbounded registry.

D6 must include ownership/lifetime/release contracts and failure/unwind examples. D2's module inventory should identify owned resources and cross-module borrowers. D3 must distinguish transient cleanup from preserved save data. D4 must define repeat-use/soak cases, memory budgets, measurement tools, and results per adopting module. New instrumentation/tests remain local in `D:/Recomp Games/pe-native-debug` unless production diagnostics are separately included in an authorized implementation.

### Leak and lifetime validation

- Repeat open/close and cancellation of Catalog, Bestiary, Wardrobe, presets, and long lists; include repeated model/outfit/language/provider changes where supported.
- Exercise failed initialization, duplicate/rejected registrations, missing/corrupt assets, partial loads, allocation failures, full queues, cancelled/stale workers, and early exits.
- Exercise save/load and New Game repeatedly, supported disable/restart/shutdown paths, and shutdown with queued work. Verify resources and references are released without losing persistent state.
- Record live owned allocations/bytes, resource/handle counts, cache occupancy, and outstanding jobs/registrations at equivalent quiescent checkpoints after warm-up and deferred render/worker cleanup. Confirm temporary/session resources return to baseline and allowed caches plateau within their documented limits.
- Measure process memory as supporting evidence, not proof: allocators/drivers may retain reserved memory after objects are freed. Compare live ownership/resource counts and trends; distinguish intentional retained capacity, fragmentation, and actual unreachable allocations.
- Use toolchain-supported leak/heap checking and address/lifetime sanitizers or equivalents where available; GPU/OS handles need their own counters/tools. Record tool coverage and exclusions, and do not claim unsupported tooling was run.
- Run representative multi-provider and low-memory cases plus an agreed-duration soak on the target low-powered machine. Set cycle counts, soak duration, allowed steady-state/peak memory, and pass criteria in D4 before marking results complete. No unexplained continuing live-allocation/resource growth is acceptable.

Leak detection alone does not prove lifetime safety; combine these checks with Section 16's interleaving/stale-callback tests and Section 17's memory/performance limits. **This section adds design requirements only. No cleanup code was changed and no current build is certified leak-free.**

## 19. Small capability APIs and coordinated Randomizer/overhaul mods

### Participation without compulsory public APIs

**Every current and future mod should be able to participate in the framework, but only publish a small API where another mod has a useful integration need.** Participation may mean subscribing to events, consuming a service, registering content, or offering one supported capability. It does not require exposing all internal functions, creating a service per source file, or making every module implement the same interface.

Publish APIs by capability rather than insisting on one API per mod. A mod can provide several capabilities; another can provide none. Examples of capability names include the existing `junk` and `costumes` services, and a possible future inventory-organization service. New names, function signatures, and capabilities remain design decisions, not implemented interfaces.

For each public surface, ask: who consumes it, what operation they need, what state it owns, and what compatibility commitment it creates. Prefer a narrow query, content registration, validated action request, calculation contribution, or notification over direct access to mutable structures. Expand only for reviewed integration requirements. Keep asset loaders, raw save buffers, internal menu rows, and private rule functions private unless a specific supported use case requires otherwise.

Reuse shared conventions from Sections 15–18: stable namespaced IDs, explicit versions/capabilities, typed payloads, ownership/release, activation/dependencies, deterministic resolution, execution-context rules, safe transactions, bounded resources, and diagnostics. Shared conventions do not require a universal untyped command API, one large table containing every feature, or a parallel dispatch system for each mod.

### Central capability catalog and maintenance

Maintain a capability catalog in D6 with provider/owner, purpose, version/size negotiation, required/optional dependencies, supported operations, thread/lifetime requirements, save implications, limits, and small usage examples. Record status as existing, proposed, implemented/verified, deprecated, or unavailable; registration of a capability is not a claim that every version exists. Cross-reference the per-module adoption matrix rather than duplicating settings definitions.

Treat public APIs as compatibility commitments. Define version transitions and deprecation/migration before removing a relied-upon operation. Check capability availability rather than assuming a particular filename/mod name implies support. Reuse existing services through compatible additions or reviewed adapters; do not break current Bestiary/costume consumers solely to impose uniform naming.

### Coordinators for major gameplay changes

A Randomizer or overarching overhaul can be a **coordinator mod**: it consumes several small capabilities and owns its own run plan, rather than becoming the owner of every participating module's state. For example, a Randomizer could propose enemy mappings, equipment/item placements, and matching Bestiary information; an overhaul could request supported combat rules, encounter policies, and economy settings. Feature owners validate and apply the supported parts. Raw memory patching outside these contracts is not covered by framework compatibility guarantees.

An ordinary category preset still changes only its own category. A coordinated package is a separate, explicit player action or run setup, with a combined preview naming every affected category, provider requirement, incompatibility, and restart/new-game restriction. Do not disguise it as a Combat or Economy preset. Mark affected settings with their source, show which values the coordinator owns versus merely suggests, and define what manual edits do: reject a prohibited change with an explanation, or mark the package customized/invalid according to its declared policy. No silent switching or automatic reapplication that fights the player's settings.

Large overhauls may intentionally replace vanilla drops, enemy tables, or native balance. That requires explicit capability contracts and opt-in scope; it is outside ordinary additive Economy modifiers. Default Economy/native-drop parity still applies when no such package is selected. An overhaul cannot bypass a player's disabled feature by masquerading as an ordinary modifier; it must request the necessary visible policy change through the owning module or declare the configuration incompatible. Stored equipment upgrades, discovery/ownership data, anti-exploit provenance, and save compatibility remain protected unless a separately reviewed migration explicitly changes them.

### Cross-module planning, conflicts, and activation

Use a staged plan for coordinated changes:

1. **Discover:** resolve required capability versions/providers; distinguish optional presentation enhancements from required gameplay support. Reject missing requirements and dependency cycles with an attributable explanation.
2. **Build and validate:** construct a bounded, immutable plan using stable content IDs. Each owner validates its part, including capacities, references, story/progression constraints, and required asset availability. Make Randomizer reachability/softlock validation an explicit algorithm/content responsibility; seed generation alone does not prove a playable run.
3. **Resolve authority:** identify supported additive contributions and explicitly exclusive replacements. If two Randomizers replace the same encounter table, or an overhaul and balancing mod both claim an exclusive rule, require a declared compatibility adapter, user-selected authority, or refusal to activate the combination. Increasing callback priority is not a compatibility solution.
4. **Preview and apply:** show the complete effect, then apply the approved plan at the appropriate safe boundary, often before New Game or with restart where required. Recheck plan/provider generations before application.
5. **Publish and observe:** expose the coherent active plan to its owners/consumers and emit completion notifications only after required parts agree on the activated generation.

Required gameplay parts must not activate partially. Define prepare/commit/abort or another reviewed coordinated activation mechanism before supporting such packages. Prepare can allocate/validate without mutating live state; failure releases staged resources and leaves the previous valid plan intact. Do not promise rollback of arbitrary mod side effects. If the existing modules cannot provide coherent runtime activation, support startup/New Game activation only rather than claiming a universal live transaction system. Optional parts may be omitted only when explicitly declared safe and explained in the preview.

For example, if encounter replacements validate but required item placements fail, do not install the encounters and silently retain old placements. Likewise, a Bestiary consumer must query the same authoritative encounter/drop generation rather than reproduce randomization independently. Derived presentation respects discovery rules; a diagnostic or spoiler log must not reveal hidden content by default.

### Deterministic runs, persistence, and missing coordinators

For Randomizers, record enough information to reproduce or validate a run: seed, generator/algorithm version, relevant content/provider versions and stable IDs, configuration, and an agreed plan fingerprint or generated mapping/state. A seed alone is insufficient across algorithm/content changes. Define stable PRNG algorithms/stream ownership and canonical ordering rather than relying on platform hashes or registration order. Cosmetic preview, diagnostic inspection, and optional presentation mods must not consume gameplay RNG draws or change the generated plan.

Partition gameplay RNG streams where appropriate so adding an unrelated loot provider does not reshuffle encounters accidentally. Define behavior for intentional gameplay contributors and their version changes; deterministic claims apply to the declared run manifest, not arbitrary incompatible mod combinations. Record mutable run progress and any required RNG state consistently with Section 16's save boundary.

D3 must review the actual save-container capacity before deciding to store mappings, compressed plans, fingerprints, or reproducible inputs. Do not assume large generated tables fit the current mod-save record budget. External run files, if proposed, need a separate portability/backup/missing-file design and must not be adopted silently. Save/editor/recovery tools should preserve unknown coordinator/provider records without needing installed mods; semantic editing of an unknown format cannot be assumed safe.

Loading a run with a missing/incompatible coordinator, required provider, plan, or algorithm version must produce a clear compatibility result before gameplay resumes. Preserve the original save and unknown data; do not silently rerandomize, choose a new seed, or fall back to unrelated native tables. Define safe supported recovery/migration paths separately. Mid-run enabling, disabling, or switching coordinated packages is not promised: it may require a new run or explicit reviewed migration. Category defaults and non-participating saves remain unchanged.

### Modular rollout and verification

Keep shared discovery/dispatch and lifecycle facilities in the host, small capability contracts and actions in their feature owners, and coordination/run generation in the Randomizer or overhaul mod. Add only the coordination infrastructure required by a real reviewed integration; do not make all mods depend on a speculative universal orchestrator. Existing registration services remain useful independently of any coordinator.

Economy remains the proposed first framework adopter. Its first slice does not implement a Randomizer, overhaul, global profile system, arbitrary table replacement, or coordinated runtime activation. This section ensures that its API design does not prevent later multi-module integration. D6 should include one small single-capability example, a two-contributor example, and a proposed multi-capability coordinator walkthrough with supported versus deferred operations clearly marked.

Before supporting a coordinator, D4 must cover capability negotiation, missing requirements/cycles, conflicting replacement providers, failed preparation/commit boundaries, obsolete plans, cleanup, and player-visible combined scope. For a Randomizer, also cover same-manifest reproducibility, registration-order independence, cosmetic/diagnostic RNG isolation, progression/reachability checks, save/load continuity, mismatched manifests/missing providers, no silent reroll, and supported seed/configuration changes. Apply Sections 16–18's race, resource, performance, and leak checks to coordinated plans as well as individual modules.

**This is a framework/API design extension only. No Randomizer, overhaul, public API, defaults, or game code have been implemented or changed.**

## 20. Custom items, weapons, armor and equipment effects, and Economy shop contributions

Added October 31, 2026. **Proposed follow-up scope, documentation only.** The implemented save-status, capacity-refusal and conditional-record facilities are prerequisites, not a custom-content registry or shop API. This section does not approve a new save format, content balance, immediate content implementation, or changes to Enhanced. The candidate policy record in D3 is not storage for arbitrary custom inventories.

### Goals and independent ownership

Allow a content mod to define items, weapons and armor once, then make them available through supported shops and, in separately adopted integrations, pickups, rewards or other sources. A content mod must remain usable without Economy when its own delivery path supports that. Economy should accept compatible offers without becoming the owner of the item's definition, assets or equipment rules. Multiple content providers may participate together.

| Responsibility | Owner / proposed boundary |
| --- | --- |
| Content identity, lookup and capability negotiation | Small shared content registry, independent of Economy |
| Item definitions, supported use/equip behavior and content assets | Content provider plus the relevant inventory/equipment/asset owners |
| Inventory instances, quantities, equipment state and validated delivery | Inventory/equipment owners through supported actions |
| Saved identities, instance data, missing-content retention and migrations | Persistence owner with versioned provider schemas |
| Offer registration, shop presentation, quoting, payment and stock coordination | Economy shop capability; payment uses the existing wallet owner |
| Drop, pickup, crafting, Dismantle/Rebuild and Randomizer integration | Each relevant feature's separate reviewed adapter; shop registration alone does not enable these |

Keep definition registration, instance storage, runtime/native adapters and shop offers in separate modules. Shared conventions in Sections 15–19 apply; do not expose raw inventory arrays, save buffers, arbitrary native function addresses or unrestricted callbacks as the public content contract. Reuse existing compatible item/effect services through reviewed adapters rather than introducing competing authorities.

### Stable definitions and supported behavior

Use permanent namespaced content IDs such as `example_pack.weapon.service_rifle`, separate from translated names, icons, registry order and native numeric slots. Persist the stable ID and required schema information. Runtime handles may be compact and generation-checked, but must never be saved as permanent identity. IDs must not change meaning or be recycled for a different item; reviewed rename aliases/migrations must detect collisions and cycles.

Definitions should declare their kind, version, localization keys, assets, stack/quantity limits, required capabilities and supported actions. Weapon/armor definitions also need validated stat ranges, native-family/animation compatibility where required, slot/effect capabilities and equip restrictions. Distinguish immutable definitions from mutable instance data: upgrades, current ammunition/charges, installed effects, provenance and other instance-specific values must not be inferred from the current definition or lost on save/load.

Unknown effects and provider-specific fields must be retained where their framing is understood. Do not equate preserving bytes with safely executing an unknown effect. A custom effect or new weapon behavior needs its own supported capability; adding a definition does not automatically implement combat mechanics, scripts, models or animations.

Audit every native path that assumes fixed item IDs, array sizes, item classes or equipment layouts: menus, storage, use/equip, battle calculations, ammunition, effects, animation/model selection and serialization. Initially support reviewed native-compatible archetypes with explicit limits. Arbitrary new mechanics can follow through separate contracts. Reject unsupported definitions with attributable diagnostics before they become available; do not claim unlimited content merely because the game is native.

### Custom weapon and armor mods / effects

This scope explicitly includes installable weapon and armor mods (equipment effects), in addition to whole custom weapons and armor. A provider may contribute an effect for existing equipment without defining a new gun or armor item. Shared effect identity and runtime behavior must remain independent of Economy; the Mod Catalog and shops are optional consumers of that capability.

Use stable namespaced effect IDs, separate from native effect bits, localized names, icons and Catalog row positions. Definitions declare weapon/armor applicability, required runtime capability, supported effect parameters/version, stacking/uniqueness, exclusions, slot cost and any removal/transfer restrictions. Preserve the existing meanings of native effects through reviewed adapters; never assign an unknown custom effect to a spare native bit without a compatibility design. New slot limits or combat rules require separate review rather than following automatically from registration.

Keep these responsibilities separate:

- **Effect registry/runtime owner:** validate definitions, resolve dependencies and execute supported combat/equipment behavior. Multiple providers must have deterministic, explicitly defined stacking and conflict rules; callback order must not decide the result.
- **Equipment instance/persistence owner:** retain installed effect IDs, parameters, slot placement and provenance. Preserve built-in versus installed/removable distinctions, unknown payloads and existing upgrades. Installed state must not depend on registry order or be reconstructed from current Catalog availability.
- **Mod Catalog adapter:** register eligible effect entries with translated labels/help, icons, discovery requirements, install/removal eligibility and price policy. Preserve current unlock/discovery rules, `????` presentation with hidden details for undiscovered effects, weapon/armor selection and independently scrolling lists. An effect definition alone does not grant discovery, ownership or permission to install it.
- **Economy shop adapter:** distinguish selling an equipment item, selling a consumable effect-granting item, and purchasing an installation service. Each needs a typed supported delivery action and explicit target/eligibility; a service must not masquerade as inventory item delivery. Installation services require their own reviewed contract before support is claimed.

Quote and validate effect installation/removal/transfer through the equipment owner before charging or consuming anything. Recheck target identity/generation, applicability, slots, duplicates/exclusions, discovery, resources and save capacity at commit. Update payment/consumption, installed state and any stock/provenance coherently; failed requests leave them unchanged. Existing Dismantle/Rebuild, salvage and refund safeguards must remain effective, with no repeated equip/remove/rebuild route to duplicate effects, items or Junk. Do not introduce an automatic refund policy through registration.

If an installed effect's provider or required runtime capability is unavailable, retain its saved identity, payload and slot/provenance data and show an unavailable effect without executing it or substituting an unrelated native effect. Do not silently free its occupied slot or allow overwrite/removal/sale/dismantling that would erase opaque data. D3 must bind whether otherwise resolvable equipment can safely function with that effect inactive, requires a temporary equipment fallback, or blocks continuation; required progression/coordinator effects cannot simply be ignored. Reinstalling a compatible provider restores resolution without a new charge, duplicate application or compounded stats. Missing icons may use a generic icon without disabling valid behavior. Newer/invalid effect schemas remain preserved and unavailable until a supported migration succeeds.

Extend D2/D3/D6 with these effect-specific contracts and D4 with native/custom mixed effects, built-in/removable distinctions, slot boundaries, conflicting/stacking providers, reversed registration order, undiscovered UI, missing/reinstalled effect providers on native equipment, migration/opaque round trips, stale installation targets and failed payment/consumption. Include install/remove/transfer/Dismantle/Rebuild anti-duplication cases and repeat-use resource checks. These remain proposed work; no new effects, prices, balance changes, Catalog grants or installation services are implemented by this document.

### Versioned saves and backward compatibility

Keep existing vanilla saves and existing mod records readable without registering or allocating custom-instance records when none are needed. Conditional emission helps avoid unused records; once meaningful state exists, preserve it even after returning to defaults. Read-only inspection must not activate content or consume save space.

The current mod container has **744 usable record bytes**; the audited baseline is 524, and the candidate 160-byte policy payload plus its header would bring that to 696. Those figures leave little space for custom instances and unknown carried records. Conditional emission does not enlarge the container. Before implementation, D3 must budget definitions versus saved instances, inventories/storage, stock/pending transactions and opaque provider data against actual limits. Do not allocate one record per item or save the entire registry by default.

If the existing container cannot fit the accepted scope, propose and review a versioned expandable storage design separately, including native checksums, atomic publication, backup/recovery, portability and editor support. Do not silently append bytes, truncate records, create sidecars or adopt an expanded format through the shop API. Capacity refusal must happen before accepting new persistent state, including purchases and pickups; it is insufficient to discover that an acquired custom item cannot be saved afterward.

| Compatibility direction | Required behavior / limit |
| --- | --- |
| Existing saves into a newer supported build | Preserve native state and existing record layouts; absent custom records mean no owned custom content. Apply only explicit, versioned migrations |
| Custom-content save with the same compatible provider | Resolve stable IDs and restore instance state without rerolls, duplicate grants, stat compounding or repeated migrations |
| Save with provider absent, disabled or incompatible | Preserve framed instance/ownership data and unknown records; enter the missing-content policy below rather than interpreting IDs as unrelated native items |
| Newer provider schema or unknown effects | Preserve opaque payloads where supported, report incompatibility and disable unsafe operations; do not reset them and publish the defaults over the originals |
| New save opened by an older game/editor | Byte preservation is a bounded format-level capability, not a promise of usable content or safe downgrade. Specify supported reader versions and refusal paths; no arbitrary older-build compatibility guarantee |

Separate container version, shared instance schema, provider schema and API version. Content-data revisions should not require a save migration unless stored meaning changes. Migrations must be bounded, validated and repeat-safe, with original data retained on failure. Tools should inspect identity/status and preserve unknown data without executing installed provider code; semantic editing of unknown schemas remains unsupported. Update save-editor/export/recovery documentation when the format is actually selected.

### Missing-mod and missing-asset policy

Distinguish a missing definition, disabled provider, unsupported schema/API, unavailable effect capability and missing presentation asset. A missing icon alone may use a generic icon; it must not make otherwise valid inventory state disappear. Missing gameplay behavior must not be executed through a cosmetic fallback.

Recommended initial policy, subject to D3 review:

- Keep unresolved items as visible, read-only placeholders identified as unavailable content, with provider/content identity available in help. Retain quantity, instance data and effects without revealing undiscovered details. No use, equip, combine, sell, dismantle or rebuild while unresolved; storage transfer requires a separately validated lossless path.
- Preserve the logical equipped custom instance. Before gameplay resumes, resolve required equipment or explicitly choose a safe supported fallback. If supported, use a temporary validated native fallback while keeping the original instance separate and unchanged; otherwise refuse continuation with clear recovery instructions. Never put an unresolved custom numeric ID into native equipment arrays or overwrite the original with the fallback.
- Block loading/resuming when missing content is required for progression or an active coordinator plan. Optional inventory content may remain quarantined only where all relevant runtime paths are proven safe. Do not silently remove a required item, grant a replacement, rerandomize a run or bypass a dependency.
- Reinstalling a compatible provider should resolve retained content without a new purchase, reroll or duplicate grant. Re-equipping after a temporary fallback requires a defined safe transition and must respect equipment changes made by the player; do not silently replace the player's current choice.
- Hide or clearly disable unavailable shop offers; never charge for unresolved content. Preserve associated saved stock, pending state and ownership. A provider restart/absence must not reset limited stock or permit repeat one-time purchases.

Deleting unavailable content, converting it to vanilla items, or discarding opaque data is a separate explicit recovery/migration action with backup and review, not an automatic load behavior. Decide whether unresolved placeholders consume inventory capacity or use bounded quarantine storage before implementation; neither unbounded free storage nor hidden eviction is acceptable. Returning to a compatible build/provider remains the preferred nondestructive recovery path.

### Small Economy shop API

Expose a versioned capability with discovery and typed offer registration/query operations. The following are conceptual requirements, **not final C signatures**:

| Surface | Required information / behavior |
| --- | --- |
| Register an offer during supported initialization | Stable namespaced offer ID, provider owner, target shop ID, stable content reference, quantity, supported currency/price policy, stock rule and availability requirements |
| Resolve and inspect | Check content/API dependencies, schema support, discovery eligibility and assets; return a bounded immutable view without granting items or revealing hidden effects |
| Quote a purchase | Final quantity/price/stock, effective pricing sources, inventory/save readiness and provider generations; preview has no payment, stock, RNG or gameplay side effects |
| Request purchase | Execute an owner-validated operation against the quote, rechecking readiness, current funds, stock, capacity, provider/content versions and price before any irreversible change |
| Query outcome / observe completion | Attributable success/refusal status and post-commit notification, with duplicate-operation handling; notifications cannot repeat payment or delivery |

Start with Junk and ordinary supported purchases, not an arbitrary currency/conversion system. Resolve whether Economy discounts/modifiers apply per declared offer policy, and show the final price and sources consistently. One-time/limited offers need stable stock/transaction identity and versioned persistence; infinite stock needs no unnecessary per-offer saved state. Availability queries must be side-effect-free and respect Catalog/discovery and story rules. Shop offers do not automatically add effects to the Mod Catalog or add buying to Wardrobe.

Multiple providers contribute distinct offers in deterministic order, using explicit stable sort keys and IDs. Duplicate IDs, incompatible dependencies, unsupported currencies or invalid prices/quantities are rejected with the owning provider named. Never silently overwrite another offer or use registration/load order to decide ownership. Separate offers for the same item are allowed when their stable offer IDs and stock policies are intentionally distinct. Replacement of an existing shop or exclusive pricing authority requires a separate opt-in conflict/adapter policy, as in Section 19.

### Purchase safety, lifecycle and efficiency

Payment, item delivery, stock change and persistent instance/transaction state must form one reviewed operation. Prefer inventory-owned prepare/reserve and commit contracts that can fail before money is consumed. If coherent runtime commit cannot be guaranteed, limit the initial API to operations with supported commit semantics; arbitrary provider delivery callbacks that may partially mutate state are insufficient. Do not promise rollback of arbitrary native callbacks.

Preview or preparation must not publish ownership. Recheck quote generations and capacities at the safe game-thread boundary, coordinate with shared wallet spends and inventory changes, and publish completion only after all required owners agree. Block or defer save/crash capture during incomplete commits according to the coherent-save design; never capture money spent without the matching item/stock state. Do not claim current capacity checks alone provide whole-save atomicity. Interrupted/retried operations must not grant or charge twice.

Registration follows the supported startup/restart lifecycle; hot unload is not implied. Validate required capability versions without circular initialization dependencies. Bound registries, offer lists, instance/quarantine counts, retained payload bytes and asset caches; ownership and failure cleanup follow Section 18. Cache resolved handles and invalidate them by generation; avoid full registry scans, disk access or allocation in combat/per-frame paths. Third-party provider code remains subject to the same game-thread, reentrancy and resource contracts.

### Delivery order, open decisions and verification

1. Extend D2 with affected native paths, controls and ownership; D6 with the shared content/instance and shop capability contracts. Audit existing fixed-ID limits and supported archetypes before choosing runtime adapters.
2. Extend D3 with stable-instance persistence, actual byte budgets, missing-provider/equipped handling and migrations. Review any storage expansion and coherent purchase/save boundary separately before enabling acquisitions.
3. Implement the shared registry and one native-compatible example per content kind under separate authorization; validate inventory/equipment/save integration independently of Economy.
4. Add the narrow Economy shop adapter and two independent example providers. Pickup/drop/crafting/Randomizer integrations remain separate work; each adopts the same identity and owner contracts where appropriate.
5. Extend D4 with old-save/no-provider parity, same-provider round trips, multiple providers/reversed order/collisions, missing/reinstalled/disabled/incompatible providers, missing assets/effects, equipped fallbacks, failed migrations, full inventory/storage/save capacity, limited stock, stale quotes, simultaneous spends, nested calls, interruption/retry and editor unknown-data preservation. Include repeated UI/provider/resource cycles and low-powered performance/memory measurements.

Before coding, settle supported item archetypes/actions, identity encoding and limits, saved instance schema and storage capacity, unresolved capacity/quarantine rules, fallback/re-equip and progression-blocking policy, price modifier/stock semantics, and purchase prepare/commit/save guarantees. Carry these as explicit open work into D2/D3/D4/D6 and the master checklist; this section does not silently finalize their existing drafts. All new test fixtures, runners and raw evidence stay local in `D:/Recomp Games/pe-native-debug`.

**No game code, save files, balances, shop contents or defaults changed for this addition. Custom-content and shop APIs remain proposed. Enhanced stays the default, category controls remain independent, and Wardrobe retains no buying functionality.**
