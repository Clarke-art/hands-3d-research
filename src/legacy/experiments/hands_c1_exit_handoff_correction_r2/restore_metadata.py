import sys,shutil
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import *
R1=ROOT/'experiments/hands_c1_dynamic_artist_correction_poc_r1';paths=set(read(R1/'CANDIDATE_2_FIXED_EDIT_LEDGER.json')['edited_paths'])
def effective(rows):
 return [dict(path=r['path'],index=r['index'],extrapolation=r['extrapolation'],keys=[dict(co=k['co'],interpolation=k['interpolation'],**({} if k['interpolation']=='LINEAR' else dict(left=k['left'],right=k['right']))) for k in r['keys']]) for r in rows]
sc,rig,mesh,left,lrig=s.open_scene(OUT/'R1_START_ISOLATED_NOT_APPROVED.blend');g.init()
source_action_name=rig.animation_data.action.name;outside_digest=c.digest(s.payload(rig.animation_data.action,paths));rows=[]
for number in [1,2]:
 oldpath=OUT/f'EXIT_CANDIDATE_{number}_NOT_APPROVED.blend';sc,rig,mesh,left,lrig=s.open_scene(oldpath);g.init()
 payload=s.payload(rig.animation_data.action);bykey={(r['path'],r['index']):r for r in payload}
 with bpy.data.libraries.load(str(OUT/'R1_START_ISOLATED_NOT_APPROVED.blend'),link=False) as (fr,to):
  assert source_action_name in fr.actions;to.actions=[source_action_name]
 action=to.actions[0];action.name=f'R2_EXIT_{number}_SAME_ANIMATION_METADATA_RESTORED';rig.animation_data.action=action
 for f in s.curves(action):
  if f.data_path not in paths:continue
  r=bykey[f.data_path,f.array_index]
  for i in reversed(range(len(f.keyframe_points))):f.keyframe_points.remove(f.keyframe_points[i],fast=True)
  f.keyframe_points.add(len(r['keys']))
  for k,kr in zip(f.keyframe_points,r['keys']):
   k.co=kr['co'];k.interpolation=kr['interpolation'];k.handle_left_type=kr['lt'];k.handle_right_type=kr['rt'];k.handle_left=kr['left'];k.handle_right=kr['right']
  f.extrapolation=r['extrapolation'];f.update()
 assert c.digest(effective(s.payload(action)))==c.digest(effective(payload)),'ANIMATION_FUNCTION_CHANGE_FORBIDDEN'
 assert c.digest(s.payload(action,paths))==outside_digest,'FROZEN_METADATA_NOT_RESTORED'
 c.settime(sc,2.6);sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']]
 newpath=OUT/f'EXIT_CANDIDATE_{number}_METADATA_RESTORED_NOT_APPROVED.blend';assert not newpath.exists();bpy.ops.wm.save_as_mainfile(filepath=str(newpath),check_existing=True)
 # Reopen and verify the entire501-sample evaluated trajectory unchanged.
 sc,rig,mesh,left,lrig=s.open_scene(newpath);g.init();assert c.digest(s.payload(rig.animation_data.action,paths))==outside_digest
 with np.load(OUT/f'CANDIDATE_{number}_DENSE.npz') as z:ref={k:z[k] for k in z.files}
 maximum=0.;maxq=0.
 for i,t in enumerate(ref['times']):
  c.settime(sc,float(t));V,T,F=s.coords_tri(mesh);Q=np.array([s.degrees(d) for d in DIGITS])
  maximum=max(maximum,float(np.max(np.linalg.norm(V-ref['V'][i],axis=1)))*1000);maxq=max(maxq,float(np.max(abs(Q-ref['Q'][i]))))
 assert maximum==0 and maxq==0
 rows.append(dict(candidate=number,before_path=str(oldpath),before_sha256=sha(oldpath),after_path=str(newpath),after_sha256=sha(newpath),effective_all_curve_payload_identical=True,all_unedited_curve_metadata_exact_to_R1=True,all501_skin_max_delta_mm=maximum,all501_joint_max_delta_deg=maxq))
final=OUT/'EXIT_CORRECTED_NOT_APPROVED.blend';backup=OUT/'EXIT_CORRECTED_PRE_METADATA_RESTORE_NOT_APPROVED.blend';assert not backup.exists();shutil.copyfile(final,backup);shutil.copyfile(OUT/'EXIT_CANDIDATE_2_METADATA_RESTORED_NOT_APPROVED.blend',final)
save('METADATA_RESTORATION.json',dict(animation_design_count=2,no_new_animation_design=True,reason='FCurve.update recalculated dormant handle X coordinates on unedited LINEAR curves. Rebuild from untouched R1 Action and transfer only allowed curves, without changing any effective animation.',candidates=rows,rendered_geometry_identical_at_all501_samples=True,original_rendered_final_preserved_as=str(backup),final_sha256=sha(final)))
protection('METADATA_RESTORATION_INPUT_RECEIPT.json');print('METADATA_RESTORATION_COMPLETE',flush=True)
