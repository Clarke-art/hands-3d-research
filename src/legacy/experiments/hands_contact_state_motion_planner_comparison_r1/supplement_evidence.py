import sys,json,importlib.metadata,urllib.request,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(r'<HANDS_ROOT>_contact_state_motion_planner_comparison_r1');sys.path.insert(0,str(O));sys.path.insert(0,str(O/'deps'));import rig_model,numpy,scipy,mink,mujoco,qpsolvers
print('RUNTIME',numpy.__version__,scipy.__version__,mujoco.__version__)
d=dict(Python=sys.version,numpy=numpy.__version__,scipy=scipy.__version__,mujoco=mujoco.__version__,mink=importlib.metadata.version('mink'),qpsolvers=qpsolvers.__version__,daqp=importlib.metadata.version('daqp'),numpy_module=numpy.__file__,scipy_module=scipy.__file__,mink_module=mink.__file__,mujoco_module=mujoco.__file__,qpsolvers_available=qpsolvers.available_solvers,installed_packages_report='INSTALL_REPORT.json',note='Frozen FK imports pre-existing NumPy2.5.3 before Mink; installed NumPy2.5.4 is not runtime NumPy. No system package was changed.')
(O/'RUNTIME_DEPENDENCIES.json').write_text(json.dumps(d,indent=2))
a=json.loads((O/'ACTUAL_DISCRETE_VALIDATION.json').read_text());import numpy as np
for r in a['results']:
 st=np.array(r['solver']['state']);q=np.array(r['anatomy']['recovered_controls']);valid=np.all(st[:3]>=np.array([-150,-30,-12.217247311392744])-.001) and np.all(st[:3]<=np.array([60,35,12])+.001) and np.all(abs(st[3:6])<=np.array([8,8,12])+.001) and np.all(q[0]>=np.array([0,0,0,-35])-.001) and np.all(q[0]<=np.array([25,25,18,35])+.001);r['gates']['authorized_control_domain']=bool(valid);r['all_geometry_and_joint_gates']=all(r['gates'].values())
(O/'ACTUAL_DISCRETE_VALIDATION.json').write_text(json.dumps(a,indent=2))
# Persist supplementary official-source evidence and observed repository commit identities.
idx=json.loads((O/'SOURCE_RESEARCH_INDEX.json').read_text())
urls={'pink_self_collision':'https://raw.githubusercontent.com/pink-kinematics/pink/main/pink/barriers/self_collision_barrier.py','pink_ci':'https://raw.githubusercontent.com/pink-kinematics/pink/main/.github/workflows/ci.yml','pin_pypi':'https://pypi.org/pypi/pin/json','mink_commit':'https://api.github.com/repos/kevinzakka/mink/commits/main','pink_commit':'https://api.github.com/repos/pink-kinematics/pink/commits/main','drake_commit':'https://api.github.com/repos/RobotLocomotion/drake/commits/master'}
for name,url in urls.items():
 try:
  data=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Codex-research'}),timeout=15).read();f=O/'sources'/(name+'.txt');f.write_bytes(data);idx.append(dict(id=name,url=url,file=str(f.relative_to(O)),sha256=hashlib.sha256(data).hexdigest(),status='SOURCE_REVIEWED_DOWNLOAD'))
 except Exception as e:idx.append(dict(id=name,url=url,error=str(e)))
(O/'SOURCE_RESEARCH_INDEX.json').write_text(json.dumps(idx,indent=2))
pin=json.loads((O/'sources/pin_pypi.txt').read_text());print('PIN_VERSION',pin['info']['version'],'WIN_WHEELS',[f['filename'] for f in pin['urls'] if 'win' in f['filename']])
for r in a['results']:print(r['phase'],r['method'],r['all_geometry_and_joint_gates'])
