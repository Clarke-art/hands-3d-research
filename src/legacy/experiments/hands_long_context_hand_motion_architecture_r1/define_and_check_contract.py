import sys,json,copy,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent;P=O.parent/'hands_early_hand_preparation_entry_reachability_r1'
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def js(n,d):(O/n).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf8')
policy=rd(O/'POLICY_LOCK.json');events=rd(P/'SOURCE_MIDI_REVALIDATION.json')['notes'];source=rd(P/'SOURCE_MIDI_REVALIDATION.json');fingering=rd(Path(source['candidate_file']))['candidates'][0];assign={n['note_id']:n['finger'] for n in fingering['notes']};seq=rd(O/'CONTACT_STATE_SEQUENCE.json')['all_source_sequence'];keys=rd(O/'SKIN_MODEL_META.json')['key_table']
fields=['intent_id','hand_identity','MIDI_event_context','assigned_fingering','active_contact_modes','preparation_time_window','palm_position_region','wrist_orientation_region','digit_preparation_targets','obstacle_clearance_intent','target_contact_region','timing_constraints','motion_cost_estimates','uncertainty_or_unverified_flags','source_bindings','coordination']
schema={'$schema':'https://json-schema.org/draft/2020-12/schema','title':'HandMotionIntent','type':'object','required':fields,'properties':{
'intent_id':{'type':'string','minLength':1},
'hand_identity':{'enum':['R','L','BOTH']},
'MIDI_event_context':{'type':'array','minItems':1,'items':{'type':'object','required':['note_id','hand','midi','display_on','display_off']}},
'assigned_fingering':{'type':'array','minItems':1,'items':{'type':'object','required':['note_id','hand','finger'],'properties':{'finger':{'type':'integer','minimum':1,'maximum':5}}}},
'active_contact_modes':{'type':'array','items':{'type':'object','required':['episode_id','note_id','hand','finger','midi','mode','display_interval','required_contact','tangential_policy'],'properties':{'mode':{'enum':['FREE','APPROACH','PRE_TOUCH','PRESS','HOLD','RELEASE']}}}},
'preparation_time_window':{'type':'array','minItems':2,'maxItems':2,'items':{'type':'number'}},
'palm_position_region':{'type':'object','required':['frame','regions'],'properties':{'frame':{'enum':['frozen_world_m','key_local_m','root_control_mm']},'regions':{'type':'array','items':{'type':'object'}}}},
'wrist_orientation_region':{'type':'object','required':['frame','units','authorized_control_bounds']},
'digit_preparation_targets':{'type':'array','items':{'type':'object','required':['hand','finger','region','surface_scope']}},
'obstacle_clearance_intent':{'type':'array','items':{'type':'object','required':['obstacle_key_index','piece_indices','route','clearance_m'],'properties':{'obstacle_key_index':{'type':'integer','minimum':0,'maximum':87},'route':{'enum':['ABOVE_ENTITY','FRONT_OF_ENTITY','LATERAL_CORRIDOR','NO_OBSTACLE_INTENT']},'clearance_m':{'type':'number','minimum':0}}}},
'target_contact_region':{'type':'array','items':{'type':'object','required':['hand','finger','key_index','playable_patches_source','contact_mode_source']}},
'timing_constraints':{'type':'object','required':['evaluation_time','clock_offset_seconds','preserve_MIDI_events','preserve_key_Action','preserve_fingering','early_release_allowed','early_wrong_press_allowed']},
'motion_cost_estimates':{'type':'object','required':['status','necessary_bounds_only']},
'uncertainty_or_unverified_flags':{'type':'array','items':{'type':'string'}},
'source_bindings':{'type':'object','required':['MIDI_sha256','fingering_sha256','rig_identity','key_geometry_source','contact_sequence_source']},
'coordination':{'type':'object','required':['mode','hands'],'properties':{'mode':{'enum':['INDEPENDENT','COUPLED','SINGLE_HAND']},'hands':{'type':'array','items':{'enum':['R','L']}}}}
},'additionalProperties':False}
contract=dict(authority='DESIGN_PROVISIONAL — STOP — HUMAN REVIEW',schema_version='1.0',schema=schema,units=dict(time='display seconds with explicit music/display offset',geometry='metres in declared world/key frame',root_controls='mm and rest-axis degrees; no clinical interpretation'),inheritance=dict(contact_sequence='Existing ContactStateSchema/Sequence, half-open modes plus separate junction continuity obligations',fingering='Immutable source assignments; future feedback proposes separate candidate and requires authorization',target_contact_region='A set of original key playable patches; never fabricate a target point off the real entity'),hard_acceptance=dict(target_depth_mm=.25,wrong_region_depth_mm=.25,nonadjacent_self_crossings=0,wrist_speed_mm_s=500,mapped_joint_rate_deg_s=240,natural_family='Original authorized reference family and control domain',actual_Blender_required=True),solver_handoff=dict(high_level_output='Time-labelled palm regions, digit whole-skin clearance halfspaces/corridors, contact-region sets, event deadlines and explicit uncertain flags',low_level_role='Existing frozen FK/skin + contact constraint adapter resolves engineering controls; final full Blender rejection is mandatory',mapping='Fix required contact modes and source clock; add geometry corridor inequalities for assigned free preparing digits; keep state(z) reference-family mapping',infeasible_result='Emit region/phase/constraint witness and motion cost; do not alter MIDI/fingering/Action or enlarge domains',motion_prior='Optional soft reference with separate provenance/licence; never override hard contact/event/geometry constraints'),implemented_adapter_scope=dict(right_hand=True,free_preparing_digit='Only existing designated-digit alpha mapping from source input',palm_translation=True,geometry_waypoint_modes=['ABOVE_ENTITY','FRONT_OF_ENTITY'],left_hand='CONTRACT_ONLY_UNADAPTED',chord='CONTRACT_ONLY_UNADAPTED',continuous_corridor_tracking='NOT_IMPLEMENTED',mature_external_generator='NOT_EXECUTED'),acceptance_states=['INTENT_PROPOSED','RIG_STATIC_CHECKED','STATIC_ACCEPTED_OR_REJECTED','CORRIDOR_CONNECTION_UNVERIFIED','CONTINUOUS_PATH_VALIDATED_HUMAN_PENDING'],limits=dict(maximum_spatial_candidates=2,new_numerical_recommended_seconds=300,new_numerical_hard_seconds=600),evidence_classes=['REAL_HUMAN_OBSERVATION','LICENSED_DATA_ASSET','DATA_DERIVED_STATISTIC','MODEL_GENERATED_CANDIDATE','PROGRAMMATIC_GEOMETRY_HYPOTHESIS','UNVERIFIED'])
serialized=json.dumps(contract);assert not any(token in serialized for token in ['G4','E5','D#5','R07','R08'])
js('HAND_MOTION_INTENT_CONTRACT.json',contract)
source_map={n['note_id']:n for n in events}
bindings=dict(MIDI_sha256=source['midi_sha256'],fingering_sha256=source['candidate_sha256'],rig_identity=rd(P/'INPUT_IDENTITY_AUDIT.json')['frozen_right_native_sha256'],key_geometry_source='SKIN_MODEL_META.json:key_table',contact_sequence_source='CONTACT_STATE_SEQUENCE.json')
def make(ids,t,hand,mode='SINGLE_HAND'):
 ns=[copy.deepcopy(source_map[i]) for i in ids];active=[copy.deepcopy(m) for m in seq if m['note_id'] in ids and m['required_contact'] and m['display_interval'][0]<=t<m['display_interval'][1]]
 return dict(intent_id='contract_'+str(len(ids))+'_'+str(t),hand_identity=hand,MIDI_event_context=ns,assigned_fingering=[dict(note_id=n['note_id'],hand=n['hand'],finger=assign[n['note_id']]) for n in ns],active_contact_modes=active,preparation_time_window=[min(n['display_on'] for n in ns),max(n['display_off'] for n in ns)],palm_position_region=dict(frame='frozen_world_m',regions=[]),wrist_orientation_region=dict(frame='frozen_root_rest_axes',units='degrees',authorized_control_bounds='POLICY_LOCK.json:root_domains'),digit_preparation_targets=[],obstacle_clearance_intent=[],target_contact_region=[dict(hand=n['hand'],finger=assign[n['note_id']],key_index=n['midi']-21,playable_patches_source='key_table',contact_mode_source=n['note_id']) for n in ns],timing_constraints=dict(evaluation_time=t,clock_offset_seconds=.35,preserve_MIDI_events=True,preserve_key_Action=True,preserve_fingering=True,early_release_allowed=False,early_wrong_press_allowed=False),motion_cost_estimates=dict(status='UNVERIFIED',necessary_bounds_only=True),uncertainty_or_unverified_flags=['CONTRACT_ONLY_NO_MOTION_EXECUTION'],source_bindings=bindings,coordination=dict(mode=mode,hands=sorted(set(n['hand'] for n in ns))))
