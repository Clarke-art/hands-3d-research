import sys,json,ast,time,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
from skin_proxy import *
from triangle_distance import distances,exact_clearance
TR=RAW['triangles'];LABEL=np.array(META['triangle_labels']);D=RAW;rot=c.axisrot
tree=ast.parse((O/'geometry_detector.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['clip','area','keylocal','keyworld','contact_metric']],type_ignores=[]),'original_contact_functions','exec'))
patch=set(META['pad_patches'][0]);pulpids=np.array([ti for ti in np.flatnonzero(LABEL==0) if all(int(v) in patch for v in TR[ti])])
def full_top_distance(V,angles,crossing):
 k=c.KEYS[46];tops=[]
 for s in k['key_top_playable_surface']:
  corners=np.array([[s['xmin'],s['ymin'],s['z']],[s['xmax'],s['ymin'],s['z']],[s['xmax'],s['ymax'],s['z']],[s['xmin'],s['ymax'],s['z']]])
  corners=keyworld(corners,k,angles[46]);tops.extend([corners[[0,1,2]],corners[[0,2,3]]])
 tops=np.array(tops)
 if crossing:return dict(distance_mm=0.,method='Original independently verified pulp/playable-top intersection; exact zero',crossing=True)
 pa=np.repeat(V[TR[pulpids]],len(tops),axis=0);pb=np.tile(tops,(len(pulpids),1,1));d,a,b=distances(pa,pb);ii=int(np.argmin(d))
 return dict(distance_mm=float(d[ii]*1000),pulp_triangle_id=int(pulpids[ii//len(tops)]),playable_top_triangle_index=ii%len(tops),witness_points_world_m=[a[ii].tolist(),b[ii].tolist()],method='Exhaustive all frozen pulp triangles x complete playable top rectangles triangulated exactly; all point-face and edge-edge features for disjoint triangles',pairs=len(pa),crossing=False)
supp=[]
for ai in [1,2]:
 r=json.loads((O/f'SOLVE_{ai}.json').read_text());a=json.loads((O/f'ACTUAL_VALIDATION_{ai}.json').read_text());snap=np.load(O/f'ACTUAL_SKIN_{ai}.npz');V=snap['vertices'];ang=snap['key_angles']
 ct=contact_metric(V,c.KEYS[46],ang[46],1);err=float(np.linalg.norm(V-skin(np.array(r['state'])),axis=1).max()*1000)
 supp.append(dict(attempt=ai,proxy_actual_max_vertex_difference_mm=err,contact_raw_boolean=bool(a['gates']['actual_surface_contact']),contact_raw_original=a['actual_geometry']['contact'],complete_pulp_to_playable_top_euclidean_distance=full_top_distance(V,ang,ct['top_surface_crossing_triangles']>0),state_change_from_previous_repair=(np.array(r['state'])-np.array(r['initial_state'])).tolist(),maximum_control_delta_mm_or_deg=float(np.max(abs(np.array(r['state'])-np.array(r['initial_state'])))),root_z_delta_from_seed_mm=float(r['state'][2]-r['initial_state'][2])))
old=O.parent/'hands_c01_g4_e5_skin_safe_bridge_r1';reg=json.loads((old/'MINIMAL_PREFLIGHT_REGRESSION.json').read_text());static=O.parent/'hands_skin_collision_static_feasibility_r1';V=np.load(static/'S2_ATTEMPT_1_ACTUAL_SKIN.npz')['vertices'];upper=reg['S2_previous_sampled_mm']/1000+1e-10
s2=exact_clearance(V,TR,np.flatnonzero(LABEL==2),np.flatnonzero(LABEL==3),META['topological_vertex_neighbors'],upper)
assert abs(s2['distance_mm']-reg['S2_exact_clearance']['distance_mm'])<1e-10
old2=np.load(old/'S1_REPAIR_2_ACTUAL_SKIN.npz');hover=full_top_distance(old2['vertices'],old2['key_angles'],False)
out=dict(attempts=supp,S2_readonly_distance_regression=s2,previous_second_repair_hover_true_distance_supplement=hover,no_extra_solve=True,no_geometry_change=True,distance_precision='Float64 exact feature enumeration on float32 Blender-evaluated geometry; original exclusions and full frozen pulp patches unchanged; floating arithmetic, not a formal exact-arithmetic proof')
(O/'INDEPENDENT_DISTANCE_AND_PARITY.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print('S2_DISTANCE_REGRESSION',s2['distance_mm'],'previous hover supplementary',hover['distance_mm'])
print('SUPPLEMENTAL',[(x['attempt'],x['proxy_actual_max_vertex_difference_mm'],x['complete_pulp_to_playable_top_euclidean_distance']['distance_mm']) for x in supp])

