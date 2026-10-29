from window_problem import *
from scipy.optimize._numdiff import approx_derivative
import scipy,traceback
start=time.monotonic();p=Problem();x=np.zeros(SIZE)
suffix='_CLOCK_FIXED'
assert np.allclose(correction(x,[START,END]),0)
test=np.linspace(-.2,.2,SIZE)
assert np.max(abs(correction(test,[START,END])))<1e-12 and np.max(abs(correction(test,[START,END],1)))<1e-10
assert np.min(np.diff(np.unique(KNOTS)))>.25
for d in [0,1,2]:assert np.isfinite(correction(test,p.t,d)).all()
# Independent finite differences verify derivative orders on non-knot interiors.
t=np.linspace(START+.01,END-.01,12);eps=1e-5
assert np.max(abs((correction(test,t+eps)-correction(test,t-eps))/(2*eps)-correction(test,t,1)))<1e-5
assert np.max(abs((correction(test,t+eps,1)-correction(test,t-eps,1))/(2*eps)-correction(test,t,2)))<1e-4
q,w=state(x,T);V=native(q,w);error=float(np.linalg.norm(V-BASE['vertices'],axis=-1).max()*1000)
assert error<.01
tic=time.monotonic();c=p.constraints(x);ct=time.monotonic()-tic
tic=time.monotonic();j=approx_derivative(p.constraints,x,method='2-point',abs_step=1e-4);jt=time.monotonic()-tic
assert j.shape==(len(c),SIZE) and np.isfinite(j).all()
peakv=p.qv.tolist();peaka=p.qa.tolist()
reference=dict(joint_peak_velocity_deg_s=peakv,joint_peak_acceleration_deg_s2=peaka,root_pivot_range_m=[p.root_lo,p.root_hi],root_velocity_axis_m_s=p.root_v,root_acceleration_axis_m_s2=p.root_a,root_angular_axis_rad_s=p.root_w,root_speed_mm_s=p.root_speed*1000,root_angular_speed_deg_s=np.degrees(p.angular_speed),joint_extrema_method='Exact polynomial derivative roots on fixed source-readback PCHIP and spline break union',root_envelope_method='Analytic RotationSpline/PCHIP derivatives at dense single-side segment checks; continuous maxima not certified',acceleration_boundary_policy='C1 position/velocity joins, bounded single-side acceleration; finite acceleration jump separately reported, no claimed C2')
atomic_json('C1_REFERENCE_ENVELOPES'+suffix+'.json',reference)
atomic_record('CONSTRAINT_JACOBIAN_PREFLIGHT'+suffix+'.npz',dict(seed=x,constraints=c,jacobian=j,planning_times=p.t))
realistic=jt<8 and np.isfinite(p.qa).all() and np.isfinite(p.root_a).all()
atomic_json('COST_PREFLIGHT'+suffix+'.json',dict(pass_=bool(realistic),representation='Original C1 state adapter + six cubic B-spline coefficient slots per 26 channels; endpoint q/dq correction zero',maximum_coefficients=156,free_variables=SIZE,contact_xy_variables=0,spline_knots=KNOTS,unique_knot_min_dt_sec=float(np.min(np.diff(np.unique(KNOTS)))),raw_reference_times=len(rawt),coalesced_reference_times=len(T),removed_binary_equivalent_readback_nodes=len(rawt)-len(T),event_identity_times_unchanged=True,minimum_reference_dt=float(np.min(np.diff(T))),constraint_count=len(c),planning_times=len(p.t),key_components_planning=len(p.keys),constraint_seconds=ct,full_jacobian_seconds=jt,native_calls=p.calls,preflight_seconds=time.monotonic()-start,baseline_native_error_mm=error,seed_violation_max=float(max(0,-c.min())),rough_20_jacobian_seconds=jt*20,root_continuous_bound_status='UNKNOWN',no_formal_solver_started=True))
protect('PROTECTION_COST_PREFLIGHT'+suffix+'.json')
print('COST_PREFLIGHT',ct,jt,len(c),c.min(),realistic,flush=True)
