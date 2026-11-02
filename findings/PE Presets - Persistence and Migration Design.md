# D3 — Scoped persistence and migration design

Date: October 30, 2026. Status: recommended design draft, not an implemented format or API. No code, save files, game settings, or balances changed.

Validation companion: [D4 scoped plan/results record](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Validation and Playtest Record.md>), especially SAV/RWD/RAC cases and PB-01–09. First read-only query results are recorded; full policy tests/playtests are unrun and policy/budget approvals remain open.

October 31 implementation note: the first read-only `pe_save_query` unit is implemented on `feat/mod-presets-framework` in `D:/Recomp Games/pe-mod-presets`, based on fetched upstream `8c52cdde5`. D4 records 21 local query cases, writer parity, rebuilt native game, and related existing regressions. This satisfies an inspection subset only: last-load/current-carried provenance, owner load outcomes, capacity/projection/uncertainty reporting. Conditional emission, save refusal, actual policy record, coherent crash capture, and full G2 acceptance remain unimplemented. `fits` is not authorization to save or proof of semantic validity.

Later October 31 update: capacity admission/refusal is also implemented. `pe_save_admission.h` checks the current valid union, stages tail publication, and propagates failure through native serialization/slot startup before file scheduling; over-capacity snapshots are unavailable rather than truncated. D4 records 12 new local admission/host/native-gate cases, final rebuild and 6 existing regressions. The earlier inspection-only note describes the first unit, not the current refusal implementation. Conditional/lazy emission, strict unreadable-policy gating and coherent whole-save crash capture are still outstanding, so G2 is not closed. Existing owner validation/reset, damaged-record recovery and foreign-container passthrough intentionally remain compatible; capacity checks do not reconstruct previously rejected data.

Latest October 31 update: the host conditional-emission prerequisite is implemented in `pe_save_emission.h`, without changing `PeSaveRecord` or the save format. An init-registered dormant record consumes a registry slot but no save header/payload bytes. Explicit owner activation checks initialized state, conservative load provenance and full live-plus-carried capacity before setting a sticky emission bit. Valid loaded records auto-enable; inactive/missing-owner and valid-CRC rejected/newer optional payloads stay preserved. Returning to defaults does not delete progress; New Game or loading an absent record clears activation. Save/load lifecycle callbacks cannot activate records or start nested writes. Existing ordinary registrations/recovery remain compatible. D4 records 25 new cases and reruns, the native rebuild and 6 existing CTests. Earlier notes describe their historical units. **The candidate 160-byte policy layout, actual policy registration, preset behavior and coherent whole-save crash capture remain unimplemented; G2 remains open.**

Read with [D1](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Economy presets and independent reward controls proposal.md>), [D2](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Control Inventory and Menu Map.md>), [D6](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Mod Extensions - API and Cooperation Contract.md>), [review D7](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets and Mod Extensions - Pre-implementation Review.md>), and the [checklist](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets and Menu Organization - Master Checklist.md>).

## 1. Baseline and boundaries

Inspected baseline: clean `feat/localization`, `ae6520fe6`, in `D:/Recomp Games/pe-localization`. Source: [save contract](<D:/Recomp Games/pe-localization/mods/host/pe_save.h>), [packing/load implementation](<D:/Recomp Games/pe-localization/mods/host/pe_save.c>), and existing record declarations in loot, Catalog, Requisition, key items, and bag sorting. Reaudit on the chosen implementation branch.

Initial scope: Economy-first engine/settings/progress and its small contribution API. Preserve `pe_economy.loot` v1's 36-byte layout and existing other records. Do not allocate per-provider records merely to register stateless callbacks/presets. Collection profile ownership remains unchanged. Section 10 adds a candidate custom-instance/effect/shop persistence contract as separately gated follow-up; it does not place third-party identities into the initial policy record. Randomizer plans remain deferred; no external sidecar or expanded save format is silently introduced.

Recommended policies here need review before coding. Explicit host prerequisites below are required to uphold the proposed preservation guarantees; current interfaces do not already provide them.

## 2. Audited byte budget

| Existing record | Payload bytes | Header bytes | Total |
| --- | ---: | ---: | ---: |
| `pe_economy.loot` v1 | 36 | 12 | 48 |
| `pe_economy.catalog` v1 | 312 | 12 | 324 |
| `pe_economy.shop` v1 | 4 | 12 | 16 |
| `pe_qol.keys` v1 | 68 | 12 | 80 |
| `pe_qol.sort` v1 | 24 | 12 | 36 |
| Container header | — | 20 | 20 |
| **Known baseline** | **444** | **80** | **524** |

Physical tail is 880 bytes; 136 bytes are reserved for the compatibility window, leaving **744** container bytes. Baseline leaves **220** bytes. These figures are a source-derived budget, not measurement of arbitrary user saves: inactive/foreign/newer records may consume the remaining space. Registered-count and carried-entry limits also apply (currently 32 and 64 respectively); do not rely on a stale source comment about header size.

Recommended new record: `pe_economy.policy`, version 1, **160-byte payload + 12-byte header**. Baseline plus this record is **696 bytes**, leaving **48 bytes** for any additional carried entries, including their 12-byte headers. That is limited space, not a general extension reserve.

A single aggregate policy/progress record avoids another header and keeps new-engine settings/progress paired. **Draft refinement to D1 §8:** settings and progress are separate logical owned sections in one versioned new record, not two separately registered records. They remain separate from legacy loot state. This refinement requires approval; an actual layout change must bump the record version. Do not register 160 bytes merely because space seems available at startup.

## 3. Recommended fixed layout — candidate, not release ABI

Encode fields explicitly little-endian with fixed offsets, checked ranges, and zero reserved bytes. Do not persist compiler struct padding, pointers, callbacks, translated labels, derived UI generations, or modifier results as base settings. Host record version/size/CRC protect the payload; do not add a redundant unchecked inner format.

| Offset | Size | Meaning |
| ---: | ---: | --- |
| 0 | 1 | Engine: 0 Legacy, 1 Configurable |
| 1 | 1 | Native Junk route: 0 Counter, 1 Items |
| 2 | 2 | Flags: income, bonus item, Super generation, Duper generation, Super redemption, Duper redemption, performance bonus, empty-steal compensation; remaining bits reserved |
| 4 | 2 | Base price percent; initial supported values 75/100/125, not an exposed slider |
| 6 | 2 | Ordinary fixed income |
| 8 | 2 | Boss fixed income |
| 10 | 2 | Payment chance in basis points, 0–10,000 |
| 12 | 2 | Non-bundle item chance, 0–10,000 |
| 14 | 2 | Item guarantee interval; 0 off |
| 16 | 2 | Super chance, 0–10,000 |
| 18 | 2 | Duper chance, 0–10,000; combined configured bundle chances ≤10,000 |
| 20 | 2 | Super redemption value |
| 22 | 2 | Duper redemption value |
| 24 | 2 | Performance-bonus percent |
| 26 | 2 | Empty-steal compensation amount |
| 28 | 1 | Preset key byte length, 0–47 |
| 29 | 1 | New-path algorithm identifier, initially candidate 1 |
| 30 | 2 | Reserved |
| 32 | 48 | ASCII namespaced preset key, null-terminated/padded; empty means user Custom |
| 80 | 4 | Payment RNG state |
| 84 | 4 | Item RNG state (outer roll and existing non-bundle selection under a documented order) |
| 88 | 4 | Bundle RNG state |
| 92 | 2 | New-path dry progress, saturating |
| 94 | 1 | New-path economy-effect selection progress |
| 95 | 1 | New-path permit selection progress |
| 96 | 4 | Fractional income remainder; candidate denominator 100,000,000, see D6 |
| 100 | 4 | Next new-path award sequence; exhaustion rejects new generation rather than wrapping to a reused ID |
| 104 | 16 | Pending bonus-item/effect/permit entry |
| 120 | 16 | Pending bundle entry |
| 136 | 16 | Pending currency entry |
| 152 | 4 | Progress flags: initialized and explicit validity flags; unused bits reserved |
| 156 | 4 | Reserved |

Candidate pending entry: kind u8, origin u8, flags u16, content ID u16, reserved u16, amount u32, sequence u32. Kind 0 means empty. Built-in IDs only; arbitrary third-party content is not supported by this first record. Store the final generated amount/identity, not a callback to recompute it. Income source breakdowns are optional bounded runtime diagnostics, not unlimited saved strings.

Validate null termination, ID/kind combinations, flag dependencies, chance bounds, supported algorithm, remainder range, reserved values, and sequence validity. u16 storage permits at most 65,535 for those amount/interval fields; that is a technical ceiling, not approved UI balance. The wallet and pending amount remain u32 with current 99,999 capacity. Any required larger field, more pending slots, longer key, extension-owned item ID, or changed arithmetic requires rebudgeting/versioning before release.

The existing wallet, legacy difficulty/pity/queue/RNG, shared charm state, and Catalog/permit ownership stay in their current records. New-record zero initialization is not a complete valid configuration; decode/reset builds explicit defaults and a status, not accidental all-off semantics.

