"""All actual source/posed crossing families at42 fresh current endpoints.
Historical comparator evaluated only from its already-recorded immutable coordinates.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import math
from types import SimpleNamespace
from mathutils import Vector
from mathutils.bvhtree import BVHTree
MM=1000.;reused=[]
G=read(OUT/'POSED_COORDINATES_R1.json');H=read(HIST/'POSED_COORDINATES_R1.json');POLY=G['faces'];EDGES=G['edges'];datasets={'CURRENT':G,'HISTORICAL_COMPARATOR':H}
reused.append(reuse(S5/'stage5b_r1e/scripts/s5b_r1e_prequal.py',['intersect_pairs'],globals()))
rn={'math':math,'Vector':Vector,'MM':MM};names=['ray_triangle','tri_tri_intersection','seg_len','closest_point_on_triangle','poke_depth','tris_of']
reused.append(reuse(S6/'stage6b_r1c/scripts/r1c_pen_common.py',names,rn));R=SimpleNamespace(**{n:rn[n] for n in names})
reused.append(reuse(S6/'stage6b_r1c/scripts/r1c_pen_v2.py',['tri_of','tri_mean_edge','pair_evidence','classify'],globals()))
results={};bind={}
for asset,data in datasets.items():
 V0=[Vector(p) for p in data['bind_raw_world_m']];FACE_TRIS={}
 for fi,t in R.tris_of(POLY,V0):FACE_TRIS.setdefault(fi,[]).append(t)
 CHARACTERISTIC_EDGE_MM=sorted((V0[a]-V0[b]).length*MM for a,b in EDGES)[len(EDGES)//2]
 vb=[Vector(p) for p in data['positions_world_m']['BIND']];basepairs=set();br=[]
 for fa,fb in sorted(intersect_pairs(vb,POLY)):
  e=pair_evidence(vb,fa,fb)
  if e['intersect']:basepairs.add((fa,fb));br.append({'face_ids':[fa,fb],'class':classify(e),**e})
 bind[asset]=br;results[asset]={}
 for c in read(OUT/'FULL_STAGE6A_POST_DONOR_CASE_MATRIX_R1.json')['cases']:
  cid=c['case_id'];v=[Vector(p) for p in data['positions_world_m'][cid]];rows=[]
  for fa,fb in sorted(intersect_pairs(v,POLY)):
   e=pair_evidence(v,fa,fb)
   if not e['intersect']:continue
   rows.append({'case_id':cid,'face_ids':[fa,fb],'class':classify(e),**e,'same_pair_at_evaluated_bind':(fa,fb) in basepairs})
  results[asset][cid]=rows
dump('COMPLETE_NATIVE_CROSSING_CENSUS_R1.json',{'results':results,'bind_exact':bind,'methods':reused,'actual_current_formal_case_count':42,'new_current_pose_applications':0,'historical_pose_applications':0,'count_semantics':'Every exact nonshared-vertex triangle pair at every current endpoint, including SOURCE_EXISTING_CONTACT. Corrected Full Stage6A hard gate retains separately evaluated bind baseline; pose-generated unapproved Class A is the formal severe gate. Existing source contacts are not silently Human-approved.'})
print('FULL CENSUS', {a:sum(len(z) for z in r.values()) for a,r in results.items()},'native bind',{a:len(z) for a,z in bind.items()},flush=True)
