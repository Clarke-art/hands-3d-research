"""Frozen native mesh and selected Human E baseline only; no other candidate families."""
import sys
sys.dont_write_bytecode=True
import json,collections,heapq,math
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parents[1]; ROOT=OUT.parents[2]
PRIOR=OUT.parent/'stage5b_r1e_thumb_distal_cap_boundary_review_r1'
NATIVE=OUT.parent/'stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1'
def load(p):return json.loads(p.read_text(encoding='utf8'))
E=load(PRIOR/'CAP_BOUNDARY_CANDIDATE_E.json')
M=load(NATIVE/'_tmp/static_mesh_states.json')['NATIVE']
LABELS=load(NATIVE/'_tmp/native_independent_partition.json')['labels']
V=np.array(M['vertices_world_m'])*1000;F=M['faces'];ED=M['edges']
BASEF=set(E['face_ids']); BASEV=set(E['vertex_ids']); FIVE={1453,2785,2790,297,298}
ADDS={1453,2785,2790}; PRESENT={297,298}; DOMAIN={v for v,x in enumerate(LABELS) if x=='thumb'}
NF={int(fi) for fi in E['metrics']['thumb_nail_coverage']['approved_nail_face_depths_mm']}; NV={v for fi in NF for v in F[fi]}
IP=np.array(E['axis_origin_world_mm']); AXIS=np.array(E['axis_unit']); SEED=284;TIP=V[SEED]
def unit(a):return a/max(np.linalg.norm(a),1e-15)
TIPAX=float((TIP-IP)@AXIS); AXIAL=(V-IP)@AXIS; DEPTH=TIPAX-AXIAL
DZ=np.array(E['circumferential_zero_unit_dorsal']);DS=np.array(E['circumferential_positive_unit'])
TRANS=V-IP-AXIAL[:,None]*AXIS;RADIUS=np.linalg.norm(TRANS,axis=1);ANGLE=(np.degrees(np.arctan2(TRANS@DS,TRANS@DZ))+360)%360
ADJ=[[] for _ in V];VF=[[] for _ in V];EF=collections.defaultdict(list);EID={tuple(sorted(e)):i for i,e in enumerate(ED)}
FN=np.zeros((len(F),3)); AREA=np.zeros(len(F));CENT=np.zeros_like(FN);VN=np.zeros_like(V)
for a,b in ED:
 w=float(np.linalg.norm(V[a]-V[b]));ADJ[a].append((b,w));ADJ[b].append((a,w))
for fi,vs in enumerate(F):
 p=V[vs];a=np.zeros(3)
 for j in range(1,len(vs)-1):
  cr=np.cross(p[j]-p[0],p[j+1]-p[0])/2;a+=cr;AREA[fi]+=np.linalg.norm(cr)
 FN[fi]=unit(a);CENT[fi]=p.mean(0)
 for v in vs:VF[v].append(fi);VN[v]+=a
 for a,b in zip(vs,vs[1:]+vs[:1]):EF[tuple(sorted((a,b)))].append(fi)
VN=np.array([unit(n) for n in VN]);NORMALAX=VN@AXIS
DUAL=collections.defaultdict(set)
for fs in EF.values():
 for a in fs:
  DUAL[a].update(set(fs)-{a})
G=np.full(len(V),np.inf);G[SEED]=0;PRED={};q=[(0.,SEED)]
while q:
 d,a=heapq.heappop(q)
 if d>G[a]:continue
 for b,w in ADJ[a]:
  if b in DOMAIN and d+w<G[b]:G[b]=d+w;PRED[b]=a;heapq.heappush(q,(G[b],b))
def rings(v):
 one={a for a,w in ADJ[v]};two={a for b in one for a,w in ADJ[b]}-one-{v};return sorted(one),sorted(two)
def curvature(v):
 one,two=rings(v);rates=[math.acos(float(np.clip(VN[v]@VN[a],-1,1)))/w for a,w in ADJ[v]]
 n=VN[v];t1=unit(np.cross(n,AXIS))
 if np.linalg.norm(t1)<.1:t1=unit(np.cross(n,DZ))
 t2=unit(np.cross(n,t1));peers=one+two;rel=V[peers]-V[v];x=rel@t1;y=rel@t2;z=rel@n
 mat=np.stack([x*x/2,x*y,y*y/2,x,y,np.ones(len(x))],axis=1);pars,_,rank,_=np.linalg.lstsq(mat,z,rcond=None)
 return {'normal_variation_rad_per_mm':float(np.median(rates)),'quadratic_principal_curvatures_per_mm':np.linalg.eigvalsh([[pars[0],pars[1]],[pars[1],pars[2]]]).tolist(),
  'quadratic_fit_rms_mm':float(np.sqrt(np.mean((mat@pars-z)**2))),'quadratic_fit_rank':int(rank),'proxy_not_anatomical_authority':True}
def components(fs):
 unseen=set(fs);result=[]
 while unseen:
  q=[min(unseen)];unseen.remove(q[0]);comp=[]
  while q:
   a=q.pop();comp.append(a)
   for b in DUAL[a]&unseen:unseen.remove(b);q.append(b)
  result.append(sorted(comp))
 return sorted(result,key=lambda c:(-len(c),c))
def corner_angle(fi,v):
 vs=F[fi];j=vs.index(v);a=unit(V[vs[j-1]]-V[v]);b=unit(V[vs[(j+1)%len(vs)]]-V[v])
 return math.degrees(math.acos(float(np.clip(a@b,-1,1))))