## 4. Save admission and provenance: required host work

Current `pe_save_register()` budgets registered records and returns only success/failure. Current packing can omit carried records after live ones fill the container. The new owner alone cannot claim lossless preservation using that API.

Required host contract, exact names pending:

1. Expose load provenance per record/container: absent legacy/vanilla, valid supported, supported upgraded, corrupt, unsupported newer record, unsupported container, and registration failure. Distinguish reset causes before choosing an engine.
2. Preflight the actual union of live replacements plus preserved carried/unknown records, counting headers and entry limits. Replacing the same ID counts once. Check at load, before opt-in, after relevant changes, and immediately before save writing.
3. Refuse an unsaveable new policy **before activation**. Preserve the prior valid state and explain the capacity/dependency problem. Do not register a large default new record that crowds out foreign data even when the player never selects new mode.
4. Support conditional/lazy emission of the new record or an equivalent reviewed strategy. If the player never leaves legacy and no record was loaded, emit no new record. This is a required capability, not present in the current registration struct.
5. A preservation failure at save time must reject the save before replacing the destination, retaining its backup/previous valid image. Merely preserving an old tail alongside newly serialized native state can create an inconsistent snapshot; do not silently do that. The existing void save callback cannot establish save cancellation by itself.

Until those contracts exist and are verified, new saved policy activation is blocked; baseline Legacy remains unchanged. Do not silently fix capacity by deleting other records, compressing unknown data, expanding the container, or moving the compatibility window. A separately reviewed host change is necessary and must preserve no-opt-in behavior except for any explicitly approved general safety fix.

## 5. Load/reset/migration matrix

| Input | Recommended behavior |
| --- | --- |
| Valid legacy blocks/loot v1; genuinely absent policy | Existing upgrade/load behavior; Legacy, no new progress/record, retain legitimate difficulty/custom profile tuning |
| Vanilla save / New Game, no policy | Legacy under existing reset semantics; never inherit previous save's new policy/RNG/pending state |
| Valid policy v1 + valid dependencies | Decode/validate sections, restore matching engine/progress, rebuild transient view/registry state |
| Valid policy whose preset provider is absent | Preserve key and concrete supported settings; show unavailable preset; skip absent stateless contributors; do not auto-select another preset |
| Policy present but corrupt/newer/unsupported | Preserve original carried bytes where supported; block new engine and new economic mutation, surface reason; no guessed reset/reseed or silent legacy switch |
| Policy supported but required wallet/progress dependencies invalid | Block new transactions before item/native mutation; preserve originals, offer reviewed recovery rather than reconstruction from guesses |
| Unsupported container | Do not inject current records or continue new policy under defaults; explicit compatibility refusal for this feature |
| Registration/capacity failure | New mode unavailable, clear reason; no silently session-only economic settings |
| Older game build loads a future new-mode save | No promised behavior unless that build understands compatibility markers; document required minimum build and protect backups |

The host's current reset callbacks do not communicate all these statuses. This matrix is a prerequisite specification, not a guarantee implemented by existing callbacks. Downgrade safety cannot be assured by preserving unknown bytes if older code ignores the new engine and continues awarding legacy rewards; refuse unsupported downgrade in documentation/compatible loaders and do not claim protection from arbitrary old builds.

Full suite/master-mod off still preserves policy/progress bytes under the host contract; no bonus rolls or conversion. New Game explicitly discards per-playthrough new progress according to normal new-run semantics, not collection ownership. Import the legacy coupled master-enable setting only through its existing per-save read path; don't let a global row overwrite loaded new settings.

## 6. Progress, admission, and transitions — recommended policy

Use D2's explicit engine table. Initialize Configurable only once on a successful first opt-in, after capacity preflight. Freeze inactive engine-only progress/RNG; keep shared wallet/charm/ownership singular. Reapplying a preset never resets progress. Never migrate a pending legacy identity through new selection or reinterpret it as a bundle.

Three pending slots are family-specific, so a disabled item does not block an enabled bundle or currency payment. New admissions for a family require its slot to be empty; otherwise freeze that family's roll/progress and display its paused status. Deliver pending entries before attempting new awards, with a fixed documented per-victory policy. Recommended first implementation: a family that started the victory occupied gets delivery only that victory, not delivery plus a second roll. This changes effective frequency under backpressure, so disclose it in playtest results.

For enabled/eligible admitted bonus-item attempts: perform the outer roll or guarantee, select from the eligible non-bundle pool, and create an identity/sequence in the same owner transaction. **Success means committed generation into its durable pending/delivery state**, not merely displaying/collecting it. Reset dry progress only then. Failed admission/no eligible pool does not consume RNG or guarantee progress. A failed random attempt increments dry progress, including documented Lucky Find/charm modifiers. Keep economy/permit sub-guarantees on the new progress fields and preserve pool eligibility semantics; exact skip/order behavior needs a fixture table before coding.

If a pending economy effect becomes unlocked by another legitimate action, settle it as already satisfied with an attributable explanation and no duplicate unlock/currency/reroll. Physical item/bundle entries retain their identity until delivered or an explicit existing discard action handles them; do not infer delivery solely because the player already owns one equivalent item. Whether item-found-screen abandonment retains or explicitly discards a new award must be confirmed with the existing UX; it cannot be silently treated as duplicate collection. These settlement rules require policy approval.

Currency pending stores the final capped-by-contract generated amount, not a recomputable balance delta. Recommended credit is all-or-nothing when space is available. Each source consumed once and each transaction identified within the loaded playthrough. Sequence IDs prevent accidental same-session duplicate requests; restoring an old save legitimately restores its progress and is not global anti-cheat or cross-crash exactly-once delivery.

## 7. New-path RNG and fractional arithmetic

Recommend fixed documented xorshift32 streams (payment/item/bundle), nonzero states, fixed u32 arithmetic, and bounded unbiased range selection; specify test vectors and draw order in D6/D4 before implementation. First successful new-mode opt-in derives three nonzero states from a one-time owner-generated seed without consuming native-game or legacy-loot RNG; persist them before any draw-dependent award. This is reproducible save continuation, not a user-facing Randomizer seed feature. Preview/diagnostics consume no draws. Disabled/backpressured families consume no draws. Separate bundle randomness from item selection.

Persist the income fractional remainder through modifier/equipment/config changes and inactive-engine periods; it is earned sub-unit progress, not a preset-owned reset field. D6's proposed combined arithmetic fixes the denominator at 100,000,000. Do not recompute it from currently equipped effects after loading. If algorithm/arithmetic changes later, provide an explicit progress migration/version rather than interpreting old remainder units under a new denominator. Legacy RNG load/reset/rounding stay exactly as they are.

## 8. Transactions, crash capture, and file writing

Normal saves serialize a coherent generation after owner commits. New reward generation couples pending identity, RNG/progress, and wallet/unlocks; redemption couples native source consumption and full credit. Settings commit is separate from later conversion. No file I/O or mod callbacks occur in the critical mutation phase.

**A mod-tail snapshot alone cannot repair interrupted native inventory mutation.** If a crash report captures current native bytes and a previous mod tail, either half of a bundle/payment may be replayed or lost. Required before claiming crash-safe new transactions: a host/recovery design capable of choosing one coherent **native-save payload plus mod tail** generation, not separately mixing them.

Recommended mechanism for design review: publish a bounded complete last-committed recoverable save image at a safe game-thread serialization point; retain a valid previous image while preparing the next. Crash handling selects a fully published immutable generation with no allocation, locks, mod callbacks, or worker waits. It may be stale but coherent; label its capture time/generation. Exact atomic publication, buffer retirement, crash context, native serialization side effects, and maximum staleness need engine audit before this is an implemented guarantee. Do not promise a fresh full snapshot after every frame or every callback. If unsupported, block release of newly claimed crash-atomic operations or narrow the guarantee explicitly with user review.

Likewise, audit the actual native save file writer for staging/flush/replace/backup and errors. INI's staged write does not prove memory-card saves are atomic. A failed write must leave the last valid destination recoverable. D3 does not propose implementing a general database or rolling back arbitrary callbacks.

## 9. Decisions and evidence required

Candidate approvals: combined 160-byte record; D2 storage/price/redemption policies; three-slot backpressure and generation-success semantics; redundant unlock settlement; algorithm/draw order/remainder; host admission/status/conditional emission/save refusal; coherent whole-save crash capture design. Missing host capabilities remain blockers, not TODOs to bypass.

D4 must include byte-budget synthetic cases with unknown/newer records, registration errors, legacy conversions, corrupt dependency states, every engine transition, guarantee/bundle backlog, cap/full inventory, repeated preview/Apply, save-switch/New Game, interruptions at every transaction/publication phase, and write failure. Keep fixtures/tools local in `D:/Recomp Games/pe-native-debug`. No tests or simulations ran for this document.

REV-01–06, 08–09 now have concrete candidate contracts, but remain open until these choices and host prerequisites are accepted and validated. This document is not a claim that arbitrary mods or old game builds can safely load every future save.

## 10. Custom instances, installed effects and contributed shop state

