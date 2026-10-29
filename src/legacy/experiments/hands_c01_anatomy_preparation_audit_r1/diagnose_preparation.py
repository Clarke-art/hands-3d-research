import sys,json,ast
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'))
from geometry_detector import *
import blender_utils as u
PRE=O.parent/'hands_c01_s1_constrained_solver_feasibility_r1';info=json.loads((PRE/'ACTUAL_VALIDATION_2.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(PRE/'S1_CONSTRAINED_DIAGNOSTIC_R1.blend'),load_ui=False,use_scripts=False)
sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[info['rig']];mesh=bpy.data.objects[info['mesh']];rt=bpy.data.objects[info['root']]
anchor=json.loads((O.parent/'hands/audits/piano_hand_static_posture_clearance_refinement_r2/SOLVED_STATIC_POSES_R2.json').read_text())['poses']['R1']['joint_increments_deg']
original=np.array(info['state']);angles=np.array(info['solver']['key_angles']);rows=[]
for label,st in [('A_ORIGINAL',original.copy()),('ONLY_MIDDLE_SPREAD_REFERENCE',original.copy()),('ALL_PASSIVE_REFERENCE',original.copy())]:
 if label=='ONLY_MIDDLE_SPREAD_REFERENCE':st[17]=anchor[2][3]
 if label=='ALL_PASSIVE_REFERENCE':st[10:]=np.array(anchor[1:]).ravel()
 u.apply(st,rt,rig);V,F=u.coords(mesh);assert u.digest(u.native(mesh,rig))==u.pf['right_native_sha256']
 m=detect(V,angles,dict(midi=67,finger=1));ep=contact_metric(V,KEYS[55],angles[55],3);pad=V[int(D['pad_indices'][2])]
 rows.append(dict(label=label,state=st.tolist(),actual_geometry=m,E5_target_old_metric=ep,middle_pad_world_m=pad.tolist(),not_numerical_solve=True,not_qualified_candidate=True))
 np.savez_compressed(O/f'PERTURBATION_{label}_SKIN.npz',vertices=V,key_angles=angles)
 print(label,'E5 pad outside',ep['pad_horizontal_outside_mm'],'gap',ep['pad_gap_mm'],'self',m['nonadjacent_self_triangle_pairs'],'thumb',m['contact']['top_surface_crossing_triangles'],'depth',m['target_key_max_depth_mm'],'wrong',m['wrong_key_or_nonpulp_max_depth_mm'],flush=True)
(O/'READONLY_PREPARATION_PERTURBATIONS.json').write_text(json.dumps(rows,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')
