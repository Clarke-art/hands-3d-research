from stage_common import *
from left_continuous_motion import *
assert not (P/'CONTINUOUS_PREFLIGHT.json').exists()
tl=read(P/'PERFORMANCE_TIMELINE.json');co=EventCoordinator(tl['notes'],DEFAULT_POLICY);dump('GENERATION_POLICY.json',DEFAULT_POLICY)
states=np.tile(co.nominal,(3,1));states[1,6:]=co.bounds[:,0].ravel();states[2,6:]=co.bounds[:,1].ravel();points,_=fk_batch(states);parity=0
for i,st in enumerate(states):
    R=extra_rotation(st[3:6])@RBASE;expected=np.array([c.fk('L',d,np.radians(st[6:].reshape(5,4)[j]))[0]@R.T+BASE+st[:3]/1000 for j,d in enumerate(c.DIGITS)])
    parity=max(parity,float(np.max(abs(points[i]-expected))))
assert parity<1e-12
groups=sorted(co.onset_groups);testtimes=[('first_chord_down',groups[0]+.035),('held_chord_next_ring_prepare',groups[1]-.075),('chord_to_single_boundary',groups[1]),
    ('next_middle_single_down',groups[2]+.035),('index_single_down',groups[3]+.035),('middle_return_down',groups[4]+.035)]
results=[]
for label,t in testtimes:
    fit=co.static_solve(t);st=fit.x[:26];xy=fit.x[26:].reshape(len(co.events),2);pads,_=fk_batch(st);measures=[]
    for r in co.task_components(t):
        goal=sum(co.target(i,xy,t,lift)*factor for i,lift,factor in r['components'])
        measures.append(dict(finger=r['finger']+1,phase=r['phase'],weight=r['weight'],components=r['components'],
            goal_error_mm=float(np.linalg.norm(pads[0,r['finger']]-goal)*1000)))
    results.append(dict(test=label,time=t,state=st,xy_mm=xy,targets=measures,nfev=fit.nfev,converged=bool(fit.success),new_actions=0))
supported=all(max(r['goal_error_mm'] for r in row['targets'] if r['weight']>3)<8 for row in results)
handoff=next(r for r in results if r['test']=='chord_to_single_boundary');assert len(handoff['targets'])==4
# A common source-derived released-to-preparation handoff has two components,
# while every currently held note remains one exact target.
blendtimes=[]
for t in np.arange(0,tl['presentation_duration_sec'],1/120):
    ds=co.task_components(t)
    for r in ds:
        if r['phase']=='HOLD_OR_PRESS':assert len(r['components'])==1 and r['components'][0][2]==1
        if len(r['components'])>1:blendtimes.append(dict(time=float(t),finger=r['finger']+1,components=r['components']))
dump('CONTINUOUS_PREFLIGHT.json',dict(mode='ONE_FINITE_PREFLIGHT_BATCH_NO_DYNAMIC_CANDIDATE',tests=results,
    point_contact_supported=supported,left_FK_parity_max_m=parity,chord_to_single_mechanical_target_peak=4,
    exact_source_different_onset_held_overlap_count=0,continuous_released_to_next_prepare_samples=blendtimes,
    currently_held_targets_never_blended=True,required_register_shift=False,new_dynamic_candidates=0))
print('FINITE_CONTINUOUS_PREFLIGHT',[(r['test'],[(x['finger'],x['phase'],round(x['goal_error_mm'],3)) for x in r['targets']]) for r in results],supported,flush=True)
