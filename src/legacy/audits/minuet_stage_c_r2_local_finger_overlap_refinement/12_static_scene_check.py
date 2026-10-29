import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from blender_local import *
man=read(P/'SCENE_MANIFEST.json');assert sha(man['path'])==man['sha256']
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False)
sm=read(ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/STATIC_SCENE_MANIFEST_R2.json');expected=read(A/'SCENE_MANIFEST.json')['static_four_core_sha256'];actual={}
for label,info in sm['mapping'].items():
    bpy.context.window.scene=bpy.data.scenes[info['scene']];bpy.context.view_layer.update();actual[label]=digest(h.core(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]))
assert actual==expected
dump('STATIC_FOUR_SCENES_PRESERVED.json',dict(pass_=True,actual=actual,expected=expected,candidate_sha256=man['sha256']))
print('FOUR_APPROVED_STATIC_SCENES_UNCHANGED',flush=True)
