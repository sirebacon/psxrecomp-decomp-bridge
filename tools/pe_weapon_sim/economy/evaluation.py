"""Checkpoint combat benchmarks: the accumulated loadout and Aya's real stats go through the
phase 1/2 engine (engine.fight). Results are cached by loadout.

Phase 3 encounters use the enemies the run actually met in each phase (campaign script, L):
normal enemies with their logged HP / defense / resist bits, and the phase's real bosses
(scripted bosses carry 1,000,000 + real HP; the real part is used, as in phase 1's room 156).
Same encounter shapes as phase 1 (close / groups / medium-mobile / keep-away boss / stationary
boss / endurance / 6 s window), distance profiles from the play log. Enemy damage = 1.6 x level
with level fitted from defense (phase 1's fit inverted, A). Armor enters as Slow AT / Attack Up /
Down (the engine's armor model); armor defense is not in the combat model (A, see report K).
"""
import math, random, statistics

from .. import data as D, encounters as N, engine as E
from ..run_benchmark import summarize, PROF
from . import acquisition as AQ, surrogate as SG

SUITE = ("close_normal", "groups", "medium_mobile", "keepaway_boss", "stationary_boss", "endurance", "short_window")
SCORE_SET = ("close_normal", "groups", "medium_mobile", "keepaway_boss", "stationary_boss", "endurance")
_CACHE = {}


def armor_of(item):
    names = item.effect_names() if item else []
    return dict(slow_at="SlowAT" in names, attack_levels=names.count("AttackUp") - names.count("AttackDown"))


def _pools():
    camp = AQ.load_campaign()
    normal, boss = {}, {}
    for e in camp["events"]:
        if e["type"] != "battle" or e["outcome"] != "win":
            continue
        for x in e["enemies"]:
            hp = x["hp"] - 1000000 if x["hp"] > 1000000 else x["hp"]
            if hp <= 0 or x["defense"] >= 200 or x["id"] == "0x0200":
                continue                       # invulnerable / scripted-only parts; room-156 helpers
            lv = max(1, round((x["defense"] - 3) / 1.6))
            row = dict(name=x["id"], loc=e["map"], hp=hp, level=lv, defense=x["defense"], boss=x["boss"],
                       heat=x["heat"], frost=x["frost"], cyanide=x["cyanide"], acid=x["acid"], tranq=x["tranq"])
            if x["boss"]:
                if hp >= 150:
                    boss.setdefault(e["phase"], {})[(x["id"], hp, x["defense"])] = row
            else:
                normal.setdefault(e["phase"], {})[(x["id"], hp, x["defense"])] = row
    return ({p: list(v.values()) for p, v in normal.items()}, {p: list(v.values()) for p, v in boss.items()})


NORMAL, BOSSES = _pools()


def _pick(pool, rng, n):
    return [dict(rng.choice(pool)) for _ in range(n)]


def build_encounter(enc, phase, rng):
    nm, bs = NORMAL[phase], BOSSES.get(phase) or sorted(NORMAL[phase], key=lambda r: -r["hp"])[:3]
    if enc == "close_normal": return dict(foes=_pick(nm, rng, rng.choice((1, 2, 2, 3))), profile=PROF["normal"])
    if enc == "groups": return dict(foes=_pick(nm, rng, rng.choice((3, 4))), profile=PROF["normal"])
    if enc == "medium_mobile": return dict(foes=_pick(nm, rng, rng.choice((1, 2))), profile=PROF["boss"])
    if enc == "keepaway_boss": return dict(foes=_pick(bs, rng, 1), profile=PROF["keepaway"])
    if enc == "stationary_boss": return dict(foes=_pick(bs, rng, 1), profile=N.Scaled(PROF["normal"], 0.8))
    if enc == "short_window": return dict(foes=_pick(bs, rng, 1), profile=PROF["boss"], time_cap=6.0, window=True)
    if enc == "endurance": return dict(foes=_pick(nm, rng, 6), profile=PROF["normal"], chain=True)
    if enc == "scripted_day5":
        _, builder = N.ENCOUNTERS["scripted_day5"]
        return builder("Day5", [], PROF, rng)
    raise KeyError(enc)


