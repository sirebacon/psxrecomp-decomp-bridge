"""Distance-gated attack choice from enemy scripts (offline, conservative).

Many ordinary enemies pick their attack by distance to Aya: e.g. map 358 actor 4 (the run's
farming room, ID 0x0A) re-reads the distance after its held counter clears and runs slot 0
when d < 630, slot 3 when d > 1000, nothing in between (root+0x2318..0x23b8); its earlier
decision approaches when 630 < d < 1500.

For every Script_RunEntityCommand on a literal slot this walks backwards through unique CFG
predecessors (decoded edges; callback edges ignored) and collects each branch that must be taken
to reach the call: Script_JumpIfZero on an operand written by Script_EvalExpr comparing a local
with a literal (ops 9 >, 10 <, 12 >=, 13 <=), or AND / OR of two such comparisons when the
taken edge allows (AND true, OR false), where that local was last written by
Entity_GetDistanceComponents #0 #0 (distance to Aya, 16.16, absolute X+Y+Z sum per the map-156
decode). The walk stops at a merge (several predecessors), so guards before a merge are not
collected (conservative: the interval may be wider than the real one, never narrower).
Result: per call an interval in game units, or no guard. Not probabilities; random and state
branches are not resolved here.
"""
import json, math
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from .enemy_identity import cells_key, identity_keys

ROOT = Path(__file__).resolve().parents[2] / 'findings/data'
CMP = {9: '>', 10: '<', 12: '>=', 13: '<='}
FLIP = {'>': '<', '<': '>', '>=': '<=', '<=': '>='}
NEG = {'>': '<=', '<': '>=', '>=': '<', '<=': '>'}


def _lit(a): return (a['value'] - (1 << 32) if a['value'] >= 1 << 31 else a['value']) if a['mode'] == 0 else None


class Interval:
    """lo < d < hi with strictness flags; open ends are None."""
    def __init__(self):
        self.lo = self.hi = None; self.lo_strict = self.hi_strict = False

    def add(self, op, value):
        v = value / 65536.0
        if op in ('>', '>='):
            strict = op == '>'
            if self.lo is None or v > self.lo or (v == self.lo and strict): self.lo, self.lo_strict = v, strict
        else:
            strict = op == '<'
            if self.hi is None or v < self.hi or (v == self.hi and strict): self.hi, self.hi_strict = v, strict

    def contains(self, d):
        if self.lo is not None and (d < self.lo or (self.lo_strict and d == self.lo)): return False
        if self.hi is not None and (d > self.hi or (self.hi_strict and d == self.hi)): return False
        return True

    def as_dict(self):
        return dict(lo=self.lo, lo_strict=self.lo_strict, hi=self.hi, hi_strict=self.hi_strict)

    @staticmethod
    def from_dict(d):
        i = Interval(); i.lo, i.lo_strict, i.hi, i.hi_strict = d['lo'], d['lo_strict'], d['hi'], d['hi_strict']; return i


def _comparison(row, by, order, cmp_node, depth=0):
    """[(op, literal)] meaning `distance op literal` when cmp_node's result is true, or None."""
    a = cmp_node['args']; op = _lit(a[0])
    if op in CMP:
        lhs, rhs = a[2], a[3]
        if lhs['mode'] != 0 and rhs['mode'] == 0: local, sym, val = lhs, CMP[op], _lit(rhs)
        elif rhs['mode'] != 0 and lhs['mode'] == 0: local, sym, val = rhs, FLIP[CMP[op]], _lit(lhs)
        else: return None
        if not _is_distance(by, order, cmp_node, local): return None
        return [(sym, val)]
    return None


