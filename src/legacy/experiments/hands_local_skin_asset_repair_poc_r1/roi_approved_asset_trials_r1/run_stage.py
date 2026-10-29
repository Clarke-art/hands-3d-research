import os,sys,time,json,subprocess
from pathlib import Path
out=Path(__file__).resolve().parent;name=sys.argv[1];tag=name+('_'+sys.argv[2] if len(sys.argv)>2 else '')
env=os.environ.copy();env.update(TEMP=str(out),TMP=str(out),PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONIOENCODING='utf-8')
log=out/(tag+'.log');receipt=out/(tag+'_PROCESS.json');assert not log.exists() and not receipt.exists()
start=time.perf_counter()
with log.open('x',encoding='utf8') as f:
 result=subprocess.run(['D:/blender/blender.exe','--background','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(out/(name+'.py'))],cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT)
with receipt.open('x',encoding='utf8') as f:json.dump({'stage':name,'returncode':result.returncode,'seconds':time.perf_counter()-start},f)
print(log.read_text(encoding='utf8',errors='replace')[-6000:]);sys.exit(result.returncode)
