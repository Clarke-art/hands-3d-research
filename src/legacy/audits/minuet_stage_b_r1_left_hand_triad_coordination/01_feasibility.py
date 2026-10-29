from stage_common import *
from left_chord_motion import *
assert not (P/'STATIC_FEASIBILITY.json').exists()
tl=read(P/'PERFORMANCE_TIMELINE.json');co=EventCoordinator(tl['notes'],DEFAULT_POLICY);dump('GENERATION_POLICY.json',DEFAULT_POLICY)
states=np.tile(co.nominal,(3,1));states[1,6:]=co.bounds[:,0].ravel();states[2,6:]=co.bounds[:,1].ravel()
points,joints=fk_batch(states);error=0
for i,st in enumerate(states):
    RR=extra_rotation(st[3:6])@RBASE
    expected=np.array([c.fk('L',d,np.radians(st[6:].reshape(5,4)[j]))[0]@RR.T+BASE+st[:3]/1000 for j,d in enumerate(c.DIGITS)])
    error=max(error,float(np.max(abs(expected-points[i]))))
assert error<1e-12
tasks=[(n['finger']-1,i,0,6.) for i,n in enumerate(co.events)];rows=[]
for label,t,lift in [('surface_at_NOTE_ON',tl['notes'][0]['note_on'],0),('all_three_fully_down',tl['notes'][0]['note_on']+.035,0),('prepared_above_surfaces',tl['notes'][0]['note_on']-.075,.009)]:
    tt=[(j,i,lift,w) for j,i,l,w in tasks];fit=co.static_solve(t,tt);st=fit.x[:26];xy=fit.x[26:].reshape(3,2);pp,_=fk_batch(st)
    gaps=[o.measure(pp[0,j],co.events[i]['midi_note'],co.key_angles(t)[co.events[i]['key_index']]) for j,i,l,w in tt]
    errs=[float(np.linalg.norm(pp[0,j]-co.target(i,xy,t,lift))*1000) for j,i,l,w in tt]
    rows.append(dict(test=label,time=t,state=st,contact_xy_mm=xy,task_contact_error_mm=errs,
        raw_key_surface_measures=gaps,lift_m=lift,nfev=fit.nfev,converged=bool(fit.success),same_shared_root=True,
        active_fingers=[n['finger'] for n in co.events],new_actions=0))
distinct=[c.SETUPS['L',c.DIGITS[n['finger']-1]][0] for n in co.events]
assert len(set(b for names in distinct for b in names))==9
proxyclear=all(max(r['task_contact_error_mm'])<8 for r in rows if r['lift_m']==0)
dump('STATIC_FEASIBILITY.json',dict(static_tests=rows,left_FK_parity_max_m=error,
    active_chains_distinct=distinct,active_chains_independent=True,common_root_unknown=True,
    left_rest_axes_and_markers_used=True,right_trajectory_mirror_used=False,
    point_contact_static_supported=proxyclear,dynamic_feasibility_not_yet_proven=True,new_dynamic_candidates=0,
    bounds_deg=co.bounds,nominal=co.nominal,state_low=co.state_low,state_high=co.state_high))
other=[dict(n,midi_note=n['midi_note']+2,key_index=n['key_index']+2) for n in co.events]
alt=EventCoordinator(other,DEFAULT_POLICY)
assert len(alt.tasks(other[0]['note_on']+.035))==3
try:EventCoordinator([dict(n,finger=1) for n in co.events],DEFAULT_POLICY)
except ValueError:duplicate_rejected=True
else:raise AssertionError('same-finger conflict was not rejected')
dump('GENERIC_CHORD_INTERFACE_CHECK.json',dict(mode='PLANNING_ONLY_NO_SECOND_ANIMATION',
    alternate_three_targets=[n['midi_note'] for n in other],concurrent_target_count=3,
    alternate_black_white_geometries=[alt.keys[n['midi_note']]['color'] for n in other],
    valid_three_independent_tasks=True,duplicate_finger_overlap_rejected=duplicate_rejected,
    new_actions=0,new_dynamic_candidates=0,claim='Another target set is accepted without code edits, not dynamically approved.'))
print('FINITE_LEFT_MULTI_CONTACT',[(r['test'],r['task_contact_error_mm'],r['state'][:6]) for r in rows],proxyclear,flush=True)
