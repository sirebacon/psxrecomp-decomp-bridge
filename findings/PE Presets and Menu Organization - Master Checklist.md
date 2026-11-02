# PE presets and menu organization: master checklist

Updated: October 31, 2026.

Status: planning and review tracker. No preset implementation or gameplay changes are approved by this checklist.

## 1. Scope and how to use this document

This is the entry point for the proposed Economy reward controls, independent presets for other mod categories, menu reorganization, and modular extension hooks for cooperating mods. It tracks design decisions, documents still needed, implementation tasks, and release evidence. It is not a completion audit of every mod or every historical port.

**The extension framework is for all current and future mods. Economy is only its proposed first implementation.** Track framework design separately from each module's adoption. Combat, Encounters, Movement, Inventory/QoL, Catalog, shops, Wardrobe, Bestiary, localization/presentation, and future modules use shared conventions while owning their own supported extension points. This scope does not mean every module's API is already implemented or must ship with the first Economy slice.

Every mod may participate without publishing an API. Expose small capability-based APIs only for useful integration needs. Separately opted-in Randomizer/overhaul coordinators may combine several capabilities under D1 §19; ordinary category presets remain independent. Economy-first delivery does not include implementing those coordinators.

The detailed design lives in [D1, the current proposal](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Economy presets and independent reward controls proposal.md>). This checklist points to its sections rather than copying its balance tables. Update the proposal when a decision changes, then update the corresponding checklist item.

**Checkbox rule:** a checked item means only the stated deliverable is complete. “Documented” does not mean approved, coded, built, tested, merged, or released. Implementation and validation remain unchecked unless accompanied by evidence from the target branch. Historical test results are not new passes.

For developers and AI assistants: read Sections 2–4 here, then the relevant D1 sections before doing work. Audit the actual target branch before using historical documents. Do not infer authorization to implement from a checked design item.

Before behavioral implementation, also read [D7, the pre-implementation review](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets and Mod Extensions - Pre-implementation Review.md>). D2/D3/D6 contain scoped candidate contracts tied to REV-01–12, and D4 now contains the scoped validation/playtest plan. Policy bindings, host prerequisites, target hardware/budgets, and readiness gates remain open; D4 has no execution results. Future coordinator/module specifications are not all prerequisites for the initial Economy slice.

## 2. Non-negotiable requirements

- [ ] Verify in the eventual implementation that **Enhanced remains the Economy default and reproduces current behavior**.
- [ ] Preserve all current category defaults and existing player settings; adding a preset selector must not apply a new configuration automatically.
- [ ] Keep ordinary category presets independent across Combat, Encounters, Movement, Inventory, Economy, Bestiary, and Wardrobe. No global Easy/Hard profile or silent cross-category changes; a separately opted-in coordinator follows D1 §19's declared multi-category scope and owner validation.
- [ ] Preserve possessions, balances, equipment upgrades, discovered effects, outfit ownership, and Bestiary progress. Preserve native drops under ordinary presets/modifiers; an explicit future overhaul may replace declared native tables only under D1 §19's reviewed scope and migration rules.
- [ ] Keep Workshop-service visibility outside the initial implementation; retain existing services and native Wayne hand-ins.
- [ ] Keep testing unlock/reset actions separate from everyday settings. Wardrobe gains no buying functionality.
- [ ] Keep player settings authoritative, extension contributions attributable and deterministic, and each transaction committed once by its owning module. No contributor may silently enable a disabled reward category.
- [ ] Keep extension infrastructure module-neutral and usable by all current/future mods without a compulsory Economy dependency. Each module defines its supported contracts; adoption can be staged.
- [ ] Publish only useful small capability APIs under shared conventions; keep private internals private. Require explicit combined scope and coherent activation for any later Randomizer/overhaul coordinator.
- [ ] Define gameplay-thread ownership, coherent transactions/save capture, stable callback/resource lifetimes, and bounded safe request handoff; callback priorities alone are not thread-safety protection.
- [ ] Meet agreed low-powered-machine performance budgets without changing defaults, dropping gameplay state, or silently skipping contributors; record actual measurements before claiming efficiency.
- [ ] Require explicit memory/resource ownership, bounded retention, and cleanup on success, failure, cancellation, and supported shutdown paths across all adopting modules; verify no unexplained continuing live-resource growth.
- [ ] Keep new tests, fixtures, disposable saves, logs, simulations, and captures local in `D:/Recomp Games/pe-native-debug`, with no remote publication of that test suite.
- [ ] Obtain a separate implementation instruction before changing game code; current work is documentation only.

## 3. Document register and reading order

### Current design and required work records

| ID | Document / location | Role and current status |
| --- | --- | --- |
| D0 | This master checklist | Entry point, coverage tracker, and completion evidence index |
| D1 | [Economy presets and independent reward controls proposal](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Economy presets and independent reward controls proposal.md>) | Current proposal: Economy §§1–12, other categories §13, menus §14, extensions §15, race/transaction safety §16, performance §17, leak prevention §18, small capability APIs and Randomizer/overhaul coordination §19. Documented; approval and implementation remain separate |
| D2 | [Scoped control inventory and menu map](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Control Inventory and Menu Map.md>) | **Draft created.** Source-audited Economy controls/defaults/scopes, candidate transitions, wallet/redemption/pricing policies, menu-key migration, module/resource ownership; policy approval remains open |
| D3 | [Scoped persistence and migration design](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Persistence and Migration Design.md>) | **Draft created.** Audited 524/744-byte baseline, proposed 160-byte combined record, load/migration/RNG/queue contracts, capacity/provenance/crash-snapshot prerequisites; not an implemented format |
| D4 | [Scoped validation and playtest plan/results](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Validation and Playtest Record.md>) | **Plan created; execution unrun.** Cases cover baseline/menu, saves/capacity/recovery, rewards, mod/API compatibility, races, performance, leaks, and playtesting; PB-01–09 bind unresolved policies. Local suite/raw evidence stay in `pe-native-debug`; hardware/numeric budgets remain open |
| D5 | Player guide and release documentation | **Update after behavior is implemented and verified.** Locate the maintained guide/README on the target branch; do not treat a historical downloaded guide as the authoritative release copy |
| D6 | [Small capability APIs and cooperation contract](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Mod Extensions - API and Cooperation Contract.md>) | **Draft created.** Shared conventions and candidate `economy_policy` v1: typed modifiers, observers, provider presets, deterministic composition, ownership/lifecycle/limits, examples; future coordinators deferred |
| D7 | [Pre-implementation review](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets and Mod Extensions - Pre-implementation Review.md>) | Existing review of D0/D1 plus source-contract checks at `ae6520fe6`; open findings REV-01–12 and readiness gates G0–G5. Documentation/source inspection only, no runtime results |
| D8 | [Character packs and standalone Wardrobe](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Character Packs and Standalone Wardrobe - Design.md>) | **Draft created November 1.** BioRand-style zip pack format for character additions/replacements; Wardrobe split from `pe_collection` with Economy as an optional shop; recipe packs for disc-derived characters; acceptance cases PACK/WRD. Not implemented |
| D9 | [Standalone mod boundaries and optional integrations](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Standalone Mod Boundaries - Design Review.md>) | **Recommendation/review, November 1.** Independent Wardrobe and Bestiary, wallet/reward/Catalog/shop boundaries, migration authority and cross-store payment/default conflicts. No extraction implemented |

D2/D3/D6 are existing design drafts, not approved or implemented interfaces. D4 is an existing plan with no test passes; bind its policies and agree acceptance limits before execution/acceptance. D5's maintained release source still needs identifying. Read D2 → D3 → D6 → D4 after D1/D7. Supporting future work can be consolidated without losing traceability.

### Supporting references: read with their date and branch limitations

| ID | Existing reference | Why it matters / qualification |
| --- | --- | --- |
| R1 | [Mod save data: preservation, recovery, and chunk format review](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Mod Save Data - Preservation, Recovery, and Chunk Format Review.md>) | Consolidated save review. Historical snapshot; verify the current host implementation before designing new records. Gap 8 was fixed in the fork; this document alone does not establish upstream inclusion |
| R2 | [Restore save and mod-data test plan](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Restore save and mod-data test plan.md>) | Historical recovery cases and save inventory; use for regression coverage, not current container-capacity assumptions |
| R3 | [Original save-chunk proposal](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/Proposal Save chunks for mods.md>) | Historical rationale and format proposal. Do not implement its sketch without comparing against the now-current host API |
| R4 | [Localization progress review, October 29](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Localization Progress Review - 2026-10-29.md>) | Historical control-tag, layout, and selection findings. Later fixes and Spanish/Cyrillic/CJK work supersede portions; inspect current localization documentation and code |
| R5 | [Native weapon review, October 26](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/pe-native-weapon-review-2026-10-26.md>) | Balance-review background and simulation limits. Contains proposals, not an authoritative list of current applied buffs |
| R6 | [Native Chrysler weapon review, October 26](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/pe-native-chrysler-weapons-2026-10-26.md>) | Additional weapon-review background. Verify current code and stored equipment behavior before defining Combat presets |
| R7 | [Bestiary/Wardrobe viewer plan, October 26](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/pe-bestiary-viewer-plan-2026-10-26.md>) | Historical collection/viewer architecture and discovery intent; implementation has progressed beyond its stated status |
| R8 | [Skins and Bestiary design, October 19](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/pe-skins-bestiary-design-2026-10-19.md>) | Historical ownership/economy design. Its buying concepts do not authorize buying functionality in the current Wardrobe UI proposal |
| R9 | [Original loot overhaul checklist](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/pe-loot-overhaul-checklist.md>) | Earlier recomp work only. Its checked items, refund behavior, defaults, and test results must not be carried into this native-preset tracker as completed work |

