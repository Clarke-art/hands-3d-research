import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
from mathutils import Vector
DIAG=ROOT/'audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1'
R=read(DIAG/'DORSAL_MCP_DENT_ROI_R1.json');G=read(DIAG/'DENT_RENDER_GEOMETRY_R1.json');D=read(OUT/'CANDIDATE_EVALUATED_COORDINATES_R1.json')['states']
F=read(DIAG/'LINEAGE_RAW_READONLY_EXTRACTION.json')['topology']['faces'];E=read(DIAG/'LINEAGE_RAW_READONLY_EXTRACTION.json')['topology']['edges']
origin=Vector(G['frame']['origin_world_mm'])/1000;n=Vector(G['frame']['outward']);x=Vector(G['frame']['x']);y=Vector(G['frame']['y']);vd=Vector(R['camera']['direction']);wholecenter=Vector(R['camera']['center_world_m'])
bpy.ops.wm.open_mainfile(filepath=str(CAND),load_ui=False,use_scripts=False)
template=bpy.data.objects['Hand  - Realistic'].data
sc=bpy.data.scenes.new('DESIGN_ONLY_NOT_PRODUCTION_REVIEW');bpy.context.window.scene=sc
sc.render.image_settings.file_format='PNG';sc.render.resolution_percentage=100;sc.render.film_transparent=False
world=bpy.data.worlds.new('design comparison world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.14,.17,1);world.node_tree.nodes['Background'].inputs[1].default_value=.25;sc.world=world
sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=False;sc.display.shading.background_type='WORLD'
if hasattr(sc.eevee,'taa_render_samples'):sc.eevee.taa_render_samples=32
cd=bpy.data.cameras.new('matched comparison');cd.type='ORTHO';cd.clip_start=.001;cd.clip_end=4
cam=bpy.data.objects.new('matched comparison',cd);sc.collection.objects.link(cam);sc.camera=cam
ld=bpy.data.lights.new('fixed production-like light','SUN');ld.energy=2;ld.angle=.08
light=bpy.data.objects.new('fixed light',ld);sc.collection.objects.link(light)
wm=bpy.data.materials.new('diagnostic wire');wm.diffuse_color=(.08,.2,.3,1)
sm=bpy.data.materials.new('silhouette');sm.diffuse_color=(.03,.03,.03,1)
made=[];manifest=[]
sil_only='--silhouette-only' in sys.argv
boundary_only='--boundary-only' in sys.argv
if sil_only:manifest=[p for p in read(OUT/'CANDIDATE_RENDER_MANIFEST_R1.json')['renders'] if p['mode']!='SILHOUETTE']
if boundary_only:manifest=[p for p in read(OUT/'CANDIDATE_RENDER_MANIFEST_R1.json')['renders'] if p['mode']!='BOUNDARY_FOLD']
def clear():
 for o in made:
  data=o.data;bpy.data.objects.remove(o,do_unlink=True)
  if isinstance(data,bpy.types.Mesh):bpy.data.meshes.remove(data)
  elif isinstance(data,bpy.types.Curve):bpy.data.curves.remove(data)
 made.clear()
def orient(center,direction,scale,size):
 cam.location=center+direction.normalized()*.4;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale
 sc.render.resolution_x=size[0];sc.render.resolution_y=size[1]
def line(a,b):
 cu=bpy.data.curves.new('native edge','CURVE');cu.dimensions='3D';cu.bevel_depth=.000025;cu.bevel_resolution=1
 sp=cu.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
 ob=bpy.data.objects.new('native edge',cu);sc.collection.objects.link(ob);cu.materials.append(wm);made.append(ob)
for label,states in D.items():
 for pose in ['RSSF_RAW','BIND','IDX_MCP_15','IDX_MCP_30','IDX_MCP_45']:
  modes=['CLOSE'] if pose=='RSSF_RAW' else ['HUMAN_CAMERA','CLOSE'] if pose!='BIND' else ['HUMAN_CAMERA','DORSAL_WHOLE','CLOSE','GRAZING','WIRE','SILHOUETTE','ANGLE_2','BOUNDARY_FOLD']
  for mode in modes:
   if sil_only and mode!='SILHOUETTE':continue
   if boundary_only and mode!='BOUNDARY_FOLD':continue
   clear();v=[Vector(p)/1000 for p in states[pose]];me=template.copy()
   for vert,p in zip(me.vertices,v):vert.co=p
   me.update();ob=bpy.data.objects.new('DESIGN_ONLY_'+label,me);sc.collection.objects.link(ob);made.append(ob)
   # Natural evaluated face normals recompute from moved vertices; no smoothing/normal flags change.
   orient(origin,vd,.023,(900,900));sc.render.engine='BLENDER_EEVEE';light.rotation_euler=(-(n+x*.3+y*.4)).to_track_quat('-Z','Y').to_euler()
   sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_shadows=True;sc.display.shading.background_type='WORLD'
   if mode=='HUMAN_CAMERA':orient(wholecenter,vd,R['camera']['ortho_scale_m'],(640,800))
   if mode=='DORSAL_WHOLE':orient(wholecenter,(n+vd).normalized(),.26,(900,1100))
   if mode=='GRAZING':light.rotation_euler=(-(x+n*.08)).to_track_quat('-Z','Y').to_euler()
   if mode=='ANGLE_2':orient(origin,(n-x*.7+y*.2).normalized(),.030,(900,900))
   if mode=='BOUNDARY_FOLD':
    a,b=E[6675];bc=(Vector(D['CURRENT']['BIND'][a])+Vector(D['CURRENT']['BIND'][b]))/2000
    orient(bc,(n-x*.2+y*.1).normalized(),.016,(900,900))
   if mode=='WIRE':
    sc.render.engine='BLENDER_WORKBENCH'
    for ei in R['edges']:
     a,b=E[ei];line(v[a],v[b])
   if mode=='SILHOUETTE':
    orient(origin,(x+n*.15+y*.15).normalized(),.035,(900,900));sc.render.engine='BLENDER_WORKBENCH';me.materials.clear();me.materials.append(sm)
    for p in me.polygons:p.material_index=0
    sc.display.shading.light='FLAT';sc.display.shading.color_type='SINGLE';sc.display.shading.single_color=(.02,.02,.02);sc.display.shading.background_type='VIEWPORT';sc.display.shading.background_color=(1,1,1);sc.display.shading.show_shadows=False
   name=f'{label}_{pose}_{mode}.png';(OUT/'renders').mkdir(exist_ok=True);sc.render.filepath=str(OUT/'renders'/name);bpy.ops.render.render(write_still=True)
   manifest.append({'path':'renders/'+name,'label':label,'pose':pose,'mode':mode,'camera_center_world_m':list(wholecenter if mode in ['HUMAN_CAMERA','DORSAL_WHOLE'] else origin),'camera_position_world_m':list(cam.location),'camera_rotation_euler':list(cam.rotation_euler),'orthographic_scale_m':cd.ortho_scale,'resolution':[sc.render.resolution_x,sc.render.resolution_y],'ordinary_native_production_flat_flags':True,'normal_material_edit_as_repair':False,'production_materials_UV_preserved':mode!='SILHOUETTE','DESIGN_ONLY_NOT_PRODUCTION':True})
   print('DESIGN_RENDER',name,flush=True)
dump('CANDIDATE_RENDER_MANIFEST_R1.json',{'renders':manifest,'count':len(manifest),'production_blend_save_count':0,'matched_camera_scale_material_light_pose_across_labels':True,'RSSF_geometry_source':'FrozenStage4C RSSF / vertex-position derived copy','candidate_bind_source':'Temporary inherited current R2 rig and weights evaluated in memory'})
print('DESIGN RENDER COMPLETE',flush=True)
