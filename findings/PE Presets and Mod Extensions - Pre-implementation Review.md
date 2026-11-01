# PE presets and mod extensions: pre-implementation review

Date: October 30, 2026.

Status: documentation/source-contract review only. No gameplay code, settings, saves, balance, or executable changed. No builds or runtime tests were run for this review.

## Assessment and scope

The modular direction is sound: capability APIs can be small, feature owners retain authority, and Economy can adopt shared conventions without requiring every future module to ship at once. However, **the documents are not yet a complete implementation specification**. Several state-transition and capacity policies must be settled before coding the affected feature.

This review covers the [proposal, D1](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Economy presets and independent reward controls proposal.md>) and [master checklist, D0](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets and Menu Organization - Master Checklist.md>). Source checks used the clean local `feat/localization` checkout at commit `ae6520fe6` in `D:/Recomp Games/pe-localization`; it is a reference checkout, not a newly selected implementation target or proof of upstream state. No historical test pass was repeated.

October 31 custom-content addendum: the review below covers D1 §20, D2 §9, D3 §10, D6 §10 and D4 §15 for multi-provider gaps. It is a document-contract review, not a new source/runtime audit. Later requested dispositions resolve **MCR-01–03 (D6 §11), MCR-04/05/10 (D3 §11, D6 §12), the MCR-04X storage expansion (D3 §12, D6 §13) and MCR-06 (D3 §13, D6 §14) at design level; MCR-07–09, 11 and 12 remain OPEN**. The original findings are retained as review history. Neither these dispositions nor existing save-host passes certify custom content/shop implementation.

Findings below distinguish contradictions/omissions in the design from limitations of existing interfaces. They are not a request to change legacy behavior or implement a new save format. Recommendations remain review proposals unless already required by D1. Preserve Enhanced/current defaults and keep tests local in `D:/Recomp Games/pe-native-debug`.

## Findings and required disposition

### REV-01 — Save capacity can contradict the preservation promise

Priority: high; blocks adding new saved records until D3 resolves it.

D1 §§8, 15, 18–19 require preserving inactive/unknown-provider data while adding settings, progress, and possibly coordinator records. The inspected host has **744 container bytes**, including a **20-byte header** and **12 bytes per record**, around its compatibility window. Successful registration budgets registered records; it does not establish that all records carried from a subsequently loaded save will also fit.

The current packer writes live records first and can omit carried records that no longer fit, with a warning. Therefore “the host preserves unknown records” is conditional under capacity pressure. Adding several small records can consume meaningful overhead; a general capability catalog does not imply unlimited save slots.

Evidence: [format and budgets](<D:/Recomp Games/pe-localization/mods/host/pe_save.h:56>), [carried-record capacity handling](<D:/Recomp Games/pe-localization/mods/host/pe_save.c:214>), [save warning](<D:/Recomp Games/pe-localization/mods/host/pe_save.c:399>).

Required: D3 must calculate live plus carried-record worst cases, unknown/newer versions, record overhead, and failure before enabling unsaveable settings. Choose a reviewed preservation/failure policy; do not invent silent truncation or claim existing registration already guarantees it. D4 must test loaded foreign/inactive records near capacity, not just current enabled mods. Any necessary host behavior change needs its own explicit scope.

### REV-02 — Custom is a label, but execution mode is missing

Priority: high; blocks the new reward path and preset application.

D1 §§4, 7–8, 12, 15 distinguish legacy Enhanced from the new configurable reward path, but editing one setting merely says the label becomes Custom. It does not say whether an edit to legacy tuning keeps the legacy engine or migrates all reward behavior into the new engine. Current legacy tuning can already differ from defaults.

Also undefined: Enhanced → Treasure Hunter → Enhanced, repeat application of the same preset, changes to a guarantee below existing progress, switching while a reward is pending, and whether separately stored legacy/new progress can be farmed by alternation. “Keep it separate” does not define how to initialize, freeze, resume, or migrate it.

Required: specify an explicit engine/mode field distinct from the selected preset ID and display label. Add a transition table covering both engines, Custom, each preset, old saves, and repeat application. Record ownership/policy for pity, economy/permit guarantees, fractional income, RNG, charm state, pending rewards, and price context. Preserve the legacy path when untouched; do not infer an engine change from label matching. Resolve transition rules before coding rather than choosing them in a setter.

### REV-03 — Counter off, wallet use, and saturation are underspecified

Priority: high; blocks offering the storage toggle and lossless new-path transactions.

D1 allows inventory storage instead of the counter and independent bonus/redemption switches. It does not define where extra battle income or redeemed bundles go when native Junk uses inventory space, how an existing large wallet remains accessible, or what shops/Wayne see during that transition. Counter storage, wallet availability, and extra income are distinct capabilities; a single `enabled()` result is insufficient to describe all of them.

The inspected wallet saturates at **99,999** and `give()` does not report an accepted amount. Consuming a new-path bundle or granting an adjusted reward near the cap therefore needs an explicit full/partial/reject/defer policy. A numeric clamp alone does not preserve value. Do not silently change existing Enhanced saturation behavior while implementing stricter new-path guarantees.

Evidence: [legacy wallet credit](<D:/Recomp Games/pe-localization/mods/pe_economy/pe_loot.c:124>), [existing service contract](<D:/Recomp Games/pe-localization/mods/host/pe_services.h:30>).

Required: define the supported storage × income × redemption combinations, wallet-cap policy, full-bag/storage behavior, and authoritative transaction return values in D2/D3/D6. If a combination is unsupported, explain and reject it before applying settings. Do not erase/convert the whole balance merely to make a toggle fit.

### REV-04 — Applying a preset versus automatically redeeming existing bundles

Priority: high; blocks enabling automatic redemption through presets.

D1 §8 says applying a preset must not grant Junk. D1 §4's Light preset enables automatic redemption, while §3 describes conversion sweeping existing inventory/storage. Applying the preset could consequently consume already owned bundles and credit Junk at the next sweep. The documents do not distinguish a settings transaction from its later economic consequences or define which conversion policy governs items already present.

Required: the preview must explicitly disclose redemption of existing eligible bundles and their displayed values. Decide whether explicit preset application authorizes that subsequent sweep, or whether existing holdings require a separate confirmation/action. Do not silently choose either policy. Define the safe boundary and interaction with REV-03's wallet cap; the settings setter itself must not perform an unreviewed bulk conversion. Retain bundle identity and one-time consumption.

