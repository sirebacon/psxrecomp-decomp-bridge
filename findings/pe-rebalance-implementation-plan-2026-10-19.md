# Rebalance — implementation plan and checklist, October 19, 2026

Turns the agreed basis (`pe-rebalance-economy-basis.md`) into mod changes. The user lifted the
build hold on 2026-10-19 ("go down the checklist one by one fixing the rebalances"). Commits stay
local (PE repo `main`; push only on request, to `mine pe-local-work`).

## Where each change goes

All weapon / mod changes live in **`src/mods/pe_mod_effects.c`** (F1 > PE Enhancements > Mod
Effects). Its entry hook on Aya's per-hit damage routine (`Battle_StepEnemyMovement`
`0x80028574`, a0 = target entity) already scales the hit's attack term through the action's power
bonus (`action + 0x00`), and restores every change at the next hit or the next `Battle_Update`
(`0x800299CC`). Each change gets its own row with a vanilla value, so the Rules switch (Vanilla /
Rebalanced / Custom) covers it.

| ID | Change | Mechanism | Row (vanilla -> rebalanced) |
|---|---|---|---|
| R-B | G3A3 (item 0x7D) base attack +45 | per hit: + 45 to the attack term while the equipped gun is a G3A3 | "G3A3 attack bonus" 0 -> 45 |
| R-C | M203 4 (item 0x86) base attack +15 | same, item 0x86 | "M203 4 attack bonus" 0 -> 15 |
| R-A | Attack All: at most 75% of a target's max HP per turn, ordinary fights with 2+ enemies alive, bosses exempt | per hit, Attack All (`turn & 0xC0 == 0xC0`): the target's HP at its first hit this action is the reference; the hit's attack is cut so HP can't fall below reference - 75% max HP; a hit already past the line deals 1; the next battle frame tops HP back to the line if a hit still crossed it | "Attack All crowd cap %" 100 -> 75 |
| R-E (power) | Installed RoF 5 / 7 / 10 (mod effects 3 / 4 / 5 without the built-in bit 0x20): volley 200% of one shot = 40 / 29 / 20% a bullet | per hit: attack term scaled from the game's per-shot % to the new one | "RoF 5 / 7 / 10 volley %" 125 / 126 / 130 (vanilla per-shot 25 / 18 / 13) -> 200 |
| R-E (speed) | follow animation at most 4 frames; per-shot hold removed | during an installed-RoF volley: Aya's animation step scaled by follow frames / 4; the kind's hold byte in `g_BattleActionAnimRows` (`0x800106A4`) zeroed, restored after | "RoF mods: fast volleys" OFF -> ON |
| R-F | Progression guns (2026-10-20, `pe-gun-ladder-2026-10-20.md`): M16A1 (0x79) +25, SG550 (0x7B) +15, M203 (0x83) +20, M203 2 (0x84) +15 | per hit, same as R-B / R-C (table `s_prog_guns`, shared lookup `pe_gun_bonus`) | "Progression gun bonuses" OFF -> ON |
| PE, Econ, Counter, elements | keep | no change | — |

The existing rows "RoF 7 per-shot %" / "RoF 10 per-shot %" (18 -> 20, 13 -> 15) are replaced by
the R-E volley rows (built-in RoF keeps vanilla per-shot values under R-E).

## Checklist (in order)

1. [x] R-B / R-C attack bonuses (rows, per-hit bonus, play-log counter `gun_bonus`). PE `593fbae`.
2. [x] R-A Attack All cap: the game's damage formula replicated (`pe_hit_damage`, from
       `battle/enemy_movement.c`), the power bonus lowered by binary search so a hit can't cross the
       line; per-turn HP references (a new turn after 40 battle frames with no Attack All hit);
       crowd = 2+ enemies alive and no boss; minimum-damage crossings topped up at the next hook.
       Play-log counters `aa_capped`, `aa_topup`. PE `593fbae`.
3. [x] R-E power: installed = RoF effects 3-5 without the built-in bit 0x20; "Installed RoF volley %"
       200 (built-in RoF keeps the RoF 7 / 10 per-shot rows). Counter `rof_volley`. PE `593fbae`.
4. [x] R-E speed / hold: in a follow-up action mode (7 / 9 / 11) Aya's animation step x follow
       frames / max(4, hit frame) per gun kind (handgun 2.5, shotgun 7.5, rifle 3.75, grenade 6.25,
       rocket 2.5; machine guns unchanged); the kind's hold byte (`0x800106A4 + kind x 5 + 2`) reads 0;
       both restored from retail values when off. Row "RoF mods: fast volleys". Counter
       `fast_volley`. PE `fa00bf6`.
