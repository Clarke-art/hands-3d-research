"""Existing reconciled finite-feature gate applied to fresh endpoint coordinates.
No pose evaluation, fitting, solvers, topology writes, or new anatomical thresholds.
"""
from common import *
import numpy as np,math
from fractions import Fraction as Fr
from functools import lru_cache
from itertools import combinations
D=read(OUT/'POSED_COORDINATE_EVIDENCE_R1.json');F=D['faces'];E=D['edges'];states=D['positions_world_m']
M=read(OUT/'MEASUREMENT_DOMAIN_MANIFEST_R1.json')
IDS=M['approved54'];OUTER=sorted(set(IDS)|set(M['first_fixed_outer_ring']))
frame=read(ROOT/'audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/DENT_RENDER_GEOMETRY_R1.json')['frame']
origin=np.array(frame['origin_world_mm']);n=np.array(frame['outward']);COMMON={}
emap={tuple(sorted(e)):i for i,e in enumerate(E)};FE=[];EF=[[] for _ in E]
for fi,p in enumerate(F):
 ee=[emap[tuple(sorted((a,b)))] for a,b in zip(p,p[1:]+p[:1])];FE.append(ee)
 for ei in ee:EF[ei].append(fi)
tri=[];owners=[]
for fi,p in enumerate(F):
 for k in range(1,len(p)-1):tri.append([p[0],p[k],p[k+1]]);owners.append(fi)
tri=np.array(tri);owners=np.array(owners);R4=ROOT/'audits/minimal_local_geometry_amendment_design_r4';sources=[]
for p,names in [(R4/'geometry.py',['normal','normals','areas','angles','face_domain','boundary_domain','boundary_audit']),(ROOT/'audits/minimal_local_geometry_amendment_design_r1/independent_contact_audit.py',['edge_tri']),(R4/'contact_geometry.py',['point_triangle','segment_segment','tri_pair_metrics']),(R4/'collision_engine.py',['common','broad']),(R4/'robust_geometry.py',['fq','sub','add','mul','dot','cross','segment_hit','on_seg','coplanar_polygon','intersection','legal_features','triangle_area_vectors','swept_min_area']),(R4/'contact_components.py',['feature','barycentric','registry','compare']),(ROOT/'audits/local_donor_shape_transfer_amendment_design_r1/geometric_gate.py',['assess'])]:sources.append(reuse(p,names,globals()))
V=np.array(states['CURRENT_DONOR_R2']['BIND'])*1000;baseN=normals(V);baseA=angles(V)
results={};failed=False
for cid in ['RING_MCP_15','RING_MCP_30','RING_MCP_45']:
 current=np.array(states['CURRENT_DONOR_R2'][cid])*1000;old=np.array(states['PRE_DONOR_R2'][cid])*1000
 # The first fixed outer ring participates in the same existing exact contact gate.
 change=assess(current,old,OUTER)
 bindcmp=assess(current,V,OUTER)
 endpoint_area=areas(current);aa=angles(current);bindangles=angles(V)
 # Named repaired dent edges are retained diagnostics, with no new anatomy gate.
 named={str(i):{'edge_id':i,'bind_deg':float(bindangles[i]),'current_posed_deg':float(aa[i]),'pre_donor_posed_deg':float(angles(old)[i])} for i in [6675,6602,6676]}
 z={'pose':cid,'post_donor_vs_pre_donor_same_pose':change,'post_donor_bind_vs_posed':bindcmp,'named_repaired_dent_edges':named,'minimum_endpoint_native_face_area_mm2':float(min(endpoint_area[M['outer_support_face_ids']])),'maximum_ROI_dihedral_deg':float(max(aa[M['incident_edges']])),'source_existing_contact_semantics':'Baseline components retained individually; no blanket face-pair exemption. New components/features/worsening fail.','linear_area_probe_semantics':'Existing swept_min_area on a declared linear chord is supplementary nonzero fan-area evidence, not continuous kinematic collision qualification.'}
 hard=change['new_self_intersection_count']+change['new_degenerate']+change['new_structural_bowtie']+len(change['boundary']['new_boundary_sharp_folds'])+len(change['contact_no_regression']['worsening_components'])+len(change['contact_no_regression']['feature_expansions'])
 hard+=bindcmp['new_self_intersection_count']+bindcmp['new_degenerate']+bindcmp['new_structural_bowtie']
 z['new_structural_evidence_count']=hard;z['status']='PASS_LOCAL_REGRESSION' if hard==0 else 'FAIL_CLOSED_DONOR_TRANSFER_LOCAL_DEFORMATION_REGRESSION'
 results[cid]=z;failed|=hard>0
 dump('DORSAL_MCP_RING_FLEX_STRUCTURE_AUDIT_R1.json',{'status':'FAIL_CLOSED' if failed else 'PASS','results':results,'sources':sources,'coverage':'54 changed vertices, 95 incident faces, 148 incident edges and complete first fixed outer ring; incident native fans versus whole mesh, legitimate shared simplex subtracted.','continuous_actual_pose_sweep_claimed':False})
 print(cid,z['status'],'new exact contact',change['new_self_intersection_count'],bindcmp['new_self_intersection_count'],'new boundary',len(change['boundary']['new_boundary_sharp_folds']),'minimum fan',bindcmp['continuous_fan_area']['minimum_fan_triangle_area_mm2'],flush=True)
 if failed:
  print('FAIL CLOSED: no further dependent regression poses will be assessed',flush=True);break
