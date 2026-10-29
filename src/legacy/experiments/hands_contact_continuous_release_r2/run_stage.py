"""Single cumulative 300s ledger, including startup and failed child processes."""
import sys,time,json,subprocess
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
name=sys.argv[1];assert name in ['prepare','setup','solve_path','validation_request','validate_path','bake','render','close']
ledger_path=P/'COMPUTE_LEDGER.json'
ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else dict(limit_seconds=300,stages=[],used_seconds=0.)
remaining=300-ledger['used_seconds'];assert remaining>0
blender=name in ['validate_path','bake','render']
cmd=['D:/Blender/blender.exe','-b','--factory-startup','--python',str(P/(name+'.py'))] if blender else [sys.executable,'-B',str(P/(name+'.py'))]
cap=min(remaining,215 if name=='solve_path' else remaining)
started=time.perf_counter();path=P/(name+'_'+str(len(ledger['stages']))+'.log')
with path.open('w',encoding='utf8') as log:
    try:
        proc=subprocess.run(cmd,cwd=P,stdout=log,stderr=subprocess.STDOUT,timeout=cap)
        status='RETURNED';code=proc.returncode
    except subprocess.TimeoutExpired:status='WATCHDOG_STOP';code=None
elapsed=time.perf_counter()-started
ledger['stages'].append(dict(name=name,elapsed_seconds=elapsed,status=status,returncode=code,log=path.name,cap_seconds=cap))
ledger['used_seconds']+=elapsed;ledger['remaining_seconds']=max(0,300-ledger['used_seconds'])
ledger_path.write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf8')
print(json.dumps(ledger['stages'][-1]));print(path.read_text(encoding='utf8')[-2000:])
