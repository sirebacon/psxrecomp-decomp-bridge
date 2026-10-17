"""Benchmark encounters: (name, builder) where builder(stage, enemies, profiles, rng) returns a dict
of fight() keyword arguments (foes, profile, threshold, ... ). Fixed seeds make them reproducible."""
import random
from .data import area_pool, DistanceProfile


class Scaled:
    """A profile with every distance multiplied (closer or farther variants)."""
    def __init__(self, base, k): self.base, self.k = base, k
    def sample(self, rng): return self.base.sample(rng) * self.k


def _group(pool, rng, n):
    return [dict(rng.choice(pool)) for _ in range(n)]


def stage_boss(enemies, stage):
    """A representative main-game boss for the stage: the one with the most HP in the area."""
    from .data import AREAS
    bosses = [e for e in enemies if e["boss"] and any(k in e["loc"] for k in AREAS[stage]) and e["hp"] < 900000]
    if not bosses:
        bosses = [e for e in enemies if e["boss"] and e["hp"] < 900000]
    return dict(max(bosses, key=lambda e: e["hp"]))


ENCOUNTERS = {}


def encounter(name, desc):
    def deco(fn):
        ENCOUNTERS[name] = (desc, fn); return fn
    return deco


@encounter("close_normal", "1-3 area enemies at normal-fight distances (log)")
def _(stage, enemies, prof, rng):
    pool = area_pool(enemies, stage)
    return dict(foes=_group(pool, rng, rng.choice((1, 2, 2, 3))), profile=prof["normal"])


@encounter("medium_mobile", "1-2 area enemies at boss-fight distances, moving every action (log)")
def _(stage, enemies, prof, rng):
    pool = area_pool(enemies, stage)
    return dict(foes=_group(pool, rng, rng.choice((1, 2))), profile=prof["boss"])


@encounter("groups", "3-4 area enemies at normal distances")
def _(stage, enemies, prof, rng):
    pool = area_pool(enemies, stage)
    return dict(foes=_group(pool, rng, rng.choice((3, 4))), profile=prof["normal"])


@encounter("keepaway_boss", "the stage boss at keep-away distances (room 156 profile)")
def _(stage, enemies, prof, rng):
    return dict(foes=[stage_boss(enemies, stage)], profile=prof["keepaway"])


@encounter("stationary_boss", "the stage boss staying close (normal profile x0.8)")
def _(stage, enemies, prof, rng):
    return dict(foes=[stage_boss(enemies, stage)], profile=Scaled(prof["normal"], 0.8))


@encounter("short_window", "damage dealt to the stage boss in a 6 s opening")
def _(stage, enemies, prof, rng):
    return dict(foes=[stage_boss(enemies, stage)], profile=prof["boss"], time_cap=6.0, window=True)


@encounter("scripted_day5", "Day 5 boss part 1: deal 450 real HP (def 33) with 3 helpers attacking, keep-away")
def _(stage, enemies, prof, rng):
    boss = dict(name="boss part 1", loc="", hp=1000450, level=30, defense=33, boss=True,
                heat="Average", frost="Average", cyanide="Strong", acid="Strong", tranq="Strong")
    adds = [dict(boss, name="helper", hp=1003392, defense=29) for _ in range(3)]
    # Damage taken calibrated: ~15 HP/s over the three logged attempts (434/27, 153/12, 131/8).
    per_hit = lambda e: 15.0 / (4 * 0.75 / 1.2)
    return dict(foes=[boss] + adds, profile=prof["keepaway"], threshold={0: 450}, target_first=0,
                enemy_dmg=per_hit, time_cap=120.0)


@encounter("endurance", "three area fights back to back, magazine carried over (ammo / reloads)")
def _(stage, enemies, prof, rng):
    pool = area_pool(enemies, stage)
    return dict(foes=_group(pool, rng, 6), profile=prof["normal"], chain=True)
