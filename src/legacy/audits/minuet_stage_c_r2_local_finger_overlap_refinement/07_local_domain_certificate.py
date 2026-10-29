from local_common import *
sys.path.insert(0,str(OLD/'_deps'))
import numpy as np
policy=read(P/'LOCAL_CORRECTION_POLICY.json');lock=read(P/'LOCAL_CORRECTION_POLICY_LOCK.json');assert sha(P/'LOCAL_CORRECTION_POLICY.json')==lock['policy_sha256']
num=dict(np.load(P/'source_numeric.npz'));start,end=policy['presentation_support_sec'];a,b=policy['plateau_sec'];amp=policy['maximum_delta_deg']
def s(u):return u*u*u*(10+u*(-15+6*u))
def d1(u):return 30*u*u*(1-u)*(1-u)
def d2(u):return 60*u*(1-u)*(1-2*u)
def correction(t):
    if t<=start or t>=end:return (0.,0.,0.)
    if t<a:
        u=(t-start)/(a-start);return amp*s(u),amp*d1(u)/(a-start),amp*d2(u)/(a-start)**2
    if t>b:
        u=(end-t)/(end-b);return amp*s(u),-amp*d1(u)/(end-b),amp*d2(u)/(end-b)**2
    return amp,0.,0.
T=np.unique(np.r_[np.arange(start,end+1e-8,1/240),start,a,b,end]);D=np.array([correction(t) for t in T]);old=np.array([np.interp(t,num['times'],num['qdeg'][:,3,3]) for t in T]);new=old+D[:,0]
assert np.all((-28<=new)&(new<=28))
assert correction(start)==(0,0,0) and correction(end)==(0,0,0)
newv=np.diff(new)/np.diff(T);oldv=np.diff(old)/np.diff(T)
h=1/240;boundaryspeed=max(abs(correction(start+h)[0]/h),abs(correction(end-h)[0]/h))
cert=dict(pass_=True,policy_sha256=lock['policy_sha256'],scope='Only altered Ring MCP spread DOF, finite local derivatives; inherited global WARN not requalified',changed_spread_range_deg=[float(new.min()),float(new.max())],engineering_spread_domain_deg=[-28,28],maximum_local_actual_delta_deg=float(np.max(abs(D[:,0]))),maximum_correction_velocity_deg_sec=float(np.max(abs(D[:,1]))),maximum_correction_acceleration_deg_sec2=float(np.max(abs(D[:,2]))),source_spread_sampled_velocity_max_deg_sec=float(np.max(abs(oldv))),corrected_spread_sampled_velocity_max_deg_sec=float(np.max(abs(newv))),analytic_support_boundary_delta_deg=[0,0],analytic_support_boundary_velocity_deg_sec=[0,0],analytic_support_boundary_acceleration_deg_sec2=[0,0],quintic_envelope_C2=True,baked_LINEAR_boundary_extra_speed_upper_estimate_deg_sec=float(boundaryspeed),baked_continuity_note='Original and corrected Actions remain LINEAR-sampled, not mathematically C2. Analytic correction is C2 with zero endpoint derivatives; at240Hz the first/last extra correction chord slope is under0.2deg/s, explicitly retained as finite bake diagnostic.',motion_solver_calls=0,refit_calls=0,source_rig_rest_modified=False)
assert boundaryspeed<.2
dump('LOCAL_DOMAIN_AND_CONTINUITY.json',cert)
print('LOCAL_SINGLE_DOF_DOMAIN_AND_BOUNDARY_CERTIFICATE_PASS',flush=True)
