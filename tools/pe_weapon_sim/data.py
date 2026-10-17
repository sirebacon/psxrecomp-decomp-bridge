"""Game data for the simulator: weapons (game item table), enemies (wiki + log-fitted defense),
distance profiles (play log), Aya's stats by story stage."""
import bisect, csv, json, math, os, random, re

HERE = os.path.dirname(os.path.abspath(__file__))
FIND = os.path.join(HERE, "..", "..", "findings", "data")
WEAPONS_CSV = os.path.join(FIND, "pe-weapons-game-2026-10-16.csv")
ENEMIES_CSV = os.path.join(FIND, "pe-enemies-wiki-2026-10-14.csv")
CALIB_JSON = os.path.join(FIND, "pe-calibration-2026-10-16.json")

KIND = {1: "handgun", 2: "shotgun", 3: "machine", 4: "rifle", 5: "grenade", 6: "rocket", 7: "special", 8: "club"}
# g_BattleActionOffenseScale 0x800106D4, by actionId == item kind (R).
ATB_FACTOR = {1: 10, 2: 8, 3: 10, 4: 8, 5: 8, 6: 4, 7: 10, 8: 20}
# g_BattleActionAnimRows 0x800106A4: [windup loops, extra windup, loops per extra shot, recovery loops, hit frame] (R).
ANIM = {1: (0, 0, 5, 10, 2), 2: (5, 0, 0, 10, 4), 3: (0, 0, 0, 10, 2), 4: (10, 7, 0, 10, 4),
        5: (0, 0, 5, 15, 3), 6: (0, 0, 20, 30, 3), 7: (0, 0, 5, 10, 2), 8: (0, 0, 0, 0, 5)}
MODS = {"RoF2": ("rof", 2), "RoF3": ("rof", 3), "RoF5": ("rof", 5), "RoF7": ("rof", 7), "RoF10": ("rof", 10),
        "Random": ("mode", "random"), "Burst": ("mode", "burst"), "AttackAll": ("mode", "all"),
        "2Cmd": ("commands", 2), "3Cmd": ("commands", 3)}
FLAGS = ("Heat", "Frost", "Cyanide", "Acid", "Tranq", "Counter", "Quickdraw", "Critical")


def range_units(stat):
    """Inv_BuildWeaponList: isqrt(stat * 22500) = 150 * sqrt(stat) (D)."""
    return int(math.isqrt(max(0, min(999, stat)) * 22500))


class Weapon:
    def __init__(self, row):
        self.id = int(row["id"], 16)
        self.name = row["name"]
        self.kind = int(row["kind"])
        self.attack = int(row["attack"]); self.range_stat = int(row["range"]); self.bullets = int(row["bullets"])
        self.bonus_attack = int(row["bonus_attack"]); self.bonus_range = int(row["bonus_range"])
        self.bonus_bullets = int(row["bonus_bullets"])
        self.slots = int(row["slots"]); self.slot_cap = int(row["slot_cap"])
        self.builtin = [e for e in row["effects"].split("|") if e and e != "m00"]

    def config(self, extra=(), bonus_attack=None, bonus_range=None, bonus_bullets=None):
        """A loadout: built-in effects plus `extra`, the last one of a group (RoF, spread, commands) wins."""
        eff = {"rof": 1}
        for e in list(self.builtin) + list(extra):
            if e in MODS:
                k, v = MODS[e]; eff[k] = v
            elif e in FLAGS:
                eff[e.lower()] = True
        ba = self.bonus_attack if bonus_attack is None else bonus_attack
        br = self.bonus_range if bonus_range is None else bonus_range
        bb = self.bonus_bullets if bonus_bullets is None else bonus_bullets
        return dict(weapon=self, kind=self.kind, power=self.attack + ba,
                    range=range_units(self.range_stat + br), magazine=max(1, self.bullets + bb), eff=eff)

    def free_slots(self):
        return self.slots - len(self.builtin)


def load_weapons():
    with open(WEAPONS_CSV, newline="") as fh:
        return {w.id: w for w in (Weapon(r) for r in csv.DictReader(fh))}


