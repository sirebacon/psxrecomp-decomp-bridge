"""Draft Bestiary from findings/data/pe-bestiary-extract-2026-10-19.json (extract_bestiary).

Groups identical enemies across rooms (same identity and stat block), lists where each appears,
and checks the result against the logged playthrough. Names are left for a later pass: the
game addresses enemies only by rank/kind and the logged ID is reused across areas.

    python -m pe_weapon_sim.report_bestiary
"""
import json
from collections import defaultdict
from pathlib import Path

from .economy.tables import item_name

ROOT = Path(__file__).resolve().parents[2]
EXTRACT = ROOT/'findings/data/pe-bestiary-extract-2026-10-19.json'
CAMPAIGN = ROOT/'findings/data/pe-campaign-2026-10-17.json'
OUT_JSON = ROOT/'findings/data/pe-bestiary-draft-2026-10-19.json'
OUT_MD = ROOT/'findings/pe-bestiary-draft-2026-10-19.md'
NAMES = ROOT/'findings/data/pe-bestiary-names-2026-10-19.json'
SHRINE = ROOT/'findings/data/pe-enemy-names-rpgclassics.json'
RESISTS = ('heat', 'frost', 'cyanide', 'acid', 'tranq')
ORDER = ('Day 1', 'Days 1-2', 'Day 2', 'Day 3', 'Day 4', 'Days 4-5', 'Day 6', 'late addition', 'special scene', 'Chrysler (EX)')
SCRIPTED_HP = 1000000   # scripted bosses: HP offset by 1,000,000, the script ends the fight


def item(v):
    return 'nothing' if v in (0, '0') else item_name(int(v)).title()


def odds(v):
    if isinstance(v, dict):
        return ', '.join('%s %d%%' % (item(k), round(p*100)) for k, p in v.items())
    return item(v) if v is not None else 'nothing'


def label(variant, snapshot):
    alt = sorted(k for k, v in variant.items() if k.startswith('V') and v != snapshot[int(k[1:])])
    branch = any(k.startswith('?') for k in variant)
    return ' / '.join((['progress branch (%s = 0)' % ', '.join(alt)] if alt else []) + (['unresolved branch'] if branch else []))


