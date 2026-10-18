# Enemy projectile timing and remaining chooser inventory — October 18, 2026

All work was offline: decompiled C, the original executable's previously extracted data,
and raw US disc assets. No game launch, control, or live memory access.

## Source findings

The map156 and map380 room directories register effect129 (burst orb) and130 (beam).
The extractor follows the registration pointer into the room's overlay and then its task
program/script pointers. It checks the callback binding against the overlay symbols and
records raw triples, addresses, room hashes and source hashes. The overlay virtual address
maps to room byte0, not the directory record's payload byte8.

Effect129 task triples are:

    (5,0,0), (1,6,44), (2,1,0), (4,46,0), (2,0,0), (4,8,0), (0,0,0)

`FieldFx_UpdateTasks` starts the held state, writes variable6=44, starts the spray task,
yields for46 updates, then starts the orb controller on effect update47. That controller
emits the orb at age1, effect update48. The spray is visual; it is not an extra damage hit.
This clock is relative to the first effect update, not a guaranteed wall-clock or battle
script pass. Exact same-frame actor/process ordering remains unresolved.

The map156 actor3 chooser's distance helper sums absolute X, Y and Z differences in16.16
units (Manhattan/L1 distance). It is not Euclidean range. The extracted close gate uses
strict distance<1300 to enter slot0. Entering the later projectile path yields these speed
bands: >3500:250, >3000:200, >2000:150, >1500:120, >1000:100, otherwise80 units/update.
These are strict comparisons; distance2000 uses120, distance2001 uses150.

The orb starts at joint7, heads along the actor's orientation, and has vertical velocity24.
Each flight callback adds velocity plus independent integer jitter[-16,15] to X/Y/Z, stored
as signed16 coordinates. It changes to floor-burst state when Y reaches the room floor.
Contact checks use X/Z only, strict squared-distance less than (extra radius + Aya's hit
cylinder radius)^2: extra150 in flight, extra400 during burst timer1..8. The particle expires
at burst timer16; outside the walkable polygon it instead expires after6 callbacks.
A contact writes player-hit flag0x4000, held counter25 and enemy flag0x80000000. The held
counter decrements while>=2, so another eligible contact requires24 more effect updates.
The model reproduces these rules but does not claim that every contact is delivered damage.

The core field0x52 polled by the actor script is the six-bit held counter in flags24..29,
not a simple animation duration. The effect script clears it and marks event state4 after
its tasks drain. Slot4 waits for that external event; clip length alone cannot finish it.

## Linked beam choices and timing

Effect130 uses task triples:

    (5,0,0), (1,6,45), (4,46,0), (2,0,0), (4,8,0), (0,0,0)

The beam task starts at effect update47. It runs six approach callbacks, six expansion
callbacks, a parameterized active duration, then32 fade callbacks. Its first active contact
opportunity is update59; radius is600 plus Aya's cylinder radius, tested around a target
position. The target's height is forced to the floor, and only X/Z enters the contact test.
A separate interval countdown gates repeat opportunities, in addition to held-state rearm.

Map156 child actors4/5/6 choose parameters from node-active-flags[27]==1:

| Actor | Flag27 equals1 | Otherwise |
|---|---|---|
| 4 | duration60 / interval60 | duration300 / interval300 |
| 5 | duration60 / interval60 | duration300 / interval140 |
| 6 | duration60 / interval60 | duration300 / interval140 |

The initializer's mode1 writes duration/interval into a slot; a subsequent mode2 writes
the target X/Z from external cells21..26. Conditional on staying within range and remaining
uninterrupted, duration60/interval60 has opportunity59; duration300/interval300 also59;
duration300/interval140 has59,199,339. Callback completion is150 or390, followed by a
possible stop check151 or391. These are opportunities, not damage totals. Parent linking,
shared target state, concurrent updates and overlapping player-hit flags need decoding
before beams can be added as independent damage sources. They are extracted/tested but
are **not** injected into this balance rerun.

## Remaining action-choice inventory

Across the prior possible control-flow graphs, the new output indexes273 immediate
comparisons after distance reads,1,583 random-assignment sites and1,982 state-branch sites.
These counts include setup randomization and possible callback paths; they are not enemy
species counts or action probabilities. Each retains map, actor type, offset and operands.
This makes further analysis targeted without pretending that unknown inputs are solved.

## Simulation integration and explicit assumptions

The opt-in projectile backend applies only to map156 ID0x0216. Its outer chooser gates are
assumed entered. Distance<1300 selects the previously derived slot0 windup35/recovery6;
otherwise the scenario forces the verified later slot4 orb path. Intermediate far-path
conditions, concurrent chooser latches and moving between attack regions remain unresolved.
Other enemies retain the prior action-timing/static catalog or generic fallback.

Two launch-height scenarios use320 or640 units above a flat floor. The player is a stationary
point on a one-dimensional axis, the actor aims down that axis, and the orb stays inside
the polygon. These positions, height, heading and zero player-cylinder radius are scenario
inputs, not extracted joint transforms. Real bank animation poses and floor polygons are
not yet replayed. Random jitter reproduces source ranges, not the shared PSX RNG stream;
its separate deterministic generator does not consume the existing combat generator.
A regression test requires the close melee branch to preserve the baseline combat results.

