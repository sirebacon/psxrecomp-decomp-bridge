"""Native-default weapon review: paired fights, no installs and Catalog separately.
Uses the calibrated Python model, NOT execution of the native game binary.
"""
import argparse, concurrent.futures, hashlib, json, random, statistics, time
from pathlib import Path
from . import compare_rules as C, run_benchmark as B, run_gun_ladder as L, rules as R
from .enemy_identity import FIRST_RUN_SHARED_CELLS, MULTI_KIND
from .progression import Gun
ROOT=Path(__file__).resolve().parents[2]
BONUSES={'G3A3':45,'M203 4':15,'M16A1':25,'SG550':15,'M203':20,'M203 2':15}
DROPPED={'M203 3':20,'M79 2':20,'M79 3':10,'PPK':10}

def init():
    for flag in (C.CALIBRATED,C.SERIAL,C.ATB_GUARD,C.LOGGED_CHARGE,C.IDENTITY_RANK): flag[0]=True

def job(task):
    init()
    stage,iid,mode,invest,seeds,battle_limit,extended=task[:7]
    w=B.W[iid]; rules=dict(R.experimental('AAc_75','RoFE'))
    rules['native_gun_arithmetic']=True
    # Native atk_pm is integer per-mille on the attack term. Engine uses floats;
    # represent that scaling, rather than rounding RoF7 to 29% per bullet.
    vanilla={5:25,7:18,10:13}
    rules['rof_mod_hit_pct']={n:p*(200000//(n*p))/1000 for n,p in vanilla.items()}
    variants=[('native',0)]
    if w.name in DROPPED:
        variants += [('candidate_half',DROPPED[w.name]//2),('candidate_full',DROPPED[w.name])]
        if extended and w.name=='M79 3':variants += [('attack_plus15',15),('attack_plus20',20)]
        if len(task)>7 and task[7] and w.name=='M79 3':variants += [('attack_plus%d'%n,n) for n in (16,17,18,19)]
    elif w.name=='M10B': variants += [('magazine_plus1',0),('magazine_plus50pct',0)]
    mods=[[]] if mode=='builtin' else sorted({tuple(L.catalog_loadout(w,stage,o)) for o in L.CAT_ORDERS[stage]})
    battles=C.campaign_battles(stage); rows=[]
    # Stratify so a small screen cannot accidentally omit bosses. Group means
    # must remain separate; this sample is not a campaign-frequency total.
    if battle_limit:
        ords=[b for b in battles if not b['boss']]; bosses=[b for b in battles if b['boss']]
        rng=random.Random(262026)
        battles=rng.sample(ords,min(battle_limit,len(ords)))+rng.sample(bosses,min(4,len(bosses)))
    for li,extra in enumerate(mods):
        g=Gun(w)
        g.invested=list(C.INVEST[stage]['typical' if invest=='attack_only' else invest]) if invest!='stock' else [0,0,0]
        if invest=='attack_only':g.invested[2]=0
        cfg=B.gun_cfg(g,list(extra))
        # Match native detection: effective RoF exists on record, absent on base item.
        rof=cfg['eff'].get('rof',1)
        cfg['eff']['rof_mod']=rof in (5,7,10) and ('RoF%d'%rof) not in w.builtin
        cfg['power']+=BONUSES.get(w.name,0)
        for seed in range(1,seeds+1):
            for bi,battle in enumerate(battles):
                b=dict(aya=None,phase=stage,seed=seed)
                for variant,bonus in variants:
                    pcfg=dict(cfg,eff=dict(cfg['eff']),power=cfg['power']+bonus)
                    if variant=='magazine_plus1': pcfg['magazine']+=1
                    if variant=='magazine_plus50pct': pcfg['magazine']=round(pcfg['magazine']*1.5)
                    result=C.run_fight(rules,pcfg,b,battle,'default',C.ASSUMPTIONS['default'],seed*7919+bi,{**FIRST_RUN_SHARED_CELLS,MULTI_KIND:1})
                    rows.append(dict(stage=stage,gun=w.name,id=iid,kind=w.kind,mode=mode,invest=invest,
                        loadout=li,mods=list(extra),variant=variant,seed=seed,battle=bi,map=battle['map'],boss=battle['boss'],**result))
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('--seeds',type=int,default=2);p.add_argument('--workers',type=int,default=4)
    p.add_argument('--battle-limit',type=int,default=8,help='ordinary samples + up to 4 bosses; 0 = every battle')
    p.add_argument('--tag',default='native-review-2026-10-26');p.add_argument('--only',nargs='*');p.add_argument('--invest',nargs='+',default=['typical'])
    p.add_argument('--stages',nargs='+',default=['D2-4','D5','Disc2'])
    p.add_argument('--extended',action='store_true',help='also test M79 3 +15 and +20 attack')
    p.add_argument('--modes',nargs='+',choices=['builtin','catalog'],default=['builtin','catalog'])
    p.add_argument('--fine',action='store_true',help='also test M79 3 +16 through +19')
    a=p.parse_args();first=L.first_seen(); tasks=[]
    from .native_audit import audit_native
    audit=audit_native('D:/Recomp Games/parasite-eve-pc')
    for stage in a.stages:
        for iid in L.pool(stage,first):
            if a.only and B.W[iid].name not in a.only: continue
            for mode in a.modes:
                for invest in a.invest:tasks.append((stage,iid,mode,invest,a.seeds,a.battle_limit,a.extended,a.fine))
    out=ROOT/'findings/data'/('pe-'+a.tag+'.json');rows=[];start=time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as ex:
        fs={ex.submit(job,t):t for t in tasks}
        for n,f in enumerate(concurrent.futures.as_completed(fs),1):
            rows+=f.result();print(n,'/',len(tasks),fs[f],len(rows),'fights',round(time.time()-start),'s',flush=True)
            if n%10==0:out.with_suffix('.partial.json').write_text(json.dumps(rows))
    native=Path('D:/Recomp Games/parasite-eve-pc/mods/pe_rebalance/pe_mod_effects.c')
    meta=dict(seeds=a.seeds,battle_limit=a.battle_limit,invest=a.invest,bonuses=BONUSES,dropped=DROPPED,native_source_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),
        native_audit=audit,
        model='calibrated Python source model; native default rules mapped; not native binary execution',
        limitations=['Integer per-hit hook arithmetic mapped from native; crowd cap models restored final HP, not delayed engine updates or the native 40-frame reference heuristic.', 'One logged campaign; synthetic loadouts, not a new acquisition/economy simulation.',
        'Catalog best-of tested orders is an optimistic upper bound, not guaranteed player ownership.', 'Built-in-only means no optional installs at ALL stages, including Disc2.',
        'Infinite reserve per isolated battle; rocket results do not establish campaign ammo viability.'])
    rows.sort(key=lambda r:(r['stage'],r['id'],r['mode'],r['invest'],r['loadout'],r['seed'],r['battle'],r['variant']))
    out.write_text(json.dumps(dict(meta=meta,rows=rows),indent=1));print('SAVED',out,flush=True)
if __name__=='__main__':main()
