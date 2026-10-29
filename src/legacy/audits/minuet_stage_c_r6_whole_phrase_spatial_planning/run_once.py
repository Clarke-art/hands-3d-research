from common import *
import subprocess,time,os
lock=read(P/'STRATEGY_LOCK.json')
assert not (P/'FORMAL_ATTEMPT_STARTED.json').exists()
for n,h in lock['code_sha256'].items():assert sha(P/n)==h
started=time.monotonic()
env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
with (P/'formal_solver.log').open('w',encoding='utf8') as log:
    proc=subprocess.Popen([sys.executable,'-u',str(P/'trajectory_solver.py'),'--solve'],stdout=log,stderr=subprocess.STDOUT,env=env)
    try:
        rc=proc.wait(timeout=lock['wall_clock_sec'])
        dump('SUPERVISOR_RECEIPT.json',dict(returncode=rc,wall_clock_sec=time.monotonic()-started,forced_stop=False))
    except subprocess.TimeoutExpired:
        proc.kill();proc.wait()
        dump('SUPERVISOR_RECEIPT.json',dict(returncode=proc.returncode,wall_clock_sec=time.monotonic()-started,forced_stop=True,
            reason='External 1800s watchdog; no restart; last accepted checkpoint retained'))
print('R6_SINGLE_ATTEMPT_PROCESS_FINISHED',flush=True)
