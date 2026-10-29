import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np, math
DIAG=ROOT/'audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1'
if not (OUT/'HISTORICAL_HASHES_BEFORE.json').exists():dump('HISTORICAL_HASHES_BEFORE.json',inventory())
R=read(DIAG/'DORSAL_MCP_DENT_ROI_R1.json');L=read(DIAG/'LINEAGE_RAW_READONLY_EXTRACTION.json');G=read(DIAG/'DENT_RENDER_GEOMETRY_R1.json')
F=L['topology']['faces'];E=L['topology']['edges'];V=np.array(L['stages']['STAGE4C_R2_RAW']['raw_world_m'])*1000
frame=G['frame'];origin=np.array(frame['origin_world_mm']);B=np.array([frame['x'],frame['y'],frame['outward']]).T
Q=(V-origin)@B
adj=[set() for _ in V]
for a,b in E:adj[a].add(b);adj[b].add(a)
EF=[[] for _ in E];emap={tuple(sorted(e)):j for j,e in enumerate(E)}
for fi,p in enumerate(F):
 for a,b in zip(p,p[1:]+p[:1]):EF[emap[tuple(sorted((a,b)))]].append(fi)
def normal(v,p):
 z=sum((np.cross(v[p[k]]-v[p[0]],v[p[(k+1)%len(p)]]-v[p[0]]) for k in range(len(p))),np.zeros(3));return z/max(np.linalg.norm(z),1e-15)
def analyze(v,write):
 fs=sorted(fi for fi,p in enumerate(F) if set(write).intersection(p));es=sorted({emap[tuple(sorted((a,b)))] for fi in fs for p in [F[fi]] for a,b in zip(p,p[1:]+p[:1])})
 ns=[normal(v,p) for p in F]; angles=[{'edge_id':ei,'angle_deg':math.degrees(math.acos(float(np.clip(ns[EF[ei][0]]@ns[EF[ei][1]],-1,1))))} for ei in es if len(EF[ei])==2]
 return {'affected_faces':fs,'affected_edges':es,'max_angle':max(a['angle_deg'] for a in angles),'edge6676_angle_deg':next(a['angle_deg'] for a in angles if a['edge_id']==6676),'largest_edges':sorted(angles,key=lambda d:-d['angle_deg'])[:10],'reference_normal_reversed_faces':[fi for fi in fs if ns[fi]@B[:,2]<0], 'normal_change_over90_faces':[fi for fi in fs if ns[fi]@normal(V,F[fi])<0]}
def fair(ids,method='harmonic'):
 ids=sorted(ids);k={i:j for j,i in enumerate(ids)}
 stencil=sorted(set(ids)|{a for i in ids for a in adj[i]})
 rows=[];rhs=[]
 for i in (ids if method=='harmonic' else stencil):
  row=np.zeros(len(ids));const=np.zeros(3)
  if i in k:row[k[i]]=1
  else:const+=Q[i]
  for j in adj[i]:
   if j in k:row[k[j]]-=1/len(adj[i])
   else:const-=Q[j]/len(adj[i])
  rows.append(row);rhs.append(-const)
 sol=np.linalg.lstsq(np.array(rows),np.array(rhs),rcond=None)[0]
 out=Q.copy();out[ids]=sol
 return out@B.T+origin
def feat(q):return np.column_stack([np.ones(len(q)),q[:,0],q[:,1],q[:,0]**2,q[:,0]*q[:,1],q[:,1]**2])
def candidate(ids,constrained=False):
 # Tangent coordinates: constrained biharmonic fairing. Fixed vertices are literal unchanged.
 ids=sorted(ids); v=fair(ids,'biharmonic'); q=(v-origin)@B
 outer=R['2_ring'];cf=np.linalg.lstsq(feat(Q[outer]),Q[outer,2],rcond=None)[0]
 # Normal coordinates: blend a curved ring-fit shallow-valley target into fairing.
 # Width and depth are explicit design parameters, not anatomy thresholds.
 center=Q[[3332,3340],:2].mean(0);width=6.0;depth=.65
 target=feat(q)@cf-depth*np.exp(-np.sum((q[:,:2]-center)**2,axis=1)/(2*width**2))
 q[ids,2]=.25*q[ids,2]+.75*target[ids]
 constraints=[];projection_info=None
 if constrained:
  # Prevent a correction from making native quads bow-tie or locally turn over.
  # Preserve each boundary face's original tangent orientation; intentionally
  # unfold the three documented inward faces in the central contour.
  fs=[fi for fi,p in enumerate(F) if set(ids).intersection(p)]
  for fi in fs:
   p=F[fi]
   if constrained=='C_boundary':sign=1
   else:sign=1 if constrained=='all_positive' or normal(V,p)@B[:,2]>=0 or fi in [3312,3330,3331] else -1
   for k in range(1,len(p)-1):
    tri=[p[0],p[k],p[k+1]];a,b,c=Q[tri,:2];u=b-a;w=c-a
    original_signed=u[0]*w[1]-u[1]*w[0]
    if constrained=='C_boundary' and fi==3316:sign=1 if original_signed>=0 else -1
    constraints.append((fi,tri,sign,max(.05,abs(original_signed)*.1)))
  free=set(ids);tol=1e-9
  for iteration in range(4000):
   worst=0.
   for fi,tri,sign,minimum in constraints:
    a,b,c=q[tri,:2];u=b-a;w=c-a;ar=sign*(u[0]*w[1]-u[1]*w[0]);deficit=minimum-ar
    worst=max(worst,deficit)
    if deficit<=tol:continue
    grads=sign*np.array([[b[1]-c[1],c[0]-b[0]],[c[1]-a[1],a[0]-c[0]],[a[1]-b[1],b[0]-a[0]]])
    denom=sum(g@g for i,g in zip(tri,grads) if i in free)
    if denom<1e-15:raise RuntimeError(('Infeasible fixed boundary',fi,tri))
    step=1.02*deficit/denom
    for i,g in zip(tri,grads):
     if i in free:q[i,:2]+=step*g
   if worst<=tol:break
  projection_info={'iterations':iteration+1,'max_signed_area_constraint_deficit_mm2':float(worst),'constraints':[{'face_id':fi,'triangle':tri,'sign':sign,'minimum_twice_projected_area_mm2':minimum} for fi,tri,sign,minimum in constraints],'constraint_is_anatomy_threshold':False,'purpose':'A deterministic feasibility projection to prevent NEW triangle reversals / quad bow-ties while unfolding only documented central folds. Baseline boundary folds are not relabeled as repaired.'}
  if worst>1e-7:raise RuntimeError(('Projection unresolved',worst))
 v[ids]=q[ids]@B.T+origin
 v[np.array(sorted(set(range(len(V)))-set(ids)))]=V[np.array(sorted(set(range(len(V)))-set(ids)))]
 return v,{'method':'Uniform-graph biharmonic tangent fairing plus75% curved ring2 quadratic shallow-valley target/25% biharmonic normal height; candidateB also applies deterministic signed-area feasibility projection. Fixed outside write set exactly.','normal_target_gaussian_width_mm':width,'normal_target_depth_mm':depth,'target_center_local_xy_mm':center.tolist(),'quadratic_fit_coefficients':cf.tolist(),'signed_area_constraint_projection':projection_info,'parameters_are_anatomy_thresholds':False}
