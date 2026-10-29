"""Matched diagnostic views of measured surfaces; only disposable display meshes.
No candidate saves, production normal/material/mesh edits, or pose execution.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,math
from mathutils import Vector,Matrix
L=read(OUT/'LINEAGE_RAW_READONLY_EXTRACTION.json');R=read(OUT/'DORSAL_MCP_DENT_ROI_R1.json');G=read(OUT/'DENT_RENDER_GEOMETRY_R1.json')
F=L['topology']['faces'];edges=L['topology']['edges'];frame=G['frame']
origin=Vector(frame['origin_world_mm'])/1000;n=Vector(frame['outward']);x=Vector(frame['x']);y=Vector(frame['y']);DORS=Vector(R['camera']['direction'])
labels=['STAGE4A_R2_FROZEN','STAGE4B_RSSF_R2','STAGE4C_R2_RAW','CORRECTED_STAGE5A_ZERO','R2_ARMATURE_OFF','R2_BIND_ZERO','IDX_MCP_15']
OUT.joinpath('renders').mkdir(exist_ok=True)
# Source material nodes/UV/smoothing are preserved in a copied mesh datablock.
bpy.ops.wm.open_mainfile(filepath=str(CAND),load_ui=False,use_scripts=False)
source=bpy.data.objects['Hand  - Realistic'];template=source.data
sc=bpy.data.scenes.new('DENT_READONLY_DIAGNOSTIC');bpy.context.window.scene=sc
sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
world=bpy.data.worlds.new('diagnostic world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.14,.17,1);world.node_tree.nodes['Background'].inputs[1].default_value=.25;sc.world=world
sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=False;sc.display.shading.background_type='WORLD'
if hasattr(sc.eevee,'taa_render_samples'):sc.eevee.taa_render_samples=32
cd=bpy.data.cameras.new('matched camera');cd.type='ORTHO';cd.ortho_scale=.023
cam=bpy.data.objects.new('matched camera',cd);sc.collection.objects.link(cam);sc.camera=cam
cd.clip_start=.001;cd.clip_end=4
lightdata=bpy.data.lights.new('matched area sun','SUN');lightdata.energy=2.;lightdata.angle=.08
light=bpy.data.objects.new('matched area sun',lightdata);sc.collection.objects.link(light)
def orient(vd):
 vd=vd.normalized();cam.location=origin+vd*.4;cam.rotation_euler=(origin-cam.location).to_track_quat('-Z','Y').to_euler()
def light_direction(vd):light.rotation_euler=(-vd).to_track_quat('-Z','Y').to_euler()
def color(name,col):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);return m
wiremat=color('diagnostic wire',(.08,.2,.3));normalmat=color('diagnostic normal',(.08,.63,.22));roimat=color('diagnostic ROI core',(.85,.42,.1));silmat=color('diagnostic silhouette',(.03,.03,.03))
made=[];manifest=[]
def clear():
 for obj in made:
  data=obj.data;bpy.data.objects.remove(obj,do_unlink=True)
  if isinstance(data,bpy.types.Mesh):bpy.data.meshes.remove(data)
  elif isinstance(data,bpy.types.Curve):bpy.data.curves.remove(data)
 made.clear()
def line(points,name,mat,radius=.000035):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=radius;cu.bevel_resolution=1
 sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 obj=bpy.data.objects.new(name,cu);sc.collection.objects.link(obj);cu.materials.append(mat);made.append(obj)
def display(v,mode):
 me=template.copy()
 for vert,p in zip(me.vertices,v):vert.co=p
 me.update();obj=bpy.data.objects.new('measured '+mode,me);sc.collection.objects.link(obj);made.append(obj)
 if mode=='FLAT':
  for p in me.polygons:p.use_smooth=False
 elif mode=='SMOOTH_RESET_COUNTERFACTUAL':
  for p in me.polygons:p.use_smooth=True
 elif mode=='ROI_SELECTION':
  me.materials.append(roimat);idx=len(me.materials)-1
  for fi in R['core_faces']:me.polygons[fi].material_index=idx
 if mode in ['WIRE','ROI_SELECTION']:
  for ei in R['edges']:
   a,b=edges[ei];line([v[a],v[b]],'actual native edge '+str(ei),wiremat)
 if mode=='NORMALS':
  for fi in R['faces']:
   p=me.polygons[fi];cen=sum((v[i] for i in F[fi]),Vector())/len(F[fi]);normal=p.normal.copy()
   line([cen,cen+normal*.0015],'actual normal '+str(fi),normalmat)
 if mode=='SILHOUETTE':
  me.materials.clear();me.materials.append(silmat)
  for p in me.polygons:p.material_index=0
 return me
for label in labels:
 v=[Vector(p)/1000 for p in G['stages'][label]['registered_world_mm']]
 for mode in ['CURRENT','FLAT','SMOOTH_RESET_COUNTERFACTUAL','WIRE','NORMALS','GRAZING','SILHOUETTE','ANGLE_2','ANGLE_3']:
  clear();me=display(v,mode);orient(DORS)
  if mode in ['CURRENT','FLAT','SMOOTH_RESET_COUNTERFACTUAL','GRAZING']:
   sc.render.engine='BLENDER_EEVEE';light_direction((n+x*.3+y*.4).normalized())
   if mode=='GRAZING':light_direction((x+n*.08).normalized())
  else:sc.render.engine='BLENDER_WORKBENCH'
  if mode=='ANGLE_2':orient((n-x*.7+y*.2).normalized())
  if mode in ['ANGLE_3','SILHOUETTE']:orient((x+n*.15+y*.15).normalized())
  name=label+'_'+mode+'.png';sc.render.filepath=str(OUT/'renders'/name);bpy.ops.render.render(write_still=True)
  manifest.append({'path':'renders/'+name,'stage':label,'mode':mode,'camera_scale_m':cd.ortho_scale,'camera_direction':list((cam.location-origin).normalized()),'same_measured_geometry_except_shading':True,'production_material_nodes_and_UV_copied_unchanged':mode in ['CURRENT','FLAT','SMOOTH_RESET_COUNTERFACTUAL','GRAZING'],'source_custom_normals':False,'source_ROI_smooth_face_count':sum(L['stages']['R2_PRODUCTION']['source_face_use_smooth'][fi] for fi in R['faces']),'geometry_registration':'Existing measured coordinates; rigid diagnostic display transform only','counterfactual_not_repair_candidate':mode=='SMOOTH_RESET_COUNTERFACTUAL'})
  print('DENT_RENDER',name,flush=True)
clear();v=[Vector(p)/1000 for p in G['stages']['R2_BIND_ZERO']['registered_world_mm']];display(v,'ROI_SELECTION');orient(DORS);sc.render.engine='BLENDER_WORKBENCH';sc.render.filepath=str(OUT/'renders/ROI_SELECTION_CLOSEUP.png');bpy.ops.render.render(write_still=True)
dump('DENT_RENDER_MANIFEST_R1.json',{'renders':manifest,'render_count':len(manifest)+1,'ROI_selection':'renders/ROI_SELECTION_CLOSEUP.png','production_save_count':0,'Stage6A_pose_execution_count':0,'rigid_registration_removes_gross_pose_orientation_only':True,'source_production_ROI_flat_shading':True})
print('DENT RENDERING COMPLETE',len(manifest)+1,flush=True)
