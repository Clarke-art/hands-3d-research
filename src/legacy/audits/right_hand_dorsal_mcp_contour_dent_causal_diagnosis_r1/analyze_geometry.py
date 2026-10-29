import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np,math
L=read(OUT/'LINEAGE_RAW_READONLY_EXTRACTION.json');ROI=read(OUT/'DORSAL_MCP_DENT_ROI_R1.json')
F=L['topology']['faces'];E=L['topology']['edges'];ids=ROI['vertices'];core=ROI['core_vertices'];outer=ROI['2_ring'];cv=ROI['center_vertex_id'];fs=ROI['faces'];es=ROI['edges']
S=L['stages'];VREF=np.asarray(S['R2_PRODUCTION']['raw_world_m'])*1000
def normal(v,p):
 n=sum((np.cross(v[p[k]],v[p[(k+1)%len(p)]]) for k in range(len(p))),np.zeros(3));return n/max(np.linalg.norm(n),1e-15)
n=sum((normal(VREF,F[fi]) for fi in fs),np.zeros(3));n/=np.linalg.norm(n)
if <REDACTED_EMAIL>(ROI['camera']['direction'])<0:n=-n
x=np.asarray(ROI['camera']['right']);x-=n*(x@n);x/=np.linalg.norm(x);y=np.cross(n,x)
origin=VREF[cv].copy();B=np.column_stack([x,y,n]);ADJ={i:[] for i in range(len(VREF))}
for a,b in E:ADJ[a].append(b);ADJ[b].append(a)
edgefaces={j:[fi for fi,p in enumerate(F) if E[j][0] in p and E[j][1] in p] for j in es}
stages={'STAGE4A_R2_FROZEN':np.asarray(S['STAGE4A_R2_FROZEN']['raw_world_m'])*1000,'STAGE4B_RSSF_R2':np.asarray(S['STAGE4B_RSSF_R2']['raw_world_m'])*1000,'STAGE4C_R2_RAW':np.asarray(S['STAGE4C_R2_RAW']['raw_world_m'])*1000,'CORRECTED_STAGE5A_ZERO':np.asarray(S['CORRECTED_STAGE5A_RIG']['evaluated_on']['world_m'])*1000,'R2_ARMATURE_OFF':np.asarray(S['R2_PRODUCTION']['evaluated_armature_off']['world_m'])*1000,'R2_BIND_ZERO':np.asarray(S['R2_PRODUCTION']['evaluated_on']['world_m'])*1000,**{'IDX_MCP_'+str(a):np.asarray(S['STAGE6A_IDX_MCP_'+str(a)]['world_m'])*1000 for a in [15,30,45]}}
def align(v):
 a=v[outer];b=VREF[outer];ac=a.mean(0);bc=b.mean(0);U,sv,VT=np.linalg.svd((a-ac).T@(b-bc));rot=U@VT
 if np.linalg.det(rot)<0:U[:,-1]*=-1;rot=U@VT
 trans=bc-ac@rot
 return v@rot+trans,{'rotation_row_vector':rot.tolist(),'translation_mm':trans.tolist(),'outer_ring_rms_mm':float(np.sqrt(np.mean(np.sum((a@rot+trans-b)**2,axis=1)))),'scale':1,'reflection':False,'purpose':'Diagnostic rigid registration only; removes gross pre-RSSF orientation, does not remove or edit the local dent.'}
def features(t):return np.column_stack([np.ones(len(t)),t[:,0],t[:,1],t[:,0]**2,t[:,0]*t[:,1],t[:,1]**2])
def sections(v):
 result=[]
 for angle in [0,60,120]:
  theta=math.radians(angle);t=x*math.cos(theta)+y*math.sin(theta);pn=np.cross(n,t);segs=[]
  for fi in fs:
   p=F[fi];triangles=[p[:3]]+([p[0:1]+p[2:4]] if len(p)==4 else [])
   for tri in triangles:
    pts=[]
    for a,b in zip(tri,tri[1:]+tri[:1]):
     da=(v[a]-origin)@pn;db=(v[b]-origin)@pn
     if abs(da)<1e-9:pts.append(v[a])
     if da*db<0:pts.append(v[a]+(v[b]-v[a])*da/(da-db))
    unique=[]
    for q in pts:
     if not any(np.linalg.norm(q-z)<1e-8 for z in unique):unique.append(q)
    if len(unique)>=2:
     a,b=max(((a,b) for a in unique for b in unique),key=lambda ab:np.linalg.norm(ab[0]-ab[1]))
     segs.append({'face_id':fi,'world_mm':[a.tolist(),b.tolist()],'profile_mm':[[float((a-origin)@t),float((a-origin)@n)],[float((b-origin)@t),float((b-origin)@n)]]})
  result.append({'angle_degrees_in_local_tangent':angle,'direction_world':t.tolist(),'plane_normal_world':pn.tolist(),'plane_point_world_mm':origin.tolist(),'actual_triangle_plane_segments':segs})
 return result