def _is_distance(by, order, node, local):
    """The local was last written (linearly before `node`, within 40 instructions) by the
    player distance read, with no other write in between."""
    i = order.index(node['offset'])
    for off in reversed(order[max(0, i - 200):i]):
        n = by[off]; a = n['args']
        if n['handler'] == 'Entity_GetDistanceComponents' and len(a) == 3 and a[2] == local:
            return _lit(a[0]) == 0 and _lit(a[1]) == 0
        if a and a[0] == local and n['handler'] in ('Script_AssignValue', 'Script_Random'): return False
        if n['handler'] == 'Script_EvalExpr' and len(a) > 1 and a[1] == local: return False
        if n['handler'].startswith(('Entity_Get', 'Script_Get')) and local in a[1:]: return False   # a getter's output
    return False


def _writer(by, order, node, operand):
    i = order.index(node['offset'])
    for off in reversed(order[max(0, i - 12):i]):
        n = by[off]; a = n['args']
        if n['handler'] == 'Script_EvalExpr' and len(a) == 4 and a[1] == operand: return n
        if a and a[0] == operand and n['handler'] in ('Script_AssignValue', 'Script_Random'): return None
    return None


class _Graph:
    def __init__(self, row):
        self.row = row
        self.by = {n['offset']: n for n in row['nodes']}
        self.order = sorted(self.by)
        self.preds = defaultdict(list); self.spawns = defaultdict(list)
        for e in row['edges']:
            (self.spawns if e['kind'] == 'child_or_callback' else self.preds)[e['target']].append(e)


def _branch(g, p, e, iv):
    """Add the distance condition of taking edge e out of JumpIfZero p; True if one was added."""
    taken_true = e['kind'] == 'nonzero'
    w = _writer(g.by, g.order, p, p['args'][0])
    if w is None: return False
    conds = _comparison(g.row, g.by, g.order, w)
    op = _lit(w['args'][0])
    if conds:
        for sym, val in conds: iv.add(sym if taken_true else NEG[sym], val)
        return True
    if op in (5, 6):                                       # OR / AND of two comparisons
        parts = [_writer(g.by, g.order, w, x) for x in (w['args'][2], w['args'][3])]
        cs = [_comparison(g.row, g.by, g.order, q) if q else None for q in parts]
        if all(cs) and ((op == 6 and taken_true) or (op == 5 and not taken_true)):
            for c in cs:
                for sym, val in c: iv.add(sym if taken_true else NEG[sym], val)
            return True
    return False


def _diamond_head(g, sources, depth=10):
    """The first node every source reaches backwards along single-predecessor chains (each
    source counts as reaching itself), or None. Only forward diamonds (head before the sources)."""
    chains = []
    for s in sources:
        chain, at = [s], s
        for _ in range(depth):
            ps = g.preds.get(at, [])
            if len(ps) != 1: break
            at = ps[0]['source']; chain.append(at)
        chains.append(chain)
    common = set(chains[0]).intersection(*chains[1:])
    if not common: return None
    head = max(common)                                     # closest common point before the merge
    return head if head < min(sources) or head in sources else None


def _walk(g, start):
    """Backward walk from `start`: (interval, guards, state requirements [(local, k)])."""
    iv, guards, states, at, seen = Interval(), 0, [], start, set()
    for _ in range(160):
        ps = g.preds.get(at, [])
        if not ps and len(g.spawns.get(at, [])) == 1 and at not in seen:
            # A child routine's entry: the choice was made where its one spawn site runs.
            seen.add(at); at = g.spawns[at][0]['source']; continue
        if len(ps) > 1 and at not in seen:
            # A local diamond (if/else rejoining here): continue from the branches' common
            # ancestor without collecting conditions from inside it.
            d = _diamond_head(g, [e['source'] for e in ps])
            if d is not None:
                seen.add(at); at = d; continue
        if len(ps) != 1 or at in seen: break
        seen.add(at)
        e = ps[0]; p = g.by.get(e['source'])
        if p is None: break
        if p['handler'] == 'Script_JumpIfZero' and e['kind'] in ('zero', 'nonzero'):
            guards += _branch(g, p, e, iv)
        elif p['handler'] == 'Script_CondBranch' and e['kind'] == 'equal':
            lhs, rhs = p['args'][0], p['args'][1]
            if lhs['mode'] == 1 and rhs['mode'] == 0: states.append((lhs['value'], _lit(rhs)))
        at = p['offset']
    return iv, guards, states