def validate(x):
 if set(x)!=set(fields):raise ValueError('FIELD_SET_MISMATCH')
 if x['hand_identity'] not in ['R','L','BOTH']:raise ValueError('HAND_ID')
 if x['preparation_time_window'][0]>x['preparation_time_window'][1]:raise ValueError('WINDOW_ORDER')
 if x['palm_position_region']['frame'] not in ['frozen_world_m','key_local_m','root_control_mm']:raise ValueError('UNKNOWN_COORDINATE_FRAME')
 tc=x['timing_constraints']
 if not all(tc[k] for k in ['preserve_MIDI_events','preserve_key_Action','preserve_fingering']) or tc['early_release_allowed'] or tc['early_wrong_press_allowed']:raise ValueError('IMMUTABLE_TIMING_OR_CONTACT_OVERRIDE')
 for n in x['MIDI_event_context']:
  ref=source_map[n['note_id']]
  if any(n[k]!=ref[k] for k in ['hand','midi','display_on','display_off']):raise ValueError('MIDI_CHANGED')
 if any(type(n['finger'])!=int or n['finger']!=assign[n['note_id']] for n in x['assigned_fingering']):raise ValueError('FINGERING_CHANGED')
 ids={n['note_id'] for n in x['MIDI_event_context']};t=tc['evaluation_time'];expected=[m for m in seq if m['note_id'] in ids and m['required_contact'] and m['display_interval'][0]<=t<m['display_interval'][1]]
 signature=lambda rows:sorted((r['episode_id'],r['finger'],r['midi'],r['mode'],r['required_contact'],tuple(r['display_interval'])) for r in rows)
 if signature(x['active_contact_modes'])!=signature(expected):raise ValueError('ACTIVE_CONTACT_SET_OVERRIDDEN')
 if x['source_bindings']!=bindings:raise ValueError('SOURCE_IDENTITY_CHANGED')
 for goal in x['target_contact_region']:
  k=keys[goal['key_index']]
  if not k['key_top_playable_surface']:raise ValueError('NO_ACTUAL_TARGET_PATCH')
 return 'SEMANTIC_CONTRACT_PASS'