### REV-05 — Preserving prices needs a real independent owner/value

Priority: high; blocks switching between legacy and new playstyles without incidental price changes.

D1 requires preserving current prices while retaining Relaxed/Normal/Grind, which changes prices and reward tuning together. In the inspected implementation, `pe_loot_price()` reads that legacy preset directly. The proposed new presets cannot simply reuse or overwrite that field while also promising independent price preservation.

Evidence: [legacy price calculation](<D:/Recomp Games/pe-localization/mods/pe_economy/pe_loot.c:161>).

Required: D2/D3 must define the source and persistence of the price policy, whether selecting a legacy difficulty deliberately updates prices, and its behavior when returning from Custom/new presets. Separate base price policy from current equipment effects such as Bargain; “preserve prices” must not freeze a temporary equipped discount into a permanent multiplier. New independent price sliders remain out of scope unless separately selected.

### REV-06 — Reward success, disabled queues, and legacy exceptions conflict

Priority: high; blocks new bonus-item delivery/guarantees.

D1 §7 states universal-sounding rules that pending rewards keep identity and never reroll; the same section also preserves legacy Enhanced queue behavior. The inspected legacy code can replace a carried economy effect that has already become unlocked. The strict rule therefore needs an explicit applicability boundary, rather than silently changing Enhanced.

Evidence: [legacy carried-effect handling](<D:/Recomp Games/pe-localization/mods/pe_economy/pe_loot.c:353>).

The new path also does not define whether a “successful bonus” means generated, queued, shown, collected, or unlocked; when pity resets; how a pending effect that becomes redundant is handled; or whether a disabled queue entry blocks enabled entries. Bounded queues plus indefinite reward generation cannot promise both never dropping rewards and never accumulating an unbounded backlog without a specified backpressure policy.

Required: document reward lifecycle states and guarantee updates, category-specific progress, item/permit/economy selection counters, queue admission before irreversible generation where applicable, full-queue/backpressure behavior, and fair delivery across disabled categories. State that new-path identity guarantees do not retroactively rewrite the untouched legacy algorithm. Resolve empty/no-eligible-pool behavior without secretly redistributing rewards. D4 needs explicit generation/delivery/reset assertions, not just average drop intervals.

### REV-07 — Existing host mechanics are not yet the proposed API contract

Priority: high for exposing first public extension interfaces; not a reason to rewrite every legacy hook.

D1 requires deterministic resolution, lifetime controls, capability negotiation, and provider cleanup. The inspected host orders equal-priority handlers by registration order, uses exact integer service versions, and exposes no unregister function in its public header. All handlers are visited; callback return values aggregate “handled” status rather than forming a transactional veto. Content/event names can be borrowed. These mechanisms are a foundation, not an implementation of the proposed typed contribution contract.

Evidence: [hook insertion/service lookup](<D:/Recomp Games/pe-localization/mods/host/pe_mod_host.c:120>), [dispatch](<D:/Recomp Games/pe-localization/mods/host/pe_mod_host.c:372>), [public API/lifecycle](<D:/Recomp Games/pe-localization/mods/host/pe_mod_host.h:25>).

Required: D6 should choose a small owner-managed typed registration/resolution layer or a specifically scoped host extension. Preserve legacy hook ordering unless explicitly changed. Define stable tie-breaks, copied/borrowed metadata, activation rechecks for cached services, init/discovery readiness, error semantics, and restart-only provider lifecycle for the initial slice if needed. Current mods are compiled through the host's mod list; distinguish source-level API compatibility from any future binary/plugin ABI guarantee. Do not assume dynamic loading, worker submission, or hot unload exists.

### REV-08 — Normal-save coherence does not cover crash capture

Priority: high for any new multi-step persistent transaction.

D1 §16 proposes coherent normal save capture at a safe boundary. The inspected crash-save contract copies live record memory without allocation, locks, or mod callbacks. A crash can interrupt a transaction before that normal boundary; lock-free copying is not automatically a coherent multi-owner snapshot. A saved charge without its item or reward progress is a recovery risk even if ordinary saves are correctly serialized.

Evidence: [crash contract](<D:/Recomp Games/pe-localization/mods/host/pe_save.h:89>).

Required: D3/D6 must distinguish ordinary save, crash capture, recovery, and interrupted file writes. Decide how new transactions expose committed state to crash reporting, for example a bounded last-committed snapshot or another reviewed mechanism; do not assume signal/crash paths can wait for a worker or acquire locks. Record cross-owner and file-write guarantees actually supported by the engine. D4 must inject interruption at transaction phases and verify that recovery cannot manufacture or lose one side of a supported operation.

### REV-09 — New reward RNG and missing/corrupt-record defaults need contracts

Priority: high for the new saved reward path; future Randomizer requirements remain separately deferred.

D1 §19 thoroughly discusses Randomizer RNG, but the initial new item/bundle path also needs deterministic draw/stream ownership, persistence, and toggle behavior. The current legacy RNG seeds from frame count when unset and is cleared by the record's load check. Changing that behavior to match a new deterministic policy would violate untouched legacy parity.

Evidence: [legacy RNG](<D:/Recomp Games/pe-localization/mods/pe_economy/pe_loot.c:200>), [load check](<D:/Recomp Games/pe-localization/mods/pe_economy/pe_loot.c:556>).

Also distinguish an old save legitimately lacking settings from a corrupt/newer record that the host preserves while initializing defaults. Starting a new-mode save under legacy defaults when its settings are unreadable is not necessarily safe. New Game/vanilla-save difficulty inheritance must be explicit; the legacy reset intentionally retains the current difficulty value.

Required: D3/D6 define new-path RNG state/streams and eligibility draws without changing legacy RNG, plus state provenance/status for absent/valid/invalid/unsupported records. Specify safe fallback or feature refusal when dependent settings/progress cannot be interpreted, preserve unknown bytes, and prevent accidental save-to-save inheritance. Include charm/temporary modifiers and guarantee-off versus zero-percent behavior. Repeated load/RNG replay policy is a design decision, not an implicit no-exploit guarantee.

### REV-10 — Preview must not execute the transaction

Priority: medium; required before exposing previews/diagnostics.

D1 requires stable base settings, optional diagnostics, and no effects while highlighting presets. An extension callback reused for preview could still draw RNG, update a guarantee, query changing state, or reserve/spend a resource unless its contract prohibits that. A previewed price may also become stale before a purchase.

