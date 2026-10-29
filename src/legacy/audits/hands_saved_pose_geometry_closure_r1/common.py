import sys,os,json,hashlib,ast
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;ROOT=O.parents[1]
R2=ROOT/'audits/hands_recomposition_saved_result_verification_r2'
SRC=ROOT/'experiments/hands_role_aware_motion_recomposition_r1'
OLD=ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1'
MODEL=ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning'
TIMES=[1.7,2.,2.0625]
READS={};IN_HASH=False
def sha(p):
    global IN_HASH
    IN_HASH=True
    try:
        h=hashlib.sha256()
        with Path(p).open('rb') as f:
            for b in iter(lambda:f.read(1048576),b''):h.update(b)
        return h.hexdigest()
    finally:IN_HASH=False
def path(raw):
    p=Path(raw)
    if not p.is_absolute() or not p.is_relative_to(ROOT):raise ValueError('INPUT_PATH_OUTSIDE_HANDS')
    if any(x.is_symlink() or x.is_junction() for x in [p,*p.parents] if x.is_relative_to(ROOT)):raise ValueError('REPARSE_PATH_REJECTED')
    if not p.resolve().is_relative_to(ROOT) or not p.is_file():raise ValueError('INPUT_PATH_INVALID')
    return p
def guard(event,args):
    if event not in ['open','os.listdir','os.scandir','os.mkdir','os.remove','os.rename'] or not args or not isinstance(args[0],(str,bytes,os.PathLike)):return
    p=Path(os.fsdecode(args[0])).resolve()
    if '/3d interactive components/piano' in p.as_posix().lower():raise RuntimeError('PIANO_ACCESS_FORBIDDEN')
    writing=event in ['os.mkdir','os.remove','os.rename']
    if event=='open':
        mode,flags=args[1:3];writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
    if writing and not p.is_relative_to(O):raise RuntimeError('WRITE_OUTSIDE_CURRENT_AUDIT')
    if event=='open' and not writing and not IN_HASH and p.is_relative_to(ROOT) and not p.is_relative_to(O) and p.is_file() and '_deps' not in p.parts:
        if str(p) not in READS:READS[str(p)]=sha(p)
sys.addaudithook(guard)
def read(p):return json.loads(path(p).read_text(encoding='utf-8-sig'))
def dump(n,v):
    p=O/n
    if p.exists():raise FileExistsError('EVIDENCE_ALREADY_EXISTS '+n)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')
def archive(p):
    import numpy as np
    with np.load(path(p),allow_pickle=False) as z:
        a={k:z[k].copy() for k in z.files if k!='metadata_utf8'}
        for k,v in a.items():
            if v.dtype.kind not in 'biuf' or not np.isfinite(v).all():raise ValueError('NONFINITE_OR_NONNUMERIC '+k)
        meta=json.loads(z['metadata_utf8'].tobytes()) if 'metadata_utf8' in z else {}
    return a,meta
def extract(p,names,ns):
    t=ast.parse(path(p).read_text(encoding='utf-8-sig'));nodes=[x for x in t.body if isinstance(x,ast.FunctionDef) and x.name in names]
    assert len(nodes)==len(names)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ns)
def snapshot(n):dump(n,READS)
