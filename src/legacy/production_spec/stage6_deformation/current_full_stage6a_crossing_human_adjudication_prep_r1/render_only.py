"""Render-only evidence from frozen fresh coordinates. No production blend opens,
pose operations, armatures, modifiers, depsgraph coordinate evaluation or classifiers.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,math
from mathutils import Vector
assert read(OUT/'CURRENT_FULL_STAGE6A_HUMAN_REVIEW_INPUT_HASHES_R1.json')['status']=='PASS'
G=read(FRESH/'POSED_COORDINATES_R1.json');F=G['faces'];E=G['edges'];rows=read(OUT/'LOCKED_CURRENT9_ROWS_R1.json')['rows'];DM=read(FRESH/'LOCAL_PATCH_AND_MEASUREMENT_DOMAINS_R1.json');native=read(CAND.parent/'R2_REOPENED_NATIVE_PAYLOAD_R1.json')['protected']['mesh']
scene=bpy.context.scene
for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
sh=scene.display.shading;sh.light='STUDIO';sh.studiolight_rotate_z=.25;sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.;sh.curvature_valley_factor=.8;sh.background_type='WORLD';sh.show_specular_highlight=True
scene.world.color=(.12,.14,.17);scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0
materials=[]
for name,c in [('neutral product surface',(.66,.68,.71,1)),('native nail surface',(.85,.87,.89,1)),('forensic face A',(.94,.31,.12,1)),('forensic face B',(.18,.56,.96,1)),('stored exact segment witness',(.15,.96,.35,1))]:
 m=bpy.data.materials.new(name);m.diffuse_color=c;materials.append(m)
nailfaces={fi for r in DM['nail_material_components'] for fi in r['face_ids']}
camdata=bpy.data.cameras.new('render-only camera');camdata.type='ORTHO';cam=bpy.data.objects.new('render-only camera',camdata);scene.collection.objects.link(cam);scene.camera=cam;camdata.clip_start=.001;camdata.clip_end=5
REND=OUT/'renders';REND.mkdir(exist_ok=True);renders=[];proofs=[];main=None;isolated=None;markers=[]
def clone(cid):
 global main
 if main is not None:
  me=main.data;bpy.data.objects.remove(main,do_unlink=True);bpy.data.meshes.remove(me)
 V=G['positions_world_m'][cid];me=bpy.data.meshes.new('frozen fresh coordinates '+cid);me.from_pydata(V,[],F);me.update();main=bpy.data.objects.new('display-only '+cid,me);scene.collection.objects.link(main)
 for m in materials:me.materials.append(m)
 for fi,p in enumerate(me.polygons):p.use_smooth=True;p.material_index=1 if fi in nailfaces else 0
 # Shading changes neither positions nor native face cycles. These are display copies only.
 check={'case_id':cid,'all3416_positions_exact':all(list(v.co)==V[i] for i,v in enumerate(me.vertices)),'all3414_face_cycles_exact':[list(p.vertices) for p in me.polygons]==F,'identity_display_object_transform':list(main.location)==[0.,0.,0.] and list(main.scale)==[1.,1.,1.],'armature_objects':sum(o.type=='ARMATURE' for o in scene.objects),'mesh_modifiers':len(main.modifiers),'shape_keys':me.shape_keys is not None,'source_payload':ref(FRESH/'POSED_COORDINATES_R1.json'),'source_case_coordinate_digest':digest(V),'native_scene_opened':False,'pose_applications':0,'coordinate_evaluations':0}
 assert check['all3416_positions_exact'] and check['all3414_face_cycles_exact'] and check['armature_objects']==check['mesh_modifiers']==0 and not check['shape_keys'];proofs.append(check)
 return [Vector(v) for v in V]
def framing(V,ids,direction):
 d=Vector(direction).normalized();r=Vector((0,0,1)).cross(d).normalized();u=d.cross(r).normalized();ps=[V[i] for i in ids];x=[p.dot(r) for p in ps];y=[p.dot(u) for p in ps];z=[p.dot(d) for p in ps];center=r*((min(x)+max(x))/2)+u*((min(y)+max(y))/2)+d*((min(z)+max(z))/2)
 w=max(max(x)-min(x),.006);h=max(max(y)-min(y),.006);aspect=scene.render.resolution_x/scene.render.resolution_y;scale=max(w*1.25,h*1.25*aspect)
 camdata.ortho_scale=scale;cam.location=center+d*.7;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();return {'center_world_m':list(center),'view_direction':list(d),'orthographic_width_m':scale,'camera_world_matrix':[list(r) for r in cam.matrix_world]}
def draw(cid,name,V,ids,direction,kind='PLAIN_PRODUCT',pair=None):
 global isolated
 main.hide_render=False
 for fi,p in enumerate(main.data.polygons):p.material_index=1 if fi in nailfaces else 0
 for o in markers:o.hide_render=True
 if isolated:isolated.hide_render=True
 if pair and kind.startswith('FORENSIC'):
  a,b=pair['face_ids'];main.data.polygons[a].material_index=2;main.data.polygons[b].material_index=3
  if 'ISOLATED' in kind:
   main.hide_render=True
   if isolated:
    me=isolated.data;bpy.data.objects.remove(isolated,do_unlink=True);bpy.data.meshes.remove(me)
   me=bpy.data.meshes.new('two frozen forensic faces');me.from_pydata([list(v) for v in V],[],[F[a],F[b]]);me.update();isolated=bpy.data.objects.new('forensic pair only',me);scene.collection.objects.link(isolated)
   for m in materials:me.materials.append(m)
   me.polygons[0].material_index=2;me.polygons[1].material_index=3
  if 'SEGMENT' in kind:
   points=pair['current_metrics']['pts']
   for pt in points:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.00009,location=pt);o=bpy.context.object;o.data.materials.append(materials[4]);markers.append(o)
   if len(points)>1:
    curve=bpy.data.curves.new('stored segment witness','CURVE');curve.dimensions='3D';curve.bevel_depth=.000045;curve.bevel_resolution=2;spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
    for q,p in zip(spline.points,points):q.co=(*p,1)
    o=bpy.data.objects.new('stored exact segment witness',curve);scene.collection.objects.link(o);curve.materials.append(materials[4]);markers.append(o)
 elif pair and kind!='PLAIN_PRODUCT':raise AssertionError('Unknown evidence kind')
 camera=framing(V,ids,direction);fn=name+'.png';scene.render.filepath=str(REND/fn);bpy.ops.render.render(write_still=True)
 camera['camera_world_matrix']=[list(row) for row in cam.matrix_world]
 # Positions are verified again after every render; no in-memory pose/skinning exists.
 exact=all(list(v.co)==G['positions_world_m'][cid][i] for i,v in enumerate(main.data.vertices));assert exact
 renders.append({'file':'renders/'+fn,'source_case':cid,'pair_id':pair['pair_id'] if pair else None,'kind':kind,'name':name,'source_posed_coordinate_payload':ref(FRESH/'POSED_COORDINATES_R1.json'),'source_case_coordinate_digest':digest(G['positions_world_m'][cid]),'camera':camera,'lighting':{'renderer':'BLENDER_WORKBENCH','light':'STUDIO','studio_rotation_z':.25,'exposure':0,'view_transform':'Standard','look':'None','cavity_ridge':1.,'cavity_valley':.8},'resolution':[1600,1100],'all_native_coordinates_exact_after_render':exact,'plain_all3414_faces_present':kind=='PLAIN_PRODUCT' and not main.hide_render,'plain_colored_overlay':False if kind=='PLAIN_PRODUCT' else None,'plain_crossing_markers':False if kind=='PLAIN_PRODUCT' else None,'isolated_supplement_not_product_view':'ISOLATED' in kind,'native_smooth_display_normals_only':True,'production_geometry_write':False,'pose_application':False})
 dump('RENDER_ONLY_VISUAL_MANIFEST_R1.json',{'renders':renders,'display_coordinate_proofs':proofs,'production_blend_opens':0,'pose_applications':0,'qualified_asset_depsgraph_evaluations':0,'crossing_classifier_calls':0,'edge_strain_calls':0,'render_only':True})
 print('RENDER_ONLY',fn,flush=True)
DORS=Vector((.631289124,.775318801,-.0188387)).normalized()
for cid in ['IDX_MCP_15','IDX_MCP_30','TH_IP_15']:
 V=clone(cid);casepairs=[p for p in rows if p['case_id']==cid];case=read(FRESH/'FULL_STAGE6A_MACHINE_EVIDENCE_R1.json')['cases'][cid];ids=sorted(set(case['local_patch']['vertex_ids'])|{v for p in casepairs for v in p['vertex_ids']})
 draw(cid,cid+'__FULL_HAND_SOLID',V,list(range(len(V))),DORS)
 draw(cid,cid+'__LOCAL_PRIMARY',V,ids,DORS)
 draw(cid,cid+'__LOCAL_ALTERNATE',V,ids,-DORS)
 draw(cid,cid+'__LOCAL_OBLIQUE',V,ids,(DORS+Vector((-.35,.25,.55))).normalized())
 for pair in casepairs:
  a,b=pair['face_ids'];focus=pair['vertex_ids'];norm=(V[F[a][1]]-V[F[a][0]]).cross(V[F[a][2]]-V[F[a][0]]).normalized();front=(norm+DORS*.55).normalized();side=(Vector(front).cross(Vector((0,0,1)))+front*.3).normalized();key=pair['pair_id']+'__'+cid
  draw(cid,key+'__PRODUCT_CONTEXT',V,focus,front,pair=pair)
  draw(cid,key+'__PRODUCT_ALTERNATE',V,focus,side,pair=pair)
  draw(cid,key+'__COLORED_CONTEXT',V,focus,front,'FORENSIC_COLORED_CONTEXT',pair)
  draw(cid,key+'__ISOLATED_PAIR',V,focus,front,'FORENSIC_ISOLATED_PAIR',pair)
  draw(cid,key+'__EXACT_POINTS_SEGMENT',V,focus,front,'FORENSIC_ISOLATED_SEGMENT',pair)
print('RENDER-ONLY COMPLETE;57 PNGs;production load0/pose0/classifier0',flush=True)
