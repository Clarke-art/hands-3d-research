import sys, os, json, hashlib, ast, time
from pathlib import Path
sys.dont_write_bytecode = True
O = Path(__file__).resolve().parent
ROOT = O.parents[1]
OLD = ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1'
MODEL = ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning'
PREV = ROOT/'experiments/hands_fingering_motion_co_design_feasibility_r1'
R2 = ROOT/'experiments/hands_role_aware_motion_recomposition_r2'
SRC = ROOT/'experiments/hands_role_aware_motion_recomposition_r1'
READS = {}; HASHING = False
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
sys.path.insert(0, str(OLD/'_deps'))

def valid_path(p):
    p = Path(p).absolute()
    if not p.is_relative_to(ROOT): raise ValueError('OUTSIDE_HANDS')
    for a in [p,*p.parents]:
        if a.is_relative_to(ROOT) and (a.is_symlink() or a.is_junction()):
            raise ValueError('REPARSE_PATH_FORBIDDEN')
    if not p.resolve().is_relative_to(ROOT) or not p.is_file(): raise ValueError('INVALID_INPUT')
    return p

def sha(p):
    global HASHING
    old=HASHING; HASHING=True
    try:
        h=hashlib.sha256()
        with Path(p).open('rb') as f:
            for b in iter(lambda:f.read(1048576),b''): h.update(b)
        return h.hexdigest()
    finally: HASHING=old

def guard(event,args):
    if event not in ('open','os.listdir','os.scandir','os.mkdir','os.remove','os.rename') or not args or not isinstance(args[0],(str,bytes,os.PathLike)): return
    raw=Path(os.fsdecode(args[0])).absolute()
    if event=='open' and os.fsdecode(args[0]).upper() in ('NUL','\\\\.\\NUL'):
        return  # Windows null device, no persisted filesystem content.
    # Check lexical path before resolution; never enter the excluded project.
    if '/3d interactive components/piano' in raw.as_posix().lower(): raise RuntimeError('PIANO_FORBIDDEN')
    if raw.is_relative_to(ROOT):
        for a in [raw,*raw.parents]:
            if a.is_relative_to(ROOT) and (a.is_symlink() or a.is_junction()): raise RuntimeError('REPARSE_FORBIDDEN')
    p=raw.resolve()
    writing=event in ('os.mkdir','os.remove','os.rename')
    if event=='open':
        mode,flags=args[1:3]
        writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
    if writing and not p.is_relative_to(O): raise RuntimeError('WRITE_OUTSIDE_EXPERIMENT')
    if event=='open' and not writing and not HASHING and p.is_relative_to(ROOT) and not p.is_relative_to(O) and '_deps' not in p.parts and p.is_file():
        if str(p) not in READS: READS[str(p)]=sha(p)
sys.addaudithook(guard)

def read(p): return json.loads(valid_path(p).read_text(encoding='utf-8-sig'))
def encode(x): return x.tolist() if hasattr(x,'tolist') else x.item()
def atomic_json(name,value):
    p=O/name
    if p.exists(): raise FileExistsError(name)
    tmp=p.with_name(p.name+'.partial')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False,default=encode)+'\n',encoding='utf8')
    os.replace(tmp,p)
    assert json.loads(p.read_text(encoding='utf8')) is not None
def archive(p):
    import numpy as np
    with np.load(valid_path(p),allow_pickle=False) as z:
        a={k:z[k].copy() for k in z.files if k!='metadata_utf8'}
        for k,v in a.items():
            if v.dtype.kind not in 'biuf' or not np.isfinite(v).all(): raise ValueError('BAD_ARRAY '+k)
        return a
def atomic_record(name,a,meta=None):
    import numpy as np
    p=O/name
    if p.exists(): raise FileExistsError(name)
    a={k:np.asarray(v) for k,v in a.items()}
    assert all(v.dtype.kind in 'biuf' and np.isfinite(v).all() for v in a.values())
    with p.with_name(p.name+'.partial').open('wb') as f:
        np.savez_compressed(f,**a,metadata_utf8=np.frombuffer(json.dumps(meta or {},ensure_ascii=False,allow_nan=False).encode(),dtype=np.uint8))
        f.flush();os.fsync(f.fileno())
    os.replace(p.with_name(p.name+'.partial'),p)
    b=archive(p);assert a.keys()==b.keys() and all(np.array_equal(a[k],b[k]) for k in a)
def extract(p,names,ns):
    t=ast.parse(valid_path(p).read_text(encoding='utf-8-sig'))
    nodes=[x for x in t.body if isinstance(x,ast.FunctionDef) and x.name in names]
    assert len(nodes)==len(names)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ns)
def protect(name):
    rows=[dict(path=p,before=h,after=sha(p),unchanged=sha(p)==h) for p,h in READS.items()]
    assert all(r['unchanged'] for r in rows)
    atomic_json(name,dict(all_unchanged=True,files=rows,piano_access=False))

