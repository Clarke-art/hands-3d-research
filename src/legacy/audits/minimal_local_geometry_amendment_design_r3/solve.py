import sys
sys.dont_write_bytecode=True
from collision_engine import *
import time
sets,records=nested()
references=read(OUT/'HEALTHY_DORSAL_MCP_REFERENCE_PATCH_AUDIT_R3.json')['reference_candidates']

def operators(ids):
 ix={i:j for j,i in enumerate(ids)};stencil=sorted(set(ids)|{j for i in ids for j in adj[i]});lap=np.zeros((len(stencil),len(ids)));full=np.zeros((len(stencil),3))
 for row,i in enumerate(stencil):
  full[row]=Q[i]-np.mean(Q[list(adj[i])],axis=0)
  if i in ix:lap[row,ix[i]]=1
  for j in adj[i]:
   if j in ix:lap[row,ix[j]]-=1/len(adj[i])
 grad=[]
 for a,b in E:
  if a not in ix and b not in ix:continue
  row=np.zeros(len(ids));le=max(np.linalg.norm(V[a]-V[b]),.5)
  if a in ix:row[ix[a]]=1/le
  if b in ix:row[ix[b]]=-1/le
  grad.append(row)
 grad=np.array(grad);H=.2*np.eye(len(ids))+.3*grad.T@grad+lap.T@lap;W=np.linalg.inv(H)
 core_rows=[stencil.index(i) for i in R['core_vertices']];return ix,lap,full,H,W,lap[core_rows],full[core_rows]

def sample_reference_profile(q):
 r=references[0];cc=np.array(r['center_world_mm']);bb=np.array(r['surface_frame']);pp=(V-cc)@bb;scale=r['alignment_to_dent']['uniform_scale_reference_to_target'];pp*=scale
 out=[];faces=r.get('healthy_prior_face_ids',r['face_ids']);pool=r.get('healthy_prior_vertex_ids',r['support_vertex_ids'])
 for p in q:
  choices=[]
  for fi in faces:
   for k in range(1,len(F[fi])-1):
    vertices=[F[fi][0],F[fi][k],F[fi][k+1]];t=pp[vertices];mat=np.column_stack([t[1,:2]-t[0,:2],t[2,:2]-t[0,:2]])
    if abs(np.linalg.det(mat))<1e-8:continue
    uv=np.linalg.solve(mat,p[:2]-t[0,:2]);w=np.r_[1-uv.sum(),uv]
    if min(w)>=-1e-7:choices.append(float(w@t[:,2]))
  if choices:out.append(min(choices,key=abs))
  else:
   vi=min(pool,key=lambda i:np.linalg.norm(pp[i,:2]-p[:2]));out.append(float(pp[vi,2]))
 out=np.array(out);trend=np.column_stack([np.ones(len(q)),q[:,:2]]);out-=<REDACTED_EMAIL>(trend,out,rcond=None)[0]
 return out

def target(dep,family):
 ids=sorted(sets[dep]);ix,lap,full,H,W,lc,fc=operators(ids);strength=3.
 rhs=-strength*lc.T@fc;rhs[:,2]*=.3 if family=='A' else .5
 d=np.linalg.solve(H+strength*lc.T@lc,rhs)
 if family=='B':
  core=R['core_vertices'];profile=sample_reference_profile(Q[core]);sur=np.array(sorted(sets[dep]-sets[dep-1]));trend=np.column_stack([np.ones(len(sur)),Q[sur,:2]]);coef=np.linalg.lstsq(trend,Q[sur,2],rcond=None)[0];shape=np.column_stack([np.ones(len(core)),Q[core,:2]])@coef+profile
  # A small soft normalized profile transfer, with current-region arch retained.
  # Neither reference absolute width nor its absolute depth is a hard target.
  anch=np.zeros(len(ids));rr=np.zeros(len(ids))
  for i,h in zip(core,shape):anch[ix[i]]=.35;rr[ix[i]]=.35*(h-Q[i,2])
  d[:,2]=np.linalg.solve(H+strength*lc.T@lc+np.diag(anch),rhs[:,2]+rr)
 vv=V.copy();vv[ids]+=d@B.T
 return vv,ids,ix,W,H,lap

def hinge_gradient(v,ei,ix):
 a,b=EF[ei];g=np.zeros((len(ix),3));h=1e-4
 for vi in sorted((set(F[a])|set(F[b]))&set(ix)):
  for k in range(3):
   saved=float(v[vi,k]);v[vi,k]=saved+h;plus=normal(v,F[a])@normal(v,F[b]);v[vi,k]=saved-h;minus=normal(v,F[a])@normal(v,F[b]);v[vi,k]=saved;g[ix[vi],k]=(plus-minus)/(2*h)
 return float(normal(v,F[a])@normal(v,F[b])),g

