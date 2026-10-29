import json as _lock_json
from pathlib import Path as _LockPath
if __name__ == "__main__" and _lock_json.loads((_LockPath(__file__).resolve().parent / "POLICY_LOCK.json").read_text(encoding="utf-8"))["no_more_solves"]:
    raise SystemExit("STOP — HUMAN REVIEW: completed experiment is locked; use a separately authorized run")
import sys,time,json,ast,os
from pathlib import Path
sys.dont_write_bytecode=True;os.environ['PYTHONUTF8']='1'
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
import derivative_probe as d
from derivative_probe import ca,np,P,F,skin,state,I,ContactDerivative,save
start=time.monotonic();rows=[]
def timing(f,x,n=3):
 ts=[]
 for _ in range(n):
  d.check();t=time.perf_counter();y=f(x);ts.append(time.perf_counter()-t)
 return np.array(y),ts
# Original graph, no solver and no historical writes. Exactly three recorded nodes.
src=(P/'solve_trajectory.py').read_text();src=src[:src.index('meta=dict(')]
src=src.replace("assert not json.loads((O/'POLICY_LOCK.json').read_text()).get('no_more_solves',True),'STOP HUMAN REVIEW: new solve is not authorized by this completed run'",'')
src=src.replace('from symbolic_skin import *','from symbolic_skin import *\nO=Path(r"'+str(P)+'")')
src=src.replace("data=np.load(O/'COLLOCATION_KEY_STATES.npz')","data={k:v[[5,6,7]] for k,v in dict(np.load(O/'COLLOCATION_KEY_STATES.npz')).items()}")
sys.path.insert(0,str(P));ns={ '__file__':str(P/'solve_trajectory.py')};t=time.perf_counter();exec(compile(src,'original_three_node_graph','exec'),ns);x=ns['x0'];G=ns['G'];X=ns['X'];old=ca.Function('original_three_jac',[X],[ca.jacobian(G,X)]);build=time.perf_counter()-t
jold,ot=timing(old,x);_,gt=timing(ns['gfun'],x)
# Stage node geometry derivatives before pulling them back to Bernstein coefficients.
# All non-geometric constraints kept identical in a separate symbolic block.
names=ns['names'];indices=[]
for n in names:
 if n['name'].startswith(('material_contact','witness_region','pad_region','pad_height','key_certificate','self_chart')):indices.extend(range(n['start'],n['start']+n['count']))
other=[i for i in range(G.numel()) if i not in set(indices)];rest=ca.Function('other_jac',[X],[ca.jacobian(G[other],X)])
nodeproblems=[];maps=[];position=[]
for it,tim in enumerate(ns['data']['times']):
 ph=0 if tim<ns['J']-1e-9 else 1;s=(tim-(ns['start'] if ph==0 else ns['J']))/ns['dur'][ph]
 zz=ns['curve'](ns['C'][ph],s,ns['dur'][ph]);maps.append(ca.Function('map'+str(it),[X],[zz,ca.jacobian(zz,X)]))
 cts=I['contacts'] if abs(tim-ns['J'])<1e-9 else [I['contacts'][0 if tim<ns['J'] else 1]]
 nodeproblems.append(ContactDerivative(cts,ns['data']['angles'][it],float(tim),(d.LOW,d.HIGH)))
 def belongs(n):
  return any(n['name']==p+str(it) or n['name'].startswith(p+str(it)+'_') for p in ['material_contact_','witness_region_','pad_region_','pad_height_','key_certificate_','self_chart_'])
 position.append([i for n in names if belongs(n) for i in range(n['start'],n['start']+n['count'])])
def chained(x):
 out=np.zeros((G.numel(),X.numel()));out[other]=np.array(rest(x))
 for p,m,ii in zip(nodeproblems,maps,position):
  z,M=m(x);p.cache=None;val,j=p.value_jac(np.array(z).ravel());out[ii]=<REDACTED_EMAIL>(M)
 return out
jnew,nt=timing(chained,x);direction=np.sin(np.arange(len(x))+1);h=1e-4;fd=(np.array(ns['gfun'](x+h*direction)).ravel()-np.array(ns['gfun'](x-h*direction)).ravel())/(2*h)
save('MULTINODE_PERFORMANCE.json',dict(case='J4 original three adjacent collocation nodes',times=ns['data']['times'],variables=X.numel(),constraints=G.numel(),old_build_seconds=build,old_jac_seconds=ot,new_jac_seconds=nt,constraint_eval_seconds=gt,speedup=np.median(ot)/np.median(nt),old_new_max_abs=abs(jold-jnew).max(),directional_max_abs=abs(fd-jnew@direction).max(),structural_nnz=old.sparsity_out(0).nnz(),numerical_nnz=int(np.sum(abs(jnew)>1e-12)),node_pullbacks=[np.array(m(x)[1]).tolist() for m in maps],scope='Includes unchanged C2, coefficient velocity/acceleration and wrist/mapped joint-rate constraints; not trajectory solve'))
print('MULTI',ot,nt,'speedup',np.median(ot)/np.median(nt),'error',abs(jold-jnew).max(),flush=True)
# J3 branch diagnosis: locate rows and compare one-sided derivatives.
junction=json.loads((O.parent/'hands_contact_junction_compatibility_r1/runs/junction_2.json').read_text());z=np.array(junction['latent']);aa=np.load(O/'BOUNDARY_KEY_STATES.npz')['angles'][3];p=ContactDerivative(I['contacts'],aa,I['junction_time'],(d.LOW,d.HIGH));g,j=p.value_jac(z);issues=[]
for i in range(12):
 h=1e-5 if i>=10 else 1e-4;delta=np.eye(12)[i]*h;plus=(np.array(p.fun(z+delta)).ravel()-g)/h;minus=(g-np.array(p.fun(z-delta)).ravel())/h;ix=np.flatnonzero(abs(plus-minus)>1e-3)
 if len(ix):issues.append(dict(variable=i,value=z[i],rows=ix.tolist(),plus=plus[ix],minus=minus[ix],AD=j[ix,i]))
save('NONSMOOTH_DIAGNOSIS.json',dict(issues=issues,classification='NON_SMOOTH_OR_UNVERIFIED',no_optimizer_blame=True))
# Physical workload probes, no finite differences mislabeled as historical AD.
import contact_solver as cs
q=cs.ContactProblem(z,I['contacts'],aa);_,fulltime=timing(lambda x:(q.cache.clear(),q.evaluate(x))[1][1],z,3)
_,skintime=timing(lambda x:skin(state(x)),z,10);_,fktime=timing(lambda x:F(x)[1],z,10)
save('WORKLOAD_PROFILE.json',dict(full_skin_seconds=skintime,symbolic_full_skin_and_wrist_seconds=fktime,SLSQP_full_contact_collision_seconds=fulltime,full_detector_calls=q.calls,notes='FK+weighted skin fused in historical Skin; symbolic wrist call also computes full skin. No invented isolated FK timing. Historical IPOPT did not call Blender or LP detector per Jacobian.'))
save('EXTRA_BUDGET.json',dict(charged_seconds=time.monotonic()-start))
