import json,math,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
M=load(O/'SOURCE_MIDI_REVALIDATION.json');A=load(O/'ORIGINAL_ACTION_INSPECTION.json');C=load(O.parent/'hands_sequence_fingering_planning_r1/SEQUENCE_CANDIDATES.json')['candidates'][0];fingers={n['note_id']:n['finger'] for n in C['notes']}
notes=[dict(n,finger=fingers[n['note_id']]) for n in M['notes']]
def angle(pitch,t):
 points=A['fcurves'][str(pitch-21)][0]['points'];before=max((p for p in points if p['display_time']<=t),key=lambda p:p['display_time'],default=points[0]);after=min((p for p in points if p['display_time']>=t),key=lambda p:p['display_time'],default=points[-1]);d=after['display_time']-before['display_time'];return before['angle'] if d==0 else before['angle']+(after['angle']-before['angle'])*(t-before['display_time'])/d

def compile_contact_sequence(events):
 out=[];warnings=[]
 for n in events:
  on=n['display_on'];off=n['display_off'];pitch=n['midi'];points=A['fcurves'][str(pitch-21)][0]['points'];maxa=max(p['angle'] for p in points if on-1e-6<=p['display_time']<=off+1e-6);full=min((p['display_time'] for p in points if on<=p['display_time']<off and abs(p['angle']-maxa)<1e-7),default=off);nexton=min((x['display_on'] for x in events if x['midi']==pitch and x['display_on']>=off-1e-10 and x['note_id']!=n['note_id']),default=1e9);zero=min((p['display_time'] for p in points if p['display_time']>=off and abs(p['angle'])<1e-8),default=None);relend=min(nexton,zero if zero is not None else off)
  if nexton<=off+1e-8 and angle(pitch,off)>1e-5:warnings.append(dict(note_id=n['note_id'],kind='RETRIGGER_WITHOUT_FULL_KEY_RESET',at=off,angle_rad=angle(pitch,off),mechanical_reset_unproven=True))
  prior=max((x['display_on'] for x in events if x['hand']==n['hand'] and x['display_on']<on-1e-9),default=0.)
  def item(mode,start,end,required,tangent,mechanical):
   return dict(episode_id=n['note_id']+':'+mode,note_id=n['note_id'],hand=n['hand'],finger=n['finger'],midi=pitch,key_index=pitch-21,mode=mode,display_interval=[start,end],music_interval=[start-.35,end-.35],interval_convention='[start,end)',required_contact=required,optional_early_contact=mode=='APPROACH',wrist_motion='ALLOWED_ONLY_IF_ALL_ACTIVE_CONTACT_AND_COLLISION_CONSTRAINTS_REMAIN_FEASIBLE',tangential_policy=tangent,mechanical_phase=mechanical,source_event_ticks=[n['on_tick'],n['off_tick']],geometry_oracle='frozen_blender_actual_skin_v1',target_depth_limit_mm=.25,non_target_depth_limit_mm=.25,nonadjacent_self_crossings_limit=0,contact_force='NOT_ESTIMATED',pre_touch_guard='Only on quiescent source key and no added key motion; exact surface crossing within unchanged penetration contract. Physical unloaded force unproved.' if mode=='APPROACH' else None)
  if prior<on:out.append(item('APPROACH',prior,on,False,'FREE_WHILE_CLEAR; PRE_TOUCH may be selected only after guard','READ_SOURCE; no fabricated early press'))
  if full>on:out.append(item('PRESS',on,full,True,'BOUNDED_SLIDE_WITHIN_SAME_PLAYABLE_PATCH','FOLLOW_SOURCE_DESCENDING_TOP'))
  if off>full:out.append(item('HOLD',full,off,True,'BOUNDED_SLIDE_OR_STICK; selected material face anchor records choice','FOLLOW_SOURCE_HOLD'))
  if relend>off:out.append(item('RELEASE',off,relend,False,'MAY_SEPARATE; if surface remains touching, follow recovering top without obstruction','FOLLOW_SOURCE_RECOVERY'))
 return out,warnings
