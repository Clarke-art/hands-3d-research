import sys,json,time,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent;before=json.loads((O/'PROTECTED_FILES_BEFORE.json').read_text(encoding='utf8'));out={};beg=time.monotonic();bad=[]
for s,h in before.items():
 p=Path(s)
 if not p.is_file():bad.append(dict(path=s,reason='MISSING'));continue
 hh=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):hh.update(b)
 digest=hh.hexdigest();out[s]=digest
 if digest!=h:bad.append(dict(path=s,before=h,after=digest))
roots=json.loads((O/'PROTECTION_SETUP.json').read_text(encoding='utf8'))['protected_roots'];current=set(str(p) for root in roots for p in Path(root).rglob('*') if p.is_file());new=sorted(current-set(before));deleted=sorted(set(before)-current)
(O/'PROTECTED_FILES_AFTER.json').write_text(json.dumps(out,indent=2),encoding='utf8');(O/'PROTECTION_CHECK.json').write_text(json.dumps(dict(status='PASS' if not bad and not new and not deleted else 'FAIL',before_count=len(before),after_count=len(out),hash_mismatches=bad,new_files_in_protected_roots=new,deleted_files=deleted,seconds=time.monotonic()-beg,independent_rehash=True),indent=2),encoding='utf8');print('PROTECTION_AFTER',len(out),'mismatch',len(bad),'new',len(new),'deleted',len(deleted),flush=True)
