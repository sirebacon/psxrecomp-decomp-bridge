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
from .enemy_choice import GatedEnemy


def run(rules,cfg,aya,foes,profile,rng,st,resolve_hit,done,*,stat22,guard,enemy_dmg,
        time_cap,max_turns,start_loaded,policy,walk_speed,close_d,close_risk,options,target_first=None,slow=False):
    from .engine import ENEMY_PERIOD,ENEMY_HIT
    options=dict(options or {})
    allowed={'hp','reserve_ammo','weapons','weapon_policy','menu_updates','stream_updates',
             'half_bar','initial_state','trace','enemy_angles','enemy_defaults','enemy_profiles',
             'counter_hp_level','player_rank','counter_reaction_updates','static_enemy_catalog','enemy_action_timing','shared_cells','contact_timing','effect_actions','enemy_choice','melee_window','melee_reach','called_slots','reaction_updates','switch_cost','hit_trace','player_status','projectile_height','linked_beams','beam_player','beam_formation','boss_beam_choice','atb_guard','logged_charge','player_evade','reaction_paused','serial_action','pe','player_max_hp','player_evade_melee','identity_rank','steals','contact_damage'}
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
    hp=initial.get('hp',options.get('hp',math.inf));taken=0.;healed=0.;finished_at=None
    pe=None
    if options.get('pe'):
        from .parasite_energy import PE
        pe=PE(aya.get('level',1),**options['pe'])
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
    if options.get('melee_reach') and not (options.get('melee_window') or options.get('enemy_choice') or options.get('called_slots')):
        raise ValueError('melee_reach needs melee_window or enemy_choice (it applies to melee window strikes)')
    for f in foes:
        p=dict(options.get('enemy_defaults',{}));extracted={}
        if options.get('static_enemy_catalog'):
            from .enemy_catalog import lookup
            extracted=lookup(f,cells)
            p.update(extracted)
            st.add('catalog_matches',int(bool(extracted)))
            st.add('catalog_foes')
        if options.get('logged_charge') and 'charge_step' not in extracted and 'charge_step' not in options.get('enemy_profiles',{}).get(f['i'],{}):
            # Labelled fallback (logged_charge.py): the runtime charge step from the play log for
            # identities whose scripts give no single literal field 0x3E.
            from .logged_charge import lookup as logged_lookup
            step=logged_lookup(f)
            if step:p['charge_step']=step;st.add('logged_charge_foes')
        gated=None
        if options.get('enemy_choice'):
            # Distance-gated attack choice (enemy_choice.py): per-slot timing and power.
            from .enemy_choice import slot_plans
            choice=options['enemy_choice'] if isinstance(options['enemy_choice'],dict) else {}
            gated=slot_plans(f,cells,choice.get('contact','early'),untimed=tuple(choice.get('untimed',(10,10))),throw_lateral=choice.get('throw_lateral',0)) or None
            st.add('choice_matches',int(bool(gated)))
        if not gated and options.get('called_slots'):
            # The slots the identity's scripts actually call (enemy_choice.called_plans), each
            # with its own timing and power; several unguarded slots = labelled uniform choice.
            from .enemy_choice import called_plans
            choice=dict(options['called_slots'] if isinstance(options['called_slots'],dict) else {},ambiguous='uniform')
            vrng=random.Random(int.from_bytes(hashlib.sha256(('variant%d'%f['i']+repr(rng.getstate())).encode()).digest()[:8],'little')) if choice.get('variants',True) else None
            gated=called_plans(f,cells,choice.get('contact','early'),untimed=tuple(choice.get('untimed',(10,10))),throw_lateral=choice.get('throw_lateral',0),variant_rng=vrng,by_hp=bool(choice.get('actor_by_hp'))) or None
            if gated and any(p.get('variant') is not None for p in gated.values()):st.add('called_slot_variant_picks')
            st.add('called_slot_matches',int(bool(gated)));st.add('called_slot_foes')
            if gated and len(gated)>1:st.add('called_slot_unguarded_multi')
            if not gated and choice.get('borrow'):
                # Opt-in, labelled: the same identity's agreed plans from other rooms (enemy_choice.borrowed_plans).
                from .enemy_choice import borrowed_plans
                gated,_rooms=borrowed_plans(f,cells,contact=choice.get('contact','early'),untimed=tuple(choice.get('untimed',(10,10))))
                gated=gated or None
                if gated:st.add('called_slot_borrowed')
            if gated and choice.get('actor_by_hp'):
                # Opt-in: the foe's HP resolves its actor type within a shared identity; an actor with no
                # declared action and no command can't strike (enemy_choice.unarmed_actor).
                from .enemy_choice import unarmed_actor
                if unarmed_actor(f,cells):gated=None;p['no_contact']=True;st.add('called_slot_unarmed_actor')
            if not gated and choice.get('silent'):
                # Opt-in: every resolving actor's whole flow lacks commands / effects / PM sends
                # (enemy_choice.silent_identity), so it never attacks; its strikes do nothing.
                from .enemy_choice import silent_identity
                if silent_identity(f,cells):p['no_contact']=True;st.add('called_slot_silent_foes')
        if gated:
            if options.get('melee_reach'):
                from .enemy_reach import reach_rows
                reach=reach_rows(f,cells)
                for slot,plan in gated.items():
                    if plan['kind']=='window' and slot in reach and plan['power']:
                        plan['power']=dict(plan['power'],melee_reach_units=reach[slot])
        if options.get('enemy_action_timing') and not gated:
            from .enemy_catalog import timing_profile
            action=timing_profile(f,options['enemy_action_timing'],cells)
            p.update(action)
            st.add('action_timing_matches',int(bool(action)))
        melee=None
        if not gated and options.get('melee_window'):
            # Source contact window for a slot 0-2 action (melee_window.py), bound 'early' / 'late';
            # supersedes enemy_action_timing / contact_timing for the foes it resolves.
            from .melee_window import melee_rows
            bound=options['melee_window']
            if bound not in ('early','late'):raise ValueError("melee_window must be 'early' or 'late'")
            rows=melee_rows(f,cells)
            want={**options.get('enemy_defaults',{}),**options.get('enemy_profiles',{}).get(f['i'],{})}.get('source_action_slot')
            if want is not None: melee=rows.get(want)
            elif rows: melee=(min if bound=='early' else max)(rows.values(),key=lambda r:(r['complete'],r['slot']))
            if melee:
                if options.get('enemy_action_timing') and action:
                    for k in ('windup','recovery','reset_on_completion'):p.pop(k,None)
                p.update(melee[bound],reset_on_completion=melee['reset_on_completion'])
                if 'source_action_slot' in p:p['source_action_slot']=melee['slot']
                action=None
                if options.get('melee_reach'):
                    from .enemy_reach import reach_rows
                    reach=reach_rows(f,cells).get(melee['slot'])
                    if reach is not None:p['melee_reach_units']=reach
            st.add('melee_window_matches',int(bool(melee)))
        contact=None
        if not gated and not melee and options.get('contact_timing') and not (options.get('enemy_action_timing') and action):
            # Bounded scenario: category-2 contact inside the action's own clips (contact_timing.py).
            from .contact_timing import contact_profile
            contact=contact_profile(f,options['contact_timing'],cells)
            p.update({k:contact[k] for k in ('windup','recovery','reset_on_completion')} if contact else {})
            st.add('contact_timing_matches',int(bool(contact)))
        effect=None
        if not gated and not melee and options.get('effect_actions') and not ((options.get('enemy_action_timing') and action) or contact):
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
            def realign(slot):
                # called_slots mode: timing and power must describe the same attack, so take the
                # timed slot's own power; without it the strike stays fallback damage (counted).
                alt=power_profile(f,slot,p.get('source_shared_cells',cells or {}),scaled_identities=bool(cells),default_critical=True)
                st.add('timing_slot_realigned' if alt else 'timing_slot_unpowered')
                if alt:p['source_action_slot']=slot
                return alt
            if options.get('enemy_action_timing') and selected and not gated and not melee:
                from .enemy_catalog import action_catalog
                from .enemy_identity import cells_key
                rows=action_catalog(cells_key(cells)).get((int(f['loc']),int(f['name'],16)),[])
                if rows:
                    choose=min if options['enemy_action_timing']=='fast' else max
                    timed=choose(rows,key=lambda a:(a['windup']+a['recovery'],a['windup'],a['slot']))
                    if timed['slot']!=p['source_action_slot']:
                        if not options.get('called_slots'):raise ValueError('timing and power slots differ')
                        selected=realign(timed['slot'])
            if contact and selected and contact['slot']!=p['source_action_slot']:
                if not options.get('called_slots'):raise ValueError('contact timing and power slots differ')
                selected=realign(contact['slot'])
            if effect and selected and effect['slot']!=p['source_action_slot']:
                if not options.get('called_slots'):raise ValueError('effect action and power slots differ')
                selected=realign(effect['slot'])
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
        elif gated:
            from .beam_combat import radii
            seed=int.from_bytes(hashlib.sha256(('choice%d'%f['i']+repr(rng.getstate())).encode()).digest()[:8],'little')
            enemy_scripts.append(GatedEnemy(clock,gated,distance=f['dist'],aya_radius=radii()[(0,cfg['kind'])],
                                            rng=random.Random(seed),scenario=choice.get('scenario'),ambiguous=choice.get('ambiguous','first')))
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

    max_hp_real=min(hp,options.get('player_max_hp',hp))   # Aya's max HP (calibration runs an unbounded cap; may be inf)
    armor_fx=aya.get('armor_effect_flags',0)

    def cur_hp(): return max_hp_real-(taken-healed)

    def heal(amount):
        nonlocal healed
        amount=max(0,min(amount,taken-healed));healed+=amount;return amount

    hold=[0]                # post-revive immunity updates (0x800000)
    contact=[0]             # Aya's 0x01000000 window (contact damage blocked)
    contact_vals={}
    if options.get('contact_damage'):
        from .contact_damage import contact_of
        from .enemy_identity import cells_key
        ck=cells_key(options.get('shared_cells',{}))
        contact_vals={f['i']:contact_of(f,ck) for f in foes}
        crng=random.Random(int.from_bytes(hashlib.sha256(('contact'+repr(rng.getstate())).encode()).digest()[:8],'little'))   # own stream, seeded without drawing

    def dead():
        """Out of HP, after Preraise / Revive (battle/encounter.c: phase 3 takes Preraise 0x800 first,
        then a Revive item 0x12; Battle_StepVictory case 7: HP = maxHP/2, PE >>= 2; Battle_ResetEnemyStats:
        gauge 0, ailments and buffs cleared; mode 1 sets Aya 0x800000 with timer 0x5A: Menu_MainUpdate resolves no
        enemy hit or contact while it runs -> 90 updates of immunity, hold_left)."""
        nonlocal healed
        if taken-healed<hp: return False
        if not pe: return True
        if pe.preraise: pe.preraise=False;how='preraise'
        elif pe.bag.get(0x12): pe.bag[0x12]-=1;how='item'
        else: return True
        healed=taken-hp+max_hp_real//2
        pe.pe>>=2;pe.barrier=pe.gene=False;pe.haste_left=0;session.haste=False;session.gauge=0
        if status: status.flags&=~0x1FFF
        hold[0]=0x5A
        st.add('revived');st.add('revive_'+how)
        return False

    def upkeep():
        """Entity_UpdateTimers (entity/combat.c) after the ailment timers: Gene Heal, armor auto-medicine
        (effect 0x4000) and auto-cure (0x8000), using the battle bag (pe.bag)."""
        if pe.gene:
            # +1 HP per update (the draw-slot gate is taken as always open: the log shows 1 HP per tick),
            # PE -= maxPE / (level * 30) (field04 = level), ends at PE <= 1.
            if heal(1): st.add('gene_healed')
            pe.pe-=pe.max//(max(1,aya.get('level',1))*30)
            if pe.pe<=0x10000: pe.pe=0x10000;pe.gene=False
        if armor_fx&0x4000:
            while 0<cur_hp()<max_hp_real//5:
                item=next((i for i in (0x0A,0x09,0x08,0x07,0x06) if pe.bag.get(i)),None)
                if item is None: break
                pe.bag[item]-=1;st.add('auto_medicine');st.add('item_%02X'%item)
                st.add('pe_healed',heal(max_hp_real if item==0x0A else {6:45,7:90,8:180,9:400}[item]))
        if armor_fx&0x8000 and status:
            for mask,bit,item in ((0x3,0x1,0x0D),(0xC,0x4,0x0F),(0x30,0x10,0x0E)):
                if status.flags&mask==bit:
                    use=item if pe.bag.get(item) else 0x11 if pe.bag.get(0x11) else None
                    if use: pe.bag[use]-=1;status.flags&=~mask;st.add('auto_cure')
            if status.flags&0xC0 in (0x40,0x80):
                use=0x10 if pe.bag.get(0x10) else 0x11 if pe.bag.get(0x11) else None
                if use: pe.bag[use]-=1;status.flags&=~0xC0;st.add('auto_cure')
            if status.flags&0x1000 and pe.bag.get(0x11): pe.bag[0x11]-=1;status.flags&=~0x1000;st.add('auto_cure')

    def stopped():
        return done() or dead() or session.update/hz>=time_cap

    def on_update(session,paused):
        nonlocal taken,finished_at,pending_counter
        now=session.update/hz
        if now>time_cap or done() or dead(): return
        if paused:
            for f in foes:
                f['t_next']+=1/hz
                if 'ptime' in f: f['ptime']+=1/hz
            return
        if pe and not session.action_busy:
            pe.regen()                               # Menu_MainUpdate: no regen while flag 0x100 / paused
            if pe.haste_left:
                pe.haste_left-=1;session.haste=pe.haste_left>0
            if status:
                # Aya's state flags: enemy buff clears / stiffness drop Haste and Barrier (player_status).
                if pe.haste_left<=0:status.flags&=~0x100
                elif not status.flags&0x100:pe.haste_left=0;session.haste=False
                if pe.barrier and not status.flags&0x200:pe.barrier=False
                if not pe.barrier:status.flags&=~0x200
                if pe.gene and not status.flags&0x400:pe.gene=False             # enemy effects 2 / 9 clear them
                if pe.preraise and not status.flags&0x800:pe.preraise=False
        if status:
            lost=status.tick()                       # Entity_UpdateTimers, once per battle update
            if lost:
                taken+=lost;st.add('player_poison',lost);session.event('player_poison',damage=lost)
                if dead(): finished_at=now;return
            session.slow=slow or status.stiff
        if pe: upkeep()
        if hold[0]: hold[0]-=1
        if contact[0]: contact[0]-=1                 # Entity_UpdateTimers: g_AyaStatusEffectTimer
        if contact_vals and not hold[0] and not contact[0]:
            # contact_damage.py: flat contactDamage on cylinder overlap; when overlap happens is a
            # labelled per-update hazard per live enemy (play-log contacts per enemy-minute).
            cd=options['contact_damage'];boss_b=any(f['boss'] for f in foes)
            if cd.get('logged'):
                from .logged_contact import rate_for                 # per-room play-log rate (labelled data)
                rate=rate_for(foes[0].get('loc'),boss_b)
            else: rate=cd.get('boss' if boss_b else 'ord',0.0)
            # Rate per battle-minute while any contact-capable enemy is alive (logged_contact.py); the
            # touching enemy is one of them at random.
            able=[f for f in foes if contact_vals.get(f['i'],0) and f['cur']>0 and not f.get('controller')]
            if able and crng.random()<rate/60/hz:
                v=contact_vals[crng.choice(able)['i']];contact[0]=0x5A
                if pe and pe.barrier: st.add('contact_barrier')
                else:
                    taken+=v;st.add('contact_hits');st.add('contact_damage',v)
                    if dead(): finished_at=now;return
        if beams:
            result=beams.begin_update(hp-taken+healed,lambda:rng.randrange(100))
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
            if dead():finished_at=now;return
        for f in foes:
            if f['cur']<=0: continue
            p=enemy_profiles[f['i']]
            if rules.get('enemy_model')=='charge':
                script=enemy_scripts[f['i']];clock=script.clock
                if f['poisoned'] and not clock.flags&0x10: clock.flags=(clock.flags|0x10)&~0x3E0
                if f['stopped']>((clock.flags>>11)&3): clock.flags|=0x1800;clock.actor_flags|=0x1000
                if hasattr(script,'distance') and script.phase=='charge':script.distance=f['dist']
                previous_projectiles=getattr(script,'projectiles',0)
                waits=script.stats['none'] if isinstance(script,GatedEnemy) else 0
                frozen=options.get('serial_action') and session.action_busy
                if frozen and script.phase=='charge':
                    # Aya's committed action sets game flag 0x100: Battle_UpdateEnemy skips charge and
                    # status timers and Script_* nodes of other entities are skipped (flow_opcodes.c),
                    # so no new attack starts; one already animating still lands (sitting duck).
                    st.add('serial_frozen_updates');continue
                if frozen:
                    saved=(clock.charge,clock.flags)
                    strike,damage=script.tick();clock.charge,clock.flags=saved;damage=0
                else:
                    strike,damage=script.tick()
                if isinstance(script,GatedEnemy) and script.stats['none']>waits:
                    # No guard holds this distance: the enemy repositions while it waits (its
                    # approach movement is not modelled), so the next decision sees a new sample.
                    st.add('choice_waits');f['dist']=profile.sample(rng)
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
                if isinstance(script,GatedEnemy) and script.current:
                    # The chosen slot's power; explicit profile overrides stay authoritative.
                    p={**p,**script.current,**options.get('enemy_profiles',{}).get(f['i'],{})}
                    st.add('choice_strikes_slot%d'%script.current['action_slot'])
                    st.add('strike_timing_'+script.plan['kind'])
                    if options.get('hit_trace'):st.add('_strike|%s|%s|%d|%s|%s'%(f.get('loc'),f.get('name'),int(bool(f['boss'])),script.plan['kind'],script.current['action_slot']))
            elif now<f['t_next']: continue
            strike_dist=f['dist'];close=f['dist']<450
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
            if p.get('no_contact'):
                st.add('no_contact_strikes');continue   # no damage path for this action (enemy_choice 'noeffect')
            if options.get('player_evade') and session.action_busy:st.add('strikes_while_committed')
            elif options.get('player_evade') and rng.random()<options['player_evade']:
                # Player behaviour, not source: the share of strikes a human avoids by moving during
                # the gauge wait, calibrated from the play log (pe-calibration-atbguard-2026-10-19.md).
                # Not while an attack or counter is committed: firing can't be cancelled (sitting duck).
                st.add('evaded_strikes');continue
            if options.get('player_evade_melee') and not session.action_busy and not (status and status.flags&0xC==0x4):
                # (Confusion: scene/player_movement.c rotates and mirrors the controls; the player can't step
                # back reliably, so no melee dodge while confused. Labelled behaviour.)
                # Player behaviour (labelled): stepping back from a melee swing during the gauge wait.
                # Effects / projectiles (geometric strikes) are not affected.
                melee=not getattr(script,'last_strike_geometric',False) and not (isinstance(script,GatedEnemy)
                    and script.plan and script.plan.get('kind') in ('module','homing','task','effect'))
                if melee and rng.random()<options['player_evade_melee']:
                    st.add('evaded_melee');continue
            if options.get('melee_reach') and 'melee_reach_units' in p:
                # Sphere contact decides the hit (enemy_reach.py): out of reach, the window
                # closes without contact; in reach, the hit lands.
                st.add('melee_reach_strikes')
                if strike_dist>p['melee_reach_units']:
                    st.add('melee_reach_misses');continue
                geometric=True
            if rng.random()<min(1.,(1. if rules.get('enemy_model')=='charge' and geometric else p.get('hit_probability',ENEMY_HIT))*(1+(close_risk if close else 0.))):
                if hold[0]:
                    st.add('revive_hold_blocked');continue      # 0x800000: Menu_MainUpdate resolves no hit
                if contact_vals: contact[0]=0x5A               # a resolved strike opens the contact window too
                barrier=False
                st.add('explicit_power_hits' if 'power' in p else 'legacy_damage_hits')
                if beams and 'power' in p:
                    if guard!=1:raise ValueError('source player HP/barrier state requires guard=1')
                    from .incoming_damage import resolve_incoming
                    from .beam_delivery import stiffness_lock
                    beams.player.hp=int(max(0,hp-taken+healed))&65535
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
                        effect_type=p.get('effect_type',0),
                        # Entity_ResolveDropTable (entity/combat.c): no barrier and atbGauge > 0 -> damage / 2.
                        # Opt-in atb_guard: the gauge is 0 from the attack commit through the action
                        # (flag 0x100 gates gain), so hits landing while Aya acts are not halved.
                        charged_guard=p.get('charged_guard',False) or bool(options.get('atb_guard') and session.gauge>0 and not session.action_busy),
                        player_flags=p.get('player_flags',0)|(status.flags&0x1100 if status else 0x100 if pe and pe.haste_left>0 else 0))
                    if pe and pe.barrier:
                        # Entity_ResolveDropTable with AYA_BARRIER: no gauge halving, the damage drains PE
                        # instead of HP (status effects still apply, HP-share ones are blocked).
                        value,_=enemy_damage(p['power'],aya.get('defense',0),
                            armor_first=p.get('armor_first',aya.get('armor_first',0)),
                            armor_second=p.get('armor_second',aya.get('armor_second',0)),
                            action_slot=p.get('action_slot',0),effect_chance=p.get('critical_chance',0),
                            critical_resist=p.get('critical_resist',aya.get('critical_resist',0)),roll=rng.randrange(100),
                            effect_type=p.get('effect_type',0),player_flags=status.flags&0x1100 if status else 0x100 if pe.haste_left>0 else 0)
                        pe.barrier_hit(value,int(options.get('player_max_hp',pe.max_hp or hp)));st.add('barrier_absorbed',value)
                        hurt=0
                        if status and not pe.barrier:status.flags&=~0x200
                    if options.get('atb_guard'):st.add('atb_guard_halved' if session.gauge>0 and not session.action_busy else 'atb_guard_full')
                    hurt*=guard
                    if status and p.get('effect_type',0):
                        # Battle_ApplyEnemyAttack after every resolved hit, damage or not.
                        # HP-share effects (e.g. 'hp to 3/4') act on Aya's real HP; player_max_hp stands in
                        # for it when the fight's hp cap is artificial (calibration runs uncapped).
                        now_hp=int(max(1,min(hp,options.get('player_max_hp',hp))-(taken-healed)-hurt))
                        new_hp,what=status.apply(p['effect_type'],p.get('status_level',0),p.get('status_period',0),
                                                 lambda:rng.randrange(1<<15),now_hp)
                        hurt+=now_hp-new_hp
                        if p['effect_type'] in (10,11,12,13) and options.get('steals'):
                            # Battle_ApplyEnemyAttack steals: literal source — only with armor effect bit 0x10
                            # (EFFECT_RESIST_STEAL), and then when rand()%100 >= 60. Items: one random stealable
                            # item (Inv_PickRandomItem; the battle bag here). Ammo: a random pool among the first
                            # `count with ammo` slots, amount = stock * RandomByte / 256 (Inv_RollRandomItemType).
                            what='steal_blocked'
                            if armor_fx&0x10 and rng.randrange(100)>=60:
                                if p['effect_type'] in (10,11) and pe and any(v>0 for v in pe.bag.values()):
                                    item=rng.choice(sorted(k for k,v in pe.bag.items() if v>0));pe.bag[item]-=1
                                    what='stole_item';f.setdefault('stolen_items',[]).append(item)
                                elif p['effect_type'] in (12,13):
                                    pools=[k for k in (0,1,2) if session.reserves.get(k,0)>0]
                                    if pools:
                                        pool=(len(pools)*rng.randrange(256))>>8
                                        take=session.reserves.get(pool,0)*rng.randrange(256)>>8
                                        session.reserves[pool]=session.reserves.get(pool,0)-take
                                        what='stole_ammo';st.add('ammo_stolen',take)
                        st.add('status_'+what.replace(' ','_'))
                        if what=='unmodelled' or p['effect_type']==3:st.add('incoming_status_unmodeled')
                    elif p.get('effect_type',0):st.add('incoming_status_unmodeled')
                else:
                    if beams:raise ValueError('beam encounters require source power profiles for enemy hits')
                    hurt=(enemy_dmg(f) if enemy_dmg else 1.6*f['level'])*guard
                taken+=hurt;st.add('hits_taken')
                if options.get('hit_trace'):
                    # Audit only: underscore keys are excluded from campaign aggregates.
                    tag='_hit|%s|%s|%d|%s|%s'%(f.get('loc'),f.get('name'),int(bool(f['boss'])),'power' if 'power' in p else 'fallback',p.get('action_slot','-'))
                    st.add(tag);st.add(tag.replace('_hit|','_dmg|',1),hurt)
                session.event('enemy_hit',target=f['i'],damage=hurt)
                # One global pending attacker: later eligible hits replace it.
                pending_counter=(f['i'],session.update+options.get('counter_reaction_updates',21))
                if dead(): finished_at=now;break

        if beams:
            for event in beams.update_effects(session.gun.kind,session.costume):
                kind=event.pop('event');session.event(kind,**event)
                st.add('beam_contacts' if kind=='beam_contact' else 'beam_cleanups')

    session=BattleSession(guns,reserves,initial.get('equipped','primary'),stat22=stat22,
        gauge=gauge,costume=rules.get('animation_costume',0),seed=rng.getrandbits(32),
        on_update=on_update,should_stop=stopped)
    session.slow=slow or bool(beams and beams.player.flags&0xc0 in (0x40,0x80))
    session.serial=bool(options.get('serial_action'))   # Menu_MainUpdate: no gauge gain while flag 0x100 is set
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
        if foes[target].get('controller'):
            st.add('counter_controller_skipped');return       # untargetable core: the log never shows Aya hitting it
        if not enemy_profiles[target].get('counter_eligible',True): return
        rank=enemy_profiles[target].get('rank',foes[target].get('rank',foes[target]['level']))
        if options.get('identity_rank') and 'rank' not in enemy_profiles[target]:
            # Battle_RollEnemySpawn: s8(Aya rank - enemy rank); the enemy rank is the identity's low byte
            # (field 41; CombatantIdentity {u8 rank; s8 kind}), Aya's is level (aya/stats.c fieldId04 = level + 1).
            try: rank=int(foes[target]['name'],16)&0xFF
            except (KeyError,TypeError,ValueError): pass
        chance=counter_probability(options.get('counter_hp_level',aya.get('hp_level',aya['level']*10)),
            options.get('player_rank',aya.get('rank',aya['level']))-rank)
        chance=min(1.,chance*rules.get('counter_mult',1.))
        st.add('counter_checks')
        if rng.randrange(100)>=round(chance*100): return
        st.add('counters')
        session.attack(counter=True,rof=effect.get('rof',1),commands=1,mode=effect.get('mode'),
            targets=[f['i'] for f in foes if f['cur']>0 and not f.get('controller')],selected=target,
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
                session.switch(name,half_bar=options.get('half_bar',True),free=options.get('switch_cost')=='free',
                    menu_updates=options.get('menu_updates',0),stream_updates=options.get('stream_updates',0))
                st.add('switches')
        if pe:
            boss=any(f['boss'] for f in foes)
            mh=pe.max_hp or hp                       # policy scale (calibration runs with an unbounded hp cap)
            def pick(g,first):
                now_hp=mh-(taken-healed)
                if pe.script is not None:          # replay of the logged casts (calibration); items replayed too when given
                    f=status.flags if status else 0
                    ailing={n for n,ok in (('poison',f&3==1),('confused',f&0xC==4),('dark',f&0x30==0x10),
                                           ('stiff',f&0xC0 in (0x40,0x80)),('defdown',bool(f&0x1000))) if ok}
                    return (pe.choose_scripted(now_hp,mh,g,poisoned='poison' in ailing,hasted=pe.haste_left>0,barrier=pe.barrier,ailing=ailing)
                            or (None if pe.items is not None else pe.choose(now_hp,mh,g,boss,False,items_only=True)))
                return pe.choose(now_hp,mh,g,boss,first)
            def want(g): return pick(g,st.get('turns',0)==0 and not st.get('pe_casts'))
            quick=pick(4500,False)
            session.wait_gauge(4500 if quick and quick[1]=='half' else 9000)
            if stopped(): break
            choice=want(session.gauge)
            if choice:
                spell,bar=choice
                if options.get('reaction_updates'):
                    session.advance(int(options['reaction_updates']),paused=bool(options.get('reaction_paused')))
                # pe_atb_items.c: a quick power costs half a bar (full bar -> 4500); others a full bar.
                session.gauge=max(0,session.gauge-4500) if bar=='half' else 0
                if isinstance(spell,tuple):
                    # Items: a committed action (flag 0x100) like an attack.
                    session.action_busy=True;session.advance(pe.cast_updates);session.action_busy=False
                else:
                    # PE powers pause the enemies for the whole animation and can't be interrupted
                    # (user observation 2026-10-19; Battle_StepAyaAction case 0 Pm_StopLowerHalf, flag
                    # 0x100 for commands 0x183..0x196): a paused advance, no strikes land.
                    session.advance(pe.cast_updates,paused=True);st.add('pe_pause_s',pe.cast_updates/hz)
                pe_before=pe.pe
                pe.cast(spell)
                if spell=='EnergyShot':
                    # Battle_ResolveHit (battle/enemy_movement.c) with state 0x100000: base = stat1E/5 + the gun's
                    # power bonus; power = base * ((7*level + 120) / 160) * PE / maxPE + base (integers); damage =
                    # power - full defense, at least 1; no hit quality / elements / status. phase.c then sets PE 0.
                    alive=[f for f in foes if f['cur']>0 and not f.get('controller')]
                    if alive:
                        from .parasite_energy import energy_shot_damage
                        f=min(alive,key=lambda f:f['cur'])
                        dmg=energy_shot_damage(aya.get('offense',0),active_cfg()['power'],max(1,aya.get('level',1)),
                                               pe_before>>16,pe.max>>16,f.get('defense',0))
                        st.add('energy_shot_damage',min(dmg,max(0.,f['cur'])));f['dealt']+=dmg;f['cur']-=dmg
                        if f['cur']<=0 and f.get('phase2_hp'): f['cur']=float(f.pop('phase2_hp'));st.add('phase2_refills')
                    pe.pe=0
                if spell=='Liberate':
                    # State 0x80000 (Battle_ApplySpellEffect case 19): Battle_StepAyaAction visits targets;
                    # each hit = liberate_power - full defense (Battle_ResolveHit), 7 hits in the log; enemies
                    # paused for the extra ~20 s of the action; phase.c zeroes PE at its end.
                    from .parasite_energy import liberate_power, LIBERATE_HITS, LIBERATE_UPDATES
                    session.advance(max(0,LIBERATE_UPDATES-pe.cast_updates),paused=True)
                    for _ in range(LIBERATE_HITS):
                        alive=[f for f in foes if f['cur']>0 and not f.get('controller')]
                        if not alive: break
                        f=rng.choice(alive)
                        dmg=max(1,liberate_power(aya.get('offense',0),max(1,aya.get('level',1)),len(alive))-int(f.get('defense',0)))
                        st.add('liberate_damage',min(dmg,max(0.,f['cur'])));f['dealt']+=dmg;f['cur']-=dmg
                        if f['cur']<=0 and f.get('phase2_hp'): f['cur']=float(f.pop('phase2_hp'));st.add('phase2_refills')
                    pe.pe=0
                if isinstance(spell,tuple):st.add('items_used');st.add('item_%02X'%spell[1])
                else:st.add('pe_casts');st.add('pe_cast_'+spell)
                # Battle_ApplySpellEffect (battle/attack.c) side effects.
                if spell=='Haste' and status:
                    status.flags|=0x100                                  # Entity_ResolveDropTable: defense term x3/10
                    if status.stiff:status.flags&=~0xC0                  # Haste also cures stiffness
                elif spell=='Detox' and status and status.flags&3!=3:status.flags&=~3
                elif spell=='Barrier' and status:status.flags|=0x200
                elif spell in ('Medic','FullRecover') and status:
                    # Medic / Full Recover: every ailment pair cleared unless it reads immune (both bits), and 0x1000.
                    for mask in (0x3,0xC,0x30,0xC0):
                        if status.flags&mask!=mask:status.flags&=~mask
                    status.flags&=~0x1000
                elif isinstance(spell,tuple) and spell[1] in (0x0D,0x0E,0x0F,0x10) and status:
                    # Battle_ApplyDamage cures: an active ailment is cleared; none -> one-use immunity (both bits).
                    mask={0x0D:0x3,0x0E:0x30,0x0F:0xC,0x10:0xC0}[spell[1]]
                    if status.flags&mask==0:status.flags|=mask
                    elif status.flags&mask!=mask:status.flags&=~mask
                elif isinstance(spell,tuple) and spell[1]==0x11 and status:
                    for mask in (0x3,0xC,0x30,0xC0):
                        if status.flags&mask!=mask:status.flags&=~mask
                    status.flags&=~0x1000
                elif spell=='GeneHeal' and status:status.flags|=0x400
                elif spell=='Preraise' and status:status.flags|=0x800
                elif spell in ('Slow','Confuse') and rules.get('enemy_model')=='charge':
                    alive=[f for f in foes if f['cur']>0 and not f.get('controller')]
                    if alive:
                        clock=enemy_scripts[min(alive,key=lambda f:f['cur'])['i']].clock
                        # Success: certain when the target's status pair reads 2, a coin flip at 0; the
                        # catalog has no statusFlags2, so the coin flip is used (labelled).
                        if not rng.randrange(2):
                            st.add('pe_'+spell.lower()+'_landed')
                            if spell=='Slow':clock.flags|=1                # Battle_UpdateEnemy: step x3/5
                            else:                                          # 3-5 skipped charge cycles
                                clock.flags=(clock.flags&~0xE)|(((rng.randrange(1<<15)%3)+3)&7)*2;clock.actor_flags|=0x1000
                if pe.heal_of(spell,mh):
                    amount=min(pe.heal_of(spell,mh),taken-healed)
                    healed+=max(0,amount);st.add('pe_healed',max(0,amount))
                continue
        session.wait_gauge()
        if stopped(): break
        if options.get('reaction_updates'):
            # Player policy (calibrated from the play log, not source): delay from a full gauge to the attack.
            session.advance(int(options['reaction_updates']),paused=bool(options.get('reaction_paused')));st.add('reaction_s',int(options['reaction_updates'])/hz)
            if stopped(): break
        current=active_cfg();alive=[f for f in foes if f['cur']>0 and not f.get('controller')]   # controllers are untargetable
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
    st['damage_taken']=taken;st['healed']=healed;st['loaded_left']=session.gun.loaded;st['won']=int(done())
    st['reserve_left']=sum(session.reserves.values())
    st['rounds']=sum(e['event']=='fire' and session.guns[e['weapon']].kind!=8 for e in session.events)
    st['reloads']=sum(e['event']=='ammo_transfer' for e in session.events)
    st['click']=sum(e['event']=='empty_click' for e in session.events)
    st['ammo_balance']=initial_rounds-sum(g.loaded for g in session.guns.values())-st['reserve_left']-st['rounds']
    st['_source_state']=dict(equipped=session.equipped,gauge=session.gauge,
        loaded={k:g.loaded for k,g in session.guns.items()},reserves=dict(session.reserves))
    if math.isfinite(hp): st['_source_state']['hp']=max(0.,hp-taken+healed)
    if beams:
        st['_source_state']['beam_player']=beams.state()
        st['_beam_state']=dict(active_update=beams.active_update,player=beams.state(),
            effects=[dict(owner=e['emitter'].owner.name,held=e['emitter'].held,effect_state=e['emitter'].owner.effect_state,finished=e['emitter'].cleanup.finished) for e in beams.entries])
    if options.get('trace'): st['_source_events']=session.events
    if options.get('trace') and rules.get('enemy_model')=='charge':
        st['_enemy_clocks']=[dict(charge=s.clock.charge,flags=s.clock.flags,phase=s.phase) for s in enemy_scripts]
    return st
