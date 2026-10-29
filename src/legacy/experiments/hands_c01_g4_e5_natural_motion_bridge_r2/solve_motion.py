import sys,json,time
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
from motion_model import *
from triangle_distance import distances
from scipy.optimize import minimize
assert not (O/'MOTION_CANDIDATE.npz').exists(),'Only one trajectory'
assert json.loads((O/'ENDPOINT_ACTUAL_2.json').read_text())['status']=='ENDPOINT_GATES_PASS'
started=time.monotonic();endpoint_seconds=sum(json.loads((O/f'ENDPOINT_SOLVE_{i}.json').read_text())['elapsed_seconds'] for i in [1,2]);deadline=started+min(280,600-endpoint_seconds)
class BudgetStop(Exception):pass
def budget():
 if time.monotonic()>deadline:raise BudgetStop()
# Entire candidate jointly optimized. Verified start/end retained; full-press body retained,
# thumb may release smoothly and return during the E5 hold rather than snap back in35ms.
Yseed=np.array([ZS+(ZE-ZS)*np.clip((t-START)/(FULL-START),0,1) for t in K])
for ki,spread in [(1,-4),(2,14),(3,26),(4,26),(5,0)]:Yseed[ki,9]=spread
Yseed[4,:6]=ZE[:6];Yseed[4,10:]=ZE[10:];Yseed[5,:6]=ZE[:6];Yseed[5,10:]=ZE[10:]
Yseed[0]=ZS;Yseed[-1]=ZE
mask=np.zeros_like(Yseed,dtype=bool);mask[1:4,:]=True;mask[4:6,6:10]=True
x0=Yseed[mask];lo=np.tile(LOW,(len(K),1))[mask];hi=np.tile(HIGH,(len(K),1))[mask];x0=np.clip(x0,lo+1e-9,hi-1e-9)
def assemble(x):
 Y=Yseed.copy();Y[mask]=x;return Y
reference=curve(assemble(x0))(TC);ids=[np.flatnonzero(LABEL==j) for j in range(5)];neighbors=META['topological_vertex_neighbors'];models=[]
safeU=[unroot(skin(state(z)),state(z)) for z in [ZS,ZE]]
for ci,(t,z,angles) in enumerate(zip(TC,reference,KA)):
 budget();st=state(z);V=skin(st);U=unroot(V,st);pieces=prepkey(angles,67 if t<=EXCHANGE else 76,1 if t<=EXCHANGE else 3);pointrows=[]
 # Cheap material witness constraints; complete triangles are reserved for actual acceptance.
 TV=V[TR];tl=TV.min(1);th=TV.max(1)
 for note,N,d,blo,bhi in pieces:
  if np.any(V.max(0)<blo-.003) or np.any(V.min(0)>bhi+.003):continue
  signed=V@N.T-d;vd=np.max(signed,axis=1);vv=np.flatnonzero((vd<.003)&np.all(V>=blo-.004,1)&np.all(V<=bhi+.004,1))
  for v in vv:
   plane=int(np.argmax(signed[v]));pointrows.append((np.array([v,v,v]),np.array([1.,0,0]),N[plane],float(d[plane]),.20 if (note==67 and t<=EXCHANGE) or (note==76 and t>=EXCHANGE) else .10))
  cand=np.flatnonzero(np.all(th>=blo-1e-8,1)&np.all(tl<=bhi+1e-8,1))
  if len(cand):
   sig=np.einsum('tvi,ni->tvn',TV[cand],N)-d;cand=cand[np.all(np.min(sig,1)<=1e-8,1)]
  for ti in cand:
   dep,w=triangle_inside_depth(TV[ti],np.c_[N,d])
   if dep<=1e-4:continue
   beta=np.linalg.lstsq(np.column_stack([TV[ti,1]-TV[ti,0],TV[ti,2]-TV[ti,0]]),w-TV[ti,0],rcond=None)[0];bar=np.r_[1-beta.sum(),beta]
   plane=int(np.argmax(w@N.T-d));pointrows.append((TR[ti],bar,N[plane],float(d[plane]),.20 if (note==67 and t<=EXCHANGE) or (note==76 and t>=EXCHANGE) else .10))
 pp=set()
 for j in range(5):
  for k in range(j+1,5):
   A=U[TR[ids[j]]];BB=U[TR[ids[k]]];al=A.min(1);ah=A.max(1);bl=BB.min(1);bh=BB.max(1)
   for ii,ta in enumerate(ids[j]):
    delta=np.maximum(np.maximum(bl-ah[ii],al[ii]-bh),0)
    for bi in np.flatnonzero(np.sum(delta*delta,1)<=.003**2):
     tb=int(ids[k][bi])
     if tb in neighbors[int(ta)] or set(TR[ta])&set(TR[tb]):continue
     pp.add((int(ta),tb))
 pairs=np.array(sorted(pp),dtype=int).reshape(-1,2)
 ds,pa,pb=distances(U[TR[pairs[:,0]]],U[TR[pairs[:,1]]]);axes=(pa-pb)/np.maximum(ds[:,None],1e-12)
 sep=(np.min(np.einsum('pvi,pi->pv',U[TR[pairs[:,0]]],axes),1)-np.max(np.einsum('pvi,pi->pv',U[TR[pairs[:,1]]],axes),1))
 for bad in np.flatnonzero((ds<1e-10)|(sep< -1e-9)):
  pair=pairs[bad];found=False
  for SU in safeU:
   dd,aa,bb=distances(SU[TR[pair[:1]]],SU[TR[pair[1:]]])
   if dd[0]>1e-10:axes[bad]=(aa[0]-bb[0])/dd[0];found=True;break
  if not found:raise RuntimeError('No credible endpoint-based separation axis')
 if pointrows:
  vi=np.array([p[0] for p in pointrows]);bar=np.array([p[1] for p in pointrows]);normal=np.array([p[2] for p in pointrows]);offset=np.array([p[3] for p in pointrows]);allow=np.array([p[4] for p in pointrows])
 else:vi=np.zeros((0,3),int);bar=np.zeros((0,3));normal=np.zeros((0,3));offset=np.zeros(0);allow=np.zeros(0)
 models.append(dict(vertices=vi,bary=bar,normal=normal,offset=offset,allowed=allow,pairs=pairs,axes=axes,angles=angles,time=float(t),cache={}))
