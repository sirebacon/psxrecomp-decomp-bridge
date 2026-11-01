# D6 — Small capability APIs and cooperation contract

Date: October 30, 2026. Status: scoped design specification draft; names/signatures/limits are proposed, not existing APIs or implemented support.

Validation companion: [D4 scoped plan/results record](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Validation and Playtest Record.md>), especially MOD/RAC/PERF/MEM cases and PB-06/07. A written case is not proof of implemented API support or a test pass.

Companions: [D1 proposal](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Economy presets and independent reward controls proposal.md>), [D2 controls](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Control Inventory and Menu Map.md>), [D3 persistence](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Persistence and Migration Design.md>), [D7 review](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets and Mod Extensions - Pre-implementation Review.md>), and [master checklist](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets and Menu Organization - Master Checklist.md>).

## 1. Scope and compatibility promise

All current/future mods may participate using shared conventions. A mod need not publish any API: it can register content, consume a capability, or observe events. Publish only small capabilities needed by real consumers. Shared infrastructure has no compulsory Economy dependency. Economy is the first provider, not the name or owner of a universal framework.

Baseline checked: clean `feat/localization` at `ae6520fe6`, `D:/Recomp Games/pe-localization`. Existing [host](<D:/Recomp Games/pe-localization/mods/host/pe_mod_host.h>) offers exact-version service lookup and ordered mutable hooks; [services](<D:/Recomp Games/pe-localization/mods/host/pe_services.h>) include `junk`, `catalog`, `keys`, `wardrobe`, `bestiary`, and `costumes`. New contracts must preserve them. The host compiles mods into a generated mod list; this draft promises no dynamic shared-library ABI or runtime hot unload.

First new public capability, proposed `economy_policy` v1, belongs to Economy and covers only:

1. Read-only policy/status query.
2. Init-time registration of new-path battle-Junk modifiers.
3. Init-time registration of completed new-path reward observers.
4. Init-time registration of additional complete Economy presets.

No public arbitrary balance setter, grant/spend callback, custom reward items, native table replacement, cross-category setter, worker API, custom price modifier, or live unregister is included in this first `economy_policy` slice. Existing `junk` v1 remains separate and unchanged. Section 10 specifies proposed separate content/effect/shop capabilities; these are not additions to the payout-modifier API. Generic registration identity/lifetime/result conventions can be reused without making other capabilities consume `economy_policy`.

## 2. Capability catalog and adoption

| Capability / owner | Observed or proposed | This slice |
| --- | --- | --- |
| `junk` v1 / Economy | Observed: balance/spend/give/pricing and equipment helpers | Preserve semantics; its `give()` is not a new lossless transaction API |
| `catalog` v1 / Economy | Observed: armor unlock query/action | Preserve; no speculative effect registry |
| `keys` v1 / QoL | Observed key pocket operation | Preserve |
| `wardrobe`, `costumes`, `bestiary` v1 / Collection | Observed selection/registration/creature interfaces | Preserve current contracts; no Wardrobe buying added to UI |
| `economy_policy` v1 / Economy | Proposed typed status/registration table | First implementation candidate, not implemented |
| Combat/Encounters | Later feature-owned operations/events | Adopt common conventions when actual integrations exist |
| Movement/Inventory/QoL | Later supported policies/actions | Preserve item integrity and field/combat separation |
| Localization/Presentation | Existing interfaces plus later integrations as needed | Audit exact versions independently; no new first-slice API here |
| Randomizer/overhaul coordinator | Later consumer of multiple capabilities | Design walkthrough only; no universal orchestration service |

For every adopted capability record owner, version, required dependencies, consumer, public operations, activation/thread/lifetime restrictions, saved-state effects, capacity, status, examples, and deprecation plan. Discover by capability/version rather than guessing support from a mod's name. No automatic replacement provider when a named capability is unavailable.

## 3. Discovery, versioning, and lifecycle

Use the existing exact service major version for discovery. The proposed table includes `api_version`, `struct_size`, and supported capability flags. Callers must check required flags/field availability; compatible additions use a new negotiated size/minor revision only under an explicit contract. Never append fields to a published table and assume old/new consumers can access them safely. Major semantic/layout changes publish a new service version. Keep the public source header small with fixed-width fields and typed callbacks; compiler-specific layout and cross-allocator ownership are not an external binary compatibility guarantee.

Required Economy consumers declare the existing `pe_economy` dependency so it initializes first, then resolve `economy_policy` during init. Registration copies validated metadata while retaining the callback/context under a session-lifetime contract. If the provider is inactive/unavailable, optional consumers skip cleanly; required consumers report their unsatisfied capability without a partial gameplay install. All-init/all-mods-off combinations must be checked against actual host behavior. Do not poll for services each frame or execute transactions during init.

Recommended first lifecycle: registration during init only, then seal/sort after dependency initialization. Changing enabled provider sets or registrations requires the existing restart flow; UI must say so. The resolver still checks effective provider activity at dispatch so cached pointers do not let disabled providers continue to contribute. Register handles identify provider generation; callback storage remains alive until shutdown. No worker dispatch and no live structural mutation during callbacks.

Registration failure rolls back that registration and any owner-managed resources. A consumer that cannot establish a required registration must unwind its own partial init. Normal cleanup stops submissions, finishes safe dispatch, and releases owner-held copied metadata/references in dependency order. Do not assume normal shutdown runs after failed init. If the actual host cannot provide safe partial-init cleanup or seal/readiness notification, explicitly scope the minimal host support instead of pretending it exists.

## 4. Shared registration and error conventions

Each registration carries a stable provider ID and provider-namespaced entry ID, format/version/size, optional display translation key with bounded fallback label, typed callback/descriptor, and context lifetime. Validate declared provider against host ownership; do not trust an arbitrary supplied owner string. IDs use canonical lowercase ASCII namespaced keys. Candidate key ceiling: **47 bytes excluding null**, matching D3 preset storage; reject longer IDs rather than silently truncating or hashing them into collisions.

Recommended bounded initial capacities: 16 payout modifiers, 16 reward observers, 32 provider presets. They are technical starting limits pending memory/startup measurements, not automatic permission to consume all 32 host services. Each feature contributes through one typed service rather than one host event/service per registration. Capacity failures are explicit; never evict an existing mod to admit another. Rebudget if target measurements require different bounds before publishing v1.

Results distinguish `OK`, `UNAVAILABLE`, `INACTIVE`, `WRONG_THREAD`, `WRONG_PHASE`, `BAD_VERSION`, `BAD_ARGUMENT`, `DUPLICATE_ID`, `CAPACITY`, `STALE_GENERATION`, `UNSUPPORTED`, `CONFLICT`, and `UNSAVEABLE`. No error implies partial payment, item consumption, or settings application. Repeated invalid runtime contributions are attributed/rate-limited, not silently persisted. Error diagnostics must have a bounded allocation-free fallback.

Callbacks/contexts are borrowed for the supported session lifetime; copied ID/descriptor text is owned by the provider registry. Input/output payload pointers are valid only for the callback; observers copy any needed small result into their own bounded storage. Registries never own arbitrary consumer allocations. Use matching owner release operations, not cross-module guessing at allocators.

## 5. Proposed operation surface

| Operation | Inputs / output | Ownership and side effects |
| --- | --- | --- |
| `query_status` | Caller-sized snapshot: engine, availability/block reason, generation, copied supported settings, active contribution count | Game-thread read-only; no RNG/progress changes; no hidden effect identities |
| `register_payout_modifier` | Versioned provider/entry descriptor and typed pure callback → registration handle/result | Init-only; does not credit money or enable income |
| `subscribe_reward_committed` | Versioned observer descriptor → handle/result | Init-only registration; callback after completed owner commit |
| `register_preset` | Stable key, localized labels, complete supported config/dependencies → handle/result | Init-only; validated/copied, never auto-applied |

