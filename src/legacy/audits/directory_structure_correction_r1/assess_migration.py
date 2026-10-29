import sys
sys.dont_write_bytecode=True
import json,ast,re,ctypes,hashlib,collections,csv
from pathlib import Path
ROOT=Path(r'D:\codex one\3D interactive components');H=ROOT/'hands';O=Path(__file__).parent
def rd(n):return json.loads((O/n).read_text(encoding='utf8'))
def save(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  while b:=f.read(4*1024*1024):h.update(b)
 return h.hexdigest()
inventory=rd('DIRECTORY_INVENTORY.json');files=rd('FILES_BEFORE.json');names={x['name'] for x in inventory};idx=rd('REFERENCE_INDEX.json');deps={x['name']:x for x in rd('DEPENDENCY_SUMMARY.json')};protection={x['name']:x for x in rd('PROTECTION_RELATIONSHIPS.json')}
def mapped(p):
 try:parts=p.relative_to(ROOT).parts
 except ValueError:return p
 return H.joinpath(*parts) if parts[0] in names else p
# Static AST analysis only: never import/execute legacy modules or delete/solve code.
effects=[];ast_errors=[]
for name in sorted(names):
 for row in files[name]:
  p=Path(row['path'])
  if p.suffix!='.py':continue
  try:text=p.read_text(encoding='utf-8-sig');tree=ast.parse(text)
  except (UnicodeError,SyntaxError) as e:ast_errors.append({'file':str(p),'error':str(e)});continue
  for node in ast.walk(tree):
   if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Div) and isinstance(node.left,ast.Attribute) and node.left.attr=='parent' and isinstance(node.left.value,ast.Name) and node.left.value.id=='O' and isinstance(node.right,ast.Constant) and isinstance(node.right.value,str):
    rel=node.right.value;old=p.parent.parent/rel;new=mapped(p.parent).parent/rel;expected=mapped(old)
    if any(rel.startswith(k) for k in ['hands','piano']):
     effects.append({'source':str(p),'line':node.lineno,'expression':ast.get_source_segment(text,node),'kind':'layout_sensitive_parent_path','before_path':str(old),'before_exists':old.exists(),'after_all_17_moved_path':str(new),'expected_after_mapping':str(expected),'equivalent_after_all_17_moved':new==expected,'after_only_this_directory_moved_preserves_old_dependency':new==old,'runtime_executed':False})
   if isinstance(node,ast.Constant) and isinstance(node.value,str) and str(ROOT).lower() in node.value.lower():
    for n in names:
     prefix=str(ROOT/n)
     if node.value.lower().startswith(prefix.lower()):
      target=mapped(Path(node.value))
      if target!=Path(node.value):effects.append({'source':str(p),'line':node.lineno,'expression':ast.get_source_segment(text,node),'kind':'unchanged_absolute_literal','before_path':node.value,'after_all_17_moved_path':node.value,'expected_after_mapping':str(target),'equivalent_after_all_17_moved':False,'runtime_executed':False})
