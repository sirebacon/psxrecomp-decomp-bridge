# D9 — Standalone mod boundaries and optional integrations

Date: November 1, 2026. Status: recommendation and open-decision review; documentation only. No game code, profiles, saves, prices, defaults or build settings changed. No implementation or runtime tests performed.

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
