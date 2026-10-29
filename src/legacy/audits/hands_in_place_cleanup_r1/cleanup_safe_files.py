import sys
sys.dont_write_bytecode=True
import os,json,csv,hashlib,ctypes,importlib.util,collections,time,tarfile
from pathlib import Path
H=Path(r'<HANDS_ROOT>');O=Path(__file__).parent
assert O==H/'audits/hands_in_place_cleanup_r1' and H.resolve()==H
assert not (O/'DELETE_PLAN.csv').exists(),'One-shot execution; do not overwrite prior cleanup records'
BASE=H/'hands_fingering_inference_poc_r1';CACHE=BASE/'npm-cache/_cacache';ORT=BASE/'node_modules/onnxruntime-node';BIN=ORT/'bin/napi-v6';EXPECTED_HOST=('win32','x64')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  while b:=f.read(4*1024*1024):h.update(b)
 return h.hexdigest()
def scan():
 files={};dirs=set();issues=[];stack=[H]
 while stack:
  d=stack.pop();st=d.stat(follow_symlinks=False)
  if st.st_file_attributes&0x400:issues.append(str(d));continue
  dirs.add(str(d))
  for e in os.scandir(d):
   p=Path(e.path)
   if p==O:continue
   st=e.stat(follow_symlinks=False)
   if st.st_file_attributes&0x400:issues.append(str(p));continue
   if st.st_file_attributes&0x10:stack.append(p)
   else:
    st=p.stat(follow_symlinks=False);files[str(p)]={'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'file_id':st.st_ino,'device':st.st_dev,'nlink':st.st_nlink}
 return files,dirs,issues
def save(n,d):
 with (O/n).open('w',encoding='utf8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
def safe(p):
 p=Path(p)
 assert p.is_absolute() and p.is_relative_to(H) and not p.is_relative_to(O) and '..' not in p.parts,str(p)
 assert p.resolve()==p,str(p)
 cur=p
 while cur!=H.parent:
  assert not cur.stat(follow_symlinks=False).st_file_attributes&0x400,str(cur)
  if cur==H:break
  cur=cur.parent
 return p
before,dirs_before,issues=scan();assert not issues,issues
binding=(ORT/'dist/binding.js').read_text();package=json.loads((ORT/'package.json').read_text());assert package['name']=='onnxruntime-node' and package['version']=='1.23.2'
assert '../bin/napi-v6/${process.platform}/${process.arch}/onnxruntime_binding.node' in binding
assert os.name=='nt' and ctypes.sizeof(ctypes.c_void_p)==8
host_files=[Path(p) for p in before if Path(p).is_relative_to(BIN/'win32/x64')];assert len(host_files)==5
# Largest cached package has a complete installed authoritative copy, verified before pruning foreign builds.
cached=[Path(p) for p in before if Path(p).is_relative_to(CACHE)];largest=max(cached,key=lambda p:before[str(p)]['bytes']);matched=[]
with tarfile.open(largest,'r:gz') as archive:
 info=json.load(archive.extractfile('package/package.json'));assert (info['name'],info['version'])==('onnxruntime-node','1.23.2')
 for member in archive:
  if not member.isfile():continue
  rel=Path(*Path(member.name).parts[1:]);assert '..' not in rel.parts and not rel.is_absolute();target=ORT/rel;safe(target)
  assert target.is_file(),str(target)
  expected=hashlib.sha256(archive.extractfile(member).read()).hexdigest();assert sha(target)==expected,str(target);matched.append(str(target))
assert len(matched)==44
plan=[]
for name,m in before.items():
 p=Path(name);reason=None;category=None
 if p.suffix=='.pyc' and '__pycache__' in p.parts:
  source=Path(importlib.util.source_from_cache(name))
  if source.is_file():category='PYTHON_REGENERABLE_CACHE';reason='Bytecode only; existing .py source retained: '+str(source)
 elif p.is_relative_to(CACHE):category='NPM_DOWNLOAD_CACHE';reason='npm _cacache; no project runtime path reads. Full installed package copy verified (largest cache: 44/44 files); installed sources, Windows x64 runtime, package lock, licenses and npm logs retained'
 elif p.is_relative_to(BIN):
  parts=p.relative_to(BIN).parts
  if tuple(parts[:2])!=EXPECTED_HOST:
   assert p.suffix.lower() in ['.node','.dylib','.dll','.1'],str(p)
   category='NON_HOST_NATIVE_BUILD';reason=f'Host verified win32/x64; binding.js dispatches only process.platform/process.arch. {parts[0]}/{parts[1]} binary not usable on current host; Windows x64 five runtime files retained; source/license/version lock retained'
 if reason:
  safe(p);assert m['nlink']==1,str(p);plan.append({'path':name,'bytes':m['bytes'],'sha256':sha(p),'category':category,'basis':reason})
assert len(plan)>0 and all(Path(x['path']).is_relative_to(H) for x in plan)
delete_names={x['path'] for x in plan}
# Protect all existing native/scientific assets, original code, contracts and authorization/FAIL ledgers.
protected={}
key_ext={'.blend','.blend1','.npz','.mid','.midi','.onnx','.casadi','.py','.js','.mjs','.ts','.ps1','.jsonl'}
words=['MANIFEST','PROTECT','FROZEN','POLICY','APPROV','HUMAN','AUTHORIZ','LEDGER','STATUS','FINAL','CANDIDATE','TRAJECTORY','CONTACT_STATE','SOURCE_EVENT','SOURCE_MIDI','INPUT_BIND','RIG_PREFLIGHT','HAND_MOTION','PACKAGE-LOCK']
for name in before:
 p=Path(name)
 if name in delete_names:continue
 if p.suffix.lower() in key_ext or (p.suffix.lower()=='.json' and any(w in p.name.upper() for w in words)) or p.is_relative_to(BIN/'win32/x64'):
  protected[name]=sha(p)
approved=[]
historical=json.loads((H/'hands_cleanup_audit_r1/POST_CLEANUP_VERIFICATION.json').read_text())
for x in historical['six_protected_assets']:
 p=safe(x['path']);assert p.is_file() and sha(p)==x['expected_sha256'],str(p);approved.append({'path':str(p),'expected':x['expected_sha256']})
def aggregate(mapping):return hashlib.sha256('\n'.join(p+'\t'+mapping[p] for p in sorted(mapping)).encode()).hexdigest()
before_digest=aggregate(protected)
with (O/'DELETE_PLAN.csv').open('x',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['path','bytes','sha256','category','basis']);w.writeheader();w.writerows(plan)
print('PLAN_SAVED',len(plan),'files',sum(x['bytes'] for x in plan),'bytes; protected',len(protected),'files; piano not scanned',flush=True)
# Exact single-file, exclusive Windows handle deletion. No recursive deletion or legacy program.
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.CreateFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_void_p,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_void_p];k.CreateFileW.restype=ctypes.c_void_p
k.GetFileInformationByHandleEx.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_ulong];k.GetFileInformationByHandleEx.restype=ctypes.c_int
k.SetFileInformationByHandle.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_ulong];k.SetFileInformationByHandle.restype=ctypes.c_int
k.CloseHandle.argtypes=[ctypes.c_void_p];k.CloseHandle.restype=ctypes.c_int
k.ReadFile.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong,ctypes.POINTER(ctypes.c_ulong),ctypes.c_void_p];k.ReadFile.restype=ctypes.c_int
k.GetDiskFreeSpaceExW.argtypes=[ctypes.c_wchar_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p];k.GetDiskFreeSpaceExW.restype=ctypes.c_int
class Standard(ctypes.Structure):_fields_=[('allocation',ctypes.c_longlong),('length',ctypes.c_longlong),('links',ctypes.c_ulong),('pending',ctypes.c_ubyte),('directory',ctypes.c_ubyte)]
class Identity(ctypes.Structure):_fields_=[('volume',ctypes.c_ulonglong),('file_id',ctypes.c_ubyte*16)]
class Dispose(ctypes.Structure):_fields_=[('delete',ctypes.c_ubyte)]
def free():
 a=ctypes.c_ulonglong();b=ctypes.c_ulonglong();c=ctypes.c_ulonglong();assert k.GetDiskFreeSpaceExW(str(H),ctypes.byref(a),ctypes.byref(b),ctypes.byref(c));return c.value
