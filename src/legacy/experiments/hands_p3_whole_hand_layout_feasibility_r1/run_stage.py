import sys, subprocess, time, json
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
name=sys.argv[1];assert name in ['prepare','solve','recover_initial','actual','close']
p=O/'COMPUTE_LEDGER.json'
ledger=json.loads(p.read_text()) if p.exists() else dict(limit_seconds=180,used_seconds=0,stages=[])
previous=[x for x in ledger['stages'] if x['name']==name]
assert not previous or (name=='prepare' and all(x['returncode']!=0 for x in previous) and not (O/'BATCH_STARTED.json').exists()),'NO_NUMERIC_RETRY'
cap=min(180-ledger['used_seconds'],65 if name=='solve' else 90)
assert cap>0
cmd=['D:/blender/blender.exe','--background','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(O/'actual.py')] if name=='actual' else [sys.executable,'-B',str(O/(name+'.py'))]
start=time.perf_counter()
logpath=O/(name+'.log') if not previous else O/(name+'_technical_repair_'+str(len(previous))+'.log')
with logpath.open('w',encoding='utf8') as log:
 try:
  r=subprocess.run(cmd,cwd=O,stdout=log,stderr=subprocess.STDOUT,timeout=cap)
  status='RETURNED';code=r.returncode
 except subprocess.TimeoutExpired:status='WATCHDOG_STOP';code=None
elapsed=time.perf_counter()-start
ledger['stages'].append(dict(name=name,elapsed_seconds=elapsed,status=status,returncode=code,cap_seconds=cap,log=logpath.name))
ledger['used_seconds']+=elapsed;ledger['remaining_seconds']=180-ledger['used_seconds']
p.write_text(json.dumps(ledger,indent=2)+'\n')
print(json.dumps(ledger['stages'][-1]));print(logpath.read_text(encoding='utf8')[-3500:])
