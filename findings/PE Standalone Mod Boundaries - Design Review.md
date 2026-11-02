# D9 — Standalone mod boundaries and optional integrations

Date: November 1, 2026. Status: recommendation and open-decision review; documentation only. No game code, profiles, saves, prices, defaults or build settings changed. No implementation or runtime tests performed.

November 2 phase 1 disposition: D8 §12 and §8 below resolve **SPL-01 at design level** using the user's standalone-free / optional Economy restriction decision. SPL-02–09 remain open; the original nine-finding review below is retained as history. No implementation/testing claim follows from this disposition.

November 2 importing scope: D8 §11 focuses the future drop-in loader on Wardrobe player skins prepared in supported PE formats. Enemy/Bestiary pack importing is deferred; this does not defer the standalone Bestiary feature split. SPL-04/09 still apply to Wardrobe keys/packs; no new enemy pack contract is implied.

Read with [D8, character packs and standalone Wardrobe](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Character Packs and Standalone Wardrobe - Design.md>), [D6, capability contracts](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Mod Extensions - API and Cooperation Contract.md>), [D3, persistence](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Persistence and Migration Design.md>) and the [master checklist](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets and Menu Organization - Master Checklist.md>). This review complements the user's latest edits without replacing their policies or declaring unresolved features approved.

## 1. Source observations and limits

Read-only check of `D:/Recomp Games/pe-mod-presets` on November 1: `mods/pe_collection/pe_collection.c` publishes Bestiary and costume services, initializes both features, owns shared Junk helpers and a combined reset action. `pe_profile.c` stores both features in `pe_collection.ini`. `pe_bestiary.c` directly spends through those helpers to buy information tiers. The build list groups both under `pe_collection`; host model/view/stage helpers already exist separately.

Economy's folder contains wallet/reward logic, Catalog and Rebuild state, Dismantle, Requisition, Wayne/Warner menus and Junk display code. A directory split alone would leave state and transaction coupling unresolved. D8 inspected the more recent Wardrobe browser in `pe-requisition`; this check is not a claim that the two worktrees, latest upstream or every current UI path match. Re-audit the actual chosen target before extraction.

## 2. Recommended feature and capability boundaries

| Module / capability boundary | Owns | Required relationship | Optional integration |
| --- | --- | --- | --- |
| Shared host support | Save safety/store, registry conventions, model/asset/view helpers; content core only to the extent required by its accepted compatibility design | Feature-neutral infrastructure | No compulsory Economy, Wardrobe or Bestiary gameplay |
| `pe_wardrobe` | Costume registry/packs, wear/preview, ownership, worn/default choice, Wardrobe profile/UI | Host; its supported asset/runtime helpers | Separate acquisition/payment adapter; does not own wallet or call a specific Economy implementation |
| `pe_bestiary` (preferred explicit identity) | Creature registry, encountered/kills/discovery facts, viewer and earned progression, Bestiary profile/UI | Host; its supported viewer/runtime helpers | Optional paid-information adapter; earned research/tracking stays useful without Economy |
| Junk wallet/routing capability | Authoritative balance, counter/inventory routing, validated spend/credit and persistence adapter | Save/inventory owners | Economy rewards and any supported shops are consumers; wallet does not require extra battle income |
| Economy rewards | Enhanced/configurable income, extra drops, bundle policies, progress/RNG | Wallet and supported inventory/save actions | No requirement for Collection viewers, costume packs or information purchases |
| Mod Catalog feature | Entry presentation, discovery/unlocks and install/remove eligibility/action coordination | Equipment/effect services and persistence | Wallet-backed paid actions; does not require enhanced battle drops, Wardrobe or Bestiary |
| Shops/Requisition/Workshop integration | Shop offers, pricing/stock, payment coordination and NPC entry points | Required wallet/action owners for the offered action | Wardrobe, Bestiary, Catalog and custom content through ready capabilities |

Names beyond `pe_wardrobe`/`pe_bestiary` are responsibility boundaries, not a decision to ship one selectable mod for every source file. Extract Wardrobe and Bestiary first; subdivide Economy into independently testable owners before deciding which deserve separate build/runtime toggles. Keep a convenient aggregate/default configuration so modularity does not require ordinary players to configure many technical switches. Explicit feature toggles must still reflect actual supported dependencies.

Dependency direction: optional integrations consume feature capabilities and a payment capability; independent features do not depend on the integrations. Economy can contribute an acquisition adapter without becoming costume/discovery authority. Shared viewer, profile parsing and UI helpers are libraries, not reasons to require both feature mods at runtime. Native creature and costume packs must register their own feature subsets without references to an absent feature's functions.