Required: separate pure preview/description from authoritative operation evaluation. Identify estimates versus guaranteed values; capture the relevant generation and revalidate before action. Preview and diagnostic calls must not change RNG/progress or replay notifications. Record actual final values in the completed transaction's diagnostic result without retaining unbounded snapshots. Add tests that repeatedly open/hover/inspect without affecting the next real operation.

### REV-11 — Implementation gates must be scoped to a delivery slice

Priority: medium; required for a manageable implementation plan.

D0 at the original review interleaved required Economy work and future category/coordinator work; D2/D3/D4/D6 had not yet been created. D2/D3/D6 scoped drafts and D4's validation plan now exist (follow-ups below), without approved policies or executed results. Without a scoped readiness gate, the broad checklist can be interpreted either as permission to improvise missing contracts or as a demand to finish the entire future framework before the first feature.

Required: record the selected slice and distinguish prerequisites, release checks, and future work. Recommend: (A) target-branch inventory and scoped contracts, (B) Economy setting/reward separation with compatible persistence, (C) small typed Economy contribution API plus two local providers, (D) menu changes, (E) later module adoption/coordinators. This is a recommended sequence only; resolve which work is actually authorized before implementation. Do not build workers, hot unload, custom item registries, or a universal orchestrator solely because future sections mention them.

D4 must exist as a plan before behavioral implementation, with results added afterward. Performance hardware/budgets and leak cycle/soak criteria are deliberately open today; they must be agreed before claiming release acceptance. Full future module specs are not prerequisites for a scoped Economy implementation.

### REV-12 — Category independence versus coordinator authority needs matching wording

Priority: medium; required before future coordinator work, not an Economy blocker.

D1 §§13 and 19 explicitly permit opted-in coordinated packages. D0 §2's unconditional category independence/native-drop preservation could be read to prohibit the very overhaul operations D1 §19 allows. Both can coexist if normal preset guarantees and explicit run-package scope are distinguished consistently.

Required: state that ordinary category presets and ordinary modifiers preserve independence/native drops. A separately opted-in coordinator can request reviewed changes across declared categories/native tables through their owners, without bypassing disabled features or unreviewed migrations. The player's opt-in may define run restrictions; it does not grant arbitrary direct state access. D0 and D1 should point to the same exception and retain these checks for future rollout.

## Readiness gates and modular deliverables

| Gate | Required before the affected coding | Where to resolve | Current state |
| --- | --- | --- | --- |
| G0 — Scope/baseline | Select actual target branch/commit, scoped slice, unchanged-default baseline | D2/D4; REV-11 | Open |
| G1 — Economy state | Engine/preset transitions, wallet/storage/cap, redemption consequences, pricing, reward lifecycle/queue, new RNG/defaults | D2/D3/D6; REV-02–06, 09 | Open |
| G2 — Safe persistence | Byte/record capacity including carried data, registration failure, committed state/crash capture | D3/D4; REV-01, 08 | Open |
| G3 — Public extensions | Typed contribution scope, version/discovery/lifetime, deterministic order, pure previews | D6/D4; REV-07, 10 | Open |
| G4 — Release acceptance | Matched build/compatibility tests, target performance budgets, leak criteria and evidence | D4/D5; REV-11 and D1 §§11, 16–18 | Open; criteria before implementation, results before release |
| G5 — Future coordination | Explicit package authority, staged activation, deterministic plan/persistence | D3/D6; REV-12 and D1 §19 | Deferred until a coordinator is separately requested |

Documentation work and read-only baseline audits can proceed now. Resolve the applicable gates before coding that slice. This review does not require implementing every deferred API before Economy work.

## What is already consistent

- Framework-wide participation versus optional small public APIs is coherent.
- Economy-first rollout versus later Combat/Inventory/collection/Randomizer adoption is coherent when scoped per gate.
- Single transaction ownership, immutable completed notifications, race protections, bounded memory, and cleanup responsibilities reinforce each other.
- Low-powered-machine requirements do not require gameplay-changing fallback or parallelizing simple arithmetic.
- Preserving current interfaces while versioning new capabilities is compatible with incremental rollout.
- Workshop visibility, Wardrobe buying, unlock/reset automation, and additional unapproved balancing remain outside the initial scope.

## Review disposition

### Scoped follow-up — October 30, 2026

Created [D2](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Control Inventory and Menu Map.md>), [D3](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Persistence and Migration Design.md>), and [D6](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Mod Extensions - API and Cooperation Contract.md>) as candidate specifications. They address the findings without claiming implementation or gate closure:

| Findings | Candidate disposition |
| --- | --- |
| REV-01/08 | D3 budgets existing/new records and requires actual host admission/status/conditional emission/save refusal and coherent whole-save crash capture; prerequisites remain unimplemented |
| REV-02–05 | D2 specifies candidate engine transitions, supported storage combinations, all-or-nothing/deferred credit, preview-authorized existing-bundle conversion, and explicit return-to-Enhanced pricing |
| REV-06/09 | D3 specifies candidate generation-success/reset, family backpressure, frozen state, load provenance, and isolated saved RNG/remainder |
| REV-07/10 | D6 specifies a small owner-managed capability, init-only typed registration, deterministic numeric contributions, observers, provider presets, and observational previews |
| REV-11/12 | D2 scopes A–D; D6 defers coordinators while retaining their design space. D4's scoped plan now exists; policy/budget approvals and execution remain open |

Additional source-confirmed constraint: `pe_mod_menu.c` derives global settings keys from page/label, so persisted-row moves need stable identity/alias migration, described in D2 §6. The baseline existing records total 524 of 744 bytes; D3's candidate 160-byte record plus header would leave only 48 bytes for other records. These are source arithmetic/inspection, not runtime passes. Original gate states remain open until the corresponding contracts are accepted and verified.

### Validation-plan follow-up — October 30, 2026

Created [D4, scoped validation and playtest plan](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Validation and Playtest Record.md>) with test-case families, PB-01–09 policy bindings, expected results, REV-01–12 traceability, save/recovery and compatibility matrices, race schedules, performance/memory measurement protocols, proposed cycle/soak workloads, playtest metrics, and an empty result ledger. Hardware/numeric budgets and unresolved design policies still require binding; no test suite/code was written or executed. The missing-plan deliverable is complete, but review gates and runtime acceptance remain open. All raw tests/fixtures/evidence are designated local-only in `pe-native-debug`, whose no-remote status was checked during planning.

