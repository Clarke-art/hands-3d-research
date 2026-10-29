import sys
sys.dont_write_bytecode=True
from semantic_audit import *
reuse(R3DIR/'solve.py',['operators','hinge_gradient'],globals())
ix,lap,full,H,W,lc,fc=operators(IDS);WB=np.kron(W,np.eye(3));NVAR=len(IDS)*3
prior=np.array(R3['solves']['R3_B_S4_V3']['target_world_mm'])
boundary_edges=boundary_domain(IDS)[0]

def objective(v):
 core=R['core_vertices'];d=v[IDS]-V[IDS];loss=float(np.mean(np.sum((v[core]-prior[core])**2,axis=1))+.05*np.sum(d*(H@d))/len(IDS));a=angles(v);bl=float(np.mean((a[boundary_edges]-baseA[boundary_edges])**2))
 return {'dent_depth_mm':depth(v),'edge6676_angle_deg':float(a[6676]),'reference_surrounding_continuity_loss_mm2':loss,'boundary_normal_progression_loss_deg2':bl}

def derivatives(v):
 q=(v-origin)@B;res=q[:,2]-feat(q)@cf;i=min(R['core_vertices'],key=lambda i:res[i]);gd=np.zeros((len(IDS),3));gd[ix[i]]=-n+(cf[1]+2*cf[3]*q[i,0]+cf[4]*q[i,1])*x+(cf[2]+cf[4]*q[i,0]+2*cf[5]*q[i,1])*y
 dotval,gg=hinge_gradient(v,6676,ix);ga=-(180/math.pi)*gg/max(math.sqrt(1-dotval*dotval),1e-9);gc=.1*(H@(v[IDS]-V[IDS]))/len(IDS)
 active=i
 for i in R['core_vertices']:gc[ix[i]]+=2*(v[i]-prior[i])/len(R['core_vertices'])
 return [gd.ravel(),ga.ravel(),gc.ravel()],{'depth_active_vertex':active,'gradient_names':['depth_mm','hinge_deg','continuity_mm2'],'depth_is_frozen_surrounding_diagnostic_not_anatomy_target':True}

def volume_grad(v,z):
 p=v[list(z)];a,b,c=p[1:]-p[0];gg=[None,np.cross(b,c),np.cross(c,a),np.cross(a,b)];gg[0]=-sum(gg[1:]);g=np.zeros((len(IDS),3))
 for i,t in zip(z,gg):
  if i in ix:g[ix[i]]+=t
 return g.ravel()

def cone(glist,rows=None,equalities=None):
 # Linearized minimum-metric-norm descent witness. This only solves a vector
 # cone, not positions; no objective continuation or repair geometry is made.
 rows=[] if rows is None else rows;mat=[];rhs=[]
 for g in glist:
  size=np.linalg.norm(g)
  if size>1e-12:mat.append(-g/size);rhs.append(.05)
 for row in rows:
  size=np.linalg.norm(row)
  if size>1e-12:mat.append(row/size);rhs.append(0.)
 A=np.array(mat);b=np.array(rhs);d=np.zeros(NVAR);dual=np.zeros(len(b));q=WB@A.T;den=np.sum(A*q.T,axis=1)
 for iteration in range(1000):
  for j in range(len(b)):
   delta=max(-dual[j],(b[j]-A[j]@d)/max(den[j],1e-18));dual[j]+=delta;d+=delta*q[:,j]
  residual=float(max(0,np.max(b-A@d)))
  if residual<1e-9:break
 return d,{'linear_constraint_count':len(b),'rank':int(np.linalg.matrix_rank(A)),'iterations':iteration+1,'max_linearized_deficit':residual,'algorithm':'Dual coordinate metric projection (Hildreth) in frozen displacement/gradient/bending metric','no_infeasibility_proof_if_no_witness':True}

def field(d):
 vv=np.zeros_like(V);dd=d.reshape(-1,3);maxv=np.linalg.norm(dd,axis=1).max()
 if maxv<1e-14:return vv
 vv[IDS]=dd/maxv;return vv

