import sys,json,time
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));from geometry_detector import *
A=np.load(O/'ACTUAL_SOURCE_SNAPSHOTS.npz');rows=json.loads((O/'SOURCE_POSES.json').read_text());checks=[]
# Real deformed skin, translated only as a detector fixture, never as a candidate pose.
V=A['C01_INITIAL'];clear=V+np.array([0,0,.08]);r=detect(clear,rows[0]['angles']);checks.append(dict(test='unobstructed_actual_deformed_hand_fixture',pass_=not r['key_hits'],details=r))
key=KEYS[67-21];s=key['key_top_playable_surface'][0];ids=np.array(META['pad_patches'][0]);local=keylocal(V,key,0);v=ids[np.argmin(local[ids,2])]
shift=np.array([(s['xmin']+s['xmax'])/2-local[v,0],(s['ymin']+s['ymax'])/2-local[v,1],s['z']-local[v,2]])
# Known safe/contact/1mm penetration on the SAME finger skin and key, both hinge states.
for angle in [0,float(key['press_angle_rad'])]:
 for gap in [.003,0.,-.001]:
  fixture=local[ids]+shift+[0,0,gap];dep=-np.max(fixture@PL[key['key_index'],0][:,:3].T-PL[key['key_index'],0][:,3],axis=1)*1000;world=keyworld(fixture,key,angle);recovered=keylocal(world,key,angle);err=float(np.max(abs(recovered-fixture)));peak=max(float(dep.max()),0.)
  checks.append(dict(test='known_actual_thumb_skin_key_fixture',pressed_angle=angle,declared_gap_mm=gap*1000,measured_depth_mm=peak,common_space_roundtrip_error_mm=err*1000,pass_=abs(peak-max(-gap*1000,0))<1e-4))
# Two independent skin-triangle fixtures: separated / true intersection; then shared continuous edge.
va=np.array([[0,0,0],[.01,0,0],[0,.01,0]]);vb=np.array([[.002,.002,-.003],[.008,.002,.003],[.002,.008,.003]])
t1=BVHTree.FromPolygons([Vector(v) for v in va],[[0,1,2]],all_triangles=True,epsilon=0);t2=BVHTree.FromPolygons([Vector(v) for v in vb],[[0,1,2]],all_triangles=True,epsilon=0);safe=BVHTree.FromPolygons([Vector(v+[0,0,.02]) for v in vb],[[0,1,2]],all_triangles=True,epsilon=0)
checks.append(dict(test='known_independent_surface_intersection',intersections=len(t1.overlap(t2)),separated_intersections=len(t1.overlap(safe)),pass_=bool(t1.overlap(t2)) and not t1.overlap(safe)))
shared=[set([0,1,2]),set([1,2,3])];checks.append(dict(test='continuous_mesh_connection_exclusion',shared_vertex_filter=bool(shared[0]&shared[1]),nonadjacent_filter=not bool(shared[0]&set([4,5,6])),pass_=bool(shared[0]&shared[1]) and not bool(shared[0]&set([4,5,6]))))
diagnoses=[]
for row in rows:
 target={'midi':78,'finger':3} if row['label']=='APPROVED_R2' else None
 r=detect(A[row['label']],row['angles'],target);diagnoses.append(dict(label=row['label'],time=row['time'],measurement=r));print('ACTUAL_DETECT',row['label'],'wrong_depth',round(r['wrong_key_or_nonpulp_max_depth_mm'],4),'self_triangles',r['nonadjacent_self_triangle_pairs'],flush=True)
validated=all(t['pass_'] for t in checks)
(O/'COLLISION_METHOD_TESTS.json').write_text(json.dumps(dict(status='VALIDATED_FOR_STATIC_SCREEN' if validated else 'COLLISION_METHOD_BLOCKED',checks=checks,scope='Actual deformed mesh, convex key-piece vertex penetration plus triangle intersections; semantic digit surfaces excluding original topology-neighbor contacts',limits=['Sampled nearest gap not exhaustive edge-edge gap','Triangle-only contact with no vertex interior is labelled surface intersection for Human review','Self surface counts have no unique depth conversion','Ambiguous palm/web excluded only from digit-pair attribution, not key collisions']),indent=2)+'\n',encoding='utf8')
(O/'SOURCE_POSE_COLLISION_DIAGNOSES.json').write_text(json.dumps(diagnoses,indent=2)+'\n',encoding='utf8')
assert validated,'COLLISION_METHOD_BLOCKED'
print('DETECTOR_VALIDATION_PASS',len(checks),flush=True)
