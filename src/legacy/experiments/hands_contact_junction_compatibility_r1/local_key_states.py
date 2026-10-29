import sys,json,math
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'));import blender_utils as u
P=json.loads((O/'POLICY_LOCK.json').read_text());M=P['source_action_scene'];bpy.ops.wm.open_mainfile(filepath=M['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[M['scene']];bpy.context.window.scene=sc;plan=json.loads((O/'LOCAL_PATH_PLAN.json').read_text());A=[]
for t in plan['post_knots']:u.settime(sc,t);A.append(u.keyangles())
np.savez_compressed(O/'LOCAL_PATH_KEY_STATES.npz',times=plan['post_knots'],angles=A);print('SOURCE_KEY_POST_STATES',len(A))