def hinfo(handle,cls,kind):
 x=kind();assert k.GetFileInformationByHandleEx(handle,cls,ctypes.byref(x),ctypes.sizeof(x)),ctypes.get_last_error();return x
def hsha(handle):
 h=hashlib.sha256();buf=ctypes.create_string_buffer(1024*1024);got=ctypes.c_ulong()
 while True:
  assert k.ReadFile(handle,buf,len(buf),ctypes.byref(got),None),ctypes.get_last_error()
  if not got.value:break
  h.update(buf.raw[:got.value])
 return h.hexdigest()
done=[];skipped=[];free_before=free()
fields=['path','bytes','allocated_bytes','category','status','detail']
with (O/'DELETE_EXECUTION.csv').open('x',encoding='utf-8-sig',newline='') as log:
 writer=csv.DictWriter(log,fieldnames=fields);writer.writeheader();log.flush()
 for row in plan:
  p=safe(row['path']);saved=before[str(p)];handle=k.CreateFileW(str(p),0x80010080,0,None,3,0x00200000,None)
  if handle==ctypes.c_void_p(-1).value:
   out={'path':str(p),'bytes':row['bytes'],'allocated_bytes':0,'category':row['category'],'status':'SKIPPED_OPEN_OR_PERMISSION','detail':str(ctypes.get_last_error())};skipped.append(out);writer.writerow(out);log.flush();continue
  try:
   st=hinfo(handle,1,Standard);identity=hinfo(handle,18,Identity)
   assert not st.directory and st.links==1 and st.length==row['bytes']
   assert int.from_bytes(bytes(identity.file_id),'little')==saved['file_id'] and identity.volume==saved['device']
   assert hsha(handle)==row['sha256'],'Candidate changed; do not delete'
   out={'path':str(p),'bytes':st.length,'allocated_bytes':st.allocation,'category':row['category'],'status':'PRE_DELETE_VERIFIED','detail':'Exclusive handle, 1 link, ID/size/SHA matched; exact file only'};writer.writerow(out);log.flush()
   request=Dispose(1)
   if not k.SetFileInformationByHandle(handle,4,ctypes.byref(request),ctypes.sizeof(request)):
    out.update(status='SKIPPED_DELETE_DENIED',detail=str(ctypes.get_last_error()));skipped.append(dict(out));writer.writerow(out);log.flush();continue
  finally:k.CloseHandle(handle)
  assert not p.exists(),str(p);out.update(status='DELETED_CONFIRMED',detail='Handle closed; original path absent');done.append(dict(out));writer.writerow(out);log.flush()
  if len(done)%25==0:print('DELETED',len(done),flush=True)
