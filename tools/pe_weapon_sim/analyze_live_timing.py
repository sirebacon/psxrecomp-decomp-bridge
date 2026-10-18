"""Extract auditable gauge/switch facts from frame-ring captures, not host timings."""
import json
from collections import Counter
from .live_probe import SESSION


def analyze(capture):
    rows=capture['rows']; changes=[]; gains=[]; switches=[]; ammo=[]
    for a,b in zip(rows,rows[1:]):
        if b['frame']!=a['frame']+1: raise ValueError('noncontiguous capture')
        delta=b['gauge']-a['gauge']
        if delta:
            changes.append(dict(frame=b['frame'],before=a['gauge'],after=b['gauge'],flags=b['flags']))
        if delta>0 and b['gauge']<9000 and a['fill_rate']==b['fill_rate'] and a['entity']==b['entity']:
            gains.append((b['frame'],delta,b['fill_rate']))
        if a.get('weapon_slot')!=b.get('weapon_slot'):
            switches.append(dict(frame=b['frame'],before=a.get('weapon_slot'),after=b.get('weapon_slot'),
                gauge_before=a['gauge'],gauge_after=b['gauge'],rate_before=a['fill_rate'],rate_after=b['fill_rate']))
        valid_ammo = all(r.get('action_sample_valid', True) for r in (a,b))
        if valid_ammo and 'ammo' in a and a['ammo']!=b['ammo']:
            ammo.append(dict(frame=b['frame'],before=a['ammo'],after=b['ammo']))
    gaps=[b[0]-a[0] for a,b in zip(gains,gains[1:]) if a[1:]==b[1:]]
    return dict(label=capture['label'],frames=len(rows),hp_start=rows[0]['hp'],hp_end=rows[-1]['hp'],
        gauge_min=min(r['gauge'] for r in rows),gauge_max=max(r['gauge'] for r in rows),
        gain_counts=dict(Counter(str((delta,rate)) for _,delta,rate in gains)),
        gain_gap_vblanks=dict(Counter(map(str,gaps))),gauge_changes=changes,weapon_changes=switches,
        ammo_changes=ammo,pause_flag_frames=sum(bool(r['flags']&0x100) for r in rows),
        paused_gauge_increases=sum(b['gauge']>a['gauge'] and bool(a['flags']&0x100) and bool(b['flags']&0x100)
            for a,b in zip(rows,rows[1:])))


def main():
    out=[]
    for path in sorted(SESSION.glob('*.json')):
        d=json.loads(path.read_text(encoding='utf-8'))
        if 'rows' in d: out.append(analyze(d))
    (SESSION/'measurement-summary.json').write_text(json.dumps(out,indent=1),encoding='utf-8')
    for r in out:
        print(r['label'],'gains',r['gain_counts'],'gap',r['gain_gap_vblanks'],
              'switches',r['weapon_changes'],'ammo',r['ammo_changes'],'paused',r['pause_flag_frames'])


if __name__=='__main__':main()
