import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;OLD=P.parent/'piano_hand_static_to_dynamic_transition_r1';LAST=P.parent/'left_little_finger_moving_key_reachability_r1';DIAG=P.parent/'left_octave_neighbor_key_clearance_conflict_isolation_r1';sys.path.insert(0,str(OLD));import common as o
import numpy as np
c=o.c
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False,default=lambda a:a.tolist() if hasattr(a,'tolist') else a),encoding='utf8')
A=np.load(P/'evaluated_coordinated.npz');M=np.load(P/'coordinated_motion.npz');pol=o.read(P/'COORDINATED_CLEARANCE_POLICY_R1.json');times=A['times'];contacts=[]
for n in o.EVENTS['L']:
 rows=[];j=n['finger']-1
 for i,t in enumerate(times):
  if not n['note_on']-1e-8<=t<=o.recovery_end(n)+1e-8:continue
  required=t<n['note_off']-1e-8;ph='NOTE_ON' if abs(t-n['note_on'])<1e-8 else o.phase(n,t)
  fixed=o.measure(A['pads'][i,j],n['midi_note'],A['key_angles'][i,n['key_index']]);skin=o.measure(A['skin_pads'][i,j],n['midi_note'],A['key_angles'][i,n['key_index']]);rows.append({'time':float(t),'phase':ph,'contact_class':'REQUIRED_CONTACT_PHASE' if required else 'NATURAL_RELEASE_PHASE','required':bool(required),'fixed':fixed,'skin':skin,'fixed_xyz_mm':A['pads'][i,j]*1000,'skin_xyz_mm':A['skin_pads'][i,j]*1000})
 required=[r for r in rows if r['required']];assert required
 contacts.append({'note_id':n['note_id'],'midi':n['midi_note'],'pass':all(r['fixed']['pass'] and r['skin']['pass'] for r in required),'max_fixed_gap_mm':max(abs(r['fixed']['gap_mm']) for r in required),'max_skin_gap_mm':max(abs(r['skin']['gap_mm']) for r in required),'required_contact_phases':{ph:all(r['fixed']['pass'] and r['skin']['pass'] for r in required if r['phase']==ph) for ph in ['NOTE_ON','KEY_PRESS','HOLD']},'natural_release_max_absolute_skin_gap_mm':max(abs(r['skin']['gap_mm']) for r in rows if not r['required']),'natural_release_adhesion_required':False,'rows':rows})
dump('DYNAMIC_CONTACT_R1.json',{'status':'PASS' if all(r['pass'] for r in contacts) else 'FAIL','notes':contacts,'required_interval':'[NOTE_ON, NOTE_OFF)','release_interval':'[NOTE_OFF, recovery_end]','note_off_and_key_rebound_not_extended':True,'vertical_tolerance_mm':3,'horizontal_tolerance_mm':2,'strict_playable_region':True,'saved_reopened_evaluated_geometry':True})
extract=o.read(o.FORMAL/'FORMAL_INPUT_EXTRACTION_R1.json')['L'];rest=np.array(extract['rest_vertices_canonical']);palm=np.flatnonzero(rest[:,1]<.105);weights=np.array(extract['weights']);bones=extract['bone_names'];deep_hits=[];wrong=[];target_rows={'40':[],'42':[]};mingap=None;all_positive={};new_deep={}
for i,t in enumerate(times):
 V=A['verts'][i]
 for k in c.KEYS:
  midi=k['midi_note'];angle=A['key_angles'][i,k['key_index']];V0=o.keytransform(midi,V,angle,True) if angle else V
  for g in k['geometry']:
   pts=np.array(g['vertices']);lo=pts.min(0);hi=pts.max(0);exitdist=np.minimum(V0-lo,hi-V0).min(1);ids=np.flatnonzero(exitdist>1e-8);deep=ids[V0[ids,2]<hi[2]-.003]
   if len(ids):
    s=all_positive.setdefault(str(midi),{'unique_vertices':set(),'times':[],'max_vertical_depth_mm':0.,'max_minimum_exit_mm':0.});s['unique_vertices'].update(map(int,ids));s['times'].append(float(t));s['max_vertical_depth_mm']=max(s['max_vertical_depth_mm'],float(np.max(hi[2]-V0[ids,2])*1000));s['max_minimum_exit_mm']=max(s['max_minimum_exit_mm'],float(np.max(exitdist[ids])*1000))
   if len(deep):
    row={'time':float(t),'midi':midi,'piece':g['name'],'vertices':list(map(int,deep)),'palm_vertices':int(np.isin(deep,palm).sum()),'max_depth_mm':float(np.max(hi[2]-V0[deep,2])*1000)};deep_hits.append(row)
    if midi not in [40,42]:new_deep.setdefault(str(midi),[]).append(row)
   if midi in [40,42]:
    target_rows[str(midi)].extend({'time':float(t),'vertex':int(vid),'piece':g['name'],'xyz_mm':V[vid]*1000,'vertical_below_top_mm':float((hi[2]-V0[vid,2])*1000),'minimum_exit_distance_mm':float(exitdist[vid]*1000),'dominant_bone':bones[int(np.argmax(weights[vid]))]} for vid in ids)
  for j in range(5):
   if midi==[50,None,None,None,38][j]:continue
   mm=o.measure(A['pads'][i,j],midi,angle)
   if mm['pass']:wrong.append({'time':float(t),'finger':j+1,'midi':midi,'gap_mm':mm['gap_mm']})
  pts=V0[palm]
  for top in k['key_top_playable_surface']:
   mask=(pts[:,0]>=top['xmin'])&(pts[:,0]<=top['xmax'])&(pts[:,1]>=top['ymin'])&(pts[:,1]<=top['ymax'])
   if mask.any():value=float(np.min(pts[mask,2]-top['z'])*1000);mingap=value if mingap is None else min(mingap,value)
