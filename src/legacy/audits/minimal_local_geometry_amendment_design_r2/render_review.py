import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
from mathutils import Vector
DIAG=ROOT/'audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1'
R=read(DIAG/'DORSAL_MCP_DENT_ROI_R1.json');G=read(DIAG/'DENT_RENDER_GEOMETRY_R1.json')
payload=read(OUT/'REVIEW_COORDINATES_R2.json');D=payload['states'];E=read(DIAG/'LINEAGE_RAW_READONLY_EXTRACTION.json')['topology']['edges']
origin=Vector(G['frame']['origin_world_mm'])/1000;n=Vector(G['frame']['outward']);x=Vector(G['frame']['x']);y=Vector(G['frame']['y']);vd=Vector(R['camera']['direction']);wholecenter=Vector(R['camera']['center_world_m'])
TEMP.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(CAND),load_ui=False,use_scripts=False)
template=bpy.data.objects['Hand  - Realistic'].data
sc=bpy.data.scenes.new('DESIGN_R2_ONLY_REVIEW');bpy.context.window.scene=sc
sc.render.image_settings.file_format='PNG';sc.render.resolution_percentage=100;sc.render.film_transparent=False
world=bpy.data.worlds.new('R2 fixed review world');world.use_nodes=True
bg=world.node_tree.nodes.new('ShaderNodeBackground');bg.inputs[0].default_value=(.12,.14,.17,1);bg.inputs[1].default_value=.25
wo=world.node_tree.nodes.new('ShaderNodeOutputWorld');world.node_tree.links.new(bg.outputs[0],wo.inputs['Surface']);sc.world=world
sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=False;sc.display.shading.background_type='WORLD'
cd=bpy.data.cameras.new('R2 matched');cd.type='ORTHO';cd.clip_start=.001;cd.clip_end=4
cam=bpy.data.objects.new('R2 matched',cd);sc.collection.objects.link(cam);sc.camera=cam
ld=bpy.data.lights.new('R2 fixed production-like light','SUN');ld.energy=2;ld.angle=.08
light=bpy.data.objects.new('R2 fixed light',ld);sc.collection.objects.link(light)
wm=bpy.data.materials.new('R2 wire');wm.diffuse_color=(.04,.18,.26,1)
made=[];manifest=[]
def clear():
 for ob in made:
  data=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
  if isinstance(data,bpy.types.Mesh):bpy.data.meshes.remove(data)
  elif isinstance(data,bpy.types.Curve):bpy.data.curves.remove(data)
 made.clear()
def orient(center,direction,scale,size=(640,640)):
 cam.location=center+direction.normalized()*.4;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale;sc.render.resolution_x=size[0];sc.render.resolution_y=size[1]
def wire(v,ids):
 cu=bpy.data.curves.new('native wire','CURVE');cu.dimensions='3D';cu.bevel_depth=.000024;cu.bevel_resolution=1
 for ei in ids:
  a,b=E[ei];sp=cu.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*v[a],1);sp.points[1].co=(*v[b],1)
 ob=bpy.data.objects.new('native wire',cu);sc.collection.objects.link(ob);cu.materials.append(wm);made.append(ob)
for label,poses in D.items():
 for pose,coords in poses.items():
  modes=['CLOSE','HUMAN_CAMERA','DORSAL_WHOLE','GRAZING','FLAT','WIRE','SILHOUETTE','ANGLE_2','SIDE_2','BOUNDARY_6675','BOUNDARY_6602','FAILURE_BOUNDARY'] if pose in ['BIND','RSSF_RAW'] else ['CLOSE','HUMAN_CAMERA','GRAZING']
  if pose=='RSSF_RAW' and 'BIND' in poses:continue
  for mode in modes:
   clear();v=[Vector(p)/1000 for p in coords];me=template.copy()
   for vert,p in zip(me.vertices,v):vert.co=p
   me.update();ob=bpy.data.objects.new('R2_DESIGN_ONLY_'+label,me);sc.collection.objects.link(ob);made.append(ob)
   orient(origin,vd,.030);sc.render.engine='BLENDER_EEVEE';light.rotation_euler=(-(n+x*.3+y*.4)).to_track_quat('-Z','Y').to_euler()
   sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_shadows=True;sc.display.shading.background_type='WORLD'
   if mode=='HUMAN_CAMERA':orient(wholecenter,vd,R['camera']['ortho_scale_m'],(600,750))
   if mode=='DORSAL_WHOLE':orient(wholecenter,(n+vd).normalized(),.26,(600,750))
   if mode=='GRAZING':light.rotation_euler=(-(x+n*.08)).to_track_quat('-Z','Y').to_euler()
   if mode=='FLAT':sc.render.engine='BLENDER_WORKBENCH'
   if mode=='ANGLE_2':orient(origin,(n-x*.7+y*.2).normalized(),.045)
   if mode=='SIDE_2':orient(origin,(x+n*.35-y*.3).normalized(),.045)
   if mode.startswith('BOUNDARY_'):
    ei=int(mode.split('_')[1]);a,b=E[ei];bc=(Vector(D['CURRENT']['RSSF_RAW'][a])+Vector(D['CURRENT']['RSSF_RAW'][b]))/2000
    orient(bc,(n-x*.2+y*.1).normalized(),.020)
   if mode=='FAILURE_BOUNDARY':
    ei=payload.get('failure_edge_id',6675);a,b=E[ei];bc=(Vector(D['CURRENT']['RSSF_RAW'][a])+Vector(D['CURRENT']['RSSF_RAW'][b]))/2000;orient(bc,(n-x*.2+y*.1).normalized(),.025)
   if mode=='WIRE':sc.render.engine='BLENDER_WORKBENCH';wire(v,payload['comparison_edge_ids'])
   if mode=='SILHOUETTE':
    orient(origin,(x+n*.15+y*.15).normalized(),.045);sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='FLAT';sc.display.shading.color_type='SINGLE';sc.display.shading.single_color=(.02,.02,.02);sc.display.shading.background_type='VIEWPORT';sc.display.shading.background_color=(1,1,1);sc.display.shading.show_shadows=False
   name=f'{label}_{pose}_{mode}.png';sc.render.filepath=str(TEMP/name);bpy.ops.render.render(write_still=True)
   manifest.append({'path':(TEMP/name).relative_to(ROOT).as_posix(),'label':label,'pose':pose,'mode':mode,'camera_position':list(cam.location),'camera_rotation':list(cam.rotation_euler),'camera_scale':cd.ortho_scale,'camera_center':list(cam.location-(cam.rotation_euler.to_quaternion()@Vector((0,0,1)))*.4),'engine':sc.render.engine,'single_frame_is_temporary':True,'mesh_flags_UV_materials_preserved':True,'DESIGN_ONLY':True})
   print('REVIEW_FRAME',name,flush=True)
dump('R2_RENDER_MANIFEST.json',{'renders':manifest,'production_blend_saves':0,'matched_across_labels':True,'normal_or_material_used_as_repair':False})
