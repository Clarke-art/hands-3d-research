import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy, math
from mathutils import Vector, Matrix
G=read(OUT/'DIAGNOSTIC_RENDER_GEOMETRY_R1.json');F=G['faces'];E=G['edges'];roi=G['roi'];ids=roi['vertices'];fs=set(roi['visible_hit_faces'])
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1600;sc.render.resolution_y=1100;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.world=bpy.data.worlds.new('diagnostic display world');sc.world.color=(.12,.14,.17)
sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.view_settings.exposure=0
sh=sc.display.shading;sh.light='STUDIO';sh.studiolight_rotate_z=.25;sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.;sh.curvature_valley_factor=.8;sh.background_type='WORLD';sh.show_specular_highlight=True
mat=[]
for name,col in [('plain',(.66,.68,.71,1)),('nail',(.85,.87,.89,1)),('wire',(.06,.07,.09,1)),('face normal',(.99,.36,.1,1)),('vertex normal',(.1,.65,.95,1)),('pair A',(.94,.31,.12,1)),('pair B',(.18,.56,.96,1)),('white silhouette',(.95,.95,.95,1))]:
 m=bpy.data.materials.new(name);m.diffuse_color=col;mat.append(m)
camera_data=bpy.data.cameras.new('display camera');camera_data.type='ORTHO';camera_data.clip_start=.001;camera_data.clip_end=5;camera=bpy.data.objects.new('display camera',camera_data);sc.collection.objects.link(camera);sc.camera=camera
REND=OUT/'renders';REND.mkdir(exist_ok=True);records=[];triangles={};ob=None;extras=[]
def clear():
 global ob,extras
 for x in ([ob] if ob else [])+extras:
  data=x.data;bpy.data.objects.remove(x,do_unlink=True)
  if isinstance(data,bpy.types.Mesh):bpy.data.meshes.remove(data)
  elif isinstance(data,bpy.types.Curve):bpy.data.curves.remove(data)
 ob=None;extras=[]
def clone(label):
 global ob
 clear();source=G['source_states'].get(label);v=source['positions_mm'] if source else G['states'][label];faces=source['faces'] if source else F
 me=bpy.data.meshes.new('native topology display '+label);me.from_pydata([[x/1000 for x in p] for p in v],[],faces);me.update();ob=bpy.data.objects.new('display '+label,me);sc.collection.objects.link(ob)
 for m in mat:me.materials.append(m)
 for i,p in enumerate(me.polygons):p.material_index=0 if source else (1 if G['native_material_indices'][i] else 0)
 me.calc_loop_triangles();triangles[label]=[{'face_id':t.polygon_index,'vertex_ids':list(t.vertices)} for t in me.loop_triangles]
 assert [list(p.vertices) for p in me.polygons]==faces
 return [Vector([x/1000 for x in p]) for p in v],source
basecam=G['camera_source']['camera']
def camset(angle):
 if angle=='MATCHED_CANDIDATE':camera.matrix_world=Matrix(basecam['camera_world_matrix']);camera_data.ortho_scale=basecam['orthographic_width_m']
 else:
  center=Vector([x/1000 for x in G['frame']['origin_world_mm']]);direction=Vector(basecam['view_direction']);direction=(direction+Vector((.3,-.2,.42))).normalized()
  camera.location=center+direction*.7;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.ortho_scale=.052
def linepaths(segments,index,width=.00004):
 curve=bpy.data.curves.new('diagnostic overlay','CURVE');curve.dimensions='3D';curve.bevel_depth=width;curve.bevel_resolution=0
 for seg in segments:
  s=curve.splines.new('POLY');s.points.add(len(seg)-1)
  for q,p in zip(s.points,seg):q.co=(*p,1)
 x=bpy.data.objects.new('display overlay',curve);sc.collection.objects.link(x);curve.materials.append(mat[index]);extras.append(x)
