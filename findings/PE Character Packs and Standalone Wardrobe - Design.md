# D8 — Character packs and a standalone Wardrobe

Date: November 1, 2026. Status: recommended design and requirements, documentation only. No code, asset, profile or save changed.

Scope update, November 2: focus drop-in importing on **Wardrobe player skins already prepared in the supported PE skin/pack formats**. Enemy/Bestiary pack importing and NPC/enemy replacement are deferred, including source-specific integration from other decompiled games. This does not cancel the standalone Bestiary split or its existing creature registration/tracking. Section 11 controls the current importing scope.

Requested by the user:

1. "a file format with downloadable character replacements/additions", following whatever is popular for PS1-era games such as Resident Evil and BioRand;
2. "split the wardrobe to its own thing", so Economy uses the Wardrobe for paying while anyone can use the Wardrobe.

Read with the [master checklist, D0](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets and Menu Organization - Master Checklist.md>) (Section 5 P), the [versioning policy, D3 §15](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Persistence and Migration Design.md>), the [API contract, D6](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Mod Extensions - API and Cooperation Contract.md>), the model-swap research (`findings/pe-model-swap-research-2026-10-19.md`) and the Workshop Overhaul discussion document.

## 1. What exists today

Read from `D:/Recomp Games/pe-requisition` (branch `feat/requisition-list`, based on `mine/feat/mod-ui-improvements`), where the Wardrobe browser lives. Re-audit on the implementation branch.

- **Wardrobe is inside `pe_collection`**, beside the Bestiary: `mods/pe_collection/pe_wardrobe.c`, `pe_wardrobe_menu.c`, `pe_skin_loader.c`, `pe_profile.c`.
- **Costumes come from the `costumes` v1 service** (`mods/host/pe_services.h:119–147`, `PeCostume`). Three kinds:
  - one of the game's player bundles (bank 10/12/13), with an optional room pack;
  - a skin folder (bank -1, `bundle`);
  - a provider's own loader (`load`).

  Keys are stable and saved in the profile ("pe1/tshirt", "re2/claire"), and must never change.
- **A skin is a folder of the game's own formats**, `pe_skins/<folder>/` beside the preferences (`pe_skin_loader.c:1–27`): `texture.bin` (TIMs), `model.bin` (player bundle), `day1-8.bin` (animation rows), optional `rooms.bin` (retargeted room animations, `PERR`) and optional `meta.bin` (`PEMT`, the weapon hand part). The bridge's `tools/pe_assets/build_skin.py` builds them from the player's own disc. Missing files hide the costume.
- **Buying spends Junk inside the Wardrobe.** `pe_wardrobe.c:132–136` calls `pe_col_spend`, which uses the `junk` service (`pe_collection.c:21–31`), and refuses with "Turn on Junk economy to buy" when Economy is off. Price is a Junk number in `PeCostume.price` (the user-kept curve: 25 extras / 50 outfits / 100 supporting / 250 main / 400 Melissa).
- **Ownership and the worn costume live in the profile, not in saves.** They are kept across every game in `pe_collection.ini` (text: `costume <key>`, `worn <key>`; `pe_profile.c:9, 80–94`), shared with Bestiary records, with a one-time import of the psxrecomp `pe_collection.dat`. The file has no format version line.
- **The `wardrobe` v1 service** (`PeWardrobeApi`: count/name/price/state/pick/preview) lets Wayne's Workshop show and sell costumes. `pick` buys or wears.

Shortcomings for the two requirements: there is no downloadable unit beyond a bare folder, with no metadata, license, version or portrait; and the Wardrobe cannot be used without Economy, because buying is the only way to own a priced costume.

## 2. What PS1-era communities use

Researched November 1, 2026:

