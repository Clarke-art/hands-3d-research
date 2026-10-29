import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,numpy as np
from mathutils import Vector,Matrix
assert read(OUT/'PALMAR_APPLICATION_STRUCTURE_AUDIT_R1.json')['status']=='PASS'
C=read(OUT/'PALMAR_APPLICATION_NATIVE_GEOMETRY_R1.json');G=read(PRIOR/'DIAGNOSTIC_RENDER_GEOMETRY_R1.json');B=read(OUT/'PALMAR_APPLICATION_BEFORE_SAVE_SNAPSHOT_R1.json');lock=read(DESIGN/'PALMAR_ROOT_HUMAN_TARGET_LOCK_R1.json');core=read(DESIGN/'PALMAR_ROOT_DEFECT_CORE_R1.json');normal=read(DESIGN/'PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json');NAT=B['source_snapshot']['protected']['mesh'];F=C['faces'];E=C['edges'];cfs=set(core['face_ids']);nfs=set(normal['face_ids']);ids=core['visible_upper_box_hit_vertex_ids'];P={'baseline_world_mm':C['source_world_mm'],'moved_vertex_ids':IDS}
def state(v):return {'vertices':v,'faces':F,'smooth':NAT['smooth_flags'],'material_indices':NAT['face_material_indices']}
states={'SOURCE_STAGE4C':state(C['source_world_mm']),'APPROVED_FORMAL_CANDIDATE':state(C['approved_candidate_world_mm']),'APPLIED_NEW_STAGE4C_REVISION':state(C['application_world_mm'])}
dump('PALMAR_APPLICATION_MATCHED_REVIEW_GEOMETRY_R1.json',{'states':states,'frame':G['frame'],'camera':lock['camera'],'faces':F,'edges':E,'core':core,'normal':normal,'coordinate_source':'fresh factory-clean native source / approved candidate / actual saved application reopen; no design renders or probe coordinate substitution','authority':{'source':ref(SOURCE),'approved_candidate':ref(CANDIDATE),'application':ref(ASSET)},'target_formula_runs':0,'ancestry_recompute_runs':0})
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1600;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.world=bpy.data.worlds.new('display world');sc.world.color=(.12,.14,.17);sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
sh=sc.display.shading;sh.light='STUDIO';sh.studiolight_rotate_z=.25;sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.;sh.curvature_valley_factor=.8;sh.background_type='WORLD';sh.show_specular_highlight=True
mat=[]
for name,col in [('plain',(.66,.68,.71,1)),('nail',(.85,.87,.89,1)),('wire',(.03,.05,.07,1)),('PRIMARY_DEFECT_ROI',(.99,.33,.10,1)),('EXCLUDED_NORMAL_ROI',(.13,.62,.82,1)),('ancestry closure',(.95,.73,.16,1))]:
 m=bpy.data.materials.new(name);m.diffuse_color=col;mat.append(m)
cd=bpy.data.cameras.new('display camera');cd.type='ORTHO';cd.clip_start=.001;cd.clip_end=5;cam=bpy.data.objects.new('display camera',cd);sc.collection.objects.link(cam);sc.camera=cam;ob=None;extras=[];records=[];tris={};REND=OUT/'renders';REND.mkdir(exist_ok=True)
def clear():
 global ob,extras
 for x in ([ob] if ob else [])+extras:
  me=x.data;bpy.data.objects.remove(x,do_unlink=True)
  if isinstance(me,bpy.types.Mesh):bpy.data.meshes.remove(me)
  elif isinstance(me,bpy.types.Curve):bpy.data.curves.remove(me)
 ob=None;extras=[]
def lines(segments,color=2,width=.00004):
 cu=bpy.data.curves.new('display overlay','CURVE');cu.dimensions='3D';cu.bevel_depth=width;cu.bevel_resolution=0
 for seg in segments:
  sp=cu.splines.new('POLY');sp.points.add(len(seg)-1)
  for q,p in zip(sp.points,seg):q.co=(*p,1)
 x=bpy.data.objects.new('display overlay',cu);sc.collection.objects.link(x);cu.materials.append(mat[color]);extras.append(x)
