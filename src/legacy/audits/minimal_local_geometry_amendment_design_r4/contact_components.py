import sys
sys.dont_write_bytecode=True
from semantic_audit import *
from itertools import combinations

def feature(p,aa,cache):
 for i in aa:
  if p==cache[int(i)]:return {'kind':'VERTEX','vertex_ids':[int(i)]}
 for a,b in zip(aa,list(aa[1:])+[aa[0]]):
  if on_seg(p,cache[int(a)],cache[int(b)]):return {'kind':'EDGE','vertex_ids':sorted([int(a),int(b)])}
 return {'kind':'TRIANGLE_INTERIOR','vertex_ids':sorted(map(int,aa))}

def barycentric(p,aa,cache):
 a,b,c=[cache[int(i)] for i in aa];u=sub(b,a);w=sub(c,a);r=sub(p,a);nn=cross(u,w);axis=max(range(3),key=lambda i:abs(nn[i]));axes=[i for i in range(3) if i!=axis]
 def cr(z,t):return z[axes[0]]*t[axes[1]]-z[axes[1]]*t[axes[0]]
 den=cr(u,w);b=cr(r,w)/den;c=cr(u,r)/den;return [1-b-c,b,c]

def registry(v,ids,with_rows=False):
 pairs=broad(v,ids);cache={i:fq(v[i]) for i in set(map(int,tri[pairs].ravel()))};found={};tested=0;anchors=[];raw={}
 for a,b in pairs:
  aa=tri[a];bb=tri[b];lv,le=legal_features(a,b);shared=set(aa)&set(bb)
  if len(shared)==2:
   pts=[cache[int(i)] for i in sorted(set(aa)|set(bb))]
   if dot(sub(pts[1],pts[0]),cross(sub(pts[2],pts[0]),sub(pts[3],pts[0])))!=0:continue
  rr=intersection(v,aa,bb,lv,le,cache,True);tested+=1
  if not rr['illegal']:continue
  pts=rr.pop('_points_exact');key=tuple(sorted((int(owners[a]),int(owners[b]))));fans=[int(a),int(b)];features=[{'a':feature(p,aa,cache),'b':feature(p,bb,cache)} for p in pts];raw[tuple(fans)]=pts
  rr.update({'triangle_indices':fans,'feature_identity':features,'shared_vertex_ids':lv,'shared_edges':le});found.setdefault(key,[]).append(rr)
  if with_rows:
   for p in pts:
    for tt in [aa,bb]:
     weights=barycentric(p,tt,cache);anchors.append({'triangle_vertex_ids':list(map(int,tt)),'barycentric_weights':[float(w) for w in weights],'exact_barycentric_weights':[str(w) for w in weights],'fixed_intersection_point_world_mm':[float(x) for x in p],'face_pair':list(key)})
 components={}
 for key,rows in found.items():
  groups=[]
  for rr in rows:
   points=raw[tuple(rr['triangle_indices'])];touch=[]
   for k,group in enumerate(groups):
    for other in group:
     qq=raw[tuple(other['triangle_indices'])]
     if any(p==q for p in points for q in qq) or (len(qq)==2 and any(on_seg(p,*qq) for p in points)) or (len(points)==2 and any(on_seg(q,*points) for q in qq)):touch.append(k);break
   if not touch:groups.append([rr])
   else:
    merged=[rr]
    for k in reversed(touch):merged.extend(groups.pop(k))
    groups.append(merged)
  comps=[]
  for group in groups:
   group.sort(key=lambda z:z['triangle_indices']);points=list({p for rr in group for p in raw[tuple(rr['triangle_indices'])]});diam=max((float(np.linalg.norm(np.array([float(x-y) for x,y in zip(p,q)]))) for p in points for q in points),default=0.)
   membership=[z['triangle_indices'] for z in group];comps.append({'component_id':'/'.join(map(str,key))+':'+','.join('-'.join(map(str,z)) for z in membership),'native_face_pair':list(key),'fan_pair_membership':membership,'feature_identity':[z['feature_identity'] for z in group],'segment_extent_mm':diam,'sum_fan_intersection_lengths_mm':sum(z['intersection_segment_mm'] for z in group),'coplanar_overlap_area_mm2':sum(z['coplanar_overlap_area_mm2'] for z in group),'closest_features':[tri_pair_metrics(v,tri[z['triangle_indices'][0]],tri[z['triangle_indices'][1]]) for z in group],'fan_contact_records':group})
  components[key]=comps
 return components,anchors,{'broadphase_pairs':len(pairs),'exact_narrowphase_pairs':tested,'true_contact_native_pair_count':len(components),'component_count':sum(map(len,components.values()))}