## 3. Standalone behavior and ownership rules

- Wardrobe alone must load supported packs, preview and wear under its accepted acquisition policy. D8's temporary everything-available fallback must remain distinct from permanently granting ownership. Do not write every costume as owned merely because the shop is absent.
- Bestiary alone must register creatures, track encounters/kills, earn the existing research progression and display discovered information. Missing a payment adapter disables only paid research. Do not reveal all information or reset earned facts as a side effect of disabling Economy.
- Economy rewards alone must retain current Enhanced defaults and behavior. Bestiary visibility and worn appearance cannot affect whether its basic wallet/rewards initialize.
- Wallet/counter convenience must be usable without extra reward generation when the accepted routing policy supports it. Junk counter display belongs to its presentation owner and must not become a second wallet. Existing state inside `pe_economy.loot` cannot be split into duplicate saved balances.
- Catalog alone, if made independently selectable, must preserve discovery and equipment rules. Without a payment capability, paid actions are unavailable rather than free; unpriced/earned actions need their own explicit supported policy. Do not use module absence to grant unlocks.
- Paid adapters query owner eligibility and perform supported coordinated actions. They cannot directly edit costume/profile/discovery buffers, infer ownership from prices, or duplicate wallet state. Multiple acquisition adapters require deterministic identity/selection/conflict rules, not a single silently overwritten shop callback.

## 4. Compatibility and migration prerequisites

Keep saved costume/creature IDs and existing record/section keys stable even if code ownership or mod display names change. In particular, extracting Catalog must not simply rename `pe_economy.discovery` or native Catalog records. One active serializer owns each retained record; split mods cannot both rewrite the same mixed record/file. Preserve unknown and absent-provider data.

Profile migration is a separate unit from code extraction. Copy/import into feature-owned files through staged writes, keep originals and unrelated lines, and mark migration only after the destination is valid. Decide whether Bestiary uses a new file or temporarily retains `pe_collection.ini`; no two independent writers may lose each other's records. A shared codec is useful, but each profile needs a clear owner and version policy.

D8 describes both a one-time import and later repeat merging from the old profile. Those conflict with explicit test resets/locking: repeated import can resurrect deliberately cleared ownership. Choose a migration epoch/tombstone or explicit re-import policy before implementation. Existing legacy profile keys, debug resets, enabled-state settings and menu-key migration must be covered; turning off Wardrobe must not reset Bestiary or vice versa.

Preserve `costumes`/`bestiary`/`wardrobe` service compatibility through one authoritative publisher per service version. A temporary `pe_collection` compatibility aggregate may select/configure the new modules, but must not publish duplicate services or own a second profile. Whether to retain the old mod ID, map its enabled setting to both new features, or retain a build-list alias is an explicit migration decision. Advertise source/build dependencies separately from runtime optional capability presence.

## 5. Conflicts and decisions requiring disposition

1. **Wardrobe buying UI:** earlier D0/D1/D2 exclude Wardrobe buying, while D8 allows direct purchasing and leaves its placement open. Standalone extraction does not decide that product choice. Keep the no-buying UI baseline until explicitly revised; optional Workshop purchasing can integrate independently.
2. **Acquisition defaults:** D8 recommends Everything unlocked without Economy and Shop with Economy. Preserve explicit player choice and distinguish session availability from saved ownership. Specify first-run detection versus subsequent provider toggles before changing any defaults. Bestiary does not inherit this all-unlocked rule.
3. **Profile versus per-save payment:** Junk is per-save; costume and Bestiary facts are profile-wide. Spending first and then calling `grant` is insufficient if profile write fails or the game crashes. Define preparation, persistent publication and supported failure/recovery across both stores under MCR-08/09. Do not imply the proposed per-save transaction alone makes this atomic, or alter current legacy operations silently.
4. **Economy state split:** wallet, legacy difficulty, reward progress and other fields already share saved state. Choose a single compatibility owner/adapter, loading with rewards absent, and any reviewed versioned migration before independently registering wallet/rewards modules.
5. **Stable file/service/mod identities:** define aliasing and one-time import precedence, ownership of mixed Catalog/Rebuild state, unknown-line retention, reset scope and old-build limits. Code movement is not permission to rename persistent identities.
6. **Multiple payment/acquisition providers:** choose explicit adapter IDs, declared policy and default/selection behavior using D6 registration rules; no register-last winner or circular Wardrobe↔Economy hard dependency.

