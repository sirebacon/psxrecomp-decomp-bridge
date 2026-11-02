# D2 — Scoped control inventory and menu map

Date: October 30, 2026. Status: source-audited design draft; no implementation, balance change, build, or runtime validation.

## 1. Scope, sources, and authority

This document scopes the Economy-first work from [D1, the proposal](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Economy presets and independent reward controls proposal.md>) and addresses [D7, REV-01–12](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets and Mod Extensions - Pre-implementation Review.md>). Its companions are [D3, persistence](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Persistence and Migration Design.md>) and [D6, small APIs](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Mod Extensions - API and Cooperation Contract.md>). Progress is tracked in the [master checklist](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets and Menu Organization - Master Checklist.md>).

Reference baseline: clean `feat/localization`, HEAD `ae6520fe6`, `D:/Recomp Games/pe-localization`. This is the inspected baseline, not a choice of implementation branch or proof that upstream matches. Recheck all values and source ownership on the eventual target branch. New stable IDs and API/record names below are proposed, not existing identifiers.

October 31 kickoff: implementation checkout selected as `D:/Recomp Games/pe-mod-presets`, branch `feat/mod-presets-framework`, fetched upstream base `8c52cdde5d60ee52f00913517ffb593e9521bf2d`. Initial read-only save-host checks confirm the capacity/admission gap persists; the entire control inventory is not yet revalidated against this newer base. First code unit is the host-owned read-only provenance/capacity query recorded in D0, before any new saved policy is registered. No implementation code or tests were added during branch setup.

Labels: **Observed** means source-confirmed; **Required** means a previously stated invariant; **Recommended** means a concrete draft policy for review. None authorizes code changes. Numeric playtest balance in D1 remains provisional.

### Included slices

| Slice | Included | Preconditions |
| --- | --- | --- |
| A — Inventory/contracts | Current controls, persistence scopes, ownership, menu keys, capacity and lifecycle audit | Documentation only |
| B — Economy separation | Counter-only play, explicit legacy/configurable engines, reward settings, safe redemption and progress | Approved D2/D3 policies and save-host prerequisites |
| C — Small extension API | New-path battle-Junk contributions, completed-reward notifications, additional Economy presets | Approved D6; no-provider parity and two local sample consumers |
| D — Economy navigation | Economy subpages, linked Inventory counter setting, legacy-key migration | Stable setting identity/migration contract |

Deferred from A–D: other category presets, full top-level menu reorder, pricing extensions/sliders, Workshop visibility, custom reward item/effect registration, Randomizers, global overhaul activation, worker execution, and runtime module unloading. Section 9 now specifies proposed follow-up slices E–G for custom content/effects and shops; it does not expand the first implementation or approve coding. Custom reward/drop adapters remain separate.

## 2. Observed controls and persistence

Sources: [loot controls/state](<D:/Recomp Games/pe-localization/mods/pe_economy/pe_loot.c>), [menu persistence](<D:/Recomp Games/pe-localization/mods/host/pe_mod_menu.c>), [row types](<D:/Recomp Games/pe-localization/mods/host/pe_mod_menu.h>), [existing pages](<D:/Recomp Games/pe-localization/mods/host/pe_pages.h>).

The prefix `PE Enhancements/` precedes page names below. Ordinary toggle/choice/int rows persist in `pe_mods.ini`; live rows do not. A registered save record separately persists runtime state. Do not infer persistence from a row's visual location.

