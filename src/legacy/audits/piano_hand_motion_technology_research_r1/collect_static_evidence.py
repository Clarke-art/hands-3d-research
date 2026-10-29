"""Download only bounded public text/JSON. Never weights, datasets, media or executable code."""
from pathlib import Path
import urllib.request,json,hashlib,concurrent.futures,datetime
P=Path(__file__).resolve().parent;E=P/'evidence';E.mkdir(exist_ok=True)
urls={
 'pianomotion_tree.json':'https://api.github.com/repos/agnJason/PianoMotion10M/git/trees/master?recursive=1',
 'pianomotion_model_info.json':'https://huggingface.co/api/models/agnJason/PianoMotion_models?blobs=true',
 'pianomotion_model_tree.json':'https://huggingface.co/api/models/agnJason/PianoMotion_models/tree/main?recursive=true&expand=false',
 'furelise_info.json':'https://huggingface.co/api/datasets/rcwang/for_elise?blobs=true',
 'furelise_tree.json':'https://huggingface.co/api/datasets/rcwang/for_elise/tree/main?recursive=true&expand=false',
 'furelise_README.txt':'https://huggingface.co/datasets/rcwang/for_elise/raw/main/README.md',
 'furelise_download_data.txt':'https://huggingface.co/datasets/rcwang/for_elise/raw/main/download_data.sh',
 'pianomotion_project.html':'https://agnjason.github.io/PianoMotion-page/',
 'furelise_project.html':'https://for-elise.github.io/',
 'furelise_visualizer.html':'https://for-elise.github.io/static_visualizer/vis.html?id=100',
 'tipiano_project.html':'https://tipiano.io/',
}
records=[]
def fetch(item):
 name,url=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Codex-public-readonly-research-R1'})
  with urllib.request.urlopen(req,timeout=25) as res:
   data=res.read(524289)
   if len(data)>524288:raise ValueError('Text exceeds 512KiB cap; not retained')
   (E/name).write_bytes(data)
   return dict(name=name,url=url,status=res.status,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 except Exception as ex:return dict(name=name,url=url,error=str(ex))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:records=list(pool.map(fetch,urls.items()))
treepath=E/'pianomotion_tree.json'
if treepath.exists():
 tree=json.loads(treepath.read_text());commit=tree['sha'];paths=['infer.py','requirements.txt','LICENSE','docs/install.md','docs/prepare_dataset.md','docs/train_and_eval.md','datasets/PianoPose.py','datasets/show.py','models/piano2posi.py','mano/mano.py']
 actual={x['path'] for x in tree['tree'] if x['type']=='blob'}
 items=[('pianomotion_'+p.replace('/','__')+'.txt',f'https://raw.githubusercontent.com/agnJason/PianoMotion10M/{commit}/{p}') for p in paths if p in actual]
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:records+=list(pool.map(fetch,items))
 print('CODE_COMMIT',commit,'TREE_FILES',[(x['path'],x.get('size')) for x in tree['tree'] if x['type']=='blob'])
(P/'SOURCE_FETCH_MANIFEST.json').write_text(json.dumps(dict(checked_date='2026-10-11',records=records,total_bytes=sum(x.get('bytes',0) for x in records),no_code_executed=True),indent=2),encoding='utf8')
for r in records:print(r['name'],r.get('bytes'),r.get('error','OK'))
