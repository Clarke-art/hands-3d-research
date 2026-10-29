"""Post-solve evidence only. Never calls an optimizer or adjusts the result."""
from trajectory_solver import *
assert (P/'FORMAL_ATTEMPT_STARTED.json').exists()
path=P/'FORMAL_RESULT.npz'
if not path.exists():
    path=P/'FORMAL_CHECKPOINT.npz'
    assert path.exists(),'No accepted numerical iterate exists; report the supervisor receipt without manufacturing motion'
res=dict(np.load(path));knots=res['knots'];q=res['q'].reshape(-1,20)
t=D['times'];B,V,A,C=spline_matrices(knots,t)
qq=(B@q).reshape(-1,5,4);vel=(V@q).reshape(-1,5,4);acc=(A@q).reshape(-1,5,4)
np.savez_compressed(P/'TERMINAL_TRAJECTORY_EVIDENCE.npz',times=t,qdeg=qq,velocity=vel,acceleration=acc,
    source_qdeg=source_angles(t),knots=knots,knot_angles=res['q'])
lo=np.array([np.degrees(c.bounds(d)[0]) for d in c.DIGITS]).ravel()
hi=np.array([np.degrees(c.bounds(d)[1]) for d in c.DIGITS]).ravel()
base=read(P/'READONLY_MODEL_CHECK.json')
vlim=1.5*np.maximum(base['source_peak_velocity_deg_sec'],60)
alim=1.5*np.maximum(base['source_peak_acceleration_deg_sec2'],1000)
model=Spatial(t);g=model.evaluate(qq);source_g=model.evaluate(source_angles(t))
spatial=g[:len(t)*15].reshape(-1,15);source_spatial=source_g[:len(t)*15].reshape(-1,15)
rows=[]
for label,mask in [('FULL',np.ones(len(t),bool)),('EARLY',(t>=.778571)&(t<=2.134284)),('LATE',(t>=2.741426)&(t<=4.70571)),('START',t<=.35),('END',t>=5.492852)]:
    rows.append(dict(scope=label,source_min_key_slack_mm=float(source_spatial[mask,:5].min()),terminal_min_key_slack_mm=float(spatial[mask,:5].min()),
        source_min_pair_support_slack_mm=float(source_spatial[mask,5:].min()),terminal_min_pair_support_slack_mm=float(spatial[mask,5:].min())))
box=max(0,float(np.max(lo-C@q)),float(np.max(C@q-hi)))
dump('NUMERICAL_TERMINAL_DIAGNOSTICS.json',dict(evidence_from=path.name,samples=len(t),
    active_contacts=len(model.contacts),spatial_constraint_min_mm=float(g.min()),violations_over_1e_minus4=int(np.sum(g < -1e-4)),
    contact_constraint_min_mm=float(g[len(t)*15:].min()),engineering_bezier_box_violation_deg=box,
    joint_min_deg=qq.min(0),joint_max_deg=qq.max(0),peak_velocity_deg_sec=np.max(abs(vel),axis=0),
    peak_acceleration_deg_sec2=np.max(abs(acc),axis=0),velocity_limits=vlim,acceleration_limits=alim,
    velocity_gate=bool(np.all(np.max(abs(vel),axis=0)<=vlim)),acceleration_gate=bool(np.all(np.max(abs(acc),axis=0)<=alim)),
    derivative_continuity='C1 by shared analytic Hermite slopes; endpoint angular slopes exactly zero',
    naturalness='HUMAN_PENDING',scope_comparison=rows,
    pass_=bool(g.min()>=-1e-4 and box<1e-6 and np.all(np.max(abs(vel),axis=0)<=vlim) and np.all(np.max(abs(acc),axis=0)<=alim)),
    no_resolve=True,new_dynamic_candidates=0))
print('TERMINAL_NUMERIC_EVIDENCE',g.min(),'mm slack; box',box,flush=True)

