import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
lock=json.loads((P/'PRE_SOLVE_LOCK_R1.json').read_text(encoding='utf8'))
assert not (P/'ROOT_FINGER_COORDINATION_R1.json').exists()
v={'type':'CONFIRMED_FLOAT32_FINITE_DIFFERENCE_IMPLEMENTATION_BUG','evidence':'DERIVATIVE_PRECISION_CHECK_R1.json','evidence_sha256':sha(P/'DERIVATIVE_PRECISION_CHECK_R1.json'),'original_script_sha256':lock['solver_script_sha256'],'repaired_script_sha256':sha(P/'01_coordinate.py'),'policy_sha256_unchanged':sha(P/'COORDINATED_CLEARANCE_POLICY_R1.json')==lock['policy_sha256'],'original_attempt':'Interrupted before fit result or saved candidate, not a competing candidate','bug':'Relative differences around zero produced zero evaluated vertex displacements in shared lateral root and all three idle flexion channels; absolute 0.02mm /0.03deg steps produced measurable geometry changes.','repair':'Bounds-aware absolute finite-difference Jacobian; 0.02mm XYZ,0.03deg pitch/active/idle offsets,0.003 thumb blend coefficient.','absolute_difference_steps':[.02]*3+[.03]*9+[.003]*8+[.03]*9,'engineering_ranges_weights_seed_max_nfev_unchanged':True,'motion_retuning':False,'parameter_sweep':False,'candidate_count':1}
(P/'IMPLEMENTATION_REPAIR_R1.json').write_text(json.dumps(v,indent=2),encoding='utf8')
print('IMPLEMENTATION_REPAIR_RECORDED')
