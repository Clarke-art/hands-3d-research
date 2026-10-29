import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
from mathutils import Vector
G=read(OUT/'MATCHED_ZERO_BIND_REVIEW_GEOMETRY_R1.json');D=read(ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_r1/APPLICATION_MATCHED_REVIEW_GEOMETRY_R1.json');G['camera']=D['camera'];frame=D['frame'];origin=Vector(frame['origin_world_mm'])/1000;n=Vector(frame['outward']);x=Vector(frame['x']);y=Vector(frame['y']);human=Vector(G['camera']['direction'])
assert read(OUT/'PHASE_MACHINE_RESULT_R1.json')['BIND_ZERO']=='PASS'
(OUT/'renders').mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.render.film_transparent=False
world=bpy.data.worlds.new('AUDIT_WORLD');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.18,.21,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35;sc.world=world
sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_cavity=False;sc.display.shading.show_shadows=True;sc.display.shading.background_type='WORLD'
cd=bpy.data.cameras.new('MATCHED_CAMERA');cd.type='ORTHO';cd.clip_start=.001;cd.clip_end=4;cam=bpy.data.objects.new('MATCHED_CAMERA',cd);sc.collection.objects.link(cam);sc.camera=cam
ld=bpy.data.lights.new('MATCHED_SUN','SUN');ld.energy=2;ld.angle=.08;light=bpy.data.objects.new('MATCHED_SUN',ld);sc.collection.objects.link(light)
mat=bpy.data.materials.new('COMMON_NEUTRAL_CLAY');mat.diffuse_color=(.57,.63,.7,1)
active=None;manifest=[]
overview_only='--' in sys.argv and sys.argv[sys.argv.index('--')+1:]==['OVERVIEWS']
if overview_only:manifest=read(OUT/'DORSAL_BIND_ZERO_MATCHED_RENDER_MANIFEST_R1.json')['renders']
def render(label,view,shade,target,direction,scale,size=(640,640),engine='BLENDER_EEVEE'):
 global active
 if active:
  me=active.data;bpy.data.objects.remove(active,do_unlink=True);bpy.data.meshes.remove(me)
 s=G['stages'][label];me=bpy.data.meshes.new('DISPLAY_MEASURED_GEOMETRY');me.from_pydata(s['world_m'],[],G['faces']);me.materials.append(mat)
 for p,sm in zip(me.polygons,G['smooth']):p.use_smooth=sm if shade=='SOURCE_NATIVE' else False
 me.update();active=bpy.data.objects.new('UNSAVED_AUDIT_DISPLAY',me);sc.collection.objects.link(active)
 cam.location=Vector(target)+Vector(direction)*.55;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale
 light.rotation_euler=(-(x+n*.08) if 'GRAZING' in view else -(n+x*.3+y*.4)).to_track_quat('-Z','Y').to_euler()
 sc.render.engine=engine;sc.render.resolution_x=size[0];sc.render.resolution_y=size[1]
 name=f'{label}_{view}_{shade}.png';sc.render.filepath=str(OUT/'renders'/name);bpy.ops.render.render(write_still=True)
 manifest[:]=[r for r in manifest if r['path']!='renders/'+name]
 manifest.append({'path':'renders/'+name,'label':label,'view':view,'shade':shade,'target_world_m':list(target),'direction':list(direction),'orthographic_scale_m':scale,'resolution':list(size),'camera_right_world':list(cam.rotation_euler.to_matrix().col[0]),'camera_up_world':list(cam.rotation_euler.to_matrix().col[1]),'engine':engine,'authoritative_geometry_source':'actual saved raw or actual evaluated zero bind coordinates; no modeling','asset_edits_or_saves':0})
 dump('DORSAL_BIND_ZERO_MATCHED_RENDER_MANIFEST_R1.json',{'renders':manifest,'count':len(manifest),'matched_camera_lighting_material_scale_per_row':True,'only_display_meshes_created':True,'native_asset_saves':0,'Stage6_poses_run':[]})
 print('AUDIT_RENDER',name,flush=True)

for view,shade,direction in [('CLOSE','FLAT',human),('CLOSE','SOURCE_NATIVE',human),('GRAZING','SOURCE_NATIVE',human)]:
 for label in G['stages']:render(label,'DORSAL_'+view,shade,origin,direction,.028)
