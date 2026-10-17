"""Weapon bookkeeping and progression strategies.

Gun keeps the parts of its +bonuses apart (intrinsic from the item table, invested by the player:
boosters / bonus points, received through Tool transfers) and its installed mods. transfer()
follows armor_capacity.c TRANSFER_STAT: all three bonuses add to the destination (cap 999) and
the source's become 0; the source item stays (D).
"""

class Gun:
    def __init__(self, weapon):
        self.w = weapon
        self.intrinsic = [weapon.bonus_attack, weapon.bonus_range, weapon.bonus_bullets]
        self.invested = [0, 0, 0]
        self.received = [0, 0, 0]
        self.zeroed = False
        self.mods = []                 # installed extra effects (names as in data.MODS / FLAGS)
        self.slots_bought = 0          # Mod Permits used

    def bonus(self):
        return [min(999, self.intrinsic[i] + self.invested[i] + self.received[i]) for i in range(3)]

    def free_slots(self):
        return self.w.slots + self.slots_bought - len(self.w.builtin) - len(self.mods)

    def config(self):
        b = self.bonus()
        return self.w.config(self.mods, bonus_attack=b[0], bonus_range=b[1], bonus_bullets=b[2])


def transfer(src, dst):
    """Tool: move all three bonuses from src to dst; returns what moved."""
    moved = src.bonus()
    for i in range(3):
        room = 999 - dst.bonus()[i]
        dst.received[i] += min(moved[i], max(0, room))
    src.intrinsic = [0, 0, 0]; src.invested = [0, 0, 0]; src.received = [0, 0, 0]
    src.zeroed = True
    return moved


def transfer_mod(src, dst, name):
    """Tool: move one installed mod into a free slot of dst (fails when none is free)."""
    if name not in src.mods or dst.free_slots() <= 0:
        return False
    src.mods.remove(name); dst.mods.append(name)
    return True