Apply remains a player-facing owner action using the canonical settings module, not a callback that arbitrary consumers invoke. No new exposed cross-owner purchase transaction is needed for the first contribution API. Existing shop/install operations must satisfy D3's safety prerequisites where their behavior is touched; this API does not certify untouched legacy operations.

### Payout context and contribution

The modifier context is a read-only value snapshot: version/size, operation identity and generation, origin `extra_battle_junk`, ordinary/boss class, owner nominal fixed amount, documented equipment/performance factor, relevant enabled flags, and stable eligible-provider set. Do not expose native inventory pointers or mutable wallet/RNG. No gameplay content registration is performed in the callback.

Each callback returns only a numeric contribution: proposed nonnegative addition in whole Junk and a factor in basis points (10,000 = neutral). Candidate bounds: addition 0–65,535; factor 0–40,000. All values validate before aggregation; unsupported fields/types fail. A zero factor intentionally removes this operation's extra income but cannot alter native Junk. This must be visible in the active-modifier summary. The feature remains enabled; lack of extra income is an effective contribution, not a settings rewrite.

Recommended **draft composition** (requires approval): keep owner equipment/performance calculation as a numerator in 1/10,000 Junk; add external whole-unit additions; combine external factors by adding their deviations from neutral, not by multiplying every provider factor. In symbols: `N = owner_numerator + 10000 × sum(additions)`; `F = 10000 + sum(factor_i − 10000)`; final numerator is `N × F` over **100,000,000**. This produces 18 for base 10, +2, and a lone 1.5 factor. Two 1.5 factors combine to 2.0 under this rule, not 2.25; authors must not assume multiplicative stacking.

This keeps additive stacking independent of registration order and allows a fixed u32 fractional remainder in D3. Validate `F >= 0`, checked u64 intermediate arithmetic, and the owner's final per-award technical ceiling (currently proposed 99,999). Do not clamp unknown negative/overflow totals into a misleading valid contribution. Invalid individual contributions are rejected with source diagnostics; an invalid aggregate blocks the uncommitted attempt with a clear reason and no RNG/progress/item side effects. Do not discard an already generated pending award if later contributors change.

Carry fractional new-path income under D3, round once at commit, and preserve remainder. Base/Scavenger/performance calculation must be specified as integer basis-point factors before implementation; no floating-point callbacks, per-provider rounding, or double application of Scavenger. Technical composition and ceilings are proposed API semantics, not new balance approval. Legacy calculation/rounding is untouched; modifiers report inactive under Legacy and cannot turn a disabled bonus system on.

### Ordering and error boundaries

Snapshot eligible registrations at operation start and visit in canonical entry-ID order for deterministic diagnostics. Contributions do not observe predecessors' mutable output. The mathematical aggregate is order-independent within the checked representation; do not solve conflicts by callback priority. Existing legacy hooks keep their current registration-order tie behavior.

Pure callbacks may return a failure; they must not log recursively through an event loop, allocate unbounded state, consume RNG, perform I/O, wait on workers, mutate settings, or invoke wallet/install/grant actions. The host cannot sandbox arbitrary native code; documented discipline plus local tests is the guarantee boundary. A callback that never returns cannot safely be preempted; no timeout skipping during mutation.

## 6. Completed reward notifications

First-slice notifications cover owner-controlled **new-path** committed results, not speculative legacy hook interception. Payload: size/version, operation/award sequence, result phase (generated/pending versus credited/delivered/settled), family/source kind, final amount, permitted built-in identity, generation, and success status. Document phase distinctions so logging does not count generation and collection as two credits. Mask undiscovered effect information in player-facing consumers; private diagnostics remain governed by spoiler policy.

Dispatch after coherent state commit, using a fixed observer snapshot; no allocation of an unbounded event history. Notification delivery is synchronous/game-thread-only initially. It cannot veto the result or synchronously restart the same reward operation. This slice offers no general deferred arbitrary gameplay-action queue. An observer may update its own bounded UI/log state; reward-producing follow-ups require a later explicit action contract. Deduplicate by loaded playthrough and award/phase identity when appropriate, not a cross-save/global anti-cheat promise.

Changing provider availability cannot change the already saved final pending amount. No listener callback runs from save serialization or crash capture. Optional logging/profiling does not change game outcomes or RNG. Legacy reward notifications can be added only after an explicit parity-audited integration; their existence is not assumed in v1.

## 7. Additional presets and pure previews

Preset descriptors provide one canonical key, version, label/description translation keys and bounded fallbacks, required capability dependencies, and the complete supported D3 configuration. Validate chances, storage/income/redemption combinations, technical ranges, and required policy support before registration. No arbitrary executable setter, per-frame callback, cross-category payload, asset grant, private equipment mutation, or provider-specific save blob is included.

Matching retains key plus concrete supported settings; per-save state never references a registry index. A missing provider leaves settings/key intact and displays unavailable-provider status. Manual configuration edits commit through the owner and display Custom. Re-registering a descriptor in a later build must not silently update existing saves' concrete settings; offer a new explicit preview/apply if defaults changed.

Preview reads candidate config, current status, and descriptions without calling gameplay modifier callbacks. It can show the nominal base and list of active modifiers; variable effective values are labeled estimates until an actual transaction evaluates them. No RNG draw, resource reservation, progress mutation, notifications, conversion, or wallet change while highlighting. Apply revalidates provider/config/capacity/generation and the safe-field boundary. Unknown future descriptors fail explicitly rather than applying only the fields the old reader happens to recognize.

## 8. Examples for local fixtures — design, not shipped mods

1. **Single-capability consumer:** a statistics overlay resolves `economy_policy` v1 optionally, registers an observer at init, and records credited new-path amounts in a bounded counter. Economy absent/inactive → overlay shows unavailable, no gameplay change. No public overlay API is necessary.
2. **Two contributors:** provider `example.a` returns +2/neutral; `example.b` returns +0/15,000 factor. Base 10 yields 18; reversing init order yields 18. Disabling extra income yields no call/payment. Legacy yields no modifier call. Base 1 with Scavenger but no contributors alternates 1/2 under new-mode fractional carry; legacy rounding remains the baseline. Examples are local test providers, not buffs installed in the game.
3. **Future coordinator walkthrough:** a Randomizer discovers versioned encounter mapping and item placement capabilities (not provided here), builds one immutable seed/config/content plan, validates reachability/capacity with owners, previews affected categories, then requests reviewed prepare/commit at startup/New Game. A missing required capability refuses activation before any live replacement. Two exclusive table providers conflict; priority does not pick a winner. Bestiary reads the activated authoritative plan and respects discovery. Seed/version/mapping persistence and whole-plan activation require their own contracts; `economy_policy` cannot perform those changes.

The walkthrough preserves future design space without adding a speculative universal coordinator API, native-table mutator, or per-mod compulsory dependency today.

## 9. Modular implementation plan and acceptance

Proposed responsibilities: shared small types/identity/version conventions under host headers; Economy-owned policy registry and numeric resolver; existing wallet remains authoritative; settings/presets own preview/apply; D3 adapter owns saved config/progress and host admission dependencies; menus own localization/presentation. Keep public declarations separate from private aggregation/state structures. File names and exported signatures are to be selected on the implementation branch.

No runtime heap allocation is needed in normal modifier/observer dispatch. Fixed-capacity copied registrations are sorted at seal, operation snapshots are small, and diagnostics are optional. Empty subscriber paths return immediately; do not scan all content, poll service discovery each frame, or call observers for a non-event. Respect nesting guards and D1's safe lifetimes/cleanup; do not build worker queues/hot unload just to satisfy future sections.

