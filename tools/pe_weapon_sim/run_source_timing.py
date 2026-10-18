"""Generate source-derived switch/refill cases without controlling the game."""
import json
from dataclasses import asdict
from pathlib import Path
from .data import KIND
from .source_timing import gauge_gain, refill_updates, switch_to_attack


def main():
    out = Path(__file__).resolve().parents[2] / 'findings'
    cases = []
    for half in (False, True):
        for gauge in (0, 4500, 7800, 9000):
            for source in range(1, 9):
                for dest in range(1, 9):
                    r = switch_to_attack(gauge, gauge_gain(79, source), gauge_gain(79, dest), half_bar=half)
                    cases.append(dict(mode='current_half' if half else 'retail_full', gauge=gauge,
                        source=KIND[source], destination=KIND[dest], **asdict(r), total_updates=r.total_updates))
    raw = dict(stat22=79, units='eligible battle gauge updates; not VBlanks or seconds',
        excludes=['menu duration', 'switch animation', 'enemy actions', 'damage', 'clock calibration'], cases=cases)
    (out/'data'/'pe-source-timing-2026-10-18.json').write_text(json.dumps(raw, indent=2), encoding='utf-8')
    lines = ['# Source-derived timing cases — 2026-10-18', '',
        '512 deterministic switch transitions at stat22 79. Values count eligible gauge updates,',
        'not VBlanks or seconds. Menu and switch execution durations are excluded.', '',
        '| Destination | Integer gain | Empty-to-full updates | Full-bar CURRENT switch to attack | Full-bar retail switch to attack |',
        '|---|---:|---:|---:|---:|']
    for kind, name in KIND.items():
        gain = gauge_gain(79, kind)
        current = switch_to_attack(9000, 79, gain)
        retail = switch_to_attack(9000, 79, gain, half_bar=False)
        lines.append(f'| {name} | {gain} | {refill_updates(0,gain)} | {current.total_updates} | {retail.total_updates} |')
    lines += ['', 'The CURRENT gain after switching follows the destination weapon. Starting from an',
        'empty gauge additionally requires reaching 4500 using the source weapon; retail',
        'requires 9000. Rounded threshold overshoot is retained by CURRENT.', '',
        'These are gauge-state calculations, not within-fight portfolio results. Historical',
        'campaign rankings and optimistic secondary-weapon bounds have not been regenerated.',
        'Clock rate and animation/event scheduling remain open. See the source audit and handoff.']
    (out/'pe-source-timing-2026-10-18.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(f'Wrote {len(cases)} source-derived cases and timing table.')


if __name__ == '__main__':
    main()