def render(label,kind,angle='MATCHED_CANDIDATE'):
 V,source=clone(label);camset(angle);me=ob.data;native=source['smooth_flags'] if source else G['source_native_smooth'];rfs=source['roi_faces'] if source else list(fs);rids=source['roi_vertices'] if source else ids
 for i,p in enumerate(me.polygons):p.use_smooth=True if kind in ['SMOOTH','WIRE','GRAZING','FACE_NORMALS','VERTEX_NORMALS','FORENSIC'] else native[i] if kind=='SOURCE_NATIVE' else False
 sh.light='FLAT' if kind=='SILHOUETTE' else 'STUDIO';sh.show_cavity=kind!='SILHOUETTE';sh.show_shadows=kind!='SILHOUETTE';sh.show_specular_highlight=kind!='SILHOUETTE';sh.studiolight_rotate_z=1.8 if kind=='GRAZING' else .25
 if kind=='SILHOUETTE':
  for p in me.polygons:p.material_index=7
 elif kind=='WIRE':
  edge=set(tuple(sorted((a,b))) for i in rfs for a,b in zip(list(me.polygons[i].vertices),list(me.polygons[i].vertices)[1:]+list(me.polygons[i].vertices)[:1]));linepaths([[V[a],V[b]] for a,b in edge],2)
 elif kind=='FACE_NORMALS':
  linepaths([[p.center,p.center+p.normal*.0015] for i in rfs for p in [me.polygons[i]]],3)
 elif kind=='VERTEX_NORMALS':linepaths([[V[i],V[i]+me.vertices[i].normal*.0015] for i in rids],4)
 elif kind=='FORENSIC':
  for pair in G['all_current9']:
   if pair['case_id']==label:
    for i,mi in zip(pair['face_ids'],[5,6]):me.polygons[i].material_index=mi
  linepaths([[V[a],V[b]] for ei in roi['edges'] for a,b in [E[ei]]],2)
 fn=f'{label}__{angle}__{kind}.png';sc.render.filepath=str(REND/fn);bpy.ops.render.render(write_still=True)
 # Display-copy setters only; no qualified assets in this renderer.
 original=source['positions_mm'] if source else G['states'][label]
 maxerr=max((v.co-Vector([x/1000 for x in original[i]])).length for i,v in enumerate(me.vertices))
 assert maxerr<2e-7
 records.append({'file':'renders/'+fn,'state':label,'kind':kind,'angle':angle,'resolution':[1600,1100],'camera_matrix_world':[list(r) for r in camera.matrix_world],'orthographic_width_m':camera_data.ortho_scale,'all_native_faces_present':True,'native_topology_exact':True,'display_float32_max_coordinate_error_m':maxerr,'SOURCE_NATIVE_flags_used':kind=='SOURCE_NATIVE','smooth_display_variant':kind in ['SMOOTH','WIRE','GRAZING','FACE_NORMALS','VERTEX_NORMALS','FORENSIC'],'lighting':{'engine':'BLENDER_WORKBENCH','light':sh.light,'studio_rotation_z':sh.studiolight_rotate_z,'cavity':sh.show_cavity,'view_transform':'Standard'},'qualified_asset_loaded':False,'qualified_asset_writes':0})
 dump('DIAGNOSTIC_RENDER_MANIFEST_R1.json',{'renders':records,'display_only':True,'production_opens':0,'pose_applications':0,'blend_saves':0,'source_coordinates':'DIAGNOSTIC_RENDER_GEOMETRY_R1.json','original_source_native_is_flat':True})
 print('RENDER',fn,flush=True)
for angle in ['MATCHED_CANDIDATE','SECOND_ANGLE']:
 for state in ['CURRENT_R2_RAW','CURRENT_R2_ZERO','IDX_MCP_30']:
  for kind in ['SOURCE_NATIVE','SMOOTH','WIRE','FACE_NORMALS','VERTEX_NORMALS','GRAZING','SILHOUETTE']:render(state,kind,angle)
for state in ['OFFICIAL_L1','STAGE2_L1','STAGE4A_R2_BASE','STAGE4A_R2','STAGE4B_RSSF','PRE_DONOR_STAGE4C_RAW','NEW_STAGE4C_RAW','IDX_MCP_15','TH_IP_15','IDX_MCP_30_PRE_DONOR']:
 for kind in ['SOURCE_NATIVE','SMOOTH']:render(state,kind)
for state in CASES:render(state,'FORENSIC')
dump('NATIVE_DISPLAY_LOOP_TRIANGLES_R1.json',triangles)
print('Diagnostic render complete',len(records),flush=True)
