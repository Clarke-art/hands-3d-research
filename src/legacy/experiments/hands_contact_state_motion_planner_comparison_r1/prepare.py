import sys,json,hashlib,shutil,urllib.request,concurrent.futures
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;PRE=O.parent/'hands_c01_g4_e5_natural_motion_bridge_r2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((PRE/'PROTECTED_FILES_BEFORE.json').read_text());old.update({str(p):sha(p) for p in PRE.rglob('*') if p.is_file() and '__pycache__' not in p.parts});assert all(sha(Path(p))==h for p,h in old.items());(O/'PROTECTED_FILES_BEFORE.json').write_text(json.dumps(old,indent=2))
for n in ['skin_proxy.py','geometry_detector.py','triangle_distance.py','SKIN_MODEL.npz','SKIN_MODEL_META.json','extract_anatomy.py','ENDPOINT_SOLVE_2.json','MOTION_COLLOCATION_KEYS.npz']:shutil.copyfile(PRE/n,O/n)
shutil.copyfile(PRE/'motion_model.py',O/'rig_model.py')
for d in ['sources','deps','logs']: (O/d).mkdir(exist_ok=True)
urls={
'mink_solve':'https://raw.githubusercontent.com/kevinzakka/mink/main/src/mink/solve_ik.py',
'mink_task':'https://raw.githubusercontent.com/kevinzakka/mink/main/src/mink/tasks/task.py',
'mink_limit':'https://raw.githubusercontent.com/kevinzakka/mink/main/src/mink/limits/limit.py',
'mink_collision':'https://raw.githubusercontent.com/kevinzakka/mink/main/src/mink/limits/collision_avoidance_limit.py',
'mink_project':'https://raw.githubusercontent.com/kevinzakka/mink/main/pyproject.toml',
'mink_license':'https://raw.githubusercontent.com/kevinzakka/mink/main/LICENSE',
'pink_project':'https://raw.githubusercontent.com/pink-kinematics/pink/main/pyproject.toml',
'pink_solve':'https://raw.githubusercontent.com/pink-kinematics/pink/main/pink/solve_ik.py',
'pink_license':'https://raw.githubusercontent.com/pink-kinematics/pink/main/LICENSE',
'pink_version':'https://raw.githubusercontent.com/pink-kinematics/pink/main/pink/__init__.py',
'drake_license':'https://raw.githubusercontent.com/RobotLocomotion/drake/master/LICENSE.TXT',
'drake_install':'https://drake.mit.edu/installation.html',
'drake_ik':'https://raw.githubusercontent.com/RobotLocomotion/drake/master/multibody/inverse_kinematics/inverse_kinematics.h',
'drake_release':'https://api.github.com/repos/RobotLocomotion/drake/releases/latest',
'mink_pypi':'https://pypi.org/pypi/mink/json',
'pink_pypi':'https://pypi.org/pypi/pin-pink/json'}
def fetch(item):
 n,u=item
 try:
  data=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Codex-research'}),timeout=25).read();f=O/'sources'/(n+'.txt');f.write_bytes(data);return dict(id=n,url=u,file=str(f.relative_to(O)),sha256=sha(f),status='SOURCE_REVIEWED_DOWNLOAD')
 except Exception as e:return dict(id=n,url=u,error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:res=list(ex.map(fetch,urls.items()))
(O/'SOURCE_RESEARCH_INDEX.json').write_text(json.dumps(res,indent=2));print('protected',len(old));print(json.dumps(res,indent=2))
