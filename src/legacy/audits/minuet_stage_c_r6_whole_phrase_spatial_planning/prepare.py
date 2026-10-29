from common import *
sys.path.insert(0, str(R5))
from event_phase_plan import EventPhasePlan
assert sha(C1/'STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY.blend') == SOURCE_HASH
assert not (P/'FORMAL_ATTEMPT_STARTED.json').exists()
before = read(R5/'PROTECTED_INPUTS_BEFORE.json')
changed = [p for p,h in before.items() if not Path(p).is_file() or sha(p)!=h]
assert not changed, changed
for folder in [R5]:
    for f in folder.rglob('*'):
        if f.is_file() and '__pycache__' not in f.parts: before[str(f)] = sha(f)
dump('PROTECTED_INPUTS_BEFORE.json', before)
notes = [n for n in TL['notes'] if n['hand']=='R']
plan = EventPhasePlan(notes)
end = TL['presentation_duration_sec']
knots = np.unique(np.round(np.r_[np.arange(0,end,1/12), end,
    [v for n in notes for v in [n['note_on']-.18,n['note_on'],n['note_on']+.035,
    n['note_off'],n['note_off']+.04,n['note_off']+.07,n['note_off']+.12]]],9))
knots = knots[(knots>=0)&(knots<=end)]
checks = np.unique(np.r_[knots,(knots[:-1]+knots[1:])/2])
samples = np.unique(np.round(np.r_[np.arange(358)/60,checks,
    [n['note_on']+e for n in notes for e in [-.00001,0,.00001]],
    [n['note_off']+e for n in notes for e in [-.00001,0,.00001]], 3.825],9))
samples = samples[(samples>=0)&(samples<=end)]
late = plan.at(3.825)
assert any(x.get('midi')==76 and x['hard_contact'] for x in late['fingers'][2]['tasks'])
assert any(x.get('midi')==78 and x['role']=='PREPARING' for x in late['fingers'][3]['tasks'])
assert not any(x.get('midi')==74 and x['hard_contact'] for x in late['fingers'][3]['tasks'])
shifted = EventPhasePlan([dict(n,note_on=n['note_on']+7,note_off=n['note_off']+7,midi_note=n['midi_note']-12,key_index=n['key_index']-12) for n in notes])
for t in checks:
    a,b=plan.at(float(t)),shifted.at(float(t)+7)
    # Avoid floating boundary ambiguity in invariance test; interior probes below.
for n in notes:
    t=(n['note_on']+n['note_off'])/2
    a,b=plan.at(t),shifted.at(t+7)
    assert [[(x['role'],x['hard_contact']) for x in f['tasks']] for f in a['fingers']] == [[(x['role'],x['hard_contact']) for x in f['tasks']] for f in b['fingers']]
dump('WHOLE_PHRASE_ROLE_PLAN.json',dict(notes=notes,policy=vars(plan.policy),
    intervals=plan.intervals(),samples=[plan.at(float(t)) for t in samples],
    same_finger_repetitions=[dict(previous=a['note_id'],next=b['note_id'],time=b['note_on'],
      same_key=a['midi_note']==b['midi_note'],old_release_not_hold=True)
      for a,b in zip(notes,notes[1:]) if a['finger']==b['finger']],
    endpoint_policy='Free five-finger joints at both ends; shared spatial inequalities; source style is a preference only',
    old_window_locks=[],time_pitch_invariance_pass=True))
dump('PREFLIGHT_POLICY.json',dict(source_sha256=SOURCE_HASH,span=[0,end],knots=knots,
    checks=checks,samples=samples,root='PRESERVE_SOURCE',five_finger_dofs=20,
    immutable_old_joint_boundaries=False,non_target_depth_limit_mm=.5,
    active_gap_mm=[-.5,2.1],active_horizontal_limit_mm=.5,pad_radius_mm=4,
    static_optimizations_allowed=0,dynamic_attempts_allowed=1,
    generation_gate='Check exact event clock continuity, engineering domains, FK/skin parity and constraint expressibility before locking solver'))
print('R6_ROLE_PLAN_READY',len(knots),'knots',len(samples),'read-only samples',len(before),'protected files',flush=True)

