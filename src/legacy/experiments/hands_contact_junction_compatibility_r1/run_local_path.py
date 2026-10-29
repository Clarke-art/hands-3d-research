import sys,json,subprocess
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));from contact_solver import *
p=json.loads((O/'LOCAL_PATH_PLAN.json').read_text());d=np.load(O/'LOCAL_PATH_KEY_STATES.npz');seed=json.loads((O/'runs/junction_2.json').read_text())['latent'];rows=[]
for i,t in enumerate(p['post_knots']):
 r=run_solve('path_'+str(i+1),seed,[I['contacts'][1]],t,d['angles'][i],35)
 with (O/'logs'/('path_'+str(i+1)+'_actual.log')).open('w') as log:
  subprocess.run([r'D:\blender\blender.exe','-b','--python',str(O/'blender_verify.py'),'--',str(O/'runs'/(r['id']+'.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
 a=json.loads((O/'runs'/(r['id']+'_actual.json')).read_text());rows.append(dict(id=r['id'],all_gates=a['all_gates']));(O/'LOCAL_PATH_KNOT_INDEX.json').write_text(json.dumps(rows,indent=2))
 if not a['all_gates']:break
 seed=r['latent']
