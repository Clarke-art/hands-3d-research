import sys
sys.dont_write_bytecode=True
import json,hashlib,math,ast
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PHASE='STAGE5_GEOMETRY_PROPAGATION_AFTER_PALMAR_DONOR_RESTORATION_R1'
OLD=ROOT/'production_spec/stage5_production_rig/geometry_propagation_after_donor_transfer_r1'
APP=ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_palmar_root_r1'
DESIGN=ROOT/'audits/palmar_digit_root_local_donor_shape_restoration_design_r1'
PRIOR=ROOT/'audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1'
STAGE4=APP/'RIGHT_HAND_ENGINEERING_STAGE4C_DONOR_TRANSFER_PALMAR_ROOT_R1.blend'
SOURCES={'STAGE4':STAGE4,'CORRECTED':OLD/'RIGHT_HAND_STAGE5A_CORRECTED_RIG_DONOR_TRANSFER_R1.blend','R2':OLD/'RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_GEOMETRY_R1.blend'}
EXPECTED={'STAGE4':'0c1831042151a40f87f3779b97ece94cfc29a7831babfa1dda64c9ac0f4ae9c6','CORRECTED':'513323c98a0d2a1c3b45f5543c6738476af7090447e84a0cc510d6e9606adc62','R2':'d8ea48d5d09635a46aebabb7a6e516f2a2a8599c92f2ca68489cdbeb0ec6866d','RIG_AUTHORITY':'5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe'}
WEIGHT_HASH='1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55'
IDS=list(range(3348,3364))
ASSETS={'CORRECTED':OUT/'RIGHT_HAND_STAGE5A_CORRECTED_RIG_DONOR_TRANSFER_PALMAR_ROOT_R1.blend','R2':OUT/'RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend'}
REQUEST=Path('<USER_HOME>/.codex/attachments/d1b3b829-4194-40f9-bfa7-1b2c9212bfcb/已粘贴的文本.txt')
RESPONSE=Path('<USER_HOME>/Downloads/CURRENT_FULL_STAGE6A_CROSSING_HUMAN_RESPONSE_R1.json')
NEXT='JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_PALMAR_DONOR_RESTORATION_R1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def canon(d):return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(d):return hashlib.sha256(canon(d)).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ref(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def dump(n,d):
 def cv(x):
  if hasattr(x,'tolist'):return x.tolist()
  if hasattr(x,'item'):return x.item()
  raise TypeError(type(x))
 (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False,default=cv)+'\n',encoding='utf-8')
def inventory():return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
def reuse(p,names,ns):
 tree=ast.parse(Path(p).read_text(encoding='utf-8-sig'));nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];assert {n.name for n in nodes}==set(names)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ns)
 return {'source':ref(p),'AST_sha256':{n.name:digest(ast.dump(n)) for n in nodes}}
if __name__=='__main__':
 assert all(not p.exists() for p in ASSETS.values())
 inv=inventory();dump('PROTECTED_HISTORY_HASHES_BEFORE.json',inv)
 rig=Path(read(OLD/'STAGE5_CURRENT_LINEAGE_INPUT_RECOVERY_R1.json')['inputs']['CORRECTED']['path']);SOURCES['RIG_AUTHORITY']=rig
 matched={k:ref(p) for k,p in SOURCES.items()};ok=all(v['sha256']==EXPECTED[k] for k,v in matched.items())
 dump('PALMAR_STAGE5_INPUT_LINEAGE_RECOVERY_R1.json',{'status':'PASS' if ok else 'FAIL_CLOSED_STAGE5_LINEAGE_INPUT_MISMATCH','inputs':matched,'expected':EXPECTED,'weight_hash_expected':WEIGHT_HASH,'rig_authority_semantics':'Hash of existing canonical corrected-rig blend, recovered via frozen prior lineage receipt and independently verified; not a substituted native-payload digest','no_pre_donor_Stage5_application_source':True,'protected_file_count':len(inv),'full_mesh_geometry_authority':ref(STAGE4)})
 assert ok,'FAIL_CLOSED_STAGE5_LINEAGE_INPUT_MISMATCH'
 (OUT/'USER_PHASE_SCOPE_ORIGINAL.txt').write_bytes(REQUEST.read_bytes())
 dump('USER_PHASE_SCOPE_REFERENCE.json',ref(REQUEST))
 dump('CURRENT9_RESPONSE_STATE_BEFORE.json',{'external_present':RESPONSE.is_file(),'external_source':ref(RESPONSE) if RESPONSE.is_file() else None,'prior_hold_receipt':ref(PRIOR/'CURRENT9_HUMAN_RESPONSE_HOLD_VERIFICATION_R1.json'),'state':'HOLD_NOT_CLOSED'})
 print('Input file hashes PASS; corrected-rig authority recovered and verified; frozen files',len(inv),flush=True)
