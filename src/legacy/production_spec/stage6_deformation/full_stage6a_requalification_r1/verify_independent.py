"""Second fresh Blender process: reproduce all42 posed coordinates and exact failures.
No blend saves; no historical qualification reruns.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,math
from types import SimpleNamespace
from mathutils import Vector,Quaternion
MM=1000.
G=read(OUT/'POSED_COORDINATES_R1.json');E=read(OUT/'FULL_STAGE6A_MACHINE_EVIDENCE_R1.json')
ns={'bpy':bpy,'math':math,'Vector':Vector,'Quaternion':Quaternion,'MM':MM}
reuse(S6/'stage6a/scripts/s6a_common.py',['reset_pose','set_joint_rotation','evaluate'],ns)
S=SimpleNamespace(**{k:ns[k] for k in ['reset_pose','set_joint_rotation','evaluate']})
bpy.ops.wm.open_mainfile(filepath=str(CAND),load_ui=False,use_scripts=False)
ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];MW=ob.matrix_world.copy()
V0=[<REDACTED_EMAIL> for v in ob.data.vertices];POLY=[tuple(f.vertices) for f in ob.data.polygons]
EDGES=[tuple(e.vertices) for e in ob.data.edges];EDGE_LEN0=[(V0[a]-V0[b]).length for a,b in EDGES]
CHARACTERISTIC_EDGE_MM=sorted(EDGE_LEN0)[len(EDGES)//2]*MM
rn={'Vector':Vector,'MM':MM,'math':math}
names=['ray_triangle','tri_tri_intersection','seg_len','closest_point_on_triangle','poke_depth','tris_of']
reuse(S6/'stage6b_r1c/scripts/r1c_pen_common.py',names,rn);R=SimpleNamespace(**{k:rn[k] for k in names})
TRIS=R.tris_of(POLY,V0);FACE_TRIS={}
for fi,t in TRIS:FACE_TRIS.setdefault(fi,[]).append(t)
reuse(S6/'stage6b_r1c/scripts/r1c_pen_v2.py',['tri_of','tri_mean_edge','pair_evidence','classify'],globals())
rows=[];pair_rows=[]
for cid,row in E['cases'].items():
 S.reset_pose(rig);bpy.context.view_layer.update()
 c=row['case'];S.set_joint_rotation(rig,c['bone'],c['applied_rotation_deg']);bpy.context.view_layer.update()
 V,P=S.evaluate(ob,MW);assert P==POLY
 diff=max((v-Vector(saved)).length*MM for v,saved in zip(V,G['positions_world_m'][cid]))
 severe=[j for j,(a,b) in enumerate(EDGES) if EDGE_LEN0[j]*MM>=3 and (V[a]-V[b]).length/EDGE_LEN0[j]>5]
 assert diff==0 and severe==[r['edge_id'] for r in row['severe_edges']],(cid,diff,severe)
 for r in row['crossings']:
  if not r['hard_blocker'] and not r['acceptance'].startswith('KNOWN_'):continue
  p=r['face_ids'];ev=pair_evidence(V,*p)
  assert classify(ev)==r['class'] and all(ev[k]==r[k] for k in ['intersect','depth_mm','local_edge_mm','seg_mm'])
  bind=pair_evidence([Vector(v) for v in G['positions_world_m']['BIND']],*p)
  assert not bind['intersect'],(cid,p,'preexisting bind crossing')
  pair_rows.append({'case_id':cid,'face_ids':p,'numeric_exact_match':True,'bind_exact_crossing':False,'posed_classifier':classify(ev),'pose_pair_acceptance':r['acceptance']})
 rows.append({'case_id':cid,'posed_coordinates_max_difference_mm':diff,'severe_edge_count':len(severe)})
S.reset_pose(rig);bpy.context.view_layer.update()
assert sha(CAND)==EXPECTED_CAND
dump('INDEPENDENT_REPRODUCTION_VERIFICATION_R1.json',{'status':'PASS_EXACT_42_CASE_COORDINATE_AND_12_PAIR_NUMERIC_MATCH','cases':rows,'severe_or_accepted_pairs':pair_rows,'blend_save_count':0,'production_drift':0,'prior_historical_candidates_reexecuted':0})
print('INDEPENDENT VERIFIED',len(rows),'cases',len(pair_rows),'pairs; zero saves')
