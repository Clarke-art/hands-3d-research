import bpy,json,sys,ast,hashlib
import numpy as np
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;R=P.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'audits/dual_hand_synchronized_real_motion_validation_r1/DUAL_HAND_REAL_MOTION_VALIDATION_CANDIDATE_R1.blend'),load_ui=False,use_scripts=False)
out={}
for side in ['R','L']:
 rig=bpy.data.objects[side.replace('R','RIGHT').replace('L','LEFT')+'_HAND_PRODUCTION_RIG']
 rig.parent=None;rig.location=(0,0,0)
 rig.animation_data.action=None
 for b in rig.pose.bones:b.rotation_quaternion=(1,0,0,0)
 bpy.context.view_layer.update()
 out[side]={'matrix':[list(x) for x in rig.matrix_world],'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'matrix':[list(x) for x in b.matrix_local]} for b in rig.data.bones}}
(P/'HAND_GEOMETRY_PROBE_R1.json').write_text(json.dumps(out,indent=2))
print('HAND_PROBE_DONE')
