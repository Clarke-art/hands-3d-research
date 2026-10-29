import sys,json,urllib.request,hashlib,time
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
get=lambda u:urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Codex-source-review'}),timeout=25).read()
meta=json.loads((O/'SOURCE_COMMITS.json').read_text());rows=json.loads((O/'SOURCE_FILES.json').read_text())
for p in ['trajopt/LICENSE','trajopt_sco/LICENSE']:
 ref=meta['trajopt']['commit'];url=f'https://raw.githubusercontent.com/tesseract-robotics/trajopt/{ref}/{p}';b=get(url);fn='trajopt__'+p.replace('/','__');(O/'sources'/fn).write_bytes(b);rows.append(dict(project='trajopt',path=p,url=url,ref=ref,local=fn,sha256=hashlib.sha256(b).hexdigest()))
(O/'SOURCE_FILES.json').write_text(json.dumps(rows,indent=2));wheel={}
for name in ['ompl','casadi']:
 try:
  d=json.loads(get('https://pypi.org/pypi/'+name+'/json'));wheel[name]=dict(version=d['info']['version'],files=[dict(filename=f['filename'],bytes=f['size'],sha256=f['digests']['sha256']) for f in d['urls']],source='https://pypi.org/pypi/'+name+'/json')
 except Exception as e:wheel[name]=dict(error=str(e))
(O/'PYTHON_DISTRIBUTION_REVIEW.json').write_text(json.dumps(wheel,indent=2));print({n:dict(version=d.get('version'),Windows=[f['filename'] for f in d.get('files',[]) if 'win_' in f['filename']]) for n,d in wheel.items()})
