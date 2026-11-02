# D4 — Scoped validation and playtest plan / results record

Created: October 30, 2026. Updated: October 31, 2026. Status: **scoped plan plus save-query, capacity-refusal and conditional-emission unit results**. The initial plan executed no tests; follow-up results cover queries, refusal/dispatch/native-gate and conditional-emission fixtures, supported-save byte parity, native rebuild and six related regressions. Full preset validation and interactive playtests remain unrun.

## 1. Reading order and scope

References: [D1 proposal](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Economy presets and independent reward controls proposal.md>), [D2 control inventory/menu map](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Control Inventory and Menu Map.md>), [D3 persistence](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets - Persistence and Migration Design.md>), [D6 small API contract](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Mod Extensions - API and Cooperation Contract.md>), [D7 review/gates](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets and Mod Extensions - Pre-implementation Review.md>), and [master checklist](<D:/Recomp Games/psxrecomp-decomp-bridge/findings/PE Presets and Menu Organization - Master Checklist.md>).

Initial verification covers D2 slices A–D: audited baseline/contracts, Economy reward/storage separation, small typed contribution/observer/preset APIs, and scoped Economy navigation. Shared conventions apply across all future adopting mods, but this plan does not certify unimplemented Combat/Movement/collection/coordinator APIs.

October 31 scope addition: Section 15 plans separate D2 slices E–G for custom items/weapons/armor, installed effects and contributed shops under D1 §20, D3 §10 and D6 §10. These 36 additional cases and PB-10–14 are **unrun planned work**. Earlier save-host results remain limited to their recorded scope and do not certify custom content, new shop transactions or expanded storage. The original 83-case plan and historical results remain distinct from this extension.

Reference baseline from the design audit is clean `feat/localization` at `ae6520fe6` in `D:/Recomp Games/pe-localization`. Reconfirm the actual unchanged baseline, implementation branch, commits, build options, and dirty state before testing. Do not assume this reference executable is already built or still matches the source. Do not pull, switch branches, rebuild, or run the game merely to create this plan.

This plan defines behavior to prove rather than tests that simply reproduce implementation internals. Source inspection, mocked contracts, native integration, headless runs, and player sessions provide different evidence and must be labeled separately.

## 2. Local-only test suite and evidence rules

**All new test code, helper programs, example providers, fault injectors, benchmarks, fixture saves, generated packs, logs, screenshots, traces, crash reports, and raw playtest results stay local in `D:/Recomp Games/pe-native-debug`.** This checkout exists and has no configured remote as checked while preparing the plan. No local suite files or directories were created/modified for this document. Recheck remotes before later suite work; do not add one or publish the suite.

Suggested future layout inside that local checkout, not created here:

- `tools/presets/`: runners, fault/allocator shims, independent arithmetic/serialization checks, small local example providers.
- `scenarios/presets/`: scripted integration/menu/battle scenarios.
- `fixtures/presets/`: synthetic versioned records and disposable copies of owned saves; keep original saves outside destructive test paths.
- `runs/presets/<run-id>/`: manifest, case results, logs, before/after checksums, captures, timing/resource summaries, and failure artifacts.

Production implementation builds remain in the selected game checkout; local test executables/output belong under the local suite. The design documents may contain summarized outcomes and relative local evidence references after testing. Do not copy raw private saves, game/disc assets, full crash reports, usernames/paths, or local test sources into a PR. Do not introduce fixture/data download dependencies.

Each scenario gets an isolated preference directory, disposable card/storage data, and explicit pack/mod configuration. Never launch against the player's normal profile by accident. Verify the resolved profile/card paths before any write/fault test. Start the baseline and candidate in equivalent isolation so installed language packs/global settings cannot contaminate the comparison. Preserve originals; restore/copy the fixture between cases instead of carrying state across unrelated tests.

## 3. Readiness, policy bindings, and result vocabulary

Before behavioral implementation, approve this plan's applicable assertions and record the selected scope. Draft technical recommendations are not automatically accepted because a test uses them.

| Binding | Must be recorded before affected assertions run | Documents / review |
| --- | --- | --- |
| PB-01 | Legacy/new engine transition and Custom identity rules, shared charm behavior | D2 §§3–4; REV-02/09 |
| PB-02 | Routing combinations, wallet cap/credit/backpressure, existing-bundle consent | D2 §5, D3 §6; REV-03/04 |
| PB-03 | Price context and return-to-Enhanced behavior | D2 §5; REV-05 |
| PB-04 | Record layout/versions/status, conditional emission, carried-data capacity, save refusal, crash coherence | D3; REV-01/08/09 |
| PB-05 | Generation-success, pending identity/settlement, delivery/abandonment, guarantees/pool eligibility | D3 §6; REV-06 |
| PB-06 | RNG/draw order/test vectors, fractional arithmetic, contribution composition and ranges | D3 §7, D6 §5; REV-07/09 |
| PB-07 | Service/registration signatures, activation/readiness, lifetime, ID/capacity limits, notification phases | D6; REV-07/10 |
| PB-08 | Stable menu key/legacy alias migration and presentation scope | D2 §6; REV-11 |
| PB-09 | Target machine/build/settings, measurement budgets, cycle counts, and soak duration | D1 §§17–18, Sections 10–11 here |
| PB-10 | Supported custom archetypes/actions, stable ID encoding/limits, runtime adapters, instance schemas and provider ownership | D1 §20, D2 §9, D3 §10, D6 §10; CONTENT-01–03 |
| PB-11 | Actual custom-state/container capacity, migrations/reader matrix, opaque preservation, placeholder capacity, missing-equipment fallback/refusal and reinstall policy | D3 §10; CONTENT-04–06, EFFECT-02 |
| PB-12 | Effect runtime contexts, applicability, slots, native/custom adapters, built-in/removable provenance, stacking/conflicts and Catalog discovery presentation | D2 §9, D6 §10; EFFECT-01–04 |
| PB-13 | Offer/stock scope, Junk price/modifier policy, quote lifetime/generations, action preparation/commit/deduplication and coherent save/crash boundary | D3 §10, D6 §10; SHOP-01–04 |
| PB-14 | Registry/instance/attachment/payload/quote limits, lifecycle/seal/dependencies, cleanup ownership, target performance/memory budgets and tools/editor scope | D2 §9, D6 §10, Sections 10–11/15 here; CONTENT/SHOP verification |
| PB-15 | Standalone target branch, feature build/enable matrix, v1 service/build aliases and single publishers/record owners | D2 §10, D6 §15, D9; standalone extraction |
| PB-16 | Feature profiles/format, legacy INI/binary precedence, atomic import marker, reset/unknown-data retention and settings aliases | D3 §16; standalone migration |
| PB-17 | Wardrobe stored choice versus temporary availability, buying placement, Bestiary earned/paid distinction, wallet versus reward/routing readiness | D2 §10, D6 §15, D8/D9; product decisions must be explicit |
| PB-18 | Acquisition adapter selection/authentication, profile-plus-save durable purchase protocol, recovery/dedup, target resource budgets | D3 §16, D6 §15; MCR-08/09 and standalone acceptance |

Every run pins the accepted policy revision/hash alongside source commits. If a policy is not accepted or required host support is absent, mark the dependent case **BLOCKED — policy/implementation missing**, never PASS. A changed policy updates expected results and links the decision; it must not be retrofitted merely to excuse observed behavior.

Statuses: PLANNED (not attempted), BLOCKED (named prerequisite missing), PASS (assertions and evidence recorded), FAIL (observed violation), INCONCLUSIVE (noise/incomplete evidence), DEFERRED (outside current authorized slice), and NOT APPLICABLE (specific scoped reason). Deferred/unavailable-hardware/tool cases do not count as passes. Existing historical suites' results are not new results for this build.

G0: choose baseline/target/scope. G1: bind relevant Economy policies. G2: verify save-host prerequisites. G3: bind the actual typed API. G4: approve measurement criteria before acceptance and record results before release. G5: future coordinators remain deferred. Creating D4 closes only the missing-plan document task, not these gates.

## 4. Run manifest, fixtures, and independent checks

Record for every run:

| Field | Required contents |
| --- | --- |
| Identity | Run ID, date/time/timezone, tester, purpose, case IDs, status |
| Software | Baseline/candidate commit and dirty-state summary, executable digest, compiler/build options, linked mod list and versions, host/API/save versions |
| Policy | PB revisions, selected preset/engine, actual numeric settings, registration IDs/order, contributor activity, language/pack versions |
| Environment | OS/architecture, CPU/cores, RAM/GPU, display/resolution/frame limit, power mode, background load, tooling/instrumentation |
| Inputs | Disposable fixture ID/digest, scenario/seed/draw trace where controlled, action sequence and fault schedule |
| Outcomes | Expected invariants, before/after state, actual result, case status, local evidence paths, known limits/issue ID |

Fixture classes: vanilla/zero-tail save; historical fixed blocks; current five-record save; supported new policy under both engines; non-default legacy INI; full/empty bag/trunk; wallet 0/1/99,998/99,999; native and bonus copies of identical item IDs; pending item/bundle/currency; duplicate effects and permit thresholds; unknown/inactive/newer/corrupt records; near-full save union; missing preset provider. Create synthetic copies later; none are produced by this planning task.

