import sys
sys.dont_write_bytecode=True
from geometry import *

def point_triangle(p,t):
 a,b,c=t;ab=b-a;ac=c-a;ap=p-a;d1=ab@ap;d2=ac@ap
 if d1<=0 and d2<=0:return a,np.array([1.,0,0])
 bp=p-b;d3=ab@bp;d4=ac@bp
 if d3>=0 and d4<=d3:return b,np.array([0.,1,0])
 vc=d1*d4-d3*d2
 if vc<=0 and d1>=0 and d3<=0:
  s=d1/(d1-d3);return a+s*ab,np.array([1-s,s,0])
 cp=p-c;d5=ab@cp;d6=ac@cp
 if d6>=0 and d5<=d6:return c,np.array([0.,0,1])
 vb=d5*d2-d1*d6
 if vb<=0 and d2>=0 and d6<=0:
  s=d2/(d2-d6);return a+s*ac,np.array([1-s,0,s])
 va=d3*d6-d5*d4
 if va<=0 and d4-d3>=0 and d5-d6>=0:
  s=(d4-d3)/((d4-d3)+(d5-d6));return b+s*(c-b),np.array([0,1-s,s])
 den=max(va+vb+vc,1e-30);u=vb/den;v=vc/den
 return a+u*ab+v*ac,np.array([1-u-v,u,v])

def segment_segment(p1,q1,p2,q2):
 d1=q1-p1;d2=q2-p2;r=p1-p2;a=d1@d1;e=d2@d2;f=d2@r
 if a<=1e-20 and e<=1e-20:s=t=0.
 elif a<=1e-20:s=0.;t=float(np.clip(f/e,0,1))
 else:
  c=d1@r
  if e<=1e-20:t=0.;s=float(np.clip(-c/a,0,1))
  else:
   b=d1@d2;den=a*e-b*b;s=float(np.clip((b*f-c*e)/den,0,1)) if den>1e-20 else 0.;t=(b*s+f)/e
   if t<0:t=0.;s=float(np.clip(-c/a,0,1))
   elif t>1:t=1.;s=float(np.clip((b-c)/a,0,1))
 return p1+d1*s,p2+d2*t,s,t

def tri_pair_metrics(v,aa,bb):
 a=v[aa];b=v[bb];choices=[];hits=[]
 for u,z in [(a,b),(b,a)]:
  for p,q in zip(u,np.roll(u,-1,axis=0)):
   pt=edge_tri(p,q,z)
   if pt is not None:hits.append(pt)
 for i,p in enumerate(a):
  q,w=point_triangle(p,b);wa=np.eye(3)[i];choices.append((float(np.linalg.norm(p-q)),p,q,wa,w,'VERTEX_TRIANGLE'))
 for i,q in enumerate(b):
  p,w=point_triangle(q,a);wb=np.eye(3)[i];choices.append((float(np.linalg.norm(p-q)),p,q,w,wb,'TRIANGLE_VERTEX'))
 for i in range(3):
  for j in range(3):
   p,q,s,t=segment_segment(a[i],a[(i+1)%3],b[j],b[(j+1)%3]);wa=np.zeros(3);wb=np.zeros(3);wa[i]=1-s;wa[(i+1)%3]=s;wb[j]=1-t;wb[(j+1)%3]=t
   choices.append((float(np.linalg.norm(p-q)),p,q,wa,wb,'EDGE_EDGE'))
 d,p,q,wa,wb,kind=min(choices,key=lambda z:z[0]);length=max((np.linalg.norm(p-q) for p in hits for q in hits),default=0.)
 if hits:d=0.
 return {'distance_mm':d,'closest_world_mm':[p.tolist(),q.tolist()],'a_weights':wa.tolist(),'b_weights':wb.tolist(),'a_vertex_ids':list(map(int,aa)),'b_vertex_ids':list(map(int,bb)),'feature_kind':kind,'intersection_points_world_mm':[p.tolist() for p in hits],'crossing_segment_mm':float(length)}

def face_pair_metrics(v,fa=204,fb=207):
 pairs=[]
 for ia in range(1,len(F[fa])-1):
  for ib in range(1,len(F[fb])-1):
   a=[F[fa][0],F[fa][ia],F[fa][ia+1]];b=[F[fb][0],F[fb][ib],F[fb][ib+1]];m=tri_pair_metrics(v,a,b);m['fan_indices']=[ia,ib];pairs.append(m)
 closest=min(pairs,key=lambda z:z['distance_mm']);na=normal(v,F[fa]);nb=normal(v,F[fb]);signed=(v[F[fa]]-v[F[fb][0]])@nb
 return {'minimum_separation_mm':closest['distance_mm'],'closest_features':closest,'normal_dot':float(na@nb),'normal_angle_deg':math.degrees(math.acos(float(np.clip(na@nb,-1,1)))),'face204_vertex_signed_side_to_face207_plane_mm':{str(i):float(d) for i,d in zip(F[fa],signed)},'all_fan_pairs':pairs,'exact_contact':any(z['intersection_points_world_mm'] for z in pairs),'crossing':any(z['crossing_segment_mm']>1e-7 for z in pairs),'max_crossing_segment_mm':max(z['crossing_segment_mm'] for z in pairs)}