5. [x] DPS line shows R-B / R-C / R-E (getters `pe_fx_attack_bonus`, `pe_fx_rof_volley_pct`). PE `d008f27`.
6. [ ] **In-game checks (user)** with the matching save states: Day 4-5 rifle (G3A3) and grenade
       (M203 4) fights; a Day 5 crowd with a catalog Attack All gun; a Disc2 crowd with the P90 / MAG;
       a RoF 7 install on a handgun / rifle (volley speed and damage). The play log's `modfx` rows
       show what fired; compare fight times with the basis tables.
7. [x] Mod header comment updated; basis status updated (built, awaiting in-game checks).

Also done this round: Scan summary (PE balance mod, commit 64720a7) — Scan lists weaknesses and
resistances on one line.

8. [x] Self-check for R-A: every gun hit's damage is predicted with the replica and compared with the
       HP the target lost; the `modfx` row shows `dmg_pred=matched/total`, and each miss gets a
       `dmgchk` row (first 8 a battle). PE `6101495`.
10. [x] Play log 2026-10-20 (Day 4 Hospital, G3A3 + Catalog Attack All + RoF 7): R-B `gun_bonus` and R-A
       `aa_capped` / `aa_topup` fire, `dmg_pred` 100%, Bestiary kills recorded. **Bug found:** R-E never
       fired (`rof_volley=0`, `fast_volley=0`): the "built-in bit 0x20" test is wrong, because every RoF mod
       byte is `(1 << 5) | effect`. Fixed: installed = the base item lacks that RoF (mod effects + DPS line).
       Needs a rebuild and a recheck: `rof_volley` / `fast_volley` > 0 with the RoF 7 G3A3.
9. [x] R-F progression gun bonuses (user approved 2026-10-20 after the gun ladder with stage-gated Catalog
       installs): one ON/OFF row; counted in `gun_bonus`; DPS line through `pe_fx_attack_bonus`. Built,
       untested in game. In-game check: an M16A1 / SG550 (Day 3) or M203 (Day 2) fight, `modfx` gun_bonus > 0.

## Phase 2 — Collection (Bestiary + Wardrobe), design `pe-skins-bestiary-design-2026-10-19.md`

New mod `src/mods/pe_collection.c` (F1 > PE Enhancements > Collection), data generated by
`tools/pe_assets/gen_collection_data.py` into `src/mods/pe_collection_data.h`.

1. [x] Profile file `pe_collection.dat` beside the game: skins owned / worn, one byte per creature
       (met, weaknesses, loot, kills to 31); checksum; permanent across games; Debug > Reset collection.
       PE `8bee561`.
2. [x] Bestiary page: 75 creatures (story + Chrysler) in a grid (??? until met, gold when complete,
       corner mark for bosses), four detail lines, "Buy next tier" (Junk from the running game).
       Unlocks: kills (enemy-slot watch: HP above 0 -> 0, creature from map + identity; 5 kills
       weaknesses, 15 loot; bosses: defeat = weaknesses), Scan (`0x80024250` power 7), Junk. PE `8bee561`.
3. [x] Wardrobe page: skins with prices; buy once, wear in every game. Aya's outfits (evening dress,
       jacket, T-shirt) by rewriting `g_SceneAreaType` (`0x800B0CE2`, = requested_entity_bank) in
       gameplay outfit rooms before the scene start-up reads it. PE `8bee561`.
4. [x] Character skins: `tools/pe_assets/build_skin.py` builds `pe_skins/<folder>/` (model.bin,
       texture.bin, day1-8.bin) from the user's disc in the game's own formats (retarget: semantic
       chains + world orientation + shoulder correction; texture moved to the player slot) and
       installs it beside the game; round-trip checked. 21 built: Daniel, Maeda, Maya, Chief Baker?,
       Daniel (gun), Maeda (backpack), Melissa, Aya's date, two policewomen, two officers, two NYPD
       men, four opera performers, harlequin, usher, crew. Eve does not fit the body plan (stays
       "soon"). The swap runs from the tick between scene start-up steps: the skin texture goes
       through the game's own upload (loader sent back to step 3), then model.bin replaces the bundle
       and the pointers move, then the day rows at step 0x27. PE `0e9239a`, bridge `a131e42` /
       `03a65e6` / `138fdfa`.
5. [ ] **In-game checks (user)**: (a) Bestiary: kill a few enemies (entries, kills), Scan one
       (weaknesses tier + the Scan line), buy a tier; quit and reload: still unlocked.
       (b) Wardrobe: buy and wear the evening dress / T-shirt, change rooms; then Daniel: change rooms,
       walk, run, aim, fire, take a hit, open a door, start and finish a battle. The play log's `skin`
       rows show each step. Expected rough edges: gowns (Melissa, opera actress) shear in deep
       crouches; the gun may sit off the hand; first room after loading a save stays Aya.
6. [x] Wayne's Workshop Wardrobe screen (Workshop > Wardrobe: wearable / buyable skins, 5 a page,
       red when too expensive; buy once, wear). PE commit after `0e9239a` (see `git log`).
7. [ ] Per-skin fixes from the checks (hand / gun attachment part, anchor and hit cylinder from the
       model header, foot height).
