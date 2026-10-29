from native_model import *
from scipy.interpolate import BSpline,PchipInterpolator,PPoly
from scipy.spatial.transform import Rotation,RotationSpline
from scipy.optimize import NonlinearConstraint,Bounds
import itertools

RAWBASE=archive(O/'BASELINE_ACTUAL.npz');rawt=RAWBASE['times']
KEPT=[]
for i,t in enumerate(rawt):
    if not KEPT or t-rawt[KEPT[-1]]>1e-10:KEPT.append(i)
KEPT=np.asarray(KEPT,dtype=int)
BASE={k:v[KEPT] if v.ndim and v.shape[0]==len(rawt) else v for k,v in RAWBASE.items()}
T=BASE['times'];DURATION=END-START
assert np.min(np.diff(T))>1e-10
def unique_times(values):
    out=[]
    for t in sorted(values):
        if not out or t-out[-1]>1e-10:out.append(float(t))
    return np.asarray(out)
QREF=PchipInterpolator(T,BASE['q_deg'].reshape(-1,20))
PREF=PchipInterpolator(T,BASE['rig_world'][:,:3,3])
RREF=RotationSpline(T,Rotation.from_matrix(BASE['rig_world'][:,:3,:3]))
SCALE=np.einsum('kji,kjl->kil',RREF(T).as_matrix(),BASE['rig_world'][:,:3,:3])
assert np.max(abs(SCALE-np.eye(3)))<1e-5
KNOTS=np.r_[np.repeat(START,4),START+DURATION/3,START+2*DURATION/3,np.repeat(END,4)]
IDENT=BSpline(KNOTS,np.eye(6),3)
# C1 zero displacement and zero velocity at both boundaries eliminate four
# coefficients per channel. Remaining two coefficients are shared in time.
FREE=[2,3];SIZE=52
LIMIT=np.r_[np.repeat(8.,3),np.repeat(4.,3),np.repeat(8.,20)]
PAIRLIST=list(itertools.combinations(DIGITS,2))
union=set(v for d in ROIS.values() for v in d['vertices'])
REGIONS={d:np.array(ROIS[d]['vertices'],dtype=int) for d in DIGITS}
REGIONS['PALM_SHARED_WEB']=np.array([i for i in range(len(W)) if i not in union])
DW=np.column_stack([W[:,[i for i,n in enumerate(M['bones']) if n.startswith(d+'_')]].sum(1) for d in DIGITS])
REGIONS['CROSS_DIGIT_MIXED']=np.flatnonzero((DW>.05).sum(1)>=2)
WP=REST[BN['WRIST_R'],:3,3]
def coeff(x):
    c=np.zeros((6,26));c[FREE]=np.asarray(x).reshape(2,26);return c
def correction(x,t,order=0):return IDENT(np.asarray(t),nu=order)@coeff(x)
def skew(v):
    v=np.asarray(v);out=np.zeros(v.shape[:-1]+(3,3))
    out[...,0,1]=-v[...,2];out[...,0,2]=v[...,1];out[...,1,0]=v[...,2]
    out[...,1,2]=-v[...,0];out[...,2,0]=-v[...,1];out[...,2,1]=v[...,0]
    return out
def right_jac(v):
    a=np.linalg.norm(v,axis=-1);K=skew(v);safe=np.maximum(a,1e-8)
    f=np.where(a>1e-5,(1-np.cos(a))/safe**2,.5-a*a/24)
    g=np.where(a>1e-5,(a-np.sin(a))/safe**3,1/6-a*a/120)
    return np.eye(3)-f[...,None,None]*K+g[...,None,None]*(K@K)
def state(x,t):
    t=np.atleast_1d(t);delta=correction(x,t);q=(QREF(t)+delta[:,6:]).reshape(-1,5,4)
    R=RREF(t).as_matrix();Rd=Rotation.from_rotvec(np.radians(delta[:,3:6])).as_matrix()
    world=np.tile(np.eye(4),(len(t),1,1));world[:,:3,:3]=R@Rd
    # Rotation about the frozen wrist pivot, never about the far rig origin.
    world[:,:3,3]=PREF(t)+np.einsum('kij,kj->ki',R,WP-np.einsum('kij,j->ki',Rd,WP))+delta[:,:3]/1000
    return q,world
