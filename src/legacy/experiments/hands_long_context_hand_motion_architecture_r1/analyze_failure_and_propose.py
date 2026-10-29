from coupled_model import *
import hashlib
I=json.loads((O/'EXPERIMENT_INPUT.json').read_text(encoding='utf8'))
P=O.parent/'hands_early_hand_preparation_entry_reachability_r1'
def read(n):return json.loads((P/n).read_text(encoding='utf8'))
rows=sorted(read('ENTRY_ACTUAL_SAMPLES.json')+read('ENTRY_ADAPTIVE_ACTUAL.json'),key=lambda r:r['display_time'])
facts=read('FINAL_FACTS.json');last=next(r for r in rows if r['id']==facts['entry_prefix']['last_pass_id']);worst=max(rows,key=lambda r:r['non_target_or_wrong_region_max_mm']);first=next(r for r in rows if not r['all_gates'])
assert len(rows)==85 and sum(not r['all_gates'] for r in rows)==45
assert first['display_time']==facts['entry_prefix']['first_sampled_failure_time']
hits=worst['contact_results'][0]['geometry']['key_hits'];hit=max((h for h in hits if h['role']=='NON_TARGET_KEY'),key=lambda h:h['maximum_triangle_surface_inside_depth_mm'])
obstacle=next(k for k in c.KEYS if k['midi_note']==hit['midi']);assert obstacle['color']=='BLACK'
digit_name=max(hit['digit_attribution'],key=lambda d:hit['digit_attribution'][d]['max_depth_mm']);finger=c.DIGITS.index(digit_name)+1
skinV=np.load(P/('AUDIT_'+worst['id']+'_ACTUAL_SKIN.npz'))['vertices'];aa=np.array(worst['key_angles']);local=keylocal(skinV,obstacle,aa[obstacle['key_index']]);s=obstacle['key_top_playable_surface'][0]
witness=[]
for r in hit['triangle_interior_witnesses']:
 p=keylocal(np.array([r['world_point_m']]),obstacle,aa[obstacle['key_index']])[0]
 distances_mm={'left':(p[0]-s['xmin'])*1000,'right':(s['xmax']-p[0])*1000,'front':(p[1]-s['ymin'])*1000,'back':(s['ymax']-p[1])*1000,'top':(s['z']-p[2])*1000,'bottom':p[2]*1000}
 ti=r['hand_triangle_id'];weights=RAW['weights'][TR[ti]].mean(0);names=[dict(bone=META['names'][i],mean_weight=float(weights[i])) for i in np.argsort(weights)[-3:][::-1]]
 witness.append(dict(triangle=ti,world_point_m=r['world_point_m'],local_point_m=p.tolist(),inside_depth_mm=r['inside_depth_mm'],nearest_entity_face=min(distances_mm,key=distances_mm.get),support_plane_distances_mm=distances_mm,controlling_bones=names))
events=read('SOURCE_MIDI_REVALIDATION.json')['notes'];context=[n for n in events if n['hand']==I['hold'].get('hand','R') and last['display_time']-1.2<n['display_on']<last['display_time']+1.2]
anatomy=json.loads((O.parent/'hands_c01_anatomy_preparation_audit_r1/B_SOLVE_2.json').read_text(encoding='utf8'))
save('BASELINE_FAILURE_READONLY_CHECK.json',dict(status='READONLY_VERIFIED',all_original_counts_match=True,prefix=facts['entry_prefix'],worst_failure=dict(id=worst['id'],time=worst['display_time'],wrong_depth_mm=worst['non_target_or_wrong_region_max_mm']),E5_contact_failures=facts['required_contact_failures'],target_max_depth_mm=facts['entry_target_max_depth_mm'],self_crossings=facts['entry_self_crossings_max'],original_actions_match=facts['original_actions_all'],obstacle=obstacle,dominant_digit=dict(name=digit_name,finger=finger),witnesses=witness,lookahead_context=context,earlier_R06_to_R07='READONLY_CONTEXT; CONTINUOUS_ENTRY_UNVERIFIED',source_files={n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['ENTRY_ACTUAL_SAMPLES.json','ENTRY_ADAPTIVE_ACTUAL.json','FINAL_FACTS.json','ENTRY_CORRECTION_RESULT.json','PROTECTION_SCOPE_AUDIT.json']}))
def pulp_hold_transport(z,angle):
 nd=DynamicNode(z,[I['contacts'][0]],angle,worst['display_time'],(LOW,HIGH));trace=[]
 for _ in range(3):
  v=nd.value(z);normal=c.axisrot(-angle[I['hold']['midi']-21],c.KEYS[I['hold']['midi']-21]['press_axis'])[2,2];trace.append(float(v[0]));z[2]-=v[0]/normal
 return z,trace
def low_x_envelope(z):
 V=keylocal(skin(state(z)),obstacle,aa[obstacle['key_index']]);points=[]
 for ti in np.flatnonzero(LABEL==finger-1):
  poly=[p.copy() for p in V[TR[ti]]]
  for axis,bound,sign in [(0,s['xmin'],-1),(0,s['xmax'],1),(2,s['z']+.0005,1)]:
   poly=clip(poly,axis,bound,sign) if poly else []
  points.extend(poly)
 return max(p[1] for p in points) if points else None
