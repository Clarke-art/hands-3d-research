import sys,json,hashlib,time,datetime,shutil
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;BASE=O.parent;P=BASE/'hands_early_hand_preparation_entry_reachability_r1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def js(n,d):(O/n).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf8')
scope=read(P/'PROTECTION_SCOPE_AUDIT.json');proof=read(O/'CONCURRENT_TASK_RAW_EVIDENCE.json')
records=[]
for s in [r['path'] for r in scope['changed_files']]+scope['new_files']:
 p=Path(s);st=p.stat();h=sha(p);expected=next((r['after'] for r in scope['changed_files'] if r['path']==s),None)
 attribution='ATTRIBUTED_CONCURRENT_CHANGE' if proof['turn_id']==scope['concurrent_task_evidence']['turn_id'] and proof['startedAt']-1<=st.st_mtime<=proof['completedAt']+1 and (expected is None or h==expected) else 'PROVENANCE_UNCERTAIN'
 records.append(dict(path=s,bytes=st.st_size,sha256=h,previous_after_sha256=expected,mtime_unix=st.st_mtime,mtime_UTC=datetime.datetime.fromtimestamp(st.st_mtime,datetime.timezone.utc).isoformat(),mtime_Asia_Shanghai=datetime.datetime.fromtimestamp(st.st_mtime,datetime.timezone(datetime.timedelta(hours=8))).isoformat(),owner_task='PIANO_PROJECT_STORAGE_CLEANUP_AUDIT_R1',owner_thread=proof['thread_id'],owner_turn=proof['turn_id'],status=attribution,role='CONCURRENT_PIANO_AUDIT_DELIVERABLE_OR_SCRIPT'))
assert all(r['status']=='ATTRIBUTED_CONCURRENT_CHANGE' for r in records),'Stop later stages: unexplained provenance'
js('CONCURRENCY_ATTRIBUTION.json',dict(status='ATTRIBUTED_CONCURRENT_CHANGE',records=records,modified_count=3,new_count=15,unknown_changes=[],previous_global_protection_status='FAIL_PRESERVED',original_frozen_protection_status='PASS_9277_ITEMS',raw_authorization_evidence_file='CONCURRENT_TASK_RAW_EVIDENCE.json',classification=dict(Hands_frozen_assets='unchanged scientific inputs',historical_experiment_results='read-only including the entire previous experiment',concurrent_Piano_task='the18 recorded files',unexplained='none in historical discrepancy set'),revert_delete_overwrite=False))
(O/'PROTECTION_CONCURRENCY_AUDIT.md').write_text('# 并发保护归因\n\nDESIGN_PROVISIONAL — STOP — HUMAN REVIEW\n\n已重读另一聊天的原始Human任务、文件更改与执行记录。3处变化和15个新增均归属已授权的 PIANO_PROJECT_STORAGE_CLEANUP_AUDIT_R1；逐文件完整路径、SHA256、大小、时间和归属见 CONCURRENCY_ATTRIBUTION.json，授权原文与调用证据见 CONCURRENT_TASK_RAW_EVIDENCE.json。当前3处变化的身份与上一轮after哈希完全一致，18项mtime均在所属任务时间窗口内。分类为 ATTRIBUTED_CONCURRENT_CHANGE；没有无法解释的历史变化。上一轮85850项扩展保护FAIL事实保持，不追改为PASS，不恢复、删除或覆盖任何文件。\n\n完成归因后建立本轮独立当前保护基线；本轮基线与旧历史FAIL是两个不同时间窗口。冻结源、所有Hands历史和Piano均只读，当前Piano审计文件不作为任何Rig/规划求解写入依赖。\n',encoding='utf8')
old=read(P/'PROTECTED_FILES_AFTER.json');allowed={r['path'] for r in scope['changed_files']}
roots=[p for p in BASE.iterdir() if p.is_dir() and (p.name=='piano' or p.name.startswith('hands')) and p!=O]
paths=set(old)
for root in roots:paths.update(str(f) for f in root.rglob('*') if f.is_file())
beg=time.monotonic();hashes={s:sha(Path(s)) for s in sorted(paths)}
bad=[s for s,h in old.items() if hashes[s]!=h];assert not bad,bad
js('PROTECTED_FILES_BEFORE.json',hashes);js('PROTECTION_SETUP.json',dict(current_count=len(hashes),previous_historical_count=len(old),previous_snapshot_current_match=True,prior_global_FAIL_preserved=True,protected_roots=[str(p) for p in roots],seconds=time.monotonic()-beg))
(O/'logs').mkdir(exist_ok=True);(O/'runs').mkdir(exist_ok=True);(O/'sources').mkdir(exist_ok=True)
for n in ['rig_model.py','skin_proxy.py','geometry_detector.py','triangle_distance.py','SKIN_MODEL.npz','SKIN_MODEL_META.json','extract_anatomy.py','ENDPOINT_SOLVE_2.json','MOTION_COLLOCATION_KEYS.npz','EXPERIMENT_INPUT.json','POLICY_LOCK.json','CONTACT_STATE_SEQUENCE.json','kinematic_derivative_api.py','contact_solver.py','batch_verify.py','coupled_model.py','run_stage.py']:
 shutil.copyfile(P/n,O/n)
policy=read(O/'POLICY_LOCK.json');policy.update(task='PIANO_LONG_CONTEXT_HAND_MOTION_ARCHITECTURE_R1',no_more_solves=False,maximum_high_level_candidates=2,total_new_numerical_budget_seconds=600,recommended_numerical_seconds=300,formal_Action_authorized=False);js('POLICY_LOCK.json',policy)
print('NEW_BASELINE_READY',len(hashes),flush=True)
