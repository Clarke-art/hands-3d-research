import sys
sys.dont_write_bytecode=True
import os,json,hashlib,time
from pathlib import Path
ROOT=Path(r'D:\codex one\3D interactive components');H=ROOT/'hands';O=Path(__file__).parent
def rd(n):return json.loads((O/n).read_text(encoding='utf8'))
def save(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  while b:=f.read(4*1024*1024):h.update(b)
 return h.hexdigest()
def paths(r):
 stack=[r];out=set();issues=[]
 while stack:
  d=stack.pop()
  for e in os.scandir(d):
   p=Path(e.path)
   if p==O:continue
   s=e.stat(follow_symlinks=False)
   if s.st_file_attributes&0x400:issues.append(str(p));continue
   if s.st_file_attributes&0x10:stack.append(p)
   else:out.add(str(p))
 return out,issues
before=rd('FILES_BEFORE.json');ids={x['path']:x for x in rd('SUPPLEMENTAL_FILE_IDENTITIES.json')};groups=[];after={};issues=[]
for name,rows in before.items():
 current,reparse=paths(ROOT/name);expected={r['path'] for r in rows};allowed={str(H/'AGENTS.md')} if name=='hands' else set()
 result={'name':name,'expected_files':len(rows),'missing':sorted(expected-current),'unexpected_new_files':sorted(current-expected-allowed),'allowed_new_file_paths':sorted((current-expected)&allowed),'reparse_paths':reparse,'metadata_changes':[],'content_changes':[],'supplemental_identity_changes':[],'after_hash_count':0,'before_hash_count':len(rows)}
 hashed=[]
 for row in rows:
  p=Path(row['path'])
  if not p.is_file():continue
  s=p.stat(follow_symlinks=False)
  if (s.st_size,s.st_mtime_ns)!=(row['bytes'],row['mtime_ns']):result['metadata_changes'].append(str(p))
  ident=ids.get(str(p))
  if ident and (s.st_dev,s.st_ino,s.st_nlink)!=(ident['device'],ident['file_id'],ident['nlink']):result['supplemental_identity_changes'].append(str(p))
  # Full SHA recheck for every root experiment. Hands: all native/scientific/code inputs;
  # large retained media/images are metadata-only after (before SHA exists for every file).
  if name!='hands' or p.suffix.lower() in {'.blend','.blend1','.mid','.midi','.npz','.py','.json','.jsonl','.mjs','.js','.ps1','.casadi','.toml','.ini','.cfg','.yml','.yaml'}:
   h=sha(p);hashed.append({'path':str(p),'sha256':h,'matches_before':h==row['sha256']})
   if h!=row['sha256']:result['content_changes'].append(str(p))
 result['after_hash_count']=len(hashed)
 result['unchanged'] = not any(result[k] for k in ['missing','unexpected_new_files','reparse_paths','metadata_changes','content_changes','supplemental_identity_changes'])
 result['verification_scope']='FULL_CONTENT_SHA256' if name!='hands' else 'ALL_ORIGINAL_FILES_SIZE_MTIME; ALL_NATIVE_SCIENTIFIC_CODE_SUFFIXES_SHA256; LARGE_MEDIA_METADATA_ONLY'
 after[name]=hashed;groups.append(result);print(name,len(rows),len(hashed),'PASS' if result['unchanged'] else 'FAIL',flush=True)
save('FILES_AFTER_HASHES.json',after)
old_assets=json.loads((ROOT/'hands_cleanup_audit_r1/POST_CLEANUP_VERIFICATION.json').read_text())['six_protected_assets'];assetchecks=[]
for r in old_assets:
 h=sha(r['path']);assetchecks.append({'path':r['path'],'expected_approved_hash':r['expected_sha256'],'actual_hash':h,'matches':h==r['expected_sha256']})
legacy=[]
for row in before:
 for f in before[row]:
  n=Path(f['path']).name
  if n in {'PROTECTION_CHECK.json','PROTECTION_SCOPE_AUDIT.json','R2_PROTECTION_SCOPE_AUDIT.json','R2_PROTECTION_AUDIT.md','PROTECTION_CONCURRENCY_AUDIT.md','CLEANUP_EXECUTION_STATUS.json','APPROVED_CLEANUP_LEDGER.jsonl','CLEANUP_MANIFEST.json'}:
   h=sha(f['path']);legacy.append({'path':f['path'],'before_sha256':f['sha256'],'after_sha256':h,'unchanged':h==f['sha256']})
rootlist=[{'name':p.name,'path':str(p),'directory':p.is_dir(),'reparse':bool(p.stat(follow_symlinks=False).st_file_attributes&0x400)} for p in sorted(ROOT.iterdir())]
save('ROOT_AFTER.json',{'entries':rootlist,'only_hands_and_piano':{p['name'] for p in rootlist}=={'hands','piano'},'required_cleanup_complete':False})
save('VERIFICATION_RESULTS.json',{'time_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'task':'HANDS_DIRECTORY_STRUCTURE_CORRECTION_R1','separate_from_R3_research':True,'groups':groups,'all_checked_unchanged':all(x['unchanged'] for x in groups),'six_approved_assets':assetchecks,'approved_assets_all_same':all(x['matches'] for x in assetchecks),'historical_records':legacy,'historical_records_all_unchanged':all(x['unchanged'] for x in legacy),'migrated_directories':0,'historical_protection_FAIL_reset':False,'piano_mutating_operations':[],'global_piano_hash_qualification':'NOT_CLAIMED; active independent task. This task only read references there.','R3_wrong_root_exists':(ROOT/'hands_contact_execution_foundation_r3').exists(),'R3_correct_target':str(H/'hands_contact_execution_foundation_r3'),'R3_research_executed':False,'root_only_hands_piano':False,'status':'AUDIT_COMPLETE_MIGRATION_PENDING_HUMAN_REVIEW','windows_DirEntry_identity_limitation':'FILES_BEFORE inode/device/nlink zero values are not identity proof. Valid Path.stat supplementary identities separately verified for 17 experiment trees.'})
assert all(x['unchanged'] for x in groups)
assert all(x['matches'] for x in assetchecks)
assert all(x['unchanged'] for x in legacy)
print('VERIFIED_STOP_HUMAN_REVIEW',flush=True)