def intervals(rows):
 ticks=sorted(set(round(r['time']*240) for r in rows if abs(r['time']*240-round(r['time']*240))<1e-7));out=[]
 for tick in ticks:
  if out and tick==out[-1][1]+1:out[-1][1]=tick
  else:out.append([tick,tick])
 return [{'observed_start_s':a/240,'observed_end_s':b/240,'estimated_duration_s':(b-a+1)/240,'sampling_interval_s':1/240} for a,b in out]
keys={}
for midi,rows in target_rows.items():
 ids=sorted(set(r['vertex'] for r in rows));dep=max([r['vertical_below_top_mm'] for r in rows],default=0);keys[midi]={'key':'E2' if midi=='40' else 'F#2','status':'NO_SAMPLED_VERTEX_PENETRATION' if not rows else 'RESIDUAL_GEOMETRY_CONFLICT','unique_vertex_count':len(ids),'vertex_ids':ids,'max_vertical_depth_mm':dep,'max_minimum_exit_distance_mm':max([r['minimum_exit_distance_mm'] for r in rows],default=0),'observed_intervals':intervals(rows),'deep_over_3mm_record_count':sum(r['vertical_below_top_mm']>3 for r in rows),'dominant_bones':sorted(set(r['dominant_bone'] for r in rows)),'rows':rows,'human_visible_severity':'PENDING_NORMAL_VIEW_PRECHECK'}
