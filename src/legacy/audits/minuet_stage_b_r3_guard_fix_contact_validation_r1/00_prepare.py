from stage_common import *
import shutil
assert not (P/'CANDIDATE_ATTEMPT.json').exists()
protected=set(read(ISO/'PROTECTED_INPUTS_BEFORE.json'))
protected.update(str(p) for p in ISO.rglob('*') if p.is_file())
dump('PROTECTED_INPUTS_BEFORE.json',{p:sha(p) for p in sorted(protected)})
for name in ['PERFORMANCE_TIMELINE.json','PAD_PATCHES.json']:
    shutil.copyfile(R3/name,P/name)
policy=read(R3/'GENERATION_POLICY.json')
policy.update(scope='GUARD_FIX_AND_CONTACT_VALIDATION_ONLY',curve_method='single PCHIP of bounded total angles, original113 knots, frozen PCHIP influence collars',unknown_representation='actual joint delta degrees, no unwindowed latent',envelope_role='window definition and phase metadata, never multiplied after interpolation',root_fixed=True,actual_budget_applies_to_static_and_dynamic=True,actual_budget_output_penalty_weight=6.,candidate_limit=1,formal_attempt_limit=1)
dump('GENERATION_POLICY.json',policy)
dump('BASELINE_BIND.json',dict(R2_motion_sha256=sha(R2/'motion.npz'),R2_fit_sha256=sha(R2/'COORDINATED_TRAJECTORY_FIT.json'),contact_regions_exactly_equal_R3=policy['regions']==read(R3/'GENERATION_POLICY.json')['regions'],budget_values_exactly_equal_R3=policy['joint_delta_limits_deg']==read(R3/'GENERATION_POLICY.json')['joint_delta_limits_deg'],MIDI_sha256=sha(SOURCE),source_timeline_sha256=sha(P/'PERFORMANCE_TIMELINE.json'),contact_region_source_sha256=sha(R3/'contact_region.py'),diagnostic_recorder_source_sha256=sha(ISO/'diagnostic_recorder.py'),historical_failed_trajectory_unavailable=True))
print('PROTECTED_BASELINES_BOUND_CONTACT_REGION_AND_ACTUAL_BUDGET_UNCHANGED',flush=True)
