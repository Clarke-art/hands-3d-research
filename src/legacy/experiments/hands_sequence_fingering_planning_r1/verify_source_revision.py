import json,hashlib,urllib.request
from pathlib import Path
O=Path(__file__).resolve().parent;E=O/'evidence'
for tag,repo in [('pianoplayer','marcomusy/pianoplayer'),('ramoneda','PRamoneda/Automatic-Piano-Fingering')]:
 branch=json.loads((E/f'{tag}_repo.json').read_text())['default_branch'];req=urllib.request.Request(f'https://api.github.com/repos/{repo}/commits/{branch}',headers={'User-Agent':'piano-sequence-planning-r1'})
 with urllib.request.urlopen(req,timeout=35) as response:data=response.read()
 (E/f'{tag}_commit.json').write_bytes(data);commit=json.loads(data);tree=json.loads((E/f'{tag}_tree.json').read_text());print(tag,'COMMIT',commit['sha'],'TREE',commit['commit']['tree']['sha'],'saved',tree['sha'])
 assert commit['commit']['tree']['sha']==tree['sha'] or commit['sha']==tree['sha']
 for file in (E/tag).rglob('*'):
  if not file.is_file():continue
  rel=file.relative_to(E/tag).as_posix();entry=next(x for x in tree['tree'] if x['path']==rel);content=file.read_bytes();blobsha=hashlib.sha1(f'blob {len(content)}\0'.encode()+content).hexdigest();assert blobsha==entry['sha'],rel
