# Projectile geometry and linked beam delivery — October 18, 2026

Balance reruns are on hold at the user's request. This pass performed offline asset
extraction and11 focused decoder/geometry/delivery checks only. No balance suite,
targeted combat benchmark, game control or live memory scan was run. Previous balance
outputs remain historical; these findings have not been reflected in their scores.

## Geometry now backed by assets

The hospital map156 scene script sets the effect floor to **Y=-1873** through player
context field255. Actor7 also registers a nine-vertex X/Z polygon from its script blob:

    (4000,-4550), (5000,-6892), (5513,-8647), (5556,-10550),
    (-2165,-10773), (-918,-8117), (-718,-7770), (-1507,-5210), (2487,-4450)

These replace the assumption that the projectile always stays inside an infinite plane.
`projectile_geometry.point_in_polygon` ports the source parity test, including signed32
low-product behavior. Edge behavior follows the source comparisons, rather than an
invented inclusive-boundary rule. Integration into projectile flight is still staged.

The script spawns boss type3/sub31 at a literal16.16 world position. Model records for
actor types3/4/5/6 share the same47-part model, with cylinder radius390. The extractor
records part translations, bounds and the67-byte push/pop matrix command stream.
The model's radius is not Aya's radius and is not a launch-height measurement.

The initial Aya collision radius is read by Render_SetupEntityPrims from the model's
section14 pad. All16 weapon banks (eight classes x two costumes) were read from Disc1:

| Kind | Weapon class | Radius, costume0 | Radius, costume1 |
|---|---|---:|---:|
| 1 | handgun | 23 | 23 |
| 2 | shotgun | 35 | 35 |
| 3 | machine | 41 | 41 |
| 4 | rifle | 63 | 63 |
| 5 | grenade | 37 | 37 |
| 6 | rocket | 53 | 53 |
| 7 | special | 23 | 23 |
| 8 | club | 27 | 27 |

This is weapon-model-dependent collision data, not one universal Aya radius. The existing
Disc2 PST's runtime radius63 matches its model section exactly. Normal model setup and
weapon-switch reload paths must preserve the corresponding radius when integrated; do not
copy the snapshot's63 to every weapon. Attachment helpers have separate radius writes.
This matters for projectile hit chance as well as attack speed and range.

The raw root translations and47 bone rotation channels are decoded for modes8/9/10/11:
45+36+42+45=168 frames. Both byte-packed and halfword-packed channel formats are supported,
including constant channels, padded strides, signed root translation and byte-angle x16.
These replace opaque frame-count-only records with the data needed for pose reconstruction.

`FieldFx_TransformMatrixPoint` rotates a local offset by a joint's world rotation, adds
that joint's translation, and narrows to signed16. Orb launch uses joint7 with local
**(0,-70,-100)**; the beam emitter uses joint31 with local **(0,0,-100)**. The direction
helper uses transform0 to derive heading. These are not literal world coordinates or fixed
heights. `transform_point` supports a checked sf12 subset; it rejects the range requiring
GTE saturation emulation. It does not claim a completed PSX joint/world-pose solver.

Remaining geometry work: recreate RotMatrixYXZ/fixed-point bone hierarchy, actor world
rotation/position, animation overrides and shared render transforms; confirm which frame
is visible to each effect pass. The decoded floor and player radius alone do not make
height320/640 or aligned-heading scenarios retail-accurate.

## How the beam owners are linked

The analyzed path does not require a C parent pointer. Each owner4/5/6 has a separate
combat record and waits on a shared trigger cell18/19/20. When triggered, it queries the
position of **actor type3/sub31** and copies that position to itself. The query's31 is an
actor sub-ID, not a bone number. This is distinct from joint31 used inside the beam effect.

Each owner starts effect130, writes its own slot0/1/2 parameters, copies target cells
21/22,23/24,25/26, and executes its own action record3 (enter10/exit11). It then waits for
held field0x52 to reach zero, clears its trigger cell, and returns to the wait loop.
The main actor writes the target cells; they are not necessarily Aya's current position.
Their complete strategies and concurrent scheduling remain to be decoded.

