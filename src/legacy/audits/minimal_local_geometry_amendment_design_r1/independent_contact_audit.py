"""Float64 contact confirmation including native faces sharing vertices and coplanar overlaps.
Local write-incident coverage against the complete mesh. No old9 contact reclassification.
"""
import sys
sys.dont_write_bytecode=True
from design import *
D=read(OUT/'GEOMETRY_AMENDMENT_CANDIDATES_R1.json');ST=read(OUT/'CANDIDATE_EVALUATED_COORDINATES_R1.json')['states']
union=set(i for c in D['candidates'].values() for i in c['write_vertices'])
affected={fi for fi,p in enumerate(F) if union.intersection(p)}
tri=[];owners=[]
for fi,p in enumerate(F):
 for j in range(1,len(p)-1):tri.append([p[0],p[j],p[j+1]]);owners.append(fi)
tri=np.array(tri);owners=np.array(owners);changed=np.array([i for i,fi in enumerate(owners) if fi in affected])
eps=1e-5
def cross2(a,b):return a[0]*b[1]-a[1]*b[0]
def coplanar_overlap(a,b):
 norm=np.cross(a[1]-a[0],a[2]-a[0]);l=np.linalg.norm(norm)
 if l<1e-12:return 0.
 norm/=l;nb=np.cross(b[1]-b[0],b[2]-b[0]);lb=np.linalg.norm(nb)
 if lb<1e-12 or np.linalg.norm(np.cross(norm,nb/lb))>1e-8 or max(abs((b-a[0])@norm))>1e-6:return 0.
 drop=int(np.argmax(abs(norm)));axes=[i for i in range(3) if i!=drop];aa=a[:,axes];bb=b[:,axes];poly=[p.copy() for p in aa]
 sign=1 if cross2(bb[1]-bb[0],bb[2]-bb[0])>=0 else -1
 for u,v in zip(bb,np.roll(bb,-1,axis=0)):
  new=[]
  for p,q in zip(poly,poly[1:]+poly[:1]):
   dp=sign*cross2(v-u,p-u);dq=sign*cross2(v-u,q-u)
   if dp>=-1e-10:new.append(p)
   if (dp>0 and dq<0) or (dp<0 and dq>0):new.append(p+(q-p)*dp/(dp-dq))
  poly=new
  if len(poly)<3:return 0.
 return abs(sum(cross2(p,q) for p,q in zip(poly,poly[1:]+poly[:1])))*.5/max(abs(norm[drop]),1e-12)
def edge_tri(p,q,a):
 d=q-p;e1=a[1]-a[0];e2=a[2]-a[0];h=np.cross(d,e2);det=e1@h
 if abs(det)<1e-12:return None
 s=p-a[0];u=(s@h)/det;qq=np.cross(s,e1);v=(d@qq)/det;t=(e2@qq)/det
 if -1e-10<=u<=1+1e-10 and -1e-10<=v and u+v<=1+1e-10 and -1e-10<=t<=1+1e-10:return p+d*t
 return None
def point_seg_dist(p,a,b):
 d=b-a;return np.linalg.norm(p-(a+d*np.clip((p-a)@d/max(d@d,1e-30),0,1)))
def contacts(v):
 v=v-origin;t=v[tri];lo=t.min(1);hi=t.max(1);pairs=set()
 for i in changed:
  bs=np.where(np.all(hi>=lo[i]-eps,axis=1)&np.all(lo<=hi[i]+eps,axis=1))[0]
  for j in bs:
   if i==j or owners[i]==owners[j]:continue
   pairs.add(tuple(sorted((int(i),int(j)))))
 found={};checked=0
 for i,j in sorted(pairs):
  fi,fj=int(owners[i]),int(owners[j]);common=sorted(set(F[fi])&set(F[fj]));a,b=t[i],t[j]
  overlap=coplanar_overlap(a,b)
  if overlap>1e-6:
   key=tuple(sorted((fi,fj)));found[key]={'kind':'COPLANAR_AREA_OVERLAP','area_mm2':float(overlap),'shared_vertex_ids':common};continue
  pts=[]
  for aa,bb in [(a,b),(b,a)]:
   for p,q in zip(aa,np.roll(aa,-1,axis=0)):
    hit=edge_tri(p,q,bb)
    if hit is not None:pts.append(hit)
  checked+=1
  if len(pts)<2:continue
  length=max(np.linalg.norm(p-q) for p in pts for q in pts)
  if length<=eps:continue
  if len(common)==1:away=max(np.linalg.norm(p-v[common[0]]) for p in pts)
  elif len(common)==2:away=max(point_seg_dist(p,v[common[0]],v[common[1]]) for p in pts)
  elif len(common)>2:continue
  else:away=length
  if away>eps:
   key=tuple(sorted((fi,fj)));found[key]={'kind':'SEGMENT_CROSSING_AWAY_FROM_SHARED_TOPOLOGY','segment_mm':float(length),'away_from_shared_contact_mm':float(away),'shared_vertex_ids':common}
 return found,checked
result={};baseline={}
for label,poses in ST.items():
 result[label]={}
 for pose in ['BIND','IDX_MCP_15','IDX_MCP_30','IDX_MCP_45']:
  pairs,count=contacts(np.array(poses[pose]))
  if label=='CURRENT':baseline[pose]=pairs
  introduced=sorted(set(pairs)-set(baseline[pose]));removed=sorted(set(baseline[pose])-set(pairs))
  result[label][pose]={'broadphase_triangle_pairs_tested':count,'introduced_pairs':[{'face_ids':list(p),**pairs[p]} for p in introduced],'removed_pairs_INCIDENTAL_ONLY':[list(p) for p in removed],'all_local_intersections':{str(p):r for p,r in pairs.items()}}
  print('INDEPENDENT_CONTACT',label,pose,'introduced',introduced,flush=True)
dump('CANDIDATE_INDEPENDENT_CONTACT_AUDIT_R1.json',{'status':'LOCAL_DIAGNOSTIC_EXACT_CONTACT_CHECK_NOT_STAGE6A','algorithm':'Independent NumPy float64 native fan triangles; translated world-mm AABB; bidirectional segment/triangle clipping and 2D coplanar area clipping. Shared topology contact excluded only when intersection remains at the actual common vertex/edge.','numerical_segment_tolerance_mm':eps,'numerical_coplanar_area_tolerance_mm2':1e-6,'human_threshold':False,'scope_affected_face_ids':sorted(affected),'poses':result,'old9_crossing_classification_unchanged':True})