Independent oracles: decode save records without using the candidate's decoder as the sole expected result; compare accepted byte-layout arithmetic, record IDs/version/CRC and preserved payload bytes; compute payout/fractional/RNG expectations from frozen contract vectors; track wallet/source-item/unlock conservation; compare unaffected native rewards/settings to the matched baseline. Whole-file byte equality applies where promised; otherwise compare semantic fields and documented volatile bytes, never ignore arbitrary differences.

## 5. Baseline, controls, and menu cases

| Case | Setup/action | Required observable result |
| --- | --- | --- |
| BAS-01 | Candidate with mods off; matched unchanged baseline | Native behavior and unaffected settings match; carried data preserved under supported capacity policy; no new API gameplay effects |
| BAS-02 | Untouched Enhanced, zero external providers | Existing payout/rounding/rare cascade/bundle values/prices/Wayne behavior match baseline; no new policy record if absent and never opted in |
| BAS-03 | Enhanced at Relaxed/Normal/Grind and custom legacy tuning | Coupling/rounding/RNG reset behavior retained; editing tuning never silently selects the new engine |
| BAS-04 | Existing Catalog/Rebuild/Requisition/QoL/collection enabled in normal supported combinations | Existing interactions remain usable; ownership, equipment, anti-exploit provenance and collection state unchanged by settings work |
| CTL-01 | Preview all presets, cancel, reselect, repeatedly inspect diagnostics | No RNG/progress/wallet/item/settings changes; no calculation callbacks or reward notifications from preview |
| CTL-02 | Explicit Apply and repeated identical Apply; stale preview token | First validated Apply uses safe boundary; repeat is no-op; stale/invalid application fails with no partial settings |
| CTL-03 | Legacy → new presets → Custom → Enhanced; pending entries and lowered guarantee | Accepted PB-01/PB-05 transition table exactly; no progress transfer/reset, duplicate victory credit, or settings-action reward |
| CTL-04 | Edit during battle/reward screen/Wayne action | Preview allowed where supported, mutation rejected/deferred according to policy until safe boundary; no mixed-engine battle |
| CTL-05 | Old page/label INI keys, conflicting canonical/alias keys, missing/unknown lines | Correct valid precedence, no loss of unrelated settings, no stale alias reimport after later edits |
| CTL-06 | Inventory Junk display on/off, link to routing, ordinary other-category settings | Presentation alone changes; no added income activation or duplicate backing value; other categories retain values |
| CTL-07 | English/es-419, long lists/provider descriptions, keyboard/controller Back/navigation | Readable text without clipping; clear Apply/Cancel; parent selection/scroll restored; moving focus never applies |
| CTL-08 | Catalog Weapon/Armor, hidden effects, Bestiary/Wardrobe viewers | Existing sidebar/discovery/independent-list behavior retained; undiscovered details hidden; no Wardrobe buying/unlocks added |

For legacy RNG parity, frame-seeded initialization must be controlled in a local harness or compared with equivalent known initial RNG state/draw trace. A difference caused by launching two processes at unrelated frame counts is not evidence of a regression. Do not change production RNG to make parity tests convenient.

## 6. Saves, migration, capacity, and recovery

| Case | Setup/action | Required observable result |
| --- | --- | --- |
| SAV-01 | Vanilla, fixed legacy blocks, and current five-record saves | Existing upgrade paths preserve legitimate wallet/catalog/shop/keys/sort; absent new record means Legacy, not unreadable-record fallback |
| SAV-02 | Supported policy round-trip; nonzero fractions/RNG/pity and all pending families | Decode/save/reload preserves accepted fields, engine, final identities/amounts, and progress; transient registry pointers never serialized |
| SAV-03 | Switch save A ↔ B; New Game/Tutorial/EX Game | Correct per-playthrough resets/retention; no new-policy/RNG/reward leakage; shared collection ownership follows existing profile policy |
| SAV-04 | Inactive/absent provider records, unknown IDs, unsupported newer record/container | Preserve carried bytes where supported; expose status; refuse unsafe new-mode mutation rather than guessing defaults or rewriting unknown data |
| SAV-05 | Corrupt policy/dependency CRC, truncated payload, bad enum/range/reserved bytes, missing dependency | Distinguish genuine absence from invalidity; block unsafe operations before consumption; valid unrelated records remain intact |
| SAV-06 | Accepted layout boundary, key length 47/48, chance sum 10,000/10,001, remainder/sequence maxima | Boundary acceptance/rejection exactly follows final schema; no truncation/wrap/reused sequence; no guessed larger-format support |
| SAV-07 | Actual union exactly fits, one byte over, record/header overhead, entry/count limits | Capacity preflight agrees with serialized union; same ID counted once; unsafe opt-in/save rejected before replacement, with no lost carried record |
| SAV-08 | Register new record but remain legacy; load large carried data after initialization | No unconditional policy emission/crowding out of other data; startup registration success alone does not admit a later save |
| SAV-09 | Fail registration; save preparation/allocation; path permissions/disk write/flush/replace | Attributable failure before unsafe mutation/replacement; last valid destination/backup remains recoverable; no false saved-success message |
| SAV-10 | Save/load with same supported provider ID but changed preset defaults | Stored concrete settings retained; missing/reappearing preset metadata does not reapply or reset progress |
| SAV-11 | Toggle master/mods off, save again, restart/load, reenable | Records preserved under accepted admission policy; no disabled reward delivery/roll; no duplicate registrations or delayed bonus replay |
| SAV-12 | Crash injection before/within/after credit, bundle consumption, unlock, and config activation | Recovery yields one coherent committed native+mod generation; no mismatched source-item/payment halves; staleness clearly identified |
| SAV-13 | Crash image publication interrupted; snapshot absent; recovery sees newer/unsupported image | Only fully published coherent generation used; no crash-path locks/allocations/mod callbacks; unsupported capture explicitly reported |
| SAV-14 | Terminate during staged card-file write/rename; restart recovery | Previous complete or new complete supported image recoverable as promised; no reliance on INI writer guarantees for card data |
| SAV-15 | Save editor/recovery round-trip without provider installed; inspect schema-known fields | Unknown records preserved; no semantic edits to unknown formats; known policy edits validate ranges and dependencies |
| SAV-16 | Older build/downgrade attempt using disposable copy | Record supported/unsupported outcome honestly; no claim arbitrary old builds honor new markers; backup retained and minimum-build restriction documented |

Candidate D3 budget vectors: baseline 524 bytes, candidate policy 172 including its header, total 696, remainder 48. An additional unknown record with 36-byte payload consumes that remainder exactly; 37-byte payload exceeds it by one. Include count/CRC/window variations separately. Update vectors if the accepted layout changes. Verify full union admission; merely observing the current warning after records were omitted is FAIL for the proposed lossless contract.

Crash tests must compare coherent native inventory/Wayne/equipment state and mod tail together. A correct tail CRC is insufficient. Use local deterministic interruption hooks/shims where feasible and label simulated versus actual crash-report/recovery coverage. Never execute fault cases against the user's real saves.

## 7. Reward correctness, loss prevention, and exploit cases

| Case | Setup/action | Required observable result |
| --- | --- | --- |
| RWD-01 | Counter-only/Vanilla-drops fixture with native Tool/Junk/booster/bundle rewards | Native non-Junk IDs/counts unchanged, native Junk routes 1:1, no added rolls/empty-steal compensation; bonus category ID filtering never removes native items |
| RWD-02 | New preset ordinary and boss wins; losses/escape/non-battle scene transitions | Fixed base payment only on admitted eligible victories; boss replaces ordinary, no double payment or spurious scene award |
| RWD-03 | Scavenger/Lucky Find/charm combinations, fractional base 1, saves and engine switches | Accepted equipment order/duration/remainder applied once; disabled families stay off; new fractional policy matches independent vectors; Legacy unchanged |
| RWD-04 | Item chance off/0/100%, guarantee off/near threshold/lowered; no eligible pool | Accepted attempt/draw/reset semantics; “disabled” differs explicitly from chance 0 with enabled guarantee; no draws/progress on inadmissible attempts |
| RWD-05 | Independent item/bundle families; Super/Duper switches/chances | At most one bundle, probability sum enforced, disabled probability remains no bundle; item+bundle coexist where configured |
| RWD-06 | Fill each pending slot independently; disabled item pending while bundle/currency enabled | Family backpressure visible and bounded; enabled families progress independently; no dropped earned identities or hidden infinite debt |
| RWD-07 | Generate → queue → present → deliver/settle/discard; redundant pending unlock; already owned equivalent physical item | Accepted lifecycle/reset policy; generation counted once; no guessed delivery from item count alone; no reroll/refund of redundant unlock |
| RWD-08 | Wallet near cap; native Junk routing; bundle conversion; free/full bag and trunk | Full-credit/source-retention policy or recorded pending income exact; no bundle consumed for partial credit, wrap, or hidden value loss |
| RWD-09 | Existing bundles in inventory/storage; enable Light/redemption through preview/Apply | Correct displayed value and accepted consent; no conversion during preview/setter; safe later sweep consumes each eligible source once |
| RWD-10 | Disable/re-enable/revalue redemption, move bundle between bag/trunk, repeated sweeps/reload | No second consumption/payment; inactive values retained; generation switch independent of conversion |
| RWD-11 | Counter/Items routes and unsupported income/redemption combinations; withdrawal with limited capacity | Accepted combinations explicit, unsupported Apply rejected atomically; wallet retained, only what fits withdrawn; no silent field changes |
| RWD-12 | Price transitions at each legacy difficulty and Bargain equip/unequip | Base policy persists as accepted; discount evaluated at request, not baked into save; return-to-Enhanced consequences visible |
| RWD-13 | Wayne next-gun/all hand-ins, full bag, failed craft, native Super/Duper results | Existing crafting/counter rules preserved; refund remains disabled by default; no new refund via preset |
| RWD-14 | Dismantle/Rebuild, Salvager equip/unequip, repeated rebuild/buyback/discard, save/load | Existing provenance and anti-refund protections retained; no replayed salvage credit or infinite-Junk route |
| RWD-15 | Reapply/toggle presets at guarantee/payment boundaries and reload saved progress | One engine per victory, frozen inactive progress, no reroll/reset/repeated fractional payout beyond legitimate restored-save semantics |
| RWD-16 | Invalid provider aggregate/technical ceiling; later drain pending after provider change | No partial generation/RNG/progress mutation on rejected attempt; previously committed final pending amounts remain unchanged |

