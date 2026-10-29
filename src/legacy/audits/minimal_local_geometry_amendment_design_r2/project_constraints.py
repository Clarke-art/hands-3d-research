import sys
sys.dont_write_bytecode=True
from search_anchored import *

def projected(dep,pw=.03,gw=.03,strength=3.,metric_weight=.3,maxiter=180,constrain_core=False):
 ids=sorted(sets[dep]);index={i:j for j,i in enumerate(ids)}
 v,method=anchored(dep,pw,gw,strength)
 lap=np.zeros((len(ids),len(ids)))
 for i in ids:
  lap[index[i],index[i]]=1
  for j in adj[i]:
   if j in index:lap[index[i],index[j]]-=1/len(adj[i])
 # Sobolev metric propagates each active-constraint correction as a smooth
 # position-only field over the entire native pool; exterior remains zero.
 W=np.linalg.inv(metric_weight*np.eye(len(ids))+lap.T@lap)
 es=sorted({ei for fi in face_domain(ids) for ei in FE[fi]})
 constraints={ei:math.cos(math.radians(min(85.,max(35.,float(baseA[ei])+10.)))) for ei in es if baseA[ei]<90}
 constraints[6676]=math.cos(math.radians(30.))
 history=[];best=None;bestscore=float('inf');h=1e-4
 for it in range(maxiter):
  ns=normals(v);dots={ei:float(ns[EF[ei][0]]@ns[EF[ei][1]]) for ei in constraints}
  active=sorted([ei for ei in constraints if dots[ei]<constraints[ei]-1e-7],key=lambda ei:dots[ei]-constraints[ei])
  deficit=max((constraints[ei]-dots[ei] for ei in active),default=0.)
  q=(v-origin)@B;res=q[:,2]-feat(q)@cf
  heightdef=max([max(0.,-res[i]-.95,res[i]-.25) for i in R['core_vertices']]) if constrain_core else 0.
  history.append({'iteration':it,'active_constraint_edge_ids':active,'max_dot_product_deficit':deficit,'core_height_constraint_deficit_mm':heightdef})
  if deficit<bestscore:bestscore=deficit;best=v.copy()
  if not active and heightdef<1e-7:break
  for ei in active:
   fa,fb=EF[ei];pointids=sorted((set(F[fa])|set(F[fb]))&set(ids));g=np.zeros((len(ids),3))
   current=normal(v,F[fa])@normal(v,F[fb]);shortfall=constraints[ei]-current
   if shortfall<=1e-7:continue
   for i in pointids:
    for axis in range(3):
     v[i,axis]+=h;plus=normal(v,F[fa])@normal(v,F[fb]);v[i,axis]-=2*h;minus=normal(v,F[fa])@normal(v,F[fb]);v[i,axis]+=h
     g[index[i],axis]=(plus-minus)/(2*h)
   direction=W@g;denom=float(np.sum(g*direction))
   if denom<1e-14:continue
   step=direction*shortfall/denom
   maxstep=float(np.linalg.norm(step,axis=1).max())
   if maxstep>.3:step*=.3/maxstep
   v[ids]+=step
  if constrain_core:
   for i in R['core_vertices']:
    q=(v[i]-origin)@B
    value=q[2]-feat(q[None,:])[0]@cf
    if -.95<=value<=.25:continue
    desired=-.95 if value<-.95 else .25
    tangent_x=cf[1]+2*cf[3]*q[0]+cf[4]*q[1]
    tangent_y=cf[2]+cf[4]*q[0]+2*cf[5]*q[1]
    g=np.zeros((len(ids),3));g[index[i]]=n-tangent_x*x-tangent_y*y
    direction=W@g;denom=float(np.sum(g*direction))
    if denom<1e-14:continue
    step=direction*(desired-value)/denom;maxstep=float(np.linalg.norm(step,axis=1).max())
    if maxstep>.3:step*=.3/maxstep
    v[ids]+=step
 # Use final iterate; preserve a best-deficit witness separately for diagnosis.
 st,fail=initial_gate(v,ids)
 method.update({'explicit_constraint_projection':True,'constraint_edges':sorted(constraints),'target_min_normal_dot':{str(ei):z for ei,z in constraints.items()},'constraint_thresholds_are_anatomy':False,'correction_metric':'inverse regularized native graph biharmonic displacement metric','metric_displacement_penalty_weight':metric_weight,'max_step_mm':.3,'iteration_limit':maxiter,'iterations':len(history),'final_max_constraint_deficit':history[-1]['max_dot_product_deficit'],'best_max_constraint_deficit':bestscore,'projection_convergence_is_not_proof_of_position_only_impossibility':True})
 method['core_height_constraint_enabled']=constrain_core
 method['core_height_design_interval_mm']=[-.95,.25] if constrain_core else None
 return v,method,st,fail,history

