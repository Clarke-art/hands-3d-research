import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import *
sc,rig,mesh,left,lrig=s.open_scene(OUT/'IDLE_INDEX_CLEARANCE_B_NOT_APPROVED.blend');g.init()
sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']];cam=sc.camera
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
assert cam.data.type=='ORTHO';assert sc.render.engine=='BLENDER_WORKBENCH'
folder=OUT/'candidate_frames';folder.mkdir(exist_ok=False)
frames=list(range(1,83))+list(range(127,203));records=[]
for ix,frame in enumerate(frames):
 t=(frame-1)/60;c.settime(sc,t);dest=folder/f'{ix:04d}.png';sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
 records.append(dict(index=ix,source_frame=frame,time=t,path=str(dest)))
save('RENDER_SEQUENCE.json',dict(frames=records,camera=dict(name=cam.name,matrix=np.array(cam.matrix_world),scale=cam.data.ortho_scale),engine=sc.render.engine,size=[1280,720],fps=60))
# Exact witness projections are from actual saved candidate, not a synthetic overlay pose.
stills=[]
for identity,path in [('ORIGINAL_C1',SOURCE),('CANDIDATE_B',OUT/'IDLE_INDEX_CLEARANCE_B_NOT_APPROVED.blend')]:
 sc,rig,mesh,left,lrig=s.open_scene(path);g.init();sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']];cam=sc.camera
 sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
 from bpy_extras.object_utils import world_to_camera_view
 def project(points):
  uv=[world_to_camera_view(sc,cam,Vector(v)) for v in points];return [[v.x*1280,(1-v.y)*720] for v in uv]
 for label,t in [('A',26/60),('B',2.6)]:
  c.settime(sc,t);V,T,F=s.coords_tri(mesh);geo=g.keycheck(V,deep=True);cols=[r for r in geo if r['depth_mm']>1e-5]
  dest=OUT/f'{identity}_{label}_RAW.png';sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
  pts=[]
  for r in cols:
   cert=r['certificate']
   if cert:pts.append(dict(key=r['key'],depth_mm=r['depth_mm'],world=cert['witness_world_m'],pixel=project([cert['witness_world_m']])[0],triangle=cert['triangle']))
  stills.append(dict(identity=identity,label=label,time=t,path=str(dest),geometry=geo,witnesses=pts,index_pixels=project(V[g.IDS]),pad_pixel=project([V[1750]])[0]))
save('STILL_GEOMETRY_PROJECTIONS.json',stills);protection('RENDER_INPUT_RECEIPT.json');print('RENDER_DONE',len(frames),flush=True)
