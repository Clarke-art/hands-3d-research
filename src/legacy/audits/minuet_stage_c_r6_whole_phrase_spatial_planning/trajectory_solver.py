"""One sparse constrained whole-phrase solve. No multistart or fallback backend.

The spatial constraints are conservative sampled inequalities. A failed solve is
not a proof that the frozen hand is physically infeasible.
"""
from whole_phrase_model import *
import time,itertools
from scipy import sparse
from scipy.optimize import minimize,Bounds,LinearConstraint,NonlinearConstraint,BFGS
POL=read(P/'PREFLIGHT_POLICY.json')

def spline_matrices(knots,t):
    n=len(knots);h=np.diff(knots);E=np.eye(n);S0=np.zeros((n,n))
    for i in range(1,n-1):S0[i]=(E[i+1]-E[i-1])/(knots[i+1]-knots[i-1])
    B=[];V=[];A=[]
    for tt in t:
        i=int(np.clip(np.searchsorted(knots,tt,side='right')-1,0,n-2));u=(tt-knots[i])/h[i]
        B.append((2*u**3-3*u*u+1)*E[i]+(u**3-2*u*u+u)*h[i]*S0[i]+(-2*u**3+3*u*u)*E[i+1]+(u**3-u*u)*h[i]*S0[i+1])
        V.append((6*u*u-6*u)/h[i]*E[i]+(3*u*u-4*u+1)*S0[i]+(-6*u*u+6*u)/h[i]*E[i+1]+(3*u*u-2*u)*S0[i+1])
        A.append((12*u-6)/h[i]**2*E[i]+(6*u-4)/h[i]*S0[i]+(-12*u+6)/h[i]**2*E[i+1]+(6*u-2)/h[i]*S0[i+1])
    # Bounding all four Bezier controls guarantees each entire cubic stays in
    # the engineering box, not just its sampled endpoints.
    controls=np.array([row for i in range(n-1) for row in [E[i]+h[i]*S0[i]/3,E[i+1]-h[i]*S0[i+1]/3]])
    return tuple(sparse.csr_matrix(x) for x in [B,V,A,controls])

