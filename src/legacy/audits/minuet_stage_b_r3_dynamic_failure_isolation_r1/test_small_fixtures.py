"""Fixed small artificial arrays only. Never run a hand planner or optimizer."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
sys.path.insert(0,str(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'))
import numpy as np
from scipy.interpolate import PchipInterpolator
from diagnostic_recorder import inspect_stage,write_checkpoint,record_before_guard
sp=json.loads((ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/STATIC_REFINEMENT_POLICY_R2.json').read_text(encoding='utf8'))
b=np.array([sp['joint_increment_bounds_deg']['THUMB' if j==0 else 'LONG'] for j in range(5)]);lo=b[:,0].ravel();hi=b[:,1].ravel();checks=[]
baseline=np.tile((lo+hi)/2,(2,1));t=np.array([0.,.25]);copy=baseline.copy()
valid=inspect_stage('SYNTHETIC_LEGAL',t,baseline,lo,hi);assert valid['pass_'];assert np.array_equal(copy,baseline);checks.append('legal arrays unchanged')
bad=baseline.copy();bad[1,2]=-.125;bad[1,19]=30.
summary=inspect_stage('SYNTHETIC_OUT_OF_DOMAIN',t,bad,lo,hi);assert summary['violation_count']==2
assert summary['violations'][0]['joint']=='IP' and summary['violations'][0]['finger']==1 and summary['violations'][0]['excess_deg']==.125
assert summary['violations'][1]['finger']==5 and summary['violations'][1]['dof']=='BASE_SPREAD_INCREMENT' and summary['violations'][1]['excess_deg']==5.
checks.append('lower/upper, time, hand/finger/joint/DOF/units correctly recorded')
invalid=baseline.copy();invalid[0,0]=np.nan
nan=inspect_stage('SYNTHETIC_NONFINITE',t,invalid,lo,hi);assert nan['nonfinite_count']==1 and not nan['pass_'];checks.append('nonfinite separate from finite limit excess')
knots=np.array([0.,1.,2.]);reference=np.tile((lo+hi)/2,(3,1));latent=np.zeros((3,20))
reference[:,0]=[22.,24.7,25.];latent[:,0]=[3.,.3,-.3]
combined=reference+latent;grid=np.linspace(0.,2.,201)
separate=PchipInterpolator(knots,reference,axis=0)(grid)+PchipInterpolator(knots,latent,axis=0)(grid)
single=PchipInterpolator(knots,combined,axis=0)(grid)
knotcheck=inspect_stage('SYNTHETIC_LEGAL_KNOT_SUM',knots,combined,lo,hi)
separatecheck=inspect_stage('SYNTHETIC_SEPARATE_INTERPOLATION_SUM',grid,separate,lo,hi)
singlecheck=inspect_stage('SYNTHETIC_TOTAL_Q_INTERPOLATION',grid,single,lo,hi)
assert knotcheck['pass_'] and not separatecheck['pass_'] and singlecheck['pass_']
checks.append('legal knot sums can violate domain after separately interpolated addition; NOT original failed trajectory')
fixture_meta=dict(origin='ARTIFICIAL_ARRAY_FIXTURE_ONLY',nfev=7,success=True,status=1,message='Synthetic metadata; no optimizer executed',cost=0.,optimality=0.,max_nfev=10,residual_callback_calls=3303)
destination=P/'fixtures'/'synthetic_failure_checkpoint.json'
allowed=record_before_guard(destination,fixture_meta,[knotcheck,separatecheck],dict(knots_sec=knots,reference_q_deg=reference,latent_correction_deg=latent,envelope=1.),{},origin='ARTIFICIAL_ARRAYS_NOT_R3_FAILURE_SCENE')
assert not allowed and destination.exists()
stored=json.loads(destination.read_text(encoding='utf8'));assert stored['solver']['nfev']==7 and stored['solver']['residual_callback_calls']==3303
checks.append('checkpoint exists before rejection; returned nfev not replaced by callback counter')
try:write_checkpoint(destination,{'overwrite':True})
except FileExistsError:checks.append('existing evidence cannot be overwritten')
else:raise AssertionError('Exclusive checkpoint write failed')
write_checkpoint(P/'fixtures'/'synthetic_nonfinite_checkpoint.json',nan)
result=dict(origin='ARTIFICIAL_ARRAY_FIXTURES_ONLY',bounded_test_cases=7,checks=checks,
    synthetic_reference_thumb_CMC_deg=reference[:,0],synthetic_latent_thumb_CMC_deg=latent[:,0],
    synthetic_knot_sums_deg=combined[:,0],synthetic_joint_allowed_deg=[float(lo[0]),float(hi[0])],
    knot_guard_pass=knotcheck['pass_'],separate_interpolation_guard_pass=separatecheck['pass_'],total_q_interpolation_guard_pass=singlecheck['pass_'],
    separate_interpolation_max_excess_deg=separatecheck['max_finite_excess_deg'],
    worst_synthetic_sample=max(separatecheck['violations'],key=lambda r:r['excess_deg']),
    R3_original_failure_localized=False,production_solver_invocations=0,new_dynamic_candidates=0,
    no_motion_npz_or_Action_created=True,not_a_candidate_or_reconstructed_failure=True)
write_checkpoint(P/'SMALL_FIXTURE_VERIFICATION.json',result)
print('SEVEN_SMALL_FIXTURE_CHECKS_PASS','synthetic max excess',separatecheck['max_finite_excess_deg'],'worst',result['worst_synthetic_sample'],flush=True)
