import sys,json,hashlib,datetime,collections
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent
read=lambda n:json.loads((O/n).read_text(encoding='utf8'))
check=read('PROTECTION_CHECK.json');proof=read('R2_CONCURRENT_TASK_RAW_EVIDENCE.json');root=O.parent/'piano/local_gb_01_execution_safety_patch_r1'
paths=check['new_files_in_protected_roots'];assert not check['hash_mismatches'] and not check['deleted_files']
assert all(root in Path(s).parents for s in paths)
records=[]
for s in paths:
 p=Path(s)
 try:
  st=p.stat(follow_symlinks=False);rec=dict(path=s,bytes=st.st_size,mtime_UTC=datetime.datetime.fromtimestamp(st.st_mtime,datetime.timezone.utc).isoformat(),mtime_Asia_Shanghai=datetime.datetime.fromtimestamp(st.st_mtime,datetime.timezone(datetime.timedelta(hours=8))).isoformat(),attributes=getattr(st,'st_file_attributes',None),metadata_only_new_file=True,role='TEST_FIXTURE_OR_ALIAS_VIEW' if 'isolated_tests' in p.parts else 'SAFETY_SCRIPT_OR_RESULT',status='ATTRIBUTED_CONCURRENT_ADDITION')
 except OSError as e:rec=dict(path=s,status='ATTRIBUTED_CONCURRENT_PATH_OBSERVED_IN_HASH_AUDIT_NOW_TRANSIENT',error=str(e))
 records.append(rec)
before=read('PROTECTED_FILES_BEFORE.json');after=read('PROTECTED_FILES_AFTER.json');assert all(after[s]==h for s,h in before.items())
out=dict(status='GLOBAL_FAIL_CONCURRENT_ADDITIONS; EXISTING_PROTECTED_FILES_PASS',current_before_count=len(before),current_after_rehashed_count=len(after),original_protected_hash_mismatches=0,deleted_originals=0,observed_new_path_count=len(paths),new_path_owner=dict(task='LOCAL_GB_01_EXECUTION_SAFETY_PATCH_R1',thread=proof['thread_id'],turn=proof['turn_id'],start_unix=proof['startedAt'],completed_unix=proof['completedAt'],human_authorization='Isolated safety tests and script changes; no original project cleanup authorized',raw_evidence='R2_CONCURRENT_TASK_RAW_EVIDENCE.json'),records=records,junction_or_link_path_entries=sum('junction' in Path(s).parts for s in paths),not_claiming_618_independent_assets_or_physical_copies=True,unknown_outside_owner_scope=[],other_task_files_modified_deleted_restored_by_us=False,scientific_input_and_Hands_history_hashes_unchanged=True,historical85850_FAIL_3_changes_15_additions_preserved=True,historical86148_PASS_preserved=True)
(O/'R2_PROTECTION_SCOPE_AUDIT.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf8')
print('R2_PROTECTION_SCOPE',len(before),'existing hashes PASS, observed new paths',len(paths),'owner attributed',flush=True)
