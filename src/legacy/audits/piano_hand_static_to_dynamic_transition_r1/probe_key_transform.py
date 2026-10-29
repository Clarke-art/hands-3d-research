import bpy,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from common import *
man=read(P/'DYNAMIC_SCENE_MANIFEST_R1.json');bpy.ops.wm.open_mainfile(filepath=str(P/'STATIC_TO_DYNAMIC_TRANSITION_CANDIDATE_R1.blend'),load_ui=False,use_scripts=False);out={}
for s,info in man['mapping'].items():
 sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;sc.frame_set(1);bpy.context.view_layer.update();rows=[]
 for index,pivotname in info['key_pivots'].items():
  pivot=bpy.data.objects[pivotname];rows.append({'midi':int(index)+21,'pivot_xyz':list(pivot.matrix_world.translation),'child_matrices':[{'object':o.name,'world_translation':list(o.matrix_world.translation),'expected_translation':[0,0,0]} for o in pivot.children]})
 out[s]=rows
dump('CONFIRMED_CODE_ERROR_R1.json',{'bug':'Key pivot.location not evaluated before assigning child.matrix_world; child local matrix left identity, producing erroneous extra translation. Fix explicit inverse-pivot child basis; no motion/planner/parameter changes.','candidate_before_fix_sha256':man['candidate_sha256'],'motion_sha256':sha(P/'temporal_motion.npz'),'observed_key_transforms':out})
print(json.dumps(out),flush=True)
