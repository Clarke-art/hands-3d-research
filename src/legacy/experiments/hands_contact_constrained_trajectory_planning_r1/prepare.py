import sys,json,hashlib,shutil,time,urllib.request
from pathlib import Path
O=Path(__file__).resolve().parent;PRE=O.parent/'hands_contact_junction_compatibility_r1';start=time.time();(O/'sources').mkdir(exist_ok=True);(O/'logs').mkdir(exist_ok=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
p=json.loads((PRE/'PROTECTED_FILES_BEFORE.json').read_text());p.update({str(f):sha(f) for f in PRE.rglob('*') if f.is_file() and '__pycache__' not in f.parts});assert all(Path(f).exists() and sha(Path(f))==h for f,h in p.items());(O/'PROTECTED_FILES_BEFORE.json').write_text(json.dumps(p,indent=2))
for n in ['rig_model.py','skin_proxy.py','geometry_detector.py','triangle_distance.py','SKIN_MODEL.npz','SKIN_MODEL_META.json','extract_anatomy.py','ENDPOINT_SOLVE_2.json','MOTION_COLLOCATION_KEYS.npz','EXPERIMENT_INPUT.json','POLICY_LOCK.json','blender_verify.py','verify_local_path.py','BOUNDARY_KEY_STATES.npz','LOCAL_PATH_KEY_STATES.npz','boundary_rules.py','CONTACT_STATE_SEQUENCE.json']:
 shutil.copyfile(PRE/n,O/n)
repos={'ompl':'ompl/ompl','trajopt':'tesseract-robotics/trajopt','tesseract_planning':'tesseract-robotics/tesseract_planning','casadi':'casadi/casadi'};out={}
for name,repo in repos.items():
 req=urllib.request.Request('https://api.github.com/repos/'+repo+'/commits',headers={'User-Agent':'Codex-local-source-review'})
 try:
  data=json.load(urllib.request.urlopen(req,timeout=30));item=data[0];commit=item['sha'];out[name]=dict(repo=repo,commit=commit,date=item['commit']['committer']['date']);(O/'sources'/(name+'_commit.json')).write_text(json.dumps(item,indent=2))
 except Exception as e:out[name]=dict(error=str(e))
(O/'SOURCE_COMMITS.json').write_text(json.dumps(out,indent=2));print('protected',len(p),'source metadata',out)
