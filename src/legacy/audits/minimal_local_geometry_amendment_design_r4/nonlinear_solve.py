import sys
sys.dont_write_bytecode=True
from local_analysis import *
from contact_components import registry,compare
from certified_path import certify
import time
npz=np.load(OUT/'R4_CONTACT_ANCHOR_NULLSPACE.npz');Z=np.eye(len(IDS));A=np.zeros((0,len(IDS)));Wc=W
base_components,anchors,_=registry(V,IDS,True)
core=R['core_vertices'];coreidx=[ix[i] for i in core];incident=sorted(face_domain(IDS));corefaces=face_domain(core);alledges=sorted({ei for fi in incident for ei in FE[fi]});coreedges=[ei for ei in alledges if set(EF[ei])<=corefaces];target_depth_fraction=.4
refs=read(R3DIR/'HEALTHY_DORSAL_MCP_REFERENCE_PATCH_AUDIT_R3.json')['reference_candidates'];reference95=float(np.percentile([a for r in refs for a in r['native_normal_progression'].values()],95));hinge_design_target=max(30.,reference95+15.)
target_z=Q[core,2]+(1-target_depth_fraction)*np.maximum(0,-(Q[:,2]-feat(Q)@cf)[core]);target_world_prior=np.array(R3['solves']['R3_B_S4_V3']['target_world_mm']);sets,_=nested();outer=sorted(set(IDS)-sets[3]);taper=np.array([1.5 if i in outer else .12 if i not in sets[2] else .02 for i in IDS])
farray=np.array(F);prev=np.roll(farray,1,axis=1);nxt=np.roll(farray,-1,axis=1)

def skew(a):return np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
def native_jacobian(v):
 ns=normals(v);ar=areas(v);J={}
 for fi in incident:
  projector=(np.eye(3)-np.outer(ns[fi],ns[fi]))/max(2*ar[fi],1e-14)
  for k,vi in enumerate(F[fi]):
   if vi in ix:J[(fi,vi)]=projector@skew(v[F[fi][(k-1)%4]]-v[F[fi][(k+1)%4]])
 return ns,J
def dot_grad(ns,J,ei):
 a,b=EF[ei];g=np.zeros((len(IDS),3))
 for fi,other in [(a,b),(b,a)]:
  for vi in F[fi]:
   if (fi,vi) in J:g[ix[vi]]+=J[(fi,vi)].T@ns[other]
 return float(ns[a]@ns[b]),g
def objective4(v,gradient=True):
 d=v[IDS]-V[IDS];q=(v-origin)@B;g=np.zeros_like(d);metrics={};r=q[core,2]-target_z;metrics['dent_surrounding_relative_target']=float(np.mean(r*r));g[coreidx]+=2*r[:,None]*n/len(core)
 ns,J=native_jacobian(v);angle_loss=0.;progress_loss=0.;boundary_loss=0.
 for ei in coreedges:
  val,gg=dot_grad(ns,J,ei);theta=math.acos(max(-1,min(1,val)));target=math.radians(hinge_design_target if ei==6676 else min(float(baseA[ei]),max(reference95,35.)));excess=max(0,theta-target);weight=2. if ei==6676 else .08/len(coreedges);angle_loss+=weight*excess*excess
  if excess:g+=-2*weight*excess*gg/max(math.sqrt(max(0,1-val*val)),1e-9)
 for ei in boundary_edges:
  val,gg=dot_grad(ns,J,ei);src=math.cos(math.radians(float(baseA[ei])));r0=val-src;weight=.8/len(boundary_edges);boundary_loss+=weight*r0*r0;g+=2*weight*r0*gg
 continuation=lc@(v[IDS]-target_world_prior[IDS]);metrics['healthy_surrounding_continuation']=.08*float(np.mean(np.sum(continuation**2,axis=1)));g+=.16*lc.T@continuation/len(core)
 metrics['hinge_normal_progression']=angle_loss;metrics['outer_normal_progression']=boundary_loss;metrics['position_penalty']=.01*float(np.sum(d*d));metrics['gradient_bending_penalty']=.05*float(np.sum(d*(H@d)))-metrics['position_penalty'];g+=.1*(H@d)
 metrics['outer_falloff_penalty']=float(np.sum(taper[:,None]*d*d));g+=2*taper[:,None]*d
 return sum(metrics.values()),g,metrics

def anchor_row(a):
 row=np.zeros(len(IDS))
 for i,w in zip(a['triangle_vertex_ids'],a['barycentric_weights']):
  if i in ix:row[ix[i]]+=w
 return row