def compare(baseline,current):
 new=[];worse=[];expansion=[];removed=[];delta=[];tol=1e-7
 for pair,comps in current.items():
  old={z['component_id']:z for z in baseline.get(pair,[])}
  for z in comps:
   cid=z['component_id']
   if cid not in old:new.append(z);continue
   b=old[cid];identity_same=z['feature_identity']==b['feature_identity'];row={'component_id':cid,'before_segment_mm':b['segment_extent_mm'],'after_segment_mm':z['segment_extent_mm'],'before_sum_fan_segment_mm':b['sum_fan_intersection_lengths_mm'],'after_sum_fan_segment_mm':z['sum_fan_intersection_lengths_mm'],'before_area_mm2':b['coplanar_overlap_area_mm2'],'after_area_mm2':z['coplanar_overlap_area_mm2'],'feature_identity_unchanged':identity_same,'membership_unchanged':z['fan_pair_membership']==b['fan_pair_membership']};delta.append(row)
   if not identity_same:expansion.append(row)
   if z['segment_extent_mm']>b['segment_extent_mm']+tol or z['sum_fan_intersection_lengths_mm']>b['sum_fan_intersection_lengths_mm']+tol or z['coplanar_overlap_area_mm2']>b['coplanar_overlap_area_mm2']+tol:worse.append(row)
 for pair,comps in baseline.items():
  ids={z['component_id'] for z in current.get(pair,[])};removed.extend(z['component_id'] for z in comps if z['component_id'] not in ids)
 return {'PASS':not new and not worse and not expansion,'new_true_contact_components':new,'worsening_components':worse,'feature_expansions':expansion,'removed_components':removed,'before_after':delta,'COMPUTATIONAL_GEOMETRY_TOLERANCE':{'contact_extent_mm':tol,'contact_area_mm2':tol,'anatomy_clearance':False},'existing_true_contacts_reclassified_legal':False}

def build():
 base,anchors,counts=registry(V,IDS,True);context,_,staticcounts=registry(V,F[3351]);dump('R4_BASELINE_CONTACT_COMPONENT_AUDIT.json',{'baseline_components':{str(k):z for k,z in base.items()},'source_existing_classifications':{'2181/3329':'NONADJACENT_TRUE_COLLISION'},'independent_static3351_context':{str(k):z for k,z in context.items()},'mutable_scope_counts':counts,'static3351_context_counts':staticcounts,'anchor_invariance_strategy':'Hold only source intersection barycentric feature points fixed by homogeneous linear displacement equalities. Re-identify and compare every accepted trial; anchors do not exempt a face pair or new component.','source_component_feature_anchors':anchors,'candidate_comparisons':{},'unaffected_source_components':'No vertices outside S4 move; source contacts with no changed incident fan remain exactly unchanged. No claim of global source collision freedom.'})
 A=[]
 for ra,rb in zip(anchors[::2],anchors[1::2]):
  row=np.zeros(len(IDS))
  for r,sign in [(ra,1),(rb,-1)]:
   for i,w in zip(r['triangle_vertex_ids'],r['barycentric_weights']):
    if i in IDS:row[IDS.index(i)]+=sign*w
  if np.linalg.norm(row)>1e-12:A.append(row)
 A=np.array(A);U,s,vh=np.linalg.svd(A,full_matrices=True);rank=int(sum(s>1e-9));Z=vh[rank:].T;np.savez(OUT/'R4_CONTACT_ANCHOR_NULLSPACE.npz',A=A,Z=Z)
 audit=read(OUT/'R4_BASELINE_CONTACT_COMPONENT_AUDIT.json');audit['anchor_invariance_strategy']='Preserve coincidence of each source contact barycentric feature point across its two triangles. World points may move together; per-component convex extent inequalities prevent expansion. No component is an optimizer repair target.';dump('R4_BASELINE_CONTACT_COMPONENT_AUDIT.json',audit)
 dump('R4_CONTACT_ANCHOR_CONSTRUCTION.json',{'row_count':len(A),'rank_per_axis':rank,'remaining_position_dof':int(Z.shape[1]*3),'anchor_constraints_are_conservative_design_choice_not_infeasibility_proof':True,'native_support_pool_count':len(IDS),'semantics':'Relative barycentric-point coincidence, not world-point freezing. Absolute freezing was an algebraic precheck with zero depth/hinge gradient and was discarded before nonlinear optimization; it is not a geometric impossibility proof.'})
 print('COMPONENTS',counts,'ANCHOR_RANK',rank,'remaining dof',Z.shape[1]*3,flush=True)
if __name__=='__main__':build()
