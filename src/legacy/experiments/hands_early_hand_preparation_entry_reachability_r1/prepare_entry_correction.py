import sys,json
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent
r=json.loads((O/'ENTRY_MAIN_RESULT.json').read_text(encoding='utf8'))
assert r['history']==[] and 'LBX[6]' in r['error'] and 'UBX[6]' in r['error']
s=(O/'solve_entry.py').read_text(encoding='utf8')
s=s.replace("p.lbx[:12]=p.x0[:12];p.ubx[:12]=p.x0[:12]","p.lbx=p.lbx.astype(float);p.ubx=p.ubx.astype(float)\np.lbx[:12]=p.x0[:12];p.ubx[:12]=p.x0[:12]\nassert np.all(p.lbx<=p.ubx) and np.max(abs(p.ubx[:12]-p.x0[:12]))==0")
s=s.replace('ENTRY_MAIN_RESULT','ENTRY_CORRECTION_RESULT').replace('ENTRY_MAIN_PROGRESS','ENTRY_CORRECTION_PROGRESS').replace('TIME_COUPLED_ENTRY_INTERFACE','TIME_COUPLED_ENTRY_CORRECTION_INTERFACE').replace('correction_count=0','correction_count=1')
(O/'solve_entry_correction.py').write_text(s,encoding='utf8')
(O/'ENTRY_CORRECTION_RATIONALE.json').write_text(json.dumps(dict(evidence=r['error'],cause='Inherited HIGH array is integer dtype; assigning fractional fixed B2 controls truncated upper bounds (thumb 9.825665 became 9). IPOPT rejected before iterations.',change='Cast both bound arrays to float before assigning exact B2; assert feasibility of bound ordering and exact start identity.',same_time_grid=True,same_initialization=True,same_physical_constraints=True,no_extra_solver_iterations=True,correction_limit=1),indent=2),encoding='utf8')
print('CORRECTION_PREPARED_EXACT_START_BOUNDS',flush=True)