def _assignment_interval(g, local, k):
    """Distance interval under which local ends up == k: each `AssignValue L #k` site's own
    backward guards, plus the negated condition of an immediately following conditional
    overwrite (`AssignValue L #k; cmp; JumpIfZero -> skip; AssignValue L #other`). None unless
    every site gives the same guarded interval."""
    sites = [n for n in g.row['nodes'] if n['handler'] == 'Script_AssignValue'
             and n['args'][0] == dict(mode=1, value=local) and _lit(n['args'][1]) == k]
    results = set()
    for site in sites:
        iv, guards, _ = _walk(g, site['offset'])
        i = g.order.index(site['offset'])
        nxt = [g.by[o] for o in g.order[i + 1:i + 4]]
        if len(nxt) == 3 and nxt[1]['handler'] == 'Script_JumpIfZero' and nxt[2]['handler'] == 'Script_AssignValue' \
                and nxt[2]['args'][0] == dict(mode=1, value=local) and _lit(nxt[2]['args'][1]) != k:
            skip = [e for e in g.row['edges'] if e['source'] == nxt[1]['offset'] and e['kind'] == 'zero']
            if skip:                                        # staying k means the overwrite was skipped
                guards += _branch(g, nxt[1], skip[0], iv)
        if not guards: return None
        results.add(json.dumps(iv.as_dict(), sort_keys=True))
    return json.loads(results.pop()) if len(results) == 1 else None


def call_guards(row):
    g = _Graph(row)
    out = []
    for n in row['nodes']:
        if n['handler'] != 'Script_RunEntityCommand' or _lit(n['args'][0]) is None: continue
        iv, guards, states = _walk(g, n['offset'])
        via = []
        for local, k in states:
            sub = _assignment_interval(g, local, k)
            if sub is None: continue
            s = Interval.from_dict(sub)
            if s.lo is not None: iv.add('>' if s.lo_strict else '>=', int(s.lo * 65536))
            if s.hi is not None: iv.add('<' if s.hi_strict else '<=', int(s.hi * 65536))
            guards += 1; via.append('L%d==%d' % (local, k))
        out.append(dict(slot=_lit(n['args'][0]), offset=n['offset'] - row['root'], guards=guards,
                        interval=iv.as_dict() if guards else None, via_state=via))
    return out

@lru_cache(maxsize=1)
def guards():
    dec = json.loads((ROOT / 'pe-enemy-actions-2026-10-18.json').read_text(encoding='utf-8'))
    return {(r['map'], r['actor_type']): call_guards(r) for r in dec['scripts'] if r['calls']}


@lru_cache(maxsize=4)
def catalog(cells=()):
    """{(map, identity): [dict(slot, interval)]} where every attack call of the identity has a
    distance guard and the slots' intervals are consistent per slot (one interval per slot)."""
    keys = identity_keys(dict(cells))
    cand = defaultdict(list)
    for (m, actor), calls in guards().items():
        if not calls or any(c['interval'] is None for c in calls): continue
        per = defaultdict(list)
        for c in calls: per[c['slot']].append(json.dumps(c['interval'], sort_keys=True))
        if any(len(set(v)) != 1 for v in per.values()): continue
        rows = [dict(slot=s, interval=json.loads(v[0])) for s, v in sorted(per.items())]
        for ident, _ in keys.get((m, actor), []):
            cand[m, ident].append(json.dumps(rows, sort_keys=True))
    return {k: json.loads(v[0]) for k, v in cand.items() if len(set(v)) == 1}


OPEN = dict(lo=None, lo_strict=False, hi=None, hi_strict=False)


