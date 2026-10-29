import sys
sys.dont_write_bytecode=True
import os,json,hashlib,shutil,ast,ctypes,time,re
from pathlib import Path
ROOT=Path(r'D:\codex one\3D interactive components');H=ROOT/'hands';O=Path(__file__).parent
NAME='hands_long_context_corridor_ik_bridge_r2';SOURCE=ROOT/NAME;FORMAL=H/NAME;SHADOW=O/'shadow'/NAME;R1=H/'audits/directory_structure_correction_r1'
resume='--resume-copy-receipt' in sys.argv
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(n,x):
 p=O/n
 if resume and p.exists():
  assert rd(p)==x,f'Resume mismatch, no overwrite: {p}'
  return
 with p.open('x',encoding='utf8') as f:json.dump(x,f,ensure_ascii=False,indent=2)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  while b:=f.read(4*1024*1024):h.update(b)
 return h.hexdigest()
def scan(r):
 out={};dirs=[];stack=[r]
 while stack:
  d=stack.pop();s=d.stat(follow_symlinks=False);assert not s.st_file_attributes&0x400,str(d);dirs.append(d)
  for e in os.scandir(d):
   p=Path(e.path);s=e.stat(follow_symlinks=False);assert not s.st_file_attributes&0x400,str(p)
   if s.st_file_attributes&0x10:stack.append(p)
   else:out[str(p.relative_to(r))]=p
 return out,dirs
