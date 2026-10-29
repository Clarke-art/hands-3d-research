from coupled_model import *
from scipy.optimize import linprog
import copy,hashlib
CTX=json.loads((O/'R2_CONTEXT_RAW.json').read_text(encoding='utf8'));I=json.loads((O/'EXPERIMENT_INPUT.json').read_text(encoding='utf8'))
def keyangles(t):
 out=np.zeros(88)
 for idx,curves in CTX['curves'].items():
  for f in curves:
   if f['path']=='rotation_euler' and f['index']==0:
    assert all(p['interpolation']=='LINEAR' for p in f['points'])
    out[int(idx)]=np.interp(t,[p['time'] for p in f['points']],[p['value'] for p in f['points']])
 return out
def contact_transport(z,ct,t):
 a=keyangles(t);node=DynamicNode(z,[ct],a,t,(LOW,HIGH))
 for _ in range(3):
  k=c.KEYS[ct['midi']-21];normal=c.axisrot(-a[k['key_index']],k['press_axis'])[2,2];
  try:z[2]-=node.value(z)[0]/normal
  except ValueError as e:
   if 'NO_PROJECTED_PULP_FACE' not in str(e):raise
   return z  # Unverified initializer; fixed-material IK will resolve it before the joint graph.
 return z
def load_inputs():
 A=O.parent/'hands_long_context_hand_motion_architecture_r1';failure=json.loads((A/'BASELINE_FAILURE_READONLY_CHECK.json').read_text(encoding='utf8'));ob=failure['obstacle']
 return ob,CTX['contact_descriptors'][0],CTX['contact_descriptors'][1]
