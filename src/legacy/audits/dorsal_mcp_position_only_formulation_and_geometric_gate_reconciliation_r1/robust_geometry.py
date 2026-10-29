import sys
sys.dont_write_bytecode=True
from collision_engine import *
from fractions import Fraction as Fr
from functools import lru_cache

def fq(p):return tuple(Fr.from_float(float(x)) for x in p)
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def mul(a,t):return tuple(x*t for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def segment_hit(p,q,a):
 d=sub(q,p);e1=sub(a[1],a[0]);e2=sub(a[2],a[0]);h=cross(d,e2);det=dot(e1,h)
 if det==0:return None
 s=sub(p,a[0]);u=dot(s,h)/det;qq=cross(s,e1);w=dot(d,qq)/det;t=dot(e2,qq)/det
 if 0<=u<=1 and 0<=w and u+w<=1 and 0<=t<=1:return add(p,mul(d,t))
 return None
def on_seg(p,a,b):
 d=sub(b,a);q=sub(p,a)
 if any(cross(d,q)):return False
 return 0<=dot(q,d)<=dot(d,d)
def coplanar_polygon(a,b):
 nn=cross(sub(a[1],a[0]),sub(a[2],a[0]));nb=cross(sub(b[1],b[0]),sub(b[2],b[0]))
 if not any(nn) or not any(nb):return None
 if any(cross(nn,nb)) or any(dot(sub(p,a[0]),nn) for p in b):return None
 drop=max(range(3),key=lambda i:abs(nn[i]));axes=[i for i in range(3) if i!=drop]
 def cr2(a,b,c):return (b[axes[0]]-a[axes[0]])*(c[axes[1]]-a[axes[1]])-(b[axes[1]]-a[axes[1]])*(c[axes[0]]-a[axes[0]])
 orient=1 if cr2(*b)>0 else -1;poly=list(a)
 for u,w in zip(b,b[1:]+b[:1]):
  out=[]
  if not poly:break
  for p,q in zip(poly,poly[1:]+poly[:1]):
   dp=orient*cr2(u,w,p);dq=orient*cr2(u,w,q)
   if dp>=0:out.append(p)
   if (dp>0 and dq<0) or (dp<0 and dq>0):out.append(add(p,mul(sub(q,p),dp/(dp-dq))))
  poly=list(dict.fromkeys(out))
 area=abs(sum(p[axes[0]]*q[axes[1]]-p[axes[1]]*q[axes[0]] for p,q in zip(poly,poly[1:]+poly[:1])))/2
 return poly,float(area)*float(np.linalg.norm(np.array([float(x) for x in nn]))/abs(float(nn[drop])))

def intersection(v,aa,bb,legal_vertices=(),legal_edges=(),cache=None):
 cache={} if cache is None else cache
 def pt(i):
  i=int(i)
  if i not in cache:cache[i]=fq(v[i])
  return cache[i]
 a=tuple(pt(i) for i in aa);b=tuple(pt(i) for i in bb);cop=coplanar_polygon(a,b);pts=[];area=0.
 if cop is not None:pts,area=cop
 else:
  for u,z in [(a,b),(b,a)]:
   for p,q in zip(u,u[1:]+u[:1]):
    hit=segment_hit(p,q,z)
    if hit is not None:pts.append(hit)
 pts=list(dict.fromkeys(pts));illegal=[]
 for p in pts:
  legal=any(p==pt(i) for i in legal_vertices) or any(on_seg(p,pt(i),pt(j)) for i,j in legal_edges)
  if not legal:illegal.append(p)
 if area>0:kind='COPLANAR_POSITIVE_AREA_OVERLAP';bad=True
 elif illegal:kind='OFF_LEGAL_FEATURE_EXACT_CONTACT';bad=True
 elif pts:kind='LEGAL_SHARED_TOPOLOGY_CONTACT';bad=False
 else:kind='DISJOINT';bad=False
 length=max((np.linalg.norm(np.array([float(x-y) for x,y in zip(p,q)])) for p in pts for q in pts),default=0.)
 return {'classification':kind,'illegal':bad,'exact_intersection_point_count':len(pts),'illegal_point_count':len(illegal),'coplanar':cop is not None,'coplanar_overlap_area_mm2':area,'intersection_segment_mm':float(length),'points_world_mm':[[float(x) for x in p] for p in pts],'illegal_points_world_mm':[[float(x) for x in p] for p in illegal],'predicate':'Exact rational predicates on stored binary64 coordinates; no distance clearance or barycentric extension tolerance.'}

def legal_features(i,j):
 fa=int(owners[i]);fb=int(owners[j]);verts=sorted(set(F[fa])&set(F[fb]))
 if fa==fb:
  vv=sorted(set(tri[i])&set(tri[j]));return vv,[vv] if len(vv)==2 else []
 edges=[E[ei] for ei in set(FE[fa])&set(FE[fb])]
 return verts,edges

def exact_certified(v,ids,only_faces=None):
 pairs=broad(v,ids,band=1e-8);cache={};found={};tested=0;legalcount=0
 # Noncoplanar triangles with two identical vertices intersect only on their
 # shared edge. This exact geometric fact avoids unnecessary rational clips.
 for i,j in pairs:
  fa=int(owners[i]);fb=int(owners[j]);key=tuple(sorted((fa,fb)))
  if only_faces is not None and not (set(key)&set(only_faces)):continue
  verts,edges=legal_features(i,j);sharedtri=set(tri[i])&set(tri[j])
  if len(sharedtri)==2:
   pp=[fq(v[k]) for k in list(set(tri[i])|set(tri[j]))];z=sub(pp[1],pp[0]);w=sub(pp[2],pp[0]);u=sub(pp[3],pp[0]);vol=dot(z,cross(w,u))
   if vol!=0:legalcount+=1;continue
  result=intersection(v,tri[i],tri[j],verts,edges,cache);tested+=1
  if result['illegal']:
   result.update({'triangle_indices':[int(i),int(j)],'shared_vertex_ids':verts,'shared_native_edge_vertex_ids':edges})
   if key not in found or result['intersection_segment_mm']>found[key]['intersection_segment_mm']:found[key]=result
  elif result['classification']=='LEGAL_SHARED_TOPOLOGY_CONTACT':legalcount+=1
 return found,{'swept_or_static_broadphase_pairs':len(pairs),'rational_narrowphase_pairs':tested,'legal_shared_triangle_pairs':legalcount}

def triangle_area_vectors(v):return np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])/2
def swept_min_area(v,d,triangle_ids):
 minimum=float('inf');where=None
 for ti in triangle_ids:
  a,b,c=tri[ti];u=v[b]-v[a];w=v[c]-v[a];du=d[b]-d[a];dw=d[c]-d[a];A=np.cross(u,w)/2;B0=(np.cross(du,w)+np.cross(u,dw))/2;C0=np.cross(du,dw)/2
  co=np.array([A@A,2*A@B0,B0@B0+2*A@C0,2*B0@C0,C0@C0]);der=np.arange(1,5)*co[1:];last=next((k for k in range(3,-1,-1) if abs(der[k])>1e-24),-1);times=[0.,1.]
  if last>=1:times.extend(float(z.real) for z in np.roots(der[:last+1][::-1]) if abs(z.imag)<1e-9 and 0<z.real<1)
  for tau in times:
   area=float(np.linalg.norm(A+B0*tau+C0*tau*tau))
   if area<minimum:minimum=area;where={'triangle_index':int(ti),'fraction':tau,'native_face_id':int(owners[ti])}
 return {'minimum_fan_triangle_area_mm2':minimum,'location':where,'numeric_area_audit_tolerance_mm2':1e-10,'COMPUTATIONAL_GEOMETRY_TOLERANCE':True,'anatomy_threshold':False}
