"""Known official text URLs found in already-read source; no executable imports."""
from pathlib import Path
import urllib.request,json,hashlib,concurrent.futures
P=Path(__file__).resolve().parent;E=P/'evidence';commit=json.loads((E/'pianomotion_tree.json').read_text())['sha']
repo='https://raw.githubusercontent.com/agnJason/PianoMotion10M/'+commit+'/'
urls={
 'pianomotion_docs__train_eval.md.txt':repo+'docs/train_eval.md',
 'pianomotion_models__mano.py.txt':repo+'models/mano.py',
 'pianomotion_models__denoise_diffusion.py.txt':repo+'models/denoise_diffusion.py',
 'pianomotion_models__wav2vec.py.txt':repo+'models/wav2vec.py',
 'pianomotion_args_base_tf.json':'https://huggingface.co/agnJason/PianoMotion_models/raw/main/diffusion_posiguide_hubertbase_tf2/args.txt',
 'pianomotion_args_posi_base_tf.json':'https://huggingface.co/agnJason/PianoMotion_models/raw/main/diffusion_posiguide_hubertbase_tf2/args_posi.txt',
 'furelise_server.py.txt':'https://huggingface.co/datasets/rcwang/for_elise/raw/main/visualizer/server.py',
 'furelise_web_vis.js.txt':'https://for-elise.github.io/static_visualizer/js/vis.js',
 'furelise_metadata.json':'https://huggingface.co/datasets/rcwang/for_elise/raw/main/metadata.json',
 'mano_license.html':'https://mano.is.tue.mpg.de/license.html',
}
def fetch(item):
 name,url=item
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Codex-public-readonly-research-R1'}),timeout=25) as r:
   data=r.read(524289)
   if len(data)>524288:raise ValueError('512KiB cap')
   (E/name).write_bytes(data);return dict(name=name,url=url,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 except Exception as ex:return dict(name=name,url=url,error=str(ex))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:records=list(pool.map(fetch,urls.items()))
(P/'FOLLOWUP_FETCH_MANIFEST.json').write_text(json.dumps(records,indent=2),encoding='utf8')
for r in records:print(r['name'],r.get('bytes'),r.get('error','OK'))
