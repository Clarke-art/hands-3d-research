import sys
sys.dont_write_bytecode=True
from geometry import *
sets,records=nested()
def solve(depth_i,position_weight,gradient_weight,bending_weight=1.,normal_strength=3.,target_depth=.65,anisotropy=1.):
 ids=sorted(sets[depth_i]);idx={i:j for j,i in enumerate(ids)};stencil=sorted(set(ids)|{j for i in ids for j in adj[i]})
 lap=np.zeros((len(stencil),len(ids)));lbase=np.zeros((len(stencil),3))
 for ri,i in enumerate(stencil):
  js=sorted(adj[i]);weights=[]
  for j in js:
   vec=Q[j,:2]-Q[i,:2];direction=abs(vec[1])/max(np.linalg.norm(vec),1e-12)
   weights.append(1+(anisotropy-1)*direction**2)
  weights=np.array(weights)/sum(weights)
  if i in idx:lap[ri,idx[i]]=1
  lbase[ri]=Q[i]-sum((w*Q[j] for j,w in zip(js,weights)),np.zeros(3))
  for j,w in zip(js,weights):
   if j in idx:lap[ri,idx[j]]-=w
 grad=[]
 for a,b in E:
  if a not in idx and b not in idx:continue
  row=np.zeros(len(ids))
  # First-order displacement differences; native graph normalized by edge length.
  length=max(np.linalg.norm(Q[a]-Q[b]),.5)
  if a in idx:row[idx[a]]=1/length
  if b in idx:row[idx[b]]=-1/length
  grad.append(row)
 grad=np.array(grad)
 H=position_weight*np.eye(len(ids))+gradient_weight*grad.T@grad+bending_weight*lap.T@lap
 # Minimize new surface bending in tangent directions while regularizing the
 # displacement and its gradient. Normal displacement uses a thin-plate field,
 # with only core surface targets; all exterior displacements are identically0.
 d=np.zeros((len(ids),3));d[:,:2]=np.linalg.solve(H,-bending_weight*lap.T@lbase[:,:2])
 qt=Q.copy();qt[ids,:2]+=d[:,:2]
 center=Q[[3332,3340],:2].mean(0)
 target=feat(qt)@cf-target_depth*np.exp(-np.sum((qt[:,:2]-center)**2,axis=1)/(2*6.**2))
 diagonal=np.zeros(len(ids));rhs=np.zeros(len(ids))
 for i in R['core_vertices']:
  diagonal[idx[i]]=normal_strength;rhs[idx[i]]=normal_strength*(target[i]-Q[i,2])
 d[:,2]=np.linalg.solve(H+np.diag(diagonal),rhs)
 v=V.copy();v[ids]=(Q[ids]+d)@B.T+origin
 return v,{'position_weight':position_weight,'first_order_gradient_weight':gradient_weight,'second_order_bending_weight':bending_weight,'core_normal_target_strength':normal_strength,'valley_target_depth_mm':target_depth,'valley_width_mm':6.,'anisotropic_valley_axis_weight':anisotropy,'objective':'regularized native graph thin-plate tangent fairing plus core curved shallow-valley normal target, first-order displacement differences and second-order displacement Laplacian with fixed exterior zero','SURFACE_DESIGN_PRIOR':True,'ANATOMICAL_AUTHORITY':False,'deterministic_linear_solve':True}

def initial_gate(v,ids):
 global FULLFS
 # Outside incident faces geometry is identical; full topology identities and
 # outside geometry equality are explicit invariants, not a cropped visual gate.
 import geometry
 geometry.FULLFS=sorted(face_domain(ids))
 st=structure(v,ids)
 failures=[]
 for k in ['new_degenerate_faces','new_quad_bowties','new_reference_reversed_faces','new_previously_outward_normal_reversals','new_boundary_sharp_folds']:
  if st[k]:failures.append(k)
 if st['edge6676_deg']>60:failures.append('central_crease_not_substantially_corrected')
 if st['fixed_reference_core_depth_mm']>1.1:failures.append('core_depth_not_substantially_improved')
 # Conservative localized high-change edge screen, not just global max.
 an=angles(v);es=sorted({ei for fi in face_domain(ids) for ei in FE[fi]})
 bad=[ei for ei in es if baseA[ei]<90 and an[ei]>=90]
 st['all_incident_new_obtuse_edges']=bad
 if bad:failures.append('new_internal_opposing_hinge')
 return st,failures

