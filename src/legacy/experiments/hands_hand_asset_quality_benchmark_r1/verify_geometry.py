import bpy,json,sys,hashlib
from pathlib import Path
import numpy as np
from mathutils import Matrix,Vector
from bpy_extras.object_utils import world_to_camera_view
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'HAND_ASSET_BENCHMARK_STATIC.blend'),load_ui=False,use_scripts=False)
sc=bpy.context.scene;align=json.loads((OUT/'ALIGNMENT_AND_POSE_RECEIPT.json').read_text());renders=json.loads((OUT/'RENDER_MANIFEST.json').read_text())
rows={};projects=[]
for ident in ['C1','MAKEHUMAN']:
 rows[ident]={}
 neutral=np.load(OUT/(ident+'__NEUTRAL.npz'),allow_pickle=True)['V']
 for state in ['NEUTRAL','INDEX_FLEX','THUMB_SPREAD']:
  ob=bpy.data.objects[ident+'__'+state];me=ob.data;me.calc_loop_triangles();v=np.array([list(x.co) for x in me.vertices]);t=np.array([list(f.vertices) for f in me.loop_triangles]);p=v[t];area2=np.linalg.norm(np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]),axis=1)
  unique,inv=np.unique(np.round(v,8),axis=0,return_inverse=True)
  edges=np.concatenate([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);edges=np.sort(edges,axis=1);_,ct=np.unique(edges,axis=0,return_counts=True)
  we=np.sort(inv[edges],axis=1);_,wct=np.unique(we,axis=0,return_counts=True)
  rows[ident][state]=dict(vertices=len(v),faces=len(me.polygons),triangles=len(t),unique_positions_rounded_1e_8_m=len(unique),nonfinite_vertices=int(np.sum(~np.all(np.isfinite(v),axis=1))),degenerate_triangles_area2_lt_1e_14=int(np.sum(area2<1e-14)),min_double_area_mm2=float(area2.min()*1e6),native_boundary_edges=int(np.sum(ct==1)),native_nonmanifold_edges_gt2=int(np.sum(ct>2)),position_welded_boundary_edges=int(np.sum(wct==1)),position_welded_nonmanifold_edges_gt2=int(np.sum(wct>2)),max_displacement_from_neutral_mm=float(np.linalg.norm(v-neutral,axis=1).max()*1000),self_intersection='NOT_TESTED',collision_and_contact='NOT_TESTED')
for r in renders:
 sc.camera.matrix_world=Matrix(r['camera_matrix']);sc.camera.data.ortho_scale=r['ortho_scale'];sc.render.resolution_x,sc.render.resolution_y=r['resolution'];bpy.context.view_layer.update()
 points={}
 for label,key in [('MCP','index'),('PIP','pip')]:
  co=align[r['identity']]['states'][r['state']]['pose_joints_normalized_m'][key];q=world_to_camera_view(sc,sc.camera,Vector(co));points[label]=[float(q.x*r['resolution'][0]),float((1-q.y)*r['resolution'][1])]
 projects.append(dict(identity=r['identity'],view=r['view'],points_pixels=points))
assert all(all(x['camera_matrix']==y['camera_matrix'] and x['ortho_scale']==y['ortho_scale'] for x,y in zip(renders[::2],renders[1::2])) for _ in [0])
(OUT/'GEOMETRY_AND_TEST_SCOPE.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
(OUT/'JOINT_PROJECTION_RECEIPT.json').write_text(json.dumps(projects,indent=2),encoding='utf8')
print('GEOMETRY_SCOPE_AND_CAMERA_EQUALITY_VERIFIED',flush=True)
