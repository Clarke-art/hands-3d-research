"""Read-only future preflight. This script has no delete/move/rename/archive code."""
import sys
sys.dont_write_bytecode=True
import argparse,json,hashlib,os,time
from pathlib import Path
P=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description='HANDS R1 read-only preflight; never executes cleanup')
parser.add_argument('--plan',choices=['conservative','deep'],default='conservative')
args=parser.parse_args()
M=json.loads((P/'CLEANUP_MANIFEST.json').read_text(encoding='utf8'));R=Path(M['root'])
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as x:
  while b:=x.read(4*1024*1024):h.update(b)
 return h.hexdigest()
issues=[];existing={};links=[]
if sha(P/M['baseline_inventory'])!=M['baseline_inventory_sha256']:issues.append({'type':'inventory_tampered'})
F=[json.loads(x) for x in (P/M['baseline_inventory']).read_text(encoding='utf8').splitlines()];B={f['relative']:f for f in F};stack=[R]
while stack:
 d=stack.pop()
 try:entries=list(os.scandir(d))
 except OSError as ex:issues.append({'type':'inaccessible_directory','path':str(d),'error':str(ex)});continue
 for e in entries:
  try:
   s=os.stat(e.path,follow_symlinks=False)
   if getattr(s,'st_file_attributes',0)&0x400:links.append(e.path);issues.append({'type':'reparse_detected','path':e.path});continue
   if getattr(s,'st_file_attributes',0)&0x10:stack.append(Path(e.path));continue
   rel=str(Path(e.path).relative_to(R));existing[rel]=s
  except OSError as ex:issues.append({'type':'inaccessible_file','path':e.path,'error':str(ex)})
for rel,s in existing.items():
 b=B.get(rel)
 if not b:issues.append({'type':'new_file_requires_reaudit','path':str(R/rel)});continue
 if (s.st_size,s.st_mtime_ns,s.st_dev,s.st_ino,s.st_nlink)!=(b['size'],b['mtime_ns'],b['device'],b['file_id'],b['nlink']):issues.append({'type':'file_metadata_changed','path':str(R/rel)})
for rel in sorted(set(B)-set(existing)):issues.append({'type':'missing_baseline_file','path':str(R/rel)})
checks={a['path']:a['expected_sha256'] for a in M['protected_assets']};checks.update({x['path']:x['sha256'] for x in M['protected_code_hashes']})
selected=[e for e in M['entries'] if e['classification']=='DELETE_CANDIDATE' and (args.plan=='deep' or e['plan']=='conservative')]
for e in selected:
 try:
  target=Path(e['path']).resolve()
  if not target.is_relative_to(R.resolve()):issues.append({'type':'target_outside_workspace','path':e['path']})
 except OSError as ex:issues.append({'type':'resolve_failed','path':e['path'],'error':str(ex)})
 for f in e['members']:
  if f.get('expected_sha256'):checks[f['path']]=f['expected_sha256']
 for p in e['dependency_result']['required_retained_inputs']:
  if not Path(p).is_file():issues.append({'type':'required_retained_input_missing','path':p})
 for evidence in e['evidence']:
  if isinstance(evidence,dict) and evidence.get('canonical'):checks[evidence['canonical']]=evidence['sha256']
for p,d in checks.items():
 try:
  if sha(p)!=d:issues.append({'type':'sha256_mismatch','path':p})
 except OSError as ex:issues.append({'type':'hash_read_error','path':p,'error':str(ex)})
# Restat selected files after hashing so a change during preflight is explicit.
for e in selected:
 for f in e['members']:
  try:
   s=os.stat(f['path'],follow_symlinks=False)
   if (s.st_size,s.st_mtime_ns,s.st_ino,s.st_nlink)!=(f['expected_bytes'],f['expected_mtime_ns'],f['expected_file_id'],f['expected_nlink']):issues.append({'type':'changed_during_preflight','path':f['path']})
  except OSError as ex:issues.append({'type':'restat_error','path':f['path'],'error':str(ex)})
result={'task':M['task'],'mode':'READ_ONLY','plan':args.plan,'checked_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'checked_file_count':len(existing),'hash_checks':len(checks),'selected_entries':len(selected),'selected_bytes':sum(e['expected_bytes'] for e in selected),'snapshot_checks_pass':not issues,'issues':issues,'cleanup_executed':False,'human_approval_required':True,'remaining_manual_gate':'Even PASS is not deletion authorization: verify current runtime/dynamic/external references and render environments; explicitly approve exact IDs. Historical full-file checks require an approved intentional omission ledger.'}
(P/f'PREFLIGHT_{args.plan.upper()}_RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='issues'},ensure_ascii=False,indent=2))
if issues:print(json.dumps(issues[:30],ensure_ascii=False,indent=2))
sys.exit(0 if not issues else 2)
