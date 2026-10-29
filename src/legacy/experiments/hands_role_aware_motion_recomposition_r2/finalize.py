from bootstrap import *
from collections import Counter
I=read(O/'INPUT_BINDINGS.json');man=I['scene'];before=read(O/'PROTECTED_BEFORE.json');after={p:sha(valid_path(p)) for p in before}
assert before==after,'REFERENCED_HISTORICAL_INPUT_SHA_CHANGED'
lock=read(O/'FORMAL_CODE_LOCK.json');motion_modules=['generate.py','representation.py','bootstrap.py','model.py','support.py','persistence.py']
assert all(sha(O/p)==lock['scripts'][p] for p in motion_modules),'FORMAL_MOVEMENT_CODE_CHANGED'
assert sha(O/'POLICY.json')==lock['policy_sha256']
closed=read(CLOSE/'FINAL_PROTECTION.json')['after_sha256'];static_hashes={}
for i in range(3):
    p=SRC/('SOURCE_LOCAL_RESULT_'+str(i)+'.npz');actual=sha(p);assert actual==closed[str(p)];static_hashes[str(p)]=actual
assert sha(man['path'])==man['sha256']
blender=read(O/'BLENDER_CANDIDATE_GATE.json');assert not blender['pass_']
G=read(O/'DYNAMIC_BLENDER_GEOMETRY.json');L=read(O/'NUMERICAL_LEDGER.json');F=read(O/'FAILURE_AND_SURFACE_SUMMARY.json');D=read(O/'CONTINUOUS_DOMAIN_READBACK.json');V=read(O/'CONTINUITY_AND_ROLE_DIAGNOSTICS.json')
event_stats={}
for which,label in [('rows','candidate'),('baseline_rows','baseline')]:
    event_stats[label]={}
    for event in ['R11','R12','R13','R14']:
        cs=[c for row in G[which] for c in row['contacts'] if c['event']==event]
        event_stats[label][event]=dict(samples=len(cs),failures=sum(not c['pass_'] for c in cs),horizontal_max_mm=max(c['horizontal_mm'] for c in cs),gap_abs_max_mm=max(abs(c['gap_mm']) for c in cs))
local_counts=Counter()
for p in O.glob('LOCAL_RESULT_*.npz'):
    a,meta=archive(p);local_counts['success' if meta['success'] else 'returned_at_limit']+=1
surface_max=max(F['surface_witnesses'],key=lambda s:s['candidate']['non_target_surface_bounds_mm'][0])
result=dict(task='HANDS_ROLE_AWARE_MOTION_RECOMPOSITION_R2',RESULT='GENERATED_WITH_DEFECTS',LOW_COMPLEXITY_RECOMPOSITION='NOT_SUPPORTED_WITHIN_SCOPE',HUMAN_NATURALNESS='NOT_TESTED',
    source_count=1,target_count=1,representation_count=1,strategy_starts=1,dynamic_candidates=1,restarts=0,numerical_seconds=L['seconds'],numerical_limit_seconds=180,
    machine_contact_pass=False,product_geometry_pass=False,continuous_joint_domain_pass=D['joint_domain_pass'],prior_A2_root_world_range_comparison_pass=D['root_sample_domains']['candidate']['pass_'],root_range_comparison_is_new_gate=False,added_velocity_pass=False,
    acceptance_FAIL_basis=['original contact contract','original added velocity gate','actual non-target key and finger geometry'],
    target_C1_q_trace_generation_input=False,boundary_q_samples_generation_input=6,posthoc_reference_read_after_candidate=True,
    event_stats=event_stats,whole_hand_regression_count=F['whole_hand_new_regression_count'],unique_regression_sample_times=len({v['time'] for v in F['whole_hand_new_regression_records']}),
    actual_dynamic_samples=G['actual_sample_count'],real_skin_reconstruction_error_max_mm=G['native_skin_error_max_mm'],non_target_vertex_max_mm=blender['non_target_vertex_peak_mm'],
    exact_joint_speed_max_deg_s=V['exact_Hermite_joint_speed_peak_deg_s'],surface_failure_witness=surface_max,local_termination_counts=dict(local_counts),
    Actions_saved=0,Blends_saved=0,videos=0,original_asset_hashes_unchanged=True,piano_access=False,STOP='HUMAN REVIEW')
atomic_json('FINAL_RESULT.json',result)
atomic_json('PROTECTION_CHECK.json',dict(pass_=True,before_sha256=before,after_sha256=after,referenced_files=len(before),original_static_result_sha256=static_hashes,
    formal_movement_modules_unchanged=True,policy_sha256=sha(O/'POLICY.json'),candidate_sha256=sha(O/'MOTION_CANDIDATE.npz'),curve_sha256=sha(O/'CONTINUOUS_CURVE.npz'),
    diagnostic_software_repair_separate_from_motion=True,wrapper_change_after_generation='run.py diagnostic retry log separation only; no generation retry',
    original_scene_sha256=man['sha256'],original_native_sha256=blender['original_native_sha256'],original_actions_sha256=blender['original_actions_sha256'],
    prior_concurrency_FAILURE_evidence_not_touched=True,piano_access=False))
print('FINAL',result['RESULT'],result['LOW_COMPLEXITY_RECOMPOSITION'],'SHA_FILES',len(before),'LOCAL_RETURNS',dict(local_counts),flush=True)
