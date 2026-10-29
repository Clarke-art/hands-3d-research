import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,numpy as np
from mathutils import Vector,Matrix
assert read(OUT/'PALMAR_ROOT_TRANSFER_STRUCTURE_AUDIT_R1.json')['status']=='PASS'
P=read(OUT/'TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.json');G=read(PRIOR/'DIAGNOSTIC_RENDER_GEOMETRY_R1.json');S=read(SOURCE/'RAW_SOURCE_GEOMETRY.json')['stages'];J=np.array(read(SOURCE/'HISTORICAL_RSSF_COORDINATE_CORRESPONDENCE.json')['per_vertex_linear_part']);don=np.array(S['OFFICIAL_L1']['canonical_world_m']);rest=np.array(S['STAGE4A_R2']['canonical_world_m']);old=np.array(S['STAGE4C_R2']['canonical_world_m']);dv=(old[:len(don)]+np.einsum('ijk,ik->ij',J[:len(don)],don-rest[:len(don)]))*1000
core=read(OUT/'PALMAR_ROOT_DEFECT_CORE_R1.json');normal=read(OUT/'PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json');lock=read(OUT/'PALMAR_ROOT_HUMAN_TARGET_LOCK_R1.json');scope=read(OUT/'PALMAR_ROOT_TRANSFER_SCOPE_R1.json');F=P['faces'];E=P['edges'];NAT=read(ROOT/'production_spec/stage5_production_rig/geometry_propagation_after_donor_transfer_r1/R2_REOPENED_NATIVE_PAYLOAD_R1.json')['protected']['mesh'];cfs=set(core['face_ids']);nfs=set(normal['face_ids']);ids=core['visible_upper_box_hit_vertex_ids']
states={'CURRENT_RAW':{'vertices':P['baseline_world_mm'],'faces':F,'smooth':NAT['smooth_flags'],'material_indices':NAT['face_material_indices']},'TRANSFER_PROBE':{'vertices':P['world_mm'],'faces':F,'smooth':NAT['smooth_flags'],'material_indices':NAT['face_material_indices']},'OFFICIAL_L1_RSSF_DISPLAY':{'vertices':dv.tolist(),'faces':S['OFFICIAL_L1']['faces'],'smooth':S['OFFICIAL_L1']['smooth'],'material_indices':S['OFFICIAL_L1']['materials']}}
for key in ['STAGE4A_R2_BASE','STAGE4A_R2','STAGE4B_RSSF']:
 if key in G['source_states']:
  z=G['source_states'][key];states[key]={'vertices':z['positions_mm'],'faces':z['faces'],'smooth':z['smooth_flags'],'material_indices':[0]*len(z['faces'])}
 else:states[key]={'vertices':G['states'][key],'faces':F,'smooth':NAT['smooth_flags'],'material_indices':NAT['face_material_indices']}
states['SOURCE_PRE_ENGINEERING_L1']=G['source_states']['OFFICIAL_L1']|{'vertices':G['source_states']['OFFICIAL_L1']['positions_mm'],'smooth':G['source_states']['OFFICIAL_L1']['smooth_flags'],'material_indices':[0]*len(G['source_states']['OFFICIAL_L1']['faces'])}
dump('MATCHED_REVIEW_GEOMETRY_R1.json',{'states':states,'frame':G['frame'],'camera':lock['camera'],'faces':F,'edges':E,'core':core,'normal':normal,'source_display_mapping':'Official native L1 vertices + existing frozen per-original-vertex RSSF linear mapping. This is a display-only static coordinate mapping, no pose application, no evaluated donor modifier edit. Engineering inserted vertices use source ancestry in probe; donor retains native 3300 vertices/3298 faces.','donor_native_shape_file':S['OFFICIAL_L1']['input'],'temporary_save_raw_geometry':ref(OUT/'TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.json')})
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
 rr=Vector((0,0,1)).cross(direction).normalized();up=direction.cross(rr).normalized();points=[Vector([x/1000 for x in states[st]['vertices'][i]]) for st in ['CURRENT_RAW','TRANSFER_PROBE'] for i in ids];xx=[p.dot(rr) for p in points];yy=[p.dot(up) for p in points];zz=[p.dot(direction) for p in points]
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
 records.append({'path':'renders/'+fn,'state':state,'style':kind,'view':view,'pose':'STATIC_RAW_RSSF_BAKED_ONLY' if state in ['CURRENT_RAW','TRANSFER_PROBE','OFFICIAL_L1_RSSF_DISPLAY'] else 'historical native snapshot / fixed diagnostic registration; not common RSSF pose','camera_matrix':[list(r) for r in cam.matrix_world],'orthographic_width_m':cd.ortho_scale,'resolution':[1600,1100],'studio_rotation_z':sh.studiolight_rotate_z,'same_lighting_for_compared_states':True,'all_native_faces_present':True,'qualified_asset_loaded':False,'pose_setters':0,'diagnostic_only':True})
 dump('MATCHED_RENDER_MANIFEST_R1.json',{'records':records,'static_structure_PASS_before_preview':True,'source_donor_mapping':'frozen historical RSSF display coordinate mapping, no new pose solution','Full42_runs':0,'Stage6_runs':0,'pose_smoke_runs':0,'deformation_qualification_runs':0,'production_blend_saves':0})
 print('RENDER',fn,flush=True)
for view in ['HUMAN_CAMERA','CLOSE','ALTERNATE']:
 for st in ['CURRENT_RAW','OFFICIAL_L1_RSSF_DISPLAY','TRANSFER_PROBE']:
  for kind in ['SOLID','GRAZING','FLAT_SOURCE_NATIVE']:render(st,kind,view)
 for st in ['CURRENT_RAW','TRANSFER_PROBE']:
  for kind in ['WIRE','ROI_LABEL']:render(st,kind,view)
for st in ['SOURCE_PRE_ENGINEERING_L1','STAGE4A_R2_BASE','STAGE4A_R2','STAGE4B_RSSF']:render(st,'SOLID','HUMAN_CAMERA')
dump('NATIVE_RENDER_LOOP_TRIANGLES_R1.json',tris)
print('STATIC RENDER DONE',len(records),flush=True)
