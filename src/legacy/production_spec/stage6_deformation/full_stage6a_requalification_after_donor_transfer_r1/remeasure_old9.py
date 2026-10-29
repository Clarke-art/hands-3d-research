"""Forced measurement of each old pair on freshly evaluated current coordinates.
No additional poses, legacy selectors, Blender input asset writes or decisions.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import math
from types import SimpleNamespace
from mathutils import Vector
MM=1000.;G=read(OUT/'POSED_COORDINATES_R1.json');POLY=G['faces'];EDGES=G['edges'];V0=[Vector(p) for p in G['bind_raw_world_m']];reused=[]
rn={'Vector':Vector,'MM':MM,'math':math};names=['ray_triangle','tri_tri_intersection','seg_len','closest_point_on_triangle','poke_depth','tris_of']
reused.append(reuse(S6/'stage6b_r1c/scripts/r1c_pen_common.py',names,rn));R=SimpleNamespace(**{n:rn[n] for n in names})
FACE_TRIS={}
for fi,t in R.tris_of(POLY,V0):FACE_TRIS.setdefault(fi,[]).append(t)
CHARACTERISTIC_EDGE_MM=sorted((V0[a]-V0[b]).length*MM for a,b in EDGES)[len(EDGES)//2]
reused.append(reuse(S6/'stage6b_r1c/scripts/r1c_pen_v2.py',['tri_of','tri_mean_edge','pair_evidence','classify'],globals()))
H=read(HIST/'FULL_STAGE6A_MACHINE_EVIDENCE_R1.json');HC=read(HIST/'POSED_COORDINATES_R1.json')['positions_world_m'];rows=[]
for b in H['blockers']:
 assert 'face_ids' in b
 cid=b['case_id'];pair=b['face_ids'];old=next(z for z in H['cases'][cid]['crossings'] if z['face_ids']==pair);V=[Vector(p) for p in G['positions_world_m'][cid]]
 e=pair_evidence(V,*pair);cls=classify(e);ids=sorted({v for fi in pair for v in POLY[fi]});posed_exact=all(G['positions_world_m'][cid][v]==HC[cid][v] for v in ids)
 ds={k:e[k]-old[k] for k in ['depth_mm','local_edge_mm','seg_mm']};ds['poke_over_bind_facet_ratio']=e['depth_mm']/e['local_edge_mm']-old['depth_mm']/old['local_edge_mm']
 still=e['intersect'] and cls=='CASE_A_VISIBLE_GEOMETRIC_INTERPENETRATION'
 trend='UNCHANGED_EXACT' if all(v==0 for v in ds.values()) else 'SEVERITY_INCREASED' if ds['poke_over_bind_facet_ratio']>0 or ds['seg_mm']>0 else 'SEVERITY_REDUCED'
 state='STILL_PRESENT' if still else 'SEVERITY_REDUCED' if e['intersect'] else 'DISAPPEARED'
 rows.append({'case_id':cid,'face_ids':pair,'classification':'HISTORICAL_PRE_DONOR_BLOCKER_REMEASURED','current_identity_status':state,'severity_trend':trend,'current_severe_blocker':still,'current_V2_class':cls,'current_fresh_evidence':e,'old_evidence':{k:old[k] for k in ['intersect','depth_mm','local_edge_mm','seg_mm','pts','class']},'old_to_new_severity_delta':ds,'vertex_ids':ids,'donor54_vertex_overlap':sorted(set(ids)&set(APPROVED54)),'current_face_coordinates_world_m':{str(fi):[G['positions_world_m'][cid][v] for v in POLY[fi]] for fi in pair},'old_face_coordinates_world_m':{str(fi):[HC[cid][v] for v in POLY[fi]] for fi in pair},'posed_pair_coordinates_exact_unchanged':posed_exact,'same_pose_approval':False,'cross_pose_approval_not_applied':True,'visible_evidence_paths':{'current_solid_context':f'renders/{cid}__PAIR_{pair[0]}_{pair[1]}_CONTEXT__CURRENT_FRESH.png','current_isolated_exact_segment':f'renders/{cid}__PAIR_{pair[0]}_{pair[1]}_ISOLATED__CURRENT_FRESH.png','pre_donor_context':f'renders/{cid}__PAIR_{pair[0]}_{pair[1]}_CONTEXT__PRE_DONOR_HISTORICAL.png'},'remeasured_even_if_current_classifier_would_disappear':True})
dump('OLD_9_BLOCKER_FRESH_REMEASUREMENT_R1.json',{'count':9,'rows':rows,'current_asset':ref(CAND),'historical_comparator':ref(HIST/'FULL_STAGE6A_MACHINE_EVIDENCE_R1.json'),'method':reused,'fresh_pose_source':ref(OUT/'POSED_COORDINATES_R1.json'),'extra_pose_applications':0,'historical_gate_verdict_inherited':False,'still_present_count':sum(r['current_severe_blocker'] for r in rows),'disappeared_count':sum(not r['current_fresh_evidence']['intersect'] for r in rows),'severity_reduced_count':sum(r['severity_trend']=='SEVERITY_REDUCED' for r in rows),'severity_increased_count':sum(r['severity_trend']=='SEVERITY_INCREASED' for r in rows)})
print('OLD9 FORCED FRESH',[(r['case_id'],r['face_ids'],r['current_identity_status'],r['severity_trend']) for r in rows],flush=True)
