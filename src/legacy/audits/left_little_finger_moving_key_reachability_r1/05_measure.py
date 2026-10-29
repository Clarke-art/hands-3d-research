import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;PRE=P.parent/'piano_hand_static_to_dynamic_transition_r1';sys.path.insert(0,str(PRE));import common as o
import numpy as np
c=o.c
def dump(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else v),encoding='utf8')
A=np.load(P/'evaluated_probe.npz');M=np.load(P/'probe_motion.npz');pol=o.read(P/'ROOT_FOLLOW_THROUGH_POLICY_R1.json');times=A['times'];contacts=[]
for n in o.EVENTS['L']:
 rows=[];j=n['finger']-1
 for i,t in enumerate(times):
  if not n['note_on']-1e-8<=t<=n['note_off']+.07+1e-8:continue
  fixed=o.measure(A['pads'][i,j],n['midi_note'],A['key_angles'][i,n['key_index']]);skin=o.measure(A['skin_pads'][i,j],n['midi_note'],A['key_angles'][i,n['key_index']]);rows.append({'time':float(t),'phase':'NOTE_ON' if abs(t-n['note_on'])<1e-8 else o.phase(n,t),'fixed':fixed,'skin':skin,'fixed_xyz_mm':A['pads'][i,j]*1000,'skin_xyz_mm':A['skin_pads'][i,j]*1000})
 contacts.append({'note_id':n['note_id'],'midi':n['midi_note'],'pass':all(r['fixed']['pass'] and r['skin']['pass'] for r in rows),'max_fixed_gap_mm':max(abs(r['fixed']['gap_mm']) for r in rows),'max_skin_gap_mm':max(abs(r['skin']['gap_mm']) for r in rows),'phases':{ph:all(r['fixed']['pass'] and r['skin']['pass'] for r in rows if r['phase']==ph) for ph in ['NOTE_ON','KEY_PRESS','HOLD','RELEASE']},'rows':rows})
extract=o.read(o.FORMAL/'FORMAL_INPUT_EXTRACTION_R1.json')['L'];rest=np.array(extract['rest_vertices_canonical']);palm=np.flatnonzero(rest[:,1]<.105);hits=[];wrong=[];mingap=None
for i,t in enumerate(times):
 V=A['verts'][i]
 for k in c.KEYS:
  angle=A['key_angles'][i,k['key_index']];V0=o.keytransform(k['midi_note'],V,angle,True) if angle else V
  for g in k['geometry']:
   pts=np.array(g['vertices']);lo=pts.min(0);hi=pts.max(0);inside=np.all(V0>=lo-1e-8,axis=1)&np.all(V0<=hi+1e-8,axis=1);deep=inside&(V0[:,2]<hi[2]-.003)
   if deep.any():hits.append({'time':float(t),'midi':k['midi_note'],'piece':g['name'],'vertices':int(deep.sum()),'palm_vertices':int(deep[palm].sum()),'max_depth_mm':float(np.max(hi[2]-V0[deep,2])*1000)})
  for j in range(5):
   if k['midi_note']==[50,None,None,None,38][j]:continue
   mm=o.measure(A['pads'][i,j],k['midi_note'],angle)
   if mm['pass']:wrong.append({'time':float(t),'finger':j+1,'midi':k['midi_note'],'gap_mm':mm['gap_mm']})
  pts=V0[palm]
  for top in k['key_top_playable_surface']:
   mask=(pts[:,0]>=top['xmin'])&(pts[:,0]<=top['xmax'])&(pts[:,1]>=top['ymin'])&(pts[:,1]<=top['ymax'])
   if mask.any():value=float(np.min(pts[mask,2]-top['z'])*1000);mingap=value if mingap is None else min(mingap,value)