if __name__=='__main__':
 attempts=[];feasible={};first=None;boundaryrefs={};bestfails={}
 for dep in range(1,6):
  if any(records[dep]['authority_intersections'].values()):
   attempts.append({'support_depth':dep,'status':'PROTECTION_BOUNDARY_REACHED','authority_intersections':records[dep]['authority_intersections']});break
  if first is not None and dep>first+1:break
  pool=sorted(sets[dep]);basecontact,_=contact_check(V,pool);bestscore=None
  for pw in [.001,.01,.05,.2,.8,2.]:
   for gw in [.01,.1,1.]:
    for ns in [1.,10.]:
     v,method=solve(dep,pw,gw,normal_strength=ns)
     st,fail=initial_gate(v,pool)
     con=None
     if not fail:
      cc,num=contact_check(v,pool);new=sorted(set(cc)-set(basecontact));con={'introduced_pairs':[{'face_ids':list(k),**cc[k]} for k in new],'removed_pairs_INCIDENTAL_EFFECT':[list(k) for k in sorted(set(basecontact)-set(cc))],'triangle_pairs_tested':num}
      if new:fail.append('new_exact_contact_or_self_intersection')
     tag=f'S{dep}_p{pw}_g{gw}_n{ns}';a={'attempt_id':tag,'support_depth':dep,'method':method,'status':'STRUCTURALLY_FEASIBLE_SUPPORT_DEPTH' if not fail else 'FAIL_FEASIBILITY','failures':fail,'max_displacement_mm':float(np.linalg.norm(v-V,axis=1).max()),'edge6675_deg':st['edge6675_deg'],'edge6602_deg':st['edge6602_deg'],'edge6676_deg':st['edge6676_deg'],'core_depth_mm':st['fixed_reference_core_depth_mm'],'new_boundary_sharp_fold_edge_ids':[r['edge_id'] for r in st['new_boundary_sharp_folds']],'new_quad_bowtie_face_ids':st['new_quad_bowties'],'new_reversal_face_ids':st['new_reference_reversed_faces'],'new_outward_normal_reversal_face_ids':st['new_previously_outward_normal_reversals'],'new_internal_obtuse_edge_ids':st['all_incident_new_obtuse_edges'],'contact':con}
     attempts.append(a)
     score=(len(fail),len(st['new_boundary_sharp_folds'])+len(st['new_quad_bowties'])+len(st['new_reference_reversed_faces'])+len(st['all_incident_new_obtuse_edges']),st['edge6676_deg'])
     if bestscore is None or score<bestscore:
      bestscore=score;bestfails[dep]={'attempt':a,'world_mm':v.tolist(),'full_structural_audit':st}
     if not fail:
      ds=np.linalg.norm(v-V,axis=1);rms=float(np.sqrt(np.mean(ds[pool]**2)))
      if dep not in feasible or rms<feasible[dep]['RMS_displacement_mm']:
       feasible[dep]={'attempt_id':tag,'world_mm':v.tolist(),'method':method,'support_depth':dep,'support_pool_vertex_ids':pool,'write_vertices':[i for i in pool if ds[i]>1e-7],'max_displacement_mm':float(ds.max()),'RMS_displacement_mm':rms,'structure':st,'contact':con}
  if dep in feasible and first is None:first=dep
  dump('SUPPORT_DEPTH_FEASIBILITY_MATRIX_R2.json',{'DESIGN_ONLY':True,'attempts':attempts,'first_structurally_feasible_support_depth':first,'support_depths_tested':sorted(set(a['support_depth'] for a in attempts)),'search_limit':'At most first feasible depth+1, maximum S5 only if necessary. Solver failure does not prove connectivity limitation.','geometric_screen_parameters_not_anatomy':True})
  dump('FEASIBLE_SOLVES_R2.json',{'first':first,'solutions':feasible})
  dump('FAILED_SOLVE_WITNESSES_R2.json',{'best_failed_or_feasible_per_depth':bestfails})
  print('DEPTH',dep,'pool',len(pool),'FEASIBLE',dep in feasible,'best',bestfails[dep]['attempt'],flush=True)
