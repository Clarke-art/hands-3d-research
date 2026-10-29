import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np, math
G=read(FRESH/'POSED_COORDINATES_R1.json');F=G['faces'];E=G['edges'];P={k:np.array(v)*1000 for k,v in G['positions_world_m'].items()}
RAW=np.array(G['bind_raw_world_m'])*1000;ZERO=P['BIND'];nat=read(NATIVE);mesh=nat['protected']['mesh']
old=read(HIST/'POSED_COORDINATES_R1.json');oldnat=read(S5/'static_skin_compatibility_revalidation_after_donor_transfer_r1/OLD_R2_CLEAN_REOPEN_NATIVE_PAYLOAD_R1.json')
S=read(SOURCE/'RAW_SOURCE_GEOMETRY.json')['stages'];A=read(ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_r1/APPLICATION_NATIVE_GEOMETRY_R1.json')
M=read(PREP/'RENDER_ONLY_VISUAL_MANIFEST_R1.json');pairs=read(PREP/'LOCKED_CURRENT9_ROWS_R1.json')['rows']
tri=np.array([(p[0],p[k],p[k+1]) for p in F for k in range(1,len(p)-1)]);tf=np.array([i for i,p in enumerate(F) for k in range(1,len(p)-1)])
adj=[set() for _ in RAW];ef={}
for ei,(a,b) in enumerate(E):adj[a].add(b);adj[b].add(a);ef[tuple(sorted((a,b)))]=[]
for fi,p in enumerate(F):
 for a,b in zip(p,p[1:]+p[:1]):ef[tuple(sorted((a,b)))].append(fi)
def ring(v):return set(v)|{j for i in v for j in adj[i]}
def normals(v,faces):
 n=[];area=[];cent=[]
 for p in faces:
  q=v[p];a=sum((np.cross(q[k]-q[0],q[k+1]-q[0]) for k in range(1,len(q)-1)),np.zeros(3))
  n.append(a/max(np.linalg.norm(a),1e-15));area.append(np.linalg.norm(a)/2);cent.append(q.mean(0))
 return np.array(n),np.array(area),np.array(cent)
def hit(cid,camera,x,y):
 v=P[cid];ma=np.array(camera['camera_world_matrix']);w=camera['orthographic_width_m']*1000;h=w*1100/1600
 o=ma[:3,3]*1000+ma[:3,0]*(x/1600-.5)*w+ma[:3,1]*(.5-y/1100)*h;d=-ma[:3,2]
 q=v[tri];e1=q[:,1]-q[:,0];e2=q[:,2]-q[:,0];a=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,a)
 inv=np.divide(1.,det,out=np.zeros_like(det),where=abs(det)>1e-10);s=o-q[:,0];u=np.einsum('ij,ij->i',s,a)*inv;tq=np.cross(s,e1);b=tq@d*inv;t=np.einsum('ij,ij->i',e2,tq)*inv
 ok=(abs(det)>1e-10)&(u>=-1e-7)&(b>=-1e-7)&(u+b<=1+1e-7)&(t>0)
 if not ok.any():return None
 ii=np.where(ok)[0];i=ii[np.argmin(t[ii])];return {'pixel':[x,y],'face_id':int(tf[i]),'triangle_vertex_ids':tri[i].tolist(),'world_mm':(o+d*t[i]).tolist(),'barycentric':[float(1-u[i]-b[i]),float(u[i]),float(b[i])]}
