import sys
sys.dont_write_bytecode=True
from continuous_witness import volume_coeff,area_coeff
from contact_components import *
from fractions import Fraction as Fr

def polyadd(a,b):
 r=[Fr(0)]*max(len(a),len(b))
 for i,v in enumerate(a):r[i]+=v
 for i,v in enumerate(b):r[i]+=v
 return r
def polymul(a,b):
 r=[Fr(0)]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):r[i+j]+=x*y
 return r
def polysub(a,b):return polyadd(a,[-x for x in b])
def bernstein(c):
 n=len(c)-1;return [sum((c[j]*Fr(math.comb(k,j),math.comb(n,j)) for j in range(k+1)),Fr(0)) for k in range(n+1)]
def nonnegative(c,depth=8):
 def check(b,d):
  if min(b)>=0:return True
  if max(b)<0 or d==0:return False
  levels=[b]
  for k in range(len(b)-1):levels.append([(x+y)/2 for x,y in zip(levels[-1],levels[-1][1:])])
  return check([q[0] for q in levels],d-1) and check([q[-1] for q in levels[::-1]],d-1)
 return check(bernstein(c),depth)
def strict(c):
 if all(x==0 for x in c):return 0
 b=bernstein(c)
 if min(b)>0:return 1
 if max(b)<0:return -1
 return None
def vecpoly(points,delta,i):return [[points[i][k],delta[i][k]] for k in range(3)]
def vsub(a,b):return [polysub(x,y) for x,y in zip(a,b)]
def vdot(a,b):
 z=[Fr(0)]
 for x,y in zip(a,b):z=polyadd(z,polymul(x,y))
 return z
def vcross(a,b):return [polysub(polymul(a[1],b[2]),polymul(a[2],b[1])),polysub(polymul(a[2],b[0]),polymul(a[0],b[2])),polysub(polymul(a[0],b[1]),polymul(a[1],b[0]))]

def rational_separation(v,end,aa,bb,points,delta):
 a=v[aa];b=v[bb];axes=[np.cross(a[1]-a[0],a[2]-a[0]),np.cross(b[1]-b[0],b[2]-b[0])]
 for pa,pb in [(a,b),(end[aa],end[bb])]:
  ea=np.roll(pa,-1,axis=0)-pa;eb=np.roll(pb,-1,axis=0)-pb
  axes.extend(np.cross(u,w) for u in ea for w in eb);axes.extend([np.cross(ea[0],np.cross(ea[0],ea[1])),np.cross(eb[0],np.cross(eb[0],eb[1]))])
 pa=np.vstack([a,end[aa]]);pb=np.vstack([b,end[bb]])
 for axis in axes:
  if np.linalg.norm(axis)<1e-18:continue
  s=pa@axis;t=pb@axis
  if not (min(s)>max(t)+1e-12 or min(t)>max(s)+1e-12):continue
  ax=fq(axis);sa=[dot(points[int(i)],ax) for i in aa]+[dot(add(points[int(i)],delta[int(i)]),ax) for i in aa];sb=[dot(points[int(i)],ax) for i in bb]+[dot(add(points[int(i)],delta[int(i)]),ax) for i in bb]
  if min(sa)>max(sb) or min(sb)>max(sa):return True
 return False

