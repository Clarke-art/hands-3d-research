import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
OLD=ROOT/'audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1'
PHASE='ORIGINAL_SOURCE_DORSAL_MCP_LINEAGE_AND_PATCH_TRANSFER_FEASIBILITY_R1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(n,d):
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def inventory():return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
if __name__=='__main__':
 dump('FROZEN_HASHES_BEFORE.json',inventory());print('Protected inventory captured')