Read D1 first. Use R1–R9 only where relevant; they are not an instruction to reopen every historical project. The current target branch and explicitly agreed design resolve differences; record any unresolved conflict rather than silently choosing a historical behavior.

## 4. Documentation completed so far

- [x] Document the player feedback and distinction between native drops, extra battle Junk, bonus items, and bundle redemption — D1 §§1–3.
- [x] Document Enhanced compatibility and the proposed Economy presets — D1 §4.
- [x] Record provisional Light Economy, Steady Income, and Treasure Hunter values, explicitly open to playtesting — D1 §4.
- [x] Document six implementation recommendations, equipment modifiers, independent reward families, and deferred Workshop visibility — D1 §§4–8, 12.
- [x] Document modular responsibilities and Economy validation requirements — D1 §§9–11.
- [x] Add independent preset ideas for Combat, Encounters, Movement, Inventory, Bestiary, and Wardrobe — D1 §13.
- [x] Add proposed menu grouping, category layout, Economy subpages, and setting ownership — D1 §14.
- [x] Document extension registration, calculation contributions, notifications, multi-mod cooperation/conflicts, and modular staged scope — D1 §15. API details and implementation remain open.
- [x] Clarify framework-wide coverage for all current/future mods, per-module ownership, and Economy as the first adopter rather than the framework boundary — D1 scope note and §15.
- [x] Document proposed race-condition/reentrancy protections, transaction/save coherence, lifecycle/resource safety, and modular ownership — D1 §16. Verification remains open.
- [x] Document low-powered-machine performance requirements, measurement scenarios, and open budget/hardware decisions — D1 §17. No benchmark results are claimed.
- [x] Document memory/resource ownership, cleanup/failure handling, bounded retention, and leak/lifetime validation requirements — D1 §18. No current build is certified leak-free.
- [x] Document optional small capability APIs, shared conventions/catalog, and staged Randomizer/overhaul coordination requirements — D1 §19. No coordinator or new public API is implemented.
- [x] Document modular custom item/weapon/armor/effect support and Economy shop contributions, stable identities, versioned instance saves, backward compatibility, missing-provider/equipment handling and purchase safety — D1 §20. This is a proposed follow-up, not implemented content/API support.
- [x] Extend D2 §9, D3 §10 and D6 §10 with candidate custom-content/effect/shop controls, ownership, schemas and capability/action contracts; extend D4 §15 with PB-10–14 and 36 planned validation cases. Contracts, storage choices and limits still require approval; no extension implementation, tests or build performed.
- [x] Review the custom-content/shop drafts for multiple providers submitting multiple entries. D7 records MCR-01–12, references, recommendations and validation gaps. The initial review left all 12 open; later requested dispositions resolve MCR-01–03 (D6 §11) and MCR-04/05/10 (D3 §11, D6 §12) at design level. MCR-04X storage expansion is specified in D3 §12 and MCR-06 in D3 §13 / D6 §14. MCR-07–09/11/12 and implementation/validation remain open; no code/test/build changed.
- [x] Review D0/D1 and selected existing source contracts, record REV-01–12 and readiness gates in D7, and clarify the ordinary-preset/coordinator boundary. Findings remain open; implementation is not certified ready.
- [x] Create scoped D2/D3/D6 drafts using the review findings, audit the reference Economy/menu/save contracts, calculate the save budget, and document candidate transition/API policies. Approval, host prerequisites, implementation, and validation remain open.
- [x] Create D4's scoped validation/playtest plan with case IDs, expected invariants, policy bindings, local-only fixture/evidence rules, review traceability, and an empty result ledger. No suite/test code, builds, runtime tests, or playtests were performed.
- [x] Create this checklist and link the applicable existing background documents.

These boxes confirm written coverage only. The values, final menu map, and engineering details still need the decisions below.

## 5. Decisions and detailed documents still needed

### A. Current-branch audit and control inventory — D2; D1 §§3, 13–14

- [ ] Record the target repository, branch, commit, and date. Recheck them when implementation starts.
- [ ] Inventory every affected setting: stable identifier, type/range, current default/value, owning module, save/profile scope, dependencies, and existing menu location.
- [ ] Record feature enable/disable and restart requirements without changing their defaults.
- [ ] Map proposed categories to existing pages and retain unrelated existing settings.
- [ ] Identify controls referenced by row numbers, hooks, breadcrumbs, translations, or saved selection state before moving them.
- [ ] Record actual current weapon-rebalance behavior and whether each component is runtime-switchable or already stored in equipment.
- [ ] Resolve conflicts with historical reference documents explicitly.

### B. Economy decisions — D1 §§4–8, 12; D2–D4

- [ ] Review the provisional Light/Steady/Treasure values as first-playtest candidates; keep Enhanced unchanged.
- [ ] Define Low/Standard/Frequent numeric mappings, custom limits, and a separate displayed guarantee interval.
- [ ] Specify boss classification, fixed-payment behavior, performance bonus controls, and empty-steal compensation.
- [ ] Verify Scavenger/Lucky Find behavior and descriptions; define fractional state for the new path while preserving Enhanced rounding.
- [ ] Confirm independent item/bundle selection, Super/Duper probability bounds, and disabled probability remaining “no bundle.”
- [ ] Confirm inactive redemption values and manual toggle behavior; conversion off keeps the item.
- [ ] Define legacy Relaxed/Normal/Grind presentation and price preservation; avoid applying its income multiplier to new fixed payments.
- [ ] Finalize bounded pending-reward capacity, full-queue behavior, mixed enabled/disabled categories, and between-battle application.
- [ ] Specify a safe counter-to-inventory transition with a full bag; do not discard value or assume space is available.
- [ ] Record Workshop visibility as a follow-up rather than an initial dependency.

### C. Independent category definitions — D1 §13; D2

- [ ] **Combat:** define Original Rules/Rebalanced/Custom ownership; preserve stored upgrades; exclude display-only DPS and unrelated categories. Assisted Combat requires separate review.
- [ ] **Encounters:** map Story Focus/Original/More/Custom to existing controls; document the no-random override and preserve required fights. Do not imply larger enemy groups.
- [ ] **Movement:** map Original/Comfort/Fast Exploration/Custom to audited defaults; decide battle-entry scope and preserve combat movement for Fast Exploration.
- [ ] **Inventory:** define Manual/Convenient/Custom contents; preserve manual sorting behavior and keep the counter policy owned by Economy.
- [ ] **Bestiary:** define Spoiler-Free/Standard/Reference visibility field by field, including a decision on undiscovered information; keep filters and earned progress separate.
- [ ] **Wardrobe:** confirm feasibility of Story Appearance/Owned Outfits across story transitions; preserve outfit selection/ownership, keep viewer controls separate, and add no buying.
- [ ] Give each category its own Custom detection and matching rules; adding preset metadata must not overwrite existing settings.

### D. Final navigation and menu map — D1 §§5, 14; D2

- [ ] Review the proposed category order with the player-facing labels, descriptions, and expected access paths.
- [ ] Define each category's summary, preset preview/application, common options, and Advanced page.
- [ ] Define Economy subpages and retain simple access to the preset and Junk balance.
- [ ] Decide which existing pages to reuse; avoid empty pages and unnecessary navigation depth.
- [ ] Separate F1 configuration from Aya's Catalog/Bestiary/Wardrobe actions; preserve Catalog discovery and install/remove rules.
- [ ] Give shared controls one backing value and owner; cross-category links open the owning setting.
- [ ] Specify Back behavior, restored selection/scroll position, long-list scrolling, dependency explanations, and keyboard/controller labels.
- [ ] Keep Developer Tools separate and preserve their current availability.
- [ ] Review layouts in English and Latin American Spanish, including long help text.

### E. Persistence and migration — D1 §§7–8, 13–14; D3; R1–R3

- [ ] Inspect the actual current save API, record/byte budgets, unknown-record preservation, and failure behavior. Historical fixed-offset diagrams are not current evidence.
- [ ] Record versioned settings/progress layouts and ownership; do not append fields to the asserted 36-byte `pe_economy.loot` v1 record without a versioned plan.
- [ ] Define older-save behavior: missing new settings retains legacy Enhanced behavior, existing difficulty, wallet, and progress.
- [ ] Preserve other categories' existing persistence scope, including collection profile ownership.
- [ ] Define fractional bonuses, guarantee counters, and pending reward identities across save/load and disabled categories.
- [ ] Define corrupt/unsupported records, capacity exhaustion, disabled/missing mods, and failed-save behavior without silently destroying carried data.
- [ ] Verify switching saves/New Game does not leak another playthrough's settings or rewards.
- [ ] Specify safe between-battle application and prevent rerolls, reward replay, and duplication.