Required D4 evidence: source/API version checks, startup/dependency/all-off cases, duplicate and capacity errors, short caller sizes, wrong thread/phase, owner attribution, reversed registration, invalid/aggregate arithmetic, fractional save/load, Legacy/no-subscriber parity, disabled/busy states, pure previews, missing provider presets, save-capacity refusal, reentry rejection, and notification phase/deduplication. Repeat registry/menu use under leak counters and measure no-provider/multi-provider overhead on the agreed low-powered target. Tooling/fixtures stay local in `D:/Recomp Games/pe-native-debug`.

Remaining decisions: approve composition and technical bounds/capacities; finalize callback/table field signatures and seal/readiness lifecycle; implement D3 status/admission/crash prerequisites before promising safe saved results; agree D4 budgets/fixtures. REV-07/10 have concrete candidates, not implementation passes. No new API, mod, worker, executable, or game code changed while writing this document.

## 10. Proposed custom-content, equipment-effect and shop capabilities

October 31 follow-up to D1 §20, D2 §9 and D3 §10; bind D4 PB-10–14. **Semantic specification draft; operation names and payloads below are conceptual, not published C symbols or implemented services.** Final public headers, table layouts, limits and ownership adapters need review before code. Preserve existing `junk`, `catalog` and other v1 consumers unchanged; do not reinterpret an existing table as this API.

Review disposition: Section 11 now resolves **MCR-01–03 at the recommended design-contract level**: deterministic registration/batches/budgets, cross-owner authority and phased dependencies/readiness. It takes precedence over earlier ambiguous registration/dependency wording in this section for E/F/G. No implementation or runtime validation is claimed. Later October 31: §12 (with D3 §11) resolves MCR-04/05/10 at design level: native mapping authority, ledger encoding/capacity and the minimum compatible reader; §13 (with D3 §12) specifies that storage expansion, MCR-04X, and §14 (with D3 §13) resolves MCR-06 discovery/entitlement. MCR-07–09, 11 and 12 remain open, including shop stock/quote/token/commit authority. D0 Section 5 M tracks implementation and validation separately.

### Capability split and adoption catalog

| Proposed capability / owner | Consumer / purpose | Required dependencies and saved effects |
| --- | --- | --- |
| `content_registry` v1 / shared content owner | Register/query item, weapon and armor definitions; no grants | Host identity/lifecycle conventions; static metadata alone creates no saved state; independent of Economy |
| `equipment_effects` v1 / equipment/effect owner | Register/query effect definitions and supported install/remove/transfer preparation | Shared IDs and relevant equipment runtime adapters; persisted attachments use D3, not native bit guessing |
| `inventory_actions` v1 / inventory owner | Resolve instances, inspect readiness and prepare supported use/equip/delivery actions | Reviewed native adapters and D3 instance/capacity contract; authority over actual instances remains here |
| `catalog_entries` v1 / Catalog owner | Optional presentation/discovery adapter for effect entries | Effect capability plus existing discovery/ownership rules; separate from effect runtime and preserves existing `catalog` v1 |
| `economy_shop` v1 / Economy shop owner | Register/query offers, quote and request purchases | Relevant inventory/effect action capability and wallet/stock adapters; saved state only for committed ownership/stock/required metadata |

All rows are proposed/unimplemented. They are capabilities, not one mandatory service per source file or per content mod. Existing provider initialization must be audited against host service limits. Do not consume a host service entry for every item/effect/offer. Content providers declare required content/runtime dependencies; Economy integration is optional where their other delivery paths are supported.

### Shared payload, identity and lifecycle rules

Use caller/descriptor `version`, `struct_size` and supported-operation flags under §3 negotiation. Use §4's proposed 47-byte maximum canonical namespaced keys unless a reviewed schema changes it consistently; no silent truncation/hash-only matching. Host-derived ownership must match the namespace; definitions cannot impersonate another provider. Runtime handles carry registry generation, and instance handles include loaded-playthrough generation. Saved IDs are stable keys, never these handles.

Init-time registrations copy bounded identity/metadata; callbacks and contexts are borrowed through the documented supported session lifetime. Asset references use their owner handles/lifetimes, not UI pointers. Declare registration counts, copied text bytes, parameter bytes, live instance/attachment counts, quote/reservation counts and stock/dedup limits before acceptance. The earlier 16/16/32 policy limits do not set these new bounds. Failed registration/preparation unwinds owned resources; capacity errors never evict live content.

Recommended dependency flow: discover required services → register definitions/effects → register optional Catalog/shop entries → seal/validate references → publish readiness. Optional forward references may be staged until seal but never become purchasable unresolved. If the host lacks a safe seal/readiness phase, design that small prerequisite or constrain registration ordering; do not assume it exists. Cycles/missing required capabilities refuse the affected provider's readiness. No transactions during initialization or from validation/render/notification callbacks. Provider set changes use restart; no hot unload/worker dispatch is introduced.

### Definition and effect descriptors

| Descriptor | Typed semantic fields / validation |
| --- | --- |
| Content definition | Owner/content IDs, kind enum (item/weapon/armor), definition/schema compatibility, localization keys/fallbacks, asset refs, native-compatible archetype, stack limits, mutable-field schema, required capabilities and supported-action flags |
| Equipment definition extension | Valid stat/ammunition ranges, animation/model family, equip restrictions, native/effect adapter references and supported slot model; never raw native array addresses |
| Effect definition | Owner/effect IDs, supported weapon/armor classes, schema/parameter bounds, runtime capability, slot cost, built-in/removable policy, stacking/uniqueness and conflict-group rules, translated/icon metadata |
| Catalog entry | Stable entry/effect IDs, discovery eligibility, visible metadata policy, supported target/action flags and pricing source; does not implement combat or auto-grant discovery |
| Offer | Owner/offer/shop/content or effect-service IDs, typed delivery kind, quantity bounds, Junk price policy, stock key/scope, availability/discovery requirements and explicit modifier policy |

Runtime behavior must use owner-validated supported actions. New arbitrary combat behavior requires reviewed typed event/context/result contracts, not a universal raw callback capable of mutating any subsystem. Numeric/effect stacking specifies canonical ordering, checked arithmetic and conflict rules; conflicting exclusive behavior refuses readiness/action instead of choosing registration priority. Identical content in distinct offers is allowed intentionally; duplicate offer identity is rejected. Shared stock requires an explicit stock key and common ownership contract.

### Typed operation families

| Operation family | Inputs → outputs | Side effects / phase |
| --- | --- | --- |
| `register_content`, `register_effect`, `register_catalog_entry`, `register_offer` | Versioned corresponding descriptor → owner-attributed handle/result | Init only; no grants, payment or record activation |
| `lookup_definition`, `query_instance`, `query_eligibility` | Stable ID/instance handle, caller-sized output and context → bounded copied view/readiness reason | Read-only game-thread; discovery-filtered, no RNG, allocation-required registry walk or gameplay mutation |
| `quote_purchase` | Offer, quantity, optional typed target → immutable bounded quote with final price/stock, dependencies, generations and refusal reason | Read-only; quotes are not reservations and consume no stock or save records |
| `prepare_delivery`, `prepare_equipment_action` | Owner-resolved definition/action, target, quantity and expected generations → prepared reservation/result | Private supported owner contracts, safe phase only; reserve without publishing ownership, consumption or payment |
| `request_purchase` | Quote ID/contents, operation identity, current playthrough and explicit confirmation → committed/refused result | Shop coordinates checked wallet/stock/item/effect owners; stale quote refreshes, never silently accepts changed terms |
| `abort_prepared`, owner `commit_prepared` | Exact reservation/transaction token → terminal result | Internal coordinator/owner boundary; not public arbitrary grants. One owner releases each reservation exactly once |
| `observe_committed` | Bounded immutable completed result with operation/offer/instance identifiers | After coherent publication only; cannot veto/replay purchase or mutate registry synchronously |

