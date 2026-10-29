import sys
sys.dont_write_bytecode=True
import json,hashlib,ast
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
PRIOR=ROOT/'audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1'
SOURCE=ROOT/'audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1'
PHASE='PALMAR_DIGIT_ROOT_LOCAL_DONOR_SHAPE_RESTORATION_FEASIBILITY_R1'
CURRENT=ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_r1/RIGHT_HAND_ENGINEERING_STAGE4C_DONOR_TRANSFER_R1.blend'
R2=ROOT/'production_spec/stage5_production_rig/geometry_propagation_after_donor_transfer_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_GEOMETRY_R1.blend'
RESPONSE=Path('<USER_HOME>/Downloads/CURRENT_FULL_STAGE6A_CROSSING_HUMAN_RESPONSE_R1.json')
REQUEST=Path('<USER_HOME>/.codex/attachments/8c667de0-aa92-4d10-90ed-d4a3e594f0a1/已粘贴的文本.txt')
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
def inventory():return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
def reuse(path,names,ns):
 tree=ast.parse(Path(path).read_text(encoding='utf-8-sig'));nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];assert {n.name for n in nodes}==set(names)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns)
 return {'source':ref(path),'function_AST_sha256':{n.name:digest(ast.dump(n)) for n in nodes}}
if __name__=='__main__':
 dump('FROZEN_HASHES_BEFORE.json',inventory())
 dump('HUMAN_RESPONSE_HASH_BEFORE.json',{'current_external_source_present':RESPONSE.is_file(),'current_source':ref(RESPONSE) if RESPONSE.is_file() else None,'prior_byte_preservation_receipt':ref(PRIOR/'CURRENT9_HUMAN_RESPONSE_HOLD_VERIFICATION_R1.json'),'state':'HOLD_NOT_CLOSED','note':'External downloaded response unavailable at start of this round; prior receipt remains frozen, no response recreated or written'});print('Frozen source and response inventory captured',flush=True)
