"""Aya's incoming status effects, ported from the decomp (offline).

Apply: battle/enemy_actions.c Battle_ApplyEnemyAttack, called by entity/combat.c
Entity_ResolveDropTable for every resolved enemy hit with effectType != 0 (no separate status
roll; also at zero damage and under Barrier). Tick: entity/combat.c Entity_UpdateTimers, once
per battle update, in its order: poison (Battle_SubActionStep: every effectDuration updates lose
effectLevel HP; timer 9000 - statusStep3E per update), confusion / darkness / stiffness (timers
9000 - statusStep3C), flag 0x1000 has no timer (cleared only by cures).

Each ailment pair: 0 clear, one bit = afflicted, both bits = one-use immunity from a cure taken
while healthy (consumed by the next matching attack). Armor resist mods: armor tail effect k sets
effectFlags bit 1 << (k - 1) (aya/stats.c Inv_BuildArmorList); the attack tests 0x1 poison,
0x2 confusion, 0x4 darkness, 0x8 stiffness (battle_ailment.h). Note the in-game mod names call
effect 2 "RESIST STIFFNESS" and 5 "RESIST CONFUSION"; the bits are used as the code does.

Combat effects modelled: poison HP loss, darkness forces weapon range to 200, stiffness (slow
or lock) slows ATB gain (and lock stops modelled movement), 0x1000 cuts the defense term to
3/10 (Entity_ResolveDropTable), HP-fraction effects 8 / 9 / 16, buff clear 2 (Haste only here).
Confusion (3) and steals (10-13) are tracked as unmodelled.
"""
from dataclasses import dataclass, field

POISON, CONFUSION, DARKNESS, STIFF_SLOW, STIFF_LOCK = 0x1, 0x4, 0x10, 0x40, 0x80
HASTE, BARRIER, FLAG_1000 = 0x100, 0x200, 0x1000
RESIST = {1: (0x1, 70), 3: (0x2, 60), 4: (0x4, 60), 5: (0x8, 50), 6: (0x8, 70)}


def armor_effect_flags(armor_effect_codes):
    """Inv_BuildArmorList: tail effects 1-5 -> bits 0x1..0x10 (6 / 7 auto medicine / cure)."""
    out = 0
    for k in armor_effect_codes:
        if 1 <= k <= 5: out |= 1 << (k - 1)
        elif k == 6: out |= 0x4000
        elif k == 7: out |= 0x8000
    return out


def s16(v): return ((v + 32768) & 65535) - 32768


@dataclass
class PlayerStatus:
    step3c: int
    step3e: int
    effect_flags: int = 0
    flags: int = 0
    timers: dict = field(default_factory=lambda: dict(poison=0, confusion=0, darkness=0, stiffness=0))
    poison_step: int = 0
    poison_period: int = 0
    poison_counter: int = 0
    unmodelled: int = 0

    def _resisted(self, effect_type, roll):
        bit, chance = RESIST[effect_type]
        return bool(self.effect_flags & bit) and roll() % 100 < chance

    def apply(self, effect_type, level, duration, roll, hp):
        """Battle_ApplyEnemyAttack. Returns the new HP (fraction effects) and what happened."""
        f = self.flags
        if effect_type == 1:
            if f & 0x3 == POISON: return hp, 'already'
            if self._resisted(1, roll): return hp, 'resisted'
            if f & 0x3 == 0x3: self.flags = f & ~0x3; return hp, 'immunity used'
            self.flags = (f & ~0x3) | POISON
            self.timers['poison'] = 0x2328
            self.poison_counter, self.poison_step = 0, level & 255
            self.poison_period = duration & 255
            return hp, 'poison'
        if effect_type == 2:
            self.flags &= ~(HASTE | BARRIER | 0x400 | 0x800)
            return hp, 'buffs cleared'
        if effect_type in (3, 4):
            mask, bit, key = (0xC, CONFUSION, 'confusion') if effect_type == 3 else (0x30, DARKNESS, 'darkness')
            if f & mask == bit: return hp, 'already'
            if self._resisted(effect_type, roll): return hp, 'resisted'
            if f & mask == mask: self.flags = f & ~mask; return hp, 'immunity used'
            self.flags = (f & ~mask) | bit
            self.timers[key] = 0x2328
            if effect_type == 3:
                roll()                                   # facing nudge rand(); motion not modelled
                self.unmodelled += 1
            return hp, key
        if effect_type in (5, 6):
            m = f & 0xC0
            if m == STIFF_LOCK or (effect_type == 6 and m == STIFF_SLOW): return hp, 'already'
            if self._resisted(effect_type, roll): return hp, 'resisted'
            if m == 0xC0: self.flags = f & ~0xC0; return hp, 'immunity used'
            self.flags = (self.flags & ~HASTE & ~0xC0) | (STIFF_LOCK if effect_type == 5 else STIFF_SLOW)
            self.timers['stiffness'] = 0x2328
            return hp, 'stiffness lock' if effect_type == 5 else 'stiffness slow'
        if effect_type == 7:
            self.flags |= FLAG_1000
            return hp, 'defense down'
        if effect_type == 8:
            return (hp >> 1 if not f & BARRIER and hp >= 2 else hp), 'halve hp'
        if effect_type == 9:
            self.flags &= ~(HASTE | BARRIER | 0x400 | 0x800)
            return (1 if hp >= 2 else -1 if hp == 1 else hp), 'hp to 1'
        if effect_type == 16:
            return ((hp * 3) // 4 if not f & BARRIER and hp >= 2 else hp), 'hp to 3/4'
        self.unmodelled += 1
        return hp, 'unmodelled'

    def tick(self):
        """Entity_UpdateTimers for Aya (one battle update). Returns poison HP lost."""
        lost = 0
        if self.flags & 0x3 == POISON:
            if self.poison_counter >= self.poison_period:
                lost = self.poison_step; self.poison_counter = 0
            self.poison_counter += 1
            self.timers['poison'] = s16(self.timers['poison'] - self.step3e)
            if self.timers['poison'] <= 0: self.flags &= ~0x3
        for key, mask, bit in (('confusion', 0xC, CONFUSION), ('darkness', 0x30, DARKNESS)):
            if self.flags & mask == bit:
                self.timers[key] = s16(self.timers[key] - self.step3c)
                if self.timers[key] <= 0: self.flags &= ~mask
        if self.flags & 0xC0 in (STIFF_SLOW, STIFF_LOCK):
            self.timers['stiffness'] = s16(self.timers['stiffness'] - self.step3c)
            if self.timers['stiffness'] <= 0: self.flags &= ~0xC0
        return lost

    @property
    def dark(self): return self.flags & 0x30 == DARKNESS

    @property
    def stiff(self): return self.flags & 0xC0 in (STIFF_SLOW, STIFF_LOCK)

    @property
    def locked(self): return self.flags & 0xC0 == STIFF_LOCK
