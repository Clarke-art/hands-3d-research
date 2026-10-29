import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from sculpt_common import *
sc,mesh,rig,left=open_scene(SOURCE);c.settime(sc,2.6);v,tt,ff=coords(mesh)
z=np.load(PREV/'ORIGINAL_SNAPSHOT.npz');assert np.array_equal(v,z['V']) and np.array_equal(ff,F)
assert len(v)==3300 and len(F)==3298
n=normals(v);J=jacobians(mesh,rig)
neigh={i:set() for i in range(3300)}
for a,b in E:neigh[int(a)].add(int(b));neigh[int(b)].add(int(a))
def edge_distance(ids):
 editable=set(map(int,ids));d={i:0 for i in range(3300) if i not in editable};front=set(d)
 for step in range(1,8):
  more={j for i in front for j in neigh[i] if j not in d}
  for i in more:d[i]=step
  front=more
 return d
def brush(point,center,radius):
 t=np.linalg.norm(point-center)/radius
 if t>=1:return 0.
 return (1-t*t)**2
plans={}
for kind,ids in [('A',A),('B',B)]:
 d=edge_distance(ids);world=np.zeros_like(v)
 if kind=='A':
  center=v[[1075,2576,2591]].mean(0);shoulder=v[1076]
  for i in ids:
   # A deliberate grab of the thumb-facing sidewall, with a softer dorsal shoulder.
   f=brush(v[i],center,.022)*min(1.,.45*d[int(i)])*max(0.,-n[i,0])**.65
   world[i]+=np.array([.0020,0,0])*f
   g=brush(v[i],shoulder,.016)*min(1.,.35*d[int(i)])*max(0.,n[i,2])**2
   world[i]+=np.array([0,0,.00028])*g
  intent='Reduce the non-joint thumb-facing bulge by a broad sidewall grab; retain a gently rounded dorsal shoulder, actual MCP/PIP positions and soft tissue curvature.'
  strokes=[dict(center_world_m=center,radius_m=.022,drag_world_m=[.002,0,0],type='CONTROLLED_LOCAL_GRAB'),dict(center_world_m=shoulder,radius_m=.016,drag_world_m=[0,0,.00028],type='SMALL_DORSAL_SHOULDER_SUPPORT')]
 else:
  center=v[1376];lower=v[1375];core=set(SCOPE['patches']['B']['core_editable_vertex_ids']);normal=n[1376]
  for i in ids:
   facing=max(0.,float(n[i]@normal))
   boundary=min(1.,.65+.17*d[int(i)]) if int(i) in core else min(1.,.36*d[int(i)])
   f=brush(v[i],center,.020)*boundary*facing
   world[i]+=np.array([-.00155,0,.00085])*f
   g=brush(v[i],lower,.018)*min(1.,.30*d[int(i)])*facing
   world[i]+=np.array([-.00035,0,.00012])*g
  intent='Broaden the lower first-web tissue fan and lift the local pinched hollow; preserve the upper natural web recess and fixed S collar, rather than inflate the entire web.'
  strokes=[dict(center_world_m=center,radius_m=.020,drag_world_m=[-.00155,0,.00085],type='CONTROLLED_LOWER_WEB_FILL_GRAB'),dict(center_world_m=lower,radius_m=.018,drag_world_m=[-.00035,0,.00012],type='LOWER_FAN_BLEND')]
 local=np.zeros_like(world)
 for i in ids:local[i]=np.linalg.solve(J[i],world[i])
 plans[kind]={'intent':intent,'strokes':strokes,'world_target_displacements_m':world,'shape_key_displacements_local_m':local}
save('ROUND_1_SCULPT_INTENT_AND_STROKES.json',plans)
for kind,ids in [('A',A),('B',B)]:
 sc,mesh,rig,left=open_scene(SOURCE);c.settime(sc,2.6);sig=signature(mesh,rig,left);_,w=weights(mesh)
 original_shapes={k.name:np.array([list(p.co) for p in k.data]) for k in mesh.data.shape_keys.key_blocks};basis=original_shapes['Basis'];mesh.data=mesh.data.copy()
 key=mesh.shape_key_add(name=kind+'_ANATOMICAL_SCULPT_VISUAL_R1_EXPERIMENT',from_mix=False);key.relative_key=mesh.data.shape_keys.key_blocks['Basis']
 delta=plans[kind]['shape_key_displacements_local_m']
 for i in ids:key.data[int(i)].co=Vector(basis[i]+delta[i])
 key.value=1.;mesh.data.update();bpy.context.view_layer.update()
 assert signature(mesh,rig,left)==sig and np.array_equal(weights(mesh)[1],w)
 for name,co in original_shapes.items():assert np.array_equal(co,np.array([list(p.co) for p in mesh.data.shape_keys.key_blocks[name].data]))
 actual=np.array([list(p.co) for p in key.data])-basis;changed=np.flatnonzero(np.linalg.norm(actual,axis=1)>1e-10)
 assert set(changed)<=set(ids) and not set(changed)&set(SCOPE['S_protected_collar_vertex_ids'])
 vv,t1,f1=coords(mesh);outside=np.setdiff1d(np.arange(3300),ids);assert np.max(abs(vv[outside]-v[outside]))==0
 report={'region':kind,'round':1,'method':'Direct controlled vertex sculpt in an independent additive shape key. No optimization/search, no weight or pose edit.','intent':plans[kind]['intent'],'actual_changed_vertices':changed,'actual_changed_count':len(changed),'max_local_shape_delta_mm':float(np.linalg.norm(actual,axis=1).max()*1000),'max_evaluated_shift_2_6_mm':float(np.linalg.norm(vv-v,axis=1).max()*1000),'outside_allowed_shift_mm':0.,'S_and_collar_shift_mm':float(np.linalg.norm(vv[np.array(SCOPE['S_protected_collar_vertex_ids'])]-v[np.array(SCOPE['S_protected_collar_vertex_ids'])],axis=1).max()*1000),'frozen_basis_weights_corrective_driver_unchanged':True,'manual_shape_value':1.,'automatic_trigger':False,'vertices':[dict(vertex=int(i),basis_local_m=basis[i],sculpt_delta_local_mm=actual[i]*1000,evaluated_delta_world_mm=(vv[i]-v[i])*1000) for i in changed]}
 dest=OUT/(kind+'_SCULPT_ROUND_1_NOT_APPROVED.blend');assert not dest.exists();sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']];bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=True)
 save(kind+'_ROUND_1_EDIT_RECEIPT.json',report);np.savez_compressed(OUT/(kind+'_ROUND_1_SCULPT.npz'),delta=actual,V=vv,T=t1,baseline_V=v)
 print('SCULPTED',kind,'round1','points',len(changed),'maxshift',report['max_evaluated_shift_2_6_mm'],flush=True)
protection('SCULPT_ROUND_1_INPUT_RECEIPT.json')

