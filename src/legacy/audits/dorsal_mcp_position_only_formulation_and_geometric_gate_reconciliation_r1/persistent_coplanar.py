import sys
sys.dont_write_bytecode=True
from robust_geometry import *
from math import isqrt

def exact_quadratic_roots(co):
 c,b,a=co
 if a==0:return ([-c/b] if b else []),not b and c==0
 disc=b*b-4*a*c
 if disc<0:return [],False
 sn=isqrt(disc.numerator);sd=isqrt(disc.denominator)
 if sn*sn!=disc.numerator or sd*sd!=disc.denominator:return None,False
 sq=Fr(sn,sd);return list(set([(-b-sq)/(2*a),(-b+sq)/(2*a)])),False

def persistent_planar_path(v0,v1,aa,bb,legal_vertices=(),legal_edges=(),axes=(0,1)):
 p=[fq(z) for z in v0];d=[sub(fq(z),q) for z,q in zip(v1,p)];events={Fr(0),Fr(1)};identical=0;unresolved=[]
 def cr(a,b):return a[axes[0]]*b[axes[1]]-a[axes[1]]*b[axes[0]]
 triples=[]
 for a,b in [(aa,bb),(bb,aa)]:
  for vertex in a:
   for k in range(3):triples.append((vertex,b[k],b[(k+1)%3]))
 for z in triples:
  if len(set(z))<3:continue
  i,j,k=z;u=sub(p[j],p[i]);w=sub(p[k],p[i]);du=sub(d[j],d[i]);dw=sub(d[k],d[i]);co=[cr(u,w),cr(du,w)+cr(u,dw),cr(du,dw)];roots,zero=exact_quadratic_roots(co)
  if zero:identical+=1
  if roots is None:unresolved.append({'vertices':list(z),'reason':'Nonrational quadratic event time requires algebraic-root interval/finite-feature sign certification. Conservatively unresolved; never safe-by-sampling.'});continue
  events.update(t for t in roots if 0<=t<=1)
 if unresolved:return {'status':'UNRESOLVED_FAIL_CLOSED','unresolved':unresolved,'safe':False,'collision_detected':False}
 ev=sorted(events);samples=ev+[(a+b)/2 for a,b in zip(ev,ev[1:])];rows=[]
 for t in sorted(set(samples)):
  cache={i:add(q,mul(d[i],t)) for i,q in enumerate(p)};r=intersection(v0,aa,bb,legal_vertices,legal_edges,cache);rows.append({'fraction_exact':str(t),'fraction':float(t),**r})
 bad=[r for r in rows if r['illegal']]
 return {'status':'CERTIFIED_COLLISION' if bad else 'CERTIFIED_LEGAL','safe':not bad,'collision_detected':bool(bad),'exact_rational_event_fractions':[str(t) for t in ev],'identically_zero_2D_feature_polynomial_count':identical,'event_partition_tests':rows,'completeness':'For this fixed common-plane path, finite triangle contact combinatorics can change only at the enumerated 2D orientation roots. Exact rational event and open-interval tests certify all intervals. No positive shared-feature gap is imposed.'}
