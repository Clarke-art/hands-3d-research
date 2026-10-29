import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
from mathutils import Vector,Quaternion,Matrix
ns={'bpy':bpy,'math':math,'Vector':Vector,'Quaternion':Quaternion,'Matrix':Matrix,'MM':1000.}
provenance=reuse(S6/'stage6a/scripts/s6a_common.py',['reset_pose','set_joint_rotation','evaluate','pose_state','face_area'],ns)
methods=read(OUT/'MINIMUM_SAFETY_PROCEDURE_R1.json');floor=methods['automatic_gates']
cases=read(OUT/'AUTHORIZED_THREE_POSES_R1.json')['case_definitions']
lock=read(DESIGN/'PALMAR_ROOT_HUMAN_TARGET_LOCK_R1.json')['camera'];core=read(DESIGN/'PALMAR_ROOT_DEFECT_CORE_R1.json');normal=read(DESIGN/'PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json')
root_ids=sorted(set(core['visible_upper_box_hit_vertex_ids'])|set(range(3348,3364))|set(normal['vertex_ids']))
camera_jobs={};manifest=[];resets=[];safety={};coordinates={};native={}
(OUT/'renders').mkdir(exist_ok=True)
def state_zero(rig):
 return all(tuple(b.location)==(0,0,0) and tuple(b.scale)==(1,1,1) and b.rotation_mode=='QUATERNION' and abs(b.rotation_quaternion.angle)<1e-7 and b.matrix_basis==Matrix.Identity(4) for b in rig.pose.bones)
def native_payload(ob,rig):
 return {'coordinates':[list(v.co) for v in ob.data.vertices],'faces':[list(f.vertices) for f in ob.data.polygons],'edges':[list(e.vertices) for e in ob.data.edges],'groups':[g.name for g in ob.vertex_groups],'weights':[[[g.group,float(g.weight)] for g in v.groups] for v in ob.data.vertices],'mesh_world':[list(r) for r in ob.matrix_world],'rig_world':[list(r) for r in rig.matrix_world],'rest':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'matrix':[list(r) for r in b.matrix_local],'parent':b.parent.name if b.parent else None,'use_deform':b.use_deform} for b in rig.data.bones},'modifiers':[[m.name,m.type,m.object.name if getattr(m,'object',None) else None,m.show_viewport,m.show_render] for m in ob.modifiers]}
def make_display():
 sc=bpy.data.scenes.new('UNSAVED_MATCHED_VISUAL_REVIEW');sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1400;sc.render.resolution_y=1050;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
 sc.world=bpy.data.worlds.new('UNSAVED_REVIEW_WORLD');sc.world.color=(.15,.17,.20);sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
 sh=sc.display.shading;sh.light='STUDIO';sh.studiolight_rotate_z=.25;sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=False;sh.show_specular_highlight=True;sh.background_type='WORLD'
 cd=bpy.data.cameras.new('UNSAVED_MATCHED_CAMERA');cd.type='ORTHO';cd.clip_start=.001;cd.clip_end=5;cam=bpy.data.objects.new('UNSAVED_MATCHED_CAMERA',cd);sc.collection.objects.link(cam);sc.camera=cam
 clay=bpy.data.materials.new('UNSAVED_NEUTRAL_SOLID');clay.diffuse_color=(.66,.68,.71,1);nail=bpy.data.materials.new('UNSAVED_NAIL_SOLID');nail.diffuse_color=(.86,.88,.90,1)
 return sc,cam,cd,clay,nail
