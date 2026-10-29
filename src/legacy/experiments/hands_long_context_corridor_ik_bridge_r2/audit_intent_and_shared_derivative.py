from bridge_model import *
import copy,hashlib
plans=json.loads((O/'R2_PLANS.json').read_text(encoding='utf8'));seq=json.loads((O/'CONTACT_STATE_SEQUENCE.json').read_text(encoding='utf8'))['all_source_sequence'];source_byid={e['note_id']:e for e in CTX['events']};checks=[]
def validate_and_compile(p):
 compiled=copy.deepcopy(p);series=p['serialized_intent_series'];deadline=series[-1]['intent']['timing_constraints']['source_event_deadline'];assert deadline==CTX['time_span']['junction']
 for entry in series:
  intent=entry['intent'];t=intent['timing_constraints']['evaluation_time'];expected=[m for m in seq if m['hand']==CTX['hand'] and m['required_contact'] and m['display_interval'][0]<=t<m['display_interval'][1]]
  sig=lambda mm:sorted((m['episode_id'],m['midi'],m['finger'],m['required_contact'],tuple(m['display_interval'])) for m in mm)
  if sig(intent['active_contact_modes'])!=sig(expected):raise ValueError('SERIALIZED_ACTIVE_CONTACT_MODE_MISMATCH:'+entry['phase']['name'])
  for ev in intent['MIDI_event_context']:
   ref=source_byid[ev['note_id']]
   if any(ev[k]!=ref[k] for k in ['hand','midi','display_on','display_off','finger']):raise ValueError('IMMUTABLE_SOURCE_EVENT_CHANGED')
  if intent['timing_constraints']['early_release_allowed'] or intent['timing_constraints']['early_wrong_press_allowed']:raise ValueError('EARLY_CONTACT_OVERRIDE')
  if intent['preparation_time_window']!=entry['phase']['window']:raise ValueError('PHASE_WINDOW_MISMATCH')
 clear=next(e for e in series if e['phase']['name']=='UPPER_CLEARANCE_TRAVERSE');desc=next(e for e in series if e['phase']['name']=='DESCEND');press=next(e for e in series if e['phase']['name']=='PRESS_AND_RELEASE_ESCAPE')
 compiled['reference_time_allocation']['ready']=clear['intent']['preparation_time_window'][1];compiled['mode']=desc['intent']['obstacle_clearance_intent'][0]['descent_strategy'];compiled['target_subset']=desc['intent']['target_contact_region'][0]['subset'];compiled['obstacle']['key_index']=clear['intent']['obstacle_clearance_intent'][0]['obstacle_key_index'];compiled['obstacle']['margin_m']=clear['intent']['obstacle_clearance_intent'][0]['clearance_m'];compiled['serialized_intent_sha256']=hashlib.sha256(json.dumps(series,sort_keys=True).encode()).hexdigest()
 assert compiled['mode']==p['mode'] and compiled['target_subset']==p['target_subset'];assert press['phase']['window']==[deadline,CTX['time_span']['first_full_press']]
 return compiled
for p in plans:
 try:validate_and_compile(p);checks.append(dict(candidate=p['candidate_id'],status='SERIALIZED_CONTRACT_PASS'))
 except ValueError as e:checks.append(dict(candidate=p['candidate_id'],status='REJECTED_SERIALIZED_SCHEMA_SEMANTICS',reason=str(e),normalized_backend_physical_contacts='Backend derived contacts from source clock, so physical equation did not inherit the stale header',corrective_optimizer_execution=False))
# Preserve the first candidate's exact original input; no second optimization of that candidate.
save('candidate_front_PLAN_EXECUTED.json',plans[0])
right=copy.deepcopy(plans[1])
for entry in right['serialized_intent_series']:
 intent=entry['intent'];t=intent['timing_constraints']['evaluation_time'];intent['active_contact_modes']=[copy.deepcopy(m) for m in seq if m['hand']==CTX['hand'] and m['required_contact'] and m['display_interval'][0]<=t<m['display_interval'][1]]
 intent['palm_position_region']=dict(frame='frozen_world_m',regions=[dict(kind='AUTHORIZED_RIG_REACHABLE_REGION_REQUEST',source='POLICY_LOCK.json',fixed_waypoint=False)])
 intent['wrist_orientation_region']=dict(frame='frozen_root_rest_axes',units='degrees',authorized_control_bounds=[[-8,-8,-12],[8,8,12]])
 intent['motion_cost_estimates']=dict(status='REFERENCE_SCOPED_SCHEDULE_ESTIMATE',necessary_bounds_only=True,reference_allocation=right['reference_time_allocation'])
 if abs(t-CTX['time_span']['junction'])<1e-10:intent['timing_constraints']['closed_left_contact_compatibility_required']=True
