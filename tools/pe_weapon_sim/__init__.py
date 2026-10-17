"""Parasite Eve weapon simulator (2026-10-16 rewrite).

Three independent rulesets (rules.py): VANILLA (the original game, decomp formulas), CURRENT
(what the PE mod implements today, read from pe_mod_effects.c / pe_pe_balance.c) and
EXPERIMENTAL (CURRENT plus switchable proposals E1..E6, all off by default). Baselines are frozen
dicts; experiments are built with rules.experimental(**switches) and never edit them.

Modules: rules (rulesets + validation table), data (weapons from the game's item table, enemies
from the wiki with the log-fitted defense, play-log distance calibration), engine (one fight),
encounters (benchmark scenarios), metrics (summaries, Pareto), run_benchmark (the CLI).
"""