class Spatial:
    def __init__(self,t):
        self.t=np.array(t);self.K=len(t)
        # Every skin vertex enters key-body constraints, including proximal
        # skin and webbing. Pair envelopes exclude shared palm/web only.
        self.ids=list(range(len(W)))
        self.im={v:i for i,v in enumerate(self.ids)}
        self.roi=[np.array([self.im[v] for v in M['rois'][d]['vertices']]) for d in c.DIGITS]
        influence=np.column_stack([W[:,[i for i,name in enumerate(M['bones']) if name.startswith(d+'_')]].sum(1) for d in c.DIGITS])
        owner=influence.argmax(1)
        self.keyroi=[np.flatnonzero(owner==j) for j in range(5)]
        self.pad=np.array([self.im[m['mesh_vertex']] for m in M['markers']])
        self.model=Skin(t,self.ids);self.components=key_components()
        self.comp=[]
        for k,g in self.components:
            pl=component_planes(g);v=np.array(g['vertices']);lo=v.min(0);hi=v.max(0)
            assert len(pl)==6 and np.all(np.sum(abs(pl[:,:3])>1e-7,axis=1)==1), 'Only verified exact rectangular components use box shortcut'
            self.comp.append((k,lo,hi,np.cos(self.model.angles[:,k['key_index']])[:,None],np.sin(self.model.angles[:,k['key_index']])[:,None],np.array(k['press_pivot'])))
        self.pairs=list(itertools.combinations(range(5),2))
        self.source=self.model(source_angles(t))
        self.contacts=[]
        for ti,tt in enumerate(t):
            for n in TL['notes']:
                # Both outgoing and incoming contacts at an exact shared
                # event boundary: continuity limit only, no post-OFF hold.
                if n['hand']=='R' and n['note_on']-1e-8<=tt<=n['note_off']+1e-8:
                    j=n['finger']-1;k=c.KEYS[n['key_index']];pv=np.array(k['press_pivot'])
                    R=rot(-self.model.angles[ti,k['key_index']],[1,0,0]);pt=R@(self.source[ti,self.pad[j]]-pv)+pv
                    s=min(k['key_top_playable_surface'],key=lambda s:np.linalg.norm(pt[:2]-np.clip(pt[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))
                    self.contacts.append((ti,j,n,k,s,R,pv))
        # Spatial rows per time: five key-body slacks and ten digit separators.
        self.local_rows=15
        self.row_times=np.r_[np.repeat(np.arange(self.K),15),[v[0] for v in self.contacts for _ in range(6)]]
        self.calls=0;self.max_calls=None;self.deadline=None
    def evaluate(self,q):
        if self.deadline is not None and time.monotonic()>=self.deadline:raise BudgetStop('WALL_CLOCK_LIMIT')
        if self.max_calls is not None and self.calls>=self.max_calls:raise BudgetStop('SPATIAL_EVALUATION_LIMIT')
        self.calls+=1
        V=self.model(q);worst=np.full((self.K,5),-1e6)
        for key,lo,hi,co,si,pv in self.comp:
            xx=V[:,:,0];dy=V[:,:,1]-pv[1];dz=V[:,:,2]-pv[2]
            yy=co*dy+si*dz+pv[1];zz=-si*dy+co*dz+pv[2]
            dep=np.minimum(np.minimum(np.minimum(xx-lo[0],hi[0]-xx),np.minimum(yy-lo[1],hi[1]-yy)),np.minimum(zz-lo[2],hi[2]-zz))*1000
            for j,ids in enumerate(self.keyroi):
                worst[:,j]=np.maximum(worst[:,j],dep[:,ids].max(axis=1))
        # No whole-finger target exemption. Even target-pad interior is capped
        # at 0.5 mm, while the contact anchor must stay within [-0.5,2.1] mm.
        keyslack=.5-worst
        pair=[]
        for a,b in self.pairs:
            pa,pb=V[:,self.roi[a]],V[:,self.roi[b]]
            axis=pb.mean(axis=1)-pa.mean(axis=1);axis/=np.maximum(np.linalg.norm(axis,axis=1,keepdims=True),1e-12)
            # Supporting-plane separation over actual skin vertices. Taking
            # the best of fixed XYZ axes and centroid axis is conservative:
            # positive separation guarantees disjoint convex envelopes.
            gaps=[]
            for ax in [np.tile(np.eye(3)[i],(self.K,1)) for i in range(3)]+[axis]:
                aa=np.einsum('kvi,ki->kv',pa,ax);bb=np.einsum('kvi,ki->kv',pb,ax)
                gaps.append(np.maximum(bb.min(1)-aa.max(1),aa.min(1)-bb.max(1))*1000)
            pair.append(np.max(gaps,axis=0))
        spatial=np.c_[keyslack,np.array(pair).T].ravel()
        contact=[]
        for ti,j,n,k,s,R,pv in self.contacts:
            pt=R@(V[ti,self.pad[j]]-pv)+pv;gap=(pt[2]-s['z'])*1000
            contact.extend([gap+.5,2.1-gap,(pt[0]-s['xmin'])*1000+.5,(s['xmax']-pt[0])*1000+.5,(pt[1]-s['ymin'])*1000+.5,(s['ymax']-pt[1])*1000+.5])
        return np.r_[spatial,contact]
    def local_jac(self,q,base):
        # All time slices are independent here. Perturb the same coordinate
        # at all times in one batch, then chain through the sparse C1 spline.
        columns=[];eps=1e-4
        for j in range(20):
            qq=q.reshape(-1,20).copy();qq[:,j]+=eps
            columns.append((self.evaluate(qq)-base)/eps)
        rows=np.repeat(np.arange(len(base)),20)
        cols=(self.row_times[:,None]*20+np.arange(20)).ravel()
        val=np.array(columns).T.ravel();keep=abs(val)>1e-12
        return sparse.csr_matrix((val[keep],(rows[keep],cols[keep])),shape=(len(base),self.K*20))

class BudgetStop(Exception):pass

def setup():
    knots=np.array(POL['knots']);t=np.array(POL['checks']);B,V,A,controls=spline_matrices(knots,t)
    spatial=Spatial(t);q0=source_angles(knots).reshape(-1,20)
    low=np.array([np.degrees(c.bounds(d)[0]) for d in c.DIGITS]).ravel()
    high=np.array([np.degrees(c.bounds(d)[1]) for d in c.DIGITS]).ravel()
    return knots,t,B,V,A,controls,spatial,q0,low,high

def readonly_preflight():
    knots,t,B,V,A,controls,sp,q0,lo,hi=setup()
    start=time.monotonic();g=sp.evaluate(B@q0);elapsed=time.monotonic()-start
    # No perturbations or optimization in this preflight. Initial violations
    # do not certify infeasibility because every joint endpoint is free.
    dump('SPATIAL_INTERFACE_PREFLIGHT.json',dict(initial_min_slack_mm=float(g.min()),
        initial_violating_rows=int(np.sum(g<0)),constraint_rows=len(g),variables=q0.size,
        samples=len(t),one_geometry_evaluation_sec=elapsed,skin_vertices=len(sp.ids),
        contacts=len(sp.contacts),pair_count=10,key_components=len(sp.comp),
        immutable_boundary_equalities=0,initial_seed='Source C1 angles only',
        formal_solves=0,static_solves=0,initial_source_not_claimed_feasible=True,
        source_bezier_box_violation_deg=float(max(0,np.max(lo-controls@q0),np.max(controls@q0-hi)))))
    print('R6_SPATIAL_INTERFACE',q0.size,len(g),elapsed,'seconds','min',g.min(),flush=True)

def solve():
    lock=read(P/'STRATEGY_LOCK.json')
    assert lock['formal_attempt_limit']==1 and lock['preflight_gate']=='CONTINUE_SINGLE_ATTEMPT'
    # Exclusive creation consumes the sole attempt before any optimization.
    with (P/'FORMAL_ATTEMPT_STARTED.json').open('x',encoding='utf8') as f:
        json.dump(dict(attempt=1,lock_sha256=sha(P/'STRATEGY_LOCK.json'),unix_time=time.time()),f,indent=2)
    start=time.monotonic()
    knots,t,B,V,A,controls,sp,q0,lo,hi=setup();n=q0.size
    sp.deadline=start+lock['wall_clock_sec'];sp.max_calls=lock['max_spatial_evaluations']
    BB=sparse.kron(B,sparse.eye(20),format='csr');CC=sparse.kron(controls,sparse.eye(20),format='csr')
    # A single fixed quadratic natural-style prior. Preparing fingers are
    # attracted mildly toward their next event's source contact configuration.
    guide=source_angles(t).reshape(-1,20)
    sys.path.insert(0,str(R5));from event_phase_plan import EventPhasePlan
    plan=EventPhasePlan([n0 for n0 in TL['notes'] if n0['hand']=='R'])
    for i,tt in enumerate(t):
        for j,f in enumerate(plan.at(float(tt))['fingers']):
            for task in f['tasks']:
                if task['role']=='PREPARING' and not f['active_keys']:
                    note=next(n0 for n0 in plan.notes if n0['note_id']==task['note_id'])
                    w=.15*task['envelope'];guide[i,j*4:j*4+4]=(1-w)*guide[i,j*4:j*4+4]+w*source_angles([note['note_on']])[0,j]
    scale=np.tile([18.,25.,22.,14.],5)
    G=sparse.kron(B,sparse.diags(1/scale),format='csr')/np.sqrt(len(t))
    DV=sparse.kron(V,sparse.diags(.025/scale),format='csr')/np.sqrt(len(t))
    DA=sparse.kron(A,sparse.diags(.001/scale),format='csr')/np.sqrt(len(t))
    H=(G.T@G+DV.T@DV+DA.T@DA).tocsr()
    target=(guide/scale).ravel()/np.sqrt(len(t));x0=q0.ravel()
    rhs=G.T@target+DV.T@(DV@x0)+DA.T@(DA@x0)
    counts=dict(objective=0,objective_jac=0,constraint=0,constraint_jac=0,major_iterations=0)
    cache={};latest={'x':x0.copy()};trace=[]
    def objective(x):
        counts['objective']+=1
        if counts['objective']>lock['max_objective_nfev']:raise BudgetStop('OBJECTIVE_EVALUATION_LIMIT')
        if time.monotonic()>=sp.deadline:raise BudgetStop('WALL_CLOCK_LIMIT')
        return float(.5*x@(H@x)-rhs@x)
    def gradient(x):counts['objective_jac']+=1;return H@x-rhs
    def con(x):
        counts['constraint']+=1
        if 'x' not in cache or not np.array_equal(x,cache['x']):
            cache.update(x=x.copy(),q=(<REDACTED_EMAIL>(-1,20)),g=None,jac=None)
            cache['g']=sp.evaluate(cache['q'])
        return cache['g']
    def jac(x):
        counts['constraint_jac']+=1;g=con(x)
        if cache['jac'] is None:cache['jac']=sp.local_jac(cache['q'],g)@BB
        return cache['jac']
    def callback(x,state):
        counts['major_iterations']=int(state.nit);latest['x']=x.copy()
        row=dict(iteration=int(state.nit),elapsed_sec=time.monotonic()-start,
            nfev=int(state.nfev),spatial_evaluations=sp.calls,
            constraint_violation=float(state.constr_violation),optimality=float(state.optimality))
        trace.append(row)
        print('R6_ITERATION',json.dumps(row),flush=True)
        np.savez_compressed(P/'FORMAL_CHECKPOINT.npz',knots=knots,q=x.reshape(-1,5,4))
        dump('SOLVER_PROGRESS.json',row)
        return time.monotonic()>=sp.deadline
    result=None;reason=None
    try:
        result=minimize(objective,x0,method='trust-constr',jac=gradient,hess=lambda x:H,
            bounds=Bounds(np.tile(lo,len(knots)),np.tile(hi,len(knots))),
            constraints=[LinearConstraint(CC,np.tile(lo,controls.shape[0]),np.tile(hi,controls.shape[0])),
                NonlinearConstraint(con,0,np.inf,jac=jac,hess=BFGS())],callback=callback,
            options=dict(maxiter=lock['major_iteration_limit'],gtol=1e-5,xtol=1e-8,barrier_tol=1e-8,
                sparse_jacobian=True,verbose=0,initial_tr_radius=2.,factorization_method='AugmentedSystem'))
        latest['x']=result.x;reason=str(result.message)
    except BudgetStop as e:reason=str(e)
    except Exception as e:reason=type(e).__name__+': '+str(e)
    elapsed=time.monotonic()-start
    np.savez_compressed(P/'FORMAL_RESULT.npz',knots=knots,q=latest['x'].reshape(-1,5,4),checks=t)
    dump('SOLVER_TERMINATION.json',dict(attempts=1,counts=counts,spatial_evaluations=sp.calls,
        elapsed_sec=elapsed,status=int(result.status) if result is not None else -1,
        success=bool(result.success) if result is not None else False,termination_reason=reason,
        nfev=int(result.nfev) if result is not None else counts['objective'],trace=trace,
        result_is_unvalidated_numeric_evidence=True,dynamic_candidate_count=0))
    print('R6_FORMAL_TERMINATED',reason,elapsed,flush=True)

if __name__=='__main__':
    if '--solve' in sys.argv:solve()
    else:readonly_preflight()
