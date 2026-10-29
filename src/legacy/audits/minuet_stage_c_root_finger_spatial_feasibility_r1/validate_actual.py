import sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];R3=ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance';R4=ROOT/'audits/minuet_stage_c_r4_multi_finger_coordinated_clearance'
exec(compile((R3/'diagnose.py').read_text(encoding='utf8').split('results={};witnesses={}')[0],str(R3/'diagnose.py'),'exec'))
P=HERE;OUT=HERE
from mathutils import Quaternion,Matrix
rois=read(R3/'LOCAL_SKIN_ROI.json');pre=read(P/'BOUNDED_STATIC_RESULTS.json');assert pre['complete']
man,sc,rig,mesh=open_stage(C1);root=bpy.data.objects[man['mapping']['R']['root']]
rig_action=rig.animation_data.action;root_action=root.animation_data.action
fixed=next(r for r in read(R4/'STATIC_PREFLIGHT.json')['poses'] if abs(r['video_sec']-3.825)<1e-6)
def triangles(faces):return [[f[0],f[j],f[j+1]] for f in faces for j in range(1,len(f)-1)]
def closed_patch(V,d):
 fs=triangles(rois[d]['faces']);edges={}
 for f in fs:
  for a,b in zip(f,f[1:]+f[:1]):
   key=tuple(sorted([a,b]));edges.setdefault(key,[]).append((a,b))
 boundary=[e[0] for e in edges.values() if len(e)==1];verts=V.tolist();cap=len(verts);verts.append(V[sorted(set(i for e in boundary for i in e))].mean(axis=0).tolist())
 return np.array(verts),fs+[[b,a,cap] for a,b in boundary],len(fs),len(boundary)
def penetration_witnesses(V,a,b):
 bv,faces,real_count,boundary=closed_patch(V,b);tri=bv[np.array(faces)];tree=BVHTree.FromPolygons([Vector(v) for v in V],rois[b]['faces'],epsilon=0);closed=BVHTree.FromPolygons([Vector(v) for v in bv],faces,all_triangles=True,epsilon=0)
 witnesses=[];cap_nearest=0
 for vid in rois[a]['vertices']:
  p=V[vid];vec=tri-p;l=np.linalg.norm(vec,axis=-1);num=np.einsum('ij,ij->i',vec[:,0],np.cross(vec[:,1],vec[:,2]));den=l.prod(axis=1)+np.einsum('ij,ij->i',vec[:,0],vec[:,1])*l[:,2]+np.einsum('ij,ij->i',vec[:,1],vec[:,2])*l[:,0]+np.einsum('ij,ij->i',vec[:,2],vec[:,0])*l[:,1]
  winding=float(np.arctan2(num,den).sum()/(2*np.pi))
  if abs(winding)<.5:continue
  closed_hit=closed.find_nearest(Vector(p))
  if closed_hit[2]>=real_count:cap_nearest+=1;continue
  hit=tree.find_nearest(Vector(p));witnesses.append(dict(vertex=vid,point_world_m=p,nearest_skin_world_m=list(hit[0]),depth_to_actual_skin_mm=hit[3]*1000,inside_closed_local_patch_winding=winding))
 witnesses.sort(key=lambda x:x['depth_to_actual_skin_mm'],reverse=True)
 return dict(from_digit=a,into_digit=b,inside_witness_count=len(witnesses),max_depth_mm=witnesses[0]['depth_to_actual_skin_mm'] if witnesses else 0,witnesses=witnesses[:4],cap_nearest_excluded=cap_nearest,closure_boundary_edges=boundary,method='Local distal skin patch closed only across cut boundary; solid-angle inside classification. Depth is distance of an inside sampled vertex to real opposing skin, excluding artificial-cap-nearest witnesses. Not an exact global maximum penetration or minimum separation translation.')
