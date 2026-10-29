import sys,os,json,hashlib,ast,time
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
C1=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance'
OLD=ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1'
os.environ.update(TEMP=str(OUT),TMP=str(OUT),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
READS={};HASHING=False
def safe(p):
    p=Path(p).absolute()
    if not p.is_relative_to(ROOT):raise ValueError('OUTSIDE_HANDS')
    if any(a.is_symlink() or a.is_junction() for a in [p,*p.parents] if a.is_relative_to(ROOT)):raise ValueError('REPARSE_FORBIDDEN')
    if not p.resolve().is_relative_to(ROOT):raise ValueError('RESOLVED_OUTSIDE_HANDS')
    return p
def sha(p):
    global HASHING
    before=HASHING;HASHING=True
    try:
        h=hashlib.sha256()
        with safe(p).open('rb') as f:
            for b in iter(lambda:f.read(1048576),b''):h.update(b)
        return h.hexdigest()
    finally:HASHING=before
def guard(event,args):
    if event not in ('open','os.listdir','os.scandir','os.mkdir','os.remove','os.rename') or not args or not isinstance(args[0],(str,bytes,os.PathLike)):return
    raw=Path(os.fsdecode(args[0])).absolute()
    if '/3d interactive components/piano' in raw.as_posix().lower():raise RuntimeError('PIANO_FORBIDDEN')
    if event=='open' and os.fsdecode(args[0]).upper() in ('NUL','\\\\.\\NUL'):return
    p=safe(raw) if raw.is_relative_to(ROOT) else raw.resolve()
    writing=event in ('os.mkdir','os.remove','os.rename')
    if event=='open':
        mode,flags=args[1:3];writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
    if writing and not p.is_relative_to(OUT):raise RuntimeError('WRITE_OUTSIDE_EXPERIMENT')
    if event=='open' and not writing and not HASHING and p.is_relative_to(ROOT) and not p.is_relative_to(OUT) and '_deps' not in p.parts and p.is_file():
        if str(p) not in READS:READS[str(p)]=sha(p)
sys.addaudithook(guard)
def read(p):return json.loads(safe(p).read_text(encoding='utf-8-sig'))
def encode(x):return x.tolist() if hasattr(x,'tolist') else x.item()
def save(name,value):
    p=OUT/name
    with p.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False,default=encode)
def extract(p,names,ns):
    tree=ast.parse(safe(p).read_text(encoding='utf-8-sig'));nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
    assert len(nodes)==len(names);exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ns)
def protection(name):
    rows=[dict(path=p,before=h,after=sha(p),unchanged=sha(p)==h) for p,h in READS.items()]
    assert all(r['unchanged'] for r in rows);save(name,dict(all_unchanged=True,files=rows,piano_access=False))
MAN=read(C1/'SCENE_MANIFEST.json');SOURCE=safe(MAN['path'])
assert sha(SOURCE)==MAN['sha256']=='d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7'
READS[str(SOURCE)]=sha(SOURCE)
NOTES=read(C1/'PERFORMANCE_TIMELINE.json')['notes']
START,END=4.4,5.6