def moving_separator(v,end,aa,bb,points,delta):
 # Continuous SAT with moving axes removes plane-extension events that
 # do not involve the finite triangles. Float tests only select axes;
 # acceptance always uses exact rational polynomial inequalities.
 pa=[vecpoly(points,delta,int(i)) for i in aa];pb=[vecpoly(points,delta,int(i)) for i in bb];ea=[vsub(pa[(k+1)%3],pa[k]) for k in range(3)];eb=[vsub(pb[(k+1)%3],pb[k]) for k in range(3)];axes=[vcross(ea[0],ea[1]),vcross(eb[0],eb[1])]+[vcross(a,b) for a in ea for b in eb]
 m0=tri_pair_metrics(v,aa,bb);m1=tri_pair_metrics(end,aa,bb);a0,b0=np.array(m0['closest_world_mm']);a1,b1=np.array(m1['closest_world_mm']);ax0=a0-b0;ax1=a1-b1
 if np.linalg.norm(ax0)>1e-12 and np.linalg.norm(ax1)>1e-12:axes.insert(0,[[Fr.from_float(float(a)),Fr.from_float(float(b-a))] for a,b in zip(ax0,ax1)])
 for axis in axes:
  polys=[vdot(vsub(b,a),axis) for a in pa for b in pb]
  signs=[strict(c) for c in polys]
  if all(s==1 for s in signs) or all(s==-1 for s in signs):return True
 return False

def shared_vertex_separator(v,end,aa,bb,shared,points,delta):
 origin=next(iter(shared));av=[i for i in aa if i!=origin];bv=[i for i in bb if i!=origin]
 def axis_at(coords):
  rows=np.array([coords[i]-coords[origin] for i in av]+[coords[origin]-coords[i] for i in bv]);rows/=np.linalg.norm(rows,axis=1)[:,None]
  candidates=list(rows)+[a+b for a,b in combinations(rows,2)]+[np.cross(b-a,c-a) for a,b,c in combinations(rows,3)];candidates+=[-q for q in candidates];best=None;margin=0.
  for q in candidates:
   size=np.linalg.norm(q)
   if size>1e-20:
    q=q/size;m=float(np.min(rows@q))
    if m>margin:best=q;margin=m
  if margin>1e-14:return best
  x=np.zeros(3);dual=np.zeros(4)
  for iteration in range(700):
   for k in range(4):
    step=max(-dual[k],1-rows[k]@x);dual[k]+=step;x+=step*rows[k]
   if np.min(rows@x)>1-1e-9:break
  if np.min(rows@x)<=1e-7:return None
  return x/np.linalg.norm(x)
 n0=axis_at(v);n1=axis_at(end)
 if n0 is None or n1 is None:return False
 for n in [n0,n1]:
  axis=fq(n);checks=[dot(sub(points[int(i)],points[origin]),axis) for i in av]+[-dot(sub(points[int(i)],points[origin]),axis) for i in bv];ends=[dot(sub(add(points[int(i)],delta[int(i)]),add(points[origin],delta[origin])),axis) for i in av]+[-dot(sub(add(points[int(i)],delta[int(i)]),add(points[origin],delta[origin])),axis) for i in bv]
  if min(checks+ends)>0:return True
 axis=[[Fr.from_float(float(a)),Fr.from_float(float(b-a))] for a,b in zip(n0,n1)];o=vecpoly(points,delta,origin)
 return all(strict(vdot(vsub(vecpoly(points,delta,int(i)),o),axis))==sign for ids,sign in [(av,1),(bv,-1)] for i in ids)

def endpoint_function(points,delta,aa,bb,feat):
 for side in ['a','b']:
  f=feat[side]
  if f['kind']=='VERTEX':return vecpoly(points,delta,f['vertex_ids'][0]),[Fr(1)]
 for side,other in [('a',bb),('b',aa)]:
  f=feat[side]
  if f['kind']=='EDGE':
   a,b=f['vertex_ids'];pa=vecpoly(points,delta,a);pb=vecpoly(points,delta,b);q0,q1,q2=[vecpoly(points,delta,int(i)) for i in other];normal=vcross(vsub(q1,q0),vsub(q2,q0));D=vdot(normal,vsub(pb,pa));T=vdot(normal,vsub(q0,pa))
   if strict(D) is None or strict(D)==0:continue
   numerator=[polyadd(polymul(z,D),polymul(d,T)) for z,d in zip(pa,vsub(pb,pa))];return numerator,D
 return None

