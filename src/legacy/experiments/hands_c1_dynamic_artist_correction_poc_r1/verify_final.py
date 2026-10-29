import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import *
expected=np.load(OUT/'CANDIDATE_2_FIXED_DENSE.npz');times=expected['times']
sc,rig,mesh,left,lrig=s.open_scene(OUT/'DYNAMIC_CANDIDATE_NOT_APPROVED.blend');g.init()
chosen=set()
for t in [2.2,2.3,2.42,2.45,2.492855,2.6,2.68,2.78,2.86,2.92,2.921426,3.02,3.12]:
 ix=int(np.argmin(abs(times-t)));chosen.update([max(0,ix-1),ix,min(len(times)-1,ix+1)])
rows=[]
for ix in sorted(chosen):
 t=float(times[ix]);c.settime(sc,t);V,T,F=s.coords_tri(mesh);Q=np.array([s.degrees(d) for d in DIGITS])
 rows.append(dict(time=t,full_skin_max_delta_mm=float(np.max(np.linalg.norm(V-expected['V'][ix],axis=1)))*1000,joint_max_delta_deg=float(np.max(abs(Q-expected['Q'][ix]))),frame=sc.frame_current,subframe=sc.frame_subframe))
assert max(r['full_skin_max_delta_mm'] for r in rows)<.001
assert max(r['joint_max_delta_deg'] for r in rows)<.001
assert sha(OUT/'DYNAMIC_CANDIDATE_NOT_APPROVED.blend')==sha(OUT/'CANDIDATE_2_IMPLEMENTATION_FIXED_NOT_APPROVED.blend')
baseline=np.load(OUT/'BASELINE_DENSE.npz');joints=[]
for t in [2.2,3.12]:
 ix=int(np.argmin(abs(times-t)));before=max(0,ix-1);after=min(len(times)-1,ix+1)
 deltaQ=expected['Q']-baseline['Q'];deltaV=expected['V']-baseline['V']
 joints.append(dict(time=t,endpoint_skin_delta_mm=float(np.max(np.linalg.norm(deltaV[ix],axis=1)))*1000,endpoint_joint_delta_deg=float(np.max(abs(deltaQ[ix]))),max_added_left_joint_rate_deg_s=float(np.max(abs((deltaQ[ix]-deltaQ[before])/(times[ix]-times[before])))),max_added_right_joint_rate_deg_s=float(np.max(abs((deltaQ[after]-deltaQ[ix])/(times[after]-times[ix]))))))
save('FINAL_REOPEN_SUBFRAME_VERIFICATION.json',dict(pass_=True,samples=rows,joins=joints,wrist_pose_scale=list(rig.pose.bones['WRIST_R'].scale),max_skin_delta_mm=max(r['full_skin_max_delta_mm'] for r in rows),max_joint_delta_deg=max(r['joint_max_delta_deg'] for r in rows),blend_sha256=sha(OUT/'DYNAMIC_CANDIDATE_NOT_APPROVED.blend'),exact_byte_copy=True))
protection('FINAL_REOPEN_INPUT_RECEIPT.json')
print('FINAL_REOPEN_PASS',len(rows),flush=True)
