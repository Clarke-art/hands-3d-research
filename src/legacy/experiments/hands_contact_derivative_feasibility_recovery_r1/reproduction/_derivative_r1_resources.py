import os,sys,time,json,ctypes,ast
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));t0=time.monotonic()
import derivative_probe as d
from derivative_probe import np,ca,save
class Memory(ctypes.Structure):
 _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong)]+[(s,ctypes.c_size_t) for s in ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage']]
def rss():
 k=ctypes.windll.kernel32;p=ctypes.windll.psapi;k.GetCurrentProcess.restype=ctypes.c_void_p;p.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.POINTER(Memory),ctypes.c_ulong];m=Memory();m.cb=ctypes.sizeof(m);ok=p.GetProcessMemoryInfo(k.GetCurrentProcess(),ctypes.byref(m),m.cb);assert ok;return dict(working_set_bytes=m.WorkingSetSize,peak_working_set_bytes=m.PeakWorkingSetSize)
results=[];bd=np.load(O/'BOUNDARY_KEY_STATES.npz');joint=json.loads((O.parent/'hands_contact_junction_compatibility_r1/runs/junction_2.json').read_text())
for name,z,cts,a in [('J1',d.I['seeds']['P2']['latent'],d.I['contacts'][:1],bd['angles'][1]),('J2',d.ZE,d.I['contacts'][1:],bd['angles'][-1]),('J3',joint['latent'],d.I['contacts'],bd['angles'][3])]:
 before=rss();p=d.ContactDerivative(cts,a,0,(d.LOW,d.HIGH));p.old_j(z);oldrss=rss();p.value_jac(z);newrss=rss();results.append(dict(id=name,before=before,after_old=oldrss,after_new=newrss,note='Same process allocations retained; RSS not allocation-attributed'))
import skin_proxy as sp
source=(O.parent/'hands/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py').read_text();tree=ast.parse(source);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Skin');func=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='__call__');code=ast.unparse(func).replace('def __call__','def instrumented');code=code.replace('    basis = self.base.copy()','    start = time.perf_counter(); fk = 0.; sk = 0.\n    basis = self.base.copy()');code=code.replace('    poses = []','    fk += time.perf_counter()-start\n    poses = []');code=code.replace("    for b, p in enumerate(D['parents']):","    for b, p in enumerate(D['parents']):\n        start=time.perf_counter()");code=code.replace('        ids = self.bone_ids[b]','        fk += time.perf_counter()-start; start=time.perf_counter()\n        ids = self.bone_ids[b]');code=code.replace("    return np.einsum('kij,kvj->kvi', self.world, V)[:, :, :3]","        sk += time.perf_counter()-start\n    start=time.perf_counter(); out=np.einsum('kij,kvj->kvi', self.world, V)[:, :, :3]; sk+=time.perf_counter()-start\n    return out, fk, sk")
ns=dict(vars(sp));ns['time']=time;exec(code,ns);z=np.array(joint['latent']);st=d.state(z);timings=[]
for _ in range(10):
 out,fk,sk=ns['instrumented'](sp.S,st[6:].reshape(1,5,4));ref=sp.S(st[6:].reshape(1,5,4));assert abs(out-ref).max()<1e-12;timings.append(dict(FK_seconds=fk,weighted_skin_seconds=sk))
contact=[];V=d.skin(st)
for _ in range(5):
 t=time.perf_counter();[d.contact_metric(V,d.c.KEYS[c['midi']-21],bd['angles'][3][c['midi']-21],c['finger']) for c in d.I['contacts']];contact.append(time.perf_counter()-t)
save('RESOURCE_PROFILE.json',dict(memory=results,skin_instrumentation=timings,face_contact_detection_seconds=contact,instrumentation_source='AST copy of historical Skin.__call__; exact output matched <1e-12 m',old_J4_external_observation=dict(working_set_bytes=8945868800,CPU_seconds=57.02,note='PowerShell Get-Process snapshot during old extra probe, not peak or per-function allocation'),new_J4_serialized_function_bytes=(O/'PRUNED_J.casadi').stat().st_size))
save('RESOURCE_BUDGET.json',dict(charged_seconds=time.monotonic()-t0))