These are open design tasks, not a request for broad code changes. D8's pack reader is separate from the module extraction and can follow afterward. Shared display helpers need not become another mod. No new prices, reward rates or reveal rules are selected here.

## 6. Proposed delivery and validation order

1. Audit actual target service publishers, build dependencies, cross-feature symbols, profile/record writers, menu identities and NPC adapters. Agree the migration/default/acquisition decisions above.
2. Extract feature-neutral viewer/profile codec helpers as needed; preserve published service behavior and avoid gameplay changes.
3. Separate Wardrobe and Bestiary registration, profile authority and debug actions, with compatibility import/aliases. Make their Economy adapters optional. Do not duplicate native pack registration.
4. Separate wallet/routing from reward calculations behind one authority, preserving existing save records/defaults; evaluate Catalog/shops as subsequent separately authorized feature extractions.
5. Add pack/API improvements after the standalone baseline is verified; then adopt the newer content/shop contracts only where their own prerequisites are ready.

Required future test matrix: Wardrobe only; Bestiary only; both without Economy; Economy only; wallet with rewards off; each feature with its optional paid adapter; all features; all off; feature absent from build versus merely disabled. Also test legacy profile/setting import, reset/lock without re-import resurrection, unknown pack retention, missing worn outfit, independent bestiary progress, service-version compatibility, shared helper resource cleanup, multiple adapters, and failure during profile-plus-save payment. Run real supported native paths, not just stubs. All new fixtures/runners/raw evidence remain local in `pe-native-debug`; no tests have been created or executed for this review.

This document recommends the boundaries and records conflicts. It does not authorize extraction, resolve MCR-08/09, revise D8's outstanding choices, or certify backward compatibility. Implementation needs separate scope and evidence.

## 7. Standalone specification review — November 1, 2026

Reviewed D2 §10, D3 §16, D6 §15, D4 §16 and D8 §§3–4/10 against the boundaries above and the shared D6 registration conventions. **Document-contract review only**: no fresh full source audit, builds, tests, profile changes or game code changes. Existing source observations in §1 retain their worktree/date limits. The initial review left all nine findings open; §8 now design-resolves SPL-01 for phase 1. **SPL-02–09 remain OPEN**; other recommendations below are not automatically adopted policies. Earlier MCR design dispositions do not close these extraction-specific gaps.

The split is still a suitable direction. Independent feature owners, one wallet, optional integrations, stable storage IDs and separate profiles should remain. However, a complete extraction specification must settle the applicable findings below before implementation; a document with planned tests is not an implementation pass.

### SPL-01 — Stored acquisition choice versus effective no-shop fallback

Priority: **high for Wardrobe behavior**. References: D2 §10 Unlocking row; D6 §15.3; D8 §§4.2/4.5/10; D4 STN-11.

The documents say explicit stored Shop choice takes precedence, while also requiring temporary Everything availability whenever the shop is absent. Preserving the stored value alone does not resolve which behavior the player actually gets. A costume worn under temporary eligibility may become unowned/ineligible when the adapter returns, yet no wear/fallback transition is defined. Multiple conflicting default adapters create another distinction: unavailable payment is not necessarily equivalent to no shop installed.

Required disposition: specify a state table for stored choice (unset/Shop/Everything), adapter readiness (absent/disabled/conflicted/blocked/ready), effective wear eligibility, permanent ownership, and already-worn unowned costume behavior after transition. Decide whether an explicit Shop choice permits the free session fallback or instead remains owned-only. Keep first-install defaults and direct-buying placement explicit product decisions; do not choose them in a getter. Bestiary remains earned-information behavior, not Everything unlocked.

Acceptance extension: STN-10/11/16, no ownership writes on fallback, adapter reappearance after restart, conflicting defaults, missing versus failed payment, story outfit/room transitions and continued wearing versus safe native fallback under the selected policy.

### SPL-02 — Missing profile is not sufficient evidence of first-run migration

Priority: **high**, blocks profile migration guarantees. References: D3 §16.2; D8 §10; D4 STN-05–08/23.

D3 imports when the destination does not exist, but also says missing/damaged/newer destinations require recovery rather than silent reimport. The import marker lives in that same destination. If a migrated/reset destination is deleted or lost, its marker vanishes and stale legacy ownership can be resurrected despite the no-repeat-import promise. Existence also does not distinguish a new blank profile created by another version from completed import. Independent feature imports may read a legacy file changed by an older executable between starts.

