import numpy as np
# Exact closest features for disjoint triangles: point-face and edge-edge.
def distances(A,B):
 n=len(A);best=np.full(n,np.inf);pa=np.zeros((n,3));pb=pa.copy()
 def update(P,Q,valid=None):
  d=np.sum((P-Q)**2,axis=1);ok=d<best
  if valid is not None:ok &= valid
  best[ok]=d[ok];pa[ok]=P[ok];pb[ok]=Q[ok]
 for T,U,swap in [(A,B,False),(B,A,True)]:
  e=U[:,1]-U[:,0];f=U[:,2]-U[:,0];normal=np.cross(e,f);nn=np.sum(normal*normal,axis=1)
  ee=np.sum(e*e,axis=1);ef=np.sum(e*f,axis=1);ff=np.sum(f*f,axis=1);den=ee*ff-ef*ef
  for i in range(3):
   P=T[:,i];Q=P-normal*(np.sum((P-U[:,0])*normal,axis=1)/np.maximum(nn,1e-30))[:,None]
   w=Q-U[:,0];we=np.sum(w*e,axis=1);wf=np.sum(w*f,axis=1)
   a=(we*ff-wf*ef)/np.maximum(den,1e-30);b=(wf*ee-we*ef)/np.maximum(den,1e-30)
   valid=(a>=-1e-12)&(b>=-1e-12)&(a+b<=1+1e-12)&(den>1e-30)
   update(Q,P,valid) if swap else update(P,Q,valid)
   for j in range(3):
    E=U[:,(j+1)%3]-U[:,j];t=np.clip(np.sum((P-U[:,j])*E,axis=1)/np.maximum(np.sum(E*E,axis=1),1e-30),0,1);Q=U[:,j]+t[:,None]*E
    update(Q,P) if swap else update(P,Q)
 for i in range(3):
  P=A[:,i];e=A[:,(i+1)%3]-P
  for j in range(3):
   Q=B[:,j];f=B[:,(j+1)%3]-Q;w=P-Q
   ee=np.sum(e*e,1);ef=np.sum(e*f,1);ff=np.sum(f*f,1);ew=np.sum(e*w,1);fw=np.sum(f*w,1);den=ee*ff-ef*ef
   s=(ef*fw-ff*ew)/np.maximum(den,1e-30);t=(ee*fw-ef*ew)/np.maximum(den,1e-30)
   valid=(den>1e-30)&(s>=0)&(s<=1)&(t>=0)&(t<=1)
   update(P+s[:,None]*e,Q+t[:,None]*f,valid)
 return np.sqrt(best),pa,pb

def exact_clearance(V,TR,ia,ib,neighbors,upper):
 A=V[TR[ia]];B=V[TR[ib]];alo=A.min(1);ahi=A.max(1);blo=B.min(1);bhi=B.max(1);pairs=[]
 for i in range(len(ia)):
  delta=np.maximum(np.maximum(blo-ahi[i],alo[i]-bhi),0);ids=np.flatnonzero(np.sum(delta*delta,1)<=upper*upper+1e-18)
  for j in ids:
   ta=int(ia[i]);tb=int(ib[j])
   if tb in neighbors[ta] or set(TR[ta])&set(TR[tb]):continue
   pairs.append((i,j))
 if not pairs:return dict(distance_mm=None,reason='no nonadjacent candidate within supplied upper bound')
 pairs=np.array(pairs);d,p,q=distances(A[pairs[:,0]],B[pairs[:,1]]);k=int(np.argmin(d));i,j=pairs[k]
 return dict(distance_mm=float(d[k]*1000),triangle_ids=[int(ia[i]),int(ib[j])],witness_points_world_m=[p[k].tolist(),q[k].tolist()],exact_feature_candidates=len(pairs),aabb_pruning_upper_mm=upper*1000,method='All nonadjacent triangle pairs with AABB lower bound <= sampled upper; exact point-face and all edge-edge feature minima for disjoint triangles')
