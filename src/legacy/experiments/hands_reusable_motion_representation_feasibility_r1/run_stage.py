import sys,subprocess,time,json,os
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;name=sys.argv[1]
assert name in ['prepare','source_audit','reference_frames','reports']
p=O/'COMPUTE_LEDGER.json'
ledger=json.loads(p.read_text()) if p.exists() else dict(limit_seconds=120,used_seconds=0,stages=[])
assert not any(s['name']==name for s in ledger['stages']),'NO_STAGE_RETRY_WITHOUT_RECORDED_CODE_REPAIR'
cap=min(120-ledger['used_seconds'],65 if name=='source_audit' else 20)
assert cap>0
cmd=['D:/blender/blender.exe','--background','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(O/(name+'.py'))] if name=='source_audit' else [sys.executable,'-B',str(O/(name+'.py'))]
env=os.environ.copy();env['PYTHONIOENCODING']='utf-8';env['PYTHONDONTWRITEBYTECODE']='1'
start=time.perf_counter()
with (O/(name+'.log')).open('w',encoding='utf8') as log:
 try:r=subprocess.run(cmd,cwd=O,stdout=log,stderr=subprocess.STDOUT,timeout=cap,env=env);code=r.returncode;status='RETURNED'
 except subprocess.TimeoutExpired:code=None;status='WATCHDOG_STOP'
elapsed=time.perf_counter()-start
ledger['stages'].append(dict(name=name,status=status,returncode=code,elapsed_seconds=elapsed,cap_seconds=cap,log=name+'.log'))
ledger['used_seconds']+=elapsed;ledger['remaining_seconds']=120-ledger['used_seconds']
temp=O/'COMPUTE_LEDGER.json.pending';temp.write_text(json.dumps(ledger,indent=2)+'\n');temp.replace(p)
print(json.dumps(ledger['stages'][-1]));print((O/(name+'.log')).read_text(encoding='utf8',errors='replace')[-3500:])
