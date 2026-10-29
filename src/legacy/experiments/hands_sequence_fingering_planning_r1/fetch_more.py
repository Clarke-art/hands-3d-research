import json,urllib.request,zipfile,io,re
from pathlib import Path
O=Path(__file__).resolve().parent;E=O/'evidence'
def fetch(url,p):
 req=urllib.request.Request(url,headers={'User-Agent':'piano-sequence-planning-r1'})
 try:
  with urllib.request.urlopen(req,timeout=35) as r:d=r.read()
 except Exception:
  with urllib.request.urlopen(req,timeout=35) as r:d=r.read()
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(d);return d
for tag,repo,paths in [('pianoplayer','marcomusy/pianoplayer',['pianoplayer/models.py','pianoplayer/core.py']),('ramoneda','PRamoneda/Automatic-Piano-Fingering',['nns/seq2seq_model.py','nns/f_seq2seq.py','common_classification.py'])]:
 rev=json.loads((E/f'{tag}_tree.json').read_text())['sha']
 for path in paths:fetch(f'https://raw.githubusercontent.com/{repo}/{rev}/{path}',E/tag/path)
page=fetch('https://statpianofingering.github.io/demo.html',E/'nakamura_demo.html').decode()
links=re.findall(r'href="([^"]+)"',page);print(links)
url=next(u for u in links if 'code' in u.lower() and u.endswith('.zip'))
from urllib.parse import urljoin
url=urljoin('https://statpianofingering.github.io/demo.html',url)
d=fetch(url,E/'nakamura_source.zip');z=zipfile.ZipFile(io.BytesIO(d))
for name in z.namelist():
 p=E/'nakamura'/name
 if name.endswith('/') or '..' in Path(name).parts:continue
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name))
print('NAKAMURA',url,len(d),z.namelist())