| Existing page / label | Source/default; allowed values | Backing owner / persistence | Planned handling |
| --- | --- | --- | --- |
| Economy / Junk | Read-only; 0–99,999 runtime balance | Wallet; `pe_economy.loot` v1 | Preserve and show on main page |
| Economy / Difficulty | Live choice; Normal=1; Relaxed=0, Grind=2 | Legacy `s_st.preset`, saved in loot record | Keep legacy coupling, clearly labeled Advanced |
| Economy / Rare drop within | Read-only; current guarantee estimate | Legacy calculation/progress | Show engine-appropriate estimate, not a generic promise |
| Economy / Wayne hand-in | Next gun=0 default; All Junk=1 | Ordinary choice; profile INI | Preserve value/scope and key alias |
| Economy / Junk economy | On=1 default | INI `s_enabled` plus per-save `disabled` synchronization | Preserve legacy control; do not relabel it as storage-only |
| Economy / Take out Junk | Action; economy must be off, fills free bag/trunk slots | Wallet + native inventory; no saved action | Preserve; remainder stays in wallet |
| Economy / Wayne junk refund | Off=0 default | Separate feature/INI | Preserve disabled default; never included in a reward preset |
| Inventory / Junk counter | On=1 default; display only | `pe_junk_counter.c`, INI | Keep separate from storage/rewards |

Observed legacy tuning (page `Debug/Loot tuning`; all ordinary INI integers):

| Label | Default | Range / step | Owner |
| --- | ---: | --- | --- |
| Junk floor | 1 | 0–10 / 1 | Legacy payout |
| EXP per Junk | 8 | 1–100 / 1 | Legacy payout |
| Battle Junk cap | 12 | 1–200 / 1 | Legacy base payout cap |
| Boss Junk cap | 25 | 1–200 / 1 | Legacy base payout cap |
| No-hit bonus % | 25 | 0–100 / 5 | Legacy hit-based bonus; label is less precise than its implementation |
| Rare base % | 4 | 0–100 / 1 | Legacy rare roll |
| Rare step % | 1 | 0–50 / 1 | Legacy escalating chance |
| Rare guarantee | 25 | 1–200 / 1 | Legacy guarantee |
| Economy mod guarantee | 8 | 1–50 / 1 | Legacy non-bundle selection |
| Mod Permit guarantee | 8 | 1–50 / 1 | Legacy non-bundle selection |
| Empty steal Junk | 2 | 0–20 / 1 | Legacy compensation |

Debug actions Give 100 Junk, Give 1000 Junk, and live Set Junk (0–99,999, step 10) stay under Developer Tools; no preset invokes them. Existing custom legacy tuning is preserved. Do not move it into per-save new-mode fields merely because the new settings are per save.

Other existing controls are preserved by their current owners: Catalog/Dismantle/Rebuild/Requisition enablement, smoke/combat behavior, armor-effect display, collection ownership, item combining, inventory sorting, and localization. A complete cross-mod reorder is a later inventory exercise; this scoped inventory does not claim to enumerate every row in the suite.

## 3. New canonical setting ownership

| Proposed ID/group | Type / scope | Owner / meaning |
| --- | --- | --- |
| `economy.engine` | Legacy / Configurable; per save | Reward policy; never inferred from display label |
| `economy.preset_key` | Stable namespaced key; per save | Preset selection metadata; empty for user-defined Custom |
| `economy.native_junk_route` | Counter / Items; per save in new mode | Wallet routing of actual native Junk |
| `economy.income.*` | Enabled, ordinary/boss fixed amount, payment chance, performance and empty-steal settings | Extra-income module; per save in new mode |
| `economy.bonus_item.*` | Enabled, basis-point chance, guarantee interval | Non-bundle reward module; per save |
| `economy.bundle.*` | Separate Super/Duper enabled flags/chances; mutually exclusive outcomes | Bundle generation; per save |
| `economy.redemption.*` | Separate automatic flags and values | Conversion, independent of generation; per save |
| `economy.price_base_pct` | Legacy-derived price context, not a new slider | Pricing adapter; per-save new-mode context |
| `inventory.show_junk` | Boolean; existing profile preference | Display owner; no routing/reward effects |
| Legacy difficulty/tuning and Wayne preference | Existing scopes | Preserve existing owners and restart/save semantics |