Required disposition: define migration identity/epoch and available evidence for first use versus missing migrated state, including profile-directory relocation/copy and source changes. Choose a bounded durable migration receipt/backup or explicit user-confirmed recovery policy; do not introduce an extra store silently. Specify precedence for existing valid format-1 destinations without a marker, interrupted temp/backup files, truly absent source and legacy binary input. Limit the no-resurrection promise to evidence the reader actually has. Reset retains the accepted migration history; explicit reimport remains a separately reviewed action.

Acceptance extension: STN-05–09/23 with deleted destination after lock/reset, missing marker, destination-only/source-only copies, interrupted first publication, changed source and unknown newer profile. Preserve originals on every refusal.

### SPL-03 — Compatibility writer location and feature activation are unassigned

Priority: **high**, blocks wallet/rewards/Catalog extraction. References: D3 §16.1; D6 §15.1/15.3; D2 §10; D4 STN-13/14/22.

One writer for `pe_economy.loot` is required, but the documents do not name its lifecycle/build owner when rewards, wallet or Economy itself is absent. A writer compiled only into the removed reward module cannot provide wallet-only persistence; a host writer that initializes feature state indiscriminately can overwrite inactive fields or alter All mods off behavior. Catalog/Rebuild share legacy data too, and a code-owner move must not imply two independent writers. Counter routing, legacy enabled/disabled fields and reward difficulty need explicit ownership beyond the word "aggregate".

Required disposition: assign concrete persistence adapter/build ownership and per-field load/reset/mutate/serialize authority for supported feature combinations. Distinguish live owned fields from carried uninterpreted fields and define how legacy enabled state maps to wallet/reward/routing statuses. Keep storage identities and record sizes unchanged for extraction; a physical record split needs separate approval. Define build-time missing owner versus runtime disabled owner, New Game, unknown/newer data and compatibility hook ordering. Do not make the feature-neutral host responsible for new gameplay calculations merely to solve serialization.

Acceptance extension: STN-03/04/13/14/22 with wallet-only, rewards omitted, Catalog omitted, aggregate alias plus explicit features, newer carried state, save/load/New Game and no-provider output/default comparison.

### SPL-04 — v1 services, keys and mod aliases need an exact compatibility matrix

Priority: **high**, blocks claiming existing consumers keep working. References: D6 §15.1/15.3; D3 §16.2; D8 §§3.3/4.3/10; D4 STN-04/09/15.

"Preserve or report unsupported" is not yet a per-operation contract. Existing Wardrobe pick/buy behavior and Junk enabled semantics can conflict with withholding new paid adapters. There is no mapping for old callback/action results, providers requiring the old `pe_collection` mod ID, or old build-list/setting aliases after one feature is explicitly selected. Old costume keys such as `pe1/tshirt` and D8's `<pack-id>/<folder>` also differ from D6's new general key conventions and 47-byte ceiling; forcing new validation onto legacy IDs can break imports or external packs.

Required disposition: list actual v1 table versions/fields/operations, source consumers, required-mod declarations and key limits on the selected branch. Define one publisher, compatible forwarding/error result per operation, and a bounded immutable mapping for preserved legacy keys versus new pack IDs. If an old interface cannot safely represent a disabled purchase, constrain its advertised support explicitly; do not silently change numeric prices or behavior. Bind canonical setting precedence and aggregate expansion/de-duplication including hard dependency IDs. No binary ABI compatibility promise is inferred.

Acceptance extension: STN-01–04/09/15 with representative old providers, v1 calls without payment, preserved slash keys, maximum-length pack keys, old dependency metadata and explicit single-feature builds. D8 pack-key limits must be coherent before its reader ships.

### SPL-05 — Cross-store purchase blocker must be applied to every adapter path

Priority: **high for paid actions**, known unresolved gate, not a new atomicity design. References: D3 §16.4; D6 §15.2/15.4; D8 §4.3; D4 STN-17–21; MCR-08/09.

The new documents correctly block paid profile unlocks until a profile-plus-save protocol exists. However, D8's old spend-then-grant recipe, v1 pick/buy entry points, legacy Bestiary research and Workshop calls must all be classified. Otherwise extraction can advertise a blocked new adapter while an old facade still charges through the unsafe route. Profile save failure also matters for nonpaid ownership/research actions: in-memory success, persistent success and subsequent retry cannot be conflated.

