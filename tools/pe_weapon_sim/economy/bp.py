"""Bonus Points: earning (per enemy, minus hits taken), the level-up bank, and spending.

Game rules (D, see rules.VALIDATION): each defeated enemy adds max(0, base - A x hits it landed)
to the battle's reward; Aya_SetTotalExp adds the battle's BP to a pool that becomes spendable
only when the battle's EXP makes Aya level up (spendable total capped at 99,999). Spending 100 BP
buys +1 of a weapon's attack / range / bullets or an armor axis (bonusStats, cap 999), or +1 stat
level of Active Time (stat22) or item capacity.
"""
from . import tables as T

CATEGORIES = ("attack", "range", "bullets", "armor", "active_time", "capacity")
STAT_INDEX = {"attack": 0, "range": 1, "bullets": 2}


def enemy_bp(base, factor, hits):
    return max(0, base - factor * hits)


class Ledger:
    def __init__(self, cost=100, cap=99999):
        self.cost, self.cap = cost, cap
        self.earned = 0          # every BP a battle awarded
        self.pool = 0            # awarded, waiting for a level-up
        self.banked = 0          # spendable
        self.spent = {c: 0 for c in CATEGORIES}
        self.lost_to_hits = 0
        self.capped = 0          # banked past the cap: gone
        self.history = []        # (when, what, amount, detail)

    @property
    def total_spent(self): return sum(self.spent.values())

    def award(self, amount, lost, when):
        self.earned += amount; self.pool += amount; self.lost_to_hits += lost
        self.history.append((when, "earn", amount, lost))

    def level_up(self, when):
        """Aya_SetTotalExp: on a level-up the pool is banked (total capped)."""
        if self.pool:
            room = max(0, self.cap - self.banked)
            add = min(room, self.pool)
            self.banked += add
            self.capped += self.pool - add
            self.history.append((when, "bank", add, self.pool - add))
            self.pool = 0

    def can_spend(self, n=1): return self.banked >= self.cost * n

    def spend(self, category, when, detail=""):
        assert category in CATEGORIES
        if not self.can_spend():
            raise ValueError("not enough banked BP")
        self.banked -= self.cost
        self.spent[category] += self.cost
        self.history.append((when, "spend", self.cost, category + (" " + detail if detail else "")))

    def check(self):
        assert self.banked >= 0 and self.pool >= 0
        assert self.banked + self.pool + self.total_spent + self.capped == self.earned, (self.banked, self.pool, self.spent, self.earned)


class Aya:
    """Aya's level, Active Time and capacity stat levels (BP buys stat levels on top of level-ups)."""

    def __init__(self, source=False):
        """source=False keeps the phase 1-3 linear approximations (historical results);
        source=True uses the game's level-stat rows and growth tables (source_stats)."""
        self.exp = 0
        self.at_bought = 0
        self.cap_bought = 0
        self.source = source
        self.at_extra = 0        # stat value bought above 10 x (level - 1), source mode
        self.cap_extra = 0
        self.armor = None        # worn armor Item, for source defensive inputs

    @property
    def level(self): return T.level_of(self.exp)

    def buy_active_time(self):
        """100 BP: the Active Time value jumps to the next kind-5 threshold (source mode)."""
        if self.source:
            from . import source_stats as S
            v = S.value_at(self.level) + self.at_extra
            self.at_extra += S.next_threshold(5, v) - v
        self.at_bought += 1

    def buy_capacity(self):
        if self.source:
            from . import source_stats as S
            v = S.value_at(self.level) + self.cap_extra
            self.cap_extra += S.next_threshold(6, v) - v
        self.cap_bought += 1

    def _src(self):
        from . import source_stats as S
        return S.aya_stats(self.level, self.at_extra, self.cap_extra)

    @property
    def stat22(self):
        return self._src()["stat22"] if self.source else T.stat22_of(self.level + self.at_bought)

    @property
    def offense(self):
        return self._src()["offense"] if self.source else T.offense_of(self.level)

    def capacity(self, armor_bag=0):
        base = self._src()["capacity"] if self.source else T.capacity_of(self.level + self.cap_bought)
        return min(50, base + armor_bag)

    def combat(self):
        out = dict(level=self.level, stat22=self.stat22, offense=self.offense)
        if self.source:
            from . import source_stats as S
            out.update(defense=self._src()["defense"], **S.armor_inputs(self.armor))
        return out
