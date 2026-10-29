import sys,importlib.util,json,ast,math,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
import bpy
from mathutils import Quaternion,Vector
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
spec=importlib.util.spec_from_file_location('helpers',ROOT/'audits/official_l1_first_web_targeted_deformation_fix_r1/common.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.old.lib.OUT=OUT
BASE=ROOT/'production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend';TEST=OUT/'RIGHT_HAND_PIANO_MOTION_TEST_R1.blend'
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
node=next(n for n in ast.parse((BASE.parent/'freeze_baseline.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='shape_payload');exec(compile(ast.Module(body=[node],type_ignores=[]),'shape_payload','exec'))
ob,rig=m.open_file(BASE);native=m.product_payload(ob,rig);shape=shape_payload(ob);materials=[m.material_payload(mat) for mat in ob.data.materials if mat];V0,F=m.evaluate(ob,ob.matrix_world)
ob,rig=m.open_file(TEST);scene=bpy.context.scene;raw=bpy.data.actions['PIANOVAM_PHYSICAL_RIGHT_RAW_R1'];rig.animation_data.action=raw
names=[b.name for b in rig.data.bones if b.use_deform];qs={k:[] for k in names}
for i in range(421):
 scene.frame_set(1+i//2,subframe=(i%2)/2);bpy.context.view_layer.update()
 for name in names:
  q=rig.pose.bones[name].rotation_quaternion.copy()
  if qs[name] and q.dot(qs[name][-1])<0:q.negate()
  qs[name].append(q)
smooth={}
for name,seq in qs.items():
 smooth[name]=[]
 for i,q in enumerate(seq):
  neighbors=[seq[max(0,i-1)],q,seq[min(420,i+1)]];weights=[.25,.5,.25]
  v=[sum(w*x[k] for w,x in zip(weights,neighbors)) for k in range(4)];s=Quaternion(v);s.normalize()
  if smooth[name] and s.dot(smooth[name][-1])<0:s.negate()
  smooth[name].append(s)
action=bpy.data.actions.new('PIANOVAM_PHYSICAL_RIGHT_SMOOTHED_R1');action.use_fake_user=True
for key in raw.keys():action[key]=raw[key]
action['TEMPORAL_SMOOTHING_USED']=True;action['SMOOTHING']='One symmetric 3-tap quaternion filter [0.25,0.5,0.25] at 60fps, normalized after sign-continuity; 33.3ms total neighbor support, zero phase. No resynthesis or constraints.'
rig.animation_data.action=action
for name,seq in smooth.items():
 pb=rig.pose.bones[name]
 for i,q in enumerate(seq):pb.rotation_quaternion=q;pb.keyframe_insert(data_path='rotation_quaternion',frame=1+i/2,group=name)
for layer in action.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:
   for fc in bag.fcurves:
    for key in fc.keyframe_points:key.interpolation='LINEAR'
directions={k:[] for k in names};finite=0;web=[];mesh_bounds=[]
for i in range(421):
 scene.frame_set(1+i//2,subframe=(i%2)/2);bpy.context.view_layer.update();V,faces=m.evaluate(ob,ob.matrix_world);assert faces==F
 finite+=sum(not math.isfinite(float(x)) for v in V for x in v);web.append(float(ob.data.shape_keys.key_blocks[1].value))
 for name in names:directions[name].append(rig.pose.bones[name].matrix.to_3x3()@Vector((0,1,0)))
steps={name:[math.degrees(p.angle(q)) for p,q in zip(ds,ds[1:])] for name,ds in directions.items()}
flips=sum(x>90 for vals in steps.values() for x in vals);maxsteps={name:max(math.degrees(p.rotation_difference(q).angle) for p,q in zip(seq,seq[1:])) for name,seq in smooth.items()}
sign=sum(p.dot(q)<0 for seq in smooth.values() for p,q in zip(seq,seq[1:]));maxchange=max(math.degrees(q.rotation_difference(s).angle) for name in names for q,s in zip(qs[name],smooth[name]))
rig.animation_data.action=None;m.reset_pose(rig);bpy.context.view_layer.update();Vz,Fz=m.evaluate(ob,ob.matrix_world);zero=max((a-b).length*1000 for a,b in zip(V0,Vz));assert zero==0
assert m.product_payload(ob,rig)==native and shape_payload(ob)==shape and [m.material_payload(mat) for mat in ob.data.materials if mat]==materials
rig.animation_data.action=action;scene.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(TEST),compress=False)
name=action.name;ob,rig=m.open_file(TEST);rig.animation_data.action=bpy.data.actions[name];bpy.context.scene.frame_set(1);bpy.context.view_layer.update();assert m.product_payload(ob,rig)==native and shape_payload(ob)==shape
rawcheck=json.loads((OUT/'RETARGET_MACHINE_CHECKS_R1.json').read_text());dump('RAW_RETARGET_MACHINE_CHECKS_R1.json',rawcheck)
check={'RETARGET_FRAME_COUNT':421,'animated_deform_bones':16,'animated_tip_helpers':0,'NaN_Inf':finite,'BONE_FLIP_COUNT':flips,'bone_flip_definition':'Consecutive evaluated bone direction change >90 degrees at source 60fps','max_world_direction_step_deg_by_bone':{k:max(v) for k,v in steps.items()},'quaternion_sign_discontinuity_count':sign,'max_consecutive_quaternion_step_deg_by_bone':maxsteps,'TEMPORAL_SMOOTHING_USED':True,'smoothing':'One pass 3-tap quaternion normalized weighted average [.25,.5,.25] at 60fps; neighbor span 33.3ms, no phase shift','smoothing_authority':'Visible raw finger direction pops corroborated by raw 4 >90-degree world direction jumps; raw preview preserved. No heavy filtering.','max_raw_smoothed_quaternion_difference_deg':maxchange,'raw_BONE_FLIP_COUNT':rawcheck['BONE_FLIP_COUNT'],'ZERO_RESTORE':'PASS','zero_restore_max_error_mm':zero,'zero_method':'Detach Action and reset pose; evaluate all vertices against frozen baseline ZERO.','first_web_driver_value_range':[min(web),max(web)],'native_payload_exact_after_save_reopen':True,'shape_driver_exact_after_save_reopen':True,'materials_exact':True,'baseline_sha_before':rawcheck['baseline_sha_before'],'baseline_sha_after':hashlib.sha256(BASE.read_bytes()).hexdigest(),'test_sha256':hashlib.sha256(TEST.read_bytes()).hexdigest(),'action_names':['PIANOVAM_PHYSICAL_RIGHT_RAW_R1',name],'raw_preview':'RAW_RETARGET_PREVIEW.mp4','saved_frame':1,'saved_action':name}
assert check['baseline_sha_after']==check['baseline_sha_before'];dump('RETARGET_MACHINE_CHECKS_R1.json',check)
mapping=json.loads((OUT/'PIANOVAM_TO_RIGHT_HAND_MAPPING_R1.json').read_text());mapping['TEMPORAL_SMOOTHING_USED']=True;mapping['smoothing']=check['smoothing'];mapping['raw_action']='PIANOVAM_PHYSICAL_RIGHT_RAW_R1';mapping['action']=name;dump('PIANOVAM_TO_RIGHT_HAND_MAPPING_R1.json',mapping)
print('SMOOTH_DONE','FLIPS',flips,'MAX_WORLD_STEP',max(max(v) for v in steps.values()),'ZERO',zero,flush=True)