Required disposition: enumerate UI/service/legacy entry points and which stay unchanged, become unavailable or use a verified protocol; specify truthful result/status and player feedback. Do not silently alter untouched legacy behavior or certify it as safe. For new paid support, bind durable recovery, completion notification, operation identity, profile/save backups and restart/slot rollback scope under MCR-08/09. For earned/nonpaid facts, define dirty-write failure/retry and clear durability semantics without inventing charges.

Acceptance extension: STN-15/17–21/23 through real Workshop/viewer/service callbacks, read-only/full profile path, disk failures, crash/restart and retry. A mock commit cannot discharge the native/file guarantee. Basic nonpaid extraction may proceed independently once its own gates are satisfied.

### SPL-06 — Optional adapter selection lacks feature-scoped eligibility and fallback semantics

Priority: **medium; required before multiple adapters**. References: D6 §15.2; D2 §10 integration status; D4 STN-16/18.

The specification picks an explicit compatible adapter or one default, but does not define the persisted selection owner/scope, selection per feature/action, or whether temporary target ineligibility changes the default. A costume-only adapter must not suppress research offers. A missing selected provider must not silently switch the player to another price/currency policy. A default selected per quote based on eligibility could change unpredictably as ownership or discovery changes.

Required disposition: feature/action-specific adapter registration, saved selection identity/scope, readiness versus target eligibility, missing-selection behavior and deterministic default resolution. Distinguish provider absent, wrong version, protocol blocked and conflicting defaults. Requote on relevant generation/selection changes without automatically paying, granting or rewriting the player's preference. Bound the registry under shared D6 conventions and declare extension/selection ownership.

Acceptance extension: STN-11/16/18 with costume-only and research-only adapters, two defaults, explicit missing selection, no eligible target, restored provider and changed profile/playthrough. Leave paid execution blocked until SPL-05/MCR-08/09 are resolved.

### SPL-07 — Single writer does not yet address concurrent processes or external profile edits

Priority: **high for persistence claims**. References: D3 §16.1/16.2; D6 §15.4; D4 STN-06/08/23.

One in-process feature owner prevents competing modules from rewriting a profile, but two game instances, an older build or an editor can still change the same preferences. Atomic file replacement prevents a torn file, not last-writer-wins loss of ownership/progress/reset. Wardrobe and Bestiary intentionally share profile scope across save slots; profile-generation validation and dirty/deferred flush behavior need an external-change policy.

Required disposition: choose a supported single-instance/profile-lock policy or explicit compare-generation/read-only refusal mechanism; define lock lifetime, crash-stale recovery and editor expectations without inventing arbitrary merge semantics. Specify bounded dirty-save retry and shutdown/disable failure reporting. Record source/destination identity for migration and prevent silent overwrite of externally changed newer data. This does not require worker threads or a general database.

Acceptance extension: STN-06/08/18/23 with two writers, external reset/edit between load and flush, failed shutdown write and stale lock if selected. State unsupported concurrency explicitly if no coordination is provided; do not claim atomic replace alone preserves all updates.

### SPL-08 — Shared runtime resource ownership needs an extraction audit

Priority: **medium**, required for each extracted viewer. References: D2 §10 shared helpers; D6 §15.1/15.4; D4 STN-01–04/10/23/24; D9 §1.

The documents say shared helpers remain libraries, but do not yet assign stage/model contexts, pack registrars, input/tick hooks, borrowed strings, caches and shutdown order. A shared singleton initialized/freed by Collection can still make a separately linked viewer depend on it. Duplicate native-pack registration, a dangling menu callback or both features owning the same stage can survive source-file movement and fail only in single-feature/all-off combinations. Appearance application also needs story/room/equip transition checks, not just viewer preview.

Required disposition: audit actual target symbols/resources and assign shared support versus feature/session ownership, stage/input arbitration, callback lifetime and restart cleanup. Keep native gameplay hooks outside preview-only contexts; preserve existing story appearance rules. De-duplicate helpers/caches without sharing mutable feature progress. Do not infer hot unload support from testing one feature disabled at startup.

Acceptance extension: STN-01–04/10/23/24 with each feature compiled alone, both viewers opened sequentially, preview cancellation, room/story transitions and resource failure/unwind. Measure accepted resource limits; source-level separation alone is insufficient.

### SPL-09 — Pack admission/version selection needs an explicit shared-registry exception or alignment

Priority: **medium for extraction; high before pack reader**, scoped to the later pack unit. References: D8 §§3.2–3.5/6 and PACK-04/05; D6 §11; D4 STN-04/15/24.