source_lengths=[];dynamic_lengths=[];sum_length_constraints=[]
for pair,comps in base_components.items():
 for comp in comps:
  sourcepoints=[]
  for rr in comp['fan_contact_records']:
   tt=rr['triangle_indices'][0]
   for p in rr['points_world_mm']:
    anchor=next(a for a in anchors if a['triangle_vertex_ids']==list(map(int,tri[tt])) and a['fixed_intersection_point_world_mm']==p);sourcepoints.append((np.array(p),anchor_row(anchor)))
  for (p,ap),(q,aq) in __import__('itertools').combinations(sourcepoints,2):
   le=np.linalg.norm(p-q)
   if le>1e-10:source_lengths.append((p-q,ap-aq,le,comp['component_id']))
  functions=[];segments=[]
  for rr in comp['fan_contact_records']:
   ff=[(rr,feat) for feat in rr['feature_identity']]
   if len(ff)==2:segments.append(tuple(ff))
   functions.extend(ff)
  for u,w in __import__('itertools').combinations(functions,2):dynamic_lengths.append((u,w,comp['segment_extent_mm'],comp['component_id']))
  sum_length_constraints.append((segments,comp['sum_fan_intersection_lengths_mm'],comp['component_id']))

def endpoint_float(v,desc):
 rr,f=desc;a,b=rr['triangle_indices']
 for side in ['a','b']:
  if f[side]['kind']=='VERTEX':return v[f[side]['vertex_ids'][0]].copy()
 for side,other in [('a',tri[b]),('b',tri[a])]:
  if f[side]['kind']=='EDGE':
   i,j=f[side]['vertex_ids'];e=v[j]-v[i];p=v[other];normal=np.cross(p[1]-p[0],p[2]-p[0]);den=normal@e
   if abs(den)>1e-14:return v[i]+e*(normal@(p[0]-v[i]))/den
 raise ValueError('Unresolved finite contact endpoint')

def extent_gradient(v,u,w):
 pu=endpoint_float(v,u);pw=endpoint_float(v,w);dist=np.linalg.norm(pu-pw)
 if dist<1e-10:return dist,np.zeros((len(IDS),3))
 direction=(pu-pw)/dist;g=np.zeros((len(IDS),3));pool=set()
 for desc in [u,w]:
  for tt in desc[0]['triangle_indices']:pool.update(map(int,tri[tt]))
 h=1e-5;vv=v.copy()
 for vi in pool&set(IDS):
  for k in range(3):
   old=vv[vi,k];vv[vi,k]=old+h;plus=endpoint_float(vv,u)-endpoint_float(vv,w);vv[vi,k]=old-h;minus=endpoint_float(vv,u)-endpoint_float(vv,w);vv[vi,k]=old;g[ix[vi],k]=direction@((plus-minus)/(2*h))
 return dist,g

