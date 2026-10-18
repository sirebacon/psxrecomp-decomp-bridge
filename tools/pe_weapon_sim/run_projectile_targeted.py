"""Focused map156 boss comparison with fixed, aligned 1D distance scenarios."""
import argparse,json,statistics,random,hashlib
from pathlib import Path
from .run_behavior_balance import GROUPS,config
from .economy import evaluation,tables
from .decomp_animation import source_behavior_rules
from . import engine,rules

class Fixed:
    def __init__(self,distance):self.distance=distance
    def sample(self,rng):return self.distance

def main():
    root=Path(__file__).resolve().parents[2]/'findings'
    historical=json.loads((root/'data/pe-weapon-p3-completion-2026-10-17.json').read_text())
    foe=next(f for f in evaluation.BOSSES['D5'] if str(f['loc'])=='156' and f['name']=='0x0216')
    records=[];total=0
    for height in (0,320,640):
        for group in GROUPS:
            for run in historical['raw']['overlap|'+group][:8]:
                cp=run['cps']['D5'];cfg=config(cp)
                aya=dict(level=cp['level'],stat22=cp['stat22'],offense=tables.offense_of(cp['level']),hp_level=cp['level']*10)
                armor=dict(slow_at='SlowAT'in cp['armor_mods'],attack_levels=cp['armor_mods'].count('AttackUp')-cp['armor_mods'].count('AttackDown'))
                for distance in (1000,1300,2000,4000):
                    fights=[]
                    for i in range(3):
                        result=engine.fight(source_behavior_rules(rules.CURRENT),cfg,aya,[foe],Fixed(distance),random.Random(run['seed']*7919+i),armor=armor,time_cap=90,
                            source_options=dict(hp=385,reserve_ammo={0:999,1:999,2:999},static_enemy_catalog=True,enemy_action_timing='fast',projectile_height=height or None))
                        assert result['ammo_balance']==0;fights.append(result);total+=1
                    records.append(dict(height=height,group=group,seed=run['seed'],distance=distance,won=statistics.mean(f['won'] for f in fights),time=statistics.mean(f['time'] for f in fights),damage_taken=statistics.mean(f['damage_taken'] for f in fights),launched=sum(f.get('projectiles_launched',0) for f in fights),contacts=sum(f.get('projectile_contacts',0) for f in fights)))
        print('Completed focused height',height,flush=True)
    aggregates=[]
    for height in (0,320,640):
        for distance in (1000,1300,2000,4000):
            rs=[r for r in records if r['height']==height and r['distance']==distance]
            aggregates.append(dict(height=height,distance=distance,win=statistics.mean(r['won'] for r in rs),time=statistics.mean(r['time'] for r in rs),damage_taken=statistics.mean(r['damage_taken'] for r in rs),launched=sum(r['launched'] for r in rs),contacts=sum(r['contacts'] for r in rs)))
    path=root/'data/pe-projectile-targeted-2026-10-18.json'
    path.write_text(json.dumps(dict(meta=dict(total_fights=total,seeds=8,fights_per_cell=3,foe=foe,scope='fixed D5 earned loadouts; fixed aligned 1D stationary point player; outer chooser gates assumed; height0 means old melee-only scenario',projectile_extract_sha256=hashlib.sha256((root/'data/pe-projectile-extract-2026-10-18.json').read_bytes()).hexdigest()),aggregates=aggregates,records=records),indent=2))
    print('Wrote focused fights',total,flush=True)
if __name__=='__main__':main()
