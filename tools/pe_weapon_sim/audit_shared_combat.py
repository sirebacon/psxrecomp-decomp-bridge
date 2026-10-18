"""Offline broad-combat coverage audit; no fights or balance experiments."""
import hashlib,json
from collections import Counter
from .enemy_power import ROOT,records,evaluate_power
from .extract_enemy_scripts import PROJECT


def main():
    rows,catalog=records()
    campaign_path=ROOT/'pe-campaign-2026-10-17.json'
    campaign=json.loads(campaign_path.read_text(encoding='utf-8'))
    appearances=[(int(e['map']),int(f['id'],16),f.get('boss',False))
        for e in campaign['events'] if e['type']=='battle' for f in e['enemies']]
    available={key[:2] for key in catalog}
    coverage={}
    for name,subset in [('all',appearances),('normal',[r for r in appearances if not r[2]]),('boss',[r for r in appearances if r[2]])]:
        coverage[name]=dict(logged_appearances=len(subset),any_supported_slot=sum((m,i) in available for m,i,_ in subset),
            supported_slot0=sum((m,i,0) in catalog for m,i,_ in subset))
    source=PROJECT/'parasite-eve-decomp'
    names=['src/main/entity/combat.c','src/main/battle/context.c','src/main/script/value_ops.c',
        'src/main/battle/enemy_actions.c','src/main/script/system_opcodes.c']
    examples=[]
    for key,entry in sorted(catalog.items()):
        examples.append(dict(map=key[0],identity=hex(key[1]),slot=key[2],entry=entry,
            controlled_scale1_power=evaluate_power(entry['expression'],{10:65536}) if entry['expression'].get('shared_cell',10)==10 else None))
    out=dict(scope='Static attack-data coverage and common damage audit, not enemy chooser coverage or balance results',
        rerun_readiness=False,declarations=len(rows),resolved=sum(bool(r['expression']) for r in rows),
        expression_kinds=dict(Counter(r['expression']['kind'] if r['expression'] else 'unresolved' for r in rows)),
        conservative_slot_keys=len(catalog),enemy_identity_keys=len(available),campaign_coverage=coverage,
        inventory_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in
            ('pe-enemy-actions-2026-10-18.json','pe-enemy-scripts-2026-10-18.json','pe-campaign-2026-10-17.json')},
        source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest() for n in names},
        declarations_detail=rows,catalog=examples,
        priority=dict(completed=['source power operands with explicit scales/action slots','shared integer HP/barrier branch','barrier integration regression fix'],
            next=['ordinary enemy action choice and delivery timing','source-earned player defense/armor/status fields','generic incoming status and reactions'],
            deferred=['further hospital boss choreography','balance reruns']),
        limits=['static declaration/identity joins do not prove selected runtime action','shared scale and slot must be supplied',
            'player armor and defense must come from matching state','unmodeled status effects are counted',
            'coverage denominators refer to the existing saved campaign log, not all game encounters'])
    target=ROOT/'pe-shared-combat-coverage-2026-10-18.json'
    target.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in ('declarations','resolved','conservative_slot_keys','enemy_identity_keys','campaign_coverage')},indent=2));print(target)

if __name__=='__main__':main()