Technical representation limits are in D3/D6. They are not approved gameplay ranges. Named Low/Standard/Frequent mappings and advanced UI limits remain pending balance/UI review. Initial new income uses fixed payments; EXP-scaling controls remain on the legacy path, not implicitly copied into new mode.

Presets use D1's exact provisional table. Enhanced selects Legacy; Vanilla drops + inventory QoL, Light, Steady Income, and Treasure Hunter select Configurable. All named new presets route native Junk to the counter. Additional provider presets must contain a complete supported configuration; no cross-category fields or content grants.

## 4. Recommended engine and transition rules

**Execution mode, selected preset key, and display match are separate.** Legacy custom tuning displays `Enhanced · custom legacy tuning` rather than switching engines. Editing a new-path field while Legacy is active opens an explicit conversion preview; cancel keeps Legacy unchanged. New-mode manual edits display Custom without deleting valid provider metadata until the user commits the edit.

| From / action | Recommended result | Progress/state rule |
| --- | --- | --- |
| Old valid save, no new record | Legacy, existing configuration | Do not initialize new RNG/progress or rewrite loot v1 |
| Legacy tuning edit | Legacy; retain custom tuning | Existing legacy semantics, no new-path migration |
| Legacy → a new preset | Configurable after preview/admission | Initialize new progress once; freeze legacy-only progress |
| Configurable → another new preset/Custom | Same engine, validated new config | Retain progress/RNG/remainders/pending identities; no reset or immediate reward |
| Configurable → Enhanced | Legacy, previous legacy difficulty/tuning | Freeze new-only progress; resume legacy state under its existing algorithm |
| Reapply identical config | No-op | No reseed, conversion replay, or progress reset |
| Guarantee lowered below existing dry progress | New interval takes effect | Evaluate at next admitted eligible victory, never pay from a settings action |
| Missing/corrupt/newer records | D3 status policy | No inferred legacy fallback for a known but unreadable new-mode save |

Apply engine/policy changes only at a free-field boundary after the current battle/reward presentation/Wayne action has settled. Freeze inactive engine progress; no transfer, duplicate entitlement, or simultaneous victory credit. Frozen legacy pending rewards may retain legacy replacement semantics when that engine resumes; new pending entries never reroll merely because settings changed. At most one engine handles any battle. Mid-battle edits can be previewed but cannot commit.

Shared wallet, Catalog/permit ownership, and `charm_left` remain authoritative in their existing record. Do not duplicate them into the new record. Recommended charm behavior: only an enabled, admitted bonus-item attempt consumes/advances its new-mode duration, once per relevant victory; Legacy keeps its existing behavior. Scavenger/Lucky Find/charm ordering and consumption are explicitly part of policy review, not silently settled by this draft.

## 5. Recommended storage, cap, redemption, and pricing policies

For a manageable first slice, recommend allowing new bonus income/redemption only with native routing set to Counter. Items routing is supported only with new added income/automatic redemption off; otherwise reject Apply with a clear reason. Bonus non-currency items can remain enabled. This intentionally narrows the first implementation; accepting it requires reconciling D1's unrestricted Custom table. Do not silently disable fields to make the combination valid.

Items routing leaves existing wallet funds intact and available to existing spending/Wayne actions while Economy is active. It does not empty the wallet or create inventory stacks. Explicit Take out Junk moves only what fits. The existing master economy-off behavior remains a separate legacy compatibility operation. `junk.enabled()` continues to mean Economy availability, not “added income on”; do not change v1 semantics for consumers.

Recommended new-path cap policy: commit each native routing/bundle conversion in full or leave its source item intact; a generated new payout that cannot fit is retained once in the bounded currency pending slot. Stop admitting further extra-income attempts while that slot is occupied. Notify the player that income is paused until capacity is freed; never accumulate an invisible unbounded debt. Legacy saturation remains unchanged. Preserving already generated value does not promise infinite new income at a full wallet; backpressure is visible and occurs before another attempt.

