from problem import *
from persistence import atomic_json,atomic_record,load_record
pr=Problem();J=pr.sparsity();r0=pr.residual(pr.x0);assert np.isfinite(r0).all()
assert np.all(pr.sourceT[0]>=pr.state_lo-.002) and np.all(pr.sourceT[-1]<=pr.state_hi+.002)
assert np.all(pr.sourceT[-1]>=pr.state_lo-.002) and np.all(pr.sourceT[0]<=pr.state_hi+.002)
src=pr.source;bone_names=pr.source_meta['bone_names'];order=[bone_names.index(n) for n in M['bones']]
ix=np.unique(np.linspace(0,len(src['times'])-1,6).astype(int))
v,_=skin(src['joint_basis'][ix][:,order],src['rig_world'][ix],np.arange(len(W)))
fullerr=float(np.max(np.linalg.norm(v-src['vertices'][ix],axis=-1))*1000);assert fullerr<.01
pads=native_skin(pr.sourceT,pr.I,pr.padids);paderr=float(np.max(np.linalg.norm(pads-src['vertices'][pr.ixT][:,pr.padids],axis=-1))*1000);assert paderr<.03,paderr
assert float(np.ptp(pr.sourceT[:,0]))>1
# A few deterministic structural checks, no solve/alternative seed/search.
for col in [0,5,25,26,len(pr.x0)-1]:
 test=pr.x0.copy();test[col]+=min(1e-4,(pr.high[col]-test[col])/2)
 dr=pr.residual(test)-r0;allowed=J[:,col].toarray().ravel()>0
 assert np.max(abs(dr[~allowed]),initial=0)<1e-7,('INCORRECT_SPARSE_DEPENDENCY',col)
states,xy=pr.unpack(pr.x0)
atomic_record('INPUT_GATE_SCHEMA_RECORD.npz',dict(x=pr.x0,fun=r0,grad=np.zeros_like(pr.x0),active_mask=np.zeros_like(pr.x0,dtype=np.int8),control_times=pr.T,states=states,source_states=pr.sourceT,contact_xy=xy,jac_data=J.data,jac_indices=J.indices,jac_indptr=J.indptr),dict(record_type='DETERMINISTIC_INPUT_SCHEMA_TEST_NOT_OPTIMIZER_RESULT',nfev=0,njev=0,status=0,success=False,message='No optimizer run',cost=float(r0@r0/2),optimality=None,elapsed_seconds=0.,residual_calls=pr.calls,jac_shape=list(J.shape)))
a,m=load_record('INPUT_GATE_SCHEMA_RECORD.npz');assert a['states'].shape==(pr.K,26);assert np.array_equal(a['x'],pr.x0)
policy_hash=sha(O/'POLICY.json')
atomic_json('INPUT_CONTRACT_GATE.json',dict(pass_=True,formal_optimizer_calls=0,controls=pr.K,residual_times=pr.N,variables=len(pr.x0),residuals=len(r0),jacobian_shape=list(J.shape),jacobian_nnz=J.nnz,sparsity_spot_checks_pass=True,boundaries_fixed_to_actual_C1=True,full_native_LBS_parity_mm=fullerr,all_control_source_pad_reconstruction_error_mm=paderr,source_wrist_time_variation_mm=np.ptp(pr.sourceT[:,:3],axis=0),policy_sha256=policy_hash,raw_state_schema_roundtrip_pass=True,event_times_preserved=True))
atomic_json('POLICY_LOCK.json',dict(policy_sha256=policy_hash,locked_before_optimization=True,scripts={n:sha(O/n) for n in ['problem.py','persistence.py','solve.py','support.py']}))
protect();print('INPUT_CONTRACT_GATE PASS',pr.K,'time-varying states',len(pr.x0),'variables, LBS',fullerr,'mm source pad',paderr,'mm')