assert not FORMAL.exists(),'Formal migration target forbidden'
assert resume or not SHADOW.exists(),'Shadow target exists; no overwrite'
root_entries=[p.name for p in sorted(ROOT.iterdir())]
if not resume:save('ROOT_BASELINE.json',{'time_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'members':root_entries,'count':len(root_entries),'only_hands_piano':root_entries==['hands','piano']})
else:assert root_entries==rd(O/'ROOT_BASELINE.json')['members']
evidence_names=['DIRECTORY_CORRECTION_REPORT.md','PATH_MAPPING.json','DEPENDENCY_SUMMARY.json','PROTECTION_RELATIONSHIPS.json','MIGRATION_DECISIONS.json','STATIC_PATH_IMPACT.json','FINAL_STATUS.json','HISTORICAL_PROTECTION_PRESERVATION.json','DIRECTORY_INVENTORY.json','FILES_BEFORE.json']
evidence=[{'path':str(R1/n),'sha256':sha(R1/n),'purpose':'Reused R1 evidence; not rescanned 17 directory inventories'} for n in evidence_names]
evidence.append({'path':str(H/'AGENTS.md'),'sha256':sha(H/'AGENTS.md'),'purpose':'Fixed directory policy'})
save('R1_EVIDENCE_BINDINGS.json',evidence)
old=rd(R1/'FILES_BEFORE.json');expected={r['relative']:r for r in old[NAME]}
paths,dirs=scan(SOURCE);assert set(paths)==set(expected),'R2 membership drift'
# Restart Manager resource census (no shutdown/restart functions). It is not exhaustive handle enumeration.
class FT(ctypes.Structure):_fields_=[('low',ctypes.c_ulong),('high',ctypes.c_ulong)]
class UP(ctypes.Structure):_fields_=[('pid',ctypes.c_ulong),('start',FT)]
class PI(ctypes.Structure):_fields_=[('process',UP),('app',ctypes.c_wchar*256),('service',ctypes.c_wchar*64),('app_type',ctypes.c_uint),('status',ctypes.c_ulong),('session',ctypes.c_ulong),('restartable',ctypes.c_int)]
rm=ctypes.WinDLL('Rstrtmgr',use_last_error=True)
rm.RmStartSession.argtypes=[ctypes.POINTER(ctypes.c_ulong),ctypes.c_ulong,ctypes.c_wchar_p];rm.RmStartSession.restype=ctypes.c_ulong
rm.RmRegisterResources.argtypes=[ctypes.c_ulong,ctypes.c_uint,ctypes.POINTER(ctypes.c_wchar_p),ctypes.c_uint,ctypes.c_void_p,ctypes.c_uint,ctypes.c_void_p];rm.RmRegisterResources.restype=ctypes.c_ulong
rm.RmGetList.argtypes=[ctypes.c_ulong,ctypes.POINTER(ctypes.c_uint),ctypes.POINTER(ctypes.c_uint),ctypes.POINTER(PI),ctypes.POINTER(ctypes.c_ulong)];rm.RmGetList.restype=ctypes.c_ulong
rm.RmEndSession.argtypes=[ctypes.c_ulong];rm.RmEndSession.restype=ctypes.c_ulong
session=ctypes.c_ulong();key=ctypes.create_unicode_buffer(33);status=999 if resume else rm.RmStartSession(ctypes.byref(session),0,key);usage=rd(O/'OPEN_RESOURCE_CENSUS.json') if resume else {'api':'Windows Restart Manager resource census','start_code':status,'users':[],'exhaustive_open_handles_claim':False,'no_shutdown_or_restart':True}
if status==0:
 try:
  arr=(ctypes.c_wchar_p*len(paths))(*(str(p) for p in paths.values()));usage['register_code']=rm.RmRegisterResources(session,len(paths),arr,0,None,0,None)
  needed=ctypes.c_uint();size=ctypes.c_uint();reason=ctypes.c_ulong();rc=rm.RmGetList(session,ctypes.byref(needed),ctypes.byref(size),None,ctypes.byref(reason));usage['first_get_code']=rc
  if rc==234:
   for attempt in range(3):
    size=ctypes.c_uint(needed.value);result=(PI*size.value)();rc=rm.RmGetList(session,ctypes.byref(needed),ctypes.byref(size),result,ctypes.byref(reason))
    if rc==0:
     usage['users']=[{'pid':x.process.pid,'app':x.app,'service':x.service,'app_type':x.app_type,'status':x.status} for x in result[:size.value]];break
    if rc!=234:break
  usage['get_code']=rc;usage['reboot_reason']=reason.value
 finally:usage['end_code']=rm.RmEndSession(session)
save('OPEN_RESOURCE_CENSUS.json',usage)
# Pin all pilot files with GENERIC_READ, FILE_SHARE_READ only. A conflicting writer prevents baseline/copy.
k=ctypes.WinDLL('kernel32',use_last_error=True);k.CreateFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_void_p,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_void_p];k.CreateFileW.restype=ctypes.c_void_p;k.CloseHandle.argtypes=[ctypes.c_void_p];k.CloseHandle.restype=ctypes.c_int
handles=[];baseline=[];maps=[]
try:
 for p in paths.values():
  handle=k.CreateFileW(str(p),0x80000000,1,None,3,0x00200000,None)
  if handle==ctypes.c_void_p(-1).value:raise RuntimeError(f'FAIL_CLOSED: cannot deny writer/delete sharing for {p}; error={ctypes.get_last_error()}')
  handles.append(handle)
 for rel,p in sorted(paths.items()):
  s=p.stat();digest=sha(p);assert digest==expected[rel]['sha256'],f'Protected R2 change: {p}'
  baseline.append({'path':str(p),'relative':rel,'sha256':digest,'bytes':s.st_size,'mtime_ns':s.st_mtime_ns,'device':s.st_dev,'file_id':s.st_ino,'nlink':s.st_nlink})
 save('PILOT_BASELINE.json',{'source':str(SOURCE),'file_count':len(paths),'directory_count':len(dirs),'logical_bytes':sum(x['bytes'] for x in baseline),'files':baseline,'matches_R1_count_members_SHA':True,'all_files_pinned_during_hash_and_copy':True,'pin_sharing':'FILE_SHARE_READ only: denies new write/delete opens; concurrent writer at pin time fails closed','RM_read_handles_not_exhaustively_excluded':True})
 if not resume:SHADOW.mkdir(parents=True,exist_ok=False)
 for d in sorted(dirs,key=lambda p:len(p.parts)):
  if d!=SOURCE:
   if resume:assert (SHADOW/d.relative_to(SOURCE)).is_dir()
   else:(SHADOW/d.relative_to(SOURCE)).mkdir(exist_ok=False)
 for row in baseline:
  src=Path(row['path']);dst=SHADOW/row['relative']
  if not resume:
   with src.open('rb') as f,dst.open('xb') as g:shutil.copyfileobj(f,g,4*1024*1024)
  digest=sha(dst);assert digest==row['sha256']
  maps.append({'source':str(src),'formal_proposed_path':str(FORMAL/row['relative']),'shadow':str(dst),'relative':row['relative'],'bytes':row['bytes'],'expected_sha256':row['sha256'],'shadow_sha256':digest,'pass':True})
 copied,_=scan(SHADOW);assert set(copied)==set(paths)
 assert all(sha(row['path'])==row['sha256'] for row in baseline)
 save('SHADOW_COPY_MANIFEST.json',{'source':str(SOURCE),'formal_target':str(FORMAL),'physical_shadow':str(SHADOW),'files':maps,'file_count':len(maps),'members_equal':True,'all_SHA_equal':True,'source_unchanged_during_copy':True,'created_links':[],'original_files_moved':[]})
finally:
 for handle in handles:k.CloseHandle(handle)
assert not FORMAL.exists()
# Per-source side-effect and declared-path inspection. Never import legacy code.
code=[];legacy_expressions=[]
for rel,p in sorted(paths.items()):
 if p.suffix!='.py':continue
 text=p.read_text(encoding='utf-8-sig');tree=ast.parse(text);calls=[];imports=[]
 for node in ast.walk(tree):
  if isinstance(node,(ast.Import,ast.ImportFrom)):imports.append({'line':node.lineno,'statement':ast.get_source_segment(text,node)})
  if isinstance(node,ast.Call):
   target=ast.unparse(node.func)
   if any(w in target.lower() for w in ['write','mkdir','copy','save','remove','unlink','subprocess','popen','exec','compile','open_mainfile','settime','apply','nlpsol','solve','render','optimize']):calls.append({'line':node.lineno,'call':target,'statement':ast.get_source_segment(text,node)[:500]})
  if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Div) and isinstance(node.left,ast.Attribute) and node.left.attr=='parent' and isinstance(node.left.value,ast.Name) and node.left.value.id=='O' and isinstance(node.right,ast.Constant) and isinstance(node.right.value,str):
   suffix=node.right.value;legacy_expressions.append({'source':str(p),'relative_source':rel,'line':node.lineno,'expression':ast.get_source_segment(text,node),'suffix':suffix,'old_resolved':str(SOURCE.parent/suffix),'naive_formal_resolved':str(FORMAL.parent/suffix),'naive_shadow_resolved':str(SHADOW.parent/suffix),'role':'historical setup/protection' if any(t in p.name for t in ['prepare','protection','write','reports']) else 'runtime/import/data path','not_executed':True})
 code.append({'file':str(p),'shadow':str(SHADOW/rel),'sha256':sha(p),'imports':imports,'side_effect_or_dynamic_call_sites':calls,'historical_file_executed':False,'whole_module_import_whitelisted':False})