Recommended redemption consent: Apply's preview states that enabling automatic redemption also covers currently held eligible inventory/trunk bundles, at the displayed values. Explicit Apply authorizes later safe-field sweeps; the setter does not consume anything. A preset adding redemption must display this consequence even if the field is in a collapsed subpage. No additional per-item popup. Items remain untouched if full credit cannot commit. This resolves REV-04 as a draft recommendation requiring sign-off, not an implementation.

Pricing: when entering new mode, capture the **base** legacy price percentage (Relaxed 75 / Normal 100 / Grind 125), excluding Bargain. New reward presets leave it unchanged. Equipped Bargain is evaluated at the actual price request using existing rounding. Returning to Enhanced restores the price implied by its retained legacy difficulty; disclose a possible price change in that transition preview. If the user wants current prices preserved even on return to Enhanced, a separate independent legacy price policy is necessary; that alternative changes the scope and remains a decision. New price sliders/extensions are deferred.

## 6. Scoped menu map and migration requirement

Proposed Economy main page: Current setup/engine; concise active or blocked summary; Junk balance; Choose preset/Preview/Apply; links to Junk Storage, Battle Income, Bonus Drops, Bundle Redemption, Wayne, and Advanced Legacy. Add a provider-adjustment summary only when contributors are active. Keep actual Catalog/Requisition/Dismantle/Rebuild actions and Aya's UI rules in place.

| Page | Content |
| --- | --- |
| Junk Storage | Native route, retained wallet explanation, supported-combination errors, link/action to existing withdrawal |
| Battle Income | Fixed ordinary/boss values, payment chance, performance and empty-steal controls; explain active equipment/contributors |
| Bonus Drops | Item and bundle families; separate chances/guarantees; pending/admission status |
| Bundle Redemption | Super/Duper auto switches, current/inactive values, existing-holdings conversion explanation |
| Wayne | Existing hand-in preference; unchanged refund toggle remains clearly separate and off by default |
| Advanced Legacy | Retained Difficulty and legacy tuning, scope/coupling help; new-engine controls are not aliases for these values |
| Inventory | Existing display-only Junk counter; link to Economy's canonical routing page |

**Newly confirmed migration risk:** current menu persistence constructs `page/label` keys. Moving `Economy/Wayne hand-in` or `Debug/Loot tuning/Rare base %` changes its saved key even if its backing variable is unchanged. Translated display text must not become identity.

Before moving any ordinary persisted row, implement a reviewed explicit stable-key/legacy-alias mechanism in the host menu layer, or retain its old registered identity while changing only presentation through a supported adapter. Neither facility is claimed to exist today. Alias precedence: explicit canonical value first, otherwise valid old key; preserve unrelated/unknown INI lines and don't repeatedly reimport aliases over later edits. Live per-save controls must use the owning save-state adapter, not ordinary global INI rows. Test migration from custom non-default INI values. Stage the full top-level reorder until this works.

Preview has a generation/version token and is observational: no callbacks that award/roll/consume, no RNG advances, no progress reset. Apply revalidates config, provider, save status, capacity, current safe boundary, and the token. Failure leaves all settings and holdings unchanged. Returning from subpages restores selection/scroll; invalid removed rows fall back safely. No automatic reset to row zero should apply a provider preset.

## 7. Resource and module inventory for this slice

| Responsibility | Owns | Lifetime/cleanup |
| --- | --- | --- |
| Wallet/routing | Balance adapter, transfer preflight, source item identity | Existing saved wallet; transient transfer descriptors released after commit/failure |
| Reward policy/income | Config snapshot, per-battle engine choice, numeric result | Bounded operation lifetime; no borrowed UI buffer pointers |
| Bonus generation/delivery | New progress and three typed pending slots | D3 per-save state; no arbitrary heap backlog |
| Presets/settings | Canonical config, provider keys, validated draft preview | Copied bounded metadata; never own game items |
| Extension resolver | Init-time owned registration records, ordered contributors | D6 fixed capacities, session lifetime, no hot unload |
| Menu/presentation | Short-lived view state and translated strings | Borrow pack strings only per documented lifetime; bounded scratch, no permanent copies per open |
| Save host adapter | Admission/status and coherent committed image | Host-owned; D3 prerequisites, no duplicate per-feature serializer |

