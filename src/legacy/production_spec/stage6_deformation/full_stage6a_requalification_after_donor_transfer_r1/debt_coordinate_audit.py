import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import math
from types import SimpleNamespace
from mathutils import Vector
MM=1000.;G=read(OUT/'POSED_COORDINATES_R1.json');V0=[Vector(p) for p in G['bind_raw_world_m']];POLY=G['faces'];EDGES=G['edges'];H=read(HIST/'POSED_COORDINATES_R1.json')['positions_world_m'];C=read(OUT/'FULL_STAGE6A_MACHINE_EVIDENCE_R1.json')['cases']
sn={'math':math,'Vector':Vector,'MM':MM};names=['face_area','face_normal','stats'];provenance=reuse(S6/'stage6a/scripts/s6a_common.py',names,sn);S=SimpleNamespace(**{n:sn[n] for n in names})
bl=[(V0[a]-V0[b]).length for a,b in EDGES];ba=[S.face_area(V0,p) for p in POLY];rows=[];total=0
for d in read(TARGETED/'TARGETED_INHERITED16_DEBT_REVALIDATION_R1.json')['rows']:
 k=d['debt_id'];a,b=EDGES[k];fs=[i for i,p in enumerate(POLY) if a in p or b in p];es=[i for i,e in enumerate(EDGES) if a in e or b in e];ids=sorted({i for fi in fs for i in POLY[fi]});obs=[]
 for cid,c in C.items():
  if c['case']['bone'] not in d['driver_family']:continue
  v=[Vector(p) for p in G['positions_world_m'][cid]];ers={str(i):(v[EDGES[i][0]]-v[EDGES[i][1]]).length/bl[i] for i in es};ars={str(i):S.face_area(v,POLY[i])/ba[i] for i in fs}
  severe=[i for i in es if bl[i]*MM>=3 and ers[str(i)]>5];collapsed=[i for i in fs if S.face_area(v,POLY[i])<=1e-12 or ars[str(i)]<=1e-6];destroy=[i for i in fs if ars[str(i)]<.05];deg=[i for i in es if (v[EDGES[i][0]]-v[EDGES[i][1]]).length<=1e-12]
  cr=[z for z in c['crossings'] if z['hard_blocker'] and set(z['face_ids']).intersection(fs)]
  fail=len(severe)+len(collapsed)+len(destroy)+len(deg)+len(cr);total+=fail
  obs.append({'case_id':cid,'endpoint_edge_ratio':ers[str(k)],'incident_max_edge_ratio':max(ers.values()),'incident_min_edge_ratio':min(ers.values()),'incident_min_face_area_ratio':min(ars.values()),'edge_ratios':ers,'face_area_ratios':ars,'severe_edge_ids':severe,'collapsed_face_ids':collapsed,'destroyed_area_face_ids':destroy,'degenerate_edge_ids':deg,'unapproved_severe_exact_crossings':cr,'true_failure_count':fail,'old_vs_current_patch_coordinate_exact':all(G['positions_world_m'][cid][i]==H[cid][i] for i in ids)})
 rows.append({'debt_id':k,'endpoints':[a,b],'incident_vertex_ids':ids,'incident_face_ids':fs,'incident_edge_ids':es,'support_overlap54':sorted(set(ids)&set(APPROVED54)),'observations':obs,'true_failure_count':sum(z['true_failure_count'] for z in obs),'static_debt_status':'NOT_RESOLVED','disposition':'STATIC_QUALIFICATION_DEBT_WITHOUT_TRUE_DEFORMATION_FAILURE' if not any(z['true_failure_count'] for z in obs) else 'TRUE_DEFORMATION_FAILURE_RECORDED','old_static_debt_deleted':False,'scope_expanded':False})
dump('FULL_STAGE6A_INHERITED16_DEBT_AUDIT_R1.json',{'count':16,'rows':rows,'true_deformation_failure_count':total,'fresh_current_endpoint_coordinates':ref(OUT/'POSED_COORDINATES_R1.json'),'source_methods':provenance,'historical_debt_authority':ref(TARGETED/'TARGETED_INHERITED16_DEBT_REVALIDATION_R1.json'),'extra_pose_applications':0,'debt_static_resolved':False})
print('FULL42 DEBT SUPPORT MAPPING',len(rows),'true failures',total,flush=True)
