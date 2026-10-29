from pathlib import Path
import json,hashlib,math
import numpy as np
P=Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
def dump(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def sha(n):return hashlib.sha256((P/n).read_bytes()).hexdigest()
policy=read('CONTACT_TOLERANCE_POLICY_R1.json');assert sha('CONTACT_TOLERANCE_POLICY_R1.json')==read('PRE_RESULT_POLICY_LOCK_R1.json')['sha256']
tl=read('PERFORMANCE_TIMELINE_R1.json');keys=read('KEYBOARD_88_KEY_TABLE_R1.json')['keys'];motion=np.load(P/'hand_motion_canonical.npz');ext=read('HAND_EXTRACTION_R1.json');N=421;times=np.arange(N)/60
def active(t):return [n for n in tl['notes'] if n['source_on_sec']<=11.5+t<n['source_off_sec']]
# Approved runtime update/ease at a declared fixed60Hz audit clock, all note owners retained.
angles=np.zeros((N,88));a=np.zeros(88)
for i,t in enumerate(times):
 held={n['key_index'] for n in active(t)};target=np.array([k['press_angle_rad'] if j in held else 0 for j,k in enumerate(keys)])
 # Start at an already-settled state for carry-in notes; subsequent frames update once.
 if i==0:a=target.copy()
 else:a=np.where(np.abs(a-target)<.00005,target,a+(target-a)*.42)
 angles[i]=a
def rot(points,pivot,angle):
 p=np.array(points)-pivot;c=np.cos(angle);s=np.sin(angle);q=p.copy();q[...,1]=p[...,1]*c-p[...,2]*s;q[...,2]=p[...,1]*s+p[...,2]*c;return q+pivot
def target_for(k,a):
 x=k['key_center'][0];y=k['front_extent']+(.025 if k['color']=='WHITE' else .015)
 surf=next(s for s in k['key_top_playable_surface'] if s['xmin']<=x<=s['xmax'] and s['ymin']<=y<=s['ymax'])
 return rot(np.array([x,y,surf['z']]),np.array(k['press_pivot']),a)
def measurement(point,k,a):
 pv=np.array(k['press_pivot']);q=rot(point,pv,-a);surfaces=k['key_top_playable_surface'];ds=[math.hypot(max(s['xmin']-q[0],0,q[0]-s['xmax']),max(s['ymin']-q[1],0,q[1]-s['ymax'])) for s in surfaces];j=int(np.argmin(ds));s=surfaces[j]
 top=pv[2]+(s['z']-pv[2])/math.cos(a)+(point[1]-pv[1])*math.tan(a)
 gap=float(point[2]-top)*1000;err=ds[j]*1000;inside=err<1e-5
 return {'vertical_gap_mm':gap,'horizontal_in_key_error_mm':err,'inside_correct_playable_region':inside,'penetration':bool(inside and gap<-policy['penetration_threshold_mm']),'contact_within_fixed_tolerances':bool(inside and abs(gap)<=policy['CONTACT_VERTICAL_TOLERANCE_MM'] and err<=policy['CONTACT_HORIZONTAL_TOLERANCE_MM'])}
D=np.diff(np.eye(N),n=2,axis=0);lam=(.080*60)**4;roots={};models={};metrics={};spatial={};contacts=[];chords=[];safeties={}
for side in ['R','L']:
 pads=motion[side+'_pads'];weights=np.zeros(N);rhs=np.zeros((N,3));targets=[];sets=[]
 for i,t in enumerate(times):
  assigned=[n for n in active(t) if n['hand']==side and n['finger']];sets.append(assigned)
  for n in assigned:
   k=keys[n['key_index']];tar=target_for(k,angles[i,n['key_index']]);rhs[i]+=tar-pads[i,n['finger']-1];weights[i]+=1
 assert weights.sum()>0
 # One global linear solve; translation only; all contacts use identical coefficients.
 T=np.linalg.solve(np.diag(weights)+lam*(D.T@D),rhs);roots[side]=T;V=motion[side+'_verts']+T[:,None,:];PP=pads+T[:,None,:];spatial[side+'_verts']=V;spatial[side+'_pads']=PP;spatial[side+'_roots']=T
 steps=np.linalg.norm(np.diff(T,axis=0),axis=1)*1000
 models[side]={'static_alignment':ext['frames'][side],'time_varying_DOF':['x','y','z'],'dynamic_rotation_DOF':0,'scale_changes':0,'lambda':lam,'smoothing_time_sec':.080,'constraints':int(weights.sum()),'constrained_observations':int((weights>0).sum()),'max_step_mm_per_60Hz':float(steps.max()),'root_jump_flag':bool(steps.max()>policy['root_jump_flag_mm_per_60Hz']),'translation_m':T.tolist(),'root_transform_definition':'world=Q*(native-wrist)+T(t); external empty only','review_offsets_inherited':False,'fit_status':'PROVISIONAL; predicted labels used as fitting hypotheses, not independent evidence'}
 for e in tl['events']:
  if e['event_type']!='NOTE_ON' or e['hand']!=side or not e['finger']:continue
  u=e['time_sec']*60;i=min(int(u),419);f=u-i;pt=(1-f)*PP[i,e['finger']-1]+f*PP[i+1,e['finger']-1];ang=(1-f)*angles[i]+f*angles[i+1];k=keys[e['key_index']];row=measurement(pt,k,ang[e['key_index']]);neighbors=[]
  for kk in keys:
   if kk['midi_note']==e['midi_note']:continue
   mm=measurement(pt,kk,ang[kk['key_index']])
   if mm['inside_correct_playable_region'] and abs(mm['vertical_gap_mm'])<15:neighbors.append(kk['midi_note'])
  contacts.append({'note_id':e['note_id'],'time_sec':e['time_sec'],'hand':side,'finger':e['finger'],'finger_source':e['finger_source'],'finger_confidence':None,'midi_note':e['midi_note'],'note_name':e['note_name'],'pad_world_m':pt.tolist(),**row,'neighbor_key_misassignment_candidates':neighbors,'measurement_time':'exact onset, linearly interpolated native60Hz evaluated samples; not nearest-frame timing drift'})
 for i,assigned in enumerate(sets):
  if len(assigned)<2:continue
  rr=[dict(note_id=n['note_id'],midi_note=n['midi_note'],finger=n['finger'],**measurement(PP[i,n['finger']-1],keys[n['key_index']],angles[i,n['key_index']])) for n in assigned]
  # Translation-invariant pad-to-target relative displacement: chord cannot hide in root translation.
  tar=[target_for(keys[n['key_index']],angles[i,n['key_index']]) for n in assigned];pair=[]
  for j in range(len(assigned)):
   for k in range(j+1,len(assigned)):
    dp=pads[i,assigned[j]['finger']-1]-pads[i,assigned[k]['finger']-1];dt=tar[j]-tar[k];pair.append(float(np.linalg.norm(dp-dt)*1000))
  chords.append({'hand':side,'observation':i,'time_sec':float(times[i]),'active_assigned_notes':rr,'all_contacts_within_policy':all(r['contact_within_fixed_tolerances'] for r in rr),'duplicate_finger_assignment':len({n['finger'] for n in assigned})<len(assigned),'translation_invariant_pair_residual_mm':pair,'single_root_used':True})
 # Actual key-volume vertex inclusion with >3mm below playable top, both mesh and markers.
 collisions=[];regions=ext['body_regions'][side]
 for i in range(N):
  v=V[i];hit=np.zeros(len(v),bool)
  for k in keys:
   pv=np.array(k['press_pivot']);q=rot(v,pv,-angles[i,k['key_index']])
   for g in k['geometry']:
    gv=np.array(g['vertices']);lo=gv.min(0);hi=gv.max(0);hit|=np.all(q>=lo,axis=1)&np.all(q<=hi,axis=1)&(q[:,2]<hi[2]-.003)
  count=int(hit.sum())
  if count:collisions.append({'observation':i,'time_sec':float(times[i]),'key_volume_vertices':count,'wrist_vertices':int(hit[regions['wrist_vertices']].sum()),'palm_vertices':int(hit[regions['palm_vertices']].sum())})
 rr=[r for r in contacts if r['hand']==side];cc=[r for r in chords if r['hand']==side]
 metrics[side]={'note_on_measured':len(rr),'note_on_contacts_within_policy':sum(r['contact_within_fixed_tolerances'] for r in rr),'correct_key_region_count':sum(r['inside_correct_playable_region'] for r in rr),'max_abs_vertical_gap_mm':max(abs(r['vertical_gap_mm']) for r in rr),'median_abs_vertical_gap_mm':float(np.median([abs(r['vertical_gap_mm']) for r in rr])),'max_horizontal_error_mm':max(r['horizontal_in_key_error_mm'] for r in rr),'penetrating_note_ons':sum(r['penetration'] for r in rr),'neighbor_misassignments':sum(bool(r['neighbor_key_misassignment_candidates']) for r in rr),'chord_observations':len(cc),'chord_all_contact_pass':sum(r['all_contacts_within_policy'] for r in cc),'duplicate_finger_chord_observations':sum(r['duplicate_finger_assignment'] for r in cc),'max_step_mm_per_60Hz':float(steps.max()),'mesh_key_collision_observations':len(collisions),'wrist_collision_observations':sum(r['wrist_vertices']>0 for r in collisions),'palm_collision_observations':sum(r['palm_vertices']>0 for r in collisions)}
 safeties[side]={'NaN_Inf':int((~np.isfinite(V)).sum()),'motion_and_root_observations':N,'root_jump_observations':np.flatnonzero(steps>10).tolist(),'key_volume_collisions':collisions,'collision_limit':'Vertex-in-box conservative screen on exact runtime rectangular pieces; absence is not complete triangle collision proof.','rig_internal_deformation':'unchanged approved Action and frozen components; full geometry comparison pending candidate reopen'}
dump('ROOT_ANCHOR_MODEL_R1.json',{'model':'STATIC_KEYBOARD_ALIGNMENT_PLUS_TIME_VARYING_TRANSLATION','policy_sha256':sha('CONTACT_TOLERANCE_POLICY_R1.json'),'hands':models,'objective':'all assigned held note pads equally fitted to fixed playable target points + second-difference temporal penalty; gaps interpolated by same global objective','root_candidate_not_Human_approved':True,'no_6DOF_no_IK_no_joint_change':True})
dump('CONTACT_MEASUREMENTS_R1.json',{'CONTACT_EVIDENCE':'PARTIAL_PREDICTED_ASSIGNMENTS_WITH_FIT_FAILURES','not_independent_contact_validation':True,'summary':metrics,'note_on_measurements':contacts,'chord_observations':chords,'unknown_assignments_excluded_from_contact_metrics':sum(n['hand']=='UNKNOWN' for n in tl['notes']),'all_note_keys_still_animated':True})
dump('MINIMUM_SAFETY_R1.json',{'hands':safeties,'fixed_thresholds_before_results':True,'protected_actions_unchanged':True})
dump('KEY_EVENT_ANIMATION_R1.json',{'KEY_MOTION_SOURCE':'MIDI_EVENT_TIMELINE','timeline_sha256':sha('PERFORMANCE_TIMELINE_R1.json'),'source':'approved key_performance_layer_v1_1d.js update() angle easing .42 and .00005 snap; approved manifest pivot, geometry and full angles','audit_clock_Hz':60,'render_fps':30,'initial_state':'carry-in keys initialized pressed; startup settling pre-window not claimed observed','unknown_hand_notes_animate_correct_keys':True,'collision_triggered':False,'angles_radians_421x88':angles.tolist(),'audio':'interface only; no sound rendered or source video audio used'})
np.savez_compressed(P/'spatial_evaluations.npz',angles=angles,**spatial)
print(json.dumps(metrics,indent=2))
