import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));from geometry_detector import *
V=np.load(O/'ACTUAL_SOURCE_SNAPSHOTS.npz')['C01_INITIAL'];k=KEYS[67-21];s=k['key_top_playable_surface'][0];ids=np.array(META['pad_patches'][0]);p=keylocal(V,k,0);v=ids[np.argmin(p[ids,2])];shift=np.array([(s['xmin']+s['xmax'])/2-p[v,0],(s['ymin']+s['ymax'])/2-p[v,1],s['z']-p[v,2]])
rows=[]
for a in [0,float(k['press_angle_rad'])]:
 for g in [.003,0.,-.001]:
  F=keyworld(p+shift+[0,0,g],k,a);r=contact_metric(F,k,a,1);ok=abs(r['true_pulp_min_signed_gap_mm']-g*1000)<1e-5 and (r['hover_only'] if g>0 else not r['hover_only']);rows.append(dict(angle=a,known_gap_mm=g*1000,result=r,pass_=ok));print('TRUE_CONTACT_FIXTURE',a,g,r['true_pulp_min_signed_gap_mm'],r['top_surface_crossing_triangles'],r['near_contact_projected_area_mm2'],ok)
M=json.loads((O/'COLLISION_METHOD_TESTS.json').read_text());M['true_pulp_contact_fixture_tests']=rows;M['contact_tangent_vs_hover_validation']=all(r['pass_'] for r in rows);M['status']='VALIDATED_FOR_STATIC_SCREEN' if M['contact_tangent_vs_hover_validation'] else 'COLLISION_METHOD_BLOCKED';(O/'COLLISION_METHOD_TESTS.json').write_text(json.dumps(M,indent=2)+'\n',encoding='utf8');assert M['contact_tangent_vs_hover_validation']
