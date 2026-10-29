"""Read-only native reopen, two assets, ten distinct authorized endpoint probes.
Historical primitives/metrics/classifier are loaded as definitions only.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,math,numpy as np,os
from types import SimpleNamespace
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
MM=1000.;reused=[]
assert read(OUT/'PREREQUISITE_GATE_R1.json')['status']=='PASS'
def module(p,names):
 ns={'bpy':bpy,'math':math,'Vector':Vector,'Quaternion':Quaternion,'MM':MM,'np':np,'os':os}
 reused.append(reuse(p,names,ns));return SimpleNamespace(**{n:ns[n] for n in names})
C=module(S5/'stage5b_r1e/scripts/s5b_r1e_common.py',['reset_pose','set_joint_rotation','update','evaluate','read_weights'])
C.SEVERE_MIN_BIND_MM=3.;C.SEVERE_STRETCH_X=5.;C.TEAR_X=3.;C.TEAR_MIN_POSED_MM=5.;C.MM=MM
S=module(S6/'stage6a/scripts/s6a_common.py',['face_area','face_normal','pose_state'])
R=module(S6/'stage6b_r1c/scripts/r1c_pen_common.py',['ray_triangle','tri_tri_intersection','seg_len','closest_point_on_triangle','poke_depth','tris_of'])
extract=module(S5/'targeted_rig_and_skin_data_rebuild_after_approval_r1/blender_extract.py',['mesh_payload','rig_payload','weights'])
matrix=read(HIST/'TARGETED_FIXTURE_MATRIX.json');fixtures=matrix['fixtures']
cases=matrix['poses']+[{'case_id':f'RING_MCP_{a}','bone':'RING_MCP_R','angle_deg':a,'run_label':'DONOR_TRANSFER_LOCAL_REGRESSION'} for a in [15,30,45]]
CM6B={c['case_id']:c for c in read(S6/'stage6b/STAGE6B_CASE_MATRIX.json')['cases']}
reused.append(reuse(S5/'stage5b_r1e/scripts/s5b_r1e_prequal.py',['intersect_pairs','set_s6a','set_s6b'],globals()))
reused.append(reuse(S6/'stage6a_r1b/scripts/s6a_r1b_run_cases.py',['metrics'],globals()))
reused.append(reuse(S6/'stage6b_r1c/scripts/r1c_pen_v2.py',['tri_of','tri_mean_edge','pair_evidence','classify'],globals()))
reused.append(reuse(HIST/'run_targeted.py',['local_metrics'],globals()))
labels=read(R3_PATH)['membership']['vertex_labels']
debts=read(HIST/'INHERITED_DEBT_DEFORMATION_MAPPING.json')['rows']
oldnative=read(OLD_CAND.parent/'R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json')
POLY=[tuple(p) for p in oldnative['mesh']['faces']];EDGES=[tuple(e) for e in oldnative['mesh']['edges']];NV=3416
FD=[]
for p in POLY:
 labs={labels.get(str(v),'OUTSIDE_BOUNDED_DOMAIN') for v in p};FD.append(next(iter(labs)) if len(labs)==1 else 'MIXED_AUTHORITY_BAND')
core=set(APPROVED54);roi_fs=[i for i,p in enumerate(POLY) if core.intersection(p)];roi_es=[i for i,e in enumerate(EDGES) if core.intersection(e)]
ring=set(v for fi in roi_fs for v in POLY[fi])-core
support=core|ring;outer_fs=[i for i,p in enumerate(POLY) if support.intersection(p)];outer_es=[i for i,e in enumerate(EDGES) if support.intersection(e)]
assert (len(roi_fs),len(roi_es))==(95,148)
domain=read(S6/'full_stage6a_requalification_r1/LOCAL_PATCH_AND_MEASUREMENT_DOMAINS_R1.json')
sentinels={d:{'clean_shaft_support':domain['functional_clean'][d],'MCP_support':domain['patches'][d+'_MCP']} for d in ['MIDDLE','LITTLE']}
dump('MEASUREMENT_DOMAIN_MANIFEST_R1.json',{'fixtures':fixtures,'approved54':sorted(core),'incident_faces':roi_fs,'incident_edges':roi_es,'first_fixed_outer_ring':sorted(ring),'outer_support_face_ids':outer_fs,'outer_support_edge_ids':outer_es,'sentinels':sentinels,'sentinel_source':ref(S6/'full_stage6a_requalification_r1/LOCAL_PATCH_AND_MEASUREMENT_DOMAINS_R1.json'),'not_new_anatomical_labels':True})

coords=read(OUT/'POSED_COORDINATE_EVIDENCE_R1.json')['positions_world_m'];out={};binds={}
for asset,states in coords.items():
 V0=[Vector(p) for p in states['RAW_BIND']];TRIS=R.tris_of(POLY,V0);FACE_TRIS={}
 for fi,t in TRIS:FACE_TRIS.setdefault(fi,[]).append(t)
 CHARACTERISTIC_EDGE_MM=3.888205
 bindV=[Vector(p) for p in states['BIND']];binds[asset]={}
 for fa,fb in sorted(intersect_pairs(bindV,POLY)):
  e=pair_evidence(bindV,fa,fb)
  if e['intersect']:binds[asset][str((fa,fb))]={'face_ids':[fa,fb],'evidence':e,'V2_class':classify(e)}
 out[asset]={}
 for case in cases:
  cid=case['case_id'];V=[Vector(p) for p in states[cid]];rows=[]
  for fa,fb in sorted(intersect_pairs(V,POLY)):
   e=pair_evidence(V,fa,fb)
   if not e['intersect']:continue
   rows.append({'face_ids':[fa,fb],'evidence':e,'V2_class':classify(e),'domains':[FD[fa],FD[fb]],'fixture_membership':[n for n,f in fixtures.items() if fa in f['face_ids'] or fb in f['face_ids']],'affected_by_donor54':sorted(core.intersection(set(POLY[fa])|set(POLY[fb])))})
  out[asset][cid]=rows
 dump('EXACT_CROSSING_CENSUS_R1.json',{'results':out,'bind_exact_pairs':binds,'reused':reused,'new_pose_applications':0,'scope':'Fresh coordinate replay of ten authorized endpoints only; shared native vertices excluded by historical R1E BVH and V2 exact-ish triangle-crossing. ROI also receives stronger rational shared-feature gate separately.'})
print('COORDINATE EXACT CROSSING CENSUS DONE',flush=True)
