from recovery_kernel import *
A=dict(np.load(P/'motion.npz'));O=dict(np.load(R2/'motion.npz'));d=read(P/'ENGINEERING_DIAGNOSTICS.json');scene=read(P/'SCENE_MANIFEST.json');policy=read(P/'RECOVERY_POLICY.json')
allrows=d['notes'];allimproved=all(r['summary']['pad_margin_improvement_mm']>0 and r['summary']['all_finite_pad_P90_inside'] for r in allrows)
function=all(r['summary']['all_centers_inside'] and max(abs(r['summary']['gap_min_mm']),abs(r['summary']['gap_max_mm']))<=3 for r in allrows)
function&=d['triad_pressure_max_difference']<1e-6 and scene['key_angle_parity_max_rad']<1e-5
penetration=max(r['after']['max_sampled_penetration_mm'] for r in d['finite_skin_probe_collision'])
clearance=penetration<=3
root=all(np.array_equal(A[k],O[k]) for k in A if k!='L_q')
timeline=sha(P/'PERFORMANCE_TIMELINE.json')==sha(R2/'PERFORMANCE_TIMELINE.json')
readback=scene['save_reopen_verified'] and scene['actual_pad_vs_FK_max_mm']<.03 and scene['actual_key_world_parity_max_mm']<.03
pass_=bool(function and clearance and root and timeline and readback and d['joint_bounds_excess_deg']<=1e-7 and policy['classification']=='WARN_ACCEPTABLE')
dump('ENGINEERING_GATE.json',dict(pass_=pass_,music_functional_correctness='PASS' if function and timeline else 'FAIL',finite_key_penetration_safety='PASS' if clearance else 'FAIL',finite_max_key_penetration_mm=penetration,root_and_key_arrays_bitwise_preserved=root,original_timeline_preserved=timeline,actual_Blend_readback_pass=readback,all_seven_active_contact_geometry_improved=allimproved,budget_policy_warn_retained=True,NEW_SOLVER_CALLS=0,Human_visible_quality='HUMAN_PENDING',normal_speed_visual_agent_review_still_required=True,contact_tolerance_mm=3,finite_dangerous_penetration_gate_mm=3,gate_source='inherited static engineering contact tolerance and dangerous penetration screen, not motion-budget relaxation'))
print('ACTUAL_ENGINEERING_GATE',pass_,'ALL7_GEOMETRY_IMPROVED',allimproved,'penetration',penetration,flush=True)
if not pass_:raise RuntimeError('FAIL_CLOSED_ACTUAL_ENGINEERING_GATE_NO_REFIT')
