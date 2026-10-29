import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np,math
from fractions import Fraction as Fr
from functools import lru_cache
C=read(OUT/'APPLICATION_NATIVE_GEOMETRY_R1.json');F=C['faces'];E=C['edges'];V=np.array(C['source_world_mm']);P=np.array(C['application_world_mm']);frame=read(DIAG/'DENT_RENDER_GEOMETRY_R1.json')['frame'];origin=np.array(frame['origin_world_mm']);n=np.array(frame['outward']);COMMON={}
emap={tuple(sorted(e)):i for i,e in enumerate(E)};FE=[];EF=[[] for _ in E]
for fi,p in enumerate(F):
 ee=[emap[tuple(sorted((a,b)))] for a,b in zip(p,p[1:]+p[:1])];FE.append(ee)
 for ei in ee:EF[ei].append(fi)
tri=[];owners=[]
for fi,p in enumerate(F):
 for k in range(1,len(p)-1):tri.append([p[0],p[k],p[k+1]]);owners.append(fi)
tri=np.array(tri);owners=np.array(owners);R4=ROOT/'audits/minimal_local_geometry_amendment_design_r4';sources=[]
sources.append(reuse(R4/'geometry.py',['normal','normals','areas','angles','face_domain','boundary_domain','boundary_audit'],globals()))
sources.append(reuse(ROOT/'audits/minimal_local_geometry_amendment_design_r1/independent_contact_audit.py',['edge_tri'],globals()))
sources.append(reuse(R4/'contact_geometry.py',['point_triangle','segment_segment','tri_pair_metrics'],globals()))
sources.append(reuse(R4/'collision_engine.py',['common','broad'],globals()))
sources.append(reuse(R4/'robust_geometry.py',['fq','sub','add','mul','dot','cross','segment_hit','on_seg','coplanar_polygon','intersection','legal_features','triangle_area_vectors','swept_min_area'],globals()))
sources.append(reuse(R4/'contact_components.py',['feature','barycentric','registry','compare'],globals()))
baseN=normals(V);baseA=angles(V)
sources.append(reuse(DESIGN/'geometric_gate.py',['assess'],globals()))
result=assess(P,V,IDS);assert result['status']=='PASS','FAIL_CLOSED_DONOR_TRANSFER_APPLICATION: static structure'
contact={k:result[k] for k in ['baseline_counts','candidate_counts','baseline_components','candidate_components','contact_no_regression','new_nonadjacent_exact_intersection','new_off_shared_crossing','new_illegal_coplanar_overlap']};contact.update({'status':'PASS','coverage':'All54 application write-incident native fans vs whole mesh; all other pairs exactly unchanged. Actual legal shared simplex subtracted, baseline contact components/features/extent retained; no projected bowtie absolute-zero gate.','actual_reopened_geometry':ref(OUT/'APPLICATION_NATIVE_GEOMETRY_R1.json'),'source_AST_provenance':sources});dump('APPLICATION_CONTACT_AUDIT_R1.json',contact)
boundary=result.pop('boundary');a=angles(V);b=angles(P);expected=read(DESIGN/'FORMAL_DONOR_TRANSFER_BOUNDARY_AUDIT_R1.json')['named_edges']
named={str(i):{'edge_id':i,'vertex_ids':E[i],'face_ids':EF[i],'source_dihedral_deg':float(a[i]),'application_dihedral_deg':float(b[i]),'approved_candidate_dihedral_deg':expected[str(i)]['candidate_dihedral_deg'],'application_vs_approved_candidate_delta_deg':float(b[i])-expected[str(i)]['candidate_dihedral_deg']} for i in [6675,6602,6676]}
assert all(r['application_vs_approved_candidate_delta_deg']==0 for r in named.values()),'FAIL_CLOSED contour diagnostic mismatch'
boundary.update({'status':'PASS','named_edges':named,'high_delta_boundary_edges':[r for r in boundary['all_edges'] if abs(r['delta_deg'])>10],'new_obtuse_sharp_transition_migration_count':len(boundary['new_boundary_sharp_folds']),'angles_are_diagnostics_not_anatomy_thresholds':True,'approved_candidate_contour_geometry_exact':True,'visual_evidence':'PENDING_APPLICATION_MATCHED_RENDER_REVIEW'});dump('APPLICATION_BOUNDARY_CONTOUR_AUDIT_R1.json',boundary)
result.update({'source_AST_provenance':sources,'native_V_E_F':[3416,6828,3414],'TOPOLOGY_PRESERVED':'PASS','UV_MATERIAL_PRESERVED':'PASS','STRUCTURAL_GATE':'PASS','CONTACT_NO_REGRESSION':'PASS','new_obtuse_sharp_transition_migration_count':len(boundary['new_boundary_sharp_folds']),'actual_reopened_application':ref(ASSET),'qualification_scope':'Stage4 local static application validation only. Endpoint exact contacts + continuous fan-area evidence, not full continuous collision or Stage6 qualification.','face_reversal_semantics':'Native oriented cycles unchanged; linear source-to-application morph no zero fan-area event. Fixed-chart normal sign changes diagnostic, not intrinsic reversal.','production_promoted':False,'Stage5_propagated':False,'Stage6A_rerun':False});dump('APPLICATION_STRUCTURE_AUDIT_R1.json',result)
print('APPLICATION STATIC TRUE3D PASS; new contact0 / worsening0 / feature expansion0 / new transition0; native named-edge diagnostics exact',flush=True)