free_after=free();after,dirs_after,scan_issues=scan();deleted={x['path'] for x in done}
assert set(before)-set(after)==deleted and not (set(after)-set(before)),'Unexpected project member change'
assert dirs_before==dirs_after,'Existing directory structure changed'
metadata_changes=[p for p in after if after[p]!=before[p]];assert not metadata_changes,metadata_changes[:5]
afterhash={p:sha(p) for p in protected};mismatches=[p for p,h in protected.items() if afterhash[p]!=h];assert not mismatches,mismatches
assert aggregate(afterhash)==before_digest
for x in approved:x['after']=sha(x['path']);x['pass']=x['after']==x['expected'];assert x['pass']
save('PROTECTION_CHECK.json',{'protected_file_count':len(protected),'protected_bytes':sum(before[p]['bytes'] for p in protected),'before_aggregate_SHA256':before_digest,'after_aggregate_SHA256':aggregate(afterhash),'mismatches':mismatches,'six_approved_assets':approved,'remaining_all_file_metadata_equal':True,'only_missing_are_executed_deletions':True,'existing_directories_unchanged':True,'historical_manifest_and_FAIL_content_unchanged':True,'old_manifest_path_membership_global_PASS_not_claimed':True,'piano_scan_read_write_delete_move_operations':[],'directory_relocation_operations':[],'Blender_render_or_solver_calls':0,'largest_cached_package_authority_verified_files':len(matched),'retained_windows_x64_native_files':[str(p) for p in host_files]})
topdirs=collections.Counter()
for p,m in after.items():
 rel=Path(p).relative_to(H)
 if len(rel.parts)>1:topdirs[str(Path(*rel.parts[:2])) if rel.parts[0] in ['audits','production_spec'] else rel.parts[0]]+=m['bytes']
