import sys
from common import *
locked();model=sys.argv[1] if len(sys.argv)>1 else 'A';assert model in ['A','B']
if model=='B':assert read(P/'MODEL_B_GATE_R1.json')['MODEL_B_AUTHORIZED_BY_EVIDENCE'] is True
assert not (P/f'MODEL_{model}_SOLUTION_R1.json').exists(),'NO_RESTART_OR_SECOND_SWEEP'
dof=read(P/'ROOT_POSE_DOF_POLICY_R1.json');temp=read(P/'ROOT_POSE_TEMPORAL_POLICY_R1.json');ev=read(P/'PRE_SOLVE_ORIENTATION_EVIDENCE_R1.json');motion=np.load(PRE/'hand_motion_canonical.npz');old=np.load(PRE/'spatial_evaluations.npz');angles=old['angles'];D=np.diff(np.eye(N),n=2,axis=0);lam=temp['lambda_xyz'];B=spline_basis();K=B.shape[1];dims=1 if model=='A' else 3;bound=np.radians([dof['bounds_degrees'][s][1] for s in ['YAW','PITCH','ROLL']][:dims]);curves={};spatial={'angles':angles};log={}
for side in ['R','L']:
 pads=motion[side+'_pads'];index=[];fingers=[];targets=[];weights=np.zeros(N)
 for i,t in enumerate(times):
  for n in active(t):
   if n['hand']!=side or n['finger'] is None:continue
   index.append(i);fingers.append(n['finger']-1);targets.append(target_for(keys[n['key_index']],angles[i,n['key_index']]));weights[i]+=1
 index=np.array(index);fingers=np.array(fingers);targets=np.array(targets);M=np.linalg.inv(np.diag(weights)+lam*D.T@D);leverage=dof['evidence']['wrist_to_middle_mcp_m'];heading=np.radians([r['heading_deg'] for r in ev[side]['source_wrist_observations']]);corridor=math.radians(dof['anatomical_orientation_prior']['heading_soft_corridor_deg'])
 def compute(x,full=False):
  coeff=x.reshape(K,dims);ang=np.zeros((N,3));ang[:,:dims]=B@coeff;R=rotations(ang);q=np.einsum('nij,nfj->nfi',R,pads);rhs=np.zeros((N,3));np.add.at(rhs,index,targets-q[index,fingers]);T=M@rhs
  contact=(q[index,fingers]+T[index]-targets).ravel();prior=np.sqrt(.01)*leverage*ang[:,:dims];smoothang=np.sqrt(lam)*leverage*(D@ang[:,:dims]);head=heading+ang[:,0];corr=leverage*(head-np.clip(head,-corridor,corridor));res=np.concatenate([contact,(np.sqrt(lam)*D@T).ravel(),smoothang.ravel(),prior.ravel(),corr])
  return (res,T,ang,R,q) if full else res
 if model=='A':x=np.zeros(K*dims)
 else:
  init=read(P/'MODEL_A_SOLUTION_R1.json')['hands'][side]['orientation_coefficients_rad'];x=np.zeros((K,dims));x[:,0]=np.array(init).reshape(K);x=x.ravel()
 lower=np.tile(-bound,K);upper=np.tile(bound,K);history=[];stop='MAX_ITERATIONS'
 for it in range(40):
  res=compute(x);cost=float(res@res);J=np.empty((len(res),len(x)));eps=1e-5
  for j in range(len(x)):
   d=x.copy();d[j]+=eps;J[:,j]=(compute(d)-res)/eps
  step=np.linalg.solve(J.T@J+np.eye(len(x))*1e-8,-J.T@res);accepted=False
  for alpha in [1,.5,.25,.125,.0625]:
   trial=np.clip(x+alpha*step,lower,upper);rr=compute(trial);new=float(rr@rr)
   if new<cost:accepted=True;break
  delta=float(np.max(np.abs(trial-x))) if accepted else 0;history.append({'iteration':it,'objective':cost,'accepted':accepted,'max_coefficient_step_rad':delta,'line_search_alpha':alpha})
  print('MODEL',model,side,'iter',it,'cost',round(cost,6),'delta',round(delta,6),flush=True)
  if not accepted:stop='NO_DESCENT';break
  x=trial
  if delta<1e-7:stop='CONVERGED';break
 res,T,ang,R,q=compute(x,True);V=np.einsum('nij,nvj->nvi',R,motion[side+'_verts'])+T[:,None,:];PP=q+T[:,None,:]
 for k,v in [('verts',V),('pads',PP),('roots',T),('orientation',ang),('rotation',R)]:spatial[side+'_'+k]=v
 curves[side]={'orientation_coefficients_rad':x.reshape(K,dims).tolist(),'orientation_421_rad':ang.tolist(),'translation_421_m':T.tolist(),'rotation_421_matrices':R.tolist(),'basis':'cubic cardinal spacing12 source observations','objective_final':float(res@res),'stop':stop,'iterations':len(history),'degrees_min':np.degrees(ang.min(0)).tolist(),'degrees_max':np.degrees(ang.max(0)).tolist(),'orientation_bound_saturated_coefficients':int(np.sum(np.isclose(x,lower,atol=1e-6)|np.isclose(x,upper,atol=1e-6))),'label_assignments_never_changed':True};log[side]=history
np.savez_compressed(P/f'model_{model.lower()}_evaluations.npz',**spatial)
dump(f'MODEL_{model}_SOLUTION_R1.json',{'model':model,'hands':curves,'policy_lock':read(P/'PRE_RESULT_POLICY_LOCK_R1.json'),'source_claim':'PRODUCT_SPATIALIZATION_LAYER_NOT_MOCAP','previous_rejected_model_rerun':False,'previous_solution_used_only_as_reference':True,'dynamic_rotation_dofs':dims,'finger_changes':0,'scale':1,'objective_comparison':'XYZ point-target and second-difference objective inherited unchanged; orientation adds bounded spline, temporal and anatomical priors. No contact-threshold or target change.'});dump(f'MODEL_{model}_SOLVER_LOG_R1.json',log)
print('MODEL_'+model+'_SOLVED',flush=True)
