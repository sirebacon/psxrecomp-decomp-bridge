"""Generate the targeted follow-up report from its raw JSON."""
import json
import math
import os
from .run_followups import OUT
from . import run_phase3 as P, reporting as R


def table(head, rows):
    return R.table(head, [[str(v).replace('|','\\|') for v in row] for row in rows])


def main():
    with open(OUT,encoding='utf-8') as f: d=json.load(f)
    n=d['meta']['n']
    rows=[]
    for group,phases in d['summary'].items():
        for phase,s in phases.items():
            rows.append([group,phase,str(s['commands_present'])+'/'+str(n),str(s['quickdraw_present'])+'/'+str(n),
                         R.mci(s['baseline'])]+[R.mci(s['delta'][v]) for v in ('no_commands','no_quickdraw','neither')])
    rate_rows=[]
    for group in d['summary']:
        low={r['seed']:r['suite'] for r in d['tick_rates'] if r['group']==group and r['tick_hz']==59.9}
        high={r['seed']:r['suite'] for r in d['tick_rates'] if r['group']==group and r['tick_hz']==94.0}
        rate_rows.append([group,R.mci(P.stats(list(high.values()))),R.mci(P.stats(list(low.values()))),
                          R.mci(P.stats([low[s]-high[s] for s in sorted(low)]))])
    portfolio_rows=[]
    for group in ('overlap|D','serial|D'):
        for phase in ('D5','Disc2'):
            rs=[r for r in d['portfolios'] if r['group']==group and r['phase']==phase]
            # Screening is only interpretable when both component suites reliably win.
            safe=[r for r in rs if all(a>=.999 and b>=.999 for a,b in r['free']['wins'].values())]
            portfolio_rows.append([group,phase,f'{len(rs)}/{n}',f'{len(safe)}/{len(rs)}',
                R.mci(P.stats([r['free']['envelope']-r['free']['main'] for r in safe])),
                R.mci(P.stats([r['charged']['envelope']-r['charged']['main'] for r in safe])),
                sum(bool(r['charged']['secondary_faster']) for r in safe)])
    text=(
        '# Phase 3 targeted validation follow-ups\n\n'
        f'{len(d["raw"])*n} new invariant-checked campaign replays; {n} matched seeds per policy/timing '
        'group. Each D5 and Disc2 checkpoint uses 20 fights per encounter. Original historical '
        'JSON and reports C–L are preserved. No live gameplay or save changes.\n\n'
        '## Timing source audit\n\n'
        'Local decompiled action processing sets game flag 0x100, and Aya’s gauge update is gated '
        'by that flag. This favors serial-style pause behavior; it does not calibrate every animation '
        'or establish a new real-time clock. See `pe-weapon-p3-runtime-validation-plan.md` for verified '
        'source locations, caveats and a concrete frame-level capture protocol. No new runtime '
        'capture was performed. Both timing hypotheses remain explicitly tested.\n\n'
        '## Matched mod-removal experiments\n\n'
        'Positive differences mean slower than the identical baseline checkpoint. Removing Commands '
        'sets the command count to one; removing Quickdraw disables its effect. Other stats and '
        'effects remain fixed. Slots are left empty, no replacement effect is added, and progression '
        'is not rerun with the weakened gun. C = optimizer, G = ATB-first, controlled_shotgun = C’s '
        'decision rules with a shotgun preference, D = two-weapon policy main gun.\n\n'+
        table(['group','phase','Commands present','Quickdraw present','baseline seconds',
               'remove Commands Δs','remove Quickdraw Δs','remove both Δs'],rows)+
        '\n\nIntervals are the inherited normal approximation over paired campaign-seed differences. '
        'They do not include model error. If an effect is absent, its removal is a no-op; presence '
        'counts give the relevant denominator. This quantifies the cost of removal in the tested '
        'loadouts, not whether the effect is mandatory after legal replacement/reinvestment.\n\n'
        '## Gauge-clock sensitivity on frozen final loadouts\n\n'
        'Only the engine’s fill-time conversion changes. The 94-Hz value is the historical '
        'aggregate-turn calibration; 59.9 is an alternative suggested by the logger frame conversion, '
        'not a newly measured gauge tick rate. Earned equipment, BP strategy and encounter samples '
        'stay fixed. A full campaign under a different clock can make different investment choices.\n\n'+
        table(['group','94-Hz suite seconds','59.9-Hz suite seconds','paired Δs'],rate_rows)+
        '\n\n## Two-weapon screening\n\n'
        'For each encounter, the optimistic envelope picks the faster of the two separately '
        'benchmarked weapons. A second version adds half of the secondary weapon’s fill time '
        'when choosing it. Both assume advance knowledge of the encounter and start each component '
        'fight independently. They do not simulate enemy actions during a switch, within-fight '
        'switching, shared ammo, menu/animation time or carried ATB. The half-fill delay is an '
        'assumed scalar cost screen informed by the CURRENT half-bar switch, not a validated '
        'switch-duration model. Negative deltas are optimistic improvements versus the main gun.\n\n'+
        table(['group','phase','secondary owned','both suites win','free-choice Δs','half-fill-cost Δs',
               'runs with any secondary niche after delay'],portfolio_rows)+
        '\n\nThe envelope analysis excludes runs with any component encounter win rate below 99.9%. '
        'It compares D’s two components, not D against an equally funded single-gun policy. '
        'A benefit here is only a candidate niche to test dynamically; a lack of benefit does not '
        'rule out movement, status or tactical benefits absent from the encounter model.\n\n'
        '## What remains\n\n'
        '- Measure guest-frame gauge increments, firing/reload duration and the half-bar weapon '
        'change using the capture protocol. Source evidence is stronger than before, but runtime '
        'duration remains unmeasured.\n'
        '- For any high-cost mod removal, test a legal alternative effect with the same slot '
        'and resource budget before calling it mandatory.\n'
        '- Verify actual early Wayne access and 300-Junk timing. The simulated first M10B '
        'observation reflects policy behavior, not the earliest legal acquisition.\n'
        '- Build a dynamic switching model only around an observed secondary niche and validate '
        'its gauge/ammo/animation transitions against captured gameplay.\n\n'
        '## Reproduce\n\nFrom `D:/Recomp Games/psxrecomp-decomp-bridge/tools`, use the bundled Python:\n\n'
        '```powershell\n'
        "$simPython = 'C:\\Users\\maver\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe'\n"
        '& $simPython -m unittest discover -s pe_weapon_sim/tests\n'
        '& $simPython -m pe_weapon_sim.economy.run_followups --n 40\n'
        '& $simPython -m pe_weapon_sim.economy.report_followups\n```\n\n'
        'Raw output: `data/pe-weapon-p3-followups-2026-10-17.json`. It includes paired seed-level '
        'benchmarks, portfolio component win rates, clock alternatives, parameters and source hashes.\n')
    path=os.path.join(P.OUT_DIR,'..','pe-weapon-p3-targeted-followups-2026-10-17.md')
    with open(path,'w',encoding='utf-8') as f:f.write(text)
    print('wrote',os.path.abspath(path))


if __name__=='__main__':main()
