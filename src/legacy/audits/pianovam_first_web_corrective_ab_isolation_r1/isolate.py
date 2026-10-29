import sys,json,hashlib,math,ast,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
import bpy
from mathutils import Vector
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PREV=ROOT/'audits/pianovam_single_sample_right_hand_retarget_r1'
SOURCE=PREV/'RIGHT_HAND_PIANO_MOTION_TEST_R1.blend';BASE=ROOT/'production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend'
SOURCE_SHA='43e8e2854aa24c74053830118ea6d939fc56af4efb450bf0098a7bd99838dae8';BASE_SHA='4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2'
KEY='FIRST_WEB_OPPOSITION_CREASE_R1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
assert sha(SOURCE)==SOURCE_SHA and sha(BASE)==BASE_SHA
spec=importlib.util.spec_from_file_location('readonly_helpers',ROOT/'audits/official_l1_first_web_targeted_deformation_fix_r1/common.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.old.lib.OUT=OUT
node=next(n for n in ast.parse((BASE.parent/'freeze_baseline.py').read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name=='shape_payload');exec(compile(ast.Module(body=[node],type_ignores=[]),'read_only_shape_payload','exec'))
def open_readonly(p):
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
 return bpy.data.objects['RIGHT_HAND_OFFICIAL_L1_PRODUCT_MESH'],bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
def action_payload(action):
 return {'name':action.name,'slots':[{'id':s.identifier,'target_id_type':s.target_id_type} for s in action.slots], 'layers':[{'name':layer.name,'strips':[{'type':strip.type,'bags':[{'slot_handle':bag.slot_handle,'curves':[{'path':fc.data_path,'index':fc.array_index,'mute':fc.mute,'keys':[[list(k.co),k.interpolation,list(k.handle_left),list(k.handle_right)] for k in fc.keyframe_points]} for fc in bag.fcurves]} for bag in strip.channelbags]} for strip in layer.strips]} for layer in action.layers]}
def pose_payload(rig):return {p.name:{'matrix':[list(r) for r in p.matrix],'basis':[list(r) for r in p.matrix_basis],'quaternion':list(p.rotation_quaternion),'location':list(p.location),'scale':list(p.scale),'mode':p.rotation_mode} for p in rig.pose.bones}
ob,rig=open_readonly(BASE);native=m.product_payload(ob,rig);protected_shape=shape_payload(ob);materials=[m.material_payload(mat) for mat in ob.data.materials if mat];baseline_zero=m.state_zero(rig);assert baseline_zero and all(k.value==0 for k in ob.data.shape_keys.key_blocks[1:])
ob,rig=open_readonly(SOURCE);scene=bpy.context.scene;action=rig.animation_data.action
assert action.name=='PIANOVAM_PHYSICAL_RIGHT_SMOOTHED_R1'
assert m.product_payload(ob,rig)==native and shape_payload(ob)==protected_shape
actions_before={a.name:digest(action_payload(a)) for a in bpy.data.actions};native_sha=digest(native);shape_sha=digest(protected_shape)
sk=ob.data.shape_keys;key=sk.key_blocks[KEY];fc=next(f for f in sk.animation_data.drivers if f.data_path==f'key_blocks["{KEY}"].value');driver_mute=fc.mute;key_mute=key.mute
assert not driver_mute and not key_mute
selection_rows=[(16,'DEFECT','MILD','窄而清楚的虎口凹口'),(31,'DEFECT','MODERATE','夹皱及三角边缘可见'),(76,'DEFECT','SEVERE','虎口有明显三角形内陷缺口'),(106,'DEFECT','MODERATE','虎口边缘出现裂口状折线'),(121,'DEFECT','SEVERE','多折线缺口，在原 review poster 中清楚可见'),(126,'DEFECT','SEVERE','明显内陷且呈尖角'),(130,'DEFECT','MOST_SEVERE','大而尖锐的三角形缺口'),(205,'DEFECT','MOST_SEVERE','虎口裂口状尖角最显著的一组帧之一'),(61,'RELATIVE_LOW_DEFECT_CONTROL','LOW_DEFECT_REFERENCE','相对平顺对照；仍有小折痕，不宣称完全正常'),(181,'RELATIVE_LOW_DEFECT_CONTROL','LOW_DEFECT_REFERENCE','相对轻微对照；不是另一个 motion 或 ZERO')]
rows=[]
for f,role,severity,note in selection_rows:rows.append({'frame':f,'frame_domain':'Blender scene 30fps, 1-based','review_video_frame_zero_based':f-1,'source_frame':690+2*(f-1),'time_sec':11.5+(f-1)/30,'review_time_sec':(f-1)/30,'role':role,'human_visible_severity':severity,'visual_note':note,'severity_authority':'Agent ordinary-solid visual selection from existing review frames; no numerical severity score and no new Human judgment'})
selection={'SOURCE_RETARGET':{'path':SOURCE.relative_to(ROOT).as_posix(),'sha256':SOURCE_SHA},'MOTION_WINDOW':'11.5-18.5 sec','action':action.name,'DEFECT_FRAME_COUNT':8,'control_frame_count':2,'selection_source':'Existing smoothed_motion_frames and review.mp4 only; chosen visually before inspecting driver values','normal_control_available':False,'normal_control_note':'Two comparatively mild source-motion frames supplied; do not label either as entirely defect-free.','frames':rows}
dump('FIRST_WEB_DEFECT_FRAME_SELECTION_R1.json',selection)
request=Path('<USER_HOME>/.codex/attachments/261d5aff-3519-456a-a87d-d6424dc95290/已粘贴的文本.txt')
dump('PRIOR_RETARGET_HUMAN_REJECTION_BIND_R1.json',{'authority':'Direct current user-authored instruction','request_path':str(request),'request_sha256':sha(request),'source_retarg_sha256':SOURCE_SHA,'HUMAN_VERDICT':'REJECT','reasons':['FIRST_WEB_VISIBLE_DEFECT','UNNATURAL_FINGERTIP_TURNING'],'this_phase_scope':'Only FIRST_WEB_VISIBLE_DEFECT; fingertips not investigated or repaired','previous_machine_pending_records_preserved':True})
affected=read(ROOT/'audits/official_l1_first_web_targeted_deformation_fix_r1/CORRECTIVE_KEY_R1.json')['changed_vertex_ids']
driver_rows=[];matching=[];render_records=[];cameras={}
for row in rows:
 f=row['frame'];scene.frame_set(f);bpy.context.view_layer.update();assert rig.animation_data.action==action and fc.mute==driver_mute and key.mute==key_mute
 pose_a=pose_payload(rig);value=float(key.value);inputs={};targets=[]
 for var in fc.driver.variables:
  assert var.type=='TRANSFORMS' and len(var.targets)==1
  t=var.targets[0];assert t.id==rig and t.transform_type=='ROT_X' and t.transform_space=='LOCAL_SPACE' and t.rotation_mode=='XYZ'
  x=float(rig.pose.bones[t.bone_target].matrix_basis.to_euler('XYZ').x);inputs[var.name]=x;targets.append({'variable':var.name,'bone':t.bone_target,'actual_input_rad':x,'actual_input_deg':math.degrees(x),'transform_type':t.transform_type,'transform_space':t.transform_space,'rotation_mode':t.rotation_mode})
 expression_value=eval(fc.driver.expression,{'__builtins__':{},'min':min,'max':max},inputs)
 assert abs(expression_value-value)<2e-6
 VA,FA=m.evaluate(ob,ob.matrix_world)
 center=sum((VA[i] for i in affected),Vector())/len(affected);wrist=<REDACTED_EMAIL>['WRIST_R'].head;down=(wrist-center).normalized()
 cams={'PALMAR_THENAR_CLOSE':{'center':list(center+down*.014),'direction':[-.38183954,-.92405248,.0180442],'ortho_scale_m':.110,'resolution':[960,880]},'FIRST_WEB_OBLIQUE':{'center':list(center),'direction':list(Vector((.20,-.94,.28)).normalized()),'ortho_scale_m':.072,'resolution':[960,880]}}
 cameras[str(f)]=cams
 renderer=m.Renderer(cams,'renders');renderer.sc.display.shading.shadow_intensity=0
 renderer.draw('CURRENT',f'F{f:03}',VA,FA,list(cams))
 # The selected defect and control values are already zero. Direct temporary value override
 # suffices; do not mute, replace, remove, or edit the driver, and do not touch key contents.
 key.value=0.0;bpy.context.view_layer.update();VB,FB=m.evaluate(ob,ob.matrix_world);off_value=float(key.value)
 assert off_value==0.0,'Driver reasserted nonzero; do not silently produce invalid B'
 assert pose_payload(rig)==pose_a and scene.frame_current==f and FB==FA
 assert m.product_payload(ob,rig)==native and shape_payload(ob)==protected_shape
 assert fc.mute==driver_mute and key.mute==key_mute
 renderer.draw('CORRECTIVE_OFF',f'F{f:03}',VB,FB,list(cams));render_records.extend(renderer.records);renderer.dispose()
 key.value=value;scene.frame_set(f);bpy.context.view_layer.update();assert abs(key.value-value)<1e-7 and pose_payload(rig)==pose_a
 max_delta=max((a-b).length for a,b in zip(VA,VB))
 matching.append({'frame':f,'same_scene_frame':True,'same_action':True,'same_all_bone_pose_matrices_and_channels':True,'same_camera_per_view':True,'same_mesh_basis_weights_rig_uv_material_payload':True,'same_shape_content_driver_expression_variables_mute':True,'same_native_face_list':True,'A_current_value':value,'B_forced_value':off_value,'temporary_override':'Existing key.value=0.0 only. All selected A values naturally already 0; no driver/key mute needed.','max_A_B_evaluated_vertex_delta_m':max_delta,'nonzero_A_B_vertex_count':sum((a-b).length!=0 for a,b in zip(VA,VB)),'current_value_restored_after_B':True})
 driver_rows.append({'frame':f,'source_time_sec':row['time_sec'],'role':row['role'],'corrective_current_value':value,'corrective_forced_zero_value':off_value,'driver_expression_value_recomputed_from_actual_inputs':expression_value,'expression_agreement_abs':abs(expression_value-value),'driver_inputs':targets,'INDEX_MCP_R_referenced_by_driver':False})
 assert actions_before=={a.name:digest(action_payload(a)) for a in bpy.data.actions}
assert m.product_payload(ob,rig)==native and shape_payload(ob)==protected_shape
assert [m.material_payload(mat) for mat in ob.data.materials if mat]==materials
assert sha(BASE)==BASE_SHA and sha(SOURCE)==SOURCE_SHA
dump('FIRST_WEB_CORRECTIVE_DRIVER_VALUES_R1.json',{'corrective_name':KEY,'driver_type':fc.driver.type,'driver_expression':fc.driver.expression,'driver_variables':[{'name':v.name,'bone':v.targets[0].bone_target,'transform_type':v.targets[0].transform_type,'transform_space':v.targets[0].transform_space,'rotation_mode':v.targets[0].rotation_mode} for v in fc.driver.variables],'INDEX_MCP_R_referenced':False,'frames':driver_rows,'defect_min':min(r['corrective_current_value'] for r in driver_rows if r['role']=='DEFECT'),'defect_max':max(r['corrective_current_value'] for r in driver_rows if r['role']=='DEFECT'),'driver_logic_modified':False})
dump('MATCHED_AB_VERIFICATION_R1.json',{'source_sha_before':SOURCE_SHA,'source_sha_after':sha(SOURCE),'baseline_sha_before':BASE_SHA,'baseline_sha_after':sha(BASE),'baseline_saved_ZERO_verified':baseline_zero,'native_payload_digest':native_sha,'shape_driver_content_digest':shape_sha,'actions_digest_before':actions_before,'actions_digest_after':{a.name:digest(action_payload(a)) for a in bpy.data.actions},'no_blend_saved':True,'no_mesh_basis_weight_rest_joint_roll_shape_driver_mapping_smoothing_edits':True,'all_temporary_overrides_restored':True,'frames':matching,'cameras':cameras,'render_records':render_records,'only_allowed_runtime_difference':'Existing first-web key scalar value temporarily forced to zero; here A was already zero, so evaluated A and B are identical.','no_stress_audit_run':True})
print('AB_EVIDENCE_COMPLETE',len(rows),'DEFECT8','VALUES',[r['corrective_current_value'] for r in driver_rows],flush=True)