def separation_gradient(v,baseline_contacts):
 best=None
 for a,b in broad(v,IDS,band=.1):
  if common(a,b) or tuple(sorted((int(owners[a]),int(owners[b])))) in baseline_contacts:continue
  m=tri_pair_metrics(v,tri[a],tri[b])
  if m['distance_mm']<1e-12:continue
  if best is None or m['distance_mm']<best[0]:best=(m['distance_mm'],a,b,m)
 if best is None:return None
 dist,a,b,m=best;p,q=np.array(m['closest_world_mm']);axis=(p-q)/dist;g=np.zeros((len(IDS),3))
 for ids,weights,sign in [(tri[a],m['a_weights'],1),(tri[b],m['b_weights'],-1)]:
  for i,w in zip(ids,weights):
   if i in ix:g[ix[i]]+=sign*w*axis
 return g.ravel(),{'face_ids':[int(owners[a]),int(owners[b])],'triangle_indices':[int(a),int(b)],'minimum_separation_mm':dist,'closest_features':m,'existing_intersections_excluded_from_new-separation_stat':True}

def warning_rows(v):
 rr=POINT['accepted_iterations'][-1]['active_separation_constraints'];rows=[];metadata=[];seen=set()
 for z in rr:
  if 'four_point_vertex_ids' not in z:continue
  key=tuple(z['four_point_vertex_ids'])
  if key in seen:continue
  seen.add(key);sign=z['preserved_sign'];g=sign*volume_grad(v,key);val=sign*signed_volume(v,key);rows.append(g);metadata.append({'face_ids':z['face_ids'],'vertex_ids':list(key),'sign':sign,'current_signed_volume_mm3':val,'role':'R3 conservative four-point side warning; finite-feature membership must decide whether structural.'})
 return rows,metadata

def finite_event_rows(v,d,new_contacts):
 rows=[];info=[]
 for pair,rr in new_contacts.items():
  i,j=rr['triangle_indices'];aa=tri[i];bb=tri[j];features=[]
  for p in aa:features.append((int(p),*map(int,bb)))
  for p in bb:features.append((int(p),*map(int,aa)))
  for k in range(3):
   for l in range(3):features.append((int(aa[k]),int(aa[(k+1)%3]),int(bb[l]),int(bb[(l+1)%3])))
  for z in sorted(set(features)):
   if len(set(z))!=4:continue
   a=signed_volume(v,z);b=signed_volume(v+d,z)
   if a*b<=0 and abs(a)>1e-14:
    sign=1 if a>0 else -1;rows.append(sign*volume_grad(v,z));info.append({'face_ids':list(pair),'four_point_vertex_ids':list(z),'classification':'Side row activated only after an exact finite off-feature contact was certified in this micro trial.'})
 return rows,info

def inspect_micro(v,df,amp,basecontacts):
 vv=v+amp*df;cc,count=exact_certified(vv,IDS);new=set(cc)-set(basecontacts);ts=np.where(np.isin(owners,list(face_domain(IDS))))[0];sweeparea=swept_min_area(v,amp*df,ts);ns=normals(vv);reversed_faces=[fi for fi in face_domain(IDS) if normal(v,F[fi])@ns[fi]<0];proj0={fi:projected_cross(v,fi) for fi in [2771,3332,3351]};proj1={fi:projected_cross(vv,fi,np.array(proj0[fi]['projection_chart'])) for fi in proj0};projreg=all(not proj1[fi]['flag'] or proj0[fi]['flag'] for fi in proj0);srcprojblock=any(proj1[fi]['flag'] for fi in proj1 if fi in face_domain(IDS));oldengine,num=exact(vv,IDS);oldbase,n0=exact(V,IDS);oldnew=set(oldengine)-set(oldbase);cont,cdevent=ccd(v,vv,IDS,set(oldbase));strpass=not new and not reversed_faces and sweeparea['minimum_fan_triangle_area_mm2']>1e-10
 return {'step_max_mm':amp,'new_exact_true3D_contacts':[{'face_ids':list(k),**cc[k]} for k in sorted(new)],'true3D_gate_pass':strpass,'reconciled_gate_pass':strpass and projreg,'CURRENT_R3_FULL_GATE_PASS':strpass and not oldnew and cont and not srcprojblock,'CURRENT_R3_ITERATION_GATE_PASS':not oldnew and cont and not reversed_faces,'absolute_projected_flag_blocker_present':srcprojblock,'projection_specific_no_new_flag':projreg,'r3_float_contacts':list(map(list,sorted(oldnew))),'R3_CCD_supplement':cdevent,'swept_triangle_area':sweeparea,'new_reference_hemisphere_reversals':reversed_faces,'exact_contact_coverage':count,'raw_metrics':objective(vv),'certification_scope':'Native fan triangulation, stored binary64 geometry, new contact families relative to frozen baseline; source-existing contact classifications disclosed separately. No Full42 or anatomy judgment.'}, {k:cc[k] for k in new}

