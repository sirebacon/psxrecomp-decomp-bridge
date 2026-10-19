"""Enemy body-contact damage (opt-in source_options['contact_damage']).

Source (decomp):
  - menu/main_update.c Menu_MainUpdate, per battle update while Aya's state has no 0x800000 (the
    post-revive / battle-start hold, timer 0x5A) and no 0x180000 (Liberate / Energy Shot): for an
    enemy entity with flag 0x02000000 (set by entity/allocation.c when its hit cylinder overlaps
    Aya's), if Aya's state has no 0x01000000 and the enemy is alive: Aya loses the enemy's
    contactDamage (EnemyCombatant 0x92, flat: no defense, no gauge halving) unless Barrier (0x200)
    is up; then 0x01000000 is set with g_AyaStatusEffectTimer = 0x5A (90 updates; cleared by
    Entity_UpdateTimers) and Aya is knocked back by contactKnockback (0x93).
    Resolved strikes set the same 0x01000000 window (they are not blocked by it).
  - The value is the script's Entity_SetField 65 (0x41 -> effect_param92 = contactDamage, battle/
    context.c Entity_WriteFieldByCmd); 66 is the knockback (60 in every script).

Not source (labelled): when the cylinders overlap. The simulator has no enemy body motion, so the
contact rate is a calibrated chance per enemy per update while it is in melee range
(contact_rate), fitted to the play-log hurts that equal a present enemy's contactDamage.
"""
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / 'findings/data'
WINDOW_UPDATES = 0x5A


@lru_cache(maxsize=4)
def contact_table(cells=()):
    """{(map, identity): contactDamage}. Scripts that write several literals (phase blocks, e.g.
    room 86 0x20D: 5/7/8/10) keep the most common one, ties to the smallest (labelled pick)."""
    from .enemy_identity import identity_keys
    inv = json.loads((ROOT / 'pe-enemy-scripts-2026-10-18.json').read_text(encoding='utf-8'))
    keys = identity_keys(dict(cells))
    values = {}
    for room in inv['rooms']:
        for s in room.get('scripts', []):
            vals = [n['args'][1]['value'] for n in s['facts'] if n['handler'] == 'Entity_SetField' and len(n['args']) == 2
                    and n['args'][0] == dict(mode=0, value=65) and n['args'][1].get('mode') == 0]
            if not vals: continue
            pick = sorted(Counter(vals).items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            for ident, _ in keys.get((room['map'], s['actor_type']), []):
                values.setdefault((room['map'], ident), set()).add(pick)
    return {k: tuple(sorted(v)) for k, v in values.items()}


def contact_of(foe, cells=()):
    try: key = (int(foe['loc']), int(foe['name'], 16))
    except (KeyError, TypeError, ValueError): return 0
    vals = contact_table(cells).get(key, ())
    if not vals: return 0
    if len(vals) > 1 and 'hp' in foe:
        # Several actor types share the identity (room 332: 170-HP actor 6 = 7, 45-HP actor 7 = 8):
        # labelled pick, the larger foe takes the smaller value.
        return vals[0] if foe['hp'] >= 100 else vals[-1]
    return vals[0]
