"""Read-only checks that the reviewed native defaults match the model profile."""
import hashlib,re
from pathlib import Path

def audit_native(root, expected_progression=None):
    path=Path(root)/'mods/pe_rebalance/pe_mod_effects.c'; text=path.read_text()
    expected={'Heat/Frost neutral %':115,'Heat/Frost weak %':150,'Heat/Frost resist %':80,
        'Heat+Frost best of two':1,'RoF 7 per-shot %':20,'RoF 10 per-shot %':15,
        'Installed RoF volley %':200,'G3A3 attack bonus':45,'M203 4 attack bonus':15,
        'Progression gun bonuses':1,'Attack All crowd cap %':75,'RoF mods: fast volleys':1,
        'Acid/Tranq vs resist %':20,'Acid/Tranq vs normal %':60,'Poison strength %':125,
        'Critical bonus points':40,'Quickdraw bonus points':15,'Attack Down dmg taken %':75,'Slow AT dmg taken %':85}
    for label,value in expected.items():
        match=re.search(r'\{\s*"'+re.escape(label)+r'",\s*"[^"]*",\s*\d+,\s*(\d+)',text)
        if not match or int(match[1])!=value: raise ValueError('Native default changed: '+label)
    table=re.search(r's_prog_guns\[\]\[2\]\s*=\s*\{(.*?)\};',text,re.S)[1]
    actual={int(i,16):int(v) for i,v in re.findall(r'\{\s*0x([0-9A-Fa-f]+)u,\s*(\d+)\s*\}',table)}
    if expected_progression is None:expected_progression={0x79:25,0x7b:15,0x83:20,0x84:15}
    if actual!=expected_progression:raise ValueError('Native progression bonus table changed')
    paths=['mods/pe_rebalance/pe_mod_effects.c','src/main/battle/enemy_movement.c','src/main/battle/character_action.c']
    return dict(defaults=expected,progression=actual,source_hashes={p:hashlib.sha256((Path(root)/p).read_bytes()).hexdigest() for p in paths if (Path(root)/p).exists()})