# Pixel-selected, visible faceted patch from an actually inspected current image.
# This is a provisional diagnostic candidate, never a claim that the absent Human screenshot matches it.
view=next(r for r in M['renders'] if r['name']=='IDX_MCP_30__LOCAL_ALTERNATE');cam=view['camera']
boxes=[[330,380,720,640],[520,260,720,350]]
hits=[h for x0,y0,x1,y1 in boxes for y in range(y0,y1+1,16) for x in range(x0,x1+1,16) if (h:=hit('IDX_MCP_30',cam,x,y))]
faces=sorted({h['face_id'] for h in hits});verts=sorted({v for f in faces for v in F[f]});vset=set(verts);r1=ring(vset);r2=ring(r1)
edges=[i for i,e in enumerate(E) if set(e)<=vset];fs1=[i for i,p in enumerate(F) if set(p)&r1];fs2=[i for i,p in enumerate(F) if set(p)&r2]
center=np.array(hit('IDX_MCP_30',cam,510,470)['world_mm']);seedface=hit('IDX_MCP_30',cam,510,470)['face_id'];seed=F[seedface];origin=RAW[seed].mean(0)
fn,ar,ct=normals(RAW,F);n=fn[seedface];axis=np.array([0.,0.,1.]);axis-=n*(axis@n);axis/=np.linalg.norm(axis);cross=np.cross(n,axis)
frame={'origin_world_mm':origin,'seed_face_id':seedface,'seed_pixel':[510,470],'normal':n,'finger_axis_tangent':axis,'cross_finger_tangent':cross,'basis_semantics':'local diagnostic tangent derived from world +Z projected onto visible seed face; no anatomical ownership authority'}
rig=nat['protected']['rigs']['RIGHT_HAND_PRODUCTION_RIG']['bones']
mcp=sorted([{'bone':k,'distance_mm':float(np.linalg.norm(np.array(b['head_world_m'])*1000-origin))} for k,b in rig.items() if 'MCP' in k],key=lambda z:z['distance_mm'])
roi={'status':'PROVISIONAL_VISUAL_CANDIDATE_NOT_HUMAN_CONFIRMED','name':'PALMAR_DIGIT_ROOT_IRREGULARITY_ROI_R1','source_image':ref(PREP/view['file']),'camera':cam,'case_id':'IDX_MCP_30','pixel_rectangles_xyxy':boxes,'raycast_method':'orthographic native-face triangle z-buffer equivalent; nearest positive ray hit; all faces present','visible_hit_faces':faces,'vertices':verts,'edges':edges,'1_ring_vertices':sorted(r1),'2_ring_vertices':sorted(r2),'1_ring_faces':fs1,'2_ring_faces':fs2,'pixel_hit_witnesses':hits,'nearest_MCP_context':mcp,'diagnostic_frame':frame,'anatomical_ownership_changed':False}
dump('PALMAR_DIGIT_ROOT_IRREGULARITY_ROI_R1.json',roi)
candidates=[{'case_id':cid,'pose_id':cid,'image':ref(PREP/rr['file']),'camera':rr['camera'],'resolution':rr['resolution'],'shading':'display clone all smooth, unlike SOURCE_NATIVE flags','match':'POSSIBLE_NOT_UNIQUE'} for cid in CASES for rr in M['renders'] if rr['source_case']==cid and rr['name'].endswith(('LOCAL_ALTERNATE','LOCAL_PRIMARY'))]
dump('HUMAN_PALMAR_IRREGULARITY_VISUAL_TARGET_R1.json',{'MATCHED_CASE':None,'MATCHED_POSE':None,'MATCHED_RENDER_SOURCE':None,'MATCH_CONFIDENCE':'UNRESOLVED_NO_HUMAN_SCREENSHOT','TOP_CANDIDATE_CASES':candidates,'candidate_used_for_detailed_measurement':'IDX_MCP_30__LOCAL_ALTERNATE','candidate_justification':'visible triangular facet band on palm/digit-root candidate patch, selected directly in inspected image pixel space','human_source_screenshot_present':False,'unique_match_claimed':False,'surface_target_requires_human_confirmation':True})
corr=read(SOURCE/'DONOR_TO_CURRENT_TOPOLOGY_CORRESPONDENCE_R1.json')['rigid_display_registration'];rot=np.array(corr['rotation_row']);trans=np.array(corr['translation_mm'])
states={'STAGE4A_R2':np.array(S['STAGE4A_R2']['canonical_world_m'])*1000@rot+trans,'STAGE4B_RSSF':np.array(S['STAGE4B_RSSF']['canonical_world_m'])*1000,'PRE_DONOR_STAGE4C_RAW':np.array(S['STAGE4C_R2']['canonical_world_m'])*1000,'NEW_STAGE4C_RAW':np.array(A['application_world_mm']),'CURRENT_R2_RAW':RAW,'CURRENT_R2_ZERO':ZERO,**{cid:P[cid] for cid in CASES},**{cid+'_PRE_DONOR':np.array(old['positions_world_m'][cid])*1000 for cid in CASES}}
assert np.max(abs(np.array(nat['coordinates_world_m'])*1000-RAW))<1e-8
allfn={};metrics={};baseedges=np.linalg.norm(RAW[np.array(E)[:,1]]-RAW[np.array(E)[:,0]],axis=1)
def stats(a):return {'min':float(np.min(a)),'max':float(np.max(a)),'mean':float(np.mean(a)),'median':float(np.median(a))}
def measure(v,ff,roi_faces,roi_vertices,edge_list,baseline=None):
 nn,aa,cc=normals(v,ff);di=[];fr=set(roi_faces)
 for i,(a,b) in enumerate(edge_list):
  fs=ef.get(tuple(sorted((a,b))),[]) if ff is F else []
  if len(fs)==2 and set(fs)<=fr:
   angle=math.degrees(math.acos(float(np.clip(nn[fs[0]]@nn[fs[1]],-1,1))))
   di.append({'edge_id':i,'vertex_ids':[a,b],'face_ids':fs,'dihedral_degrees':angle})
 di.sort(key=lambda z:z['dihedral_degrees'],reverse=True)
 return nn,aa,cc,di