- **BioRand** (Resident Evil 1–3 randomizer):
  - Since v3.3.0 it ships characters as **datapacks**: a plain `.zip` holding a `data/` folder tree, plus `LICENSE` and `VERSION` files, with **no manifest** ([biorand/classic-data `create-pack.py`](https://github.com/biorand/classic-data)).
  - **One folder per character**, named `base.game` or `base.game$variant` (for example `leon.re2`), inside a fixed per-game path such as `data/re2/pld0/leon.re2/`. That folder holds the game's own formats (`PL00.PLD`, weapon `PL00Wxx.PLW`) plus a `face.png` portrait ([classic-data `data/re2/pld0/leon.re2`](https://github.com/biorand/classic-data/tree/master/data/re2/pld0/leon.re2)).
  - Voices and hurt sounds sit in parallel `data/voice/<character>/` and `data/hurt/<character>/` folders, and voice file names carry condition tags.
  - A user content folder `%APPDATA%\biorand\data` overlays the built-in data ([BioRand changelog](https://github.com/IntelOrca/biorand/blob/master/CHANGELOG.md)).
- **Classic REbirth** (RE1/RE2 PC patches): mods are archives in the game folder named `mod_*.7z` that overlay loose game files, chosen from a mod loader ([Nexus example](https://www.nexusmods.com/residentevil1996/mods/84)).

**The common pattern:** a zip of loose files in a fixed folder layout, one folder per character named by convention, assets in the game's own formats, a portrait PNG, a license, no code, and the user's folder overlaying built-in data. Our skin folders already match the "game's own formats per folder" part.

## 3. Pack format v1 (`.zip`, BioRand-style)

### 3.1 Layout

```text
<pack-id>-<version>.zip            plain zip: stored or deflate only, no encryption, UTF-8 names
  pack.json                        required, small manifest (below)
  LICENSE                          required: the author's terms for redistribution
  VERSION                          optional, BioRand convention; pack.json is authoritative
  characters/<base>.<source>[$<variant>]/
      character.json               required: display data and fitting
      texture.bin model.bin day1.bin … day8.bin    the current skin files (§1), unchanged formats
      rooms.bin meta.bin           optional, as today
      face.png                     optional portrait (64×64 recommended) for the Wardrobe list
      preview.png                  optional larger picture for pack pages and the F1 detail row
  outfits/<base>.pe1$<outfit>/     optional: room packs for the game's own outfits (rooms.bin only), as today
  voice/<base>.<source>[$<variant>]/   reserved, BioRand-style; ignored in v1
  npc/<target>/                    reserved for NPC/enemy replacement (§3.6); ignored in v1
  source/                          ignored by the game: authors' working files
```

Folder names follow BioRand's convention so modders recognize them. Examples: `claire.re2`, `claire.re2$biker`, `daniel.pe1`, `aya.pe1$swimsuit`. Characters are matched only by folder name, never by order.

### 3.2 `pack.json`

```json
{
  "format": 1,
  "id": "example-re-classics",
  "name": "RE Classics",
  "version": "1.2.0",
  "author": "Example",
  "license": "CC-BY-4.0",
  "min_wardrobe": 1,
  "kind": "assets"
}
```

- `id` is canonical lowercase `[a-z0-9-]`, at most 31 bytes, and permanent. It is the namespace of every key in the pack (D6 §11.1).
- `kind` is `assets` (compiled files present) or `recipe` (§5).
- `min_wardrobe` is the lowest Wardrobe pack reader that may load the pack (D3 §15 `min_reader`).
- Unknown fields are ignored and preserved by tools.

### 3.3 `character.json`

```json
{
  "name": "Claire (RE2)",
  "group": "Resident Evil",
  "tier": "main",
  "revision": 1,
  "replaces": null,
  "accepts_previous_keys": []
}
```

- `tier`: `extra`, `outfit`, `supporting`, `main` or `special`, the user-kept curve. **Packs state a tier, never a Junk price.** Prices belong to Economy (§4.3).
- `replaces`: `null` makes the costume an addition. `"aya"` lets the player choose it as the default appearance, through a Wardrobe setting rather than by overwriting game files. NPC targets are reserved for v2.
- `revision` follows D3 §15.5. `accepts_previous_keys` covers renames.
- The costume key is `<pack id>/<folder name>`, for example `example-re-classics/claire.re2`. It is permanent and stored in the profile.

### 3.4 Installing

- **Location:** `<preferences>/packs/`. Each pack is either the `.zip` itself or an unzipped folder with the same layout; both are supported, like Classic REbirth archives and BioRand's user data folder.
- **Scan:** at startup only (restart lifecycle, D6 §11.5). The Wardrobe lists packs, characters and refusals, with reasons, on an F1 "Packs" page.
- **Existing skins:** the current `pe_skins/<folder>/` folders keep working as an implicit local pack, with keys unchanged. Nothing has to be repacked.
- **Same pack twice:** if two copies of one pack `id` are present, only the higher `version` loads and the other is listed as a duplicate.
- **Clashes:** two packs that share an `id` but have different authors are both refused, following D6 §11's duplicate rule.

### 3.5 Safety and limits

- **Data only.** A pack may contain no code, scripts, DLLs or executables; unknown file types are ignored. This matches Fluffy-style "file mods only" managers.
- **Zip hardening:** reject absolute paths, `..`, drive letters, symlinks, duplicate names, encrypted entries, and size or ratio bombs. Every file is read into bounded memory; the existing `PE_FILE_MAX` is 4 MiB per file.
- **Pack and character limits:** whole pack ≤ 64 MiB; ≤ 64 characters per pack; ≤ 256 costumes in total (the current `PE_MAX_COSTUMES`).
- **Validation before listing:** each character's binary files go through the same structural checks as `build_skin.py`'s checkers (`check_skins_struct.py`, `check_skins_gun.py`) before the character is listed. One bad character is refused alone; the rest of the pack loads.
- **No game file is overwritten,** on disk or in memory. Swaps keep using the current pointer-only method (`pe_skin_loader.c:14–17`).

### 3.6 Scope v1 and later

| | v1 | Later (each needs its own research and review) |
| --- | --- | --- |
| Player additions (new Wardrobe costumes) | Yes | — |
| Player replacement (default appearance) | Yes, as a Wardrobe setting | — |
| Room packs for the game's outfits | Yes (`outfits/`) | — |
| NPC / enemy replacement | Reserved folder | Needs NPC model-swap research; Bestiary viewer reuse |
| Voices / hurt sounds | Reserved folder | PE has little voiced dialogue; low priority |
| Importing common 3D formats (glTF) | No | An authoring tool converting glTF to PE's formats for original characters |

## 4. Standalone Wardrobe

### 4.1 Module split

| Module | Owns | Depends on |
| --- | --- | --- |
| **`pe_wardrobe`** (new mod) | Costume registry (`costumes` service), pack reader (§3), skin loader, wearing and preview, ownership and worn costume in its own profile file, F1 Wardrobe and Packs pages, the acquisition policy (§4.2) | Host only; model stage for previews |
| `pe_collection` | Bestiary only (plus its model viewer) | Host |
| `pe_economy` | Prices, Junk payment, Wayne's Workshop Wardrobe row | `pe_wardrobe` **optional** |
| Other mods (randomizer, challenges, packs with code) | Register costumes and grant unlocks through the service | `pe_wardrobe` |

Dependencies point one way: Economy uses the Wardrobe; the Wardrobe never calls Economy. The Wardrobe keeps working with Economy off, with Collection off, or with only the Wardrobe on.

### 4.2 Acquisition policy (Wardrobe setting)

Phase 1 decision, November 2: Wardrobe alone makes every installed compatible costume available for preview/wearing. **Economy owns the optional "Costume unlock rules" toggle, default on**; when Economy and that toggle are on, preserve current unlock/purchase rules. Toggle off, or Economy disabled/absent, means unrestricted access without permanently granting ownership. There is no second Wardrobe-owned acquisition switch in phase 1. Section 12 supplies the controlling state/transition rules.

Existing owned costumes stay owned in every mode. Feature-owned validated reward/grant integrations remain possible under D6, but new progression/challenge acquisition policies are later work, not part of the extraction baseline.

### 4.3 How Economy pays (inverting today's call)

- The Wardrobe exposes, in a proposed `wardrobe` v2: list/name/tier/state/preview, `grant(key, why)`, and `register_shop(shop)`. A shop supplies `price(key)` and `buy(key)`.
- Economy registers as the shop:
  - its `price` maps tier → Junk with the user-kept curve (25/50/100/250/400), then applies its preset and Bargain;
  - its purchase action coordinates wallet and ownership through the supported cross-store protocol; spend-then-grant alone is not sufficient (D3 §16.4; MCR-08/09).
- Supported external purchase entry points use the same acquisition adapter, so prices and refusals agree. Phase 1 adds no buying controls to the Wardrobe viewer (§12).
- With no shop registered, the Wardrobe page shows no prices; the policy is "Everything unlocked".
- **Compatibility:** `costumes` v1 and `wardrobe` v1 stay published by `pe_wardrobe` for existing providers and the Workshop mockup. Existing v1 numeric prices must not be silently reinterpreted as a different tier price; newer tier descriptors use their own negotiated contract.

### 4.4 Profile file and migration

- The Wardrobe gets its own profile, `pe_wardrobe.ini`, with a first line `format 1`. It holds `costume <key>`, `worn <key>`, `default <key>` (player replacement) lines; Economy owns the phase 1 restriction toggle (§12), not this profile.
- **First run:** copy `costume` and `worn` lines from `pe_collection.ini` into it, and record `imported pe_collection.ini`. The lines stay in `pe_collection.ini` untouched, so an older build still finds them (downgrade keeps working, D3 §15.8).
- **Later runs** use only `pe_wardrobe.ini`. An older build's later purchases in `pe_collection.ini` are merged by the same import at the next start (ownership only ever grows).
- Add `format 1` to `pe_collection.ini` too, and list both files in the D3 §15.6 version table. Profile files follow the same versioning rules as saves.

### 4.5 Missing packs and mods off

- **Pack removed:** its costumes are hidden (current `available()` behavior) and ownership stays in the profile. If the worn costume is missing, Aya wears her own clothes for the session; `worn` is kept, so it comes back when the pack returns.
- **Wardrobe mod off:** the game uses its own outfits and the profile stays untouched. No save data is involved, so the D3 §14 notices do not apply.
- **Economy off:** the policy falls back to "Everything unlocked" for the session without changing the setting. Bought costumes stay owned.

## 5. Distribution and copyright rule

The format can be downloaded and shared, but **what may be shared depends on where the art came from**:

| Pack content | Shareable? | Pack kind |
| --- | --- | --- |
| Original models made by the author | Yes, under the author's `LICENSE` | `assets` |
| Models from Parasite Eve's disc (Daniel, Maeda, outfits…) | **No compiled files.** Share a recipe that rebuilds them from the player's own disc | `recipe` |
| Models from other commercial games (RE2 Claire…) | The author's responsibility under their own license; the project ships and hosts none | `assets` |

- A **recipe pack** contains `pack.json`, `LICENSE` and per-character `character.json` + `recipe.json`. The recipe names the room, actor and fitting parameters that `build_skin.py` uses. Running the bridge's builder against the player's disc produces the compiled files locally. This is the same model as the localization project's option B (contributors share instructions, not game data).
- The project repositories and releases never include game-derived renders, skins or compiled files. The bridge repository is public, and its game-derived output stays git-ignored, as today.

## 6. Versioning

Under D3 §15:
- pack `format` and `min_wardrobe`;
- character `revision` and `accepts_previous_keys`;
- costume keys that are permanent and never reused;
- profile `format` lines.

Pack `version` is for people: it orders duplicate copies of a pack, but is never a compatibility gate. The skin binary formats (`PERR`, `PEMT`, the TIM/bundle layouts) gain version rows in D3 §15.6 when the pack reader is built.

## 7. Acceptance cases (planned, unrun)

| Case | Setup / action | Expected result |
| --- | --- | --- |
| PACK-01 | Valid assets pack as a zip and as a folder | Same costumes listed, with face portraits; wearing works as with today's `pe_skins` folders |
| PACK-02 | Existing `pe_skins/` folders, no packs | Same keys, ownership and worn costume as before |
| PACK-03 | Malicious zip: `..`, absolute paths, symlink, oversize, bomb ratio, encrypted entries | Pack refused with a reason; nothing written outside memory; game unaffected |
| PACK-04 | One character with a broken `model.bin` | That character refused; the pack's others load |
| PACK-05 | Two versions of one pack; two different packs sharing an `id` | The higher version loads and the other is listed as a duplicate; same-id clash refuses both |
| PACK-06 | Pack removed while its costume is worn and owned | Aya's own clothes this session; ownership and `worn` kept; restored when the pack returns |
| PACK-07 | Recipe pack with and without the player's disc build | Not listed until built; after building, identical to an assets pack |
| WRD-01 | Wardrobe on, Economy off/absent | Every installed compatible costume available; no purchase requirement/prices, wearing works and no owned facts are added |
| WRD-02 | Wardrobe/Economy on, Costume unlock rules on (default) | Current eligible/free/owned/purchase behavior and prices preserved through supported existing entry points; no new buying UI; unavailable payment does not grant unrestricted access |
| WRD-03 | Rules off/on, Economy off/re-enabled, restart with explicit false | Access follows §12; ownership/Junk/other Economy settings unchanged; explicit false persists; ineligible worn skin uses safe explained fallback with requested key retained |
| WRD-04 | First run with an existing `pe_collection.ini` | Costumes and worn imported once; old lines still present; an older build still sees its costumes |
| WRD-05 | `grant` from another mod with policy Shop | Owned without payment; logged with its reason |
| WRD-06 | Wardrobe-only (Collection and Economy off) | Wardrobe pages and wearing work; no service lookups fail |

## 8. Open decisions

1. Recipe packs need `build_skin.py` (Python) on the player's machine. Should the builder ship as a standalone tool, or should the game build from the disc itself later?
2. Should the "Shop" policy also let the Wardrobe page buy directly, or only Wayne's Workshop? The design allows both; the Workshop Overhaul document's open questions decide this.
3. Does the project host a pack index (for example a list on GitHub), or only document the format and leave hosting to the community?

## 9. Disposition

These are recommended requirements and design only. Implementation is a separate unit, after the user approves:
1. split `pe_wardrobe` out of `pe_collection` with the profile migration;
2. add `wardrobe` v2 and the Economy shop adapter;
3. build the pack reader;
4. add the recipe builder.

D0 Section 5 P tracks it.

## 10. Standalone extraction specification alignment — November 1

Review status: D9 §7 now records **SPL-02–09 OPEN**; SPL-01 is phase 1 design-resolved in §12 across the standalone specifications. SPL-01/02/04/05/09 specifically cover this draft's fallback, import, legacy keys/services, payment and pack conflict/version behavior. The alignment below removes earlier recommendations where explicitly stated, but does not settle those remaining policy/implementation gaps. Pack-reader work is separate from basic feature extraction.

D9's wider split is now specified in D2 §10, D3 §16, D6 §15 and D4 §16 (24 planned STN cases). Those sections control extraction compatibility where this initial draft differed:

- Both Wardrobe and Bestiary are independent features (`pe_wardrobe`, `pe_bestiary`); legacy `pe_collection` is a compatibility build/settings alias rather than a second runtime publisher/writer. Shared model/profile helpers remain libraries.
- Each feature has its own versioned profile. Import once into an absent destination, commit marker with data, and leave legacy source files untouched. No repeated automatic old-profile merge; explicit resets cannot resurrect data. D3 §16 supersedes §4.4's subsequent-merge and source-version-write recommendations.
- Temporary Everything-available policy is not permanent ownership and cannot overwrite a stored choice. Phase 1 defaults and toggle ownership are fixed by §12; the no-buying viewer baseline stays until explicitly changed. Bestiary retains earned research and does not inherit Everything unlocked.
- Existing v1 price/service semantics must be preserved or explicitly refused where unsupported. Do not silently convert an arbitrary v1 numeric costume price to a nearest-tier price. New tier descriptors keep their separate pricing contract; numeric pricing changes are not authorized by extraction.
- Economy/acquisition integration is optional and follows D6 §11/15's adapter identity/selection. New paid profile unlocks require a supported per-save-wallet plus profile-wide commit/recovery protocol under MCR-08/09; spend-then-grant from §4.3 is not sufficient. No new paid API is implemented by this draft.

Pack format/research and user edits above remain as recorded. This alignment does not finalize pack-index hosting, recipe-builder delivery, later acquisition improvements, direct buying or payment atomicity. Code and data are unchanged; tests remain local in `pe-native-debug` and unrun for this update.

November 2 superseding decision: Section 12 now fixes phase 1 acquisition defaults and policy ownership. Earlier references to open first-run Shop/Everything choices or a Wardrobe Unlocking setting no longer control phase 1. Direct buying remains outside the baseline viewer; payment safety and unrelated open decisions are unchanged.

## 11. Wardrobe-only importing focus — November 2

User direction: hold off on enemy importing and focus on installing player skins that have already been formatted for this game. The first drop-in loader must validate compatible prepared skins, not promise automatic conversion from another game's files or arbitrary 3D formats. A model originating in another decompiled game still needs an authoring/conversion step to produce the supported player model, textures, animation/room compatibility and metadata before installation.

Planned player flow: open Wardrobe's content folder, drop in a compatible skin pack, restart, then browse/preview/wear it under the accepted acquisition policy. Keep `<preferences>/packs/` for the proposed ZIP/folder packs and retain existing `pe_skins/<folder>/` compatibility. Add a Wardrobe **Open content folder** action and show the resolved writable path, accepted layouts, restart requirement and validation/refusal messages. Opening this folder must not install, unlock or buy anything. No requirement to search the executable/source tree or overwrite game files.

Maintain per-character structural/animation validation, bounded loading, missing-pack ownership preservation and the pending SPL-04/09 identity/admission decisions. Installing a formatted skin does not guarantee every animation is safe; preview and representative gameplay/room checks remain required. The pack reader, folder-opening action and new UI are not implemented by this document.

Enemy/NPC imports, Bestiary drop-in viewer packs, enemy behavior/encounter replacement and cross-game enemy adapters are **deferred, outside this Wardrobe unit**. Reserved `npc/` data remains ignored in v1. A future enemy-content proposal must separately define source conversion, runtime behavior and whether it adds a viewer entry or changes actual enemies; do not infer that from the skin loader. Existing Bestiary standalone work remains independent.

Validation additions for the future local suite: actual resolved folder discovery/opening, ZIP/folder/legacy-skin installation, compatible versus unconverted foreign assets, clear restart/errors, missing/reinstalled skins without ownership loss, and no enemy-content activation. These extend the relevant PACK/WRD/STN expectations without adding a pass count or executing tests. No code, files in player profiles, assets or balances changed.

## 12. Phase 1 Wardrobe plan — user decision, November 2

**Purpose:** split ownership cleanly while preserving today's Economy-enabled experience. Wardrobe is the viewer/equipment feature; Economy is an optional acquisition-policy provider. This supersedes conflicting acquisition-setting/default wording in §§4/10 and the initial standalone drafts. No game code or runtime behavior is changed by this document.

| Wardrobe | Economy | Economy: Costume unlock rules | Effective behavior |
| --- | --- | --- | --- |
| Off/absent | Any | Any | Native appearance; Wardrobe profile untouched |
| On | Off/absent | Retained, ignored | All installed compatible costumes available; no prices or required unlocks |
| On | On | Off | All installed compatible costumes available; other Economy systems keep their own settings/behavior |
| On | On | On (default) | Current owned/free/unlock/purchase eligibility, prices and unlock sources; no new progression or unlock grants |
| On | On | On, but payment adapter/required protocol unavailable or conflicted | Remain restricted under current eligibility; purchases report unavailable. Failure is not equivalent to the player disabling the rules |

"Everything available" is effective access, not writing every key into the owned set. Installed also means asset/animation compatible under the supported loader; missing/broken skins do not become usable through a policy toggle. Wardrobe owns costume facts and effective query results; Economy contributes a typed optional policy and owns its setting, prices and payment. It never edits the Wardrobe profile directly. The base Wardrobe must not link to concrete Economy code.

Use one stable Economy-owned setting (proposed logical key `economy.wardrobe_unlock_rules`), default true when genuinely absent; explicit stored false survives restart and Economy disable/re-enable. Removing Economy does not rewrite that setting or owned facts. New builds must not infer true merely because the provider returned. Do not add a competing `unlocking everything|shop` preference in new Wardrobe profiles; retain any already-existing draft/test field without reinterpretation until its compatibility migration is explicitly bound. Canonical Economy setting takes precedence once present.

Disabling rules or Economy leaves purchased ownership unchanged. Re-enabling rules restores current earned/free eligibility. If the selected/worn costume is not eligible, explain the restriction and apply a supported native/story appearance fallback at the next safe outfit boundary; retain its requested key and do not grant it, delete it, charge automatically or reset other facts. Re-evaluate before later wearing and do not silently displace a newer explicit eligible choice. Do not swap model pointers mid-battle/unsafe room transition; defer publication and explain if needed. Effective toggle changes invalidate previews/quotes/reservations before further acquisition actions.

Toggle changes are never purchase/unlock/reset actions and cannot alter Junk, discoveries, Bestiary, reward RNG/progress, stock or Economy presets. Bestiary's earned behavior is independent and does not adopt this rule. The existing no-buying Wardrobe viewer baseline remains; current supported external/Workshop purchase entry points retain their reviewed roles. No extra viewer purchase path is added by the split.

**Phase 1 scope:** extract independent Wardrobe/Bestiary responsibilities and their compatibility/migration baseline; make the optional Economy policy reproduce current unlock behavior, with the one opt-out toggle. No new prices, currencies, challenge rewards, progression algorithms or acquisition presets. Prepared-skin pack reader/folder UX remains a separately staged Wardrobe unit (§11), not a prerequisite for preserving existing skins. After phase 1, Economy may add acquisition presets/progression/challenges through separately reviewed policies and the same owner API.

New paid adapters remain blocked by SPL-05/MCR-08/09 until save-wallet and profile ownership can commit/recover safely. Preserve-as-now is not permission to add a spend-then-grant shortcut or to certify untouched legacy paths. Migration, v1 compatibility and concurrency findings stay open. D2 §10, D3 §16, D6 §15, D4 STN-10/11/16/18 and WRD cases bind the phase 1 state table; no tests ran for this update.
