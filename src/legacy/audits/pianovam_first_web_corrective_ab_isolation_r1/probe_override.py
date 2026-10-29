import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'audits/pianovam_single_sample_right_hand_retarget_r1/RIGHT_HAND_PIANO_MOTION_TEST_R1.blend'
bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];ob=bpy.data.objects['RIGHT_HAND_OFFICIAL_L1_PRODUCT_MESH'];key=ob.data.shape_keys.key_blocks['FIRST_WEB_OPPOSITION_CREASE_R1'];fc=ob.data.shape_keys.animation_data.drivers[0]
bpy.context.scene.frame_set(205);bpy.context.view_layer.update()
before=float(key.value);pose=[list(pb.rotation_quaternion) for pb in rig.pose.bones]
print('VALUE_BEFORE',before,'MUTE',fc.mute,key.mute,flush=True)
key.value=0;bpy.context.view_layer.update()
ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());print('VALUE_AFTER_DIRECT',float(key.value),'EVAL_VALUE',float(ev.data.shape_keys.key_blocks[key.name].value),'POSE_UNCHANGED',pose==[list(pb.rotation_quaternion) for pb in rig.pose.bones],flush=True)
bpy.context.scene.frame_set(205);bpy.context.view_layer.update();print('VALUE_RESTORED_FRAME_REFRESH',float(key.value),flush=True)
print('EXPRESSION',fc.driver.expression,'INPUTS',[(v.name,v.targets[0].bone_target,v.targets[0].transform_space,v.targets[0].transform_type) for v in fc.driver.variables],flush=True)
for f in [1,16,31,61,76,106,121,126,130,151,181,205]:
 bpy.context.scene.frame_set(f);bpy.context.view_layer.update();value=float(key.value);e={name:list(rig.pose.bones[name].matrix_basis.to_euler('XYZ')) for name in ['THUMB_CMC_R','THUMB_MCP_R']}
 key.value=0;bpy.context.view_layer.update();off=float(key.value)
 bpy.context.scene.frame_set(f);bpy.context.view_layer.update();restored=float(key.value)
 print('PROBE_FRAME',f,'VALUE',value,'OFF',off,'RESTORED',restored,'VARS',e,flush=True)