for label,v in states.items():
 nn,aa,cc,di=measure(v,F,faces,verts,E);allfn[label]=nn
 displacement=v-RAW;elen=np.linalg.norm(v[np.array(E)[:,1]]-v[np.array(E)[:,0]],axis=1);rat=elen[edges]/baseedges[edges]
 dri=[]
 for ei in edges:
  a,b=E[ei];delta=displacement[b]-displacement[a];dri.append({'edge_id':ei,'neighbor_displacement_gradient':float(np.linalg.norm(delta)/baseedges[ei]),'relative_normal_displacement_mm':float(delta@n),'relative_tangent_displacement_mm':float(np.linalg.norm(delta-n*(delta@n))),'bind_direction_world':((RAW[b]-RAW[a])/baseedges[ei]).tolist(),'edge_ratio':float(elen[ei]/baseedges[ei])})
 metrics[label]={'face_area_mm2':{str(i):float(aa[i]) for i in faces},'edge_length_mm':{str(i):float(elen[i]) for i in edges},'posed_bind_edge_ratios':{str(i):float(elen[i]/baseedges[i]) for i in edges},'edge_ratio_summary':stats(rat),'surface_area_ratio':float(aa[faces].sum()/ar[faces].sum()),'adjacent_face_dihedral':di,'dihedral_summary_degrees':stats([x['dihedral_degrees'] for x in di]),'normal_angle_from_raw_degrees':{str(i):float(math.degrees(math.acos(float(np.clip(nn[i]@fn[i],-1,1))))) for i in faces},'vertex_displacement_mm':{str(i):displacement[i].tolist() for i in verts},'displacement_magnitude_mm':stats(np.linalg.norm(displacement[verts],axis=1)),'neighbor_gradients':dri,'curvature_proxy':'native adjacent-face dihedral / shared edge length; no human anatomical threshold','boundary_slope_edges':[x for x in di if any(j not in vset for a in x['vertex_ids'] for j in adj[a])],'silhouette':'projected diagnostic ROI boundary only, see silhouette overlays; whole hand silhouette not classified'}
dump('PALMAR_IRREGULARITY_GEOMETRY_METRICS_R1.json',{'scope':'provisional pixel-selected ROI only','units':'mm, mm2, dimensionless ratios, degrees','no_anatomical_thresholds':True,'states':metrics,'frame':frame})
# Recover only exact historical IDs / ancestry. Do not project current vertices onto donor geometry.
base=S['STAGE4A_R2_BASE'];a4=S['STAGE4A_R2'];lookup={tuple(v):i for i,v in enumerate(base['local_m'])};ancestry=read(SOURCE/'HISTORICAL_OPERATION_RAM_REPLAY.json')['final_ancestry'];mapping={};unresolved=[]
for i in sorted(r2):
 bi=lookup.get(tuple(a4['local_m'][i]))
 if bi is not None:mapping[str(i)]={'stage4a_base_vertex':bi,'L1_parent_weights':ancestry[bi]}
 else:unresolved.append(i)
donorids=sorted({int(j) for m in mapping.values() for j in m['L1_parent_weights']});donorfs=[i for i,p in enumerate(S['OFFICIAL_L1']['faces']) if set(p)&set(donorids)]
corr=read(SOURCE/'DONOR_TO_CURRENT_TOPOLOGY_CORRESPONDENCE_R1.json')['rigid_display_registration'];rot=np.array(corr['rotation_row']);trans=np.array(corr['translation_mm'])
source_states={}
for label in ['OFFICIAL_L1','STAGE2_L1','STAGE4A_R2_BASE']:
 s=S[label];v=np.array(s['canonical_world_m'])*1000@rot+trans
 ids=donorids if label!='STAGE4A_R2_BASE' else sorted({m['stage4a_base_vertex'] for m in mapping.values()});ff=s['faces'];fs=[i for i,p in enumerate(ff) if set(p)&set(ids)]
 source_states[label]={'positions_mm':v.tolist(),'faces':ff,'roi_faces':fs,'roi_vertices':ids,'smooth_flags':s['smooth'],'registration':'frozen rigid diagnostic registration from earlier exact ancestry audit; no scale, no nearest projection','source_input':s['input']}
