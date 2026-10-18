"""Fast loadout score for routine decisions and battles (A; validated against engine.fight at the
checkpoints, see evaluation.validate_surrogate).

Expected damage per second against a phase's typical enemy, from the same formulas the engine
uses: per-bullet power (offense / 5 + attack) x hit% - defense, crit / graze zones by distance
relative to the gun's range (play-log distance profiles), bullets per command by mode, the
magazine (reload only when empty, clicks), and turn time = max(ATB fill, firing commitment).
"""
import functools, random, statistics

from .. import data as D, engine as E, rules as R

PROFILES = D.load_profiles()
TIMING = "overlap"        # sensitivity: "serial" (the bar waits for the firing animation)
_SAMPLES = {}


def _dist(profile, n=3000):
    if profile not in _SAMPLES:
        rng = random.Random(97)
        _SAMPLES[profile] = [PROFILES[profile].sample(rng) for _ in range(n)]
    return _SAMPLES[profile]


@functools.lru_cache(maxsize=None)
def zone_mult(profile, rng_units, critical, rules_name):
    """Mean damage multiplier of a bullet (miss 0, graze 0.3 x chance, crit 1.5) over the profile."""
    rules = R.CURRENT if rules_name == "current" else R.VANILLA if rules_name == "vanilla" else R.experimental()
    tot = 0.0
    conv = rules["crit_convert_pct"] / 100.0 if critical else 0.0
    for d in _dist(profile):
        rel = d * 1000.0 / max(1, rng_units)
        if rel >= rules["miss_beyond"] + 1:
            continue
        graze = None
        for lo, hi, p in reversed(rules["graze_bands"]):
            if rel >= lo + 1:
                graze = p; break
        if graze is not None:
            tot += graze / 100.0 * rules["graze_mult"]
            continue
        thr = (rules["crit_points"] if critical else 0) + (5 if rel >= 801 else 20 if rel >= 501 else 50)
        pc = min(1.0, thr / 100.0)
        pc = pc + (1 - pc) * conv
        tot += 1 + (rules["crit_mult"] - 1) * pc
    return tot / len(_dist(profile))


def volley_bullets(eff, group):
    rof = eff.get("rof", 1)
    mode = eff.get("mode")
    if mode == "all": return rof * group, rof * group      # (rounds used, bullets landing)
    if mode == "random": return rof * 3 // 2, rof * 3 // 2
    if mode == "burst": return rof, rof * (1 + 0.5 * (group - 1))
    return rof, rof


@functools.lru_cache(maxsize=None)
def magazine_cycle(magazine, demand_per_cmd, commands, turns=40):
    """(mean rounds fired per turn, mean clicks per turn, reloads per turn): reload at the end
    of a turn only when the magazine is empty (D)."""
    loaded, fired, clicks, reloads = magazine, 0, 0, 0
    for _ in range(turns):
        for _c in range(commands):
            f = min(demand_per_cmd, loaded)
            loaded -= f; fired += f; clicks += demand_per_cmd - f
        if loaded <= 0:
            loaded = magazine; reloads += 1
    return fired / turns, clicks / turns, reloads / turns


def dps(cfg, aya, defense, profile="normal", group=2.0, rules=R.CURRENT, slow=False, timing=None):
    if rules.get('combat_backend')=='source':
        raise ValueError('source combat requires encounter benchmarks; aggregate surrogate is not calibrated')
    eff = cfg["eff"]
    if rules.get('animation_model') == 'asset_queue' and eff.get('mode'):
        raise ValueError('asset_queue currently supports ordinary queued shots only')
    kind = cfg["kind"]
    rof = eff.get("rof", 1)
    hitp = rules["hit_pct"].get(rof, 100)
    commands = eff.get("commands", 1)
    used, landing = volley_bullets(eff, group)
    fired, clicks, reloads = magazine_cycle(cfg["magazine"], used, commands)
    frac = fired / max(1e-9, used * commands)                    # share of the demand actually fired
    per = (aya["offense"] / 5.0 + cfg["power"]) * hitp / 100.0
    dmg = max(1.0, per - defense / (1 if kind == 8 else rof))
    if (eff.get("heat") or eff.get("frost")) and kind != 6:
        dmg *= rules["elem_neutral"] / 100.0
    damage_name = rules.get('damage_rules_name',rules['name'])
    mult = zone_mult(profile, cfg["range"], bool(eff.get("critical")), damage_name if damage_name in ("current", "vanilla") else "current")
    per_turn = landing * commands * frac * dmg * mult
    fill = E.rule_fill_seconds(aya["stat22"], kind, slow, rules)
    commit = E.commit_seconds(kind, int(round(fired)), rules) + reloads * E.RELOAD_S
    t = max(fill, commit) if (timing or TIMING) == "overlap" else fill + commit
    if eff.get("quickdraw"):
        t *= 0.97
    return per_turn / t


_RULES = {}


def score(cfg, aya, defense, rules=R.CURRENT):
    """Mixed suite: 70% normal-distance fights, 30% keep-away (geometric). Memoised."""
    _RULES.setdefault(rules["name"], rules)
    return _score(cfg["kind"], cfg["power"], cfg["range"], cfg["magazine"], tuple(sorted(cfg["eff"].items())),
                  aya["stat22"], aya["offense"], defense, rules["name"], TIMING)


@functools.lru_cache(maxsize=500000)
def _score(kind, power, rng_units, magazine, eff, stat22, offense, defense, rules_name, timing):
    rules = _RULES[rules_name]
    cfg = dict(kind=kind, power=power, range=rng_units, magazine=magazine, eff=dict(eff))
    aya = dict(stat22=stat22, offense=offense)
    a = dps(cfg, aya, defense, "normal", rules=rules, timing=timing)
    b = dps(cfg, aya, defense, "keepaway", group=1.0, rules=rules, timing=timing)
    return (max(a, 1e-6) ** 0.7) * (max(b, 1e-6) ** 0.3)