Do not expose raw wallet spend plus arbitrary delivery as the shop integration recipe. A free offer still uses eligibility, capacity, stock and duplicate checks. Removal/transfer services require their own target/consumption contract and cannot be inferred from item delivery. First shop scope is Junk only; external currencies, global stock and shop replacement need separate versioned contracts.

Query views/inputs are call-lifetime snapshots unless a documented copied handle is returned; menus retain IDs/generations rather than borrowed pointers. The quote must identify offer/provider/content revisions, playthrough, target generation, quantity, final price and stock/pricing generations, with a defined invalidation/expiry policy. Any mismatch returns `STALE_GENERATION` or an attributable refreshed quote requiring confirmation. Do not promise a quote freezes funds or capacity.

### Action safety and missing dependencies

Reuse §4 results, adding proposed typed reasons `MISSING_CONTENT`, `MISSING_EFFECT`, `SCHEMA_UNSUPPORTED`, `UNDISCOVERED`, `TARGET_INVALID`, `NO_SLOT`, `INSUFFICIENT_FUNDS`, `OUT_OF_STOCK` and `INVENTORY_FULL` where useful; save capacity remains `UNSAVEABLE`/`CAPACITY`. Report structured reasons with translation keys, not only hardcoded text. No error result permits partial payment, consumption, stock loss or installed effect change.

All owners validate at prepare, and commit rechecks dependencies at one safe game-thread boundary under shared transaction/reentrancy rules. Preparation must guarantee supported commit or fail with no visible gameplay change; if the inventory/native path cannot do so, mark that action unsupported until an adapter exists. Reject nested actions affecting the same state; observers may only schedule separately supported future actions. Release reservations on cancel/failure/restart shutdown; no live quotes across playthrough/provider generations. Save/crash publication obeys D3 §10, not a new shop-specific serializer. Bounded sequence deduplication is playthrough-local, not global rollback prevention.

Unresolved instances/effect attachments preserve D3 identity/payload/slots. Queries return unavailable views; no raw native indices or executable opaque data leak through the API. Missing discovered Catalog entries may show unavailable status while undiscovered ones retain `????` and hidden details. Absent effect provider does not grant a removable/free slot. Runtime fallback/refusal belongs to equipment/compatibility owners, never the shop. Optional offer dependencies hide/disable the offer; required gameplay dependencies refuse readiness/resume. Reinstall cannot reset one-time stock or duplicate installed bonuses.

### Required examples, acceptance and unresolved decisions

Local-only future examples: provider A defines one native-compatible item/weapon/armor and effect; provider B contributes a distinct effect and shop offer; reverse their registration order. Demonstrate content use without Economy, Catalog registration without sales, two distinct offers for one definition, a missing provider round trip and a rejected stale purchase with no payment. Use the same owner APIs, not privileged test-only grant paths.

Before implementing, approve actual fixed-width C payloads/table layouts, capacity limits, supported native archetypes/actions, registry seal/readiness, prepared-commit guarantees, quote invalidation, stock scope, stacking/conflict algebra and effect runtime contexts. D3 must accept storage/missing-equipped behavior; D4 §15 must bind and execute corresponding cases. Registration dispatch/quote paths require bounded work, cache invalidation and no-provider fast paths; measure memory/cleanup and low-powered costs. No new capability/header/code or examples were built by this documentation update.

## 11. Registration, ownership and dependency rules — MCR-01–03 disposition

October 31 recommended design decision, requested as documentation only. This section binds registration semantics for the proposed E/F/G capabilities; it does not change existing host hooks/services, legacy registration order or gameplay. Names below describe contracts, not existing functions. Numeric limits are an initial **technical profile**, not balance values or measured performance certification. Public C layouts and implementation evidence remain follow-up work. Actual instance/save/stock/quote limits are not supplied by this registry profile.

### 11.1 Identities, owners and required versus optional batches

The host supplies an immutable owner identity and its registered namespace; callers cannot select another owner with a string. Reserve native/framework namespaces for their authorities. A registry key is `(capability domain, canonical namespaced entry ID)`; content kinds share one content domain, so one key cannot simultaneously mean item and weapon. Different domains may use the same textual key but references always carry the domain/kind expected by the consumer. Keys are case-sensitive canonical lowercase ASCII, maximum 47 bytes excluding null; reject noncanonical/overlong input rather than rewriting/truncating it. Hashes accelerate lookup only; equality/conflicts use full keys.

Every participating owner submits one bounded registration manifest per startup generation, with named owner-scoped batches and complete declared membership. Dynamic discoveries during runtime cannot append definitions. A batch is the smallest admission unit: either every required descriptor/reference in it is ready, or none is published. Multiple kinds may share a batch when the author intentionally requires them together. An entry belongs to exactly one batch and owns exactly one key; payload variants are not duplicate registrations.

Required and optional describe the relationship between batches, not permission to partially register a descriptor. A provider declares its base batch and other explicitly required batches; failure makes that provider's new capability integration unavailable. Optional batches fail independently unless another batch explicitly requires them. Keep base content/effects separate from optional Catalog and shop adapters, so missing Economy cannot discard independent definitions. No saved state, grants or assets become live merely because a manifest is collected.

Failure of a provider's base/required batch removes all its new E/F/G contributions from eligibility for that generation, then invalidates any foreign batch that requires those contributions; repeat to a fixed point. Failure of a genuinely optional batch removes only that batch and its declared dependents. Do not publish otherwise valid entries from an unavailable provider or call its failed initialization contexts. These rules apply before readiness publication and cannot erase retained saved records.

Provider readiness here controls only its new E/F/G capability contributions. It does not retroactively disable unrelated legacy features or change the host's mod-enabled setting. Missing required runtime behavior still prevents unsafe gameplay through the separate compatibility gates. One provider with many items uses batches/entries, not one host service per item. A failure result must identify owner, batch, entry/domain and reason where known.

### 11.2 Provisional registration and deterministic conflict handling

Collection returns a provisional receipt, **not a usable handle or readiness success**. At seal, sort by canonical full domain/owner/batch/entry keys for reproducible validation, diagnostics and iteration. Sorting is not priority-based conflict resolution.

If two descriptors claim the same registry key, invalidate **all claimants** and their containing batches, including duplicate calls/entries within one owner's manifest. Never retain the first claimant or silently treat a different payload as an update. One failed optional integration cannot be replaced with a hidden winner. Repeated receipt/status queries are read-only; malformed submission cannot be retried within the same generation to erase a recorded conflict. A corrected manifest requires restart/new generation.

Apply validation to the complete declared provisional set, then propagate required-batch/reference failure until no further batch becomes unavailable. Do not resurrect a conflicting key when another claimant subsequently fails for a different reason; otherwise validation order could select a winner. Valid unrelated optional batches remain eligible. Readiness publishes once after this fixed point, not incrementally as each mod initializes. No published entry is evicted to admit a late submission; registrations after collection closes return wrong-phase.

### 11.3 Initial registry resource profile and overflow policy

Bound staging, copied metadata, graph storage, diagnostics and publication, not only successful entries. The following starting profile applies to the new registries collectively, **not existing host service slots**:

| Limit | Per owner per domain | Whole domain |
| --- | ---: | ---: |
| Content definitions | 256 entries / 64 KiB metadata | 1,024 entries / 256 KiB metadata |
| Equipment effect definitions | 64 entries / 16 KiB metadata | 256 entries / 64 KiB metadata |
| Catalog entries | 128 entries / 16 KiB metadata | 512 entries / 64 KiB metadata |
| Shop offers | 256 entries / 32 KiB metadata | 1,024 entries / 128 KiB metadata |