### Implementation follow-up — October 31, 2026

On `feat/mod-presets-framework` from upstream `8c52cdde5`, read-only queries and normal capacity refusal now address part of REV-01/07. The writer no longer publishes valid carried-record omissions on overflow: admission runs before hooks and before staged tail publication, and the native save flow aborts before destination writing. Crash-tail snapshots also refuse overflow. D4 records local refusal/query/host/native-gate evidence, supported-save byte parity and 6 existing CTests after rebuilding. This is not complete G2/REV-08 closure: lazy policy emission, unreadable new-policy gating and coherent full native-plus-mod crash capture remain separate, unimplemented work. The original source audit above describes the reference baseline, not an assertion that the new branch still allows normal capacity truncation. All source changes remain uncommitted; new tests/raw evidence remain local.

No balance values or open engineering policies were silently finalized. No confirmed source limitation was fixed in code. D0 tracks REV-01–12 as unresolved design work; D1 links this review so future implementers see the caveats before treating examples as executable contracts. Link checks verify document/source paths only; they do not establish runtime correctness or current upstream parity.

### Conditional-emission follow-up — October 31, 2026

The same branch now implements the modular host prerequisite: dormant registration plus explicit
checked activation, with no `PeSaveRecord` ABI or on-disk format change. Inactive/absent-provider
carried state and valid-CRC rejected/newer optional payloads remain preserved. Source uncertainty,
uninitialized state, lifecycle reentrancy and capacity overflow refuse activation. D4 records
25 new local cases, reruns of 33 prior local cases, 3 existing fixture modes, 100 byte-identical
supported card images, rebuild and 6 existing CTests. All new fixtures/raw evidence stay local.
This advances REV-01/08 prerequisites but does not close G2: actual policy validation/registration,
preset transitions, whole-save coherent crash capture, and broader playtest/performance/leak
acceptance remain open. No balances or provisional policy values were implemented.

## Custom content and shop API review — October 31, 2026

### Assessment, scope and evidence

The separation into shared definitions, inventory/equipment instances, effect runtime, Catalog presentation and Economy offers is appropriate. It allows multiple mods to submit multiple kinds of content without making each mod own a shop, serializer or transaction engine. The documents already require stable namespaced IDs, inactive/unknown-data preservation, separate API/schema versions, explicit quote/commit, bounded resources and independent Economy integration. Retain those requirements.

**E/F/G are not yet implementation-ready.** Remaining issues include actual contradictions, unresolved decisions already acknowledged in the drafts, and additional multi-provider omissions. The references below identify the affected document section/table rather than treating proposed APIs as existing code. No game files, saves, balances or settings changed; no tests/builds were run. All recommendations below remain proposals until accepted and reflected consistently in D2/D3/D6 and D4 bindings. Original REV-01–12 and G0–G5 retain their own scope/status.

Reviewed: D1 §20; D2 §9 (slices, control table, missing-content and audit responsibilities); D3 §10 (logical entities, capacity, load matrix, transactions); D6 §10 (capabilities, descriptors, lifecycle, operations and results); D4 §15 (36 planned cases), with earlier shared API conventions where referenced.

### MCR-01 — Duplicate and capacity rejection can still select the first mod loaded

Priority: **high**, blocks registry sealing/public v1. Type: conflict plus missing policy. References: D6 §10 descriptor/lifecycle rules; D4 CNT-04/SHP-01.

D6 says duplicate IDs are rejected and load order cannot determine ownership. A sequential register-first/reject-second implementation violates that: reversing two registrations changes which definition/offer survives. The same issue occurs when A fills a registry before B registers, even with no duplicate IDs. One mod submitting many definitions/large descriptions can exhaust a shared count/byte budget. Reversed order alone is not a complete acceptance oracle until the admission policy is specified.

Recommendation: distinguish provisional registration acceptance from sealed readiness. Stage bounded owner-scoped registrations, resolve conflicts under a canonical policy, and publish only a coherent validated set. Define collision disposition explicitly (for example, invalidate every conflicting entry/required batch instead of keeping the first). Choose per-owner and global count/byte budgets and overflow treatment before coding; account for staging memory as well as published metadata. Define atomic required batches versus explicitly optional entries, failure unwind and diagnostics. Do not retroactively evict published content. If a simpler deterministic startup-refusal policy is selected, document that limit rather than promising arbitrary partial acceptance.

Acceptance needed: same active set or same attributed refusal across permutations, many entries from one owner versus many small owners, duplicate within one batch, duplicate across batches, global/per-owner count and text-byte exhaustion, and failure halfway through a required content/effect/offer bundle. D2/D6 and PB-10/14 must bind the chosen policy.

### MCR-02 — Ownership does not yet define permission to reference or extend another mod's content

Priority: **high**, blocks third-party shop/effect attachments. Type: missing cross-owner contract. References: D6 §10 IDs, descriptors and offer rules; D3 §10 provider extensions.

Host-derived namespace ownership prevents B from registering A's ID, but does not answer whether B may sell A's weapon, attach an extension payload/effect, place it in another shop, share A's stock or replace A's availability rule. Conversely, requiring the registrant to own every referenced ID would prevent intended integrations. One equipment instance can contain effects/payloads from several owners; a single undifferentiated provider blob cannot safely allocate mutation authority among them.

Recommendation: separate definition ownership, supported cross-provider references, target-shop admission, extension attachment ownership and stock authority. Choose an explicit default for ordinary public references and optional opt-in restrictions; replacement/migration/mutation must require a specific capability/adapter. Each opaque extension has a stable owner/schema key and cannot overwrite another owner's bytes. Mutations go through inventory/equipment actions, not a provider's raw view. These are cooperative native API rules, not protection against arbitrary malicious memory writes.

Acceptance needed: B contributes an allowed offer for A's item, an unauthorized definition/stock replacement is refused, A is absent/incompatible, two providers attach independent data to one native weapon, and one attachment owner disappears without erasing another's data. D3/D6 and PB-10/13 must specify authority.

### MCR-03 — Service initialization, reference resolution and readiness dependencies are conflated

Priority: **high**, blocks lifecycle design. Type: unresolved prerequisite. References: D6 §3 and §10 dependency flow; D2 E/F/G entry gates.

The drafts acknowledge that sealing/readiness may not exist in the host. They do not yet distinguish a required service initialization edge from an item-definition reference or optional shop integration. Two packs referencing each other's content can form a harmless data-reference cycle, while a required initialization cycle is not executable. Treating every cycle as the same error can reject valid packs or introduce order-dependent partial readiness. A content mod that declares Economy required just to register optional offers also undermines Economy independence.