dump('PALMAR_IRREGULARITY_SOURCE_DONOR_COMPARISON_R1.json',{'classification':'SOURCE_COMPARISON_UNRESOLVED_FOR_HUMAN_TARGET','candidate_correspondence_status':'EXACT_COORDINATE_ID_AND_SAVED_ANCESTRY' if not unresolved else 'PARTIAL_EXACT_CORRESPONDENCE','candidate_current_to_source':mapping,'unresolved_current_vertex_ids':unresolved,'donor_native_face_ids':donorfs,'projection_used':False,'registration':corr,'registration_RMS_mm':corr['outer_RMS_mm'],'caveat':'donor and engineered meshes differ in topology; compare native meshes, not interpolated donor as an official asset','source_same_faceting_visual_decision':'PENDING_VISUAL_QA'})
dump('PALMAR_IRREGULARITY_LINEAGE_COMPARISON_R1.json',{'human_target':'UNRESOLVED','states_compared':list(source_states)+list(states),'exact_current_ROI_vertices':verts,'RAW_ZERO_max_delta_mm':float(np.max(np.linalg.norm(ZERO[verts]-RAW[verts],axis=1))),'pre_new_stage4c_ROI_max_delta_mm':float(np.max(np.linalg.norm(states['NEW_STAGE4C_RAW'][verts]-states['PRE_DONOR_STAGE4C_RAW'][verts],axis=1))),'new_stage4c_current_RAW_max_delta_mm':float(np.max(np.linalg.norm(states['NEW_STAGE4C_RAW'][verts]-RAW[verts],axis=1))),'earliest_human_target':'UNRESOLVED','correspondence_method':'exact coordinate identity against Stage4A_R2 then saved Stage4A_R2_BASE ancestry; native oriented face correspondence checked below','required_missing':'Human screenshot/explicit candidate confirmation'})
weights=nat['positive_weight_vectors'];drivers=[]
for i in verts:
 w=weights[i];ordered=sorted(w.items(),key=lambda z:-z[1]);drivers.append({'vertex_id':i,'current_weight_vector':w,'dominant':ordered[0] if ordered else None,'secondary':ordered[1:]})
support={cid:('INDEX_MCP_R' if cid.startswith('IDX') else 'THUMB_IP_R') for cid in CASES}
dump('PALMAR_IRREGULARITY_SKIN_DRIVER_DIAGNOSTIC_R1.json',{'scope':'candidate ROI, not confirmed Human target','vertices':drivers,'driver_support':{cid:{'direct_driver':bn,'nonzero_vertices':[i for i in verts if weights[i].get(bn,0)>0]} for cid,bn in support.items()},'pose_displacement_and_neighbor_gradient_source':'PALMAR_IRREGULARITY_GEOMETRY_METRICS_R1.json','weight_or_rig_edits':0,'causal_identifiability':'saved coords show actual combined deformation; without counterfactual skin/kinematic edits, cannot apportion responsibility for acceptability','SKIN_CAUSAL':'UNRESOLVED_FOR_HUMAN_TARGET','POSE_KINEMATIC_CAUSAL':'UNRESOLVED_FOR_HUMAN_TARGET','BASE_GEOMETRY_CAUSAL':'UNRESOLVED_FOR_HUMAN_TARGET','no_MCP_proximity_inference':True})
over=[]
for p in pairs:
 pf=set(p['face_ids']);pv=set(p['vertex_ids']);cid=p['case_id'];bn=support[cid];vov=pv&vset;fov=pf&set(faces);near1=pv&r1;near2=pv&r2;driversame=bool(any(weights[i].get(bn,0)>0 for i in verts) and any(weights[i].get(bn,0)>0 for i in pv))
 cat='DIRECT_PAIR_OVERLAP' if fov or vov else 'NEIGHBORHOOD_OVERLAP' if near1 or near2 else 'SAME_DRIVER_ONLY' if driversame else 'NO_MEANINGFUL_OVERLAP'
 paircenter=P[cid][list(pv)].mean(0);distance=np.min(np.linalg.norm(P[cid][verts]-paircenter,axis=1))
 over.append({'pair_id':p['pair_id'],'case_id':cid,'face_ids':p['face_ids'],'classification_for_candidate':cat,'face_overlap':sorted(fov),'vertex_overlap':sorted(vov),'1_ring_overlap':sorted(near1),'2_ring_overlap':sorted(near2),'same_pose_overlap':cid=='IDX_MCP_30','same_driver_support_overlap':driversame,'pair_center_nearest_ROI_vertex_mm':float(distance),'crossing_causes_irregularity':'UNRESOLVED_NOT_ESTABLISHED_BY_OVERLAP'})