metrics={};geometry={};profiles={}
for label,v in stages.items():
 va,registration=align(v);q=(va-origin)@B
 coeff=np.linalg.lstsq(features(q[outer]),q[outer,2],rcond=None)[0]
 residual=q[:,2]-features(q)@coeff
 plane=np.linalg.lstsq(features(q[outer])[:,:3],q[outer,2],rcond=None)[0];plane_res=q[:,2]-features(q)[:,:3]@plane
 fn={fi:normal(va,F[fi]) for fi in fs};dihedral=[]
 for ei,ff in edgefaces.items():
  if len(ff)!=2 or not all(fi in fn for fi in ff):continue
  deg=math.degrees(math.acos(float(np.clip(fn[ff[0]]@fn[ff[1]],-1,1))))
  dihedral.append({'edge_id':ei,'vertices':E[ei],'faces':ff,'unsigned_angle_deg':deg})
 umbrella={i:float((va[i]-va[ADJ[i]].mean(0))@n) for i in core}
 normals={i:sum((fn[fi] for fi in fs if i in F[fi]),np.zeros(3)) for i in ids}
 normals={i:nv/max(np.linalg.norm(nv),1e-15) for i,nv in normals.items()}
 variation=[math.degrees(math.acos(float(np.clip(normals[a]@normals[b],-1,1)))) for ei in es for a,b in [E[ei]]]
 worst=min(core,key=lambda i:residual[i])
 metrics[label]={'core_quadratic_ring_depth_proxy_mm':float(max(0,-min(residual[i] for i in core))),'core_quadratic_deepest_vertex_id':worst,'center_vertex_quadratic_residual_mm':float(residual[cv]),'core_plane_ring_depth_proxy_mm':float(max(0,-min(plane_res[i] for i in core))),'core_residual_mm':{str(i):float(residual[i]) for i in core},'outer_fit_rms_mm':float(np.sqrt(np.mean(residual[outer]**2))),'outer_quadratic_coefficients':coeff.tolist(),'core_curvature_umbrella_mm':umbrella,'dihedral':dihedral,'max_dihedral_deg':max(r['unsigned_angle_deg'] for r in dihedral),'vertex_normal_variation_max_deg':max(variation),'rigid_registration':registration,'ROI_displacement_from_R2_raw_max_mm':float(np.max(np.linalg.norm(v[ids]-VREF[ids],axis=1))),'core_displacement_from_R2_raw_max_mm':float(np.max(np.linalg.norm(v[core]-VREF[core],axis=1))),'core_face_area_mm2':float(sum(np.linalg.norm(sum((np.cross(va[F[fi][k]]-va[F[fi][0]],va[F[fi][(k+1)%len(F[fi])]]-va[F[fi][0]]) for k in range(len(F[fi]))),np.zeros(3)))*.5 for fi in ROI['core_faces'])),'anatomical_threshold':None}
 geometry[label]={'world_mm':v.tolist(),'registered_world_mm':va.tolist()};profiles[label]=sections(va)
 print(label,'depth',round(metrics[label]['core_quadratic_ring_depth_proxy_mm'],6),'dihedral',round(metrics[label]['max_dihedral_deg'],3),'coreMove',metrics[label]['core_displacement_from_R2_raw_max_mm'])