save('LEGACY_SOURCE_SAFETY_AUDIT.json',code);save('LEGACY_PATH_EXPRESSIONS.json',legacy_expressions)
protected=rd(SHADOW/'PROTECTED_FILES_BEFORE.json');r1hash={r['path']:r['sha256'] for group in old.values() for r in group};pilot_hash={r['path']:r['sha256'] for r in baseline}
allknown={**r1hash,**protected,**pilot_hash};registry={}
def register(path,role,evidence,contract_hash=None):
 p=Path(path)
 assert p.is_absolute(),str(p)
 assert p.is_relative_to(ROOT),str(p)
 if not p.is_file():return False
 expected_sha=contract_hash or allknown.get(str(p));assert expected_sha,f'No protected hash for input {p}'
 if str(p) not in registry:registry[str(p)]={'logical_legacy_path':str(p),'resolved_path':str(SHADOW/p.relative_to(SOURCE)) if p.is_relative_to(SOURCE) else str(p),'expected_sha256':expected_sha,'roles':[],'evidence':[]}
 else:assert registry[str(p)]['expected_sha256']==expected_sha,str(p)
 registry[str(p)]['roles'].append(role);registry[str(p)]['evidence'].append(evidence);return True
for row in baseline:register(row['path'],'pilot_copy','R1 FILES_BEFORE + pinned pilot SHA')
unresolved=[]
for expr in legacy_expressions:
 p=Path(expr['old_resolved'])
 if p.is_file():register(p,expr['role'],f"{expr['relative_source']}:{expr['line']}")
 elif p.is_dir():
  # Locate only module filenames explicitly used in audited imports; no full dependency inventory.
  module_names=['performance_core.py','blender_utils.py','numpy/__init__.py','scipy/__init__.py','scipy/interpolate/__init__.py','scipy/spatial/transform/__init__.py','casadi/__init__.py','casadi/casadi.py','mido/__init__.py']
  found=[]
  for n in module_names:
   if register(p/n,'declared_math_or_rig_module_resource',f"{expr['relative_source']}:{expr['line']} import path"):found.append(str(p/n))
  if not found:unresolved.append({'expression':expr,'reason':'directory/import resolution not expanded; dynamic modules not imported'})
 else:unresolved.append({'expression':expr,'reason':'source path does not currently exist'})
policy=rd(SHADOW/'POLICY_LOCK.json');bindings=rd(ROOT/'hands_sequence_fingering_planning_r1/SOURCE_EVENT_BINDINGS.json')
register(ROOT/'hands_sequence_fingering_planning_r1/SOURCE_EVENT_BINDINGS.json','source_MIDI_event_binding','verify_midi.py:6')
register(bindings['source_midi'],'formal_MIDI','SOURCE_EVENT_BINDINGS.source_midi',bindings['source_midi_sha256'])
register(bindings['source_timeline'],'formal_timeline','SOURCE_EVENT_BINDINGS.source_timeline',bindings['source_timeline_sha256'])
register(policy['source_input']['candidate_source'],'locked_fingering','POLICY_LOCK.source_input',policy['source_input']['candidate_sha256'])
for field in ['source_action_scene']:
 r=policy[field];register(r['path'],'frozen_Rig_Action_container',f'POLICY_LOCK.{field}',r['sha256'])