def segment_triangle(p,q,tri):
 a,b,c0=tri;n=np.cross(b-a,c0-a);den=np.dot(n,q-p)
 if abs(den)<1e-15:return None
 s=np.dot(n,a-p)/den
 if s< -1e-7 or s>1+1e-7:return None
 hit=p+s*(q-p);u=b-a;v=c0-a;w=hit-a;uv=np.dot(u,v);uu=np.dot(u,u);vv=np.dot(v,v);wu=np.dot(w,u);wv=np.dot(w,v);det=uu*vv-uv*uv
 if abs(det)<1e-20:return None
 alpha=(vv*wu-uv*wv)/det;beta=(uu*wv-uv*wu)/det
 return hit if alpha>=-1e-6 and beta>=-1e-6 and alpha+beta<=1+1e-6 else None
def key_depth(V,d,kv,kf,tree):
 tri=kv[np.array(triangles(kf))];rows=[]
 for vid in rois[d]['vertices']:
  p=V[vid];vec=tri-p;l=np.linalg.norm(vec,axis=-1);num=np.einsum('ij,ij->i',vec[:,0],np.cross(vec[:,1],vec[:,2]));den=l.prod(axis=1)+np.einsum('ij,ij->i',vec[:,0],vec[:,1])*l[:,2]+np.einsum('ij,ij->i',vec[:,1],vec[:,2])*l[:,0]+np.einsum('ij,ij->i',vec[:,2],vec[:,0])*l[:,1]
  winding=float(np.arctan2(num,den).sum()/(2*np.pi))
  if abs(winding)>.5:
   h=tree.find_nearest(Vector(p));rows.append(dict(vertex=vid,depth_mm=h[3]*1000,point_world_m=p,surface_world_m=list(h[0]),winding=winding))
 rows.sort(key=lambda r:r['depth_mm'],reverse=True)
 return dict(inside_vertices=len(rows),max_depth_mm=rows[0]['depth_mm'] if rows else 0,witnesses=rows[:3],method='Solid angle of actual key triangles plus nearest actual surface distance; sampled distal skin vertices only')
def pairs(V,a,b):
 trees=[BVHTree.FromPolygons([Vector(v) for v in V],rois[d]['faces'],epsilon=0) for d in [a,b]];overlap=trees[0].overlap(trees[1]);points=[]
 for i,j in overlap:
  for f1 in triangles([rois[a]['faces'][i]]):
   for f2 in triangles([rois[b]['faces'][j]]):
    for x,y in [(V[f1],V[f2]),(V[f2],V[f1])]:
     for k in range(3):
      hit=segment_triangle(x[k],x[(k+1)%3],y)
      if hit is not None:points.append(hit)
 return dict(digits=[a,b],face_pairs=len(overlap),intersection_point_count=len(points),intersection_world_bbox_m=[np.min(points,axis=0),np.max(points,axis=0)] if points else None,penetration=[penetration_witnesses(V,a,b),penetration_witnesses(V,b,a)] if overlap else [])
