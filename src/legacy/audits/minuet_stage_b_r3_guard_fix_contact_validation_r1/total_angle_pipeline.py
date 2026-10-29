"""One PCHIP of bounded TOTAL q. Actual delta budget in degrees everywhere.

Phase envelope determines windows, never multiplies an interpolated correction.
Freeze the PCHIP influence collar to preserve reference position/velocity outside
windows. No output angle clipping, guard relaxation, or root optimization.
"""
from stage_common import *
from left_continuous_motion import *
import importlib.util
spec=importlib.util.spec_from_file_location('frozen_region_kernel',R3/'contact_region.py')
region=importlib.util.module_from_spec(spec);spec.loader.exec_module(region)
spec=importlib.util.spec_from_file_location('independent_recorder',ISO/'diagnostic_recorder.py')
rec=importlib.util.module_from_spec(spec);spec.loader.exec_module(rec)
skin_caps_batch=region.skin_caps_batch

def actual_delta_bounds(reference_q,engineering_low,engineering_high,budget):
    return np.maximum(-budget,engineering_low-reference_q),np.minimum(budget,engineering_high-reference_q)

def total_angles(reference_q,actual_delta):return reference_q+actual_delta

class TotalAnglePipeline:
    def __init__(self):
        self.policy=read(P/'GENERATION_POLICY.json');self.timeline=read(P/'PERFORMANCE_TIMELINE.json')
        self.co=EventCoordinator(self.timeline['notes'],self.policy['source_policy'])
        self.oldfit=read(R2/'COORDINATED_TRAJECTORY_FIT.json');self.knots=np.array(self.oldfit['knots']);self.reference_states=np.array(self.oldfit['solved_states'])
        self.reference_q=self.reference_states[:,6:];self.refcurve=PchipInterpolator(self.knots,self.reference_q,axis=0)
        self.budget=np.array(self.policy['joint_delta_limits_deg']).ravel()
        self.low=self.co.state_low[6:];self.high=self.co.state_high[6:]
        self.windows=[]
        for j in range(5):
            windows=[]
            for n in self.co.events:
                if n['finger']!=j+1:continue
                a=max(0,n['note_on']-self.policy['source_policy']['prepare_sec']);b=min(self.knots[-1],n['note_off']+self.policy['source_policy']['recovery_sec'])
                if windows and a<=windows[-1][1]+1e-12:windows[-1][1]=max(b,windows[-1][1])
                else:windows.append([a,b])
            self.windows.append(windows)
        # A changed scalar node i influences segments i-2 through i+1 because
        # PCHIP derivatives at i-1,i,i+1 use adjacent secants. Entire influence
        # interval must be strictly inside a phase window.
        self.mutable=np.zeros_like(self.reference_q,dtype=bool)
        for i in range(2,len(self.knots)-2):
            for j,windows in enumerate(self.windows):
                if any(self.knots[i-2]>a+1e-12 and self.knots[i+2]<b-1e-12 for a,b in windows):self.mutable[i,j*4:(j+1)*4]=True
        self.lower,self.upper=actual_delta_bounds(self.reference_q,self.low,self.high,self.budget)
        self.mutable&=(self.upper-self.lower)>1e-12
        self.free=np.flatnonzero(self.mutable.ravel())
        self.boundaries=np.unique([t for ws in self.windows for w in ws for t in w])
        self.A=dict(np.load(R2/'motion.npz'));self.times=self.A['times']
        self.check_times=np.unique(np.r_[self.times,self.knots,self.boundaries,[n[k] for n in self.co.events for k in ['note_on','note_off']]])

    def outside_mask(self,times):
        t=np.atleast_1d(times);mask=np.ones((len(t),20),dtype=bool)
        for j,ws in enumerate(self.windows):
            active=np.zeros(len(t),dtype=bool)
            for a,b in ws:active|=(t>a)&(t<b)
            mask[:,j*4:(j+1)*4]=~active[:,None]
        return mask

    def expand(self,x):
        delta=np.zeros_like(self.reference_q);delta.ravel()[self.free]=x
        return delta

    def curve(self,x):return PchipInterpolator(self.knots,total_angles(self.reference_q,self.expand(x)),axis=0)

    def evaluate(self,x,times):
        return self.curve(x)(times)

    def certify(self,x):
        curve=self.curve(x);delta_curve=type(curve).construct_fast(curve.c-self.refcurve.c,self.knots,extrapolate=False,axis=0)
        domain=polynomial_domain_certificate(curve,self.low,self.high)
        budget=polynomial_domain_certificate(delta_curve,-self.budget,self.budget)
        out=self.outside_mask(self.check_times);diff=curve(self.check_times)-self.refcurve(self.check_times)
        outside_max=float(np.max(abs(diff[out]))) if np.any(out) else 0.
        boundary=[]
        for j,ws in enumerate(self.windows):
            for a,b in ws:
                for t in [a,b]:
                    sl=slice(j*4,(j+1)*4);boundary.append(dict(finger=j+1,time=float(t),position_difference_max_deg=float(np.max(abs(curve(t)[sl]-self.refcurve(t)[sl]))),velocity_difference_max_deg_sec=float(np.max(abs(curve.derivative()(t)[sl]-self.refcurve.derivative()(t)[sl])))))
        # Exact left/right polynomial limit checks at all internal knots.
        cc=curve.c;h=np.diff(self.knots)[:,None]
        left=((cc[0]*h+cc[1])*h+cc[2])*h+cc[3];leftv=(3*cc[0]*h+2*cc[1])*h+cc[2]
        c1pos=float(np.max(abs(left[:-1]-cc[3,1:])));c1vel=float(np.max(abs(leftv[:-1]-cc[2,1:])))
        return dict(domain=domain,actual_delta_budget=budget,outside_window_max_change_deg=outside_max,
            window_boundaries=boundary,C1_position_jump_max_deg=c1pos,C1_velocity_jump_max_deg_sec=c1vel,
            boundary_position_and_velocity_preserved=all(r['position_difference_max_deg']<1e-10 and r['velocity_difference_max_deg_sec']<1e-8 for r in boundary),
            output_domain_guarantee=domain['pass_'],pass_=domain['pass_'] and budget['pass_'] and outside_max<1e-10 and all(r['position_difference_max_deg']<1e-10 and r['velocity_difference_max_deg_sec']<1e-8 for r in boundary) and c1pos<1e-10 and c1vel<1e-8)