def called_slots(foe, cells=None):
    """{slot: [actor types calling it]} over every actor resolving to the identity (script
    Script_RunEntityCommand calls with a literal slot)."""
    from .power_gaps import _scripts
    try: m, ident = int(foe['loc']), int(foe['name'], 16)
    except (KeyError, ValueError, TypeError): return {}
    keys = identity_keys(dict(cells_key(cells)))
    out = defaultdict(list)
    for (mm, a), ids in keys.items():
        if mm != m or not any(i == ident for i, _ in ids) or (m, a) not in _scripts(): continue
        for s in sorted({c['slot'] for c in _scripts()[m, a]['calls'] if isinstance(c['slot'], int)}):
            out[s].append(a)
    return dict(out)


@lru_cache(maxsize=None)
def _flow_can_attack(m, actor):
    """True / False: the actor's whole decoded flow (decode_enemy_actions.flow over the disc-1
    room blob, conditional child edges included) can start an action or an effect:
    Script_RunEntityCommand (the only caller of Entity_TriggerAnimEvent 0x8002FAF8 in main, and
    no jal to it in the Disc2 boss room blobs), Script_GetEntityEffect or a PM send. None when
    the flow has decode errors."""
    from .decode_enemy_actions import flow, sectors, BRIDGE, PROJECT
    inv = json.loads((BRIDGE / 'findings/data/pe-enemy-scripts-2026-10-18.json').read_text())
    room = next(r for r in inv['rooms'] if r['disc'] == 1 and r['map'] == m)
    script = next(s for s in room['scripts'] if s['actor_type'] == actor)
    with (PROJECT / 'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc 1).bin').open('rb') as disc:
        cfg = flow(sectors(disc, room['lba'], room['sectors']), script['start'], script['end'], inv['handlers'])
    if cfg['errors']: return None
    return any(n['handler'] in ('Script_RunEntityCommand', 'Script_GetEntityEffect') or n['handler'].startswith('Pm_ScriptSendCommand')
               for n in cfg['nodes'])


def silent_identity(foe, cells=None):
    """True when every actor resolving to the identity has an error-free decoded flow with no
    Script_RunEntityCommand, effect or PM send: it never starts an attack (e.g. room 269 actors
    6/7, boss 0x041B, a kind-4 form with no command calls; room 273 actors 5-7, 0x0125). False when any actor can, or nothing resolves."""
    try: m, ident = int(foe['loc']), int(foe['name'], 16)
    except (KeyError, ValueError, TypeError): return False
    keys = identity_keys(dict(cells_key(cells)))
    actors = [a for (mm, a), ids in keys.items() if mm == m and any(i == ident for i, _ in ids) and a != 0]
    return bool(actors) and all(_flow_can_attack(m, a) is False for a in actors)


def phase_powers(foe, cells):
    """{slot: [power profile, ...]} for slots an actor declares several times with resolvable power
    (e.g. room 86 0x20D: four phase blocks, slot 0 = N10 x 52 / 60 / 62 / 66 >> 16). The block taken
    depends on state the extractor does not evaluate; callers pick one (labelled)."""
    from .power_gaps import _scripts, DECLARATIONS, power_expression
    from .enemy_power import evaluate_power
    try: m, ident = int(foe['loc']), int(foe['name'], 16)
    except (KeyError, ValueError, TypeError): return {}
    keys = identity_keys(dict(cells_key(cells)))
    out = defaultdict(list)
    for (mm, a), ids in keys.items():
        if mm != m or not any(i == ident for i, _ in ids) or (m, a) not in _scripts(): continue
        row = _scripts()[m, a]
        crit = {n['args'][1]['value'] for n in row['nodes'] if n['handler'] == 'Entity_SetField'
                and n['args'][0] == dict(mode=0, value=63) and n['args'][1]['mode'] == 0}
        chance = next(iter(crit)) if len(crit) == 1 else 0
        decls = defaultdict(list)
        for n in row['nodes']:
            if n['handler'] in DECLARATIONS and n['args'][0]['mode'] == 0 and n['args'][1]['mode'] == 0:
                decls[n['args'][0]['value']].append(n)
        for s, ns in decls.items():
            if len(ns) < 2: continue
            exprs = [power_expression(row, n) for n in ns]
            if any(e is None for e in exprs): continue
            try: powers = [evaluate_power(e, cells) for e in exprs]
            except (ValueError, KeyError): continue
            for n, pw in zip(ns, powers):
                out[s].append(dict(power=pw, action_slot=s, effect_type=n['args'][1]['value'], critical_chance=chance,
                                   power_source='phase pick of %d declarations' % len(ns)))
    return dict(out)