# Main-game availability (where each gun is first available; RPGClassics weapons page, A).
STAGES = ["Day1", "Day2", "Day3", "Day4", "Day5"]
AVAILABLE = {  # stage -> gun ids
    "Day1": [0x44, 0x50],
    "Day2": [0x45, 0x79],
    "Day3": [0x94, 0x5A, 0x71, 0x6F, 0x7B],
    "Day4": [0x5B, 0x7D, 0x89],
    "Day5": [0x47, 0x48, 0x5F, 0x72, 0x68, 0x6A, 0x86, 0x66, 0x6E, 0x78, 0x82, 0x8F],
}
WAYNE_DAY5 = {0x66, 0x6E, 0x78, 0x82, 0x8F}
# Aya by stage: level from the play log, stat22 and offense from the game's level table
# (AyaLevelStats at *0x800A803C + 0x800A8028, read from a save state; R).
AYA = {"Day1": dict(level=7, stat22=56, offense=65), "Day2": dict(level=12, stat22=61, offense=90),
       "Day3": dict(level=16, stat22=65, offense=135), "Day4": dict(level=19, stat22=68, offense=170),
       "Day5": dict(level=24, stat22=73, offense=200)}
AYA_LEVEL21 = dict(level=21, stat22=70, offense=180)   # the Day 5 keep-away boss attempts
# Free mod slots a player realistically fills by stage (mods found / bought so far, A).
MOD_BUDGET = {"Day1": 0, "Day2": 1, "Day3": 2, "Day4": 3, "Day5": 4}
# Effects available to install by stage (main game; Cyanide and 3 Commands are EX-game, A).
MOD_POOL = {"Day1": [], "Day2": ["RoF3", "Heat"], "Day3": ["RoF3", "RoF5", "Heat", "Frost", "Acid", "Burst"],
            "Day4": ["RoF3", "RoF5", "Heat", "Frost", "Acid", "Tranq", "Burst", "Random", "Critical", "Quickdraw", "Counter"],
            "Day5": ["RoF3", "RoF5", "RoF7", "Heat", "Frost", "Acid", "Tranq", "Burst", "Random", "AttackAll",
                     "Critical", "Quickdraw", "Counter", "2Cmd"]}

AREAS = {"Day1": ["Theater", "Carnegie"], "Day2": ["Central Park"], "Day3": ["NYPD", "N.Y.P.D"],
         "Day4": ["Hospital"], "Day5": ["Chinatown", "Sewer", "Subway", "Museum", "Warehouse"]}


def _num(s):
    m = re.search(r"[\d,]+", s or "")
    return int(m.group(0).replace(",", "")) if m else None


def defense_of(level):
    return round(1.6 * level + 3)          # L: least-squares over 18 logged enemies


def load_enemies():
    out = []
    with open(ENEMIES_CSV, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        if "Chrysler" in r["location"] or not r["location"]:
            continue
        hp, lvl = _num(r["hp"]), _num(r["level"])
        if not hp or not lvl or r["Heat"] == "?":
            continue
        out.append(dict(name=r["variant"], loc=r["location"], hp=hp, level=lvl, defense=defense_of(lvl),
                        boss=r["o_Escape"] == "No", heat=r["Heat"], frost=r["Freeze"],
                        cyanide=r["Cyanide"], acid=r["Acid"], tranq=r["Tranq"]))
    return out


def area_pool(enemies, stage, boss=False):
    kws = AREAS[stage]
    return [e for e in enemies if any(k in e["loc"] for k in kws) and e["boss"] == boss]


class DistanceProfile:
    """Absolute distance (game units) at Aya's turn, sampled from play-log bins (L)."""

    def __init__(self, bins, tail=None, ref_range=1492):
        self.bins = [b for b in bins if b[2] > 0]
        tot = sum(b[2] for b in self.bins)
        inside = 1.0
        self.tail = []
        if tail:
            inside = max(0.0, 1.0 - tail["far"] - tail["out"])
            self.tail = [((1.5 * ref_range, 1.8 * ref_range), tail["far"]), ((1.8 * ref_range, 2.4 * ref_range), tail["out"])]
        self.cum, acc = [], 0.0
        for b in self.bins:
            acc += b[2] / tot * inside; self.cum.append(acc)
        for (lo, hi), w in self.tail:
            acc += w; self.cum.append(acc)
        self.parts = [(b[0], b[1]) for b in self.bins] + [lh for lh, _ in self.tail]
        self.total = acc

    def sample(self, rng):
        x = rng.random() * self.total
        i = min(bisect.bisect_left(self.cum, x), len(self.parts) - 1)
        lo, hi = self.parts[i]
        return rng.uniform(lo, hi)

    def mean(self, n=20000, seed=1):
        r = random.Random(seed)
        return sum(self.sample(r) for _ in range(n)) / n


def load_profiles():
    with open(CALIB_JSON) as fh:
        d = json.load(fh)
    prof = {}
    for ctx, bins in d["abs_distance"].items():
        # hitq bins already include grazes; the reach tail adds the far / out-of-reach time hits never show.
        prof[ctx] = DistanceProfile(bins, d["reach_tail"].get(ctx))
    return prof
