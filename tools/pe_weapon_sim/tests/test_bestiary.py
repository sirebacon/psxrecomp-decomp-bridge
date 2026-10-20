import unittest
from fractions import Fraction

from pe_weapon_sim.extract_bestiary import evaluate_setup, stat_value, summarize


def L(v): return dict(mode=0, value=v & 0xFFFFFFFF)
def LOC(v): return dict(mode=1, value=v)
def OP(v): return dict(mode=3, value=v)
def CELL(v): return dict(mode=4, value=v)
def VAR(v): return dict(mode=2, value=v)


def program(base, rows):
    """rows: [(label, handler, args)]; a str arg names a label and becomes its jump word."""
    at, labels, nodes = base, {}, []
    for label, h, a in rows:
        if label: labels[label] = at
        nodes.append([at, h, a]); at += 8 + 4 * len(a)
    out = []
    for at, h, a in nodes:
        out.append(dict(offset=at, handler=h, args=[L((labels[x] - base) // 2) if isinstance(x, str) else x for x in a]))
    return dict(nodes=out, edges=[], errors=[])


class EvaluateSetup(unittest.TestCase):
    def test_scaled_hp_and_random_drop_odds(self):
        base = 1000
        cfg = program(base, [
            (None, 'Script_AssignValue', [CELL(10), VAR(80)]),            # N10 = V80
            (None, 'Script_EvalExpr', [L(11), OP(0), CELL(10), L(0)]),    # V80 == 0 -> N10 = 65536
            (None, 'Script_JumpIfZero', [OP(0), 'scaled']),
            (None, 'Script_AssignValue', [CELL(10), L(65536)]),
            ('scaled', 'Script_Random', [LOC(42), L(0), L(10)]),
            (None, 'Script_EvalExpr', [L(9), OP(0), LOC(42), L(6)]),      # roll > 6 -> item 5
            (None, 'Script_JumpIfZero', [OP(0), 'common']),
            (None, 'Script_AssignValue', [LOC(42), L(5)]),
            (None, 'Script_JumpToEntityOffset', ['stats']),
            ('common', 'Script_AssignValue', [LOC(42), L(7)]),
            ('stats', 'Entity_SetField', [L(0x29), L(8)]),
            (None, 'Entity_SetField', [L(0x2A), L(0)]),
            (None, 'Script_EvalExpr', [L(15), OP(0), CELL(10), L(44)]),
            (None, 'Script_EvalExpr', [L(18), OP(1), OP(0), L(16)]),
            (None, 'Entity_SetField', [L(0x2C), OP(1)]),
            (None, 'Entity_SetField', [L(0x28), L(100000)]),
            (None, 'Entity_SetField', [L(0x5C), LOC(42)]),
        ])
        variables = [0] * 128; variables[80] = 65536
        paths = evaluate_setup(cfg, base, variables)
        self.assertAlmostEqual(float(sum(p for _, p, _ in paths)), 2.0)       # one full tree per V80 fork
        for v in summarize(paths):
            s = v['stats']
            self.assertEqual((s['rank'], s['kind'], s['hp'], s['exp']), (8, 0, 44, 34464))  # EXP is u16
            self.assertEqual(s['drop'], {'7': 0.7, '5': 0.3})

    def test_stat_widths(self):
        self.assertEqual(stat_value('poison', 0xFFFE), -2)
        self.assertEqual(stat_value('heat', 6), 2)
        self.assertEqual(stat_value('drop', 0x1FF), 0xFF)


if __name__ == '__main__':
    unittest.main()
