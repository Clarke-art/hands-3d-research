import sys
sys.dont_write_bytecode=True
import json,hashlib,ast,math
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
S5=ROOT/'production_spec/stage5_production_rig'
PROP=S5/'geometry_propagation_after_donor_transfer_r1'
APP=ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_r1'
PHASE='JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_DONOR_TRANSFER_R1'
FILES={'STAGE4':APP/'RIGHT_HAND_ENGINEERING_STAGE4C_DONOR_TRANSFER_R1.blend','CORRECTED':PROP/'RIGHT_HAND_STAGE5A_CORRECTED_RIG_DONOR_TRANSFER_R1.blend','R2':PROP/'RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_GEOMETRY_R1.blend','OLD_CORRECTED':S5/'human_thumb_kinematic_authority_correction_r1/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_THUMB_KINEMATIC_CORRECTED_R1.blend','OLD_R2':S5/'targeted_rig_and_skin_data_rebuild_r2/RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R2.blend'}
EXPECTED={'STAGE4':'5f48ffa5ac6ff6d10b5d3bde1348571437b3a4fdf5c3ecfb97922e7dc0acd4d1','CORRECTED':'513323c98a0d2a1c3b45f5543c6738476af7090447e84a0cc510d6e9606adc62','R2':'d8ea48d5d09635a46aebabb7a6e516f2a2a8599c92f2ca68489cdbeb0ec6866d','OLD_CORRECTED':'5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe','OLD_R2':'adf757aeace8a0d69070b94f102b9bef9eb99da9847dd7a5639c4c2c3799dde9'}
WEIGHT_HASH='1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def canon(d):return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(d):return hashlib.sha256(canon(d)).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def ref(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def inventory():return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
def reuse(p,names,ns):
 tree=ast.parse(Path(p).read_text(encoding='utf-8-sig'));nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
 assert {n.name for n in nodes}==set(names)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ns)
 return {'source':ref(p),'functions_AST_sha256':{n.name:digest(ast.dump(n)) for n in nodes},'top_level_code_executed':False}
if __name__=='__main__':
 inv=inventory();dump('PROTECTED_HISTORY_HASHES_BEFORE.json',inv)
 assert all(sha(p)==EXPECTED[k] for k,p in FILES.items())
 assert read(PROP/'STAGE5_GEOMETRY_PROPAGATION_AFTER_DONOR_TRANSFER_R1_STATUS.json')['STAGE5_GEOMETRY_PROPAGATION_VERDICT']=='PASS_GEOMETRY_PROPAGATED_WITH_RIG_AND_WEIGHTS_FROZEN'
 (OUT/'payload.py').write_bytes((PROP/'payload.py').read_bytes())
 request=Path('<USER_HOME>/.codex/attachments/043cf137-211b-4930-aac1-ad2daf3cd0d3/已粘贴的文本.txt')
 (OUT/'USER_PHASE_SCOPE_ORIGINAL.txt').write_bytes(request.read_bytes())
 dump('PHASE_INPUT_HASH_RECOVERY_R1.json',{'status':'PASS','inputs':{k:ref(p) for k,p in FILES.items()},'prior_phase':ref(PROP/'STAGE5_GEOMETRY_PROPAGATION_AFTER_DONOR_TRANSFER_R1_STATUS.json'),'payload_reader_reused_exact':ref(PROP/'payload.py'),'user_scope':ref(request),'protected_file_count':len(inv)})
 print('PRE-EXISTING FILES',len(inv),'INPUT HASHES PASS')
