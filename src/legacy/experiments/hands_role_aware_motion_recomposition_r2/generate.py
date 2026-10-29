from representation import *
from scipy.optimize import least_squares
from scipy.interpolate import CubicHermiteSpline
import time,traceback

class Strategy:
    def __init__(self):
        self.r=Representation();self.P=read(O/'POLICY.json');self.start=None;self.calls=0;self.local_calls=0
        self.last_x=np.zeros(8);self.last_fun=np.zeros(1)
        self.outer_times=np.linspace(self.r.start+.025,self.r.end-.025,self.P['outer_support_count'])
        self.components=[(k,g,pl) for k,g,pl in n.COMPONENTS if 64<=k['midi_note']<=82]
        self.regions=[np.array(n.ROIS[d]['vertices']) for d in n.DIGITS]
        self.lo=np.array([p['low'] for p in self.P['outer_parameters']]);self.hi=np.array([p['high'] for p in self.P['outer_parameters']])
    def budget(self):
        if self.start is not None and time.monotonic()-self.start>180:raise TimeoutError('SOLE_STRATEGY_180_SECOND_LIMIT')
    def target(self,e,xy,t,lift=0):return n.point_on_key(n.KEYS[e['key_index']],xy,self.r.target_angle(t)[e['key_index']],lift)
    def outer_residual(self,x):
        self.budget();self.calls+=1;out=[]
        q=np.array([self.r.prior(t,x) for t in self.outer_times]);world=np.array([self.r.world(t,x) for t in self.outer_times]);V=n.native(q,world)
        for ix,t in enumerate(self.outer_times):
            owned={}
            for j,idx,lift,w in self.r.roles(t):
                e=self.r.events[idx];goal=self.target(e,self.r.preferred_xy(e),t,lift);out.extend((V[ix,n.PADIDS[j]]-goal)*1000*w)
                owned.setdefault(e['key_index'],set()).add(j)
            angles=self.r.target_angle(t)
            for k,g,pl in self.components:
                pv=np.array(k['press_pivot']);local=(V[ix]-pv)@n.rot(angles[k['key_index']],k['press_axis'])+pv
                d=-np.max(local@pl[:,:3].T-pl[:,3],axis=1)*1000
                for j,ids in enumerate(self.regions):out.append(0. if j in owned.get(k['key_index'],set()) else max(0,float(d[ids].max())+.5)*2.)
        out.extend(x*.10);y=np.array(out);assert np.isfinite(y).all();self.last_x=x.copy();self.last_fun=y.copy();return y
    def local_inputs(self,q,world,t,task,previous):
        j,idx,lift,w=task;e=self.r.events[idx];key=n.KEYS[e['key_index']];xy=self.r.preferred_xy(e);loxy,hixy=n.inset(key)
        lower=np.r_[self.r.bounds[j,0],loxy];upper=np.r_[self.r.bounds[j,1],hixy]
        own=np.flatnonzero(n.W[:,[i for i,name in enumerate(n.M['bones']) if name.startswith(n.DIGITS[j]+'_')]].sum(1)>.05)
        ids=np.unique(np.r_[own,n.PADIDS[j]]);pad=int(np.flatnonzero(ids==n.PADIDS[j])[0]);qref=q[j].copy();angles=self.r.target_angle(t)
        comps=[(k,pl) for k,g,pl in self.components if k['key_index']!=e['key_index']]
        def fun(v):
            self.budget();changed=q.copy();changed[j]=v[:4];verts=n.native(changed,world,ids)[0];target=self.target(e,v[4:],t,lift)
            out=[(verts[pad]-target)*1000*w]
            for k,pl in comps:
                pv=np.array(k['press_pivot']);local=(verts-pv)@n.rot(angles[k['key_index']],k['press_axis'])+pv;depth=-np.max(local@pl[:,:3].T-pl[:,3],axis=1)*1000
                out.append(np.maximum(depth+.5,0)*2.)
            out.extend([(v[:4]-qref)*.055,(v[4:]-xy)*.12,(v[:4]-previous[j])*.08])
            value=np.concatenate(out);assert np.isfinite(value).all();return value
        seed=np.clip(np.r_[qref,xy],lower+1e-7,upper-1e-7)
        return seed,lower,upper,fun

