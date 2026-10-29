import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mapping_core import *
assert read(OUT/'DEFECT_FRAME_OLD_VS_CORRECTED_R1.json')['AXIS_MAPPING_CORRECTION']=='PROMISING'
ob,rig=m.open_file(BASE);native=m.product_payload(ob,rig);shape=shape_payload(ob);materials=[m.material_payload(x) for x in ob.data.materials if x];V0,F=m.evaluate(ob,ob.matrix_world)
ob,rig=m.open_file(OLD);old_names=[a.name for a in bpy.data.actions]
# Read-only reuse of exact Action payload hashing from isolation; no source top-level execution.
ns={};node=next(n for n in ast.parse((AB/'isolate.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='action_payload');exec(compile(ast.Module(body=[node],type_ignores=[]),'action_payload','exec'),ns);action_payload=ns['action_payload'];digest=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
old_hashes={a.name:digest(action_payload(a)) for a in bpy.data.actions};solver=Solver(ob,rig,2);raw={n:[] for n in solver.rest if rig.data.bones[n].use_deform};smooth={n:[] for n in raw}
for i in range(421):
 rq=solver.raw(i)[0];sq=solver.smoothed(i)[0]
 for n in raw:
  for q,seq in [(rq[n].copy(),raw[n]),(sq[n].copy(),smooth[n])]:
   if seq and q.dot(seq[-1])<0:q.negate()
   seq.append(q)
def action_from(name,data):
 a=bpy.data.actions.new(name);a.use_fake_user=True;rig.animation_data.action=a
 a['SOURCE_MOTION']='PIANOVAM_SAME_11_5_18_5_WINDOW';a['SOURCE_MOTION_CHANGED']=False;a['USAGE_SCOPE']='INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY';a['LICENSE']='CC BY-NC-SA 4.0';a['DO_NOT_PROMOTE_DATASET_MOTION_TO_COMMERCIAL_PRODUCT']=True;a['MAPPING_ITERATION']=2;a['EULER_PRIMARY_SOLVER']=False
 for n,seq in data.items():
  pb=rig.pose.bones[n];pb.rotation_mode='QUATERNION'
  for i,q in enumerate(seq):pb.rotation_quaternion=q;pb.keyframe_insert(data_path='rotation_quaternion',frame=1+i/2,group=n)
 for layer in a.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for key in fc.keyframe_points:key.interpolation='LINEAR'
 return a
raw_action=action_from('PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_RAW_R1',raw);raw_action['SMOOTHING']='NONE'
new=action_from('PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1',smooth);new['SMOOTHING']='Unchanged 60fps quaternion [.25,.5,.25], sign continuity, normalize; zero-phase neighbor span33.3ms'
scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=210;scene.render.fps=30;scene['PHASE']='PIANOVAM_RETARGET_LOCAL_AXIS_MAPPING_CORRECTION_R1';scene['HUMAN_APPROVED']=False;scene['HUMAN_APPROVAL_PENDING']=True;scene['USAGE_SCOPE']='INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY';scene['PRODUCTION_PROMOTION']='NO'
dirs={n:[] for n in smooth};finite=0;corrective=[];union=[]
for i in range(421):
 scene.frame_set(1+i//2,subframe=(i%2)/2);bpy.context.view_layer.update();V,faces=m.evaluate(ob,ob.matrix_world);assert faces==F;finite+=sum(not math.isfinite(float(x)) for v in V for x in v);corrective.append(float(ob.data.shape_keys.key_blocks[1].value))
 if i%15==0:union.extend(v.copy() for v in V)
 for n in dirs:dirs[n].append(rig.pose.bones[n].matrix.to_3x3()@Vector((0,1,0)))
world_steps={n:[math.degrees(a.angle(b)) for a,b in zip(vs,vs[1:])] for n,vs in dirs.items()};local_steps={n:[math.degrees(a.rotation_difference(b).angle) for a,b in zip(vs,vs[1:])] for n,vs in smooth.items()}
flips=sum(v>90 for vals in world_steps.values() for v in vals);jump_frames=[i+1 for i in range(420) if any(vals[i]>90 for vals in local_steps.values())];sign=sum(a.dot(b)<0 for vs in smooth.values() for a,b in zip(vs,vs[1:]))
rig.animation_data.action=None;m.reset_pose(rig);bpy.context.view_layer.update();Vz,Fz=m.evaluate(ob,ob.matrix_world);zero=max((a-b).length*1000 for a,b in zip(V0,Vz));assert zero==0
assert m.product_payload(ob,rig)==native and shape_payload(ob)==shape and [m.material_payload(x) for x in ob.data.materials if x]==materials
rig.animation_data.action=new;scene.frame_set(1);bpy.context.view_layer.update();TEST=OUT/'RIGHT_HAND_PIANO_AXIS_CORRECTED_TEST_R1.blend';new_name=new.name
assert old_hashes=={n:digest(action_payload(bpy.data.actions[n])) for n in old_names};bpy.ops.wm.save_as_mainfile(filepath=str(TEST),compress=False)
ob,rig=m.open_file(TEST);rig.animation_data.action=bpy.data.actions[new_name];scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
assert m.product_payload(ob,rig)==native and shape_payload(ob)==shape and old_hashes=={n:digest(action_payload(bpy.data.actions[n])) for n in old_names}
cams={}
for view in ['PALMAR_FULL','DORSAL_FULL']:
 original=read(PREV/'REVIEW_CAMERAS_R1.json')[view];cams[view]=m.frame(union,original['direction'],[640,640],padding=1.16)
dump('FULL_REVIEW_CAMERAS_R1.json',cams)
dump('PIANOVAM_AXIS_CORRECTED_ACTION_R1.json',{'new_test_blend':TEST.relative_to(ROOT).as_posix(),'new_test_sha256':sha(TEST),'new_action':new_name,'raw_new_action':'PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_RAW_R1','old_actions_preserved':old_names,'old_actions_hashes_unchanged':True,'SOURCE_MOTION_CHANGED':'NO','observation_count':421,'source_frame_range':[690,1110],'scene_fps':30,'animation_frames_rendered':210,'source_observation_keys':'half-frame positions1..211, all421 samples retained','smoothing_window_changed':False,'smoothing_kernel':[.25,.5,.25],'TEMPORAL_CONTINUITY':{'NaN_Inf':finite,'quaternion_sign_discontinuity_count':sign,'BONE_FLIP_COUNT':flips,'CATASTROPHIC_FRAME_JUMP_COUNT':len(jump_frames),'catastrophic_frame_jump_definition':'Any local geodesic quaternion step >90deg per60fps source observation','catastrophic_jump_observation_indices':jump_frames,'max_world_direction_step_deg':max(max(v) for v in world_steps.values()),'max_local_quaternion_step_deg':max(max(v) for v in local_steps.values())},'corrective_value_natural_range':[min(corrective),max(corrective)],'ZERO_RESTORE':'PASS','zero_restore_max_error_mm':zero,'baseline_sha_before_after':sha(BASE),'old_source_sha_before_after':sha(OLD),'protected_mesh_weights_rest_shape_driver_materials_exact_after_save_reopen':True,'TIP_animation_channels':0,'wrist_translation_keys':0,'geometry_edits':0,'weight_edits':0,'driver_edits':0,'corrective_edits':0,'mapping_iteration_count':2})
renderer=m.Renderer(cams,'full_motion_frames');renderer.sc.display.shading.shadow_intensity=0
for j in range(210):
 scene.frame_set(1+j);bpy.context.view_layer.update();V,F=m.evaluate(ob,ob.matrix_world);renderer.draw('AXIS_CORRECTED',f'{j:04}',V,F,list(cams))
renderer.dispose();assert sha(BASE)==BASE_SHA and sha(OLD)==OLD_SHA
print('FULL_DONE','FLIPS',flips,'JUMPS',len(jump_frames),'ZERO',zero,'FINITE',finite,flush=True)