dump('PROBE_DYNAMIC_CONTACT_R1.json',{'status':'PASS' if all(r['pass'] for r in contacts) else 'FAIL','notes':contacts,'uses_saved_reopened_evaluated_geometry':True})
dump('PROBE_CLEARANCE_R1.json',{'status':'PASS_FINITE_SCREEN' if not hits and not wrong else 'FAIL_FINITE_SCREEN','samples':len(times),'vertex_count':3300,'key_count':88,'hits':hits,'wrong_pad_contacts':wrong,'minimum_palm_projected_gap_mm':mingap,'limitation':'Finite vertex/key-piece screen, not exhaustive triangle collision; visible review is separate.'})
grid=np.arange(48,217)/120;idx=[int(np.argmin(abs(times-t))) for t in grid];assert max(abs(times[idx]-grid))<1e-8
Q=np.degrees(M['q'][idx]);vel=np.diff(Q,axis=0)*120;acc=np.diff(vel,axis=0)*120;bounds=[]
for j,d in enumerate(c.DIGITS):bounds.append(pol['joint_policy']['hard_bounds_deg']['THUMB' if j==0 else 'LEFT_IDLE_'+d if j in [1,2,3] else 'LONG'])
bounds=np.array(bounds);boundok=bool(np.all(Q>=bounds[:,0]-1e-7) and np.all(Q<=bounds[:,1]+1e-7));N=np.array(c.RIG['L']['native_to_canonical']);R=A['root_matrices'][idx]@np.linalg.inv(N);xyz=R[:,:3,3]*1000;v=np.diff(xyz,axis=0)*120;ac=np.diff(v,axis=0)*120;pitch=np.array([np.arctan2((r[:3,:3]@R[0,:3,:3].T)[2,1],(r[:3,:3]@R[0,:3,:3].T)[1,1]) for r in R])*180/np.pi;av=np.diff(pitch)*120;aa=np.diff(av)*120;dwell=[]
for n in o.EVENTS['L']:
 j=n['finger']-1;ids=np.flatnonzero((grid>=n['note_on']-1e-8)&(grid<n['note_off']+.07-1e-8));near=(Q[ids,j]-bounds[j,0]<.25)|(bounds[j,1]-Q[ids,j]<.25);run=0;longest=0
 for b in np.any(near,axis=1):run=run+1 if b else 0;longest=max(run,longest)
 dwell.append({'note_id':n['note_id'],'longest_near_bound_sec':longest/120,'not_sole_pass_gate':True})
limits=pol['continuity'];check={'joint_bounds':boundok,'joint_velocity':float(np.max(abs(vel)))<=limits['joint_velocity_deg_sec'],'joint_acceleration':float(np.max(abs(acc)))<=limits['joint_acceleration_deg_sec2'],'root_velocity':float(np.max(np.linalg.norm(v,axis=1)))<=limits['root_velocity_mm_sec'],'root_acceleration':float(np.max(np.linalg.norm(ac,axis=1)))<=limits['root_acceleration_mm_sec2'],'root_angular_velocity':float(np.max(abs(av)))<=limits['root_angular_velocity_deg_sec'],'root_angular_acceleration':float(np.max(abs(aa)))<=limits['root_angular_acceleration_deg_sec2']}
dump('PROBE_CONTINUITY_R1.json',{'status':'PASS' if all(check.values()) else 'FAIL','checks':check,'joint_velocity_max_deg_sec':float(np.max(abs(vel))),'joint_acceleration_max_deg_sec2':float(np.max(abs(acc))),'root_velocity_max_mm_sec':float(np.max(np.linalg.norm(v,axis=1))),'root_acceleration_max_mm_sec2':float(np.max(np.linalg.norm(ac,axis=1))),'root_angular_velocity_max_deg_sec':float(np.max(abs(av))),'root_angular_acceleration_max_deg_sec2':float(np.max(abs(aa))),'root_xyz_min_mm':xyz.min(0),'root_xyz_max_mm':xyz.max(0),'root_pitch_delta_range_deg':[float(pitch.min()),float(pitch.max())],'idle_joint_delta_deg':float(np.max(abs(Q[:,1:4]-np.degrees(o.qanchor('L1')[1:4])))),'active_near_bound_dwell':dwell,'root_shared_count':1,'analytic_curve':'C2 phase curves sampled120Hz. Saved quaternion channels are piecewise-linear approximations.','physiological_certification':False})
print(json.dumps({'contacts':[{k:v for k,v in r.items() if k!='rows'} for r in contacts],'deep_hits':len(hits),'wrong_pads':len(wrong),'continuity':check},indent=2),flush=True)
