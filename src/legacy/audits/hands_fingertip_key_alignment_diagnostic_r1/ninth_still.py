import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_support as s
from blender_support import *
sc,rig,mesh,left,lrig=s.open_scene(SOURCE);sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']]
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100
cam=sc.camera;camera_matrix=np.array(cam.matrix_world);vf=np.array([list(v) for v in cam.data.view_frame(scene=sc)]);vlo=vf[:,:2].min(0);vhi=vf[:,:2].max(0)
method=read(OUT/'ANATOMICAL_SAMPLES_AND_METHOD.json');caps={d:np.array(v,int) for d,v in method['distal_cap_indices'].items()};term=method['terminal_vertices'];padpatch={d:np.array(v,int) for d,v in method['pad_neighborhood_indices'].items()}
RNOTES=[n for n in NOTES if n['hand']=='R'];black=[k for k in KEYS if k['color']=='BLACK']
extract(OUT/'diagnose.py',['project','world_key','surfaces','role','finger'],globals())
t=3.88571075;c.settime(sc,t);V,T,F=s.coords_tri(mesh);r=dict(name='09_MIDDLE_ACTIVE_E5',time=t,identity='ORIGINAL_C1',state=role(t,3),finger=finger(V,KEYS[55],3),raw_path=str(OUT/'raw_stills/09_MIDDLE_ACTIVE_E5.png'))
sc.render.image_settings.file_format='PNG';sc.render.filepath=r['raw_path'];bpy.ops.render.render(write_still=True);save('NINTH_STILL_PROJECTION.json',r);protection('NINTH_STILL_SHA_RECEIPT.json')