Also bound participating owners to 32, batches to 16 per owner, entry dependency/reference edges to 8 per entry and explicit batch requirement edges to 16 per batch. These limits are simultaneous ceilings; fitting a count does not imply fitting its byte budget. Metadata includes copied keys/labels/descriptors/reference edges and registry-owned indexing/bookkeeping attributed to that domain. Assets, callbacks' private allocations and gameplay instances are separate owner budgets, not permission to allocate without bounds. Graph traversal must be iterative/bounded or explicitly depth-checked.

Each domain has a separate fixed budget; unused Shop capacity cannot crowd out Content or be borrowed to change outcomes. The four domain metadata budgets total 512 KiB for one staged/published logical set; if a separate copy is needed for publication, cap the simultaneous old/staged/published registry-owned metadata at 1 MiB and document accounting before implementation. Owner/batch headers must be charged to the declared domain budgets, without an unbounded auxiliary map. Diagnostics use a bounded independent fallback, not one allocated error string for every failed attempt. Measure/revise the profile before release if the low-powered target requires it; never silently revise a published profile's semantics.

Overflow behavior deliberately favors reproducibility over silently selecting a subset:

- A per-owner/domain count/byte violation rejects that owner's entire contribution in that domain and all affected batches. Do not keep its first N entries. Other domains/owners continue only according to their explicit required dependencies.
- Exceeding a whole-domain budget makes that **new capability domain unavailable for the startup generation**, with an attributed capacity error, rather than selecting the first or lexicographically preferred packs. Required-batch propagation applies; unrelated domains remain usable. In particular Shop overflow alone does not suppress a base Content batch that does not require Shop.
- Exceeding shared owner/header accounting makes the new registration generation unavailable, not an order-dependent first-32-owner selection. Existing legacy APIs/default gameplay are not changed by this policy, but existing custom saves may need to refuse resume when required capabilities are unavailable.
- Staging must never exceed its fixed memory budget just to discover overflow. Account the declared bounded manifest envelopes before copying; once overflow is known, retain only bounded failure status and stop publishing that domain. Continue bounded status processing where possible, without pretending all claimant payloads were retained. No retry, budget borrowing or removal of failed entries to manufacture a winner in that generation.

Counts/bytes cover the full provisional declaration before conflict/dependency pruning; rejected batches do not become a way to change capacity admission by registration order. Known owner-quota rejection and domain overflow may both be reported. Memory allocation failure at staging/publication aborts the affected new generation/domain safely; no partially live replacement or promise of deterministic success under different machine memory failures. These limits are availability controls, not a sandbox against hostile native code. Operators fix incompatibility by changing installed packs or an explicitly versioned technical profile and restarting, not by deleting saved unknown content.

### 11.4 Cross-owner reference and mutation policy

| Operation | Default / required authority |
| --- | --- |
| Inspect/reference another definition | Allowed as a typed stable reference to a ready compatible definition; public UI queries remain discovery-filtered. Reference is not permission to invoke arbitrary behavior or grant ownership |
| Register/rename/replace another owner's definition | Forbidden. Only the defining authority may publish its schema/aliases; native/framework definitions use their reviewed adapters. No implicit replacement API in v1 |
| Offer another owner's item for sale | Allowed only when the content definition explicitly opts into `allow_external_shop_offers` and the target shop admits that provider/action. Flag defaults false; referring provider owns its distinct offer ID, never the item definition |
| Add offers to another shop | Shop owner declares its accepted typed contribution policy and optional allowlist. Default closed; Economy may explicitly mark an extensible shop open to compatible offers. Closed vanilla shops cannot be replaced by registration |
| Install a foreign effect on equipment | Effect and target policies must both permit the classes/action, and the equipment owner validates slots/conflicts/discovery. Custom targets default closed to external effects until they opt into supported effect classes; native adapter policy must be declared explicitly |
| Attach provider-specific instance data | Only at a target-declared supported extension point. Attachment key includes extension owner and schema identity; default deny unspecified extension points. Registry/persistence framing remains authoritative |
| Share a foreign stock pool | Requires explicit stock-owner admission to the pool/action, never inferred from the same item or a copied string key. Pool units/migrations remain MCR-07 |
| Mutate inventory/common instance/another attachment | No direct writes. Use supported inventory/equipment actions. A provider validates/migrates only its own payload; common fields and other owners' payloads remain with their authorities |

Owner authorization is declarative/versioned and checked at seal and action eligibility; no user scripting or arbitrary grant callbacks are introduced. Content and shop owners can restrict compatible actions/providers but cannot bypass player discovery, wallet/save capacity, disabled features or existing anti-exploit rules. Self-owned offers still need shop admission and all gameplay checks. Renaming a foreign ID is not a permitted integration workaround. Runtime provider absence invalidates eligibility even with cached resolved handles.

Independent attachments use `(instance ID, attachment owner, attachment key/schema)` framing; an installed effect additionally references its effect definition and source provenance. Removing/migrating A's data must retain B's framed payload and occupied slots. Two distinct effects from one provider remain distinct entries. Exact persistent encoding and byte budget remain MCR-04/05/06, not resolved by this ownership decision. Cross-owner services may execute their documented validated actions; namespace ownership does not prohibit ordinary supported gameplay changes such as installing an authorized effect.

### 11.5 Dependency kinds and startup phases

The following graph types are separate; a single undifferentiated dependency list is insufficient:

| Edge | Resolution and cycle rule |
| --- | --- |
| Required service initialization | Existing host ordering plus reviewed capability-export support. Required provider must initialize/export compatible service first; cycles are invalid and refuse the involved initialization integrations |
| Passive typed definition reference | Resolve stable IDs/kinds/versions/policies from the complete staged set at seal. Forward references and passive cycles are allowed when validation needs only identity/metadata presence, with no recursive construction or gameplay execution |
| Derived construction/evaluation or hard readiness order | Must be explicitly declared and acyclic; reject the cycle's affected batches and propagate required failure. Never run recursive provider constructors to resolve a passive reference |
| Required batch dependency | All-or-nothing readiness; directed acyclic batch requirement graph. Reject cycles, even if authors intended mutual readiness; put genuinely atomic same-owner entries in one batch instead |
| Optional adapter | Missing/incompatible capability makes only that adapter batch unavailable; it cannot silently become a required edge for independent content |

An effect composition or exclusive runtime conflict is not made valid just because its passive IDs resolve. Those rules remain the equipment owner's MCR-11 contract. A missing required passive reference rejects its consuming batch and propagates until stable. A passive cycle whose members otherwise validate can resolve as a set; a missing external requirement can invalidate the set through that propagation. This is bounded graph validation, not unbounded callback recursion.

Chosen lifecycle requires a **small shared collection/seal/readiness facility**, to be implemented only under separate authorization. It is a prerequisite absent from this draft's verified host capabilities; do not emulate it by exposing entries early. No fallback to register-first ownership is allowed if the facility is unavailable.

1. **BOOTSTRAP:** establish shared registry/coordinator and collect actual enabled provider identities/capability exports under valid host initialization ordering. Capability availability/version and ready-for-gameplay are distinct states. Collection itself is not an Economy service.
2. **COLLECT:** providers submit complete manifests and declarative adapter requirements through the shared collector during supported initialization. They need the collector, but do not invoke optional Economy/Catalog APIs whose providers may initialize later. Retain bounded unresolved typed references; no asset/gameplay/save side effects or callbacks that assume readiness.
3. **SEAL:** after all eligible initialization completes and before affected load/gameplay use, close collection. Check envelopes, duplicate claims, schemas, ownership/policies and graph kinds canonically. Feature owners validate only their typed staged data through bounded pure validation; no live registrations, user actions or purchases. Apply batch failure propagation to a fixed point.
4. **PUBLISH:** commit the complete ready registry generation and each entry/batch's outcome once. No callbacks/allocations that can introduce partial publication. Resolved runtime handles include this generation; a receipt becomes usable only if its final outcome is ready. Optional consumers query their batch result instead of assuming the whole provider succeeded.
5. **RUN / RESTART:** only published ready actions are eligible. Still recheck active provider/capability/player state at action time. No late registration or structural hot unload. Restart/shutdown stops submissions, releases pending registry/session resources and callbacks in dependency-safe order; new generation invalidates receipts/handles. Saved stable IDs remain for preservation/migration.

