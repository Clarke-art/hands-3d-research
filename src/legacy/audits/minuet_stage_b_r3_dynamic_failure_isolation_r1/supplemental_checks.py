"""Finite read-only checks on stored static probes; no re-solving."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1];R3=ROOT/'audits/minuet_stage_b_r3_left_hand_global_contact_placement';R2=ROOT/'audits/minuet_stage_b_r2_left_hand_continuous_accompaniment'
sys.path.insert(0,str(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'))
import numpy as np
from scipy.interpolate import PchipInterpolator
from diagnostic_recorder import write_checkpoint,joint_identities
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
pol=read(R3/'GENERATION_POLICY.json');tl=read(R3/'PERFORMANCE_TIMELINE.json');stat=read(R3/'STATIC_REACHABILITY.json');orig=read(R2/'COORDINATED_TRAJECTORY_FIT.json')
knots=np.array(orig['knots']);states=np.array(orig['solved_states']);curve=PchipInterpolator(knots,states,axis=0);A=dict(np.load(R2/'motion.npz'));times=A['times'];limits=np.array(pol['joint_delta_limits_deg'])
domain=read(ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/STATIC_REFINEMENT_POLICY_R2.json')['joint_increment_bounds_deg'];B=np.array([domain['THUMB' if j==0 else 'LONG'] for j in range(5)]);lo=B[:,0];hi=B[:,1]
def smooth(u):
    u=np.clip(u,0,1);return u*u*u*(10+u*(-15+6*u))
def env(t):
    e=np.zeros(5)
    for n in tl['notes']:
        r=smooth((t-n['note_on']+pol['source_policy']['prepare_sec'])/pol['source_policy']['prepare_sec']);f=1-smooth((t-n['note_off'])/pol['source_policy']['recovery_sec'])
        e[n['finger']-1]=max(e[n['finger']-1],r*f)
    return e
rows=[]
for test in stat['tests']:
    t=test['time'];e=env(t);actual=np.array(test['joint_delta_deg']);latent=np.divide(actual,e[:,None],out=np.zeros_like(actual),where=e[:,None]>1e-12);ref=curve(t)[6:].reshape(5,4)
    effective=e[:,None]>1e-12;low=np.maximum(-limits,lo-ref);high=np.minimum(limits,hi-ref)
    excess=np.where(effective,np.maximum(np.maximum(low-latent,latent-high),0),0)
    rows.append(dict(time=t,activity_envelope=e,actual_static_delta_deg=actual,
        reconstructed_static_latent_where_envelope_nonzero=latent,
        final_policy_latent_bound_excess_deg=float(excess.max()),
        violations=[dict(**joint_identities()[j*4+d],actual_latent_deg=float(latent[j,d]),allowed_lower_deg=float(low[j,d]),allowed_upper_deg=float(high[j,d]),excess_deg=float(excess[j,d])) for j,d in np.argwhere(excess>1e-7)],
        reconstructs_only_saved_static_probe_not_failed_dynamic_trajectory=True))
distance=np.min(abs(times[:,None]-knots[None,:]),axis=1);closest=np.min(abs(knots[:,None]-times[None,:]),axis=1)
nan=read(P/'fixtures/synthetic_nonfinite_checkpoint.json');assert nan['q_deg'][0][0]=={'nonfinite':'NaN'} and nan['violations'][0]['actual_deg']=={'nonfinite':'NaN'}
result=dict(static_probe_vs_tightened_formal_policy=rows,
    all_stored_static_latents_fit_tightened_policy=all(r['final_policy_latent_bound_excess_deg']<=1e-7 for r in rows),
    support_knots_in_output_grid=bool(np.max(closest)<1e-12),
    output_samples_not_support_knots=int(np.sum(distance>1e-12)),
    nonfinite_json_serialization_verification='PASS',
    final_failed_trajectory='UNAVAILABLE',dynamic_solve_calls=0)
write_checkpoint(P/'SUPPLEMENTAL_CHECKS.json',result)
print('STATIC_FINAL_POLICY',[(r['time'],r['final_policy_latent_bound_excess_deg']) for r in rows],flush=True)
print('OUTPUT_GRID','all knots present',result['support_knots_in_output_grid'],'nonknots',result['output_samples_not_support_knots'],'NaN record PASS',flush=True)
