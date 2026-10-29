import json,urllib.request,time,concurrent.futures,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;meta=json.loads((O/'SOURCE_COMMITS.json').read_text());rows=[]
def get(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Codex-source-review'}),timeout=30).read()
paths={'ompl':['LICENSE','CMakeLists.txt','src/ompl/base/spaces/constraint/ProjectedStateSpace.h','src/ompl/base/spaces/constraint/src/ProjectedStateSpace.cpp','src/ompl/base/spaces/constraint/AtlasStateSpace.h','src/ompl/base/spaces/constraint/TangentBundleStateSpace.h','src/ompl/base/SpaceInformation.h','src/ompl/geometric/planners/rrt/RRTConnect.h'],'trajopt':['LICENSE','README.md','CMakeLists.txt'],'tesseract_planning':['LICENSE','README.md','CMakeLists.txt'],'casadi':['LICENSE.txt','docs/examples/python/direct_collocation.py','docs/examples/python/direct_multiple_shooting.py','casadi/interfaces/ipopt/ipopt_interface.cpp','casadi/core/callback.hpp']}
def fetch(job):
 name,p,ref=job;repo=meta[name]['repo'];url=f'https://raw.githubusercontent.com/{repo}/{ref}/{p}'
 try:
  b=get(url);fn=name+'__'+p.replace('/','__');(O/'sources'/fn).write_bytes(b);return dict(project=name,path=p,ref=ref,url=url,local=fn,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
 except Exception as e:return dict(project=name,path=p,error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(fetch,[(n,p,'3.7.2' if n=='casadi' else meta[n]['commit']) for n,pp in paths.items() for p in pp]))
try:
 tag=json.loads(get('https://api.github.com/repos/casadi/casadi/git/ref/tags/3.7.2'));meta['casadi_executed_tag']=tag
except Exception as e:meta['tag_error']=str(e)
(O/'SOURCE_COMMITS.json').write_text(json.dumps(meta,indent=2));(O/'SOURCE_FILES.json').write_text(json.dumps(rows,indent=2));print([(r['project'],r['path'],r.get('bytes',r.get('error'))) for r in rows])