dump('PALMAR_IRREGULARITY_CURRENT9_OVERLAP_R1.json',{'human_target_classification':'UNRESOLVED','candidate_rows':over,'candidate_direct_pair_overlap_count':sum(x['classification_for_candidate']=='DIRECT_PAIR_OVERLAP' for x in over),'candidate_neighborhood_overlap_count':sum(x['classification_for_candidate']=='NEIGHBORHOOD_OVERLAP' for x in over),'same_pose_direct_pair_count':sum(x['same_pose_overlap'] and x['classification_for_candidate']=='DIRECT_PAIR_OVERLAP' for x in over),'pair_adjudication_changed':False,'causation_from_overlap_claimed':False})
shading={k:mesh[k] for k in ['smooth_flags','sharp_edges','custom_normal_state','explicit_custom_normals']};oldmesh=oldnat['protected']['mesh']
dump('PALMAR_IRREGULARITY_GEOMETRY_VS_SHADING_R1.json',{'human_target':'UNRESOLVED','SOURCE_NATIVE':{'smooth_face_count':sum(mesh['smooth_flags']),'flat_face_count':len(mesh['smooth_flags'])-sum(mesh['smooth_flags']),'sharp_edge_count':sum(mesh['sharp_edges']),'has_custom_split_normals':mesh['custom_normal_state'],'ROI_flags':[mesh['smooth_flags'][i] for i in faces],'ROI_sharp_edges':[i for i in edges if mesh['sharp_edges'][i]],'modifiers':nat['protected']['object']['modifiers'],'auto_smooth':'Blender 5.1 mesh.use_auto_smooth absent; no angle smooth modifier in stored stack; native face flags false; actual runtime readback separately recorded'},'pre_donor_current_shading_payload_equal':{k:mesh[k]==oldmesh[k] for k in shading},'HUMAN_REVIEW_DISPLAY_CLONE':'all faces use_smooth=True, calculated display normals; does not represent SOURCE_NATIVE flags','NORMAL_SHADING_CAUSAL':'UNRESOLVED_FOR_HUMAN_TARGET','production_normals_written':0,'display_only_variants':['SOURCE_NATIVE','FLAT','SMOOTH','WIRE','FACE_NORMALS','VERTEX_NORMALS','GRAZING','SILHOUETTE'],'FLAT_SHADING_SHOWS_DEFECT':'PENDING_CANDIDATE_VISUAL_QA','SMOOTH_SHADING_ONLY':'UNRESOLVED'})
dump('PALMAR_IRREGULARITY_RAW_ZERO_POSED_COMPARISON_R1.json',{'human_target':'UNRESOLVED','STATE_A':'saved raw world coords, armature not evaluated for rendering','STATE_B':'saved BIND evaluated coordinates, zero/RSSF','STATE_C':CASES,'STATE_D':'saved pre-donor same three poses','RAW_ZERO_exact_all_vertices':bool(np.array_equal(RAW,ZERO)),'RAW_ZERO_candidate_max_delta_mm':float(np.max(np.linalg.norm(RAW[verts]-ZERO[verts],axis=1))),'states_geometry_metric_source':'PALMAR_IRREGULARITY_GEOMETRY_METRICS_R1.json','pose_application_count':0,'micro_probe_count':0,'FULL42_RERUN':0})
dump('DIAGNOSTIC_RENDER_GEOMETRY_R1.json',{'faces':F,'edges':E,'roi':roi,'source_states':source_states,'states':{k:v.tolist() for k,v in states.items()},'source_native_smooth':mesh['smooth_flags'],'native_material_indices':mesh['face_material_indices'],'camera_source':view,'all_current9':pairs,'frame':frame})
print('Candidate ROI',len(verts),'vertices',len(faces),'faces; source unmapped',len(unresolved),flush=True)
print('Candidate dihedral summaries',{k:v['dihedral_summary_degrees'] for k,v in metrics.items()},flush=True)
