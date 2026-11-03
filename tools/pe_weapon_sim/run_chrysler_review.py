"""Remaining Chrysler weapon benchmark under the current native balance.
Reuses the logged campaign and explicitly synthetic EX stat stress cases.
Never writes native game files or settings.
"""
import argparse,concurrent.futures,csv,hashlib,json,random,time
from functools import lru_cache
from pathlib import Path
from . import run_shotgun_review as S,run_benchmark as B,compare_rules as C,rules as R
from .native_audit import audit_native
from .progression import Gun
ROOT=Path(__file__).resolve().parents[2]
NATIVE=Path('D:/Recomp Games/parasite-eve-pc')
CURRENT={0x5f:5,0x69:10,0x79:25,0x7b:15,0x83:20,0x84:15,0x85:20,0x8a:20,0x8b:18}
ANCHORS=['M9 3','DE50AE7','PPK','M10B','P90','MP5PDW','G3A3','MAG','M203 4','M79 3','HK40','LAW80','CLUB 3']

@lru_cache(None)
def baseline():
 a=audit_native(NATIVE,expected_progression=CURRENT)
 bonuses={**a['progression'],0x7d:a['defaults']['G3A3 attack bonus'],0x86:a['defaults']['M203 4 attack bonus']}
 r=dict(R.experimental('AAc_75','RoFE'),native_gun_arithmetic=True)
 r['crit_convert_pct']=(a['defaults']['Critical bonus points']-20)*100//75
 r['rof_mod_hit_pct']={n:p*(200000//(n*p))/1000 for n,p in {5:25,7:18,10:13}.items()}
 return a,bonuses,r

@lru_cache(None)
def chrysler_ids():
 norm=lambda s:''.join(c for c in s.upper() if c.isalnum())
 by={norm(w.name):i for i,w in B.W.items()}
 aliases={'AM444':'AM44','MA102':'M8702'}
 ids=[]
 with (ROOT/'findings/data/pe-gear-locations-2026-10-11.csv').open() as f:
  for row in csv.DictReader(f):
   if 'Chrysler' not in row['location'] or row['type']=='armor':continue
   key=norm(row['name']);key=aliases.get(key,key)
   if key not in by:raise ValueError('Unmapped Chrysler weapon: '+row['name'])
   iid=by[key]
   if B.W[iid].kind!=2:ids.append(iid)
 assert len(ids)==len(set(ids))
 return tuple(ids)

def configuration(w,stage,profile):
 g=Gun(w);inv=C.INVEST['D5' if stage=='D5' else 'Disc2']['typical']
 g.invested=[0,0,0] if profile=='stock' else [inv[0],inv[1],2 if profile=='mag2' else 0]
 c=B.gun_cfg(g,[]);c['eff']['rof_mod']=False;c['power']+=baseline()[1].get(w.id,0)
 return c

def job(task):
 stage,wid,profile,seeds,variants=task;S.init();w=B.W[wid];cfg=configuration(w,stage,profile);r=baseline()[2];rows=[]
 for seed in range(1,seeds+1):
  for bi,b in enumerate(S.scenarios(stage)):
   for v in variants:
    c=dict(cfg,eff=dict(cfg['eff']))
    if v.startswith('attack'):c['power']+=int(v[6:])
    elif v.startswith('mag'):c['magazine']+=int(v[3:])
    result=S.run_one(r,c,b,seed*7919+bi)
    rows.append(dict(stage=stage,id=wid,gun=w.name,kind=w.kind,chrysler=wid in chrysler_ids(),profile=profile,variant=v,
      seed=seed,case=bi,map=b['map'],scenario_kind=b['scenario_kind'],boss=b['boss'],magazine=c['magazine'],power=c['power'],**result))
 return rows

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',default='native-chrysler-weapons-2026-10-26');p.add_argument('--seeds',type=int,default=4)
 p.add_argument('--workers',type=int,default=4);p.add_argument('--stages',nargs='+',default=['Disc2','EX33','EX50'])
 p.add_argument('--profiles',nargs='+',choices=['stock','attack_only','mag2'],default=['stock','attack_only'])
 p.add_argument('--only',nargs='*');p.add_argument('--variants',nargs='+',default=['current']);p.add_argument('--no-anchors',action='store_true')
 a=p.parse_args();audit,bonuses,_=baseline();targets=chrysler_ids()
 guns={i:w for i,w in B.W.items() if i in targets or (not a.no_anchors and w.name in ANCHORS)}
 if a.only:guns={i:w for i,w in guns.items() if w.name in a.only}
 assert guns and a.seeds>0
 # Freeze provenance before dispatch. No native writes at any point.
 hashes={n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest() for n in ('run_chrysler_review.py','run_shotgun_review.py','native_damage.py','engine.py','source_combat.py','source_battle.py')}
 tasks=[(st,i,pr,a.seeds,a.variants if i in targets else ['current']) for st in a.stages for i in guns for pr in a.profiles]
 out=ROOT/'findings/data'/('pe-'+a.tag+'.json');rows=[];start=time.time()
 with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as ex:
  futures={ex.submit(job,t):t for t in tasks}
  for n,f in enumerate(concurrent.futures.as_completed(futures),1):
   rows+=f.result();print(n,'/',len(tasks),futures[f][:3],len(rows),'fights',round(time.time()-start),'s',flush=True)
   if n%10==0:out.with_suffix('.partial.json').write_text(json.dumps(rows))
 assert audit_native(NATIVE,expected_progression=CURRENT)==audit,'Native code changed during run'
 meta=dict(native_audit=audit,bonuses=bonuses,seeds=a.seeds,profiles=a.profiles,variants=a.variants,model_hashes=hashes,
   guns={i:dict(name=w.name,kind=w.kind,chrysler=i in targets,attack=w.attack+w.bonus_attack,range=w.range_stat+w.bonus_range,magazine=w.bullets+w.bonus_bullets,builtin=w.builtin) for i,w in guns.items()},
   scenarios={st:S.scenarios(st) for st in a.stages},
   note='Current native Rebalanced defaults, including PPK +5, M870-2 +10, and the three approved grenade bonuses. Native files and settings untouched.',
   limitations=['All weapons keep built-in effects; no Catalog installs or installed-RoF acceleration.',
    'Stock means no player investment; attack_only adds typical late attack/range (+50/+18), no magazine bonus. Profiles retain intrinsic bonuses.',
    'EX33/EX50 use twelve extracted regular Chrysler enemy stat blocks, solo and synthetic triples, fixed level 33/50 with logged endgame armor, no PE/items.',
    'Campaign battles retain logged Aya/armor/PE/bag. EX stress cases are not actual tower encounters, pickup-floor progression, or a full EX playthrough.',
    'No scripted Chrysler boss or True Eve validation. Enemy behavior, geometry, fallback attacks, and shot scheduling remain modeled.',
    'Clubs include melee damage, Counter and Quickdraw; Steal/loot utility is not modeled, and gun-style clear times alone cannot value them.',
    'Rocket tests start with 999 reserve rockets; ammo cost/availability and friendly splash are not an economy validation.',
    'Native damage-floor status gating corrected before this run; damage arithmetic checked against native C. No native RNG replay or exact delayed hit/crowd-cap replication.'])
 rows.sort(key=lambda r:(r['stage'],r['id'],r['profile'],r['seed'],r['case'],r['variant']))
 out.write_text(json.dumps(dict(meta=meta,rows=rows),indent=1));print('SAVED',out,flush=True)
if __name__=='__main__':main()
