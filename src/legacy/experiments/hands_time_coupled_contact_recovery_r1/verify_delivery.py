"""Independent delivery/protection verification; no solver or Blender imports."""
import json,hashlib,time,math
from pathlib import Path
O=Path(__file__).resolve().parent;start=time.monotonic()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
before=json.loads((O/'PROTECTED_FILES_BEFORE.json').read_text());changed=[];missing=[]
for name,h in before.items():
 p=Path(name)
 if not p.exists():missing.append(name)
 elif sha(p)!=h:changed.append(name)
protection=dict(status='PASS' if not changed and not missing else 'FAIL_CLOSED',protected_count=len(before),changed=changed,missing=missing,independent_rehash=True,seconds=time.monotonic()-start)
(O/'PROTECTION_CHECK.json').write_text(json.dumps(protection,indent=2));assert protection['status']=='PASS',protection
# Read actual Blender-recovered controls rather than relying only on requested state vectors.
rows=json.loads((O/'LOCAL_ADJACENCY_CHECK.json').read_text())['actual_samples'];rates=[]
for a,b in zip(rows,rows[1:]):
 dt=b['display_time']-a['display_time'];qa=[v for finger in a['anatomy']['recovered_controls'] for v in finger];qb=[v for finger in b['anatomy']['recovered_controls'] for v in finger];v=[(y-x)/dt for x,y in zip(qa,qb)];rates.append(dict(times=[a['display_time'],b['display_time']],recovered_joint_rate_deg_s=v,max_abs=max(abs(x) for x in v),pass_=all(abs(x)<=240 for x in v)))
assert all(r['pass_'] for r in rates)
(O/'ACTUAL_RECOVERED_JOINT_RATE_CHECK.json').write_text(json.dumps(dict(source='Blender anatomy.recovered_controls, not supplied target state',segments=rates,all_pass=True,max_abs_deg_s=max(r['max_abs'] for r in rates)),indent=2))
required=['RECOVERY_TIMELINE_AUDIT.md','TIME_COUPLED_CONSTRAINT_CONTRACT.json','NONSMOOTH_DERIVATIVE_GUARD.md','TIME_COUPLED_SOLVE_RESULTS.json','ACTUAL_BLENDER_VALIDATION.json','LOCAL_ADJACENCY_CHECK.json','PRODUCT_ROUTE_EXIT_REVIEW.md','FINAL_RECOMMENDATION.md'];assert all((O/f).exists() for f in required)
for f in O.rglob('*.json'):json.loads(f.read_text(encoding='utf-8-sig'))
for f in O.glob('*.py'):compile(f.read_text(encoding='utf-8-sig'),str(f),'exec')
(O/'DELIVERY_CHECK.json').write_text(json.dumps(dict(required=required,all_present=True,all_json_parse=True,all_python_compile=True,protected_unchanged=len(before),actual_recovered_joint_rates_pass=True,authority='DESIGN_PROVISIONAL',stop='STOP — HUMAN REVIEW'),indent=2))
f=O/'FINAL_RECOMMENDATION.md';s=f.read_text(encoding='utf-8');s=s.replace('保护文件独立复核见PROTECTION_CHECK.json。',f'独立重算{len(before)}个受保护文件哈希，0处变化、0个缺失（PROTECTION_CHECK.json）。Blender反解关节角的相邻速率也独立通过240deg/s原门禁。');f.write_text(s,encoding='utf-8')
print('PROTECTION',protection);print('ACTUAL_JOINT_RATE_MAX',max(r['max_abs'] for r in rates));print('DELIVERY_PASS')