### F. Extension API and multiple cooperating mods — D1 §15; D6 with D2–D4

- [ ] Audit existing hooks/events/services and activation behavior; reuse the host and keep current public contracts compatible.
- [ ] Document framework-wide contracts independently of Economy formulas and categories; use module-neutral discovery, registration, versioning, lifecycle, conflict, and diagnostic conventions.
- [ ] Create a per-module adoption matrix in D6 covering Combat, Encounters, Movement, Inventory/QoL, Economy/shops, Catalog/custom content, Wardrobe, Bestiary, localization/presentation, and future categories. Record owners, existing/proposed interfaces, capabilities, versions, dependencies, status, and validation evidence.
- [ ] Define first-slice scope: new-path battle-Junk modifiers, committed reward notifications, and provider Economy presets. Mark other modules' contracts as later adoption within the same framework, not excluded from its scope or implicitly delivered.
- [ ] Specify typed registration, calculation, and notification contracts with stable namespaced provider/entry IDs, units, bounds, payload ownership, lifetimes, and failure results.
- [ ] Define additions/multipliers, arithmetic representation, rounding/fractions, overflow limits, and owner-enforced eligibility; settle operation-specific formulas rather than a universal multiplier pipeline.
- [ ] Specify deterministic ordering/tie-breaks where sequential resolution is needed. Define duplicate IDs, conflicting replacements/limits, allowed vetoes, and visible fallback behavior; omit unresolved capabilities from the initial API.
- [ ] Require one owner to validate and commit each transaction once; prohibit side effects in calculation callbacks and prevent recursive/replayed transactions through notifications.
- [ ] Keep disabled reward categories off. Preserve Enhanced by default and report first-slice gameplay modifiers inactive on its legacy path.
- [ ] Separate stored preset/base values from effective external adjustments. Define provider summaries and diagnostic traces without leaking undiscovered effects.
- [ ] Specify additional preset field/dependency validation, localization, explicit application, category isolation, and unavailable-provider presentation.
- [ ] Define version/size/capability negotiation, dependency handling, registration limits, provider-scoped cleanup, and restart requirements; do not promise unsupported hot unloading.
- [ ] Reconcile saved IDs/progress, unknown-provider preservation, pending identities, missing content, and safe application boundaries with D3. Never save pointers or compounded effective values.
- [ ] Include examples with at least two simultaneous providers and the no-provider baseline; identify which combination decisions still need approval.

### G. Race conditions, ordering, and coherent transactions — D1 §16; D3, D4, D6

- [ ] Audit game/host/render/save/worker execution contexts; designate gameplay mutation ownership and classify API thread access without assuming existing hooks are thread-safe.
- [ ] Define stable operation inputs, contributor generations/lifetimes, authoritative execution-time validation, and calculate/validate/commit/notify phases.
- [ ] Specify cross-owner purchase/install/payment coordination, reservations or equivalent, and failure behavior before exposing multi-resource actions.
- [ ] Define reentry rejection, allowed deferred follow-ups, duplicate-operation handling, and limits preventing notification loops.
- [ ] Define synchronized worker handoff, deterministic drain ordering, queue capacities/overflow, and per-drain limits without silently losing accepted gameplay operations.
- [ ] Specify provider/preset registration changes at safe boundaries and callback lifetime during dispatch; retain restart-only behavior where required.
- [ ] Specify stale-request/asset cancellation across provider/outfit/save/New Game changes and render/GPU-safe resource publication/release.
- [ ] Specify coherent committed save snapshots and their relation to pending progress; never capture partial spend/consume/install state.
- [ ] Document lock ownership/order where needed; avoid invoking mod callbacks, I/O, or worker waits while holding shared locks. Do not promise isolation/preemption of arbitrary native code.

### H. Low-powered-machine performance — D1 §17; D4, D6

- [ ] Agree representative target hardware, OS/build/settings/frame-rate target, matched baseline, and numeric CPU/frame-time/memory/startup/queue-latency budgets.
- [ ] Define event-driven dispatch, cheap no-subscriber paths, cached registration/order, relevant-contributor traversal, and cache invalidation.
- [ ] Define reusable scratch storage, nesting/lifetime rules, registration/queue/memory limits, and clear capacity failure behavior.
- [ ] Define callback cost guidance: no blocking I/O/decoding/waits in ordinary callbacks; justify bounded worker usage on few-core machines.
- [ ] Define separately reviewed per-hit/per-frame contracts and avoid heavyweight diagnostics/allocations on those paths.
- [ ] Define optional trace/timing, bounded history, essential error reporting, and diagnostic rate limits without suppressing gameplay operations.
- [ ] Plan no-provider, multi-provider, supported-capacity, burst/full-queue, menu/viewer, hot-path, and worker-contention measurements; record unavailable hardware as a coverage gap.

### I. Memory/resource ownership and leak prevention — D1 §18; D2–D4, D6

- [ ] Inventory resource owners/borrowers and document allocation/copy/borrow/transfer/release contracts, matching allocators, and lifetimes in D2/D6.
- [ ] Define cleanup for registration/subscription/menu state, models/textures, language packs, files/handles, jobs/queues, scratch storage, and diagnostics; preserve existing borrowed-data API contracts.
- [ ] Define initialization-failure unwind, partial-load/allocation failure, rejected registration, cancellation/stale completion, and all early-exit ownership paths.
- [ ] Define dependency-safe teardown and deferred render/worker release; prevent dangling callbacks, double-free/use-after-free, and reference cycles. Retain restart-only lifecycle where required.
- [ ] Set entry/byte limits, eviction/reset points, and peak/steady-state budgets for caches/pools/history/job records; do not hide leaks in growing pools.
- [ ] Preserve previous valid state on allocation failure and distinguish transient cleanup from earned rewards, unknown records, and persistent progress in D3.
- [ ] Define live resource/allocation counters, supported leak/lifetime tools, repeat-cycle counts, soak duration, quiescent checkpoints, and pass criteria in D4; keep instrumentation bounded and local unless separately authorized for production.

### J. Small APIs and major gameplay coordinators — D1 §19; D2–D4, D6

- [ ] Identify real consumers/use cases before publishing each API; allow mods to participate through consumption/events without providing a public service.
- [ ] Define a capability catalog with purpose, owner, version, operations, dependencies, thread/lifetime rules, save implications, limits, examples, and implementation/deprecation status; cross-reference module adoption.
- [ ] Prefer narrow queries, registration, validated actions, contributions, and notifications over mutable internal access; preserve useful existing APIs and plan compatibility transitions.
- [ ] Define an explicit coordinator manifest/plan and combined player preview distinct from ordinary category presets, including affected settings, manual-edit policy, required providers, conflicts, and restart/New Game restrictions.
- [ ] Define capability discovery/version negotiation, required/optional dependencies, cycle detection, stable content references, and validation responsibilities for a multi-module plan.
- [ ] Specify exclusive replacement authority/compatibility adapters and activation refusal; do not resolve incompatible overhauls by arbitrary priority/load order.
- [ ] Define prepare/commit/abort or supported startup-only activation so required encounter/item/combat/economy parts cannot partially apply; release staged resources on failure and preserve the previous valid plan.
- [ ] Keep major native-table replacements explicitly opt-in and separately contracted; ordinary modifiers cannot bypass disabled settings or change native drops. Review migrations before changing earned/stored state.
- [ ] For future Randomizers, define seed/algorithm/content/config manifest, stable ordering/PRNG streams, plan fingerprint/mapping, RNG progress, and cosmetic/diagnostic isolation; include progression/reachability validation.
- [ ] Review generated-plan persistence capacity and save/editor/recovery compatibility in D3; define missing/version-mismatched coordinator/provider/plan behavior with no silent reroll or native fallback.
- [ ] Include a small consumer, two contributors, and a multi-capability coordinator walkthrough in D6, distinguishing examples/design from implemented support. Keep coordinator implementation outside the Economy-first scope unless separately requested.

### K. Custom content, weapon/armor effects and Economy shop contributions — D1 §20; extensions required in D2–D4/D6

