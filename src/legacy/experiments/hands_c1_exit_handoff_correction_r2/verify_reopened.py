import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import *
R1=ROOT/'experiments/hands_c1_dynamic_artist_correction_poc_r1';ledger=read(R1/'CANDIDATE_2_FIXED_EDIT_LEDGER.json');paths=set(ledger['edited_paths'])
sc,rig,mesh,left,lrig=s.open_scene(OUT/'R1_START_ISOLATED_NOT_APPROVED.blend');g.init()
original_outside=s.payload(rig.animation_data.action,paths);outside_digest=c.digest(original_outside);scale={b.name:list(b.scale) for b in rig.pose.bones}
def effective(rows):
 return [dict(path=r['path'],index=r['index'],extrapolation=r['extrapolation'],keys=[dict(co=k['co'],interpolation=k['interpolation'],**({} if k['interpolation']=='LINEAR' else dict(left=k['left'],right=k['right']))) for k in r['keys']]) for r in rows]
results=[]
for number in [1,2]:
 path=OUT/f'EXIT_CANDIDATE_{number}_METADATA_RESTORED_NOT_APPROVED.blend' if number==1 else OUT/'EXIT_CORRECTED_NOT_APPROVED.blend'
 with np.load(OUT/f'CANDIDATE_{number}_DENSE.npz') as z:ref={k:z[k] for k in z.files}
 sc,rig,mesh,left,lrig=s.open_scene(path);g.init();current_outside=s.payload(rig.animation_data.action,paths)
 if c.digest(current_outside)!=outside_digest:
  save(f'CANDIDATE_{number}_UNEDITED_CURVE_METADATA_DIFFERENCE.json',dict(original=original_outside,candidate=current_outside))
 assert c.digest(effective(current_outside))==c.digest(effective(original_outside)),'UNEDITED_EFFECTIVE_CURVE_CHANGED'
 assert scale=={b.name:list(b.scale) for b in rig.pose.bones}
 assert ledger['native']=={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]}
 indices=set()
 for t in [2.6,2.68,2.78,2.86,2.8875,2.890625,2.92,2.9214260000000003,3.02,3.066666666666667,3.12]:
  i=int(np.argmin(abs(ref['times']-t)));indices.update([max(0,i-1),i,min(len(ref['times'])-1,i+1)])
 rows=[]
 for i in sorted(indices):
  t=float(ref['times'][i]);c.settime(sc,t);V,T,F=s.coords_tri(mesh);Q=np.array([s.degrees(d) for d in DIGITS])
  rows.append(dict(time=t,frame=sc.frame_current,subframe=sc.frame_subframe,skin_delta_mm=float(np.max(np.linalg.norm(V-ref['V'][i],axis=1)))*1000,joint_delta_deg=float(np.max(abs(Q-ref['Q'][i])))))
 assert max(r['skin_delta_mm'] for r in rows)<.001 and max(r['joint_delta_deg'] for r in rows)<.001
 results.append(dict(candidate=number,path=str(path),sha256=sha(path),samples=rows,max_skin_delta_mm=max(r['skin_delta_mm'] for r in rows),max_joint_delta_deg=max(r['joint_delta_deg'] for r in rows),unmodified_bone_effective_curves_exact=True,unmodified_full_curve_metadata_exact=c.digest(current_outside)==outside_digest,pose_scales_exact_to_R1=True))
assert sha(OUT/'EXIT_CORRECTED_NOT_APPROVED.blend')==sha(OUT/'EXIT_CANDIDATE_2_METADATA_RESTORED_NOT_APPROVED.blend')
save('FINAL_REOPEN_SUBFRAME_VERIFICATION.json',dict(pass_=True,candidates=results,final_exact_copy=True,notes_count=len(NOTES)))
protection('FINAL_REOPEN_INPUT_RECEIPT.json');print('R2_REOPEN_PASS',sum(len(r['samples']) for r in results))
