"""Aya's bag and Wayne's storage.

Bag slots: each gear item, Tool, Super Tool, Mod Permit, kit and booster takes one slot (D: one
item per slot); healing items and ammo pools take a reserve that grows with the story (A: the
run carried 6-8 consumable kinds, L save rows). Storage (Wayne's trunk, 100 slots) is reachable
only at Wayne. Capacity = the item-capacity stat (level + BP) + bag mods on the worn armor.
"""
from . import tables as T

RESERVE = {"D1": 4, "D2-4": 6, "D5": 7, "Disc2": 8}
STACKED = (T.TOOL, T.SUPER_TOOL, T.MOD_PERMIT, T.TOOL_KIT, T.SUPER_TOOL_KIT)


class Inventory:
    def __init__(self):
        self.gear = {}                       # uid -> Item (alive, in the bag)
        self.stored = {}                     # uid -> Item (Wayne's storage)
        self.count = {k: 0 for k in STACKED}           # in the bag
        self.stored_count = {k: 0 for k in STACKED}    # in storage
        self.boosters = []                   # booster item ids waiting to be used
        self.overflow = 0                    # pickups refused for lack of room
        self.overflow_log = []
        self.reserve_cut = {}                # consumables dropped to make room, per phase

    def used(self, phase):
        return (RESERVE[phase] - self.reserve_cut.get(phase, 0) + len(self.gear) + sum(self.count.values())
                + len(self.boosters))

    def free(self, capacity, phase):
        return capacity - self.used(phase)

    def held(self, kind):
        """Bag + storage (the cascade counts both, D pe_loot.c pe_held)."""
        return self.count[kind] + self.stored_count[kind]

    def has_kit(self):
        return self.held(T.TOOL_KIT) > 0 or self.held(T.SUPER_TOOL_KIT) > 0

    def check(self):
        for k in STACKED:
            assert self.count[k] >= 0 and self.stored_count[k] >= 0
        for it in list(self.gear.values()) + list(self.stored.values()):
            assert it.alive
            it.check()
