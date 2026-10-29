import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mapping_core import *
iteration=int(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else 1
assert sha(BASE)==BASE_SHA and sha(OLD)==OLD_SHA
ob,rig=m.open_file(BASE);native=m.product_payload(ob,rig);shape=shape_payload(ob);solver=Solver(ob,rig,iteration);audit=solver.audit();dump('PIANOVAM_TO_RIG_COORDINATE_FRAME_AUDIT_R1.json',audit)
selection=read(AB/'FIRST_WEB_DEFECT_FRAME_SELECTION_R1.json')['frames'];cams=read(AB/'MATCHED_AB_VERIFICATION_R1.json')['cameras'];rows=[]
for r in selection:
 f=r['frame'];i=r['source_frame']-690
 ob,rig=m.open_file(OLD);old_action=rig.animation_data.action;bpy.context.scene.frame_set(f);bpy.context.view_layer.update();Vold,F=m.evaluate(ob,ob.matrix_world);old={n:list(rig.pose.bones[n].rotation_quaternion) for n in ['INDEX_MCP_R','INDEX_PIP_R','THUMB_CMC_R','THUMB_MCP_R']}
 old_pose={n:arr(rig.pose.bones[n].matrix) for n in old};qnew,comp=solver.smoothed(i)
 # Solver uses exactly the same rig rest matrices; only independent runtime poses change.
 solver.ob=ob;solver.rig=rig;solver.apply(qnew);Vnew,Fnew=m.evaluate(ob,ob.matrix_world);assert Fnew==F and m.product_payload(ob,rig)==native and shape_payload(ob)==shape
 # Cross-check local-basis conversion in Blender, no world pose writes or rest edits.
 conversion_errors={}
 for name in ['INDEX_MCP_R','INDEX_PIP_R','THUMB_CMC_R','THUMB_MCP_R']:
  pb=rig.pose.bones[name];pred=pb.bone.convert_local_to_pose(pb.matrix_basis,pb.bone.matrix_local,parent_matrix=pb.parent.matrix if pb.parent else Matrix.Identity(4),parent_matrix_local=pb.parent.bone.matrix_local if pb.parent else Matrix.Identity(4));conversion_errors[name]=max(abs(float(a-b)) for row1,row2 in zip(pred,pb.matrix) for a,b in zip(row1,row2))
 camera=dict(cams[str(f)]);camera['FINGER_DORSAL_FULL']=read(PREV/'REVIEW_CAMERAS_R1.json')['DORSAL_FULL']
 renderer=m.Renderer(camera,f'iteration_{iteration}_renders');renderer.sc.display.shading.shadow_intensity=0;renderer.draw('OLD',f'F{f:03}',Vold,F,list(camera));renderer.draw('AXIS_CORRECTED',f'F{f:03}',Vnew,F,list(camera));renderer.dispose()
 rows.append({**r,'iteration':iteration,'old_local_quaternions':old,'new_local_quaternions':{n:list(qnew[n]) for n in old},'source_anatomical_and_rig_axis_decomposition':{n:comp[n] for n in old},'parent_local_conversion_max_abs_errors':conversion_errors,'corrective_value_natural_new':float(ob.data.shape_keys.key_blocks['FIRST_WEB_OPPOSITION_CREASE_R1'].value),'first_web_visual_result':'PENDING_AGENT_VISUAL_REVIEW','fingertip_visual_result':'PENDING_AGENT_VISUAL_REVIEW','same_frame_and_source_smoothing':True,'same_camera':camera,'protected_payload_exact':True})
dump(f'DRY_RUN_ITERATION_{iteration}_R1.json',{'iteration':iteration,'generated_full_421_observation_action':False,'source_neighbor_observations_mapped_count':len(solver.cache),'frames':rows,'normal_sign_flip_count':audit['palm_local']['normal_sign_flip_count'],'source_retarg_unchanged':sha(OLD)==OLD_SHA,'baseline_unchanged':sha(BASE)==BASE_SHA})
dump('PIANOVAM_BONE_AXIS_MAPPING_R1.json',{'iteration':iteration,'four_finger_MCP':'Palm-radial anchored anatomical frame + source phalanx direction, separate flexion/abduction debug; rest-anatomical frame calibration preserves intrinsic rig rest curvature/splay/roll; convert desired armature orientation through actual parent and rest matrices','PIP_DIP':'Signed consecutive-segment bend about the anatomical digit-plane hinge; axis expressed in actual frozen bone rest-local coordinates. No axial twist or copied off-hinge direction.','THUMB_CMC':'Separate wrist-CMC neutral base plane, current CMC-MCP direction and thumb-plane diagnostic from MCP-IP; calibrated thumb anatomical frame with preserved rest roll, no unobservable source axial twist','THUMB_MCP_IP':'Signed thumb segment-to-segment hinge in palm-normal anchored thumb plane; frozen rest-local hinge axis.','no_automatic_local_X_assumption':True,'no_sign_negation_clamp_Z_deletion':True,'no_Stage6_fixture_used_by_solver':True,'no_Euler_primary_solver':True,'smoothing':'Unchanged 60fps quaternion [.25,.5,.25], neighbors only for dry-run frames','rest_local_hinge_axes':{n:list(v) for n,v in solver.hinges.items()},'rest_anatomical_MCP_frames':{n:arr(v) for n,v in solver.anatom.items()},'rest_roll_calibration_matrices':{n:arr(v) for n,v in solver.calibration.items()},'thumb_neutral_source':list(solver.thumb_neutral),'dry_run_only_before_Human_visible_screen':True})
print('DRY_RUN_DONE',iteration,'MAPPED_NEIGHBORS',len(solver.cache),'NORMAL_FLIPS',audit['palm_local']['normal_sign_flip_count'],flush=True)
