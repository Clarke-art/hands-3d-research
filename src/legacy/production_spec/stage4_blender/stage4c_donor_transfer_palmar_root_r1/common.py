import sys
sys.dont_write_bytecode=True
import json,hashlib,ast
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
DESIGN=ROOT/'audits/palmar_digit_root_local_donor_shape_restoration_design_r1'
PRIOR=ROOT/'audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1'
PHASE='PALMAR_DIGIT_ROOT_DONOR_RESTORATION_APPLICATION_R1'
SOURCE=ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_r1/RIGHT_HAND_ENGINEERING_STAGE4C_DONOR_TRANSFER_R1.blend'
CANDIDATE=DESIGN/'RIGHT_HAND_ENGINEERING_STAGE4C_DONOR_TRANSFER_PALMAR_ROOT_CANDIDATE_R1.blend'
ASSET=OUT/'RIGHT_HAND_ENGINEERING_STAGE4C_DONOR_TRANSFER_PALMAR_ROOT_R1.blend'
DONOR=ROOT/'references/licenses/blender_human_base_meshes/extracted/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend'
TARGET=DESIGN/'PALMAR_ROOT_FORMAL_TARGET_COORDINATES_R1.json'
WRITESET=DESIGN/'PALMAR_ROOT_FORMAL_WRITE_SET_R1.json'
IDS=list(range(3348,3364))
EXPECTED_SOURCE='5f48ffa5ac6ff6d10b5d3bde1348571437b3a4fdf5c3ecfb97922e7dc0acd4d1'
EXPECTED_CANDIDATE='278dd6b9462f96f4261319688f64a063ab79f76abb772bee09e62ce0eb43130d'
EXPECTED_DONOR='3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137'
REQUEST=Path('<USER_HOME>/.codex/attachments/cbf37ddc-39b0-4b91-bd87-8e1f3bdbd445/已粘贴的文本.txt')
RESPONSE=Path('<USER_HOME>/Downloads/CURRENT_FULL_STAGE6A_CROSSING_HUMAN_RESPONSE_R1.json')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def canon(d):return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(d):return hashlib.sha256(canon(d)).hexdigest()
def dump(n,d):
 def cv(x):
  if hasattr(x,'tolist'):return x.tolist()
  if hasattr(x,'item'):return x.item()
  raise TypeError(type(x))
 (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False,default=cv)+'\n',encoding='utf-8')
def ref(p):return {'path':Path(p).relative_to(ROOT).as_posix() if Path(p).is_relative_to(ROOT) else str(p),'sha256':sha(p)}
def reuse(path,names,ns):
 tree=ast.parse(Path(path).read_text(encoding='utf-8-sig'));nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];assert {n.name for n in nodes}==set(names)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns)
 return {'source':ref(path),'function_AST_sha256':{n.name:digest(ast.dump(n)) for n in nodes}}
def payload_helpers(ns):return reuse(ROOT/'production_spec/stage5_production_rig/geometry_propagation_after_donor_transfer_r1/payload.py',['plain','props','rna','object_payload','rig_payload','material_payload','snapshot'],ns)
def inventory():return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
if __name__=='__main__':
 assert not ASSET.exists(),'FAIL_CLOSED: never overwrite an existing application asset'
 dump('PROTECTED_HISTORY_HASHES_BEFORE.json',inventory())
 dump('CURRENT9_RESPONSE_STATE_BEFORE.json',{'external_present':RESPONSE.is_file(),'external_source':ref(RESPONSE) if RESPONSE.is_file() else None,'prior_hold_receipt':ref(PRIOR/'CURRENT9_HUMAN_RESPONSE_HOLD_VERIFICATION_R1.json'),'state':'HOLD_NOT_CLOSED'})
 print('All existing workspace files frozen; no existing files will be overwritten',flush=True)
