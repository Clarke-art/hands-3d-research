import sys,json,math
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'))
import blender_utils as u
bind=json.loads((O/'ACTION_BINDINGS.json').read_text());dest=O/'G4_E5_NATURAL_BRIDGE_DESIGN_PROVISIONAL_R2.blend';T=np.load(O/'ACTION_TRACKS.npz')
bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False);sc=bpy.data.scenes[bind['scene']];bpy.context.window.scene=sc;rt=bpy.data.objects[bind['root']];rig=bpy.data.objects[bind['rig']];mesh=bpy.data.objects[bind['mesh']]
action=rt.animation_data.action
for fc in u.curves(action):
 if fc.data_path!='location':continue
 assert len(fc.keyframe_points)==len(T['times'])
 vals=T['root_location'][:,fc.array_index];dv=T['root_location_derivative'][:,fc.array_index]
 for i,k in enumerate(fc.keyframe_points):
  k.co.y=float(vals[i]);k.interpolation='BEZIER';k.handle_left_type='FREE';k.handle_right_type='FREE'
  pts=fc.keyframe_points;left=(k.co.x-pts[i-1].co.x)/3 if i else (pts[1].co.x-k.co.x)/3;right=(pts[i+1].co.x-k.co.x)/3 if i+1<len(pts) else left;slope=float(dv[i])/60
  k.handle_left=(k.co.x-left,k.co.y-slope*left);k.handle_right=(k.co.x+right,k.co.y+slope*right)
 fc.update()
u.settime(sc,2.527855);V,_=u.coords(mesh);B=np.load(O.parent/'hands_c01_anatomy_preparation_audit_r1/B_ACTUAL_SKIN_2.npz')['vertices'];startdiff=float(np.linalg.norm(V-B,axis=1).max()*1000)
assert startdiff<.002,startdiff
u.settime(sc,3.349997);V,_=u.coords(mesh);E=np.load(O/'ENDPOINT_2_ACTUAL_SKIN.npz')['vertices'];enddiff=float(np.linalg.norm(V-E,axis=1).max()*1000);assert enddiff<.002,enddiff
assert u.digest(u.native(mesh,rig))==u.pf['right_native_sha256']
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest))
out=dict(reason='Root object origin is distinct from wrist reference BASE; omitted rotated object-origin offset in initial action position export',formula='translation = BASE + delta + RR @ (BASEMAT.translation - BASE)',same_numerical_candidate=True,no_new_optimization=True,new_action_count_unchanged=2,initial_invalid_measurements='ACTION_EXPORT_INVALID_ROOT_FRAME_VALIDATION.json',start_vertex_error_mm=startdiff,end_vertex_error_mm=enddiff,frozen_native_identity=True)
(O/'ROOT_ACTION_EXPORT_CORRECTION.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print('ROOT_EXPORT_FIXED',startdiff,enddiff,flush=True)
