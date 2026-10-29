import sys, os, json, hashlib, time, ast
from pathlib import Path
sys.dont_write_bytecode=True
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
O=Path(__file__).resolve().parent
ROOT=O.parents[1]
OLD=ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1'
C1=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance'
A2=ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion'
PREV=ROOT/'experiments/hands_fingering_motion_co_design_feasibility_r1'
MODEL=ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning'
READS={}; HASHING=False
def sha(p):
 global HASHING
 HASHING=True
 try:
  h=hashlib.sha256()
  with Path(p).open('rb') as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b)
  return h.hexdigest()
 finally:HASHING=False
def guard(event,args):
 if event not in ('open','os.listdir','os.scandir','os.mkdir','os.remove','os.rename'):return
 if not args or not isinstance(args[0],(str,bytes,os.PathLike)):return
 raw=os.fsdecode(args[0])
 if raw.lower() in ('nul','\\\\.\\nul'):return
 p=Path(raw).resolve()
 if '/3d interactive components/piano' in p.as_posix().lower():raise RuntimeError('FORBIDDEN_PIANO_ACCESS')
 write=event in ('os.mkdir','os.remove','os.rename')
 if event=='open':
  mode,flags=args[1:3]
  write=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
 if write and not p.is_relative_to(O):raise RuntimeError('WRITE_OUTSIDE_EXPERIMENT')
 if event=='open' and not write and not HASHING and p.is_relative_to(ROOT) and not p.is_relative_to(O) and '_deps' not in p.parts and p.is_file():
  if str(p) not in READS:READS[str(p)]=sha(p)
sys.addaudithook(guard)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n,x):
 (O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else v.item())+'\n',encoding='utf8')
def protect():
 prior=read(O/'PROTECTED_BEFORE.json') if (O/'PROTECTED_BEFORE.json').exists() else {}
 prior.update(READS);dump('PROTECTED_BEFORE.json',prior)
def functions_from(path,names,namespace):
 tree=ast.parse(Path(path).read_text(encoding='utf-8-sig'))
 nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
 assert len(nodes)==len(names)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),namespace)
