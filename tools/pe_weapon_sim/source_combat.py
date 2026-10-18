"""Source player events with legacy or charge-aware enemy scenarios.

Common charge/status timers and counter rules follow source. Room-script action
selection, missing enemy parameters, geometry and reaction settling are explicit
scenario assumptions. This is not PSX emulation.
"""
import math
import random
import hashlib
from .source_battle import BattleSession,Gun,ammo_pool,signed16
from .source_enemy import EnemyClock,ScriptedEnemy,counter_probability,enemy_damage


def run(rules,cfg,aya,foes,profile,rng,st,resolve_hit,done,*,stat22,guard,enemy_dmg,
        time_cap,max_turns,start_loaded,policy,walk_speed,close_d,close_risk,options,target_first=None,slow=False):
    from .engine import ENEMY_PERIOD,ENEMY_HIT
    options=dict(options or {})
    allowed={'hp','reserve_ammo','weapons','weapon_policy','menu_updates','stream_updates',
             'half_bar','initial_state','trace','enemy_angles','enemy_defaults','enemy_profiles',
             'counter_hp_level','player_rank','counter_reaction_updates','static_enemy_catalog','enemy_action_timing','shared_cells','contact_timing','effect_actions','player_status','projectile_height','linked_beams','beam_player','beam_formation','boss_beam_choice'}
    if set(options)-allowed: raise ValueError('unknown source combat options')
    hz=rules.get('battle_update_hz',59.9/2)
    if hz<=0: raise ValueError('positive battle_update_hz required')
    configs={'primary':cfg,**options.get('weapons',{})}
    initial=options.get('initial_state',{})
    guns={}
    for name,c in configs.items():
        wid=getattr(c.get('weapon'),'id',None);ms=rules.get('mag_scale') or {}
        capacity=max(1,int(c['magazine']*ms.get(wid,ms.get(c['kind'],1))))
        capacity=min(999,capacity)
        loaded=initial.get('loaded',{}).get(name,
            min(start_loaded,capacity) if name=='primary' and start_loaded is not None else capacity)
        guns[name]=Gun(c['kind'],capacity,loaded)
    reserves=initial.get('reserves',options.get('reserve_ammo',
        {ammo_pool(g.kind):999 for g in guns.values() if g.kind!=8}))
    # JSON round trips stringify integer pool keys.
    reserves={int(k) if str(k).isdigit() else k:v for k,v in reserves.items()}
    hp=initial.get('hp',options.get('hp',math.inf));taken=0.;finished_at=None
    beams=None
    if options.get('boss_beam_choice') is not None:
        if 'linked_beams' in options or 'beam_formation' in options:
            raise ValueError('boss_beam_choice is an alternative to explicit beam schedules')
        from .boss_beam_choice import boss_choice_to_launch
        decision=boss_choice_to_launch(**options['boss_beam_choice'])
        options['linked_beams']=decision['linked_beams']
        if decision['linked_beams']:
            player_config=options.get('beam_player',{})
            xyz=options['boss_beam_choice']['player_position']
            if (player_config.get('x'),player_config.get('z'))!=(xyz[0]>>16,xyz[2]>>16):
                raise ValueError('static chooser and beam_player positions must match')
            flags=initial.get('beam_player',{}).get('flags',player_config.get('flags',0))
            if flags&0xc0!=options['boss_beam_choice']['player_flags']&0xc0:
                raise ValueError('chooser and beam_player stiffness state must match')
        st['_boss_beam_choice']=decision
        if decision.get('launch_timing'):st['_beam_launch_timing']=decision['launch_timing']
    if options.get('beam_formation') is not None:
        if 'linked_beams' in options:raise ValueError('provide beam_formation or linked_beams, not both')
        from .beam_launch_timing import formation_launch
        timing=formation_launch(**options['beam_formation'])
        options['linked_beams']=timing['linked_beams']
        st['_beam_launch_timing']=timing
    if options.get('linked_beams'):
        from .beam_combat import BeamCombat
        beams=BeamCombat(options['linked_beams'],options.get('beam_player',{}),hp=hp,
            initial=initial.get('beam_player'),foe_count=len(foes))
    initial_rounds=sum(g.loaded for g in guns.values())+sum(reserves.values())
    for f in foes:
        f['angle']=options.get('enemy_angles',{}).get(f['i'],rng.randrange(-2048,2048))
    qd=0.
    if cfg['eff'].get('quickdraw'):
        qd=max(stat22,min(90,stat22+rules['quickdraw_bonus']))/100
    gauge=initial.get('gauge',9000 if rng.random()<qd else 0)
    st['quickdraw']=int(gauge==9000)
    pending_counter=None
    enemy_profiles=[];enemy_scripts=[]
    # shared_cells (e.g. enemy_identity.FIRST_RUN_SHARED_CELLS): scaled-rank identities in every
    # catalog and the default source power scale; an explicit profile source_shared_cells wins.
    cells=options.get('shared_cells')
    for f in foes:
        p=dict(options.get('enemy_defaults',{}))
        if options.get('static_enemy_catalog'):
            from .enemy_catalog import lookup
            extracted=lookup(f,cells)
            p.update(extracted)
            st.add('catalog_matches',int(bool(extracted)))
            st.add('catalog_foes')
        if options.get('enemy_action_timing'):
            from .enemy_catalog import timing_profile
            action=timing_profile(f,options['enemy_action_timing'],cells)
            p.update(action)
            st.add('action_timing_matches',int(bool(action)))
        contact=None
        if options.get('contact_timing') and not (options.get('enemy_action_timing') and action):
            # Bounded scenario: category-2 contact inside the action's own clips (contact_timing.py).
            from .contact_timing import contact_profile
            contact=contact_profile(f,options['contact_timing'],cells)
            p.update({k:contact[k] for k in ('windup','recovery','reset_on_completion')} if contact else {})
            st.add('contact_timing_matches',int(bool(contact)))
        effect=None
        if options.get('effect_actions') and not ((options.get('enemy_action_timing') and action) or contact):
            # Effect-driven slot-3 action (effect_actions.py / room_effects.py), only where no other
            # source timing resolved; its slot drives power unless an explicit profile sets one.
            from .effect_actions import effect_profile
            effect=effect_profile(f,cells) or None
            st.add('effect_action_matches',int(bool(effect)))
            if effect and 'source_action_slot' in p and 'source_action_slot' not in options.get('enemy_profiles',{}).get(f['i'],{}):
                p['source_action_slot']=effect['slot']
        p.update(options.get('enemy_profiles',{}).get(f['i'],{}))
        if 'source_action_slot' in p:
            from .enemy_power import power_profile
            selected=power_profile(f,p['source_action_slot'],p.get('source_shared_cells',cells or {}),scaled_identities=bool(cells))
            if options.get('enemy_action_timing') and selected:
                from .enemy_catalog import action_catalog
                from .enemy_identity import cells_key
                rows=action_catalog(cells_key(cells)).get((int(f['loc']),int(f['name'],16)),[])
                if rows:
                    choose=min if options['enemy_action_timing']=='fast' else max
                    timed=choose(rows,key=lambda a:(a['windup']+a['recovery'],a['windup'],a['slot']))
                    if timed['slot']!=p['source_action_slot']:raise ValueError('timing and power slots differ')
            if contact and selected and contact['slot']!=p['source_action_slot']:
                raise ValueError('contact timing and power slots differ')
            if effect and selected and effect['slot']!=p['source_action_slot']:
                raise ValueError('effect action and power slots differ')
            p={**selected,**p} # Explicit profile overrides remain authoritative.
            st.add('power_catalog_foes');st.add('power_catalog_matches',int(bool(selected)))
        enemy_profiles.append(p)
        periodic=p.get('periodic_damage',30 if f['boss'] else 2+f['level']//8)
        if not p.get('periodic_damage_is_current',False): periodic=int(periodic*rules['poison_pct']/100)
        clock=EnemyClock(p.get('charge_step',90),charge=p.get('initial_charge',0),periodic_damage=periodic)
        if options.get('projectile_height') is not None and str(f.get('loc'))=='156' and f.get('name')=='0x0216':
            from .source_projectile import OrbEnemy
            enemy_scripts.append(OrbEnemy(clock,distance=f['dist'],rng=random.Random(int.from_bytes(hashlib.sha256(repr(rng.getstate()).encode()).digest()[:8],'little')),height=options['projectile_height']))
            st.add('projectile_model_matches')
        elif effect:
            from .effect_actions import EffectEnemy
            from .beam_combat import radii
            scenario=options['effect_actions'] if isinstance(options['effect_actions'],dict) else None
            seed=int.from_bytes(hashlib.sha256(('effect%d'%f['i']+repr(rng.getstate())).encode()).digest()[:8],'little')
            enemy_scripts.append(EffectEnemy(clock,effect,distance=f['dist'],aya_radius=radii()[(0,cfg['kind'])],
                                             scenario=scenario,rng=random.Random(seed)))
        else:
            enemy_scripts.append(ScriptedEnemy(clock,windup=p.get('windup',10),recovery=p.get('recovery',10),reset_on_completion=p.get('reset_on_completion',False)))

    status=None
    if options.get('player_status'):
        # Aya's incoming ailments (player_status.py); the beam adapter keeps its own player model.
        if beams:raise ValueError('player_status and beam encounters use separate player models')
        missing={'status_step3c','status_step3e'}-set(aya)
        if missing:raise ValueError('player_status needs aya '+str(sorted(missing))+' (source_stats.player_inputs)')
        from .player_status import PlayerStatus
        status=PlayerStatus(aya['status_step3c'],aya['status_step3e'],effect_flags=aya.get('armor_effect_flags',0))

    def stopped():
        return done() or taken>=hp or session.update/hz>=time_cap

    def on_update(session,paused):
        nonlocal taken,finished_at,pending_counter
        now=session.update/hz
        if now>time_cap or done() or taken>=hp: return
        if paused:
            for f in foes:
                f['t_next']+=1/hz
                if 'ptime' in f: f['ptime']+=1/hz
            return
        if status:
            lost=status.tick()                       # Entity_UpdateTimers, once per battle update
            if lost:
                taken+=lost;st.add('player_poison',lost);session.event('player_poison',damage=lost)
                if taken>=hp: finished_at=now;return
            session.slow=slow or status.stiff
        if beams:
            result=beams.begin_update(hp-taken,lambda:rng.randrange(100))
            for event in result['events']:
                hurt=event['damage'] if not event['barrier'] else 0
                taken+=hurt;st.add('hits_taken');st.add('beam_hits');st.add('beam_damage',hurt)
                session.event('beam_hit',**event)
                target=beams.counter_target(event['owner'])
                if not event['barrier']:
                    pending_counter=(target,session.update+options.get('counter_reaction_updates',21)) if target is not None else None
                    if target is None:st.add('beam_counter_unresolved')
            session.slow=slow or beams.player.flags&0xc0 in (0x40,0x80)
            session.haste=bool(beams.player.flags&0x100)
            if taken>=hp:finished_at=now;return
        for f in foes:
            if f['cur']<=0: continue
            p=enemy_profiles[f['i']]
            if rules.get('enemy_model')=='charge':
                script=enemy_scripts[f['i']];clock=script.clock
                if f['poisoned'] and not clock.flags&0x10: clock.flags=(clock.flags|0x10)&~0x3E0
                if f['stopped']>((clock.flags>>11)&3): clock.flags|=0x1800;clock.actor_flags|=0x1000
                if hasattr(script,'distance') and script.phase=='charge':script.distance=f['dist']
                previous_projectiles=getattr(script,'projectiles',0)
                strike,damage=script.tick()
                st.add('projectiles_launched',getattr(script,'projectiles',0)-previous_projectiles)
                geometric=getattr(script,'last_strike_geometric',False)
                if geometric:st.add('projectile_contacts')
                f['stopped']=(clock.flags>>11)&3
                if damage:
                    actual=min(damage,max(0.,f['cur']));f['dealt']+=actual;f['cur']-=damage
                    st.add('poison',actual)
                    if done(): finished_at=now;break
                    if f['cur']<=0: continue
                if not strike: continue
            elif now<f['t_next']: continue
            close=f['dist']<450
            f['t_next']=now+rng.uniform(*ENEMY_PERIOD)
            f['dist']=profile.sample(rng)
            if rules.get('enemy_model')!='charge' and f['poisoned']:
                pd=(30 if f['boss'] else 2+f['level']//8)*rules['poison_pct']/100
                damage=pd*(now-f.get('ptime',now))*hz/31
                f['ptime']=now;f['dealt']+=damage;f['cur']-=damage;st.add('poison',damage)
                if done(): finished_at=now;break
                if f['cur']<=0: continue
            if rules.get('enemy_model')!='charge' and f['stopped']>0:
                f['stopped']-=1;continue
            if rng.random()<min(1.,(1. if rules.get('enemy_model')=='charge' and geometric else p.get('hit_probability',ENEMY_HIT))*(1+(close_risk if close else 0.))):
                barrier=False
                st.add('explicit_power_hits' if 'power' in p else 'legacy_damage_hits')
                if beams and 'power' in p:
                    if guard!=1:raise ValueError('source player HP/barrier state requires guard=1')
                    from .incoming_damage import resolve_incoming
                    from .beam_delivery import stiffness_lock
                    beams.player.hp=int(max(0,hp-taken))&65535
                    result=resolve_incoming(beams.player,owner=str(f['i']),power=p['power'],
                        action_slot=p.get('action_slot',0),effect_type=p.get('effect_type',0),
                        effect_chance=p.get('critical_chance',0),roll=lambda:rng.randrange(100))
                    barrier=result['barrier'];hurt=0 if barrier else result['damage']
                    if p.get('effect_type')==5:stiffness_lock(beams.player,lambda:rng.randrange(100))
                    elif p.get('effect_type',0):st.add('incoming_status_unmodeled')
                    beams.player.flags &= ~0x8000
                    if barrier:
                        session.event('enemy_barrier_hit',target=f['i'],damage=result['damage'])
                        st.add('hits_taken');continue
                elif 'power' in p:
                    # Player-side defense (Inv_BuildArmorList) comes from aya; an explicit per-enemy
                    # profile value still overrides it (older fixtures put it there).
                    hurt,_=enemy_damage(p['power'],aya.get('defense',0),
                        armor_first=p.get('armor_first',aya.get('armor_first',0)),
                        armor_second=p.get('armor_second',aya.get('armor_second',0)),
                        action_slot=p.get('action_slot',0),effect_chance=p.get('critical_chance',0),
                        critical_resist=p.get('critical_resist',aya.get('critical_resist',0)),roll=rng.randrange(100),
                        effect_type=p.get('effect_type',0),charged_guard=p.get('charged_guard',False),
                        player_flags=p.get('player_flags',0)|(status.flags&0x1100 if status else 0))
                    hurt*=guard
                    if status and p.get('effect_type',0):
                        # Battle_ApplyEnemyAttack after every resolved hit, damage or not.
                        now_hp=int(hp-taken-hurt)
                        new_hp,what=status.apply(p['effect_type'],p.get('status_level',0),p.get('status_period',0),
                                                 lambda:rng.randrange(1<<15),now_hp)
                        hurt+=now_hp-new_hp
                        st.add('status_'+what.replace(' ','_'))
                        if what=='unmodelled' or p['effect_type']==3:st.add('incoming_status_unmodeled')
                    elif p.get('effect_type',0):st.add('incoming_status_unmodeled')
                else:
                    if beams:raise ValueError('beam encounters require source power profiles for enemy hits')
                    hurt=(enemy_dmg(f) if enemy_dmg else 1.6*f['level'])*guard
                taken+=hurt;st.add('hits_taken')
                session.event('enemy_hit',target=f['i'],damage=hurt)
                # One global pending attacker: later eligible hits replace it.
                pending_counter=(f['i'],session.update+options.get('counter_reaction_updates',21))
                if taken>=hp: finished_at=now;break

        if beams:
            for event in beams.update_effects(session.gun.kind,session.costume):
                kind=event.pop('event');session.event(kind,**event)
                st.add('beam_contacts' if kind=='beam_contact' else 'beam_cleanups')

    session=BattleSession(guns,reserves,initial.get('equipped','primary'),stat22=stat22,
        gauge=gauge,costume=rules.get('animation_costume',0),seed=rng.getrandbits(32),
        on_update=on_update,should_stop=stopped)
    session.slow=slow or bool(beams and beams.player.flags&0xc0 in (0x40,0x80))
    if beams:session.haste=bool(beams.player.flags&0x100)

    def active_cfg():
        # Darkness: hit evaluation and targeting use range 200 (battle/setup.c, turn.c).
        c=configs[session.equipped]
        return dict(c,range=200) if status and status.dark else c

    def hit(event):
        nonlocal finished_at
        resolve_hit(event,active_cfg(),session.update/hz)
        if done(): finished_at=session.update/hz

    def try_counter():
        nonlocal pending_counter
        if session.action_busy or pending_counter is None or stopped(): return
        target,ready=pending_counter
        active=configs[session.equipped];effect=active['eff']
        if not effect.get('counter') or session.update<ready: return
        pending_counter=None
        if foes[target]['cur']<=0: return
        if not enemy_profiles[target].get('counter_eligible',True): return
        rank=enemy_profiles[target].get('rank',foes[target].get('rank',foes[target]['level']))
        chance=counter_probability(options.get('counter_hp_level',aya.get('hp_level',aya['level']*10)),
            options.get('player_rank',aya.get('rank',aya['level']))-rank)
        chance=min(1.,chance*rules.get('counter_mult',1.))
        st.add('counter_checks')
        if rng.randrange(100)>=round(chance*100): return
        st.add('counters')
        session.attack(counter=True,rof=effect.get('rof',1),commands=1,mode=effect.get('mode'),
            targets=[f['i'] for f in foes if f['cur']>0],selected=target,
            target_alive=lambda i:foes[i]['cur']>0,target_angles={f['i']:f['angle'] for f in foes},
            player_angle=lambda i:signed16(foes[i]['angle']+0x800),on_hit=hit)

    session.on_idle=try_counter

    while not stopped() and not (max_turns and st.get('turns',0)>=max_turns):
        try_counter()
        if pending_counter and configs[session.equipped]['eff'].get('counter'):
            session.advance(max(0,pending_counter[1]-session.update))
            try_counter()
        if stopped(): break
        choose=options.get('weapon_policy')
        if choose:
            name=choose(dict(equipped=session.equipped,gauge=session.gauge,turns=st.get('turns',0),
                foes=[dict(f) for f in foes],loaded={k:g.loaded for k,g in session.guns.items()},
                reserves=dict(session.reserves)))
            if name not in configs: raise ValueError('weapon policy selected an unowned weapon')
            if name!=session.equipped:
                session.switch(name,half_bar=options.get('half_bar',True),
                    menu_updates=options.get('menu_updates',0),stream_updates=options.get('stream_updates',0))
                st.add('switches')
        session.wait_gauge()
        if stopped(): break
        current=active_cfg();alive=[f for f in foes if f['cur']>0]
        inr=[f for f in alive if f['dist']<=current['range']]
        target=(foes[target_first] if target_first is not None and foes[target_first]['cur']>0
                else min(inr or alive,key=lambda f:f['cur']))
        if policy in ('approach','walk','close_in') and target['dist']>current['range']:
            if (beams and beams.player.flags&0xc0==0x80) or (status and status.locked):
                session.advance();st.add('stiffness_movement_wait');continue
            want=close_d if policy=='close_in' and close_d else .9*current['range']
            delay=.6 if policy=='approach' else max(0.,(target['dist']-want)/walk_speed)
            session.advance(math.ceil(delay*hz));st.add('move_s',delay)
            target['dist']=want
        if stopped(): break
        st.add('turns');start=session.update
        session.attack(rof=current['eff'].get('rof',1),commands=current['eff'].get('commands',1),
            mode=current['eff'].get('mode'),targets=[f['i'] for f in alive],selected=target['i'],
            target_alive=lambda i:foes[i]['cur']>0,target_angles={f['i']:f['angle'] for f in foes},
            player_angle=lambda i:signed16(foes[i]['angle']+0x800),on_hit=hit)
        st.add('commit_s',(session.update-start)/hz)
    st['time']=min(time_cap,finished_at if finished_at is not None else session.update/hz)
    st['damage_taken']=taken;st['loaded_left']=session.gun.loaded;st['won']=int(done())
    st['reserve_left']=sum(session.reserves.values())
    st['rounds']=sum(e['event']=='fire' and session.guns[e['weapon']].kind!=8 for e in session.events)
    st['reloads']=sum(e['event']=='ammo_transfer' for e in session.events)
    st['click']=sum(e['event']=='empty_click' for e in session.events)
    st['ammo_balance']=initial_rounds-sum(g.loaded for g in session.guns.values())-st['reserve_left']-st['rounds']
    st['_source_state']=dict(equipped=session.equipped,gauge=session.gauge,
        loaded={k:g.loaded for k,g in session.guns.items()},reserves=dict(session.reserves))
    if math.isfinite(hp): st['_source_state']['hp']=max(0.,hp-taken)
    if beams:
        st['_source_state']['beam_player']=beams.state()
        st['_beam_state']=dict(active_update=beams.active_update,player=beams.state(),
            effects=[dict(owner=e['emitter'].owner.name,held=e['emitter'].held,effect_state=e['emitter'].owner.effect_state,finished=e['emitter'].cleanup.finished) for e in beams.entries])
    if options.get('trace'): st['_source_events']=session.events
    if options.get('trace') and rules.get('enemy_model')=='charge':
        st['_enemy_clocks']=[dict(charge=s.clock.charge,flags=s.clock.flags,phase=s.phase) for s in enemy_scripts]
    return st
