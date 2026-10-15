# Parasite Eve: Parasite Energy vs items rebalance (design draft, 2026-10-15)

Status: **draft for discussion**, nothing built. Prompted by play: Aya is poisoned at full HP,
and the only answers are a full ATB bar for Detox, a full bar for a heal, or (with the mod's
half-bar items) a Cure-P for half a bar. With half-bar items, the Parasite Energy versions of
item effects lose to the items unless the bag is empty.

Companion docs: [`pe-mod-effects-overhaul-2026-10-14.md`](pe-mod-effects-overhaul-2026-10-14.md),
PE `src/mods/pe_atb_items.c` (half-bar ATB).

Sources: the decomp (cited by function), the RPGClassics Parasite Eve shrine's
[Parasite Energy](https://shrines.rpgclassics.com/psx/pe/pe.shtml) and
[items](https://shrines.rpgclassics.com/psx/pe/items.shtml) pages (summarised in our words).

---

## 1. How it works today

**The turn bar (decomp, `pe_atb_items.c` notes).** Every battle action (shooting, an item, a
Parasite Energy power, changing gear, escaping) needs Aya's ATB gauge full (9000) and empties it.
The mod's half-bar option lets chosen menu tabs act from half a bar for half a bar's cost; by
default only **Use Item**. The Parasite Energy tab can be switched on too, but only for all
powers at once.

**PE costs (decomp `Battle_ApplySpellEffect`, battle/attack.c).** Each power subtracts a fixed
amount from Aya's PE (``exp_or_acc``, 16.16 fixed point; armor with the PE-burden flag, "PE Light",
cuts it by a third). The shrine only gives tiers; the real numbers:

| Power | Learned | PE cost | Effect (decomp) |
|---|---|---|---|
| Heal 1 | start | 60 | +30 HP |
| Scan | Lv 4 | 50 | shows HP and weaknesses |
| Slow | Lv 7 | 90 | enemy ATB −40% (sure if weak, 50% if neutral, never if resistant) |
| Detox | Lv 9 | 100 | cures poison |
| Heal 2 | Lv 11 | 120 | +60 HP |
| Barrier | Lv 13 | a third of max PE | hits drain PE instead of HP until PE runs out |
| Energy Shot | Lv 15 | all remaining | one shot powered by the PE spent |
| Confuse | Lv 17 | 150 | enemy confused (sure if weak, 50% if neutral) |
| Haste | Lv 20 | 200 | Aya's ATB and movement faster for 450 frames (~7.5 s); cures Stiffness |
| Heal 3 | Lv 22 | 500 | +280 HP |
| Gene Heal | Lv 25 | 400 | regenerates HP while draining PE |
| Medic | Lv 28 | 600 | cures every ailment |
| Preraise | Lv 30 | 1000 | revives Aya once at 0 HP |
| Full Recover | Lv 32 | 1300 | full HP and every ailment |
| Liberate | Lv 33 | all | transforms; seven strong attacks |

PE recharges during battle, more slowly as it runs low (shrine). Max PE grows with level (level
table ``battleMaxAtk``; to read from the game).

**Items (shrine).** Medicine 1 / 2 / 3 / 4: +45 / 90 / 180 / 400 HP; Cure-P / C / D / M cure one
ailment; Full Cure cures all; Full Recover restores HP; Revive revives once. Finite: chests,
drops, steals, Requisition.

## 2. The problem

1. **Every power costs a full bar**, whether it's Scan (50 PE) or Full Recover (1300 PE). A full
   bar is a full volley of shots, so cheap utility powers (Scan, Detox, Heal 1) are almost never
   worth the turn.
2. **Half-bar items made it worse.** Cure-P now costs half a bar and no PE; Detox costs a full bar
   and 100 PE. Same effect, worse in every way: Detox only gets used with no Cure-P left. Medicine
   1 (+45 HP, half bar) beats Heal 1 (+30 HP, full bar, 60 PE) the same way.
3. **Little reason to choose.** Items and powers should differ in kind, not just in price: items
   are fast and finite, Parasite Energy should be renewable and flexible, and the choice should
   depend on the fight.

## 3. Principles

- **Items: fast, finite.** Half a bar (as now). Using one spends a resource you can run out of.
- **Parasite Energy: renewable, costs PE and tempo by size.** Small, reactive powers (a quick
  cleanse, a small heal, a look at the enemy) should be as fast as an item; big, game-changing
  powers (full heals, revives, lasting buffs, finishers) keep the full bar.
- **Same effect, different trade:** Detox vs Cure-P should be "PE or an item", both half a bar,
  so carrying Cure-P is about saving PE, not about tempo.
- **No new dominant option.** Quick casts must not let Aya chain heals faster than enemies hurt
  her; PE costs and regen do the limiting.

## 4. Proposal

### 4.1 Bar cost per power ("quick" = half bar, like items)

| Power | Bar today | Proposed | Why |
|---|---|---|---|
| Heal 1 | full | **half** | small reactive heal; matches Medicine 1's tempo |
| Heal 2 | full | **half** | mid heal; Medicine 2 is half a bar |
| Detox | full | **half** | the case that started this: same tempo as Cure-P, pays PE instead |
| Scan | full | **half** | information should not cost a whole volley |
| Slow | full | **half** | a control setup; cheap, can fail (resist / coin flip) |
| Confuse | full | **half** | same as Slow |
| Medic | full | **half** | cleanse-all; Full Cure (item) is half a bar |
| Haste | full | full | lasting tempo buff: casting it quickly would pay for itself |
| Barrier | full | full | strong defensive state |
| Heal 3 | full | full | +280 HP: a big swing |
| Gene Heal | full | full | lasting regen |
| Preraise | full | full | a revive |
| Full Recover | full | full | full heal + cleanse |
| Energy Shot, Liberate | full | full | finishers |

Rule of thumb: **reactive, small or can-fail → half; lasting, big or finishing → full.**

### 4.2 PE cost tweaks (small)

| Power | Today | Proposed | Why |
|---|---|---|---|
| Heal 1 | 60 (+30 HP) | 60, **+45 HP** | match Medicine 1; worst HP-per-PE today |
| Detox | 100 | **60** | a single-ailment cure costs more than Heal 2's half; Cure-P is cheap to find |
| Scan | 50 | **30** | rarely used |
| others | — | unchanged | |

(PE Light armor keeps its −⅓.)

### 4.3 Casting a full-bar power from a half bar

With the Parasite Energy tab allowed on a half bar, the menu still lists every power. Options:

- **A. Debt (recommended):** a full-bar power cast from a half bar empties the gauge and also
  holds the next refill back by half a bar, so it always costs a full bar in total, just sooner.
  No menu changes; clear rule.
- **B. Block:** grey out full-bar powers on a half bar (menu hook; more work).

### 4.4 Items stay as they are

Half a bar, all items (current default). Optional later: let Medicine 3 / 4, Full Recover (item)
and Revive cost a full bar, so the biggest heals have the same tempo whichever way you get them.

## 5. What it should feel like

- Poisoned at full HP: Detox or Cure-P, half a bar either way; Detox if you want to keep the item.
- Chip damage: Heal 1 / 2 on half a bar instead of a Medicine.
- Scan and Slow / Confuse become openers worth taking.
- Big moments (Heal 3, Full Recover, Preraise, Barrier, Haste, Liberate) still take Aya's whole
  turn.

## 6. Build notes

- Extend `pe_atb_items.c`: allow the Parasite Energy tab on a half bar with a per-power quick set
  (commands 0x183 + index, tech index as in `Battle_ApplySpellEffect`); at turn end the queued
  command decides: quick power → half cost; full power from a half bar → debt (4.3 A); full power
  from a full bar → full cost.
- PE costs: entry hook already on `Battle_ApplySpellEffect` (0x80024250, game.toml) can refund PE
  after the cast (cost tweaks) — or adjust Aya's PE before the subtraction; Heal 1's extra HP the
  same way.
- F1 page **Mod Effects > Parasite Energy**: per-power Quick / Full, PE cost %, Rules Vanilla /
  Rebalanced like the weapon effects.
- Play log: one row per cast (power, bar cost, PE before / after) so the change can be checked.
- Data to read from the game first: max PE by level (``battleMaxAtk``) and the PE regen rate, so
  costs can be judged as a share of the bar.

## 7. Open questions

1. Is half a bar right for Heal 2 and Medic, or only for the small ones (Heal 1, Detox, Scan)?
2. Should Slow / Confuse be quick? They can fail, which argues yes.
3. Full-bar power from a half bar: debt (A) or block (B)?
4. Make the biggest items (Medicine 3 / 4, Full Recover, Revive) full-bar too?
5. PE cost tweaks: as listed, or leave PE costs alone and change only the bar?
