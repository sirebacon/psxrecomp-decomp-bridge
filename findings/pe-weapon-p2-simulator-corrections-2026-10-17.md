# Weapon balance phase 2 — A. Simulator corrections (2026-10-17)

Continues [pe-weapon-simulation-audit-2026-10-17.md](pe-weapon-simulation-audit-2026-10-17.md).
Phase 1 results are kept as they were (`findings/data/pe-weapon-benchmark-2026-10-17.json`);
phase 2 results: `pe-weapon-phase2-2026-10-17.json` (+ `phase2b`), mechanism tests:
`pe-weapon-phase2-mechanism-2026-10-17.json`. Runners: `run_phase2.py`, `run_phase2b.py`;
tables: `report_phase2.py`. Tests: 24 (7 new), `python -m unittest discover -s tools/pe_weapon_sim/tests`.

## Bugs fixed

| Bug | Fix | Effect |
|---|---|---|
| **Endurance didn't carry the magazine**: `run_benchmark.run_encounter` set `loaded` but every `fight()` started full | `fight(start_loaded=...)`, returns `loaded_left`; the chain passes it on (tests `test_magazine_carries_between_fights`, `test_endurance_chain_carries_magazine`) | Endurance slower for small magazines: HK40 3.2 -> 4.2 s (+31%), M10B 6.0 -> 6.7 (+12%), M11 +10%, G19 +9%; big magazines unchanged (P90, MAG, SG550). Rankings unchanged. |
| An edit of mine broke the stagger block's indentation (caught by the tests before any run used it) | restored | none |

## New modelling (experimental rules inert in VANILLA / CURRENT; test `test_baselines_have_no_phase2_rules`)

| Addition | What | Evidence |
|---|---|---|
| Movement policies | `stand`; `approach` (old fixed 0.6 s); `walk` (Aya walks at `walk_speed` while her bar fills, stops at 90% of range; only travel beyond the fill delays her; targets keep moving; two chases max); `close_in` (walks to an absolute `close_d`) | Battle walk speed **~440 units/s measured live** (pe_mod_menu.c note, 2026-10-12); sensitivity 300 / 440 / 800; Aya can move while the bar fills (game behaviour) |
| Close risk | enemy hit chance x(1 + `close_risk`) for an enemy within 450 units when it acts | assumption; 0 and 0.25 tested |
| Magazine scaling | `mag_scale` per weapon id or kind | experiment |
| Proximity damage | `prox` by absolute distance (fixed or linear fade) and weapon kind | experiment (test `test_prox_absolute_distance_and_kind`) |
| Stagger | `stagger`: per command volley, chance, delay of the target's next action, cooldown, boss multiplier | experiment (test `test_stagger_cooldown`) |
| Smart reload | reload at turn end when the rounds left can't cover the next turn | experiment R1 |
| Mechanism probes | absolute crit-zone caps, Commands ATB cost, Attack All on the first command only | analysis only (`X_*`), not proposals |

## Findings that change how results should be read

1. **Walking removes most range problems.** At 440 units/s, out-of-range turns fall from 36-50%
   (standing, keep-away boss) to 0-3% for every class; keep-away clear times drop 8-35%. The
   phase 1 "stand" results overstate how often short guns can't attack.
2. **Magazine / volley alignment.** The game reloads only an empty magazine, so leftovers make a
   short next turn. Magazine increases are non-monotonic: M10B (2 Commands + Random = 8 bullets
   a turn) is faster at 8 rounds (+25%) than at 10 (+50%, worse than the stock 7).
3. **Per-bullet firing time decides RoF 7/10 on the P90.** At 0.05 s a bullet P90 RoF 7 beats
   RoF 3 on bosses (6.3 vs 7.9 s); at 0.10 s it loses (9.3 vs 7.9). The handgun result (RoF 7/10
   lose) holds at both. Needs a measurement before any RoF decision.
4. **The Day 5 boss attempts were at level 21, where Aya's HP was correct** (296 = chart; the
   HP-level bug began at level 24). Re-running the logged loadouts (M79 RoF 5 attack 66, M9 RoF 3
   attack 40) with walking: 14.7-15.5 s, ~220-230 HP lost (stand: 17.7 s, 260 HP).

## Remaining assumptions, by how much they can move rankings

| Assumption | Can it change rankings? | Resolve by |
|---|---|---|
| Per-bullet firing time (0.1 s) | **Yes** (RoF 7/10, Commands value on many-bullet guns) | debug-server timing: command -> control return, P90 RoF 3 vs 10, handgun RoF 3 vs 7 |
| Animation loop length | Moderately (handgun vs machine gun order was stable at x0.5-x2) | same measurement |
| Burst cone share (50%) | For shotguns in groups | log enemies hit per Burst bullet |
| How often a shotgun can stand within 400 units | **Yes** for any proximity rule | log distance at each shotgun bullet (hitq already has the band; add absolute distance) |
| Enemy attack rhythm / damage | Damage-taken totals, not clear-time order | hurt rows with enemy slot |
| Counter rank | Counter's value | log rank bytes on the roll |
| Mod availability / investment by stage | Absolute levels | loadout logging |
