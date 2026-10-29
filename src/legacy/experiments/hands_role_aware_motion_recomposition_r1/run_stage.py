import sys,subprocess,time,json,os
from pathlib import Path
O=Path(__file__).resolve().parent;name=sys.argv[1]
caps={'prepare':20,'source_fit':30,'source_actual':20,'target_inputs':15,'compose':60,'preflight_actual':60,'commit':15,'reports':20}
assert name in caps
p=O/'COMPUTE_LEDGER.json';L=json.loads(p.read_text()) if p.exists() else dict(numerical_limit_seconds=180,numerical_used_seconds=0,blender_diagnostic_seconds=0,report_seconds=0,total_process_seconds=0,stages=[])
assert not any(s['name']==name for s in L['stages']),'NO_RETRY_AFTER_FORMAL_START'
kind='reporting' if name=='reports' else 'blender_diagnostic' if name in ['source_actual','target_inputs','preflight_actual','commit'] else 'numerical'
cap=caps[name] if kind=='reporting' else min(caps[name],180-L['numerical_used_seconds']);assert cap>0
blender=kind=='blender_diagnostic';cmd=['D:/blender/blender.exe','--background','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(O/(name+'.py'))] if blender else [sys.executable,'-B',str(O/(name+'.py'))]
env=os.environ.copy();env['PYTHONIOENCODING']='utf-8';env['PYTHONDONTWRITEBYTECODE']='1';start=time.perf_counter()
with (O/(name+'.log')).open('w',encoding='utf8') as f:
 try:r=subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,timeout=cap,env=env);status='RETURNED';code=r.returncode
 except subprocess.TimeoutExpired:status='WATCHDOG_STOP';code=None
elapsed=time.perf_counter()-start;L['stages'].append(dict(name=name,kind=kind,seconds=elapsed,cap_seconds=cap,status=status,returncode=code,log=name+'.log'));L['total_process_seconds']+=elapsed
if kind=='reporting':L['report_seconds']+=elapsed
else:L['numerical_used_seconds']+=elapsed
if blender:L['blender_diagnostic_seconds']+=elapsed
tmp=O/'COMPUTE_LEDGER.json.pending';tmp.write_text(json.dumps(L,indent=2));tmp.replace(p)
print(json.dumps(L['stages'][-1]));print((O/(name+'.log')).read_text(encoding='utf8',errors='replace')[-3000:])
