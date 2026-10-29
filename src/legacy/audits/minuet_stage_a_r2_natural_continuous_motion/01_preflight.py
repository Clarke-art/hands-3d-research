from stage_common import *
from coordinated_motion import *
assert not (P/'INPUT_LOCK.json').exists()
tl=read(R1/'PERFORMANCE_TIMELINE.json');oldlock=read(R1/'INPUT_LOCK.json')
assert sha(SOURCE)==oldlock['source_sha256'];assert sha(R1/'PERFORMANCE_TIMELINE.json')==oldlock['timeline_sha256']
dump('PERFORMANCE_TIMELINE.json',tl);dump('GENERATION_POLICY.json',DEFAULT_POLICY)
co=EventCoordinator(tl['notes'],DEFAULT_POLICY)
# Vectorized FK parity, deterministic static inputs; no trajectories or actions.
states=np.tile(co.nominal,(3,1));states[1,6:]=B[:,0].ravel();states[2,6:]=B[:,1].ravel()
p,j=fk_batch(states);error=0.
for i,st in enumerate(states):
    RR=extra_rotation(st[3:6])@RBASE
    expected=np.array([c.fk('R',d,np.radians(st[6:].reshape(5,4)[z]))[0]@RR.T+BASE+st[:3]/1000 for z,d in enumerate(c.DIGITS)])
    error=max(error,float(np.max(abs(p[i]-expected))))
assert error<1e-12
rows=[];events=tl['notes'];firstblack=next(i for i,n in enumerate(events) if c.KEYS[n['key_index']]['color']=='BLACK')
leap=max(range(len(events)-1),key=lambda i:abs(events[i+1]['midi_note']-events[i]['midi_note']))
for label,i,tasks in [('first_white',0,[(events[0]['finger']-1,0,0,6)]),
    ('first_black',firstblack,[(events[firstblack]['finger']-1,firstblack,0,6)]),
    ('largest_adjacent_interval',leap,[(events[leap]['finger']-1,leap,0,6),(events[leap+1]['finger']-1,leap+1,.008,4)])]:
    t=events[i]['note_on']+.035;fit=co.static_solve(t,tasks);pads,_=fk_batch(fit.x)
    residuals=[float(np.linalg.norm(pads[0,j]-co.target(ii,co.xy_seed,t,lift))*1000) for j,ii,lift,w in tasks]
    rows.append(dict(test=label,source_indices=[r[1] for r in tasks],nfev=fit.nfev,success=bool(fit.success),
        state=fit.x,task_contact_error_mm=residuals,generated_animation=False))
dump('STATIC_PLANNING_PREFLIGHT.json',dict(mode='FINITE_STATIC_PLANNING_TESTS_NO_ANIMATION',FK_batch_parity_max_m=error,
    tests=rows,new_candidates=0,not_a_dynamic_quality_approval=True))
repeat=[]
for a,b in zip(events,events[1:]):
    if a['note_id'] in co.repeats:
        ts=[b['note_on']-.045,b['note_on'],b['note_on']+.035]
        values=[float(co.key_angles(t)[b['key_index']]/c.KEYS[b['key_index']]['press_angle_rad']) for t in ts]
        assert abs(values[0]-1)<1e-7 and abs(values[1]-.42)<1e-7 and abs(values[2]-1)<1e-7
        repeat.append(dict(old=a['note_id'],next=b['note_id'],times=ts,pressures=values))
dump('REPEATED_KEY_PLANNING_CHECK.json',dict(mechanism='Latest-note ownership with event-conditioned partial reset; no old/new max',
    original_NOTE_ON_OFF_unchanged=True,audio_retrigger_unchanged=True,checks=repeat,full_reset_not_required=True))
dump('INPUT_LOCK.json',dict(source_sha256=sha(SOURCE),timeline_sha256=sha(P/'PERFORMANCE_TIMELINE.json'),
    R1_timeline_sha256=oldlock['timeline_sha256'],fingers=oldlock['fingers'],fingering_authority='DESIGN_PROVISIONAL_UNCHANGED_FROM_R1',
    policy_sha256=sha(P/'GENERATION_POLICY.json'),candidate_limit=1,committed_before_motion=True))
print('STATIC_PREFLIGHT',[(r['test'],r['task_contact_error_mm']) for r in rows],flush=True)