def adapter_test():
    s=Strategy();y=s.outer_residual(np.zeros(8));t=s.r.target[1]['note_on']+.035;q=s.r.prior(t,np.zeros(8));w=s.r.world(t,np.zeros(8));task=s.r.roles(t)[0]
    seed,lo,hi,fn=s.local_inputs(q,w,t,task,q);z=fn(seed)
    assert seed.shape==(6,) and z.ndim==1 and np.isfinite(z).all()
    atomic_json('GENERATION_ADAPTER_SELFTEST.json',dict(pass_=True,outer_variables=8,local_variables=6,outer_residual_shape=y.shape,local_residual_shape=z.shape,optimizer_calls=0,
        all_five_role_tasks=True,boundary_q_error_deg=float(abs(s.r.prior(s.r.start,np.zeros(8))-s.r.boundary_q[0]).max()),boundary_world_error=float(abs(s.r.world(s.r.start,np.zeros(8))-s.r.boundary_w[0]).max())))
    print('GENERATION_ADAPTER_SELFTEST_PASS',len(y),len(z),flush=True)

def run():
    assert read(O/'GENERATION_ADAPTER_SELFTEST.json')['pass_'] and read(O/'REPRESENTATION_READBACK.json')['pass_']
    lock=read(O/'FORMAL_CODE_LOCK.json');assert sha(O/'POLICY.json')==lock['policy_sha256']
    assert all(sha(O/name)==h for name,h in lock['scripts'].items())
    assert not (O/'FORMAL_GENERATION_STARTED.json').exists()
    s=Strategy();r=s.r;P=s.P;s.start=time.monotonic()
    atomic_json('FORMAL_GENERATION_STARTED.json',dict(strategies=1,dynamic_candidate_limit=1,outer_variables=8,numerical_limit_seconds=180,seed=np.zeros(8),policy_sha256=sha(O/'POLICY.json')))
    states=[];priors=[];worlds=[];knots=[]
    try:
        outer=least_squares(s.outer_residual,np.clip(np.zeros(8),s.lo+1e-7,s.hi-1e-7),bounds=(s.lo,s.hi),max_nfev=18,ftol=1e-6,xtol=1e-6,gtol=1e-6)
        x=outer.x.copy();atomic_record('OUTER_RESULT.npz',dict(x=x,x0=np.zeros(8),fun=outer.fun,grad=outer.grad,active_mask=outer.active_mask),dict(success=bool(outer.success),message=outer.message,nfev=outer.nfev,residual_calls=s.calls,seconds=time.monotonic()-s.start,record_type='SOLE_OUTER_RESULT'))
        supports=unique_times([r.start,r.end,*np.arange(r.start,r.end,.025),*[e[p]+d for e in r.target for p in ['note_on','note_off'] for d in [-.18,-.075,0,.0175,.035,.04,.07]]]);supports=supports[(supports>=r.start)&(supports<=r.end)]
        previous=r.boundary_q[0].copy()
        for ix,t in enumerate(supports):
            s.budget();q=r.prior(float(t),x);prior=q.copy();world=r.world(float(t),x)
            if ix not in [0,len(supports)-1]:
                for task in r.roles(float(t)):
                    if task[3]<.1:continue
                    assert s.local_calls<P['local_call_limit'],'LOCKED_LOCAL_CALL_LIMIT'
                    seed,lo,hi,fun=s.local_inputs(q,world,float(t),task,previous);last=[seed.copy(),fun(seed)]
                    def wrapped(v):
                        val=fun(v);last[:]=[v.copy(),val.copy()];return val
                    try:fit=least_squares(wrapped,seed,bounds=(lo,hi),max_nfev=12,ftol=1e-6,xtol=1e-6,gtol=1e-6)
                    except BaseException:
                        atomic_record('LOCAL_EXCEPTION_'+str(ix)+'_'+str(task[0])+'.npz',dict(x=last[0],fun=last[1],q=q,world=world),dict(time=float(t),error=traceback.format_exc(),record_type='LAST_EVALUATED_STATE_NOT_FINAL'));raise
                    s.local_calls+=1;q[task[0]]=fit.x[:4]
                    atomic_record('LOCAL_RESULT_'+str(ix)+'_'+str(task[0])+'.npz',dict(x=fit.x,x0=seed,fun=fit.fun,q=q,world=world),dict(time=float(t),finger=task[0]+1,event=r.events[task[1]]['note_id'],role='ACTIVE' if r.events[task[1]]['note_on']<=t<r.events[task[1]]['note_off'] else 'RELEASE_OR_PREPARE',success=bool(fit.success),nfev=fit.nfev,message=fit.message))
            states.append(q.copy());priors.append(prior);worlds.append(world);knots.append(float(t));previous=q.copy()
        knots=np.array(knots);states=np.array(states);pchip=PchipInterpolator(knots,states,axis=0);dq=pchip.derivative()(knots);dq[0]=r.boundary_qdot[0];dq[-1]=r.boundary_qdot[1]
        curve=CubicHermiteSpline(knots,states,dq,axis=0)
        atomic_record('CONTINUOUS_CURVE.npz',dict(knots=knots,q_deg=states,dq_deg_s=dq,outer=x,q_prior_deg=priors,world_at_support=worlds),dict(record_type='SOLE_COMPLETE_CONTINUOUS_CANDIDATE',local_calls=s.local_calls,seconds=time.monotonic()-s.start))
        clock,_=archive(O/'TARGET_CLOCK_REQUEST.npz');times=unique_times([*clock['times'],*knots]);times=times[(times>=r.start)&(times<=r.end)]
        trajectory=curve(times);world=np.array([r.world(t,x) for t in times]);ka=np.array([r.target_angle(t) for t in times]);native=n.native(trajectory,world)
        # Persist the entire candidate BEFORE gate calculations or report export.
        atomic_record('MOTION_CANDIDATE.npz',dict(times=times,q_deg=trajectory,rig_world=world,key_angles=ka,numeric_skin_vertices=native),dict(record_type='ONE_CANDIDATE_NOT_PRODUCT',source='R04-R05',target='R12-R13',target_interior_q_used=False))
        contactrows=[]
        for ix,t in enumerate(times):
            for e in r.events:
                if e['note_on']<=t<e['note_off']:
                    j=e['finger']-1;_,h,g,_=n.surface_metrics(native[ix,n.PADIDS[j]][None],n.KEYS[e['key_index']],ka[ix,e['key_index']]);contactrows.append(dict(time=float(t),event=e['note_id'],horizontal_mm=float(h[0]*1000),gap_mm=float(g[0]*1000),pass_=bool(h[0]*1000<=.03 and abs(g[0]*1000)<=3)))
        qprior=np.array([r.prior(t,x) for t in times]);vel=curve.derivative()(times);added=np.gradient(trajectory-qprior,times,axis=0)
        domain=bool(np.all(trajectory>=r.bounds[:,0]-1e-7) and np.all(trajectory<=r.bounds[:,1]+1e-7));speed=float(abs(added).max())
        atomic_json('NUMERIC_CANDIDATE_GATE.json',dict(pass_=domain and all(v['pass_'] for v in contactrows) and speed<=180,joint_domain_pass=domain,contacts=contactrows,
            actual_curve_joint_peak_deg_s=float(abs(vel).max()),added_joint_velocity_peak_deg_s=speed,added_joint_velocity_pass=speed<=180,outer_parameters=x,
            endpoint_q_errors_deg=[float(abs(trajectory[0]-r.boundary_q[0]).max()),float(abs(trajectory[-1]-r.boundary_q[1]).max())],endpoint_q_derivative_errors=[float(abs(vel[0]-r.boundary_qdot[0]).max()),float(abs(vel[-1]-r.boundary_qdot[1]).max())],
            numeric_seconds=time.monotonic()-s.start,local_IK_calls=s.local_calls,outer_nfev=outer.nfev,candidate_count=1,strategies=1))
        atomic_json('NUMERICAL_LEDGER.json',dict(seconds=time.monotonic()-s.start,budget_seconds=180,optimizer_strategy_starts=1,outer_calls=1,outer_nfev=outer.nfev,local_IK_calls=s.local_calls,local_nfev_limit=12,trajectory_supports=len(knots),dynamic_candidates=1,retunes=0))
        print('SOLE_CANDIDATE_SAVED',len(times),len(knots),s.local_calls,'seconds',time.monotonic()-s.start,'numeric_gate',read(O/'NUMERIC_CANDIDATE_GATE.json')['pass_'],flush=True)
    except BaseException:
        arrays=dict(outer_last_x=s.last_x,outer_last_fun=s.last_fun)
        if states:arrays.update(partial_times=knots,partial_q=states,partial_world=worlds)
        atomic_record('FORMAL_EXCEPTION_STATE.npz',arrays,dict(error=traceback.format_exc(),seconds=time.monotonic()-s.start,local_calls=s.local_calls,not_a_complete_candidate=True))
        raise
    finally:protect()

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='selftest':adapter_test()
    else:run()
