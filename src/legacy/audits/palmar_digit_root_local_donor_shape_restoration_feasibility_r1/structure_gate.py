import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np,math
from fractions import Fraction as Fr
from functools import lru_cache
C=read(OUT/'TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.json');F=C['faces'];E=C['edges'];V=np.array(C['baseline_world_mm']);P=np.array(C['world_mm']);IDS=C['moved_vertex_ids'];frame=read(PRIOR/'DIAGNOSTIC_RENDER_GEOMETRY_R1.json')['frame'];origin=np.array(frame['origin_world_mm']);n=np.array(frame['normal']);COMMON={}
emap={tuple(sorted(e)):i for i,e in enumerate(E)};FE=[];EF=[[] for _ in E]
for fi,p in enumerate(F):
 es=[emap[tuple(sorted((a,b)))] for a,b in zip(p,p[1:]+p[:1])];FE.append(es)
 for ei in es:EF[ei].append(fi)
tri=np.array([(p[0],p[k],p[k+1]) for p in F for k in range(1,len(p)-1)]);owners=np.array([fi for fi,p in enumerate(F) for k in range(1,len(p)-1)])
R4=ROOT/'audits/minimal_local_geometry_amendment_design_r4';sources=[]
for p,names in [(R4/'geometry.py',['normal','normals','areas','angles','face_domain','boundary_domain','boundary_audit']),(ROOT/'audits/minimal_local_geometry_amendment_design_r1/independent_contact_audit.py',['edge_tri']),(R4/'contact_geometry.py',['point_triangle','segment_segment','tri_pair_metrics']),(R4/'collision_engine.py',['common','broad']),(R4/'robust_geometry.py',['fq','sub','add','mul','dot','cross','segment_hit','on_seg','coplanar_polygon','intersection','legal_features','triangle_area_vectors','swept_min_area']),(R4/'contact_components.py',['feature','barycentric','registry','compare']),(ROOT/'audits/local_donor_shape_transfer_amendment_design_r1/geometric_gate.py',['assess'])]:sources.append(reuse(p,names,globals()))
baseN=normals(V);baseA=angles(V);result=assess(P,V,IDS);cmp=result['contact_no_regression'];result.update({'source_AST_provenance':sources,'native_V_E_F':[len(V),len(E),len(F)],'all_changed_fans_vs_whole_mesh':True,'new_contact_component_count':len(cmp['new_true_contact_components']),'existing_contact_worsening_count':len(cmp['worsening_components']),'feature_expansion_count':len(cmp['feature_expansions']),'manifold_unchanged':all(len(f)==2 for f in EF),'face_reversal_semantics':'native cycles unchanged; linear baseline-to-probe morph has no zero fan triangle event; projected signs not intrinsic reversal; endpoint exact contact registry separate','no_absolute_projected_bowtie_zero_gate':True,'continuous_collision_claimed':False,'payload_preservation':read(OUT/'TEMP_PROBE_PAYLOAD_PRESERVATION_R1.json'),'DESIGN_ONLY':True,'NOT_PRODUCTION':True,'NOT_APPROVED':True,'Full42_runs':0,'Stage6_runs':0,'deformation_qualification_runs':0})
counts=[result[k] for k in ['new_nonadjacent_exact_intersection','new_off_shared_crossing','new_illegal_coplanar_overlap','new_self_intersection_count','new_structural_bowtie','new_degenerate','new_contact_component_count','existing_contact_worsening_count','feature_expansion_count']]
result['NEW_TRUE3D_DEFECT_COUNT']=sum(counts);result['new_boundary_transition_fold_count']=len(result['boundary']['new_boundary_sharp_folds']);dump('PALMAR_ROOT_TRANSFER_STRUCTURE_AUDIT_R1.json',result)
normal=read(OUT/'PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json');xs=normal['vertex_ids'];xfaces=normal['face_ids'];delta=P-V
unchanged=bool(np.array_equal(P[xs],V[xs]));face_exact=all(np.array_equal(P[F[i]],V[F[i]]) for i in xfaces)
dump('PALMAR_ROOT_NORMAL_CONTEXT_PROTECTION_AUDIT_R1.json',{'status':'PASS_EXACT_NORMAL_CONTEXT_PROTECTION' if unchanged and face_exact else 'FAIL_CLOSED_NORMAL_CONTEXT_DAMAGE','POSITION_LOCKED_AS_NORMAL_REFERENCE':True,'excluded_vertex_count':len(xs),'excluded_face_count':len(xfaces),'positions_exact':unchanged,'entire_excluded_face_geometry_exact':face_exact,'max_displacement_mm':float(np.linalg.norm(delta[xs],axis=1).max()),'transition_context_write_count':0,'NORMAL_CONTEXT_VISIBLE_CHANGE':'NONE_GEOMETRY_EXACT_RENDER_PENDING','new_ridge_dent_bulge_hard_crease_flattening_from_geometry':0 if face_exact else 'UNRESOLVED','normal_area_visual_illumination_change_separately_measured':True})
adj=[set() for _ in V]
for a,b in E:adj[a].add(b);adj[b].add(a)
w=set(IDS);r1=w|{j for i in w for j in adj[i]};r2=r1|{j for i in r1 for j in adj[i]};wf=face_domain(IDS);pairs=read(ROOT/'production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/LOCKED_CURRENT9_ROWS_R1.json')['rows'];rows=[]
for p in pairs:
 pv=set(p['vertex_ids']);pf=set(p['face_ids']);rows.append({'pair_id':p['pair_id'],'case_id':p['case_id'],'face_ids':p['face_ids'],'write_vertex_intersection':sorted(w&pv),'changed_incident_face_intersection':sorted(wf&pf),'1_ring_vertex_intersection':sorted(r1&pv),'2_ring_vertex_intersection':sorted(r2&pv)})
direct=sum(bool(r['write_vertex_intersection'] or r['changed_incident_face_intersection']) for r in rows);near=sum(bool(r['1_ring_vertex_intersection'] or r['2_ring_vertex_intersection']) for r in rows)
dump('PALMAR_ROOT_CURRENT9_INDEPENDENCE_R1.json',{'rows':rows,'CURRENT9_WRITESET_DIRECT_OVERLAP_COUNT':direct,'CURRENT9_WRITESET_NEIGHBORHOOD_OVERLAP_COUNT':near,'CURRENT9_CAUSAL_INDEPENDENCE':'CONFIRMED_FOR_THIS_PROBE' if not direct and not near else 'NOT_CONFIRMED','CURRENT_9_CROSSING_HUMAN_RESPONSE':'HOLD_NOT_CLOSED','pair_answers_written':False,'pair_reclassification':False,'closure_created':False,'scope':'static write incidence and topology neighborhood independence only; no posed requalification'})
print('STATIC TRUE3D',result['status'],'new count',result['NEW_TRUE3D_DEFECT_COUNT'],'boundaryfold',result['new_boundary_transition_fold_count'],'normalexact',face_exact,'current9direct',direct,'near',near,flush=True)