For grant/credit events record source, award/phase identity, source consumption, wallet delta, pending delta, and unlock delta. A useful invariant is that a committed currency award exists exactly once as credited value or an explicit pending obligation; legitimately spent/withdrawn currency is accounted separately. Do not apply this new-path promise retroactively to unchanged legacy saturation behavior.

## 8. Mod compatibility and API cases

Minimum configuration matrix: suite off; Economy absent; Economy inactive; Economy only with zero external consumers; normal existing suite; one optional observer; one modifier; two modifiers in reversed registration order; provider preset; required consumer with missing dependency; supported maximum registrations. Include dependency-off/all-mods-off startup/restart. No exhaustive Cartesian-product claim: use targeted pairs plus named high-risk combinations and record coverage.

| Case | Setup/action | Required observable result |
| --- | --- | --- |
| MOD-01 | Capability absent/inactive/wrong major/missing required field/capability | Optional client degrades cleanly; required client refuses partial init; no blind pointer calls or speculative API availability |
| MOD-02 | Caller size/version boundaries, wrong phase/thread, spoofed owner, duplicate/colliding/overlong ID | Defined errors with no partial registration; canonical identity preserved, no truncation alias or stale callback |
| MOD-03 | Init readiness/seal, provider disabled/restart, failed partial init | Effective activity respected; borrowed contexts survive documented lifetime; cleanup/unwind leaves no registered dead owner |
| MOD-04 | Zero/one/two/max modifiers, reverse init order/equal priority | Deterministic accepted composition and diagnostic order; old host hook ordering unchanged |
| MOD-05 | Valid/invalid numeric fields, zero/negative aggregate, limits/overflow | Independent checked arithmetic agrees with PB-06; invalid contribution/aggregate handled exactly as accepted, without implicit activation or RNG mutation |
| MOD-06 | Observer generation/pending/credit/delivery phases, repeated delivery attempts | Observer sees completed coherent results; phase identities prevent counting one award twice; observer cannot veto or restart payment |
| MOD-07 | Provider preset register/select/disappear/reappear/change default/manual edit | No automatic Apply, stored concrete settings/key handled correctly, category-local Custom state, no overwritten progress |
| MOD-08 | Owned metadata versus borrowed callback/context, invalid lengths and capacity+1 | Copies/lifetimes respected; capacity error doesn't evict another provider or leak a partial descriptor |
| MOD-09 | Preview/query/logging repeatedly; observers/diagnostics disabled/enabled | Next gameplay RNG/result unaffected; no hidden effects leaked, no unbounded logging or event recursion |
| MOD-10 | Existing `junk`/Catalog/costume/Bestiary consumers, language on/off | Existing service contracts preserved; no new dependency on Economy for unrelated modules; supported labels/fallbacks valid |

Golden candidate vectors, only binding if PB-06 accepts D6 arithmetic: base 10 + addition 2 + factor 15,000 → 18; base 10 with two 15,000 factors → 20; base 1 with only Scavenger → successive credits 1 then 2 under fractional carry. Add zero, maxima, accumulated sub-unit, save/load halfway, and invalid aggregate cases. Do not use these examples to silently approve buff values or a stacking rule.

## 9. Race, ordering, reentrancy, and fault scheduling

For the first slice, callbacks are game-thread-only, init-only registration, and restart-only provider lifecycle. Test rejected illegal calls and stable operation snapshots; do not implement multithreaded gameplay mutation or hot unload just to exercise a future scenario.

| Case | Controlled schedule / fault | Required observable result |
| --- | --- | --- |
| RAC-01 | Queue/issue two purchases or source-consumption requests against one remaining balance/item | At execution owner revalidates; only affordable/available complete action succeeds; no double spend or negative balance |
| RAC-02 | Notification callback attempts nested grant/spend/install/same award | Unsafe reentry rejected; original commit coherent once; no recursive payment or infinite callback chain |
| RAC-03 | Request settings/registration/provider change between calculate/validate/commit/notify | Actual supported boundary/generation contract followed; no half-old/half-new calculation or mutated traversal |
| RAC-04 | Invalidate preview/request generation before execution | Stale request fails or is recomputed only before irreversible generation under accepted policy; completed rewards never rerolled |
| RAC-05 | Attempt registration during dispatch; observer disappears via supported shutdown/restart schedule | Rejected/deferred per supported lifecycle; no freed context dereference, duplicate row, or skipped active observer |
| RAC-06 | Interrupt normal save capture/config commit/reward mutation at each phase | Immutable coherent capture/generation rules; no callbacks during save/crash serialization; compare with SAV-12/13 |
| RAC-07 | Exhaust accepted pending/registration capacities; submission burst | Defined rejection/backpressure before side effects, bounded memory, no dropped accepted payment or endless same-frame drain |
| RAC-08 | Worker completion after scene/outfit/provider/save generation change, if affected existing asset integration is touched | Obsolete result released safely; render-safe publication/lifetime verified. Otherwise DEFERRED with no worker/hot-unload support claim |
| RAC-09 | Cross-owner install/payment preparation or allocation fails after preflight | Entire supported action remains coherent; no charged-but-uninstalled effect, unconsumed grant, or unsafe arbitrary rollback assumption |

Use deterministic barrier/callback injection schedules in local harnesses and then representative real integration. Label serial reentrancy tests separately from actual thread-race tests. Where supported use thread/heap instrumentation; unsupported race tools are a coverage limitation, not a pass. Never hold a shared lock while invoking arbitrary consumer code or waiting for I/O. A crashing/non-returning arbitrary native mod remains outside isolation guarantees.

## 10. Low-powered-machine performance plan

### Hardware and budget sheet — required before acceptance

| Field | Planned value / state |
| --- | --- |
| Representative low-powered CPU/core count, RAM, GPU, OS | Not selected; record actual machine rather than infer it from an older investigation |
| Supported resolution/renderer/frame-rate target/power mode | Not selected; same baseline/candidate settings |
| Allowed median/p95/p99 frame-time and worst-stall regression | Pending numeric agreement after baseline characterization |
| Empty-path and representative/max-provider dispatch CPU budget | Pending numeric agreement; report absolute and relative cost |
| Additional live/peak memory and resource/queue caps | Pending agreement; pin accepted D3/D6 capacities and instrumentation mode |
| Startup/registration/menu latency and queue/backlog budget | Pending numeric agreement |

Unselected hardware/budgets block a performance acceptance PASS. Baseline characterization may proceed later when authorized, labeled measurement-only. A fast desktop or a profiler-only build is not evidence for the low-powered release target. Do not change game settings/providers/rewards behind the player's back to satisfy timing.

| Case | Matched workload | Measure / acceptance |
| --- | --- | --- |
| PERF-01 | Baseline versus candidate; suite off and Legacy/no consumers | Empty-path CPU/frame-time overhead, allocations, memory; accepted budgets and exact unaffected results |
| PERF-02 | New engine, observer only, one/two/max supported contributors | Owner versus dispatch versus callback time, calls per event, no normal dispatch heap allocations where promised |
| PERF-03 | Maximum supported provider presets/labels and long menus | Init/sort cost, memory, navigation/scroll response; no per-frame full registry rediscovery |
| PERF-04 | Rapid actions, full pending slots, invalid repeated calls | Work/memory bounded, clear backpressure, no dropped state-changing operations or stall-generating diagnostic flood |
| PERF-05 | Diagnostics off/on; identical action/draw sequence | Instrumentation cost isolated, bounded history, identical gameplay outcome |
| PERF-06 | Real field/battle/Catalog/viewer session on selected low-powered machine | Mean/p95/p99 frame cost, worst stalls, asset/menu transitions; distinguish cold loading from steady state |
| PERF-07 | Few-core/low-memory workload where affected asset handoffs exist | Main-thread stall/resource peaks; otherwise deferred, not justification for new workers |

Suggested sampling protocol for approval: fixed 60-second warm-up, five alternating baseline/candidate runs of five minutes each for matched steady-state scenes, and separate cold-start runs. Record every run, not just the best. For event microbenchmarks collect at least 10,000 dispatch samples and report harness/timer overhead; exclude disk logging from the timed core while separately measuring real logging cost. This is a proposed workload, not an approved performance threshold or a simulated player session.

Use uninstrumented comparable release builds for player performance; sanitizer/profiler builds diagnose cost separately. Record thermal/power/background-load changes and repeat if noise obscures budget evaluation. Measure tail sample sufficiency and worst observed stalls; a good mean cannot hide periodic stalls. If no target hardware is available, leave PERF-06 blocked and document the release coverage decision explicitly.