rows=[]
cases=[('R1_SOURCE',t,None) for t in [3.75,3.825,3.85]]+[('A_R4_FIXED_ROOT',3.825,fixed)]+[('B_BOUNDED_ROOT',r['video_sec'],r) for r in pre['poses']]
for index,(label,t,row) in enumerate(cases):
 rig.animation_data.action=rig_action;root.animation_data.action=root_action;settime(sc,t);saved={b.name:b.rotation_quaternion.copy() for b in rig.pose.bones};rootmatrix=root.matrix_world.copy();pivot=<REDACTED_EMAIL>['WRIST_R'].matrix.translation
 before_actions=len(bpy.data.actions)
 if row:
  rig.animation_data.action=None;root.animation_data.action=None
  delta=np.array(row['delta_deg'])
  for j,d in enumerate(['INDEX','MIDDLE','RING']):
   names,rels,axes,spread,pad=c.SETUPS['R',d]
   for k,name in enumerate(names):
    value=saved[name]@Quaternion(Vector(axes[k]),math.radians(delta[j,k]))
    if k==0:value=Quaternion(Vector(spread),math.radians(delta[j,3]))@value
    rig.pose.bones[name].rotation_quaternion=value
  rd=row.get('root_delta',[0]*5);rv=Vector([math.radians(rd[3]),0,math.radians(rd[4])]);rotation=Quaternion(rv.normalized(),rv.length).to_matrix().to_4x4() if rv.length else Matrix.Identity(4)
  transform=Matrix.Translation(pivot+Vector(rd[:3])/1000)@<REDACTED_EMAIL>(-pivot)
  root.matrix_world=transform@rootmatrix
 bpy.context.view_layer.update();V,F=mesh_pose(mesh);keys=key_geometry(sc);bh=black_relation(V,rois,keys)
 relation=[pairs(V,a,b) for a,b in [('INDEX','MIDDLE'),('MIDDLE','RING'),('RING','LITTLE')]]
 contacts=[]
 for n in tl['notes']:
  if n['hand']=='R' and n['note_on']<=t<n['note_off']:
   k=c.KEYS[n['key_index']];angle=bpy.data.objects[man['key_pivots'][str(n['key_index'])]].rotation_euler.x
   contacts.append(dict(note=n['note_name'],finger=n['finger'],skin=contact(V[c.MARKERS['R'][n['finger']-1]['mesh_vertex']],k,angle)))
 # Narrow local white-key safety check (D5/E5/F5), using actual meshes.
 wk={}
 for midi in [74,76,77]:
  ob=next(o for o in sc.objects if o.type=='MESH' and not o.hide_render and f'KEY_RENDER_{midi:03d}' in o.name);kv,kf=mesh_pose(ob)
  wk[midi]=dict(note=next(k['note_name'] for k in c.KEYS if k['midi_note']==midi),pairs=[])
  kt=BVHTree.FromPolygons([Vector(v) for v in kv],kf,epsilon=0)
  for d in rois:
   dt=BVHTree.FromPolygons([Vector(v) for v in V],rois[d]['faces'],epsilon=0);count=len(dt.overlap(kt))
   if count:wk[midi]['pairs'].append(dict(digit=d,face_pairs=count,penetration=key_depth(V,d,kv,kf,kt)))
 np.savez_compressed(P/f'{index:02d}_actual_skin.npz',V=V[[int(i) for i in read(P/'LOCAL_MODEL_MANIFEST.json')['ids']]])
 result=dict(label=label,video_sec=t,music_sec=t-.35,root_world=np.array(root.matrix_world),wrist_world=list(<REDACTED_EMAIL>['WRIST_R'].matrix.translation),pairs=relation,black=bh,contacts=contacts,local_white_keys=wk,actual_bone_quaternions={b.name:list(b.rotation_quaternion) for b in rig.pose.bones},action_count_unchanged=len(bpy.data.actions)==before_actions)
 rows.append(result);save('ACTUAL_STATIC_COMPARISON.json',dict(complete=len(rows)==len(cases),poses=rows,new_actions=0,new_blends=0,new_dynamic_solves=0,new_dynamic_candidates=0))
 print('ACTUAL',label,t,'PAIR',[(p['digits'],p['face_pairs'],[w['max_depth_mm'] for w in p['penetration']]) for p in relation],'BLACK',[(h['digit'],h['note'],h['depth_mm']) for h in bh],'CONTACT',contacts,flush=True)
 folder=P/'static_frames';folder.mkdir(exist_ok=True)
 for view,name in ([] if '--no-render' in sys.argv else man['cameras'].items()):
  sc.camera=bpy.data.objects[name];sc.render.filepath=str(folder/f'{index:02d}_{view}.png');bpy.ops.render.render(write_still=True)
 root.matrix_world=rootmatrix;rig.animation_data.action=rig_action;root.animation_data.action=root_action
print('STATIC_COMPARISON_FINISHED_NO_ACTION_OR_BLEND_SAVED',flush=True)
