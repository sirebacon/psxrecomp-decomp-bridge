# Disc2 boss identities: scripts that change kind, and silent actors — October 19, 2026 (Claude)

## Problem

Four Disc2 bosses had no resolved attacks. The fallback audit reported them as "no attack calls
in the identity scripts":

| Boss | Logged id | Fallback hits (earlier audit) |
|---|---|---:|
| 245 | 0x0421 | 188 |
| 429 | 0x0426 | 182 |
| 269 | 0x041B | 54 |
| 188 | 0x021A | 50 |

## Source evidence

Logged ids are the combatant core half-word at +0x04 (`pe_loot_logger.c` `EN_IDENTITY`), which
is (kind << 8) | rank from entity fields 42 / 41 (`enemy_identity.py`).

The actor scripts of these bosses set one literal rank, but write **several literal kinds**:

| Room / actor | Rank (field 41) | Kind (field 42) literal writes, in script order |
|---|---|---|
| 188 / 5–8 | 26 (0x1A) | 2, 4, 2 |
| 245 / 6–8 | 33 (0x21) | 2, 4 |
| 269 / 6–7 | 27 (0x1B) | 2, 4 |
| 429 / 2 | 38 (0x26) | 2, 4 |

- `literal_identities` only accepts one literal kind, so these actors never matched any
  logged id.
- Every write to fields 41 / 42 in these scripts is a literal; there are no computed writes.
- Each literal kind is a value the script can leave in the core. So each
  (kind << 8) | rank is a candidate identity: 0x221 / 0x421 for 245, and so on.
- The logged ids (0x0421, 0x0426, 0x041B, 0x021A) are among those candidates.
- Which branch writes which kind, and when, isn't decoded. The candidate set is exact; the
  timing of the kind change is not modelled.

## Change 1: multi-kind identities (opt-in)

- `enemy_identity.multi_kind_identities()` lists exactly those 10 scripts. No other script in
  the inventory has this pattern.
- `identity_keys(cells)` adds their candidate keys when `cells` contains the sentinel
  `MULTI_KIND` (-1). Default calls are unchanged, so historical results reproduce.
- `compare_rules --multi-kind` passes the sentinel.
- Test: `test_called_slots.MultiKindIdentityTests`.

Effect:
- **429:** slots 0, 1, 3, 4, 5 get source power.
  - Slots 0 and 1 (172 / 186) have melee windows.
  - Slot 3 (205) and slots 4–5 (status effect types 8 / 9) remain untimed.
- **245:** slots 1–3 resolve per species pick (`called_slots` variants); the actors disagree,
  so a pick is required.
- **188:** the four actors are variants, so each fight picks one. Actors 6 and 7 call only
  slot 2 (power 138).
- **269 (0x041B):** silent; see Change 2.
- Disc2 boss benchmark with this change alone
  (`pe-compare-class-bosses-multikind-nosilent-AAo40-2026-10-19`): fallback share about
  0.52 → 0.19.

## Change 2: silent actors (same opt-in)

`enemy_choice.silent_identity`: an identity is silent when every actor resolving to it has an
error-free decoded flow (`decode_enemy_actions.flow`, child edges included) containing none
of `Script_RunEntityCommand`, `Script_GetEntityEffect` or `Pm_ScriptSendCommand*`.

Why that rule is safe:
- `Script_RunEntityCommand` is the only caller of `Entity_TriggerAnimEvent` (0x8002FAF8) in
  main.
- No Disc2 boss room blob (188 / 245 / 256 / 269 / 273 / 350 / 429 / 156) contains a `jal`
  to it.
- Effects and PM sends are excluded as well, to be strict.

Over all 130 logged identities, exactly two are silent:
- **269 0x041B:** actors 6 and 7. They declare two records but never command them.
- **273 0x0125:** actors 5–7. A 60-node script with no declarations: passive parts of the
  Liberty fight.

Effect:
- `source_combat` gives a silent foe `no_contact`; its clock still runs, and its strikes are
  counted in `no_contact_strikes` / `called_slot_silent_foes`.
- Opt-in through `called_slots.silent`; `compare_rules --multi-kind` turns it on.
- Room 273 boss battle (frozen MAG build): win 0/3 → 3/3; the 23 fallback hits came entirely
  from the passive parts.
- Test: `test_called_slots.MultiKindIdentityTests.test_silent_identities_never_attack`.

## Result with both changes

Disc2 boss battles, class benchmark (`pe-compare-class-bosses-multikind-AAo40-2026-10-19`,
33 fights per class):

- fallback hit share **0.00**;
- untimed strike share 0.60;
- win rates by class (default set): machine 0.76, rifle 0.70, handgun 0.64, grenade 0.36,
  shotgun 0.30. Still pessimistic in absolute terms (incoming frequency about 2× the log).
- AAo_40 has no effect on boss battles.

## Remaining boss gaps: untimed task effects

All rooms load their overlay at 0x8018EFE8. Controllers identified for the effects behind the
untimed slots:

- **245:** effects 140 / 141, `RoomEffect_SeekingTrailController`. Named in room 245's
  symbol file and byte-identical to `ScatterTrailController`.
- **269:** 137 `GroundSweepController`, 138 `OrbitTrailBurst`, 139 `RisingSprayController`.
- **256:** 131 / 132 are unnamed.
- **428, 429, 432:** no symbol files. A masked-instruction signature search against 322
  named room functions found no match.

### Static contact scan (exploration, not used by the model)

`effect_contact_scan.py` follows code reachable from an effect record (`jal`, lui/addiu
pointers, pointer tables of functions). It flags any of three contact signatures:
- the owner-bit test `& 0x3F000000`;
- a rewrite to 0x21 / 0x19 / 0x11;
- a `jal FieldFx_RegisterOwnerContact` (0x800C6C18).

In main code, only that helper and melee contact (`actor_collision.c:1473`) set the player's
0x4000 hit flag.

- **Validation:** flags all 49 effects the simulator already models with source contact.
- **Untimed boss effects with contact code:** 245 140 / 141, 256 131 / 132, 269 137–139,
  429 145–147, 432 150 / 151 / 162. They can hit, so keeping them as (untimed) hits is right.
  Only their timing is a placeholder.
- **No signature found:** 428 152 / 153, 429 148, 432 163 / 165, and PM 70 / 75.
  - Pointer-following is noisy: effects reach each other's code, and bare `ori 0x4000`
    writes show up in 428's tree.
  - So a negative result is not used to mark any effect harmless.