def key_angles(t):
    return np.column_stack([np.interp(t,T,BASE['key_angles'][:,i]) for i in range(88)])
def wrist_kinematics(x,t):
    t=np.atleast_1d(t);d=correction(x,t);d1=correction(x,t,1);d2=correction(x,t,2)
    R=RREF(t).as_matrix();w0=RREF(t,1);a0=RREF(t,2)
    # Actual pivot position is unchanged by a pivot-centred rotation correction.
    rp=np.einsum('kij,j->ki',R,WP)
    pos=PREF(t)+rp+d[:,:3]/1000
    vel=PREF(t,1)+np.einsum('kij,kj->ki',R,np.cross(w0,WP))+d1[:,:3]/1000
    acc=PREF(t,2)+np.einsum('kij,kj->ki',R,np.cross(a0,WP)+np.cross(w0,np.cross(w0,WP)))+d2[:,:3]/1000
    rv=np.radians(d[:,3:6]);rv1=np.radians(d1[:,3:6]);Rd=Rotation.from_rotvec(rv).as_matrix()
    omega=np.einsum('kji,kj->ki',Rd,w0)+np.einsum('kij,kj->ki',right_jac(rv),rv1)
    # Bounded angular acceleration is measured from the analytic omega function
    # on original single-side segments; exact joint polynomial gates are separate.
    return pos,vel,acc,omega

def polynomial_extrema(pp):
    c=pp.c;h=np.diff(pp.x)[:,None];count=c.shape[-1]
    def ev(u):return ((c[0]*u+c[1])*u+c[2])*u+c[3]
    vals=[ev(np.zeros_like(h)),ev(h)]
    a=3*c[0];b=2*c[1];cc=c[2];dis=b*b-4*a*cc
    for sign in [-1,1]:
        safe=np.where(abs(a)>1e-14,2*a,1)
        u=(-b+sign*np.sqrt(np.maximum(dis,0)))/safe
        good=(dis>=0)&(abs(a)>1e-14)&(u>=0)&(u<=h)
        u=np.clip(u,0,h);vals.append(np.where(good,ev(u),np.nan))
    u=-cc/np.where(abs(b)>1e-14,b,1)
    good=(abs(a)<=1e-14)&(abs(b)>1e-14)&(u>=0)&(u<=h)
    vals.append(np.where(good,ev(np.clip(u,0,h)),np.nan))
    stack=np.stack(vals);return np.nanmin(stack,axis=(0,1)),np.nanmax(stack,axis=(0,1))
BREAKS=unique_times(np.r_[T,KNOTS]);BREAKS=BREAKS[(BREAKS>=START)&(BREAKS<=END)]
def qpoly(x):
    a=BREAKS[:-1];delta=correction(x,a);d1=correction(x,a,1);d2=correction(x,a,2);d3=correction(x,a,3)
    return PPoly(np.array([(QREF(a,3)+d3[:,6:])/6,(QREF(a,2)+d2[:,6:])/2,QREF(a,1)+d1[:,6:],QREF(a)+delta[:,6:]]),BREAKS)
def extrema_any(pp):
    # Promote polynomial degree to cubic for the same exact finite root check.
    pp=PPoly(np.r_[np.zeros((4-len(pp.c),)+pp.c.shape[1:]),pp.c],pp.x)
    return polynomial_extrema(pp)

