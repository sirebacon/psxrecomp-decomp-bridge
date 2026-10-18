"""pe_loot.c (CURRENT): battle Junk, soft-pity rare roll and the rare cascade, ported 1:1.

State that the game reads from the bag / storage (Tools held, Mod Permits held, kits carried,
economy mods unlocked) comes from the caller through LootView, at the moment of the roll, so a
Tool spent before a battle changes that battle's cascade (the Tool feedback loop).
"""
from . import tables as T

PRESET_JUNK = (150, 100, 75)
PRESET_PITY = (72, 100, 132)
PRESET_PITY_BASE = (150, 100, 50)
PRESET_PITY_STEP = (150, 100, 60)
PRESET_PRICE = (75, 100, 125)
RARE_BASE, RARE_STEP, RARE_GUARANTEE = 4, 1, 25
ECON_GUARANTEE, PERMIT_GUARANTEE = 8, 8
FLOOR, EXP_PER_JUNK, BATTLE_CAP, BOSS_CAP, NOHIT_BONUS = 1, 8, 12, 25, 25

CASCADE = [("econ", 15), ("supertool", 6), ("permit", 15), ("charm", 8), ("duper", 4), ("super", 8),
           ("tool", 0), ("booster", 100)]
CASCADE_ITEM = {"supertool": T.SUPER_TOOL, "permit": T.MOD_PERMIT, "duper": T.DUPER_JUNK,
                "super": T.SUPER_JUNK, "tool": T.TOOL}
TOOL_CHANCE = (85, 65, 40, 20, 10)
ECON_MODS = [("Scavenger", 18, 1), ("LuckyFind", 19, 2), ("Salvager", 20, 4), ("Bargain", 17, 3)]
BOOSTER_BASES = (0x1D, 0x21, 0x25, 0x29, 0x2D, 0x31)
BUNDLE_VALUE = {T.SUPER_JUNK: 75, T.DUPER_JUNK: 150}


class LootView:
    """What the cascade checks, read from the player state at roll time."""
    def __init__(self, tools_held=0, permits_held=0, tool_kit=False, super_tool_kit=False,
                 econ_unlocked=(), lucky_find=False, scavenger=False):
        self.tools_held, self.permits_held = tools_held, permits_held
        self.tool_kit, self.super_tool_kit = tool_kit, super_tool_kit
        self.econ_unlocked, self.lucky_find, self.scavenger = set(econ_unlocked), lucky_find, scavenger


class LootState:
    def __init__(self, rng, preset=1):
        self.rng, self.preset = rng, preset
        self.rare_dry = 0
        self.econ_since = 0
        self.permit_since = 0
        self.pity_hits = 0          # rolls that were certain (dry + 1 >= guarantee)
        self.rolls = 0
        self.history = []

    def rand(self, n):
        return self.rng.randrange(n)

    # ---- Junk ----------------------------------------------------------------------------------
    def battle_junk(self, exp, hits, boss, view):
        earned = FLOOR + exp // EXP_PER_JUNK
        earned = min(earned, BOSS_CAP if boss else BATTLE_CAP)
        if hits < 4:
            earned += earned * NOHIT_BONUS * (4 - hits) // 400
        earned = earned * PRESET_JUNK[self.preset] // 100
        if view.scavenger:
            earned += earned // 2
        return earned

    def price(self, base, bargain=False):
        if not base: return 0
        pct = PRESET_PRICE[self.preset]
        if bargain: pct = pct * 85 // 100
        p = (base * pct + 50) // 100
        return p or 1

    # ---- rare drops ----------------------------------------------------------------------------
    def guarantee(self):
        return max(1, RARE_GUARANTEE * PRESET_PITY[self.preset] // 100)

    def chance_permille(self):
        return (RARE_BASE * 10 * PRESET_PITY_BASE[self.preset] // 100 +
                RARE_STEP * 10 * PRESET_PITY_STEP[self.preset] // 100 * self.rare_dry)

    def roll(self, exp, view):
        """pe_roll_rare: returns ('item', id) / ('econ', name) / None."""
        self.rolls += 1
        certain = self.rare_dry + 1 >= self.guarantee()
        if certain or self.rand(1000) < self.chance_permille():
            self.pity_hits += certain
            self.rare_dry = 0
            return self.pick(exp, view)
        self.rare_dry = min(0xFFFF, self.rare_dry + (2 if view.lucky_find else 1))
        return None

    def skip(self, name, view, econ_missing):
        pct = dict(CASCADE)[name]
        if name == "econ": return econ_missing == 0, pct
        if name == "supertool": return view.super_tool_kit, pct
        if name == "permit": return view.permits_held >= 2, pct
        if name == "charm": return True, pct                       # removed 2026-10-15
        if name == "tool":
            if view.tool_kit or view.super_tool_kit or view.tools_held >= 5:
                return True, pct
            return False, TOOL_CHANCE[view.tools_held]
        return False, pct

    def pick(self, exp, view):
        missing = [m for m in ECON_MODS if m[0] not in view.econ_unlocked]
        hit = "booster"
        for name, _ in CASCADE:
            skipped, pct = self.skip(name, view, len(missing))
            if skipped:
                continue
            guarantee = since = 0
            if name == "econ": guarantee, since = ECON_GUARANTEE, self.econ_since
            if name == "permit": guarantee, since = PERMIT_GUARANTEE, self.permit_since
            certain = guarantee and since + 1 >= guarantee
            if name == "booster" or certain or self.rand(100) < pct:
                hit = name
                break
        if missing:
            self.econ_since = 0 if hit == "econ" else min(250, self.econ_since + 1)
        if view.permits_held < 2:
            self.permit_since = 0 if hit == "permit" else min(250, self.permit_since + 1)
        if hit == "econ":
            total = sum(w for _, _, w in missing)
            r = self.rand(total)
            for name, _, w in missing:
                if r < w:
                    out = ("econ", name); break
                r -= w
        elif hit != "booster":
            out = ("item", CASCADE_ITEM[hit])
        else:
            tier = 0 if exp < 20 else 1 if exp < 60 else 2 if exp < 150 else 3
            out = ("item", BOOSTER_BASES[self.rand(6)] + tier)
        self.history.append((hit, out))
        return out