def persistent_finite_segment_certificate(points,delta,aa,bb,rr):
 # For two noncoplanar convex triangles, the intersection is one segment.
 # Its source boundary endpoints remain the exact limits if transverse
 # edge/plane denominators and finite barycentric feature memberships persist.
 pa=[vecpoly(points,delta,int(i)) for i in aa];pb=[vecpoly(points,delta,int(i)) for i in bb];na=vcross(vsub(pa[1],pa[0]),vsub(pa[2],pa[0]));nb=vcross(vsub(pb[1],pb[0]),vsub(pb[2],pb[0]));line=vcross(na,nb)
 if not any(strict(c) in [-1,1] for c in line):return False
 for feat in rr['feature_identity']:
  endpoint=endpoint_function(points,delta,aa,bb,feat)
  if endpoint is None:return False
  numerator,D=endpoint
  for side,tt in [('a',aa),('b',bb)]:
   p0,p1,p2=[vecpoly(points,delta,int(i)) for i in tt];u=vsub(p1,p0);w=vsub(p2,p0);area=vcross(u,w);axis=max(range(3),key=lambda k:abs(float(area[k][0])));axes=[k for k in range(3) if k!=axis]
   def cr(a,b):return polysub(polymul(a[axes[0]],b[axes[1]]),polymul(a[axes[1]],b[axes[0]]))
   offset=[polysub(z,polymul(q,D)) for z,q in zip(numerator,p0)];den=polymul(D,cr(u,w));sign=strict(den)
   if sign not in [-1,1]:return False
   beta=cr(offset,w);gamma=cr(u,offset);alpha=polysub(polysub(den,beta),gamma);f=feat[side];allowed=set(f['vertex_ids'])
   for vi,c in zip(tt,[alpha,beta,gamma]):
    if f['kind']=='TRIANGLE_INTERIOR' or int(vi) in allowed:
     if strict(c)!=sign:return False
    elif any(x!=0 for x in c):return False
 return True

def distance_bound(x,y,bound):
 a,da=x;b,db=y;den=polymul(da,db);num=[polysub(polymul(z,db),polymul(w,da)) for z,w in zip(a,b)];square=vdot(num,num);right=[v*bound*bound for v in polymul(den,den)];return nonnegative(polysub(right,square))

def squared_distance_function(x,y):
 a,da=x;b,db=y;den=polymul(da,db);num=[polysub(polymul(z,db),polymul(w,da)) for z,w in zip(a,b)];return vdot(num,num),polymul(den,den)
def split_bernstein(b):
 levels=[b]
 for k in range(len(b)-1):levels.append([(x+y)/2 for x,y in zip(levels[-1],levels[-1][1:])])
 return [q[0] for q in levels],[q[-1] for q in levels[::-1]]
