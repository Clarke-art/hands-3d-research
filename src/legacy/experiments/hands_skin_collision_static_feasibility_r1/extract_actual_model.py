import sys,json,ast,math
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
O=Path(__file__).resolve().parent;PREV=O.parent/'hands_c01_whole_hand_motion_feasibility_r1';sys.path.insert(0,str(PREV));import blender_utils as u
u.O=O
P=json.loads((O/'POLICY_LOCK.json').read_text());I=P['source_input'];M=P['source_action_scene'];ROOT=O.parent/'hands'
bpy.ops.wm.open_mainfile(filepath=M['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[M['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[M['mapping']['R']['rig']];mesh=bpy.data.objects[M['mapping']['R']['mesh']]
assert u.digest(u.native(mesh,rig))==u.pf['right_native_sha256']
rest=np.array([np.array(b.matrix_local) for b in rig.data.bones]);names=[b.name for b in rig.data.bones];parents=np.array([names.index(b.parent.name) if b.parent else -1 for b in rig.data.bones]);weights=np.zeros((len(mesh.data.vertices),len(names)))
for v in mesh.data.vertices:
 for g in v.groups:
  name=mesh.vertex_groups[g.group].name
  if name in names:weights[v.index,names.index(name)]=g.weight
meshToRig=np.array(rig.matrix_world.inverted()@mesh.matrix_world);verts=np.array([list(v.co) for v in mesh.data.vertices]);shapes=mesh.data.shape_keys;assert len(shapes.key_blocks)==2
shape=np.array([list(v.co) for v in shapes.key_blocks[1].data])-verts
mesh.data.calc_loop_triangles();tri=np.array([list(t.vertices) for t in mesh.data.loop_triangles]);faceNormals=np.array([list(t.normal) for t in mesh.data.loop_triangles]);groupW=np.array([weights[:,[i for i,n in enumerate(names) if n.startswith(d+'_')]].sum(1) for d in u.c.DIGITS]).T
triW=groupW[tri].mean(1);labels=np.where(triW.max(1)>.55,triW.argmax(1),-1)
# Root/web exclusions use original mesh topological adjacency, not world proximity.
vertexTris=[set() for v in verts]
for i,T in enumerate(tri):
 for v in T:vertexTris[v].add(i)
neighbors=[]
for i,T in enumerate(tri):neighbors.append(sorted(set.union(*(vertexTris[v] for v in T))-{i}))
region={d:np.flatnonzero(labels==i).tolist() for i,d in enumerate(u.c.DIGITS)}
padIndices=np.array([r['mesh_vertex'] for r in u.c.MARKERS['R']]);patches=[]
for j,d in enumerate(u.c.DIGITS):
 ids=np.flatnonzero((groupW[:,j]>.55)&(np.linalg.norm(verts-verts[padIndices[j]],axis=1)<.016));patches.append(ids.tolist())
baseRig=np.array(u.BASEMAT)@np.array(u.pf['full_root_rig_relation'])
np.savez_compressed(O/'SKIN_MODEL.npz',rest_matrices=rest,parents=parents,weights=weights,rest_vertices=verts,mesh_to_rig=meshToRig,shape_delta=shape,triangles=tri,base_rig_world=baseRig,base_root_matrix=np.array(u.BASEMAT),group_weights=groupW,pad_indices=padIndices)
metadata=dict(names=names,regions=region,triangle_labels=labels.tolist(),topological_vertex_neighbors=neighbors,pad_patches=patches,driver=[dict(path=f.data_path,expression=f.driver.expression,variables=[dict(name=v.name,type=v.type,targets=[dict(bone=t.bone_target,transform_type=t.transform_type,space=t.transform_space) for t in v.targets]) for v in f.driver.variables]) for f in shapes.animation_data.drivers],hand_identity=u.pf['right_native_sha256'],root_base_xyz_m=u.BASE.tolist(),key_table=u.c.KEYS,source_region_scope='Mean per-triangle semantic digit weights >0.55; ambiguous palm/web faces excluded from pair attribution but included in all-key collision',source_shape_names=[x.name for x in shapes.key_blocks])
(O/'SKIN_MODEL_META.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf8')
# Actual evaluated test records for surrogate parity and source diagnoses.
rows=[];snap={};srcA=np.load(PREV/'motion.npz')
for label,t in [('C01_INITIAL',1.914284),('S1_INITIAL',2.527855),('S2_INITIAL',2.956426),('S3_INITIAL',3.384997),('S4_INITIAL',4.0278535),('S5_INITIAL',4.67071)]:
 u.settime(sc,t);V,F=u.coords(mesh);row=dict(label=label,time=t,angles=u.keyangles().tolist(),pose_quats=[list(b.rotation_quaternion) for b in rig.pose.bones],rig_world=np.array(rig.matrix_world).tolist(),root_state=np.r_[[np.interp(t,srcA['times'],srcA['R_delta'][:,j])*1000 for j in range(3)],[np.interp(t,srcA['times'],srcA['R_extra_rot_deg'][:,j]) for j in range(3)],[np.interp(t,srcA['times'],np.degrees(srcA['R_q']).reshape(-1,20)[:,j]) for j in range(20)]].tolist());rows.append(row);snap[label]=V
sm=I['static_scene'];bpy.ops.wm.open_mainfile(filepath=sm['candidate_path'],load_ui=False,use_scripts=False)
for pose in ['R1','R2']:
 info=sm['mapping'][pose];sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[info['rig']];mesh=bpy.data.objects[info['mesh']];V,F=u.coords(mesh);snap['APPROVED_'+pose]=V;rows.append(dict(label='APPROVED_'+pose,time=None,angles=[0.]*88,pose_quats=[list(b.rotation_quaternion) for b in rig.pose.bones],rig_world=np.array(rig.matrix_world).tolist()))
np.savez_compressed(O/'ACTUAL_SOURCE_SNAPSHOTS.npz',**snap)
(O/'SOURCE_POSES.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8')
print('EXTRACTED_ACTUAL_SKIN',len(verts),len(tri),'regions',[len(region[d]) for d in u.c.DIGITS],metadata['driver'],flush=True)
