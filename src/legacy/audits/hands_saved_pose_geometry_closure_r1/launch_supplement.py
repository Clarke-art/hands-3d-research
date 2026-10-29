import sys,os,subprocess,time,json,ast
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
assert json.loads((O/'TOOLCHAIN_PREFLIGHT.json').read_text())['pass_']
assert not (O/'SUPPLEMENT_LAUNCH.json').exists()
ast.parse((O/'supplement_blender.py').read_text(encoding='utf8'))
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONIOENCODING']='utf-8';env['TEMP']=str(O);env['TMP']=str(O)
cmd=['D:/blender/blender.exe','--background','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(O/'supplement_blender.py')]
(O/'SUPPLEMENT_LAUNCH.json').write_text(json.dumps(dict(command=cmd,reason='Missing actual key/triangle/BVH records; do not regenerate corrected skin',start_unix=time.time()),indent=2),encoding='utf8')
start=time.perf_counter()
with (O/'supplement_blender.log').open('w',encoding='utf8') as f:
    try:ret=subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,env=env,timeout=180).returncode
    except subprocess.TimeoutExpired:ret=9
(O/'SUPPLEMENT_PROCESS.json').write_text(json.dumps(dict(returncode=ret,seconds=time.perf_counter()-start),indent=2),encoding='utf8')
print((O/'supplement_blender.log').read_text(encoding='utf8',errors='replace')[-4000:])
sys.exit(ret)