remaining_largest=sorted(after.items(),key=lambda x:x[1]['bytes'],reverse=True)[:8]
total_before=sum(x['bytes'] for x in before.values());total_after=sum(x['bytes'] for x in after.values());logical=sum(x['bytes'] for x in done);allocated=sum(x['allocated_bytes'] for x in done)
summary={'task':'HANDS_IN_PLACE_CLEANUP_R1','status':'STOP — HUMAN REVIEW','before_original_content_bytes':total_before,'after_original_content_bytes':total_after,'deleted_files':len(done),'deleted_logical_bytes':logical,'deleted_single_link_confirmed_allocation_bytes':allocated,'reclaimed_GiB_allocation':allocated/1024**3,'drive_free_before_bytes':free_before,'drive_free_after_bytes':free_after,'observed_drive_free_difference_bytes':free_after-free_before,'drive_difference_not_solely_attributed_to_this_task':True,'skipped':skipped,'categories':dict(collections.Counter(x['category'] for x in done)),'directory_moves':0,'piano_involved':False,'audit_own_disk_bytes_not_in_original_content_totals':True,'root_path_compatibility_work':False}
save('CLEANUP_SUMMARY.json',summary)
rows='\n'.join(f"|{name}|{n/1024**3:.3f}|" for name,n in topdirs.most_common(8));lf='\n'.join(f"- `{Path(name).relative_to(H)}`：{m['bytes']/1024**2:.2f} MiB" for name,m in remaining_largest)
text=f'''# Hands 原地瘦身结果

2026-10-14。**HANDS_IN_PLACE_CLEANUP_R1 — STOP — HUMAN REVIEW。**

|项目|结果|
|---|---:|
|清理前原有内容|{total_before/1024**3:.6f} GiB（{total_before:,} bytes）|
|实际删除文件|{len(done)}|
|删除逻辑大小|{logical/1024**3:.6f} GiB|
|**实际删除释放的文件分配空间**|**{allocated/1024**3:.6f} GiB（{allocated:,} bytes）**|
|清理后原有内容|{total_after/1024**3:.6f} GiB（{total_after:,} bytes）|
|删除阶段D盘可用空间实测差|{(free_after-free_before)/1024**3:+.6f} GiB|
|未执行/删除拒绝|{len(skipped)}|

释放量按每个删除文件的 Windows FileStandardInfo.AllocationSize 实测累计：全部为单硬链接、无reparse，独占句柄核对fileID/size/SHA后精确删除，关闭句柄确认路径消失。逻辑大小、文件分配量和D盘总可用空间差独立报告；总可用空间受其他进程影响，不能全部归因本轮。没有同盘迁移、压缩或把副本体积算作释放量。清理前后原有内容总量不含本轮极小审计输出，审计占用在最终实测中另列。

实际清理：{summary['categories']}。11个Python缓存均保留对应.py源码；npm _cacache不承担运行/历史复核作用，最大下载缓存的44/44内容与完整已安装包逐SHA相同，保留npm日志、源码、license和package-lock。宿主Node已核实win32/x64，binding.js仅加载process.platform/process.arch目录，删除darwin、linux和win32/arm64的非本机打包原生产物；Windows x64五个原生运行文件原SHA保留。未来换OS/CPU需重新安装供应方包；未删除模型、指法或R3数学/几何数据。

删除前明细 `DELETE_PLAN.csv`，实际逐项句柄删除结果 `DELETE_EXECUTION.csv`。没有运行任何历史删除程序。所有原目录保持，包括空缓存/非本机目录；17个手动迁入目录没有再次移动。

保护：{len(protected):,}项原生/科学数据、原始源码、冻结合同、Human授权及历史账本在删除前后聚合SHA一致；六项已批准Rig/动画/姿态资产与批准SHA一致；所有剩余文件的size/mtime/identity不变，成员缺失严格等于删除明细。旧Manifest和历史保护FAIL内容未改写，不以本次删除重置全局资格。保护机器结果见 `PROTECTION_CHECK.json`。

## 保留的大体积内容

|目录|逻辑GiB|
|---|---:|
{rows}

最大文件：

{lf}

7.02 GiB左右PNG中包括仍被教学页面使用的逐帧资源及Human/失败复核截图，未删除；大型NPZ、CasADi函数与冻结原生payload承担轨迹/算法/失败复核，未知用途不继续深挖。许可证源ZIP保留原来源；3.06MiB的.blend1与现有.blend字节/大小不同，非已证冗余，保留。影子R2的207文件虽有权威原副本，但仍被独立复核入口和登记表直接引用，承担该轮实际执行证据，保留。未为腾空间改路径、改源码或清退历史证据。

手动迁移造成的明显问题仅登记：部分旧绝对路径仍指向上级hands_*；`O.parent/'hands'`在已迁入位置会指向hands\\hands。没有开展兼容研发或修改冻结源码，历史迁移与本轮删除分别记账。

**piano完全未参与本轮操作：未列举、扫描、读取、修改、删除或移动其文件。** 所有文件扫描/删除目标均在hands，遇reparse立即拒绝；卷空间查询仅以hands路径进行。没有创建备份或新影子，没有启动Blender、优化、动画、R3或其他研发。
'''
(O/'CLEANUP_RESULT.md').write_text(text,encoding='utf8')
print('CLEANUP_COMPLETE',json.dumps(summary,ensure_ascii=False),flush=True)
