"""Aya's source stats and defensive inputs (2026-10-18).

Tables: AyaLevelStats[99] and the 7 stat-growth tables read from the resident data pack
(findings/data/pe-aya-level-stats-2026-10-18.json, read-only live probe, R).
Rules (D):
  Aya_StatQueryLevelAndSubLevel: stat level = largest i with growth[kind][i] <= value.
  Level-ups add 10 to every stat value, so Aya level L has value 10*(L-1) on each track
  (live: level 33 -> 320 on tracks 0-5). Kind 5 (Active Time) has uneven early thresholds
  (0,20,28,36,48,72,84,96,105,120,129,140,150,160, then +10), so stat22 lags the level:
  live level 33 -> AT level 29 -> stat22 79 (the phase 1-3 linear 49+L gave 82).
  BP buys the next threshold of kind 5 / 6 (Menu_SpendBonusPoints).
  Inv_RecalcSlotStats: offense / defense (stat20) / stat22 = row[level + g_StatScaleBase[k]]
  (the scale bases read 0 for those tracks live).
  Inv_BuildArmorList: first = armor attack-or-defense (base+bonus, cap 999, action slots 0-2),
  second = PE defense (slots 3+), third = critical resist from CR evade.
  Entity_ResolveDropTable: damage = power - stat20/5 - first|second, crit chance x (100-third)%.
Verified live (Eve fight, level 33, N Jacket +32/21/12): stat20 362, first 66, second 49,
third 30, offense 350, stat22 79 all match.
"""
import bisect, json, math, os

from . import tables as T

DATA = os.path.join(T.FIND, "pe-aya-level-stats-2026-10-18.json")
with open(DATA) as _fh:
    _D = json.load(_fh)
ROWS = _D["rows"]
GROWTH = {int(k): v for k, v in _D["growth"].items()}


def stat_level(kind, value):
    g = GROWTH[kind]
    return max(0, bisect.bisect_right(g, value) - 1)


def row(level):
    return ROWS[min(98, max(0, level))]


def value_at(aya_level):
    return 10 * (max(1, aya_level) - 1)


def next_threshold(kind, value):
    """The value a 100-BP purchase sets (the next growth threshold)."""
    g = GROWTH[kind]
    i = stat_level(kind, value)
    return g[min(len(g) - 1, i + 1)]


def critical_resist(evade):
    v = min(999, evade)
    if v < 85:
        return (math.isqrt(v * 3000) // 10) & 255
    return ((v * 249 // 208 + 402) // 10) & 255


def armor_inputs(item):
    """Inv_BuildArmorList parameter word for an armor Item (None -> zeros)."""
    if item is None:
        return dict(armor_first=0, armor_second=0, critical_resist=0)
    tot = [min(999, item.base[i] + item.bonus[i]) for i in range(3)]
    return dict(armor_first=tot[0], armor_second=tot[1], critical_resist=critical_resist(tot[2]))


def aya_stats(aya_level, at_extra=0, cap_extra=0, hp_scale=0):
    """Source battle stats for Aya at a level with extra AT / capacity value bought by BP."""
    v = value_at(aya_level)
    lv = stat_level(0, v)
    status = row(stat_level(4, v))                   # Inv_RecalcSlotStats track 4: status steps
    return dict(level=aya_level, max_hp=(hp_scale + 20) * row(lv)["hp"] // 20,
                offense=row(stat_level(1, v))["offense"], defense=row(stat_level(2, v))["defense"],
                stat22=row(stat_level(5, v + at_extra))["stat22"],
                capacity=row(stat_level(6, v + cap_extra))["capacity"],
                status_step3c=status["status3c"], status_step3e=status["status3e"])


def player_inputs(aya_level, armor_item, at_extra=0, cap_extra=0):
    """The aya dict for engine.fight / source_combat: level, stat22, offense, defense and armor."""
    from ..player_status import armor_effect_flags
    s = aya_stats(aya_level, at_extra, cap_extra)
    out = dict(level=s["level"], stat22=s["stat22"], offense=s["offense"], defense=s["defense"],
               status_step3c=s["status_step3c"], status_step3e=s["status_step3e"],
               armor_effect_flags=armor_effect_flags(armor_item.effects() if armor_item else []))
    out.update(armor_inputs(armor_item))
    return out
