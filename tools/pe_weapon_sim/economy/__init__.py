"""Phase 3 (2026-10-17): integrated progression economy on top of the phase 1/2 combat engine.

Modules: tables (game data), rules (VANILLA / CURRENT / EXPERIMENTAL economy rulesets with
validation tags), bp (ledger), loot (pe_loot.c rare cascade and Junk), equipment (item instances,
provenance, Tool transfers, Mod Catalog), inventory, acquisition (campaign events by exploration
profile), surrogate (fast loadout score for routine battles), policies (A-I), playthrough
(continuous run with a transaction log), evaluation (checkpoint benchmarks with engine.fight),
reporting, run_phase3 (experiments). Phase 1/2 modules are imported, never modified.
"""
