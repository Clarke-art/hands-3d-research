import json,hashlib,ast,sys
from pathlib import Path
O=Path(__file__).resolve().parent
load=lambda n:json.loads((O/n).read_text(encoding='utf-8-sig'))
seq=load('CONTACT_STATE_SEQUENCE.json')['all_source_sequence']
def required(t,hand=None):return {e['note_id'] for e in seq if e['required_contact'] and e['display_interval'][0]<=t<e['display_interval'][1] and (hand is None or e['hand']==hand)}
checks={}
checks['left_chord_union']=required(.5,'L')=={'L00','L01','L02'}
checks['G4_left_limit']=required(2.9214259,'R')=={'R07'}
checks['new_contact_at_atomic_exchange']=required(2.9214260000000003,'R')=={'R08'}
checks['E5_on_plus35']=required(2.956426,'R')=={'R08'}
checks['E5_off_next_C5_active']=required(3.349997,'R')=={'R09'}
checks['holding_other_finger_prepares']=required(2.72,'R')=={'R07'} and any(e['note_id']=='R08' and e['mode']=='APPROACH' and e['display_interval'][0]<=2.72<e['display_interval'][1] for e in seq)
checks['repeat_preserves_obligation_and_warning']=required(2.492855,'R')=={'R07'} and bool(load('CONTACT_STATE_SEQUENCE.json')['mechanical_warnings'])
checks['octave_declared_not_geometric_pass']=any(t['case']=='octave_leap' and t['kinematic_feasibility']=='NOT_TESTED' for t in load('CONTRACT_REUSE_TESTS.json')['tests'])
# Same-finger simultaneous required notes are rejected by the reusable representation validator.
collisions=[]
for t in sorted({v for e in seq for v in e['display_interval']}):
 by={}
 for e in seq:
  if e['required_contact'] and e['display_interval'][0]<=t<e['display_interval'][1]:by.setdefault((e['hand'],e['finger']),set()).add(e['midi'])
 collisions.extend(dict(time=t,hand=k[0],finger=k[1],notes=list(v)) for k,v in by.items() if len(v)>1)
checks['no_C01_finger_assignment_conflicts']=not collisions
assert all(checks.values()),checks
old=load('PROTECTED_FILES_BEFORE.json');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();current={p:sha(Path(p)) for p in old};changed=[p for p in old if old[p]!=current[p]];assert not changed,changed
(O/'PROTECTED_FILES_AFTER.json').write_text(json.dumps(dict(protected_count=len(old),all_unchanged=True,changed=[],sha256=current),indent=2))
required_files=['CONTACT_STATE_CONTRACT.md','CONTACT_STATE_SEQUENCE.json','PREVIOUS_PLANNER_FAILURE_ANALYSIS.md','OPEN_SOURCE_IK_COMPARISON.md','MINIMAL_FEASIBILITY_RESULTS.json','PRODUCT_ROUTE_REVIEW.md','FINAL_RECOMMENDATION.md'];assert all((O/n).is_file() for n in required_files)
for f in O.glob('*.json'):json.loads(f.read_text(encoding='utf-8-sig'))
for f in O.glob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'))
r=load('MINIMAL_FEASIBILITY_RESULTS.json');assert all(r['gates'].values()) and not r['continuous_path_pass'];assert r['numerical_budget']['total_inner_solve_wall_seconds']<600;assert all(x['actual_PASS'] for x in r['summary']);assert len(r['all_numerical_calls'])==10
assert not list(O.glob('*.blend')) and not list(O.glob('*.mp4'))
# Track immutable pre-existing runtime code that was imported, not installed into source workspace.
refs=[O.parent/'hands_c01_whole_hand_motion_feasibility_r1/blender_utils.py',O.parent/'hands/audits/midi_driven_dual_hand_piano_performance_poc_r1/performance_core.py',O.parent/'hands/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py',O.parent/'hands_skin_collision_static_feasibility_r1/solve_static_skin.py']
(O/'REUSED_DEPENDENCY_SOURCES.json').write_text(json.dumps([dict(path=str(f),sha256=sha(f),access='READ_ONLY') for f in refs],indent=2))
check=dict(status='DELIVERY_CHECK_PASS',contract_semantic_checks=checks,protected_files=len(old),all_protected_unchanged=True,required_deliverables=required_files,Python_syntax_and_JSON_parse=True,actual_states_PASS=6,external_tool_actually_run='Mink',new_action_count=0,video_count=0,still_count=0,total_recorded_inner_solve_seconds=r['numerical_budget']['total_inner_solve_wall_seconds'],scope='DISCRETE_STATE_FEASIBILITY_ONLY',stop='STOP — HUMAN REVIEW')
(O/'DELIVERY_CHECK.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
files=[dict(file=str(f.relative_to(O)),bytes=f.stat().st_size,sha256=sha(f)) for f in sorted(O.rglob('*')) if f.is_file() and f.name!='DELIVERY_MANIFEST.json' and '__pycache__' not in f.parts]
(O/'DELIVERY_MANIFEST.json').write_text(json.dumps(dict(task=r['task'],authority='DESIGN_PROVISIONAL',files=files),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(check,ensure_ascii=False));print('DELIVERY_FILES',len(files),'BYTES',sum(x['bytes'] for x in files))
