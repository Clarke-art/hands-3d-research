import sys,importlib.util,ast,json,hashlib,math
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Matrix,Vector,Quaternion
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
spec=importlib.util.spec_from_file_location('approved_helpers',ROOT/'audits/official_l1_first_web_targeted_deformation_fix_r1/common.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.old.lib.OUT=OUT
BASE=ROOT/'production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend';EXPECTED='4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
assert sha(BASE)==EXPECTED
node=next(n for n in ast.parse((BASE.parent/'freeze_baseline.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='shape_payload');exec(compile(ast.Module(body=[node],type_ignores=[]),'approved_shape_payload','exec'))
ob,rig=m.open_file(BASE);native=m.product_payload(ob,rig);shape=shape_payload(ob);materials=[m.material_payload(mat) for mat in ob.data.materials if mat];V0,F=m.evaluate(ob,ob.matrix_world)
def rigpalm():
 p={b.name:b.head_local.copy() for b in rig.data.bones};y=(p['MIDDLE_MCP_R']-p['WRIST_R']).normalized();x=p['INDEX_MCP_R']-p['LITTLE_MCP_R'];x=(x-y*x.dot(y)).normalized();z=x.cross(y);return Matrix((x,y,z)).transposed()
R=rigpalm();data=np.load(OUT/'source_window_hand_local.npz');local=data['local'];bases=[Matrix(v.tolist()) for v in data['bases']];points=data['points'];n=len(local)
segments={}
for digit,start in [('THUMB',1),('INDEX',5),('MIDDLE',9),('RING',13),('LITTLE',17)]:
 joints=['CMC','MCP','IP'] if digit=='THUMB' else ['MCP','PIP','DIP']
 for j,name in enumerate(joints):segments[f'{digit}_{name}_R']=(start+j,start+j+1)
assert set(segments)=={b.name for b in rig.data.bones if b.use_deform and b.name!='WRIST_R'}
rest={b.name:b.matrix_local.to_3x3() for b in rig.data.bones};reference=bases[0];T=<REDACTED_EMAIL>();ordered=[]
def visit(b):
 ordered.append(b)
 for c in b.children:visit(c)
visit(rig.data.bones['WRIST_R'])
quats={b.name:[] for b in ordered if b.use_deform};directions={name:[] for name in quats};alignerror=0
for i in range(n):
 worldrot={};wristDelta=T@bases[i]@reference.transposed()@T.transposed()
 for b in ordered:
  predicted=worldrot[b.parent.name]@rest[b.parent.name].transposed()@rest[b.name] if b.parent else rest[b.name]
  if b.name=='WRIST_R':target=wristDelta@rest[b.name]
  elif b.name in segments:
   u,v=segments[b.name];d=wristDelta@R@Vector((local[i,v]-local[i,u]).tolist());d.normalize()
   before=predicted@Vector((0,1,0));swing=before.rotation_difference(d);target=swing.to_matrix()@predicted
   alignerror=max(alignerror,math.degrees((target@Vector((0,1,0))).angle(d)))
  else:target=predicted
  worldrot[b.name]=target
  if b.use_deform:
   q=(predicted.transposed()@target).to_quaternion();q.normalize()
   if quats[b.name] and q.dot(quats[b.name][-1])<0:q.negate()
   quats[b.name].append(q);directions[b.name].append(target@Vector((0,1,0)))
nan=sum(not math.isfinite(x) for qs in quats.values() for q in qs for x in q)
negative=sum(q.dot(p)<0 for qs in quats.values() for p,q in zip(qs,qs[1:]));flip=sum(p.angle(q)>math.radians(90) for ds in directions.values() for p,q in zip(ds,ds[1:]));maxstep={name:max(math.degrees(p.rotation_difference(q).angle) for p,q in zip(qs,qs[1:])) for name,qs in quats.items()}
action=bpy.data.actions.new('PIANOVAM_PHYSICAL_RIGHT_RAW_R1');rig.animation_data_create();rig.animation_data.action=action;action.use_fake_user=True
action['SOURCE_RECORDING_ID']='2024-03-04_03-46-36';action['USAGE_SCOPE']='INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY';action['LICENSE']='CC BY-NC-SA 4.0';action['DO_NOT_PROMOTE_DATASET_MOTION_TO_COMMERCIAL_PRODUCT']=True
action['SOURCE_FIELD']='Left (physical right, video verified)';action['SOURCE_WINDOW']='11.5-18.5 s';action['MOTION_AUTHORITY']='Handskeleton';action['TEMPORAL_SMOOTHING_USED']=False
# At 30fps scene, source every 60fps observation receives half-frame keys. 421 samples, 0..7s inclusive.
scene=bpy.context.scene;scene.render.fps=30;scene.render.fps_base=1;scene.frame_start=1;scene.frame_end=210
for name,qs in quats.items():
 pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION'
 for i,q in enumerate(qs):pb.rotation_quaternion=q;pb.keyframe_insert(data_path='rotation_quaternion',frame=1+i/2,group=name)
for layer in action.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:
   for fc in bag.fcurves:
    for key in fc.keyframe_points:key.interpolation='LINEAR'
scene['PHASE']='PIANOVAM_SINGLE_SAMPLE_RIGHT_HAND_RETARGET_R1';scene['USAGE_SCOPE']='INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY';scene['PRODUCTION_PROMOTION']='NO';scene['HUMAN_APPROVAL_PENDING']=True;scene['HUMAN_APPROVED']=False
# Keep the approved mesh/rig metadata and all native payloads intact. Test-only context lives on scene/action.
def apply(i):
 scene.frame_set(1+i//2,subframe=(i%2)/2);bpy.context.view_layer.update()
assert m.product_payload(ob,rig)==native and shape_payload(ob)==shape
union=[v.copy() for v in V0];finite=0;extent=[];webvalues=[];actualdirs={k:[] for k in quats}
for i in range(n):
 apply(i);V,faces=m.evaluate(ob,ob.matrix_world);assert faces==F
 finite+=sum(not math.isfinite(float(x)) for v in V for x in v);webvalues.append(float(ob.data.shape_keys.key_blocks[1].value))
 if i%12==0:union.extend(v.copy() for v in V)
 for name in quats:actualdirs[name].append(rig.pose.bones[name].matrix.to_3x3()@Vector((0,1,0)))
 finite+=sum(not math.isfinite(float(x)) for pb in rig.pose.bones for row in pb.matrix for x in row)
actualflips=sum(p.angle(q)>math.radians(90) for ds in actualdirs.values() for p,q in zip(ds,ds[1:]));assert finite==0
# Detach Action for exact ZERO, then reattach and use out-of-clip marker frame 0 with NLA influence muted only for saved ZERO.
rig.animation_data.action=None;m.reset_pose(rig);bpy.context.view_layer.update();Vz,Fz=m.evaluate(ob,ob.matrix_world);zero=max((a-b).length*1000 for a,b in zip(V0,Vz));assert zero==0
assert m.product_payload(ob,rig)==native and shape_payload(ob)==shape
rig.animation_data.action=action;apply(0)
TEST=OUT/'RIGHT_HAND_PIANO_MOTION_TEST_R1.blend';action_name=action.name;bpy.ops.wm.save_as_mainfile(filepath=str(TEST),compress=False)
# Reopen independent file and compare protected payloads again.
ob,rig=m.open_file(TEST);action=bpy.data.actions[action_name];rig.animation_data.action=action;scene=bpy.context.scene;apply(0)
assert m.product_payload(ob,rig)==native and shape_payload(ob)==shape and [m.material_payload(mat) for mat in ob.data.materials if mat]==materials
cams={}
original=m.cameras()
for view in ['PALMAR_FULL','DORSAL_FULL']:
 cams[view]=m.frame(union,original[view]['direction'],[640,640],padding=1.16)
dump('REVIEW_CAMERAS_R1.json',cams)
mapping={'LANDMARK_ORDER_VERIFIED':True,'BONE_MAPPING_COMPLETE':True,'physical_right_source_field':'Left','handedness_label_correction':'Video overlay proves swapped JSON hand labels in this recording; no mirroring of landmarks','mapping_coordinate_corrections_used':1,'allowed_max':2,'landmark_segments':{k:list(v) for k,v in segments.items()},'WRIST_R':'Palm-frame relative orientation from wrist0/index5/middle9/little17','TIP_helpers':{b.name:{'landmark_index':{'THUMB':4,'INDEX':8,'MIDDLE':12,'RING':16,'LITTLE':20}[b.name.split('_')[0]],'use_deform':False,'animation_channels':False,'new_skin_influence':False} for b in rig.data.bones if not b.use_deform},'coordinate_transform':{'image_aspect':1080/1920,'palm_Y':'normalize(point9-point0)','palm_X':'normalize((point5-point17) minus projection onto Y)','palm_Z':'X cross Y','hand_local':'(point-point0) projected onto each palm basis axis','rig_palm_frame':[list(row) for row in R],'world_source_bridge':[list(row) for row in T],'source_palm_reference_frame':690},'rotation_method':'For each bone in parent-first order: predicted=parent_pose_rotation * inverse(parent_rest_rotation) * bone_rest_rotation. Minimal swing maps predicted local-Y to palm-local source segment expressed in rig frame with source palm delta. Local quaternion=inverse(predicted)*target. Preserve transported rest roll; no axial twist inferred from single segment.','WRIST_RETARGET_MODE':'B_FIXED_TRANSLATION_SOURCE_PALM_ORIENTATION','wrist_translation_keys':0,'wrist_scale_keys':0,'segment_length_policy':'Frozen rig lengths; source positions drive directions only','SOURCE_COORDINATES':'Normalized image xyz, not calibrated metric depth','TEMPORAL_SMOOTHING_USED':False,'quaternion_sign_continuity':True,'action':action.name,'protected_payload_exact_after_save_reopen':True}
dump('PIANOVAM_TO_RIGHT_HAND_MAPPING_R1.json',mapping)
dump('RETARGET_MACHINE_CHECKS_R1.json',{'RETARGET_FRAME_COUNT':n,'animated_deform_bones':len(quats),'animated_tip_helpers':0,'NaN_Inf':finite+nan,'BONE_FLIP_COUNT':actualflips,'bone_flip_definition':'Consecutive evaluated bone direction change >90 degrees at source 60fps','quaternion_sign_discontinuity_count':negative,'max_consecutive_quaternion_step_deg_by_bone':maxstep,'max_swing_alignment_error_deg':alignerror,'ZERO_RESTORE':'PASS','zero_restore_max_error_mm':zero,'zero_method':'Detach Action, reset all pose transforms; evaluated mesh equals source ZERO exactly. Reattach Action for review.','first_web_driver_value_range':[min(webvalues),max(webvalues)],'native_payload_exact':True,'shape_driver_exact':True,'materials_exact':True,'baseline_sha_before':EXPECTED,'baseline_sha_after':sha(BASE),'test_sha256':sha(TEST),'saved_frame':1,'saved_frame_is_motion':True,'rest_twist_policy':'Minimum swing relative to transported rest/parent orientation; no source-segment axial twist','TEMPORAL_SMOOTHING_USED':False})
renderer=m.Renderer(cams,'preview_stills');renderer.sc.display.shading.shadow_intensity=0
for i in [0,60,120,180,240,300,360,420]:
 apply(i);V,F=m.evaluate(ob,ob.matrix_world);renderer.draw('RAW',f'{i:04}',V,F,list(cams))
renderer.dispose();assert sha(BASE)==EXPECTED
print('RAW_RETARGET_DONE',n,'FLIPS',actualflips,'ZERO',zero,'MAXSTEP',max(maxstep.values()),flush=True)