## 8. Decisions, acceptance references, and implementation readiness

Draft recommendations needing approval: cross-engine freeze/resume and shared charm policy; Counter-only extra income restriction; full-credit/deferred-income cap behavior; preview-authorized existing-bundle conversion; return-to-Enhanced price behavior; D3 layout/limits; D6 composition. Exact new UI numeric ranges/named levels and target hardware budgets remain open. These are not new balance changes.

Required checks belong in D4: current-default parity; legacy custom INI migration; every engine transition and repeat Apply; full bag/trunk/cap cases; provider missing/disabled; no preview effects; old/new/corrupt/unsupported records; price/Bargain transitions; independent inventory display; local two-provider API examples; frame/memory and leak checks.

This creates the scoped inventory and candidate menu map, addressing REV-02–05, 07, 09–12. [D4's validation plan](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Validation and Playtest Record.md>) now exists with no executed results. This does **not** close G0–G4: actual implementation target, policy sign-off, save-host prerequisites, accepted budgets, and execution evidence remain needed. No game code or saved state changed.

## 9. Custom content, equipment effects and shop control inventory

Added October 31, 2026; candidate follow-up to D1 §20, not observed or implemented controls. Historical A–D source observations remain baseline-specific. Save-host prerequisite results now exist in D4; they do not validate this new content slice. Read with D3 §10, D6 §10 and D4 §15. CONTENT/EFFECT/SHOP checklist gates remain open until accepted and verified.

Review disposition: D6 §11 now binds recommended registration, ownership and dependency rules for MCR-01–03, including optional adapter batches so missing Economy does not disable independent content. Later October 31, D6 §12 binds native identity mapping for this inventory (equipment pool record + fingerprint, sort/move/equip stable, destructive native paths vetoed for custom records) and D3 §11.5 binds core-off/equipped behavior (custom gear keeps playing as its native archetype; discard/sell/dismantle/rebuild/tune-up refused while its provider is missing). Persistent custom gear saves into the extension store of D3 §12 (MCR-04X, design only). D6 §14 binds discovery for the `effects.inspect` / Catalog and `shop.browse` rows below: the Catalog owner keeps Seen/Unlocked facts; undiscovered entries are `????` with generic help/quote/error text; offers sharing an entry show owned once unlocked. MCR-07–09, 11 and 12 remain open. D0 Section 5 M and D7 track the distinction between design resolution and unimplemented native support. No new native-path audit was performed.

### Delivery slices and module boundaries

| Slice | Scope | Entry gate |
| --- | --- | --- |
| E — Shared content and instances | Register native-compatible custom items, weapons and armor; inventory/storage/equip/use and persistence adapters independent of Economy | Audit fixed-ID assumptions; approve identities, supported archetypes, schemas, capacity and missing-content policy |
| F — Equipment effects and Catalog | Stable effect definitions, runtime/equipment actions and discovery-aware Catalog adapter | E's relevant identity/instance contracts; reviewed stacking, slots, native adapters and effect readiness |
| G — Economy shop contributions | Multiple providers' item/equipment offers; separately supported effect-consumable or installation offers | Delivery/installation prepare/commit capability and coherent payment/save boundary; no unsupported service callbacks |

Each slice may be delivered separately. Custom content does not require Economy; catalogued effects do not require shop sales. Content definitions do not register native drops, crafting, Requisition or Dismantle/Rebuild behavior automatically. Adapters belong to those feature owners. Wardrobe buying, new combat mechanics, expanded slot limits, unrestricted price controls, hot unload and Randomizer activation remain outside these slices.

### Proposed user controls and state ownership

The keys below identify proposed logical actions/views, not published INI names or API identifiers. Inventory/equipment state and purchases are save-specific. Provider enablement remains under the existing restart-based mod manager; opening a view must not enable a mod or allocate a persistent record.

| Logical control / location | Kind and allowed behavior | Owner / persistence | Dependency and refusal behavior |
| --- | --- | --- | --- |
| `content.inspect` / existing inventory and storage views | Inspect resolved name/icon, quantity, stats and supported actions; scroll long data | Presentation session; instance owner persists actual item state | Missing icon uses generic icon; unresolved gameplay content becomes read-only placeholder |
| `content.use` / inventory | Explicit use with supported quantity/target | Item behavior + inventory transaction | Disabled for unresolved content, invalid target or unsaveable result; no consumption on failure |
| `equipment.equip` / Change Weapon/Armor | Select compatible resolved instance; existing preview/confirm pattern | Equipment owner; saved instance/equipped reference | Recheck target and required effects; no unknown native ID passed to vanilla routines |
| `content.transfer` / storage | Lossless supported move with inventory/storage bounds | Inventory/storage owner | Unresolved transfer disabled initially; later support requires opaque preservation and capacity validation |
| `effects.inspect` / equipment and Mod Catalog | Weapon/armor selection, icons/help, independent effect-list scrolling | Catalog presentation; discovery belongs to current discovery owner | Undiscovered entries remain `????` with hidden descriptions/effects; missing discovered provider shows unavailable status |
| `effects.install`, `effects.remove`, `effects.transfer` / supported Catalog actions | Confirm explicit target, slot, effect, cost/consumption and eligibility | Equipment action owner plus wallet/item owners | Validate built-in/removable distinction, conflicts, discovery and capacity; preserve existing removal/refund rules |
| `shop.browse` / contributing shop's existing entry point | Provider offers, quantity/stock and displayed final price | Shop view; offer registry is session metadata | Hide undiscovered offers or show approved locked presentation without spoilers; unavailable discovered offers cannot be bought |
| `shop.quote`, `shop.confirm` / purchase panel | Preview then explicit purchase; select target for supported installation service | Shop coordinates inventory/equipment, wallet and stock owners | Stale price/target requires refreshed confirmation; failure explanation names funds, capacity or dependency issue |
| `content.compatibility` / load warning and affected item help | Provider/dependency status and nondestructive recovery instructions | Compatibility/persistence owners; bounded diagnostic session | No automatic delete, refund, reroll or content conversion |
| `content.fallback_confirm` / load recovery, only if supported | Explicit temporary equipment fallback with original instance retained | Equipment/runtime recovery owner; persistent recovery state only if approved in D3 | Block resume if required behavior cannot be made safe; never silently replace later player equipment choices |

Do not add an all-content unlock, free grant, reset-stock, delete-unavailable or auto-convert button to normal menus. Such actions need separate authorization/contracts. Displayed item/offer metadata must be translated through stable keys with bounded fallback text; current saved identifiers and menu settings remain independent of language. Existing Inventory/Junk display ownership and category defaults remain unchanged.

### Missing-content presentation and compatibility policy

Distinguish absent provider, disabled provider, unavailable API/effect, unsupported saved schema, missing definition and missing presentation asset. Keep legitimate saved identity and quantity even when display metadata is unavailable. Show a generic, non-spoiling placeholder with provider information in help rather than inventing an item name or executing unknown effects. An unavailable installed effect keeps its slot and payload; the ordinary item UI must not offer destructive overwrite/removal.

Superseded for equipment by D3 §11.5 (October 31): unresolved custom gear keeps working as its native archetype and can be used, equipped, moved, sorted and stored; only destructive actions are refused. The paragraph below remains the rule for any other class until designed. Recommended initial conservative rule: unresolved instances remain in their existing logical inventory/storage capacity and cannot be moved, sold, consumed, combined, dismantled or rebuilt. This avoids introducing free quarantine storage. If existing native capacities cannot represent them safely, refuse the affected load/operation until a separately reviewed bounded quarantine design exists. D3 must approve encoding and equipped fallback before implementation; this is a candidate UX policy, not proof of native support. Compatible reinstall restores resolution without purchases/grants. A missing required progression/coordinator dependency blocks resume rather than silently substituting content.

### Mod on/off controls (D3 §14)

| Control | Where | Owner / layer | Behavior |
| --- | --- | --- | --- |
| Missing-mod notice | Dialog at the first safe field frame after a load | Save host (S) | Lists owners of saved data that are not running; one OK button. Manage mods → "Missing-mod notice", default on |
| Save-slot warning | Native save flow, after confirming an existing slot | Save host (S) | New slot / Overwrite / Cancel, default New slot; once per slot until the next load. Manage mods → "Warn before overwriting", default on. Needs a safe native hook point (audit) |
| Custom items page | F1, present only when the loaded save has a custom-item ledger | Content core (C) | Lists non-ACTIVE custom items with owner, state and location |
| Convert to normal item | Custom items page, per item | Content core (C) | Confirmed and permanent, default No; UNAVAILABLE/UNCERTAIN only; not in battle or cutscenes; no bulk or automatic form |
| Remove record | Custom items page, per entry | Content core (C) | ORPHANED entries only; same confirm |

These are the separately designed contracts the rule above requires: nothing destructive is added to the game's own item menus.

### Required current-branch audit and resource inventory

For every path record actual file/function, fixed-ID/index assumptions, class/slot limits, current save representation, owning module, supported adapter and verification case. Required paths: inventory lists, storage/trunk, use/consume/combine, equip/unequip, stats/ammunition/effects, combat and animation/model selection, pickups/drops, Catalog install/remove, pricing/shop stock, Dismantle/Rebuild/salvage, native serializer, editor and recovery. No new source audit is claimed by this document update.

Registry owners copy bounded definition/offer metadata, retaining only documented session-lifetime callbacks/assets. Instance owners own mutable per-save state; menus borrow generation-checked views and release previews on close/error. Assets own loading/retirement and generic fallbacks. Shop owns transient quotes; transaction owners release prepared reservations on cancel/failure. No per-frame provider discovery, unbounded retained views or provider-owned pointers in saves.

Before coding bind D4 PB-10–14, actual limits and supported actions. Exact menu labels, archetypes and native adapter locations remain review items; retaining existing navigation and rule semantics takes priority over speculative new pages.

## 10. Standalone Wardrobe, Bestiary and staged Economy split

November 1 recommended specification, documentation only. Read D9 for the source-check limits and D8 for pack details; controlling persistence/API/validation contracts are D3 §16, D6 §15 and D4 §16. This is a separate extraction scope, not permission to implement all content or change balances. D8's direct-buying and acquisition choices remain product decisions; the existing no-buying Wardrobe UI baseline remains until explicitly revised.

Pre-implementation review: **D9 §8 / SPL-01 is phase 1 design-resolved; SPL-02–09 remain OPEN**, including feature activation/alias compatibility and viewer/resource authority. The control tables below are draft requirements, not resolution of the conflicting policy cases. D0 Section 5 R tracks dispositions before the applicable extraction slice.

| Feature owner | Required support | Own controls/state | Optional consumer/adapter |
| --- | --- | --- | --- |
| Wardrobe (`pe_wardrobe`) | Shared host/model helpers | Registry/packs, preview/wear/default appearance, owned outfits, explicit acquisition choice, feature-local debug actions | Acquisition adapter may request unlock purchase; no required Economy/Bestiary dependency |
| Bestiary (`pe_bestiary`) | Shared host/model helpers | Creatures, encounters/kills/earned discoveries, viewer/filters, feature-local debug actions | Paid-information adapter; tracking and earned discovery work without wallet or Wardrobe |
| Junk wallet/routing owner | Save/inventory support | One balance, routing and validated credit/spend | Rewards, shops and counter presentation consume its capability |
| Economy rewards owner | Wallet plus relevant inventory/save actions | Enhanced/configurable income, drops/bundles, saved reward progress | No costume/creature viewer dependency |
| Catalog owner | Equipment/effect/persistence support | Entry discovery, eligibility, install/remove rules | Payment adapter; no dependency on enhanced battle rewards |
| Shop/Workshop owners | Required payment/delivery services for each action | Offers, quote/stock/pricing and NPC entry points | Optional Wardrobe/Bestiary/Catalog adapters |

Wardrobe and Bestiary become separately buildable/enabled mods. Wallet/rewards/Catalog/shop rows are owner boundaries first; final Economy folder/build-toggle names are not selected here. Share codecs and viewer helpers as libraries; do not require another feature mod merely to reuse a model viewer. Native costume and creature pack registration must separate or check capability availability rather than linking both features unconditionally. Keep a simple aggregate/default build option for users.

| Proposed control/action | Persistence / standalone behavior |
| --- | --- |
| Manage mods / Wardrobe, Bestiary | Independent explicit settings; old Collection setting supplies one-time fallback only when the new canonical key is absent |
| Wardrobe / browse, preview, wear | Works alone under the accepted acquisition policy. No payment controls in the baseline viewer; optional Workshop purchasing stays separate |
| Economy / Costume unlock rules | Phase 1 optional toggle, default on. Economy off/absent or toggle off makes all installed compatible costumes available without permanent grants. Economy on + toggle on preserves current unlock/purchase eligibility; unavailable payment is not an opt-out. Economy owns the sole policy setting (D8 §12) |
| Bestiary / browse and earned research | Existing reveal thresholds and spoiler rules retained; no payment provider disables only paid research, not tracking or earned unlocks |
| Wallet / routing and Inventory counter display | Storage/credit policy separate from extra rewards and display. No second balance, no automatic conversion or newly free shop actions |
| Rewards / presets | Enhanced stays default; disabling rewards does not implicitly reset wallet, routing, profile unlocks or Catalog facts |
| Debug / Wardrobe and Debug / Bestiary | Reset/lock actions affect only their owning feature. Combined legacy reset is an explicitly labelled compatibility action, never triggered by migration/toggles |
| Integration status | Explain missing payment/feature/pack and required restart; metadata/query does not enable providers or grant facts |

Mod absence from the build, disabled mod, unavailable capability and missing content are different statuses. Required unsupported actions are unavailable, not silently free. Multiple acquisition adapters require explicit selection or exactly one eligible default; never use registration order. Changed adapter/price invalidates previews and requires renewed confirmation.

Migration and scope gates: D3 §16 owns feature profiles, retained mixed records and import precedence; D6 §15 owns compatibility publishers and adapters. Do not move persisted page/label keys without canonical aliases under §6. D8 pack-reader work follows the extraction baseline; new direct buying, multi-currency, hot unload and changes to research/price curves remain out of scope. No current-branch full symbol/build audit is claimed here.

### Phase 1 decision — November 2

D8 §12 is the controlling acquisition table: Wardrobe owns viewing/equipping and saved ownership; Economy optionally restricts access using its default-on Costume unlock rules toggle. There is no phase 1 Wardrobe acquisition selector. Explicit toggle off affects only costume restriction; it does not disable the wallet/rewards/shops globally. Missing/incompatible payment while Economy's rules are on blocks the paid action without silently making every costume free. Re-enabling restrictions on an unowned worn costume uses an explained safe appearance fallback while retaining the requested key and owned collection; no automatic grant/charge or unsafe model swap.

Phase 1 preserves existing Economy-enabled rules/prices and the no-buying viewer. Progression/challenge/acquisition presets are later Economy work; prepared-skin importing is a separately staged Wardrobe feature. Prior wording leaving these phase 1 defaults open is superseded. SPL-01's phase 1 design conflict is resolved by this table, not by implementing anything; other SPL findings and payment gates remain open.