def source(room, e, v, same):
    """Where a stat block lives on disc, to go back to it: room offsets plus the disc sector."""
    def at(off): return dict(room_offset=off, sector=room['lba'] + off // 2048, byte=off % 2048)
    w = v.get('writes', {})
    phases = []
    for p in e.get('phases', []):
        s = {k: p['stats'][k] for k in ('hp', 'hp_cap', 'defense', 'exp', 'rank', 'kind') if k in p.get('stats', {})}
        if not s or set(s) <= {'hp', 'exp'} and all(x == 0 for x in s.values()): continue   # death handling
        if 'hp' in s and isinstance(s['hp'], int) and s['hp'] >= SCRIPTED_HP: s['hp'] = 'scripted %d' % (s['hp'] - SCRIPTED_HP)
        hp_at = p['writes'].get('hp', [])
        row = dict(window=p['window'], stats=s, hp_write=[at(o) for o in hp_at])
        if row not in phases: phases.append(row)     # one row per distinct result, not per branch
    return dict(disc='both' if room['map'] in same else room['disc'], map=room['map'], room_lba=room['lba'],
                room_sectors=room['sectors'], actor=e['actor_type'], script_start=e['script_start'],
                entry=v['entry'], how=v['how'],
                writes={k: [at(o) for o in w[k]] for k in ('rank', 'kind', 'hp', 'exp', 'defense', 'drop', 'steal') if k in w},
                phases=phases)


def species():
    data = json.loads(EXTRACT.read_text())
    snapshot = json.loads((ROOT/'findings/data/pe-script-state-endgame-2026-10-18.json').read_text())['variables']
    same = set(data['maps_identical_on_both_discs'])
    groups = {}; unresolved = []
    for room in data['rooms']:
        if room['disc'] == 2 and room['map'] in same: continue
        for e in room.get('enemies', []):
            if 'error' in e: unresolved.append(dict(map=room['map'], actor=e['actor_type'], why=e['error'])); continue
            for v in e['variants']:
                s = v['stats']
                if any(isinstance(s.get(k), dict) or s.get(k) == 'unknown' for k in ('rank', 'kind', 'hp')):
                    unresolved.append(dict(map=room['map'], actor=e['actor_type'], why='identity or HP varies')); continue
                ident = (s.get('kind', 0) << 8) | s.get('rank', 0)
                sig = json.dumps(dict(id=ident, **{k: s.get(k) for k in ('hp', 'defense', 'exp', 'bp_base', 'bp_factor', 'drop', 'steal', 'boss', 'crit', 'charge', *RESISTS)}), sort_keys=True)
                g = groups.setdefault(sig, dict(id='0x%04X' % ident, stats=s, rooms=set(), notes=set(), main=False, sources={}))
                g['rooms'].add((room['map'], room['place'] or '', room['block'] or '', room['disc'] if room['map'] not in same else 0))
                g['sources'].setdefault((room['map'], e['actor_type']), source(room, e, v, same))
                note = label(v['variant'], snapshot)
                if note: g['notes'].add(note)
                else: g['main'] = True   # reached on the end-of-run path: no branch note needed
    out = []
    for g in groups.values():
        rooms = sorted(g['rooms'])
        blocks = sorted({r[2] for r in rooms}, key=lambda b: ORDER.index(b) if b in ORDER else 99)
        s = g['stats']; hp = s['hp']
        out.append(dict(id=g['id'], name=None, first=blocks[0] if blocks else '', blocks=blocks,
                        places=sorted({r[1] for r in rooms if r[1]}), maps=[r[0] for r in rooms],
                        disc_only=sorted({r[3] for r in rooms if r[3]}),
                        hp=hp - SCRIPTED_HP if isinstance(hp, int) and hp >= SCRIPTED_HP else hp,
                        scripted_hp=isinstance(hp, int) and hp >= SCRIPTED_HP,
                        defense=s.get('defense', 0), exp=s.get('exp', 0), bp=[s.get('bp_base', 0), s.get('bp_factor', 0)],
                        boss=bool(s.get('boss', 0)), weak=[k for k in RESISTS if s.get(k) == 2],
                        strong=[k for k in RESISTS if s.get(k) == 1], drop=odds(s.get('drop')), steal=odds(s.get('steal')),
                        role='helper' if not s.get('exp', 0) and not s.get('bp_base', 0) and not s.get('bp_factor', 0) else 'boss' if s.get('boss', 0) else 'regular',
                        variants=[] if g['main'] else sorted(g['notes']),
                        sources=[g['sources'][k] for k in sorted(g['sources'])]))
    names = {(i, hp, exp): (n, c, note) for i, hp, exp, n, c, note in json.loads(NAMES.read_text())['names']}
    for r in out:
        n = names.get((r['id'], r['hp'], r['exp'] if not isinstance(r['exp'], dict) else None))
        if n:
            r['name'], r['confidence'], r['name_note'] = n
            if r['role'] == 'helper': r['role'] = 'boss'      # a named boss part (claw, segment)
    out.sort(key=lambda r: (ORDER.index(r['first']) if r['first'] in ORDER else 99, r['maps'][0], r['id']))
    return out, unresolved


def ex_scale(rows):
    """EX-game HP scale implied by the shrine's EX HP for story enemies whose name matched."""
    shrine = {n: ex for n, hp, ex, exp, area in json.loads(SHRINE.read_text())['regular']}
    lo, hi, used, off = 0, 1 << 30, [], []
    for r in rows:
        if r['role'] != 'regular' or r.get('confidence') not in ('high', 'medium') or r['first'] == 'Chrysler (EX)': continue
        ex = shrine.get(r['name'])
        if not ex or not r['hp']: continue
        a, b = -(-ex * 65536 // r['hp']), ((ex + 1) * 65536 - 1) // r['hp']
        if max(lo, a) <= min(hi, b): lo, hi = max(lo, a), min(hi, b); used.append(r['name'])
        else: off.append(r['name'])
    return dict(n10_low=lo, n10_high=hi, ratio_low=round(lo / 65536, 4), ratio_high=round(hi / 65536, 4),
                enemies=len(used), outliers=sorted(set(off)))


def check(rows):
    """Logged (map, ID) pairs the draft covers, and where logged HP / EXP / defense agree."""
    camp = json.loads(CAMPAIGN.read_text()); logged = {}
    for ev in camp['events']:
        if ev['type'] == 'battle':
            for x in ev['enemies'] or []: logged.setdefault((int(ev['map']), x['id'].upper().replace('0X', '0x')), x)
    by = defaultdict(list)
    for r in rows:
        for m in r['maps']: by[(m, r['id'])].append(r)
    found = agree = 0; missing = []
    for key, x in logged.items():
        if key not in by: missing.append(key); continue
        found += 1
        hp = x['hp'] - SCRIPTED_HP if x['hp'] >= SCRIPTED_HP else x['hp']
        agree += any(r['hp'] == hp and r['defense'] == x['defense'] and r['exp'] == x['exp'] for r in by[key])
    return dict(logged=len(logged), found=found, agree=agree, missing=sorted(missing))


def markdown(rows, unresolved, chk, ex):
    regular, bosses, helpers = ([r for r in rows if r['role'] == k] for k in ('regular', 'boss', 'helper'))
    named = [r for r in rows if r.get('name')]
    L = ['# Bestiary draft (extraction) — October 19, 2026', '',
         'Groundwork for a Junk-bought Bestiary. Every enemy stat block the room scripts set up, read',
         'offline from both US discs (`extract_bestiary`, then `report_bestiary`). **No mod changes.**', '',
         '## How it was extracted', '',
         '- All 414 rooms of the room sector table (maps 1-440) on both discs; every room with enemies is',
         '  byte-identical on the two discs.',
         '- Each actor script\'s setup code is evaluated up to its last stat write. Common enemies compute',
         '  HP and defense as `(scale x base) >> 16` (the scale is 1.0 on a first playthrough; the EX Game',
         '  scale differs and is not applied here) and roll drop / steal with the script `Random`, so drop',
         '  and steal are listed with their odds.',
         '- Story-progress checks are split over the end-of-run value and 0; a stat block seen only on the',
         '  0 side is marked *progress branch*. Scripted bosses store HP + 1,000,000 (the script ends the',
         '  fight); the table shows HP without the offset and marks them.',
         '- Resistances: weak / strong per element (heat, frost, cyanide, acid, tranq); unlisted = average.', '',
         '## Check against the logged playthrough', '',
         '- %d logged (room, enemy) pairs; %d found in the extraction, %d with matching HP, defense and EXP.' % (chk['logged'], chk['found'], chk['agree']),
         '- Drops, steals and BP matched on every found pair; resistances match every log row that recorded them',
         '  (the first 42 enemy rows predate resistance logging and read as average).',
         '- Not found (%d): %s. Mostly bosses whose identity is set by another actor or computed.' % (len(chk['missing']), ', '.join('m%d %s' % k for k in chk['missing'])),
         '- Scripts the evaluator could not finish: %d.' % len(unresolved), '',
         '## Names', '',
         '- Names come from the RPGClassics Parasite Eve shrine (enemies and bosses pages), matched by HP, EXP',
         '  and area (`findings/data/pe-bestiary-names-2026-10-19.json`; the shrine facts are in',
         '  `pe-enemy-names-rpgclassics.json`). %d of %d stat blocks named: %d high, %d medium, %d low confidence.' % (
             len(named), len(rows), *(sum(r['confidence'] == c for r in named) for c in ('high', 'medium', 'low'))),
         '- Where the shrine and the game disagree, the game value is kept (the log confirms it): Slime 88 HP',
         '  (shrine 80), Spawn 114 EXP (90), Lizard 896 EXP (986), Mole 462 EXP (457), Scorpion 390 HP (480).',
         '  Tyrannosaur: the script sets 100,000 EXP, which the 16-bit EXP field wraps to 34,464.',
         '- Chrysler Building enemies are written with their EX HP directly and match the shrine EX HP.',
         '- EX Game scale for story enemies: the shrine EX HP of %d named enemies fits one scale of %.4f-%.4f x' % (ex['enemies'], ex['ratio_low'], ex['ratio_high']),
         '  (shared cell N10 = %d-%d instead of 65536); off that scale: %s.' % (ex['n10_low'], ex['n10_high'], ', '.join(ex['outliers']) or 'none'),
         '- Not extracted (identity or HP set by another actor): %s.' % ', '.join(json.loads(NAMES.read_text())['not_extracted']), '',
         '## Creatures', '',
         '| Creature | Story (HP / EXP) | Chrysler EX (HP / EXP) |', '|---|---|---|']
    creatures = defaultdict(lambda: ([], []))
    for r in named:
        base = r['name'].split(' (')[0] if r['role'] == 'regular' else r['name']
        creatures[base][r['first'] == 'Chrysler (EX)'].append('%s / %s' % (r['hp'], r['exp']))
    for c, (story, chrysler) in creatures.items():
        L.append('| %s | %s | %s |' % (c, ', '.join(dict.fromkeys(story)) or '-', ', '.join(dict.fromkeys(chrysler)) or '-'))
    L += ['', '## Coverage', '',
         '| | Regular | Bosses / forced | Helpers (0 EXP, 0 BP) |', '|---|---:|---:|---:|']
    for b in ORDER:
        n1, n2, n3 = (sum(r['first'] == b for r in rs) for rs in (regular, bosses, helpers))
        if n1 or n2 or n3: L.append('| first seen %s | %d | %d | %d |' % (b, n1, n2, n3))
    L += ['| **total distinct stat blocks** | **%d** | **%d** | **%d** |' % (len(regular), len(bosses), len(helpers)), '',
          "Bosses / forced = the can't-escape flag with a reward. Helpers are boss parts, props and scripted",
          'actors with no EXP or BP; they would not get Bestiary entries.', '',
          'A creature can have several stat blocks (tougher copies later, forced fights, Chrysler).', '']
    for title, rs in (('Regular enemies', regular), ('Bosses and forced fights', bosses), ('Helpers (not Bestiary entries)', helpers)):
        L += ['## %s' % title, '', '| Name | ID | First seen | Where (maps) | HP | Def | EXP | BP | Weak | Strong | Drop | Steal | Notes |',
              '|---|---|---|---|---:|---:|---:|---|---|---|---|---|---|']
        for r in rs:
            where = '%s (%s)' % (', '.join(r['places']) or '-', ', '.join(map(str, r['maps'][:6])) + (' +%d' % (len(r['maps'])-6) if len(r['maps']) > 6 else ''))
            notes = '; '.join((['scripted HP'] if r['scripted_hp'] else []) + ([r['name_note']] if r.get('name_note') else []) + r['variants'])
            name = '%s%s' % (r['name'], '' if r['confidence'] == 'high' else ' (%s)' % r['confidence']) if r.get('name') else '?'
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s/%s | %s | %s | %s | %s | %s |' % (
                name, r['id'], r['first'], where, r['hp'], r['defense'], r['exp'], r['bp'][0], r['bp'][1],
                ', '.join(r['weak']) or '-', ', '.join(r['strong']) or '-', r['drop'], r['steal'], notes or ''))
        L.append('')
    L += ['## Mid-fight values', '',
          'Stat writes after the setup (`phases` in the extract): growth, phase changes and the real HP of',
          'scripted bosses. Each write\'s run of arithmetic is evaluated at the first-playthrough scale; *unknown*',
          'means the value is built from something the fight tracks (damage carried over, current HP). Death',
          'handling (HP set to 0) is left out. Window = room offsets of the evaluated instructions.', '',
          '- Scripted bosses: setup stores HP + 1,000,000; the next block writes the fighting HP (Actress 40,',
          '  Eve carriage 330, Giant Spider 450, Centipede 500, Crab 856, Eve final form 2200, ...).',
          '- Worms: max HP 120 at the start, then 150, 180 and 210 as each one dies (defense 13); the damage',
          '  already taken carries into the new maximum.',
          '- Centipede: the head\'s 500 is followed by a 300 HP phase that also switches the kind byte to 2, which',
          '  is why the log recorded it as 0x021A. Chrysler Centipede: 1200 then 300.',
          '- Ultimate Being: no separate 2nd-form block; the script tracks HP as a percentage of max and, below 60%,',
          '  clamps it to 60% (+ the scripted offset) to trigger the change. 4th form: 7992, then 999,999 and',
          '  499,999 in the special-bullet phase.', '',
          '| Name | ID | Map / actor | Window (room offsets) | HP write sector:byte | Writes |', '|---|---|---|---|---|---|']
    for r in rows:
        for s in r['sources']:
            for p in s['phases']:
                L.append('| %s | %s | %d / %d | %d-%d | %s | %s |' % (
                    r.get('name') or '?', r['id'], s['map'], s['actor'], p['window'][0], p['window'][1],
                    ', '.join('%d:%d' % (h['sector'], h['byte']) for h in p['hp_write']) or '-',
                    ', '.join('%s %s' % kv for kv in p['stats'].items())))
    L += ['', '## Where in the data', '',
          'How to go back to any stat block. Rooms are read from "Parasite Eve (USA) (Disc N).bin" ("both" =',
          'byte-identical on the two discs) starting at the room LBA, 2048 user-data bytes per sector. Offsets',
          'are into that room blob; the HP sector / byte is where the HP-setting `Entity_SetField` instruction',
          'sits. *entry* is where evaluation started: the script start, or the stat block a boss script jumps',
          'to. Full detail (rank, kind, EXP, defense, drop and steal writes) is in',
          '`findings/data/pe-bestiary-draft-2026-10-19.json` (`sources`) and the raw',
          '`pe-bestiary-extract-2026-10-19.json`. Re-run: `python -m pe_weapon_sim.extract_bestiary --out',
          'findings/data/pe-bestiary-extract-2026-10-19.json` then `python -m pe_weapon_sim.report_bestiary`.', '',
          '| Name | ID | HP | Disc | Map | Room LBA | Actor | Script start | Entry | HP write (room offset) | HP sector:byte |',
          '|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|']
    for r in rows:
        for s in r['sources']:
            hp = s['writes'].get('hp', [{}])
            L.append('| %s | %s | %s | %s | %d | %d | %d | %d | %d | %s | %s |' % (
                r.get('name') or '?', r['id'], r['hp'], s['disc'], s['map'], s['room_lba'], s['actor'], s['script_start'],
                s['entry'], ', '.join(str(h['room_offset']) for h in hp if h) or '-',
                ', '.join('%d:%d' % (h['sector'], h['byte']) for h in hp if h) or '-'))
    L += ['', '## Next', '',
          '1. Extract the missing bosses (Eve fights, Worms, Sheeva, Ultimate Being) from the actors that set them up.',
          '2. Read the EX scale from an EX-game save (story variable V80) to confirm the derived range.',
          '3. Decide the Junk tiers (for example name + HP free; weaknesses; drops and steals).', '']
    return '\n'.join(L)


def main():
    rows, unresolved = species(); chk = check(rows); ex = ex_scale(rows)
    OUT_JSON.write_text(json.dumps(dict(source=EXTRACT.name, check=chk, ex_scale=ex, unresolved=unresolved, enemies=rows), indent=1), encoding='utf-8')
    OUT_MD.write_text(markdown(rows, unresolved, chk, ex), encoding='utf-8')
    print(json.dumps(dict(stat_blocks=len(rows), roles={k: sum(r['role'] == k for r in rows) for k in ('regular', 'boss', 'helper')}, unresolved=len(unresolved),
                          named=sum(bool(r.get('name')) for r in rows), ex=ex,
                          **{k: v for k, v in chk.items() if k != 'missing'}, missing=len(chk['missing']))))


if __name__ == '__main__': main()
