"""Focused source/beam regression validation; deliberately excludes balance suites."""
import hashlib,io,json,unittest
from pathlib import Path


def main():
    names=['test_shared_combat','test_boss_beam_choice','test_beam_launch_timing','test_beam_scheduling','test_enemy_actions','test_beam_combat','test_joint_beam_integration','test_projectile_geometry',
           'test_source_battle','test_source_enemy']
    loader=unittest.defaultTestLoader
    suite=unittest.TestSuite(loader.loadTestsFromName('pe_weapon_sim.tests.'+n) for n in names)
    old=loader.loadTestsFromName('pe_weapon_sim.tests.test_source_combat.SourceCombatTests')
    suite.addTests(t for t in old if not t.id().endswith('test_encounter_suite_and_surrogate_guard'))
    output=io.StringIO();result=unittest.TextTestRunner(stream=output,verbosity=1).run(suite)
    root=Path(__file__).resolve().parents[2]
    source=Path('D:/Recomp Games/Parasite Eve Project/parasite-eve-decomp')
    files=[source/n for n in ('src/main/fieldfx/geometry.c','src/overlays/room_lib/spark_attacks.c','src/main/pm/process.c','src/main/battle/context.c','src/main/script/value_ops.c','src/main/script/system_opcodes.c','src/main/script/node_actions.c','src/main/script/flow_opcodes.c','src/main/entity/frame_update.c','src/main/field/actor_collision.c','src/main/psyq/libgte/ratan.c','src/main/script/actor_opcodes.c','src/main/battle/turn.c','src/main/entity/combat.c')]
    files += [root/'tools/pe_weapon_sim'/n for n in ('beam_combat.py','beam_delivery.py','effect_cleanup.py','source_combat.py','beam_scheduling.py','script_decisions.py','beam_launch_timing.py','pm_pass_oracle.py','ratan_oracle.py','animation_wait_oracle.py','boss_beam_choice.py','enemy_power.py','incoming_damage.py')]
    report=dict(scope='Focused deterministic validation only; no balance reruns or gameplay',
        tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),
        passed=result.wasSuccessful(),rerun_readiness=False,
        sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        log=output.getvalue())
    target=root/'findings/data/pe-beam-combat-validation-2026-10-18.json'
    target.write_text(json.dumps(report,indent=2)+'\n')
    print(output.getvalue());print(target)
    if not result.wasSuccessful():raise SystemExit(1)

if __name__=='__main__':main()
