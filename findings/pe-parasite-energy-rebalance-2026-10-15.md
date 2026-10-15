# Parasite Eve: Parasite Energy vs items rebalance (2026-10-15)

Status: **decided and built (first pass, 2026-10-15)**; numbers to be tuned from play logs.
F1 > PE Enhancements > **Items & Parasite Energy** (Rules: Vanilla / Rebalanced / Custom; page
"Quick powers" for each power's bar cost). Code: PE `src/mods/pe_pe_balance.c`,
`pe_atb_items.c` (half-bar turns), `pe_custom.c` + `pe_native_menu.c` (Panacea), `pe_loot.c`
(Lucky Charm removed).

Prompted by play: poisoned at full HP, Detox cost a full ATB bar and 100 PE while the mod's
half-bar Cure-P cost half a bar and no PE, so the Parasite Energy version only made sense with
an empty bag.

Sources: the decomp (cited by function), the RPGClassics Parasite Eve shrine's
[Parasite Energy](https://shrines.rpgclassics.com/psx/pe/pe.shtml),
[items](https://shrines.rpgclassics.com/psx/pe/items.shtml) and
[experience](https://shrines.rpgclassics.com/psx/pe/experience.shtml) pages (summarised).

---

## 1. Facts (decomp and shrine)

- **Turn bar:** every battle action needs Aya's gauge full (9000) and empties it. The mod's
  half-bar turns (the gold bar) let chosen tabs act from half a bar for half a bar.
- **PE costs** (`Battle_ApplySpellEffect`, battle/attack.c; PE in 16.16; armor with PE Light,
  effect flag 0x200, pays two thirds):

  | Power (index) | PE | Effect |
  |---|---|---|
  | Heal 1 (0) | 60 | +30 HP |
  | Heal 2 (1) | 120 | +60 HP |
  | Heal 3 (2) | 500 | +280 HP |
  | Detox (3) | 100 | cures poison |
  | Medic (4) | 600 | cures every ailment |
  | Barrier (5) | a third of max PE | hits drain PE instead of HP |
  | Energy Shot (6) | all remaining | one PE-powered shot |
  | Scan (7) | 50 | shows HP and weaknesses |
  | Slow (8) | 90 | enemy ATB −40% (sure if weak, 50% if neutral, never if resistant) |
  | Haste (9) | 200 | Aya faster for 450 frames (~7.5 s); cures Stiffness |
  | Confuse (10) | 150 | as Slow's odds |
  | Gene Heal (11) | 400 | regenerates HP while draining PE |
  | Preraise (12) | 1000 | revives once |
  | Full Recover (18) | 1300 | full HP, every ailment |
  | Liberate (19) | all | transforms, seven attacks |

- **Items** (`Battle_ApplyDamage`, battle/attack.c; the same routine runs for menu use):
  Medicine 1–4 +45 / 90 / 180 / 400 HP; Full Recover full HP; **Cure-P / D / C / M cure the
  ailment, or if Aya doesn't have it, make her immune to it** (vanilla "Cures & Prevents"); Full
  Cure clears all four and state 0x1000; Super / Duper Junk restore a quarter / half of max PE
  (unusable in vanilla; the mod keeps them as Junk bundles).
- **Aya's HP grows ~14x** over the main game (experience chart: Lv 6 72, Lv 14 181, Lv 21 296,
  Lv 33 621), while every heal is a flat number.
- **Medicine 4 sources:** main game rare (Museum Armadillo drop, Pterodactyl first fight,
  Scorpion steal, Museum x2 (+3 possible), Navy man x2); Chrysler Building common (a third of
  the late-floor enemies drop or carry one).
- **Combine (mod):** two of a Medicine make the next one.

## 2. Identities

| | Items | Parasite Energy |
|---|---|---|
| Scales with | how many you collect (Combine) | Aya's level (max HP) |
| Best at | burst heals, fast; preventing ailments (vanilla); when PE is empty | renewable healing; lasting buffs (Barrier, Gene Heal, Haste, Preraise); no bag space or supplies |
| Paid with | supplies, bag slots, Junk | PE (refills in battle, slower when low) |

## 3. Decisions (built)

| Area | Rebalanced | Vanilla |
|---|---|---|
| Half-bar turns | on | off |
| Half bar: items | on | — |
| Half bar: Parasite Energy | quick powers only: Heal 1, Heal 2, Detox, Medic, Scan, Slow, Confuse | — |
| Full-bar power from a half bar | allowed; the gauge empties and the rest of a full bar is owed (debt), paid from the next refill | — |
| Heal 1 / 2 / 3 | 15 / 30 / 65% of max HP, never below 30 / 60 / 280 | +30 / 60 / 280 |
| Detox / Scan PE | 60 / 30 | 100 / 50 |
| Regen on PE cures | not built | — |
| Combine | Medicine 1→2→3→4 all 2x; **Medicine 4 + Full Cure → Panacea** | 2x only |
| Medicine 4 | unchanged (+400 HP) | — |
| **Panacea** (item 0x19) | +400 HP and cures every ailment (as Full Cure), half a bar like any item; made only by Combine | — |
| Lucky Charm | removed (Lucky Find armor does the same); a carried charm becomes Panacea | — |
| Super / Duper Junk | unchanged (Junk bundles) | — |
| Half bar: change weapon / armor / escape | off | — |

How it's built: half-bar per power in `pe_atb_items.c` (queued command 0x183 + index; debt
tracked and taken from the refill); heals and costs in an entry hook on
`Battle_ApplySpellEffect` (0x80024250; extra HP added before the game's heal, which clamps; PE
difference refunded before the game's subtraction, scaled by PE Light); Panacea in the
`Battle_ApplyDamage` hook (0x80023E14: clear ailments, then handed to the game as Medicine 4);
no new game.toml hooks.

Play log: `pe_turn` rows (power, cost half / full / full_debt, gauge before → after); `combine`
rows (into=0x19 for Panacea); spell casts in the battle summary as before.

## 4. Open items (decide from play data)

1. **Heal 3 vs Medicine 4 late.** End of Day 5: Medicine 4 heals ~64% of max HP for half a
   bar; Heal 3 (65%) a full bar and 500 PE. Main game: fine (Medicine 4 is rare). Chrysler
   Building: Medicine 4 is common, so items may win every heal there. Options: (a) accept,
   (b) Heal 3 to ~80%, (c) Heal 3 half a bar, (d) fewer Medicine 4 drops in the Chrysler
   Building (reward-list rewrite). Needs: max PE and PE regen (casts per fight), and logs.
2. **PE heal percentages** (15 / 30 / 65): check heal size per bar and per PE in logged fights.
3. **Quick power set:** Medic and Heal 2 at half a bar may be strong; Slow / Confuse may need
   it more. Watch `pe_turn` rows.
4. **Debt rule feel:** a full power from a half bar delays the next turn; check it reads clearly.
5. **Panacea:** how often it's built (combine rows) and whether it trivialises status fights.
6. **Requisition prices vs Combine:** price each Medicine a bit above half the next one.
7. **Cure items' immunity:** vanilla sets immunity when Aya isn't afflicted; find how long it
   lasts (status timers) before deciding anything more for items.
8. **Data to read from the game:** max PE by level (`battleMaxAtk`) and the PE regen rate.