def framing(view):
 if view=='HUMAN_CAMERA':cam.matrix_world=Matrix(lock['camera']['camera_world_matrix']);cd.ortho_scale=lock['camera']['orthographic_width_m'];return
 direction=Vector(lock['camera']['view_direction']);direction=(direction+Vector((.32,-.20,.5))).normalized() if view=='ALTERNATE' else direction
 rr=Vector((0,0,1)).cross(direction).normalized();up=direction.cross(rr).normalized();points=[Vector([x/1000 for x in states[st]['vertices'][i]]) for st in ['SOURCE_STAGE4C','APPLIED_NEW_STAGE4C_REVISION'] for i in ids];xx=[p.dot(rr) for p in points];yy=[p.dot(up) for p in points];zz=[p.dot(direction) for p in points]
 center=rr*((min(xx)+max(xx))/2)+up*((min(yy)+max(yy))/2)+direction*((min(zz)+max(zz))/2);cam.location=center+direction*.7;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=max(max(xx)-min(xx),(max(yy)-min(yy))*1600/1100,.009)*1.65
def render(state,kind,view):
 global ob
 clear();ss=states[state];V=[Vector([x/1000 for x in p]) for p in ss['vertices']];ff=ss['faces'];me=bpy.data.meshes.new('static frozen coordinates '+state);me.from_pydata(V,[],ff);me.update();ob=bpy.data.objects.new('display-only '+state,me);sc.collection.objects.link(ob)
 for m in mat:me.materials.append(m)
 for i,p in enumerate(me.polygons):p.use_smooth=ss['smooth'][i] if kind=='FLAT_SOURCE_NATIVE' else True;p.material_index=1 if ss['material_indices'][i]==1 else 0
 me.calc_loop_triangles();tris[state]=[{'face_id':t.polygon_index,'vertex_ids':list(t.vertices)} for t in me.loop_triangles]
 sh.studiolight_rotate_z=1.8 if kind=='GRAZING' else .25
 if kind in ['ROI_LABEL','WIRE'] and state!='OFFICIAL_L1_RSSF_DISPLAY':
  if kind=='ROI_LABEL':
   for i in cfs:me.polygons[i].material_index=3
   for i in nfs:me.polygons[i].material_index=4
   lines([[Vector([x/1000 for x in P['baseline_world_mm'][i]]),V[i]] for i in P['moved_vertex_ids']],5,width=.00008)
  else:
   edge={tuple(sorted((a,b))) for fi in cfs|nfs for a,b in zip(F[fi],F[fi][1:]+F[fi][:1])};lines([[V[a],V[b]] for a,b in edge])
 framing(view);fn=f'{state}__{view}__{kind}.png';sc.render.filepath=str(REND/fn);bpy.ops.render.render(write_still=True)
 assert [list(p.vertices) for p in me.polygons]==ff
 records.append({'path':'renders/'+fn,'state':state,'style':kind,'view':view,'pose':'STATIC_RAW_CURRENT_RSSF_ONLY','camera_matrix':[list(r) for r in cam.matrix_world],'orthographic_width_m':cd.ortho_scale,'resolution':[1600,1100],'studio_rotation_z':sh.studiolight_rotate_z,'same_lighting_for_compared_states':True,'all_native_faces_present':True,'qualified_asset_loaded':False,'pose_setters':0,'application_visual_equivalence_only':True})
 dump('PALMAR_APPLICATION_MATCHED_RENDER_MANIFEST_R1.json',{'records':records,'static_structure_PASS_before_preview':True,'actual_saved_application_coordinates':True,'Full42_runs':0,'Stage6_runs':0,'pose_smoke_evaluations_in_renderer':0,'deformation_qualification_runs':0,'production_blend_saves':0})
 print('RENDER',fn,flush=True)
for view in ['HUMAN_CAMERA','CLOSE','ALTERNATE']:
 for st in ['SOURCE_STAGE4C','APPROVED_FORMAL_CANDIDATE','APPLIED_NEW_STAGE4C_REVISION']:
  for kind in ['SOLID','GRAZING','FLAT_SOURCE_NATIVE','WIRE','ROI_LABEL']:render(st,kind,view)
dump('PALMAR_APPLICATION_NATIVE_RENDER_TRIANGLES_R1.json',tris)
print('FRESH APPLICATION STATIC RENDERS',len(records),'no pose/bind',flush=True)