def variant_powers(foe, cells):
    """{actor: {slot: power profile}} from each actor's own declarations, for identities whose
    actors disagree (two species sharing a rank/kind, e.g. 0x1A, 0x1D). Literal / scaled power
    and a literal critical chance (template 0 when never written)."""
    from .enemy_power import evaluate_power, records
    keys = identity_keys(dict(cells_key(cells)))
    try: m, ident = int(foe['loc']), int(foe['name'], 16)
    except (KeyError, ValueError, TypeError): return {}
    actors = {a for (mm, a), ids in keys.items() if mm == m and any(i == ident for i, _ in ids)}
    extracted, _ = records(cells_key(cells), True)
    out = defaultdict(dict)
    for e in extracted:
        if e['map'] != m or e['actor_type'] not in actors or not e['expression'] or e['critical_chance'] is None: continue
        try: power = evaluate_power(e['expression'], cells or {})
        except ValueError: continue
        out[e['actor_type']][e['slot']] = dict(power=power, action_slot=e['slot'], effect_type=e['effect_type'] or 0,
                                                critical_chance=e['critical_chance'], power_source='variant actor %d' % e['actor_type'])
    return dict(out)


def called_plans(foe, cells, contact='early', untimed=(10, 10), throw_lateral=0, variant_rng=None):
    """slot_plans over the identity's called slots with no distance guard (choice unresolved
    when several), keeping only slots with source power."""
    rows = [dict(slot=s, interval=OPEN) for s in sorted(called_slots(foe, cells))]
    plans = slot_plans(foe, cells, contact, rows=rows, default_critical=True, untimed=untimed, throw_lateral=throw_lateral)
    if variant_rng is not None and any(not p['power'] for p in plans.values()):
        # Labelled: the species is not identified by the log; pick one actor's declarations.
        variants = variant_powers(foe, cells)
        called = called_slots(foe, cells)
        if variants:
            actor = variant_rng.choice(sorted(variants))
            for s, p in plans.items():
                if not p['power'] and s in variants[actor] and actor in called.get(s, []):
                    p['power'] = dict(variants[actor][s]); p['variant'] = actor
            # The picked actor's own melee contact window (melee_window rows are per actor; the
            # identity-level join drops slots whose species disagree, e.g. 0x1A slot 1).
            from .melee_window import actions as melee_actions
            m = int(foe['loc'])
            win = {r['slot']: r for mm, a, r in melee_actions() if mm == m and a == actor}
            for s, p in plans.items():
                if p['kind'] == 'untimed' and s in win and actor in called.get(s, []):
                    w = win[s]
                    p.update(kind='window', windup=w[contact]['windup'], recovery=w[contact]['recovery'],
                             reset=w['reset_on_completion'], category=w['category'], variant=actor)            # ... and its own task-program effect (room_modules.task_plan restricted to that actor).
            from .room_modules import task_plan
            for s, p in plans.items():
                if p['kind'] == 'untimed' and s >= 3 and actor in called.get(s, []):
                    tp = task_plan(foe, s, cells, actor=actor)
                    if tp: p.update(kind='task', module=tp, reset=tp['action']['reset'], variant=actor)
    if variant_rng is not None and any(not p['power'] for p in plans.values()):
        phases = phase_powers(foe, cells)
        for s, p in plans.items():
            if not p['power'] and phases.get(s):
                p['power'] = dict(variant_rng.choice(phases[s])); p['phase_pick'] = True
    return {s: p for s, p in plans.items() if p['power']}