save('STATIC_PATH_IMPACT.json',{'method':'Whitelisted AST pattern inspection, no code execution. Common O.parent / string and absolute string constants. Not a complete arbitrary Python/CWD/dynamic/native path analysis.','effects':effects,'ast_errors':ast_errors})
k=ctypes.WinDLL('kernel32',use_last_error=True);k.GetCompressedFileSizeW.argtypes=[ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_ulong)];k.GetCompressedFileSizeW.restype=ctypes.c_ulong
k.CreateFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_void_p,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_void_p];k.CreateFileW.restype=ctypes.c_void_p
k.GetFileInformationByHandleEx.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_ulong];k.GetFileInformationByHandleEx.restype=ctypes.c_int
k.CloseHandle.argtypes=[ctypes.c_void_p];k.CloseHandle.restype=ctypes.c_int
class Standard(ctypes.Structure):_fields_=[('allocation',ctypes.c_longlong),('length',ctypes.c_longlong),('links',ctypes.c_ulong),('pending',ctypes.c_ubyte),('directory',ctypes.c_ubyte)]
identities=[]
for x in inventory:
 seen=set();allocated=0;compressed_reported=0;errs=[];links=0
 for r in files[x['name']]:
  st=Path(r['path']).stat(follow_symlinks=False)
  assert (st.st_size,st.st_mtime_ns)==(r['bytes'],r['mtime_ns']),r['path']
  assert not st.st_file_attributes&0x400,r['path']
  identities.append({'path':r['path'],'device':st.st_dev,'file_id':st.st_ino,'nlink':st.st_nlink,'mtime_ns':st.st_mtime_ns,'bytes':st.st_size,'role':'Supplemental identity snapshot; original before rows used Windows DirEntry.stat whose inode/device/nlink are documented unavailable (0). Original hash/size/time rows retained.'})
  links+=st.st_nlink>1
  key=(st.st_dev,st.st_ino) if st.st_ino else ('unavailable',r['path'])
  if key in seen:continue
  seen.add(key);hi=ctypes.c_ulong();ctypes.set_last_error(0);lo=k.GetCompressedFileSizeW(r['path'],ctypes.byref(hi));err=ctypes.get_last_error()
  if lo==0xffffffff and err:errs.append({'path':r['path'],'error':err})
  else:compressed_reported+=(hi.value<<32)|lo
  handle=k.CreateFileW(r['path'],0x80,7,None,3,0x00200000,None)
  if handle==ctypes.c_void_p(-1).value:errs.append({'path':r['path'],'error':ctypes.get_last_error(),'operation':'read attributes handle'});continue
  try:
   info=Standard()
   if not k.GetFileInformationByHandleEx(handle,1,ctypes.byref(info),ctypes.sizeof(info)):errs.append({'path':r['path'],'error':ctypes.get_last_error(),'operation':'FileStandardInfo'})
   else:allocated+=info.allocation
  finally:k.CloseHandle(handle)
 x.update(hardlinked_files=links,allocated_bytes_unique_file_id=allocated,compressed_file_size_reported_bytes=compressed_reported,allocation_errors=errs,space_definition='Logical bytes plus Windows FILE_STANDARD_INFO.AllocationSize and GetCompressedFileSizeW separately; deduplicated within directory by valid Path.stat volume/file ID. Directory/MFT metadata not included; no drive space release claim.')
