"""Read-only historical model, isolated deterministic constraint/Jacobian review.
No optimizer, action, pose archive or trajectory writer is called.
"""
import sys, os, types, time, json, hashlib
from pathlib import Path
sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
HIST = ROOT/'experiments/hands_sparse_window_constrained_trajectory_feasibility_r1'
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', TEMP=str(OUT), TMP=str(OUT))

def load(name, replacements=()):
    p=HIST/(name+'.py'); source=p.read_text(encoding='utf-8-sig')
    for before,after in replacements:
        assert source.count(before)==1, before
        source=source.replace(before,after)
    module=types.ModuleType(name); module.__file__=str(p);sys.modules[name]=module
    exec(compile(source,str(p),'exec'),module.__dict__)
    return module

io=load('io_core', [('O = Path(__file__).resolve().parent', 'O = Path('+repr(str(OUT))+')')])
# io_core's ROOT=O.parents[1] remains the Hands root; its write and reparse guards stay enabled.
io.READS[str(HIST/'io_core.py')]=io.sha(HIST/'io_core.py')
n=load('native_model')
w=load('window_problem', [("archive(O/'BASELINE_ACTUAL.npz')", "archive(Path("+repr(str(HIST))+ ")/'BASELINE_ACTUAL.npz')")])
for name in ['native_model','window_problem']:
    io.READS[str(HIST/(name+'.py'))]=io.sha(HIST/(name+'.py'))
import numpy as np
import scipy
from scipy.sparse import csr_matrix
from scipy.optimize._numdiff import approx_derivative, group_columns

def fast_skin(basis,world,ids):
    """Distribute linear skinning over fixed base and corrective; no weight threshold."""
    poses=n.forward(basis)
    opp=np.arctan2(basis[:,n.BN['THUMB_CMC_R'],2,1],basis[:,n.BN['THUMB_CMC_R'],2,2])
    mcp=np.arctan2(basis[:,n.BN['THUMB_MCP_R'],2,1],basis[:,n.BN['THUMB_MCP_R'],2,2])
    shape=np.maximum(np.clip((-opp-.37)/.06,0,1),np.clip((-opp-.15)/.15,0,1)*np.clip((-mcp-.175)/.175,0,1))
    V=np.einsum('kbij,bvj->kvi',poses,n.LOCAL[:,ids],optimize=True)
    V+=shape[:,None,None]*np.einsum('kbij,bvj->kvi',poses,n.SHLOCAL[:,ids],optimize=True)
    return np.einsum('kij,kvj->kvi',world,V)[:,:,:3],poses

def fast_native(q,world,ids=None):
    q=np.asarray(q);q=q[None] if q.ndim==2 else q
    world=np.asarray(world);world=world[None] if world.ndim==2 else world
    return fast_skin(n.basis(q),np.broadcast_to(world,(len(q),4,4)),np.arange(len(n.W)) if ids is None else ids)[0]

def fast_geometry(self,V):
    # Identical local transform, plane max and region max; batch the independent times.
    depths=np.empty((len(self.t),len(self.keys),len(w.REGIONS)))
    for ik,(key,g,pl) in enumerate(self.keys):
        pv,R=self.key_cache[ik]
        local=(V-pv)@R+pv
        depth=np.maximum(0,-np.max(local@pl[:,:3].T-pl[:,3],axis=2)*1000)
        for ir,ids in enumerate(w.REGIONS.values()):depths[:,ik,ir]=depth[:,ids].max(1)
    gaps=[]
    for a,b in w.PAIRLIST:
        va=V[:,w.REGIONS[a]];vb=V[:,w.REGIONS[b]]
        gaps.extend(np.maximum(va.min(1)-vb.max(1),vb.min(1)-va.max(1)).max(1)*1000)
    return dict(key_depth=depths.ravel(),pair_aabb_gap=np.array(gaps))