class Problem:
    def __init__(self):
        self.calls=0;self.timer=None;self.cache_x=None;self.cache_y=None
        stages=[e[p]+d for e in EVENTS for p in ['note_on','note_off'] for d in [-.18,-.075,0,.0175,.035,.04,.07]]
        self.t=unique_times(np.r_[START,END,np.arange(START,END,.04),[t for t in stages if START<=t<=END]])
        self.angles=key_angles(self.t);q,w=state(np.zeros(SIZE),self.t)
        self.baseV=native(q,w)
        self.active=[];self.roles=[]
        policy=read(ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion/GENERATION_POLICY.json')
        # Only the original role-task method is extracted, never its solver.
        tree=ast.parse(valid_path(ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion/coordinated_motion.py').read_text(encoding='utf-8-sig'))
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='EventCoordinator')
        task=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='tasks')
        import types
        smooth_ns={'np':np};extract(OLD/'performance_core.py',['smooth'],smooth_ns)
        ns={'c':types.SimpleNamespace(smooth=smooth_ns['smooth'])}
        exec(compile(ast.Module(body=[task],type_ignores=[]),'A2_role_tasks', 'exec'),ns)
        co=types.SimpleNamespace(events=EVENTS,policy=policy)
        for it,t in enumerate(self.t):
            self.roles.append(ns['tasks'](co,float(t)))
            for e in EVENTS:
                if e['note_on']<=t<e['note_off']:self.active.append((it,e))
        self.keys=[]
        for key,g,pl in COMPONENTS:
            v=np.asarray(g['vertices']);pv=np.asarray(key['press_pivot'])
            local=np.einsum('kvj,kjl->kvl',self.baseV-pv,rot(self.angles[:,key['key_index']],key['press_axis']))+pv
            # Fixed 60mm planning neighbourhood. A complete continuous skin
            # displacement certificate has NOT been established; this list
            # must not be represented as full continuous collision coverage.
            if np.any(np.all(local.max(1)+.06>=v.min(0),axis=1)&np.all(local.min(1)-.06<=v.max(0),axis=1)):
                self.keys.append((key,g,pl))
        self.geo_baseline=self.geometric_metrics(self.baseV)
        features=archive(SRC/'SOURCE_FEATURES.npz')
        self.role_checks=[]
        source_ids=['R03','R04','R05','R06']
        for it,taskrows in enumerate(self.roles):
            for j,idx,lift,weight in taskrows:
                e=EVENTS[idx]
                if e['note_on']<=self.t[it]<e['note_off']:continue
                key=KEYS[e['key_index']]
                if e['note_id'] in source_ids:xy=features['preferred_xy_mm'][source_ids.index(e['note_id'])]
                else:
                    pv=np.asarray(key['press_pivot']);a=self.angles[it,key['key_index']]
                    xy=((self.baseV[it,PADIDS[j]]-pv)@rot(a,key['press_axis'])+pv)[:2]*1000
                    lo,hi=inset(key);xy=np.clip(xy,lo,hi)
                target=point_on_key(key,xy,self.angles[it,key['key_index']],lift)
                error=np.linalg.norm(self.baseV[it,PADIDS[j]]-target)*1000
                self.role_checks.append((it,j,target,float(error)))
        self.owner=[]
        for it,t in enumerate(self.t):
            owned={}
            for e in EVENTS:
                if e['note_on']<=t<e['note_off']+.04:owned.setdefault(e['key_index'],set()).add(DIGITS[e['finger']-1])
            for key,g,pl in self.keys:
                for region in REGIONS:self.owner.append(region in owned.get(key['key_index'],set()))
        self.owner=np.array(self.owner)
        self.bounds_upper=np.where(self.owner,1e3,np.minimum(.5,self.geo_baseline['key_depth']+.02))
        self.derivative_t=unique_times(np.r_[np.linspace(START,END,241),BREAKS[:-1]+1e-10,BREAKS[1:]-1e-10])
        # Joint envelopes are exact polynomial extrema, not sample maxima.
        pp=qpoly(np.zeros(SIZE));vl,vh=extrema_any(pp.derivative());al,ah=extrema_any(pp.derivative(2))
        self.qv=np.maximum(abs(vl),abs(vh));self.qa=np.maximum(abs(al),abs(ah))
        bp,bv,ba,bw=wrist_kinematics(np.zeros(SIZE),self.derivative_t)
        self.root_lo=bp.min(0);self.root_hi=bp.max(0)
        self.root_v=np.max(abs(bv),axis=0);self.root_a=np.max(abs(ba),axis=0);self.root_w=np.max(abs(bw),axis=0)
        self.root_speed=float(np.linalg.norm(bv,axis=1).max());self.angular_speed=float(np.linalg.norm(bw,axis=1).max())
    def budget(self):
        if self.timer is not None:
            if time.monotonic()-self.timer>=180:raise TimeoutError('NUMERICAL_TIME_180_SECONDS')
            if self.calls>=6000:raise TimeoutError('NATIVE_CALL_6000_LIMIT')
    def geometric_metrics(self,V):
        depths=[]
        for it,t in enumerate(self.t):
            for key,g,pl in self.keys:
                pv=np.asarray(key['press_pivot']);local=(V[it]-pv)@rot(self.angles[it,key['key_index']],key['press_axis'])+pv
                depth=np.maximum(0,-np.max(local@pl[:,:3].T-pl[:,3],axis=1)*1000)
                for ids in REGIONS.values():depths.append(float(depth[ids].max()))
        gaps=[]
        for a,b in PAIRLIST:
            va=V[:,REGIONS[a]];vb=V[:,REGIONS[b]]
            # Signed separating-axis gap of complete digit-ROI AABBs. Positive
            # certifies these ROIs separated; negative is only a conservative
            # overlap warning, not an actual penetration depth.
            gaps.extend(np.maximum(va.min(1)-vb.max(1),vb.min(1)-va.max(1)).max(1)*1000)
        return dict(key_depth=np.array(depths),pair_aabb_gap=np.array(gaps))
    def constraints(self,x):
        self.budget()
        if self.cache_x is not None and np.array_equal(x,self.cache_x):return self.cache_y
        self.calls+=1;q,world=state(x,self.t);V=native(q,world)
        values=[]
        for it,e in self.active:
            key=KEYS[e['key_index']];pv=np.asarray(key['press_pivot']);p=(V[it,PADIDS[e['finger']-1]]-pv)@rot(self.angles[it,e['key_index']],key['press_axis'])+pv
            s=key['key_top_playable_surface'][0]
            values.extend([(p[0]-s['xmin'])*1000,(s['xmax']-p[0])*1000,(p[1]-s['ymin'])*1000,(s['ymax']-p[1])*1000,3-abs((p[2]-s['z'])*1000)])
        geo=self.geometric_metrics(V)
        values.extend(self.bounds_upper-geo['key_depth'])
        values.extend(geo['pair_aabb_gap']-self.geo_baseline['pair_aabb_gap']+.02)
        for it,j,target,original_error in self.role_checks:
            values.append(original_error+.02-np.linalg.norm(V[it,PADIDS[j]]-target)*1000)
        pp=qpoly(x);lo,hi=extrema_any(pp);bounds=QBOUNDS.transpose(1,0,2).reshape(2,20)
        values.extend(lo-bounds[0]);values.extend(bounds[1]-hi)
        vl,vh=extrema_any(pp.derivative());al,ah=extrema_any(pp.derivative(2))
        values.extend(self.qv-np.maximum(abs(vl),abs(vh))+1e-6)
        values.extend(self.qa-np.maximum(abs(al),abs(ah))+1e-5)
        cp=PPoly.from_spline((KNOTS,coeff(x)[:,6:].T,3)) if False else None
        add_peak=np.max(abs(correction(x,self.derivative_t,1)[:,6:]),axis=0)
        values.extend(180-add_peak)
        pos,vel,acc,omega=wrist_kinematics(x,self.derivative_t)
        values.extend((pos.min(0)-self.root_lo)*1000+1e-6);values.extend((self.root_hi-pos.max(0))*1000+1e-6)
        values.extend((self.root_v-np.max(abs(vel),axis=0))*1000+1e-5)
        values.extend((self.root_a-np.max(abs(acc),axis=0))*1000+1e-4)
        values.extend(np.degrees(self.root_w-np.max(abs(omega),axis=0))+1e-5)
        values.extend([(self.root_speed-np.linalg.norm(vel,axis=1).max())*1000+1e-5,np.degrees(self.angular_speed-np.linalg.norm(omega,axis=1).max())+1e-5])
        y=np.asarray(values);assert y.ndim==1 and np.isfinite(y).all()
        self.cache_x=np.array(x);self.cache_y=y;return y
    def objective(self,x):
        self.budget()
        delta=correction(x,self.t);deriv=correction(x,self.t,1)
        return float(np.sum((delta/np.r_[np.repeat(2.,3),np.repeat(1.,3),np.repeat(4.,20)])**2)/len(self.t)+.0001*np.sum(deriv[:,6:]**2)/len(self.t))
    def objective_jac(self,x):
        A=IDENT(self.t)[:,FREE];A1=IDENT(self.t,nu=1)[:,FREE];C=np.asarray(x).reshape(2,26)
        inv=np.r_[np.repeat(.25,3),np.repeat(1.,3),np.repeat(1/16,20)]
        g=2*(A.T@A)@C*inv/len(self.t);g[:,6:]+=.0002*(A1.T@A1)@C[:,6:]/len(self.t)
        return g.ravel()

