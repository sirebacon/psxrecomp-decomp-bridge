"""Read-only native-default shotgun review, including all Chrysler weapon records.
Campaign benchmarks and constructed Chrysler stat scenarios remain separate.
"""
import argparse,concurrent.futures,hashlib,json,math,random,time
from functools import lru_cache
from pathlib import Path
from . import run_benchmark as B,compare_rules as C,rules as R,engine as E
from .run_native_review import init
from .native_audit import audit_native
from .decomp_animation import source_behavior_rules
from .enemy_identity import FIRST_RUN_SHARED_CELLS,MULTI_KIND
from .economy import source_stats
from .progression import Gun
ROOT=Path(__file__).resolve().parents[2]
NATIVE=Path('D:/Recomp Games/parasite-eve-pc')
PROGRESSION={0x79:25,0x7b:15,0x83:20,0x84:15,0x85:20,0x8a:20,0x8b:18}
ANCHORS=['M9 3','DE50AE7','P90','MAG','M203 4','M79 3']
PROFILES=('stock','attack_only','mag2')

@lru_cache(None)
def baseline():
    audit=audit_native(NATIVE,expected_progression=PROGRESSION)
    bonuses={**audit['progression'],0x7d:audit['defaults']['G3A3 attack bonus'],0x86:audit['defaults']['M203 4 attack bonus']}
    r=dict(R.experimental('AAc_75','RoFE'),native_gun_arithmetic=True)
    r['crit_convert_pct']=(audit['defaults']['Critical bonus points']-20)*100//75
    r['rof_mod_hit_pct']={n:p*(200000//(n*p))/1000 for n,p in {5:25,7:18,10:13}.items()}
    return audit,bonuses,r

def configuration(w,stage,profile):
    g=Gun(w)
    investment=C.INVEST['D5' if stage=='D5' else 'Disc2']['typical']
    g.invested=[0,0,0] if profile=='stock' else [investment[0],investment[1],2 if profile=='mag2' else 0]
    cfg=B.gun_cfg(g,[]);cfg['eff']['rof_mod']=False
    cfg['power']+=baseline()[1].get(w.id,0)
    return cfg

@lru_cache(None)
def scenarios(stage):
    init()
    if stage in ('D5','Disc2'):
        pool=C.campaign_battles(stage);rng=random.Random(262026)
        ords=[b for b in pool if not b['boss']];bosses=[b for b in pool if b['boss']]
        return [dict(b,scenario_kind='campaign_boss' if b['boss'] else 'campaign_ordinary') for b in rng.sample(ords,min(12,len(ords)))+rng.sample(bosses,min(4,len(bosses)))]
    data=json.loads((ROOT/'findings/data/pe-bestiary-draft-2026-10-19.json').read_text())
    pool=[e for e in data['enemies'] if 'Chrysler (EX)' in e['blocks'] and e['role']=='regular' and not e['boss'] and e['hp']>0]
    pool.sort(key=lambda e:(e['hp'],e['defense'],e['id']))
    selected=[pool[round(i*(len(pool)-1)/11)] for i in range(12)]
    hardest=max(pool,key=lambda e:e['defense'])
    if hardest not in selected:selected[-2]=hardest
    assert len({(e['id'],e['hp'],e['defense']) for e in selected})==12
    level=33 if stage=='EX33' else 50
    late=C.campaign_battles('Disc2')[-1];aya=dict(late['aya']);s=source_stats.aya_stats(level)
    aya.update({k:s[k] for k in ('level','offense','defense','stat22','status_step3c','status_step3e')})
    rows=[]
    for e in selected:
        loc=next(m for m in e['maps'] if 288<=m<=318 or 382<=m<=424 or 434<=m<=437)
        f=dict(name=e['id'],loc=loc,hp=e['hp'],defense=e['defense'],level=int(e['id'],16)&255,boss=False,label=e['name'])
        for k in ('heat','frost','cyanide','acid','tranq'):f[k]='Weak' if k in e['weak'] else 'Strong' if k in e['strong'] else 'Average'
        for count in (1,3):
            rows.append(dict(map=loc,boss=False,foes=[dict(f) for _ in range(count)],aya=aya,armor=late['armor'],level=level,
                scenario_kind='ex_solo' if count==1 else 'ex_triple',ex_name=e['name'],ex_hp=e['hp'],ex_defense=e['defense']))
    return rows

def run_one(rules,cfg,battle,seed,geometry='scattered'):
    opts=C.options_for(C.ASSUMPTIONS['default'],{**FIRST_RUN_SHARED_CELLS,MULTI_KIND:1})
    opts['hp']=source_stats.aya_stats(battle['aya']['level'])['max_hp']
    if geometry=='clustered':opts['enemy_angles']={i:(i-1)*128 for i in range(len(battle['foes']))}
    if battle['scenario_kind'].startswith('campaign'):
        opts['pe']=dict(spells=battle.get('known_spells',[]),rules='current',heal_rules='current',max_hp=opts['hp'],bag=dict(battle.get('bag',{})))
        opts['player_max_hp']=opts['hp']
    st=E.fight(source_behavior_rules(rules),cfg,battle['aya'],[dict(f) for f in battle['foes']],
        B.PROF['boss'] if battle['boss'] else B.PROF['normal'],random.Random(seed),armor=battle['armor'],source_options=opts,
        time_cap=400 if battle['boss'] else 90,policy='walk')
    assert st['ammo_balance']==0
    return {k:st.get(k,0) for k in ('won','time','damage_taken','rounds','reloads','click','damage','turns','hits_taken','strikes','legacy_damage_hits','strike_timing_untimed','catalog_matches','catalog_foes')}

def job(task):
    init();stage,wid,profile,seeds,variants=task[:5]
    geometry=task[5] if len(task)>5 else 'scattered'
    w=B.W[wid];cfg=configuration(w,stage,profile);r=baseline()[2];rows=[]
    for seed in range(1,seeds+1):
        for bi,battle in enumerate(scenarios(stage)):
            for v in variants:
                c=dict(cfg,eff=dict(cfg['eff']))
                if v.startswith('attack'):c['power']+=int(v[6:])
                elif v.startswith('mag'):
                    n=v[3:];c['magazine']+=math.ceil(c['magazine']*.5) if n=='50pct' else int(n)
                result=run_one(r,c,battle,seed*7919+bi,geometry)
                rows.append(dict(stage=stage,gun=w.name,id=wid,kind=w.kind,profile=profile,variant=v,seed=seed,case=bi,map=battle['map'],
                    scenario_kind=battle['scenario_kind'],boss=battle['boss'],magazine=c['magazine'],power=c['power'],geometry=geometry,**result))
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',default='native-all-shotguns-2026-10-26');p.add_argument('--seeds',type=int,default=4)
    p.add_argument('--workers',type=int,default=4);p.add_argument('--stages',nargs='+',default=['D5','Disc2','EX33','EX50'])
    p.add_argument('--profiles',nargs='+',choices=PROFILES,default=list(PROFILES));p.add_argument('--only',nargs='*')
    p.add_argument('--variants',nargs='+',default=['current']);p.add_argument('--no-anchors',action='store_true')
    p.add_argument('--geometry',choices=['scattered','clustered'],default='scattered')
    a=p.parse_args();audit,bonuses,_=baseline();guns={w.id:w for w in B.W.values() if w.kind==2 or (not a.no_anchors and w.name in ANCHORS)}
    if a.only:guns={i:w for i,w in guns.items() if w.name in a.only}
    assert guns and a.seeds>0
    tasks=[(stage,i,profile,a.seeds,a.variants if w.kind==2 else ['current'],a.geometry) for stage in a.stages for i,w in guns.items() for profile in a.profiles]
    out=ROOT/'findings/data'/('pe-'+a.tag+'.json');rows=[];start=time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as ex:
        futures={ex.submit(job,t):t for t in tasks}
        for n,f in enumerate(concurrent.futures.as_completed(futures),1):
            rows+=f.result();print(n,'/',len(tasks),futures[f][:3],len(rows),'fights',round(time.time()-start),'s',flush=True)
            if n%10==0:out.with_suffix('.partial.json').write_text(json.dumps(rows))
    assert audit_native(NATIVE,expected_progression=PROGRESSION)==audit,'Native balance changed during run'
    metadata=dict(native_audit=audit,bonuses=bonuses,seeds=a.seeds,profiles=a.profiles,variants=a.variants,geometry=a.geometry,
        guns={i:dict(name=w.name,kind=w.kind,attack=w.attack,intrinsic_attack=w.bonus_attack,range=w.range_stat+w.bonus_range,
            magazine=w.bullets+w.bonus_bullets,builtin=w.builtin) for i,w in guns.items()},
        scenarios={stage:scenarios(stage) for stage in a.stages},
        note='No native writes. Source-model benchmark, not native game execution. Chrysler weapons in campaign cases are counterfactual comparisons, not acquisition timing.',
        limitations=['Chrysler cases use extracted regular enemy HP, defense and resistances; synthetic solos and triples, not recorded encounters or a full tower campaign.',
          'EX33/EX50 are fixed level scenarios with the logged endgame armor; no PE or consumables in EX stat stress tests; campaign cases retain logged PE/bags.',
          'No scripted Chrysler bosses or True Eve validation. Enemy behavior/geometry and unresolved timings are modeled, and may use fallbacks.',
          'All weapons use built-in effects only. Shotguns use native built-in RoF behavior, never installed-RoF acceleration.',
          'Stock means zero investment. attack_only uses typical attack/range but zero magazine investment. mag2 adds only two magazine rounds to attack_only.',
          'Rounds are ammo cost; reload and empty-click counts are model diagnostics, not live measurements. No between-fight magazine carryover.',
          'Gun damage uses native integer helper arithmetic; whole-fight scheduling, native RNG, status floors and delayed hit processing retain earlier review limitations.'],
        model_hashes={n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest() for n in ('run_shotgun_review.py','native_damage.py','engine.py','source_combat.py','source_battle.py')})
    rows.sort(key=lambda r:(r['stage'],r['id'],r['profile'],r['seed'],r['case'],r['variant']))
    out.write_text(json.dumps(dict(meta=metadata,rows=rows),indent=1));print('SAVED',out,flush=True)
if __name__=='__main__':main()