## 11. Memory/resource lifetime and leak plan

Record counters by owner and resource class where feasible: live allocated bytes/blocks, high-water marks, model/texture references and actual render resources, file/OS handles, registrations/context references, pending payloads/job records, menu scratch, language caches, diagnostic history. Process working set alone is supporting evidence: allocator/driver retention and fragmentation must be distinguished from live unreachable growth.

| Case | Repeated workload / fault | Required observable result |
| --- | --- | --- |
| MEM-01 | Economy/menu/preview/Back/cancel and long-list opens | Session-owned storage returns to quiescent baseline; bounded cache growth stops after warm-up |
| MEM-02 | Catalog/Bestiary/Wardrobe viewing and model/outfit/language switching where affected | Old references/assets/pack buffers released only after readers/rendering finish; no stale strings, double-free or continuing asset growth |
| MEM-03 | Invalid/duplicate/capacity registration and failed mod init | Partial copied descriptors/refs unwound; no dead subscriber, registry growth, or assumption of normal shutdown after failed init |
| MEM-04 | Allocation failure at each supported staging step; corrupt/missing asset; request cancellation | Previous valid state intact; partial resources released once; error handling does not depend on a large successful allocation |
| MEM-05 | Repeated save/load/A↔B/New Game and pending delivery/full-cap cycles | Transient decode/snapshot buffers released; no growing retained copies or loss of persistent progress |
| MEM-06 | Supported restart/shutdown with pending work; stale worker completion if in scope | Ownership/cleanup order correct, no use-after-free/reference cycle or forgotten handles; do not test unsupported live unload as a feature |
| MEM-07 | Diagnostic spam/history and max-capacity registries/caches | Entry and byte limits enforced, histories/queues plateau, valid gameplay requests not silently lost |
| MEM-08 | Multi-provider low-memory soak and repeated action cycles | No unexplained continuing live-resource growth; peaks and retained capacities within accepted budget; all mutations still correct |

Proposed workload counts for approval: 100 warm-up menu cycles, then 1,000 measured open/preview/cancel/close cycles in ten batches; 100 save-switch cycles using disposable fixtures; 200 affected model/language swaps if in scope; a two-hour representative multi-provider soak with quiescent checkpoints every ten minutes. Per-phase allocation-failure cases run independently from timing measurements. Counts/duration may be revised and recorded before execution; they are not current test results.

At checkpoints wait for documented asynchronous/deferred cleanup boundaries without arbitrarily ignoring outstanding objects. Compare equivalent scene/menu/provider/cache states. Temporary/session counts must return to their allowed baseline; caches must plateau under declared entry/byte caps. Investigate trends per owner, including reference cycles; do not call growing pools “reused memory” without evidence.

Use available toolchain-supported heap/leak/address tools and resource counters on local diagnostic builds. Record tool name/version, enabled checks, known unsupported GPU/OS resources, exclusions, and false-positive disposition. Do not claim leak-free solely from clean exit or bounded process memory; retain the measured scope and duration in the result.

## 12. Playtest plan and balance review

Scope: evaluate D1's provisional Light Economy, Steady Income, and Treasure Hunter against unchanged Enhanced and counter-only play. No automatic tuning, code edits, or balance changes are authorized by observing a result. Run candidate amounts only after policy values are accepted for that playtest; otherwise mark it blocked.

| Case | Session | Record / evaluate |
| --- | --- | --- |
| PLAY-01 | Early ordinary encounters, normal inventory/shops, no equipment bonuses | Income sources, first useful purchase timing, menu comprehension, counter convenience versus vanilla scarcity |
| PLAY-02 | Midgame/boss stretch with stock/built-in equipment and no bonus providers | Ordinary/boss replacement, expense pace, useful upgrade decisions, unwanted currency/reward spikes |
| PLAY-03 | Late-game/EX sample, fuller inventories, larger wallet and existing bundles | Saturation/backpressure explanations, pending deliveries, indirect power from Tools/boosters/permits, missing-capacity friction |
| PLAY-04 | Scavenger/Lucky Find/charm and two sample providers, clearly separated from base runs | Effective-source summaries, fractional feel, guarantee interactions; do not attribute provider income to preset baseline |
| PLAY-05 | Nontechnical player picks counter-only/new preset, adjusts one value, returns to Enhanced | Understands Custom/engine state, existing-bundle conversion, inactive values, prices, Apply versus highlight; no debugging required |

For controlled comparisons use matched fresh fixture copies, route/encounter counts and investment, fixed new-path stream states where supported, and documented settings. Do not force all presets to have identical RNG draws if their algorithms intentionally differ. Report wins/losses/escapes/boss classification, attempts admitted/paused, source-specific Junk earned/spent, wallet/pending balances, item types/eligibility, bonus intervals, guarantee resets, conversions, shop/equipment modifiers, progression time, and player observations.

Suggested automated reward-frequency characterization, after authorization: at least three independent fixed stream initializations with 10,000 admitted victories each for stable configurations, plus separate real-play sessions. Compare exact model expectations where specified; statistical intervals are descriptive and should account for guarantee cycles/serial dependence rather than treating all guaranteed rewards as independent Bernoulli trials. Separate roll frequency from delivery delay/backpressure and equipment effects. A single rare drought is not automatically a failed 10% roll.

Treasure Hunter's 10%/tenth-victory mean of roughly 6.5 victories is a mathematical reference only under the stated no-modifier/no-backpressure policy. Enhanced's earlier estimates are not executable parity or playtest evidence. Final pacing targets and “feels worthwhile” thresholds remain discussion items. Record suggested revisions for the user; do not apply them.

## 13. Review traceability and deferred coverage

| Review | Primary case families |
| --- | --- |
| REV-01 | SAV-04/06/07/08/09; actual union/count/header tests |
| REV-02 | BAS-03, CTL-02/03/04, SAV-02/03, RWD-15 |
| REV-03 | RWD-08/11/13, SAV-02/09, RAC-01/09 |
| REV-04 | CTL-01/02, RWD-09/10, PLAY-05 |
| REV-05 | BAS-03, RWD-12, PLAY-05 |
| REV-06 | RWD-04/05/06/07/15, SAV-02/12 |
| REV-07 | MOD-01–08, RAC-02–05, PERF-01–04, MEM-03 |
| REV-08 | SAV-09/12/13/14, RAC-06/09 |
| REV-09 | SAV-01–06, CTL-03, RWD-03/04/15, MOD-09 |
| REV-10 | CTL-01/02, MOD-09, RAC-04 |
| REV-11 | Policy binding sheet, manifests, gates and result/sign-off below |
| REV-12 | MOD-10 and future coordinator design review; no coordinator implementation pass |

Future/deferred beyond the approved implementation slice: new Combat/Encounters/Movement APIs, hot unload, generalized worker queues, full menu reorder, pricing extensions, and actual Randomizer/overhaul activation. Third-party item/effect schemas and shops now have candidate contracts and planned cases in Section 15; acceptance/implementation remain pending, not implicitly delivered by A–D. For later coordinators add cross-owner activation, exclusive replacement conflict, deterministic plan/reachability, missing/mismatched manifests and seed/stream isolation cases. Current architectural consideration does not count as runtime support.

## 14. Result ledger, failure handling, and release criteria

Required per-case entry:

