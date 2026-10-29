import sys,json,hashlib,shutil
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;PRE=O.parent/'hands_c01_s1_constrained_solver_feasibility_r1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((PRE/'DELIVERY_MANIFEST.json').read_text(encoding='utf-8-sig'))
for row in manifest['files']:assert sha(PRE/row['file'])==row['sha256'],row['file']
protected=json.loads((PRE/'PROTECTED_FILES_BEFORE.json').read_text(encoding='utf-8-sig'))
for p in PRE.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts:protected[str(p)]=sha(p)
assert all(sha(Path(p))==h for p,h in protected.items())
for name in ['skin_proxy.py','geometry_detector.py','triangle_distance.py','SKIN_MODEL.npz','SKIN_MODEL_META.json']:shutil.copyfile(PRE/name,O/name)
prior=json.loads((PRE/'POLICY_LOCK.json').read_text(encoding='utf-8-sig'))
prior.update(task='PIANO_C01_ANATOMY_AND_PREPARATION_AUDIT_R1',new_solve_wall_budget_seconds=300,total_new_numerical_budget_seconds=300,max_main_solves=2,max_new_static_solves=2,per_solve_wall_seconds=140,static_attempt_wall_limit_seconds=140,anatomy_constraints_pending=True)
prior['human_decision']=dict(S1_NUMERICAL_GEOMETRY='PASS',S1_HUMAN_ANATOMICAL_VISUAL='FAIL',DYNAMIC_BRIDGE_AUTHORIZATION='NOT_GRANTED',authority='Direct human instruction in current request; cannot be overridden by new numerical results')
prior['current_source']=str(PRE)
(O/'POLICY_LOCK.json').write_text(json.dumps(prior,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(O/'PROTECTED_FILES_BEFORE.json').write_text(json.dumps(protected,indent=2)+'\n',encoding='utf8')
print('READONLY_INPUTS_PASS',len(protected),'previous manifest',len(manifest['files']))
