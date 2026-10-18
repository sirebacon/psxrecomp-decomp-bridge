"""Campaign coverage of enemy catalogs with and without first-run shared cells (offline).

For every won-battle enemy appearance in the campaign script: static charge/rank match,
action-timing match, and any supported power slot / slot 0 power. Writes
findings/data/pe-enemy-coverage-2026-10-18.json. Coverage of static records, not AI choice.
python -m pe_weapon_sim.audit_enemy_coverage
"""
import collections, json
from pathlib import Path

from .contact_timing import catalog as contact_catalog
from .effect_actions import catalog as effect_catalog
from .enemy_catalog import action_catalog, catalog
from .enemy_identity import FIRST_RUN_PROVENANCE, FIRST_RUN_SHARED_CELLS, cells_key
from .enemy_power import power_profile

ROOT = Path(__file__).resolve().parents[2] / 'findings/data'


def coverage(cells):
    camp = json.loads((ROOT / 'pe-campaign-2026-10-17.json').read_text())
    ck = cells_key(cells)
    stat, timing, contact, effect = catalog(ck), action_catalog(ck), contact_catalog(ck), effect_catalog(ck)
    out = collections.Counter(); per = collections.Counter(); missing = collections.Counter()
    for e in camp['events']:
        if e['type'] != 'battle' or e['outcome'] != 'win': continue
        for x in e['enemies']:
            grp = 'boss' if x['boss'] else 'normal'
            key = (int(e['map']), int(x['id'], 16)); foe = dict(loc=e['map'], name=x['id'])
            out[grp, 'appearances'] += 1
            s = key in stat; t = key in timing
            slots = [k for k in range(6) if _power(foe, k, cells)]
            c = key in contact; fx = key in effect
            out[grp, 'static'] += s; out[grp, 'timing'] += t; out[grp, 'timing_or_contact_bound'] += bool(t or c)
            out[grp, 'power_any'] += bool(slots); out[grp, 'power_slot0'] += 0 in slots
            out[grp, 'all_three'] += bool(s and t and slots)
            out[grp, 'all_three_with_contact'] += bool(s and (t or c) and slots)
            out[grp, 'timing_any'] += bool(t or c or fx)
            out[grp, 'all_three_any_timing'] += bool(s and (t or c or fx) and slots)
            if grp == 'normal' and not ((t or c or fx) and slots): missing[key] += 1
    return {'%s.%s' % k: v for k, v in sorted(out.items())}, [[m, hex(i), n] for (m, i), n in missing.most_common(15)]


def _power(foe, slot, cells):
    """Literal identities use the same scale for comparability; unknown cells count as unresolved."""
    try:
        return power_profile(foe, slot, cells or FIRST_RUN_SHARED_CELLS, scaled_identities=bool(cells))
    except ValueError:
        return {}


def main():
    base, base_missing = coverage(None)
    first, first_missing = coverage(FIRST_RUN_SHARED_CELLS)
    out = dict(scope='static record coverage of logged appearances; not action selection', cells=FIRST_RUN_SHARED_CELLS,
               cells_provenance=FIRST_RUN_PROVENANCE, literal_identities=base, first_run_cells=first,
               top_uncovered_normal_literal=base_missing, top_uncovered_normal_first_run=first_missing)
    path = ROOT / 'pe-enemy-coverage-2026-10-18.json'
    path.write_text(json.dumps(out, indent=1))
    print(json.dumps(dict(literal=base, first_run=first, still_uncovered=first_missing), indent=1))


if __name__ == '__main__':
    main()
