import sys
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
sys.path.insert(0,str(ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement'))
from blender_local import *
OUT=Path(__file__).resolve().parent
def save(n,v):
    (OUT/n).write_text(json.dumps(v,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item()),encoding='utf8')
policy=read(OUT/'PREFLIGHT_POLICY.json');man=read(C1/'SCENE_MANIFEST.json')
assert sha(man['path'])==policy['source_sha256']
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False)
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
info=man['mapping']['R'];rig=bpy.data.objects[info['rig']];mesh=bpy.data.objects[info['mesh']]
settime(sc,0)
names=[b.name for b in rig.data.bones];bn={n:i for i,n in enumerate(names)}
native=np.array([list(v.co) for v in mesh.data.vertices]);W=np.zeros((len(native),len(names)))
for i,v in enumerate(mesh.data.vertices):
    for g in v.groups:
        name=mesh.vertex_groups[g.group].name
        if name in bn:W[i,bn[name]]=g.weight
rois={}
rest=np.array([list(rig.matrix_world.inverted()@<REDACTED_EMAIL>) for v in mesh.data.vertices])
for digit in c.DIGITS:
    first=digit+('_CMC_R' if digit=='THUMB' else '_MCP_R')
    tip=digit+'_TIP_R'
    origin=np.array(rig.data.bones[first].head_local);axis=np.array(rig.data.bones[tip].head_local)-origin;axis/=np.linalg.norm(axis)
    digit_weight=W[:,[j for j,n in enumerate(names) if n.startswith(digit+'_')]].sum(1)
    ids=np.flatnonzero((digit_weight>.55)&((rest-origin)@axis>.005));mask=set(ids)
    rois[digit]=dict(vertices=ids.tolist(),faces=[list(p.vertices) for p in mesh.data.polygons if all(v in mask for v in p.vertices)])
times=policy['samples'];world=[];Q=[];V=[];angles=[];shape=[]
for i,t in enumerate(times):
    settime(sc,t);world.append(np.array(rig.matrix_world));Q.append([list(b.rotation_quaternion) for b in rig.pose.bones]);V.append(mesh_pose(mesh)[0])
    angles.append([bpy.data.objects[man['key_pivots'][str(k['key_index'])]].rotation_euler.x if str(k['key_index']) in man['key_pivots'] else 0 for k in c.KEYS])
    shape.append([k.value for k in mesh.data.shape_keys.key_blocks] if mesh.data.shape_keys else [])
    if i%150==0:print('R6_READONLY_EXPORT',i,len(times),flush=True)
np.savez_compressed(OUT/'SOURCE_MODEL.npz',times=times,rest_vertices=native,weights=W,
    rest_matrices=[np.array(b.matrix_local) for b in rig.data.bones],
    parents=[bn[b.parent.name] if b.parent else -1 for b in rig.data.bones],
    mesh_to_rig=np.array(rig.matrix_world.inverted()@mesh.matrix_world),rig_world=world,
    quat=Q,actual_skin=V,key_angles=angles,shape_values=shape)
save('SOURCE_MODEL_MANIFEST.json',dict(bones=names,rois=rois,faces=[list(p.vertices) for p in mesh.data.polygons],
    modifiers=[dict(type=m.type,preserve_volume=getattr(m,'use_deform_preserve_volume',None)) for m in mesh.modifiers],
    markers=c.MARKERS['R'],source_sha256=man['sha256'],shape_names=[k.name for k in mesh.data.shape_keys.key_blocks] if mesh.data.shape_keys else [],
    actions={name:sha(man['path']) for name in ['source_scene_readonly']},new_actions=0,new_blends=0,pose_edits=0))
print('R6_READONLY_EXPORT_DONE',len(native),'vertices',flush=True)
