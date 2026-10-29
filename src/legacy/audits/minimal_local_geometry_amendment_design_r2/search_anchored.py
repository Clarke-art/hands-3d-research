import sys
sys.dont_write_bytecode=True
from search import *
prior=np.array(read(R1/'GEOMETRY_AMENDMENT_CANDIDATES_R1.json')['candidates']['C']['world_mm'])
priorD=(prior-V)@B
def anchored(dep,pw,gw,strength,axisweight=1.,core_scale=1.,full_guide=False):
 ids=sorted(sets[dep]);ix={i:j for j,i in enumerate(ids)};stencil=sorted(set(ids)|{j for i in ids for j in adj[i]})
 lap=np.zeros((len(stencil),len(ids)))
 for row,i in enumerate(stencil):
  if i in ix:lap[row,ix[i]]=1
  ws=[];js=sorted(adj[i])
  for j in js:
   vec=Q[j,:2]-Q[i,:2];direction=abs(vec[1])/max(np.linalg.norm(vec),1e-12);ws.append(1+(axisweight-1)*direction**2)
  ws=np.array(ws)/sum(ws)
  for j,w in zip(js,ws):
   if j in ix:lap[row,ix[j]]-=w
 grad=[]
 for a,b in E:
  if a not in ix and b not in ix:continue
  row=np.zeros(len(ids));length=max(np.linalg.norm(V[a]-V[b]),.5)
  if a in ix:row[ix[a]]=1/length
  if b in ix:row[ix[b]]=-1/length
  grad.append(row)
 grad=np.array(grad);H=pw*np.eye(len(ids))+gw*grad.T@grad+lap.T@lap
 diag=np.zeros(len(ids));rhs=np.zeros((len(ids),3))
 anchor_ids=R['core_vertices'] if not full_guide else [i for i in read(R1/'GEOMETRY_AMENDMENT_CANDIDATES_R1.json')['candidates']['C']['write_vertices'] if i in ix]
 for i in anchor_ids:
  diag[ix[i]]=strength;rhs[ix[i]]=strength*priorD[i]*core_scale
 d=np.linalg.solve(H+np.diag(diag),rhs);v=V.copy();v[ids]=(Q[ids]+d)@B.T+origin
 return v,{'formulation':'constrained biharmonic displacement field with soft R1-C position guide; tail solves displacement rather than changing the surrounding base shape','position_weight':pw,'gradient_weight':gw,'bending_weight':1.,'core_anchor_weight':strength,'anisotropic_existing_tangent_axis_weight':axisweight,'core_target_strength_scale':core_scale,'guide_anchor_vertex_ids':anchor_ids,'full_R1_position_guide':full_guide,'SURFACE_DESIGN_PRIOR':'Soft R1-C moved positions within native support pool' if full_guide else 'R1-C corrected core only','ANATOMICAL_AUTHORITY':False,'fixed_outside_displacement_mm':0.,'deterministic':True}

if __name__=='__main__':
 matrix=read(OUT/'SUPPORT_DEPTH_FEASIBILITY_MATRIX_R2.json');attempts=matrix['attempts'];sols=read(OUT/'FEASIBLE_SOLVES_R2.json');feasible=sols['solutions'];first=sols['first'];bf=read(OUT/'FAILED_SOLVE_WITNESSES_R2.json')['best_failed_or_feasible_per_depth']
 for dep in range(1,6):
  if any(records[dep]['authority_intersections'].values()):break
  if first is not None and dep>first+1:break
  ids=sorted(sets[dep]);basecon,_=contact_check(V,ids)
  for pw in [.001,.03,.2]:
   for gw in [.03,.3,3.]:
    for strength in [3.,30.]:
     for anis in [1.,3.]:
      v,method=anchored(dep,pw,gw,strength,axisweight=anis)
      st,fail=initial_gate(v,ids);con=None
      if not fail:
       cc,num=contact_check(v,ids);new=sorted(set(cc)-set(basecon));con={'introduced_pairs':[{'face_ids':list(k),**cc[k]} for k in new],'removed_pairs_INCIDENTAL_EFFECT':[list(k) for k in sorted(set(basecon)-set(cc))],'triangle_pairs_tested':num}
       if new:fail.append('new_exact_contact_or_self_intersection')
      tag=f'ANCHOR_S{dep}_p{pw}_g{gw}_k{strength}_a{anis}';ds=np.linalg.norm(v-V,axis=1)
      a={'attempt_id':tag,'support_depth':dep,'method':method,'status':'STRUCTURALLY_FEASIBLE_SUPPORT_DEPTH' if not fail else 'FAIL_FEASIBILITY','failures':fail,'max_displacement_mm':float(ds.max()),'edge6675_deg':st['edge6675_deg'],'edge6602_deg':st['edge6602_deg'],'edge6676_deg':st['edge6676_deg'],'core_depth_mm':st['fixed_reference_core_depth_mm'],'new_boundary_sharp_fold_edge_ids':[r['edge_id'] for r in st['new_boundary_sharp_folds']],'new_quad_bowtie_face_ids':st['new_quad_bowties'],'new_reversal_face_ids':st['new_reference_reversed_faces'],'new_outward_normal_reversal_face_ids':st['new_previously_outward_normal_reversals'],'new_internal_obtuse_edge_ids':st['all_incident_new_obtuse_edges'],'contact':con}
      attempts.append(a)
      score=lambda z:(len(z['failures']),len(z['new_boundary_sharp_fold_edge_ids'])+len(z['new_quad_bowtie_face_ids'])+len(z['new_reversal_face_ids'])+len(z['new_internal_obtuse_edge_ids']),z['edge6676_deg'])
      if score(a)<score(bf[str(dep)]['attempt']):bf[str(dep)]={'attempt':a,'world_mm':v.tolist(),'full_structural_audit':st}
      if not fail:
       rms=float(np.sqrt(np.mean(ds[ids]**2)))
       if str(dep) not in feasible or rms<feasible[str(dep)]['RMS_displacement_mm']:
        feasible[str(dep)]={'attempt_id':tag,'world_mm':v.tolist(),'method':method,'support_depth':dep,'support_pool_vertex_ids':ids,'write_vertices':[i for i in ids if ds[i]>1e-7],'max_displacement_mm':float(ds.max()),'RMS_displacement_mm':rms,'structure':st,'contact':con}
  if str(dep) in feasible and first is None:first=dep
  matrix.update({'attempts':attempts,'first_structurally_feasible_support_depth':first,'support_depths_tested':sorted(set(a['support_depth'] for a in attempts)),'formulation_refinement':'A second increasing-depth pass explores anchored displacement falloff after absolute surface fairing. Not a proof of mathematical infeasibility.'})
  dump('SUPPORT_DEPTH_FEASIBILITY_MATRIX_R2.json',matrix);dump('FEASIBLE_SOLVES_R2.json',{'first':first,'solutions':feasible});dump('FAILED_SOLVE_WITNESSES_R2.json',{'best_failed_or_feasible_per_depth':bf})
  print('ANCHORED',dep,'feasible',str(dep) in feasible,'best',bf[str(dep)]['attempt'],flush=True)