October 31 documentation extension for D1 §20 / D2 §9 / D6 §10. **Candidate logical contract, no selected byte layout or new record registration.** Existing host query/admission/emission evidence does not demonstrate storage or safe execution of custom equipment. Bind PB-10–14 in D4 before implementation.

Review disposition: D6 §11 resolves MCR-01–03 as recommended registration/ownership/dependency contracts. In particular, provider attachments have independent owner/schema keys and cannot overwrite foreign payloads, and optional Shop capacity is separate from Content. Later October 31: §11 resolves MCR-04 (ledger encoding, capacity profiles, single admission authority) and the saved-state side of MCR-10 (compatibility states, outer load gate); D6 §12 resolves MCR-05 (native mapping authority) and names the content core as the minimum reader. §12 specifies that storage expansion (MCR-04X): a linked companion file per save in a hidden `.pe-ext` folder beside the card, with per-owner sections and a 5 KiB v1 profile; §13 encodes MCR-06 discovery (`pe_economy.discovery`, 1,024 bytes); the 744-byte tail closes to new records after the policy record and a 32-byte link. Persistent custom instances wait on implementing §§11–12. MCR-07–09, 11 and 12 remain open, including stock semantics and quote/commit/tokens. D0 Section 5 M and D7 track dispositions; registry quotas are not a persistent-state budget and save-host passes do not close those gaps.

### Ownership and data separation

Definitions live in installed providers, not copied wholesale into every save. Inventory/equipment owners store logical instances, effect attachments and equipped references; Economy owns stock/purchase coordination; providers own bounded versioned opaque extension payloads. The persistence owner assembles one coherent committed generation. Do not put custom IDs in the candidate 16-bit built-in pending identity or expand `pe_economy.policy` v1 by reinterpretation. Custom reward delivery needs a separately versioned adapter.

| Logical saved entity | Required meaning, subject to concrete schema review |
| --- | --- |
| Content reference | Full stable namespaced ID, content kind and the schema/compatibility revision needed to interpret state; never session handle/native slot |
| Inventory instance | Per-save stable instance ID, content reference, logical location, quantity and validated common mutable fields; weapons/armor retain upgrades, ammunition/charges and provenance as applicable |
| Effect attachment | Owning instance ID, stable effect ID, versioned bounded parameters/payload, occupied slot/cost and built-in versus removable provenance |
| Equipped reference | Reference to an existing compatible instance, with runtime resolution distinct from persisted ownership |
| Provider extension | Explicit schema version and length framing for opaque bytes; owner attribution, configured byte ceiling and validated attachment to the owning entity |
| Shop stock | Stable provider/offer/shop identities and declared stock scope; save remaining/claimed state only when gameplay requires it, not for infinite stock |
| Committed operation metadata | Bounded playthrough-local duplicate detection/sequence or equivalent accepted design, paired with the corresponding item/effect, wallet and stock generation |
| Recovery state, if supported | Original equipped identity plus any deliberately persisted fallback/recovery choice; not a replacement copy that can duplicate the original |

Content identity is distinct from instance identity and offer identity: two copies of a gun may differ, and two offers for the same gun need not share stock. Define instance creation, splitting/merging, transfer and ID exhaustion without reusing live IDs or rolling back foreign references. Full ID encoding, field widths, dictionaries, lengths and checksums are deliberately unassigned until capacity is accepted; if a compact dictionary is chosen, preserve its mapping and unknown entries. Hash-only identity without collision handling is insufficient.

Preserve original meanings of existing native effects and equipment upgrades through reviewed adapters. Never interpret unknown saved IDs as native indices, execute opaque effect bytes, serialize pointers/padding, or recompute an instance from current defaults. Bound parsing depth/counts/lengths and validate references, quantity/class ranges, duplicate instance IDs, attachment ownership, slots and arithmetic before runtime publication. Providers may validate their own schema at a safe load boundary; unknown framing must not be guessed.

### Capacity and version gates

Current known record budget remains 524 of 744 bytes, or 696 with the candidate policy record. Include all live/carried unknown records, headers, saved identities/instance payloads and stock/metadata in an actual worst-case budget. No per-provider record is justified merely by registering static definitions. No new record when no meaningful custom state exists; once used/loaded, conditional retention is sticky and cannot be cleared merely because a shop closes or a provider disappears.

Before acquisition or any operation that grows state, project the complete committed result, not just the new item's payload. Reserve/revalidate supported instance, inventory, stock and save capacity before irreversible mutation. This needs an owner-managed transaction design: `pe_save_enable_record` checks current declared records and is not a dynamic storage reservation or serializer for arbitrary instance growth. Adding a fixed record later requires reviewed registration/init and projected capacity behavior. Reject unsupported acquisitions without charge, item consumption, stock reduction or partial state.

If accepted instance counts/payloads do not fit, stop at the design gate. A separate versioned expandable-container proposal must specify actual native file boundaries/checksums, reader detection, staging/publication, backup/recovery, crash consistency, portability, editor/export support and maximum sizes. Neither silent truncation nor an unreviewed appended region/sidecar is allowed. Separate container, shared instance, provider payload and API versions. First-slice 160-byte policy semantics stay unchanged.

### Load and missing-mod matrix

| Input / condition | Required result |
| --- | --- |
| Old vanilla/current mod save with no custom state | Existing load behavior and native ownership preserved; no invented instances or custom records |
| Resolved supported instance/effects | Validate and restore exactly once, including upgrades/slots/provenance; no repeated bonuses or migrations |
| Missing/disabled definition/provider | Preserve instance and framed payload in place; visible unavailable placeholder, no unsafe actions or unrelated native substitution |
| Missing effect on otherwise native/resolved gear | Keep attachment, occupied slot and opaque state; no effect execution, overwrite or implicit removal. Equipment usability requires the accepted safety classification |
| Missing icon/name asset only | Generic presentation fallback and bounded help; do not erase valid gameplay content |
| Newer schema, rejected payload or failed migration | Retain original framed data and mark unavailable; do not write reset defaults over it. Never call provider code against unsupported payloads |
| Structurally corrupt/unframeable data | Refuse the unsafe load/migration or use an explicit reviewed recovery path. Byte-level preservation claims are limited by framing; existing parser-discarded bytes are not recovered automatically |
| Compatible provider reinstalled | Resolve retained data once with no grant, charge, reroll or stock reset |
| Required progression/coordinator dependency missing | Refuse resume with an attributable recovery explanation; no partial plan activation |

Candidate initial placeholder capacity policy matches D2: retain original logical slots/counts and disable transfer/destructive actions while unresolved. No implicit free quarantine. If safe native representation cannot retain them, refuse continuation until compatible dependencies or a reviewed bounded quarantine adapter are available. Block combine/sell/consume/install-over/remove/Dismantle/Rebuild when they would discard unknown data. Deletion/conversion is a separate explicit backed-up recovery operation, not load fallback.

For missing equipped behavior, default to refusal until safe inactive-effect or temporary-native-fallback support is validated for the class. A runtime fallback must preserve the original logical instance separately, cannot appear as an extra owned/sellable item, and cannot overwrite it when saving. If saving/resuming with fallback is supported, encode that recovery state explicitly; otherwise refuse saving/resume as applicable with a clear message. Compatible reinstall must respect later legitimate equipment choices rather than forcibly re-equipping the old instance. Missing required gameplay behavior cannot be treated as a mere missing icon.

### Purchase/installation commit and save boundary

Candidate state machine: `QUOTE → PREPARED → COMMITTED` or `ABORTED`. Quotes/reservations are transient and never serialize as completed ownership. Preparation validates/reserves all required owner resources without visible payment, stock decrement or grants; abort releases every reservation. Final commit rechecks generations and publishes inventory/effects, wallet and stock as one coherent operation. Owners must provide guaranteed commit after preparation or a separately reviewed mechanism; arbitrary failure-prone grant callbacks cannot satisfy this contract.

Save capture occurs outside active commits using a complete committed generation. Crash capture uses a complete published image under §8; the current mod-tail snapshot alone is not that guarantee. Whole file writing must preserve a valid old or new generation under supported failures. Until this is implemented and verified, no claim of crash-safe new purchases/services is permitted. Unsupported partial commit must not be hidden with an unbounded pending queue. If a durable transaction journal is necessary, separately design its bounded identity, replay and recovery before release.

Define stock scope per offer (per-save initially recommended); profile/global stock requires separate cross-save atomicity. Missing providers cannot reset saved stock/one-time claims. Quantity purchases and effect services use the same operation boundary; consumption, target slots, installed state and provenance must agree. Refund/removal/salvage policy remains unchanged unless explicitly reviewed. Duplicate prevention is scoped to loaded playthrough/committed state, not a promise that restoring an old save cannot repeat history.

### Migrations, tools and open approvals

Migrations stage validated replacements with originals preserved until successful coherent publication; repeated load/retry cannot duplicate instances, multiply stats, free unknown slots or reissue one-time purchases. Content renames require versioned aliases with collision/cycle checks. Provider data revision alone does not reset owned instances; actual schema/meaning changes need migration. Unknown providers/effects remain opaque through supported save/editor round trips without installed code. Older builds/readers are supported only by an explicit reader matrix; unknown-byte preservation is not permission to play or semantically edit unknown data.

