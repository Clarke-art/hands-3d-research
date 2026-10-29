import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
from mathutils import Vector
G=read(OUT/'MATCHED_ZERO_BIND_REVIEW_GEOMETRY_R1.json');frame=G['frame'];origin=Vector(frame['origin_world_mm'])/1000;n=Vector(frame['outward']);x=Vector(frame['x']);y=Vector(frame['y']);human=Vector(G['camera']['direction'])
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
if overview_only:manifest=read(OUT/'MATCHED_RENDER_MANIFEST_R1.json')['renders']
def render(label,view,shade,target,direction,scale,size=(640,640),engine='BLENDER_EEVEE'):
 global active
 if active:
  me=active.data;bpy.data.objects.remove(active,do_unlink=True);bpy.data.meshes.remove(me)
 s=G['stages'][label];me=bpy.data.meshes.new('DISPLAY_MEASURED_GEOMETRY');me.from_pydata(s['world_m'],[],G['faces']);me.materials.append(mat)
 for p,sm in zip(me.polygons,G['smooth']):p.use_smooth=sm if shade=='SOURCE_NATIVE' else False
 me.update();active=bpy.data.objects.new('UNSAVED_AUDIT_DISPLAY',me);sc.collection.objects.link(active)
 cam.location=Vector(target)+Vector(direction)*.55;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale
 light.rotation_euler=(-(x+n*.08) if view=='GRAZING' else -(n+x*.3+y*.4)).to_track_quat('-Z','Y').to_euler()
 sc.render.engine=engine;sc.render.resolution_x=size[0];sc.render.resolution_y=size[1]
 name=f'{label}_{view}_{shade}.png';sc.render.filepath=str(OUT/'renders'/name);bpy.ops.render.render(write_still=True)
 manifest[:]=[r for r in manifest if r['path']!='renders/'+name]
 manifest.append({'path':'renders/'+name,'label':label,'view':view,'shade':shade,'target_world_m':list(target),'direction':list(direction),'orthographic_scale_m':scale,'resolution':list(size),'camera_right_world':list(cam.rotation_euler.to_matrix().col[0]),'camera_up_world':list(cam.rotation_euler.to_matrix().col[1]),'engine':engine,'authoritative_geometry_source':'actual saved raw or actual evaluated zero bind coordinates; no modeling','asset_edits_or_saves':0})
 dump('MATCHED_RENDER_MANIFEST_R1.json',{'renders':manifest,'count':len(manifest),'matched_camera_lighting_material_scale_per_row':True,'only_display_meshes_created':True,'native_asset_saves':0,'Stage6_poses_run':[]})
 print('AUDIT_RENDER',name,flush=True)
if not overview_only:
 for view,shade,direction in [('CLOSE','FLAT',human),('CLOSE','SOURCE_NATIVE',human),('GRAZING','SOURCE_NATIVE',human),('SIDE','FLAT',(x+n*.15+y*.15).normalized())]:
  for label in G['stages']:render(label,view,shade,origin,direction,.028)
bones=G['bones'];ring=Vector(bones['RING_MCP_R']['head_world_m'])
rot=(-n).to_track_quat('-Z','Y').to_matrix();right,up=rot.col[0],rot.col[1];points=[Vector(v) for v in G['stages']['R2_RAW']['world_m']]
lo=[min(p.dot(a) for p in points) for a in (right,up)];hi=[max(p.dot(a) for p in points) for a in (right,up)];center=Vector(G['camera']['center_world_m'])
center+=right*((lo[0]+hi[0])/2-center.dot(right))+up*((lo[1]+hi[1])/2-center.dot(up))
sc.render.resolution_x=800;sc.render.resolution_y=1000;cd.ortho_scale=1
fr=cd.view_frame(scene=sc);fw=max(v.x for v in fr)-min(v.x for v in fr);fh=max(v.y for v in fr)-min(v.y for v in fr)
scale=max((hi[0]-lo[0])/fw,(hi[1]-lo[1])/fh)*1.13
render('R2_RAW','JOINT_OVERVIEW','SOURCE_NATIVE',center,n,scale,(800,1000),'BLENDER_WORKBENCH')
render('R2_RAW','TIP_OVERVIEW','SOURCE_NATIVE',center,n,scale,(800,1000),'BLENDER_WORKBENCH')
if overview_only:sys.exit(0)
render('R2_RAW','ROI_JOINTS','FLAT',(origin+ring)/2,human,.075,(800,800),'BLENDER_WORKBENCH')
G['stages']['OLD_RAW']={'world_m':read(OUT/'CLEAN_REOPEN_NATIVE_PAYLOADS_R1.json')['OLD_CORRECTED']['coordinates_world_m']}
for label in ('OLD_RAW','R2_RAW'):render(label,'RING_MARGIN','FLAT',ring,human,.045,(720,720),'BLENDER_WORKBENCH')
render('R2_RAW','CORRECTED_THUMB_TIP','SOURCE_NATIVE',Vector(bones['THUMB_TIP_R']['head_world_m']),human,.040,(720,720),'BLENDER_WORKBENCH')
