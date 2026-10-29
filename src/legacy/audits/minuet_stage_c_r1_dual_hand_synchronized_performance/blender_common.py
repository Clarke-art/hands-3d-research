from common import *
import bpy,math,importlib.util
import numpy as np
from mathutils import Matrix,Vector
spec=importlib.util.spec_from_file_location('readonly_identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
sys.path.insert(0,str(OLD))
import performance_core as c
def curves(action):
    return [f for l in action.layers for s in l.strips for b in s.channelbags for f in b.fcurves]
def action_payload(action,shift=0):
    return [dict(path=f.data_path,index=f.array_index,extrapolation=f.extrapolation,modifiers=[h.scalars(m) for m in f.modifiers],points=[dict(co=[round(k.co.x-shift,5),k.co.y],left=[round(k.handle_left.x-shift,5),k.handle_left.y],right=[round(k.handle_right.x-shift,5),k.handle_right.y],interpolation=k.interpolation,easing=k.easing,left_type=k.handle_left_type,right_type=k.handle_right_type) for k in f.keyframe_points]) for f in curves(action)]
def settime(sc,t):
    f=1+60*t;i=math.floor(f);sc.frame_set(i,subframe=f-i);bpy.context.view_layer.update()
def geometry(ob):
    return dict(vertices=[list(v.co) for v in ob.data.vertices],edges=[list(e.vertices) for e in ob.data.edges],faces=[list(p.vertices) for p in ob.data.polygons])
def normalize(v):
    import re
    if isinstance(v,str):return re.sub(r'\.\d{3}$','',v)
    if isinstance(v,list):return [normalize(x) for x in v]
    if isinstance(v,dict):return {k:normalize(x) for k,x in v.items()}
    return v
def hand_structure(mesh,rig):
    keys=mesh.data.shape_keys
    return digest(normalize(dict(geometry=geometry(mesh),weights=[[[mesh.vertex_groups[g.group].name,g.weight] for g in v.groups] for v in mesh.data.vertices],rest=[dict(name=b.name,parent=b.parent.name if b.parent else None,head=list(b.head_local),tail=list(b.tail_local),matrix=[list(v) for v in b.matrix_local],deform=b.use_deform) for b in rig.data.bones],modifiers=[dict(type=m.type,settings=h.scalars(m,('execution_time','is_override_data')),object=getattr(m,'object',None).name if getattr(m,'object',None) else None) for m in mesh.modifiers],shape_keys=[dict(name=k.name,relative=k.relative_key.name,coordinates=[list(v.co) for v in k.data],min=k.slider_min,max=k.slider_max) for k in keys.key_blocks],drivers=[h.driver(f) for f in keys.animation_data.drivers] if keys.animation_data else [],constraints=[dict(name=b.name,constraints=[h.scalars(x) for x in b.constraints]) for b in rig.pose.bones],rig_basis=[list(v) for v in rig.matrix_basis],mesh_basis=[list(v) for v in mesh.matrix_basis],rig_parent_inverse=[list(v) for v in rig.matrix_parent_inverse],mesh_parent_inverse=[list(v) for v in mesh.matrix_parent_inverse])))
def pose(sc,mapping,side,t):
    settime(sc,t);rt=bpy.data.objects[mapping['root']];rig=bpy.data.objects[mapping['rig']];mesh=bpy.data.objects[mapping['mesh']]
    V,_=h.coords(mesh)
    pads=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS[side]])
    return dict(root=np.array(rt.matrix_world),rig_world=np.array(rig.matrix_world),joint_basis=np.array([np.array(b.matrix_basis) for b in rig.pose.bones]),joint_quat=np.array([list(b.rotation_quaternion) for b in rig.pose.bones]),verts=V,pads=pads,skin_pads=V[[r['mesh_vertex'] for r in c.MARKERS[side]]])
def keys(sc):
    return {ki:sorted([o for o in sc.objects if o.type=='MESH' and o.get('FROZEN_KEY_INDEX')==ki],key=lambda ob:(digest(geometry(ob)),normalize(ob.name))) for ki in range(88)}
