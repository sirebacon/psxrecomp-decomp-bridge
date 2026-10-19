"""Called-slot attack selection (enemy_choice.called_plans) and the template critical default.

Regression tests of the opt-in path, plus independent checks against original data: the
template critical chance is read from the retail executable, and the audit replay must
reproduce the published run's fallback count exactly (see audit_fallback_hits)."""
import json, random, struct, unittest
from pathlib import Path

from pe_weapon_sim import engine, rules
from pe_weapon_sim.decomp_animation import source_behavior_rules
from pe_weapon_sim.enemy_choice import called_plans, called_slots
from pe_weapon_sim.enemy_identity import FIRST_RUN_SHARED_CELLS as C
from pe_weapon_sim.enemy_power import power_profile
from pe_weapon_sim.extract_enemy_scripts import PROJECT
from pe_weapon_sim.tests.test_source_combat import config, foe

ROOT = Path(__file__).resolve().parents[3] / 'findings/data'


class SelectionTests(unittest.TestCase):
    def test_top_fallback_enemy_calls_only_slot3(self):
        f = dict(loc='146', name='0x0013')
        self.assertEqual(called_slots(f, C), {3: [6]})
        self.assertEqual(power_profile(f, 0, C, scaled_identities=True), {})       # the old slot-0 default
        self.assertEqual(called_plans(f, C)[3]['power']['power'], 98)

    def test_plans_keep_only_powered_called_slots(self):
        f = dict(loc='168', name='0x0018')
        self.assertEqual(sorted(called_plans(f, C)), [1, 2])
        self.assertEqual({s: p['kind'] for s, p in called_plans(f, C).items()}, {1: 'window', 2: 'window'})

    def test_disagreeing_variants_stay_unresolved(self):
        self.assertEqual(called_plans(dict(loc='333', name='0x001A'), C), {})


class RoomCellAndVariantTests(unittest.TestCase):
    def test_room_scale_cell_idiom(self):
        from pe_weapon_sim.enemy_power import room_v80_cells
        self.assertIn(11, room_v80_cells(210))                          # N11 = V80 in room 210
        self.assertEqual(called_plans(dict(loc='210', name='0x001D'), C)[1]['power']['power'], 152)

    def test_variant_pick_is_labelled_and_uniform(self):
        import collections
        picks = collections.Counter(called_plans(dict(loc='197', name='0x001D'), C, variant_rng=random.Random(s))[1]['power']['power']
                                    for s in range(40))
        self.assertEqual(set(picks), {136, 152})                        # two species share 0x1D
        self.assertEqual(called_plans(dict(loc='197', name='0x001D'), C), {})   # without a pick: unresolved


