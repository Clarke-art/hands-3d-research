import sys,json,hashlib,shutil
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;P=O.parent/'hands_contact_state_motion_planner_comparison_r1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected=json.loads((P/'PROTECTED_FILES_BEFORE.json').read_text());protected.update({str(f):sha(f) for f in P.rglob('*') if f.is_file() and '__pycache__' not in f.parts});assert all(sha(Path(p))==h for p,h in protected.items())
for n in ['skin_proxy.py','rig_model.py','geometry_detector.py','triangle_distance.py','SKIN_MODEL.npz','SKIN_MODEL_META.json','extract_anatomy.py','ENDPOINT_SOLVE_2.json','MOTION_COLLOCATION_KEYS.npz','DISCRETE_KEY_STATES.npz','CONTACT_STATE_SCHEMA.json','CONTACT_STATE_SEQUENCE.json','CONTRACT_REUSE_TESTS.json']:shutil.copyfile(P/n,O/n)
pol=json.loads((P/'POLICY_LOCK.json').read_text());pol.update(task='PIANO_CONTACT_JUNCTION_COMPATIBILITY_R1',max_boundary_solves=2,max_boundary_wall_each_seconds=100,continuation_new_nodes=6,max_continuation_wall_each_seconds=35,new_numerical_wall_limit_seconds=600,no_more_solves=False,local_path_candidates=1,local_path_prerequisite='Actual same-configuration left/right contact gates must pass',static_only=False,formal_Action_authorized=False,continuous_action_authorized=False,experiment_date='2026-10-13 Asia/Shanghai')
# Source contract explicitly requires PRESS at NOTE_ON and HOLD to NOTE_OFF left limit.
seq=json.loads((P/'CONTACT_STATE_SEQUENCE.json').read_text());assert seq['contract_status']=='CONTACT_STATE_CONTRACT_PASS';ds=seq['discrete_test_contract'];J=seq['atomic_exchange']['display_time'];assert abs(J-2.921426)<1e-9
configs=dict(task=pol['task'],junction_time=J,offset_seconds=seq['clock_offset'],hold=ds['P2']['required'][0],next=ds['P3']['required'][0],contacts=[],seeds={},continuation_start_id='P2',continuation_start_time=ds['P2']['time'],hold_left_limit_required=True,new_press_right_limit_required=True,simultaneous_geometric_contact_at_junction=True,simultaneous_full_depression=False,acoustic_or_force_requirement='UNMODELLED')
for name in ['P2','P3']:
 r=json.loads((P/f'{name}_SLSQP_SOLVE.json').read_text());configs['seeds'][name]=dict(latent=r['latent'],state=r['state'],source=str(P/f'{name}_SLSQP_SOLVE.json'));spec=ds[name]['required'][0];configs['contacts'].append(dict(midi=spec['midi'],finger=spec['finger'],note_id=spec['note'],face=r['witness_face'],vertices=r['witness_vertices'],barycentric=r['witness_barycentric'],mode='surface_slide',material_face_source=str(P/f'{name}_SLSQP_SOLVE.json')))
for n,d in [('PROTECTED_FILES_BEFORE.json',protected),('POLICY_LOCK.json',pol),('EXPERIMENT_INPUT.json',configs)]: (O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(O/'logs').mkdir(exist_ok=True);(O/'runs').mkdir(exist_ok=True)
print('PROTECTED',len(protected),'contract reused',J,'contacts',[(x['midi'],x['finger']) for x in configs['contacts']])
