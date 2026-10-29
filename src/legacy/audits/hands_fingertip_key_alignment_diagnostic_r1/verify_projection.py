import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_support as s
from blender_support import *
from bpy_extras.object_utils import world_to_camera_view
sc,rig,mesh,left,lrig=s.open_scene(SOURCE);sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']];sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100
rows=read(OUT/'STILL_PROJECTIONS.json')+[read(OUT/'NINTH_STILL_PROJECTION.json')];checks=[]
for r in rows:
    f=r['finger']
    for tag,point,pixel in [('pad',f['pad_world_m'],f['pad_pixel']),('terminal',f['terminal_world_m'],f['terminal_pixel'])]:
        co=world_to_camera_view(sc,sc.camera,Vector(point));p=[co.x*1280,(1-co.y)*720];checks.append(dict(image=r['name'],point=tag,independent_bpy_extras_pixel=p,stored_pixel=pixel,error_px=float(np.linalg.norm(np.array(p)-pixel))))
peak=max(x['error_px'] for x in checks);assert peak<.001
save('INDEPENDENT_CAMERA_PROJECTION_CHECK.json',dict(pass_=True,max_error_px=peak,checks=checks,method='Independent bpy_extras.object_utils.world_to_camera_view; compares true world coordinates with saved camera inverse/view-frame projection.',camera=sc.camera.name))
protection('PROJECTION_CHECK_SHA_RECEIPT.json')
