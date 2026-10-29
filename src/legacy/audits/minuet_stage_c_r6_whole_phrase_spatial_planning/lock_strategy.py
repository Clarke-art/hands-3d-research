from common import *
assert not (P/'FORMAL_ATTEMPT_STARTED.json').exists()
assert read(P/'READONLY_MODEL_CHECK.json')['gate']=='CONTINUE'
assert read(P/'WHOLE_PHRASE_ROLE_PLAN.json')['old_window_locks']==[]
dump('STRATEGY_LOCK.json',dict(
    formal_attempt_limit=1,dynamic_candidate_limit=1,static_optimization_limit=0,
    preflight_gate='CONTINUE_SINGLE_ATTEMPT',preflight_meaning='No known direct hard contradiction; no proof of existence or naturalness',
    backend='scipy.optimize.minimize / trust-constr 1.18.1 / sparse AugmentedSystem',
    major_iteration_limit=200,wall_clock_sec=1800,max_objective_nfev=2000,max_spatial_evaluations=4300,
    initial_seed='C1 source absolute angles at 170 event-derived knots; no static search',
    trajectory='Single C1 cubic Hermite spline over [0,5.95], all 20 finger coordinates; zero angular endpoint velocities, free endpoint angles',
    root='Source exact Action preserved, no root variables',
    hard_constraints=['Original active moving-key pad gap [-0.5,2.1] mm and rectangle overrun <=0.5 mm',
        'Every skin vertex vs 30 real convex moving black/white key components: depth <=0.5 mm, no full-finger target exemption',
        '10 finger-pair actual skin support-envelope separation >=0 mm, conservative strong-weight ROI excluding shared palm/web',
        'Absolute engineering domains, including all cubic Bezier control values'],
    pair_limitation='Supporting envelopes are conservative; failure cannot prove physical infeasibility. Vertex key checks require independent actual triangle validation.',
    preferences=dict(angle_scale_deg=[18,25,22,14],source_velocity_scale=.025,source_acceleration_scale=.001,event_preparation_mix=.15),
    finite_difference_step_deg=.0001,gtol=.00001,xtol=.00000001,barrier_tol=.00000001,
    final_velocity_policy='Per coordinate <=1.5 * max(source peak, 60 deg/s); engineering screening, not physiological certification',
    final_acceleration_policy='Per coordinate <=1.5 * max(source peak, 1000 deg/s^2); human original-speed review still required',
    source_sha256=SOURCE_HASH,
    role_plan_sha256=sha(P/'WHOLE_PHRASE_ROLE_PLAN.json'),
    source_model_sha256=sha(P/'SOURCE_MODEL.npz'),
    code_sha256={n:sha(P/n) for n in ['trajectory_solver.py','whole_phrase_model.py','common.py']},
    failure_policy='Keep terminal numerical evidence, FAIL_CLOSED, no retry or weight/root change'))
print('ONE_STRATEGY_LOCKED',sha(P/'STRATEGY_LOCK.json'),flush=True)