if __name__=='__main__':
 core_constraints='--core-constraints' in sys.argv
 matrix=read(OUT/'SUPPORT_DEPTH_FEASIBILITY_MATRIX_R2.json');attempts=matrix['attempts'];sol=read(OUT/'FEASIBLE_SOLVES_R2.json');feasible=sol['solutions'];first=sol['first'];trace={}
 for dep in range(1,6):
  if any(records[dep]['authority_intersections'].values()):break
  if first is not None and dep>first+1:break
  ids=sorted(sets[dep]);basecon=None
  for mwgt in [.1,1.]:
   v,method,st,fail,hist=projected(dep,metric_weight=mwgt,constrain_core=core_constraints)
   con=None
   if not fail:
    if basecon is None:basecon,_=contact_check(V,ids)
    cc,num=contact_check(v,ids);new=sorted(set(cc)-set(basecon));con={'introduced_pairs':[{'face_ids':list(k),**cc[k]} for k in new],'triangle_pairs_tested':num}
    if new:fail.append('new_exact_contact_or_self_intersection')
   tag=f'{"CORE_HINGE" if core_constraints else "PROJECT"}_S{dep}_metric{mwgt}';ds=np.linalg.norm(v-V,axis=1);rms=float(np.sqrt(np.mean(ds[ids]**2)))
   a={'attempt_id':tag,'support_depth':dep,'method':method,'status':'STRUCTURALLY_FEASIBLE_SUPPORT_DEPTH' if not fail else 'FAIL_FEASIBILITY','failures':fail,'max_displacement_mm':float(ds.max()),'edge6675_deg':st['edge6675_deg'],'edge6602_deg':st['edge6602_deg'],'edge6676_deg':st['edge6676_deg'],'core_depth_mm':st['fixed_reference_core_depth_mm'],'new_boundary_sharp_fold_edge_ids':[r['edge_id'] for r in st['new_boundary_sharp_folds']],'new_quad_bowtie_face_ids':st['new_quad_bowties'],'new_reversal_face_ids':st['new_reference_reversed_faces'],'new_outward_normal_reversal_face_ids':st['new_previously_outward_normal_reversals'],'new_internal_obtuse_edge_ids':st['all_incident_new_obtuse_edges'],'contact':con}
   attempts.append(a);trace[tag]={'history':hist,'world_mm':v.tolist(),'full_audit':st}
   if not fail and (str(dep) not in feasible or rms<feasible[str(dep)]['RMS_displacement_mm']):
    feasible[str(dep)]={'attempt_id':tag,'world_mm':v.tolist(),'method':method,'support_depth':dep,'support_pool_vertex_ids':ids,'write_vertices':[i for i in ids if ds[i]>1e-7],'max_displacement_mm':float(ds.max()),'RMS_displacement_mm':rms,'structure':st,'contact':con}
   print('PROJECT',dep,mwgt,'FAILURES',fail,'angles',[st[f'edge{ei}_deg'] for ei in [6675,6602,6676]],'constraint deficit',method['final_max_constraint_deficit'],'maxmove',float(ds.max()),flush=True)
  if str(dep) in feasible and first is None:first=dep
  matrix.update({'attempts':attempts,'first_structurally_feasible_support_depth':first,'explicit_hinge_constraint_refinement':True})
  dump('SUPPORT_DEPTH_FEASIBILITY_MATRIX_R2.json',matrix);dump('FEASIBLE_SOLVES_R2.json',{'first':first,'solutions':feasible});dump('CORE_HINGE_CONSTRAINT_TRACE_R2.json' if core_constraints else 'CONSTRAINT_PROJECTION_TRACE_R2.json',trace)
