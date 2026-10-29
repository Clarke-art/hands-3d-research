import sys,json,time
from pathlib import Path
sys.dont_write_bytecode=True
import numpy as np
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));from geometry_detector import *;from triangle_distance import *
P=O.parent/'hands_skin_collision_static_feasibility_r1';old=json.loads((P/'STATIC_POSE_FEASIBILITY.json').read_text());start=time.monotonic()
planes=np.array([[1,0,0,.005],[-1,0,0,.005],[0,1,0,.005],[0,-1,0,.005],[0,0,1,.005],[0,0,-1,.005]])
T=np.array([[-.012,-.012,0],[.012,-.012,0],[0,.016,0]])
dep,point=triangle_inside_depth(T,planes);safe,_=triangle_inside_depth(T+[0,0,.02],planes);touch,_=triangle_inside_depth(T+[0,0,.005],planes)
assert abs(dep-5)<1e-6 and safe==0 and touch<1e-6
# Known point-face, edge-edge and separated distances.
A=np.array([[[0,0,0],[.01,0,0],[0,.01,0]]]);B=A+[0,0,.001];ds,_,_=distances(A,B);assert abs(ds[0]-.001)<1e-12
E=np.array([[[-.01,0,0],[.01,0,0],[-.01,-.002,0]]]);F=np.array([[[0,-.01,.0001],[0,.01,.0001],[.002,.01,.0001]]]);de,_,_=distances(E,F);assert abs(de[0]-.0001)<1e-12
out=dict(status='MINIMAL_REGRESSION_PASS',triangle_interior_fixture=dict(depth_mm=dep,safe_mm=safe,tangent_mm=touch),distance_fixtures=dict(parallel_mm=float(ds[0]*1000),edge_edge_mm=float(de[0]*1000)),S1=[],source_method='Previously calibrated detector copied hash-identically; exact feature distance supplement')
for ai,a in enumerate(old['tests'][0]['attempts']):
 V=np.load(a['actual_skin_snapshot'])['vertices'];ang=np.array(a['solver']['key_angles']);m=detect(V,ang,dict(midi=67,finger=1));prep=contact_metric(V,KEYS[76-21],ang[76-21],3);witnesses=[]
 for hit in m['key_hits']:
  for w in hit['triangle_interior_witnesses']:
   tid=w['hand_triangle_id'];tt=V[TR[tid]];xy=np.linalg.lstsq(np.column_stack([tt[1]-tt[0],tt[2]-tt[0]]),np.array(w['world_point_m'])-tt[0],rcond=None)[0]
   witnesses.append(dict(midi=hit['midi'],piece=hit['piece'],triangle_id=tid,barycentric=[float(1-xy.sum()),float(xy[0]),float(xy[1])],old_depth_mm=w['inside_depth_mm'],legal_target=w['legal_target_pulp']))
 out['S1'].append(dict(initialization=a['initialization'],actual_geometry=m,preparation=prep,witness_constraints=witnesses,state=a['controls']['state'],key_angles=ang.tolist(),source_time=old['tests'][0]['source_time']))
 print('S1_RECHECK',ai+1,m['target_key_max_depth_mm'],m['contact']['pad_horizontal_outside_mm'],flush=True)
s2=old['tests'][1];a=next(a for a in s2['attempts'] if a['scene']==s2['selected_scene']);V=np.load(a['actual_skin_snapshot'])['vertices'];sm=self_metric(V);mr=next(p for p in sm if p['digits']==['MIDDLE','RING']);assert mr['true_nonadjacent_triangle_pair_count']==0
out['S2_exact_clearance']=exact_clearance(V,TR,np.flatnonzero(LABEL==2),np.flatnonzero(LABEL==3),META['topological_vertex_neighbors'],mr['minimum_gap_sampled_mm']/1000+1e-10);out['S2_previous_sampled_mm']=mr['minimum_gap_sampled_mm'];out['S2_self_metric']=sm
# Translated actual full skin is a regression fixture only, never a solution.
far=detect(V+[0,0,.08],np.array(a['solver']['key_angles']),None,with_self=False);assert far['wrong_key_or_nonpulp_max_depth_mm']==0
out['safe_translated_fixture_no_key_intrusion']=True;out['wall_seconds']=time.monotonic()-start
(O/'MINIMAL_PREFLIGHT_REGRESSION.json').write_text(json.dumps(out,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8');print('PREFLIGHT_COMPLETE',out['S2_exact_clearance'],out['wall_seconds'],flush=True)
