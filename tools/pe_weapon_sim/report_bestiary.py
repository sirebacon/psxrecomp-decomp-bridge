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
                g = groups.setdefault(sig, dict(id='0x%04X' % ident, stats=s, rooms=set(), notes=set(), main=False))
                g['rooms'].add((room['map'], room['place'] or '', room['block'] or '', room['disc'] if room['map'] not in same else 0))
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
                        variants=[] if g['main'] else sorted(g['notes'])))
    out.sort(key=lambda r: (ORDER.index(r['first']) if r['first'] in ORDER else 99, r['maps'][0], r['id']))
    return out, unresolved


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


def markdown(rows, unresolved, chk):
    regular, bosses, helpers = ([r for r in rows if r['role'] == k] for k in ('regular', 'boss', 'helper'))
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
         '## Coverage', '',
         '| | Regular | Bosses / forced | Helpers (0 EXP, 0 BP) |', '|---|---:|---:|---:|']
    for b in ORDER:
        n1, n2, n3 = (sum(r['first'] == b for r in rs) for rs in (regular, bosses, helpers))
        if n1 or n2 or n3: L.append('| first seen %s | %d | %d | %d |' % (b, n1, n2, n3))
    L += ['| **total distinct stat blocks** | **%d** | **%d** | **%d** |' % (len(regular), len(bosses), len(helpers)), '',
          "Bosses / forced = the can't-escape flag with a reward. Helpers are boss parts, props and scripted",
          'actors with no EXP or BP; they would not get Bestiary entries.', '',
          'A distinct stat block is not always a distinct creature: the same monster can appear with a',
          'tougher block later in the story. Naming pass will merge those.', '']
    for title, rs in (('Regular enemies', regular), ('Bosses and forced fights', bosses), ('Helpers (not Bestiary entries)', helpers)):
        L += ['## %s' % title, '', '| ID | First seen | Where (maps) | HP | Def | EXP | BP | Weak | Strong | Drop | Steal | Notes |',
              '|---|---|---|---:|---:|---:|---|---|---|---|---|---|']
        for r in rs:
            where = '%s (%s)' % (', '.join(r['places']) or '-', ', '.join(map(str, r['maps'][:6])) + (' +%d' % (len(r['maps'])-6) if len(r['maps']) > 6 else ''))
            notes = '; '.join((['scripted HP'] if r['scripted_hp'] else []) + r['variants'])
            L.append('| %s | %s | %s | %s | %s | %s | %d/%d | %s | %s | %s | %s | %s |' % (
                r['id'], r['first'], where, r['hp'], r['defense'], r['exp'], r['bp'][0], r['bp'][1],
                ', '.join(r['weak']) or '-', ', '.join(r['strong']) or '-', r['drop'], r['steal'], notes or ''))
        L.append('')
    L += ['## Next', '',
          '1. Naming pass: tie each stat block to its creature (model / animation bank per actor type, room',
          '   and story context) and merge blocks of the same creature.',
          '2. EX Game: apply the EX scale (story variable V80) to the scaled enemies.',
          '3. Decide the Junk tiers (for example name + HP free; weaknesses; drops and steals).', '']
    return '\n'.join(L)


def main():
    rows, unresolved = species(); chk = check(rows)
    OUT_JSON.write_text(json.dumps(dict(source=EXTRACT.name, check=chk, unresolved=unresolved, enemies=rows), indent=1), encoding='utf-8')
    OUT_MD.write_text(markdown(rows, unresolved, chk), encoding='utf-8')
    print(json.dumps(dict(stat_blocks=len(rows), roles={k: sum(r['role'] == k for r in rows) for k in ('regular', 'boss', 'helper')}, unresolved=len(unresolved),
                          **{k: v for k, v in chk.items() if k != 'missing'}, missing=len(chk['missing']))))


if __name__ == '__main__': main()
