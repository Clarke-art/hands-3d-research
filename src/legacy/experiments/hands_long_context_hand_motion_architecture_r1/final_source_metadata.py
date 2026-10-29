import sys,json,urllib.request,hashlib,datetime
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent;D=O/'sources';idx=json.loads((D/'SOURCE_INDEX.json').read_text(encoding='utf8'))
urls=[
('https://raw.githubusercontent.com/agnJason/PianoMotion10M/86539e5a16d10ba462005f1f2bd9d72459ac2000/datasets/PianoPose.py','pianomotion__datasets_PianoPose.py'),
('https://api.github.com/repos/joonhyungbae/skypiano','skypiano_repo_metadata.json'),
('https://huggingface.co/api/datasets/PianoVAM/PianoVAM','pianovam_dataset_metadata.json')]
for url,name in urls:
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Codex-source-audit'}),timeout=20) as r:b=r.read(1000001)
  if len(b)>1000000:raise ValueError('metadata source cap')
  (D/name).write_bytes(b);idx.append(dict(url=url,file=name,status='FETCHED',bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),retrieved_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 except Exception as e:idx.append(dict(url=url,file=name,status='UNAVAILABLE',error=str(e)))
(D/'SOURCE_INDEX.json').write_text(json.dumps(idx,indent=2),encoding='utf8')
print('FINAL_SOURCE_METADATA',idx[-3:],flush=True)
