import sys,json,hashlib,shutil
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent; OLD=O.parent/'hands_c01_g4_e5_skin_safe_bridge_r1'; STATIC=O.parent/'hands_skin_collision_static_feasibility_r1'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
protected=json.loads((OLD/'PROTECTED_FILES_BEFORE.json').read_text(encoding='utf-8-sig'))
for parent in [OLD,STATIC]:
 for p in parent.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts: protected[str(p)]=sha(p)
checks=[dict(path=p,expected=h,actual=sha(Path(p))) for p,h in protected.items()]
assert all(x['expected']==x['actual'] for x in checks),'Protected hash mismatch'
policy=json.loads((OLD/'POLICY_LOCK.json').read_text(encoding='utf-8-sig'))
policy.update(task='PIANO_C01_S1_CONSTRAINED_SOLVER_FEASIBILITY_R1',authority='DESIGN_PROVISIONAL',max_main_solves=2,new_solve_wall_budget_seconds=600,per_solve_wall_seconds=240,fixed_Z_each_recorded_seed=True,no_root_Z_ablation=True,source_previous=str(OLD),contact_signed_interval_mm=[-.020,-.005],active_pair_separation_mm=.020,local_domain_translation_mm=1.,local_domain_rotation_deg=2.,local_domain_joint_deg=3.,algorithm='SciPy SLSQP explicit inequality constraints',continuous_motion_generated=False)
(O/'POLICY_LOCK.json').write_text(json.dumps(policy,indent=2)+'\n',encoding='utf8')
(O/'PROTECTED_FILES_BEFORE.json').write_text(json.dumps(protected,indent=2)+'\n',encoding='utf8')
(O/'PREFLIGHT_CHECKS.json').write_text(json.dumps(dict(status='PASS',checked_count=len(checks),checks=checks),indent=2)+'\n',encoding='utf8')
for name in ['skin_proxy.py','geometry_detector.py','triangle_distance.py','SKIN_MODEL.npz','SKIN_MODEL_META.json']: shutil.copyfile(OLD/name,O/name)
print('PROTECTED_PREFLIGHT_PASS',len(checks))