def mask_for(p):
    # Dependencies from exact weighted FK ancestors, plus the global thumb corrective.
    parents=n.D['parents'];bone_dep=np.zeros((len(parents),26),bool)
    for b,parent in enumerate(parents):
        if parent>=0:bone_dep[b]|=bone_dep[parent]
        for j,names in enumerate(n.NAMES):
            for k,name in enumerate(names):
                if n.BN[name]==b:
                    bone_dep[b,6+j*4+k]=True
                    if k==0:bone_dep[b,6+j*4+3]=True
    vd=np.zeros((len(n.W),26),bool);vd[:,:6]=True
    for b in range(len(parents)):
        vd[n.W[:,b]!=0]|=bone_dep[b]
    # A nonzero shape displacement can be moved by any weighted bone; the skin
    # shape amount itself depends on both thumb CMC/spread and thumb MCP.
    shapeids=np.any(n.SHLOCAL!=0,axis=(0,2))
    vd[np.ix_(shapeids,[6,7,9])]=True
    def dep(ids):return vd[np.asarray(ids)].any(0)
    B=w.IDENT(p.t)[:,w.FREE]
    def at(d,it):return (B[it,:,None]!=0)&d[None,:]
    rows=[];sections={}
    def add(label,items):
        start=len(rows);rows.extend(items);sections[label]=[start,len(rows)]
    add('active_contact',[at(dep([n.PADIDS[e['finger']-1]]),it).ravel() for it,e in p.active for _ in range(5)])
    add('key_depth',[at(dep(ids),it).ravel() for it in range(len(p.t)) for key in p.keys for ids in w.REGIONS.values()])
    add('pair_aabb',[at(dep(np.r_[w.REGIONS[a],w.REGIONS[b]]),it).ravel() for a,b in w.PAIRLIST for it in range(len(p.t))])
    add('role',[at(dep([n.PADIDS[j]]),it).ravel() for it,j,target,error in p.role_checks])
    diag=[]
    for c in range(6,26):
        d=np.zeros(26,bool);d[c]=True;diag.append(np.tile(d,2))
    for label in ['joint_lower','joint_upper','joint_velocity','joint_acceleration','added_joint_velocity']:add(label,diag)
    rootdiag=[]
    for c in range(3):
        d=np.zeros(26,bool);d[c]=True;rootdiag.append(np.tile(d,2))
    for label in ['root_lower','root_upper','root_velocity','root_acceleration']:add(label,rootdiag)
    d=np.zeros(26,bool);d[3:6]=True;add('angular_axes',[np.tile(d,2)]*3)
    d=np.zeros(26,bool);d[:3]=True;add('root_speed',[np.tile(d,2)])
    d=np.zeros(26,bool);d[3:6]=True;add('angular_speed',[np.tile(d,2)])
    mask=np.array(rows);assert mask.shape==(11149,52)
    evidence=dict(bone_names=n.M['bones'],parents=parents,bone_channel_dependency=bone_dep.astype(int),vertex_channel_dependency_counts=vd.sum(0),
                  region_channels={r:np.flatnonzero(dep(ids)) for r,ids in w.REGIONS.items()},shape_affected_vertices=np.flatnonzero(shapeids),
                  bspline_support=B,sections=sections,nnz=int(mask.sum()),total=mask.size,groups=group_columns(csr_matrix(mask)),
                  exact_weight_dependency=True,weight_threshold_used=False)
    return mask,evidence

def proposed_bounds(p):
    bounds=p.geo_baseline['key_depth']+.02
    absolute=np.zeros(len(bounds),bool);i=0
    for it,t in enumerate(p.t):
        little_active=any(e['note_id']=='R05' and e['note_on']<=t<e['note_off'] for e in w.EVENTS)
        for key,g,pl in p.keys:
            for region in w.REGIONS:
                if p.owner[i]:bounds[i]=1e3
                elif little_active and region=='LITTLE':bounds[i]=min(.5,bounds[i]);absolute[i]=True
                i+=1
    return bounds,absolute

def error(a,b):
    d=np.abs(a-b);return dict(max_abs=float(d.max()),rms=float(np.sqrt(np.mean(d*d))),relative_scaled_max=float(np.max(d/(1+np.abs(b)))))

