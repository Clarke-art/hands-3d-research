import sys
sys.dont_write_bytecode=True
import os,json,hashlib,time,ctypes,collections,shutil,argparse
from pathlib import Path
from ctypes import wintypes as W
R=Path(r'<HANDS_ROOT>');O=Path(r'<HANDS_ROOT>_cleanup_audit_r1')
LOCK='d1e33316b66c254a9ba08acfb85bb9af79754766e1c99ab8abe1dd059f2503b7'
TASK='HANDS_WORKSPACE_DEEP_CLEANUP_EXECUTION_R1';G=1073741824
parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['prepare','execute','verify']);args=parser.parse_args()
def now():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as x:
  while b:=x.read(4*1024*1024):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(n,d):
 target=O/n;tmp=O/(n+'.writing');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8');os.replace(tmp,target)
def note(n,t):(O/n).write_text(t,encoding='utf8')
def meta(s):return {'size':s.st_size,'mtime_ns':s.st_mtime_ns,'device':s.st_dev,'file_id':s.st_ino,'nlink':s.st_nlink,'attributes':s.st_file_attributes}
def scan():
 files={};dirs={};issues=[];stack=[R]
 while stack:
  d=stack.pop()
  try:
   ds=os.stat(d,follow_symlinks=False)
   if ds.st_file_attributes&0x400:issues.append({'type':'reparse_directory','path':str(d)});continue
   dirs[str(d)]=meta(ds)
   for e in os.scandir(d):
    s=os.stat(e.path,follow_symlinks=False)
    if s.st_file_attributes&0x400:issues.append({'type':'reparse','path':e.path});continue
    if s.st_file_attributes&0x10:stack.append(Path(e.path));continue
    files[e.path]=meta(s)
    if s.st_nlink!=1:issues.append({'type':'hardlink','path':e.path,'nlink':s.st_nlink})
  except OSError as ex:issues.append({'type':'scan_error','path':str(d),'error':str(ex)})
 return files,dirs,issues
# Exact Windows handle identity and no-follow deletion. Only FileDispositionInfo is mutating.
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.CreateFileW.argtypes=[W.LPCWSTR,W.DWORD,W.DWORD,W.LPVOID,W.DWORD,W.DWORD,W.HANDLE];k.CreateFileW.restype=W.HANDLE
k.CloseHandle.argtypes=[W.HANDLE];k.CloseHandle.restype=W.BOOL
k.GetFileInformationByHandleEx.argtypes=[W.HANDLE,ctypes.c_int,W.LPVOID,W.DWORD];k.GetFileInformationByHandleEx.restype=W.BOOL
k.SetFileInformationByHandle.argtypes=[W.HANDLE,ctypes.c_int,W.LPVOID,W.DWORD];k.SetFileInformationByHandle.restype=W.BOOL
k.ReadFile.argtypes=[W.HANDLE,W.LPVOID,W.DWORD,ctypes.POINTER(W.DWORD),W.LPVOID];k.ReadFile.restype=W.BOOL
class IDINFO(ctypes.Structure):_fields_=[('volume',ctypes.c_ulonglong),('id',ctypes.c_ubyte*16)]
class BASIC(ctypes.Structure):_fields_=[('creation',ctypes.c_longlong),('access',ctypes.c_longlong),('write',ctypes.c_longlong),('change',ctypes.c_longlong),('attrs',W.DWORD)]
class STANDARD(ctypes.Structure):_fields_=[('allocated',ctypes.c_longlong),('length',ctypes.c_longlong),('links',W.DWORD),('pending',W.BOOLEAN),('directory',W.BOOLEAN)]
class DISPOSE(ctypes.Structure):_fields_=[('delete',W.BOOL)]
def info(h,cls,typ):
 x=typ()
 if not k.GetFileInformationByHandleEx(h,cls,ctypes.byref(x),ctypes.sizeof(x)):raise ctypes.WinError(ctypes.get_last_error())
 return x
def openhandle(p,directory=False):
 # No write or delete sharing for files: same inode cannot change while logged/deleted.
 h=k.CreateFileW(str(p),0x80 if directory else (0x10000|0x80|0x80000000),3 if directory else 1,None,3,0x00200000|(0x02000000 if directory else 0),None)
 if h==ctypes.c_void_p(-1).value:raise ctypes.WinError(ctypes.get_last_error())
 return h
