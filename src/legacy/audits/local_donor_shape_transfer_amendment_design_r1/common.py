import sys
sys.dont_write_bytecode=True
import json,hashlib,ast
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
PRIOR=ROOT/'audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1'
DIAG=ROOT/'audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1'
PHASE='LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_DESIGN_R1'
SOURCE=ROOT/'production_spec/stage4_blender/stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend'
MASTER=ROOT/'references/licenses/blender_human_base_meshes/extracted/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend'
REST=ROOT/'production_spec/stage4_blender/stage4a_r2/RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend'
R2=ROOT/'production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_r2/RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R2.blend'
FULL=ROOT/'production_spec/stage6_deformation/full_stage6a_requalification_r1'
CANDIDATE=OUT/'RIGHT_HAND_ENGINEERING_STAGE4C_R2_DONOR_TRANSFER_CANDIDATE_R1.blend'
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
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False,default=lambda z:z.item())+'\n',encoding='utf-8')
def reuse(path,names,ns):
 tree=ast.parse(Path(path).read_text(encoding='utf-8-sig'));nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
 assert {n.name for n in nodes}==set(names)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns)
 return {'source':ref(path),'function_AST_sha256':{n.name:digest(ast.dump(n)) for n in nodes}}
def inventory():return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
if __name__=='__main__':
 dump('FROZEN_HASHES_BEFORE.json',inventory())
 print('Protected historical and production inventory captured')