def frame(cid,view,V,cam,cd):
 key=(cid,view)
 if key not in camera_jobs:
  direction=Vector(lock['view_direction'])
  if view=='ALTERNATE':direction=(direction+Vector((.32,-.20,.50))).normalized()
  ids=list(range(len(V))) if view=='FULL_HAND' else root_ids
  rr=Vector((0,0,1)).cross(direction).normalized();up=direction.cross(rr).normalized();pts=[V[i] for i in ids];xx=[p.dot(rr) for p in pts];yy=[p.dot(up) for p in pts];zz=[p.dot(direction) for p in pts]
  center=rr*((min(xx)+max(xx))/2)+up*((min(yy)+max(yy))/2)+direction*((min(zz)+max(zz))/2)
  scale=max(max(xx)-min(xx),(max(yy)-min(yy))*1400/1050,.009)*(1.25 if view=='FULL_HAND' else 1.40)
  camera_jobs[key]={'center':list(center),'direction':list(direction),'ortho_scale_m':scale}
 job=camera_jobs[key];cam.location=Vector(job['center'])+Vector(job['direction'])*.7;cam.rotation_euler=(Vector(job['center'])-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=job['ortho_scale_m']
def render_all(asset,cid,V,F,material_indices,sc,cam,cd,clay,nail):
 me=bpy.data.meshes.new('UNSAVED_EVALUATED_DISPLAY');me.from_pydata(V,[],F);me.materials.append(clay);me.materials.append(nail)
 for f,mi in zip(me.polygons,material_indices):f.use_smooth=True;f.material_index=1 if mi==1 else 0
 me.update();ob=bpy.data.objects.new('UNSAVED_EVALUATED_DISPLAY',me);sc.collection.objects.link(ob)
 for view in ['FULL_HAND','ROOT_CLOSE','ALTERNATE','GRAZING']:
  frame(cid,view,V,cam,cd);sc.display.shading.studiolight_rotate_z=1.8 if view=='GRAZING' else .25
  fn=f'{cid}__{view}__{asset}.png';sc.render.filepath=str(OUT/'renders'/fn);bpy.ops.render.render(write_still=True,scene=sc.name)
  manifest.append({'pose':cid,'asset':asset,'view':view,'path':'renders/'+fn,'camera':camera_jobs[(cid,view)],'camera_matrix':[list(r) for r in cam.matrix_world],'studio_rotation_z':sc.display.shading.studiolight_rotate_z,'resolution':[1400,1050],'ordinary_solid':True,'smooth_display_only':True,'all_native_faces_present':True,'rendered_before_original_rig_reset':True,'source_geometry_or_materials_modified':False})
  dump('MATCHED_RENDER_MANIFEST_R1.json',{'renders':manifest,'only_three_distinct_poses':True,'matched_two_asset_camera_per_pose_view':True,'source_blend_saves':0})
 bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(me)
for asset,path in FILES.items():
 assert sha(path)==EXPECTED[asset]
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 ob=next(o for o in bpy.data.objects if o.type=='MESH' and len(o.data.vertices)==3416);rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];MW=ob.matrix_world.copy()
 start=native_payload(ob,rig);names={g.index:g.name for g in ob.vertex_groups};weights=[{names[g.group]:float(g.weight) for g in v.groups if g.weight>0} for v in ob.data.vertices]
 assert digest(weights)==WEIGHT_HASH and len(rig.data.bones)==21
 native[asset]={'source':ref(path),'weight_hash':digest(weights),'native_payload_hash_before':digest(start)}
 ns['reset_pose'](rig);bpy.context.view_layer.update();VB,F=ns['evaluate'](ob,MW);assert state_zero(rig)
 zero_raw=max((VB[i]-(<REDACTED_EMAIL>)).length*1000 for i,v in enumerate(ob.data.vertices));assert zero_raw<=floor['zero_mm']
 E=[list(e.vertices) for e in ob.data.edges];A0=[ns['face_area'](VB,f) for f in F];L0=[(VB[a]-VB[b]).length for a,b in E];mi=[f.material_index for f in ob.data.polygons]
 sc,cam,cd,clay,nail=make_display();safety[asset]={};coordinates[asset]={}
 for c in cases:
  cid=c['case_id'];ns['reset_pose'](rig);bpy.context.view_layer.update();Vz,Pz=ns['evaluate'](ob,MW);pre=max((a-b).length*1000 for a,b in zip(Vz,VB));assert state_zero(rig) and pre<=floor['zero_mm']
  ns['set_joint_rotation'](rig,c['bone'],c['applied_rotation_deg']);bpy.context.view_layer.update();V,P=ns['evaluate'](ob,MW)
  finite=sum(not math.isfinite(float(x)) for p in V for x in p);areas=[ns['face_area'](V,f) for f in P];lengths=[(V[a]-V[b]).length for a,b in E]
  collapsed=[i for i,a in enumerate(areas) if a<=floor['collapse_area_m2_le'] or a/A0[i]<=floor['collapse_ratio_le']];degenerate=[i for i,l in enumerate(lengths) if l<=floor['degenerate_edge_m_le']];severe=[i for i,l in enumerate(lengths) if L0[i]*1000>=floor['severe_bind_mm_ge'] and l/L0[i]>floor['severe_ratio_gt']]
  active=[b.name for b in rig.pose.bones if abs(b.rotation_quaternion.angle)>1e-7]
  row={'NaN_Inf_count':finite,'collapsed_face_count':len(collapsed),'degenerate_edge_count':len(degenerate),'obvious_severe_stretch_count':len(severe),'only_authorized_bone_rotated':active==['MIDDLE_MCP_R'],'active_bones':active,'topology_exact':P==F,'automatic_minimum_gate':'PASS' if not(finite or collapsed or degenerate or severe) and active==['MIDDLE_MCP_R'] and P==F else 'FAIL','visible_new_penetration_screen':'PENDING_MATCHED_SOLID_INSPECTION','neighbor_digit_gross_contamination':'PENDING_MATCHED_SOLID_INSPECTION'}
  safety[asset][cid]=row;coordinates[asset][cid]=[list(v) for v in V]
  render_all(asset,cid,V,P,mi,sc,cam,cd,clay,nail)
  ns['reset_pose'](rig);bpy.context.view_layer.update();Vr,Pr=ns['evaluate'](ob,MW);post=max((a-b).length*1000 for a,b in zip(Vr,VB));reset={'asset':asset,'pose':cid,'pre_zero_restore_mm':pre,'post_zero_restore_mm':post,'all21_channels_zero':state_zero(rig),'raw_zero_noise_mm':zero_raw,'status':'PASS' if post<=floor['zero_mm'] and state_zero(rig) and Pr==F else 'FAIL'};resets.append(reset)
  dump('ZERO_RESET_AUDIT_R1.json',{'status':'PASS' if all(r['status']=='PASS' for r in resets) else 'FAIL','rows':resets,'final_pose':'ZERO','procedure':'RESET ZERO -> apply localX -angle -> evaluate -> four matched renders -> RESET ZERO','blend_saves':0})
  dump('MINIMUM_MACHINE_SAFETY_AUDIT_R1.json',{'automatic_results':safety,'visual_obvious_penetration_gross_neighbor_screen_pending':True,'policy':'HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST','hidden_triangle_crossing_census':False,'normal_dot_or_compression_ratio_analysis':False})
  assert reset['status']=='PASS'
  print(asset,cid,'minimum automatic',row['automatic_minimum_gate'],'ZERO',reset['status'],flush=True)
  if asset=='REPAIRED_PALMAR' and row['automatic_minimum_gate']!='PASS':break
 assert native_payload(ob,rig)==start and sha(path)==EXPECTED[asset]
 native[asset]['native_payload_hash_after']=digest(native_payload(ob,rig));native[asset]['unchanged']=True
dump('POSED_COORDINATES_R1.json',{'positions_world_m':coordinates,'faces':[list(f) for f in F],'only_three_distinct_cases':CASES})
dump('IN_MEMORY_NO_ASSET_DRIFT_R1.json',{'status':'PASS','assets':native,'weights_rig_geometry_groups_modifiers_unchanged':True,'posed_blend_saves':0,'nonzero_pose_applications':sum(len(r) for r in coordinates.values()),'distinct_pose_count':3,'Stage6_Full42_runs':0,'solver_static_skin_R3_truecap_impact_runs':0,'helper_reuse':provenance})
print('THREE-POSE MATCHED EVIDENCE READY; ZERO restored; no saved source changes',flush=True)
