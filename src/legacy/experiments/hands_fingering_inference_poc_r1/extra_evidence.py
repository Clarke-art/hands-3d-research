import json,urllib.request
from pathlib import Path
O=Path(__file__).resolve().parent/'evidence'
for url,name in [('https://api.github.com/repos/lumikey/piano-fingering-model/git/trees/main?recursive=1','GITHUB_CURRENT_TREE.json'),('https://registry.npmjs.org/-/npm/v1/attestations/@lumikey%2fpiano-fingering-model@0.3.0','NPM_ATTESTATIONS.json')]:
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'hands-fingering-poc-r1'})
  with urllib.request.urlopen(req,timeout=30) as r:d=r.read()
  (O/name).write_bytes(d)
  if 'TREE' in name:
   t=json.loads(d);print(json.dumps(dict(current_tree_sha=t['sha'],license_paths=[x['path'] for x in t['tree'] if any(k in x['path'].lower() for k in ['license','copying','notice','model_card'])],truncated=t['truncated'])))
 except Exception as e:print(name,str(e))
