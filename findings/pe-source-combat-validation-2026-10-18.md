# Integrated source combat validation — 2026-10-18

944 encounter benchmark calls completed offline. Every result passed ammo conservation.
Endurance calls contain three linked combat segments carrying ammo, gauge and HP.
Synthetic equipment: power100, magazine5, RoF3; Aya stat22=79, HP300.
Source player events are combined with the existing modeled enemy periods/movement/statuses.
No campaign-policy ranking or retail parity is claimed.

Representative handgun group encounters (8 matched seeds each):

| Mode | Win fraction | Mean seconds | Mean damage dealt |
|---|---:|---:|---:|
| ordinary | 0.000 | 3.880 | 11.9 |
| random | 0.000 | 4.020 | 24.4 |
| burst | 0.000 | 4.010 | 34.0 |
| all | 0.000 | 3.880 | 10.6 |

Two-gun medium-mobile scenarios (8 matched seeds each):

| Policy | Stream wait per switch | Win fraction | Mean seconds | Switches across seeds |
|---|---:|---:|---:|---:|
| primary_only | 0 | 0.500 | 7.920 | 0 |
| primary_only | 20 | 0.500 | 7.920 | 0 |
| alternate | 0 | 0.500 | 8.720 | 6 |
| alternate | 20 | 0.500 | 8.720 | 6 |
| distance | 0 | 0.625 | 8.520 | 6 |
| distance | 20 | 0.625 | 8.520 | 6 |

Times include losses/timeouts: compare win fractions first. Defaults for unspecified enemy
angles are seeded uniform headings; burst occupancy is therefore a geometric scenario assumption.
Switch policies are simple controlled experiments, not optimized strategies. See the integration
notes and raw results for status assumptions, explicit resource budgets and unsupported features.
