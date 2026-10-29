import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
checks={}
for i,r in enumerate(read(OUT/'FRESH_MACHINE_EVIDENCE_R1.json')['reused']):
 p=ROOT/r['source']['path'];nodes={n.name:digest(ast.dump(n)) for n in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
 checks[str(i)+'_source_bytes']=sha(p)==r['source']['sha256']
 for k,v in r['function_AST_sha256'].items():checks[str(i)+'_'+k]=nodes[k]==v
dump('BLENDER_RUNTIME_AST_VERIFICATION_R1.json',{'status':'PASS' if all(checks.values()) else 'FAIL_CLOSED','checks':checks,'runtime':sys.version,'pose_applications':0,'native_asset_opens':0,'reason':'AST dump serialization differs across bundled Blender Python and system Python; verify byte-exact files and AST digests in originating runtime.'})
assert all(checks.values()),checks
print('ORIGINATING BLENDER RUNTIME AST HASHES PASS',flush=True)
