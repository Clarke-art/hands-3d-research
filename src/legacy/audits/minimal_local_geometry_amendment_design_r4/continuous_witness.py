import sys
sys.dont_write_bytecode=True
from local_analysis import *
from itertools import combinations
from fractions import Fraction as Fr

def volume_coeff(points,delta,z):
 a,b,c,d=z
 u=sub(points[b],points[a]);w=sub(points[c],points[a]);h=sub(points[d],points[a])
 du=sub(delta[b],delta[a]);dw=sub(delta[c],delta[a]);dh=sub(delta[d],delta[a])
 return [dot(u,cross(w,h)),dot(du,cross(w,h))+dot(u,cross(dw,h))+dot(u,cross(w,dh)),dot(du,cross(dw,h))+dot(du,cross(w,dh))+dot(u,cross(dw,dh)),dot(du,cross(dw,dh))]

def area_coeff(points,delta,z,axis):
 a,b,c=z;u=sub(points[b],points[a]);w=sub(points[c],points[a]);du=sub(delta[b],delta[a]);dw=sub(delta[c],delta[a])
 return [cross(u,w)[axis],(add(cross(du,w),cross(u,dw)))[axis],cross(du,dw)[axis]]

def stable(c):
 # Exact Bernstein convex-hull certificate. Identically zero chirotope
 # entries remain zero; a nonzero entry retains its sign throughout [0,1].
 if all(x==0 for x in c):return 'IDENTICALLY_ZERO'
 if len(c)==4:b=[c[0],c[0]+c[1]/3,c[0]+2*c[1]/3+c[2]/3,sum(c)]
 else:b=[c[0],c[0]+c[1]/2,sum(c)]
 if all(x>0 for x in b) or all(x<0 for x in b):return 'STRICT_SIGN_PRESERVED'
 return 'UNRESOLVED'

def certify(v,df,amp):
 d=amp*df;p={i:fq(v[i]) for i in range(len(v))};dd={i:fq(d[i]) for i in range(len(v))}
 pairs={tuple(map(int,z)) for z in broad(v,IDS,band=1e-8,end=v+d)}
 intrinsic=[]
 for face in face_domain(IDS):
  tt=list(map(int,np.where(owners==face)[0]));pairs.update(combinations(tt,2));intrinsic.extend(combinations(tt,2))
 pairs=sorted(pairs);memo={};area_memo={};unresolved=[];coplanar=0;static=0;tested=0
 for a,b in pairs:
  legalverts,legaledges=legal_features(a,b)
  ids=sorted(set(map(int,tri[a]))|set(map(int,tri[b]))|set(legalverts)|{int(i) for edge in legaledges for i in edge})
  if all(not any(dd[i]) for i in ids):static+=1;continue
  tests=[]
  for z in combinations(ids,4):
   if z not in memo:memo[z]=stable(volume_coeff(p,dd,z))
   tests.append(memo[z])
  bad=any(t=='UNRESOLVED' for t in tests)
  if tests and all(t=='IDENTICALLY_ZERO' for t in tests):
   # Complete coplanar configuration requires a persistent nonsingular
   # projection chart and rank-3 chirotope, rather than 3D volumes alone.
   coplanar+=1;aa=tri[a];nn=np.cross(v[aa[1]]-v[aa[0]],v[aa[2]]-v[aa[0]]);axis=int(np.argmax(abs(nn)));checks=[]
   for z in combinations(ids,3):
    key=(z,axis)
    if key not in area_memo:area_memo[key]=stable(area_coeff(p,dd,z,axis))
    checks.append(area_memo[key])
   bad=any(t=='UNRESOLVED' for t in checks) or not any(t=='STRICT_SIGN_PRESERVED' for t in checks)
  if bad:unresolved.append({'triangle_indices':[int(a),int(b)],'face_ids':[int(owners[a]),int(owners[b])],'vertex_ids':ids})
  tested+=1
 intrinsicbad=[]
 for a,b in intrinsic:
  lv,le=legal_features(a,b);rr=intersection(v,tri[a],tri[b],lv,le)
  if rr['illegal']:intrinsicbad.append({'face_id':int(owners[a]),'audit':rr})
 return {'status':'CERTIFIED_CONSTANT_INTERSECTION_COMBINATORICS' if not unresolved else 'UNRESOLVED_FAIL_CLOSED','whole_swept_and_intrinsic_pairs':len(pairs),'intrinsic_fan_pairs_added':len(intrinsic),'baseline_intrinsic_illegal_fans':intrinsicbad,'moving_triangle_pair_count':tested,'static_pairs':static,'distinct_exact_cubic_predicates':len(memo),'distinct_exact_quadratic_chart_predicates':len(area_memo),'persistent_fully_coplanar_moving_pairs':coplanar,'unresolved_pairs':unresolved,'step_max_mm':amp,'method':'Exact rational Bernstein sign preservation for the COMPLETE 4-point oriented matroid of each swept triangle pair, augmented with all legal native simplex vertices; fully coplanar configurations additionally preserve every 3-point chart orientation. Constant oriented-matroid signs preserve finite convex-simplex intersection combinatorics and shared-simplex membership, including source-existing contact components. No face-family whitelist is used. Same-native-face fan pairs are explicitly included.','scope':'Continuous mathematical linear path v+t*(amp*direction), with binary64 v and displacement interpreted exactly. Rounded endpoint checks are separate. Unchanged static pairs retain their prior status. This proves no NEW intersection combinatorics, not global source collision freedom or repaired shape.','anatomy_clearance_mm':0}

def run():
 data=read(OUT/'LOCAL_FEASIBLE_DESCENT_ANALYSIS_R1.json');results={}
 for label,v in [('FROZEN_BASELINE',V),('R3_BEST_FAILED_POINT',P)]:
  _,meta=derivatives(v);data['points'][label]['gradient_metadata']=meta
  rec=data['points'][label]['directions'][0];df=np.zeros_like(V);df[IDS]=np.array(rec['normalized_direction_vectors_world']);r=certify(v,df,1e-5);results[label]=r;print(label,r['status'],r['moving_triangle_pair_count'],'unresolved',len(r['unresolved_pairs']),flush=True)
 dump('LOCAL_FEASIBLE_DESCENT_ANALYSIS_R1.json',data)
 dump('CONTINUOUS_MICRO_WITNESS_CERTIFICATE_R1.json',{'witness_direction':'JOINT_METRIC_GRADIENT','points':results,'candidate_generated':False})
if __name__=='__main__':run()
