"""Independent file protection check: no imports of experiment or Blender modules."""
import json,hashlib,time
from pathlib import Path
O=Path(r'<HANDS_ROOT>_contact_derivative_feasibility_recovery_r1');start=time.monotonic()
before=json.loads((O/'PROTECTED_FILES_BEFORE.json').read_text());changed=[];missing=[]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
for p,h in before.items():
 f=Path(p)
 if not f.exists():missing.append(p)
 elif sha(f)!=h:changed.append(p)
out=dict(status='PASS' if not changed and not missing else 'FAIL_CLOSED',protected_file_count=len(before),changed=changed,missing=missing,independent_rehash=True,seconds=time.monotonic()-start,authority='DESIGN_PROVISIONAL')
(O/'PROTECTION_CHECK.json').write_text(json.dumps(out,indent=2));print(out)
required=['CASADI_JACOBIAN_ROOT_CAUSE.md','CONTACT_DERIVATIVE_CONTRACT.md','DERIVATIVE_VALIDATION.json','JACOBIAN_PERFORMANCE_COMPARISON.json','CONTACT_FEASIBILITY_RECOVERY.json','LOCAL_25MS_REGRESSION.json','PRODUCT_ROUTE_REVIEW.md','FINAL_RECOMMENDATION.md']
assert all((O/n).exists() for n in required)
for p in O.rglob('*.json'):json.loads(p.read_text(encoding='utf-8-sig'))
(O/'DELIVERY_CHECK.json').write_text(json.dumps(dict(required_files=required,all_present=True,all_json_parse=True,protection=out['status'],authority='DESIGN_PROVISIONAL',stop='STOP — HUMAN REVIEW'),indent=2))