zbase=np.array(worst['latent']);dt=worst['display_time']-last['display_time'];requests=[];candidate_info=[]
# Two spatially distinct plans, not alternate objective weights.
for mode in ['FRONT_OF_OBSTACLE','ABOVE_OBSTACLE']:
 z=zbase.copy();transport=[];target={}
 if mode=='FRONT_OF_OBSTACLE':
  y_envelope=low_x_envelope(z);required=(s['ymin']-.0005-y_envelope)*1000
  z[1]+=min(0.,required)
  z,tr=pulp_hold_transport(z,aa);transport+=tr
  # One geometric correction only: root normal transport can enlarge low-Z envelope.
  remaining=low_x_envelope(z)
  if remaining is not None and remaining>s['ymin']-.0005:
   z[1]-=(remaining-(s['ymin']-.0005))*1000;z,tr=pulp_hold_transport(z,aa);transport+=tr
  target=dict(kind='KEEP_EXPOSED_DIGIT_SURFACES_IN_FRONT_CORRIDOR',key_local_y_upper_m=s['ymin']-.0005,clearance_mm=.5,geometry_basis='All middle triangles overlapping obstacle X and below its top+0.5mm, not just fingertip')
 else:
  assert finger==I['next']['finger'],'Existing preparation-alpha adapter only controls the designated preparing digit'
  z[11]=0.;z,tr=pulp_hold_transport(z,aa);transport+=tr
  target=dict(kind='RAISE_PREPARING_DIGIT_OVER_ENTITY_TOP',key_local_z_lower_m=s['z']+.0005,clearance_mm=.5,geometry_basis='Measured whole digit/obstacle overlap; maximum extension inside unchanged authorized reference family',adapter_limit='Existing alpha only; no new joint domain or rig changes')
 V=skin(state(z));loc=keylocal(V,obstacle,aa[obstacle['key_index']]);ids=np.flatnonzero(LABEL==finger-1);vertices=np.unique(TR[ids]);relevant=loc[vertices];inside_xy=(relevant[:,0]>=s['xmin'])&(relevant[:,0]<=s['xmax'])&(relevant[:,1]>=s['ymin'])&(relevant[:,1]<=s['ymax'])
 w=np.array(KIN(z)[0]).ravel();dis=float(np.linalg.norm(w-np.array(last['wrist_world_m']))*1000);dq=abs(state(z)[6:]-np.array(last['state'])[6:]);dz=abs(z-np.array(last['latent']))
 rid='high_level_front' if mode=='FRONT_OF_OBSTACLE' else 'high_level_above'
 intent=dict(intent_id=rid,hand_identity='R',MIDI_event_context=context,assigned_fingering_source=read('SOURCE_MIDI_REVALIDATION.json')['candidate_file'],active_contact_modes=[m for m in read('CONTACT_STATE_SEQUENCE.json')['all_source_sequence'] if m['hand']=='R' and m['required_contact'] and m['display_interval'][0]<=worst['display_time']<m['display_interval'][1]],preparation_time_window=[last['display_time'],worst['display_time']],palm_position_region=dict(frame='frozen_world',adapter_control='existing_root_translation',region_kind=mode),wrist_orientation_region=dict(reference_root_euler_deg=zbase[3:6].tolist(),unchanged=True),digit_preparation_targets=[dict(finger=finger,region=target)],obstacle_clearance_intent=dict(obstacle_key_index=obstacle['key_index'],obstacle_semantic_identity=obstacle['semantic_identity'],mode=mode),target_contact_region=dict(key_index=I['hold']['midi']-21,finger=I['hold']['finger'],required_mode='HOLD',source='existing contract'),timing_constraints=dict(display_time=worst['display_time'],alter_midi_or_Action=False,early_release=False,early_wrong_press=False),motion_cost_estimates=dict(available_seconds=dt,wrist_distance_from_verified_prefix_mm=dis,necessary_wrist_seconds=dis/500,maximum_joint_delta_deg=float(dq.max()),necessary_joint_seconds=float(dq.max()/240)),uncertainty_or_unverified_flags=['STATIC_CANDIDATE_ONLY','CONNECTION_FROM_PREFIX_UNVERIFIED','NO_HUMAN_MOTION_PRIOR','NOT_CONTINUOUS_ENTRY_PASS'])
 requests.append(dict(id=rid,display_time=worst['display_time'],contacts=[I['contacts'][0]],latent=z.tolist(),state=state(z).tolist()))
 candidate_info.append(dict(intent=intent,initial_latent=zbase.tolist(),candidate_latent=z.tolist(),normal_transport_residual_trace_mm=transport,domain_pass=bool(np.all(z>=LOW)&np.all(z<=HIGH)),necessary_motion_bounds_pass=bool(dis<=500*dt and dq.max()<=240*dt and np.all(dz<=np.r_[[500]*3,[120]*3,[240]*4,5,8]*dt)),overlapping_XY_digit_vertex_min_z_mm=float(relevant[inside_xy,2].min()*1000) if inside_xy.any() else None,baseline_obstacle_surface_top_z_mm=s['z']*1000,FK_vertices=len(V)))
save('HIGH_LEVEL_CLEARANCE_REQUESTS.json',requests);save('HIGH_LEVEL_INTENT_INSTANCES.json',candidate_info)
print('GEOMETRIC_INTENTS',[(r['intent']['intent_id'],r['candidate_latent'][1],r['candidate_latent'][11],r['domain_pass'],r['necessary_motion_bounds_pass']) for r in candidate_info],flush=True)
