from pathlib import Path
import json,hashlib,urllib.request,sys
sys.dont_write_bytecode=True
ROOT=Path(r'<HANDS_ROOT>');OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
prev=ROOT/'experiments/hands_anatomical_sculpt_visual_poc_r1'
paths=[Path(r['path']) for r in json.loads((prev/'PROTECTED_BEFORE.json').read_text(encoding='utf-8-sig'))]
paths += [prev/n for n in ['A_SCULPT_NOT_APPROVED.blend','B_SCULPT_NOT_APPROVED.blend','TECHNICAL_REPORT.md','RESULT.json','PROTECTED_SHA256_BEFORE_AFTER.json']]
paths += [ROOT/'AGENTS.md',ROOT/'references/licenses/blender_human_base_meshes/extracted/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend',ROOT/'references/licenses/blender_human_base_meshes/LICENSE_EVIDENCE.md',ROOT/'audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/PALMAR_ROOT_SOURCE_ANCESTRY_R1.json']
dest=OUT/'PROTECTED_SHA256_BEFORE.json'
if not dest.exists():
 rows=[]
 for p in dict.fromkeys(paths):
  assert p.is_relative_to(ROOT) and p.resolve().is_relative_to(ROOT)
  rows.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size))
 dest.write_text(json.dumps(rows,indent=2),encoding='utf8');print('PROTECTED',len(rows),flush=True)
url='https://www.innerscene.com/api/library/posable-anatomical-right-hand-f6098b4f/download'
p=OUT/'sources/hand-posable.glb'
if not p.exists():
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60) as r:
  data=r.read();typ=r.headers.get('Content-Type');final=r.url
 assert data[:4]==b'glTF',(data[:40],typ)
 p.write_bytes(data)
 (OUT/'ASSET_DOWNLOAD_RECEIPT.json').write_text(json.dumps(dict(url=url,final_url=final,content_type=typ,bytes=len(data),sha256=sha(p)),indent=2),encoding='utf8')
 print('GLB',len(data),sha(p),flush=True)
