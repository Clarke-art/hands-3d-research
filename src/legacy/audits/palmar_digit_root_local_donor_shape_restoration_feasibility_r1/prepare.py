import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np
G=read(PRIOR/'DIAGNOSTIC_RENDER_GEOMETRY_R1.json');roi=G['roi'];F=G['faces'];E=G['edges'];hits=roi['pixel_hit_witnesses'];current=np.array(G['states']['CURRENT_R2_RAW'])/1000
small=[520,260,720,350];large=[330,380,720,640]
def in_box(p,b):return b[0]<=p[0]<=b[2] and b[1]<=p[1]<=b[3]
ch=[h for h in hits if in_box(h['pixel'],small)];xh=[h for h in hits if in_box(h['pixel'],large)];cf=set(h['face_id'] for h in ch);xf=set(h['face_id'] for h in xh);cv={i for fi in cf for i in F[fi]};xv={i for fi in xf for i in F[fi]};sharedf=cf&xf;sharedv=cv&xv
corefaces=sorted(cf-xf);coreverts=sorted(cv-xv)
lock={'HUMAN_TARGET_LOCKED':'YES','human_request':ref(REQUEST),'scope':'upper small orange box ONLY defect; lower large orange box normal reference','image_identity':ref(PRIOR/'renders/CANDIDATE_PIXEL_SELECTION.png'),'original_source_view':ref(ROOT/'production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/renders/IDX_MCP_30__LOCAL_ALTERNATE.png'),'case_id':'IDX_MCP_30','camera':G['camera_source']['camera'],'image_dimensions':[1600,1100],'PRIMARY_DEFECT_ROI_pixel_xyxy':small,'EXCLUDED_NORMAL_ROI_pixel_xyxy':large,'matching_basis':'Human explicit upper-small/lower-large confirmation resolves the two rectangles of the previously delivered candidate selection; ray hits reused exactly','new_screenshot_asset_supplied':False,'red_arrow_pixels_used':False,'shared_native_face_ids':sorted(sharedf),'shared_native_vertex_ids':sorted(sharedv),'shared_surface_policy':'native faces can straddle both image rectangles; mixed faces are boundary context, not full-face defect labels; shared vertices are NORMAL_POSITION_LOCKED, not defect write candidates','DEFECT_CORE_VERTEX_IDS':coreverts,'DEFECT_CORE_FACE_IDS':corefaces,'EXCLUDED_NORMAL_VERTEX_IDS':sorted(xv),'EXCLUDED_NORMAL_FACE_IDS':sorted(xf)}
dump('PALMAR_ROOT_HUMAN_TARGET_LOCK_R1.json',lock)
dump('PALMAR_ROOT_DEFECT_CORE_R1.json',{'name':'PALMAR_ROOT_PRIMARY_DEFECT_CORE_R1','vertex_ids':coreverts,'face_ids':corefaces,'visible_upper_box_hit_face_ids':sorted(cf),'visible_upper_box_hit_vertex_ids':sorted(cv),'visible_hit_witnesses':ch,'boundary_straddling_normal_faces_not_whole_face_defect':sorted(sharedf),'shared_vertices_removed_from_defect_membership':sorted(sharedv),'anatomy_authority_changed':False})
dump('PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json',{'name':'PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1','vertex_ids':sorted(xv),'face_ids':sorted(xf),'visible_hit_witnesses':xh,'POSITION_LOCKED_AS_NORMAL_REFERENCE':True,'defect':False,'shared_vertices_position_locked':sorted(sharedv),'whole_area_smoothing_forbidden':True})
S=read(SOURCE/'RAW_SOURCE_GEOMETRY.json')['stages'];A=read(SOURCE/'HISTORICAL_OPERATION_RAM_REPLAY.json')['final_ancestry'];J=np.array(read(SOURCE/'HISTORICAL_RSSF_COORDINATE_CORRESPONDENCE.json')['per_vertex_linear_part']);rest=np.array(S['STAGE4A_R2']['canonical_world_m']);old=np.array(S['STAGE4C_R2']['canonical_world_m']);donor=np.array(S['OFFICIAL_L1']['canonical_world_m']);base=S['STAGE4A_R2_BASE'];lookup={}
for i,v in enumerate(base['local_m']):lookup.setdefault(tuple(v),[]).append(i)
mapping={};target=current.copy();delta=np.zeros_like(current);rows={};unresolved=[]
for i,v in enumerate(S['STAGE4A_R2']['local_m']):
 matches=lookup.get(tuple(v),[])
 if len(matches)!=1:unresolved.append(i);continue
 bi=matches[0];a=A[bi];q=sum((donor[int(k)]*w for k,w in a.items()),np.zeros(3));desired=old[i]+J[i]@(q-rest[i]);target[i]=desired;delta[i]=desired-current[i]
 mapping[i]=a;rows[str(i)]={'current_vertex_id':i,'Stage4A_base_vertex_id':bi,'L1_parent_weights':a,'donor_derived_rest_world_m':q.tolist(),'frozen_RSSF_linear_part':J[i].tolist(),'target_current_frame_world_m':desired.tolist(),'current_world_m':current[i].tolist(),'candidate_delta_mm':(delta[i]*1000).tolist(),'already_applied_dorsal_transfer_delta_mm':((current[i]-old[i])*1000).tolist()}