def hmeta(h):
 i=info(h,18,IDINFO);b=info(h,0,BASIC);s=info(h,1,STANDARD)
 return {'size':s.length,'mtime_ns':(b.write-116444736000000000)*100,'device':i.volume,'file_id':int.from_bytes(bytes(i.id),'little'),'nlink':s.links,'attributes':b.attrs,'directory':bool(s.directory),'delete_pending':bool(s.pending),'allocated_bytes':s.allocated}
def hsha(h):
 hsh=hashlib.sha256();buf=ctypes.create_string_buffer(1048576);got=W.DWORD()
 while True:
  if not k.ReadFile(h,buf,len(buf),ctypes.byref(got),None):raise ctypes.WinError(ctypes.get_last_error())
  if not got.value:break
  hsh.update(buf.raw[:got.value])
 return hsh.hexdigest()
def same(a,b):return all(a[k]==b[k] for k in ['size','mtime_ns','device','file_id','nlink'])
def expected(f):return {'size':f['expected_bytes'],'mtime_ns':f['expected_mtime_ns'],'device':f['expected_device'],'file_id':f['expected_file_id'],'nlink':f['expected_nlink']}
M=read(O/'CLEANUP_MANIFEST.json');F=[json.loads(x) for x in (O/'files.jsonl').read_text(encoding='utf8').splitlines()];B={f['path']:f for f in F};C=[json.loads(x) for x in (O/'FILE_CLASSIFICATIONS.jsonl').read_text(encoding='utf8').splitlines()]
selected=[e for e in M['entries'] if e['classification']=='DELETE_CANDIDATE' and e['plan'] in ['conservative','deep']];members=[dict(f,entry_id=e['id']) for e in selected for f in e['members']];targets={f['path'] for f in members};ledger=O/'APPROVED_CLEANUP_LEDGER.jsonl'
def append(ev):
 with ledger.open('a',encoding='utf8',newline='\n') as x:x.write(json.dumps({'task':TASK,'time_utc':now(),**ev},ensure_ascii=False)+'\n');x.flush();os.fsync(x.fileno())
