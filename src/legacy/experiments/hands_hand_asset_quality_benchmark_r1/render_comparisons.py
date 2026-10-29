import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'HAND_ASSET_BENCHMARK_STATIC.blend'),load_ui=False,use_scripts=False)
sc=bpy.context.scene;R=OUT/'renders';R.mkdir(exist_ok=True);records=[]
views=[
 ('OVERALL_FLAT','NEUTRAL','FLAT',(0,-.064,0),(0,0,.5),.34,(720,880)),
 ('OVERALL_SMOOTH','NEUTRAL','UNIFORM_SMOOTH',(0,-.064,0),(0,0,.5),.34,(720,880)),
 ('INDEX_OVERHEAD','NEUTRAL','FLAT',(-.03,.018,-.01),(0,0,.5),.10,(800,600)),
 ('INDEX_SIDE','NEUTRAL','FLAT',(-.03,.018,-.01),(-.5,0,0),.10,(800,600)),
 ('WEB_DORSAL_OBLIQUE','NEUTRAL','FLAT',(-.043,-.047,-.016),(-.34,-.17,.30),.13,(800,600)),
 ('WEB_PALMAR_REVERSE','NEUTRAL','FLAT',(-.043,-.047,-.016),(-.34,-.10,-.32),.13,(800,600)),
 ('WEB_SPREAD','THUMB_SPREAD','FLAT',(-.043,-.047,-.016),(-.34,-.17,.30),.13,(800,600)),
 ('POSE_NEUTRAL','NEUTRAL','FLAT',(0,-.026,-.012),(-.33,.08,.48),.27,(800,640)),
 ('POSE_INDEX_FLEX','INDEX_FLEX','FLAT',(0,-.026,-.012),(-.33,.08,.48),.27,(800,640)),
 ('POSE_THUMB_SPREAD','THUMB_SPREAD','FLAT',(0,-.026,-.012),(-.33,.08,.48),.27,(800,640)),
]
for view,state,shading,target,offset,scale,res in views:
 for ident in ['C1','MAKEHUMAN']:
  for ob in sc.objects:
   if ob.type=='MESH':ob.hide_render=ob.name!=ident+'__'+state
  ob=bpy.data.objects[ident+'__'+state]
  for f in ob.data.polygons:f.use_smooth=shading=='UNIFORM_SMOOTH'
  cam=sc.camera;cam.location=Vector(target)+Vector(offset);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
  sc.render.resolution_x,sc.render.resolution_y=res;sc.render.filepath=str(R/(ident+'__'+view+'.png'));bpy.ops.render.render(write_still=True)
  records.append(dict(identity=ident,view=view,state=state,shading=shading,file=str(Path(sc.render.filepath).relative_to(OUT)),camera_matrix=[list(r) for r in cam.matrix_world],ortho_scale=scale,resolution=res,mesh_name=ob.name,material='SHARED_NEUTRAL_NO_TEXTURE',lighting=sc.display.shading.studio_light,visible_skin='Entire mesh retained; field of view crops close-ups; no hand geometry hidden',display_reflection_only=ident=='MAKEHUMAN'))
  print('RENDERED',ident,view,flush=True)
(OUT/'RENDER_MANIFEST.json').write_text(json.dumps(records,indent=2),encoding='utf8')
# Save a useful open state: both neutral specimens side by side, flat, same actual scale.
for ob in sc.objects:
 if ob.type=='MESH':
  ob.hide_render=not ob.name.endswith('__NEUTRAL');ob.hide_viewport=ob.hide_render
  for f in ob.data.polygons:f.use_smooth=False
bpy.data.objects['C1__NEUTRAL'].location.x=-.12;bpy.data.objects['MAKEHUMAN__NEUTRAL'].location.x=.12
sc.camera.location=(0,-.06,.6);sc.camera.rotation_euler=(0,0,0);sc.camera.data.ortho_scale=.45;sc.render.resolution_x=1600;sc.render.resolution_y=1200
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'HAND_ASSET_BENCHMARK_REVIEW.blend'),check_existing=False)
print('RENDERS_COMPLETE',flush=True)
