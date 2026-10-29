import bpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));from stage_common import *
man=read(P/'SCENE_MANIFEST.json');assert sha(man['path'])==man['sha256']
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False)
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.use_persistent_data=True
for f in range(1,sc.frame_end+1):
    sc.frame_set(f)
    for view,name in man['cameras'].items():
        folder=P/'_frames'/view;folder.mkdir(parents=True,exist_ok=True);dest=folder/f'{f-1:04d}.png'
        if dest.exists():continue
        sc.camera=bpy.data.objects[name];sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
    if f%30==0:print('SAME_SINGLE_CANDIDATE_RENDER',f,'/',sc.frame_end,flush=True)
dump('RENDER_MANIFEST.json',dict(candidate_sha256=man['sha256'],frames_each=sc.frame_end,fps=60,
    views=man['cameras'],dimensions=[1280,720],normal_speed=True,right_only=True))