def generate_plans():
 ob,held,press=load_inputs();finger=press['finger'];assert finger==I['next']['finger']
 t0=CTX['time_span']['start'];event=CTX['time_span']['junction'];end=CTX['time_span']['first_full_press'];Z0=np.array(CTX['known_start']['latent']);ref=np.array(CTX['reference_common']['latent']);Vref=skin(state(ref));pad=Vref[int(RAW['pad_indices'][finger-1])];patch=Vref[np.array(META['pad_patches'][finger-1])]
 rx=float(np.max(abs(patch[:,0]-pad[0])));ry=float(np.max(abs(patch[:,1]-pad[1])));s=ob['key_top_playable_surface'][0];target=c.KEYS[press['midi']-21]['key_top_playable_surface'][0];future=next((n for n in CTX['events'] if n['display_on']>=CTX['pair']['next']['display_off']-1e-10 and n['note_id']!=CTX['pair']['next']['note_id']),None);future_x=c.KEYS[future['midi']-21]['key_center'][0] if future else (target['xmin']+target['xmax'])/2
 plans=[];schedule_audit=[]
 for mode in ['FRONT_DESCENT_AND_FRONT_RELEASE','RIGHT_DESCENT_AND_FRONT_RELEASE']:
  subset=dict(xmin=target['xmin']+.00002,xmax=target['xmax']-.00002,ymin=target['ymin']+.00002,ymax=target['ymax']-.00002,z=target['z'])
  if mode.startswith('FRONT'):
   subset['ymax']=min(subset['ymax'],s['ymin']-ry-.0005)
   # Preview of the following event chooses the near side of the current playable set.
   if future_x<(target['xmin']+target['xmax'])/2:subset['xmax']=(target['xmin']+target['xmax'])/2
   else:subset['xmin']=(target['xmin']+target['xmax'])/2
  else:subset['xmin']=max(subset['xmin'],s['xmax']+rx+.0005)
  if subset['xmin']>=subset['xmax'] or subset['ymin']>=subset['ymax']:
   schedule_audit.append(dict(mode=mode,status='EARLY_REJECT_EMPTY_PLAYABLE_SUBSET',subset=subset));continue
  goal=np.array([(subset['xmin']+subset['xmax'])/2,(subset['ymin']+subset['ymax'])/2,pad[2]])
  seed=ref.copy();seed[:2]+=(goal[:2]-pad[:2])*1000;raised=seed.copy();raised[11]=0.;raised=contact_transport(raised,held,t0)
  velocity=np.array(CTX['motion_bounds']['latent_velocity']);w0=np.array(KIN(Z0)[0]).ravel();wr=np.array(KIN(raised)[0]).ravel();reference_ready=max(float(np.linalg.norm(wr-w0))*1000/500,float(np.max(abs(raised-Z0)/velocity)),float(np.max(abs(state(raised)[6:]-state(Z0)[6:]))/240))
  reference_descent=max(float(abs(seed[11]-raised[11])/velocity[11]),float(np.max(abs(state(seed)[6:]-state(raised)[6:]))/240))
  # Conservative allowance for a cubic C1 connector, scoped to the selected reference initializer.
  minimum=[1.5*reference_ready,1.5*reference_descent]
  fit=linprog([1.,0.],A_eq=[[1.,1.]],b_eq=[event-t0],bounds=[(minimum[0],None),(minimum[1],None)],method='highs')
  if not fit.success:
   schedule_audit.append(dict(mode=mode,status='EARLY_REJECT_SELECTED_PRIMITIVE_SCHEDULE',selected_reference_minimum=minimum,available=event-t0,not_all_boundary_states_ruled_out=True));continue
  ready=t0+float(fit.x[0]);descent=float(fit.x[1]);press_duration=end-event
  times=sorted(set([t0,(t0+ready)/2,ready,event-descent/2,event-press_duration,event,event+press_duration/2,end]))
  # Hint only; all non-start controls remain solver variables.
  guesses=[]
  for t in times:
   if t<=ready:
    u=(t-t0)/(ready-t0);z=(1-u)*Z0+u*raised;z[11]=max(0.,(1-u)*Z0[11])
   elif t<=event:
    u=(t-ready)/(event-ready);z=(1-u)*raised+u*seed
   else:
    u=(t-event)/(end-event);z=seed.copy()
    # Source release context supplies a front escape request, not an early release.
    thumbpad=Vref[int(RAW['pad_indices'][held['finger']-1])];thumbpatch=Vref[np.array(META['pad_patches'][held['finger']-1])]
    y_extent=max(float(p[1]-c.KEYS[held['midi']-21]['key_top_playable_surface'][0]['ymin']) for p in thumbpatch);z[1]-=u*(max(0.,y_extent)+.0005)*1000;z[11]+=u*(1-z[11])
   ct=held if t<event else press;z=contact_transport(z,ct,t);z=np.clip(z,LOW,HIGH);guesses.append(z.tolist())
  pid='candidate_front' if mode.startswith('FRONT') else 'candidate_right';phases=[
   dict(name='PREPARE',window=[t0,ready],entry='Actual known start and all active contacts',exit='Target hand region compatible with raised digit'),
   dict(name='LIFT_OR_MAINTAIN_ALREADY_RAISED',window=[t0,ready],entry='Source free preparing digit only',exit='Whole preparing digit satisfies upper clearance region; no early key Action'),
   dict(name='UPPER_CLEARANCE_TRAVERSE',window=[t0,ready],entry='Original held contacts remain hard',exit='Reached a position admitting the selected descending corridor'),
   dict(name='DESCEND',window=[ready,event],entry='Clearance transition occurs while all held contacts stay valid',exit='Original target contact set met at exact MIDI ON'),
   dict(name='PRESS_AND_RELEASE_ESCAPE',window=[event,end],entry='Atomic original OFF/ON; closed boundary contact compatibility',exit='Follow source target descent and avoid recovering released key')]
  plan=dict(candidate_id=pid,mode=mode,authority='DESIGN_PROVISIONAL — STOP — HUMAN REVIEW',context_event_ids=[n['note_id'] for n in CTX['events']],phase_schedule=phases,reference_time_allocation=dict(method='LP over original current-event window with reference-scoped motion estimates; earlier readiness minimized',ready_minimum_seconds=minimum[0],descent_minimum_seconds=minimum[1],ready=ready,descent_start=ready,source_event=event,scope_end=end,LP_objective=float(fit.fun),reference_bounds_not_universal=True),obstacle=dict(key_index=ob['key_index'],piece=0,finger=finger,margin_m=.0005),held_contact=held,target_contact=press,target_subset=subset,next_event_preview=future,target_subset_choice_uses_future_key_x=future_x,release_escape=dict(finger=held['finger'],key_index=held['midi']-21,mode='FRONT_ESCAPE_AFTER_SOURCE_OFF',required_at=end,margin_m=.0005),time_grid=times,initial_states=guesses,known_start_fixed=True,old_prefix_internal_anchors_fixed=False,old_common_fixed=False,corridor_rule='Per whole digit triangle, conservative halfspace union; ABOVE during traverse, then FRONT or RIGHT descent strategy; all physical gates unchanged',unverified=['REFERENCE_BANK_WARM_START_IS_C01_SPECIFIC','CORRIDOR_IK_FEASIBILITY','INTERVAL_GEOMETRY','HUMAN_NATURALNESS'])
  base=json.loads((O.parent/'hands_long_context_hand_motion_architecture_r1/HAND_MOTION_INTENT_CONTRACT_CHECKS.json').read_text(encoding='utf8'))['actual_instances'][1]['instance'];series=[]
  for phase in phases:
   intent=copy.deepcopy(base);intent['intent_id']=pid+':'+phase['name'];intent['MIDI_event_context']=CTX['events'];intent['assigned_fingering']=[dict(note_id=n['note_id'],hand=n['hand'],finger=n['finger']) for n in CTX['events']];intent['preparation_time_window']=phase['window'];intent['timing_constraints']['evaluation_time']=phase['window'][1];intent['timing_constraints']['source_event_deadline']=event;intent['digit_preparation_targets']=[dict(hand=CTX['hand'],finger=finger,surface_scope='WHOLE_DIGIT_TRIANGLE_SURFACES',region=dict(mode=mode,obstacle_key_index=ob['key_index'],margin_m=.0005,phase=phase['name']))];intent['obstacle_clearance_intent']=[dict(obstacle_key_index=ob['key_index'],piece_indices=[0],route='ABOVE_ENTITY',clearance_m=.0005,phase_window=phase['window'],descent_strategy=mode)];intent['target_contact_region']=[dict(hand=CTX['hand'],finger=press['finger'],key_index=press['midi']-21,playable_patches_source='unchanged_key_table',contact_mode_source=press['note_id'],subset=subset,active_at=event)];intent['uncertainty_or_unverified_flags']=plan['unverified'];series.append(dict(phase=phase,intent=intent))
  plan['serialized_intent_series']=series;plans.append(plan);save('plans/'+pid+'.json',plan) if (O/'plans').exists() else None
  schedule_audit.append(dict(mode=mode,status='PROPOSED_NOT_IK_PASS',selected_reference_minimum=minimum,ready=ready,descent_window=[ready,event],held_contact_until=CTX['pair']['held']['display_off'],target_subset=subset))
 return plans,schedule_audit
if __name__=='__main__':
 (O/'plans').mkdir(exist_ok=True);plans,audit=generate_plans();save('R2_PLANS.json',plans);save('R2_SCHEDULE_AUDIT.json',dict(plans=audit,candidate_count=len(plans),context=CTX['events'],warm_start_only='Existing static common reference used as numerical initializer; no old safe pose timestamp shifted or accepted',all_MIDI_times_preserved=True));assert len(plans)<=2
 print('R2_PLANS',[(p['candidate_id'],p['reference_time_allocation'],p['target_subset']) for p in plans],flush=True)