sequence,warnings=compile_contact_sequence(notes)
# Standalone schema has no G4/E5 or solver assumptions.
schema=dict(schema_version='1.0',units=dict(time='seconds display/music explicit',translation='mm',control_angle='rest-axis rig degrees; not clinical',geometry='metres internally'),modes=['FREE','APPROACH','PRE_TOUCH','PRESS','HOLD','RELEASE'],required_fields=['episode_id','note_id','hand','finger','midi','key_index','mode','display_interval','music_interval','required_contact','mechanical_phase','tangential_policy'],event_order='Atomic event batch: remove obligations ending at t, add obligations beginning at t; preserve continuous-position one-sided-limit compatibility as separate junction obligation.',contact_validation='True clipped pulp-face/top intersection and area; not distance tolerance alone; penetration and anatomy independently enforced.',boundary_compatibility='A continuous trajectory must reconcile left/right contact sets and position/velocity limits. Half-open labels do not permit teleportation or prove junction existence.',free_motion='No active contacts permits whole-hand motion only under anatomy, all-key collision and travel-time constraints.',sliding='Material witness may migrate only within verified actual pulp/playable patch; tangential displacement/velocity budget is explicit planner parameter. Sticking is a valid stricter adapter specialization.',no_force_or_acoustic_proof=True)
core=[e for e in sequence if e['note_id'] in ['R07','R08']]
for e in sequence:
 assert all(k in e for k in schema['required_fields']);assert 1<=e['finger']<=5 and e['key_index']==e['midi']-21;assert e['display_interval'][0]<=e['display_interval'][1]
 for t,m in zip(e['display_interval'],e['music_interval']):assert abs(t-m-.35)<1e-10
# Source Action LINEAR reconstruction independently checked against Blender evaluation rows.
errors=[abs(angle(n['midi'],r['display_time'])-r['angles'][n['midi']-21]) for n in notes for r in A['rows'] if n['display_on']-.0001<=r['display_time']<=n['display_off']+.1];assert max(errors)<2e-6
byid={n['note_id']:n for n in notes};tests=[]
def record(kind,ids,predicate):
 ns=[byid[i] for i in ids];assert predicate(ns);eps=[e for e in sequence if e['note_id'] in ids];assert eps;tests.append(dict(case=kind,real_source_note_ids=ids,note_summary=[dict(id=n['note_id'],hand=n['hand'],midi=n['midi'],finger=n['finger']) for n in ns],status='REPRESENTATION_PARSE_PASS',episodes=[e['episode_id'] for e in eps],kinematic_feasibility='NOT_TESTED',source='same existing23-note original MIDI; not an independent cross-MIDI performance test'))
record('single_finger_repetition',['R06','R07'],lambda n:n[0]['midi']==n[1]['midi'] and n[0]['finger']==n[1]['finger'])
record('successive_different_fingers',['R09','R10'],lambda n:n[0]['finger']!=n[1]['finger'])
record('same_hand_chord_hold',['L00','L01','L02'],lambda n:len({x['display_on'] for x in n})==1 and len({x['finger'] for x in n})==3)
record('black_press_white_release',['R11','R12'],lambda n:n[0]['key_color']=='WHITE' and n[1]['key_color']=='BLACK')
record('octave_leap',['R13','R14'],lambda n:abs(n[0]['midi']-n[1]['midi'])==12)
record('one_holds_other_prepares',['R07','R08'],lambda n:n[0]['finger']!=n[1]['finger'] and abs(n[0]['display_off']-n[1]['display_on'])<1e-10)
result=dict(task='PIANO_CONTACT_STATE_MOTION_PLANNER_COMPARISON_R1',authority='DESIGN_PROVISIONAL',contract_status='CONTACT_STATE_CONTRACT_PASS',schema='CONTACT_STATE_SCHEMA.json',clock_offset=.35,original_midi_sha256=M['midi_sha256'],source_action_payloads=A['action_payloads'],core_sequence=core,atomic_exchange=dict(display_time=byid['R08']['display_on'],remove_required=['R07:HOLD'],add_required=['R08:PRESS'],G4_recovery_until=2.991426,E5_full_press_at=2.956426,both_keys_required_for_entire_exchange=False,instantaneous_geometric_double_touch_may_follow_from_continuity=True,continuous_boundary_configuration='UNVERIFIED; P3 checks new-contact mode only'),discrete_test_contract=dict(P1=dict(time=2.527855,required=[dict(note='R07',finger=1,midi=67)],source='B2'),P2=dict(time=2.72,required=[dict(note='R07',finger=1,midi=67)],preparation='3mm wrist/root X displacement diagnostic; E5 exact suspension not required'),P3=dict(time=2.921426,required=[dict(note='R08',finger=3,midi=76)],G4='RELEASE; no hold obligation, no key obstruction',left_limit_compatibility='NOT_PROVEN'),P4=dict(time=2.956426,required=[dict(note='R08',finger=3,midi=76)])),mechanical_warnings=warnings,all_source_sequence=sequence,parse_test_file='CONTRACT_REUSE_TESTS.json',source_action_reconstruction_max_error_rad=max(errors))
for name,data in [('CONTACT_STATE_SCHEMA.json',schema),('CONTACT_STATE_SEQUENCE.json',result),('CONTRACT_REUSE_TESTS.json',dict(tests=tests,all_pass=True,no_new_motion_generated=True))]:(O/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('CONTRACT_PASS',len(sequence),'episodes',len(tests),'reuse cases','Action error',max(errors),'warnings',warnings)