def total_segment_bound(segments,bound):
 functions=[squared_distance_function(a,b) for a,b in segments]
 if len(functions)==1:
  n,d=functions[0];return nonnegative(polysub([x*bound*bound for x in d],n))
 if len(functions)==2:
  n1,d1=functions[0];n2,d2=functions[1];prod=polymul(d1,d2);u=polysub(polysub([x*bound*bound for x in prod],polymul(n1,d2)),polymul(n2,d1));second=polysub(polymul(u,u),[4*x for x in polymul(polymul(n1,n2),prod)])
  return nonnegative(u,12) and nonnegative(second,12)
 # A certified interval upper bound for the sum of square roots. Exact
 # Bernstein numerator/denominator bounds and a rational upper sqrt are
 # used on every dyadic interval, never a sample-based safety decision.
 from math import isqrt
 def check(items,depth):
  upper=Fr(0);valid=True
  for n,d in items:
   if min(d)<=0:valid=False;break
   ratio=max(Fr(0),max(n))/min(d);q=isqrt((ratio.numerator<<90)//ratio.denominator)+1;upper+=Fr(q,1<<45)
  if valid and upper<=bound:return True
  if depth==0:return False
  left=[];right=[]
  for n,d in items:
   na,nb=split_bernstein(n);da,db=split_bernstein(d);left.append((na,da));right.append((nb,db))
  return check(left,depth-1) and check(right,depth-1)
 return check([(bernstein(n),bernstein(d)) for n,d in functions],12)

def extent_certificate(points,delta,baseline_components,current_components):
 rows=[];tol=Fr.from_float(1e-7)
 for pair,comps in current_components.items():
  old={z['component_id']:z for z in baseline_components.get(pair,[])}
  for comp in comps:
   cid=comp['component_id']
   if cid not in old:return False,[{'component_id':cid,'reason':'NEW_COMPONENT'}]
   base=old[cid];functions=[];segments=[];byfan={tuple(z['triangle_indices']):z for z in base['fan_contact_records']}
   for rr in comp['fan_contact_records']:
    a,b=rr['triangle_indices'];oldrr=byfan.get((a,b));ff=[endpoint_function(points,delta,tri[a],tri[b],f) for f in rr['feature_identity']]
    if oldrr is None or any(z is None for z in ff):return False,[{'component_id':cid,'reason':'ENDPOINT_RATIONAL_REPRESENTATION_UNRESOLVED'}]
    if len(ff)==2:segments.append(tuple(ff))
    elif len(ff)>2:return False,[{'component_id':cid,'reason':'SOURCE_COPLANAR_AREA_COMPONENT_NEEDS_AREA_CERTIFICATE'}]
    functions.extend(ff)
   if not total_segment_bound(segments,Fr.from_float(base['sum_fan_intersection_lengths_mm'])+tol):return False,[{'component_id':cid,'reason':'CONTINUOUS_TOTAL_COMPONENT_LENGTH_UNRESOLVED_OR_INCREASE'}]
   for x,y in combinations(functions,2):
    if not distance_bound(x,y,Fr.from_float(base['segment_extent_mm'])+tol):return False,[{'component_id':cid,'reason':'CONTINUOUS_COMPONENT_EXTENT_UNRESOLVED_OR_INCREASE'}]
   rows.append({'component_id':cid,'continuous_segment_and_component_extent':'CERTIFIED_NONINCREASING_WITH_COMPUTATIONAL_TOLERANCE','source_extent_mm':base['segment_extent_mm'],'source_total_curve_length_mm':base['sum_fan_intersection_lengths_mm'],'tolerance_mm':float(tol),'method':'Exact rational moving edge/plane intersection functions; Bernstein squared-diameter bound and certified TOTAL curve-length bound throughout the entire step. Fan subdivision may redistribute existing length; total component and feature identities may not expand.'})
 return True,rows

def certify(v,end,baseline,current):
 d=end-v;allpairs={tuple(map(int,z)) for z in broad(v,IDS,end=end)}
 for fi in face_domain(IDS):allpairs.update(combinations(map(int,np.where(owners==fi)[0]),2))
 points={i:fq(v[i]) for i in range(len(V))};delta={i:fq(d[i]) for i in range(len(V))};memo={};failed=[];counts={};oldfans={tuple(rr['triangle_indices']):rr for comps in current.values() for c in comps for rr in c['fan_contact_records']}
 def vol(z):
  z=tuple(z)
  if z not in memo:memo[z]=strict(volume_coeff(points,delta,z))
  return memo[z]
 for a,b in sorted(allpairs):
  aa=list(map(int,tri[a]));bb=list(map(int,tri[b]));shared=set(aa)&set(bb);method=None
  if not any(np.any(d[i]) for i in set(aa)|set(bb)):method='STATIC'
  elif (a,b) not in oldfans:
   if len(shared)==2:
    s,t=sorted(shared);u=next(i for i in aa if i not in shared);w=next(i for i in bb if i not in shared);sign=vol((s,t,u,w))
    if sign not in [0,None]:method='SHARED_EDGE_STRICT_ROTATING_VOLUME'
    else:
     e=vsub(vecpoly(points,delta,t),vecpoly(points,delta,s));uu=vsub(vecpoly(points,delta,u),vecpoly(points,delta,s));ww=vsub(vecpoly(points,delta,w),vecpoly(points,delta,s));opposite=polysub(polymul(vdot(uu,ww),vdot(e,e)),polymul(vdot(uu,e),vdot(ww,e)))
     if strict(opposite)==-1:method='SHARED_EDGE_OPPOSITE_RAYS_ROTATING_OR_PERSISTENT_COPLANAR'
   if method is None and len(shared)==1:
    for anchor,other in [(aa,bb),(bb,aa)]:
     signs=[vol(tuple(anchor+[i])) for i in other if i not in shared]
     if signs and signs[0] not in [0,None] and all(s==signs[0] for s in signs):method='SHARED_VERTEX_ROTATING_SUPPORT_PLANE';break
   if method is None and not shared and rational_separation(v,end,aa,bb,points,delta):method='EXACT_SWEPT_CONVEX_SEPARATOR'
   if method is None and not shared and moving_separator(v,end,aa,bb,points,delta):method='EXACT_MOVING_FINITE_TRIANGLE_SEPARATOR'
  if method is None and (a,b) in oldfans and persistent_finite_segment_certificate(points,delta,aa,bb,oldfans[(a,b)]):method='EXACT_PERSISTENT_EXISTING_SEGMENT_FEATURE_MEMBERSHIP'
  if method is None:
   lv,le=legal_features(a,b);ids=sorted(set(aa)|set(bb)|set(lv)|{i for edge in le for i in edge});signs=[vol(z) for z in combinations(ids,4)]
   if all(z is not None for z in signs) and any(z!=0 for z in signs):method='COMPLETE_ORIENTED_MATROID_SIGN_CERTIFICATE'
   elif signs and all(z==0 for z in signs):
    normal=np.cross(v[aa[1]]-v[aa[0]],v[aa[2]]-v[aa[0]]);axis=int(np.argmax(abs(normal)));ss=[strict(area_coeff(points,delta,z,axis)) for z in combinations(ids,3)]
    if all(z is not None for z in ss) and any(z!=0 for z in ss):method='PERSISTENT_COPLANAR_COMPLETE_CHART_SIGN_CERTIFICATE'
  if method is None and len(shared)==1 and shared_vertex_separator(v,end,aa,bb,shared,points,delta):method='EXACT_SHARED_VERTEX_CONE_SEPARATOR'
  if method is None:failed.append({'triangle_indices':[a,b],'native_faces':[int(owners[a]),int(owners[b])],'reason':'NO_CONTINUOUS_FINITE_FEATURE_CERTIFICATE'})
  else:counts[method]=counts.get(method,0)+1
 if failed:return False,{'status':'UNRESOLVED_FAIL_CLOSED','failed_pairs':failed,'method_counts':counts,'swept_pairs':len(allpairs)}
 ts=np.where(np.isin(owners,list(face_domain(IDS))))[0];area=swept_min_area(v,d,ts)
 if area['minimum_fan_triangle_area_mm2']<=1e-10:return False,{'status':'DEGENERACY_FAIL','area':area}
 extentpass,extent=extent_certificate(points,delta,baseline,current)
 return extentpass,{'status':'CERTIFIED_CONTINUOUS_SAFE' if extentpass else 'UNRESOLVED_CONTACT_EXTENT_FAIL_CLOSED','method_counts':counts,'swept_and_intrinsic_pairs':len(allpairs),'distinct_exact_cubic_predicates':len(memo),'minimum_swept_native_fan_area':area,'existing_component_continuous_extent_certificates':extent,'no_anatomy_clearance':True,'coverage':'Noncoplanar, rotating-plane, shared-edge/off-edge and vertex/edge transitions certified by exact sign/finite separating predicates. Persistent-coplanar paths use rank-3 charts or exact opposite-ray proof. Event-producing intervals with no certificate reject, not safe-by-endpoints.'}