- [ ] **CONTENT-01 / ownership and native audit — D2/D6:** inventory fixed-ID tables, limits and runtime assumptions across items, weapons, armor, storage, use/equip, battle stats/effects, assets/animations and serialization. Select initially supported native-compatible archetypes and reject unsupported actions explicitly. Keep the registry independent of Economy.
- [ ] **CONTENT-02 / identity and definitions — D6:** specify permanent namespaced IDs, version negotiation, bounded definition metadata, localization/assets, stable rename aliases, runtime handle generations and duplicate/conflict behavior. Keep immutable definitions separate from mutable owned instances; no saved pointers, registry indices or translated identities.
- [ ] **CONTENT-03 / instance persistence — D3:** specify quantities, upgrades, ammunition/charges, installed/unknown effects, provenance and opaque provider fields. Review old-save migration, provider schema changes and repeat-safe failures; preserve existing vanilla and ordinary mod records.
- [ ] **CONTENT-04 / actual capacity — D3:** budget complete custom inventories/storage, unknown carried data, stock and transactions within current limits. Conditional emission does not expand the 744-byte container. If expansion is necessary, review a versioned container, checksum/publication, backup/recovery and portability design separately; no silent sidecar, truncation or format expansion.
- [ ] **CONTENT-05 / missing content — D2/D3:** bind placeholder/quarantine capacity, unavailable operations, missing versus incompatible providers/effects/assets, safe equipped fallback or refused continuation, progression/coordinator dependencies and nondestructive reinstall resolution. Preserve the logical original equipment and respect subsequent player choices when considering re-equip.
- [ ] **CONTENT-06 / compatibility matrix and tools — D3/D4:** define supported old-to-new readers/migrations and bounded downgrade behavior. Distinguish unknown-data preservation from safe execution/editing; plan save-editor/export/recovery support without requiring provider code for opaque round trips. No arbitrary older-build compatibility promise.
- [ ] **EFFECT-01 / weapon and armor mod capability — D2/D6:** explicitly support custom installable effects on native or custom equipment independently of Economy. Specify stable effect IDs, native-effect adapters, required runtime capabilities, parameters/schema, applicability, slot costs/limits, built-in/removable distinctions, stacking/uniqueness/exclusions and deterministic multi-provider behavior.
- [ ] **EFFECT-02 / installed state and missing providers — D3:** persist effect IDs, parameters, slots and provenance without relying on native bit reuse or Catalog order. Preserve opaque/unknown effects and occupied slots; bind safe inactive behavior versus equipment fallback/refusal. Prevent destructive overwrite/removal and restore compatible providers without duplicate application, lost upgrades or new charges.
- [ ] **EFFECT-03 / Catalog and sales adapters — D2/D6:** preserve weapon/armor choice, independent scrolling, icons, unlock/discovery and `????` with hidden undiscovered details. Distinguish equipment sales, effect-granting consumables and installation services; define typed installation/removal/transfer contracts before claiming service support. Registration must not grant discovery or alter refund rules.
- [ ] **EFFECT-04 / transactions and validation — D3/D4/D6:** revalidate equipment target/generation, slots, conflicts, resources and capacity before coherent payment/consumption/install commit. Test mixed native/custom effects, missing/reinstalled providers on native equipment, migrations, reversed provider order, stale targets, failed operations and install/remove/transfer/Dismantle/Rebuild salvage/refund duplication routes. Tests/evidence stay local in `pe-native-debug`.
- [ ] **SHOP-01 / small API — D6:** specify capability discovery, init/restart-only owner registration, stable offer/shop/content IDs, price/quantity/currency/availability/stock policies, immutable query/quote, validated purchase request and completion status. Start with Junk; keep definitions and delivery owned by content/inventory modules.
- [ ] **SHOP-02 / multi-provider policy — D6:** deterministic ordering and attributable duplicate/conflict rejection, deliberate distinct offers for the same item, missing capability behavior, provider version changes and bounded ownership/lifetimes. No silent replacement or registration-order authority.
- [ ] **SHOP-03 / player rules — D2:** define discovery/spoiler-safe presentation, final price/modifier sources, unavailable offers, inventory/save-capacity explanations and stock persistence. Preserve Enhanced defaults, current Catalog rules and Wardrobe's absence of buying.
- [ ] **SHOP-04 / coherent purchase — D3/D6:** define prepare/reserve/commit capabilities across wallet, inventory, stock and persistence; execution-time revalidation, duplicate/retry handling and save/crash boundaries. No charge without supported delivery and persistent capacity, no partial grants, and no assumed rollback of arbitrary callbacks. Reuse shared transaction conventions; no parallel shop-only transaction authority.
- [ ] **CONTENT/SHOP-05 / scoped verification — D4:** add selected case IDs/policy bindings for all D1 §20 compatibility and purchase cases, including missing/reinstalled equipped content, failed migrations, capacity refusal, multiple providers, stale quotes, shared spends, failure/retry, unknown-data tools, bounded resources and low-powered performance. Fixtures/runners/raw evidence stay local in `pe-native-debug`.
- [ ] Review the expanded D2/D3/D4/D6 specifications and select a separately authorized delivery slice. Initial content support and Economy sales do not automatically implement pickup/drop/crafting/Dismantle/Rebuild/Randomizer adapters or arbitrary new combat mechanics.

Draft locations for this section: D2 §9 (follow-up slices E/F/G, controls/native audit), D3 §10 (logical instances/attachments/stock, capacity, migration and missing-content/save boundaries), D6 §10 (separate proposed capabilities and typed operation semantics), D4 §15 (36 unrun CNT/EFX/SHP/RES cases and PB-10–14). The unchecked gates above require approval, final concrete schemas/headers/limits, actual source audit and later verification; writing the drafts does not complete those gates.

### L. Pre-implementation findings — D7; scoped D2/D3/D4/D6

- [ ] **REV-01:** budget all live/carried/unknown records and headers, define capacity failure before enabling new saved settings, and test near-full saves.
- [ ] **REV-02:** separate execution engine from preset label; define legacy/new/Custom transitions, repeat application, all progress/RNG/pending ownership, and toggle-exploit policy.
- [ ] **REV-03:** settle storage × income × redemption combinations, wallet availability, cap/full-bag policies, and accepted-credit transaction results.
- [ ] **REV-04:** resolve preset application versus redemption of already owned bundles; disclose conversion consequences and settle consent/safe-boundary behavior.
- [ ] **REV-05:** define independent price-policy ownership/persistence and legacy difficulty transitions without baking equipped discounts into stored prices.
- [ ] **REV-06:** distinguish new-path identity guarantees from legacy rerolls; define success/reset states, queue backpressure/fairness, redundant/empty-pool outcomes, and eligibility counters.
- [ ] **REV-07:** specify the small typed layer over existing host mechanics, deterministic ordering, activation/discovery/lifetime, error handling, and source API versus binary ABI scope.
- [ ] **REV-08:** distinguish coherent normal saves from crash snapshots/recovery and interrupted writes; define committed-state capture without unsafe crash-path locks/callbacks.
- [ ] **REV-09:** define new-path RNG, record-status/missing/corrupt/newer defaults, charm/temporary state, and New Game/save-switch rules while retaining legacy behavior.
- [ ] **REV-10:** define pure preview/diagnostic queries and stale-preview validation; verify they do not consume RNG, mutate guarantees, reserve resources, or trigger payments.
- [ ] **REV-11:** select the implementation delivery slice and satisfy its readiness gates; accept the scoped D2/D3/D6 drafts and bind D4's created plan to final policy/budget criteria without requiring every deferred feature to be implemented.
- [ ] Review the candidate D2/D3/D6 decisions explicitly: storage restrictions, redemption consent, return-to-Enhanced pricing, frozen progress/charm, queue success/settlement, 160-byte record, arithmetic/capacities, and init-only lifecycle. Revise D1 where an accepted refinement differs from its broader options.
- [ ] Resolve the newly source-confirmed page/label INI key migration before moving persisted rows; approve stable identities/aliases and precedence, without changing scopes or importing stale aliases over newer values.
- [ ] **REV-12:** carry the ordinary-preset versus explicit coordinator authority boundary through D2/D6 and future tests; matching top-level wording is clarified, but no coordinator policy is implemented.

### M. Multi-provider custom-content/shop review — D7 MCR-01–12

Read D7's **Custom content and shop API review — October 31, 2026** before implementing D2 E/F/G. The existing CONTENT/EFFECT/SHOP checklist is draft coverage, not closure of these findings. Apply only the gates relevant to the selected delivery slice; current save-host work and other categories remain independent.

