"""Native pe_mod_effects hook + enemy_movement integer gun damage arithmetic.

Weapon-specific attack bonuses are already included in cfg power by the runner.
Status application, critical conversion rolls, and crowd bookkeeping remain in engine.
"""
VANILLA_SHOT_PCT = {1:100,2:60,3:41,5:25,7:18,10:13}

def hit_damage(offense, power, defense, shots, reaction, element, rules, installed, *, with_positive=False):
    s=int(offense)//5
    p=VANILLA_SHOT_PCT[shots]
    if installed and shots in rules.get('rof_mod_hit_pct',{}):
        atk_pm=200000//(shots*p)
    else:
        atk_pm=int(rules['hit_pct'].get(shots,p))*1000//p
    both_pm=int(element)*10
    want=max(0,((s+int(power))*atk_pm//1000)*both_pm//1000-s)
    want=max(-32768,min(32767,want))
    d=min(65535,int(defense)*both_pm//1000)
    damage=(s+want)*p//100-d//shots
    positive=damage>0
    if damage>0:
        if reaction=='graze':damage=damage*3//10
        elif reaction=='crit':damage=damage*3//2
        elif reaction=='splash':damage=damage//10
    damage=damage if damage>0 else (2 if reaction=='crit' else 1)
    return (damage,positive) if with_positive else damage
