from articulation_common import *
A=np.load(P/'motion.npz');E=np.load(P/'evaluated.npz');old=read(PRE/'ENGINEERING_DIAGNOSTICS.json');fit=read(P/'RIGHT_HAND_FIT.json');man=read(P/'SCENE_MANIFEST.json');times=E['times'];regular=np.arange(round(START*120),round(END*120)+1)/120;ids=np.array([int(np.argmin(abs(times-t))) for t in regular]);assert np.max(abs(times[ids]-regular))<1e-8
contact=[];specific=[];stages=[]
rest=np.array(read(o.FORMAL/'FORMAL_INPUT_EXTRACTION_R1.json')['R']['rest_vertices_canonical']);patches={j:np.flatnonzero(np.linalg.norm(rest-rest[c.MARKERS['R'][j]['mesh_vertex']],axis=1)<=.008) for j in range(5)}
for n in TL['notes']:
 if n['hand']!='R':continue
 j=n['finger']-1;k=n['key_index'];r=[];on=n['note_on'];off=n['note_off'];inds=np.flatnonzero((times>=on-1e-8)&(times<off-1e-8))
 for i in inds:
  row=o.measure(E['R_skin_pads'][i,j],n['midi_note'],E['key_angles'][i,k]);r.append(row)
 contact.append({'note_id':n['note_id'],'midi':n['midi_note'],'finger':n['finger'],'skin_gap_min_mm':min(a['gap_mm'] for a in r),'skin_gap_max_mm':max(a['gap_mm'] for a in r),'skin_gap_max_abs_mm':max(abs(a['gap_mm']) for a in r),'horizontal_max_mm':max(a['horizontal_mm'] for a in r),'outside_samples':sum(not a['inside'] for a in r),'samples':len(r),'previous_gap_max_mm':next(v for v in old['contact']['R'] if v['note_id']==n['note_id'])['skin_gap_max_mm']})
 for phase,t in [('LIFT_END',on-.04),('NOTE_ON',on),('PRESS_MIDDLE',on+.0175),('FULL_DOWN',on+.035),('HOLD_MIDDLE',(on+.035+off)/2),('NOTE_OFF',off),('KEY_RETURN_END',off+.07),('RECOVERY_END',off+.12)]:
  i=int(np.argmin(abs(times-t)));rr=o.measure(E['R_skin_pads'][i,j],n['midi_note'],E['key_angles'][i,k]);stages.append({'note_id':n['note_id'],'midi':n['midi_note'],'phase':phase,'requested_source_time':t,'actual_source_time':float(times[i]),'video_time':float(times[i]-START),'pad_gap_mm':rr['gap_mm'],'horizontal_mm':rr['horizontal_mm'],'key_angle_rad':float(E['key_angles'][i,k]),'pad_xyz_mm':E['R_skin_pads'][i,j]*1000})
  if n['midi_note'] in [81,78] and phase in ['NOTE_ON','FULL_DOWN','HOLD_MIDDLE']:
   V=o.keytransform(n['midi_note'],E['R_verts'][i,patches[j]],E['key_angles'][i,k],True);valid=[]
   for surf in c.KEYS[k]['key_top_playable_surface']:
    mask=(V[:,0]>=surf['xmin'])&(V[:,0]<=surf['xmax'])&(V[:,1]>=surf['ymin'])&(V[:,1]<=surf['ymax']);valid.extend((V[mask,2]-surf['z'])*1000)
   specific.append({'note_id':n['note_id'],'midi':n['midi_note'],'phase':phase,'source_time':float(times[i]),'skin_pad_gap_mm':rr['gap_mm'],'patch_radius_mm':8,'patch_vertices_over_actual_face':len(valid),'closest_patch_surface_gap_mm':float(min(valid,key=abs)) if valid else None,'actual_playable_face':c.KEYS[k]['key_top_playable_surface']})
q=np.degrees(A['R_q']);b=np.array([o.SP['joint_increment_bounds_deg']['THUMB' if j==0 else 'LONG'] for j in range(5)]);violation=np.maximum(np.maximum(b[:,0]-q,q-b[:,1]),0);v=np.diff(q[ids],axis=0)*120;acc=np.diff(v,axis=0)*120
near=[]
for j,d in enumerate(c.DIGITS):
 for k in range(4):
  mask=np.minimum(q[ids,j,k]-b[j,0,k],b[j,1,k]-q[ids,j,k])<=.25;run=best=0.
  for flag in mask[:-1]:run=run+1/120 if flag else 0.;best=max(best,run)
  if best>0:near.append({'digit':d,'axis':k,'longest_near_limit_dwell_sec':best})
