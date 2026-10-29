import sys
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement'))
from blender_local import *
P=Path(__file__).resolve().parent
man=read(C1/'SCENE_MANIFEST.json');bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
pre=read(P/'STATIC_PREFLIGHT.json')
for i in [0,2,5,6,7,9,11,12]:
    settime(sc,pre['poses'][i]['video_sec'])
    for view,name in man['cameras'].items():
        folder=P/'source_static_frames';folder.mkdir(exist_ok=True);sc.camera=bpy.data.objects[name];sc.render.filepath=str(folder/f'{i:02d}_{view}.png');bpy.ops.render.render(write_still=True)
print('EXACT_TIME_ORIGINAL_STATIC_COMPARATORS_NO_SAVE',flush=True)
