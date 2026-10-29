import bpy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
def mesh_payload(ob):
    m=ob.data
    return {'positions_local_m':[list(v.co) for v in m.vertices],
     'positions_world_mm':[list((<REDACTED_EMAIL>)*1000) for v in m.vertices],
     'edges':[list(e.vertices) for e in m.edges],'faces':[list(f.vertices) for f in m.polygons],
     'face_material_indices':[f.material_index for f in m.polygons],
     'UV_layers':{u.name:[list(x.uv) for x in u.data] for u in m.uv_layers},
     'material_slots':[None if x is None else x.name for x in m.materials],
     'matrix_world':[list(r) for r in ob.matrix_world],
     'matrix_local':[list(r) for r in ob.matrix_local],
     'matrix_parent_inverse':[list(r) for r in ob.matrix_parent_inverse],
     'location':list(ob.location),'rotation_mode':ob.rotation_mode,'rotation_euler':list(ob.rotation_euler),'scale':list(ob.scale),
     'parent':None if ob.parent is None else ob.parent.name,
     'modifiers':[{'name':m.name,'type':m.type,'show_viewport':m.show_viewport,'show_render':m.show_render,
         **({'object':None if m.object is None else m.object.name,'use_deform_preserve_volume':m.use_deform_preserve_volume,
              'use_vertex_groups':m.use_vertex_groups,'use_bone_envelopes':m.use_bone_envelopes} if m.type=='ARMATURE' else {})} for m in ob.modifiers]}
def rig_payload(rig):
    if not rig:return None
    # Roll is stored in the bone matrix; read EditBone.roll via a temporary mode switch only.
    bones={b.name:{'head_local_m':list(b.head_local),'tail_local_m':list(b.tail_local),'matrix_local':[list(r) for r in b.matrix_local],
       'head_world_mm':list((<REDACTED_EMAIL>_local)*1000),'tail_world_mm':list((<REDACTED_EMAIL>_local)*1000),
       'parent':None if b.parent is None else b.parent.name,'use_deform':b.use_deform,'use_connect':b.use_connect,
       'inherit_scale':b.inherit_scale,'use_inherit_rotation':b.use_inherit_rotation,'use_local_location':b.use_local_location,
       'collections':sorted(c.name for c in b.collections),
       'pose_location':list(rig.pose.bones[b.name].location),'pose_rotation_mode':rig.pose.bones[b.name].rotation_mode,
       'pose_rotation_quaternion':list(rig.pose.bones[b.name].rotation_quaternion),
       'pose_rotation_euler':list(rig.pose.bones[b.name].rotation_euler),'pose_scale':list(rig.pose.bones[b.name].scale)} for b in rig.data.bones}
    return {'bones':bones,'matrix_world':[list(r) for r in rig.matrix_world],
       'location':list(rig.location),'rotation_mode':rig.rotation_mode,'rotation_euler':list(rig.rotation_euler),'scale':list(rig.scale),
       'parent':None if rig.parent is None else rig.parent.name,'pose_position':rig.data.pose_position}
def weights(ob):
    names={g.index:g.name for g in ob.vertex_groups}
    return [{names[g.group]:float(g.weight) for g in v.groups if g.weight>0} for v in ob.data.vertices]
if __name__=='__main__':
    result={}
    for name,p in [('STAGE4C',STAGE4),('CORRECTED',CORRECTED),('R1B',DONOR)]:
        bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
        ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects.get('RIGHT_HAND_PRODUCTION_RIG')
        assert len(ob.data.vertices)==3416
        result[name]={'source_path':str(p.relative_to(ROOT)),'source_sha256':sha(p),
            'mesh':mesh_payload(ob),'rig':rig_payload(rig),'weights':weights(ob),'group_order':[g.name for g in ob.vertex_groups]}
        print('STATIC EXTRACT',name,flush=True)
    dump('LIVE_SOURCE_DATA_R1.json',result)
