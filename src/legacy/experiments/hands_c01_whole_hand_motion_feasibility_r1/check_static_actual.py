import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from blender_utils import *
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']];rt=bpy.data.objects[man['mapping']['R']['root']]
rig.animation_data_clear();rt.animation_data_clear();A=np.load(O/'STATIC_REACH_STATES.npz');rows=[]
for t,state,n in zip(A['times'],A['states'],I['notes']):
 settime(sc,float(t));apply(state,rt,rig);r,V=measure(sc,mesh,rig,t,n);rows.append(r);print('ACTUAL_STATIC',n['note_id'],'gap',round(r['contact']['gap_mm'],3),'wrong_key_depth',round(r['max_inactive_or_wrong_key_depth_mm'],3),'middle_ring',r['finger_intersection_pairs']['MIDDLE_RING'],flush=True)
assert digest(native(mesh,rig))==pf['right_native_sha256']
out('STATIC_ACTUAL_GEOMETRY_CHECK.json',dict(rows=rows,skin_evaluated=True,frozen_geometry_preserved=True,can_render_video=False,warning='Static poses are initial seeds; this check does not claim continuous motion.'))