D8 selects the higher version of the same pack ID, compares author metadata for clashes and accepts healthy characters from a partly broken pack. D6 rejects authenticated duplicate keys/batches together and derives namespace ownership from the host; data-only pack author strings are not authenticated mod ownership. Equal versions, same author/different payload, legacy implicit packs, aliases/default replacement targets and combined pack/compiled-costume limits have no unified conflict policy. Marketing SemVer order cannot be assumed to prove compatible saved identity.

Required disposition: define a separate bounded pack discovery/selection layer before typed registration, or align it with duplicate-all admission. State identity/ownership provenance for data packs, same/equal-version conflicts, explicit replacement selection and per-character versus pack-required batches. Enforce full key and resource limits across loose/zip/implicit/compiled providers. Keep missing-pack ownership and current native keys. Metadata/version strings are not permissions to replace foreign content. Do not turn this pack-specific decision into a change to MCR-01–03 for all mods.

Acceptance extension: D8 PACK-02/04/05 and STN-04/15/24 with equal-version conflicting payloads, zip+loose duplicates, long keys, compiled providers versus data packs, missing dependencies and aggregate limits. This finding need not block initial extraction that retains only the already-supported skin registration path.

### Scoped readiness and follow-up

| Delivery slice | Required dispositions before implementing the affected behavior |
| --- | --- |
| Basic Wardrobe/Bestiary extraction and profile import | SPL-01–04, SPL-07/08; classify legacy actions under SPL-05 without claiming new paid safety |
| Wallet/reward/Catalog owner extraction | SPL-03/04, relevant SPL-07/08 and actual field/build audit; maintain Enhanced and stored-state parity |
| Multiple optional acquisition adapters | SPL-04–06 and relevant profile/concurrency gates; new paid behavior remains gated by MCR-08/09 |
| New character pack reader | SPL-04/09 plus D8's format/resource/asset validation and profile/version acceptance |

Required document follow-up: dispositions in D2/D3/D6, binding product choices under PB-17 and migration/concurrency under PB-16, adapter/durable result rules under PB-18, then strengthen D4's existing STN cases. Keep the 24 case count unchanged until new individually scoped cases are actually added; coverage notes are not executed tests. All future raw fixtures/tools/evidence remain local in `pe-native-debug`.

**Original review result: modular split retained, nine findings initially OPEN.** Section 8 subsequently resolves SPL-01 at phase 1 design level; eight remain open. Do not mark the extraction implemented or all documents accepted merely because this review is committed. Recommended first decision unit: acquisition eligibility state table, migration receipt/recovery policy and mixed-record writer authority (SPL-01–03), followed by service compatibility/concurrency/resource audit. No source code, balance, user files or executable changed.

## 8. Phase 1 Wardrobe acquisition disposition — November 2

The user chose Wardrobe as the standalone viewer/equipment feature, with every installed compatible costume available when used alone. Economy owns optional Costume unlock rules, default on, reproducing current unlock/purchase behavior when both are enabled. Explicit rules off or Economy absent/disabled gives unrestricted access while leaving the rest of Economy and all earned ownership unchanged. D8 §12 is the controlling full state table; D2 §10, D3 §16.5 and D6 §15.5 carry the control/persistence/API contracts.

**SPL-01: phase 1 design-resolved.** No separate Wardrobe Shop/Everything preference is introduced. Stored explicit false wins over default-on after restart/re-enable; unrestricted eligibility never writes a grant. Active rules with failed/conflicting/unavailable payment remain restricted, rather than accidentally unlocking everything. When rules return and an unowned selection becomes ineligible, explain/apply native story fallback at a safe outfit boundary, retain the requested key and do not displace later valid player choice or charge automatically. Direct buying stays outside the baseline viewer; existing Economy-enabled acquisition sources/prices are preserved within supported compatibility.

This resolves the phase 1 product/default/fallback conflict, not its implementation or the other migration/runtime problems. Profile mapping and settings compatibility remain SPL-02/04, safe runtime publication remains SPL-08, and new paid support remains SPL-05/MCR-08/09. Multi-provider selection (SPL-06) is not added to phase 1. SPL-02–09 remain OPEN.

After phase 1, Economy may propose acquisition presets, progression/challenge rewards and other improvements separately; none is silently enabled by this decision. Prepared-skin importing remains a separate Wardrobe unit; enemy importing stays deferred. D4 PB-17, STN-10/11/18/19 and D8 WRD-01–03/06 bind the phase 1 expectations, all unrun. No code, profiles, prices, assets, executable or local test suite changed.
