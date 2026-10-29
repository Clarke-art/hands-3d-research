"""Read historical numeric evidence. No production solver execution/import."""
from pathlib import Path
import sys,json,hashlib,ast
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
R3=ROOT/'audits/minuet_stage_b_r3_left_hand_global_contact_placement'
R2=ROOT/'audits/minuet_stage_b_r2_left_hand_continuous_accompaniment'
sys.path.insert(0,str(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'))
import numpy as np
from scipy.interpolate import PchipInterpolator
from diagnostic_recorder import inspect_stage,joint_identities,write_checkpoint
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def dump(name,value):return write_checkpoint(P/name,value)

paths=set(read(R3/'PROTECTED_INPUTS_BEFORE.json'))
paths.update(str(p) for p in R3.rglob('*') if p.is_file())
before={p:sha(p) for p in sorted(paths)}
dump('PROTECTED_INPUTS_BEFORE.json',before)
inventory=[]
for p in sorted(R3.rglob('*')):
    if p.is_file():inventory.append(dict(relative_path=str(p.relative_to(R3)),bytes=p.stat().st_size,sha256=sha(p)))
failure=read(R3/'GENERATION_FAILURE.json');lock=read(R3/'GENERATION_LOCK.json')
code=(R3/'02_generate_once.py').read_text(encoding='utf8');tree=ast.parse(code)
guard=next(n for n in tree.body if isinstance(n,ast.Assert) and isinstance(n.msg,ast.Constant) and n.msg.value=='Bound exceeded: stop, no refit')
lines=code.splitlines();source_lines={str(i):lines[i-1] for i in range(max(1,guard.lineno-3),min(len(lines),guard.end_lineno+4)+1)}
save_calls=[dict(line=n.lineno,expression=ast.unparse(n)) for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,(ast.Name,ast.Attribute)) and (ast.unparse(n.func) in ['dump','np.savez_compressed'])]
numeric=[i['relative_path'] for i in inventory if Path(i['relative_path']).suffix.lower() in ['.npy','.npz','.pkl','.pickle','.h5','.hdf5','.dmp','.tmp']]
dump('EVIDENCE_INVENTORY.json',dict(R3_files=inventory,recoverable_numeric_files=numeric,
    intended_checkpoint_IO=save_calls,guard_line=guard.lineno,source_lines=source_lines,
    FINAL_FAILED_TRAJECTORY='UNAVAILABLE',last_observed_log=failure['last_visible_progress'],
    failure_record_is_reconstructed_observed_output_not_complete_solver_stdout=True,
    script_lock_valid=all(sha(R3/n)==h for n,h in lock['scripts'].items()),policy_lock_valid=sha(R3/'GENERATION_POLICY.json')==lock['policy_sha256'],
    no_original_fit_or_latent_or_output_arrays_saved=True))

policyfile=ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/STATIC_REFINEMENT_POLICY_R2.json'
sp=read(policyfile);domains=sp['joint_increment_bounds_deg'];bounds=np.array([domains['THUMB' if j==0 else 'LONG'] for j in range(5)])
lo=bounds[:,0].ravel();hi=bounds[:,1].ravel();tl=read(R3/'PERFORMANCE_TIMELINE.json');used=sorted(set(n['finger'] for n in tl['notes']))
assert used==[1,2,3,4,5]
orig=read(R2/'COORDINATED_TRAJECTORY_FIT.json');knots=np.array(orig['knots']);states=np.array(orig['solved_states']);A=dict(np.load(R2/'motion.npz'));times=A['times'];q0=np.degrees(A['L_q']).reshape(-1,20)
curve=PchipInterpolator(knots,states,axis=0);reconstructed=curve(times)
supports=inspect_stage('R2_ORIGINAL_SUPPORT_KNOTS',knots,states[:,6:],lo,hi)
output=inspect_stage('R2_ORIGINAL_SAVED_827_SAMPLES',times,q0,lo,hi)
table=[]
for j,identity in enumerate(joint_identities()):
    table.append(dict(**identity,lower_deg=float(lo[j]),upper_deg=float(hi[j]),
        R2_min_deg=float(np.min(q0[:,j])),R2_max_deg=float(np.max(q0[:,j])),
        R2_min_bound_slack_deg=float(np.min(np.minimum(q0[:,j]-lo[j],hi[j]-q0[:,j]))),
        R2_samples_within_1e_minus7_of_boundary=int(np.sum(np.minimum(q0[:,j]-lo[j],hi[j]-q0[:,j])<=1e-7))))
stat=read(R3/'STATIC_REACHABILITY.json');staticrows=[]
for test in stat['tests']:
    t=test['time'];ref=curve(t);delta=np.asarray(test['joint_delta_deg']);q=ref[6:]+delta.ravel()
    ss=inspect_stage('R3_SAVED_STATIC_PROBE',np.array([t]),q[None,:],lo,hi)
    staticrows.append(dict(time=t,solver_success=test['solver_success'],nfev=test['nfev'],joint_delta_deg=delta,actual_joint_values_deg=q,
        min_joint_bound_slack_deg=float(np.min(np.minimum(q-lo,hi-q))),joint_guard_pass=ss['pass_'],active=test['active']))
pol=read(R3/'GENERATION_POLICY.json')
def smooth(u):
    u=np.clip(u,0,1);return u*u*u*(10+u*(-15+6*u))
def envelope(t):
    e=np.zeros((len(t),5))
    for n in tl['notes']:
        rise=smooth((t-n['note_on']+pol['source_policy']['prepare_sec'])/pol['source_policy']['prepare_sec']);fall=1-smooth((t-n['note_off'])/pol['source_policy']['recovery_sec'])
        e[:,n['finger']-1]=np.maximum(e[:,n['finger']-1],rise*fall)
    return e
outenv=envelope(times);kenv=envelope(knots)
qnoop=q0+PchipInterpolator(knots,np.zeros((len(knots),20)),axis=0)(times)*np.repeat(outenv,4,axis=1)
zero=inspect_stage('R2_WITH_IDENTICALLY_ZERO_SYNTHETIC_CORRECTION',times,qnoop,lo,hi)
dump('READ_ONLY_BASELINE_AND_DOMAIN_CHECKS.json',dict(bounds_source=str(policyfile),bounds_source_sha256=sha(policyfile),engineering_not_physiological_limits=True,
    domain_meaning=domains['meaning'],used_fingers=used,index_map_and_baseline_slack=table,
    samples=len(times),support_knots=len(knots),time_range=[float(times.min()),float(times.max())],knots_range=[float(knots.min()),float(knots.max())],
    extrapolated_original_samples=int(np.sum((times<knots[0])|(times>knots[-1]))),
    R2_support_guard_pass=supports['pass_'],R2_output_guard_pass=output['pass_'],
    R2_saved_q_vs_PCHIP_reference_max_abs_deg=float(np.max(abs(q0-reconstructed[:,6:]))),
    zero_correction_guard_pass=zero['pass_'],zero_correction_max_change_deg=float(np.max(abs(qnoop-q0))),
    envelope_min=float(outenv.min()),envelope_max=float(outenv.max()),
    degrees_to_radians_roundtrip_max_abs_deg=float(np.max(abs(q0-np.degrees(np.radians(q0))))),
    R3_static_saved_probe_rechecks=staticrows,static_probe_count=len(staticrows),
    static_all_inside_original_joint_domain=all(r['joint_guard_pass'] for r in staticrows),
    static_saved_max_delta_deg=float(np.max(np.abs([r['joint_delta_deg'] for r in staticrows]))),
    static_points_are_not_failed_dynamic_samples=True,no_solver_invocations=True,
    current_scipy_version=__import__('scipy').__version__))
print('READ_ONLY_EVIDENCE',len(inventory),'R3 files',numeric,'guard line',guard.lineno,flush=True)
print('R2_DOMAIN',supports['pass_'],output['pass_'],'zero',zero['pass_'],'reference parity',np.max(abs(q0-reconstructed[:,6:])),flush=True)
print('STATIC_RECHECK',len(staticrows),all(r['joint_guard_pass'] for r in staticrows),'max delta',max(np.max(abs(r['joint_delta_deg'])) for r in staticrows),flush=True)
