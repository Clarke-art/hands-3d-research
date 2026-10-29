import sys
sys.dont_write_bytecode=True
import json,hashlib,math
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PHASE='STAGE5_GEOMETRY_PROPAGATION_AFTER_DONOR_TRANSFER_R1'
APP=ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_r1'
STAGE4=APP/'RIGHT_HAND_ENGINEERING_STAGE4C_DONOR_TRANSFER_R1.blend'
R2=ROOT/'production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_r2/RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R2.blend'
EXPECTED={'STAGE4':'5f48ffa5ac6ff6d10b5d3bde1348571437b3a4fdf5c3ecfb97922e7dc0acd4d1','CORRECTED':'5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe','R2':'adf757aeace8a0d69070b94f102b9bef9eb99da9847dd7a5639c4c2c3799dde9'}
WEIGHT_HASH='1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55'
IDS=[738,2237,2238,2276,2328,2330]+list(range(3300,3348))
ASSETS={'CORRECTED':OUT/'RIGHT_HAND_STAGE5A_CORRECTED_RIG_DONOR_TRANSFER_R1.blend','R2':OUT/'RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_GEOMETRY_R1.blend'}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def canon(d):return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(d):return hashlib.sha256(canon(d)).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(n,d):
 (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def ref(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def inventory():return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
def inputs():
 r=read(OUT/'STAGE5_CURRENT_LINEAGE_INPUT_RECOVERY_R1.json')
 assert r['status']=='PASS'
 return {k:Path(v['path']) for k,v in r['inputs'].items()}
if __name__=='__main__':
 inv=inventory();dump('PROTECTED_HISTORY_HASHES_BEFORE.json',inv)
 blends={p:h for p,h in inv.items() if p.lower().endswith('.blend')}
 matches=[ROOT/p for p,h in blends.items() if h==EXPECTED['CORRECTED']]
 recovery={'method':'SHA256 scan of every existing workspace .blend; no path inference or fallback','workspace_blend_count':len(blends),'corrected_hash_matches':[str(p) for p in matches],'unique_corrected_artifact':len(matches)==1,'inputs':{},'status':'FAIL_CLOSED_STAGE5_LINEAGE_UNRESOLVED'}
 if len(matches)==1:
  ps={'STAGE4':STAGE4,'CORRECTED':matches[0],'R2':R2}
  recovery['inputs']={k:ref(p) for k,p in ps.items()}
  recovery['expected_input_hashes']=EXPECTED
  recovery['input_hashes_verified']=all(v['sha256']==EXPECTED[k] for k,v in recovery['inputs'].items())
  recovery['status']='PASS' if recovery['input_hashes_verified'] else 'FAIL_CLOSED_STAGE5_LINEAGE_UNRESOLVED'
 dump('STAGE5_CURRENT_LINEAGE_INPUT_RECOVERY_R1.json',recovery)
 assert recovery['status']=='PASS',recovery
 approval=Path('<USER_HOME>/.codex/attachments/a1c4f8fa-c1c9-499b-a358-5e6d61889a92/已粘贴的文本.txt')
 (OUT/'USER_PHASE_SCOPE_ORIGINAL.txt').write_bytes(approval.read_bytes())
 dump('USER_PHASE_SCOPE_REFERENCE.json',ref(approval))
 print(json.dumps({'protected_files':len(inv),'blend_scan':len(blends),'corrected_matches':[str(p) for p in matches],'status':recovery['status']}))
