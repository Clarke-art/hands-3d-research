import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_support as s
from blender_support import *
begin=time.perf_counter();edit=read(OUT/'EDIT_RECEIPT.json');sc,rig,mesh,left,lrig=s.open_scene(edit['candidate_path']);assert sha(edit['candidate_path'])==edit['candidate_sha256']
sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']];cam_before=[list(row) for row in sc.camera.matrix_world]
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
folder=OUT/'local_frames';folder.mkdir()
for frame in range(55,106):
    sc.frame_set(frame);sc.render.filepath=str(folder/f'{frame-55:04d}.png');bpy.ops.render.render(write_still=True)
    if frame%10==0:print('LOCAL_OVERHEAD_RENDER',frame,105,time.perf_counter()-begin,flush=True)
assert [list(row) for row in sc.camera.matrix_world]==cam_before
save('LOCAL_RENDER_RECEIPT.json',dict(seconds=time.perf_counter()-begin,frames=51,fps=60,start_sec=.9,end_sec=1.75,camera=sc.camera.name,camera_matrix=cam_before,dimensions=[1280,720],candidate_sha256=edit['candidate_sha256'],approval='NOT_APPROVED'))
protection('LOCAL_RENDER_PROTECTION.json')
