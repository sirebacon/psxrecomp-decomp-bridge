import struct, collections, json
from pe_weapon_sim.extract_enemy_scripts import word, sectors, PROJECT, BRIDGE
from pe_weapon_sim.extract_animations import ram_from_pst
ram = ram_from_pst(BRIDGE/'findings/live-timing-session/saves/scph1001/state_80072534_disc2_slot09.pst')
base_lba = word(ram, 0xb0dd8)
u16 = lambda b, o: struct.unpack_from('<H', b, o)[0]

def model(blob, off):
    parts, anims, verts = blob[off + 2], blob[off + 3], u16(blob, off + 6)
    npk = sum(u16(blob, off + 8 + 2 * k) for k in range(4))
    mcb = u16(blob, off + 0x18)
    at = off + 0x1C
    part_tab = [struct.unpack_from('<HHBxxxi', blob, at + 12 * i) for i in range(parts)]
    at += parts * 12 + verts * 8 + verts * 4 + npk * 12 + (2 + parts * 2 + 1) * 8
    cmds = list(struct.unpack_from('<%db' % mcb, blob, at))
    ok = all(c in (-1, -2) or 0 <= c < parts for c in cmds) and sorted(c for c in cmds if c >= 0) == list(range(parts))
    return dict(parts=parts, anims=anims, verts=verts, cmds=cmds, ok=ok, bones=[p[3] for p in part_tab])

def bank_models(blob):
    d = word(blob, 4); desc = word(blob, d + 0x0C); at = desc & 0x3fffff
    out = []
    for i in range(desc >> 22):
        w = word(blob, at + 12 * i + 4)
        try: out.append((w >> 24, model(blob, w & 0xffffff)))
        except struct.error: pass
    return out

f = open(PROJECT/'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc 1).bin', 'rb')
aya = {}
for area in range(10, 15):
    idx = area + 8; s0 = u16(ram, 0x930D8 + 2 * idx); s1 = u16(ram, 0x930D8 + 2 * idx + 2)
    aya[area] = bank_models(sectors(f, base_lba + s0, s1 - s0))[0][1]
    print('Aya area', area, 'parts', aya[area]['parts'], 'ok', aya[area]['ok'], 'cmds', aya[area]['cmds'])
streams = collections.defaultdict(list); bad = 0
for disc in (1, 2):
    f = open(PROJECT/f'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc {disc}).bin', 'rb')
    for m in range(1, 441):
        start = word(ram, 0x93378 + (m - 1) * 8); packed = word(ram, 0x9337c + (m - 1) * 8)
        if packed >> 20 == 0: continue
        try: blob = sectors(f, base_lba + start + (packed & 255) + ((packed >> 8) & 4095), packed >> 20)
        except Exception: continue
        for slot, md in bank_models(blob):
            if not md['ok']: bad += 1; continue
            if md['parts'] < 15: continue
            streams[tuple(md['cmds'])].append(dict(disc=disc, map=m, slot=slot, parts=md['parts'], anims=md['anims'], verts=md['verts'], bones=md['bones']))
print('malformed', bad, 'distinct skeletons (>=15 parts)', len(streams))
for area, a in aya.items():
    hits = streams.get(tuple(a['cmds']), [])
    print('Aya %d skeleton shared by %d room models in maps %s' % (area, len(hits), sorted({h['map'] for h in hits})[:40]))
top = sorted(streams.items(), key=lambda kv: -len(kv[1]))[:12]
for cmds, hs in top:
    print(len(hs), 'models, parts', hs[0]['parts'], 'maps', sorted({h['map'] for h in hs})[:15], 'same as Aya', [a for a, v in aya.items() if tuple(v['cmds']) == cmds])
json.dump(dict(aya={a: v for a, v in aya.items()}, streams=[dict(cmds=list(k), models=v) for k, v in streams.items()]),
          open(__file__.replace('.py', '.json'), 'w'))