Recommendation: specify separate capability initialization, staged reference resolution, runtime readiness and optional adapter edges. Resolve stable references after a bounded registration phase where supported; define which graph cycles are illegal and propagate required failure without disabling unrelated ready entries accidentally. If no sealing phase is added, define the smaller acyclic registration model and explicitly refuse unsupported forward references. Optional Catalog/shop adapters should not become required dependencies of independent definitions. Failed init must retract provisional registrations and release retained callbacks safely.

Acceptance needed: forward reference, optional missing Economy, required missing runtime, legal reference cycle if supported, illegal service cycle, transitive required failure and partial-init unwind. D2/D6 and PB-14 must bind the actual host prerequisite; no claim it already exists.

### MCR-04 — A concrete multi-provider storage envelope is still missing

Priority: **high**, blocks persistent custom acquisitions. Type: known unresolved blocker. References: D3 §10 capacity/entities; D4 CNT-11; D1 §20 byte budget.

The documents correctly retain 744 usable bytes and acknowledge a 524-byte baseline / 696-byte candidate-policy total. They have not selected an instance/attachment/stock encoding or a supported number of each. One 47-byte identity plus framing can already be material relative to the candidate's 48 remaining bytes. Definition registration can succeed while the first item, discovery or one-time stock state is unsaveable. A fixed maximum record reserves its whole declared size when emitted; conditional activation does not encode variable growth or solve concurrent logical capacity promises.

Recommendation: choose a measured minimum viable persistent-content envelope and worst-case byte layout before E can grant content. Include all provider identities, opaque attachments, unknown retained state, discovery/claims, instance references and transaction metadata, not just item count. Define one shared admission authority across prepared operations and capacity refusal for reinstalls/new limits. If the envelope cannot fit, stop for the separately reviewed expandable-storage proposal. Do not satisfy counts by truncating unknown records or allocating a record per registration.

Acceptance needed: several providers near capacity, missing-owner retained bytes, enabling policy plus content in either order, registry success but acquisition refusal, multiple staged requests competing for the same capacity and a newer build with lower supported limits. D3/PB-11 is a prerequisite, not a documentation-complete checkmark.

### MCR-05 — The logical instance model still lacks a native representation authority

Priority: **high**, blocks native item/equipment integration. Type: missing engine adapter design. References: D2 §9 native audit; D3 §10 instances/locations; D6 `inventory_actions`.

Stable logical IDs do not say how a custom item is represented in the native bag, trunk, equipped slots, battle structures or save image. Mapping by slot or native object address alone breaks under sorting, compaction, swaps, stacking, copying and save switching. Multiple mods can otherwise maintain incompatible side mappings or duplicate an instance when a native path creates/deletes a slot outside the adapter. A custom effect on a native gun has the same identity issue even if no new gun is added.

Recommendation: one inventory/equipment owner must define bidirectional mapping, identity creation/moves/splits/merges/destruction, unresolved placeholders and native serialization integration. Native paths that bypass it must be adapted, refused for custom content or explicitly outside supported scope. Define stack equivalence using full mutable/effect/provenance compatibility and collision-safe instance allocation, not merely the definition ID. Record actual current-branch path audit before choosing implementation, including combine/sell/rebuild and save-editor edits. No unreviewed spare native ID or raw-pointer identity.

Acceptance needed: sort and slot compaction with effects, bag↔trunk↔equip transitions, identical definitions with different attachments, stack split/merge refusal, legitimate deletion and copied/imported saves. D2/D3/D6 and PB-10/11 must bind the representation before code is written against it.

### MCR-06 — Custom discovery and unlock progress has no saved owner/schema yet

Priority: **high for Catalog integration**, blocks persistent custom unlocks. Type: missing persistent entity. References: D2/D6 Catalog/discovery requirements; D3 §10 saved-entity table; D4 EFX-06.

The UI promises `????`, hidden details, retained discovery and missing-provider handling, but the new saved-entity list covers instances, effects, stock and operations without defining stable custom discovery/ownership state. Existing Catalog state cannot be assumed expandable or indexed by the new registry order. Effect discovery, a purchased unlock, possession of a consumable and an installed attachment are distinct states; knowing one must not silently grant the others.

Recommendation: assign the authoritative discovery/entitlement owner, stable IDs, version/byte budget and transition rules. Retain unknown discovery/claims with missing providers. Define which supported action legitimately reveals/unlocks each entry and what multiple offers/reference aliases share. Keep first-slice legacy Catalog records unchanged unless a separately reviewed migration is chosen. Diagnostics and provider metadata must not become a discovery bypass.

Acceptance needed: discover without install, remove without losing entitlement, two offers for one unlock, provider absent/reinstalled, registry reorder/ID migration and undiscovered quote/help/error paths. D2/D3/D6 plus PB-11/12 must agree before adding custom Catalog persistence.

### MCR-07 — Shared stock needs units, update/migration and authority rules

Priority: **high for finite stock**, blocks shared/one-time offers. Type: missing semantics. References: D6 offer descriptor/shared-stock note; D3 stock and scope; D4 SHP-11.

A stable stock key and per-save scope do not define whether stock counts purchases, delivered items, bundles or installations. For example, A selling one item and B selling three under the same stock key can consume inconsistent amounts. Price/pack updates, removing/reintroducing offers, switching finite↔infinite and renaming an offer can reset claims unintentionally. Distinct offers do not necessarily imply independent entitlement: two installation offers may unlock the same effect twice.

Recommendation: define a stock-pool owner, unit, checked consumption, initial state, restock policy (initially none unless explicitly supported), revision/migration and independently identified one-time entitlement. All pool consumers must agree on scope/schema/units or fail readiness. Preserve retained claims when offers disappear; registry initialization cannot replenish them. Decide how new content revisions introduce intentionally new stock versus rename old offers without farming resets.

Acceptance needed: different bundle quantities consuming one pool, A/B prices for the same stock, partial quantities, finite/infinite revisions, alias migration, provider removal and already-owned service target. D3/D6 and PB-13 need a concrete stock contract.

### MCR-08 — Quote identity and the final non-failing commit boundary are ambiguous

Priority: **high**, blocks purchases and services. Type: internal ambiguity. References: D6 quote/prepare/request table and action-safety paragraph; D3 `QUOTE → PREPARED → COMMITTED`.

