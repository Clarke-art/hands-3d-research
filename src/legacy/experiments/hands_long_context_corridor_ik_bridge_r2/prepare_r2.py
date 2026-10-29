import sys,json,hashlib,time,shutil
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent;BASE=O.parent;P=BASE/'hands_long_context_hand_motion_architecture_r1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def js(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
(O/'logs').mkdir();(O/'runs').mkdir()
for n in ['rig_model.py','skin_proxy.py','geometry_detector.py','triangle_distance.py','SKIN_MODEL.npz','SKIN_MODEL_META.json','extract_anatomy.py','ENDPOINT_SOLVE_2.json','MOTION_COLLOCATION_KEYS.npz','EXPERIMENT_INPUT.json','POLICY_LOCK.json','CONTACT_STATE_SEQUENCE.json','kinematic_derivative_api.py','contact_solver.py','batch_verify.py','coupled_model.py','run_stage.py','HAND_MOTION_INTENT_CONTRACT.json']:
 shutil.copyfile(P/n,O/n)
shutil.copyfile(BASE/'hands_early_hand_preparation_entry_reachability_r1/guarded_node.py',O/'guarded_node.py')
shutil.copyfile(P/'CONCURRENCY_ATTRIBUTION.json',O/'HISTORICAL_CONCURRENCY_ATTRIBUTION.json')
policy=read(O/'POLICY_LOCK.json');policy.update(task='PIANO_LONG_CONTEXT_CORRIDOR_IK_BRIDGE_R2',no_more_solves=False,maximum_high_level_candidates=2,maximum_targeted_corrections=0,total_new_numerical_budget_seconds=600,new_candidate_wall_cap_seconds=180,formal_Action_authorized=False);js('POLICY_LOCK.json',policy)
old=read(P/'PROTECTED_FILES_AFTER.json');paths=set(old);roots=[r for r in BASE.iterdir() if r.is_dir() and (r.name=='piano' or r.name.startswith('hands')) and r!=O]
for root in roots:paths.update(str(f) for f in root.rglob('*') if f.is_file())
beg=time.monotonic();hashes={s:sha(Path(s)) for s in sorted(paths)};changed=[s for s,h in old.items() if hashes[s]!=h]
js('PROTECTED_FILES_BEFORE.json',hashes);js('PROTECTION_SETUP.json',dict(current_count=len(hashes),predecessor_count=len(old),predecessor_snapshot_changes=changed,protected_roots=[str(r) for r in roots],seconds=time.monotonic()-beg,old85850_FAIL_preserved=True,old86148_PASS_preserved=True))
assert not changed,'Unexpected protected asset changes; stop dependent work'
print('R2_PROTECTION_READY',len(hashes),flush=True)
