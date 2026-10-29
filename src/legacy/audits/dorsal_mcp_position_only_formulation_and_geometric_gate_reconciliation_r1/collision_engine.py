import sys
sys.dont_write_bytecode=True
from contact_geometry import *

COMMON={}
def common(i,j):
 key=(int(i),int(j))
 if key not in COMMON:COMMON[key]=sorted(set(F[int(owners[i])])&set(F[int(owners[j])]))
 return COMMON[key]

def broad(v,ids,band=1e-8,end=None):
 t=(v-origin)[tri];lo=t.min(1);hi=t.max(1)
 if end is not None:
  z=(end-origin)[tri];lo=np.minimum(lo,z.min(1));hi=np.maximum(hi,z.max(1))
 affected=face_domain(ids);ch=np.where(np.isin(owners,list(affected)))[0];pairs=set()
 for i in ch:
  for j in np.where(np.all(hi>=lo[i]-band,axis=1)&np.all(lo<=hi[i]+band,axis=1))[0]:
   if i!=j and owners[i]!=owners[j]:pairs.add(tuple(sorted((int(i),int(j)))))
 return np.array(sorted(pairs),dtype=int).reshape(-1,2)

def exact(v,ids):
 pairs=broad(v,ids);t=(v-origin)[tri];found={};point_eps=1e-8
 if not len(pairs):return found,0
 a=t[pairs[:,0]];b=t[pairs[:,1]];hitsets=[[] for _ in pairs]
 for aa,bb in [(a,b),(b,a)]:
  e1=bb[:,1]-bb[:,0];e2=bb[:,2]-bb[:,0]
  for k in range(3):
   p=aa[:,k];d=aa[:,(k+1)%3]-p;h=np.cross(d,e2);det=np.sum(e1*h,axis=1);good=abs(det)>1e-12;inv=np.where(good,1/np.where(good,det,1),0);s=p-bb[:,0];u=np.sum(s*h,axis=1)*inv;q=np.cross(s,e1);w=np.sum(d*q,axis=1)*inv;tt=np.sum(e2*q,axis=1)*inv
   good&=(u>=-1e-10)&(w>=-1e-10)&(u+w<=1+1e-10)&(tt>=-1e-10)&(tt<=1+1e-10)
   for ix in np.where(good)[0]:hitsets[ix].append(p[ix]+d[ix]*tt[ix])
 na=np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]);nb=np.cross(b[:,1]-b[:,0],b[:,2]-b[:,0]);nalen=np.linalg.norm(na,axis=1);nblen=np.linalg.norm(nb,axis=1);un=na/np.maximum(nalen[:,None],1e-30);vn=nb/np.maximum(nblen[:,None],1e-30)
 cop=(np.linalg.norm(np.cross(un,vn),axis=1)<1e-8)&(np.max(abs(np.sum((b-a[:,0,None,:])*un[:,None,:],axis=2)),axis=1)<1e-7)
 for ix,(i,j) in enumerate(pairs):
  pts=hitsets[ix];shared=common(i,j);key=tuple(sorted((int(owners[i]),int(owners[j]))))
  if cop[ix]:
   area=coplanar_overlap(a[ix],b[ix])
   if area>1e-8:found[key]={'kind':'COPLANAR_AREA_OVERLAP','area_mm2':float(area),'shared_vertex_ids':shared};continue
  if not pts:continue
  if len(shared)==1:away=max(np.linalg.norm(p-(v[shared[0]]-origin)) for p in pts)
  elif len(shared)==2:away=max(point_seg_dist(p,v[shared[0]]-origin,v[shared[1]]-origin) for p in pts)
  elif len(shared)>2:continue
  else:away=float('inf')
  length=max((np.linalg.norm(p-q) for p in pts for q in pts),default=0.)
  if away>point_eps:found[key]={'kind':'EXACT_POINT_CONTACT' if length<=point_eps else 'SEGMENT_CROSSING_AWAY_FROM_SHARED_TOPOLOGY','segment_mm':float(length),'away_from_shared_contact_mm':float(away) if np.isfinite(away) else None,'shared_vertex_ids':shared}
 return found,len(pairs)