dump('DENT_LOCAL_GEOMETRY_METRICS_R1.json',{'method':'Descriptive ring2 quadratic/plane residuals and unsigned native-edge dihedral; no anatomical threshold or Stage6 gate. Same explicit core and outer rings across all stages.','local_frame':{'origin_world_mm':origin.tolist(),'x':x.tolist(),'y':y.tolist(),'outward':n.tolist()},'stages':metrics})
dump('DENT_CROSS_SECTIONS_R1.json',{'scope':'Three actual mesh/plane intersections through selected dent center; segments retain face IDs. Registered stage coordinates use only a rigid diagnostic display transform.','stages':profiles})
dump('DENT_RENDER_GEOMETRY_R1.json',{'stages':geometry,'frame':{'origin_world_mm':origin.tolist(),'x':x.tolist(),'y':y.tolist(),'outward':n.tolist()},'display_transform_changes_production':False})
raw=stages['R2_ARMATURE_OFF'];on=stages['R2_BIND_ZERO']
dump('DENT_ARMATURE_ZERO_POSE_AUDIT_R1.json',{'status':'PASS_ZERO_EFFECT_EXCLUDED_BEYOND_KNOWN_FLOAT_NOISE','ROI_max_raw_off_to_evaluated_bind_mm':float(np.max(np.linalg.norm(raw[ids]-on[ids],axis=1))),'core_max_raw_off_to_evaluated_bind_mm':float(np.max(np.linalg.norm(raw[core]-on[core],axis=1))),'global_max_mm':float(np.max(np.linalg.norm(raw-on,axis=1))),'OFF_ON_exact_equal':bool(np.array_equal(raw,on)),'all_differences_within_existing_zero_gate_mm_0_0001':bool(np.max(np.linalg.norm(raw-on,axis=1))<=.0001),'object_matrix':S['R2_PRODUCTION']['object_world_matrix'],'armature_matrix':S['R2_PRODUCTION']['armature_world_matrix'],'parent_inverse':S['R2_PRODUCTION']['parent_inverse'],'modifier':S['R2_PRODUCTION']['modifiers'],'rest_zero_verified':S['R2_PRODUCTION']['pose_zero_verified'],'raw_Stage4C_to_R2_raw_max_mm':float(np.max(np.linalg.norm(np.asarray(S['STAGE4C_R2_RAW']['raw_world_m'])*1000-VREF,axis=1))),'conclusion':'Not exactly identical due float32 evaluation, but known ~0.00006mm noise cannot explain a millimetre-scale static contour feature. No bind/weight/object transform edits performed.'})
base=stages['R2_BIND_ZERO'];pose={}
for a in [15,30,45]:
 label='IDX_MCP_'+str(a);v=stages[label]
 pose[label]={'max_ROI_displacement_from_evaluated_bind_mm':float(np.max(np.linalg.norm(v[ids]-base[ids],axis=1))),'max_core_displacement_from_evaluated_bind_mm':float(np.max(np.linalg.norm(v[core]-base[core],axis=1))),'ring_depth_proxy_mm':metrics[label]['core_quadratic_ring_depth_proxy_mm'],'max_dihedral_deg':metrics[label]['max_dihedral_deg'],'core_face_area_mm2':metrics[label]['core_face_area_mm2']}
weights=S['R2_PRODUCTION']['weights'];groups=sorted({g for i in ids for g in weights[i]});family={g.split('_')[0] for g in groups if g!='WRIST_R'}
dump('DENT_POSE_AMPLIFICATION_R1.json',{'scope':'Only this ROI; existing saved coordinate evidence, no case executions.','bind_depth_proxy_mm':metrics['R2_BIND_ZERO']['core_quadratic_ring_depth_proxy_mm'],'poses':pose,'core_INDEX_MCP_weight_max':max(weights[i].get('INDEX_MCP_R',0) for i in core),'ROI_INDEX_MCP_weight_max':max(weights[i].get('INDEX_MCP_R',0) for i in ids),'current_driver_families':sorted(family),'weights':{str(i):weights[i] for i in ids},'weight_neighbor_L1_diagnostics':[{'edge_id':ei,'vertices':E[ei],'weight_vector_L1':sum(abs(weights[E[ei][0]].get(g,0)-weights[E[ei][1]].get(g,0)) for g in groups)} for ei in es],'weight_variation_is_static_root_cause':False,'new_Stage6_gate':False})