Preparation is said to guarantee commit while final commit also rechecks potentially stale dependencies. Both can be satisfied only if all fallible checks are defined to happen before the irreversible boundary and the prepared resources cannot be invalidated during publication. The documents do not yet assign transaction ownership/reservation ordering or say whether returned quotes are authoritative owned records or caller-editable data. Quotes can require bounded transient registry bookkeeping even though their gameplay inspection is read-only; those concepts must be distinguished.

Recommendation: define one coordinator, owner tokens, cancellation/expiry and deterministic resource acquisition order. Perform final generation/price/target/capacity checks before entering a guarded non-failing publication section; after that point no provider callback, allocation or validation may introduce ordinary failure. If actual native owners cannot support this, leave the action unavailable. A quote must be re-resolved/validated by authority, never trust a caller-supplied price or target. Explicitly permit bounded ephemeral quote bookkeeping without gameplay/persistence/RNG effects; arbitrary scripts remain outside this contract. Coherent save/crash/file requirements remain separate required gates.

Acceptance needed: two providers purchasing/installing into the same instance/slot, cancellation halfway through prepare, each fallible check, expired/altered quote, save capture and notification exceptions. D3/D6/PB-13 must define where refusal remains possible and where only a committed result is valid.

### MCR-09 — Duplicate request/result semantics and ID retention are underspecified

Priority: **high**, blocks repeated-request safety. Type: missing operational contract. References: D6 result conventions/operation identity; D3 committed metadata and playthrough scope; D4 SHP-08.

Operation identity has no allocation authority, payload binding, wrap/eviction policy or result-retrieval rule. Two mods can accidentally choose the same token. Repeating a token with a different target/quantity must not be mistaken for a harmless retry. A post-commit observer/log failure cannot return an ordinary purchase failure that encourages another payment. Persisted committed metadata is proposed, but session/playthrough reset behavior and what a post-load retry can mean are not settled.

Recommendation: coordinator-issued owner/playthrough-scoped tokens bound to a canonical operation and target; repeated identical request returns the same terminal outcome within an explicit retained window, changed payload is rejected. Specify bounded in-flight/completed tables and backpressure before admission, counter overflow and save/load/New Game invalidation. Separate committed success plus diagnostic/observer failure from aborted operation. Choose persisted recovery/dedup metadata only under the actual save boundary; do not imply cross-crash exactly-once or anti-rollback protection.

Acceptance needed: same token same payload, same token different payload/owner, full/expired dedup table, token wrap, notification failure after success and save-switch/post-load token reuse. D3/D6/PB-13/14 must bind the behavior.

### MCR-10 — Missing-mod safety depends on a reader that cannot disappear with the mod

Priority: **high**, blocks compatibility claims. Type: missing deployment boundary. References: D2/D3 missing-content/fallback policy; D6 capability availability; D4 CNT-05–09/RES-01/02.

Preservation and safe placeholders require a reader/native adapter even when the content provider is disabled. The documents do not yet identify which essential shared component remains available if Economy, the content framework, or all mods are off. An old build/save editor cannot enforce new safe equipment mapping merely because unknown mod records are retained. A native fallback written without its logical association can make a later enabled reader duplicate or misidentify equipment. Lower limits in a future build create a similar unsupported-reader problem.

Recommendation: name the minimum compatible reader/runtime adapter and supported off/all-off behavior. If core support is absent, refuse loading custom-state saves through a compatible outer load gate; where that cannot be enforced, state that older/core-less builds are unsupported and protect originals through documented backups rather than promising safety. Define the native-plus-logical saved representation in active, unavailable and fallback states together. Support module/provider absence separately from absence of the whole framework. Unknown well-framed bytes can be retained, but arbitrary old builds and structurally corrupt data cannot be guaranteed safe.

Acceptance needed: content provider off, Economy off, shared core off, all mods off, older reader, native save edited without provider, fallback save/reload and valid data exceeding configured limits. D2/D3/D6/PB-11 must limit the compatibility promise accurately.

### MCR-11 — Composed numeric/effect limits and computed-state ownership need binding

Priority: **high for effect behavior and pricing**, blocks affected operations. Type: unresolved rules, not a request for balance changes. References: D6 equipment/effect descriptors and offer pricing; D3 mutable fields; D4 EFX-02/SHP-04/06.

Several individually valid providers can jointly exceed stat/ammunition/slot/price bounds or claim incompatible effect contexts. The first battle-Junk API's arithmetic does not define combat-effect stacking or shop prices. Slot ordering, built-in versus installed effects, rounding, source-specific factors, negative/zero prices, quantity multiplication, caps, and derived-versus-base stats need their own owner rules. Saving already adjusted stats then recomputing effects on load risks compounding.

Recommendation: bind each supported effect/pricing context's algebra, checked integer intermediates, ranges, canonical composition and overflow/conflict refusal. Define base persisted upgrades versus ephemeral computed effective values and dependency invalidation. Keep player discovery and existing pricing/refund semantics. Initially restrict new effects/price policies to supported combinations instead of assuming arbitrary callbacks commute. Do not select numeric buffs or discounts during this review.

Acceptance needed: three or more providers affecting one context, boundary quantity×price, free offers, aggregate overflow/conflict, equip/load/recompute parity, non-stacking entitlements and conflicting exclusive runtime behaviors. D3/D6/PB-12/13 must bind technical arithmetic without silently changing balances.

### MCR-12 — Two-provider reversal is not enough validation for many submissions

Priority: **medium for design; required before multi-provider release**. Type: test coverage gap. References: D4 §15 manifest/cases; D6 local examples/bounds.

The 36 planned cases are a useful start, but mostly describe A/B and qualitative limits. They do not explicitly cover one pack submitting many mixed entries, required registration batches, many small packs, three-way conflicts/shared targets, selective transitive failure, partial manifests, role-specific ownership, stock revisions, core absence or token collisions above. A nominal maximum contributor count also misses total copied-string/payload/quote memory and worst-case filtering/lookup costs.

Recommendation: extend D4 after the accepted policies with a bounded scale matrix: zero, one-many, many-one, mixed packs, three-way interactions and accepted maximum count/byte limits. Include deterministic permutations/property checks against independent canonical expected state; run exhaustive permutations only where small and sampled fixed-seed permutations at larger scale. Separate init/registry/memory costs from per-frame, menu, quote and native commit costs. Measure diagnostics off/on and failed-batch cleanup. Keep all helpers/providers/raw evidence local in `pe-native-debug`; proposed test text is not a pass.