The shared flag27==1 branch selects duration60/interval60; other values select300/300 for
owner4 and300/140 for owners5/6. Some observed main-script assignments write0 or2, so the
short branch must not be assigned an arbitrary probability. The earlier conditional
phase/contact windows remain valid, but their encounter frequency is unresolved.

## Contact is separate from delivered damage

The beam controller tests the target area, sets Aya's contact latch0x4000, sets its own
pending bit0x80000000, and sets its own held counter25. The damage-delivery scan in
Menu_MainUpdate has an outer reaction/action gate. Once admitted, it scans actors in
list order and accepts pending owners whose active effect state is1 or2.

Key consequences proved by source and captured in the staged drain helper:

- Several eligible owners can deliver in the same pass. The outer gate is not rechecked
  after the first hit; later per-hit behavior can still affect damage/status calculations.
- Each delivered owner's pending bit is cleared individually. Dead owners, missing effects
  and effect states outside1/2 do not deliver through this path.
- On a gated pass, the pending owner bits can remain, but Aya's global0x4000 latch is
  cleared at the end. Pending bits do not automatically deliver next update without a
  new player latch; a later contact can admit earlier pending owners too.
- Aya's0x01000000 /90-update contact timer is checked by the separate **body-contact**
  branch. It is not the admission test for these action hits. It cannot be used to collapse
  all simultaneous beam owners to one damage event.

`projectile_geometry.drain_action_contacts` models this action-hit selection/latch subset,
with a supplied per-hit callback. It deliberately does not invent full beam damage,
reaction animation, special status behavior, or global frame ordering.

The damage function is Entity_ResolveDropTable despite its misleading name. Each owner's
record3 power is `u16((shared_cell10 * 90) >> 16)`; the scale comes from script variable80,
with a65536 fallback if it was zero. It is not safe to call all beams power90 unconditionally.
Record slot3 selects the armor's second parameter. Damage also uses Aya's defense/5,
critical chance, guard/barrier state and the effect type. The existing integer damage
helper already distinguishes selected record slot from effect category.

The beam effect type is **5: stiffness lock**, not plain damage. It may clear Haste and
sets statusTimer46 to9000 status units, decremented by statusStep3C, not9000 seconds or
necessarily9000 frames. A stiffness-resistance armor flag gives a50% prevention roll;
already-active lock and one-time immunity have separate source branches. Incoming status,
its movement/action consequences, cures, and simultaneous-owner delivery must be wired
before linked beam balance is meaningful. This is another reason to keep reruns on hold.

## Validation and artifacts

11 focused tests passed: channel decoding, real asset counts/radii/floor data, sf12 offset
math, explicit rejection of unimplemented saturation, polygon containment/winding,
same-pass multi-owner delivery, reaction gating, persistent owner flags, global latch
clearing, invalid/dead owner rejection, and separate body-contact immunity semantics.
The old132-test full suite was not rerun in this pass; no new total-suite claim is made.

New files:

- `tools/pe_weapon_sim/extract_projectile_geometry.py` — offline reproducible extraction.
- `tools/pe_weapon_sim/projectile_geometry.py` — staged geometry/delivery primitives.
- `tools/pe_weapon_sim/tests/test_projectile_geometry.py` —11 focused checks.
- `data/pe-projectile-geometry-2026-10-18.json` — channels, models, floor, bank radii,
  owner command provenance, source/asset hashes, and explicit rerun-readiness=false.

Reproduce extraction/checks only with bundled Python and PYTHONPATH=tools:

    python -m pe_weapon_sim.extract_projectile_geometry --out findings/data/pe-projectile-geometry-2026-10-18.json
    python -m unittest discover -s tools/pe_weapon_sim/tests -p test_projectile_geometry.py -v

## Before a useful balance rerun

1. Complete joint-to-world pose reconstruction and validate it against existing saved
   transforms or independently decoded asset invariants; use the source floor/polygon and
   weapon-dependent Aya radius in projectile geometry.
2. Resolve shared target strategies, trigger/lifecycle ordering and the actual cosmetic
   callback-pool drain, replacing the current completion surrogate.
3. Connect actor-ordered action-hit delivery, incoming stiffness, per-owner power/armor
   selection and reaction state without double-counting collision opportunities.
4. Run focused invariants and a small controlled validation first. Only then resume the
   matched balance comparisons. Keep all previous result sets labeled historical until then.
