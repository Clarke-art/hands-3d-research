import sys,json,urllib.request,hashlib,datetime,re,concurrent.futures
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent;D=O/'sources';D.mkdir(exist_ok=True)
index=[]
def get(url,name,cap=1500000):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Codex-source-audit'}),timeout=25) as r:data=r.read(cap+1)
  if len(data)>cap:raise ValueError('Small-source size cap exceeded; not downloaded')
  (D/name).write_bytes(data);row=dict(url=url,file=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),status='FETCHED',retrieved_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
  return row,data
 except Exception as e:return dict(url=url,file=name,status='UNAVAILABLE',error=str(e)),None
repos=[('pianomotion','agnJason/PianoMotion10M','main'),('pianomime','sNiper-Qian/pianomime','master'),('robopianist','google-research/robopianist','main'),('pianovam','yonghyunk1m/PianoVAM-Code','main')]
for key,repo,branch in repos:
 r,b=get('https://api.github.com/repos/'+repo+'/commits/'+branch,key+'_commit.json');index.append(r)
 if b is None:continue
 commit=json.loads(b)['sha'];r,b=get('https://api.github.com/repos/'+repo+'/git/trees/'+commit+'?recursive=1',key+'_tree.json',3000000);index.append(r)
 if b is None:continue
 paths=[r['path'] for r in json.loads(b)['tree'] if r['type']=='blob'];selected=['README.md']
 selected.extend(p for p in paths if p.rsplit('/',1)[-1].lower() in ['license','license.md','license.txt','copying'] and p.count('/')<2)
 patterns={'pianomotion':['infer.py','draw.py','datasets/show.py','docs/install.md','docs/dataset.md','datasets/dataset.py','requirements.txt'],'pianomime':['tutorial/data_preprocessing.ipynb','requirements.txt'],'robopianist':['robopianist/suite/tasks/piano_with_shadow_hands.py','docs/dataset.md','robopianist/music/midi_file.py'],'pianovam':['FingeringDetection/README.md','FingeringDetection/ASDF.py','requirements.txt']}
 selected.extend(p for p in patterns[key] if p in paths)
 if key=='pianomotion':selected.extend(p for p in paths if p.startswith('datasets/') and p.endswith('.py') and ('loader' in p or 'piano' in p))
 if key=='pianomime':selected.extend(p for p in paths if p.endswith('.zarray') and p.startswith('dataset_hl') or p.endswith('.py') and ('ik' in p.lower()) and p.count('/')<4)
 for p in sorted(set(selected))[:18]:
  rr,bb=get('https://raw.githubusercontent.com/'+repo+'/'+commit+'/'+p,key+'__'+p.replace('/','_'));rr.update(repo=repo,commit=commit,repo_path=p);index.append(rr)
 print('SOURCE_REPO',key,commit,'paths',len(paths),'selected',len(selected),flush=True)
for key,url in [
 ('furelise_card','https://huggingface.co/datasets/rcwang/for_elise/raw/main/README.md'),
 ('furelise_tree','https://huggingface.co/api/datasets/rcwang/for_elise/tree/main'),
 ('pianomotion_model_card','https://huggingface.co/agnJason/PianoMotion_models/raw/main/README.md'),
 ('pianomotion_model_metadata','https://huggingface.co/api/models/agnJason/PianoMotion_models'),
 ('pianomotion_paper','https://arxiv.org/html/2406.09326'),
 ('tipiano','https://tipiano.io/'),
 ('tipiano_paper','https://arxiv.org/html/2604.09692v1'),
 ('skypiano','https://joonhyungbae.github.io/skypiano/'),
 ('skypiano_paper','https://arxiv.org/html/2607.27296v1'),
 ('mano_license','https://mano.is.tue.mpg.de/license.html'),
 ('cc_nc_legal','https://creativecommons.org/licenses/by-nc/4.0/legalcode.en')]:
 r,b=get(url,key+'.txt');index.append(r)
 if key in ['tipiano','skypiano'] and b:
  html=b.decode('utf8',errors='replace');links=sorted(set(re.findall(r'https://github\.com/[^"<> \t\n]+',html)));print('PROJECT_LINKS',key,links,flush=True)
(D/'SOURCE_INDEX.json').write_text(json.dumps(index,indent=2),encoding='utf8')
print('SOURCES_DONE',sum(r['status']=='FETCHED' for r in index),'bytes',sum(r.get('bytes',0) for r in index),flush=True)
