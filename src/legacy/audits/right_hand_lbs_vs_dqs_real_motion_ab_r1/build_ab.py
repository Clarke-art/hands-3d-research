import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
before=inputs()
request=Path('<USER_HOME>/.codex/attachments/1c79f78b-8e2a-44fe-9fe8-30ed1dc8e70d/已粘贴的文本.txt')
dump('PRIOR_HUMAN_DECISION_BIND_R1.json',{'phase':'FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1','Q1':'NO','Q2':'YES','Q3':'YES','Q4':'NO','verdict':'FIRST_WEB_REAL_MOTION_FIX_LIMIT_REACHED','failed_candidate_rejected_as_input':True,'authority':'Direct user attachment','request_path':str(request),'request_sha256':sha(request)})
ob,rig=m.open_file(BASE)
mods=[x for x in ob.modifiers if x.type=='ARMATURE']
assert len(mods)==1
mode='DQS' if mods[0].use_deform_preserve_volume else 'LBS'
initial={'BASELINE_DEFORMATION_MODE':mode,'SOURCE_BASELINE_SHA256':sha(BASE),'baseline_modifier_stack':m.product_payload(ob,rig)['modifiers'],'actual_API':'ArmatureModifier.use_deform_preserve_volume','shape_evaluation':'Shape keys before modifier stack; unchanged natural approved driver'}
dump('DEFORMATION_MODE_VERIFICATION_R1.json',initial)
if mode=='DQS':
    dump(PHASE+'_STATUS.json',dict(initial,VERDICT='DQS_ALREADY_ACTIVE',PRODUCTION_PROMOTION='NO'))
    print('DQS_ALREADY_ACTIVE',flush=True);raise SystemExit()
# An existing independent test may only be reopened for verification.
native=m.product_payload(ob,rig);shape=core.shape_payload(ob)
material=[m.material_payload(x) for x in ob.data.materials if x]
assert len(ob.data.vertices)==3300 and len(rig.data.bones)==21
assert 'FIRST_WEB_REAL_MOTION_CORRECTIVE_R1' not in ob.data.shape_keys.key_blocks
with bpy.data.libraries.load(str(SOURCE),link=False) as (src,dst):
    assert ACTION in src.actions;dst.actions=[ACTION]
action=bpy.data.actions[ACTION]
expected=read(ROOT/'audits/pianovam_first_web_joint_contribution_isolation_r1/MACHINE_CHECK_R1.json')['actions_before'][ACTION]
assert digest(action_payload(action))==expected
if not TEST.exists():
    rig.animation_data_create();rig.animation_data.action=action
    rigB=rig.copy();rigB.name='B_DQS_RIG';bpy.context.scene.collection.objects.link(rigB)
    obB=ob.copy();obB.name='B_DQS';bpy.context.scene.collection.objects.link(obB)
    ob.name='A_LBS'
    if obB.parent==rig:obB.parent=rigB
    obB.modifiers[mods[0].name].object=rigB
    obB.modifiers[mods[0].name].use_deform_preserve_volume=True
    assert ob.data==obB.data and rig.data==rigB.data
    for o in [ob,obB]:
        o['DESIGN_ONLY']=True;o['HUMAN_APPROVAL_PENDING']=True;o['PRODUCT_BASELINE_STATUS']='DESIGN_ONLY_NOT_PRODUCTION';o['PRODUCTION_PROMOTION']='NO'
    sc=bpy.context.scene
    sc['PHASE']=PHASE;sc['HUMAN_APPROVED']=False;sc['HUMAN_APPROVAL_PENDING']=True;sc['RIGHT_HAND_PRODUCT_BASELINE']='INDEPENDENT_AB_TEST_NOT_PRODUCTION';sc['PRODUCTION_PROMOTION']='NO'
    sc.frame_start=1;sc.frame_end=210;sc.render.fps=30
    motion(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(TEST),compress=False)
# A clean reopen checks the saved two-condition asset, including driver targets.
bpy.ops.wm.open_mainfile(filepath=str(TEST),load_ui=False,use_scripts=False)
ob=bpy.data.objects['A_LBS'];obB=bpy.data.objects['B_DQS'];rig,rigB=rigs()
neutral()
pa=m.product_payload(ob,rig);pb=m.product_payload(obB,rigB)
for k in native:
    if k!='modifiers':assert pa[k]==pb[k]==native[k],k
assert core.shape_payload(ob)==core.shape_payload(obB)==shape
assert [m.material_payload(x) for x in ob.data.materials if x]==material
ma=modifier_payload(ob);mb=modifier_payload(obB)
for a,b in zip(ma,mb):
    aa=dict(a);bb=dict(b);aa.pop('use_deform_preserve_volume',None);bb.pop('use_deform_preserve_volume',None);assert aa==bb
assert len(ma)==len(mb)==len(native['modifiers'])
assert digest(action_payload(bpy.data.actions[ACTION]))==expected
assert inputs()==before
initial.update({'status':'PASS','test_asset':{'path':TEST.relative_to(ROOT).as_posix(),'sha256':sha(TEST)},'LBS_PRESERVE_VOLUME':False,'DQS_PRESERVE_VOLUME':True,'MESH_IDENTICAL':True,'WEIGHTS_IDENTICAL':True,'RIG_IDENTICAL':True,'CORRECTIVES_IDENTICAL':True,'DRIVERS_IDENTICAL':True,'MODIFIER_STACK_IDENTICAL_EXCEPT_DQS':True,'OBJECT_TRANSFORMS_IDENTICAL':True,'ACTION_IDENTICAL':True,'source_action_payload_sha256':expected,'saved_reopen':'PASS','shared_mesh_datablock':True,'shared_rest_armature_datablock':True,'shared_shape_keys_drivers':'One unmodified approved Key datablock. Driver target remains original A rig; both rigs are kept at identical Action/pose and checked at every observation. No target rewrite.','modifiers_A':ma,'modifiers_B':mb,'baseline_payload_sha256':digest(native),'approved_shape_driver_sha256':digest(shape),'input_hashes_unchanged':before,'NEW_CORRECTIVE_COUNT':0})
dump('DEFORMATION_MODE_VERIFICATION_R1.json',initial)
print('BASELINE_LBS_AB_SAVED_VERIFIED',sha(TEST),flush=True)
