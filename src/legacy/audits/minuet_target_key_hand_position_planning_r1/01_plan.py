from stage_common import *
from target_key_planner import TargetKeyPlanner
assert not (P/'PLANNING_LOCK.json').exists()
tl=read(P/'PERFORMANCE_TIMELINE.json');lock=read(P/'INPUT_LOCK.json')
assert sha(P/'PERFORMANCE_TIMELINE.json')==lock['timeline_sha256']
planner=TargetKeyPlanner(c.KEYS,o.ANCHORS,'R');plan=planner.plan(tl['notes'])
dump('TARGET_KEY_AND_ROOT_PLAN.json',plan)
# Same interface/code; transposed data only, no joints/action/trajectory generation.
other=[]
for n in tl['notes']:
    nn=dict(n,midi_note=n['midi_note']-2,key_index=n['key_index']-2);other.append(nn)
second=planner.plan(other)
dump('ALTERNATE_TARGET_PLANNING_CHECK.json',dict(mode='PLANNING_ONLY_NO_SECOND_MOTION',
    transposition_semitones=-2,event_count=len(other),code_sha256=sha(P/'target_key_planner.py'),
    valid_all_key_targets=True,unique_midis=sorted(set(n['midi_note'] for n in other)),
    segment_count=len(second['segments']),right_actions=0,new_candidates=0,
    black_targets=sum(t['color']=='BLACK' for t in second['key_targets'].values()),
    root_deltas=[s['delta'] for s in second['segments']],
    claim='Interface accepts different pitches without edits. Does not qualify alternate physical performance.'))
policy=dict(candidate_limit=1,no_restarts=True,no_post_render_refingering=True,
    joint_bounds_deg=o.SP['joint_increment_bounds_deg'],prepare_sec=.10,
    key_press_sec=.035,key_release_sec=.07,recovery_sec=.08,
    root_transition_before_sec=.20,root_transition_after_sec=.08,
    joint_solver_max_nfev=35,contact_weight_mm=6,joint_prior_weight_rad=3,
    joint_temporal_weight_rad=1,contact_surface_gap_mm=.5,
    collision_diagnostics='Finite pad/skin neighborhood checks after readback; no vertex-forensic repair.',
    failure_policy='Render the one finite candidate even with contact WARN/FAIL; block PASS, no parameter retries.')
dump('GENERATION_POLICY.json',policy)
scripts=['stage_common.py','target_key_planner.py','00_scope.py','01_plan.py','02_generate.py','03_scene.py']
dump('PLANNING_LOCK.json',dict(input_sha256=sha(P/'INPUT_LOCK.json'),
    plan_sha256=sha(P/'TARGET_KEY_AND_ROOT_PLAN.json'),policy_sha256=sha(P/'GENERATION_POLICY.json'),
    scripts={n:sha(P/n) for n in scripts},candidate_limit=1))
print('PLAN',[(s['first_id'],s['last_id'],s['delta']) for s in plan['segments']],flush=True)
