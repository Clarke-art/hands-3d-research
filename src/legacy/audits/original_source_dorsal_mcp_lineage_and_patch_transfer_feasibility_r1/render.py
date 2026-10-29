import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,math
from mathutils import Vector
G=read(OUT/'REVIEW_GEOMETRY.json');frame=G['frame'];origin=Vector(frame['origin_world_mm'])/1000;n=Vector(frame['outward']);x=Vector(frame['x']);y=Vector(frame['y']);human=Vector(G['camera']['direction'])
sc=bpy.context.scene
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
sc.render.resolution_x=640;sc.render.resolution_y=640;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
world=bpy.data.worlds.new('MATCHED_WORLD');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.18,.21,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35;sc.world=world
sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_cavity=False;sc.display.shading.show_shadows=True;sc.display.shading.background_type='WORLD'
cd=bpy.data.cameras.new('MATCHED_CAMERA');cd.type='ORTHO';cd.clip_start=.001;cd.clip_end=4
cam=bpy.data.objects.new('MATCHED_CAMERA',cd);sc.collection.objects.link(cam);sc.camera=cam
ld=bpy.data.lights.new('MATCHED_SUN','SUN');ld.energy=2;ld.angle=.08
light=bpy.data.objects.new('MATCHED_SUN',ld);sc.collection.objects.link(light)
mat=bpy.data.materials.new('NEUTRAL_CLAY');mat.diffuse_color=(.57,.63,.7,1)
wiremat=bpy.data.materials.new('WIRE');wiremat.diffuse_color=(.03,.07,.1,1)
dark=bpy.data.materials.new('SILHOUETTE');dark.diffuse_color=(.015,.02,.025,1)
made=[];manifest=[]
def clear():
 for ob in made:
  data=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
  if isinstance(data,bpy.types.Mesh):bpy.data.meshes.remove(data)
  else:bpy.data.curves.remove(data)
 made.clear()
def line(points):
 cu=bpy.data.curves.new('actual native wire','CURVE');cu.dimensions='3D';cu.bevel_depth=.000017;cu.bevel_resolution=0
 sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,v in zip(sp.points,points):p.co=(*v,1)
 ob=bpy.data.objects.new(cu.name,cu);sc.collection.objects.link(ob);cu.materials.append(wiremat);made.append(ob)
labels=['OFFICIAL_BASE','OFFICIAL_L1','STAGE2_L1','STAGE4A_R2_BASE','STAGE4C_R2']
views=['CLOSE','HUMAN','GRAZING','WIRE','SIDE','SILHOUETTE','FULL_DORSAL']
if '--' in sys.argv:
 args=sys.argv[sys.argv.index('--')+1:]
 if args==['PROBE_ONLY']:labels=['TRANSFER_PROBE']
 elif args==['HUMAN_ALL']:labels+=['TRANSFER_PROBE'];views=['HUMAN']
 elif args==['TRACE_ONLY']:labels=['TRACE_0','TRACE_1'];views=['CLOSE','GRAZING','WIRE']
 else:views=args
for view in views:
 sc.render.resolution_y=800 if view=='HUMAN' else 640
 for shade in ['FLAT','SOURCE_NATIVE']:
  for label in labels:
   clear();s=G['stages'][label];v=[Vector(p)/1000 for p in s['world_mm']]
   me=bpy.data.meshes.new('MEASURED_DISPLAY');me.from_pydata(v,[],s['faces']);me.materials.append(dark if view=='SILHOUETTE' else mat)
   for p,sm in zip(me.polygons,s['smooth']):p.use_smooth=sm if shade=='SOURCE_NATIVE' else False
   me.update();ob=bpy.data.objects.new(label,me);sc.collection.objects.link(ob);made.append(ob)
   target=origin.copy();direction=human.copy();scale=.028
   if view=='HUMAN':target=Vector(G['camera']['center_world_m']);scale=G['camera']['ortho_scale_m']
   if view=='FULL_DORSAL':target=Vector(G['camera']['center_world_m']);scale=.24;direction=n
   if view in ['SIDE','SILHOUETTE']:direction=(x+n*.15+y*.15).normalized()
   cam.location=target+direction*.55;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale
   sc.render.engine='BLENDER_EEVEE' if view in ['CLOSE','HUMAN','GRAZING','SIDE','FULL_DORSAL'] else 'BLENDER_WORKBENCH'
   ld.energy=2;light.rotation_euler=(-(x+n*.08) if view=='GRAZING' else -(n+x*.3+y*.4)).to_track_quat('-Z','Y').to_euler()
   if view=='WIRE':
    edges=set()
    for fi in s['roi_faces']:
     p=s['faces'][fi]
     for a,b in zip(p,p[1:]+p[:1]):edges.add(tuple(sorted([a,b])))
    for a,b in edges:line([v[a],v[b]])
   name=f'{label}_{view}_{shade}.png';sc.render.filepath=str(OUT/'renders'/name);bpy.ops.render.render(write_still=True)
   manifest.append({'path':'renders/'+name,'stage':label,'view':view,'shade':shade,'camera_target_m':list(target),'camera_direction':list(direction),'ortho_scale_m':scale,'lighting':'Shared neutral diagnostic sun; grazing direction for GRAZING','source_native_definition':'Native face smoothing flags retained; neutral diagnostic material since official source has no materials','NOT_PRODUCTION':True})
   print('MATCHED_RENDER',name,flush=True)
previous=read(OUT/'DENT_SOURCE_MATCHED_VISUAL_AUDIT_R1.json')['renders'] if (OUT/'DENT_SOURCE_MATCHED_VISUAL_AUDIT_R1.json').exists() else []
keys={r['path'] for r in manifest};manifest=[r for r in previous if r['path'] not in keys]+manifest
dump('DENT_SOURCE_MATCHED_VISUAL_AUDIT_R1.json',{'renders':manifest,'same_camera_scale_lighting_within_each_row':True,'physical_ROI':'Exact validated subdivision and historical parent edge ancestry','native_material_note':'Official source has zero materials; source-native means its actual face shading flags, with a common neutral material. No invented source material.','sections':'DENT_SOURCE_LINEAGE_METRICS_R1.json actual triangle-plane segments at 0/60/120 degrees; probe sections in PROBE_VISUAL_GEOMETRY_DIAGNOSTICS.json','Human_visual_acceptance':'PENDING_HUMAN_REVIEW','blend_saves':0})
