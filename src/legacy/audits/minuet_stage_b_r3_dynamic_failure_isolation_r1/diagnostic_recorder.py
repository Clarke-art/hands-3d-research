"""Independent failure evidence recorder. No solver, FK, clipping, or animation.

Invoke only in a newly authorized run directory. Stages are caller-supplied
numerical diagnostics, never an automatically generated motion candidate.
"""
from pathlib import Path
import json, math, os
import numpy as np

def joint_identities():
    rows=[]
    for j,digit in enumerate(['THUMB','INDEX','MIDDLE','RING','LITTLE']):
        joints=['CMC','MCP','IP'] if j==0 else ['MCP','PIP','DIP']
        for d in range(4):
            rows.append(dict(flat_index=j*4+d,hand='L',finger=j+1,digit=digit,
                joint=joints[d] if d<3 else joints[0],
                dof='FLEXION_INCREMENT' if d<3 else 'BASE_SPREAD_INCREMENT',
                unit='degrees relative to existing curved RSSF rest'))
    return rows

def inspect_stage(name,times,q_deg,lower_deg,upper_deg,identities=None,tolerance_deg=1e-7):
    times=np.asarray(times,dtype=float);q=np.asarray(q_deg,dtype=float)
    if q.ndim==3 and q.shape[1:]==(5,4):q=q.reshape(len(q),20)
    lo=np.asarray(lower_deg,dtype=float).ravel();hi=np.asarray(upper_deg,dtype=float).ravel()
    ids=joint_identities() if identities is None else identities
    if q.ndim!=2 or q.shape!=(len(times),len(ids)) or lo.shape!=(len(ids),) or hi.shape!=(len(ids),):
        raise ValueError('Explicit time/DOF/boundary shapes required')
    if not np.isfinite(times).all() or not np.all(np.diff(times)>0) or not np.isfinite(lo).all() or not np.isfinite(hi).all() or not np.all(lo<=hi):
        raise ValueError('Finite increasing times and finite ordered boundaries required')
    finite=np.isfinite(q);bad=(~finite)|(q<lo-tolerance_deg)|(q>hi+tolerance_deg)
    violations=[]
    for i,j in np.argwhere(bad):
        value=float(q[i,j]);amount=max(lo[j]-value,value-hi[j],0.) if finite[i,j] else None
        violations.append(dict(stage=name,sample_index=int(i),time_sec=float(times[i]),**ids[j],
            actual_deg=value,allowed_lower_deg=float(lo[j]),allowed_upper_deg=float(hi[j]),
            excess_deg=None if amount is None else float(amount),finite=bool(finite[i,j])))
    finite_excess=np.maximum(np.maximum(lo-q,q-hi),0.)
    return dict(stage=name,samples=len(times),dofs=len(ids),tolerance_deg=tolerance_deg,
        pass_=not violations,violation_count=len(violations),nonfinite_count=int(np.sum(~finite)),
        max_finite_excess_deg=float(np.max(finite_excess[finite])) if np.any(finite) else None,
        violations=violations,times_sec=times,q_deg=q,lower_deg=lo,upper_deg=hi)

def _serializable(value):
    if isinstance(value,np.ndarray):return _serializable(value.tolist())
    if isinstance(value,np.generic):return _serializable(value.item())
    if isinstance(value,float) and not math.isfinite(value):
        return {'nonfinite': 'NaN' if math.isnan(value) else ('+Infinity' if value>0 else '-Infinity')}
    if isinstance(value,dict):return {str(k):_serializable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [_serializable(v) for v in value]
    return value

def write_checkpoint(path,payload):
    """Exclusive output plus fsync; never overwrite an existing run artifact."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    encoded=json.dumps(_serializable(payload),ensure_ascii=False,indent=2,allow_nan=False)
    with path.open('x',encoding='utf8') as f:
        f.write(encoded);f.flush();os.fsync(f.fileno())
    return str(path)

def record_before_guard(path,solver_metadata,stages,reference_inputs,source_hashes,origin):
    # nfev belongs to the returned optimizer, never to a residual callback.
    required=['nfev','success','status','message','cost','optimality','max_nfev']
    if any(k not in solver_metadata for k in required):raise ValueError('Explicit returned optimizer metadata required')
    payload=dict(origin=origin,solver=solver_metadata,stages=stages,
        reference_inputs=reference_inputs,source_hashes=source_hashes,
        dynamic_candidate=False,read_only_of_input_arrays=True,
        violation_localization_saved_before_guard=True)
    write_checkpoint(path,payload)
    return all(s['pass_'] for s in stages)
