import sys
sys.dont_write_bytecode=True
import json,hashlib,ast,ctypes
from pathlib import Path
O=Path(__file__).parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  while b:=f.read(4*1024*1024):h.update(b)
 return h.hexdigest()
def save(n,x):
 with (O/n).open('x',encoding='utf8') as f:json.dump(x,f,ensure_ascii=False,indent=2)
r=rd(O/'PATH_ADAPTER_REGISTRY.json');S=Path(r['shadow_pilot']);ROOT=Path(r['project_root']);H=Path(r['hands_root']);p=rd(S/'POLICY_LOCK.json');known=rd(S/'PROTECTED_FILES_BEFORE.json');registry={x['logical_legacy_path']:x for x in r['inputs']}
excluded=[]
for key in list(registry):
 if 'native_math_binary_byte_access_only' in registry[key]['roles']:
  excluded.append(registry.pop(key))
def add(path,role,evidence,expected=None):
 path=Path(path);assert path.is_file(),str(path);expected=expected or known[str(path)];h=sha(path);assert h==expected,str(path)
 if str(path) in registry:return
 s=path.stat();registry[str(path)]={'logical_legacy_path':str(path),'resolved_path':str(path),'expected_sha256':expected,'roles':[role],'evidence':[evidence],'before_sha256':h,'bytes':s.st_size,'mtime_ns':s.st_mtime_ns,'file_id':s.st_ino,'device':s.st_dev,'read_whitelisted':True}
st=p['source_input']['static_scene'];add(st['candidate_path'],'approved_static_scene','POLICY_LOCK.source_input.static_scene',st['candidate_sha256'])
core=H/'audits/midi_driven_dual_hand_piano_performance_poc_r1/performance_core.py';t=ast.parse(core.read_text());declared=[]
for node in ast.walk(t):
 if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='read' and node.args and isinstance(node.args[0],ast.BinOp) and isinstance(node.args[0].left,ast.Name) and node.args[0].left.id=='P' and isinstance(node.args[0].right,ast.Constant) and isinstance(node.args[0].right.value,str):
  target=core.parent/node.args[0].right.value;add(target,'performance_core_declared_JSON_input',f'performance_core.py:{node.lineno}');declared.append(str(target))
deps=core.parent/'_deps';ca=ROOT/'hands_contact_constrained_trajectory_planning_r1/deps'
for pkg,base in [('numpy',deps),('scipy',deps),('casadi',ca)]:
 candidates=[Path(x) for x in known if Path(x).is_relative_to(base/pkg) and Path(x).suffix.lower() in ['.pyd','.dll'] and 'tests' not in str(x).lower() and 'test' not in Path(x).name.lower()]
 for q in sorted(candidates)[:2]:add(q,'declared_native_binary_byte_access_only',f'{pkg} current declared import root {base}; no load/import/ABI')
r['inputs']=list(registry.values());r['registry_revision']='v2_current_declared_package_roots';r['prior_optional_binary_paths_excluded']=excluded;r['performance_core_JSON_inputs']=declared
save('PATH_ADAPTER_REGISTRY_V2.json',r)
# Complement unavailable Restart Manager census with per-file exclusive read-open probes.
k=ctypes.WinDLL('kernel32',use_last_error=True);k.CreateFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_void_p,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_void_p];k.CreateFileW.restype=ctypes.c_void_p;k.CloseHandle.argtypes=[ctypes.c_void_p];k.CloseHandle.restype=ctypes.c_int
probes=[]
for x in rd(O/'PILOT_BASELINE.json')['files']:
 handle=k.CreateFileW(x['path'],0x80000000,0,None,3,0x00200000,None);err=ctypes.get_last_error() if handle==ctypes.c_void_p(-1).value else 0
 probes.append({'path':x['path'],'exclusive_read_open_succeeded':not err,'error_code':err})
 if not err:k.CloseHandle(handle)
save('EXCLUSIVE_READ_RESOURCE_PROBES.json',{'files':probes,'succeeded':sum(x['exclusive_read_open_succeeded'] for x in probes),'conflicts':[x for x in probes if not x['exclusive_read_open_succeeded']],'scope':'Each file probed sequentially, handles immediately closed. Does not enumerate process identities or all handle types; original copy baseline held simultaneous deny-write/delete read pins.','restart_manager_status':'UNAVAILABLE_ERROR_29; retained raw record'})
save('REGISTRY_REFINEMENT.json',{'purpose':'Close transitive performance_core JSON reads, approved static source, and restrict native-byte checks to declared package roots','additional_inputs':len(r['inputs'])-246,'excluded_optional_prior_binary_paths':excluded,'original_source_files_modified':[],'historical_program_execution':[]})
print('REGISTRY_V2',len(r['inputs']),'inputs; exclusive source read probes',sum(x['exclusive_read_open_succeeded'] for x in probes),'of',len(probes))
