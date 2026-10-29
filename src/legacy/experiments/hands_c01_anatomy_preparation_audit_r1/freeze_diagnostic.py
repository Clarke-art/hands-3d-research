import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'))
from geometry_detector import *
import blender_utils as u
info=json.loads((O/'B_ACTUAL_2.json').read_text());dest=O/'S1_ANATOMY_PREPARATION_DIAGNOSTIC_R1.blend'
bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False);sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc
# Derivative only: remove inherited Action datablocks, preserving corrective shape drivers.
for a in list(bpy.data.actions):bpy.data.actions.remove(a,do_unlink=True)
for other in list(bpy.data.scenes):
 if other!=sc:bpy.data.scenes.remove(other)
sc.frame_start=sc.frame_current;sc.frame_end=sc.frame_current
V,F=u.coords(bpy.data.objects[info['mesh']]);snapshot=np.load(O/'B_ACTUAL_SKIN_2.npz');assert np.max(abs(V-snapshot['vertices']))<1e-7
assert u.digest(u.native(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]))==u.pf['right_native_sha256']
m=detect(V,snapshot['key_angles'],dict(midi=67,finger=1));assert m['contact']['top_surface_crossing_triangles']>0 and m['target_key_max_depth_mm']<=.25 and m['wrong_key_or_nonpulp_max_depth_mm']==0 and m['nonadjacent_self_triangle_pairs']==0
assert len(bpy.data.actions)==0
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest))
bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes[info['scene']];vr,_=u.coords(bpy.data.objects[info['mesh']])
assert np.max(abs(vr-V))<1e-7 and len(bpy.data.actions)==0
out=dict(status='PURE_STATIC_DIAGNOSTIC_VERIFIED',action_datablocks=0,scene_count=len(bpy.data.scenes),selected_scene=info['scene'],vertex_difference_mm=float(np.linalg.norm(vr-snapshot['vertices'],axis=1).max()*1000),frozen_native_identity_verified=True,actual_geometry=m,original_source_actions_verified_before_freezing=True,corrective_drivers_preserved=True,all_sources_readonly=True)
(O/'STATIC_BLEND_FINAL_CHECK.json').write_text(json.dumps(out,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')
print('PURE_STATIC_DELIVERY',out['action_datablocks'],out['scene_count'],out['vertex_difference_mm'],flush=True)
