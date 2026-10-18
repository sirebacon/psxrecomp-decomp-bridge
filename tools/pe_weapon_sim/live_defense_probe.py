"""Read-only probe of Aya's battle defense inputs (never writes RAM, never sends input).

Checks the source derivation (aya/stats.c Inv_RecalcSlotStats / Inv_BuildArmorList,
entity/combat.c Entity_ResolveDropTable) against the live game:
  stat20      = AyaLevelStats[defense stat level + g_StatScaleBase[2]].defense
  first       = armor baseStats[0] + bonusStats[0] (cap 999)   -> slots 0..2
  second      = armor baseStats[1] + bonusStats[1] (cap 999)   -> slots 3+
  third       = f(armor baseStats[2] + bonusStats[2])          -> critical resist
python -m pe_weapon_sim.live_defense_probe --port 4378 [--out findings/data/...json]
"""
import argparse, json, math, struct, time

from .live_probe import call

LEVEL_TABLE_PTR, LEVEL_TABLE_ORIGIN = 0x800A803C, 0x800A8028
STAT_SCALE_BASE = 0x800A1B30
AYA_LEVELS = 0x800C0E28
ARMOR_SLOT, BAG, RECORDS = 0x800C0E22, 0x800C0E48, 0x800C0EAC


def read(addr, n, port):
    r = call(dict(cmd='read_ram', addr=hex(addr), len=n), port)
    if not r.get('ok'): raise RuntimeError(r)
    return bytes.fromhex(r['hex'])


def crit_resist(evade):
    """Inv_BuildArmorList third field (u8 store)."""
    v = min(999, evade)
    if v < 85: return (math.isqrt(v * 3000) // 10) & 255
    return ((v * 249 // 208 + 402) // 10) & 255


def level_rows(port, n=99):
    base = struct.unpack('<I', read(LEVEL_TABLE_PTR, 4, port))[0] + LEVEL_TABLE_ORIGIN
    raw = read(base, n * 0x18, port)
    rows = []
    for i in range(n):
        hp, off, dfn, s22, cap, maxatk, rate, step, st3c, st3e = struct.unpack_from('<HHHBBiiiHH', raw, i * 0x18)
        rows.append(dict(level=i, hp=hp, offense=off, defense=dfn, stat22=s22, capacity=cap, max_atk=maxatk,
                         atb_rate=rate, atb_step=step, status3c=st3c, status3e=st3e))
    return hex(base), rows


def main():
    ap = argparse.ArgumentParser(__doc__); ap.add_argument('--port', type=int, default=4378); ap.add_argument('--out')
    a = ap.parse_args(); port = a.port
    in_battle = bool(struct.unpack('<I', read(0x8009D1A0, 4, port))[0] & 2)
    entity = struct.unpack('<I', read(0x8009D254, 4, port))[0]
    core = struct.unpack('<I', read(entity, 4, port))[0] if 0x80000000 <= entity < 0x80200000 else 0
    out = dict(host_time=time.strftime('%Y-%m-%d %H:%M:%S'), in_battle=in_battle, entity=hex(entity), core=hex(core))
    levels = list(struct.unpack('<7h', read(AYA_LEVELS, 14, port)))
    scale = list(struct.unpack('<7i', read(STAT_SCALE_BASE, 28, port)))
    out.update(stat_levels_raw=levels, stat_scale_base=scale)
    slot = struct.unpack('<b', read(ARMOR_SLOT, 1, port))[0]
    value = struct.unpack('<H', read(BAG + slot * 2, 2, port))[0]
    rec = RECORDS + (value - 256) * 32
    r = read(rec, 32, port)
    base = list(r[7:10]); bonus = list(struct.unpack_from('<3h', r, 0x0E))
    out['armor'] = dict(slot=slot, value=value, record=hex(rec), item=r[4], kind=r[6], base=base, bonus=bonus,
                        raw=r.hex(), mods=[m & 31 for m in r[0x15:0x15 + r[0x14]]])
    table_base, rows = level_rows(port)
    out['level_table'] = dict(base=table_base, rows=rows)
    pred = dict(first=min(999, base[0] + bonus[0]), second=min(999, base[1] + bonus[1]),
                third=crit_resist(base[2] + bonus[2]))
    out['predicted_attributes'] = pred
    if core:
        c = read(core, 0x70, port)
        stat20 = struct.unpack_from('<h', c, 0x20)[0]
        attrs = struct.unpack_from('<I', c, 0x6C)[0]
        word, eff = struct.unpack('<II', read(attrs, 8, port))
        live = dict(first=word & 1023, second=(word >> 10) & 1023, third=(word >> 20) & 255)
        out['live'] = dict(cur_hp=struct.unpack_from('<H', c, 0x0C)[0], max_hp=struct.unpack_from('<H', c, 0x1C)[0],
                           stat1e=struct.unpack_from('<h', c, 0x1E)[0], stat20=stat20,
                           stat22=struct.unpack_from('<H', c, 0x22)[0], attributes=hex(attrs),
                           parameter_word=hex(word), effect_flags=hex(eff), **live)
        out['match'] = {k: live[k] == pred[k] for k in pred}
        out['stat20_rows'] = [r_['level'] for r_ in rows if r_['defense'] == stat20]
    txt = json.dumps(out, indent=1)
    if a.out:
        with open(a.out, 'w') as fh: fh.write(txt)
    print(json.dumps({k: v for k, v in out.items() if k != 'level_table'}, indent=1))


if __name__ == '__main__':
    main()
