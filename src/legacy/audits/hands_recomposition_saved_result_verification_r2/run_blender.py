"""Read-only Blender diagnostic launcher; no retry or solver calls."""
import os,sys,subprocess,time,json,ast
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
assert not (O/'BLENDER_LAUNCH_0.json').exists(),'NO_DUPLICATE_BATCH_LAUNCH'
assert json.loads((O/'INPUT_CONTRACT_GATE.json').read_text())['pass_']
for n in ['source_actual.py','blender_helpers.py','contract.py','support.py','model.py','persistence.py']:
    ast.parse((O/n).read_text(encoding='utf8'))
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONIOENCODING']='utf-8';env['TEMP']=str(O);env['TMP']=str(O)
env['OPENBLAS_NUM_THREADS']='1';env['OMP_NUM_THREADS']='1'
cmd=['D:/blender/blender.exe','--background','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(O/'source_actual.py')]
receipt=dict(command=cmd,start_unix=time.time(),timeout_seconds=180,optimizer_calls=0)
(O/'BLENDER_LAUNCH_0.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
start=time.perf_counter()
with (O/'blender_attempt_0.log').open('w',encoding='utf8') as f:
    try:
        proc=subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,env=env,timeout=180)
        status='RETURNED';code=proc.returncode
    except subprocess.TimeoutExpired:
        status='TIMEOUT';code=None
(O/'BLENDER_PROCESS_0.json').write_text(json.dumps(dict(status=status,returncode=code,seconds=time.perf_counter()-start),indent=2),encoding='utf8')
print(status,code,flush=True)
print((O/'blender_attempt_0.log').read_text(encoding='utf8',errors='replace')[-4000:],flush=True)
sys.exit(code if code is not None else 9)
