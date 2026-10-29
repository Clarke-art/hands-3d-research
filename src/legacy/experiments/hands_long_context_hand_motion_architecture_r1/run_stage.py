import sys,os,time,json,subprocess
from pathlib import Path
O=Path(__file__).resolve().parent;os.environ['PYTHONUTF8']='1';os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
name,cap,script=sys.argv[1:4];f=O/'NUMERICAL_BUDGET.json';b=json.loads(f.read_text()) if f.exists() else dict(limit_seconds=600,stages=[])
remaining=600-sum(r['wall_seconds'] for r in b['stages']);assert remaining>0;cap=min(float(cap),remaining)
assert not json.loads((O/'POLICY_LOCK.json').read_text())['no_more_solves'];start=time.monotonic();status='COMPLETED'
with (O/'logs'/f'{name}.log').open('w',encoding='utf-8') as log:
 p=subprocess.Popen([sys.executable,'-B',str(O/script)],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 try:code=p.wait(timeout=cap)
 except subprocess.TimeoutExpired:
  status='GLOBAL_OR_STAGE_DEADLINE';subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],capture_output=True);code=-9
b['stages'].append(dict(name=name,script=script,wall_seconds=time.monotonic()-start,cap_seconds=cap,exit_code=code,status=status));b['total_seconds']=sum(r['wall_seconds'] for r in b['stages']);b['under_budget']=b['total_seconds']<=600;f.write_text(json.dumps(b,indent=2));print(json.dumps(b['stages'][-1]));sys.exit(0 if code==0 else 1)