for s in all_positive.values():s['unique_vertices']=sorted(s['unique_vertices']);s['times']=sorted(set(s['times']))
dump('NEIGHBOR_KEY_CLEARANCE_R1.json',{'status':'PASS_FINITE_SCREEN' if not deep_hits and not wrong else 'FAIL_FINITE_SCREEN','samples':len(times),'sampling_hz':240,'vertex_count':len(rest),'key_count':88,'deep_screen_mm':3,'target_keys':keys,'all_deep_hits':deep_hits,'all_positive_penetration_summary':all_positive,'other_key_deep_hits':new_deep,'wrong_pad_contacts':wrong,'minimum_palm_projected_gap_mm':mingap,'E2_FSHARP2_zero_positive_vertex_penetrations':not any(target_rows.values()),'limitations':'Finite vertices against verified frozen rectangular key pieces; not exhaustive triangle intersection certification. Vertical depth and minimum exit distance differ. Small invisible residuals are not automatically major product defects.'})
grid=np.arange(48,217)/120;ids=[int(np.argmin(abs(M['times']-t))) for t in grid];assert max(abs(M['times'][ids]-grid))<1e-8;Q=np.degrees(M['q'][ids]);vel=np.diff(Q,axis=0)*120;acc=np.diff(vel,axis=0)*120
bounds=np.array([pol['joints']['hard_bounds_deg']['THUMB' if j==0 else 'LONG' if j==4 else 'LEFT_IDLE_'+d] for j,d in enumerate(c.DIGITS)])
N=np.array(c.RIG['L']['native_to_canonical']);R=M['root_matrices'][ids]@np.linalg.inv(N);xyz=R[:,:3,3]*1000;v=np.diff(xyz,axis=0)*120;ac=np.diff(v,axis=0)*120;pitch=np.array([np.arctan2((r[:3,:3]@R[0,:3,:3].T)[2,1],(r[:3,:3]@R[0,:3,:3].T)[1,1]) for r in R])*180/np.pi;av=np.diff(pitch)*120;aa=np.diff(av)*120;dwell=[]
for n in o.EVENTS['L']:
 j=n['finger']-1;ii=np.flatnonzero((grid>=n['note_on']-1e-8)&(grid<n['note_off']-1e-8));near=(Q[ii,j]-bounds[j,0]<.25)|(bounds[j,1]-Q[ii,j]<.25);run=0;longest=0
 for b in np.any(near,axis=1):run=run+1 if b else 0;longest=max(run,longest)
 dwell.append({'note_id':n['note_id'],'longest_required_near_bound_sec':longest/120,'joints_near_bound_any':np.any(near,axis=0),'measurement_not_physiology_or_sole_rejection':True})
limits=pol['continuity'];checks={'joint_bounds':bool(np.all(Q>=bounds[:,0]-1e-7)&np.all(Q<=bounds[:,1]+1e-7)),'joint_velocity':float(np.max(abs(vel)))<=limits['joint_velocity_deg_sec'],'joint_acceleration':float(np.max(abs(acc)))<=limits['joint_acceleration_deg_sec2'],'root_velocity':float(np.max(np.linalg.norm(v,axis=1)))<=limits['root_velocity_mm_sec'],'root_acceleration':float(np.max(np.linalg.norm(ac,axis=1)))<=limits['root_acceleration_mm_sec2'],'root_angular_velocity':float(np.max(abs(av)))<=limits['root_angular_velocity_deg_sec'],'root_angular_acceleration':float(np.max(abs(aa)))<=limits['root_angular_acceleration_deg_sec2'],'absolute_root_domain':bool(np.all(xyz>=np.array(pol['root']['absolute_xyz_bounds_mm'][0])-.001)&np.all(xyz<=np.array(pol['root']['absolute_xyz_bounds_mm'][1])+.001))}
dump('MOTION_CONTINUITY_R1.json',{'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'joint_velocity_max_deg_sec':float(np.max(abs(vel))),'joint_acceleration_max_deg_sec2':float(np.max(abs(acc))),'root_velocity_max_mm_sec':float(np.max(np.linalg.norm(v,axis=1))),'root_acceleration_max_mm_sec2':float(np.max(np.linalg.norm(ac,axis=1))),'root_angular_velocity_max_deg_sec':float(np.max(abs(av))),'root_angular_acceleration_max_deg_sec2':float(np.max(abs(aa))),'root_xyz_min_mm':xyz.min(0),'root_xyz_max_mm':xyz.max(0),'root_pitch_delta_range_deg':[float(pitch.min()),float(pitch.max())],'idle_joint_delta_max_deg':float(np.max(abs(Q[:,1:4]-np.degrees(o.qanchor('L1')[1:4])))),'idle_per_digit_delta_max_deg':np.max(abs(Q[:,1:4]-np.degrees(o.qanchor('L1')[1:4])),axis=0),'active_near_bound_dwell':dwell,'root_shared_count':1,'curve':'Original C2 phase response with jointly optimized global coefficients; saved quaternion channels piecewise linear, no post smoothing.','numerical_continuity_is_not_naturalness':True})
print(json.dumps({'contacts':[{k:v for k,v in r.items() if k!='rows'} for r in contacts],'target_clearance':{k:{a:b for a,b in v.items() if a!='rows'} for k,v in keys.items()},'all_deep_records':len(deep_hits),'other_deep_keys':list(new_deep),'continuity':checks},indent=2),flush=True)
