import sys,ast,json,time
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));from skin_proxy import *
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
P=O.parent/'hands_skin_collision_static_feasibility_r1';pre=json.loads((O/'MINIMAL_PREFLIGHT_REGRESSION.json').read_text(encoding='utf-8-sig'));assert pre['status']=='MINIMAL_REGRESSION_PASS'
WEIGHTS=json.loads((P/'SOLVER_WEIGHT_LOCK.json').read_text(encoding='utf-8-sig'));WEIGHTS.update(triangle_witness_clearance=60.,true_clipped_face_contact=25.,pad_inset_mm=.2,witness_allowed_intrusion_mm=.05,prepared_middle=.25,prepared_interval=8.)
lock=O/'REPAIR_WEIGHT_LOCK.json'
if lock.exists():assert json.loads(lock.read_text(encoding='utf-8-sig'))==WEIGHTS
else:lock.write_text(json.dumps(WEIGHTS,indent=2)+'\n',encoding='utf8')
tri=RAW['triangles'];labels=np.array(META['triangle_labels']);triangle_ids=[np.flatnonzero(labels==j) for j in range(5)];fvertex=[np.unique(tri[ids]) for ids in triangle_ids];sampleids=[ids[::5] for ids in fvertex];targetpatch=[np.array(p) for p in META['pad_patches']]
tree=ast.parse((P/'solve_static_skin.py').read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['prepkey','keyPenalty','selfPenalty','contactResidual']],type_ignores=[]),'reused_static_solver','exec'))
tree=ast.parse((O/'geometry_detector.py').read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['clip','area','keylocal','keyworld','contact_metric']],type_ignores=[]),'reused_actual_contact','exec'))
TR=tri;LABEL=labels;D=RAW;rot=c.axisrot
patchset=set(targetpatch[0]);patchtris=np.array([i for i in triangle_ids[0] if all(int(v) in patchset for v in tri[i])])
# Freeze the material witness barycentric coordinates from BOTH recorded failures.
witnesses=[]
for a in pre['S1']:witnesses+=a['witness_constraints']
staticB=json.loads((ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/STATIC_REFINEMENT_POLICY_R2.json').read_text(encoding='utf-8-sig'))['joint_increment_bounds_deg'];B=np.array([staticB['THUMB' if j==0 else 'LONG'] for j in range(5)])
ai=int(sys.argv[-1]);seed=np.array(pre['S1'][ai]['state']);angles=np.array(pre['S1'][ai]['key_angles']);pieces=prepkey(angles,67,1);midi=67;finger=1
pllookup={(note,j):(N,d) for note in set(w['midi'] for w in witnesses) for j,(_,N,d,lo,hi) in enumerate([pp for pp in pieces if pp[0]==note])}
# Reused helper's contact metric clips entire frozen pulp faces to the actual depressed playable top.
def face_residual(V):
 ct=contact_metric(V,c.KEYS[46],angles[46],1);g=ct['true_pulp_min_signed_gap_mm']
 if g is None:g=ct['pad_gap_mm']
 return np.array([(g-WEIGHTS['numerical_contact_settle_mm'])*WEIGHTS['true_clipped_face_contact']])
def witness_residual(V):
 out=[]
 for w in witnesses:
  point=np.array(w['barycentric'])@V[tri[w['triangle_id']]];N,d=pllookup[(w['midi'],w['piece'])];signed=np.max(point@N.T-d)*1000
  allowed=WEIGHTS['witness_allowed_intrusion_mm'] if w['legal_target'] else 0.
  out.append(max(-signed-allowed,0)*WEIGHTS['triangle_witness_clearance'])
 # Face centroids add fixed material samples; final acceptance still exact triangle LP.
 cent=V[tri[patchtris]].mean(1)
 for note,N,d,l,h in pieces:
  if note!=67:continue
  out.extend(np.maximum(-np.max(cent@N.T-d,axis=1)*1000-.05,0)*WEIGHTS['triangle_witness_clearance'])
 return np.array(out)
# One controlled actual-surface feedback for attempt 2, no restart or weight sweep.
self_witness=[]
if ai==1:
 from triangle_distance import distances
 actual=json.loads((O/'S1_REPAIR_1_ACTUAL_VALIDATION.json').read_text(encoding='utf-8-sig'));VS=skin(seed)
 for pair in actual['actual_geometry']['self_skin']:
  for ta,tb in pair['triangle_pair_ids']:
   dd,pp,qq=distances(VS[tri[[ta]]],VS[tri[[tb]]]);axis=pp[0]-qq[0]
   if np.linalg.norm(axis)<1e-10:raise RuntimeError('No credible separating axis in second recorded seed')
   axis/=np.linalg.norm(axis);self_witness.append(dict(triangles=[ta,tb],axis=axis.tolist(),seed_exact_gap_mm=float(dd[0]*1000)))
 (O/'SECOND_ATTEMPT_SURFACE_FEEDBACK.json').write_text(json.dumps(dict(weight_source='Existing triangle_witness_clearance=60, no retuning',desired_separation_mm=.3,constraints=self_witness),indent=2)+'\n',encoding='utf8')
fixed=ai==0
if fixed:
 low=np.r_[[-150,-30],[-8,-8,-12],B[:,0].ravel()];high=np.r_[[60,35],[8,8,12],B[:,1].ravel()];x0=np.r_[seed[:2],seed[3:]]
 def state(x):return np.r_[x[:2],seed[2],x[2:]]
else:
 low=np.r_[[-150,-30,-12.2172473],[-8,-8,-12],B[:,0].ravel()];high=np.r_[[60,35,12], [8,8,12],B[:,1].ravel()];x0=seed.copy()
 def state(x):return x.copy()
x0=np.clip(x0,low+1e-8,high-1e-8);start=time.monotonic();deadline=start+140;calls=0;history=[];best=[np.inf,x0.copy()]
class BudgetStop(Exception):pass

def residual(x):
 global calls
 calls+=1
 if time.monotonic()>deadline:raise BudgetStop()
 st=state(x);V=skin(st);oldct=contactResidual(V,67,1,angles[46]);oldct[2]=0 # Replace vertex-only contact with clipped complete-face contact.
 k=c.KEYS[46];pad=keylocal(V,k,angles[46])[int(RAW['pad_indices'][0])];sur=k['key_top_playable_surface'];errs=[pad[:2]-np.clip(pad[:2],[s['xmin']+.0002,s['ymin']+.0002],[s['xmax']-.0002,s['ymax']-.0002]) for s in sur];pe=errs[int(np.argmin([e@e for e in errs]))]
  # Conservative fixed separating axes from disjoint seed faces; no collision can pass solely on this proxy.
 actualself=[]
 for sw in self_witness:
  ta,tb=sw['triangles'];axis=np.array(sw['axis']);gap=(np.min(V[tri[ta]]@axis)-np.max(V[tri[tb]]@axis))*1000
  actualself.append(max(.3-gap,0)*WEIGHTS['triangle_witness_clearance'])
 kp=keyPenalty(V,pieces,67,1);sp=selfPenalty(V);out=[oldct,face_residual(V),witness_residual(V),pe*1000*WEIGHTS['pad_inside'],kp*WEIGHTS['full_skin_key_clearance'],sp*WEIGHTS['self_skin_signed_nearest_proxy'],(st[6:]-seed[6:])*WEIGHTS['joint_prior_deg'],(st[:3]-seed[:3])*WEIGHTS['root_xy_prior_mm'],st[3:6]*WEIGHTS['root_rotation_prior_deg']]
 # E5 preparation contract, with a weak centered preference and strong interval penalty.
 ek=c.KEYS[55];ep=keylocal(V,ek,angles[55])[int(RAW['pad_indices'][2])];s=ek['key_top_playable_surface'][0];goal=np.array([ek['key_center'][0],.035,s['z']+.012]);out.append((ep-goal)*1000*WEIGHTS['prepared_middle']);g=(ep[2]-s['z'])*1000;out.append(np.array([g-np.clip(g,4,20)])*WEIGHTS['prepared_interval']);out.append((ep[:2]-np.clip(ep[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']]))*1000*WEIGHTS['prepared_interval'])
 out.append(np.array(actualself));r=np.concatenate(out);cost=float(r@r)
 if cost<best[0]:
  best[:]=[cost,x.copy()];history.append(dict(call=calls,elapsed_seconds=time.monotonic()-start,cost=cost,state=st.tolist(),clipped_contact_residual=float(out[1][0]),witness_peak_residual=float(np.max(out[2]))))
 return r
try:
 fit=least_squares(residual,x0,bounds=(low,high),max_nfev=55,ftol=1e-6,xtol=1e-6,gtol=1e-6,x_scale='jac');chosen=fit.x;conv=dict(success=bool(fit.success),nfev=fit.nfev,status=int(fit.status),message=fit.message,optimality=float(fit.optimality))
except BudgetStop:
 chosen=best[1];conv=dict(success=False,nfev=None,status='WALL_BUDGET_STOP',message='Per-attempt 140 second wall ceiling reached, best evaluated state retained')
st=state(chosen);elapsed=time.monotonic()-start
result=dict(attempt=ai+1,initialization=pre['S1'][ai]['initialization'],state=st.tolist(),key_angles=angles.tolist(),source_time=pre['S1'][ai]['source_time'],root_z_fixed=fixed,elapsed_seconds=elapsed,residual_calls=calls,convergence=conv,cost=best[0],history=history,proxy_contact=contact_metric(skin(st),c.KEYS[46],angles[46],1),witness_count=len(witnesses),patch_triangle_count=len(patchtris),not_acceptance=True,weights_lock=str(lock))
(O/f'REPAIR_ATTEMPT_{ai+1}.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print('TARGETED_REPAIR_FINISHED',ai+1,elapsed,calls,conv,result['proxy_contact'],flush=True)