def make_c():
 pool=sorted(R['core_vertices']+R['1_ring']+[3315,3306,3338]);ids=pool.copy()
 ns={'np':np,'F':F};reuse(OUT/'geometry_metrics.py',['quad_bowties'],ns)
 ns['FULLFS']=[fi for fi,p in enumerate(F) if set(pool).intersection(p)]
 basebow=set(ns['quad_bowties'](V));baseline=analyze(V,pool)
 def info(v):
  m=analyze(v,pool);q=(v-origin)@B;cf=np.linalg.lstsq(feat(Q[R['2_ring']]),Q[R['2_ring'],2],rcond=None)[0]
  return m,float(max(0,-min((q[:,2]-feat(q)@cf)[R['core_vertices']])))
 v,method=candidate(ids);ref,refdepth=info(v);pruning=[]
 order=sorted(pool,key=lambda i:(np.linalg.norm(v[i]-V[i]),i))
 for i in order:
  trial=sorted(set(ids)-{i});vv,_=candidate(trial);mm,depth=info(vv)
  reasons=[]
  if set(ns['quad_bowties'](vv))-basebow:reasons.append('new_quad_bowtie')
  if set(mm['reference_normal_reversed_faces'])-set(baseline['reference_normal_reversed_faces']):reasons.append('new_reference_reverse')
  if mm['max_angle']>ref['max_angle']+1e-6:reasons.append('worse_max_boundary_angle_than_unpruned_C')
  if mm['edge6676_angle_deg']>31.682011:reasons.append('central_crease_worse_than_B')
  if depth>refdepth+1e-6:reasons.append('worse_fixed_ring_reference_depth_than_unpruned_C')
  pruning.append({'trial_restore_vertex_id':i,'write_count':len(trial),'accepted':not reasons,'rejection_reasons':reasons,'max_angle_deg':mm['max_angle'],'edge6676_angle_deg':mm['edge6676_angle_deg'],'depth_proxy_fixed_baseline_ring_mm':depth})
  if not reasons:ids=trial;v=vv
 v,method=candidate(ids);method['support_pool']=pool;method['greedy_support_and_core_pruning']=pruning;method['minimality_limit']='Deterministic one-pass comparative pruning within a justified34-vertex pool, not a proof of globally minimal write cardinality. Human visual acceptability and exact crossing checks still required.'
 return ids,v,method
if __name__=='__main__':
 specs={'A':R['core_vertices'],'B':R['core_vertices']+[3300,3308,3347],'C':None}
 results={}
 for label,ids in specs.items():
  if label=='C':ids,v,method=make_c()
  else:v,method=candidate(ids,constrained=label=='B')
  m=analyze(v,ids);ds=np.linalg.norm(v-V,axis=1)
  results[label]={'DESIGN_ONLY_NOT_PRODUCTION':True,'write_vertices':sorted(ids),'world_mm':v.tolist(),'method':method,'preliminary_geometry':m,'displacements':{str(i):{'vector_world_mm':(v[i]-V[i]).tolist(),'magnitude_mm':float(ds[i])} for i in sorted(ids)},'max_displacement_mm':float(ds.max()),'mean_displacement_mm':float(ds[ids].mean()),'RMS_displacement_mm':float(np.sqrt(np.mean(ds[ids]**2))),'outside_write_displacement_mm':0.0}
  print(label,'maxmove',ds.max(),'mean',ds[ids].mean(),'maxangle',m['max_angle'],'crease',m['edge6676_angle_deg'],'reversed',m['reference_normal_reversed_faces'])
 dump('GEOMETRY_AMENDMENT_CANDIDATES_R1.json',{'status':'DESIGN_ONLY_NOT_PRODUCTION','source_layer':'FROZEN_STAGE4C_R2_RSSF_GEOMETRY_NEW_DERIVED_VERSION_NOT_IN_PLACE','source':L['stages']['STAGE4C_R2_RAW']['input'],'earliest_source_is_evidence_only':'STAGE4A_R2_BASE_PRE_CMC_RETOPO','candidate_count':len(results),'candidates':results,'approval':False,'C':'CREATED_ONLY_AFTER_A_B_STRUCTURAL_FAILURES'})
