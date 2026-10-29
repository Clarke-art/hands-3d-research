"""Independent primal/dual readback and full active-region CLEAR certificate."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import numpy as np
from depth_math import max_triangle_depth

def check(proof,T,P):
    bary=np.array(proof['barycentric']);assert min(bary)>=-1e-12 and abs(sum(bary)-1)<1e-12
    point=bary@T;assert np.linalg.norm(point-proof['witness_world_m'])<1e-12
    inside=float(np.min(P[:,3]-P[:,:3]@point))*1000
    assert proof['lower_mm']<=max(0.,inside)+1e-9
    a=np.column_stack([P[:,:3]@(T[1]-T[0]),P[:,:3]@(T[2]-T[0]),np.ones(len(P))])
    A=np.r_[a,[[-1.,0,0],[0,-1.,0],[1,1,0]]];b=np.r_[P[:,3]-P[:,:3]@T[0],[0.,0.,1.]]
    ids=proof['dual_active_constraints'];lam=np.array(proof['dual_multipliers']);assert min(lam)>=0
    res=A[ids].T@lam-[0,0,1];D=float(np.max(abs(T@P[:,:3].T-P[:,3])))+.01
    certified=(b[ids]@lam+abs(res[0])+abs(res[1])+abs(res[2])*D)*1000
    assert proof['upper_mm']+1e-9>=max(0.,certified)
    assert np.max(abs(np.linalg.norm(P[:,:3],axis=1)-1))<1e-12
    return float(proof['upper_mm']-proof['lower_mm'])

def run():
    C,cm=archive(R2/'ACTUAL_BLENDER_STATIC_SKIN.npz');TT,tm=archive(O/'ACTUAL_TRIANGULATION_AND_KEY_CLOCK.npz');SUP=read(O/'ACTUAL_KEY_AND_BVH_SUPPLEMENT.json')
    W,wm=archive(MODEL/'SOURCE_MODEL.npz');M=read(MODEL/'SOURCE_MODEL_MANIFEST.json');ids=np.flatnonzero(W['weights'][:,[i for i,n in enumerate(M['bones']) if n.startswith('LITTLE_')]].sum(1)>.05)
    checked=0;gaps=[];active_rows=[]
    for ix,t in enumerate(TIMES):
        components=SUP['rows'][ix]['actual_key_components'];byname={g['name']:g for g in components}
        proofs=read(O/('TRIANGLE_DEPTH_CERTIFICATES_'+str(ix)+'.json'))
        for which in ['baseline','corrected']:
            V=C[which+'_vertices'][ix];T=TT[which+'_triangles_'+str(ix)]
            for r in proofs[which]:gaps.append(check(r,V[T[r['triangle']]],np.array(byname[r['component']]['planes'])));checked+=1
        V=C['corrected_vertices'][ix];T=TT['corrected_triangles_'+str(ix)];pid=TT['corrected_triangle_polygon_'+str(ix)]
        active=np.any(np.isin(T,ids),axis=1);tv=V[T];lo=tv.min(1);hi=tv.max(1);rows=[]
        for g in components:
            if g['key_index']==53:continue
            kv=np.array(g['vertices_world_m']);P=np.array(g['planes'])
            candidate=np.flatnonzero(active&np.all(hi>=kv.min(0)-1e-10,axis=1)&np.all(lo<=kv.max(0)+1e-10,axis=1))
            for ti in candidate:
                proof=max_triangle_depth(tv[ti],P);check(proof,tv[ti],P)
                rows.append(dict(key=g['note'],component=g['name'],triangle=int(ti),polygon=int(pid[ti]),skin_vertices=T[ti],**proof))
        L=max((r['lower_mm'] for r in rows),default=0.);U=max((r['upper_mm'] for r in rows),default=0.)
        raw_U=max((r['signed_upper_mm'] for r in rows),default=-1.)
        expected=read(O/('POSE_GEOMETRY_'+str(ix)+'.json'))['corrected']['active_surface_bounds_mm'];assert np.allclose([L,U],expected,rtol=0,atol=1e-9)
        active_rows.append(dict(time=t,candidate_count=len(rows),complete_non_target_surface_bounds_mm=[L,U],max_signed_upper_mm=raw_U,certificates=rows))
    dump('DEPTH_CERTIFICATE_READBACK.json',dict(pass_=True,stored_nonzero_certificates_checked=checked,max_stored_interval_width_mm=max(gaps),
        active_complete_certificates=active_rows,clearance_20625_proven=active_rows[2]['max_signed_upper_mm']<0,geometry_depth_solver='NumPy constraint enumeration only; no SciPy or action optimization'))
    snapshot('CERTIFICATE_INPUT_SHA.json')
    print('DEPTH_CERTIFICATES_VERIFIED',checked,'signed_max_last_mm',active_rows[2]['max_signed_upper_mm'],flush=True)

if __name__=='__main__':run()
