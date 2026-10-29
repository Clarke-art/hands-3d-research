from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1];PRE=ROOT/'audits/minuet_stage_c_motion_planning_architecture_reassessment_r1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
from event_phase_plan import EventPhasePlan
before=read(PRE/'PROTECTED_INPUTS_BEFORE.json');assert all(sha(p)==h for p,h in before.items())
for p in PRE.rglob('*'):
 if p.is_file() and '__pycache__' not in str(p):before[str(p)]=sha(p)
save('PROTECTED_INPUTS_BEFORE.json',before)
tl=read(ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/PERFORMANCE_TIMELINE.json');notes=[n for n in tl['notes'] if n['hand']=='R'];plan=EventPhasePlan(notes)
samples=[plan.at(t) for t in [1.108333333,1.133333333,1.191666667,1.25,1.4214275,3.75,3.8128535,3.825,3.85]]
late=plan.at(3.825);middle=late['fingers'][2]['tasks'];ring=late['fingers'][3]['tasks']
assert any(q.get('midi')==76 and q['hard_contact'] for q in middle)
assert any(q.get('midi')==78 and q['role']=='PREPARING' for q in ring)
assert not any(q.get('midi')==74 and (q['hard_contact'] or q['contact_permission'] or q['role']=='RELEASING') for q in ring)
assert any(q.get('midi')==74 and q['role']=='EXITING' for q in ring)
assert any(q['midi']==74 and not q['requires_finger_hold'] for q in late['mechanical_context'])
assert plan.permit(3.825,3,76,123,{123})
assert not plan.permit(3.825,3,76,124,{123})
assert not plan.permit(3.825,4,78,123,{123})
assert not plan.permit(3.825,3,75,123,{123})
# Transposition/time-shift invariance: prove roles are event-based, not pitch/time special cases.
trans=[dict(n,note_on=n['note_on']+7,note_off=n['note_off']+7,midi_note=n['midi_note']-12,key_index=n['key_index']-12) for n in notes]
other=EventPhasePlan(trans).at(10.825)
for x,y in zip(late['fingers'],other['fingers']):
 assert [(q['role'],q['hard_contact']) for q in x['tasks']]==[(q['role'],q['hard_contact']) for q in y['tasks']]
save('EVENT_ROLE_VALIDATION.json',dict(pass_=True,notes=16,fingers=5,intervals=plan.intervals(),samples=samples,transposition_and_time_translation_pass=True,pad_permission_tests_pass=True,mechanical_clock_changed=False,new_static_solves=0,new_dynamic_solves=0))
save('PRECHECK_POLICY.json',dict(windows_video_sec=[[.778571,2.134284],[2.741426,4.705710]],root='FIXED_C1',source_sha256='d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7',boundary='source position and first derivative unchanged; zero correction at endpoints',non_target_internal_depth_limit_mm=.5,active_gap_limit_mm=2.1,active_horizontal_limit_mm=.5,geometry_check='Four exact boundary source poses, existing four distal ROIs and seven known black keys only; no optimization or pose edits',stop='Any credible non-target penetration >0.5 mm at an immutable endpoint implies boundary gate FAIL and zero dynamic attempts',dynamic_method_lock='NOT_REACHED; do not fabricate a backend/strategy lock before boundary feasibility',role_policy=vars(plan.policy)))
print('ROLE_INTERFACE_VALIDATED; source files protected',len(before),flush=True)
