import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1];R3=ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance';R2=ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement'
sys.path.insert(0,str(R2))
from blender_local import *
P=Path(__file__).resolve().parent
def dump(n,v):
    (P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item()),encoding='utf8')
man=read(C1/'SCENE_MANIFEST.json');assert sha(man['path'])==man['sha256']
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
info=man['mapping']['R'];rig=bpy.data.objects[info['rig']];mesh=bpy.data.objects[info['mesh']];settime(sc,0)
print('MODIFIERS',[(m.name,m.type,getattr(m,'use_deform_preserve_volume',None)) for m in mesh.modifiers],flush=True)
print('SHAPES',[(k.name,k.value) for k in mesh.data.shape_keys.key_blocks] if mesh.data.shape_keys else [],flush=True)
print('BONES',[(b.name,b.parent.name if b.parent else None) for b in rig.data.bones],flush=True)
bone_names=[b.name for b in rig.data.bones];bn={n:i for i,n in enumerate(bone_names)}
native=np.array([list(v.co) for v in mesh.data.vertices]);weights=np.zeros((len(native),len(bone_names)))
for i,v in enumerate(mesh.data.vertices):
    for g in v.groups:
        n=mesh.vertex_groups[g.group].name
        if n in bn:weights[i,bn[n]]=g.weight
rois=read(R3/'LOCAL_SKIN_ROI.json');ids=sorted(set(v for d in rois for v in rois[d]['vertices'])|{r['mesh_vertex'] for r in c.MARKERS['R']})
times=np.array([3.729,3.75,3.825,3.85,3.867])
R=[];Q=[];V=[];keyangles=[];BAS=[];corrected=[]
for t in times:
    settime(sc,float(t));R.append(np.array(rig.matrix_world));V.append(mesh_pose(mesh)[0][ids]);Q.append([list(b.rotation_quaternion) for b in rig.pose.bones]);BAS.append([np.array(b.matrix) for b in rig.pose.bones]);keyangles.append([bpy.data.objects[man['key_pivots'][str(k['key_index'])]].rotation_euler.x if str(k['key_index']) in man['key_pivots'] else 0 for k in c.KEYS])
    # Capture shape-driven pre-armature coordinates without modifying modifiers or weights.
    if mesh.data.shape_keys:
        sk=mesh.data.shape_keys;vs=native.copy()
        for k in sk.key_blocks:
            if k==sk.reference_key or k.value==0:continue
            delta=np.array([list(v.co) for v in k.data])-np.array([list(v.co) for v in k.relative_key.data]);vs+=k.value*delta
        corrected.append(vs[ids])
    else:corrected.append(native[ids])
np.savez_compressed(P/'LOCAL_MODEL.npz',ids=ids,rest_vertices=native[ids],weights=weights[ids],rest_matrices=np.array([np.array(b.matrix_local) for b in rig.data.bones]),parents=[bn[b.parent.name] if b.parent else -1 for b in rig.data.bones],mesh_to_rig=np.array(rig.matrix_world.inverted()@mesh.matrix_world),times=times,rig_world=R,quat=Q,actual_skin=V,pose_matrices=BAS,key_angles=keyangles,corrected_rest=corrected)
dump('LOCAL_MODEL_MANIFEST.json',dict(bone_names=bone_names,rois=rois,ids=ids,modifiers=[dict(name=m.name,type=m.type,preserve_volume=getattr(m,'use_deform_preserve_volume',None)) for m in mesh.modifiers],markers=c.MARKERS['R'],baseline=man,source_R3='Read-only diagnosis reused',new_dynamic_candidates=0))
print('EXPORTED_LOCAL_MODEL',len(ids),'vertices',len(times),'saved source poses',flush=True)
