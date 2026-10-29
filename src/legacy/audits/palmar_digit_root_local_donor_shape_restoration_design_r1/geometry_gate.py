import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np,math
from fractions import Fraction as Fr
from functools import lru_cache
C=read(OUT/'PALMAR_ROOT_FORMAL_TARGET_COORDINATES_R1.json');F=C['faces'];E=C['edges'];V=np.array(C['source_world_mm']);P=np.array(C['candidate_world_mm']);IDS=C['vertex_ids'];frame=read(PRIOR/'DIAGNOSTIC_RENDER_GEOMETRY_R1.json')['frame'];origin=np.array(frame['origin_world_mm']);n=np.array(frame['normal']);COMMON={}
emap={tuple(sorted(e)):i for i,e in enumerate(E)};FE=[];EF=[[] for _ in E]
for fi,p in enumerate(F):
 es=[emap[tuple(sorted((a,b)))] for a,b in zip(p,p[1:]+p[:1])];FE.append(es)
 for ei in es:EF[ei].append(fi)
tri=np.array([(p[0],p[k],p[k+1]) for p in F for k in range(1,len(p)-1)]);owners=np.array([fi for fi,p in enumerate(F) for k in range(1,len(p)-1)])
R4=ROOT/'audits/minimal_local_geometry_amendment_design_r4';sources=[]
for p,names in [(R4/'geometry.py',['normal','normals','areas','angles','face_domain','boundary_domain','boundary_audit']),(ROOT/'audits/minimal_local_geometry_amendment_design_r1/independent_contact_audit.py',['edge_tri']),(R4/'contact_geometry.py',['point_triangle','segment_segment','tri_pair_metrics']),(R4/'collision_engine.py',['common','broad']),(R4/'robust_geometry.py',['fq','sub','add','mul','dot','cross','segment_hit','on_seg','coplanar_polygon','intersection','legal_features','triangle_area_vectors','swept_min_area']),(R4/'contact_components.py',['feature','barycentric','registry','compare']),(ROOT/'audits/local_donor_shape_transfer_amendment_design_r1/geometric_gate.py',['assess'])]:sources.append(reuse(p,names,globals()))

baseN=normals(V);baseA=angles(V)
