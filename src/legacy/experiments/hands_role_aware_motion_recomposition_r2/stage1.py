from representation import *
assert read(O/'STAGE0_BLENDER_GATE.json')['pass_']
r=Representation();F=r.features;rebuild=np.array([r.frame(float(t),False)@u for t,u in zip(r.t,r.relative)])
err=float(abs(rebuild-F['wrist_relative_world']).max());assert err<1e-8
qback=r.neutral+r.q(r.t);qerr=float(abs(qback-F['q_prior']).max());assert qerr<1e-9
padlocal=[];padback=[]
for t,pads in zip(r.t,F['skin_pads']):
    k=r.frame(float(t),False);h=np.c_[pads,np.ones(5)];local=<REDACTED_EMAIL>(k).T;padlocal.append(local[:,:3]);padback.append((local@k.T)[:,:3])
paderr=float(np.linalg.norm(np.array(padback)-F['skin_pads'],axis=-1).max()*1000);assert paderr<.001
atomic_record('KEY_RELATIVE_ROLE_REPRESENTATION.npz',dict(times=r.t,event_phase_times=r.t-r.source[1]['note_on'],shared_rig_in_key_frame=r.relative,RSSF_relative_q_deg=F['q_prior']-r.neutral,
    source_joint_velocity_deg_s=r.q.derivative()(r.t),source_skin_pads_in_key_frame=padlocal,source_contact_fraction=r.fractions),dict(record_type='ONE_KEY_RELATIVE_ROLE_REPRESENTATION',source='R04 C5(4) -> R05 D5(5)',context=['R03','R06'],source_idle_curves_not_safe_templates=True,target_q_trace_used=False))
atomic_json('REPRESENTATION_READBACK.json',dict(pass_=True,world_matrix_error=err,RSSF_q_error_deg=qerr,skin_pad_error_mm=paderr,source_samples=len(r.t),frame_definition='Moving playable key inset/contact frame; quintic event-anchor blend; one shared wrist transform',
    target_adaptation='Real black/white playable x/y/z extents and Action rotation, not fixed world translation',source_safety_claim=False))
# Lock before formal strategy: original eight coordination coefficients, local six-variable IK.
P=read(SRC/'POLICY.json');policy=dict(task='HANDS_ROLE_AWARE_MOTION_RECOMPOSITION_R2',outer_parameters=P['outer_parameters'],outer_max_nfev=18,outer_support_count=16,
    local_variables=['MCP_or_CMC_deg','PIP_or_MCP_deg','DIP_or_IP_deg','spread_deg','key_local_X_mm','key_local_Y_mm'],local_max_nfev=12,local_call_limit=160,
    support_spacing_sec=.025,numerical_limit_seconds=180.,joint_bounds_deg=P['joint_bounds_deg'],contact_horizontal_mm=.03,contact_vertical_abs_mm=3.,wrong_key_depth_mm=.5,nonregression_mm=.02,added_joint_velocity_deg_s=180.,
    contact_weight=6.,clearance_weight=2.,joint_prior_weight=.055,xy_prior_weight=.12,temporal_prior_weight=.08,outer_prior_weight=.10,
    sources=1,targets=1,representations=1,formal_strategies=1,candidate_limit=1,restarts=0,seed_search=False,retuning=False,
    method='One eight-coefficient role/root fit, then original bounded local skin-contact IK at event/phase supports, one Hermite/PCHIP curve with source priors and endpoint conditions',
    target_generation_q_samples='Only six boundary derivative samples; no interior Q',key_neighborhood_midi=[64,82])
atomic_json('POLICY.json',policy)
atomic_json('GENERATION_LOCK.json',dict(policy_sha256=sha(O/'POLICY.json'),representation_sha256=sha(O/'KEY_RELATIVE_ROLE_REPRESENTATION.npz'),implementation_sha256={p.name:sha(p) for p in O.glob('*.py')},formal_solver_calls=0))
protect();print('KEY_RELATIVE_REPRESENTATION_READBACK_PASS',err,qerr,paderr,flush=True)