def orientation(v,ids):
 fs=sorted(face_domain(ids));ns=normals(v);ar=areas(v);rev=[fi for fi in fs if baseN[fi]@n>=0 and (ns[fi]@n<-1e-8 or ns[fi]@baseN[fi]<0)];deg=[fi for fi in fs if ar[fi]<1e-8]
 old=globals()['FULLFS'];globals()['FULLFS']=fs
 # Imported function's globals belong to geometry; select affected native quads.
 import geometry
 saved=geometry.FULLFS;geometry.FULLFS=fs;bows=set(geometry.quad_bowties(v))-baseBow;geometry.FULLFS=saved
 return {'new_reversed_faces':rev,'new_degenerate_faces':deg,'new_bowtie_faces':sorted(bows),'minimum_area_mm2':float(min(ar[fs])),'positive_valid_baseline_orientation':not rev}

def solve(dep,family,maxiter=75):
 tv,ids,ix,W,H,lap=target(dep,family);v=V.copy();basecontacts,num=exact(V,ids);es=sorted({ei for fi in face_domain(ids) for ei in FE[fi]});anglelimit={ei:min(85.,max(35.,float(baseA[ei])+10)) for ei in es if baseA[ei]<90};reference95=float(np.percentile(list(references[0]['native_normal_progression'].values()),95));crease_target=60. if family=='A' else max(30.,reference95);anglelimit[6676]=crease_target
 history=[];rejects=[];totproximity=0;start=time.time();stop=None
 for it in range(maxiter):
  # Target attraction is kept soft; sequential hinge and separation projection
  # uses the same displacement/gradient/bending metric over complete support.
  direction=np.zeros_like(v);direction[ids]=.15*(tv[ids]-v[ids]);ns=normals(v)
  active=sorted([ei for ei,limit in anglelimit.items() if ns[EF[ei][0]]@ns[EF[ei][1]]<math.cos(math.radians(limit))-1e-6],key=lambda ei:ns[EF[ei][0]]@ns[EF[ei][1]]-math.cos(math.radians(anglelimit[ei])))
  for ei in active:
   current,g=hinge_gradient(v,ei,ix);shortfall=math.cos(math.radians(anglelimit[ei]))-current-float(np.sum(g*direction[ids]));dd=W@g;denom=float(np.sum(g*dd))
   if denom>1e-16 and shortfall>0:direction[ids]+=dd*min(shortfall,.15)/denom
  peak=float(np.linalg.norm(direction[ids],axis=1).max())
  if peak>.15:direction*=.15/peak
  act=[]
  for projectionpass in range(3):
   direction,rows,tested,bp=near_constraints(v,ids,W,ix,direction);act.extend(rows);totproximity+=tested
   direction,side_rows=contact_direction_projection(v,ids,W,ix,direction,set(basecontacts));act.extend(side_rows)
  accepted=False;alpha=1.;reason=None
  for trial in range(13):
   nxt=v+alpha*direction;ori=orientation(nxt,ids)
   if any(ori[k] for k in ['new_reversed_faces','new_degenerate_faces','new_bowtie_faces']):reason={'gate':'ORIENTATION_AREA_BOWTIE','detail':ori}
   else:
    cc,checked=exact(nxt,ids);new=set(cc)-set(basecontacts)
    if new:reason={'gate':'EXACT_CONTACT','face_pairs':[list(z) for z in sorted(new)]}
    else:
     continuous,ct=ccd(v,nxt,ids,set(basecontacts))
     if not continuous:reason={'gate':'CONTINUOUS_CONTACT','detail':ct}
     else:
      # Check native orientation also at deterministic interior motion samples.
      interior=[orientation(v+t*(nxt-v),ids) for t in [.25,.5,.75]]
      bad=[z for z in interior if any(z[k] for k in ['new_reversed_faces','new_degenerate_faces','new_bowtie_faces'])]
      if bad:reason={'gate':'INTERIOR_ORIENTATION','detail':bad}
      else:
       accepted=True;v=nxt;break
   rejects.append({'iteration':it,'trial':trial,'step_fraction':alpha,**reason});alpha*=.5
  if not accepted:stop='CONSTRAINED_STEP_STALLED';break
  an=angles(v);hist={'iteration':it,'accepted_step_fraction':alpha,'actual_step_max_mm':float(alpha*np.linalg.norm(direction[ids],axis=1).max()),'active_hinge_edges':active,'active_separation_constraints':act,'whole_mesh_proximity_pairs':bp,'exact_pairs_tested':checked,'new_exact_contact_count':0,'orientation':ori,'continuous_collision':ct,'edge6676_deg':float(an[6676]),'target_edge6676_deg':crease_target,'target_residual_RMS_mm':float(np.sqrt(np.mean((tv[ids]-v[ids])**2)))};history.append(hist)
  dump(f'LIVE_TRACE_{family}_S{dep}.json',{'world_mm':v.tolist(),'iterations':history,'rejected_steps':rejects})
  if it%10==0:print('ITER',dep,family,it,'angle',an[6676],'step',hist['actual_step_max_mm'],'active collision',len(act),'elapsed',round(time.time()-start,1),flush=True)
  if hist['actual_step_max_mm']<1e-5:stop='CONSTRAINED_PROGRESS_STALLED';break
  if an[6676]<=crease_target+.15 and not active and it>10:stop='HINGE_AND_CONTINUITY_CONVERGED';break
 st=structure(v,ids);cc,num=exact(v,ids);new=sorted(set(cc)-set(basecontacts));newobtuse=[ei for ei in es if baseA[ei]<90 and angles(v)[ei]>=90];ds=np.linalg.norm(v-V,axis=1)
 failures=[]
 for key in ['new_quad_bowties','new_reference_reversed_faces','new_previously_outward_normal_reversals','new_degenerate_faces','new_boundary_sharp_folds']:
  if st[key]:failures.append(key)
 if new:failures.append('NEW_EXACT_CONTACT')
 if newobtuse:failures.append('NEW_INTERNAL_OBTUSE_EDGE')
 if st['edge6676_deg']>crease_target+.3:failures.append('CORE_NOTCH_TARGET_UNMET')
 if st['fixed_reference_core_depth_mm']>=depth(V)-.15:failures.append('DEPTH_IMPROVEMENT_INSUFFICIENT')
 return {'attempt_id':f'R3_{family}_S{dep}','family':family,'support_depth':dep,'support_ids':ids,'world_mm':v.tolist(),'target_world_mm':tv.tolist(),'accepted_iterations':history,'rejected_steps':rejects,'termination':stop or 'ITERATION_LIMIT','structure':st,'contact':{'new_pairs':[{'face_ids':list(k),**cc[k]} for k in new],'baseline_local_pairs':[list(k) for k in sorted(basecontacts)],'final_local_pairs':[{'face_ids':list(k),**z} for k,z in cc.items()],'triangle_pairs_tested':num,'proximity_features_tested_during_loop':totproximity},'failures':failures,'status':'STRUCTURALLY_FEASIBLE_PENDING_VISUAL' if not failures else 'FAIL_CLOSED_SOLVE','max_displacement_mm':float(max(ds)),'RMS_displacement_mm':float(np.sqrt(np.mean(ds[ids]**2))),'actual_write_vertex_ids':[i for i in ids if ds[i]>1e-7],'crease_design_target_deg':crease_target,'elapsed_seconds':time.time()-start}

