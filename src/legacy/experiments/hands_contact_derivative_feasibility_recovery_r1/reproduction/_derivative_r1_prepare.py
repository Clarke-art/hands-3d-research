import json,hashlib,shutil
from pathlib import Path
O=Path(r'<HANDS_ROOT>_contact_derivative_feasibility_recovery_r1')
P=O.parent/'hands_contact_constrained_trajectory_planning_r1'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
old=json.loads((P/'PROTECTED_FILES_BEFORE.json').read_text())
paths=set(old)
for name in ['hands_contact_constrained_trajectory_planning_r1','hands_contact_junction_compatibility_r1','hands_contact_state_motion_planner_comparison_r1']:
 paths.update(str(p) for p in (O.parent/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
baseline={p:sha(Path(p)) for p in sorted(paths)}
(O/'PROTECTED_FILES_BEFORE.json').write_text(json.dumps(baseline,indent=2))
(O/'HISTORICAL_BASELINE_CHECK.json').write_text(json.dumps({'historical_mismatches':[p for p,h in old.items() if baseline[p]!=h],'protected_count':len(baseline)},indent=2))
for n in ['rig_model.py','skin_proxy.py','geometry_detector.py','triangle_distance.py','SKIN_MODEL.npz','SKIN_MODEL_META.json','extract_anatomy.py','ENDPOINT_SOLVE_2.json','MOTION_COLLOCATION_KEYS.npz','EXPERIMENT_INPUT.json','POLICY_LOCK.json','blender_verify.py','BOUNDARY_KEY_STATES.npz','CONTACT_STATE_SEQUENCE.json']:
 shutil.copyfile(P/n,O/n)
shutil.copyfile(O.parent/'hands_contact_junction_compatibility_r1/contact_solver.py',O/'contact_solver.py')
(O/'logs').mkdir(exist_ok=True);(O/'runs').mkdir(exist_ok=True)
print('protected',len(baseline))