| Case / run | Policy + build | Expected / actual | Status | Evidence | Issue / disposition |
| --- | --- | --- | --- | --- | --- |
| SQ-20261031 / 21 local query cases | `feat/mod-presets-framework`, base `8c52cdde5`, uncommitted source hashes pinned in local manifest | Missing/loaded/upgraded/rejected/newer/opaque/damaged status; exact-fit/overflow, hypothetical replacements, registration/entry limits, hash collision, inactive/release-pending and repeated-query immutability | PASS for these source-level query assertions only | Local `runs/save-queries/results.json`, `manifest.json` | First-unit SAV-04–08/MOD subsets; broader policy and integration cases still open |
| SQ-20261031 / existing save fixture | Same; production `pe_save.c` with current private planner | Existing default/opaque/overflow modes retain their assertions | PASS, 3 fixture modes | Same results JSON | Standalone source-level fixture; no new tests added to game repo |
| SQ-20261031 / unchanged writer | Baseline source from `8c52cdde5` versus candidate; same deterministic fixture | 100 complete 8-KB card images identical byte for byte across write/load/off/new-game sequence | PASS | Local results digest and `tools/pe_save_pack_parity.c` | Verifies the exercised sequence, not every possible save or whole-game play |
| SQ-20261031 / native rebuild + existing CTest | RelWithDebInfo, PE_MODS=ON, QoL/Rebalance/Economy/Collection; Clang native build | Game and save/crash/inventory targets link; mod-crash-save-tail, mod-inventory, mod-save-records, mod-preserve-save-tail, mod-save-registration-bounds pass | PASS, 5 CTests | Local `native-build.log`, `ctest.log`, executable digest in manifest | Full unrelated suite not run; no game launch |
| SA-20261031 / capacity admission | Same branch/base, current uncommitted sources hashed in `admission-manifest.json` | 8 cases: exact fit, unchanged refused destination/carried state, retry, unavailable overflow snapshot, nesting/registration guard, late recheck, foreign passthrough, bad arguments | PASS for local owner-level assertions | Local `admission-results.json` | Preserves existing valid format/recovery behavior; not strict provenance gating |
| SA-20261031 / host and native gate | Actual `pe_mod_host.c` plus save host; separate real extracted native functions with surrounding stubs | Preflight skips hooks, late failure refuses, nesting guarded; native serializer stops before data/CRC/write scheduling, slot sequence/error routing and retry verified | PASS, 3 host cases + 1 native control-flow fixture | Local `admission-results.json`, `admission-host.log` | Native surrounding boundaries stubbed; no full-game UI or injected SDL disk-fault session |
| SA-20261031 / final regression and build | Final source/executable hashes in local admission manifest | 21 query cases + 3 existing fixture modes + 100 supported-save images still match; native game rebuilt; previous 5 CTests plus original-game-save-safety pass; no-mod native save-flow source compiles | PASS, 6 CTests plus scoped local checks | Local `results.json`, `admission-final-build.log`, `admission-ctest.log`, `admission-manifest.json` | Standalone no-mod source compile is not a complete vanilla game rebuild; no performance/leak certification |
| SE-20261031 / conditional emission | Same branch/base; final hashes in local `emission-manifest.json` | 25 cases: dormant/slot budgets, sticky enable/reset, exact/overflow admission, valid/absent/inactive/missing-owner/newer/rejected/upgraded records, invalid sizes/upgrades, uncertain sources, inactive New Game, release/save lifecycle guards, no reservation and bad arguments | PASS, source-level local assertions | Local `emission-results.json`, `tools/pe_save_emission_test.c`, `tools/run_save_emission.py` | Uses size-matched record stand-ins; no actual Economy policy/preset implementation. First run caught an idempotent enable bug after saving; fixed and final suite rerun |
| SE-20261031 / final regression and rebuild | Final source/executable hashes in local emission manifest; RelWithDebInfo, PE_MODS=ON | 21 query + 12 admission/host/native-gate cases rerun; 3 existing fixture modes; 100 supported card images byte-identical to base; native game rebuilt; 6 existing CTests pass | PASS for these checks | Local `results.json`, `admission-results.json`, `emission-build.log`, `emission-ctest.log`, `emission-manifest.json` | No full UI/disk-fault playthrough, low-powered performance measurement or memory-leak soak; native gate boundaries remain stubbed |
| Remaining plan / 83 primary cases | Final policy bindings/target hardware still pending | Full behavioral validation/playtest expectations above | PLANNED/BLOCKED as applicable; not claimed passed | Future run-specific records required | Host refusal/conditional emission now have scoped results; actual policy semantics, coherent crash image, presets/APIs, performance and leak soak remain outstanding |

Record steps sufficient to reproduce a failure, preserve the disposable failing fixture/log, and distinguish contract bug, implementation bug, harness issue, environment noise, or unsupported scope. Do not edit expected values solely to turn a failure green. After a fix, rerun affected cases and necessary neighboring regressions; repeated full-suite runs need a reason. Optional diagnostics/tool changes must be reflected in the manifest.

Release readiness requires: accepted applicable policy bindings; verified implementation baseline and save-host prerequisites; PASS for mandatory save/data-loss/transaction/API/default-parity cases; resolved unexplained corruption, duplication, deadlock, dangling-reference, and continuing leak failures; matched low-powered measurements within accepted budgets; UI/playtest findings reviewed; known limits and deferred modules explicit. Blocked required hardware/cases require an explicit scope/coverage decision, not a fabricated PASS. No claim of safety for arbitrary native callbacks or arbitrary older builds.

Aggregate report fields: mandatory PASS/FAIL/BLOCKED/INCONCLUSIVE counts, deferred/not-applicable counts with reasons, build/commit, actual policy revisions, target hardware, duration/sample counts, capacity/leak/performance limits, open issues, and local evidence location. Summaries may update D0/D1/D7 or a PR; the suite and raw artifacts remain local. Only executed, scoped results above are passes; planned cases require their own evidence.

Original October 30 task completed planning only. October 31 follow-ups implement queries, checked capacity refusal and conditional emission, with all new fixtures/runners local under `pe-native-debug/tools` and raw evidence under `runs/save-queries`. No user saves were edited and no interactive game/playtest was launched. The raw legacy selection plan still reports would-be omissions, but normal writes and crash-tail snapshots now refuse such a plan instead of publishing it. Supported fitting outputs remain unchanged. Existing damaged-record recovery and whole newer-container passthrough remain compatible; conservative conditional activation gating is implemented, but actual policy semantics/registration and coherent whole-native-plus-mod crash capture remain unimplemented. Evidence above is not full-plan, low-powered-machine, leak-soak, disk-power-loss, or crash-atomicity certification.

## 15. Custom content, equipment effects and contributed shop validation

Added October 31 as a documentation-only plan. Bind PB-10–14 and select actual E/F/G delivery scope before execution. **All 36 cases below are PLANNED, not PASS.** No new fixture, test code, build or user-save write was performed for this extension. Run only separately authorized implementation tests; all future fixtures/example providers/fault injectors/raw results remain local in `D:/Recomp Games/pe-native-debug` with no remote publication.

Review disposition: D6 §11 now binds MCR-01–03 registration, ownership and dependency semantics; the acceptance bindings below make those outcomes explicit. Later October 31, D3 §11 and D6 §12 resolve MCR-04/05/10 at design level (ledger encoding/capacity, native mapping authority, content core and compatibility states); their bindings follow the MCR-01–03 table. MCR-04X (D3 §12) and MCR-06 (D3 §13, D6 §14) follow, with their own binding tables. MCR-07–09, 11 and 12 remain open, including stock revision/units, authoritative purchase tokens/quotes and the complete measured scale matrix. No new case count or test pass is claimed; the original 36 cases remain planned. D0 Section 5 M and D7 distinguish design disposition from implementation evidence.

### MCR-01–03 acceptance bindings — recommended contract, unrun

PB-10/14 use D6 §11's full-key identity, atomic batches, domain quotas and phased graph/readiness rules; PB-13 uses its cross-owner reference/shop-admission permissions only. They do not bind stock/price/commit behavior still open elsewhere. The following extend the existing case definitions, not add executed cases or test code:

| Existing cases | Bound expected outcome / additional setup |
| --- | --- |
| CNT-04, SHP-01 | Required batch containing two same-domain authenticated duplicate claims fails in full; all competing valid batches fail, independent of order. No resurrection after another failure. Unauthorized B claiming A's namespace fails ownership without poisoning A. Compare canonical ready IDs and attributed refusals, not incidental receipt numbers |
| CNT-04, RES-04 | One owner with many entries, many owners with one, count versus text/descriptor-byte boundaries and within-owner order permutations. Per-owner/domain overflow rejects that owner's domain contribution; whole-domain overflow makes that capability unavailable, with no first-N subset or borrowing. Shop-only overflow leaves independent Content ready. Above 32 declared owners refuses the new generation; metadata must stay within fixed staging/publication ceilings |
| CNT-04, SHP-02, RES-03 | Whole required batch publishes or fails; failed optional shop batch does not remove a base definition. Partial init/staging failure releases registry-owned copies and never leaves published callbacks to failed contexts. Wrong-phase/duplicate resubmission cannot manufacture a valid winner |
| SHP-01/02, EFX-01/03, RES-01 | B offers A's content only with content opt-in and shop admission; target/effect policies both authorize foreign effects. Deny foreign definition replacement, unadmitted stock reference or unspecified extension point; retain separately framed A/B attachment bytes when one owner is missing |
| CNT-04/12, SHP-02 | Compatible staged forward/passive-cycle references resolve with no recursive callbacks. Required service-init, hard evaluation and required-batch cycles reject affected integrations; missing required references propagate to fixed point. Missing Economy disables only optional adapter batches; required unsupported runtime still refuses readiness |
| SHP-02, RES-03/04 | Receipt is not ready during collect; no gameplay/query side effects or live entry publication before seal. Publish a complete stable generation after all eligible init; late registration/nested seal refuses. Restart invalidates receipts/handles, cleans transient resources and preserves stable saved IDs |

No runtime suite was added or executed for these bindings. Public C layouts and byte accounting/native host phase support still need implementation under a separate instruction. Measure technical-profile limits on the target machine before release rather than treating the specified 512 KiB logical / 1 MiB publication ceiling as observed usage. MCR-12 retains broader many-provider coverage beyond these bindings.

### MCR-04/05/10 acceptance bindings — recommended contract, unrun

D3 §11 (ledger v1 encoding, P0/P1 profiles, single admission authority, compatibility states, outer load gate) and D6 §12 (mapping by pool index + fingerprint, supported classes, lifecycle, native veto hooks, content core) bind these cases. Persistent custom instances are blocked on the storage-expansion gate MCR-04X, so every case that grants a persistent custom item is **BLOCKED** until that proposal is accepted and implemented; pure parse/accounting checks may run earlier against a fixture ledger. The rows extend existing case definitions; no case or test code is added.

