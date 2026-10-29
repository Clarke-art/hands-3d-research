import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));from contact_solver import *
z0=np.array(I['seeds']['P2']['latent']);j=json.loads((O/'runs/junction_2.json').read_text());desired=z0+.12*(np.array(j['latent'])-z0);trust=np.r_[[4,4,2],[2,2,2],[5,5,5,5],.12,.18];d=np.load(O/'BOUNDARY_KEY_STATES.npz');goal=dict(I['next'],pose_target=desired.tolist(),meaning='Small predictor along a known natural feasible boundary configuration direction, no hard next-key hover')
run_solve('hold_corrected',z0,[I['contacts'][0]],2.75218,d['angles'][1],35,goal=goal,trust=trust)