### Readiness, document follow-ups and delivery order

| Gate / proposed slice | Open findings that must be bound for that slice | Required artifact |
| --- | --- | --- |
| Definition-only registry prototype, no grants/persistence | MCR-01–03 plus relevant MCR-12 bounds | D6 exact identity, staged registration/seal/batch/dependency model and D4 startup cases |
| E — usable/persistent content instances | MCR-04/05/10, relevant MCR-02/09/11, plus registry prerequisites | Current-branch native-path audit, D3 accepted representation/storage/reader matrix, D6 inventory actions |
| F — custom equipment effects/Catalog | MCR-02/05/06/10/11 plus instance gates | Effect evaluation/attachment/discovery schemas and Catalog adapter; no compulsory shop dependency |
| G — contributed sales/services | MCR-07–11 plus identity/capacity/lifecycle gates for supported delivery | Stock/price, quote/token, reservation/commit/save contracts; installation services gated separately from item delivery |
| Multi-provider release for an accepted slice | MCR-12 and applicable above findings | Bound D4 cases, actual native evidence, measured limits/resources, recovery and compatibility documentation |

These are scoped disposition gates under the existing G0–G4 framework, not new automatic approval steps for unrelated already-authorized work. A documentation-complete draft does not close them. G5 coordinators remain deferred. Suggested next document unit: bind deterministic registry/batch/dependency/ownership behavior (MCR-01–03), then choose the minimum viable storage/native mapping (MCR-04/05/10), then effect discovery and shop transaction details. The current save-host query/admission/emission work can remain independent; do not retroactively claim it implements these capabilities.

**Original review result: modular approach retained; 12 findings initially OPEN.** The requested dispositions below subsequently resolve MCR-01–06, MCR-10 and MCR-04X at design level; MCR-07–09, 11 and 12 remain open. No code, balances, saved data, API implementations, test suite or executables changed. D0 tracks the open work; update contracts/bindings only with explicit dispositions and keep unresolved alternatives visible.

### Requested MCR-01–03 disposition — October 31, 2026

Following the user's instruction to resolve registration/ownership/dependency rules, D6 §11 now specifies the recommended contract. This supersedes the original OPEN status for these three **design findings only**; the original diagnosis remains above for traceability. MCR-04–12 remain open and E/F/G are not yet implementation-ready.

| Finding | Design disposition | Verification binding / remaining boundary |
| --- | --- | --- |
| MCR-01 | D6 §§11.1–11.3: owner-scoped complete manifests, atomic required/optional batches, provisional receipts, invalidation of all authenticated duplicate claimants, canonical seal, per-owner/domain count/byte limits and deterministic domain-level global-overflow refusal; no first-wins subset or late replacement | D4 CNT-04/SHP-01/RES-03/04 plus §15 disposition bindings. Public C/profile accounting and low-powered measurements unimplemented; actual instance/save capacity remains MCR-04 |
| MCR-02 | D6 §11.4: public typed references; immutable owner authority; opt-in external sales/effects/extension points and shop/stock admission; independently owned attachments; foreign namespace impersonation rejected without invalidating its authorized target | D4 CNT-04/EFX-01/03/SHP-01/02/RES-01 coverage bindings. Persisted encoding, native instance authority and stock units remain MCR-04/05/07 |
| MCR-03 | D6 §11.5: small shared bootstrap/collect/seal/publish/run facility; distinct service-init, passive-reference, hard-evaluation, batch and optional-adapter edges. Permit validated passive reference cycles, reject required initialization/readiness/batch cycles; propagate failures and preserve unrelated optional batches | D4 CNT-04/12/SHP-02/RES-03 bindings. Actual host seal/readiness phase is a separately authorized implementation prerequisite; no change to legacy host ordering or hot unload |

Initial registry profile limits are technical starting requirements, not gameplay balance or performance results. They bound registry metadata only; installed assets, instances, transactions, stock and saves need their own accepted limits. D0 marks these design dispositions complete and keeps their implementation/validation unchecked. D2/D3 notices link the controlling D6 rules; D4 binds acceptance scenarios without adding tests or claiming a pass.

Next recommended document unit: MCR-04/05/10 (actual storage envelope, native mapping and minimum compatible reader). No source code, user saves, test suite, executable, defaults or balance changed for this disposition; no runtime tests/builds were run.

### Requested MCR-04/05/10 disposition — October 31, 2026

Following the user's instruction to resolve save capacity, native inventory mapping and missing-mod compatibility, D3 §11 and D6 §12 specify the recommended contract. This supersedes the original OPEN status for these three **design findings only**. The design's main outcome is a stop: the smallest useful ledger does not fit beside the candidate policy record in the existing 744-byte container, so persistent custom instances (slice E) wait on a separately reviewed storage-expansion proposal, tracked as **MCR-04X**.

| Finding | Design disposition | Verification binding / remaining boundary |
| --- | --- | --- |
| MCR-04 | D3 §§11.1–11.4: native-complete equipment records plus one shared `pe_content.ledger` v1 owned by the content core; fixed-width encoding (16-byte section header, ≤ 51-byte dictionary entries, 12-byte instance entries, ≤ 37-byte attachment frames); declared-maximum accounting over the whole container; single reservation-based admission authority; newer builds with lower limits keep everything and refuse growth. Profiles P0 = 178 bytes, P1 (supported minimum) = 1,360 bytes vs 48 free beside the policy record | D4 CNT-01/10/11/12 and RES-02 bindings. Blocked on MCR-04X (≥ 4 KiB starting estimate, ≤ 2 KiB for this ledger, one coherent generation, detection, editor support). MCR-06/07/09 must declare their own sub-budgets there. Not permitted meanwhile: hidden P0 limit, truncation/compression, sidecar files |
| MCR-05 | D6 §§12.1–12.5: one mapping authority (the content core); anchor = (pool index, fingerprint), never slot index or pointer; equipment kinds 1–9 only in v1; no stack equivalence or merge; lifecycle for create/move/sort/equip/battle/save/destroy; current-branch native path audit with file:line; pre-free and merge veto hooks required at every record-freeing site. `reserved02` shown not free (holds the item number in all 255 base records) | D4 CNT-02/03/05/07, EFX-04/05/08 bindings. Audit items open: fingerprint field immutability, carry-over reset meaning, complete retail list of freeing sites. Hooks unimplemented; Dismantle/Rebuild/tune-up of custom records refused until adapted |
| MCR-10 | D6 §12.6: the content core is host-level, in every `PE_MODS` build, outside Manage mods, running with All mods off; carries a reader revision checked against the ledger's `min_reader`. D3 §11.5: per-state matrix (ACTIVE / UNAVAILABLE / UNCERTAIN / ORPHANED) for provider off, Economy off, All mods off, vanilla, older build, save editor, over-profile, newer format and structurally invalid; outer load gate for unreadable ledgers; reconciliation by `native_stamp` that only demotes identity | D4 CNT-05/06/07/10, RES-01/02 bindings. Requires approval of the All-mods-off exception and the outer load gate. Vanilla and core-less builds are one-way losses of the ledger (native items stay playable), documented rather than prevented |