def polynomial_domain_certificate(curve,low,high,tolerance=1e-7):
    # Finite exact-polynomial extrema: endpoints plus real roots of derivative.
    # There is no sampling-only assertion of continuous domain legality.
    low=np.asarray(low);high=np.asarray(high);worst=0.;violations=[];segments=len(curve.x)-1
    for k in range(segments):
        h=curve.x[k+1]-curve.x[k]
        for j in range(len(low)):
            coeff=curve.c[:,k,j];a,b,d=3*coeff[0],2*coeff[1],coeff[2];ts=[0.,h]
            if abs(a)>1e-14:
                disc=b*b-4*a*d
                if disc>=0:
                    sd=np.sqrt(disc)
                    for t in [(-b-sd)/(2*a),(-b+sd)/(2*a)]:
                        if 0<t<h:ts.append(float(t))
            elif abs(b)>1e-14:
                t=-d/b
                if 0<t<h:ts.append(float(t))
            vals=np.polyval(coeff,ts);ex=np.maximum(np.maximum(low[j]-vals,vals-high[j]),0.)
            worst=max(worst,float(ex.max()))
            for z in np.flatnonzero(ex>tolerance):violations.append(dict(segment=k,flat_index=j,time_sec=float(curve.x[k]+ts[z]),actual_deg=float(vals[z]),lower_deg=float(low[j]),upper_deg=float(high[j]),excess_deg=float(ex[z])))
    return dict(pass_=not violations,max_excess_deg=worst,tolerance_deg=tolerance,segments_checked=segments,dofs=len(low),method='all scalar cubic extrema and endpoints',violations=violations)