| Existing cases | Bound expected outcome / additional setup |
| --- | --- |
| CNT-01 | Zero custom instances: the ledger is never emitted; native save and existing tail byte-identical to the current baseline, including with providers registered and the content core present |
| CNT-02, CNT-03 | Custom weapon and armor are complete native pool records (native archetype, kind and ranges). Two instances of one definition with different ammo/bonus stats/attachments get distinct `instance_id`s and never merge or stack. Sort bag and storage, move bag ↔ storage, equip/unequip, battle and save/load: ledger bytes unchanged except `native_stamp`; pool indices unchanged; equipped references re-found by value |
| CNT-05 | Provider missing: entries UNAVAILABLE, record usable as its archetype; discard, sell, dismantle, rebuild and tune-up merge refused with slot, record, equipped state and ledger unchanged. Repeat with Economy off and with All mods off: same native behavior, ledger preserved byte-for-byte |
| CNT-06 | Compatible reinstall after a missing-provider round trip: each entry returns to ACTIVE once; no grant, reroll, new `instance_id` or duplicate record |
| CNT-07 | Missing provider while the item is equipped: stays equipped as its archetype; no substitution, unequip or duplicate fallback copy |
| CNT-10 | Fixture ledgers with duplicate `instance_id`, duplicate or out-of-range pool index, count/length beyond bounds, attachment payload over 32 bytes, frame to a missing instance, newer `format`, `min_reader` above the core: bounded parse, no out-of-bounds read, outer load gate refuses continuing with an attributable message, file untouched |
| CNT-11 | Projections use declared maxima (51-byte dictionary entries) and count carried unknown records and outstanding reservations. Two staged acquisitions competing for the last bytes: exactly one reservation succeeds; the other refuses with `CAPACITY` before charge/consumption. Ledger above this build's profile: kept whole, extra entries UNAVAILABLE, growth refused, nothing dropped. Record P0/P1 measured sizes against D3 §11.3 |
| CNT-12 | Save switch and New Game: no instance handle or reservation survives; ledger cleared only by New Game or loading a save without it; `instance_id` never reused within a save and never wraps |
| EFX-04, EFX-05 | Attachment frames of a missing owner retained byte-for-byte with their slot; reinstall resolves once; repeated save/load/equip does not grow the ledger or compound bonuses |
| EFX-08 | Dismantle/Rebuild/tune-up/discard of custom records go only through supported core destroy/merge actions or refuse; every native record-freeing path in D6 §12.4 is vetoed for custom records, and a vetoed path leaves no side effect |
| RES-01 | Save editor and older mod build mutate the pool without the core: next supporting load sees a `native_stamp` mismatch; a matching fingerprint gives UNCERTAIN, a freed or changed record ORPHANED; no reattachment to another record, no regrant. Include "old build discards gun A, a native gun of the same type takes the same pool record" |
| RES-02 | Reader matrix: current core, lower core revision (read-only preservation), newer `format` (gate refusal), vanilla build (ledger lost at next save; native items intact and playable). No downgrade-success claim |

Open before running: the D6 §12.4 audit items (fingerprint field immutability, carry-over reset meaning, every retail record-freeing site) and the MCR-04X proposal. No runtime suite was added or executed for these bindings.

### MCR-04X acceptance bindings — recommended contract, unrun

D3 §12 (save extension store) and D6 §13 (section service) bind these. They extend existing cases; no case or test code is added. All use disposable copies of cards in isolated configuration roots.

| Existing cases | Bound expected outcome / additional setup |
| --- | --- |
| CNT-01 | No active section: no link record, no `.pe-ext` file; card bytes identical to the current baseline. Card slot count and listing unchanged with a populated `.pe-ext` folder present |
| CNT-11, RES-04 | Section at, one under and one over its maximum; total at the 5 KiB profile (D3 §13.2); registration that would exceed the profile refused at init. Over-maximum serialization refuses the whole save with no file written and the old card and extension unchanged |
| SHP-10, RES-03 | Inject failure or kill at each write step (extension temp, extension rename, card temp, card rename, cleanup). After restart the card always links to an existing matching generation, or to none if it never had one; leftover files are cleaned only by the next save to that card name |
| RES-01 | Copy only the card file: without *required*, the save loads with sections absent and the next save drops the link; with *required*, the gate prompt appears, Back changes nothing, Continue loads plain native items and leaves files untouched until saving. Save editor rewrite of the card: the link stays valid or the same handling applies |
| RES-02 | Wrong generation, wrong card name, truncated or oversized file, bad header CRC, one bad section CRC (only that owner affected), unknown and newer sections (carried byte-for-byte), smaller profile than the file (kept whole, growth refused), vanilla save over a linked card (orphan cleaned by the next supporting save) |
| CNT-12 | Clear-data save under a new name retires the old name's extension generations only after the new card is published; save to a different slot writes that slot's own extension; New Game clears activation |

The crash-report companion dump and the editor bundle export are follow-up checks once those tools change.

### MCR-06 acceptance bindings — recommended contract, unrun

D6 §14 (facts, transitions, identity, spoiler rules) and D3 §13 (`pe_economy.discovery` encoding and capacity) bind these. They extend existing cases; no case or test code is added. Native Catalog behavior and the `pe_economy.catalog` v1 record must stay byte-identical in every row.

| Existing cases | Bound expected outcome / additional setup |
| --- | --- |
| EFX-06 | Undiscovered custom effect: `????` row; help, quote, price, refusal and log text (non-debug) never contain its name, icon or description; query returns `UNDISCOVERED`. Carrying gear with it shows it as seen without saving anything; acquiring it latches Seen. Seen-but-locked shows name + locked. English and Spanish; long mixed native/custom lists scroll independently |
| EFX-03, EFX-08 | Removing an installed custom effect keeps Unlocked. Dismantling gear carrying it sets Seen + Unlocked exactly once; repeated dismantle/rebuild loops add no extra unlocks or Junk beyond existing rules |
| SHP-01, SHP-04 | Two offers (same or different providers) referencing one entry: buying either sets the same fact; the other then shows grayed as owned and refuses purchase with no charge |
| SHP-03 | Browse/inspect/quote/cancel of undiscovered and seen entries changes no fact and writes no section |
| SHP-11 | Unlock purchased, provider removed, save, reinstall: still Unlocked; offer still shows owned; no repurchase or reset |
| CNT-04 | Duplicate ordinal within an owner rejected at seal; reverse provider order gives identical saved bytes for identical facts; rename with `accepts_previous_keys` keeps facts and rewrites the guard at the next save; `absorbs_ordinals` ORs facts and drops the retired entry; a guard mismatch without acceptance is carried, not applied, and logged |
| CNT-05, CNT-06, RES-01 | Provider missing: Seen entries show "unavailable (mod missing)" with the namespace only; undiscovered entries not listed; section bytes carried unchanged through saves with the provider, then Economy, then all mods off; reinstall restores display with no grant |
| CNT-10, RES-02 | Damaged section (duplicate namespace/ordinal, bad counts, Unlocked without Seen): bytes kept, notice shown, new transitions refused, nothing rewritten. Reserved fact bits from a newer build survive a save |
| CNT-11, RES-04 | Seal with registrations at, under and over 1,024 bytes: overflowing owner's whole Catalog batch refused deterministically. Save with large carried groups leaves too little room: discovery read-only for the owners that do not fit, with a notice; existing facts still display |
| CNT-12 | New Game clears custom discovery and native unlocks together; loading a save without the section clears it; debug unlock-all sets the `debug` flag |

No runtime suite was added or executed for these bindings.

### Mod on/off bindings — recommended contract, unrun

D3 §14 binds these. Layer S rows need no custom content and can run as soon as S is implemented, using today's records (loot, Catalog, keys, sort, policy). The rows extend existing cases; no case or test code is added.

| Existing cases | Layer | Bound expected outcome / additional setup |
| --- | --- | --- |
| CNT-01 | S, C | All mods off, saves with no mod data: no notice, no warning, no Custom items page; card bytes and game behavior unchanged. With a ledger-free save, the content core registers no hooks (verify by hook registry/log) |
| CNT-05 | S | Save with QoL key-pocket data loaded with QoL off: notice lists QoL once at the first safe field frame (not during a cutscene or battle); data carried unchanged on save. Notice option off: no dialog. Five missing owners: four named + "and 1 more" |
| CNT-05, SHP-10 | S | Overwriting an existing slot with missing-owner data: warning appears; New slot returns to the list with nothing written; Cancel writes nothing; Overwrite saves normally and does not warn again for that slot until the next load. Empty slot: no warning. Option off: no warning. Native save never blocked or delayed on refusal paths |
| CNT-05, CNT-07 | C | All mods off with a custom-item save: veto hooks active; items usable and equippable as archetypes; discard/sell/dismantle/rebuild/tune-up refused; Custom items page lists them as "mod off" |
| CNT-06, RES-01 | C | Convert one UNAVAILABLE item: confirm defaults to No; Yes removes only that entry and its attachments; the native record, other entries and discovery are unchanged; re-enabling the provider does not restore it. Convert is not offered for ACTIVE items, in battle or in cutscenes. Remove record works only for ORPHANED entries. After converting all of an owner's items with no other data, the notice stops listing that owner |
| RES-02 | S | Unreadable or newer data for any owner (not only the ledger) reaches the outer load gate with an attributable message and an untouched file |

Tester guidance (D3 §14.6) is checked as documentation review, not a runtime case.

### Versioning and migration bindings — recommended contract, unrun

D3 §15 binds these. They extend existing cases; no case or test code is added. The fixtures are synthetic and stay local in `pe-native-debug`.

