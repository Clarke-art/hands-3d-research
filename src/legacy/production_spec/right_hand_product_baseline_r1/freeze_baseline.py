import sys,importlib.util,json,hashlib,math
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
FIX=ROOT/'audits/official_l1_first_web_targeted_deformation_fix_r1'
spec=importlib.util.spec_from_file_location('approved_fix_helpers',FIX/'common.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.old.lib.OUT=OUT
ASSET=OUT/'RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
status=read(FIX/'OFFICIAL_L1_FIRST_WEB_TARGETED_DEFORMATION_FIX_R1_STATUS.json')
source=ROOT/status['candidate']['path'];source_sha=status['candidate']['sha256']
assert sha(source)==source_sha
assert not ASSET.exists(),'Refuse to overwrite an existing frozen baseline'
manifest=read(FIX/'FINAL_OUTPUT_MANIFEST_R1.json');assert manifest['candidate']==status['candidate']
verified=[]
for f in manifest['files']:
    path=FIX/f['path'];assert sha(path)==f['sha256'],str(path)
    verified.append({'path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':f['sha256']})
request=Path('<USER_HOME>/.codex/attachments/a677fbaa-adba-4976-a198-b43965ac51c6/已粘贴的文本.txt')
approval={'phase':'OFFICIAL_L1_FIRST_WEB_TARGETED_DEFORMATION_FIX_R1','HUMAN_APPROVED':'YES','VERDICT':'HUMAN_APPROVED','VISIBLE_PRODUCT_BLOCKER_COUNT':0,'NEW_VISIBLE_DEFECT_COUNT':0,'authority':'Direct user-authored instruction in the current chat, supplied via pasted request attachment','request_path':str(request),'request_sha256':sha(request),'source_candidate':status['candidate'],'approved_case_ids':status['authorized_case_ids'],'approved_cases':{c:'HUMAN_ACCEPTED' for c in status['authorized_case_ids']},'review_evidence_matches_candidate':True,'verified_evidence_file_count':len(verified),'historical_preliminary_status_preserved':True,'supersedes_human_pending_in':str((FIX/'OFFICIAL_L1_FIRST_WEB_TARGETED_DEFORMATION_FIX_R1_STATUS.json').relative_to(ROOT)).replace('\\','/')}
write('SOURCE_HUMAN_APPROVAL_BIND_R1.json',approval)
def shape_payload(ob):
    sk=ob.data.shape_keys
    return {'relative':sk.use_relative,'keys':[{'name':k.name,'relative_key':k.relative_key.name,'interpolation':k.interpolation,'slider_min':k.slider_min,'slider_max':k.slider_max,'vertex_group':k.vertex_group,'mute':k.mute,'coords':[list(v.co) for v in k.data]} for k in sk.key_blocks],
        'drivers':[{'path':d.data_path,'index':d.array_index,'type':d.driver.type,'expression':d.driver.expression,'variables':[{'name':v.name,'type':v.type,'targets':[{'id':t.id.name if t.id else None,'bone':t.bone_target,'transform_type':t.transform_type,'transform_space':t.transform_space,'rotation_mode':t.rotation_mode} for t in v.targets]} for v in d.driver.variables]} for d in sk.animation_data.drivers]}
ob,rig=m.open_file(source)
native=m.product_payload(ob,rig);shape=shape_payload(ob);materials=[m.material_payload(mat) for mat in ob.data.materials if mat]
assert len(rig.data.bones)==21 and len(ob.data.vertices)==3300
assert m.state_zero(rig) and all(k.value==0 for k in ob.data.shape_keys.key_blocks[1:])
assert len(shape['keys'])==2 and len(shape['drivers'])==1
V0,F=m.evaluate(ob,ob.matrix_world)
ob['DESIGN_ONLY']=False;ob['PRODUCTION_PROMOTION']='HUMAN_APPROVED_PRODUCT_BASELINE_FROZEN'
ob['PRODUCT_BASELINE_STATUS']='HUMAN_APPROVED_FROZEN'
ob['PRODUCT_BASELINE_SOURCE_SHA256']=source_sha
scene=m.bpy.context.scene
scene['PHASE']='RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1'
scene['HUMAN_APPROVAL_PENDING']=False;scene['HUMAN_APPROVED']=True
scene['RIGHT_HAND_PRODUCT_BASELINE']='HUMAN_APPROVED_FROZEN'
scene['PRODUCT_QUALITY_ROUTE']='PRODUCT_VISIBLE_QUALITY_FIRST'
scene['LEFT_HAND_STARTED']=False;scene['WEB_EXPORT_STARTED']=False
scene.frame_set(1);m.reset_pose(rig);m.bpy.context.view_layer.update()
assert m.product_payload(ob,rig)==native and shape_payload(ob)==shape
m.bpy.ops.wm.save_as_mainfile(filepath=str(ASSET),compress=False)
ob,rig=m.open_file(ASSET)
assert m.product_payload(ob,rig)==native and shape_payload(ob)==shape
assert [m.material_payload(mat) for mat in ob.data.materials if mat]==materials
assert m.state_zero(rig) and all(k.value==0 for k in ob.data.shape_keys.key_blocks[1:])
V1,F1=m.evaluate(ob,ob.matrix_world);assert F1==F
finite=sum(not math.isfinite(float(x)) for v in V1 for x in v)
error=max((a-b).length*1000 for a,b in zip(V1,V0));assert finite==0 and error==0
# One direct round trip of an already Human-approved pose checks reset, not requalification.
m.pose(rig,next(c for c in m.CASES if c['case_id']=='FULL_OPP_L3'))
active_key_value=float(ob.data.shape_keys.key_blocks[1].value);assert active_key_value==1
m.reset_pose(rig);m.bpy.context.view_layer.update()
Vr,Fr=m.evaluate(ob,ob.matrix_world)
restore=max((a-b).length*1000 for a,b in zip(Vr,V1));assert restore==0 and m.state_zero(rig)
assert all(k.value==0 for k in ob.data.shape_keys.key_blocks[1:])
assert m.product_payload(ob,rig)==native and shape_payload(ob)==shape
renderer=m.Renderer(m.cameras(),'renders');renderer.sc.display.shading.shadow_intensity=0
renderer.draw('BASELINE','ZERO',V1,F1,['PALMAR_FULL','DORSAL_FULL','THENAR_CLOSE']);renderer.dispose()
write('BASELINE_FREEZE_VERIFICATION_R1.json',{'status':'PASS','source':status['candidate'],'baseline':{'path':ASSET.relative_to(ROOT).as_posix(),'sha256':sha(ASSET)},'source_review_evidence_match':'PASS','verified_evidence_file_count':len(verified),'file_clean_reopen':'PASS','saved_pose':'ZERO / RSSF','basis_mesh_weights_groups_rest_bones_hierarchy_joint_layout_UV_modifiers_transforms_exact':True,'materials_exact':True,'shape_keys_delta_drivers_exact':True,'bone_count':21,'mesh_vertex_count':3300,'face_count':len(F1),'group_count':len(ob.vertex_groups),'deform_bones':sum(b.use_deform for b in rig.data.bones),'non_deform_tip_helpers':[b.name for b in rig.data.bones if not b.use_deform],'corrective_key_count':len(shape['keys'])-1,'driver_count':len(shape['drivers']),'corrective_values_at_saved_ZERO':[float(k.value) for k in ob.data.shape_keys.key_blocks[1:]],'NaN_Inf':finite,'source_baseline_ZERO_max_error_mm':error,'zero_restore_test':'Already approved FULL_OPP_L3 once, then reset all pose transforms; no full Stage6 matrix','ZERO_RESTORE':'PASS','zero_restore_max_error_mm':restore,'geometry_repairs':0,'weight_repairs':0,'correctives_added':0,'source_sha256_after':sha(source),'approved_payload_sha256':m.digest(native),'approved_shape_driver_sha256':m.digest(shape),'render_records':renderer.records})
assert sha(source)==source_sha
print('BASELINE_FROZEN_REOPEN_PASS',sha(ASSET),'V3300 B21 KEY1 DRIVER1 ZERO_RESTORE0MM',flush=True)
