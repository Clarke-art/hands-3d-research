import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));from stage_common import *
man=read(R1/'SCENE_MANIFEST.json');assert sha(man['path'])==man['sha256']
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False)
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
dump('R1_REVIEW_CAMERA_BIND.json',dict(candidate_sha256=man['sha256'],render_engine=sc.render.engine,
    fps=sc.render.fps,dimensions=[sc.render.resolution_x,sc.render.resolution_y],
    cameras={view:dict(matrix_world=np.array(bpy.data.objects[name].matrix_world),ortho_scale=bpy.data.objects[name].data.ortho_scale,
        type=bpy.data.objects[name].data.type,clip_start=bpy.data.objects[name].data.clip_start,clip_end=bpy.data.objects[name].data.clip_end)
        for view,name in man['cameras'].items()}))
print('READ_ONLY_R1_CAMERAS_BOUND')