def near_constraints(v,ids,W,index,direction,band=.05,clearance=1e-6):
 pairs=broad(v,ids,band=band,end=v+direction);active=[];tested=0
 for i,j in pairs:
  if common(i,j):continue
  m=tri_pair_metrics(v,tri[i],tri[j]);tested+=1
  if m['intersection_points_world_mm']:continue # Frozen baseline families are independent.
  p,q=np.array(m['closest_world_mm']);dist=np.linalg.norm(p-q)
  if dist<1e-12:continue
  axis=(p-q)/dist;wa=np.array(m['a_weights']);wb=np.array(m['b_weights']);g=np.zeros((len(index),3))
  for vi,w in zip(tri[i],wa):
   if vi in index:g[index[vi]]+=w*axis
  for vi,w in zip(tri[j],wb):
   if vi in index:g[index[vi]]-=w*axis
  change=sum(w*(direction[vi]@axis) for vi,w in zip(tri[i],wa))-sum(w*(direction[vi]@axis) for vi,w in zip(tri[j],wb))
  gap=min(clearance,dist*.5)
  if dist+change<gap:
   correction=W@g;denom=float(np.sum(g*correction))
   if denom>1e-18:
    direction[list(index)]+=correction*(gap-dist-change)/denom
    active.append({'triangle_indices':[int(i),int(j)],'face_ids':[int(owners[i]),int(owners[j])],'distance_mm':float(dist),'feature_kind':m['feature_kind'],'a_vertex_ids':m['a_vertex_ids'],'b_vertex_ids':m['b_vertex_ids'],'a_weights':m['a_weights'],'b_weights':m['b_weights'],'side_axis':axis.tolist(),'computational_gap_mm':gap})
 return direction,active,tested,len(pairs)

def ccd(v,end,ids,baseline_pairs):
 # Every possible collision under linear vertex motion must have a four-point
 # coplanarity event: a vertex on a face, or two edges meeting. Solve cubic
 # event times on swept whole-mesh AABBs, then exclude only actual shared
 # vertex/edge contact. Endpoint checks also cover permanent coplanarity.
 pairs=broad(v,ids,end=end);d=end-v;events=set();roots_checked=0;all_features=[];feature_pairs=[]
 for i,j in pairs:
  key=tuple(sorted((int(owners[i]),int(owners[j]))))
  if key in baseline_pairs:continue
  aa=tri[i];bb=tri[j];quads=[]
  for p in aa:quads.append((int(p),*map(int,bb)))
  for p in bb:quads.append((int(p),*map(int,aa)))
  for k in range(3):
   for l in range(3):quads.append((int(aa[k]),int(aa[(k+1)%3]),int(bb[l]),int(bb[(l+1)%3])))
  for z in sorted(set(quads)):
   if len(set(z))==4:all_features.append(z);feature_pairs.append((int(i),int(j)))
 if all_features:
  z=np.array(all_features);p=v[z];delta=d[z];u=p[:,1:]-p[:,0,None,:];w=delta[:,1:]-delta[:,0,None,:]
  dot=lambda a,b:np.sum(a*b,axis=1)
  c0=dot(u[:,0],np.cross(u[:,1],u[:,2]));c1=dot(w[:,0],np.cross(u[:,1],u[:,2]))+dot(u[:,0],np.cross(w[:,1],u[:,2]))+dot(u[:,0],np.cross(u[:,1],w[:,2]));c2=dot(w[:,0],np.cross(w[:,1],u[:,2]))+dot(w[:,0],np.cross(u[:,1],w[:,2]))+dot(u[:,0],np.cross(w[:,1],w[:,2]));c3=dot(w[:,0],np.cross(w[:,1],w[:,2]));co=np.column_stack([c0,c1,c2,c3]);bern=np.column_stack([c0,c0+c1/3,c0+2*c1/3+c2/3,c0+c1+c2+c3]);possible=~(np.all(bern>1e-12,axis=1)|np.all(bern<-1e-12,axis=1))
  for row in np.where(possible)[0]:
   coeff=co[row];last=next((k for k in range(3,-1,-1) if abs(coeff[k])>1e-12),-1)
   if last<1:continue
   i,j=feature_pairs[row]
   for r in np.roots(coeff[:last+1][::-1]):
    if abs(r.imag)<1e-7 and 1e-8<r.real<1-1e-8:events.add((i,j,round(float(r.real),11)))
 for i,j,tau in sorted(events):
  vv=v+tau*d;mm=tri_pair_metrics(vv,tri[i],tri[j]);pts=mm['intersection_points_world_mm'];roots_checked+=1
  if not pts:continue
  shared=common(i,j)
  if len(shared)==1:away=max(np.linalg.norm(p-vv[shared[0]]) for p in np.array(pts))
  elif len(shared)==2:away=max(point_seg_dist(p,vv[shared[0]],vv[shared[1]]) for p in np.array(pts))
  elif len(shared)>2:continue
  else:away=float('inf')
  if away>1e-7:return False,{'face_ids':[int(owners[i]),int(owners[j])],'fraction':tau,'kind':'COPLANARITY_EVENT_CROSSING','swept_pairs':len(pairs),'event_roots_checked':roots_checked}
 return True,{'swept_pairs':len(pairs),'event_roots_checked':roots_checked,'event_count':len(events)}

