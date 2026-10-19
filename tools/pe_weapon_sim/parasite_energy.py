"""Aya's Parasite Energy in battle (opt-in source_options['pe']).

Source (decomp):
  - Regeneration, menu/main_update.c Menu_MainUpdate: while game flag 0x100 is clear (no committed
    action) and the menu is not paused, and PE (exp_or_acc, 16.16) < max (maxAtk):
        atbRate -= 3 (min 1); atbStep -= maxAtk / (atbRate * 100) (min 0x1999); PE += atbStep.
    The start values are Aya's level-table row (track 3): battleMaxAtk / battleAtbRate /
    battleAtbStep (aya/stats.c Inv_RecalcSlotStats; economy/source_stats ROWS max_atk/atb_rate/atb_step).
  - Effects and costs, battle/attack.c Battle_ApplySpellEffect: Heal 1 / 2 / 3 add 30 / 60 / 280 HP
    (clamped to max) and cost 60 / 120 / 500 PE; Detox 100; Medic 600; Barrier max/3; Scan 50;
    Slow 90; Haste 200 (haste bit, timer 0x1C2; Menu_MainUpdate: gauge fill + scaledOffense / 2);
    Confuse 150; Gene Heal 400; Preraise 1000; Full Recover 1300. Armor effect 0x200 (PE Light) takes
    a third off the cost.
  - Mod (CURRENT, pe_pe_balance.c / pe_atb_items.c): heals 15 / 30 / 65% of max HP (never below
    vanilla); quick powers (Heal 1, Heal 2, Detox, Medic, Scan, Slow, Confuse) usable from a half bar
    for half a bar; other powers cost a full bar.
PE powers pause the enemies for the whole cast, which can't be interrupted (user observation; Pm_StopLowerHalf).
Not source (labelled, options): the cast's duration (default 60 battle updates) and
the player's policy (heal below a share of max HP with the best affordable known heal; Haste on the
first turn of a boss battle).
"""
from .economy.source_stats import row, stat_level, value_at

COST = {'Heal1': 60, 'Heal2': 120, 'Heal3': 500, 'Detox': 100, 'Medic': 600, 'Scan': 50, 'Slow': 90,
        'Haste': 200, 'Confuse': 150, 'GeneHeal': 400, 'Preraise': 1000, 'FullRecover': 1300}
HEAL_VANILLA = {'Heal1': 30, 'Heal2': 60, 'Heal3': 280}
HEAL_PCT = {'Heal1': 15, 'Heal2': 30, 'Heal3': 65}
QUICK = {'Heal1', 'Heal2', 'Detox', 'Medic', 'Scan', 'Slow', 'Confuse'}
HASTE_UPDATES = 0x1C2                     # g_ActorEffectFlag100Timer, -1 per update (Entity_UpdateTimers)
# battle/attack.c Battle_ApplyDamage: Medicine 1-4 (items 6-9) +45 / +90 / +180 / +400 HP, Full Recover
# (0x0A) to max. The mod allows items from a half bar for half a bar (pe_atb_items.c).
MEDICINE = {0x06: 45, 0x07: 90, 0x08: 180, 0x09: 400}
FULL_RECOVER = 0x0A


