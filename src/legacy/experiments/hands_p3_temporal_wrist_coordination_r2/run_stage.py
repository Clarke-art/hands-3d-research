import sys,subprocess,time,json
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;name=sys.argv[1]
assert name in ['gate1','prepare','source_probe','input_gate','solve','diagnose','actual','reports']
p=O/'COMPUTE_LEDGER.json'
ledger=json.loads(p.read_text()) if p.exists() else dict(limit_seconds=180,used_seconds=0,stages=[])
previous=[s for s in ledger['stages'] if s['name']==name]
assert not previous or (name=='input_gate' and all(s['returncode']!=0 for s in previous) and not (O/'FORMAL_ATTEMPT_STARTED.json').exists()),'NO_OPTIMIZER_RETRY'
if name=='solve':
 assert json.loads((O/'RESULT_PERSISTENCE_GATE.json').read_text())['RESULT_PERSISTENCE_GATE']=='PASS'
 assert json.loads((O/'INPUT_CONTRACT_GATE.json').read_text())['pass_']
cap=min(180-ledger['used_seconds'],85 if name=='solve' else 55 if name=='actual' else 20)
assert cap>0
blender=name in ['source_probe','actual']
cmd=['D:/blender/blender.exe','--background','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(O/(name+'.py'))] if blender else [sys.executable,'-B',str(O/(name+'.py'))]
start=time.perf_counter()
logpath=O/(name+'.log') if not previous else O/(name+'_preformal_repair_'+str(len(previous))+'.log')
with logpath.open('w',encoding='utf8') as log:
 try:r=subprocess.run(cmd,cwd=O,stdout=log,stderr=subprocess.STDOUT,timeout=cap);code=r.returncode;status='RETURNED'
 except subprocess.TimeoutExpired:code=None;status='WATCHDOG_STOP'
elapsed=time.perf_counter()-start
ledger['stages'].append(dict(name=name,status=status,returncode=code,elapsed_seconds=elapsed,cap_seconds=cap,log=logpath.name))
ledger['used_seconds']+=elapsed;ledger['remaining_seconds']=180-ledger['used_seconds']
temp=O/'COMPUTE_LEDGER.json.pending';temp.write_text(json.dumps(ledger,indent=2)+'\n');temp.replace(p)
print(json.dumps(ledger['stages'][-1]));print(logpath.read_text(encoding='utf8')[-3500:])