def signed_volume(v,z):
 p=v[list(z)];u=p[1:]-p[0];return float(u[0]@np.cross(u[1],u[2]))

def contact_direction_projection(v,ids,W,index,direction,baseline_pairs,maxpasses=5):
 # Adjacent native quads can contact away from their legal common edge even
 # though the ordinary nearest distance is permanently zero. Detect such
 # predicted contact and preserve the sign of nontrivial four-point volume
 # features. This is a deliberately local conservative half-space constraint;
 # failure to find progress through it is optimizer insufficiency, not a
 # global infeasibility proof.
 active=[];h=1e-5
 for passno in range(maxpasses):
  cc,_=exact(v+direction,ids);bad=sorted(set(cc)-set(baseline_pairs))
  if not bad:break
  for fa,fb in bad:
   for i in np.where(owners==fa)[0]:
    for j in np.where(owners==fb)[0]:
     aa=tri[i];bb=tri[j];features=[]
     for p in aa:features.append((int(p),*map(int,bb)))
     for p in bb:features.append((int(p),*map(int,aa)))
     for k in range(3):
      for l in range(3):features.append((int(aa[k]),int(aa[(k+1)%3]),int(bb[l]),int(bb[(l+1)%3])))
     for z in sorted(set(features)):
      if len(set(z))!=4:continue
      a=signed_volume(v,z);b=signed_volume(v+direction,z)
      if abs(a)<1e-12 or a*b>0:continue
      sign=1 if a>0 else -1;g=np.zeros((len(index),3))
      for vi in z:
       if vi not in index:continue
       for k in range(3):
        saved=float(v[vi,k]);v[vi,k]=saved+h;plus=signed_volume(v,z);v[vi,k]=saved-h;minus=signed_volume(v,z);v[vi,k]=saved;g[index[vi],k]=sign*(plus-minus)/(2*h)
      predicted=abs(a)+float(np.sum(g*direction[list(index)]));floor=min(abs(a)*.5,1e-9)
      if predicted>=floor:continue
      correction=W@g;den=float(np.sum(g*correction))
      if den>1e-18:
       direction[list(index)]+=correction*(floor-predicted)/den
       active.append({'face_ids':[fa,fb],'four_point_vertex_ids':list(z),'baseline_iterate_signed_volume_mm3':a,'preserved_sign':sign,'computational_volume_floor_mm3':floor,'kind':'ADJACENT_OR_NONADJACENT_NONTRIVIAL_FEATURE_SIDE'})
 return direction,active