class MultiKindIdentityTests(unittest.TestCase):
    def test_bosses_that_switch_kind_resolve_only_when_opted_in(self):
        from pe_weapon_sim.enemy_identity import MULTI_KIND, identity_keys, multi_kind_identities
        self.assertEqual(multi_kind_identities()[245, 6], (33, (2, 4)))         # kind 2 at setup, 4 later
        self.assertNotIn((245, 6), identity_keys(dict(C)))                      # historical default unchanged
        keys = identity_keys({**C, MULTI_KIND: 1})[245, 6]
        self.assertEqual([k for k, _ in keys], [0x221, 0x421])                  # logged boss id 0x0421
        f = dict(loc='429', name='0x0426')
        self.assertEqual(called_plans(f, C), {})
        plans = called_plans(f, {**C, MULTI_KIND: 1})
        self.assertEqual(sorted(plans), [0, 1, 3, 4, 5])
        self.assertEqual((plans[0]['kind'], plans[0]['power']['power']), ('window', 172))

    def test_silent_identities_never_attack(self):
        from pe_weapon_sim.enemy_choice import silent_identity
        from pe_weapon_sim.enemy_identity import MULTI_KIND
        mk = {**C, MULTI_KIND: 1}
        self.assertTrue(silent_identity(dict(loc='269', name='0x041B'), mk))      # actors 6/7: no command in flow
        self.assertFalse(silent_identity(dict(loc='269', name='0x041B'), C))      # unresolved without opt-in
        self.assertTrue(silent_identity(dict(loc='273', name='0x0125'), C))       # passive parts
        self.assertFalse(silent_identity(dict(loc='269', name='0x0220'), mk))
        self.assertFalse(silent_identity(dict(loc='146', name='0x0013'), C))

        class Fixed:
            def sample(self, rng): return 600
        def run(silent):
            opts = dict(shared_cells=C, static_enemy_catalog=True, called_slots=dict(contact='early', silent=silent),
                        enemy_defaults=dict(source_action_slot=0, charge_step=90, windup=10, recovery=10))
            return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), dict(level=21, stat22=67, offense=180),
                                [{**foe(100000), 'loc': '273', 'name': '0x0125'}], Fixed(), random.Random(2), time_cap=30.0,
                                source_options=opts)
        loud, quiet = run(False), run(True)
        self.assertGreater(loud['damage_taken'], 0)
        self.assertEqual(quiet['damage_taken'], 0)
        self.assertEqual(quiet['called_slot_silent_foes'], 1)
        self.assertGreater(quiet['no_contact_strikes'], 0)


class AtbGuardTests(unittest.TestCase):
    def test_gauge_above_zero_halves_incoming(self):
        class Fixed:
            def sample(self, rng): return 600
        def run(guard):
            opts = dict(shared_cells=C, static_enemy_catalog=True, called_slots=dict(contact='early'), hp=10 ** 7,
                        enemy_defaults=dict(source_action_slot=0, charge_step=90, windup=10, recovery=10))
            if guard: opts['atb_guard'] = True
            return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), dict(level=21, stat22=67, offense=180),
                                [{**foe(100000), 'loc': '146', 'name': '0x0013'}], Fixed(), random.Random(2), time_cap=30.0,
                                source_options=opts)
        off, on = run(False), run(True)
        self.assertEqual(off['hits_taken'], on['hits_taken'])                    # same timeline, only damage differs
        self.assertGreater(on['atb_guard_halved'], 0)
        self.assertLess(on['damage_taken'], off['damage_taken'])
        self.assertNotIn('atb_guard_halved', off)                                # opt-in


class LoggedChargeAndEvadeTests(unittest.TestCase):
    def test_logged_charge_fills_only_missing_steps(self):
        from pe_weapon_sim.logged_charge import lookup
        from pe_weapon_sim.enemy_catalog import lookup as cat
        self.assertEqual(lookup(dict(loc='332', name='0x0015', hp=45)), 40)    # small form
        self.assertEqual(lookup(dict(loc='332', name='0x0015', hp=170)), 65)   # large form
        self.assertNotIn('charge_step', cat(dict(loc='332', name='0x0015'), C))
        self.assertEqual(cat(dict(loc='146', name='0x0013'), C)['charge_step'], lookup(dict(loc='146', name='0x0013')))

    def test_player_evade_drops_strikes(self):
        class Fixed:
            def sample(self, rng): return 600
        def run(evade):
            opts = dict(shared_cells=C, static_enemy_catalog=True, called_slots=dict(contact='early'), hp=10 ** 7,
                        enemy_defaults=dict(source_action_slot=0, charge_step=90, windup=10, recovery=10))
            if evade: opts['player_evade'] = evade
            return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), dict(level=21, stat22=67, offense=180),
                                [{**foe(100000), 'loc': '146', 'name': '0x0013'}], Fixed(), random.Random(2), time_cap=30.0,
                                source_options=opts)
        base, all_evaded = run(0), run(1.0)
        self.assertGreater(base['hits_taken'], 0)
        self.assertEqual(all_evaded.get('hits_taken', 0), 0)
        self.assertGreater(all_evaded['evaded_strikes'], 0)