def energy_shot_damage(offense, gun_power, level, pe, max_pe, defense):
    """Battle_ResolveHit (battle/enemy_movement.c) with state 0x100000: base = stat1E/5 + the gun's power
    bonus; power = base * ((7*level + 120) / 160) * PE / maxPE + base (integers, PE in whole points);
    damage = power - full defense, at least 1. Live check 2026-10-19 (room 273, level 33, PE 1420/1420,
    target defense 85): 572 logged = base 219 (the save-derived inputs give 217)."""
    base = int(offense) // 5 + int(gun_power)
    power = base * ((level * 7 + 120) // 160) * int(pe) // max(1, int(max_pe)) + base
    return max(1, power - int(defense))


class PE:
    def __init__(self, level, spells, start=None, pe_light=False, rules='current', heal_rules=None, heal_below=0.5,
                 cast_updates=60, haste_bosses=True, max_hp=None, bag=None, script=None, items=None):
        r = row(stat_level(3, value_at(level)))
        self.max = r['max_atk']; self.rate = r['atb_rate']; self.step = r['atb_step']
        self.pe = self.max if start is None else min(self.max, int(start * 65536))
        self.spells, self.pe_light, self.rules = set(spells), pe_light, rules
        self.heal_rules = heal_rules or rules           # 'vanilla' heals with the half-bar quick powers: the logged run
        self.heal_below, self.cast_updates, self.haste_bosses = heal_below, cast_updates, haste_bosses
        self.bag = dict(bag or {})                        # {item id: count} usable in battle
        self.haste_left = 0; self.max_hp = max_hp      # policy HP scale when the fight's hp cap is not Aya's max
        self.script = dict(script) if script else None  # logged casts to replay (choose_scripted)
        self.items = dict(items) if items else None     # logged item use to replay {item id: count}
        self.barrier = self.gene = self.preraise = False

    def regen(self):
        if self.pe >= self.max: return
        self.rate = max(1, self.rate - 3)
        self.step = max(0x1999, self.step - self.max // (self.rate * 100))
        self.pe = min(self.max, self.pe + self.step)          # PE caps at max (the game adds then clamps on display)

    def cost(self, spell):
        if spell == 'Barrier': return self.max // 3            # exp_or_acc -= maxAtk / 3, no PE Light cut
        if spell == 'EnergyShot': return 0x10000                # needs PE; the shot then spends all of it (phase.c)
        c = COST[spell] << 16
        return c * 2 // 3 if self.pe_light else c

    def can(self, spell): return spell in self.spells and self.pe >= self.cost(spell)

    def choose_scripted(self, hp_now, max_hp, gauge, poisoned=False, hasted=False, barrier=False, ailing=()):
        """Replay of a logged battle's casts (self.script, {spell: count left}): the logged player's
        choices, cast when they apply. Heals below heal_below, Detox only while poisoned, buffs while
        absent, Slow / Confuse early. Labelled player behaviour, not source."""
        left = lambda s: self.script.get(s, 0) > 0 and self.pe >= self.cost(s)     # logged, so known
        def bar(s):
            half = self.rules == 'current' and s in QUICK
            if gauge >= 9000 or (half and gauge >= 4500): return s, 'half' if half else 'full'
        if hp_now <= self.heal_below * max_hp:
            for s in ('Heal3', 'Heal2', 'Heal1'):
                if left(s) and bar(s): return bar(s)
        if poisoned and left('Detox') and bar('Detox'): return bar('Detox')
        if ailing and left('Medic') and bar('Medic'): return bar('Medic')
        if hp_now <= 0.25 * max_hp and left('FullRecover') and bar('FullRecover'): return bar('FullRecover')
        item = self.scripted_item(hp_now, max_hp, gauge, ailing)
        if item: return item
        if not hasted and left('Haste') and bar('Haste'): return bar('Haste')
        if not barrier and left('Barrier') and bar('Barrier'): return bar('Barrier')
        if not self.preraise and left('Preraise') and bar('Preraise'): return bar('Preraise')
        if not self.gene and hp_now <= 0.75 * max_hp and left('GeneHeal') and bar('GeneHeal'): return bar('GeneHeal')
        if self.pe >= self.max * 3 // 4 and left('EnergyShot') and bar('EnergyShot'): return bar('EnergyShot')
        for s in ('Slow', 'Confuse'):
            if left(s) and bar(s): return bar(s)
        return None

    def scripted_item(self, hp_now, max_hp, gauge, ailing=()):
        """Replay of a logged battle's item use (self.items): medicine below heal_below (the largest
        logged one that fits the missing HP, else the smallest), a cure while its ailment is active.
        Items take half a bar in the mod (pe_atb_items.c). Labelled player behaviour."""
        if not self.items or gauge < 4500: return None
        have = lambda i: self.items.get(i, 0) > 0 and self.bag.get(i, 0) > 0
        for ailment, item in (('poison', 0x0D), ('dark', 0x0E), ('confused', 0x0F), ('stiff', 0x10)):
            if ailment in ailing and have(item): return ('item', item), 'half'
        if ailing and have(0x11): return ('item', 0x11), 'half'
        if hp_now <= self.heal_below * max_hp:
            meds = sorted((v, k) for k, v in MEDICINE.items() if have(k))
            fit = [k for v, k in meds if v <= max_hp - hp_now]
            if fit or meds: return ('item', fit[-1] if fit else meds[0][1]), 'half'
            if have(FULL_RECOVER): return ('item', FULL_RECOVER), 'half'
        return None

    def heal_amount(self, spell, max_hp):
        v = HEAL_VANILLA[spell]
        return max(v, max_hp * HEAL_PCT[spell] // 100) if self.heal_rules == 'current' else v

    def choose(self, hp_now, max_hp, gauge, boss, first_turn, items_only=False):
        """(spell, bar cost) for this turn, or None. bar cost: 'half' (quick power) or 'full'."""
        if not items_only and self.haste_bosses and boss and first_turn and self.can('Haste') and gauge >= 9000:
            return 'Haste', 'full'
        if hp_now <= self.heal_below * max_hp:
            missing = max_hp - hp_now
            for spell in () if items_only else ('Heal3', 'Heal2', 'Heal1'):
                if not self.can(spell): continue
                if spell == 'Heal3' and missing < self.heal_amount('Heal2', max_hp) and self.can('Heal2'): continue
                half = self.rules == 'current' and spell in QUICK
                if gauge >= 9000 or (half and gauge >= 4500): return spell, 'half' if half else 'full'
            if gauge >= 4500 or gauge >= 9000:
                meds = sorted((v, k) for k, v in MEDICINE.items() if self.bag.get(k))
                fit = [k for v, k in meds if v <= missing] or [k for v, k in meds]
                if fit: return ('item', fit[-1] if [k for v, k in meds if v <= missing] else fit[0]), 'half'
                if self.bag.get(FULL_RECOVER) and hp_now <= 0.25 * max_hp: return ('item', FULL_RECOVER), 'half'
        return None

    def heal_of(self, action, max_hp):
        if isinstance(action, tuple):
            return max_hp if action[1] == FULL_RECOVER else MEDICINE.get(action[1], 0)
        if action == 'FullRecover': return max_hp
        return self.heal_amount(action, max_hp) if action in HEAL_VANILLA else 0

    def cast(self, spell):
        if isinstance(spell, tuple):
            self.bag[spell[1]] -= 1
            if self.items and self.items.get(spell[1]): self.items[spell[1]] -= 1
            return
        self.pe -= self.cost(spell)
        if self.script and self.script.get(spell): self.script[spell] -= 1
        if spell == 'Haste': self.haste_left = HASTE_UPDATES
        if spell == 'Barrier': self.barrier = True
        if spell == 'GeneHeal': self.gene = True
        if spell == 'Preraise': self.preraise = True

    def barrier_hit(self, value, max_hp):
        """Entity_ResolveDropTable under Barrier: PE -= value * (maxAtk * 4 / maxHP), HP untouched;
        Entity_UpdateTimers ends the barrier at PE <= 1 (clamped to 1)."""
        self.pe -= value * ((self.max * 4) // max(1, max_hp))
        if self.pe <= 0x10000: self.pe = 0x10000; self.barrier = False
