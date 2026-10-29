from phrase_common import *
import math
A=np.load(P/'motion.npz');E=np.load(P/'evaluated.npz');man=read(P/'SCENE_MANIFEST.json');times=E['times'];rows=[];summary={};continuity={};clearance={}
for s in ['L','R']:
 V=E[s+'_verts'];pads=E[s+'_pads'];skin=E[s+'_skin_pads'];q=np.degrees(A[s+'_q']);reg=[]
 for n in EVENTS[s]:
  inds=np.flatnonzero((times>=n['note_on']-1e-8)&(times<n['note_off']-1e-8));j=n['finger']-1;measure=[]
  for i in inds:
   fixed=o.measure(pads[i,j],n['midi_note'],E['key_angles'][i,n['key_index']]);actual=o.measure(skin[i,j],n['midi_note'],E['key_angles'][i,n['key_index']]);r={'note_id':n['note_id'],'hand':s,'midi':n['midi_note'],'finger':n['finger'],'time_source_sec':float(times[i]),'video_time_sec':float(times[i]-START),'fixed_gap_mm':fixed['gap_mm'],'skin_gap_mm':actual['gap_mm'],'horizontal_mm':actual['horizontal_mm'],'inside_playable':bool(actual['inside'])};rows.append(r);measure.append(r)
  reg.append({'note_id':n['note_id'],'midi':n['midi_note'],'finger':n['finger'],'samples':len(measure),'skin_gap_min_mm':min(r['skin_gap_mm'] for r in measure),'skin_gap_max_mm':max(r['skin_gap_mm'] for r in measure),'skin_gap_max_abs_mm':max(abs(r['skin_gap_mm']) for r in measure),'horizontal_max_mm':max(r['horizontal_mm'] for r in measure),'outside_samples':sum(not r['inside_playable'] for r in measure),'historical_gap_over3mm_samples':sum(abs(r['skin_gap_mm'])>3 for r in measure)})
 summary[s]=reg
 regular=np.arange(round(START*120),round(END*120)+1)/120;ii=np.array([int(np.argmin(abs(times-t))) for t in regular]);assert np.max(abs(times[ii]-regular))<1e-8;vel=np.diff(q[ii],axis=0)*120;acc=np.diff(vel,axis=0)*120
 b=np.array([o.SP['joint_increment_bounds_deg']['THUMB' if j==0 else 'LONG'] for j in range(5)]);outside=np.maximum(np.maximum(b[:,0]-q,q-b[:,1]),0)
 near=[]
 for j,d in enumerate(c.DIGITS):
  for k in range(4):
   flags=np.minimum(q[:,j,k]-b[j,0,k],b[j,1,k]-q[:,j,k])<=.25;run=best=0
   for i,v in enumerate(flags[:-1]):run=run+float(times[i+1]-times[i]) if v else 0;best=max(best,run)
   if best>0:near.append({'digit':d,'axis':k,'longest_near_limit_dwell_sec':best})
 semantic=[];rt=E[s+'_root_matrices'];wrist=np.r_[o.ANCHORS['L1' if s=='L' else 'R1']['root_xyz_m'],1];local=np.linalg.inv(rt[0])@wrist
 for M in rt:semantic.append((M@local)[:3])
 semantic=np.array(semantic);rootv=np.diff(semantic[ii],axis=0)*120*1000
 continuity[s]={'joint_velocity_max_deg_sec':float(np.max(abs(vel))),'joint_acceleration_max_deg_sec2':float(np.max(abs(acc))),'joint_bound_violation_max_deg':float(outside.max()),'near_limit_dwell':near,'largest_120Hz_joint_step_deg':float(np.max(abs(np.diff(q,axis=0)))),'semantic_wrist_displacement_max_mm':float(np.max(np.linalg.norm(semantic-semantic[0],axis=1))*1000),'semantic_wrist_velocity_max_mm_sec':float(np.max(np.linalg.norm(rootv,axis=1))),'root_pitch_range_deg':[float(A['L_pitch_deg'].min()),float(A['L_pitch_deg'].max())] if s=='L' else [0,0],'root_rotation_domain':'Inherited world-X pitch left, fixed right','numeric_limits':'Engineering policy, not physiological certification'}
 # All 88 frozen key boxes, actual saved/reopened skin vertices. Diagnostic, no automatic visual rejection.
 rest=np.array(read(o.FORMAL/'FORMAL_INPUT_EXTRACTION_R1.json')[s]['rest_vertices_canonical']);perkey=[];worst=None
 for k in c.KEYS:
  depths=np.zeros(len(times));counts=np.zeros(len(times),int)
  for i,t in enumerate(times):
   vv=o.keytransform(k['midi_note'],V[i],E['key_angles'][i,k['key_index']],True) if E['key_angles'][i,k['key_index']] else V[i];pen=np.zeros(len(vv))
   for g in k['geometry']:
    verts=np.array(g['vertices']);low=verts.min(0);high=verts.max(0);d=np.abs(vv-(low+high)/2)-(high-low)/2;sdf=np.linalg.norm(np.maximum(d,0),axis=1)+np.minimum(np.max(d,axis=1),0);pen=np.maximum(pen,-sdf)
   depths[i]=pen.max()*1000;counts[i]=int(np.sum(pen>.003))
  if depths.max()>1e-5:
   i=int(np.argmax(depths));record={'midi':k['midi_note'],'note_name':k['note_name'],'depth_max_mm':float(depths[i]),'time_source_sec':float(times[i]),'samples_with_penetration':int(np.sum(depths>1e-5)),'samples_over3mm':int(np.sum(depths>3)),'vertices_over3mm_max':int(counts.max()),'may_be_own_key':any(n['midi_note']==k['midi_note'] for n in EVENTS[s])};perkey.append(record)
   if worst is None or record['depth_max_mm']>worst['depth_max_mm']:worst=record
 clearance[s]={'screen':'All actual evaluated 3300 vertices against all88 frozen piece boxes; vertex-only screen does not prove triangle nonintersection','worst':worst,'penetrated_keys':perkey}
 print('MEASURED',s,'contact notes',len(reg),'worst',worst,flush=True)
status='FAIL' if any(v['joint_bound_violation_max_deg']>1e-3 for v in continuity.values()) else 'WARN' if any(r['historical_gap_over3mm_samples'] or r['outside_samples'] for v in summary.values() for r in v) or any(v['worst'] and v['worst']['depth_max_mm']>3 for v in clearance.values()) else 'PASS'
dump('ENGINEERING_DIAGNOSTICS.json',{'status':status,'visual_product_status':'HUMAN_PENDING','music_status':'PENDING_AGENT_VIDEO_CHECK','old_3mm_threshold_is_not_visual_veto':True,'candidate_sha256':man['sha256'],'actual_saved_reopened':True,'contact':summary,'clearance':clearance,'continuity':continuity,'playback_parity':{k:man[k] for k in ['actual_pad_vs_FK_max_mm','actual_joint_rotation_parity_max','actual_key_world_parity_max_mm','key_angle_parity_max_rad']},'samples':len(times),'sampling_hz':120,'maximum_pressure_phase_joints_deg':{s:np.degrees(A[s+'_q']).max(axis=0) for s in ['L','R']},'minimum_joints_deg':{s:np.degrees(A[s+'_q']).min(axis=0) for s in ['L','R']},'limitations':['Frozen rectangular-key vertex screen, not complete surface-surface collision','Virtual skin pad is not a pressure center','Naturalness is awaiting Human review','Two repeated bars in one five-finger position; no register shifts or new fingering demonstrated']})
dump('CONTACT_SAMPLES.json',rows)
print('ENGINEERING',status,flush=True)

