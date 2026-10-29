import json,urllib.request,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent; E=OUT/'evidence'; E.mkdir(exist_ok=True)
rev=json.loads((OUT/'NPM_PACKAGE_METADATA.json').read_text(encoding='utf-8-sig'))['gitHead']
def fetch(url,name):
 req=urllib.request.Request(url,headers={'User-Agent':'hands-fingering-poc-r1'})
 with urllib.request.urlopen(req,timeout=45) as r:data=r.read()
 (E/name).write_bytes(data);return data
repo=json.loads(fetch('https://api.github.com/repos/lumikey/piano-fingering-model','GITHUB_REPO.json'))
tree=json.loads(fetch(f'https://api.github.com/repos/lumikey/piano-fingering-model/git/trees/{rev}?recursive=1','GITHUB_RELEASE_TREE.json'))
fetch(f'https://api.github.com/repos/lumikey/piano-fingering-model/commits/{rev}','GITHUB_RELEASE_COMMIT.json')
paths=[x['path'] for x in tree['tree']]
for path in ['README.md','js/README.md','js/package.json','js/src/node.ts','js/src/inference.ts','python/train.py','python/export_onnx.py']:
 if path in paths:fetch(f'https://raw.githubusercontent.com/lumikey/piano-fingering-model/{rev}/{path}',path.replace('/','__'))
license_paths=[p for p in paths if any(k in p.lower() for k in ['license','copying','notice','model_card'])]
for path in license_paths:fetch(f'https://raw.githubusercontent.com/lumikey/piano-fingering-model/{rev}/{path}',path.replace('/','__'))
weights=[]
for hand in ['left','right']:
 name=f'fingering_transformer_{hand}.onnx'; data=fetch(f'https://raw.githubusercontent.com/lumikey/piano-fingering-model/{rev}/js/models/{name}',name)
 local=OUT/'node_modules/@lumikey/piano-fingering-model/models'/name
 assert data==local.read_bytes()
 weights.append(dict(hand=hand,file=str(local),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),matches_release_git_revision=True))
result=dict(release_git_revision=rev,github_repository_license=repo.get('license'),license_related_paths=license_paths,weights=weights,tree_truncated=tree['truncated'])
(E/'MODEL_PROVENANCE.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result))
