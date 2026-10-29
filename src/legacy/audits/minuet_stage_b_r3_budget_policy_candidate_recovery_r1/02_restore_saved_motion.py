from stage_common import *
import importlib.util
assert not (P/'RECOVERY_ATTEMPT.json').exists(),'ONE_RECOVERED_CANDIDATE_ONLY'
lock=read(P/'POLICY_LOCK.json');assert sha(P/'RECOVERY_POLICY.json')==lock['policy_sha256'];assert sha(G/'SOLVER_AND_GUARD_DIAGNOSTICS.json')==lock['source_guard_sha256'];assert sha(G/'SOLVER_RETURN_CHECKPOINT.json')==lock['source_solver_sha256']
policy=read(P/'RECOVERY_POLICY.json');assert policy['classification']=='WARN_ACCEPTABLE'
spec=importlib.util.spec_from_file_location('saved_restore_curve',G/'total_angle_pipeline.py');k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k);p=k.TotalAnglePipeline()
returned=read(G/'SOLVER_RETURN_CHECKPOINT.json');guard=read(G/'SOLVER_AND_GUARD_DIAGNOSTICS.json');raw=np.array(returned['raw_unknown_actual_delta_deg']);q=np.array(guard['final_total_q_deg']);assert np.array_equal(p.evaluate(raw,p.times),q)
certificate=p.certify(raw);assert certificate['domain']['pass_'] and certificate['outside_window_max_change_deg']==0 and certificate['boundary_position_and_velocity_preserved']
dump('RECOVERY_ATTEMPT.json',dict(attempt=1,status='DETERMINISTIC_RECONSTRUCTION_STARTED',source_guard_sha256=lock['source_guard_sha256'],NEW_SOLVER_CALLS=0,one_existing_numeric_object=True))
A=p.A;Q=A['L_q'].copy();inside=~p.outside_mask(p.times);flat=Q.reshape(-1,20);flat[inside]=np.radians(q)[inside]
assert np.array_equal(Q.reshape(-1,20)[~inside],A['L_q'].reshape(-1,20)[~inside])
np.savez_compressed(P/'motion.npz',**{**A,'L_q':Q})
dump('SAVED_MOTION_RECONSTRUCTION.json',dict(source_guard_sha256=lock['source_guard_sha256'],source_solver_sha256=lock['source_solver_sha256'],motion_sha256=sha(P/'motion.npz'),samples=len(p.times),raw_parameters_changed=False,output_angles_clipped=False,actual_correction_rescaled=False,root_and_key_arrays_bitwise_preserved=True,window_outside_radians_bitwise_preserved=True,NEW_SOLVER_CALLS=0,budget_reclassification='retrospective WARN, original budget failure retained',continuous_joint_domain_certificate=certificate['domain']))
dump('RECOVERY_ATTEMPT.json',dict(attempt=1,status='SAVED_NUMERIC_MOTION_RECONSTRUCTED',NEW_SOLVER_CALLS=0,motion_sha256=sha(P/'motion.npz'),Blender_candidate_saved=False))
print('SAME_SAVED_TRAJECTORY_DETERMINISTICALLY_RECONSTRUCTED',len(p.times),'NEW_SOLVER_CALLS 0',flush=True)