If any required collection/validation/publication step cannot complete, expose unavailable status and preserve existing saves; never publish a half set. Native load/refusal behavior when required core support is absent remains MCR-10. Phase callbacks use the shared game-thread/reentrancy rules and cannot recursively seal, register or issue gameplay transactions. A legacy required service consumer may still follow §3's dependency ordering; the new collector is the optional cross-provider integration path, not a change to old services.

### 11.6 Deterministic examples and acceptance bindings

| Submission / dependency | Final result under this contract |
| --- | --- |
| A registers 20 definitions and B registers 30 distinct definitions, reversed order | Same ready set and canonical iteration order if both fit; no per-item host service |
| A repeats its own item key with a different payload | Both declarations' containing batches fail; no first call wins, no in-generation replacement |
| B claims A's namespace | Ownership rejection before it can replace A; B cannot invalidate A simply by an unauthorized foreign claim. Duplicate-all rule applies to authenticated valid claims, not impersonation |
| A/B offer distinct IDs for A's externally saleable item in an open shop | Both offers may be ready; each has its own owner and explicit stock authority. No automatic shared stock |
| A content is valid; optional Shop adapter references absent Economy | Content ready, Shop batch unavailable, no partial saved grants or enablement changes |
| A and B have passive cross-references | Resolve together if kind/version/policy checks pass and neither requires cyclic evaluation; one missing required external target propagates failure |
| A/B require each other's initialization or hard readiness | Cycle diagnosed, involved batches/integrations unavailable; optional independent entries remain only if their dependency graph permits |
| Shop global envelope exceeded while Content fits | New Shop domain unavailable; independent Content remains ready. No earliest packs selected, even if reversing manifests |

Bind PB-10/14 to this section's identity/quota/batch/lifecycle rules and PB-13 to reference/shop admission only; stock units, quotes and purchase commits remain open. D4 CNT-04, SHP-01/02 and RES-03/04 need the acceptance scenarios above plus within-owner permutations, required-batch failure, quota count/text-byte boundaries, unauthorized claim isolation, denied extension/foreign stock access, passive versus hard cycles, partial-init resource unwind and restart invalidation. No test execution or added test files accompanies this decision. All future examples/tools/raw evidence stay local in `pe-native-debug`.

**Disposition:** MCR-01–03 are resolved as recommended design rules in this section. Public-header/source implementation, graph/resource measurements and native validation remain unchecked work. MCR-04–12 remain open; definitions being ready does not mean acquisitions, effects or purchases are saveable or supported.

Later October 31: §12 resolves MCR-05 and the component side of MCR-10; D3 §11 resolves MCR-04 and the saved-state side of MCR-10. MCR-06–09, 11 and 12 remain open.

## 12. Native inventory mapping authority and the content core — MCR-05/MCR-10 disposition

October 31 recommended design decision, documentation only. This section binds how a logical custom instance is represented in, and kept attached to, the native inventory, and names the minimum component that must exist for that to stay safe when providers or mods are off. The saved bytes and the compatibility state table are D3 §11. Names describe contracts, not existing functions. No code, hook or save changed.

### 12.1 One mapping authority

The **content core** (§12.6) owns the only logical-to-native mapping, the D3 §11 ledger. Providers, Economy, Catalog and tools never keep their own native mappings, never write pool records and never cache pool indices across frames; they hold generation-bound instance handles from `inventory_actions` (§10) and act through its supported actions. A provider that needs per-instance data uses an attachment (§11.4), keyed by `instance_id`, never by slot or pool index.

The mapping key is **(pool index, fingerprint)** (D3 §11.2). The anchor is the native equipment pool record, not a bag/storage slot and not a pointer. Rationale from the audit below: every native path that moves equipment moves only the 16-bit slot value (0x100 + pool index); the pool record and its index stay put. The game itself re-finds equipped gear after a sort by searching for that slot value (`src/main/item/armor_capacity.c:722–758`), so the pool index is already the native identity.

### 12.2 Supported native classes in v1

| Native representation | Per-instance identity possible | v1 decision |
| --- | --- | --- |
| Equipment pool record (weapon kinds 1–8, armor kind 9; slot value 0x100–0x17F) | Yes: one record per item | **Supported** for custom persistent instances, under the D3 §11.1 native-complete rule |
| Slot-value item (kinds 10, 12–15; slot holds the base item number) | No: identical items are indistinguishable natively; no per-item record | Not a custom instance class. Any custom consumable needs a separate definition-level design (fungible, no attachments) |
| Ammo pools and special records (kinds 16–18; slot value 0x200–0x208) | No: shared counters | Unsupported in v1 |
| Key items and pe_qol pocketed keys | Owned by other records | Unsupported in v1 |

**Stack equivalence:** none. Equipment never stacks natively, and no two custom instances are ever treated as equivalent or merged, even with the same definition and identical attachments. Splitting does not exist for this class.

### 12.3 Identity lifecycle

| Event | Rule |
| --- | --- |
| Create | Only through a core `inventory_actions` delivery: reserve ledger capacity (D3 §11.3), allocate a free pool record by the native rule (`iconId` 0), write the complete native record, place its slot value, assign the next `instance_id` and fingerprint, all in one commit. Pool full or bag full refuses before any charge |
| Move bag ↔ storage, sort, compact, equip, unequip | No ledger change: the pool index is unchanged. Native code keeps equipped slots correct by value |
| Use in battle | Battle reads the equipped pool record; effects resolve instance → pool index each time; no identity change |
| Native mutation of mutable fields (ammo, bonus stats, mods, flags) | Allowed through native paths; excluded from the fingerprint |
| Destroy (discard, sell, dismantle, carry-over reset) | Only through a supported core destroy action that removes the ledger entry and its attachments in the same commit as the native free. Native free paths are vetoed for custom records (§12.5) |
| Merge (Wayne tune-up consuming a source record) | Refused when either record is custom, until a reviewed merge adapter exists |
| Snapshot/compare copies (`g_MenuItemUseSelectedItemSnapshot`, `g_InvCompareSlotLeft/Right`) | Transient views, not identities; their write-backs land on the pool record |
| Save / load | Native half saves the whole pool; the ledger saves with `native_stamp`. Load reconciles the ledger against the pool before the first field frame (D3 §11.5) |
| Save editor edit / older build | Detected by stamp/fingerprint at the next supporting load; identity only ever demoted (UNCERTAIN/ORPHANED), never reassigned to another record |

`instance_id` is never reused, so an attachment or an operation record can never silently point at a different item after a destroy.

### 12.4 Native path audit (current branch, read-only)

