# Enemy body-contact damage — October 19, 2026 (Claude)

Started from the Day 5 boss in room 332: its 0x0015s landed 66 simulated hits for 0 damage, while
the log shows six hits of 7–8. The slot-3 attack (power N10 × 78) really does deal 0 against
Aya's defense at level 19. **The real damage was body contact**, a separate path the simulator
never had.

## Source

`menu/main_update.c` `Menu_MainUpdate`, once per battle update. While Aya's state has neither
0x800000 (post-revive hold) nor 0x180000 (Liberate / Energy Shot):
- **Strikes:** an enemy whose effect is live and whose hit flag is set gets
  `Entity_ResolveDropTable`. Afterwards Aya's 0x01000000 is set with
  `g_AyaStatusEffectTimer = 0x5A`. The timer does not block strikes.
- **Contact:** applies to an enemy with entity flag **0x02000000**, which `entity/allocation.c`
  sets when its hit cylinder overlaps Aya's. If Aya has no 0x01000000 and the enemy is alive:
  - Aya loses the enemy's **`contactDamage`** (EnemyCombatant 0x92) flat: no defense, no gauge
    halving.
  - Barrier (0x200) blocks the loss.
  - Then 0x01000000 is set for 90 updates (cleared by `Entity_UpdateTimers`), with knockback
    `contactKnockback` (0x93) over 6 frames.
- **Value:** scripts write it with `Entity_SetField 65` (0x41 → `effect_param92`, battle/context.c
  `Entity_WriteFieldByCmd`); field 66 is the knockback, 60 in every script. 378 actor scripts set
  2–12 (Disc 2 bosses 10, room 430 30).
- **Post-revive hold:** `Battle_ResetEnemyStats(1)` sets 0x800000 with timer 0x5A. For those 90
  updates no strike or contact resolves. That's the "hold timer" from the revive work: it is
  Aya's immunity.

## Where the attackers come from: actor by HP

Room 332's 0x0015 is two actor types:
- actor 6: HP N10×170, owns slot 3;
- actor 7: HP N10×45, declares no action and runs no command; it only rams.

`enemy_choice.unarmed_actor` resolves a shared identity's actor from the foe's HP (the script's HP
literal × V80). If none of the matching actors declares an action or runs a command, the foe
can't strike: opt-in `called_slots.actor_by_hp`, `--actor-by-hp`. Flagged in the log:
- the small 0x0015s in rooms 152, 153, 154 and 332;
- the parts in rooms 123 and 273, already silent.

## When contact happens (labelled)

The simulator has no enemy body motion, so the contact rate is measured from the log
(`logged_contact.py`, data `pe-logged-contact-rate-2026-10-19.json`). A hurt counts as contact
when:
1. it equals a present enemy's contactDamage;
2. it is ≥ 3 s after the previous contact-valued hurt (the 90-update window; poison ticks repeat
   about every second and are excluded, e.g. room 126's run of 3s);
3. no present enemy's resolved strike could deal that value at that battle's level and armor.

Rates per battle-minute: per room where logged; defaults are ordinary 0.82 and boss 0.89. Examples:
332 = 6.1, 245 = 3.6, 123 = 2.0. Overall, contact is about 5–7% of ordinary damage, but it is
**all** of room 332's.

The contact rolls use their own random stream. Sharing the fight's stream made per-battle results
jump by ±50 (pure noise).

## Calibration (`pe-calibration-logged-contact-v3-2026-10-19`, full flag set + `--contact logged --actor-by-hp`)

| Group | Before (Aya final) | Now (r) |
|---|---|---|
| All ordinary | 1.04 | **1.07 (0.76)** |
| Day 2–4 ordinary | 1.10 | 1.12 |
| Day 5 ordinary | 1.06 | 1.11 (0.88) |
| Disc2 ordinary | 0.98 | 1.00 |
| Day 5 bosses | 0.94 | **1.02** (room 332: 3.75 → 28 vs 44) |
| Day 2–4 bosses | 1.20 | 1.20 (0.89) |
| Disc2 bosses | 0.57 | 0.57 (out-of-reach turns, room 273) |

Refitting the early melee dodge for contact isn't worth it: 0.7 / 0.8 change Day 2–4 by less
than the noise.

## Follow-ups the same day: room 273 and Liberate

**Room 273 — counters killed the controller.** The 10-HP core 0x0325, untargetable and the
attacker, was hit by Aya's counters. Counters aim at whoever just hit her, and the counter target
list included controllers. Normal attacks already skipped controllers. Counters now skip them too
(the log never shows Aya damaging 0x0325). Result: 0x0325 strikes about every 3 s as its charge
step (120) says, and room 273 goes from 239 to 1091 against 1264 logged.

**Liberate** (Battle_ResolveHit state 0x80000):
- Power = (stat1E − 25 + level) × 6 × (1 + 0.1·(targets − 1)) / 7; damage = power − full
  defense; 7 hits per cast; all PE spent.
- It matches the log exactly:
  - room 273, 3 targets: 368 = 283 + 85 = 298 + 70 = 313 + 55;
  - room 432, 1 target: 306 = 256 + 50.
- That also pins Aya's offense at 350, so the Energy Shot 2-point gap was the gun's attack bonus
  (149, not the save's 147).
- Room 432: 340 → **83 vs 79**.

Calibration `pe-calibration-logged-contact-v5-2026-10-19`:
- ordinary 1.07× (r 0.76);
- **bosses 0.68× (r 0.82)**;
- Disc2 bosses 0.61× (r 0.72).

**Remaining Disc2 boss gap = player behaviour:**
- Rooms 245 / 256: club turns (`acts` 8:7 / 8:6) and weapon swaps.
- Room 188: 5 volleys in 11 turns.
- Room 350: still open.

The sim fires a full volley every turn and kills 2–3× sooner, so it takes less damage. Replaying
the logged weapon / club turns would close this; it isn't an enemy-model error.

Files:
- code: `contact_damage.py`, `logged_contact.py`, `enemy_choice.unarmed_actor`, `source_combat`
  (`contact_damage`, `hold`);
- tests: `test_contact_damage.py`;
- flags: `--contact [global|logged]`, `--actor-by-hp`.
