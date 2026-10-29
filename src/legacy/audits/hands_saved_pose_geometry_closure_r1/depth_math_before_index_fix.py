"""Triangle/convex-body max signed interior depth, with primal/dual bounds.
Only mesh diagnosis; no action solver, pose optimizer or SciPy dependency.
"""
import numpy as np,itertools
COMBOS={}
def planes_from_mesh(vertices,triangles):
    V=np.asarray(vertices,float);center=V.mean(0);planes=[]
    for tri in triangles:
        a,b,c=V[tri];n=np.cross(b-a,c-a);length=np.linalg.norm(n)
        if length<1e-14:continue
        n/=length
        if n@(center-a)>0:n=-n
        pl=np.r_[n,n@a]
        if not any(np.max(abs(pl-p))<1e-10 for p in planes):planes.append(pl)
    P=np.array(planes)
    err=float(np.max(V@P[:,:3].T-P[:,3]))
    if len(P)<4 or err>1e-7:raise ValueError('NONCONVEX_OR_INVALID_COMPONENT '+str(err))
    return P,err

def max_triangle_depth(T,P):
    T=np.asarray(T,float);P=np.asarray(P,float)
    origin=T[0];e1=T[1]-origin;e2=T[2]-origin
    if np.linalg.norm(np.cross(e1,e2))<1e-15:raise ValueError('DEGENERATE_SKIN_TRIANGLE')
    # x=(u,v,d); d<=h_i-n_i.(p0+u*e1+v*e2); simplex constraints.
    A=np.r_[np.c_[P[:,:3]@e1,P[:,:3]@e2,np.ones(len(P))],[[-1.,0,0],[0,-1.,0],[1,1,0]]]
    b=np.r_[P[:,3]-P[:,:3]@origin,[0.,0.,1.]]
    count=len(A)
    if count not in COMBOS:COMBOS[count]=np.array(list(itertools.combinations(range(count),3)))
    combos=COMBOS[count];mat=A[combos];det=np.linalg.det(mat)
    valid=abs(det)>1e-20;combos=combos[valid];mat=mat[valid]
    if not len(mat):raise ValueError('NO_NONSINGULAR_CERTIFICATE')
    X=np.linalg.solve(mat,b[combos][...,None])[...,0]
    tol=np.r_[np.full(len(P),2e-12),np.full(3,2e-10)]
    feasible=np.all(X@A.T-b<=tol,axis=1)
    if not np.any(feasible):raise ValueError('NO_PRIMAL_VERTEX')
    xf=X[feasible];ix=int(np.argmax(xf[:,2]));x=xf[ix]
    bary=np.maximum([1-x[0]-x[1],x[0],x[1]],0);bary/=sum(bary)
    point=bary@T;raw_lower=float(np.min(P[:,3]-P[:,:3]@point))
    # Every nonnegative lambda with A^T lambda=c is an upper certificate.
    c=np.array([0.,0.,1.]);lambdas=np.linalg.solve(np.swapaxes(mat,1,2),np.broadcast_to(c,(len(mat),3))[...,None])[...,0]
    candidates=np.flatnonzero(np.all(lambdas>=-1e-10,axis=1));duals=[]
    # d is bounded at the optimum by max signed depth of this bounded key neighborhood.
    # For u,v in [0,1], min_i slack <= max absolute corner slack; the maximum
    # is at least each corner depth. Thus |d*| <= D.
    D=float(np.max(abs(T@P[:,:3].T-P[:,3])))+.01
    for j in candidates:
        lam=np.maximum(lambdas[j],0);res=A[combos[j]].T@lam-c
        allowance=abs(res[0])+abs(res[1])+abs(res[2])*D
        upper=float(b[combos[j]]@lam+allowance)
        arithmetic=2e-12*(1+sum(lam))
        duals.append((upper+arithmetic,j,lam,arithmetic))
    if not duals:raise ValueError('NO_DUAL_BOUND')
    upper,j,lam,rounding=min(duals,key=lambda v:v[0]);lower=raw_lower-2e-12
    if upper<lower-1e-11 or upper-lower>1e-8:raise ValueError('UNCLOSED_PRIMAL_DUAL_GAP '+str(upper-lower))
    lower=max(0.,lower);upper=max(0.,upper)
    return dict(lower_mm=lower*1000,upper_mm=upper*1000,gap_mm=(upper-lower)*1000,witness_world_m=point.tolist(),barycentric=bary.tolist(),
        raw_signed_depth_mm=raw_lower*1000,dual_active_constraints=combos[j].tolist(),dual_multipliers=lam.tolist())

def selftest():
    P=np.array([[1,0,0,1],[-1,0,0,0],[0,1,0,1],[0,-1,0,0],[0,0,1,1],[0,0,-1,0]],float)
    cases=[('inside',np.array([[.25,.25,.5],[.75,.25,.5],[.25,.75,.5]]),.5),
        ('outside',np.array([[2,.1,.5],[2,.9,.5],[2.5,.5,.5]]),0.),
        ('tangent',np.array([[0,.1,.5],[0,.9,.5],[0,.5,.8]]),0.),
        ('interior_only',np.array([[-1,.5,.5],[.5,-1,.5],[2,2,.5]]),.5)]
    rows=[]
    for name,T,expected in cases:
        r=max_triangle_depth(T,P);assert r['lower_mm']-1e-6<=expected*1000<=r['upper_mm']+1e-6,(name,r)
        if name=='interior_only':assert np.all(np.maximum(0,np.min(P[:,3]-T@P[:,:3].T,axis=1))==0)
        rows.append(dict(case=name,expected_mm=expected*1000,**r))
    return rows
