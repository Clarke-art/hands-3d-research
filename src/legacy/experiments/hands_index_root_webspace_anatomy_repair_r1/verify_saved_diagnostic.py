import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import support as s
from support import *
sc,rig,mesh,left,lrig=s.open_scene(SOURCE);c.settime(sc,2.6)
base=dict(native=c.digest(c.native(mesh,rig)),actions=s.protected_state(),R=s.coords_tri(mesh)[0],L=s.coords_tri(left)[0],q={d:s.degrees(d) for d in DIGITS},clock=[sc.frame_start,sc.frame_end,sc.render.fps,sc.render.fps_base],key_angles=[s.keyangle(k) for k in KEYS])
rows=[]
for name in ['ORIGINAL_C1_DIAGNOSTIC_ONLY.blend','ANATOMICAL_DIAGNOSTIC_ONLY.blend','ANATOMICAL_DIAGNOSTIC_WITH_TRUE_SIDE.blend']:
 sc,rig,mesh,left,lrig=s.open_scene(OUT/name);c.settime(sc,2.6);R=s.coords_tri(mesh)[0];L=s.coords_tri(left)[0]
 row=dict(file=name,sha256=sha(OUT/name),right_mesh_max_difference_mm=float(np.linalg.norm(R-base['R'],axis=1).max()*1000),left_mesh_max_difference_mm=float(np.linalg.norm(L-base['L'],axis=1).max()*1000),frozen_native_same=c.digest(c.native(mesh,rig))==base['native'],all_animated_object_actions_same=s.protected_state()==base['actions'],joint_values_same=all(np.array_equal(s.degrees(d),base['q'][d]) for d in DIGITS),clock_same=[sc.frame_start,sc.frame_end,sc.render.fps,sc.render.fps_base]==base['clock'],all_88_key_angles_same=[s.keyangle(k) for k in KEYS]==base['key_angles'],corrective_values={k.name:k.value for k in mesh.data.shape_keys.key_blocks},diagnostic_only=True)
 assert row['right_mesh_max_difference_mm']==row['left_mesh_max_difference_mm']==0
 assert all(row[k] for k in ['frozen_native_same','all_animated_object_actions_same','joint_values_same','clock_same','all_88_key_angles_same'])
 rows.append(row)
save('REOPEN_DIAGNOSTIC_VERIFICATION.json',dict(all_pass=True,t_s=2.6,source=str(SOURCE),source_sha256=sha(SOURCE),saved_files=rows,animated_object_actions=base['actions'],clock=base['clock'],notes_count=len(NOTES),pose_rounds=0,repair_candidate=None))
print('REOPEN_DIAGNOSTIC_PASS',len(rows),flush=True)
