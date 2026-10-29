from coupled_model import *
import hashlib
I=json.loads((O/'EXPERIMENT_INPUT.json').read_text(encoding='utf8'))
def read(n):return json.loads((O/n).read_text(encoding='utf8'))
def transport(z,contacts,angles,t):
 nd=DynamicNode(z,contacts,angles,t,(LOW,HIGH))
 for _ in range(3):
  k=c.KEYS[contacts[0]['midi']-21];normal=c.axisrot(-angles[k['key_index']],k['press_axis'])[2,2];z[2]-=nd.value(z)[0]/normal
 return z
def adapt_intent(intent,baseline_latent,contacts,key_angles):
 if intent['hand_identity']!='R':raise ValueError('UNSUPPORTED_ADAPTER_HAND: schema can express it, current actual adapter cannot')
 if any(ct['mode'] not in ['HOLD','PRESS'] or not ct['required_contact'] for ct in intent['active_contact_modes']):raise ValueError('UNSUPPORTED_CONTACT_PHASE')
 if not intent['timing_constraints']['preserve_MIDI_events'] or intent['timing_constraints']['early_release_allowed'] or intent['timing_constraints']['early_wrong_press_allowed']:raise ValueError('IMMUTABLE_SOURCE_CONTRACT')
 target=intent['digit_preparation_targets'][0];finger=target['finger'];ob=intent['obstacle_clearance_intent'][0];k=c.KEYS[ob['obstacle_key_index']];surface=k['key_top_playable_surface'][0];region=target['region'];z=np.array(baseline_latent).copy();aa=np.array(key_angles);t=intent['timing_constraints']['evaluation_time'];mode=ob['route']
 if mode=='ABOVE_ENTITY':
  if finger!=I['next']['finger']:raise ValueError('UNSUPPORTED_PREPARING_DIGIT_CAPABILITY')
  # Select maximum extension from the existing natural-family control, then check the intent geometry.
  z[11]=0.;z=transport(z,contacts,aa,t)
 elif mode=='FRONT_OF_ENTITY':
  if abs(aa[k['key_index']])>1e-8:raise ValueError('UNSUPPORTED_MOVING_OBSTACLE_FRAME')
  def envelope(zz):
   loc=keylocal(skin(state(zz)),k,aa[k['key_index']]);pts=[]
   for ti in np.flatnonzero(LABEL==finger-1):
    poly=[p.copy() for p in loc[TR[ti]]]
    for axis,bound,sign in [(0,surface['xmin'],-1),(0,surface['xmax'],1),(2,surface['z']+ob['clearance_m'],1)]:poly=clip(poly,axis,bound,sign) if poly else []
    pts.extend(poly)
   return max(p[1] for p in pts) if pts else None
  e=envelope(z)
  if e is not None:z[1]+=min(0.,(region['key_local_y_upper_m']-e)*1000)
  z=transport(z,contacts,aa,t);e=envelope(z)
  if e is not None and e>region['key_local_y_upper_m']:z[1]-=(e-region['key_local_y_upper_m'])*1000;z=transport(z,contacts,aa,t)
 else:raise ValueError('UNSUPPORTED_CORRIDOR_MODE')
 if np.any(z<LOW) or np.any(z>HIGH):raise ValueError('OUTSIDE_AUTHORIZED_RIG_DOMAIN')
 return z
if __name__=='__main__':
 begin=time.monotonic();contracts=read('HAND_MOTION_INTENT_CONTRACT_CHECKS.json')['actual_instances'];source=read('HIGH_LEVEL_CLEARANCE_REQUESTS.json');raw=read('HIGH_LEVEL_INTENT_INSTANCES.json');baseline=read('BASELINE_FAILURE_READONLY_CHECK.json');P=O.parent/'hands_early_hand_preparation_entry_reachability_r1';old=next(r for r in json.loads((P/'ENTRY_ACTUAL_SAMPLES.json').read_text(encoding='utf8')) if r['id']==baseline['worst_failure']['id']);replay=[]
 for case,req,info in zip(contracts,source,raw):
  intent=case['instance'];z=adapt_intent(intent,info['initial_latent'],req['contacts'],old['key_angles']);diff=float(np.max(abs(z-np.array(req['latent']))));assert diff<1e-10
  st=state(z);sdiff=float(np.max(abs(st-np.array(req['state']))));assert sdiff<1e-10
  replay.append(dict(intent_id=intent['intent_id'],serialized_intent_consumed=True,source_contract='HAND_MOTION_INTENT_CONTRACT_CHECKS.json:actual_instances',key_index_not_note_name=True,input_pose_is_historical_failed_baseline=True,output_control_max_difference_from_Blender_checked_candidate=diff,output_full_state_difference=sdiff,frame=req['display_time'],actual_geometry_reused_by_identical_state=True,all_actual_gates=next(r['actual_ALL_GATES'] for r in read('REAL_RIG_CLEARANCE_FEASIBILITY.json')['candidates'] if r['candidate_id']==req['id'])))
 elapsed=time.monotonic()-begin;save('SERIALIZED_INTENT_ADAPTER_EXECUTION.json',dict(status='EXECUTED_REAL_FROZEN_RIG_ADAPTER_FROM_SERIALIZED_INTENT',candidates=replay,additional_candidate_count=0,additional_optimizer_calls=0,elapsed_seconds=elapsed,unimplemented=['LEFT_OR_BIMANUAL_ADAPTER','CONTINUOUS_CORRIDOR_TRACKING','GENERATED_HUMAN_MOTION_PRIOR']))
 facts=read('REAL_RIG_CLEARANCE_FEASIBILITY.json');facts['serialized_intent_adapter_execution']='SERIALIZED_INTENT_ADAPTER_EXECUTION.json';facts['intents_consumed_before_FK_adaptation']=True;save('REAL_RIG_CLEARANCE_FEASIBILITY.json',facts)
 budget=read('NUMERICAL_BUDGET.json');budget['stages'].append(dict(name='serialized_intent_adapter_replay',script='intent_rig_adapter.py',wall_seconds=elapsed,cap_seconds=70,exit_code=0,status='COMPLETED_SAME_TWO_CANDIDATES_NO_SEARCH'));budget['total_seconds']=sum(r['wall_seconds'] for r in budget['stages']);budget['under_budget']=budget['total_seconds']<=600;save('NUMERICAL_BUDGET.json',budget);print('SERIALIZED_INTERFACE_EXECUTED',replay,flush=True)