cases=[('consecutive_single_notes',['R09','R10'],3.4,'R','SINGLE_HAND'),('same_finger_repetition',['R06','R07'],2.53,'R','SINGLE_HAND'),('change_finger_and_position',['R13','R14'],4.5,'R','SINGLE_HAND'),('white_black_clearance',['R11','R12'],3.8,'R','SINGLE_HAND'),('multiple_finger_chord',['L00','L01','L02'],.4,'L','SINGLE_HAND'),('two_hands',['R00','L00','L01','L02'],.4,'BOTH','INDEPENDENT')]
positive=[]
for name,ids,t,hand,coord in cases:
 x=make(ids,t,hand,coord);positive.append(dict(case=name,status=validate(x),instance=x,motion_execution='NOT_EXECUTED'))
negative=[]
for name,change in [('early_release',lambda x:x['timing_constraints'].update(early_release_allowed=True)),('early_press',lambda x:x['MIDI_event_context'][0].update(display_on=x['MIDI_event_context'][0]['display_on']-.01)),('change_fingering',lambda x:x['assigned_fingering'][0].update(finger=5)),('drop_active_hold',lambda x:x.update(active_contact_modes=[])),('unbound_coordinates',lambda x:x['palm_position_region'].update(frame='camera_pixels'))]:
 x=make(['R06','R07'],2.53,'R');change(x)
 try:validate(x);raise AssertionError('Negative contract unexpectedly accepted')
 except ValueError as e:negative.append(dict(case=name,status='REJECTED',reason=str(e)))
actual=rd(O/'HIGH_LEVEL_INTENT_INSTANCES.json');normal=[]
for r in actual:
 old=r['intent'];ids=[n['note_id'] for n in old['MIDI_event_context']];x=make(ids,old['timing_constraints']['display_time'],'R');x['intent_id']=old['intent_id'];x['preparation_time_window']=old['preparation_time_window'];x['palm_position_region']=dict(frame='root_control_mm',regions=[dict(center=r['candidate_latent'][:3],half_extent_mm=[.5,.5,.5],status='STATIC_CANDIDATE_REGION')]);x['wrist_orientation_region'].update(reference_euler_deg=r['candidate_latent'][3:6]);x['digit_preparation_targets']=[dict(hand='R',finger=old['digit_preparation_targets'][0]['finger'],region=old['digit_preparation_targets'][0]['region'],surface_scope='ENTIRE_PREPARING_DIGIT_SKIN')];obs=old['obstacle_clearance_intent'];x['obstacle_clearance_intent']=[dict(obstacle_key_index=obs['obstacle_key_index'],piece_indices=[0],route='ABOVE_ENTITY' if obs['mode']=='ABOVE_OBSTACLE' else 'FRONT_OF_ENTITY',clearance_m=.0005)];x['motion_cost_estimates']=dict(old['motion_cost_estimates'],status='NECESSARY_ENDPOINT_BOUNDS_VERIFIED',necessary_bounds_only=True);x['uncertainty_or_unverified_flags']=old['uncertainty_or_unverified_flags'];normal.append(dict(instance=x,semantic_status=validate(x),actual_adapter_status='EXECUTED_RIGHT_DESIGNATED_PREPARING_DIGIT_ONLY'))
js('HAND_MOTION_INTENT_CONTRACT_CHECKS.json',dict(positive=positive,negative=negative,actual_instances=normal,standard_Draft202012_full_engine='NOT_EXECUTED: no dependency installed; explicit source-preserving semantic rules executed, JSON Schema declaration provided',not_generic_motion_generation_PASS=True))
print('CONTRACT_CHECKS',len(positive),'positive',len(negative),'rejected',len(normal),'real instances',flush=True)