Before implementation approve ID encoding, archetypes and mutable fields, instance/attachment limits, provider payload ceilings, stock scope, equipped safety classes, capacity/container choice, migrations, save-editor boundaries and guaranteed purchase prepare/commit/publication. D4 §15 contains planned cases; none has executed for this extension. No code, records, user saves, balances or runtime settings changed for this addition.

## 11. Content ledger encoding, capacity envelope and compatibility states — MCR-04/MCR-10 disposition

October 31 recommended design decision, documentation only. This section selects the persistent encoding and capacity rules for custom **equipment instances and their attachments**, and the saved representation in every compatibility state. The native mapping authority it relies on is D6 §12 (MCR-05); the minimum reader component and its API boundary are D6 §12.6. Discovery/entitlement (MCR-06), stock (MCR-07) and operation metadata (MCR-09) are **not** encoded here; they receive their own sub-budgets in the same storage decision, not space borrowed from this ledger. No code, record registration, save file or balance changed.

**Result in one line:** the selected encoding's smallest useful profile does not fit beside the candidate policy record in the existing 744-byte container, so persistent custom instances (slice E) stop at a separately reviewed storage-expansion gate (§11.4). The encoding, accounting and compatibility rules below are independent of where the bytes finally live and carry over to that container unchanged.

### 11.1 Saved representation: native-complete records plus one shared ledger

Evidence, read from `feat/mod-presets-framework` (`D:/Recomp Games/pe-mod-presets`, base `8c52cdde5`; native sources unmodified in that worktree): equipment lives in a fixed pool of 128 `ItemDataRecord`s (`InventoryRuntime.equipment`, 0x20 bytes each), which the native save stores whole inside `SaveRuntimeState.inventory` (0x1064 bytes at offset 0x68). Bag and storage slots hold only 16-bit values (0x100 + pool index for equipment). There is no spare per-record field: `reserved02[2]`, the only field named reserved, holds the item's own 16-bit number in every one of the 255 base records on both US discs (item 1 = `01 00`, item 2 = `02 00` …), and new pool records are copied from those base records. The save editor round-trips it but zeroes it for records it creates (`save-editor/src/save/equipment.rs`). It is therefore not available for tagging.

Decisions:

1. **Native-complete rule.** A persistent custom weapon or armor is always a complete, valid native pool record: a native archetype base item number, native kind, and stats/ammo/mod codes within native ranges. The native record alone is a playable item for any reader. Custom identity, presentation and extra behavior are additive and dormant when unavailable. Content definitions that cannot satisfy this are not persistent equipment in v1 (D6 content descriptor "native-compatible archetype" becomes mandatory for this class).
2. **No separate fallback copy.** The native record *is* the fallback. The ledger never stores a second item, so no state can show an extra owned/sellable copy (D3 §10 duplication rule satisfied structurally).
3. **One shared ledger record**, `pe_content.ledger` v1, owned by the content core (D6 §12.6), not by any provider. No per-provider or per-definition records. Conditional emission (§4 host capability, implemented on the reference branch): dormant until the first custom instance is committed in a playthrough; sticky after that, including when providers are missing; cleared only by New Game or loading a save without it.
4. **Classes in scope:** equipment records only (D6 §12.2). Slot-value consumables, ammo pools/special records and key items carry no per-instance native record and get no ledger entries in v1.

### 11.2 Ledger v1 encoding (little-endian, fixed widths)

| Part | Bytes | Fields |
| --- | ---: | --- |
| Host record header | 12 | Existing host framing (ID, version, size, CRC) |
| Section header | 16 | format u8 (1); flags u8; `min_reader` u16 (lowest content-core reader revision allowed to **mutate** this ledger); `dict_count` u8; `instance_count` u8; `attach_count` u8; reserved u8 (0); `next_instance_id` u32; `native_stamp` u32 |
| Dictionary entry ×`dict_count` | 4 + key length (≤ 51) | kind u8 (definition / attachment owner-schema); key length u8 (1–47); revision u16; canonical key bytes (D6 §11.1 rules, no terminator) |
| Instance entry ×`instance_count` | 12 | `instance_id` u32; dictionary index u8; pool index u8 (0–127); state u8 (§11.5); flags u8; `fingerprint` u32 |
| Attachment frame ×`attach_count` | 5 + payload (payload ≤ 32 in v1) | instance index u8; owner/schema dictionary index u8; schema version u16; payload length u8; opaque payload |

- `fingerprint` = CRC-32 over the native identity fields no supported native path mutates: item number (`reserved02`), `itemId`, `kind`, `tailCapacity`, `baseStats[3]`. Mutable fields (ammo, reserve ammo, `bonusStats`, `flags`, mod tail) are excluded. D6 §12.4 lists the audit that must confirm this field set before implementation.
- `native_stamp` = CRC-32 over the identity fields plus `iconId` of all 128 pool records, written by a ledger-aware writer at every save. A mismatch at load means something other than a ledger-aware build changed the pool since the ledger was written (§11.5).
- `instance_id` is per save, monotonic, never reused, never 0. Exhaustion of u32 refuses new instances; it never wraps.
- Ordering: dictionary entries and instances are written in ascending key and `instance_id` order, so identical state serializes identically. Duplicate instance IDs, duplicate pool indices, out-of-range indices or counts, or frames referencing a missing instance make the record structurally invalid (§11.5 row "structurally invalid").
- Attachment payloads are opaque framed bytes owned by their owner/schema key (D6 §11.4). The core validates framing and the 32-byte v1 ceiling only; never payload meaning.

### 11.3 Capacity accounting and admission authority

Budget arithmetic uses **declared maxima, not typical sizes**: a dictionary entry costs 51 bytes unless its actual key is known (an existing entry being reused). Every projection counts the whole container: live records, carried unknown/newer/inactive records, this ledger after the change, and every outstanding reservation.

**Single admission authority.** The content core owns the only ledger capacity account. Any operation that can grow the ledger (acquisition, rebuild of a custom item, a new attachment) must obtain a reservation for its worst-case growth (new dictionary entries + one instance entry per created instance + declared attachment frames) before preparation completes (D6 §10 prepare). Reservations are released on abort/cancel/restart. Two staged operations cannot both rely on the same free bytes. A refused reservation is an ordinary prepare failure with reason `CAPACITY`: no charge, consumption, stock change or partial item (D3 §10 commit rule).

**Lower limits in a newer build.** A build whose profile is smaller than the ledger it loads keeps the whole ledger and resolves entries it can, but refuses any growth while over its profile. It never truncates, compacts or drops entries to fit.

**Supported profiles (technical, not balance):**

| Profile | Contents | Worst-case bytes incl. 12-byte host header |
| --- | --- | ---: |
| P0 — smallest useful | 2 definitions, 4 instances, no attachments | 12 + 16 + 2×51 + 4×12 = **178** |
| P1 — recommended minimum supported | 8 definitions + 4 attachment owner/schema keys, 32 instances, 16 attachments × 16-byte payload | 12 + 16 + 12×51 + 32×12 + 16×21 = **1,360** |

Available in the existing container (§2): 744 bytes; known baseline 524, leaving **220**; with the candidate 160-byte policy record, **48**. P0 fits the bare baseline (42 bytes left for everything else) and does not fit beside the policy record. P1 fits neither. MCR-06/07/09 state is not yet counted in either figure.

### 11.4 Decision: the existing container is not the home for custom instances

The supported minimum is defined as **P1**. It cannot fit, and even P0 would make custom content and the Economy policy record mutually exclusive per save, decided only by which one a save happened to activate first. That is not an acceptable product rule. Per §10 and the MCR-04 recommendation, **persistent custom instances stop at a separately reviewed storage-expansion proposal (D0 Section 5 M, MCR-04X)**. Not permitted meanwhile: shipping P0 inside the 744 bytes as a hidden limit, truncating unknown records, compressing them, moving the compatibility window, or an unreviewed sidecar file. The reviewed proposal is §12.

Requirements the expansion proposal must meet (its own review; listed here so the ledger design does not depend on its choices):

- Room for P1 plus separately declared MCR-06/07/09 sub-budgets, with headroom stated per section rather than one shared pool. Starting estimate for review: ≥ 4 KiB, of which ≤ 2 KiB for this ledger.
- Detection by readers that understand it; vanilla and older builds keep loading the native save unchanged (native-complete records make that safe; the ledger is simply absent for them, §11.5).
- One coherent generation: the native save, the mod tail and the expansion are published together or not at all (§8); a failed write leaves the previous valid generation recoverable.
- Checksums, maximum sizes, editor/export/import support and portability of card files between machines.
- The ledger encoding in §11.2 moves into it unchanged; only the host framing differs.

Until that proposal is accepted and implemented: definition-only registries (D6 §11), native-alias presentation that saves nothing, and non-persistent experiments remain possible; granting persistent custom equipment does not.

