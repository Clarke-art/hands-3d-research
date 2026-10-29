from pathlib import Path
import ast
O=Path(__file__).resolve().parent;ROOT=O.parent/'hands'
s=(ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion/02_generate.py').read_text()
s=s[s.index('end=np.ceil'):]
s=s.replace('end=np.ceil(tl[\'presentation_duration_sec\']*60)/60','end=END')
s=s.replace('np.r_[0,end,','np.r_[START,end,').replace('(priority>=0)','(priority>=START)').replace('np.arange(0,end,.09)','np.arange(START,end,.09)').replace('if 0<=t<=end','if START<=t<=end').replace('np.arange(0,end+1/240,1/120)','np.arange(START,end+1/240,1/120)').replace('(times>=0)','(times>=START)')
a=s.index('# Event-level adjacent-pair initial poses');z=s.index('X0=np.r_')
s=s[:a]+"A=np.load(O/'STATIC_REACH_STATES.npz');seedstates=A['states'];seedtimes=A['times'];seed=np.column_stack([np.interp(knots,seedtimes,seedstates[:,d]) for d in range(26)])\n"+s[z:]
s=s.replace('source_event_count=16','source_event_count=9').replace('source_notes=16','source_notes=9')
header="from motion_core import *\nimport time\nassert not (O/'motion.npz').exists(), 'One continuous trajectory only'\n(O/'GENERATION_POLICY.json').write_text(json.dumps(pol,indent=2)+'\\n',encoding='utf8')\n"
(O/'solve_continuous.py').write_text(header+s,encoding='utf8')
print('EXISTING_BANDED_SOLVER_ADAPTED: 9 context/core notes; actual key actions; 40 iterations; one joint trajectory; no local repair loop')
