import sys,os,time,subprocess,json
from pathlib import Path
O=Path(__file__).resolve().parent
name=sys.argv[1];tag=name+('_'+sys.argv[2] if len(sys.argv)>2 else '')
receipt=O/(tag+'_PROCESS.json');assert not receipt.exists()
blender=name in ['export_baseline','validate_candidate','render_candidate']
cmd=['D:/blender/blender.exe','--background','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(O/(name+'.py'))] if blender else [sys.executable,'-B',str(O/(name+'.py'))]
env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8',TEMP=str(O),TMP=str(O),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
start=time.monotonic()
with (O/(tag+'.log')).open('w',encoding='utf8') as f:
    try:code=subprocess.run(cmd,cwd=O,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900 if blender else 185 if name=='solve_once' else 120).returncode
    except subprocess.TimeoutExpired:code=9
receipt.write_text(json.dumps(dict(stage=name,seconds=time.monotonic()-start,returncode=code,blender=blender),indent=2),encoding='utf8')
print((O/(tag+'.log')).read_text(encoding='utf8',errors='replace')[-4500:],flush=True)
sys.exit(code)