rootxyz=A['R_delta'][ids]*1000;rootv=np.diff(rootxyz,axis=0)*120;roota=np.diff(rootv,axis=0)*120
continuity={'joint_bound_violation_max_deg':float(violation.max()),'joint_velocity_max_deg_sec':float(np.max(abs(v))),'joint_acceleration_max_deg_sec2':float(np.max(abs(acc))),'near_limit_dwell':near,'root_translation_displacement_max_mm':float(np.max(np.linalg.norm(rootxyz,axis=1))),'root_velocity_max_mm_sec':float(np.max(np.linalg.norm(rootv,axis=1))),'root_acceleration_max_mm_sec2':float(np.max(np.linalg.norm(roota,axis=1))),'root_pitch_range_deg':[float(A['R_pitch_deg'].min()),float(A['R_pitch_deg'].max())],'regular_sampling_hz':120,'physiological_certification':False}
# Aggregate neighbor screen only, no per-vertex forensic tracing or hidden camera evidence.
clear=[];Vall=E['R_verts'];screenids=ids[::2];screenids=np.unique(np.r_[screenids,[int(np.argmin(abs(times-n['note_on']-.035))) for n in TL['notes'] if n['hand']=='R']])
for key in c.KEYS:
 worst=0.;timeworst=0.
 for i in screenids:
  VV=o.keytransform(key['midi_note'],Vall[i],E['key_angles'][i,key['key_index']],True) if E['key_angles'][i,key['key_index']] else Vall[i];pen=np.zeros(len(VV))
  for g in key['geometry']:
   vvv=np.array(g['vertices']);lower=vvv.min(0);upper=vvv.max(0);d=np.abs(VV-(lower+upper)/2)-(upper-lower)/2;sdf=np.linalg.norm(np.maximum(d,0),axis=1)+np.minimum(np.max(d,axis=1),0);pen=np.maximum(pen,-sdf)
  depth=float(pen.max()*1000)
  if depth>worst:worst=depth;timeworst=float(times[i])
 if worst>1e-5:clear.append({'midi':key['midi_note'],'note_name':key['note_name'],'maximum_depth_mm':worst,'source_time':timeworst,'is_performed_key':any(n['midi_note']==key['midi_note'] for n in TL['notes'] if n['hand']=='R')})
engineering='FAIL' if violation.max()>1e-3 or continuity['joint_velocity_max_deg_sec']>850*1.05 or continuity['joint_acceleration_max_deg_sec2']>90000*1.05 else 'WARN' if any(x['skin_gap_max_abs_mm']>3 or x['outside_samples'] for x in contact) or any(x['maximum_depth_mm']>3 for x in clear) or near else 'PASS'
dump('ENGINEERING_DIAGNOSTICS.json',{'status':engineering,'candidate_sha256':man['sha256'],'contact_right_all10_notes':contact,'A5_Fsharp5_actual_moving_surface_check':specific,'event_phase_contact':stages,'right_continuity':continuity,'right_aggregate_key_penetration':clear,'neighbor_screen_samples':len(screenids),'neighbor_screen_hz':60,'diagnostic_is_not_human_product_verdict':True,'left_actual_geometry_difference_mm':man['left_actual_geometry_max_difference_mm'],'left_actions_arrays_geometry_unchanged':True,'left_prior_diagnostic_retained':old['contact']['L'],'left_current_approval':'NOT_APPROVED; unchanged control','key_midi_audio_chain':'Exact source events, unchanged original key actions and PCM','original_event_count':18,'complete_mesh_for_existing_aggregate_screen':True,'no_per_vertex_forensic_report':True,'human_review':'HUMAN_PENDING'})
dump('A5_FSHARP5_CONTACT_PHASE_DATA.json',{'samples':specific,'all_right_contacts':contact,'classification_basis':'Actual saved/reopened skin patch over true moved key face, matched source times and original review cameras; geometric evidence does not prove finite-pressure contact'})
print('ENGINEERING_MEASURED',engineering,continuity,flush=True)
for r in contact:print('RIGHT_CONTACT',r,flush=True)
print('AGGREGATE_CLEARANCE',clear,flush=True)
