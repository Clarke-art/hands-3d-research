import json,urllib.request,hashlib,zipfile,io
from pathlib import Path
O=Path(__file__).resolve().parent; E=O/'evidence';E.mkdir(exist_ok=True)
def fetch(url,p):
 req=urllib.request.Request(url,headers={'User-Agent':'piano-sequence-planning-r1'})
 with urllib.request.urlopen(req,timeout=35) as r:d=r.read()
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(d);return d
for repo,tag in [('marcomusy/pianoplayer','pianoplayer'),('PRamoneda/Automatic-Piano-Fingering','ramoneda')]:
 meta=json.loads(fetch(f'https://api.github.com/repos/{repo}',E/f'{tag}_repo.json'))
 tree=json.loads(fetch(f'https://api.github.com/repos/{repo}/git/trees/{meta["default_branch"]}?recursive=1',E/f'{tag}_tree.json'));rev=tree['sha'];paths=[x['path'] for x in tree['tree']]
 print(json.dumps(dict(route=tag,revision=rev,license=meta.get('license'),truncated=tree['truncated'],files=[x for x in tree['tree'] if x['path'].startswith(('models/','pianoplayer/','nns/')) or x['path'] in ['README.md','LICENSE','pyproject.toml']],)))
 selected=['README.md','LICENSE','pyproject.toml','pianoplayer/hand.py','pianoplayer/scorereader.py','pianoplayer/utils.py','pianoplayer/__init__.py','pianoplayer/pianoplayer.py','nns/seq2seq.py','nns/beam_search.py','choice_model.py','experiment_beam_k.py']
 for path in selected:
  if path in paths:fetch(f'https://raw.githubusercontent.com/{repo}/{rev}/{path}',E/tag/path)
