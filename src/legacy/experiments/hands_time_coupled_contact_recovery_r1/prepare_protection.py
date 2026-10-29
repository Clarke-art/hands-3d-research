import json,hashlib,shutil,time
from pathlib import Path
O=Path(__file__).resolve().parent;P=O.parent/'hands_contact_derivative_feasibility_recovery_r1';t=time.monotonic()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
b=json.loads((P/'PROTECTED_FILES_BEFORE.json').read_text());paths=set(b)
paths.update(str(f) for f in P.rglob('*') if f.is_file() and '__pycache__' not in f.parts)
hashes={s:sha(Path(s)) for s in sorted(paths)};assert all(hashes[s]==h for s,h in b.items())
(O/'PROTECTED_FILES_BEFORE.json').write_text(json.dumps(hashes,indent=2))
for n in ['rig_model.py','skin_proxy.py','geometry_detector.py','triangle_distance.py','SKIN_MODEL.npz','SKIN_MODEL_META.json','extract_anatomy.py','ENDPOINT_SOLVE_2.json','MOTION_COLLOCATION_KEYS.npz','EXPERIMENT_INPUT.json','POLICY_LOCK.json','blender_verify.py','CONTACT_STATE_SEQUENCE.json','contact_solver.py','kinematic_derivative_api.py']:
 shutil.copyfile(P/n,O/n)
pol=json.loads((O/'POLICY_LOCK.json').read_text());pol.update(task='PIANO_TIME_COUPLED_CONTACT_RECOVERY_R1',no_more_solves=False,maximum_joint_solves=2);(O/'POLICY_LOCK.json').write_text(json.dumps(pol,indent=2))
(O/'logs').mkdir(exist_ok=True);(O/'runs').mkdir(exist_ok=True)
(O/'PROTECTION_SETUP.json').write_text(json.dumps(dict(count=len(hashes),seconds=time.monotonic()-t,historical_match=True),indent=2));print('PROTECTED',len(hashes))
