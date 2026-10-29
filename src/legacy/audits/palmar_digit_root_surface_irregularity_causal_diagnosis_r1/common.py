import sys
sys.dont_write_bytecode=True
import json, hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
S5=ROOT/'production_spec/stage5_production_rig'
S6=ROOT/'production_spec/stage6_deformation'
FRESH=S6/'full_stage6a_requalification_after_donor_transfer_r1'
PREP=S6/'current_full_stage6a_crossing_human_adjudication_prep_r1'
HIST=S6/'full_stage6a_requalification_r1'
SOURCE=ROOT/'audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1'
NATIVE=S5/'geometry_propagation_after_donor_transfer_r1/R2_REOPENED_NATIVE_PAYLOAD_R1.json'
RESPONSE=Path('<USER_HOME>/Downloads/CURRENT_FULL_STAGE6A_CROSSING_HUMAN_RESPONSE_R1.json')
PHASE='PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_CAUSAL_DIAGNOSIS_R1'
CASES=['IDX_MCP_15','IDX_MCP_30','TH_IP_15']
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(n,d):
 def cv(x):
  if hasattr(x,'tolist'):return x.tolist()
  if hasattr(x,'item'):return x.item()
  raise TypeError(type(x))
 (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False,default=cv)+'\n',encoding='utf-8')
def ref(p):return {'path':str(Path(p).relative_to(ROOT)) if Path(p).is_relative_to(ROOT) else str(p),'sha256':sha(p)}
def inventory():return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
if __name__=='__main__':
 dump('FROZEN_HASHES_BEFORE.json',inventory())
 dump('RESPONSE_SOURCE_HASH_BEFORE.json',{'source':ref(RESPONSE),'size_bytes':RESPONSE.stat().st_size,'claimed_state':'HOLD_NOT_CLOSED','closure_created':False})
 print('Frozen inventory and external response captured',flush=True)
