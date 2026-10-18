"""Opt-in linked beam timeline for the full source combat engine.

Schedules and world targets must be supplied explicitly. No chooser probabilities
or parent-counter target are guessed. Enemy legacy movement remains independent.
"""
import json,math
from functools import lru_cache
from pathlib import Path
from .projectile_geometry import point_in_polygon
from .beam_delivery import BeamOwner,BeamPlayer,BeamEmitter,deliver_beams,tick_beam_player

@lru_cache(maxsize=1)
def radii():
    root=Path(__file__).resolve().parents[2]/'findings/data/pe-projectile-geometry-2026-10-18.json'
    rows=json.loads(root.read_text())['aya_disc_models']
    return {(r['costume'],r['kind']):r['cylinder_radius'] for r in rows}

class BeamCombat:
    def __init__(self,schedules,player_config,*,hp,initial=None,foe_count=0):
        required={'max_hp','defense','armor_second','status_step','pe_gauge','x','z'}
        if not required<=player_config.keys():raise ValueError('beam_player missing '+str(sorted(required-player_config.keys())))
        if not math.isfinite(hp) or hp!=int(hp) or not 0<hp<32768:raise ValueError('beams require finite integer starting HP below32768')
        if not 0<player_config['status_step']<=32767:raise ValueError('positive source status decrement required')
        allowed=required|{'armor_first','critical_resist','effect_flags','flags','max_atk','barrier_energy','stiffness_timer','contact_timer','motion','mode','base_mode'}
        if set(player_config)-allowed:raise ValueError('unknown beam player inputs')
        values={k:v for k,v in player_config.items() if k not in ('x','z','pe_gauge')}
        values['atb']=player_config['pe_gauge']
        if values.get('flags',0)&0x200 and not {'max_atk','barrier_energy'}<=player_config.keys():raise ValueError('barrier stats required')
        for key in ('flags','barrier_energy','stiffness_timer','contact_timer','mode'):
            if initial and key in initial:values[key]=initial[key]
        if values.get('flags',0)&0x200 and not {'max_atk','barrier_energy'}<=player_config.keys():raise ValueError('restored barrier requires explicit stats')
        self.player=BeamPlayer(int(hp),**values)
        self.x=player_config['x'];self.z=player_config['z'];self.active_update=0;self.entries=[]
        names=set()
        for spec in schedules:
            required_schedule={'owner','start_update','target_x','target_z','duration','interval','scale'}
            if not required_schedule<=spec.keys():raise ValueError('incomplete beam schedule')
            if set(spec)-(required_schedule|{'effect_chance','counter_target'}):raise ValueError('unknown beam schedule fields')
            if spec['owner'] in names:raise ValueError('beam owners must be unique per encounter')
            names.add(spec['owner'])
            if not isinstance(spec['start_update'],int) or spec['start_update']<0:raise ValueError('invalid beam start')
            target=spec.get('counter_target')
            if target is not None and (not isinstance(target,int) or not 0<=target<foe_count):raise ValueError('invalid explicit counter target')
            owner=BeamOwner(spec['owner'],effect_state=1,scale=spec['scale'],effect_chance=spec.get('effect_chance',50))
            geometry=json.loads((Path(__file__).resolve().parents[2]/'findings/data/pe-projectile-geometry-2026-10-18.json').read_text())
            valid=point_in_polygon(spec['target_x']<<16,spec['target_z']<<16,geometry['floor_polygons'][0]['vertices_integer'])
            emitter=BeamEmitter(owner,spec['target_x'],spec['target_z'],spec['duration'],spec['interval'],target_valid=valid)
            self.entries.append(dict(start=spec['start_update'],emitter=emitter,counter_target=target,reported_done=False))

    def begin_update(self,remaining_hp,roll):
        self.active_update+=1
        if remaining_hp!=int(remaining_hp):raise ValueError('beam HP must remain integer')
        self.player.hp=int(max(0,remaining_hp))&65535
        owners=[e['emitter'].owner for e in self.entries if self.active_update>e['start']]
        result=deliver_beams(self.player,owners,roll)
        tick_beam_player(self.player)
        return result

    def update_effects(self,kind,costume):
        radius=radii()[(costume,kind)];events=[]
        for entry in self.entries:
            age=self.active_update-entry['start']
            if age<=0:continue
            emitter=entry['emitter']
            if emitter.cleanup.finished:continue
            if emitter.update_effect(self.player,age,player_x=self.x,player_z=self.z,player_radius=radius):
                events.append(dict(event='beam_contact',owner=emitter.owner.name,active_update=self.active_update,effect_update=age,radius=radius))
            if emitter.cleanup.finished and not entry['reported_done']:
                events.append(dict(event='beam_cleanup',owner=emitter.owner.name,active_update=self.active_update,effect_update=age))
                entry['reported_done']=True
        return events

    def counter_target(self,owner):
        return next(e['counter_target'] for e in self.entries if e['emitter'].owner.name==owner)

    def state(self):
        p=self.player
        return {key:getattr(p,key) for key in ('flags','barrier_energy','stiffness_timer','contact_timer','mode')}
