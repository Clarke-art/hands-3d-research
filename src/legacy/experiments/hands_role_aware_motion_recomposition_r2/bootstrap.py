import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from support import *
sys.path.insert(0,str(OLD/'_deps'))
import numpy as np
from persistence import atomic_json,atomic_record
SRC=ROOT/'experiments/hands_role_aware_motion_recomposition_r1'
CLOSE=ROOT/'audits/hands_saved_pose_geometry_closure_r1'
def archive(p):
    with np.load(p,allow_pickle=False) as z:
        a={k:z[k].copy() for k in z.files if k!='metadata_utf8'}
        assert all(v.dtype.kind in 'biuf' and np.isfinite(v).all() for v in a.values())
        meta=json.loads(z['metadata_utf8'].tobytes()) if 'metadata_utf8' in z else {}
    return a,meta
def valid_path(p):
    p=Path(p)
    assert p.is_absolute() and p.is_relative_to(ROOT)
    assert not any(x.is_symlink() or x.is_junction() for x in [p,*p.parents] if x.is_relative_to(ROOT))
    assert p.resolve().is_relative_to(ROOT) and p.is_file()
    return p
def unique_times(values):
    out=[]
    for t in sorted(values):
        if not out or t-out[-1]>1e-7:out.append(float(t))
    return np.array(out)