Read from `feat/mod-presets-framework` in `D:/Recomp Games/pe-mod-presets` (base `8c52cdde5`; the worktree's uncommitted changes are in host save files, not in these native sources). Re-audit on the implementation branch before coding.

| Path | Location | Touches | Mapping consequence |
| --- | --- | --- | --- |
| Slot value encoding | `include/pe1/inventory_slots.h:91–120` | 1–0xFF base item, 0x100+ pool record, 0x200+ special record | Defines the classes in §12.2 |
| Pool layout and save | `include/pe1/inventory_runtime_types.h`; `include/pe1/save_blob.h` (`inventory` 0x1064 at 0x68) | 128 × 0x20 records saved whole | Native half always carries complete records |
| Add item / allocate record | `src/main/item/active_list.c:1230` `Inv_AddItem` (kinds 1–9 via `Inv_FindSlotByIndex`); `PE_HOOK_ITEM_ADD` already present | Allocates a pool record from base data | Native grants create plain native items; custom creation uses the core action, not this path |
| Free on removal | `src/main/item/actions.c:1033–1039` | Clears slot, frees record | Needs a pre-free veto/notify hook |
| Free on capacity/discard | `src/main/item/armor_capacity.c:286–289` `DeleteSlot`; `src/main/save/game_data.c:544–553` `RemoveItem` (also clears the equipped armor slot) | Clears slot, frees record | Same hook |
| Carry-over reset | `src/main/item/active_list.c:381–390` | Frees every record whose flags lack 0x18 | Treated as a playthrough reset; exact trigger and the meaning of flags 0x08/0x10 to be confirmed before coding |
| Sorts | `src/main/item/armor_capacity.c:646, 687, 737, 774, 794` (`qsort` on bag, storage, special lists) | Permute slot values only; equipped slots re-found by value | No mapping change |
| Equipped references | `src/main/item/swap.c:464` (`tracked[0]` weapon, `tracked[2]` armor), `g_AyaEquippedWeaponSlot`/`ArmorSlot` | Bag slot indices | Resolve slot → value → pool index; never store slot indices in the ledger |
| Bag ↔ storage swap | `src/main/item/swap.c`; `src/main/menu/inventory.c:177` | Move slot values | No mapping change |
| Battle grants | `src/main/battle/attack.c:330`, `commands.c:76`, `phase.c:94`, `setup.c:556` | `Inv_AddItem` of native items | Native only |
| Script grants | `src/main/script/system_opcodes.c:1007` | `Inv_AddItem` | Native only |
| Mod paths | pe_economy dismantle/rebuild (`pe_create_item`), pe_qol sort and pocketed keys, pe_economy Workshop/Requisition delivery | Create/free/move | Must route custom records through core actions; dismantle/rebuild of custom records refused until adapted |
| Save editor | `save-editor/src/save/equipment.rs` | Round-trips `reserved02`; zeroes it for new records | Editor edits trigger reconciliation; editor must keep the mod tail |

Items to confirm before implementation: the fingerprint field set is never written by a supported native path (in particular that tune-up changes only bonus stats and mods); the exact meaning of the carry-over reset; whether any path rewrites `reserved02`; and a complete list of record-freeing sites in the retail binary, not just in decompiled names. An unaudited path that frees a custom record is caught by reconciliation (ORPHANED) but not prevented, so the hook list must be complete before custom instances ship.

### 12.5 Required native hooks (implementation prerequisites, not existing support)

- **Pre-free veto with notify** at every record-freeing site above: given the pool index and the reason, the core refuses when the record is custom and the action is not a supported destroy for it, and the native path aborts without side effects. Refusal must leave the slot, record and equipped state exactly as before.
- **Merge veto** at the tune-up consume path.
- **Post-load reconcile** before the first field frame, and **pre-save stamp** at the point where the native save image is built.
- No per-frame scanning of the pool; reconciliation runs at load and after an unhooked path is detected.

If a site cannot be hooked safely, custom instances must not be allowed in the situations that reach it, and the D2/D3 placeholder rules apply.

### 12.6 The content core: minimum compatible reader (MCR-10)

The content core is a **host-level component**, compiled into every `PE_MODS` build, not listed in Manage mods and not part of any provider or of Economy. It initializes with the save host and runs when All mods is off (D3 §11.5). It contains only: ledger parse, validation and serialization; capacity account and reservations; reconciliation; the native veto hooks; and the `inventory_actions` instance resolution needed by those. It has no gameplay of its own and owns no content.

- **Reader revision.** The core carries a reader revision; the ledger's `min_reader` names the lowest revision allowed to mutate it. A lower revision preserves the ledger read-only if it can parse it and refuses continuing the save through the outer load gate if it cannot (D3 §11.5).
- **Independence.** Provider absence, Economy absence and All mods off are all handled by the core alone. Absence of the core itself is the vanilla build, where nothing can be enforced; that case is a documented one-way conversion (D3 §11.5), not a supported mode.
- **Outer load gate.** A small check at save load, before any field frame, that can refuse continuing a save with an attributable message and leave the file untouched. It reuses the host's load-status reporting (D3 §4 host capabilities) rather than a new UI system.
- **Inert without a ledger.** Installed beside the save host (which already runs with All mods off, `mods/host/pe_mod_host.c:336`), but it registers no veto hooks and shows nothing unless the loaded save has a ledger with entries (D3 §14.2).
- **Custom items page and Convert.** The core owns an F1 "Custom items" page listing non-ACTIVE entries. Its only actions are the explicit, confirmed, per-item Convert to normal item (UNAVAILABLE/UNCERTAIN) and Remove record (ORPHANED), each one core destroy commit (D3 §14.5). Providers cannot call these; they are player actions.

### 12.7 Deterministic examples and acceptance bindings

| Situation | Result under this contract |
| --- | --- |
| Custom gun A in bag slot 3 is sorted to slot 0 and equipped | Ledger unchanged (pool index unchanged); equipped slot re-found by value |
| Custom gun A moved to storage and back | Ledger unchanged |
| Two instances of definition A, different attachments | Two entries with different `instance_id`s; never merged or treated as a stack |
| Player discards custom gun A with its provider missing | Refused (UNAVAILABLE); slot, record and equipment unchanged |
| Player discards custom gun A with its provider present | Supported destroy: native free and ledger entry/attachments removed in one commit |
| Wayne tune-up uses custom gun A as the source | Refused until a merge adapter exists |
| Older build discards gun A, then the save loads in a supporting build | Stamp mismatch; record freed → ORPHANED; nothing regranted |
| Old build discards gun A and a native gun of the same type lands in the same pool record | Fingerprint may match → UNCERTAIN, not ACTIVE; custom extras stay dormant until an explicit backed-up repair |

Bind D4 §15 CNT-02/03/05/07/10/12 and EFX-04/05/08 to §§12.2–12.5 and CNT-05/06/07 and RES-01/02 to §12.6 (D4 records the bindings in "MCR-04/05/10 acceptance bindings"; none has run). **Disposition:** MCR-05 and the component side of MCR-10 are resolved as recommended design rules. The native hooks, the core, the outer load gate and the audit items in §12.4 are unimplemented prerequisites; persistent custom instances additionally wait on the storage-expansion store (MCR-04X, D3 §12, §13 below).

## 13. Save extension sections — MCR-04X service boundary

October 31 recommended contract, documentation only; the file format, write order and missing-file behavior are D3 §12.

- **Who uses it.** Host-level owners and providers that need persistent state beyond a small tail record. The content core's ledger is the first user; MCR-06 discovery, MCR-07 stock and MCR-09 operation results get their own sections. A provider never writes into another owner's section; per-instance provider data still goes through ledger attachments (§11.4), not a provider section, unless a separate review approves one.
- **Registration.** At init, with the same lifecycle as tail records: canonical key (D6 §11.1), version, `min_reader`, declared maximum bytes, optional `upgrade` for older versions. Registration fails if the declared maximum does not fit the remaining profile; there is no first-come borrowing.
- **Activation.** Dormant until the owner activates it for the playthrough; sticky; cleared by New Game or loading a save without it. A save with no active section writes no link and no file.
- **Read.** Before the first field frame the host offers each owner its section bytes, or a status: absent, damaged (section CRC), newer than this owner, or file missing. The owner decides its own fallback; the host carries unclaimed sections forward unchanged.
- **Write.** The host asks each active owner to serialize into a buffer of its declared maximum. Exceeding it or failing refuses the whole save before any file is written (existing admission path). Owners never see paths, generations or file I/O.
- **Required flag.** An owner marks its section *required* when continuing without it would misrepresent player data (the ledger with instances). This drives the outer load gate prompt (D3 §12.4).

Not provided: random access during play, per-frame writes, sharing a section between owners, or hot reload. All save I/O stays inside the native save sequence.

## 14. Custom discovery and entitlement — MCR-06 disposition

October 31 recommended contract, documentation only. Encoding is D3 §13. No code, record or save changed.

### 14.1 What exists today (read from `feat/mod-presets-framework`)

- `pe_economy.catalog` v1 (tail, 312 bytes; `mods/pe_economy/pe_catalog.h:31–36`) saves **unlock bits** for native effects 1–20 per gun/armor, plus the Rebuild list. A New Game clears it.
- **"Seen" is not saved.** The Catalog derives it live from mods on carried gear (`pe_seen`, `mods/pe_economy/pe_catalog_pages.c:30–38`). Grid labels show `?` when an effect is neither unlocked nor seen, and "(locked)" when seen.
- Unlocks come from dismantling gear that carries the effect (`pe_dismantle.c`), from Requisition and from rare drops (`pe_loot.c:701, 761`, through the `catalog` v1 service `unlock_armor`). Removing an installed effect keeps it unlocked.

### 14.2 Owner and scope

- **Owner: the Catalog owner** (Economy), for custom entries registered through `catalog_entries` v1, in one extension section `pe_economy.discovery` (D3 §13). There are no per-provider discovery records, and providers never write discovery state directly.
- **Native effects stay where they are.** The 1–20 unlock bits stay in `pe_economy.catalog` v1, unchanged and not migrated. The Catalog shows native and custom entries together through one query, with two storage back ends.
- **Entry kinds in v1:** `effect` (installable through the Catalog; both facts below apply) and `info` (a reveal-only flag that offers or presentation can require, such as a found blueprint; *unlocked* has no meaning for it). Custom item definitions get no discovery state in v1; an offer that should stay hidden until something happens requires an `info` entry.
- **Economy off:** the host carries the section unchanged (D6 §13). Effects already installed on gear keep working, because installation lives in ledger attachments, not discovery. Only the Catalog/shop presentation and actions are absent.

### 14.3 Four separate facts

| Fact | Stored where | Meaning |
| --- | --- | --- |
| **Seen** | Discovery section, sticky | Name, description and icon may be shown. Never grants anything |
| **Unlocked** (entitlement) | Discovery section, sticky; implies Seen | The player may install the effect through the Catalog at its price. Sticky like native unlocks: removing, selling or losing gear never relocks |
| **Carried** | Derived live from the ledger's attachments, as native "seen" is today | Shows the effect as seen while gear carrying it is in the bag or storage; latched to *Seen* on a supported acquisition commit (§14.4) |
| **Installed** | Ledger attachment (D3 §11) | The effect is on that item. Not discovery state |

Possession of an effect consumable is inventory (MCR-07/08 services), not entitlement; holding one reveals *Seen* only.

### 14.4 Supported transitions

| Event (committed through a supported action) | Seen | Unlocked |
| --- | --- | --- |
| Acquire an item carrying the effect (delivery, drop, purchase) | Set | — |
| Dismantle an item carrying the effect (existing rule) | Set | Set |
| Buy an unlock offer (Requisition-style) | Set | Set |
| Provider reward through a supported grant action that declares an unlock | Set | Set |
| Trigger a declared `info` reveal through a supported action | Set | — |
| Browse, inspect, quote, cancel, help text, errors, diagnostics, registration, load | — | — |
| Debug "unlock all" (debug page only) | Set | Set, and the section's `debug` flag is set for diagnostics |

There is no relock, and transitions never decrement. A failed or cancelled operation changes nothing (same prepare/commit rule as D6 §10). Each change happens inside its operation's commit, never from an observer.

### 14.5 Identity, offers and renames

- **An entry's saved identity is (owner namespace, owner-assigned stable ordinal u16)**, declared by the provider at registration like a save ID. Seal rejects duplicate ordinals within one owner, and ordinals are never reused. The saved form also keeps a 16-bit hash of the full key **as a guard only**: when the ordinal matches but the hash does not, the provider renumbered by mistake. That entry is then treated as an unknown carried entry: preserved, not applied, and logged. Equality and lookup still use full keys (D6 §11.1).
- **Renames:** an entry may declare up to 4 previous keys it accepts for its ordinal. A matching stored hash is accepted and rewritten at the next save.
- **Merges:** an entry may declare up to 4 retired ordinals it absorbs. Their facts are ORed in and the retired entries are dropped at the next save. Splitting an entry, or moving it to another owner, is not supported in v1; the old state stays carried.
- **Offers share entitlement through the entry they reference.** Two offers (from one or several shops or providers) that unlock the same entry set the same fact. Once it is unlocked, every such offer shows as already owned, in the same grayed one-of-a-kind style as Requisition, and cannot be bought again. Offers may require *Seen* or *Unlocked* of any ready entry they are permitted to reference (D6 §11.4).

### 14.6 Presentation and spoiler rules

- **Not seen, not unlocked and not carried:** the list row shows `????`. Help, quote, price, error and refusal text use generic strings ("Not found yet") and never the entry's name, icon or description. Queries return `UNDISCOVERED` with no metadata. Diagnostics and logs outside debug builds name the ordinal, not the entry.
- **Seen but not unlocked:** name and description shown, marked locked, with how to unlock it if the entry declares that.
- **Provider missing:** stored facts stay as they are. A *Seen* entry shows "unavailable (mod missing)" with the owner namespace only, because names belong to the provider and are not saved. Undiscovered entries of missing providers are not listed.

### 14.7 Capacity

Every registered entry's worst-case bytes are reserved at seal, so a discovery event can never fail at runtime because of space (D3 §13.2). If an owner's entries do not fit, that owner's whole Catalog batch is refused at seal, with an attributable reason (MCR-01 domain rule). Entries carried from missing providers are never dropped. If a loaded save's carried entries leave too little room for the registered reservation, discovery for that playthrough becomes read-only for the owners that do not fit, with a visible notice and a logged reason. Existing facts still display.

### 14.8 API additions to `catalog_entries` v1 (conceptual)

- `register_catalog_entry` gains `ordinal`, `kind` (`effect`/`info`), up to 4 `accepts_previous_keys` and up to 4 `absorbs_ordinals`.
- `query_discovery(entry) → {seen, unlocked, carried, available}`: read-only and discovery-filtered.
- Transitions are not public setters. They are effects declared by supported actions (dismantle, delivery, purchase, reveal), committed by the action's owner through the Catalog.

### 14.9 Versioning obligations for every owner and provider (D3 §15)

- Never rename or reuse a record name, section key, definition/effect/stock key, Catalog ordinal, flag bit or enum value. Use declared renames and absorbs instead.
- Any byte-layout change raises the layout version. Prefer appending fields whose zero value keeps the old behavior, and raise `min_reader` only when older readers would misread the data.
- Ship upgrades as frozen single-step functions (vN → vN+1), each pure and bounded, plus a golden fixture for the new version. Update the D3 §15.6 version table in the same change.
- Content meaning changes raise the definition or attachment revision. Existing items change only through a declared per-instance migration step.
- Interface versions (`PE_MOD_API_VERSION`, capability and descriptor versions) are negotiated in code and never used as save gates.

**Disposition:** MCR-06 is resolved as a recommended design. Implementation waits on the extension store (D3 §12), the content ledger (for *carried* and dismantle) and the Catalog adapter; D4 binds the cases ("MCR-06 acceptance bindings").