if __name__=='__main__':
 results={}
 if (OUT/'COLLISION_CONSTRAINED_SOLVE_AUDIT_R3.json').exists():results=read(OUT/'COLLISION_CONSTRAINED_SOLVE_AUDIT_R3.json').get('solves',{})
 chosen=[int(sys.argv[1])] if len(sys.argv)>1 and sys.argv[1]!='--healthy-B' else [3,4,5]
 for dep in chosen:
  for family in (['B'] if '--healthy-B' in sys.argv else ['A','B']):
   key=f'R3_{family}_S{dep}_'+('V3' if '--healthy-B' in sys.argv else 'V2')
   if key in results:continue
   assert not any(records[dep]['authority_intersections'].values())
   res=solve(dep,family);res['attempt_id']=key;res['implementation_revision']='V3: healthy central reference patch excludes outer display context' if '--healthy-B' in sys.argv else 'V2 exact coordinate restoration in finite differences, adjacent feature side projection, vectorized CCD';results[key]=res
   dump('COLLISION_CONSTRAINED_SOLVE_AUDIT_R3.json',{'method':'Sequential constrained native-normal progression and dynamically refreshed closest-feature signed separation projection in inverse displacement/gradient/bending metric; whole-mesh exact point/segment/coplanar contact gating and swept-AABB cubic coplanarity-event continuous collision checks before each accepted iteration.','COMPUTATIONAL_GEOMETRY_TOLERANCE':{'proximity_activation_band_mm':.05,'signed_separation_gap_mm':1e-6,'exact_point_mm':1e-8,'exact_coplanar_area_mm2':1e-8,'minimum_native_face_area_mm2':1e-8,'CCD_shared_feature_exclusion_mm':1e-7,'anatomy_clearance':False},'native_cycles_immutable':True,'baseline_valid_outward_convention':'Initially outward faces retain outward chart and baseline normal hemisphere. Documented pre-existing inward folded faces may unfold with positive area and unchanged cycles.','baseline_to_final_path_starts_at_frozen_source':True,'solves':results})
   print('RESULT',key,res['failures'],'crease',res['structure']['edge6676_deg'],'depth',res['structure']['fixed_reference_core_depth_mm'],flush=True)