| Existing cases | Bound expected outcome / additional setup |
| --- | --- |
| CNT-09 | Every golden fixture from v0 (legacy blocks) or v1 upgrades through the chain to the current version and matches expected state. Running the chain twice gives the same result. A failing step resets that owner only, preserves its original bytes where the store supports it, and leaves other owners untouched |
| CNT-09, RES-02 | A section with a higher `version` but `min_reader` ≤ the reader: known prefix used, trailing bytes and unknown flag bits written back unchanged. `min_reader` above the reader: preserved whole; owner dormant, or the gate if *required*. Tail record with a newer version: preserved, mod at defaults (current behavior unchanged) |
| CNT-06, EFX-05 | Definition revision N → N+1 with a declared per-instance step: each instance migrated exactly once and the dictionary revision updated. Without a step, existing items unchanged. Attachment of an unknown or newer schema preserved, not run |
| CNT-05, SHP-10 | Saving after a `min_reader` raise or tail version raise shows the format-upgrade warning once per slot (New slot / Overwrite / Cancel); a save with no such change shows none |
| RES-01 | F1 save diagnostics page lists every record and section with version, `min_reader`, state (current / upgraded / newer-kept / reset) and last writer; the load log records each upgrade |
| — (process) | Review check for every layout change: version table row updated, step added, fixture added, older steps unchanged (diff check) |

### Manifest and independent fixtures

Extend Section 4's manifest with accepted D2/D3/D6 revisions, implementation commit/dirty hashes, capability/schema/container versions, provider order/dependencies, supported archetypes/actions and limits, offer pricing/stock scope, quote policy, equipped fallback policy, identity encoding and transaction/save publication guarantee. Record tool versions, actual adapter paths, UI language/input, asset availability and disposable resolved save/profile locations. Preserve old fixtures independently; installed providers must not be needed simply to decode the test manifest's expected opaque bytes.

Plan two independent synthetic providers A/B with distinct namespaced definitions and optional Economy/Catalog adapters. Cover one native-compatible item, weapon and armor; native and custom effects; built-in/removable effects; unknown opaque payload; duplicate/colliding/overlong IDs; unsupported schema and invalid reference/lengths; missing required runtime capability; missing icon/model; and safe versus progression-critical equipment. Include distinct instances of one definition with different upgrades/ammunition/effects, distinct offers with shared versus separate declared stock, old saves, genuinely absent custom records, and full/near-full carried records. Use developer-owned synthetic assets/content; no redistribution of private saves or disc assets.

Define independent expected logical inventories, attachments, wallet, stock and byte payloads before running. Serializer tests compare preserved original bytes where promised; valid migrations compare intended semantic fields and repeat behavior. Operation tests inspect all owners and the emitted file/snapshot, not just success text. Separate pure/mocked contract checks from actual native inventory/combat/equipment/UI/file integration. A stubbed prepare/commit success does not prove the real native action can commit safely.

### Content and compatibility cases — 12

| Case | Setup / action | Required observable result |
| --- | --- | --- |
| CNT-01 | Old vanilla/current-record saves and zero content providers | Existing native ownership, defaults and fitting output preserved; no unused custom record or registry-grant side effect |
| CNT-02 | A's item, weapon and armor using each accepted action without Economy | Supported native-compatible behavior and inventory/storage/equip paths work independently; unsupported actions refuse before mutation |
| CNT-03 | Two instances of one definition with distinct stats/ammo/charges/effects | Save/load/transfer preserve identity and mutable differences; no reconstruction from current defaults or reference aliasing |
| CNT-04 | Reverse A/B registration; duplicate/overlong IDs, alias cycle/collision | Stable resolution and attributable rejection; no silent truncation, overwrite or order-dependent ownership |
| CNT-05 | Missing/disabled provider with item in bag/trunk | Read-only placeholder retains logical capacity, quantity and opaque bytes; unsafe operations blocked; no free quarantine/eviction |
| CNT-06 | Compatible reinstall after missing-provider save round trip | Exact owned content resolves once with upgrades/effects and no grants, rerolls, charges or duplicated instances |
| CNT-07 | Missing equipped definition/required runtime | Accepted fallback/refusal policy; no unknown native index, duplicate owned fallback or loss of original; later player equipment choice respected |
| CNT-08 | Missing icon/text/model versus missing gameplay capability | Approved presentation fallback only where safe; required runtime/model constraints refuse action/resume as bound, without deleting state |
| CNT-09 | Newer/rejected provider schema; valid and failed/repeated migrations | Original framed data retained on failure; successful migration is validated and repeat-safe, with no compounded stats |
| CNT-10 | Invalid sizes/counts/references, duplicate instance IDs and cyclic aliases | Bounded parse/validation and attributable refusal; no out-of-bounds access, unsafe callback or partial published inventory |
| CNT-11 | Near/exact/over capacity with unknown carried state; acquisition growth | Whole result admitted or refused before charge/grant/consumption; unknown records unchanged; no silent omission or assumed dynamic reservation |
| CNT-12 | Save switching/New Game, missing progression/coordinator dependency | No stale instance handles, cross-save leak or stock carryover beyond accepted scope; required missing dependency blocks resume without partial plan |

### Equipment effect and Catalog cases — 8

| Case | Setup / action | Required observable result |
| --- | --- | --- |
| EFX-01 | Native/custom equipment with native and A/B effects | Applicable runtime behavior through reviewed adapters; existing native meanings unchanged and no bit/index collision |
| EFX-02 | Duplicate/stacking/exclusive effects; reverse registration | Accepted deterministic algebra/conflict result; duplicates/exclusions refuse installation without consuming resources |
| EFX-03 | Boundary slots/costs, built-in and removable effects | Bound slot rules and provenance retained; built-in/unknown attachments cannot be removed/overwritten through an ordinary install action |
| EFX-04 | Missing/newer provider effect on otherwise native gear | Preserve effect ID, occupied slot, parameters and opaque data; no execution or unrelated native substitution; accepted safe inactive/fallback/refusal policy |
| EFX-05 | Reinstall/migrate effect and repeat save/load/equip | Resolution once; no extra charge, multiplied stat bonus, slot loss or lost native upgrades |
| EFX-06 | Discovered/undiscovered effects, missing discovered provider, English/Spanish, long lists | Correct weapon/armor selection, icons/fallbacks and independent scrolling; `????` hides undiscovered details; no leak through help/quote/errors |
| EFX-07 | Target moved/changed between preview and install/remove/transfer; resource/save failure | Stale request refused/requoted; target, item consumption, installed state, payment and provenance remain coherent |
| EFX-08 | Repeated equip/remove/transfer/Dismantle/Rebuild with salvage/refunds | Existing anti-exploit rules retained; no duplicated effect/item/Junk or new refund policy caused by registration |

### Shop and transaction cases — 12

| Case | Setup / action | Required observable result |
| --- | --- | --- |
| SHP-01 | Two providers, distinct offers for one item, deliberate duplicate offer ID | Deterministic valid offers; duplicate rejected with owner; shared stock only when explicitly declared |
| SHP-02 | Missing Economy/required delivery service, restart/all-off and failed init | Optional integration skips; required readiness refuses and unwinds partial resources; definitions can remain independently usable |
| SHP-03 | Repeated browse/inspect/quote/cancel | Wallet, inventory, stock, RNG, discovery and emitted records unchanged; no reservation leak or hidden ownership |
| SHP-04 | Valid purchase, zero-price purchase and maximum accepted quantity | One coherent item/equipment grant, exact displayed payment and stock update; free offer still enforces eligibility/capacity/dedup |
| SHP-05 | Insufficient funds, full inventory/trunk, stock or persistent-capacity exhaustion | No payment/consumption/partial delivery or lost stock; structured reason agrees with actual blocking owner |
| SHP-06 | Price/modifier/quantity/stock/provider/target change after quote | Bound generation/expiry rejection and refreshed explicit confirmation; no changed-price silent purchase |
| SHP-07 | Competing wallet spends, inventory use/move and shop requests | Controlled interleavings yield only valid complete operations; no overspend/overfill or reused reservation |
| SHP-08 | Repeat operation token, nested request and notification-triggered replay | One supported commit; duplicates/reentry refused/deduplicated per playthrough contract; no repeated grant/charge |
| SHP-09 | Cancel/failure at each preparation step or provider readiness change | All reservations released; previous valid gameplay state retained; unsupported native partial-commit adapter blocks availability |
| SHP-10 | Save/crash/file failure before/during/after commit and publication | Within accepted guarantee, recover a complete old or new generation, never item/payment/stock hybrid; no invented cross-crash exactly-once claim |
| SHP-11 | Limited/one-time stock across save/load/missing provider/reinstall | Stock/claim identity retained; no reset/rebuy exploit. Independent saves follow declared scope; rollback to old save is not global anti-cheat |
| SHP-12 | Equipment sale versus effect consumable versus installation service | Only explicitly supported typed actions offered; target/slot/discovery/consumption validated; no service masquerading as ordinary delivery or Wardrobe buying |

### Tools and resource cases — 4

| Case | Setup / action | Required observable result |
| --- | --- | --- |
| RES-01 | Editor/export/recovery round trips without A/B, then compatible reader | Unknown IDs, payloads, attachments and stock retained within supported framing; no installed provider execution needed for opaque preservation |
| RES-02 | Supported old/new reader matrix and any accepted expanded format | Explicit detection/refusal/migration and recoverable original; no unsupported downgrade-success claim or silently truncated conversion |
| RES-03 | Repeated views/quotes/cancel/save switches/provider restart; allocation failure/shutdown | Registry/quote/reservation/cache/asset counts obey bounds and return to accepted baselines; no double release, stale reference or continuing live growth |
| RES-04 | Zero/representative/maximum providers and offers on accepted low-powered target | Mean/tail menu/action/frame cost, bounded lookup/dispatch, memory peaks and cleanup meet PB-14 budgets; no per-frame discovery/disk access or skipped rules |

