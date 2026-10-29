from common import *
A=np.load(P/'evaluated_temporal_candidate.npz');M=np.load(P/'temporal_motion.npz');man=read(P/'DYNAMIC_SCENE_MANIFEST_R1.json');policy=read(P/'TEMPORAL_MOTION_POLICY_R1.json')
assert sha(P/'STATIC_TO_DYNAMIC_TRANSITION_CANDIDATE_R1.blend')==man['candidate_sha256']
contacts={};clearance={};continuity={}
for s in ['L','R']:
 times=A[s+'_times'];VV=A[s+'_verts'];PP=A[s+'_pads'];SS=A[s+'_skin_pads'];KA=A[s+'_key_angles'];model=models(s);rest=model['V'];palm=np.flatnonzero((rest[:,1]>=.045)&(rest[:,1]<.105));wrist=np.flatnonzero(rest[:,1]<.045);fingers=[np.flatnonzero(model['W'][:,[i for i,n in enumerate(model['names']) if n.startswith(d+'_')]].sum(1)>.65) for d in c.DIGITS];rows=[]
 for n in EVENTS[s]:
  samples=[]
  for i,t in enumerate(times):
   if n['note_on']-1e-8<=t<=n['note_off']+.07+1e-8:
    j=n['finger']-1;fixed=measure(PP[i,j],n['midi_note'],KA[i,n['key_index']]);sk=measure(SS[i,j],n['midi_note'],KA[i,n['key_index']]);target0=worldpads(s,qanchor('L1' if s=='L' and j==4 else 'L2' if s=='L' else 'R2'))[j];target=keytransform(n['midi_note'],target0,KA[i,n['key_index']]);samples.append({'time':float(t),'phase':phase(n,float(t)),'depression_fraction':float(KA[i,n['key_index']]/c.KEYS[n['key_index']]['press_angle_rad']),'fixed_pad':fixed,'skin_pad':sk,'registered_target_error_mm':float(np.linalg.norm(PP[i,j]-target)*1000),'fixed_xyz_mm':PP[i,j]*1000,'skin_xyz_mm':SS[i,j]*1000})
  summary={'note_id':n['note_id'],'midi':n['midi_note'],'finger':n['finger'],'note_on':n['note_on'],'note_off':n['note_off'],'contact_all_samples_pass':all(v['fixed_pad']['pass'] and v['skin_pad']['pass'] for v in samples),'max_absolute_pad_gap_mm':max(abs(v['fixed_pad']['gap_mm']) for v in samples),'max_absolute_skin_gap_mm':max(abs(v['skin_pad']['gap_mm']) for v in samples),'max_horizontal_error_mm':max(v['fixed_pad']['horizontal_mm'] for v in samples),'max_registered_target_error_mm':max(v['registered_target_error_mm'] for v in samples),'phases':{p:{'samples':len([v for v in samples if v['phase']==p]),'pass':all(v['fixed_pad']['pass'] and v['skin_pad']['pass'] for v in samples if v['phase']==p)} for p in ['CONTACT','KEY_PRESS','HOLD','RELEASE']},'release_lift':[],'samples':samples}
  for i,t in enumerate(times):
   if n['note_off']+.07+1e-8<t<=recovery_end(n)+1e-8:summary['release_lift'].append({'time':float(t),'phase':phase(n,float(t)),'key_gap_mm':measure(PP[i,n['finger']-1],n['midi_note'],KA[i,n['key_index']])['gap_mm']})
  rows.append(summary)
 contacts[s]={'status':'PASS_CONTACT_SCREEN' if all(v['contact_all_samples_pass'] for v in rows) else 'FAIL_CONTACT_SCREEN','note_rows':rows,'uses_current_rotated_key_geometry':True,'unpressed_plane_not_used_for_pressed_checks':True,'timebase_hz':120,'finite_pressure_model':False}
 hitrows=[];wrongpads=[];maxdepth=0;neighbor_specific={75:0,80:0};all_hitframes=0;palmframes=0;wristframes=0;digit_hits=np.zeros(5,int);min_palm=None
 for i,t in enumerate(times):
  V=VV[i];hit=np.zeros(len(V),bool)
  for k in c.KEYS:
   angle=KA[i,k['key_index']];V0=keytransform(k['midi_note'],V,angle,True) if angle else V;mask=np.zeros(len(V),bool);depth=0
   for g in k['geometry']:
    points=np.array(g['vertices']);lo=points.min(0);hi=points.max(0);inside=np.all(V0>=lo-1e-8,axis=1)&np.all(V0<=hi+1e-8,axis=1);deep=inside&(V0[:,2]<hi[2]-.003);mask|=deep
    if deep.any():depth=max(depth,float(np.max(hi[2]-V0[deep,2])*1000))
   if mask.any():
    hitrows.append({'time':float(t),'midi':k['midi_note'],'note':k['note_name'],'vertices':int(mask.sum()),'max_depth_mm':depth,'palm_vertices':int(mask[palm].sum()),'wrist_vertices':int(mask[wrist].sum()),'digit_vertices':[int(mask[ids].sum()) for ids in fingers]});maxdepth=max(maxdepth,depth)
    if k['midi_note'] in neighbor_specific:neighbor_specific[k['midi_note']]+=int(mask.sum())
   hit|=mask
   for j in range(5):
    expected=([50,None,None,None,38] if s=='L' else [74,76,78,79,81])[j]
    if k['midi_note']==expected:continue
    m=measure(PP[i,j],k['midi_note'],angle)
    if m['pass']:wrongpads.append({'time':float(t),'finger':j+1,'unexpected_midi':k['midi_note'],'gap_mm':m['gap_mm']})
   if len(palm):
    pts=V0[palm]
    for top in k['key_top_playable_surface']:
     over=(pts[:,0]>=top['xmin'])&(pts[:,0]<=top['xmax'])&(pts[:,1]>=top['ymin'])&(pts[:,1]<=top['ymax'])
     if over.any():v=float(np.min(pts[over,2]-top['z'])*1000);min_palm=v if min_palm is None else min(min_palm,v)
  all_hitframes+=int(hit.any());palmframes+=int(hit[palm].any());wristframes+=int(hit[wrist].any());digit_hits+=[int(hit[ids].sum()) for ids in fingers]
 clearance[s]={'status':'PASS_FINITE_SCREEN' if not hitrows and not wrongpads else 'FAIL_FINITE_SCREEN','evaluated_frames':len(times),'complete_vertex_count':VV.shape[1],'all_88_keys_checked':True,'inverse_current_key_transform':True,'key_geometry_unchanged':True,'deep_hit_frames':all_hitframes,'palm_hit_frames':palmframes,'wrist_hit_frames':wristframes,'per_digit_deep_vertex_samples':digit_hits,'max_depth_mm':maxdepth,'palm_min_projected_surface_gap_mm':min_palm,'right_Dsharp5_vertex_samples':neighbor_specific[75] if s=='R' else None,'right_Gsharp5_vertex_samples':neighbor_specific[80] if s=='R' else None,'hits':hitrows,'unexpected_pad_contacts':wrongpads,'limitation':'Finite vertex/key-volume screen, not exhaustive triangle collision. Human-visible path review required.'}
 grid=np.arange(round(WINDOWS[s][0]*120),round(WINDOWS[s][1]*120)+1)/120;ctrl={p:np.array(x) for p,x in read(P/'CONTACT_AWARE_MOTION_PLAN_R1.json')['controls_radians'].items()};Q=np.array([sample(s,t,ctrl)[0] for t in grid]);degrees=np.degrees(Q);vel=np.diff(degrees,axis=0)*120;acc=np.diff(vel,axis=0)*120;lo=[];hi=[]
 for j,d in enumerate(c.DIGITS):
  typ='THUMB' if j==0 else 'LEFT_IDLE_'+d if s=='L' and j in [1,2,3] else 'LONG';b=np.array(SP['joint_increment_bounds_deg'][typ]);lo.append(b[0]);hi.append(b[1])
 lo=np.array(lo);hi=np.array(hi);boundok=bool(np.all(degrees>=lo-1e-7) and np.all(degrees<=hi+1e-7));dwell=[]
 for n in EVENTS[s]:
  j=n['finger']-1;ids=np.flatnonzero((grid>=n['note_on']-1e-8)&(grid<n['note_off']+.07-1e-8));near=(degrees[ids,j]-lo[j]<.25)|(hi[j]-degrees[ids,j]<.25)
  run=0;longest=0
  for b in np.any(near,axis=1):run=run+1 if b else 0;longest=max(run,longest)
  dwell.append({'note_id':n['note_id'],'active_near_bound_longest_sec':longest/120,'all_control_points_are_bounded':True,'pass':longest/120<=.05})
 qref=qanchor('L1' if s=='L' else 'R1');idle=[1,2,3] if s=='L' else [0,1,3,4]
 continuity[s]={'generated_complete_sequence':True,'joint_velocity_max_deg_sec':float(np.max(np.abs(vel))),'joint_acceleration_max_deg_sec2':float(np.max(np.abs(acc))),'max_single_120Hz_joint_step_deg':float(np.max(np.abs(np.diff(degrees,axis=0)))),'joint_bounds_pass':boundok,'velocity_limit_pass':bool(np.max(np.abs(vel))<=850),'acceleration_limit_pass':bool(np.max(np.abs(acc))<=90000),'root_translation_delta_mm':0,'root_rotation_delta_deg':0,'root_velocity_mm_sec':0,'root_acceleration_mm_sec2':0,'idle_joint_max_delta_from_human_anchor_deg':float(np.max(np.abs(degrees[:,idle]-np.degrees(qref[idle])))),'active_near_bound_dwell':dwell,'near_bound_dwell_pass':all(x['pass'] for x in dwell),'no_ik_branch_switch_by_construction':True,'polynomial_phase_boundary_velocity_acceleration':'C2 analytic underlying curves; saved120Hz quaternion channels LINEAR approximate them. Finite-difference120Hz continuity reported.','human_visible_naturalness':'PENDING_NORMAL_VIDEO_PRECHECK','new_near_bound_inactive_state':'Right thumb IP at0 is inherited unchanged, not a new active saturation.'}
 continuity[s]['machine_temporal_pass']=bool(boundok and continuity[s]['velocity_limit_pass'] and continuity[s]['acceleration_limit_pass'] and continuity[s]['near_bound_dwell_pass'])
 print('MEASURED',s,json.dumps({k:continuity[s][k] for k in ['joint_velocity_max_deg_sec','joint_acceleration_max_deg_sec2','joint_bounds_pass','near_bound_dwell_pass','machine_temporal_pass']}),'contact',contacts[s]['status'],'clearance',clearance[s]['status'],flush=True)
dump('DYNAMIC_CONTACT_R1.json',contacts);dump('NEIGHBOR_CLEARANCE_R1.json',clearance);dump('MOTION_CONTINUITY_R1.json',continuity)