save('SUPPLEMENTAL_FILE_IDENTITIES.json',identities)
save('DIRECTORY_SPACE.json',inventory)
purpose={
'hands_c01_anatomy_preparation_audit_r1':'C01 手型/解剖及 E5 准备审计，B2 静态起点与参考族来源',
'hands_c01_g4_e5_natural_motion_bridge_r2':'G4→E5 自然参考族端点和连续候选失败现场',
'hands_c01_g4_e5_skin_safe_bridge_r1':'G4→E5 面级皮肤安全静态修复与诊断场景',
'hands_c01_s1_constrained_solver_feasibility_r1':'S1 显式约束求解器可行性、合格静态点及失败尝试',
'hands_c01_whole_hand_motion_feasibility_r1':'C01 全手运动实验、原生候选场景、blender_utils 共用依赖',
'hands_cleanup_audit_r1':'已执行的 Hands 历史清理审计、锁定 Manifest、批准与删除账本',
'hands_contact_constrained_trajectory_planning_r1':'接触约束轨迹规划、CasADi 依赖及冻结符号皮肤函数',
'hands_contact_derivative_feasibility_recovery_r1':'接触导数、分支和局部可行性恢复审计及复现依赖',
'hands_contact_junction_compatibility_r1':'换音边界接触兼容性与共同构型证据',
'hands_contact_state_motion_planner_comparison_r1':'接触状态/离散规划器比较、原琴键 Action 与 MIDI 基准',
'hands_early_hand_preparation_entry_reachability_r1':'早期准备及完整入口可达性 R1，250ms 采样前缀与失败轨迹',
'hands_fingering_inference_poc_r1':'Lumikey 指法推理、ONNX/运行依赖、原输入绑定',
'hands_long_context_corridor_ik_bridge_r2':'高层走廊→IK R2 的 PARTIAL 结果、导数阻碍与失败曲线',
'hands_long_context_hand_motion_architecture_r1':'长上下文架构 A、HandMotionIntent、静态清障与先验来源审计',
'hands_sequence_fingering_planning_r1':'PianoPlayer 序列规划、C01 指法候选及源事件身份绑定',
'hands_skin_collision_static_feasibility_r1':'真实完整皮肤/键体检测及静态可行性原始模型和几何实现',
'hands_time_coupled_contact_recovery_r1':'时间耦合接触恢复，2.083ms 局部诊断证据及外部入口限制'}
rows=[]
for x in inventory:
 n=x['name'];d=deps[n];pr=protection[n]
 own=[a for a in effects if Path(a['source']).relative_to(ROOT).parts[0]==n and not a['equivalent_after_all_17_moved']]
 inc=[a for a in idx if a['owner']!=n and a.get('potential_runtime_source') and n in a.get('targets',[])]
 incoming=[{'source':a['file'],'examples':[e for e in a['examples'] if e['target']==n]} for a in inc]
 reasons=[]
 if own:reasons.append('现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用')
 if inc:reasons.append('存在外部源码的历史复现/后续输入引用；调用方路径与保护绑定尚未迁移闭合')
 if pr['entries']:reasons.append('历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL')
 if x['destination_conflict']:reasons.append('目标路径冲突，禁止覆盖')
 if x['reparse_or_scan_issues'] or x['allocation_errors']:reasons.append('文件系统检查存在未闭合问题')
 assert reasons,'Potentially safe directory requires separate assessment, not blanket defer: '+n
 documents=sorted((ROOT/n).glob('*.md'));preferred=[p for p in documents if any(w in p.name.upper() for w in ['FINAL_RECOMMENDATION','FINAL_CLEANUP_REPORT','FINAL_REPORT'])]
 row={**x,'purpose':purpose[n],'purpose_source_documents':[str(p) for p in (preferred or documents)[:2]],'observed_running_task':'未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务','retained_use':'历史审计复核，锁定账本与批准缺失例外' if n=='hands_cleanup_audit_r1' else ('后续技术输入/历史复现源码引用仍存在' if inc else 'R2 当前交付及拟议 R3 输入；未发现外部源码直接引用，但本目录父层级依赖已失效预测'),'incoming_potential_runtime_source_count':len(inc),'incoming_runtime_evidence':incoming,'own_blocking_static_path_evidence':own,'latest_R2_protection_entries':pr['entries'],'latest_R2_protected_same_hash':pr['same_hash'],'historical_path_bound_protection_record_count':len(pr['protection_reference_records']),'decision':'PENDING_HUMAN_APPROVAL','migrated':False,'reasons':reasons,'migration_reproducibility':'NOT_VALIDATED; identified deterministic path breakages; no legacy solver/cleanup/Blender executed','freeze_interpretation':'Manifest membership alone is not proof of an absolute ban on relocation; actual path-sensitive code and unresolved validator/contract mappings independently block safe relocation.'}
 rows.append(row)
save('MIGRATION_DECISIONS.json',rows)
save('PATH_MAPPING.json',{'status':'PROPOSED_ONLY_NO_MOVE','rows':[{'source':r['source'],'destination':r['proposed_destination'],'status':r['decision'],'file_count':r['file_count'],'content_hash_manifest':'FILES_BEFORE.json','executed':False} for r in rows],'actual_migrations':[],'symbolic_links_created':[],'historical_manifests_modified':[]})
with (O/'DIRECTORY_INVENTORY.csv').open('w',encoding='utf-8-sig',newline='') as f:
 fields=['name','source','proposed_destination','purpose','file_count','logical_bytes','GiB','allocated_bytes_unique_file_id','destination_conflict','incoming_potential_runtime_source_count','latest_R2_protection_entries','decision'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in rows)
print(json.dumps({'directories':len(rows),'files':sum(r['file_count'] for r in rows),'logical_bytes':sum(r['logical_bytes'] for r in rows),'allocated_bytes':sum(r['allocated_bytes_unique_file_id'] for r in rows),'all_pending':all(r['decision']=='PENDING_HUMAN_APPROVAL' for r in rows),'blocking_paths':len([e for e in effects if not e['equivalent_after_all_17_moved']]),'ast_errors':len(ast_errors),'destination_conflicts':sum(r['destination_conflict'] for r in rows)},ensure_ascii=False))
