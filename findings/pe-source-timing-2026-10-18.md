# Source-derived timing cases — 2026-10-18

512 deterministic switch transitions at stat22 79. Values count eligible gauge updates,
not VBlanks or seconds. Menu and switch execution durations are excluded.

| Destination | Integer gain | Empty-to-full updates | Full-bar CURRENT switch to attack | Full-bar retail switch to attack |
|---|---:|---:|---:|---:|
| handgun | 79 | 114 | 57 | 114 |
| shotgun | 63 | 143 | 72 | 143 |
| machine | 79 | 114 | 57 | 114 |
| rifle | 63 | 143 | 72 | 143 |
| grenade | 63 | 143 | 72 | 143 |
| rocket | 31 | 291 | 146 | 291 |
| special | 79 | 114 | 57 | 114 |
| club | 158 | 57 | 29 | 57 |

The CURRENT gain after switching follows the destination weapon. Starting from an
empty gauge additionally requires reaching 4500 using the source weapon; retail
requires 9000. Rounded threshold overshoot is retained by CURRENT.

These are gauge-state calculations, not within-fight portfolio results. Historical
campaign rankings and optimistic secondary-weapon bounds have not been regenerated.
Clock rate and animation/event scheduling remain open. See the source audit and handoff.
