from coupled_model import *
t=time.monotonic();p,data=load_problem();save('TIME_COUPLED_CONSTRAINT_CONTRACT.json',p.interface());rows=[]
for i,node in enumerate(p.nodes):
 z=p.initial[i];j1=node.jac(z,1e-3);j2=node.jac(z,1e-4);j3=node.jac(z,1e-5);diff=abs(j2-j3);rows.append(dict(node=i,coarse_vs_fine_max=float(abs(j1-j2).max()),fine_vs_finer_max=float(diff.max()),relative_frobenius=float(np.linalg.norm(j2-j3)/max(np.linalg.norm(j3),1e-12)),unstable_variables=np.flatnonzero(diff.max(0)>1e-3),verified=bool(diff.max()<1e-3),stats=node.stats,switch_log=node.switch_log,face_signature=node.signature[0]))
tick=time.perf_counter();J=np.array(p.jfun(p.x0));jacsec=time.perf_counter()-tick;h=1e-4;cols=[]
for k in range(len(p.x0)):
 step=h*(.1 if k%12>=10 else 1);delta=np.eye(len(p.x0))[k]*step;cols.append((np.array(p.gfun(p.x0+delta)).ravel()-np.array(p.gfun(p.x0-delta)).ravel())/(2*step))
fd=np.array(cols).T;err=abs(J-fd);missing=int(np.sum((abs(J)<1e-12)&(abs(fd)>1e-5)));sp=p.jfun.sparsity_out(0);rr,cc=sp.get_triplet();save('JACOBIAN_SPARSITY.json',dict(shape=J.shape,rows=rr,columns=cc,source='CasADi dependency of local callbacks and adjacent AD constraints; dense intra-node fallback, no manual zeroing'))
# Inspect nearest separating axes independently at seed; no claimed smoothness for changes.
from triangle_distance import distances
axisrows=[]
for i,node in enumerate(p.nodes):
 z=p.initial[i];U=unroot(skin(state(z)),state(z));dist,a,b=distances(U[TR[node.pairs[:,0]]],U[TR[node.pairs[:,1]]]);axes=(a-b)/np.maximum(dist[:,None],1e-12);axisrows.append(dict(node=i,min_candidate_pair_distance_mm=float(dist.min()*1000),axis_difference_max=float(np.linalg.norm(axes-node.axes,axis=1).max()),note='Seed check only; frozen separating-axis certificates never replace final full BVH acceptance'))
result=dict(status='LOCAL_BRANCH_VERIFIED' if all(r['verified'] for r in rows) and err.max()<1e-3 and not missing else 'NONSMOOTH_DERIVATIVE_PARTIAL',node_checks=rows,full_jacobian_seconds=jacsec,global_vs_block_max_abs=float(err.max()),missing_nonzeros=missing,shape=J.shape,structural_nonzeros=sp.nnz(),axis_checks=axisrows,total_seconds=time.monotonic()-t,universal_branch_claim=False,solver_safe_fallback='Recompute central FD on current actual face/key branch; abort if no projected pulp face. Unobserved self pairs must pass full Blender acceptance.')
save('DERIVATIVE_GUARD_VALIDATION.json',result);print(result['status'],result['global_vs_block_max_abs'],jacsec,p.violation(p.x0)[0],flush=True)
