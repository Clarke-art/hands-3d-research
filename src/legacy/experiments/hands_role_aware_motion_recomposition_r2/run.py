import sys,os,subprocess,time,json
from pathlib import Path
O=Path(__file__).resolve().parent;name=sys.argv[1];is_blender=name in ['stage0_blender','validate_blender','bake_visual']
tag=name
if len(sys.argv)>2:
    assert is_blender and name!='bake_visual' and sys.argv[2].startswith('software_retry_')
    tag=name+'_'+sys.argv[2]
receipt=O/(tag+'_PROCESS.json');assert not receipt.exists(),'NO_AUTOMATIC_STAGE_RETRY'
cmd=['D:/blender/blender.exe','--background','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(O/(name+'.py'))] if is_blender else [sys.executable,'-B',str(O/(name+'.py'))]
env=os.environ.copy();env.update(PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1',TEMP=str(O),TMP=str(O),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
start=time.monotonic()
with (O/(tag+'.log')).open('w',encoding='utf8') as f:
    try:code=subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,env=env,timeout=300 if is_blender else 185 if name=='generate' else 60).returncode
    except subprocess.TimeoutExpired:code=9
receipt.write_text(json.dumps(dict(returncode=code,seconds=time.monotonic()-start,blender=is_blender),indent=2),encoding='utf8')
print((O/(tag+'.log')).read_text(encoding='utf8',errors='replace')[-4500:],flush=True)
sys.exit(code)