Completion still uses an explicit visual-drain surrogate: at least63 action updates and
25 after floor impact. Full cosmetic callback-pool traversal and its exact final-update
ordering are unresolved. The model resets charge at effect completion as the script does,
but that completion time remains approximate. Status/counter interruptions and delivered
projectile damage still use the earlier combat approximation and fallback damage formula.
Geometric orb contacts bypass the generic75% hit roll to avoid counting hit chance twice.

The standalone flight sweep contains112 samples: seven distances, two heights, eight seeds.
For example, at distance2000, height320 produced contact in4/8 samples; height640 in8/8.
At4000 the same counts were3/8 and8/8. This illustrates sensitivity to unextracted geometry,
not retail accuracy.

## Results and validation

Final full-suite and targeted results follow below. Historical reports remain unchanged.

Completed **27,936 combat simulations**: two full runs of12,816 plus2,304 focused boss fights.
Full runs retain eight frozen campaign seeds/group, six fights/encounter, eight build groups,
D5/Disc2 and fallback charge steps60/90/120. Each has150 eligible Counter-for-Quickdraw
seed/loadout comparisons. Equipment progression was not reoptimized. HP385 and reserves999
per ammo pool are controlled inputs. All ammo-conservation checks passed.

| Launch height | Matching enemy instances | Orbs launched | Geometric contacts |
|---|---:|---:|---:|
| 320 | 432/23838 | 942 | 426 |
| 640 | 432/23838 | 483 | 483 |

Projectile coverage is432/23,838 enemy instances (1.8%) per full run. Prior attack-timing
coverage remains15.0%, and static charge/rank/poison coverage76.1%. The new projectile
case is in D5; **Disc2 combat records and rankings remain unchanged** from the prior
action-timing run. Controlled machine scores5.178/5.379/5.535 at fallback60/90/120.
At D5 fallback90, groupG is lowest-score in both scenarios:12.435 (win.995) at height320,
11.347 (win1.000) at height640. These do not establish retail balance or a new recommendation.

Focused comparison: eight D5 frozen seeds for each of eight groups, three fights per
distance/height cell. Height0 is the old melee-only timing baseline. Table means pool
the64 seed/loadouts per cell; source geometry remains assumed.

| Distance | Height | Win fraction | Mean fight seconds | Mean damage taken |
|---|---|---:|---:|---:|
| 1000 | 0 | 1.000 | 17.281 | 60.483 |
| 1000 | 320 | 1.000 | 17.281 | 60.483 |
| 1000 | 640 | 1.000 | 17.281 | 60.483 |
| 1300 | 0 | 0.880 | 62.442 | 240.192 |
| 1300 | 320 | 0.885 | 63.051 | 256.342 |
| 1300 | 640 | 0.896 | 63.106 | 239.717 |
| 2000 | 0 | 0.005 | 88.213 | 343.742 |
| 2000 | 320 | 0.000 | 90.000 | 240.667 |
| 2000 | 640 | 0.005 | 89.989 | 335.667 |
| 4000 | 0 | 0.000 | 88.233 | 343.742 |
| 4000 | 320 | 0.000 | 90.000 | 133.000 |
| 4000 | 640 | 0.000 | 90.000 | 335.667 |

The distance1000 melee-only control is identical across all three cases, confirming that
projectile setup does not perturb the existing combat random stream. At distances2000/4000
most earned weapons cannot reach the boss, so these are projectile pressure/horizon checks,
not useful evidence for gun ranking. Greater assumed launch height changes orb lifetime and
therefore contact and recharge opportunities; its effect is not monotonic across all metrics.

**132 tests passed.** New cases validate task47/controller age1 launch, strict speed bands,
horizontal/cylinder collision, flight contact, floor timer9 cutoff/timer16 expiry,24-update
rearm, polygon expiry, beam windows, source option integration, pause behavior, ammo
conservation and unchanged close melee control.

Files: `data/pe-projectile-extract-2026-10-18.json`,
`data/pe-projectile-h320-balance-2026-10-18.json`,
`data/pe-projectile-h640-balance-2026-10-18.json`,
`data/pe-projectile-targeted-2026-10-18.json`.
Readable full comparisons are the corresponding height320/640 Markdown reports.

Reproduce with bundled Python and PYTHONPATH=tools:

    python -m pe_weapon_sim.extract_projectiles --out findings/data/pe-projectile-extract-2026-10-18.json
    python -m pe_weapon_sim.run_behavior_balance --projectile-height 320
    python -m pe_weapon_sim.run_behavior_balance --projectile-height 640
    python -m pe_weapon_sim.run_projectile_targeted
    python -m unittest discover -s tools/pe_weapon_sim/tests -q

## Next targeted work

1. Recover joint7 launch transforms, floor polygons, cylinder radius and heading from the
   already extracted room animations; replace height/aim/inside-polygon assumptions.
2. Replay actual callback pools and final task-stop ordering to replace the visual-drain
   surrogate. Trace contact flags through player damage delivery and interruption handling.
3. Interpret node-active-flags[27] and shared beam target cells21..26; couple the three
   child emitters to the boss and resolve overlapping hit flags before adding beam damage.
4. Use the indexed distance/state/random sites to recover remaining chooser predicates.
   Preserve unknowns and per-room identity joins; do not assign uniform action probabilities.
5. Resolve indirect attack power and field scaling, then rerun the same frozen seeds and
   focused controls. Leave campaign reoptimization pending until the surrogate is calibrated.