def run():
 output={};direction_audit=[]
 frozen_contacts,_=exact_certified(V,IDS)
 for label,v in [('FROZEN_BASELINE',V),('R3_BEST_FAILED_POINT',P)]:
  grads,gmeta=derivatives(v);oldrows,warnmeta=warning_rows(v);dj,coneinfo=cone(grads);dc,currentcone=cone(grads,oldrows);sep=separation_gradient(v,set(frozen_contacts));g=sum(g/max(np.linalg.norm(g),1e-12) for g in grads)
  dirs={'JOINT_METRIC_GRADIENT':field(-(WB@g)),'JOINT_DESCENT_CONE_TRUE3D':field(dj),'JOINT_DESCENT_CONE_R3_SIDE_ROWS':field(dc)}
  hist=(P-V)[IDS]
  for suffix,axis in [('VALLEY_AXIS_TANGENT',y),('CROSS_VALLEY_TANGENT',x),('SURFACE_NORMAL',n)]:dirs[suffix]=field(np.outer(hist@axis,axis).ravel())
  dirs['HISTORICAL_NET_DIRECTION_MICRO_ONLY']=field(hist.ravel())
  baseobj=objective(v);records=[];realrows=[];realrowinfo=[]
  for name,df in dirs.items():
   dr=df[IDS].ravel();j=[float(a@dr) for a in grads];hm=1e-5;plus=objective(v+hm*df);minus=objective(v-hm*df);bder=(plus['boundary_normal_progression_loss_deg2']-minus['boundary_normal_progression_loss_deg2'])/(2*hm);micro=[];badfirst=None
   for amp in [1e-6,1e-5,1e-4]:
    rr,bad=inspect_micro(v,df,amp,frozen_contacts);micro.append(rr)
    if bad and badfirst is None:badfirst=(amp,bad)
   if badfirst:
    newrows,info=finite_event_rows(v,badfirst[0]*df,badfirst[1]);realrows.extend(newrows);realrowinfo.extend(info)
   derivatives_record={'objective_derivative_normalized_sum':float(sum(j0/max(np.linalg.norm(gg),1e-12) for j0,gg in zip(j,grads))),'dent_depth_derivative_mm_per_mm_peak':j[0],'edge6676_derivative_deg_per_mm_peak':j[1],'reference_continuity_derivative_mm2_per_mm_peak':j[2],'minimum_new_nonshared_separation_derivative_mm_per_mm_peak':float(sep[0]@dr) if sep else None,'minimum_separation_feature':sep[1] if sep else None,'boundary_normal_progression_loss_derivative_deg2_per_mm_peak':bder,'R3_shared_off_edge_volume_margin_derivatives_mm3_per_mm_peak':[{'feature':mm,'derivative':float(gr@dr)} for gr,mm in zip(oldrows,warnmeta)],'off_edge_margin_note':'There is no strictly positive pair-wide distance for legal adjacency. These finite-feature side derivatives are warnings, not a uniform surface gap. Exact off-simplex contact decides the hard gate.'}
   rec={'direction_name':name,'baseline_label':label,'nonzero':bool(np.max(abs(df))>1e-12),'normal_tangent_component_RMS':{a:float(np.sqrt(np.mean((df[IDS]@axis)**2))) for a,axis in [('cross_valley',x),('valley_axis',y),('normal',n)]},'derivatives':derivatives_record,'all_three_objective_components_descend':all(z<-1e-8 for z in j),'micro_steps':micro,'variable_vertex_indices_for_mathematics_only':IDS,'normalized_direction_vectors_world':df[IDS].tolist(),'coordinate_arrays_or_geometry_candidates_saved':False};records.append(rec);direction_audit.append(rec)
   print('PROBE',label,name,'derivatives',j,'true/reconciled',[r['reconciled_gate_pass'] for r in micro],'iteration',[r['CURRENT_R3_ITERATION_GATE_PASS'] for r in micro],flush=True)
  if realrows:
   drr,inf=cone(grads,realrows);df=field(drr);j=[float(a@df[IDS].ravel()) for a in grads];micro=[]
   for amp in [1e-6,1e-5,1e-4]:
    rr,bad=inspect_micro(v,df,amp,frozen_contacts);micro.append(rr)
   rec={'direction_name':'FINITE_CONTACT_ACTIVATED_JACOBIAN_CONE','baseline_label':label,'nonzero':bool(np.max(abs(df))>1e-12),'derivatives':{'dent_depth_derivative_mm_per_mm_peak':j[0],'edge6676_derivative_deg_per_mm_peak':j[1],'reference_continuity_derivative_mm2_per_mm_peak':j[2]},'all_three_objective_components_descend':all(z<-1e-8 for z in j),'micro_steps':micro,'variable_vertex_indices_for_mathematics_only':IDS,'normalized_direction_vectors_world':df[IDS].tolist(),'exact_finite_contact_activation_rows':realrowinfo,'linear_cone':inf};records.append(rec);direction_audit.append(rec);print('CONTACT_CONE',label,j,[r['reconciled_gate_pass'] for r in micro],flush=True)
  exists=any(r['all_three_objective_components_descend'] and any(z['reconciled_gate_pass'] for z in r['micro_steps']) for r in records);iterexists=any(r['all_three_objective_components_descend'] and any(z['CURRENT_R3_ITERATION_GATE_PASS'] and z['true3D_gate_pass'] for z in r['micro_steps']) for r in records)
  output[label]={'source':ref(R3DIR/'COLLISION_CONSTRAINED_SOLVE_AUDIT_R3.json') if label.startswith('R3') else L['stages']['STAGE4C_R2_RAW']['input'],'baseline_metrics':baseobj,'objective_gradients':{name:gr.reshape(-1,3).tolist() for name,gr in zip(gmeta['gradient_names'],grads)},'gradient_metadata':gmeta,'normalized_objective_Jacobian_rank':int(np.linalg.matrix_rank(np.array(grads))),'true3D_cone_construction':coneinfo,'R3_active_side_cone_construction':currentcone,'warning_feature_rows':warnmeta,'directions':records,'TRUE_3D_ONLY_GATESET_FEASIBLE_DESCENT_EXISTS':exists,'RECONCILED_GATESET_FEASIBLE_DESCENT_EXISTS':exists,'CURRENT_R3_ITERATION_GATESET_FEASIBLE_DESCENT_WITNESS_FOUND':iterexists,'CURRENT_R3_FULL_GATESET_FEASIBLE_DESCENT_EXISTS':False,'full_gate_no_descent_proof':'At the frozen and failed points, affected projected bowties are strict crossings with interior parameters. Continuity preserves their flags in an open infinitesimal neighborhood, while R3 final eligibility requires their absolute elimination. The initial point itself fails that eligibility condition. This is a terminal-gate statement, not a proof that R3 iterative tangent space is empty.'}
  dump('LOCAL_FEASIBLE_DESCENT_ANALYSIS_R1.json',{'analysis_scope':'Local Jacobians and normalized direction vectors only. No geometry optimization beyond micro amplitude1e-4mm, no candidate generation.','variable_vertex_count':len(IDS),'variable_dimension':NVAR,'maximum_micro_step_mm':1e-4,'tolerance_class':'COMPUTATIONAL_GEOMETRY_TOLERANCE','anatomy_clearance':False,'points':output,'global_position_only_infeasibility_proved':False})
  dump('NORMAL_TANGENT_COUPLED_DIRECTION_AUDIT_R1.json',{'directions':direction_audit,'combined_directions_are_mathematical_vectors_only':True,'coordinate_repairs_saved':False,'candidate_count':0})
 if __name__=='__main__':pass
if __name__=='__main__':run()
