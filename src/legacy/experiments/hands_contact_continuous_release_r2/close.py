from path_model import *
r=read(OUT/'ACTUAL_PATH_VALIDATION.json');p=read(OUT/'PATH_PREFLIGHT_RESULT.json');a=dict(np.load(OUT/'ACTUAL_PATH_ANGLES.npz'));curve=Curve();path=dict(np.load(OUT/'PATH_PREFLIGHT.npz'));x=path['coefficients']
contacts=[]
for event in sorted({v['event'] for v in r['contacts']}):
    rows=[v for v in r['contacts'] if v['event']==event]
    contacts.append(dict(event=event,records=len(rows),failed=sum(not v['pass_'] for v in rows),
        max_absolute_gap_mm=max(abs(v['gap_mm']) for v in rows),max_horizontal_mm=max(v['horizontal_mm'] for v in rows)))
q=a['new_qdeg'][:,CHANGED];low=np.array([0,0,0,-28]);high=np.array([75,95,65,28]);violation=np.maximum(low-q,q-high)
idx=np.unravel_index(int(np.argmax(violation)),violation.shape)
boundary_times=np.unique([START,END,SCOPE['old']['note_off'],SCOPE['old']['note_off']+POL['finger_release_follow_sec'],SCOPE['new']['note_off'],curve.middle_begin,curve.middle_begin+POL['finger_release_follow_sec']])
phase=[]
for t in boundary_times:
    eps=1e-8;delta=curve.delta(x,np.array([max(START,t-eps),t,min(END,t+eps)]))
    phase.append(dict(t=float(t),left_right_position_difference_deg=float(abs(delta[2]-delta[0]).max()),
        added_curve_continuity='Cubic C2 spline times quintic C2 gate; zero value and derivative at window endpoints analytically'))
save('FINAL_METRICS.json',dict(actual_samples=r['samples'],source_peak_pairs=max(v['source_pairs'] for v in r['rows']),new_peak_pairs=r['max_skin_pairs'],
    source_collision_samples=sum(v['source_pairs']>0 for v in r['rows']),new_collision_samples=r['skin_collision_samples'],
    new_collision_first_observed=next(v['t'] for v in r['rows'] if v['new_pairs']),new_collision_last_observed=next(v['t'] for v in reversed(r['rows']) if v['new_pairs']),
    first_new_key_surface_crossing=r['first_failure_observed'],first_pointwise_depth_witness=next(w for w in r['witnesses'] if w['key_witnesses']),
    contacts=contacts,key_regression_samples=r['key_regression_samples'],surface_regression_samples=r['surface_regression_samples'],
    domain_witness=dict(t=float(a['times'][idx[0]]),digit=c.DIGITS[CHANGED[idx[1]]],coordinate=['MCP_FLEX','PIP_FLEX','DIP_FLEX','MCP_SPREAD'][idx[2]],
        actual_angle_deg=float(q[idx]),violation_deg=float(violation[idx])),
    source_actions_preserved=True,formal_dynamic_candidates=0))
save('PHASE_CURVE_CONTINUITY.json',dict(rows=phase,maximum_near_boundary_position_difference_deg=max(v['left_right_position_difference_deg'] for v in phase),
    analytic_added_field_C2=True,actual_domain_and_speed_pass=False,
    limitations='Continuity of the correction field does not certify original quaternion bake velocity, contact or collision. Actual finite-difference speed failed; no Action baked.'))
protect_after()
extra=read(OUT/'ADDITIONAL_PROTECTED_BEFORE.json');assert all(sha(f)==h for f,h in extra.items())
protected=read(OUT/'PROTECTION_CHECK.json');protected['additional_helper_files']=len(extra);protected['total_referenced_files']=protected['files']+len(extra);save('PROTECTION_CHECK.json',protected)
save('FINAL_STATUS.json',dict(task='HANDS_CONTACT_CONTINUOUS_RELEASE_R2',status='FAIL',
    off_target_jump_fixed=True,envelope_accuracy='PARTIAL_FALSE_POSITIVES_REMAIN',legal_continuous_path_found=False,
    path_schemes=1,continuous_optimizer_calls=1,static_optimizer_calls=0,formal_dynamic_candidates=0,new_actions=0,new_blends=0,new_videos=0,
    human_naturalness='NO_LEGAL_CANDIDATE_NOT_ASSESSED',
    stop_current_local_portal_static_fk_ik_mechanism_expansion=True,next_allowed_scope='Technical route decision only; no implementation',stop='STOP — HUMAN REVIEW'))
print('R2_STOP_CURRENT_MECHANISM',protected['total_referenced_files'],'protected files unchanged; no candidate',flush=True)