Gate status after this disposition: slice E (usable/persistent content instances) has its design dispositions for MCR-04/05/10 but stays blocked by MCR-04X, the §12.4 audit items and relevant MCR-02/09/11. Slice F additionally needs MCR-06/11; slice G needs MCR-07–09/11. Definition-only registries and non-persistent native-alias presentation remain possible without MCR-04X.

Next recommended document unit: either the MCR-04X storage-expansion proposal (it unblocks E and must host the MCR-06/07/09 sub-budgets) or MCR-06 discovery. No source code, user saves, test suite, executable, defaults or balance changed for this disposition; no runtime tests/builds were run.

### MCR-04X storage expansion and approvals — October 31, 2026

The user delegated the open approvals ("do what you think is best, stable, modular and scalable"). Adopted as written: the native-complete rule, the 32-byte attachment ceiling, P1 as the supported minimum, the All-mods-off preservation exception and the outer load gate (D3 §11.6).

MCR-04X is specified in D3 §12 and D6 §13: each save gets a linked companion file in a hidden `.pe-ext` folder beside its card file. The evidence that decided it: every card file costs a save slot, and card listing skips folders and dot-names on all platforms. Native saves already publish by temp file and rename, so the companion is published first and the card rename is the single commit point. A 32-byte link record in the tail names the generation, size and CRC. Per-owner sections with independent CRCs sit inside a 4 KiB v1 profile: ledger 2,048, discovery 512, stock 512, operations 256, plus unassigned and overhead. The 744-byte tail closes to new records after the policy record and the link. A missing companion for a save with custom items triggers the outer load gate's explicit *Continue without mod data / Back* prompt.

| Item | Disposition | Remaining boundary |
| --- | --- | --- |
| MCR-04X | Resolved as recommended design: D3 §12 format, write order, load and missing-file rules; D6 §13 section service | D4 "MCR-04X acceptance bindings". Host prerequisites are unimplemented: card path access, directory operations, extension write step before the card rename. Editor bundle export and crash-report dump are follow-up |

Slice E now has design dispositions for everything it depends on (MCR-01–05, 10, 04X), apart from the D6 §12.4 audit items and the relevant MCR-02/09/11 parts. It still needs implementation and validation under separate authorization. Next recommended document unit: MCR-06 (discovery/entitlement), which now has a section budget to design against.

### Requested MCR-06 disposition — October 31, 2026

D6 §14 and D3 §13 specify the recommended contract; this supersedes the original OPEN status for MCR-06 as a design finding only.

| Finding | Design disposition | Verification binding / remaining boundary |
| --- | --- | --- |
| MCR-06 | **Owner:** the Catalog owner, in one extension section `pe_economy.discovery`. Native unlock bits stay unchanged in `pe_economy.catalog` v1, with no migration. **Four separate facts:** Seen and Unlocked are stored and sticky; Carried is derived live from ledger attachments, like native "seen" today; Installed is a ledger attachment. **Transitions:** only committed supported actions change facts (acquire, dismantle, unlock purchase, declared grant or reveal); browsing, quotes, diagnostics and registration never do; nothing ever relocks. **Identity:** owner namespace + provider-declared stable ordinal, with a 16-bit key guard; declared renames and absorbs. **Offers:** several offers referencing one entry share its entitlement; once owned they show grayed and refuse purchase. **Spoilers:** `????` and generic text everywhere for undiscovered entries; a missing provider shows "unavailable (mod missing)". **Space:** reserved at seal, so discovery never fails at runtime; section 1,024 bytes, extension profile raised to 5,120 bytes | D4 "MCR-06 acceptance bindings" (EFX-03/06/08, SHP-01/03/04/11, CNT-04/05/06/10/11/12, RES-01/02/04). Needs the extension store, the ledger (for Carried and dismantle) and the Catalog adapter implemented. Custom item definitions get no discovery state in v1 (`info` entries cover hidden offers) |

**Mod on/off follow-up (same day).** After reviewing how players and testers switch mods, D3 §14 adds:
- the three-layer split with build order S → C → M (S: save safety and extension store, mod-independent and useful now; C: content core; M: mod-owned features);
- the rule that the core is inert unless the loaded save has a custom-item ledger;
- a missing-mod notice on load and a save-slot warning (New slot / Overwrite / Cancel);
- an F1 Custom items page with explicit per-item Convert to normal item;
- tester guidance.

D2 §9 records the controls, D6 §12.6 the core boundary, D4 "Mod on/off bindings" the cases and D0 Section 5 N the S unit. These close the remaining MCR-10 user-experience gaps (missing-mod visibility, permanently stuck items) without changing any earlier rule.

**Versioning follow-up (same day).** D3 §15 consolidates versioning so migrations stay cheap:
- six version kinds with one meaning each;
- append-only changes with prefix read for extension sections, raising `min_reader` only for breaking changes;
- frozen single-step upgrade chains;
- declared per-instance content migrations;
- a single version table, golden fixtures for every released version, and a format-upgrade save warning.

D6 §14.9 lists the provider obligations, D4 "Versioning and migration bindings" the cases and D0 Section 5 O the standing review obligation. Existing tail records and their behavior are unchanged; one consequence is that data expected to evolve should live in extension sections.

Gate status: slice F (custom effects / Catalog) now also needs only MCR-11 (composed effect/pricing arithmetic) at design level, plus implementation. Slice G needs MCR-07–09/11. Next recommended document unit: MCR-07 (stock units and ownership), which has a 512-byte section, then MCR-08/09 together (quote/commit and operation tokens), then MCR-11, then MCR-12. No code, saves, tests, builds, defaults or balance changed.