def checklocked():
 assert sha(O/'CLEANUP_MANIFEST.json')==LOCK,'Manifest SHA differs from Human authorization'
 assert sha(O/'files.jsonl')==M['baseline_inventory_sha256'],'Baseline hash mismatch'
 assert (len(selected),len(members),sum(f['expected_bytes'] for f in members),len(M['protected_code_hashes']),len(M['protected_assets']))==(339,18409,13548637683,2186,6),'Authorized counts differ'
 assert len(targets)==len(members),'Duplicate deletion member'
 byclass={x['path']:x['classification'] for x in C}
 for f in members:
  p=Path(f['path']);assert p.is_absolute() and p.resolve()==p and p.resolve().is_relative_to(R.resolve()),'Member normalization escaped root'
  assert byclass[f['path']]=='DELETE_CANDIDATE','Overlap with protected classification'
  assert same(expected(f),B[f['path']]),'Member identity differs from baseline'
  assert B[f['path']]['nlink']==1,'Hardlinked baseline member'
 for p in [R/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/_frames'/v/'0024.png' for v in ['OVERHEAD','SIDE_OBLIQUE']]:assert str(p) not in targets and p.is_file(),'Missing special poster'
 frame_entries=[e for e in selected if e['path']==str(R/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/_frames')];assert len(frame_entries)==1 and len(frame_entries[0]['members'])==1069,'C1 exact exception count differs'
 for t in ['minuet_stage_c_lightweight_animation_poc_r1','piano_pedagogical_motion_refinement_r1']:
  pref=str(R/'audits'/t/'_frames')+os.sep;assert not any(p.startswith(pref) for p in targets),'Protected teaching frames selected'
checklocked()
if args.phase=='prepare':
 if ledger.exists():raise RuntimeError('Execution ledger already exists; stop instead of duplicate execution')
 append({'event':'HUMAN_AUTHORIZATION','manifest_sha256':LOCK,'classification':'DELETE_CANDIDATE','plans':['conservative','deep'],'authorized_entries':339,'authorized_files':18409,'authorized_bytes':13548637683,'audit_manifest_human_approval_received_preserved':False,'approval_source':'Explicit Human message in this chat: HANDS_WORKSPACE_DEEP_CLEANUP_EXECUTION_R1','successful_deletions':0})
 issues=[]
 try:
  pf=read(O/'PREFLIGHT_DEEP_RESULT.json');assert pf['snapshot_checks_pass'] and pf['selected_entries']==339 and pf['selected_bytes']==13548637683,'Existing preflight failed'
  current,dirs,errs=scan();issues+=errs
  for p,s in current.items():
   if p not in B:issues.append({'type':'new_file','path':p})
   elif not same(s,B[p]):issues.append({'type':'file_changed','path':p})
  for p in set(B)-set(current):issues.append({'type':'missing_file','path':p})
  db={x['path']:x for x in read(O/'directories.json')}
  if set(db)!=set(dirs):issues.append({'type':'directory_members_changed','added':list(set(dirs)-set(db)),'missing':list(set(db)-set(dirs))})
  for p,d in dirs.items():
   if p in db and d['mtime_ns']!=db[p]['mtime_ns']:issues.append({'type':'directory_mtime_changed','path':p})
  # All exact candidates must be deletable without touching attributes; verify Windows handle identities read-only.
  for ix,f in enumerate(members):
   h=openhandle(f['path'])
   try:
    s=hmeta(h);assert same(s,expected(f)) and not s['directory'] and not s['delete_pending'] and not (s['attributes']&0x401),f'Handle identity/access mismatch {f["path"]}'
   finally:k.CloseHandle(h)
   if ix and ix%4000==0:print('READ_ONLY_DELETE_ACCESS_CHECK',ix,flush=True)
  # No new source dependency: all 2,186 sources match locked hashes; retained review pages and resources also inventoried.
  protected={a['path']:a['expected_sha256'] for a in M['protected_assets']};protected.update({x['path']:x['sha256'] for x in M['protected_code_hashes']})
  for p,s in protected.items():assert sha(p)==s,f'Protected SHA mismatch {p}'
  retained={}
  for f in F:
   if f['path'] not in targets and (f['extension'] in {'.blend','.npz','.mid','.wav','.mp4','.html','.cjs','.js','.mjs','.ps1'} or (f['extension']=='.json' and any(x in f['relative'] for x in ['PERFORMANCE_TIMELINE','SCENE_MANIFEST','PRODUCT_BASELINE','STATIC_SCENE','SOLVED_STATIC','CONTACT_MARKERS','ROLE_PLAN','POLICY','AUDIO_INTEGRATION']))):retained[f['path']]=sha(f['path'])
  save('RETAINED_ASSET_HASHES_BEFORE.json',retained)
  # Every existing static HTML reference must stay; dynamic teaching frames are checked exhaustively.
  idx=read(O/'reference_index.json');static=[h for h in idx['html_references'] if h['exists']]
  assert not any(h['resolved'] in targets for h in static),'A retained HTML resource is selected'
  assert all(Path(h['resolved']).is_file() for h in static),'Missing existing HTML resource'
  frames={}
  for t in ['minuet_stage_c_lightweight_animation_poc_r1','piano_pedagogical_motion_refinement_r1']:
   for view in ['OVERHEAD','TEACHING','SIDE_OBLIQUE']:
    for i in range(357):
     p=R/'audits'/t/'_frames'/view/f'{i:04d}.png';assert p.is_file() and str(p) not in targets,'Dynamic frame unavailable';frames[str(p)]=sha(p)
  save('TEACHING_FRAME_HASHES_BEFORE.json',frames)
  save('EXECUTION_PREFLIGHT_SNAPSHOT.json',{'files':current,'directories':dirs,'checked_utc':now()})
 except Exception as ex:issues.append({'type':'preflight_exception','error':repr(ex)})
 result={'task':TASK,'manifest_sha256':LOCK,'preflight_pass':not issues,'checked_utc':now(),'issues':issues,'authorized_entries':339,'authorized_files':18409,'authorized_bytes':13548637683,'protected_source_count':2186,'protected_asset_count':6,'actual_deletions':0,'static_reference_check':'Existing static review resources excluded from targets; dynamic teaching frames exhaustively protected','directory_action':'No directories will be deleted; empty directory skeletons retained'}
 save('EXECUTION_PREFLIGHT_RESULT.json',result)
 append({'event':'PREFLIGHT_RESULT','pass':not issues,'issues':issues,'deleted_files':0})
 save('CLEANUP_EXECUTION_STATUS.json',{'task':TASK,'status':'PREFLIGHT_PASS_READY' if not issues else 'FAIL_CLOSED_NO_DELETE','manifest_sha256':LOCK,'deleted_files':0,'deleted_logical_bytes':0,'remaining_files':18409,'issues':issues})
 note('CLEANUP_PREFLIGHT_RESULT.md','# 深度清理执行 R1：安全预检\n\n'+('**PASS**' if not issues else '**FAIL_CLOSED_NO_DELETE**')+'。Manifest SHA-256 `'+LOCK+'`；基线哈希与授权339项/18409文件/13548637683 bytes完全一致。\n\n全量文件与目录成员/mtime检查、路径规范化/越界检查、reparse/硬链接检查、所有成员Windows句柄身份及删除访问权限检查、6项保护资产与2186源码SHA检查、分类无交叉检查均已执行。Stage C R1的1069个候选成员之外两张0024.png保留；两套教学帧每视角357帧全部排除。\n\n现有全部源码哈希一致，审核页面与资源仍与库存一致，没有检测到新增阻断依赖。动态/外部调用不通过启动研发任务验证；现有明确的HTML动态帧保留。原有全文件历史验证会有获批缓存缺失，仅以实际成功删除账本作精确例外。\n\n目录不删除，避免扩大范围。此报告生成时实际删除0。\n\n异常：'+json.dumps(issues,ensure_ascii=False)+'\n')
 print(json.dumps(result,ensure_ascii=False),flush=True);sys.exit(0 if not issues else 2)
if args.phase=='execute':
 assert ledger.exists(),'Missing authorization ledger'
 pf=read(O/'EXECUTION_PREFLIGHT_RESULT.json');assert pf['preflight_pass'] and pf['manifest_sha256']==LOCK,'Supplementary preflight failed'
 status=read(O/'CLEANUP_EXECUTION_STATUS.json');assert status['status']=='PREFLIGHT_PASS_READY' and status['deleted_files']==0,'Not pristine execution state'
 # Reconfirm entire tree immediately before the first deletion, not only each target.
 pre=read(O/'EXECUTION_PREFLIGHT_SNAPSHOT.json');current,dirs,issues=scan()
 for p,s in current.items():
  if p not in pre['files'] or not same(s,pre['files'][p]):issues.append({'type':'changed_after_preflight','path':p})
 if set(current)!=set(pre['files']):issues.append({'type':'file_members_changed_after_preflight'})
 if set(dirs)!=set(pre['directories']):issues.append({'type':'directory_members_changed_after_preflight'})
 for p,s in dirs.items():
  if p in pre['directories'] and not same(s,pre['directories'][p]):issues.append({'type':'directory_changed_after_preflight','path':p})
 if issues:
  save('CLEANUP_EXECUTION_STATUS.json',dict(status,status='FAIL_CLOSED_NO_DELETE',issues=issues));append({'event':'EXECUTION_ABORT_BEFORE_DELETE','issues':issues,'remaining_unexecuted':[f['path'] for f in members]});print(json.dumps(issues,ensure_ascii=False));sys.exit(2)
 before=shutil.disk_usage(R).free;save('DISK_SPACE_BEFORE.json',{'free_bytes':before,'measured_utc':now(),'volume':'D:'})
 append({'event':'EXECUTION_START','disk_free_before_bytes':before,'directory_deletions_permitted':False})
 handles={};done=[];total=0;failure=None
 try:
  # Keep relevant ancestors open without delete sharing, blocking rename/replacement while handling selected members.
  parents=set()
  for f in members:
   p=Path(f['path']).parent
   while True:
    parents.add(str(p))
    if p==R:break
    p=p.parent
  for p in sorted(parents,key=lambda x:len(Path(x).parts)):
   h=openhandle(p,True);s=hmeta(h)
   if s['attributes']&0x400 or not same(s,pre['directories'][p]):k.CloseHandle(h);raise RuntimeError('Ancestor changed '+p)
   handles[p]=h
  for ix,f in enumerate(members):
   h=None;intent=False
   try:
    # Parent chain tags checked again for every deletion. Final file opened with OPEN_REPARSE_POINT.
    p=Path(f['path']).parent
    while True:
     ds=hmeta(handles[str(p)])
     assert not ds['attributes']&0x400 and ds['file_id']==pre['directories'][str(p)]['file_id'] and ds['device']==pre['directories'][str(p)]['device'],'Ancestor reparse/identity changed'
     if p==R:break
     p=p.parent
    h=openhandle(f['path']);s=hmeta(h);assert same(s,expected(f)) and not s['directory'] and not s['delete_pending'] and not s['attributes']&0x400,'Target identity changed'
    if f.get('expected_sha256'):assert hsha(h)==f['expected_sha256'],'Target SHA changed'
    append({'event':'PRE_DELETE','entry_id':f['entry_id'],'path':f['path'],'original_identity':s,'expected_sha256':f.get('expected_sha256'),'preflight_pass':True,'immediate_identity_check':'PASS','immediate_hash_check':'PASS' if f.get('expected_sha256') else 'NO_HASH_IN_LOCKED_MANIFEST','result':'NOT_YET_DELETED','cumulative_successful_files':len(done),'cumulative_deleted_logical_bytes':total});intent=True
    disposal=DISPOSE(True)
    if not k.SetFileInformationByHandle(h,4,ctypes.byref(disposal),ctypes.sizeof(disposal)):raise ctypes.WinError(ctypes.get_last_error())
    if not k.CloseHandle(h):raise ctypes.WinError(ctypes.get_last_error())
    h=None
    try:os.stat(f['path'],follow_symlinks=False)
    except FileNotFoundError:pass
    else:raise RuntimeError('Path still exists after delete, cannot declare success')
    done.append(f['path']);total+=f['expected_bytes']
    append({'event':'DELETE_RESULT','entry_id':f['entry_id'],'path':f['path'],'result':'SUCCESS','original_bytes':f['expected_bytes'],'original_file_id':f['expected_file_id'],'expected_sha256':f.get('expected_sha256'),'cumulative_successful_files':len(done),'cumulative_deleted_logical_bytes':total})
    if len(done)%500==0:
     save('CLEANUP_EXECUTION_STATUS.json',{'task':TASK,'status':'EXECUTING','manifest_sha256':LOCK,'deleted_files':len(done),'deleted_logical_bytes':total,'remaining_files':len(members)-len(done),'issues':[]});print('DELETED',len(done),'LOGICAL_BYTES',total,flush=True)
   except Exception as ex:
    failure={'path':f['path'],'entry_id':f['entry_id'],'error':repr(ex),'pre_delete_intent_saved':intent};append({'event':'DELETE_RESULT','path':f['path'],'entry_id':f['entry_id'],'result':'FAILED_OR_UNCONFIRMED','error':repr(ex),'cumulative_successful_files':len(done),'cumulative_deleted_logical_bytes':total});break
   finally:
    if h is not None:k.CloseHandle(h)
 except Exception as ex:failure={'error':repr(ex),'phase':'ancestor_guards'}
 finally:
  for h in handles.values():k.CloseHandle(h)
 done_set=set(done);remaining=[f['path'] for f in members if f['path'] not in done_set]
 result={'task':TASK,'status':'PARTIAL_EXECUTION_STOP' if failure and done else ('FAIL_CLOSED_NO_DELETE' if failure else 'DELETE_COMPLETE_PENDING_ACCEPTANCE'),'manifest_sha256':LOCK,'deleted_files':len(done),'deleted_logical_bytes':total,'remaining_files':len(remaining),'remaining_unexecuted_paths':remaining,'issues':[failure] if failure else [],'directories_deleted':0,'disk_free_before_bytes':before,'stopped_utc':now(),'rollback_available':False,'next_step':'Read-only acceptance; no further cleanup'}
 save('CLEANUP_EXECUTION_STATUS.json',result);append({'event':'EXECUTION_STOP' if failure else 'DELETION_PHASE_COMPLETE',**result});print(json.dumps({k:v for k,v in result.items() if k!='remaining_unexecuted_paths'},ensure_ascii=False),flush=True);sys.exit(2 if failure else 0)
if args.phase=='verify':
 status=read(O/'CLEANUP_EXECUTION_STATUS.json');events=[json.loads(x) for x in ledger.read_text(encoding='utf8').splitlines()];success={x['path']:x for x in events if x['event']=='DELETE_RESULT' and x['result']=='SUCCESS'};current,dirs,issues=scan();missing=set(B)-set(current)
 if missing!=set(success):issues.append({'type':'actual_missing_not_exact_success_ledger','unexpected_missing':sorted(missing-set(success)),'success_paths_still_present':sorted(set(success)-missing)})
 if set(current)-set(B):issues.append({'type':'unexpected_new_files','paths':sorted(set(current)-set(B))})
 for p,s in current.items():
  if p in B and not same(s,B[p]):issues.append({'type':'retained_metadata_changed','path':p})
 assetchecks=[]
 for a in M['protected_assets']:
  h=sha(a['path']);assetchecks.append({'path':a['path'],'role':a['role'],'actual_sha256':h,'expected_sha256':a['expected_sha256'],'pass':h==a['expected_sha256']})
  if h!=a['expected_sha256']:issues.append({'type':'protected_asset_hash_mismatch','path':a['path']})
 sources=0
 for x in M['protected_code_hashes']:
  if sha(x['path'])!=x['sha256']:issues.append({'type':'protected_source_hash_mismatch','path':x['path']})
  else:sources+=1
 retained=read(O/'RETAINED_ASSET_HASHES_BEFORE.json');bad=[]
 for p,h in retained.items():
  if sha(p)!=h:bad.append(p)
 if bad:issues.append({'type':'retained_asset_hash_mismatch','paths':bad})
 framehashes=read(O/'TEACHING_FRAME_HASHES_BEFORE.json');badframes=[]
 for p,h in framehashes.items():
  if sha(p)!=h:badframes.append(p)
 if badframes:issues.append({'type':'teaching_frame_hash_mismatch','paths':badframes})
 idx=read(O/'reference_index.json');missingrefs=[h for h in idx['html_references'] if h['exists'] and not Path(h['resolved']).is_file()]
 if missingrefs:issues.append({'type':'retained_static_review_reference_missing','references':missingrefs})
 logical=sum(x['size'] for x in current.values());freed=sum(B[p]['size'] for p in missing);diskafter=shutil.disk_usage(R).free
 if logical+freed!=sum(f['size'] for f in F):issues.append({'type':'logical_size_sum_disagrees'})
 result={'task':TASK,'status_before_acceptance':status['status'],'verified_utc':now(),'issues':issues,'post_file_count':len(current),'post_directory_count':len(dirs),'post_logical_bytes':logical,'actual_missing_files':len(missing),'actual_logical_reduction_bytes':freed,'ledger_success_files':len(success),'ledger_success_bytes':sum(e['original_bytes'] for e in success.values()),'six_protected_assets':assetchecks,'protected_sources_pass':sources,'protected_sources_expected':2186,'retained_asset_hashes_checked':len(retained),'teaching_frames_hashes_checked':len(framehashes),'static_review_existing_references_checked':sum(h['exists'] for h in idx['html_references']),'missing_static_review_refs':len(missingrefs),'disk_free_before_bytes':status.get('disk_free_before_bytes'),'disk_free_after_bytes':diskafter,'disk_free_increase_bytes':diskafter-status.get('disk_free_before_bytes',diskafter),'manifest_hash_still_locked':sha(O/'CLEANUP_MANIFEST.json')==LOCK,'baseline_hash_still_locked':sha(O/'files.jsonl')==M['baseline_inventory_sha256'],'all_expected_missing_are_exact_success_exceptions':missing==set(success),'remaining_selected_files':len(targets & set(current)),'browser_function_check':'PENDING'}
 save('POST_CLEANUP_VERIFICATION.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ['six_protected_assets']},ensure_ascii=False),flush=True)

