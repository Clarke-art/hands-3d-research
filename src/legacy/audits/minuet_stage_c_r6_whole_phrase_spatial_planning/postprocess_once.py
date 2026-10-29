"""Wait for the existing sole solve, then measure its unchanged terminal state."""
from common import *
import subprocess,time,os
while not (P/'SUPERVISOR_RECEIPT.json').exists():time.sleep(1)
assert (P/'FORMAL_ATTEMPT_STARTED.json').exists()
env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
steps=[('numeric_terminal',[sys.executable,str(P/'prepare_validation.py')]),
    ('actual_blender',[r'D:\Blender\blender.exe','-b','--factory-startup','--python',str(P/'validate_actual.py')]),
    ('skin_parity',[sys.executable,str(P/'check_terminal_parity.py')]),
    ('reports',[sys.executable,str(P/'finish_reports.py')])]
for name,cmd in steps:
    dump('POSTPROCESS_PROGRESS.json',dict(stage=name,status='RUNNING',optimization_calls=0))
    with (P/(name+'.log')).open('w',encoding='utf8') as log:
        result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=env)
    if result.returncode:
        dump('POSTPROCESS_PROGRESS.json',dict(stage=name,status='FAILED',returncode=result.returncode,optimization_calls=0))
        raise RuntimeError(name+' failed; inspect its log; do not rerun solver')
    print('R6_POSTPROCESS',name,'finished',flush=True)
dump('POSTPROCESS_PROGRESS.json',dict(stage='complete',status='COMPLETE',optimization_calls=0))