class TemplateCriticalTests(unittest.TestCase):
    def test_template_byte_is_zero_in_retail_exe(self):
        raw = (PROJECT / 'parasite-eve-recomp/disc/SLUS_006.62.original-backup').read_bytes()
        load = struct.unpack_from('<I', raw, 0x18)[0]
        self.assertEqual(raw[0x800109B0 + 0x90 - load + 0x800], 0)                # g_EnemyCombatantInitial.effectChance

    def test_status_only_attacks_resolve_with_default(self):
        f = dict(loc='429', name='0x0026')
        self.assertEqual(power_profile(f, 3, C, scaled_identities=True), {})       # strict path unchanged
        p = power_profile(f, 3, C, scaled_identities=True, default_critical=True)
        self.assertEqual((p['power'], p['effect_type'], p['critical_chance'], p['critical_source']), (0, 2, 0, 'template default 0'))


class CombatTests(unittest.TestCase):
    def run_one(self, called):
        class Fixed:
            def sample(self, rng): return 600
        opts = dict(shared_cells=C, static_enemy_catalog=True, hit_trace=True,
                    enemy_defaults=dict(source_action_slot=0, charge_step=90, windup=10, recovery=10))
        if called: opts['called_slots'] = dict(contact='early')
        return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), dict(level=21, stat22=67, offense=180),
                            [{**foe(100000), 'loc': '146', 'name': '0x0013'}], Fixed(), random.Random(2), time_cap=30.0,
                            source_options=opts)

    def test_fallback_replaced_by_source_power(self):
        old, new = self.run_one(False), self.run_one(True)
        self.assertGreater(old.get('legacy_damage_hits', 0), 0)
        self.assertEqual(new.get('legacy_damage_hits', 0), 0)
        self.assertGreater(new['explicit_power_hits'], 0)
        self.assertEqual(new['called_slot_matches'], 1)
        self.assertGreater(new.get('strike_timing_module', 0), 0)                  # room-module timeline (room_modules)
        self.assertEqual(new.get('strike_timing_untimed', 0), 0)

    def test_audit_files_reproduce_published_run(self):
        base = json.loads((ROOT / 'pe-fallback-hit-audit-baseline-2026-10-18.json').read_text())
        pub = json.loads((ROOT / 'pe-current-model-balance-2026-10-18.json').read_text())['coverage']
        self.assertEqual(base['fallback_hits'], pub['legacy_damage_hits'])
        self.assertEqual(base['hits'] - base['fallback_hits'], pub['explicit_power_hits'])


class TemplateRankAndMeleeDodgeTests(unittest.TestCase):
    def test_template_rank_identity_is_silent_part(self):
        from pe_weapon_sim.enemy_identity import rank_default_identities, MULTI_KIND, identity_keys
        from pe_weapon_sim.enemy_choice import silent_identity
        self.assertEqual(rank_default_identities()[34, 4], 0x100)
        self.assertNotIn((34, 4), identity_keys(dict(C)))                      # opt-in only
        self.assertTrue(silent_identity(dict(loc='34', name='0x0100'), {**C, MULTI_KIND: 1}))

    def test_melee_dodge_skips_melee_only(self):
        class Fixed:
            def sample(self, rng): return 600
        def run(dodge):
            opts = dict(hp=10 ** 7, enemy_defaults=dict(charge_step=90, windup=10, recovery=10, power=50))
            if dodge: opts['player_evade_melee'] = dodge
            return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), dict(level=21, stat22=67, offense=180),
                                [foe(100000)], Fixed(), random.Random(2), time_cap=30.0, source_options=opts)
        self.assertLess(run(1.0).get('hits_taken', 0), run(0)['hits_taken'])     # committed hits still land
        self.assertGreater(run(1.0)['evaded_melee'], 0)
        self.assertGreater(run(0)['hits_taken'], 0)

if __name__ == '__main__':
    unittest.main()
