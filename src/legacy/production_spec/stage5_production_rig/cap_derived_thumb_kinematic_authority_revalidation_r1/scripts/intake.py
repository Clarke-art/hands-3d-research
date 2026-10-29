from pathlib import Path
import json,hashlib,sys
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
A=read(OUT.parent/'stage5b_r1e_human_cap_authority_freeze_r1/THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1.json')
h=hashlib.sha256(json.dumps({k:v for k,v in A.items() if k!='combined_authority_hash'},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
assert h==A['combined_authority_hash']=='c81dd96d6925ed402cdf0ba44c148d7a78c2c60640fe23fb6247fb729f346cc8'
assert A['status']=='HUMAN_APPROVED_FROZEN' and len(A['vertex_ids'])==37 and len(A['face_ids'])==25
dump('CAP_AUTHORITY_INPUT_VERIFICATION.json',{'hash':h,'status':A['status'],'vertices':37,'faces':25,'selector_runs':0,'membership_changed':False})
prior=read(OUT.parent/'stage5b_r1e_cap_dependency_blast_radius_audit_r1/PROTECTED_STATE_VERIFICATION.json')
external=prior.get('external',[])
paths=[p for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents and '.git' not in p.parts]
extra=[]
for r in external:
 p=Path(r['path'])
 if p.exists():extra.append(p)
dump('FROZEN_HASHES_BEFORE.json',{'workspace':{str(p.relative_to(ROOT)):sha(p) for p in paths},'external':{str(p):sha(p) for p in extra}})
print('VERIFIED cap37',h,'protected',len(paths),'external',len(extra))
