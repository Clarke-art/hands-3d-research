import json,hashlib,shutil
from pathlib import Path
O=Path(__file__).resolve().parent;PRE=O.parent/'hands_skin_collision_static_feasibility_r1';ROOT=O.parent/'hands'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
F=json.loads((PRE/'STATIC_POSE_FEASIBILITY.json').read_text());manifest=json.loads((PRE/'DELIVERY_MANIFEST.json').read_text());checks=[]
required=['geometry_detector.py','skin_proxy.py','SKIN_MODEL.npz','SKIN_MODEL_META.json','STATIC_POSE_FEASIBILITY.json','COLLISION_METHOD_TESTS.json','POLICY_LOCK.json','SOLVER_WEIGHT_LOCK.json','S2_ATTEMPT_1_ACTUAL_SKIN.npz']
for name in required:
 p=PRE/name;known=next(x['sha256'] for x in manifest['files'] if x['file']==name);assert sha(p)==known,name;checks.append(dict(file=str(p),sha256=known))
for name in ['SKIN_MODEL.npz','SKIN_MODEL_META.json']:shutil.copyfile(PRE/name,O/name)
for name in ['skin_proxy.py','geometry_detector.py']:shutil.copyfile(PRE/name,O/name)
policy=json.loads((PRE/'POLICY_LOCK.json').read_text());policy.update(task='PIANO_C01_G4_E5_SKIN_SAFE_BRIDGE_R1',total_new_numerical_budget_seconds=900,max_new_static_solves=2,static_attempt_wall_limit_seconds=140,max_new_static_nfev=55,max_new_bridge_trajectories=1,root_z_ablation=dict(attempt1='Keep prior S1 C01 root Z fixed',attempt2='Use prior second S1 and allow recorded original root-Z delta domain [-12.2172473,12] mm, actual wrist height [30,54.2172473] mm; true contact remains mandatory'),pad_horizontal_outside_max_mm=1e-5,prepared_E5=dict(pad_horizontal_outside_max_mm=2,pad_gap_interval_mm=[4,20]),validation_hz=120,risk_adaptive_sampling=True,temporal_identity=dict(R06_OFF_R07_ON=2.492855,R07_OFF_R08_ON=2.921426,R08_OFF=3.349997,presentation_lead_sec=.35),source_static=str(PRE),authority='DESIGN_PROVISIONAL')
(O/'PREFLIGHT_INPUT_CHECKS.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf8');(O/'CONTRACT_LOCK.json').write_text(json.dumps(policy,indent=2)+'\n',encoding='utf8');(O/'POLICY_LOCK.json').write_text(json.dumps(policy,indent=2)+'\n',encoding='utf8')
protected={p:expected for p,expected in json.loads((PRE/'PROTECTED_INPUTS_BEFORE.json').read_text()).items()}
for p in PRE.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts:protected[str(p)]=sha(p)
assert all(sha(Path(p))==h for p,h in protected.items())
(O/'PROTECTED_FILES_BEFORE.json').write_text(json.dumps(protected,indent=2)+'\n',encoding='utf8');print('MINIMAL_PREFLIGHT_HASH_PASS',len(checks),'source/previous files protected',len(protected))