right=validate_and_compile(right);save('candidate_right_PLAN_COMPILED.json',right);checks.append(dict(candidate='candidate_right',status='CORRECTED_SERIALIZED_CONTRACT_PASS',correction_scope='State labels/derived fields only before any second IK call; same timing/corridor/physical equations'))
front=json.loads((O/'candidate_front_RESULT.json').read_text(encoding='utf8'));Z=np.array(front['initial']);T=np.array(front['times'])
# The actual IPOPT first interior push is visible as9.9e-7 in the recorded log.
pushed=np.clip(Z,LOW+.99e-6,HIGH-.99e-6);pushed[0]=Z[0];t=(T[0]+T[1])/2;before=numeric_curve(Z,T,t)[0];trial=numeric_curve(pushed,T,t)[0];diagnostics=[]
for p in [plans[0],right]:
 n=CorridorNode(before,[p['held_contact']],keyangles(t),t,p);mats=[];steps=[]
 for h in [1e-4,1e-5,1e-6]:
  M=n.jac(trial,h);mats.append(M)
  if len(mats)>1:
   diff=abs(mats[-1]-mats[-2]);ri,ci=np.unravel_index(diff.argmax(),diff.shape);nc=1;key_start=nc+6*nc;key_end=key_start+len(n.pieces);kind='contact_normal' if ri<nc else ('pad_or_crossing' if ri<key_start else ('key_piece' if ri<key_end else ('self_separator' if ri<key_end+len(n.pairs) else 'corridor')))
   info=dict(h=h,max_difference=float(diff[ri,ci]),row=int(ri),column=int(ci),row_kind=kind)
   if kind=='key_piece':info['key_piece_identity']=dict(midi=int(n.pieces[ri-key_start][0]),piece_list_index=int(ri-key_start))
   step=h*(.1 if ci>=10 else 1);dd=np.eye(12)[ci]*step;info['base']=float(n.value(trial)[ri]);info['plus']=float(n.value(trial+dd)[ri]);info['minus']=float(n.value(trial-dd)[ri]);steps.append(info)
 try:n.checked_jac(trial);guard='VERIFIED'
 except ValueError as e:guard='STRICT_GUARD_REJECTED'
 diagnostics.append(dict(candidate=p['candidate_id'],time=t,initial_node_before_IPOPT_push=before.tolist(),tested_trial=trial.tolist(),IPOPT_push_rule='Reconstructed .99e-6 interior push from captured raw log; fixed start left exact',steps=steps,guard=guard,all_node_contacts=CTX['pair']['held']['note_id'],full_exact_IPOPT_trial_not_claimed=True))
same=np.max(abs(np.array(diagnostics[0]['tested_trial'])-diagnostics[1]['tested_trial']))==0
if same and diagnostics[1]['guard']=='STRICT_GUARD_REJECTED':
 result=dict(candidate_id='candidate_right',authority='DESIGN_PROVISIONAL — STOP — HUMAN REVIEW',status='EARLY_STOP_SHARED_EXECUTOR_DERIVATIVE_REJECTION',solver_called=False,initial=front['initial'],latents=front['initial'],times=front['times'],history=[],error='Same initial HOLD collocation and strict derivative rejection as candidate_front; do not repeat an expensive identical failing Jacobian',different_high_level_strategy=right['mode'],actual_validation='INITIALIZER_PREVIEW_ONLY; geometry may reuse exact duplicate controls/time/source Action, no solved path claim',fixed_start_error=front['fixed_start_error'],compiled_intent_file='candidate_right_PLAN_COMPILED.json')
 save('candidate_right_RESULT.json',result)
save('R2_INTENT_SEMANTIC_AUDIT.json',dict(original_inputs=checks,historical_front_input_preserved=True,first_candidate_no_optimization_retry=True,right_compiler_consumes_serialized_series=True))
save('R2_DERIVATIVE_SHARED_BLOCKER.json',dict(diagnostics=diagnostics,shared_same_trial=same,second_expensive_solver_early_stopped=same and diagnostics[1]['guard']=='STRICT_GUARD_REJECTED',exact_recorded_front_errors=[.24846700914515907,.36132615210959873],rule='Candidate early stop follows a reproduced common executor precondition failure, not a claim that both corridors or human motions are impossible.'))
print('R2_SHARED_BLOCKER',diagnostics,'same',same,flush=True)
