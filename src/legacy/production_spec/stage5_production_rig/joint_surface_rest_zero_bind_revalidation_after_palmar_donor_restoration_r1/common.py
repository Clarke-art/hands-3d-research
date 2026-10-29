import sys
sys.dont_write_bytecode=True
import json,hashlib,ast,math
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
S5=ROOT/'production_spec/stage5_production_rig'
PROP=S5/'geometry_propagation_after_palmar_donor_restoration_r1'
OLD=S5/'geometry_propagation_after_donor_transfer_r1'
PRIOR=S5/'joint_surface_rest_zero_bind_revalidation_after_donor_transfer_r1'
IDS=list(range(3348,3364))
APP=ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_palmar_root_r1'
PHASE='JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_PALMAR_DONOR_RESTORATION_R1'
FILES={'STAGE4':APP/'RIGHT_HAND_ENGINEERING_STAGE4C_DONOR_TRANSFER_PALMAR_ROOT_R1.blend','CORRECTED':PROP/'RIGHT_HAND_STAGE5A_CORRECTED_RIG_DONOR_TRANSFER_PALMAR_ROOT_R1.blend','R2':PROP/'RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend','OLD_CORRECTED':OLD/'RIGHT_HAND_STAGE5A_CORRECTED_RIG_DONOR_TRANSFER_R1.blend','OLD_R2':OLD/'RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_GEOMETRY_R1.blend'}
EXPECTED={'STAGE4':'0c1831042151a40f87f3779b97ece94cfc29a7831babfa1dda64c9ac0f4ae9c6','CORRECTED':'b7a4fe408ba979ee41f72b1a62e25b7ce292da42da561dc47bbc65b9475d6b8e','R2':'90d3ebd1c1973f94020b66281781db481d5a366271a9d6aac6b921861e2b45aa','OLD_CORRECTED':'513323c98a0d2a1c3b45f5543c6738476af7090447e84a0cc510d6e9606adc62','OLD_R2':'d8ea48d5d09635a46aebabb7a6e516f2a2a8599c92f2ca68489cdbeb0ec6866d'}
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
