"""Enemy charge steps recorded in the play log, as a labelled fallback for identities whose
scripts give no single literal field 0x3E (enemy_catalog.catalog has no charge_step).

python -m pe_weapon_sim.logged_charge     (rebuilds findings/data/pe-logged-enemy-charge-2026-10-19.json)

Source: pe_loot_logger.c `enemy` rows (one per enemy when its battle slot is freed) carry the
runtime charge step. Where the catalog has a value, all 105 logged identities agree with it
exactly, so the logged value is the same quantity read at runtime. Keyed (map, id, hp) because
one id can cover variants (room 332 0x0015: hp 45 -> 40, hp 170 -> 65); (map, id) keeps the most
common value. Only used through source_options['logged_charge'] (historical default unchanged).
"""
import collections, csv, json, re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'findings/data/pe-logged-enemy-charge-2026-10-19.json'


def build():
    from .calibrate_logged import RAW_LOG
    kv = lambda s: dict(re.findall(r'(\w+)=([^ ]*)', s))
    by_hp, by_id = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
    for r in csv.DictReader(open(RAW_LOG, encoding='utf-8', errors='replace')):
        if r['kind'] != 'enemy': continue
        d = kv(r['detail'])
        if not d.get('charge'): continue
        c = int(d['charge'])
        by_hp['%s|%s|%s' % (r['map'], d['id'], d['hp'])][c] += 1
        by_id['%s|%s' % (r['map'], d['id'])][c] += 1
    pick = lambda cs: cs.most_common(1)[0][0]
    return dict(source='pe_play_log.csv enemy rows (pe_loot_logger.c), runtime charge step',
                by_hp={k: pick(v) for k, v in sorted(by_hp.items())}, by_id={k: pick(v) for k, v in sorted(by_id.items())},
                counts={k: dict(v) for k, v in sorted(by_id.items())})


@lru_cache(maxsize=1)
def table():
    return json.loads(OUT.read_text(encoding='utf-8'))


def lookup(foe):
    """Logged charge step for a foe dict (loc, name, hp), or None."""
    t = table(); m, i = str(foe.get('loc')), str(foe.get('name'))
    v = t['by_hp'].get('%s|%s|%s' % (m, i, foe.get('hp')))
    return v if v is not None else t['by_id'].get('%s|%s' % (m, i))


if __name__ == '__main__':
    data = build()
    OUT.write_text(json.dumps(data, indent=1), encoding='utf-8')
    print(len(data['by_id']), 'identities,', len(data['by_hp']), 'hp variants ->', OUT)
