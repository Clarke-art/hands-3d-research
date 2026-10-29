"""Reconciled exact gate functions only; no optimizer/fitting module execution."""
import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np,math
from fractions import Fraction as Fr
from functools import lru_cache
C=read(OUT/'FORMAL_DONOR_TRANSFER_COORDINATES_R1.json');W=read(OUT/'FORMAL_DONOR_TRANSFER_WRITE_SET_R1.json');R=read(DIAG/'DORSAL_MCP_DENT_ROI_R1.json');frame=read(DIAG/'DENT_RENDER_GEOMETRY_R1.json')['frame']
F=C['faces'];E=C['edges'];V=np.array(C['source_world_mm']);P=np.array(C['candidate_world_mm']);IDS=W['vertex_ids'];origin=np.array(frame['origin_world_mm']);n=np.array(frame['outward']);COMMON={}
emap={tuple(sorted(e)):i for i,e in enumerate(E)};FE=[];EF=[[] for _ in E]
for fi,p in enumerate(F):
 ee=[emap[tuple(sorted((a,b)))] for a,b in zip(p,p[1:]+p[:1])];FE.append(ee)
 for ei in ee:EF[ei].append(fi)
tri=[];owners=[]
for fi,p in enumerate(F):
 for k in range(1,len(p)-1):tri.append([p[0],p[k],p[k+1]]);owners.append(fi)
tri=np.array(tri);owners=np.array(owners)
R4=ROOT/'audits/minimal_local_geometry_amendment_design_r4';sources=[]
sources.append(reuse(R4/'geometry.py',['normal','normals','areas','angles','face_domain','boundary_domain','boundary_audit'],globals()))
sources.append(reuse(ROOT/'audits/minimal_local_geometry_amendment_design_r1/independent_contact_audit.py',['edge_tri'],globals()))
sources.append(reuse(R4/'contact_geometry.py',['point_triangle','segment_segment','tri_pair_metrics'],globals()))
sources.append(reuse(R4/'collision_engine.py',['common','broad'],globals()))
sources.append(reuse(R4/'robust_geometry.py',['fq','sub','add','mul','dot','cross','segment_hit','on_seg','coplanar_polygon','intersection','legal_features','triangle_area_vectors','swept_min_area'],globals()))
sources.append(reuse(R4/'contact_components.py',['feature','barycentric','registry','compare'],globals()))
baseN=normals(V);baseA=angles(V)
def assess(v,baseline,ids):
 global baseN,baseA,V
 old=V.copy();V=baseline;baseN=normals(baseline);baseA=angles(baseline);COMMON.clear()
 b,_,bc=registry(baseline,ids);p,_,pc=registry(v,ids);cmp=compare(b,p);fs=face_domain(ids);intrinsic=[]
 for fi in sorted(fs):
  tt=np.where(owners==fi)[0]
  for k,a in enumerate(tt):
   for z in tt[k+1:]:
    vv=sorted(set(tri[a])&set(tri[z]));r=intersection(v,tri[a],tri[z],vv,[vv] if len(vv)==2 else [])
    if r['illegal']:intrinsic.append({'face_id':fi,**r})
 area=swept_min_area(baseline,v-baseline,np.where(np.isin(owners,list(fs)))[0]);deg=area['minimum_fan_triangle_area_mm2']<=1e-10;boundary=boundary_audit(v,ids)
 result={'status':'PASS' if cmp['PASS'] and not intrinsic and not deg and not boundary['new_boundary_sharp_folds'] else 'FAIL_CLOSED','baseline_counts':bc,'candidate_counts':pc,'baseline_components':{str(k):z for k,z in b.items()},'candidate_components':{str(k):z for k,z in p.items()},'contact_no_regression':cmp,'intrinsic_native_fan_intersections':intrinsic,'continuous_fan_area':area,'new_degenerate':int(deg),'new_structural_bowtie':len(intrinsic),'face_reversal_count':0 if not deg else 'UNRESOLVED','new_self_intersection_count':len(cmp['new_true_contact_components'])+len(intrinsic),'new_nonadjacent_exact_intersection':sum(1 for z in cmp['new_true_contact_components'] if not z['fan_contact_records'][0]['shared_vertex_ids']),'new_off_shared_crossing':sum(1 for z in cmp['new_true_contact_components'] if z['fan_contact_records'][0]['shared_vertex_ids']),'new_illegal_coplanar_overlap':sum(1 for z in cmp['new_true_contact_components'] if z['coplanar_overlap_area_mm2']>0),'boundary':boundary,'absolute_projected_bowtie_zero_required':False}
 V=old;baseN=normals(old);baseA=angles(old)
 return result
if __name__=='__main__':
 result=assess(P,V,IDS);preserved=read(OUT/'FORMAL_PAYLOAD_PRESERVATION_R1.json');assert preserved['all_protected_fields_exact']
 contact={k:result[k] for k in ['baseline_counts','candidate_counts','baseline_components','candidate_components','contact_no_regression','new_nonadjacent_exact_intersection','new_off_shared_crossing','new_illegal_coplanar_overlap']}
 contact.update({'status':'PASS' if result['contact_no_regression']['PASS'] else 'FAIL_CLOSED','coverage':'All54 write-incident fans vs whole mesh; all other pairs identical. Exact rational finite features minus actual legal shared simplex. Baseline component membership/features/extent no-regression.','source_AST_provenance':sources})
 dump('FORMAL_DONOR_TRANSFER_CONTACT_AUDIT_R1.json',contact)
 boundary=result.pop('boundary');angles0=angles(V);angles1=angles(P)
 boundary.update({'status':'PASS' if not boundary['new_boundary_sharp_folds'] else 'FAIL_CLOSED','named_edges':{str(ei):{'edge_id':ei,'vertices':E[ei],'faces':EF[ei],'source_dihedral_deg':float(angles0[ei]),'candidate_dihedral_deg':float(angles1[ei]),'delta_deg':float(angles1[ei]-angles0[ei])} for ei in [6675,6602,6676]},'high_delta_boundary_edges':[r for r in boundary['all_edges'] if abs(r['delta_deg'])>10],'new_obtuse_sharp_transition_migration_count':len(boundary['new_boundary_sharp_folds']),'angles_are_diagnostics_not_anatomy_thresholds':True,'new_ridge_notch_silhouette_kink':'PENDING_RENDER_REVIEW; numerical transition screen reports0 if PASS'})
 dump('FORMAL_DONOR_TRANSFER_BOUNDARY_AUDIT_R1.json',boundary)
 result.update({'source_AST_provenance':sources,'TOPOLOGY_PRESERVED':'PASS','UV_MATERIAL_PRESERVED':'PASS','WEIGHT_RIG_PAYLOAD_PRESERVED':'PASS','native_V_E_F':[len(V),len(E),len(F)],'face_reversal_semantics':'Native oriented cycles unchanged and declared linear morph has no zero fan-area event; fixed-chart normal sign changes are diagnostic, not intrinsic reversal. Endpoint contacts separate; no full continuous collision qualification claim.','new_obtuse_sharp_transition_migration_count':len(boundary['new_boundary_sharp_folds']),'DESIGN_ONLY':True,'NOT_PRODUCTION':True,'NOT_HUMAN_APPROVED':True,'DO_NOT_PROMOTE':True,'old_Stage6A_status_not_requalified':True})
 dump('FORMAL_DONOR_TRANSFER_STRUCTURE_AUDIT_R1.json',result)
 print('FORMAL STATIC GATE',result['status'],'contacts',result['candidate_counts'],'boundary new sharp',len(boundary['new_boundary_sharp_folds']),flush=True)