### Scheduling, evidence and acceptance

For SHP-06–10 and EFX-07, inject changes at quote, each owner prepare, final revalidation, commit, notification and save-image publication boundaries. Verify observers cannot see half a committed state or mutate the same operation synchronously. Test native and mod save segments together where coherence is claimed; current isolated tail tests cannot discharge SHP-10. If no safe image/publication mechanism or native commit adapter exists, mark the case BLOCKED and action unsupported rather than claiming a pass using a mock. Distinguish a permitted stale coherent crash image from an inconsistent fresh hybrid.

Use Sections 10–11 budgets, workloads and tools only after PB-14 binds them to actual content scope/hardware. Include English/Spanish help and long effect lists, input backtracking and player comprehension of unavailable content. Do not change balance/prices/refunds based on test observations without review.

Traceability: CONTENT-01/02 → CNT-02/04/10 and RES-04; CONTENT-03/04 → CNT-01/03/09/11 and RES-01/02; CONTENT-05/06 → CNT-05–09/12 and RES-01/02; EFFECT-01–04 → EFX-01–08; SHOP-01–04 → SHP-01–12; shared lifecycle/resource gates → RES-03/04 and SHP-02/09. Record each case's policy bindings, run manifest, expected/actual results, local evidence and limitation in a separate extension result ledger; leave all entries PLANNED/BLOCKED until executed.

Release criteria for an accepted E/F/G slice require its applicable bindings approved, relevant mandatory cases executed, data-loss/duplication/unsafe-execution failures resolved, real native adapter/save coverage, and agreed resource/performance measurements. Installation services may remain unavailable if only item delivery is verified. The original 83-case plan, this 36-case extension and historical host-unit counts are separate totals; do not add them into a misleading pass count. No implementation, build or test execution accompanies this document update.

## 16. Standalone Wardrobe, Bestiary and Economy extraction validation

November 1 documentation-only extension: **24 additional STN cases, all PLANNED/unrun**. They are separate from the original 83 and custom-content 36 cases and do not change historical host-unit results. Bind PB-15–18 to D2 §10, D3 §16 and D6 §15, with D8 pack tests/D9 boundaries. MCR-08/09 remain open; a new cross-store paid adapter cannot be certified using a successful stub or a single-file save test.

Review follow-up: D9 §7 records **SPL-01–09 OPEN** and maps required acceptance extensions to the existing STN cases. Before execution, bind policy outcomes for acquisition transitions, missing migration receipts, actual writer/alias/v1 contracts, legacy purchase paths, feature-scoped adapters, concurrent profile edits and shared resource ownership. Later pack cases also need admission/key/version alignment. These review coverage notes add no executed cases or pass count; the original 24 STN IDs remain planned. D0 Section 5 R tracks the gaps.

Manifest additions: exact game commit/source hashes and module list, compiled-out versus disabled feature status, actual service publishers/versions, profile/settings migration source/destination/markers and checksums, wallet record owner, selected acquisition adapter, explicit acquisition/default policy, load slot/profile identity, cross-store protocol revision and measured resource budgets. Do not launch against a user's real preferences; use isolated disposable card/profile directories and preserved originals. Future fixture code, tools, providers, logs and screenshots stay local in `D:/Recomp Games/pe-native-debug`; none is created by this document update.

| Case | Setup / action | Required observable result |
| --- | --- | --- |
| STN-01 | Build/run Wardrobe with Bestiary and Economy omitted | No missing symbols/services; supported packs, preview and eligible wearing work; no prices or automatic owned grants |
| STN-02 | Build/run Bestiary with Wardrobe and Economy omitted | Creature registration, encounters/kills and earned reveals work; no outfit/profile dependency or free paid reveals |
| STN-03 | Both features without Economy, then Economy without either feature | Each initializes only supported capabilities; native packs register their own subsets exactly once; Enhanced baseline unchanged |
| STN-04 | All features; one disabled at a time; all mods off; legacy aggregate plus explicit module lists | No duplicate publishers/entries; documented core behavior retained; absent build and disabled runtime are distinguished; no double alias expansion |
| STN-05 | Legacy mixed profile with both valid subsets and unknown/missing-pack keys | First import creates independent valid feature destinations; source unchanged, progress/ownership exact and markers committed with data |
| STN-06 | Fault before/during/after each staged profile import | Valid original/destination recoverable, failed import not marked successful; one feature's import retry cannot erase the other |
| STN-07 | Valid destination already exists; old source gains later records; reset/lock and restart | Destination remains authoritative; no repeated merge or reset resurrection; explicit import marker survives owner-local reset |
| STN-08 | Malformed/newer destination, legacy binary source, source absent | Accepted precedence/recovery behavior, unknown data preserved; no silent overwrite via re-import/default creation |
| STN-09 | Canonical settings present versus absent, old Collection on/off and All mods off | Canonical choices win; legacy fallback imports once only; unrelated INI lines/defaults and explicit off remain intact |
| STN-10 | Wardrobe off/missing worn pack, Bestiary active, then reverse | Native appearance/session fallback as supported; saved worn key/ownership retained; no changed Bestiary facts or invented retroactive kills |
| STN-11 | Wardrobe Everything/Shop choices, missing/reappearing adapter and restart | Temporary availability distinct from owned set; explicit stored choice unchanged; no toggle-based permanent grant or payment |
| STN-12 | Bestiary encounters/earned thresholds with payment adapter absent/present | Same baseline earned progress/reveal rules; payment absence blocks only paid research; no inherited all-unlocked Wardrobe behavior |
| STN-13 | Wallet/counter routing with enhanced rewards off and on | One balance and record owner; no extra income when off, lost reward progress, duplicate serializer or automatic inventory conversion |
| STN-14 | Catalog/shop independent supported combinations and missing payment | Retain existing discovery, eligibility and stock; paid actions unavailable rather than free; no Wardrobe/Bestiary requirement |
| STN-15 | Existing v1 costumes/wardrobe/bestiary/junk consumers after extraction | Audited meanings/price expectations retained or explicit unsupported result; no reinterpretation of numeric costume price or enabled state |
| STN-16 | Two acquisition adapters, reversed registration, explicit selected adapter | Canonical ready entries; explicit compatible selection wins, no last-registration winner; conflicting defaults need selection |
| STN-17 | Unauthorized grant/direct profile edit request, discovery-hidden target | Feature owner rejects unsupported caller/action without state or spoiler leak; authorized reward/debug paths remain separately scoped |
| STN-18 | Adapter/price/profile/playthrough/target changes after preview | Stale quote/reservation rejected and refreshed confirmation required; transient handles cannot cross generations |
| STN-19 | Preparing/cancelling/failing optional paid action | Wallet/stock/profile unchanged; every reservation released; unsupported cross-store protocol keeps new action unavailable |
| STN-20 | Fault each durable publication/recovery phase for per-save Junk plus profile entitlement | Accepted protocol restores coherent entitled/payment outcome; no lost spend, unpaid grant or duplicate retry. BLOCKED until actual MCR-08/09 protocol exists |
| STN-21 | Profile write refusal, disk/file failure, crash/restart and old-save restoration | Scope-specific recovery/diagnostic matches PB-18; no false committed success, automatic replay charge or unclaimed global anti-rollback guarantee |
| STN-22 | Mixed legacy wallet/reward/Catalog/Rebuild records with feature absent | One compatibility writer preserves inactive fields/keys and unknown sections; module names do not cause layout/key changes or resets |
| STN-23 | Repeated independent debug reset/import/restart, missing packs, feature/view/adapter cycles | Reset stays owner-local, unknown ownership/progress retained; temporary resources/callbacks/quotes clean up under declared bounds |
| STN-24 | Zero/one/both viewers, reward-only and representative adapters on target machine | Existing no-provider/frame behavior preserved; measured startup/menu/action costs and live/peak resources meet PB-18, no duplicate asset caches or forced unrelated module load |

Use independent before/after logical snapshots of both profiles, native/mod card records, wallet, stock and emitted bytes as applicable. STN-20/21 need real durable-store/error-path integration; mocks only prove local call ordering. Profile-wide unlocks intentionally persist across different save slots, so tests must distinguish that declared scope from a double-grant bug. Restoring an old save is not prevented globally by playthrough dedup.

Run English/Spanish long-list/controller/menu-back checks for touched views and explain missing adapter/migration/refusal in player-facing language. D8 PACK/WRD cases remain companion coverage, with import/price/UI conflicts resolved by D3 §16/D6 §15 and explicit PB-17 product decisions. No direct Wardrobe buying is presumed. Test shared helper cleanup with one consumer shutting down while another remains valid under the supported restart lifecycle; no unsupported hot unload implied.

Before release of an accepted extraction slice, require real standalone compile/link plus runtime evidence, v1 and profile migration checks, no-default/balance change comparison and relevant resource measurements. Paid adapters remain disabled unless their own cross-store guarantee passes; extraction alone cannot certify it. Record actual pass/fail/blocked results separately; no tests/builds executed here.