def main():
    begin=time.perf_counter();ledger=[]
    def timed(label,fn):
        tic=time.perf_counter();v=fn();ledger.append(dict(label=label,seconds=time.perf_counter()-tic));print(label,ledger[-1]['seconds'],flush=True);return v
    # Frozen test contract BEFORE numerical evaluations. Perturbation is a bounded
    # derivative probe, never a feasible/candidate motion; no constraints are solved.
    spec=dict(method='2-point',absolute_step=1e-4,inputs=['zeros(52)', '0.02*sin(arange(52)+1), retaining only root channels 0:6 and spread channels 9,13,17,21,25 in both coefficient blocks'],
              constraint_atol=1e-9,jacobian_atol=2e-6,jacobian_rtol=2e-6,structural_zero_atol=2e-6,
              timer='perf_counter wall clock; one measured complete Jacobian per state, including baseline and all columns',
              numerical_budget_seconds=120,threads=1,formal_solve=False)
    io.atomic_json('TEST_SPEC.json',spec)
    p=timed('historical_initialization',w.Problem)
    p.key_cache=[(np.asarray(k['press_pivot']),w.rot(p.angles[:,k['key_index']],k['press_axis'])) for k,g,pl in p.keys]
    x0=np.zeros(52);x1=.02*np.sin(np.arange(52)+1)
    x1[~np.tile(np.isin(np.arange(26),[0,1,2,3,4,5,9,13,17,21,25]),2)]=0
    oldnative=w.native
    mask,evidence=mask_for(p);io.atomic_json('STRUCTURAL_EVIDENCE.json',evidence)
    io.atomic_record('STRUCTURAL_MASK.npz',dict(mask=mask.astype(np.uint8)))
    saved=io.archive(HIST/'CONSTRAINT_JACOBIAN_PREFLIGHT_CLOCK_FIXED.npz')
    assert np.array_equal(saved['seed'],x0) and np.array_equal(saved['planning_times'],p.t)
    old0=timed('old_constraints_zero',lambda:p.constraints(x0).copy())
    assert np.max(abs(old0-saved['constraints']))<1e-9
    # One new full reference, not two expensive historical evaluations.
    old1=timed('old_constraints_nonzero',lambda:p.constraints(x1).copy())
    j1=timed('old_full_jacobian_nonzero',lambda:approx_derivative(p.constraints,x1,method='2-point',abs_step=1e-4))
    oldbounds=p.bounds_upper.copy();newbounds,absolute=proposed_bounds(p)
    offset=np.zeros(len(old0));a,b=evidence['sections']['key_depth'];offset[a:b]=newbounds-oldbounds
    # Same-contract oracle: only constant gate RHS changes. Derivatives unchanged.
    # Fast implementation uses the identical constraints method and row order.
    w.native=fast_native
    p.geometric_metrics=types.MethodType(fast_geometry,p)
    results=[];arrays={}
    for label,x,old,jref in [('zero',x0,old0,saved['jacobian']),('nonzero',x1,old1,j1)]:
        p.bounds_upper=oldbounds;p.cache_x=None
        fastold=timed('fast_original_constraints_'+label,lambda:p.constraints(x).copy())
        p.bounds_upper=newbounds;p.cache_x=None
        c=timed('fast_proposed_constraints_'+label,lambda:p.constraints(x).copy())
        p.cache_x=None;calls=p.calls
        j=timed('fast_full_jacobian_'+label,lambda:approx_derivative(p.constraints,x,method='2-point',abs_step=1e-4))
        assert np.allclose(fastold,old,atol=1e-9,rtol=0)
        assert np.allclose(c,old+offset,atol=1e-9,rtol=0)
        outside=float(np.max(abs(jref[~mask])))
        ok=bool(np.allclose(j,jref,atol=2e-6,rtol=2e-6))
        results.append(dict(state=label,original_constraint_error=error(fastold,old),proposed_constraint_error=error(c,old+offset),
                            jacobian_error=error(j,jref),jacobian_allclose=ok,masked_reference_max=outside,calls=p.calls-calls,
                            violations=int((c<-1e-9).sum()),minimum=float(c.min())))
        arrays['constraints_'+label]=c;arrays['jacobian_'+label]=j
    # Reverse structural-zero check: independent original evaluator at a second
    # signed finite perturbation size, all 52 columns checked above, six here.
    w.native=oldnative;p.geometric_metrics=types.MethodType(w.Problem.geometric_metrics,p);p.bounds_upper=newbounds
    reverse=[]
    base=p.constraints(x1).copy()
    for col in [0,3,6,10,22,51]:
        z=x1.copy();z[col]-=3e-4
        c=timed('reverse_zero_column_'+str(col),lambda:p.constraints(z).copy())
        reverse.append(dict(column=col,masked_rows=int((~mask[:,col]).sum()),maximum_abs=float(np.max(abs((c-base)[~mask[:,col]]/(-3e-4))))))
    # Boundary invariants and row-level diagnosis; evaluate only, no optimization.
    sec=evidence['sections'];c0=arrays['constraints_zero'];viol={}
    for label,(a,b) in sec.items():
        bad=np.flatnonzero(c0[a:b]<-1e-9);viol[label]=dict(count=len(bad),minimum=float(c0[a:b].min()),rows=(bad+a).tolist())
    q,world=w.state(x1,p.t);Q=w.QREF(p.t).reshape(-1,5,4)
    bound=np.asarray(w.QBOUNDS);inside=bool(np.all(q>=bound[:,0][None]-1e-9) and np.all(q<=bound[:,1][None]+1e-9))
    # Correct lower/upper orientation QBOUNDS is (5,2,4), not a new angle policy.
    boundary_rows=[];i=sec['key_depth'][0]
    for it,t in enumerate(p.t):
        for key,g,pl in p.keys:
            for region in w.REGIONS:
                if it in [0,len(p.t)-1] and c0[i]<-1e-9:boundary_rows.append(dict(row=i,time=float(t),region=region,key=key['name'] if 'name' in key else key['key_index'],value=float(c0[i])))
                i+=1
    fixed_bad=np.flatnonzero((~mask.any(1))&(c0<-1e-9))
    nonzero_target_cols=np.flatnonzero(mask[np.r_[np.arange(*sec['key_depth'])[absolute]],:].any(0))
    io.atomic_record('NUMERICAL_RESULTS.npz',arrays)
    result=dict(scipy=scipy.__version__,numpy=np.__version__,tests=results,reverse_zero_checks=reverse,ledger=ledger,
                total_seconds=time.perf_counter()-begin,nnz=int(mask.sum()),groups=int(np.max(evidence['groups'])+1),
                input_nonzero_within_joint_domain=inside,input_nonzero_within_coefficient_bounds=bool(np.all(abs(x1)<=np.tile(w.LIMIT,2))),
                input_nonzero_endpoint_correction=w.correction(x1,[w.START,w.END]),input_nonzero_endpoint_velocity=w.correction(x1,[w.START,w.END],1),
                proposed_violations=viol,proposed_boundary_geometry_violations=boundary_rows,fixed_zero_rows=int((~mask.any(1)).sum()),
                fixed_infeasible_rows=fixed_bad,absolute_target_rows=int(absolute.sum()),absolute_target_influencing_columns=nonzero_target_cols,
                events=w.EVENTS,planning_times=p.t,original_bounds_unchanged=False,contract_change='proposal only; no approval inferred',
                formal_trajectory_solve='NOT_EXECUTED',new_motion_candidate='NONE')
    io.atomic_json('DIAGNOSTIC_RESULTS.json',result)
    for pth in [ROOT/'AGENTS.md',OUT/'review_diagnostics.py']:
        io.READS[str(pth)]=io.sha(pth)
    io.protect('SOURCE_SHA_CHECK.json')
    print('DONE',json.dumps(results),flush=True)

if __name__=='__main__':main()