r=policy['source_input']['source_scene'];register(r['path'],'original_scene_container','POLICY_LOCK.source_input.source_scene',r['sha256'])
for key in ['right_pointer','left_pointer']:
 ptr=policy['source_input'].get(key)
 if ptr:
  r=ptr['asset'];register(H/r['path'],'approved_frozen_asset',f'POLICY_LOCK.source_input.{key}.asset',r['sha256'])
# Additional files are taken verbatim from actual blender_utils/skin_proxy/context code and manifest.
for name,rel,role,why in [
 ('hands_c01_whole_hand_motion_feasibility_r1','blender_utils.py','rig_interface_source','batch_verify.py import blender_utils'),
 ('hands_c01_whole_hand_motion_feasibility_r1','INPUT_BINDINGS.json','rig_source_bindings','blender_utils.py:9'),
 ('hands_c01_whole_hand_motion_feasibility_r1','RIG_PREFLIGHT.json','native_identity_evidence','blender_utils.py:9'),
 ('hands_c01_whole_hand_motion_feasibility_r1','DIGIT_SKIN_ROI.json','skin_geometry_metadata','blender_utils.py:9'),
 ('hands_c01_whole_hand_motion_feasibility_r1','blender_preflight.py','frozen_native_helpers','blender_utils AST selection'),
 ('hands_early_hand_preparation_entry_reachability_r1','ANCHOR_REQUESTS.json','historical_anchor','preflight_r2.py:10'),
 ('hands_early_hand_preparation_entry_reachability_r1','ENTRY_ACTUAL_SAMPLES.json','historical_actual_data','preflight_r2.py:10'),
 ('hands_long_context_hand_motion_architecture_r1','HIGH_LEVEL_CLEARANCE_ACTUAL.json','historical_safe_state','preflight_r2.py:10'),
 ('hands_c01_anatomy_preparation_audit_r1','B_SOLVE_2.json','B2_source','rig_model.py:9'),
 ('hands_contact_state_motion_planner_comparison_r1','ORIGINAL_ACTION_INSPECTION.json','original_Action_comparison','batch_verify.py:31'),
 ('hands_contact_constrained_trajectory_planning_r1','FROZEN_SKIN_SYMBOLIC.casadi','frozen_symbolic_resource','coupled_model.py:9')]:register(ROOT/name/rel,role,why)
hands_sources=['audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py','audits/midi_driven_dual_hand_piano_performance_poc_r1/performance_core.py','production_spec/RIGHT_HAND_PRODUCT_BASELINE.json','production_spec/LEFT_HAND_PRODUCT_BASELINE.json']
for rel in hands_sources:register(H/rel,'formal_hands_interface','Source skin_proxy/blender_utils and frozen pointer contracts')
# Native package files are located only within declared import directories and matched against existing protected manifest entries.
for name in ['numpy','scipy','casadi']:
 candidates=[Path(p) for p in protected if name in Path(p).parts and Path(p).suffix.lower() in ['.pyd','.dll']]
 if candidates:
  for p in sorted(candidates)[:2]:register(p,'native_math_binary_byte_access_only',f'{name} existing protected manifest; no native loader/ABI invocation')
input_rows=[]
for row in registry.values():
 p=Path(row['resolved_path']);h=sha(p);assert h==row['expected_sha256'],f'Input drift: {p}'
 st=p.stat();row.update(before_sha256=h,bytes=st.st_size,mtime_ns=st.st_mtime_ns,file_id=st.st_ino,device=st.st_dev,read_whitelisted=True)
 input_rows.append(row)
save('PATH_ADAPTER_REGISTRY.json',{'project_root':str(ROOT),'hands_root':str(H),'piano_root':str(ROOT/'piano'),'original_pilot':str(SOURCE),'formal_proposed_pilot':str(FORMAL),'shadow_pilot':str(SHADOW),'inputs':input_rows,'unresolved_declared_directories':unresolved,'legacy_expression_file':'LEGACY_PATH_EXPRESSIONS.json','original_pilot_reads_allowed_in_validator':False,'outside_registry_fallback':False})
save('BASELINE_SUMMARY.json',{'pilot_files':len(baseline),'pilot_bytes':sum(r['bytes'] for r in baseline),'copied_files':len(maps),'shadow_SHA_matches':True,'registry_files':len(input_rows),'external_inputs':sum(not Path(r['logical_legacy_path']).is_relative_to(SOURCE) for r in input_rows),'original_R2_moves':0,'formal_target_created':False,'native_resource_runtime_checked':False,'original_scripts_executed':[],'R1_full_inventory_repeated':False})
print('SHADOW_PREPARED',len(maps),'files; registered',len(input_rows),'read resources; source unchanged',flush=True)