assert all(i in mapping for i in cv|xv)
# Tolerance excludes only saved float32 roundtrip noise from already restored dorsal vertices.
# It is not a free optimizer or blend factor and does not exempt true3D structure checks.
eligible=set(np.where(np.linalg.norm(delta,axis=1)*1000>.0001)[0].tolist())&set(mapping)
adj=[set() for _ in current]
for a,b in E:adj[a].add(b);adj[b].add(a)
remain=set(eligible);comps=[]
while remain:
 todo=[remain.pop()];c=set(todo)
 while todo:
  i=todo.pop();new=remain&adj[i];remain-=new;c|=new;todo.extend(new)
 comps.append(c)
selected=set().union(*(c for c in comps if c&set(coreverts)))
seeded=selected.copy();closure_steps=[]
while selected:
 roots={int(k) for i in selected for k in mapping[i]};extra={i for i in eligible if set(map(int,mapping[i]))&roots}-selected
 if not extra:break
 closure_steps.append(sorted(extra));selected|=extra
normal_intersection=selected&xv
# Do not silently move excluded normal area. A required overlap is a feasibility blocker.
transfer=sorted(selected-xv);boundary=sorted({j for i in transfer for j in adj[i]}-set(transfer));corewrites=sorted(set(transfer)&set(coreverts));closurewrites=sorted(set(transfer)-set(coreverts));probe=current.copy()
for i in transfer:probe[i]=target[i]
core_parent={int(k) for i in coreverts for k in mapping[i]};relevant=sorted({i for i,a in mapping.items() if set(map(int,a))&core_parent}|cv|xv|set(boundary)|selected)
dump('PALMAR_ROOT_SOURCE_ANCESTRY_R1.json',{'confidence':'EXACT_SUBDIVISION_GRAPH_ANCESTRY_AND_HISTORICAL_SPLIT_PARENTAGE','canonical_donor':S['OFFICIAL_L1']['input'],'historical_replay_provenance':ref(SOURCE/'HISTORICAL_OPERATION_RAM_REPLAY.json'),'subdivision_graph_validation':read(SOURCE/'DONOR_TO_CURRENT_TOPOLOGY_CORRESPONDENCE_R1.json')['multires_graph_validation'],'RSSF_linear_transform_provenance':ref(SOURCE/'HISTORICAL_RSSF_COORDINATE_CORRESPONDENCE.json'),'existing_RSSF_solution_preserved':True,'nearest_projection':False,'current_to_donor':{str(i):rows[str(i)] for i in relevant if i in mapping},'unmapped_remote_current_vertex_ids':unresolved,'unresolved_in_defect_or_normal_area':[]})
dump('PALMAR_ROOT_DONOR_TARGET_COORDINATES_R1.json',{'method':'old Stage4C position + frozen RSSF J * (exact ancestry donor rest position - Stage4A engineered rest position); already applied dorsal transfer subtracted from new delta to avoid double restoration','canonical_donor':'OFFICIAL_L1','coarse_base_used_as_target':False,'all_relevant_targets':{str(i):rows[str(i)] for i in relevant if i in mapping},'optimizer':False,'generic_smoothing':False,'float_roundtrip_noise_cutoff_mm':.0001})
scope={'DEFECT_CORE_COUNT':len(corewrites),'DEFECT_CORE_MEMBERSHIP_VERTEX_COUNT':len(coreverts),'DEFECT_CORE_WRITE_COUNT':len(corewrites),'ANCESTRY_CLOSURE_COUNT':len(closurewrites),'TRANSITION_CONTEXT_COUNT':0,'TOTAL_TRANSFER_PROBE_WRITE_COUNT':len(transfer),'DEFECT_CORE_VERTEX_IDS':coreverts,'DEFECT_CORE_WRITE_VERTEX_IDS':corewrites,'ANCESTRY_CLOSURE_VERTEX_IDS':closurewrites,'TRANSITION_CONTEXT_VERTEX_IDS':[],'TOTAL_WRITE_VERTEX_IDS':transfer,'unchanged_boundary_vertex_ids':boundary,'excluded_normal_required_closure_overlap':sorted(normal_intersection),'scope_blocker':bool(normal_intersection),'initial_deviation_component_vertex_ids':sorted(seeded),'shared_ancestry_closure_steps':closure_steps,'normal_reference_vertex_ids_locked':sorted(xv),'components':[{'vertex_ids':sorted(c),'seeded_from_core':bool(c&set(coreverts))} for c in comps],'scope_is_not_fixed_ring_expansion':True,'full_eligible_vertex_count':len(eligible),'existing_dorsal_transfer_not_reapplied':True,'boundary_blending':'none; deterministic ancestry restoration only; boundary continuity assessed by exact structural gate and visuals','source_noise_excluded_core_vertex_ids':[i for i in coreverts if 0<np.linalg.norm(delta[i])*1000<=.0001]}
dump('PALMAR_ROOT_TRANSFER_SCOPE_R1.json',scope)
dump('TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.json',{'DESIGN_ONLY':True,'NOT_PRODUCTION':True,'NOT_APPROVED':True,'world_mm':(probe*1000).tolist(),'baseline_world_mm':(current*1000).tolist(),'faces':F,'edges':E,'moved_vertex_ids':transfer,'write_set':[rows[str(i)] for i in transfer],'normal_position_locked_vertex_ids':sorted(xv),'scope_blocker':bool(normal_intersection),'source':ref(CURRENT),'current_R2_raw_equal_current_Stage4C':np.array_equal(np.array(read(ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_r1/APPLICATION_NATIVE_GEOMETRY_R1.json')['application_world_mm']),current*1000),'source_native_flags':read(ROOT/'production_spec/stage5_production_rig/geometry_propagation_after_donor_transfer_r1/R2_REOPENED_NATIVE_PAYLOAD_R1.json')['protected']['mesh']['smooth_flags']})
parents=sorted({int(k) for i in relevant if i in mapping for k in mapping[i]});l1faces=[fi for fi,p in enumerate(S['OFFICIAL_L1']['faces']) if set(p)&set(parents)]
eq=S['OFFICIAL_L1']['local_m']==S['STAGE2_L1']['local_m'] and S['OFFICIAL_L1']['faces']==S['STAGE2_L1']['faces']
dump('PALMAR_ROOT_DONOR_SOURCE_COMPARISON_R1.json',{'DONOR_SOURCE':'OFFICIAL_HAND_REALISTIC_MULTIRES_L1','official_vs_Stage2_exact_geometry_and_topology_equal':eq,'official_input':S['OFFICIAL_L1']['input'],'Stage2_input':S['STAGE2_L1']['input'],'donor_relevant_face_ids':l1faces,'donor_relevant_vertex_ids':parents,'SOURCE_NATURAL_CREASE_PRESENT':'PENDING_TARGETED_VISUAL_REVIEW','CURRENT_HARD_FACETING_PRESENT':True,'SOURCE_TO_CURRENT_GEOMETRY_DEVIATION':{'per_vertex_target_delta_source':'PALMAR_ROOT_DONOR_TARGET_COORDINATES_R1.json','core_max_mm':float(np.linalg.norm(delta[coreverts],axis=1).max()*1000),'write_set_max_mm':float(np.linalg.norm(delta[transfer],axis=1).max()*1000) if transfer else 0},'ENGINEERING_AMPLIFICATION_CONFIRMED':'PENDING_TARGETED_COMPARISON','EARLIEST_CONFIRMED_HARD_FACETING_STAGE':'PENDING_TARGETED_COMPARISON'})
print('Core',len(coreverts),'vertices',len(corefaces),'faces; excluded',len(xv),'vertices',len(xf),'faces; write',transfer,'closure',closurewrites,'normal overlap',sorted(normal_intersection),flush=True)