def patch(fs):
 fs=set(fs);verts={v for fi in fs for v in F[fi]};se=collections.defaultdict(list)
 for fi in fs:
  vs=F[fi]
  for a,b in zip(vs,vs[1:]+vs[:1]):se[tuple(sorted((a,b)))].append(fi)
 be=sorted(e for e,s in se.items() if len(s)==1);ba=collections.defaultdict(list)
 for a,b in be:ba[a].append(b);ba[b].append(a)
 unused=set(be);loops=[];openpaths=[]
 while unused:
  a,b=min(unused);seq=[a,b];unused.remove((a,b))
  while seq[-1]!=seq[0]:
   nxt=[v for v in ba[seq[-1]] if tuple(sorted((v,seq[-1]))) in unused]
   if not nxt:break
   v=min(nxt);unused.remove(tuple(sorted((v,seq[-1]))));seq.append(v)
  (loops if seq[-1]==seq[0] else openpaths).append(seq)
 comp=components(fs);nonman=[e for e,s in se.items() if len(s)>2];baddegree=[v for v,x in ba.items() if len(x)!=2]
 linkbad=[]
 for v in verts:
  links=collections.defaultdict(set)
  for fi in fs&set(VF[v]):
   vs=F[fi];j=vs.index(v);a,b=vs[j-1],vs[(j+1)%len(vs)];links[a].add(b);links[b].add(a)
  todo=[min(links)];seen=set()
  while todo:
   a=todo.pop()
   if a in seen:continue
   seen.add(a);todo+=list(links[a]-seen)
  if len(seen)!=len(links) or max(map(len,links.values()))>2 or sum(len(x)==1 for x in links.values()) not in [0,2]:linkbad.append(v)
 boundary=[]
 for seq in loops:
  for j,v in enumerate(seq[:-1]):
   prev=seq[j-1] if j>0 else seq[-2];nxt=seq[j+1];din=unit(V[v]-V[prev]);dout=unit(V[nxt]-V[v])
   turn=math.degrees(math.acos(float(np.clip(din@dout,-1,1))))
   l1=np.linalg.norm(V[v]-V[prev]);l2=np.linalg.norm(V[nxt]-V[v])
   n1=math.acos(float(np.clip(VN[v]@VN[prev],-1,1)))/l1;n2=math.acos(float(np.clip(VN[v]@VN[nxt],-1,1)))/l2
   interior=sum(corner_angle(fi,v) for fi in fs&set(VF[v]))
   boundary.append({'vertex_id':v,'previous_vertex_id':prev,'next_vertex_id':nxt,'degree':len(ba[v]),'turning_angle_deg':turn,
    'selected_face_interior_angle_sum_deg':float(interior),'intrinsic_corner_type':'CONCAVE_NOTCH_PROXY' if interior>240 else ('NARROW_SPIKE_PROXY' if interior<60 else 'ORDINARY_MESH_CORNER'),
    'boundary_curve_normal_discontinuity_rad_per_mm':float(abs(n1-n2)),
    'boundary_turning_curvature_per_mm':float(math.radians(turn)/((l1+l2)/2)),
    'incoming_edge_length_mm':float(l1),'outgoing_edge_length_mm':float(l2)})
 euler=len(verts)-len(se)+len(fs);disk=len(comp)==1 and len(loops)==1 and not openpaths and not nonman and not baddegree and not linkbad and euler==1
 return {'face_ids':sorted(fs),'vertex_ids':sorted(verts),'vertex_count':len(verts),'face_count':len(fs),
  'boundary_edge_ids':[EID[e] for e in be],'boundary_edges':[list(e) for e in be],'boundary_vertex_ids':sorted(ba),
  'boundary_edge_count':len(be),'boundary_vertex_count':len(ba),'connected_components':comp,'connected_component_count':len(comp),
  'closed_boundary_loops':loops,'closed_loop_count':len(loops),'open_boundary_paths':openpaths,
  'nonmanifold_edges':[list(e) for e in nonman],'nonmanifold_vertex_links':linkbad,'boundary_bad_degree_ids':baddegree,'manifold_disk':disk,'euler_characteristic':euler,
  'seed_included':SEED in verts,'max_geodesic_mm':float(max(G[list(verts)])),
  'boundary_axial_spread_mm':float(np.ptp(DEPTH[list(ba)])),'surface_area_mm2':float(sum(AREA[list(fs)])),
  'boundary_perimeter_mm':float(sum(np.linalg.norm(V[a]-V[b]) for a,b in be)),'boundary_smoothness_rows':boundary,
  'nail_margin_edge_preserved':(37,879) in be,'nail_face_ids_selected':sorted(fs&NF),
  'max_axial_depth_from_tip_mm':float(max(DEPTH[list(verts)])),'new_vertices_outside_five':sorted(verts-BASEV-FIVE),
  'lost_uncontested_baseline_vertices':sorted(BASEV-FIVE-verts)}
if __name__=='__main__':
 for name,fs in [('BASE',BASEF),('ADD_PAIRED',BASEF|{1220}),('REMOVE297',BASEF-set(VF[297])),('REMOVE298',BASEF-set(VF[298]))]:
  p=patch(fs);print(name,p['vertex_count'],p['face_count'],'spread',p['boundary_axial_spread_mm'],'perim',p['boundary_perimeter_mm'],'disk',p['manifold_disk'])
  for r in p['boundary_smoothness_rows']:
   if r['vertex_id'] in FIVE|{341,1382,2965,2966,1378,1380,1452,1454}:print(r)
