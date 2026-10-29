import bpy,json,numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parent
data=json.loads((P/'RENDER_INPUT_R1.json').read_text());geo=np.load(P/'render_geometry.npz');S=Matrix(data['plane']['reflection_armature_matrix'])
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=600;sc.render.resolution_y=650;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.world=bpy.data.worlds.new('EVIDENCE_WORLD');sc.world.color=(.10,.12,.15)
sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
sh=sc.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.66,.68,.71);sh.background_type='WORLD';sh.show_cavity=False;sh.show_shadows=True;sh.shadow_intensity=0;sh.show_specular_highlight=True
cd=bpy.data.cameras.new('REVIEW_CAMERA');cd.type='ORTHO';cd.clip_start=.001;cd.clip_end=10
cam=bpy.data.objects.new('REVIEW_CAMERA',cd);sc.collection.objects.link(cam);sc.camera=cam
tiles=P/'_render_tiles';tiles.mkdir(exist_ok=True)
qualification=json.loads((P.parents[1]/'audits/right_hand_first_web_production_weight_qualification_r1/APPROVED_POSE_REGRESSION_R1.json').read_text())
cameras={r['pose']:r['cameras'] for r in qualification['poses']};records=[]
active=None
for case in data['cases']:
 for view in ['PALMAR','DORSAL','FIRST_WEB']:
  d=Vector((-.38183954,-.92405248,.0180442) if view=='PALMAR' else ((.30,.94,.16) if view=='DORSAL' else (.19980031,-.93906146,.27972043))).normalized()
  r=Vector((0,0,1)).cross(d).normalized();u=d.cross(r).normalized();V=[Vector(v) for v in geo['R_'+case]]
  if view=='FIRST_WEB':center=Vector(cameras[case]['REASONABLE_CLOSE_VIEW']['center']);scale=.14
  else:
   projections=[[v.dot(a) for v in V] for a in [r,u,d]]
   center=sum((a*((min(p)+max(p))/2) for a,p in zip([r,u,d],projections)),Vector())
   scale=max((max(projections[0])-min(projections[0]))*650/600,max(projections[1])-min(projections[1]))*1.14
  for side in ['R','L']:
   if active:
    me=active.data;bpy.data.objects.remove(active,do_unlink=True);bpy.data.meshes.remove(me)
   me=bpy.data.meshes.new('EVALUATED_NATIVE_GEOMETRY');me.from_pydata(geo[side+'_'+case].tolist(),[],data['right_faces' if side=='R' else 'left_faces'])
   for p,smooth in zip(me.polygons,data['smooth']):p.use_smooth=smooth
   me.update();active=bpy.data.objects.new('EVALUATED_NATIVE_GEOMETRY',me);sc.collection.objects.link(active)
   dd=d if side=='R' else S.to_3x3()@d;uu=u if side=='R' else S.to_3x3()@u;rr=uu.cross(dd).normalized();cc=center if side=='R' else S@center
   rot=Matrix((rr,uu,dd)).transposed().to_4x4();rot.translation=cc+dd*.8;cam.matrix_world=rot;cd.ortho_scale=scale
   dest=tiles/f'{case}__{view}__{side}.png';sc.render.filepath=str(dest)
   bpy.ops.render.render(write_still=True)
   records.append({'pose':case,'view':view,'side':side,'camera_world':list(map(list,rot)),'ortho_scale_m':scale,'native_evaluated_vertices':3300,'native_smooth_flags':True,'display':'neutral studio surface, no cavity, no geometry edits'})
(P/'RENDER_EVIDENCE_METADATA_R1.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('RENDER_REVIEW_COMPLETE',flush=True)
