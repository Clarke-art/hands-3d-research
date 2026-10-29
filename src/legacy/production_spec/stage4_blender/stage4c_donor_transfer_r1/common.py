import sys
sys.dont_write_bytecode=True
import json,hashlib,ast
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
DESIGN=ROOT/'audits/local_donor_shape_transfer_amendment_design_r1'
DIAG=ROOT/'audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1'
PHASE='LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_APPLICATION_R1'
SOURCE=ROOT/'production_spec/stage4_blender/stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend'
DONOR=ROOT/'references/licenses/blender_human_base_meshes/extracted/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend'
CANDIDATE=DESIGN/'RIGHT_HAND_ENGINEERING_STAGE4C_R2_DONOR_TRANSFER_CANDIDATE_R1.blend'
ASSET=OUT/'RIGHT_HAND_ENGINEERING_STAGE4C_DONOR_TRANSFER_R1.blend'
R2=ROOT/'production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_r2/RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R2.blend'
FULL=ROOT/'production_spec/stage6_deformation/full_stage6a_requalification_r1'
APPROVAL_INPUT=Path('<USER_HOME>/.codex/attachments/5235f116-c911-4cd9-a6af-6bcc1ebbd8b5/已粘贴的文本.txt')
IDS=[738,2237,2238,2276,2328,2330]+list(range(3300,3348))
EXPECTED_SOURCE='fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7'
EXPECTED_CANDIDATE='9788ef1582344b12d17c8c201b59f6f1b5c59eb22648a0753bba1725481ed8e8'
EXPECTED_DONOR='3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def canon(d):return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(d):return hashlib.sha256(canon(d)).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ref(p):return {'path':Path(p).relative_to(ROOT).as_posix(),'sha256':sha(p)}
def dump(n,d):
 (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False,default=lambda z:z.item())+'\n',encoding='utf-8')
def reuse(path,names,ns):
 tree=ast.parse(Path(path).read_text(encoding='utf-8-sig'));nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
 assert {n.name for n in nodes}==set(names)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns)
 return {'source':ref(path),'function_AST_sha256':{n.name:digest(ast.dump(n)) for n in nodes}}
def inventory():return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
if __name__=='__main__':
 dump('PROTECTED_HISTORY_HASHES_BEFORE.json',inventory())
 print('All pre-existing workspace files hash-captured; new revision directory excluded')
