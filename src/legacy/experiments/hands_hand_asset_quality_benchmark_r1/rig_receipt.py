import bpy,json,sys
import numpy as np
from pathlib import Path
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CANDIDATE_IMPORTED_UNALTERED.blend'),load_ui=False,use_scripts=False)
ob=bpy.data.objects['Avery | anatomical body'];rig=bpy.data.objects['Avery | anatomical body.rig']
w=np.zeros((len(ob.data.vertices),len(ob.vertex_groups)))
for v in ob.data.vertices:
 for g in v.groups:w[v.index,g.group]=g.weight
v=np.array([list(v.co) for v in ob.data.vertices]);uni,inv=np.unique(np.round(v,8),axis=0,return_inverse=True)
spread=0.
for k in range(len(uni)):
 ids=np.where(inv==k)[0]
 if len(ids)>1:spread=max(spread,float(np.ptp(w[ids],axis=0).max()))
rec=dict(armature_world_determinant=float(rig.matrix_world.to_3x3().determinant()),mesh_world_determinant=float(ob.matrix_world.to_3x3().determinant()),bones=len(rig.data.bones),deform_bones=sum(b.use_deform for b in rig.data.bones),joint_constraints=sum(len(b.constraints) for b in rig.pose.bones),armature_object_constraints=len(rig.constraints),object_drivers=len(rig.animation_data.drivers) if rig.animation_data else 0,shape_keys=len(ob.data.shape_keys.key_blocks) if ob.data.shape_keys else 0,weight_groups=len(ob.vertex_groups),unweighted_vertices=int(np.sum(w.sum(1)<1e-6)),weight_sum_range=[float(w.sum(1).min()),float(w.sum(1).max())],max_nonzero_influences=int(np.sum(w>1e-6,axis=1).max()),max_weight_difference_at_coincident_positions=spread,animations=len(bpy.data.actions),custom_shapes=[dict(name=o.name,scene_member=o.name in bpy.context.scene.objects) for o in bpy.data.objects if o.name=='Icosphere'],images=[i.name for i in bpy.data.images])
(OUT/'CANDIDATE_RIG_AND_SKIN_RECEIPT.json').write_text(json.dumps(rec,indent=2),encoding='utf8');print(json.dumps(rec),flush=True)