def run_enc(rules, cfg, aya, enc, phase, n, seed=7, armor=None, timing="overlap", policy="stand", **extra):
    out = []
    for i in range(n):
        kw = build_encounter(enc, phase, random.Random(seed * 100003 + i))
        window = kw.pop("window", False); chain = kw.pop("chain", False)
        foes, prof = kw.pop("foes"), kw.pop("profile")
        kw.update(extra)
        rng = random.Random(seed * 7919 + i)
        if chain:
            tot = E.Stats(); loaded = None;source_state=None
            for j in range(3):
                fight_kw=dict(kw)
                if source_state is not None:
                    fight_kw['source_options']=dict(fight_kw.get('source_options') or {},initial_state=source_state)
                st = E.fight(rules, cfg, aya, foes[2 * j:2 * j + 2], prof, rng, policy=policy, timing=timing,
                             armor=armor, start_loaded=loaded, **fight_kw)
                loaded = st["loaded_left"]
                source_state=st.get('_source_state')
                for k, v in st.items():
                    if k != "loaded_left" and not k.startswith('_'): tot.add(k, v)
            tot["won"] = int(tot["won"] == 3)
            out.append(tot)
        else:
            st = E.fight(rules, cfg, aya, foes, prof, rng, policy=policy, timing=timing, armor=armor, **kw)
            st["window"] = int(window)
            out.append(st)
    return out

def cfg_key(cfg):
    return (cfg["kind"], cfg["power"], cfg["range"], cfg["magazine"], tuple(sorted(cfg["eff"].items())),
            getattr(cfg.get("weapon"), "id", None))


def benchmark(rules, cfg, aya, phase, armor=None, n=16, seed=7, timing="overlap", policy="stand", suite=SUITE):
    key = (rules["name"], cfg_key(cfg), tuple(sorted(aya.items())), phase, tuple(sorted((armor or {}).items())),
           n, seed, timing, policy, suite)
    if key in _CACHE:
        return _CACHE[key]
    res = {}
    for enc in suite:
        sts = run_enc(rules, cfg, aya, enc, phase, n, seed=seed, armor=armor, timing=timing, policy=policy)
        s = summarize(sts)
        s["clicks"] = round(statistics.mean(x.get("click", 0) for x in sts), 2)
        res[enc] = s
    if phase == "D5":
        sts = run_enc(rules, cfg, aya, "scripted_day5", phase, n, seed=seed, armor=armor, timing=timing, policy="walk")
        res["scripted_day5"] = summarize(sts)
    logs = [math.log(max(0.1, res[e]["time_mean"] + (0 if res[e]["win"] >= 0.999 else 60))) for e in SCORE_SET if e in res]
    res["suite_time"] = round(math.exp(sum(logs) / len(logs)), 3)
    res["window_damage"] = res.get("short_window", {}).get("damage")
    _CACHE[key] = res
    return res


def validate_surrogate(rules, loadouts, phase, n=16):
    """Rank agreement between the surrogate score and the engine's suite time over loadouts:
    returns (Spearman rho of score vs 1/time, pairs)."""
    pairs = []
    for cfg, aya in loadouts:
        s = SG.score(cfg, aya, {"D1": 8, "D2-4": 20, "D5": 32, "Disc2": 48}[phase], rules)
        b = benchmark(rules, cfg, aya, phase, n=n)
        pairs.append((s, 1.0 / b["suite_time"]))
    return spearman([p[0] for p in pairs], [p[1] for p in pairs]), pairs


def spearman(a, b):
    def ranks(x):
        o = sorted(range(len(x)), key=lambda i: x[i]); r = [0] * len(x)
        k = 0
        while k < len(o):
            end = k + 1
            while end < len(o) and x[o[end]] == x[o[k]]:
                end += 1
            for i in o[k:end]:
                r[i] = (k + end - 1) / 2
            k = end
        return r
    if len(a) != len(b):
        raise ValueError("rank vectors must have equal length")
    ra, rb = ranks(a), ranks(b)
    n = len(a)
    if n < 3: return float("nan")
    ma, mb = statistics.mean(ra), statistics.mean(rb)
    va = sum((x - ma) ** 2 for x in ra)
    vb = sum((y - mb) ** 2 for y in rb)
    return sum((x - ma) * (y - mb) for x, y in zip(ra, rb)) / math.sqrt(va * vb) if va and vb else float("nan")
