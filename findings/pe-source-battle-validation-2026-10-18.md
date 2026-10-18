# Offline reload, firing-mode and switching validation — 2026-10-18

192 attack cases and 168 carried-state switch sequences completed.
Each firearm case asserts conservation of loaded ammo + pooled reserve + rounds fired.
No game process, controller, save load or live scan is used.

Representative bank0 handgun cases, RoF5, three eligible targets:

| Mode | Ammo setup | Updates | Shots | Transfers | Loaded left | Reserve left |
|---|---|---:|---:|---:|---:|---:|
| ordinary | loaded | 89 | 5 | 0 | 25 | 0 |
| ordinary | reload | 175 | 5 | 2 | 0 | 3 |
| ordinary | empty | 65 | 0 | 0 | 0 | 0 |
| random | loaded | 171 | 7 | 0 | 23 | 0 |
| random | reload | 300 | 7 | 3 | 0 | 1 |
| random | empty | 85 | 0 | 0 | 0 | 0 |
| burst | loaded | 89 | 5 | 0 | 25 | 0 |
| burst | reload | 175 | 5 | 2 | 0 | 3 |
| burst | empty | 65 | 0 | 0 | 0 | 0 |
| all | loaded | 197 | 15 | 0 | 15 | 0 |
| all | reload | 361 | 8 | 4 | 0 | 0 |
| all | empty | 95 | 0 | 0 | 0 | 0 |

Representative handgun→rifle→handgun sequences (three RoF3 attacks, six menu updates per switch):

| Gauge cost | Stream wait per switch | Total updates | Nominal seconds | Final loaded a / b |
|---|---:|---:|---:|---|
| retail full | 0 | 583 | 19.466 | 7 / 4 |
| retail full | 20 | 583 | 19.466 | 7 / 4 |
| CURRENT half | 0 | 459 | 15.326 | 7 / 4 |
| CURRENT half | 20 | 459 | 15.326 | 7 / 4 |

The all-target partial-magazine path can repeat more than nominal RoF after a reload:
the traced ready branch resets the remaining-shot counter. This literal-source result
is flagged for independent retail validation; do not turn it into a balance recommendation.
Seconds use nominal29.95 updates/s; stream waits are explicit inputs, not predicted disk latency.
See pe-source-battle-derivation-2026-10-18.md for source references and scope.