### 11.5 Saved representation in every compatibility state (MCR-10)

Entry states (instance entry `state` byte): **ACTIVE** (resolved and matched), **UNAVAILABLE** (definition/provider/schema missing or beyond this build's limits; native record intact), **UNCERTAIN** (native pool changed by a non-ledger-aware writer and the fingerprint still matches; identity not provable), **ORPHANED** (native anchor gone or changed; the entry and its attachments are kept for diagnostics and recovery only). The minimum compatible reader is the content core of D6 §12.6.

| Condition | Native half | Ledger | Supported behavior |
| --- | --- | --- | --- |
| All providers present, core present | Unchanged | ACTIVE entries | Full behavior |
| One provider off or missing | Unchanged; record plays as its archetype | Entries UNAVAILABLE; attachments retained | Use, equip, move, sort and store allowed as the native archetype; custom extras dormant. Destructive actions refused while UNAVAILABLE: discard, sell, Wayne merge/tune-up as a source, dismantle, rebuild over it (D6 §12.5). Compatible reinstall returns entries to ACTIVE once, with no grant or reroll |
| Economy off | Unchanged | Unaffected | Instances behave as above with their providers; shop and stock state dormant (MCR-07) |
| All mods off (Manage mods) | Unchanged | Preserved by the host | The content core still runs as host-level preservation, like the existing save host: entries UNAVAILABLE, the same destructive-action refusals. This is a stated exception to "plays as the original" and needs approval with this disposition |
| Core absent: vanilla build (`PE_MODS` off) | Saved normally | Lost at the next save (vanilla writes no mod tail) | One-way: instances become plain native items permanently. Cannot be refused from inside a vanilla build; documented, with backups recommended before playing a custom-content save in one |
| Older mod build without a content core, or with a lower core revision | May be mutated without hooks | Carried as an unknown record | On the next load in a supporting build, `native_stamp` mismatch triggers reconciliation: fingerprint match makes an entry UNCERTAIN; mismatch or freed record makes it ORPHANED. Never reattached to another record, never regranted. UNCERTAIN leaves only through an explicit, backed-up repair action |
| Save edited by the save editor | Native records edited | Preserved if the editor keeps the tail | Same reconciliation as the row above. Editor support for showing ledger entries is follow-up work |
| Ledger valid but larger than this build's profile | Unchanged | Kept whole | Entries beyond the profile UNAVAILABLE; growth refused; nothing dropped |
| Ledger `format` newer than this core, or `min_reader` above it | Unchanged | Unparsed but preserved | **Outer load gate refuses continuing that save in this build**, with an attributable message; the original file is untouched. The core cannot safely enforce refusals for records it cannot identify |
| Structurally invalid ledger | Unchanged | Preserved as carried bytes | Same outer load gate refusal; an explicit reviewed recovery may later drop the ledger and leave plain native items |

The vanilla and older-build rows are the limit of the compatibility promise: an older build can neither be made to understand the ledger nor be stopped from writing native changes. Safety comes from native-complete records (nothing unplayable is ever saved) and from reconciliation that only ever demotes identity, never invents it. Arbitrary old builds and corrupt data are not claimed safe beyond that.

### 11.6 Acceptance and remaining work

Bind D4 §15 CNT-01/05/06/07/10/11 and RES-01/02 to §§11.2–11.5 (D4 records the bindings; none has run). Before implementation: approve the native-complete rule, the 32-byte attachment ceiling, the P1 profile, the All-mods-off exception and the outer load gate; write and review the storage-expansion proposal (MCR-04X); complete the D6 §12.4 native audit items. MCR-06/07/09 must state their own sub-budgets inside the expansion proposal. **Disposition: MCR-04 and MCR-10 are resolved as recommended design rules here. Persistent custom instances remain blocked on MCR-04X; implementation and validation remain unchecked.**

**Decisions recorded October 31** (the user asked for the most stable, modular and scalable choice and delegated these): the native-complete rule, the 32-byte v1 attachment ceiling, P1 as the supported minimum, the All-mods-off exception (the content core keeps preserving and protecting custom items with all mods off; it adds no gameplay) and the outer load gate are adopted as written. The storage expansion is specified in §12.

## 12. Save extension store — MCR-04X proposal

October 31 recommended design, documentation only. It gives persistent mod state more room than the 744-byte tail without changing the native save, the 8 KiB card file, the card slot count or anything a vanilla build reads. No code, save or card file changed.

### 12.1 Evidence that constrains the choice

Read from `feat/mod-presets-framework` (`D:/Recomp Games/pe-mod-presets`, base `8c52cdde5`):

- **Each save is one 8,192-byte card file** (`bu00:BASLUS-00662000000%c%c`, `src/main/memcard/save_flow.c:32`), mapped under `<preferences>/memory-cards/bu00|bu10/` by `Host_CardPath` (`src/main/boot/main.c:620`). The legacy importer accepts only regular files of exactly 8,192 bytes named `BASLUS-00662…` (D-v0.7 handoff §4.3). The mod tail starts at 0x1C90 (`mods/host/pe_save.h:51`).
- **The game counts every listed card file as a used block** (`save_flow.c:821–849`: the scan of `bu00:*` marks each file, then makes that many of the 15 slots unavailable). Any extra card file per save therefore costs the player a save slot and shows as a foreign file.
- **Card listing skips directories and names starting with `.`** on every PsyZ platform: Windows `plat_win.c:113–116`, Unix `plat_unix.c:50–55`, PSP `psp_file.c:68–72`.
- **Native saves already publish by temp file and rename**: `MemCard_BeginWrite`/`MemCard_CommitWrite` (`save_flow.c:55–91`) write `.pe-save-<port>-<ticks>.tmp` beside the target, flush, close and rename; a clear-data save under a different name retires the previous name only after the new file is published.

### 12.2 Options considered

| Option | Result |
| --- | --- |
| Grow the save to a 2-block (16 KiB) card file | Rejected: fails the 8,192-byte import rule, card-image export, editor and every older reader; changes the native file |
| A second card file per save | Rejected: the game counts it as a used block (15 slots become 7 usable saves) and lists it as foreign data |
| Reclaim bytes inside the native save or the 136-byte compatibility window | Rejected: no native bytes are proven unused; the window protects older saves (D3 §2) |
| Compress the tail | Rejected: worst case is not bounded; unknown carried records cannot be recompressed safely |
| **Companion file in a hidden folder beside the card, linked from the tail** | **Selected** (§12.3): invisible to card listing, does not touch the native file, published by the same temp-and-rename pattern |

### 12.3 Layout

**Location.** `<card directory>/.pe-ext/<card file name>.<generation as 8 hex digits>.pex`, for example `memory-cards/bu00/.pe-ext/BASLUS-006620000000A.0000002A.pex`. The path derives only from the card's own mapped path; no user or save data chooses it. Name characters are validated to `[A-Za-z0-9-]` before use.

**Link record in the tail.** `pe_host.extlink` v1, owned by the save host: 12-byte header + 20-byte payload = **32 bytes** — format u8 (1), flags u8 (bit 0 *required*: the extension holds state a reader must not continue without), reserved u16 (0), generation u32, file size u32, file CRC-32 u32, section count u8, reserved 3 bytes (0). It is conditionally emitted (host capability, D3 §4): absent until some extension section holds data, so saves without extension state stay byte-identical to today (D4 CNT-01). Tail budget with it: baseline 524 + policy 172 + link 32 = **728 of 744**. **The 744-byte tail is closed to new records after the policy record and this link;** all future persistent mod state goes into extension sections.

**File format** (little-endian):

| Part | Bytes | Fields |
| --- | ---: | --- |
| File header | 32 | magic `PEX1`; format u16 (1); header size u16; generation u32; total size u32; section count u16; writer revision u16 (§15.2); card file name 12 bytes (the slot part, zero-padded); header CRC-32 u32 |
| Section directory entry × count | 16 | owner/section key hash u32; offset u32; length u32; section CRC-32 u32 |
| Section key table | variable | per section: key length u8 + canonical key (D6 §11.1 rules, ≤ 47) + version u16 + `min_reader` u16 |
| Section payloads | variable | owner-encoded bytes, each bounded by its declared maximum |

A section is valid only if the file's generation and CRC match the link record and its own CRC matches. One damaged section affects only its owner; the others still load (independent framing, same rule as tail records). Unknown sections from providers or newer builds are carried forward byte-for-byte within the file profile, exactly like carried tail records.

**Profile v1 (technical, reviewable):**

| Section | Owner | Max bytes |
| --- | --- | ---: |
| `pe_content.ledger` | content core (D3 §11, D6 §12.6) | 2,048 (P1 = 1,348 without the tail header) |
| Discovery / entitlement | MCR-06: `pe_economy.discovery` (§13) | 1,024 (raised from 512 by §13.2) |
| Stock / claims | MCR-07 owner, when designed | 512 |
| Operation results | MCR-09 owner, when designed | 256 |
| Unassigned and carried unknown sections | host | 1,152 |
| File header + directory + key table for 16 sections | host | ≤ 128 |
| **File maximum v1** | | **5,120** (4,096 before §13.2) |

The format allows up to 64 sections and 64 KiB; the profile is the enforced limit and can grow in a later build without a format change. A build with a smaller profile than a loaded file keeps the whole file and refuses growth, the same rule as §11.3.

### 12.4 Write and load

**Write (one coherent generation):**

1. Build every section in memory; check each against its maximum and the file maximum. Any failure refuses the whole save before anything is written (existing admission path, D3 §4).
2. Write the next generation's file to `.pe-ext/.tmp-<port>-<ticks>`, flush, close and rename it to its generation name. The previous generation stays.
3. Write the card file through the existing temp-and-rename path, with a link naming the new generation. **The card rename is the commit point.**
4. After the card is published, remove extension generations for this card name older than the previous one, and the generations of a retired card name (clear-data rename, `save_flow.c:84–88`).

A failure or crash before step 3 leaves the old card linked to a generation that still exists. A failure after step 3 only leaves extra files for the next save to clean up. The card's own crash coherence (D3 §8) is unchanged. Generation = the previous link's generation + 1 (1 for a save with no link); it never wraps (u32 exhaustion refuses the save).

**Load:** read the card; if there is no link, there is no extension. With a link: open only the named generation; check its size against the link and the maximum before reading; then check the CRC, generation and card name. On a match, sections are offered to their owners before the first field frame, as tail records are now.

**Link present but file missing or mismatched** (only the card was copied, or the folder was lost):

- Link without the *required* flag: load with those sections absent and owners at defaults. The next save drops the link (one-way, logged).
- Link with *required* (the ledger holds instances): the outer load gate (D3 §11.5) explains that the save's extension file is missing and asks **Continue without mod data? / Back** (default Back). Continue loads the native save (custom items become plain native items, already playable); the original card file and any extension files stay untouched until the player saves. Back leaves everything unchanged.

### 12.5 Tools, import and portability

- **Copying** a card folder (`bu00`) copies `.pe-ext` with it; on Windows a leading dot does not hide a folder. Players moving saves are told to copy the folder, not single files.
- **Legacy importer** (8,192-byte files only) does not carry extensions. Saves made before this feature have none, so nothing is lost for them. A later explicit import action (D-v0.7 §4.5) should copy matching `.pe-ext` generations too.
- **Save editor:** must open the linked generation beside a card file, keep the link valid when it rewrites the card (either by rewriting the extension with the next generation or by keeping both untouched), and offer a bundle export (card file + extension) because `.mcs`/`.srm`/card images cannot hold it. Until the editor supports this, an editor write that drops or breaks the link is handled by §12.4 (required → gate).
- **Crash report:** `pe_save_crash_tail` gains a companion dump of the extension sections as they would be saved, beside the tail it already writes.
- **Vanilla build:** never writes the link; the ledger is lost at its next save (§11.5, unchanged). Extension files are left orphaned and cleaned up by the next supporting save to that card name.

### 12.6 Host service boundary (modular)

The store is a save-host service (`pe_save_ext`, name illustrative) beside the record registry, not part of any mod. Owners register a section with a key, version, `min_reader` and maximum size at init, the same lifecycle as tail records (dormant until activated, sticky, cleared by New Game or loading a save without it). The host owns paths, generations, CRCs, the link record, cleanup and admission; owners see only `read(section bytes)` and `write(buffer, max)`. Within a section, the owner keeps its own admission authority (for the ledger, D3 §11.3 reservations). Host prerequisites, not existing support: the mapped card path for the file being saved (via `Host_CardPath`), a directory create/list/remove hook through SDL, and the extension write step inside the native write sequence before the card rename.

### 12.7 Disposition

MCR-04X is resolved as a recommended design. Granting persistent custom equipment (slice E) needs this store and the content core implemented and validated; D4 §15 binds the cases ("MCR-04X acceptance bindings"). MCR-06/07/09 must use their sections here and stay inside the stated maxima, or propose a profile change.

## 13. Discovery section encoding — MCR-06

October 31 recommended design, documentation only. The contract (owner, facts, transitions, identities, spoiler rules) is D6 §14. Native effect unlocks stay in `pe_economy.catalog` v1 in the tail, unchanged.

### 13.1 Section `pe_economy.discovery` v1 (little-endian; extension store, D3 §12)

| Part | Bytes | Fields |
| --- | ---: | --- |
| Section header | 4 | format u8 (1); flags u8 (bit 0 `debug`: a debug unlock was used); `group_count` u8; reserved u8 (0) |
| Owner group × `group_count` | 2 + namespace | namespace length u8 (1–46); namespace bytes; `entry_count` u8 |
| Entry × `entry_count` | 5 | ordinal u16; key guard u16 (low 16 bits of CRC-32 of the full canonical key); facts u8 (bit 0 Seen, bit 1 Unlocked; bits 2–7 reserved) |

- **Sparse:** only entries with at least one fact are written. Groups are ordered by namespace bytes and entries by ordinal, so equal state serializes identically.
- **Invalid structure:** duplicate namespace or ordinal, a count beyond the section, bad length or the Unlocked bit without Seen. The owner then receives a *damaged* status: bytes kept, custom discovery shown as nothing new, new transitions refused for that playthrough with a notice, and nothing rewritten until a reviewed reset.
- **Reserved fact bits** set by a newer build are preserved; the known bits still apply.
- **Unknown namespaces** (missing providers) and guard mismatches stay as carried entries, written back unchanged.

### 13.2 Capacity

Reservation per ready owner at seal = 2 + namespace length + 5 × that owner's registered entries. Total = 4 + all reservations + carried unknown groups' actual bytes. Every registered entry is covered whether or not it has been seen, so runtime transitions cannot run out of space (D6 §14.7).

The section maximum is raised to **1,024 bytes**, so the D6 §11 starting registry profile of 128 Catalog entries fits: for example 16 owners with 20-byte namespaces = 16 × 22 + 128 × 5 + 4 = 996 bytes. The extension file profile v1 becomes **5,120 bytes**:

| Section | Max bytes |
| --- | ---: |
| `pe_content.ledger` | 2,048 |
| `pe_economy.discovery` | 1,024 |
| Stock / claims (MCR-07) | 512 |
| Operation results (MCR-09) | 256 |
| Unassigned and carried unknown sections | 1,152 |
| Header + directory + key table | ≤ 128 |
| **File maximum v1** | **5,120** |

This supersedes the 4,096-byte figure in §12.3; the format limits (64 sections, 64 KiB) are unchanged. The tail is untouched.

### 13.3 Lifecycle

Dormant until the first custom fact is set in a playthrough; then sticky (D6 §13). New Game clears it, matching the native Catalog record. Loading a save without the section clears it. Rename acceptance and absorbed ordinals are applied in memory at load and written in canonical form at the next save. A save made in a build without the provider or Economy carries the section unchanged.

## 14. Turning mods on and off: layers, save safety and recovery

October 31 recommended design, documentation only, written at the user's request after reviewing how §§11–13 behave when players and testers change which mods are on. No code changed.

### 14.1 Three layers and build order

| Layer | Contents | Depends on | Useful without custom content? |
| --- | --- | --- | --- |
| **S — Save safety and extension store** (mod-independent) | Extension store (§12); outer load gate for any unreadable mod data (§11.5 rows, generalized); missing-mod load notice (§14.3); save-slot warning (§14.4); crash-report and editor support (§12.5); tester guidance (§14.6) | Existing save host and `pe_save_query` | **Yes**: protects today's records (loot, Catalog, keys, sort, policy) |
| **C — Content core** (mod-independent) | Ledger (§11), native veto hooks and reconciliation (D6 §12), `inventory_actions`, Custom items page and Convert (§14.5) | S | Only when a save has custom items |
| **M — Mod-owned features** | Catalog discovery (§13), shop stock/quotes/tokens (MCR-07–09), effect and price rules (MCR-11) | S and C | No |

Dependencies point downward only: S never depends on C or M, and C never depends on M. **Recommended build order: S, then C, then M.** S is a self-contained unit that can ship and be tested before any custom content exists (D0 Section 5 N).

### 14.2 All mods off: what still runs

Evidence: the save host is installed even with All mods off (`mods/host/pe_mod_host.c:336`: "always: a save made with mods off keeps their data too"); with All mods off no mod starts and the menu, equipment sync and presentation layers are skipped (`:331–335`). Layer S follows the same rule as the save host. Layer C:

- **Inert unless the loaded save has a ledger with at least one entry.** In that case it registers no native veto hooks, shows no page and adds no work beyond the save host's existing parse. New Game, the title screen and saves without custom items behave exactly as now.
- **Active only to protect.** With a ledger present, the veto hooks, reconciliation and the Custom items page run, so a session with mods off cannot strand or destroy custom data. It adds no gameplay.
- The README promise "nothing but the F1 panel touches the game" is already qualified by the save host. When S/C are implemented, the README should read "nothing but the F1 panel and the preservation of mod save data, including protection of custom items in saves that have them". That change belongs to the implementation unit, not this document change.

### 14.3 Missing-mod notice on load (layer S)

- **When:** after a load, at the first safe field frame (not during a cutscene, battle or menu), if any saved data belongs to an owner that is not running. Saved data means a tail record, an extension section or a ledger dictionary owner. The owner load outcomes come from the existing `pe_save_query`.
- **What:** one dialog per load. Example: "This save has data from mods that are off: Mod Catalog, Example Arms (3 items). It is kept unchanged. Items work as normal items until the mod is back." It lists up to 4 owners plus "and N more", with player-facing mod names where known and the namespace otherwise. One button: OK.
- **Never shown for:** All mods off with a save that has no mod data; owners that are running; saves whose only mod data is from owners deliberately removed by Convert.
- **Option:** Manage mods → "Missing-mod notice", default on.

### 14.4 Save-slot warning (layer S)

- **When:** the player confirms saving over an **existing** file, and the current game holds saved data whose owners are not running (the same set as §14.3). Saving to an empty slot never warns.
- **What:** "Some mods this save uses are off: Example Arms. Their data is kept, but if this session goes wrong you cannot go back. Save to a different slot?" with **New slot** (back to the slot list), **Overwrite** and **Cancel** (default New slot).
- **Frequency:** after Overwrite, no further warning for that slot until the next load or restart.
- **Option:** Manage mods → "Warn before overwriting", default on.
- **Prerequisite (audit):** a hook in the native save flow between the slot confirmation and the write (`src/main/memcard/save_flow.c`, slot-list states after `Menu_CreateSaveSlotListView`, about `:856–870`), showing a dialog through the game's own message box. If no safe point exists, fall back to a notice in the pause/F1 save area. Never block the native save.

### 14.5 Custom items page and Convert to normal item (layer C)

- **Where:** an F1 page "Custom items", provided by the content core rather than Economy or any provider, so it exists with All mods off whenever the save has a ledger. Nothing is added to the game's own item menus (D2 §9 rule against destructive buttons in normal menus).
- **Lists:** every ledger entry not in ACTIVE state, with item name (native), owner namespace, state (mod off / changed outside the game / missing) and location (bag/storage/equipped).
- **Convert to normal item** (UNAVAILABLE or UNCERTAIN entries):
  - one item at a time;
  - a confirm dialog states that the custom data and effects for that item are removed permanently and the item stays as a normal item;
  - default No;
  - removes the ledger entry and its attachments in one commit; the native record is unchanged; logged.
  - It is not offered for ACTIVE entries (use the provider's own actions) and not available during battle or cutscenes. There is no bulk version and no automatic conversion.
- **Remove record** (ORPHANED entries only): same confirm; removes a ledger entry that no longer has a native item.
- Converted entries count as legitimate removals: the §14.3 notice stops listing that owner once it has no data left in the save.

### 14.6 Tester guidance (documentation)

Add to the player/tester guide when S ships:

- Before trying other or possibly incompatible mods, save to a spare slot; the warning in §14.4 offers this.
- To back up or move saves, copy the whole `memory-cards\bu00` (and `bu10`) folder; it includes the `.pe-ext` folder.
- Turning a mod off never deletes its data or items. Convert is only for mods you have dropped for good.
- Do not play saves that have custom items in a vanilla (non-mod) build: its next save drops the custom data permanently.

### 14.7 Limits of the promise

Mods that register conflicting keys are refused at seal (D6 §11) and touch nothing. A mod or build that changes the inventory directly, bypassing the native item code and the veto hooks, cannot be prevented: reconciliation (§11.5) only detects it afterwards and demotes identity. Backups are the protection in that case, and the guidance says so.

## 15. Versioning and migration policy

October 31 recommended policy, documentation only, at the user's request to "capture versioning so migrations get easier". It applies to every layer in §14.1 and to existing records. It changes no current record or format.

### 15.1 What exists today (`mods/host/pe_save.h`, `pe_save.c`)

- **Container.** `PEMC`, format u8 = 1, flags u8. A writer marker records the mod API version (`PE_MOD_API_VERSION` = 1, `mods/host/pe_mod_host.h:24`) and the save writer revision. A newer container is kept whole and written back unchanged.
- **Records.** Each record carries a u16 layout `version`. On load:
  - an older version goes through the owner's `upgrade(data, old, size, version)`;
  - a newer one is kept unchanged while the mod starts from defaults;
  - version 0 is the legacy fixed block from before the host (PELT, PECT, PESH, PKEY, SORT, `pe_save.c:52–56`).
- **Names are ids:** "never rename it".

This is a sound base. What it lacks for easier migrations: a way for an older build to keep using a record that only gained fields; a standard shape for upgrade code; a single list of every version; and frozen test fixtures.

### 15.2 Six kinds of version, one meaning each

| Kind | Examples | Owned by | Changes when | Reader rule |
| --- | --- | --- | --- | --- |
| **Container / file format** | `PEMC` format; extension file format (§12.3); `pe_host.extlink` format | Save host | Framing changes (rare) | Newer: keep whole, write back unchanged; for the extension file, gate if *required* |
| **Layout version** | Tail record `version`; section `version`; ledger `format`; discovery `format` | Each owner | Any change to its bytes | Older: upgrade chain (§15.4). Newer: see `min_reader` |
| **`min_reader`** (sections and ledger only) | Section key table; ledger header | Each owner | Only when older readers would misread or corrupt the new bytes | Reader's layout version ≥ `min_reader`: read the fields it knows, keep the rest (§15.3). Otherwise: preserve whole; dormant, or gated if *required* |
| **Content revisions** | Ledger dictionary `revision`; attachment schema version; Catalog ordinal + accepted keys/absorbs (D6 §14.5); offer/stock revisions (MCR-07) | Each provider | The meaning of a definition, attachment or entry changes | Identity keys never change; revision drives per-instance migration (§15.5) |
| **Interface versions** | `PE_MOD_API_VERSION`; capability versions (D6 §3); descriptor `version`/`struct_size` | Host and capability owners | Code interfaces change | Code negotiation only; never a save compatibility gate |
| **Writer identity** | Tail writer marker; extension header `writer` (below) | Save host | Every build that writes | Diagnostics only (which build last wrote this) |

The extension file header (§12.3) uses its reserved u16 for the writer revision, so both stores record the writer identically.

### 15.3 Additive changes without breaking older builds (sections and ledger)

- **Prefer appending.** New fields go at the end of a section or ledger entry. Zero must mean the old behavior. Raise `version`, keep `min_reader` unchanged.
- **Prefix read.** A reader with `version ≥ min_reader` reads the prefix it knows. It keeps any trailing bytes and unknown flag bits, and writes them back unchanged when it saves. The discovery section already works this way for its reserved fact bits (§13.1); the rule generalizes it.
- **Raise `min_reader`** only for a change older readers would misinterpret: a reordered or resized field, or a new meaning for an existing value. Record the reason in the version table (§15.6).
- **Tail records** keep today's rule: any newer version is preserved and the mod uses defaults. The tail is closed to new records apart from the policy record and `pe_host.extlink` (§12.3), and its record header has no room for `min_reader` without a container format change, which is not worth making for the few remaining tail records. **Data that is expected to evolve goes in an extension section.**

### 15.4 Upgrade code: single-step chains

- An owner writes one step per version change: `step_N(bytes of version N) → bytes of version N+1`. The host helper (proposed `pe_save_upgrade_chain`) runs the steps in order, from the stored version to the current one. Today's single `upgrade()` keeps working; owners can wrap it.
- Steps are **frozen once released**: never edited, only added. Each step is a pure function of its input bytes: bounded sizes, no game state, no RNG, no allocation beyond its output buffer, deterministic.
- A step that cannot convert returns failure. The owner then resets as today, and the original bytes are preserved for diagnostics where the store supports it (extension sections: kept as a carried copy until the next successful save).
- **Defaults live with the step that adds a field,** not in later code. A field added in version 3 gets its default inside `step_2`, so each version means the same thing forever.
- Migration runs **in memory at load**. Nothing is written until the player saves; the original file stays readable by the build that wrote it until then.

### 15.5 Content migrations

- **Identity never changes.** Definition keys, effect keys, Catalog ordinals and stock keys are permanent. Renames use declared accepted previous keys, merges use absorbs (D6 §14.5), and keys and ordinals are never reused.
- **Existing items keep their native records.** Under the native-complete rule (§11.1), changing a definition's stats does not silently rewrite items already owned. A provider that wants existing items updated declares a per-instance migration step for `revision N → N+1`. The core runs it once per instance at load and updates the dictionary entry's `revision`, which records the revision the saved instances were last migrated to. Without a declared step, existing items stay as they were.
- **Attachments** carry their own schema version and follow §15.4 under their owner. An unknown or newer attachment version is preserved, not run (EFX-04).

### 15.6 The version table (single source of truth)

Every persistent layout gets a row here. Any change to a layout must update the row, add an upgrade step and add a golden fixture, in the same change. Current state:

| Store | Name / key | Layout version | `min_reader` | History |
| --- | --- | --- | --- | --- |
| Tail container | `PEMC` | format 1 | — | Writer marker: mod API 1, save writer revision (`pe_save.c`) |
| Tail record | `pe_economy.loot` | 1 | — | v0 = legacy `PELT` block (0x000, 0x20 bytes) |
| Tail record | `pe_economy.catalog` | 1 | — | v0 = legacy `PECT` (0x040, 0x148); 312-byte state |
| Tail record | `pe_economy.shop` | 1 | — | v0 = legacy `PESH` (0x1C0, 0x14) |
| Tail record | `pe_qol.keys` | 1 | — | v0 = legacy `PKEY` (0x200, 0x54); compatibility window |
| Tail record | `pe_qol.sort` | 1 | — | v0 = legacy `SORT` (0x260, 0x28); compatibility window |
| Tail record (proposed) | `pe_economy.policy` | 1 | — | §3 candidate, 160 bytes; not registered |
| Tail record (proposed) | `pe_host.extlink` | format 1 | — | §12.3, 20-byte payload |
| Extension file (proposed) | `PEX1` | format 1 | — | §12.3; profile 5,120 bytes (§13.2) |
| Section (proposed) | `pe_content.ledger` | format 1 | 1 | §11.2 |
| Section (proposed) | `pe_economy.discovery` | format 1 | 1 | §13.1 |

| Legacy profile file | `pe_collection.ini` | Existing unversioned layout retained | — | Read-only migration source after split; mixed costume/creature lines retained unchanged (§16) |
| Profile file (proposed) | `pe_wardrobe.ini` | `format 1` | — | §16; bounded first import of costume/worn state; no automatic repeat merge |
| Profile file (proposed) | `pe_bestiary.ini` | `format 1` | — | §16; bounded first import of creature facts/kills/seen state; separate writer |
| Character pack (proposed) | `pack.json` `format` | 1 | `min_wardrobe` 1 | D8 §3 |

Retired names, keys, flag bits and enum values are listed here too and never reused. There are none yet.

### 15.7 Golden fixtures and migration tests

- Every released layout version of every record and section gets a frozen byte fixture. It is local in `D:/Recomp Games/pe-native-debug`, made from synthetic state, never from a user's save.
- Each change runs all of these:
  - every older fixture upgrades to the current version and matches its expected state;
  - the current fixture round-trips byte for byte;
  - a fixture with a version above the current one is preserved byte for byte;
  - for sections, a fixture appending unknown trailing bytes survives a save.
- Steps are tested individually and as a full chain (v0 or v1 → current).

### 15.8 Players and format upgrades

- **Load:** at the first safe field frame, the host logs "upgraded `name` vN → vM". A save diagnostics page in F1 shows each record and section with its version, `min_reader`, state (current / upgraded / newer-kept / reset) and the writer that last saved it, reusing `pe_save_crash_describe`.
- **Save:** the §14.4 save-slot warning also appears, once per slot, when this save will rewrite data in a form older builds cannot fully use. That means a section's `min_reader` was raised or a tail record version went up. The dialog reads: "Saving updates mod data from Example Arms to a newer version. Older builds keep it but can't use it. Save to a different slot?" Same options and setting as §14.4.
- **Downgrade:** older builds never destroy newer data. Tail records and sections are preserved; a ledger older builds cannot read reaches the outer gate. Using a downgraded build therefore loses features, not data. The only exception is the vanilla build (§11.5).

### 15.9 Disposition

Recommended policy. Implementation pieces:
- the chain helper and prefix-read support in the save host and extension store (unit S);
- the per-instance content migration hook in the content core (C);
- the diagnostics page and the format-upgrade warning (S);
- the fixture suite.

D4 binds the cases ("Versioning and migration bindings"). D0 Section 5 O tracks the version table as a standing obligation.

## 16. Standalone feature persistence and extraction migration

November 1 recommended contract, no format implementation or user-data changes. Read D2 §10 / D6 §15 / D4 §16 and D9. This section supersedes D8's conflicting one-time-versus-repeat-import wording and adding a version line to the old mixed source. Existing supported record meanings stay unchanged. Actual file parser/serializer layouts need implementation review and golden fixtures under §15.

### 16.1 Single writer and stable storage identity

| State | Sole active authority after extraction | Required preservation |
| --- | --- | --- |
| Costume ownership, worn/default and acquisition choice | Wardrobe, `pe_wardrobe.ini` format 1 | Existing costume keys and absent-pack records; session availability separate from ownership |
| Creature facts/kills/acknowledged discoveries | Bestiary, `pe_bestiary.ini` format 1 | Existing creature keys, exact imported progress and missing-pack records; no automatic research reset |
| Legacy mixed Collection profile | No feature writer; migration source only | Leave `pe_collection.ini` and legacy binary source unchanged, including unknown lines |
| Wallet and legacy reward fields | One compatibility persistence owner for `pe_economy.loot` v1 | Preserve record identity/layout; wallet remains authoritative when enhanced rewards are disabled |
| Catalog/Rebuild/discovery and shop state | Existing one-writer compatibility adapters | Keep `pe_economy.catalog`, `pe_economy.discovery`, `pe_economy.shop` keys and unknown fields/sections; code owner name is not storage identity |

New module names do not rename records, clone balances or add headers automatically. While wallet and reward fields share one record, a single adapter loads/serializes the aggregate; feature owners mutate only their own validated logical fields. With rewards absent/disabled, preserve uninterpreted reward state and avoid zeroing its progress. A future physical record split requires a separately versioned migration/admission budget; folder extraction alone does not justify it. Unloaded optional owners retain their saved records through the accepted host/store policy.

### 16.2 Profile import and restart safety

Each feature imports independently. If its destination does not exist, parse its own recognized legacy lines into a bounded staged destination, retain missing-pack identities, and commit destination plus `imported_collection 1` marker together through the supported atomic profile writer. Only mark success after valid durable publication. Legacy binary import follows the established reader precedence and occurs through one documented source adapter, not twice through two live mixed-profile writers. Source files are never deleted or edited by extraction.

If a valid destination already exists, it is authoritative, including deliberate empty ownership/progress after a debug reset. **No automatic merge on every startup.** Explicit re-import, if later provided, must be a separate backed-up user action with reviewed reset/merge semantics; it is not part of normal startup. Lock/reset keeps the import marker so old source data cannot resurrect cleared facts. Copying a legacy source again does not change the import epoch. Missing/damaged/newer destinations require the versioned recovery policy, not silently reimporting over them or creating defaults that overwrite originals.

Wardrobe import and Bestiary import need not commit simultaneously: each has its own source subset and marker, so failure/retry cannot erase the other. Atomic profile staging/replace/flush and error handling must be audited on the target implementation; do not infer those guarantees from a text format. If import publication fails, expose migration-unavailable status and preserve originals; do not claim ownership saved or make paid actions eligible.

Keep explicit canonical mod/settings/profile values first. Otherwise import the old `pe_collection` enabled state into each feature's absent canonical setting once, retaining All mods off and unrelated settings. If neither canonical nor legacy value exists, retain current default-build behavior; new acquisition defaults remain a product decision. Retain old settings as read-only aliases, never repeatedly overwrite explicit later choices. Old builds continue seeing the untouched old profile, but later changes across divergent old/new files do not automatically synchronize; document this downgrade limit.

### 16.3 Feature absence and reset semantics

Wardrobe disabled/absent: use native story appearance; do not edit its profile, grant ownership or reset Bestiary. A missing worn pack uses the supported session appearance fallback while retaining its stable saved key. Everything-available session policy affects eligibility only, not the owned set. Bestiary disabled/absent: preserve its profile and stop its tracking; no invented retroactive kills on re-enable. Economy absent: independent features keep their nonpaid behavior; paid actions unavailable and no profile/currency conversion. Counter/rewards/shops do not become multiple wallet writers.

Feature-local reset/lock must not change another profile or import marker. Unknown fields/records are preserved within the supported framing/version limits. Shared codecs may share implementation, not mutable buffers or write ownership. Rebuild/Dismantle and profile actions retain their existing anti-exploit policy; no new refunds are inferred.

### 16.4 Per-save currency versus profile-wide unlocks — explicit blocker

Costume/Bestiary entitlements are profile-wide; Junk comes from the loaded save. A per-save coherent transaction is insufficient to commit both durable stores. A spend followed by `grant` can lose money on profile failure; reversing them can grant an unpaid unlock. A local operation token alone does not solve crash recovery or older-save restoration.

New paid adapters remain **unavailable until MCR-08/09 specify and verify the cross-store protocol**: preparation, durable publication/recovery authority, pending/terminal states and bounded retention, original-save/profile backups, file failures and restart replay. Do not introduce a journal/sidecar format here by implication. Define action scope and guarantee explicitly, including legitimate save rollback versus exploit prevention; no global anti-rollback promise. Existing legacy purchase paths are not certified or silently changed by this design.

Before extraction implementation bind PB-15–18, exact profile format/error behavior, legacy binary precedence, aggregate-record ownership and service/mod-key compatibility. UI buying/default choices stay open. Record native file-write and one-writer evidence; no build/tests ran for this documentation update.
