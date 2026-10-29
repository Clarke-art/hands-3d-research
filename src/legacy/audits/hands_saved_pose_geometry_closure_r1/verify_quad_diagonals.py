"""Conservative depth bounds across either legal diagonal of each cached quad."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
from depth_math import max_triangle_depth
import numpy as np
C,cm=archive(R2/'ACTUAL_BLENDER_STATIC_SKIN.npz');D,dm=archive(MODEL/'SOURCE_MODEL.npz');M=read(MODEL/'SOURCE_MODEL_MANIFEST.json');S=read(O/'ACTUAL_KEY_AND_BVH_SUPPLEMENT.json')
ids=set(np.flatnonzero(D['weights'][:,[i for i,n in enumerate(M['bones']) if n.startswith('LITTLE_')]].sum(1)>.05).tolist())
faces=[(i,f) for i,f in enumerate(M['faces']) if any(v in ids for v in f)]
rows=[]
for ix,t in enumerate(TIMES):
    row=dict(time=t)
    for which in ['baseline','corrected']:
        V=C[which+'_vertices'][ix];L=0.;U=0.;signedU=-float('inf');count=0
        for comp in S['rows'][ix]['actual_key_components']:
            if comp['key_index']==53:continue
            kv=np.array(comp['vertices_world_m']);P=np.array(comp['planes'])
            for fi,f in faces:
                quad=V[f]
                if np.any(quad.max(0)<kv.min(0)-1e-10) or np.any(quad.min(0)>kv.max(0)+1e-10):continue
                assert len(f)==4
                variants=[[(0,1,2),(0,2,3)],[(0,1,3),(1,2,3)]];vl=[];vu=[];vs=[]
                for variant in variants:
                    proof=[max_triangle_depth(quad[list(tr)],P) for tr in variant];count+=len(proof)
                    vl.append(max(p['lower_mm'] for p in proof));vu.append(max(p['upper_mm'] for p in proof));vs.append(max(p['signed_upper_mm'] for p in proof))
                L=max(L,min(vl));U=max(U,max(vu));signedU=max(signedU,max(vs))
        actual=read(O/('POSE_GEOMETRY_'+str(ix)+'.json'))[which]['active_surface_bounds_mm']
        assert L<=actual[0]+1e-7 and U>=actual[1]-1e-7
        row[which]=dict(triangulation_independent_surface_bounds_mm=[L,U],maximum_signed_upper_mm=signedU,triangle_queries=count)
    rows.append(row)
dump('QUAD_DIAGONAL_ROBUSTNESS.json',dict(pass_=True,scope='Full little-influenced cached quads versus all non-target actual key components; both diagonals; no pose regeneration',rows=rows))
print('QUAD_ROBUST_BOUNDS',[(r['time'],r['corrected']['triangulation_independent_surface_bounds_mm']) for r in rows],flush=True)
