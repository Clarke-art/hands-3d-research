import sys,json,urllib.request,concurrent.futures,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;meta=json.loads((O/'SOURCE_COMMITS.json').read_text());rows=json.loads((O/'SOURCE_FILES.json').read_text())
def get(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Codex-source-review'}),timeout=25).read()
for name in ['trajopt','tesseract_planning']:
 repo=meta[name]['repo'];ref=meta[name]['commit'];tree=json.loads(get(f'https://api.github.com/repos/{repo}/git/trees/{ref}?recursive=1'))['tree'];paths=[x['path'] for x in tree if x['type']=='blob'];(O/'sources'/(name+'_tree_paths.json')).write_text(json.dumps(paths,indent=2));selected=[]
 for key in (['trajopt/include/trajopt/collision_terms.hpp','trajopt/include/trajopt/kinematic_terms.hpp','trajopt/src/collision_terms.cpp','trajopt/src/kinematic_terms.cpp','trajopt/src/problem_description.cpp','trajopt_sco/src/optimizers.cpp','trajopt/CMakeLists.txt','LICENSE.Apache-2.0','LICENSE.BSD-2-Clause'] if name=='trajopt' else ['LICENSE.Apache-2.0','LICENSE.BSD-2-Clause','LICENSE.BSD-3-Clause']):
  if key in paths:selected.append(key)
 if name=='tesseract_planning':selected += [p for p in paths if ('trajopt' in p and p.endswith('planner.cpp'))][:2]
 for p in selected:
  url=f'https://raw.githubusercontent.com/{repo}/{ref}/{p}';b=get(url);fn=name+'__'+p.replace('/','__');(O/'sources'/fn).write_bytes(b);rows.append(dict(project=name,path=p,ref=ref,url=url,local=fn,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b)))
 print(name,selected)
(O/'SOURCE_FILES.json').write_text(json.dumps(rows,indent=2))