def project_constraints(v,direction,trust):
 dcur=v[IDS]-V[IDS];pairs=broad(v,IDS,band=.05);rows=[];details=[];sharedskip=0;closest=[]
 # Re-identify finite endpoint barycentric coordinates at this iteration.
 # Positive coordinates retain their feature; no anatomical gap is imposed.
 feature_rows=[];current,_,_=registry(v,IDS)
 for comps in current.values():
  for comp in comps:
   for rr in comp['fan_contact_records']:
    for f in rr['feature_identity']:
     desc=(rr,f);pool=set(map(int,tri[rr['triangle_indices']].ravel()))&set(IDS)
     for side,tt in zip(['a','b'],rr['triangle_indices']):
      aa=tri[tt];active=set(f[side]['vertex_ids'])
      def weights(vv):
       p=vv[aa];u=p[1]-p[0];w=p[2]-p[0];r=endpoint_float(vv,desc)-p[0];den=(u@u)*(w@w)-(u@w)**2
       b=((r@u)*(w@w)-(r@w)*(u@w))/den;c=((r@w)*(u@u)-(r@u)*(u@w))/den
       return np.array([1-b-c,b,c])
      values=weights(v);jac=np.zeros((3,len(IDS),3));h=1e-5;vv=v.copy()
      for vi in pool:
       for k in range(3):
        old=vv[vi,k];vv[vi,k]=old+h;plus=weights(vv);vv[vi,k]=old-h;minus=weights(vv);vv[vi,k]=old;jac[:,ix[vi],k]=(plus-minus)/(2*h)
      for k,vi in enumerate(aa):
       if int(vi) in active and values[k]>0 and np.linalg.norm(jac[k])>1e-12:
        rows.append((jac[k],-.8*values[k]));feature_rows.append({'component_id':comp['component_id'],'fan_triangle':tt,'positive_barycentric_vertex':int(vi),'current_weight':float(values[k])})
 for a,b in pairs:
  aa=tri[a];bb=tri[b];pair=tuple(sorted([int(owners[a]),int(owners[b])]));shared=set(aa)&set(bb)
  if pair in base_components:continue
  if len(shared)==2:
   e0,e1=sorted(shared);u=next(i for i in aa if i not in shared);w=next(i for i in bb if i not in shared);edge=v[e1]-v[e0];ur=v[u]-v[e0];wr=v[w]-v[e0];ur-=edge*(ur@edge)/(edge@edge);wr-=edge*(wr@edge)/(edge@edge)
   if ur@wr>0:
    zz=(e0,e1,u,w);sv=signed_volume(v,zz);sign=1 if sv>=0 else -1;gg=sign*volume_grad(v,zz).reshape(-1,3);rows.append((gg,-.8*abs(sv)));details.append({'face_ids':list(pair),'feature':'SAME_SIDE_SHARED_EDGE_OFF_EDGE_LIMIT','four_point_vertex_ids':list(zz),'signed_volume_mm3':abs(sv)})
   else:sharedskip+=1
   continue
  m=tri_pair_metrics(v,aa,bb);dist=m['distance_mm']
  if dist<1e-10 and common(a,b):sharedskip+=1;continue
  if dist<=1e-12:continue
  if dist<.05:
   p,q=np.array(m['closest_world_mm']);axis=(p-q)/dist;gg=np.zeros((len(IDS),3))
   for tt,ww,sign in [(aa,m['a_weights'],1),(bb,m['b_weights'],-1)]:
    for i,w in zip(tt,ww):
     if i in ix:gg[ix[i]]+=sign*w*axis
   rows.append((gg,-.8*dist));closest.append({'face_ids':list(pair),'distance_mm':dist,'closest_feature':m['feature_kind'],'vertex_ids':[list(map(int,aa)),list(map(int,bb))]})
 for u,w,limit,cid in dynamic_lengths:
  try:size,gg=extent_gradient(v,u,w)
  except ValueError:continue
  if np.linalg.norm(gg)>1e-12:rows.append((-gg,-max(0,limit-size)))
 for segs,limit,cid in sum_length_constraints:
  size=0.;gg=np.zeros((len(IDS),3))
  for u,w in segs:
   dist,g0=extent_gradient(v,u,w);size+=dist;gg+=g0
  if np.linalg.norm(gg)>1e-12:rows.append((-gg,-max(0,limit-size)))
 dd=direction.copy();prepared=[]
 for gg,bound in rows:
  wg=Wc@gg;den=float(np.sum(gg*wg))
  if den>1e-16:prepared.append((gg,bound,wg,den))
 dual=np.zeros(len(prepared))
 for iteration in range(250):
  worst=0.
  for j,(gg,bound,wg,den) in enumerate(prepared):
   deficit=bound-float(np.sum(gg*dd));step=max(-dual[j],deficit/den);dual[j]+=step;dd+=step*wg;worst=max(worst,deficit)
  if worst<1e-10:break
 for cycle in range(16):
  for gg,bound in rows:
   pred=float(np.sum(gg*dd));wg=Wc@gg;den=float(np.sum(gg*wg))
   if pred<bound and den>1e-16:dd+=(bound-pred)*wg/den
  for u,w,limit,cid in dynamic_lengths:
   vv=v.copy();vv[IDS]+=dd
   try:size,gg=extent_gradient(vv,u,w)
   except ValueError:continue
   wg=Wc@gg;den=float(np.sum(gg*wg))
   if size>limit and den>1e-16:dd-=(size-limit+1e-10)*wg/den
  for segs,limit,cid in sum_length_constraints:
   vv=v.copy();vv[IDS]+=dd;size=0.;gg=np.zeros((len(IDS),3))
   for u,w in segs:
    dist,g0=extent_gradient(vv,u,w);size+=dist;gg+=g0
   wg=Wc@gg;den=float(np.sum(gg*wg))
   if size>limit and den>1e-16:dd-=(size-limit+1e-10)*wg/den
  peak=np.linalg.norm(dd,axis=1).max()
  if peak>trust:dd*=trust/peak
 return dd,{'fresh_swept_proximity_fan_pairs':len(pairs),'reidentified_finite_corner_side_rows':details,'reidentified_closest_features':closest,'legal_shared_simplex_rows_released':sharedskip,'source_component_nonlinear_extent_constraints':len(dynamic_lengths),'barycentric_parameters_reidentified_not_frozen':True,'active_rows_not_carried_from_previous_iteration':True,'normal_and_both_tangents_solved_together':True}

