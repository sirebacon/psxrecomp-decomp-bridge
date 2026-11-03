"""Summarize paired native-default screening and dropped proposals."""
import argparse,csv,json,random,statistics
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def mean(rows,key):return statistics.mean(r[key] for r in rows) if rows else None

def selected(rows):
    groups=defaultdict(list)
    for r in rows:
        if r['variant']=='native':groups[r['loadout']].append(r)
    def score(item):
        rr=[r for r in item[1] if not r['boss']]
        return (-mean(rr,'won'),mean(rr,'time'))
    return min(groups.items(),key=score)[0]

def paired(base,prop):
    key=lambda r:(r['seed'],r['battle'])
    bm={key(r):r for r in base};pm={key(r):r for r in prop}
    diffs=defaultdict(list)
    for k,b in bm.items():diffs[k[1]].append(pm[k]['time']-b['time'])
    ds=[statistics.mean(v) for v in diffs.values()];rng=random.Random(26)
    bs=sorted(statistics.mean(rng.choices(ds,k=len(ds))) for _ in range(1000))
    return [round(bs[24],2),round(bs[974],2)]

def summarize(data):
    groups=defaultdict(list)
    for r in data['rows']:groups[(r['stage'],r['gun'],r['mode'],r['invest'])].append(r)
    summary=[];candidates=[]
    for (stage,gun,mode,invest),rs in groups.items():
        li=selected(rs);base=[r for r in rs if r['variant']=='native' and r['loadout']==li]
        entry=dict(stage=stage,gun=gun,mode=mode,invest=invest,kind=rs[0]['kind'],mods=base[0]['mods'])
        for boss,label in ((False,'ord'),(True,'boss')):
            rr=[r for r in base if r['boss']==boss]
            for k in ('time','won','damage_taken','rounds','reloads'):
                entry[label+'_'+k]=mean(rr,k)
        summary.append(entry)
        for variant in sorted({r['variant'] for r in rs}-{'native'}):
            for boss,label in ((False,'ordinary'),(True,'boss')):
                bb=[r for r in base if r['boss']==boss]
                pp=[r for r in rs if r['variant']==variant and r['loadout']==li and r['boss']==boss]
                if not bb:continue
                candidates.append(dict(stage=stage,gun=gun,mode=mode,invest=invest,variant=variant,encounter=label,n=len(bb),
                    base_time=mean(bb,'time'),prop_time=mean(pp,'time'),change_pct=100*(mean(pp,'time')/mean(bb,'time')-1),
                    base_win=mean(bb,'won'),prop_win=mean(pp,'won'),delta_ci=paired(bb,pp),
                    base_damage=mean(bb,'damage_taken'),prop_damage=mean(pp,'damage_taken'),base_reload=mean(bb,'reloads'),prop_reload=mean(pp,'reloads')))
    return summary,candidates

def main():
    p=argparse.ArgumentParser();p.add_argument('tag');a=p.parse_args()
    data=json.loads((ROOT/'findings/data'/('pe-'+a.tag+'.json')).read_text());ss,cc=summarize(data)
    (ROOT/'findings/data'/('pe-'+a.tag+'-summary.json')).write_text(json.dumps(dict(meta=data['meta'],ladder=ss,candidates=cc),indent=1))
    for suffix,records in (('ladder',ss),('candidates',cc)):
        with (ROOT/'findings/data'/('pe-'+a.tag+'-'+suffix+'.csv')).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    lines=['# Native weapon balance review — 2026-10-26','',
        'Simulation only. No native game source, balance settings, or binaries changed.','',
        f"{len(data['rows']):,} simulated fights; {data['meta']['seeds']} seeds; native-default attack bonuses and combat rules mapped into the calibrated source model.",
        f"Screen: up to {data['meta']['battle_limit']} ordinary encounters and four bosses per stage, sampled separately with a fixed seed. Built-in-only has zero optional installs, including Disc2. Catalog selects the best native loadout from the tested feasible orders, prioritizing wins and then ordinary time; candidate comparisons keep that same loadout.",
        'Stage availability follows the historical ladder: D5 includes museum-era guns and Wayne rewards. It is not exact pickup chronology.',
        'Boss and ordinary results stay separate; these are not campaign-weighted totals. Candidate intervals resample encounter-level paired differences and describe model variation, not confidence in real gameplay.','',
        '## Revisited proposals','',
        'candidate_half / candidate_full: M203-3 +10 / +20, M79-2 +10 / +20, M79-3 +5 / +10, PPK +5 / +10 attack. Extended runs also test M79-3 +15 and +20. M10B: +1 or +50% magazine. Existing six native bonuses remain enabled in every case.','',
        '| Stage | Gun | Setup | Candidate | Fights | Ordinary seconds | Change | Paired delta interval, s | Win rate |',
        '|---|---|---|---|---:|---|---:|---|---|']
    for c in cc:
        if c['encounter']!='ordinary':continue
        lines.append(f"| {c['stage']} | {c['gun']} | {c['mode']} / {c['invest']} | {c['variant']} | {c['n']} | {c['base_time']:.2f} → {c['prop_time']:.2f} | {c['change_pct']:+.1f}% | {c['delta_ci']} | {c['base_win']:.2f} → {c['prop_win']:.2f} |")
    for stage in ('D2-4','D5','Disc2'):
        for mode in ('builtin','catalog'):
            for invest in data['meta']['invest']:
                rr=sorted([r for r in ss if r['stage']==stage and r['mode']==mode and r['invest']==invest],key=lambda r:r['ord_time'])
                if not rr:continue
                med=statistics.median(r['ord_time'] for r in rr)
                lines += ['',f'## {stage} / {mode} / {invest} — median {med:.2f}s','',
                    '| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |','|---|---|---|---:|---:|---:|---:|']
                for r in rr:
                    bt='—' if r['boss_time'] is None else f"{r['boss_time']:.2f}"
                    bw='—' if r['boss_won'] is None else f"{r['boss_won']:.2f}"
                    lines.append(f"| {r['gun']} | {r['kind']} | {', '.join(r['mods']) or '—'} | {r['ord_time']:.2f} | {r['ord_time']/med:.2f} | {bt} | {bw} |")
    lines += ['','## Model limits','']+['- '+x for x in data['meta']['limitations']]
    lines += ['- Per-hit integer arithmetic passed 2,000 randomized comparisons against the native C helper compiled unchanged. This does not validate the entire fight model.',
        '- Critical conversion uses the inherited probability 26.67% rather than native integer 26%; random sequences are not native RNG replays. The five disputed weapons have no built-in Critical.',
        '- At the minimum-damage floor, the model may apply a status that native gun damage skips. Treat near-floor status results as approximate.',
        '- Native crowd-cap binary-search granularity and delayed hit processing are approximated by limiting final HP loss. Shot queues and enemy behavior remain a model, not native-game execution.']
    (ROOT/'findings'/('pe-'+a.tag+'.md')).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(len(ss),'ladder entries;',len(cc),'candidate comparisons')
if __name__=='__main__':main()
