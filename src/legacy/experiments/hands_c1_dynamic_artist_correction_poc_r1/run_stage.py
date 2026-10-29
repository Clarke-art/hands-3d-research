import os,sys,time,json,subprocess
from pathlib import Path
O=Path(__file__).resolve().parent;name=sys.argv[1];tag=name+('_'+sys.argv[2] if len(sys.argv)>2 else '')
log=O/(tag+'.log');receipt=O/(tag+'_PROCESS.json')
assert not log.exists() and not receipt.exists()
env=os.environ.copy();env.update(TEMP=str(O),TMP=str(O),PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONIOENCODING='utf-8')
cmd=['D:/blender/blender.exe','--background','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(O/(name+'.py'))]
begin=time.perf_counter()
with log.open('x',encoding='utf8') as f:
    try:code=subprocess.run(cmd,cwd=O,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=2400).returncode
    except subprocess.TimeoutExpired:code=9
with receipt.open('x',encoding='utf8') as f:json.dump(dict(stage=name,seconds=time.perf_counter()-begin,returncode=code),f,indent=2)
print(log.read_text(encoding='utf8',errors='replace')[-5000:],flush=True);sys.exit(code)