setup=time.monotonic()-started;calls=0;cellcalls=0;jcalls=0;iters=0;best=[np.inf,x0.copy()];history=[]
def cell(ci,z):
 global cellcalls
 m=models[ci];key=z.tobytes()
 if key in m['cache']:return m['cache'][key]
 cellcalls+=1;st=state(z);V=skin(st);U=unroot(V,st);t=m['time'];angles=m['angles'];out=[]
 for note,finger in ([(67,1)] if t<EXCHANGE-1e-10 else [(67,1),(76,3)] if abs(t-EXCHANGE)<1e-10 else [(76,3)]):
  k=c.KEYS[note-21];surface=k['key_top_playable_surface'][0];local=keylocal(V,k,angles[note-21]);ct=contact_metric(V,k,angles[note-21],finger);g=ct['true_pulp_min_signed_gap_mm']
  if g is None:g=float(np.min(local[np.array(META['pad_patches'][finger-1]),2]-surface['z'])*1000)
  p=local[int(RAW['pad_indices'][finger-1])]*1000
  out.extend([-g-.004,g+.020,p[0]-surface['xmin']*1000-.01,surface['xmax']*1000-.01-p[0],p[1]-surface['ymin']*1000-.01,surface['ymax']*1000-.01-p[1],3-abs(p[2]-surface['z']*1000)])
 points=np.einsum('wi,wij->wj',m['bary'],V[m['vertices']]);out.extend(np.einsum('wi,wi->w',points,m['normal'])*1000-m['offset']*1000+m['allowed'])
 gap=(np.min(np.einsum('pvi,pi->pv',U[TR[m['pairs'][:,0]]],m['axes']),1)-np.max(np.einsum('pvi,pi->pv',U[TR[m['pairs'][:,1]]],m['axes']),1))*1000-.02
 out.extend(gap)
 # Actual release risk is independently measured; prevent continuing to obstruct recovering G4.
 if t>=FULL-1e-10:
  kk=c.KEYS[46];loc=keylocal(V,kk,angles[46]);out.append(float(np.min(loc[np.array(META['pad_patches'][0]),2]-kk['key_top_playable_surface'][0]['z'])*1000)-.1)
 ans=np.array(out)
 if len(m['cache'])>150:m['cache'].clear()
 m['cache'][key]=ans
 return ans
