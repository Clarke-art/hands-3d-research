import sys,json,re,urllib.request,hashlib,urllib.parse,datetime
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent;D=O/'sources';index=json.loads((D/'SOURCE_INDEX.json').read_text(encoding='utf8'))
def get(url,name,cap=2500000):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Codex-source-audit'}),timeout=25) as r:b=r.read(cap+1)
  if len(b)>cap:raise ValueError('small source cap')
  (D/name).write_bytes(b);index.append(dict(url=url,file=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),status='FETCHED',retrieved_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()));return b
 except Exception as e:index.append(dict(url=url,file=name,status='UNAVAILABLE',error=str(e)));return None
repo='agnJason/PianoMotion10M';b=get('https://api.github.com/repos/'+repo,'pianomotion_repo.json')
if b:
 default=json.loads(b)['default_branch'];b=get('https://api.github.com/repos/'+repo+'/commits/'+default,'pianomotion_commit_verified.json')
 if b:
  sha=json.loads(b)['sha'];tree=get('https://api.github.com/repos/'+repo+'/git/trees/'+sha+'?recursive=1','pianomotion_tree_verified.json')
  paths=[r['path'] for r in json.loads(tree)['tree'] if r['type']=='blob']
  chosen=[p for p in paths if p in ['README.md','LICENSE','infer.py','draw.py','docs/install.md','docs/dataset.md','datasets/show.py','requirements.txt'] or p.startswith('datasets/') and p.endswith('.py') and ('loader' in p or 'piano' in p)]
  for p in chosen:get('https://raw.githubusercontent.com/'+repo+'/'+sha+'/'+p,'pianomotion__'+p.replace('/','_'))
  print('PIANOMOTION_DEFAULT',default,sha,chosen,flush=True)
for key,base in [('tipiano','https://tipiano.io/'),('skypiano','https://joonhyungbae.github.io/skypiano/')]:
 html=(D/(key+'.txt')).read_text(encoding='utf8');src=re.search(r'<script[^>]+src="([^"]+)"',html).group(1);b=get(urllib.parse.urljoin(base,src),key+'_official_bundle.txt')
 if b:
  text=b.decode('utf8',errors='replace');links=sorted(set(re.findall(r'https://github\.com/[^"<> \t\n)]+',text)));print('OFFICIAL_LINKS',key,links,flush=True)
  print('LICENSE_SNIPPETS',key,[text[max(0,m.start()-80):m.end()+160] for m in re.finditer(r'CC BY|CC-BY|[Ll]icen[cs]e|TBD|coming soon',text)][:15],flush=True)
(D/'SOURCE_INDEX.json').write_text(json.dumps(index,indent=2),encoding='utf8')