def projection_diagnostics(v):
 result={};worsening=[]
 for fi in [2771,3332,3351]:
  src=projected_cross(V,fi);chart=np.array(src['projection_chart']);cur=projected_cross(v,fi,chart)
  def overlap(points):
   pp=np.c_[points,np.zeros(4)];return intersection(pp,[0,1,2],[0,2,3],[0,2],[[0,2]])['coplanar_overlap_area_mm2']
  a=overlap(src['points_chart_mm']);b=overlap(cur['points_chart_mm']);result[str(fi)]={'baseline':src,'current':cur,'fixed_chart_projected_fan_overlap_area_before_mm2':a,'fixed_chart_projected_fan_overlap_area_after_mm2':b,'no_regression':len(cur['hits'])<=len(src['hits']) and b<=a+1e-7}
  if not result[str(fi)]['no_regression']:worsening.append(fi)
 return result,worsening

def run():
 v=V.copy();trace=[];rejects=[];certificates=[];features=[];start=time.time();trust=.08;reason=None;best=v.copy();bestloss=objective4(v)[0]
 if '--resume-certified' in sys.argv:
  live=read(OUT/'R4_LIVE_NONLINEAR_TRACE.json');v=np.array(live['world_mm']);trace=live['iterations'];rejects=live['rejections'];certificates=read(OUT/'R4_CONTINUOUS_COLLISION_CERTIFICATE.json')['accepted_step_certificates'];features=read(OUT/'R4_FEATURE_REIDENTIFICATION_AUDIT.json')['iterations'][:len(trace)];best=v.copy();bestloss=objective4(v)[0]
 print('START coupled nonlinear S4',len(IDS),'contact coincidence rank',len(IDS)-Z.shape[1],'reference95',reference95,'relative depth target',target_depth_fraction,flush=True)
 for iteration in range(len(trace),90):
  loss,g,terms=objective4(v);direction=-(Wc@g);peak=np.linalg.norm(direction,axis=1).max()
  if peak>trust:direction*=trust/peak
  direction,reid=project_constraints(v,direction,trust);features.append({'iteration':iteration,**reid});slope=float(np.sum(g*direction));accepted=False;amplitude=1.
  if slope>=-1e-12:reason='NONLINEAR_CONSTRAINED_DIRECTION_NO_MERIT_DESCENT';break
  for trial in range(15):
   nxtv=v.copy();nxtv[IDS]+=amplitude*direction;newloss,_,newterms=objective4(nxtv);gate=None
   if newloss>loss+1e-4*amplitude*slope:gate={'kind':'NONLINEAR_MERIT_LINE_SEARCH'}
   if gate is None:
    diag,pw=projection_diagnostics(nxtv)
    if pw:gate={'kind':'PROJECTED_NO_REGRESSION','faces':pw}
   if gate is None:
    st=structure(nxtv,IDS)
    if st['new_degenerate_faces'] or st['new_boundary_sharp_folds']:gate={'kind':'BOUNDARY_OR_DEGENERACY','folds':st['new_boundary_sharp_folds'],'degenerate':st['new_degenerate_faces']}
   if gate is None:
    reg,_,coverage=registry(nxtv,IDS);comp=compare(base_components,reg)
    if not comp['PASS']:gate={'kind':'COMPONENT_IDENTITY_OR_EXTENT','new':[z['component_id'] for z in comp['new_true_contact_components']],'worse':comp['worsening_components'],'expansion':comp['feature_expansions']}
   if gate is None:
    continuous,cert=certify(v,nxtv,base_components,reg)
    if not continuous:gate={'kind':'CONTINUOUS_CERTIFICATE','detail':cert}
   if gate is None:
    dump(f'accepted_steps/step_{iteration:03}.json',{'before_world_mm_on_support':v[IDS].tolist(),'after_world_mm_on_support':nxtv[IDS].tolist(),'support_ids':IDS,'before_full_coordinate_sha256':digest(v.tolist()),'after_full_coordinate_sha256':digest(nxtv.tolist()),'outside_support_unchanged':True});cert.update({'before_full_coordinate_sha256':digest(v.tolist()),'after_full_coordinate_sha256':digest(nxtv.tolist()),'coordinate_evidence':f'accepted_steps/step_{iteration:03}.json'});accepted=True;actual=float(np.linalg.norm(nxtv[IDS]-v[IDS],axis=1).max());v=nxtv;record={'iteration':iteration,'objective':newloss,'objective_terms':newterms,'accepted_step_fraction':amplitude,'actual_step_max_mm':actual,'core_depth_mm':depth(v),'edge6676_deg':float(angles(v)[6676]),'component_no_worsening':comp,'source_component_coincidence_residual':float(np.max(abs(A@(v[IDS]-V[IDS])))) if len(A) else None};trace.append(record);certificates.append({'iteration':iteration,**cert})
    if newloss<bestloss:bestloss=newloss;best=v.copy()
    dump('R4_LIVE_NONLINEAR_TRACE.json',{'method':'Coupled nonlinear merit/trust-region descent with reidentified finite-feature halfspaces, existing-contact convex extent balls and exact continuous certificates.','iterations':trace,'rejections':rejects,'world_mm':v.tolist(),'not_human_candidate':True})
    dump('R4_CONTINUOUS_COLLISION_CERTIFICATE.json',{'accepted_step_certificates':certificates,'every_accepted_step_certified':True,'accepted_step_count':len(certificates),'endpoint_only_used_for_safety':False,'full_baseline_to_diagnostic_endpoint_path_certified':True});dump('R4_FEATURE_REIDENTIFICATION_AUDIT.json',{'iterations':features,'feature_reidentification_each_iteration':True,'pair_wide_shared_gap_mm':0,'new_anatomy_clearance_mm':0})
    print('ACCEPT',iteration,'objective',round(newloss,8),'depth',round(depth(v),6),'hinge',round(record['edge6676_deg'],6),'step',actual,'alpha',amplitude,'elapsed',round(time.time()-start,1),flush=True);break
   rejects.append({'iteration':iteration,'trial':trial,'fraction':amplitude,**gate});amplitude*=.5
  if not accepted:reason='NO_CERTIFIED_NONLINEAR_STEP';break
  if depth(v)<.6*depth(V) and angles(v)[6676]<90:reason='DESIGN_OBJECTIVE_MILESTONE_REQUIRES_VISUAL_REVIEW';break
  if actual<1e-6:reason='CERTIFIED_PROGRESS_STALLED';break
  if iteration>5 and trace[-6]['objective']-trace[-1]['objective']<1e-7:reason='NONLINEAR_MERIT_PROGRESS_STALLED';break
 audit={'phase':PHASE,'SOLVER_FORMULATION':'COUPLED_NONLINEAR_TRUST_REGION_FEATURE_AWARE_CONSTRAINED_DESCENT','support_depth':4,'support_ids':IDS,'nonlinear_iteration_count':len(features),'accepted_iterations':trace,'rejected_trials':rejects,'termination':reason or 'NONLINEAR_ITERATION_LIMIT','world_mm':best.tolist(),'baseline_metrics':objective(V),'final_metrics':objective(best),'nonlinear_objective_baseline':objective4(V)[0],'nonlinear_objective_final':bestloss,'objective_components':['Surrounding-relative dent reduction','Healthy reference native normal progression','Reference continuation consistency','Displacement magnitude','First-order displacement gradient','Second-order bending','Outer displacement falloff and boundary normal progression'],'reference95_deg_is_shape_prior_not_anatomy_threshold':reference95,'hinge_soft_design_target_deg':hinge_design_target,'absolute_reference_depth_width_curvature_copied':False,'component_coincidence_rank_per_axis':len(IDS)-Z.shape[1],'contact_component_extent_constraints':len(source_lengths),'position_only_global_infeasibility_proved':False,'candidate_status':'UNQUALIFIED_SOLVER_DIAGNOSTIC_PENDING_STRUCTURE_AND_VISUAL','S5_not_attempted':'Only enter for demonstrated S4 boundary transition conflict.','S6_constructed':False,'elapsed_seconds':time.time()-start}
 dump('R4_NONLINEAR_SOLVER_AUDIT.json',audit);dump('R4_FEATURE_REIDENTIFICATION_AUDIT.json',{'iterations':features,'feature_reidentification_each_iteration':True,'pair_wide_shared_gap_mm':0,'new_anatomy_clearance_mm':0});dump('R4_CONTINUOUS_COLLISION_CERTIFICATE.json',{'accepted_step_certificates':certificates,'every_accepted_step_certified':all(z['status']=='CERTIFIED_CONTINUOUS_SAFE' for z in certificates),'accepted_step_count':len(certificates),'rejected_unresolved_intervals_never_accepted':True,'endpoint_only_used_for_safety':False,'full_baseline_to_diagnostic_endpoint_path_certified':bool(certificates)});print('TERMINATION',audit['termination'],'ACCEPTED',len(trace),flush=True)
if __name__=='__main__':run()