def constraints(x):
 global calls
 budget();calls+=1;Y=assemble(x);Z=curve(Y)(TC);r=np.concatenate([cell(i,z) for i,z in enumerate(Z)]);v=float(max(-r.min(),0))
 if v<best[0]:
  best[:]=[v,x.copy()];history.append(dict(call=calls,elapsed_seconds=time.monotonic()-started,max_violation_mm=v))
 return r
def jac(x):
 global jcalls
 jcalls+=1;cols=[];h=.001
 for j in range(len(x)):
  a=x.copy();b=x.copy();a[j]+=h;b[j]-=h;cols.append((constraints(a)-constraints(b))/(2*h))
 return np.array(cols).T
# Smoothness costs only, all geometrical requirements are inequalities.
TO=np.linspace(START,END,101);scale=np.r_[[300,300,300],[180,180,180],[300,300,300,300],10,10]
def obj(x):
 f=curve(assemble(x));v=f.derivative()(TO)/scale;ac=f.derivative(2)(TO)/(scale*10)
 return float(np.mean(v*v)+.1*np.mean(ac*ac)+.0001*np.mean(((x-x0)/np.maximum(hi-lo,1))**2))
def objjac(x):
 h=.001;g=[]
 for j in range(len(x)):
  a=x.copy();b=x.copy();a[j]+=h;b[j]-=h;g.append((obj(a)-obj(b))/(2*h))
 return np.array(g)
def cb(x):
 global iters
 iters+=1;budget();print('ONE_BRIDGE_ITERATION',iters,round(time.monotonic()-started,3),'violation',float(max(-constraints(x).min(),0)),flush=True)
initial=constraints(x0)
try:
 fit=minimize(obj,x0,jac=objjac,method='SLSQP',bounds=list(zip(lo,hi)),constraints=[dict(type='ineq',fun=constraints,jac=jac)],callback=cb,options=dict(maxiter=45,ftol=1e-7,disp=True))
 chosen=fit.x;conv=dict(success=bool(fit.success),status=int(fit.status),message=str(fit.message),nit=int(fit.nit),nfev=int(fit.nfev),njev=int(fit.njev))
except BudgetStop:chosen=best[1];conv=dict(success=False,status='WALL_BUDGET_STOP',message='Single 280s bounded trajectory fit; no restart',nit=iters,nfev=None,njev=None)
Y=assemble(chosen);f=curve(Y);times=np.unique(np.r_[np.arange(START,END,1/120),K,TC,EXCHANGE,FULL,END]);states=np.array([state(z) for z in f(times)])
np.savez_compressed(O/'MOTION_CANDIDATE.npz',knots=K,latent_knots=Y,times=times,states=states,latent_states=f(times),latent_velocity=f.derivative()(times),latent_acceleration=f.derivative(2)(times))
out=dict(candidate_count=1,restarts=0,authority='DESIGN_PROVISIONAL',convergence=conv,elapsed_seconds=time.monotonic()-started,setup_seconds=setup,variables=len(x0),geometry_collocations=len(TC),constraint_calls=calls,actual_skin_cell_proxy_calls=cellcalls,jacobian_calls=jcalls,initial_constraint_violation_mm=float(max(-initial.min(),0)),retained_best_violation_mm=best[0],history=history,knots=K.tolist(),latent_knots=Y.tolist(),start_exact_B2=True,end_exact_verified_E5=True,full_press_body_exact_verified_E5=True,thumb_release_jointly_optimized=True,interpolation='C1 limited Hermite; all output must be independently baked/re-read',collision_proxy='Fixed local material witnesses and unrooted triangle separating axes; not globally equivalent to complete skin',key_witness_counts=[len(m['vertices']) for m in models],self_pair_counts=[len(m['pairs']) for m in models],max_wall_seconds=280,not_acceptance=True,video_authorized_only_after_actual_pass=True)
(O/'ONE_BRIDGE_SOLVE.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print('ONE_BRIDGE_FINISHED',out['elapsed_seconds'],conv,'best violation',best[0],flush=True)
