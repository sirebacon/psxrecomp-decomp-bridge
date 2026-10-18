"""Source-derived gauge transitions; units are eligible battle updates, NOT VBlanks.

References are relative to Parasite Eve Project:
decomp/src/main/battle/enemy_actions.c: Battle_SetupEnemyAnims
decomp/src/main/menu/main_update.c: Menu_MainUpdate
recomp/src/mods/pe_atb_items.c: pe_on_battle_update
Clock rate and animation/menu duration are deliberately caller inputs.
"""
from dataclasses import dataclass
from .data import ATB_FACTOR

FULL = 9000
HALF = 4500


def gauge_gain(stat22, kind, *, slow=False, haste=False):
    if stat22 < 0 or kind not in ATB_FACTOR:
        raise ValueError('expected nonnegative stat22 and a known weapon kind')
    rate = stat22 * ATB_FACTOR[kind] // 10
    # The slow branch takes precedence over haste, with integer truncation.
    if slow:
        return rate - rate * 2 // 5
    if haste:
        return rate + (rate >> 1)
    return rate


def refill_updates(gauge, gain, target=FULL):
    if not 0 <= gauge <= FULL or not 0 <= target <= FULL or gain < 0:
        raise ValueError('invalid gauge, target or gain')
    if gauge >= target:
        return 0
    if gain == 0:
        raise ValueError('zero fill rate cannot reach the target')
    return (target - gauge + gain - 1) // gain


def step_gauge(gauge, gain, *, menu_mode=1, game_flags=0):
    """Normalized ready gauge; retail clamps at its next ready-state check."""
    if not 0 <= gauge <= FULL or gain < 0:
        raise ValueError('invalid gauge or gain')
    return min(FULL, gauge + gain) if menu_mode & 0xFF and not game_flags & 0x100 else gauge


@dataclass(frozen=True)
class SwitchResult:
    entry_updates: int
    entry_gauge: int
    after_gauge: int
    attack_updates: int

    @property
    def total_updates(self):
        return self.entry_updates + self.attack_updates


def switch_to_attack(gauge, source_gain, destination_gain, *, half_bar=True,
                     completed=True):
    """Wait for legal menu entry, resolve one switch, then wait for an attack.

    Excludes time spent selecting/executing the change. No gauge gain is assumed
    during that interval. CURRENT half-bar handling restores saved entry gauge
    minus 4500; a full-bar change leaves 4500. Cancellation refunds a borrowed
    bar; retail/full-bar cancellation is outside this switch-only abstraction.
    Destination rate is supplied after Battle_SetupEnemyAnims changes action kind.
    """
    if not completed and not half_bar:
        raise ValueError('retail cancellation requires full turn-state modeling')
    threshold = HALF if half_bar else FULL
    before = refill_updates(gauge, source_gain, threshold)
    entry = min(FULL, gauge + before * source_gain)
    if not completed:
        if entry >= FULL:
            raise ValueError('only borrowed-menu cancellation is modeled')
        after = entry
        destination_gain = source_gain
    else:
        after = entry - HALF if half_bar else 0
    return SwitchResult(before, entry, after, refill_updates(after, destination_gain))
