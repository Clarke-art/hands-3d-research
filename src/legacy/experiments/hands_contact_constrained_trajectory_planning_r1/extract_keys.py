import sys, json, ast, time, math
from pathlib import Path
sys.dont_write_bytecode = True
import bpy, numpy as np
from mathutils import Matrix
O = Path(__file__).resolve().parent
sys.path.insert(0, str(O))
sys.path.insert(0, str(O.parent / 'hands_c01_whole_hand_motion_feasibility_r1'))
from geometry_detector import *
from triangle_distance import *
import blender_utils as u
RAW = D
P = json.loads((O / 'POLICY_LOCK.json').read_text())
I = json.loads((O / 'EXPERIMENT_INPUT.json').read_text())
PRE = O.parent / 'hands_contact_state_motion_planner_comparison_r1'
tree = ast.parse((O / 'extract_anatomy.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ['unit', 'angle', 'matrix', 'coords', 'signed_rot', 'anatomy']], type_ignores=[]), 'anatomy', 'exec'))
tree = ast.parse((O.parent / 'hands_c01_g4_e5_natural_motion_bridge_r2/bake_and_validate.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'strict'], type_ignores=[]), 'strict', 'exec'))
M = P['source_action_scene']
bpy.ops.wm.open_mainfile(filepath=M['path'], load_ui=False, use_scripts=False)
sc = bpy.data.scenes[M['scene']]
bpy.context.window.scene = sc
rig = bpy.data.objects[M['mapping']['R']['rig']]
mesh = bpy.data.objects[M['mapping']['R']['mesh']]
rt = bpy.data.objects[M['mapping']['R']['root']]
expected = json.loads((PRE / 'ORIGINAL_ACTION_INSPECTION.json').read_text())['action_payloads']
actual = {str(i): u.digest(u.payload(bpy.data.objects[n].animation_data.action)) if bpy.data.objects[n].animation_data and bpy.data.objects[n].animation_data.action else None for i, n in u.man['key_pivots'].items()}
assert expected == actual
E = json.loads((O / 'ENDPOINT_SOLVE_2.json').read_text())
Q0 = np.array(E['reference_q_R1'])
Q1 = np.array(E['reference_q_R2'])
ACTIVE = np.array(E['active_flex_anchor'])
times=json.loads((O/'COLLOCATION_TIMES.json').read_text());angles=[]
for t in times:u.settime(sc,t);angles.append(u.keyangles())
np.savez_compressed(O/'COLLOCATION_KEY_STATES.npz',times=times,angles=angles)
assert u.digest(u.native(mesh,rig))==u.pf['right_native_sha256']
(O/'INPUT_SCENE_VERIFICATION.json').write_text(json.dumps(dict(native_identity=True,key_action_payloads_match=True,key_action_payloads=actual,source_saved=False,times=times)))
print('INPUT_SCENE_IDENTITY_PASS',len(times))