def _slot_loads_effect(foe, slot, cells):
    """True if any actor calling `slot` loads an effect (Script_GetEntityEffect) within the 40
    instructions before a call of that slot."""
    from .decode_enemy_actions import literal
    from .power_gaps import _scripts
    m = int(foe['loc'])
    for a in called_slots(foe, cells).get(slot, []):
        nodes = sorted(_scripts()[m, a]['nodes'], key=lambda n: n['offset'])
        for k, n in enumerate(nodes):
            if n['handler'] == 'Script_RunEntityCommand' and literal(n['args'][0]) == slot:
                if any(q['handler'] == 'Script_GetEntityEffect' for q in nodes[max(0, k - 40):k]): return True
    return False


def slot_plans(foe, cells, contact='early', rows=None, default_critical=False, untimed=(10, 10), throw_lateral=0):
    """Per-slot timing / power for an identity: {'slot': dict(kind, windup/recovery or effect,
    power profile)}. kind: 'window' (melee_window contact window, slots 0-2, bound = `contact`),
    'anim' (decode_enemy_actions), 'contact' (contact_timing bound), 'effect' (effect_actions),
    or 'untimed'."""
    from .contact_timing import catalog as contact_catalog
    from .effect_actions import effect_profile
    from .enemy_catalog import action_catalog
    from .enemy_power import power_profile
    from .melee_window import melee_rows
    from .room_modules import module_plan, task_plan
    from .homing_throw import homing_plan
    key =(int(foe['loc']), int(foe['name'], 16)); ck = cells_key(cells)
    anim = {a['slot']: a for a in action_catalog(ck).get(key, [])}
    cont = {r['slot']: r for r in (contact_catalog(ck).get(key) or [])}
    eff = effect_profile(foe, cells)
    melee = melee_rows(foe, cells)
    out = {}
    for row in (choice_profile(foe, cells) if rows is None else rows):
        s = row['slot']
        try: power = power_profile(foe, s, cells or {}, scaled_identities=bool(cells), default_critical=default_critical, room_cells=default_critical)
        except ValueError: power = {}
        if s in melee:
            # Source contact window (melee_window.py); supersedes the anim / contact readings.
            m = melee[s]
            plan = dict(kind='window', windup=m[contact]['windup'], recovery=m[contact]['recovery'],
                        reset=m['reset_on_completion'], category=m['category'])
        elif s in anim:
            plan = dict(kind='anim', windup=anim[s]['windup'], recovery=anim[s]['recovery'],
                        reset=anim[s]['reset_on_completion'])
        elif s in cont:
            r = cont[s][contact]
            plan = dict(kind='contact', windup=r['windup'], recovery=r['recovery'], reset=cont[s]['reset_on_completion'])
        elif eff and eff['slot'] == s:
            plan = dict(kind='effect', action=eff, reset=eff['reset'])
        elif s >= 3 and module_plan(foe, s, cells):
            # Room-module effect (room_modules.py): exact field-engine timeline.
            mp = module_plan(foe, s, cells, geometry_upper=throw_lateral == 'aimed')
            plan = dict(kind='module', module=mp, reset=mp['action']['reset'])
        elif s >= 3 and homing_plan(foe, s, cells, throw_lateral):
            # Thrown homing projectile + ground eruption (homing_throw.py).
            hp_ = homing_plan(foe, s, cells, throw_lateral)
            plan = dict(kind='homing', module=hp_, reset=hp_['action']['reset'])
        elif s >= 3 and task_plan(foe, s, cells):
            # Room task program with a ported controller (room_modules.TASK_CONTROLLERS).
            tp = task_plan(foe, s, cells)
            plan = dict(kind='task', module=tp, reset=tp['action']['reset'])
        elif s >= 3 and not _slot_loads_effect(foe, s, cells):
            # Slot 3+ with no effect object: melee contact needs slot < 3 (Entity_CheckActionIdMatch)
            # and effect contact needs an effect (FieldFx_RegisterOwnerContact), so no damage path.
            # Completion is unresolved (death / stun bits 0x6000 or a PE reset): labelled timing.
            plan = dict(kind='noeffect', windup=untimed[0], recovery=untimed[1], reset=False)
            power = dict(power, no_contact=True) if power else dict(power=0, action_slot=s, no_contact=True)
        else:
            plan = dict(kind='untimed', windup=untimed[0], recovery=untimed[1], reset=False)   # labelled fallback
        out[s] = dict(plan, power=power, interval=row['interval'])
    return out


