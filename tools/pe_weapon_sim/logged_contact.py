"""Per-room enemy contact rates measured from the play log (labelled data, like logged_charge).

A logged hurt counts as body contact when it equals the contactDamage of an enemy present in that
battle (contact_damage.contact_of), is >= 3 s after the previous contact-valued hurt (Aya's
0x01000000 window is 90 updates; poison ticks repeat about every second), and is not a damage
any present enemy's resolved strike could deal at that battle's level and armor (each called
slot's power - stat20/5 - armor, plain / halved by the gauge / critical / both), so a strike that
happens to equal the contact value is not counted twice.
Rate = contacts per battle-minute (battles with a contact-capable enemy), per map; the simulator
applies it per battle update while any contact-capable enemy is alive. Rebuild with
  python -m pe_weapon_sim.logged_contact
"""
import collections, json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / 'findings/data'
DATA = ROOT / 'pe-logged-contact-rate-2026-10-19.json'


def strike_damages(foe, aya, cells):
    """Every damage a resolved strike of this foe can deal (Entity_ResolveDropTable variants)."""
    from .enemy_choice import called_plans
    out = set()
    scale = int(aya.get('defense', 0)) // 5
    for slot, plan in (called_plans(foe, cells) or {}).items():
        power = plan.get('power', {}).get('power')
        if power is None: continue
        armor = aya.get('armor_first', 0) if slot < 3 else aya.get('armor_second', 0)
        for p in (power - scale * 3 // 10, power - scale):            # with / without the Haste / 0x1000 cut
            d = p - armor
            if d <= 0: continue
            for v in (d, d * 3 // 2):
                out |= {v, v // 2}
    return out


def build():
    from .calibrate_logged import battles, setup
    from .contact_damage import contact_of
    from .enemy_identity import FIRST_RUN_SHARED_CELLS as C, MULTI_KIND, cells_key
    cells = {**C, MULTI_KIND: 1}; ck = cells_key(cells)
    per = collections.defaultdict(lambda: dict(contacts=0, secs=0.0, battles=0, excluded=0))
    total = collections.defaultdict(lambda: dict(contacts=0, secs=0.0))
    for b in battles():
        if not b.get('hurts'): continue
        vals = {contact_of(f, ck) for f in b['foes']} - {0}
        if not vals: continue
        _, aya, _ = setup(b)
        strikes = set()
        for f in b['foes']: strikes |= strike_damages(f, aya, cells)
        last = -99; contacts = excluded = 0
        for t, dmg in b['hurts']:
            if dmg not in vals: continue
            if dmg in strikes: excluded += 1; continue
            if t - last >= 3: contacts += 1
            last = t
        g = per[int(b['map'])]; g['contacts'] += contacts; g['secs'] += b['logged_secs']; g['battles'] += 1; g['excluded'] += excluded
        k = 'boss' if b['boss'] else 'ord'
        total[k]['contacts'] += contacts; total[k]['secs'] += b['logged_secs']
    rate = lambda g: round(g['contacts'] / g['secs'] * 60, 3) if g['secs'] else 0.0
    out = dict(rule=__doc__.split('\n\n')[1].strip(), default={k: rate(g) for k, g in total.items()},
               maps={str(m): dict(rate=rate(g), contacts=g['contacts'], battles=g['battles'], strike_matches_excluded=g['excluded'])
                     for m, g in sorted(per.items())})
    DATA.write_text(json.dumps(out, indent=1), encoding='utf-8')
    return out


@lru_cache(maxsize=1)
def rates():
    return json.loads(DATA.read_text(encoding='utf-8'))


def rate_for(map_id, boss):
    r = rates()
    m = r['maps'].get(str(map_id))
    return m['rate'] if m else r['default']['boss' if boss else 'ord']


if __name__ == '__main__':
    o = build(); print(o['default'], len(o['maps']), 'maps')