- [x] **MCR-01 / design disposition:** D6 §§11.1–11.3 bind provisional owner manifests, atomic batches, authenticated duplicate-all failure, canonical seal/publication, explicit per-owner/domain count/byte profiles and deterministic domain refusal on global overflow. No first-registered subset, retry or budget borrowing. Implementation/measurement remain unverified.
- [x] **MCR-02 / design disposition:** D6 §11.4 binds typed public references versus owned mutation, opt-in external sales/effects/extension points, target-shop and stock-owner permission, and independent attachment framing. Unauthorized namespace claims cannot poison an authorized owner's entry. Actual persistence encoding remains MCR-04/05.
- [x] **MCR-03 / design disposition:** D6 §11.5 binds collector/bootstrap/collect/seal/publish/run phases, required service and batch DAGs, permitted passive reference cycles, optional adapters, fixed-point failure propagation and restart-only lifecycle. The small shared seal/readiness facility is a future prerequisite, not existing host support.
- [ ] Implement and verify MCR-01–03 contracts only under separate code authorization: finalize public C payloads/profile byte accounting, audit host phase/dependency integration, and validate local quota/conflict/ownership/graph/cleanup cases. Design-resolution boxes above do not claim implemented registry support or close E/F/G/G2/G3 acceptance.
- [x] **MCR-04 / design disposition:** D3 §§11.1–11.4 bind native-complete equipment records, one shared `pe_content.ledger` v1 owned by the content core, fixed-width encoding, declared-maximum accounting with one reservation-based admission authority, and P0 (178 B) / P1 (1,360 B, supported minimum) profiles. P1 does not fit beside the policy record (48 B free), so persistent custom instances stop at MCR-04X below. Discovery/stock/operation state is not in this ledger; MCR-06/07/09 declare their own sub-budgets.
- [x] **MCR-05 / design disposition:** D6 §§12.1–12.5 bind the content core as sole mapping authority, anchored by (pool index, fingerprint); equipment kinds 1–9 only; no stack equivalence or merging; identity lifecycle across create/move/sort/equip/battle/save/destroy; current-branch native path audit with file:line; required pre-free and merge veto hooks. `reserved02` is not free for tagging.
- [x] **MCR-04X / design disposition:** D3 §12 and D6 §13 specify the save extension store: one linked companion file per save in a hidden `.pe-ext` folder beside the card (card listing skips folders and dot-names; an extra card file would cost a slot). It holds per-owner sections with independent CRCs and a 5 KiB v1 profile (ledger 2,048 / discovery 1,024 / stock 512 / operations 256 / unassigned 1,152 / overhead 128; raised from 4 KiB by D3 §13.2). The companion is written first and the card rename is the commit point; a 32-byte `pe_host.extlink` sits in the tail, and the 744-byte tail closes to new records after policy + link. A missing companion for a save with custom items prompts *Continue without mod data / Back*.
- [x] **Approvals delegated by the user (October 31):** native-complete rule, 32-byte attachment ceiling, P1 supported minimum, All-mods-off preservation exception and outer load gate adopted as written (D3 §11.6).
- [ ] Implement and verify the content core (layer C, after Section 5 N's unit S) only under separate code authorization:
  - close the D6 §12.4 audit items (fingerprint field immutability, carry-over reset meaning, complete retail record-freeing sites);
  - build the ledger parse/serialize/accounting, reconciliation, native veto hooks, the inert-without-ledger rule, and the Custom items page with Convert / Remove record (D3 §14.5);
  - run the D4 §15 MCR-04/05/10 bindings and the layer C rows of "Mod on/off bindings".
- [x] **MCR-06 / design disposition:** D6 §14 and D3 §13. The Catalog owner keeps custom discovery in the `pe_economy.discovery` extension section (1,024 B); native unlocks stay unchanged in `pe_economy.catalog` v1.
  - Facts: Seen and Unlocked are stored and sticky; Carried is derived live; Installed is a ledger attachment.
  - Only committed supported actions change facts; there is no relock.
  - Identity: namespace + stable ordinal with a key guard; declared renames and absorbs.
  - Offers referencing one entry share its entitlement.
  - Undiscovered entries show `????` and generic text.
  - Space is reserved at seal; the extension profile is raised to 5,120 B.
- [ ] Implement and verify MCR-06 under separate code authorization (after the extension store and ledger): Catalog adapter merging native and custom entries, discovery section, transition hooks in dismantle/delivery/purchase, spoiler-safe text; run the D4 §15 "MCR-06 acceptance bindings".
- [ ] **MCR-07:** bind stock-pool ownership, units, scope, consumers, restock/revision/rename migrations and one-time entitlements so several offers/providers cannot reset or inconsistently consume the same stock.
- [ ] **MCR-08:** bind authoritative quote validation and bounded bookkeeping, reservation ownership/order, final fallible validation and non-failing publication boundary. Native unsupported commit adapters must refuse readiness rather than partially purchase.
- [ ] **MCR-09:** bind coordinator-issued operation token/payload identity, retained terminal results, changed-payload refusal, table bounds/backpressure, wrap and save/load invalidation. Observer failure after commit must not report an aborted purchase.
- [x] **MCR-10 / design disposition:** D6 §12.6 names the content core as the minimum compatible reader: host-level, in every `PE_MODS` build, outside Manage mods, running with All mods off, with a reader revision checked against the ledger's `min_reader`. D3 §11.5 binds the native-plus-ledger representation in every state (ACTIVE/UNAVAILABLE/UNCERTAIN/ORPHANED) for provider off, Economy off, All mods off, vanilla, older build, save editor, over-profile, newer format and invalid data, with an outer load gate and demote-only reconciliation. Vanilla/core-less builds are documented one-way ledger loss, not prevented.
- [ ] **MCR-11:** bind owner-specific composed effect/pricing arithmetic, range/overflow/conflict rules and base-persisted versus computed stats. Do not borrow payout arithmetic for combat/pricing or change balances through this review.
- [ ] **MCR-12:** extend D4 bindings/cases for one-many/many-one/mixed packs, three-way conflicts, deterministic permutations, partial batches/manifests, stock revisions, token/core absence, count and byte limits, failure cleanup and measured scale. All raw tooling/evidence remains local in `pe-native-debug`.

Resolve design findings with their documented rules and linked acceptance bindings; implementation/runtime acceptance still needs actual evidence. MCR-01–03 now have recommended design dispositions in D6 §11 and D4 §15 coverage; public C layouts, technical-profile measurements, native-path audit and storage/publication capabilities remain future work. MCR-04/05/10 now have recommended design dispositions in D3 §11 and D6 §12 with D4 §15 bindings; the MCR-04X storage expansion they required is specified in D3 §12 / D6 §13. MCR-06 discovery is specified in D3 §13 / D6 §14. Suggested next document units: MCR-07 stock, then MCR-08/09 quote/commit and tokens, then MCR-11, then MCR-12. No implementation is authorized by this document update.

### N. Turning mods on and off; build layers — D3 §14

Layers: **S** save safety and extension store (mod-independent, useful now), **C** content core (mod-independent, only with custom items), **M** mod-owned features (Catalog discovery, shop, effect rules). Dependencies point only S ← C ← M. Build S first.

- [x] **Design disposition (October 31):**
  - D3 §14: layers and build order; All-mods-off behavior (core inert without a ledger, following the always-installed save host); missing-mod notice; save-slot warning; Custom items page with per-item Convert; tester guidance; limits of the promise.
  - D2 §9: the "Mod on/off controls" table.
  - D6 §12.6: the core boundary.
  - D4 §15: "Mod on/off bindings".
- [ ] **Unit S: implement and verify only under separate code authorization.** Build:
  - the extension store (card path access via `Host_CardPath`, directory create/list/remove, extension write before the card rename, `pe_host.extlink`, generation cleanup);
  - the outer load gate for any unreadable mod data, with the missing-extension prompt;
  - the missing-mod notice;
  - the save-slot warning, after auditing a safe native hook point in `save_flow.c`;
  - the two Manage mods options.

  Run the D4 MCR-04X bindings and the layer S rows of "Mod on/off bindings" using today's records.
- [ ] Unit S follow-ups: the save editor opens and keeps linked extensions and offers a bundle export; the crash report dumps extension sections; a future explicit import also copies `.pe-ext`; the D-v0.7 editor save-location fixes can share this work.
- [ ] With unit S: update `mods/README.md`'s All-mods-off wording (D3 §14.2) and add the tester guidance (D3 §14.6) to the player/tester guide.

### O. Versioning and migrations — D3 §15, D6 §14.9

- [x] **Design disposition (October 31):**
  - six version kinds with one meaning each (container/file format, layout version, `min_reader`, content revisions, interface versions, writer identity);
  - append-only changes with prefix read for extension sections; tail records keep the current rule, and evolving data goes in sections;
  - frozen single-step upgrade chains with defaults set in the step that adds a field;
  - content migration through declared per-instance steps;
  - golden fixtures for every released version;
  - a load log, an F1 save diagnostics page and a format-upgrade save warning;
  - the provider obligations in D6 §14.9.
- [x] **Version table created** (D3 §15.6) for all current tail records, legacy v0 blocks and proposed records/sections.
- [ ] **Standing obligation:** every layout change updates the D3 §15.6 row, adds a frozen upgrade step and a golden fixture in the same change, and never edits a released step. Check this in review.
- [ ] Implement under separate code authorization:
  - with unit S: chain helper (`pe_save_upgrade_chain`, name illustrative), prefix read with trailing-byte preservation in the extension store, writer revision in the extension header, diagnostics page and format-upgrade warning;
  - with unit C: per-instance content migration hook.

  Build the fixture suite in `pe-native-debug` and run the D4 "Versioning and migration bindings".

### P. Character packs and standalone Wardrobe — D8

Requirements from the user (November 1): a downloadable character replacement/addition format in the style popular for PS1-era games (BioRand, Classic REbirth); the Wardrobe as its own mod that anyone can use, with Economy only paying for it.

November 2 scope direction: prioritize Wardrobe importing of already PE-compatible formatted player skins (D8 §11). Defer enemy/Bestiary drop-in packs and NPC/enemy replacement; potential sources in other decompiled games need later source/runtime-specific design. Standalone Bestiary separation/tracking is still in scope independently.

- [x] Record Wardrobe-only importing focus, compatible-prepared-assets requirement and accessible folder UX in D8 §11; this is documentation, not loader implementation.
- [ ] Add Wardrobe Open content folder plus resolved writable path/layout/restart/refusal guidance when the pack reader is separately implemented. Preserve proposed `<preferences>/packs/` and existing `pe_skins/` compatibility; no automatic foreign-model conversion or game-file overwrite.
- [x] **Phase 1 user decision documented (November 2):** D8 §12; Wardrobe views/equips compatible costumes freely alone. Economy controls current unlock rules through its default-on optional toggle, without changing true ownership or other Economy behavior. No extra viewer buying, new acquisition algorithms or balance changes.
- [ ] After the phase 1 extraction/compatibility baseline, discuss and separately implement Economy acquisition presets, progression/challenge rewards or other improvements. These are not required for phase 1; Wardrobe importing/folder UX is a separately staged feature too.

- [x] **Requirements and design recorded:** D8 §§1–7.
  - Pack format v1: a plain zip, or the same layout as a folder, in `<preferences>/packs/`, with `pack.json`, `LICENSE` and one `characters/<base>.<source>[$<variant>]/` folder each, holding `character.json`, the existing skin files and `face.png`. Data only, hardened zip reading, per-character validation, existing `pe_skins/` kept as an implicit pack.
  - Packs state a price *tier*, never Junk.
  - Wardrobe split into `pe_wardrobe`, with its own profile and a one-time import from `pe_collection.ini`.
  - Phase 1 acquisition policy (November 2, D8 §12): standalone Wardrobe offers all installed compatible costumes; Economy owns default-on Costume unlock rules with an optional off toggle. Effective access never grants permanent ownership; other Economy functions stay independent.
  - Economy registers as the Wardrobe's shop (`wardrobe` v2), mapping tier → the user-kept 25/50/100/250/400 curve; the Wardrobe never calls Economy. v1 services stay.
  - Copyright rule: disc-derived characters are shared only as recipe packs built from the player's own disc.
- [ ] **User decisions** (D8 §8): ship the recipe builder as a standalone tool or build in the game later; whether the Wardrobe page buys directly, or only Wayne's Workshop (with the Workshop Overhaul decisions); whether the project hosts a pack index.
- [ ] Implement under separate code authorization, in order:
  1. split `pe_wardrobe` from `pe_collection` with the profile migration and `format` lines;
  2. `wardrobe` v2 and the Economy shop adapter, keeping v1 working;
  3. the pack reader and the F1 Packs page;
  4. the recipe pack builder.

  Run D8 §7 PACK-01–07 and WRD-01–06. Add the pack, profile and skin binary formats to the D3 §15.6 version table when built.
- [ ] Later, each needing its own research: NPC/enemy replacement, voices, a glTF → PE authoring tool for original characters.

### Q. Standalone feature boundaries — D9; D8/D2/D3/D6

November 2 phase 1 decision: D8 §12 / D9 §8 supersede earlier open acquisition/default wording. Wardrobe views/equips freely alone; Economy optionally enforces current unlock rules through its default-on toggle. SPL-01 is design-resolved for this phase; SPL-02–09 and implementation/validation remain open.

Review status: D9 §8 design-resolves SPL-01 for phase 1; **SPL-02–09 remain OPEN**. The checked draft/specification deliverables below confirm written coverage, not complete migration/service/behavior decisions or implementation readiness. Section 5 R tracks the new scoped gaps.

- [x] Record the recommended feature split and current checked coupling, while retaining the user's latest D8/other document edits. D9 distinguishes independent Wardrobe/Bestiary, wallet versus reward responsibilities and optional Catalog/shop adapters; this is review documentation, not extraction approval.
- [x] Extend D2 §10 (control/dependency ownership), D3 §16 (profiles, imports and one-writer compatibility), D6 §15 (standalone capabilities and optional adapters), and D4 §16 (PB-15–18 and 24 planned STN cases). D8 §10 aligns earlier import/price/payment recommendations. Documentation complete for this slice; all code/native integration and runtime checks remain unimplemented/unrun.
- [ ] Re-audit the selected implementation branch for cross-feature symbols, service publishers, native packs, build/mod dependencies, settings aliases and every profile/save writer. D9's limited check is in `pe-mod-presets`; D8's UI observations use `pe-requisition`.
- [x] **Phase 1 Wardrobe policy recorded:** D8 §12, D2 §10, D3 §16.5 and D6 §15.5 bind all-available alone, Economy default-on Costume unlock rules/explicit off, stored false retention, no permanent grant, failed-payment restriction and safe re-restriction. No new viewer buying; actual implementation/payment/migration remains unchecked. Bestiary retains its independent earned behavior.
- [ ] Implement/verify the phase 1 policy only under separate code authorization, preserving current Economy-on sources/prices and true ownership; bind remaining profile/key/runtime/payment gates. Paid Bestiary scope and later acquisition improvements remain separate.
- [x] **Recommended profile/alias contract:** D3 §16 and D6 §15 specify separate format-1 feature profiles, one-time import markers/no repeat merge, unchanged legacy sources, canonical setting precedence and a nonpublishing legacy build alias. Concrete code/parsers/native migration and acceptance remain unchecked; no reset may resurrect old facts.
- [ ] Specify optional payment/acquisition adapters and multiple-adapter identity/selection. Resolve per-save wallet versus profile-wide unlock publication/failure under MCR-08/09; spend-then-grant is not a sufficient atomicity guarantee.
- [ ] Design one wallet/routing authority independent of enhanced rewards while preserving existing mixed loot records. Evaluate Catalog and shop extraction separately; moving a folder cannot rename persisted keys or create duplicate balances/serializers.
- [ ] When separately authorized, extract and verify Wardrobe/Bestiary first, then staged Economy boundaries; maintain an accessible default/aggregate configuration and shared host helpers rather than one selectable mod per source file.
- [x] Extend D4/D8 planning with standalone/build-absence/all-off, migration/reset, multi-adapter, v1 service/price compatibility, resource and cross-store failure coverage (STN-01–24); no cases executed. All future tests/raw evidence stay local in `pe-native-debug`.
- [ ] Finalize and implement only the separately authorized extraction scope; bind PB-15–18, actual target symbol/build audit, atomic profile writer and cross-store MCR-08/09 protocol before claiming paid adapter support. Validate real standalone binaries/paths rather than only mocks.

### R. Standalone specification review — D9 §7, SPL-01–09

- [x] Review D2 §10 / D3 §16 / D6 §15 / D4 §16 / D8 for missing or conflicting standalone contracts; record nine findings with references, recommended dispositions, acceptance extensions and scoped readiness in D9 §7. No new source audit, tests, build or code changes performed.
- [x] **SPL-01 / phase 1 design disposition:** D8 §12/D9 §8 and D2/D3/D6 bind the November 2 user decision: standalone free access, Economy-owned default-on optional restrictions, no grant/reset, payment failure remains restricted, safe fallback when restrictions return, no new Wardrobe buying. D4 PB-17/STN-10/11/18/19 and WRD-01–03/06 carry planned acceptance. No code/tests implemented; SPL-02–09 stay open.
- [ ] **SPL-02:** bind migration identity/receipt/recovery when destination or its marker is missing, deleted, damaged, copied or changed after import. Resolve first-run import versus lost migrated data; do not promise no resurrection from an in-file marker alone.
- [ ] **SPL-03:** assign concrete single-writer build/lifecycle and field authority for mixed loot and Catalog/Rebuild records in wallet-only, rewards-off, absent-owner and All mods off combinations; keep storage keys/layouts and inactive data.
- [ ] **SPL-04:** produce exact v1 service/action/price/key/mod-ID and build/settings alias compatibility matrix on the selected target. Preserve old slash keys without blindly applying new key rules; define results when safe legacy purchase behavior is unavailable.
- [ ] **SPL-05:** classify every legacy/new UI, service and Workshop purchase/grant path; enforce MCR-08/09 for new profile-plus-save paid support and define earned/profile-write failure status. No spend-then-grant safety claim or silent change to untouched legacy behavior.
- [ ] **SPL-06:** bind feature/action-scoped adapter selection owner, persistence/default/eligibility rules, explicit missing-selection behavior and quote invalidation; no implicit fallback to another provider's price policy.
- [ ] **SPL-07:** bind supported profile concurrency/external-edit policy, atomic publication versus lost-update protection, dirty/failed flush and migration-source identity. Two processes/editors are not solved by one in-process writer.
- [ ] **SPL-08:** audit target shared viewer/model/input/tick/cache/pack/gameplay-hook ownership and cleanup; verify single-feature builds, both-viewer use and story/room appearance transitions. Shared library placement alone does not prove independence.
- [ ] **SPL-09:** before the new pack reader, reconcile D8 version selection/author/partial-pack rules with D6 deterministic batch admission, namespace provenance, equal-version payload conflicts, preserved keys and combined limits. Keep the existing-skin extraction slice separate from later pack work.

Close design findings with explicit D2/D3/D6 dispositions and PB-15–18/STN coverage; implementation acceptance requires later real evidence. D4's 24 STN cases stay planned and need the D9 acceptance extensions. Basic extraction gates differ from new paid adapters and the later pack reader; do not require unrelated future scope or mark open gates solved by committing the review.

## 6. Implementation checklist — only after a separate instruction to build

### Branch kickoff — October 31, 2026

Created local branch `feat/mod-presets-framework` in the isolated checkout [D:/Recomp Games/pe-mod-presets](<D:/Recomp Games/pe-mod-presets>), based on fetched upstream `origin/main` at `8c52cdde5d60ee52f00913517ffb593e9521bf2d`. Existing localization/UI worktrees remain on their own branches. The new branch is not pushed and does not track upstream main. Branch creation/initial read-only audit does not approve every provisional balance or API choice in D2/D3/D6.

- [x] Select/create the isolated implementation branch and record its upstream base.
- [x] Recheck this base's save-host header/packing and native save-write integration. The 744-byte container and carried-record omission policy remain present; the save hook returns no direct write-failure result. These are source checks, not executed regression tests.
- [x] **First code unit — read-only save provenance and capacity queries:** implemented `pe_save_query.h/.c` with last-load/current-carried status, record load outcomes, complete live/carried union accounting, hypothetical registration projection, limits and uncertainty reasons. `pe_save_plan.h` shares selection with the unchanged-policy writer. This is inspection, not save permission or veto.
- [x] Verify the query locally in `pe-native-debug`: 21 query cases, three modes of the existing source regression fixture, and byte-identical output for 100 full card images versus upstream `8c52cdde5`. Rebuilt the native game and passed five existing save/crash/inventory CTests. This exercises first-unit subsets of D4 SAV/MOD cases, not all 83 cases or crash atomicity.
- [x] **Capacity admission/refusal unit:** normal save dispatch checks the complete valid live/carried union before hooks and again afterward. Tail packing is staged, overflow refuses without publication/carry mutation, and native serialization aborts before CRC/file scheduling. Save-slot startup exits through its error UI and restores sequence. Nested writes/registrations are guarded. Over-capacity crash-tail snapshots are reported unavailable instead of truncated.
- [x] Verify capacity refusal locally: 8 owner admission cases, 3 actual-host dispatch cases, 1 extracted-native serializer/slot control-flow fixture; rerun 21 query cases, 3 existing fixture modes, and 100 byte-identical supported card images. Native rebuild and 6 existing CTests pass; no-mod native save-flow source also compiles. Evidence is local in `runs/save-queries/admission-*`. The extracted gate fixture has surrounding boundaries stubbed; it is not a full UI/disk-fault playthrough.
- [x] **Conditional-record host prerequisite:** `pe_save_emission.h` provides init-time dormant registration and explicit checked owner activation. Dormant records occupy a registry slot but no save header/payload bytes. Activation checks complete union capacity, initialized owner state and source provenance; loaded/used records stay preserved. Valid-CRC rejected/newer optional records are carried intact. Existing ordinary records and serialized format are unchanged.
- [x] Verify conditional emission locally: 25 new cases plus rerun 21 query and 12 admission/host/native-gate cases, 3 existing fixture modes, 100 byte-identical supported card images, native rebuild and 6 existing CTests. Evidence and source/executable hashes are local in `runs/save-queries/emission-*`; no new test files enter the game repository.
- [ ] **Next prerequisite — policy semantics and coherent crash images:** bind the actual candidate policy layout/validation and readiness rules before registering/enabling preset data. Conditional activation now conservatively refuses uncertain sources, but no actual policy record or preset transition exists. Whole native-plus-mod coherent crash capture remains separate. Existing damaged-record recovery and whole newer-container passthrough intentionally remain compatible.

New rewards, 160-byte policy registration, preset activation, broad menu reordering, and public contribution APIs follow their dependent gates. Safe whole-save crash capture remains a separate required design/implementation step. Kickoff initially changed no code; read-only queries, capacity refusal and conditional emission are now implemented and rebuilt on October 31, with uncommitted source and local-only fixtures. Numeric gameplay and shared callback composition policies are still provisional. Evidence: `D:/Recomp Games/pe-native-debug/runs/save-queries/` (query/admission/emission manifests, results, build and CTest logs). The rebuilt executable is `D:/Recomp Games/pe-mod-presets/build-mods/parasite-eve-pc.exe`; there was no interactive game playthrough. This protects valid carried records from capacity omission; it does not recover bytes the existing parser already rejected or provide rollback of arbitrary mod callback side effects.

References: D1 §§9, 12–19; approved D2 and D3, plus D6 for extension work.

Readiness: close applicable D7 gates before the corresponding coding. G4's criteria/plan precede behavioral implementation and its measured results precede release; G5 stays deferred until coordinator work is requested. Record each finding's disposition and supporting document rather than checking it off merely because it appears in the proposal.

- [ ] Record the authorized scope; implement Economy first unless the user chooses a different scope.
- [ ] Separate wallet, battle income, bonus reward generation, redemption, preset/settings, and presentation responsibilities.
- [ ] Keep Enhanced's existing calculation/cascade/queue path compatible; isolate the new configurable path.
- [ ] Implement canonical settings and category-local preset definitions without duplicating game rules in menu code.
- [ ] Add explicit preview/apply behavior and preserve unrelated settings.
- [ ] Add persistence/migration with documented versions and capacity handling.
- [ ] Register/reorganize controls through their owning modules, preserving stable identifiers and safe navigation.
- [ ] Add stable translation keys and Latin American Spanish interface text; keep translated text out of saved identifiers.
- [ ] Add clear reward-source feedback and inactive-system explanations without excessive battle popups.
- [ ] Implement additional categories separately, only after their definitions and scope are approved.
- [ ] If extension work is authorized, implement feature-owned contracts and owner-scoped registration/resolution separately from menus, persistence, and transaction commit; retain no-provider parity.
- [ ] Keep shared extension infrastructure free of compulsory Economy dependencies; add each subsequent module through reviewed, versioned contracts and update its adoption status separately.
- [ ] Implement reviewed execution-context, transaction coordination, bounded handoff, lifecycle/resource-lifetime, and coherent save boundaries in their owning modules.
- [ ] Implement cached/empty dispatch paths, bounded scratch/queues, and optional diagnostics separately from game rules; do not sacrifice safety or gameplay results for speed.
- [ ] Implement resource ownership/cleanup and failure unwind in the owning modules, including deferred release and bounded caches; preserve saved state and current valid assets on failure.
- [ ] Publish only the reviewed capabilities needed by actual consumers; keep future Randomizer/overhaul coordination separate and implement it only under its own approved scope/contracts.
- [ ] Record the actual changed files/commits and any departures from the proposal in D4.
- [ ] When separately authorized, implement the custom-content registry/native adapters and instance persistence first, with one reviewed item/weapon/armor example independent of Economy; then implement the narrow Economy shop capability and two independent provider examples. Close applicable CONTENT/SHOP gates above before acquisitions can persist.

## 7. Verification and playtesting checklist — D1 §11; D4

For every result, record the build/commit, configuration, expected outcome, observed outcome, date, and local evidence path. Never copy a historical pass into a new build's results.

- [ ] Bind D4 PB-01–09 to accepted policies/build scope, select mandatory case IDs and actual target hardware/budgets, and record blocked/deferred cases explicitly before claiming acceptance.

- [ ] Rebuild the affected native targets and record the output location and result.
- [ ] Compare untouched Enhanced/new defaults and migrated saves against the previous build: payouts, rounding, rare cascade, bundles, prices, queues, and Wayne preferences.
- [ ] Compare native rewards under counter-only/Vanilla-drops settings, including native bundles and successful Junk steals.
- [ ] Exercise pickups, storage, full inventory, Wayne crafting/hand-ins, counter transitions, and one-time bundle conversion.
- [ ] Test independent switches, named/numeric synchronization, Custom detection, and preview versus explicit application.
- [ ] Test separate reward families, probability bounds, guarantees, equipment modifiers, and fractional carry across saves.
- [ ] Test disabled-category freeze/resume, pending identities, capacity limits, mixed queues, and between-battle changes.
- [ ] Test legacy ↔ new-path ↔ Custom transitions, repeat presets, changed guarantees, queue admission/reset states, redundant effects, and new-path RNG/save provenance as resolved in D7/D3.
- [ ] Test wallet cap/full-bag storage combinations and existing-bundle redemption previews/consent; no new-path item consumption or accepted value may disappear silently.
- [ ] Test carried/unknown/newer records near save capacity and dependency records that fail validation; test crash/interrupted transactions separately from ordinary save/load.
- [ ] Repeatedly preview/hover/inspect and compare the next actual operation's RNG/progress/payment against a control; revalidate stale quotes before commit.
- [ ] Attempt toggle/equip/load/Dismantle/Rebuild reward duplication routes; retain existing anti-exploit protections.
- [ ] Change each category while checking all others remain unchanged; verify stored equipment and collection ownership/progress are intact.
- [ ] Verify Story Focus required encounters, Movement combat-speed boundaries, and Inventory manual-sort behavior if those categories are implemented.
- [ ] Verify Bestiary visibility policies and Wardrobe story transitions/viewer controls if implemented; presets must not grant or reset progress.
- [ ] Test old/missing/corrupt/unsupported settings, multiple saves, New Game, absent mods, and save-capacity handling.
- [ ] Check English/Spanish layouts, controller/keyboard input, long lists/help, Back/scroll restoration, Aya's sidebar, and Catalog discovery rules.
- [ ] Run appropriate existing checks plus new local tests; document failures and limits rather than claiming an unrun full-suite pass.
- [ ] Playtest Light/Steady/Treasure progression, reward variability, and indirect upgrade value; distinguish mathematical estimates from actual play/simulation evidence.
- [ ] Review provisional values with the user before any subsequent balance adjustment.
- [ ] For extensions, compare no-provider results against the unchanged baseline, including Enhanced and native drops.
- [ ] Test two or more providers, reverse registration order, equal priorities, defined arithmetic/fractions, duplicate IDs, invalid/overflow contributions, and conflicts; confirm deterministic outcomes and attributable diagnostics.
- [ ] Test disabled categories, recursive calls, notification-triggered replay, and transaction side effects; verify one commit per operation.
- [ ] Test provider disable/restart, missing dependencies/API versions, registration capacity, and stale/duplicate callback or menu prevention under the supported lifecycle.
- [ ] Test save/load with missing providers/presets and pending rewards; preserve unknown records and prevent compounding effective values, rerolls, or duplicate payments.
- [ ] Verify selected preset versus effective-value summaries, category independence, English/Spanish provider labels, and diagnostics respecting discovery rules.
- [ ] Verify shared infrastructure remains usable without Economy enabled/installed as supported by the host; run contract-specific no-provider/multi-provider/lifecycle checks for each adopting module and leave unimplemented adoption rows open.
- [ ] Test competing spends/item consumption, cross-owner failures, nested callbacks/notification loops, settings/registration changes during dispatch, queue saturation, and execution-time revalidation using controlled interleavings.
- [ ] Test worker completion after outfit/provider/save changes, resource lifetime during render use, and save capture at transaction phases; verify coherent results and no stale publication/replay. Use race-detection tools where supported and record limitations.
- [ ] Benchmark matched previous/framework builds with zero, representative, and maximum supported contributors on the agreed low-powered target; record hardware, commit, settings, sample sizes, cold/warm runs, and coverage gaps.
- [ ] Record mean/tail frame and dispatch costs, worst stalls, allocation counts, memory high-water marks, startup/menu cost, and queue latency/backlog against agreed budgets.
- [ ] Compare diagnostics off/on and justified worker handoffs on few-core hardware; verify bounded growth, unchanged outcomes, and no callback skipping or lost state under load.
- [ ] Attribute performance regressions to dispatch, contributors, assets, or instrumentation; repeat matched runs as needed and record pass/fail per adopting module rather than assuming Economy results cover all mods.
- [ ] Repeat menu/viewer open/close, model/outfit/language changes, provider lifecycle, save/load, and New Game; compare live allocation/resource counts at equivalent quiescent checkpoints after cache warm-up and deferred cleanup.
- [ ] Test initialization/partial-load/allocation failures, rejected registrations, full queues, cancelled/stale workers, early exits, and shutdown with work pending; check leaks, dangling references, double-free, and preserved progress.
- [ ] Verify cache entry/byte caps, plateau behavior, handle/job/registration counts, and steady/peak budgets; distinguish live leaks from allocator/driver retention or fragmentation.
- [ ] Run available leak/heap/lifetime tools and the agreed multi-provider/low-memory soak; record tool limitations, cycle counts, duration, baseline/end counts, and per-module results without certifying untested paths.
- [ ] For any later coordinator, test missing capabilities/versions, cycles, conflicting replacements, combined preview/manual-edit policy, failed staged activation, and cleanup; verify no partially active required plan.
- [ ] For any later Randomizer, verify identical-manifest reproducibility, registration-order independence, isolated cosmetic/diagnostic RNG, progression validity, and save/load continuity. Test missing/mismatched plans/providers and seed/config changes without silent rerolls or data loss.
- [ ] Measure multi-module plan generation/publication, memory peaks, queues, and lifecycle safety against D1 §§16–18; do not inherit single-module test/performance passes.
- [ ] For custom content/shop adoption, execute the D1 §20 matrix and newly scoped D4 cases: old saves/no-provider parity, instance/effect preservation, missing/reinstalled/incompatible providers, equipped fallback/refusal, missing assets, migration failures, full capacity, stock persistence, reversed provider order/collisions and unknown-data editor round trips.
- [ ] Test purchase refusal/retry/interruption, stale prices/providers, concurrent logical spends, save/crash boundaries and duplicate requests; verify coherent item/payment/stock state without extra charges, grants or save-data loss. Measure bounded resource usage and repeat-use cleanup for each adopting module.

## 8. Delivery and documentation checklist — D4–D5

- [ ] Update D1 with final decisions, implemented scope, approved values, and remaining follow-ups.
- [ ] Finish D2's actual control/menu map and D3's implemented persistence/version details.
- [ ] Finish D4 with build/test/playtest evidence, known limitations, and open issues.
- [ ] Finish D6 with the implemented API version, supported operations, composition/conflict rules, lifecycle/save requirements, and multi-provider examples; publish no unsupported compatibility guarantees.
- [ ] Distinguish framework-wide architectural coverage from actually implemented module contracts in D6, developer examples, and release notes. State Economy-first rollout explicitly and retain later module adoption as open work.
- [ ] Include threading/transaction restrictions, supported queue/resource limits, slow-callback guidance, and measured target-hardware results in D6/D4; leave unsupported thread-safety/performance claims explicitly unverified.
- [ ] Include ownership/release/failure contracts in D6, resource inventory in D2, persistent-state boundaries in D3, and leak/soak evidence in D4; keep unverified leak/lifetime claims open.
- [ ] Keep the capability catalog/status current, document compatibility commitments and small examples, and separate available Economy-first APIs from proposed Randomizer/overhaul support in release notes.
- [ ] For later custom-content/shop releases, document supported archetypes/actions, stable ID/schema/API versions, save capacity/reader limits, missing-mod placeholders/equipment recovery, restart requirements and actual transaction guarantees. Link provider examples and verified tests; do not describe proposed APIs as available.
- [ ] Update D7 finding dispositions and gate evidence; leave deferred/unresolved findings visible and do not equate document completion with release acceptance.
- [ ] Update the maintained Player Guide/README with default behavior, preset summaries, Custom controls, storage/redemption explanations, and new navigation paths.
- [ ] State clearly that normal drops remain, Enhanced is unchanged, settings categories are independent, and Wardrobe has no buying functionality.
- [ ] Explain any restart or save-specific behavior in player-facing language.
- [ ] Prepare a focused PR description with verified testing results and links to the applicable design documents.
- [ ] Commit/push/create PR or publish only when separately requested; this checklist itself is not publication authorization.
- [ ] After merge/release, record the version, PR/commit links, and deferred work; do not mark deferred categories complete.

## 9. Completion evidence and open-work log

Use one entry per deliverable or unresolved decision. Link completed artifacts and keep unchecked work visible.

| Item | Owner | State | Branch / commit | Document / evidence | Next action |
| --- | --- | --- | --- | --- | --- |
| Current proposal, D1 | Unassigned | Documented; decisions remain | Documentation only | D1 §§1–20 | Review Section 5 of this checklist |
| Custom content/effects and Economy shop API | Unassigned | Proposal and scoped draft extensions added; no implementation or runs | Documentation-only addition, October 31 | D1 §20, D2 §9, D3 §10, D6 §10, D4 §15; Section 5 K CONTENT/EFFECT/SHOP gates | Review/approve PB-10–14, concrete schemas/limits and native adapters; settle missing-mod and coherent purchase/save contracts before code |
| Multi-provider content/shop review | Unassigned | MCR-01–06, MCR-10 and MCR-04X design-resolved; MCR-07–09/11/12 OPEN; no implementation/runs | Documentation-only dispositions, October 31 | D3 §§11–14, D6 §§11–14, D7 disposition addenda, D4 §15 bindings; Sections 5 M and N | Design MCR-07 next; when code is authorized, build unit S (Section 5 N) first; finalize and later verify registry headers/resource profile under separate implementation scope |
| Master checklist, D0 | Unassigned | Created | Documentation only | This document | Keep status/evidence current |
| Control inventory/menu map, D2 | Unassigned | Scoped draft created | Reference `ae6520fe6`; implementation target pending | Linked D2 | Review candidate policies and INI-key migration |
| Persistence design, D3 | Unassigned | Scoped draft created | Reference `ae6520fe6`; implementation target pending | Linked D3 | Approve layout/policies; resolve host prerequisites |
| Validation record, D4 | Unassigned | Scoped plan created; no runs | Baseline/target for execution pending | Linked D4; result ledger empty | Bind PB-01–09, select hardware/budgets; execute only after separate authorization |
| Player guide update, D5 | Unassigned | Pending implemented behavior | Not selected | Maintained copy not yet identified | Locate source and update after verification |
| Extension API specification, D6 | Unassigned | Scoped draft created | Reference `ae6520fe6`; no API implemented | Linked D6 | Review composition, bounds, registration lifecycle, and typed surface |
| Pre-implementation review, D7 | Unassigned | Candidate dispositions and D4 plan linked; findings/gates open | Reference checkout `ae6520fe6` | Linked report and D2/D3/D4/D6 | Approve candidate contracts and scoped plan bindings before coding |

No game code was changed to create this checklist. The proposed systems are not marked implemented or tested.
