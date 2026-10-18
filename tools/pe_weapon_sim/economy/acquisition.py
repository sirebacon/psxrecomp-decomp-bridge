"""Progression event streams by exploration profile, built from the one real playthrough.

Backbone (L): the campaign script (campaign.py) - every kept battle with its enemies (EXP, BP
base / factor / hits on Aya), vanilla reward items, field Tools / boosters / Mod Permits, save
rows (the logged loadout over time). Gear: the gear-locations table (A: wiki) by area -> phase.

Profiles (the transformations are assumptions, bounded in the sensitivity runs):
  typical       the logged run without its farming streaks (battles 4+ in a row in one map),
                the gear the player actually picked up, logged field items.
  minimal       typical with 60% of non-boss battles, 60% of the optional field items, half the gear.
  completionist typical + 25% more non-boss battles (same phase), +30% field items, all table gear.
  farmer        typical + the logged farming streaks x2.
  logged        the run exactly as logged (farming once): calibration.
"""
import json, random

from . import tables as T

PROFILES = ("minimal", "typical", "completionist", "farmer", "logged")
UPGRADE_ITEMS = {T.TOOL, T.SUPER_TOOL, T.TOOL_KIT, T.SUPER_TOOL_KIT, T.MOD_PERMIT} | set(range(0x1D, 0x35))


def load_campaign(path=T.CAMPAIGN_JSON):
    with open(path) as fh:
        return json.load(fh)


def _farm_flags(battles):
    """A battle is farming when it is the 4th+ consecutive battle in the same map (not a boss)."""
    flags, run, last = [], 0, None
    for b in battles:
        run = run + 1 if b["map"] == last else 1
        last = b["map"]
        flags.append(run >= 4 and not b["boss"])
    return flags


def logged_loadouts(camp):
    """[(battle index, gun dict, armor dict)] from save rows: the loadout in use from that battle on."""
    out, n = [], 0
    for e in camp["events"]:
        if e["type"] == "battle":
            n += 1
        elif e["type"] == "save" and "gun" in e:
            out.append((n, e["gun"], e.get("armor")))
    return out


def logged_loadouts_t(camp):
    """[(progress clock, gun dict, armor dict)] sorted by clock, for the combat-feedback reference."""
    out = [(tuple(e["t"]), e["gun"], e.get("armor")) for e in camp["events"] if e["type"] == "save" and "gun" in e]
    return sorted(out, key=lambda x: x[0])


def gear_picked(camp):
    """Gear ids the player picked up in the field (log) - matched against the location table."""
    ids = set()
    for e in camp["events"]:
        if e["type"] == "field" and not e.get("post_battle") and 0x3F <= e["item"] <= 0xC7:
            ids.add(e["item"])
    return ids


def build(profile, camp, rng):
    """Ordered events for one run. rng is the encounter stream (independent of loot / policy)."""
    assert profile in PROFILES
    events = camp["events"]
    battles = [e for e in events if e["type"] == "battle" and e["outcome"] == "win"]
    farm = dict(zip(map(id, battles), _farm_flags(battles)))
    table_gear = T.GEAR_LOCATIONS
    picked = gear_picked(camp)
    if profile == "completionist":
        gear = list(table_gear)
    else:
        gear = [g for g in table_gear if g[0] in picked]
        if profile == "minimal":
            gear = [g for g in gear if rng.random() < 0.5]
    # Gear arrives spread over its phase: slot it after a battle drawn uniformly within the phase.
    by_phase = {p: [i for i, b in enumerate(battles) if b["phase"] == p] for p in T.PHASES}
    out = []
    gear_at = {}
    for iid, phase, area in gear:
        idx = by_phase.get(phase) or [0]
        gear_at.setdefault(rng.choice(idx), []).append(("gear", iid, area))
    extra_battles = {}
    if profile == "completionist":
        for p in T.PHASES:
            pool = [b for b in battles if b["phase"] == p and not b["boss"] and not farm[id(b)]]
            for _ in range(int(round(0.25 * len(pool)))):
                extra_battles.setdefault(rng.choice(by_phase[p]), []).append(rng.choice(pool))
    wayne_marks = _wayne_points(battles)
    bi = -1
    for e in events:
        t = e["type"]
        if t == "battle":
            if e["outcome"] != "win":
                continue
            bi += 1
            if bi in wayne_marks:
                out.append(dict(type="wayne", phase=e["phase"], why=wayne_marks[bi]))
            if farm[id(e)] and profile != "logged":
                if profile == "farmer":
                    out.append(dict(e, farm=True)); out.append(dict(e, farm=True))
                continue
            if profile == "minimal" and not e["boss"] and rng.random() > 0.6:
                continue
            out.append(e)
            for x in extra_battles.get(bi, []):
                out.append(dict(x, extra=True))
            for g in gear_at.get(bi, []):
                out.append(dict(type="gear", phase=e["phase"], item=g[1], area=g[2]))
        elif t == "field" and not e.get("post_battle") and e["item"] in UPGRADE_ITEMS:
            keep = 1
            if profile == "minimal":
                keep = 1 if rng.random() < 0.6 else 0
            elif profile == "completionist":
                keep = 2 if rng.random() < 0.3 else 1
            for _ in range(keep):
                out.append(dict(type="pickup", phase=e["phase"], item=e["item"]))
    out.append(dict(type="wayne", phase="Disc2", why="end"))
    return out


def _wayne_points(battles):
    """Wayne (storage, Mod Permits, his 300-Junk gun) is visited at each phase start, at the end
    of Day 5 and once mid Day 6 (the run's visits to the precinct / ship, L)."""
    marks, last = {}, None
    d6 = [i for i, b in enumerate(battles) if b["phase"] == "Disc2"]
    for i, b in enumerate(battles):
        if b["phase"] != last and last is not None:
            marks[i] = "phase " + b["phase"]
        last = b["phase"]
    if d6:
        marks.setdefault(d6[len(d6) // 2], "mid Disc2")
    d24 = [i for i, b in enumerate(battles) if b["phase"] == "D2-4"]
    if d24:   # Day 4 (the Hospital) starts about 70% of the way through the run's Days 2-4 battles (A)
        marks.setdefault(d24[int(len(d24) * 0.7)], "Day 4")
    return marks
