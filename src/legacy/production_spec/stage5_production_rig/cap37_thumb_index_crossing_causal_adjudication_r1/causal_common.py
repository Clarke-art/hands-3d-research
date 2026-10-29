import sys
sys.dont_write_bytecode=True
import json,hashlib,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
S5=ROOT/'production_spec/stage5_production_rig';S6=ROOT/'production_spec/stage6_deformation'
PREV=S5/'cap_fixture_static_validation_and_targeted_deformation_r1'
R1D=S5/'targeted_rig_and_skin_data_rebuild_after_approval_r1';R2D=S5/'targeted_rig_and_skin_data_rebuild_r2'
PHASE='CAP37_THUMB_INDEX_CROSSING_CAUSAL_ADJUDICATION_R1'
EXPECTED='adf757aeace8a0d69070b94f102b9bef9eb99da9847dd7a5639c4c2c3799dde9'
VECTOR='1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55'
ASSETS={'HISTORICAL_R1B_DONOR':S5/'stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend','CORRECTED_R1':R1D/'RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R1.blend','R2':R2D/'RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R2.blend'}
PAIRS=[{'id':'PAIR_1225_2740','faces':[1225,2740],'pose':'TH_IP_30','bone':'THUMB_IP_R','max_angle':30.0},{'id':'PAIR_1041_2735','faces':[1041,2735],'pose':'IDX_MCP_45','bone':'INDEX_MCP_R','max_angle':45.0},{'id':'PAIR_1226_2742','faces':[1226,2742],'pose':'IDX_MCP_45','bone':'INDEX_MCP_R','max_angle':45.0}]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.item())+'\n',encoding='utf-8')
def digest(d):return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def inventory():return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
def reuse(path,names,ns):
 tree=ast.parse(Path(path).read_text(encoding='utf-8-sig'));nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
 assert {n.name for n in nodes}==set(names)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns)
 return {n.name:digest(ast.dump(n)) for n in nodes}