class GatedEnemy:
    """Distance-gated attack choice. At full charge the current distance picks the slot whose
    guard contains it; that slot's timing and power are used. No slot: keep the charge and
    re-decide after a wait (30-59 updates, map 358 actor 4 root+0x21ac). Several slots
    (overlapping guards): `ambiguous` = 'first' (lowest slot) or 'uniform'."""

    def __init__(self, clock, plans, *, distance, aya_radius, rng, scenario=None, ambiguous='first', wait=(30, 60)):
        self.clock, self.plans, self.distance = clock, plans, distance
        self.aya_radius, self.rng, self.scenario = aya_radius, rng, scenario
        self.ambiguous, self.wait = ambiguous, wait
        self.phase, self.age, self.hold = 'charge', 0, 0
        self.current = None; self.plan = None
        self.last_strike_geometric = False
        self.stats = dict(chosen={}, none=0, ambiguous=0, untimed=0)

    def _choose(self):
        slots = [s for s, p in sorted(self.plans.items()) if Interval.from_dict(p['interval']).contains(self.distance)]
        if not slots: return None
        if len(slots) > 1:
            self.stats['ambiguous'] += 1
            return self.rng.choice(slots) if self.ambiguous == 'uniform' else slots[0]
        return slots[0]

    def tick(self, *, paused=False):
        poison = self.clock.tick(paused=paused); self.last_strike_geometric = False
        if paused or self.clock.incapacitated: return False, poison
        if self.phase == 'charge':
            if self.hold: self.hold -= 1; return False, poison
            if self.clock.charge < 9000: return False, poison
            slot = self._choose()
            if slot is None:
                self.stats['none'] += 1; self.hold = self.rng.randrange(*self.wait)
                return False, poison
            p = self.plans[slot]
            self.stats['chosen'][slot] = self.stats['chosen'].get(slot, 0) + 1
            self.stats['untimed'] += p['kind'] == 'untimed'
            self.current = dict(p['power'])
            if not p['reset']: self.clock.charge = 0
            if p['kind'] in ('module', 'homing', 'task'):
                t = p['module']['run'](self.distance, self.aya_radius, self.rng)
                self.plan = dict(strikes={c + 1 for c in t['contacts']}, total=t['release'], geometric=True, reset=p['reset'], kind=p['kind'])
            elif p['kind'] == 'effect':
                from .effect_actions import timeline
                t = timeline(p['action'], self.distance, self.aya_radius, self.scenario, self.rng)
                self.plan = dict(strikes=set(t['contacts']), total=t['release'], geometric=True, reset=p['reset'], kind=p['kind'])
            else:
                self.plan = dict(strikes={p['windup']}, total=p['windup'] + p['recovery'], geometric=False, reset=p['reset'], kind=p['kind'])
            self.phase, self.age = 'action', 0
            return False, poison
        self.age += 1
        strike = self.age in self.plan['strikes']
        if strike and self.plan['geometric']: self.last_strike_geometric = True
        if self.age >= self.plan['total']:
            if self.plan['reset']: self.clock.charge = 0
            self.phase = 'charge'
        return strike, poison


def choose(rows, distance):
    """Slots whose distance interval contains `distance` (game units)."""
    return [r['slot'] for r in rows if Interval.from_dict(r['interval']).contains(distance)]


def choice_profile(foe, cells=None):
    try: return list(catalog(cells_key(cells)).get((int(foe['loc']), int(foe['name'], 16))) or [])
    except (KeyError, ValueError, TypeError): return []
