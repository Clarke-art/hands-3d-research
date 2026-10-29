"""Position-excluding payload snapshots. No geometry/normal/weight setters."""
import sys
sys.dont_write_bytecode=True
from common import *
import bpy
ns={'bpy':bpy}
PAYLOAD_SOURCE=reuse(ROOT/'production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_after_approval_r1/blender_extract.py',['mesh_payload','rig_payload'],ns)
def plain(v):
 if hasattr(v,'to_dict'):return {k:plain(z) for k,z in v.to_dict().items()}
 if isinstance(v,dict):return {k:plain(z) for k,z in v.items()}
 if isinstance(v,(str,int,float,bool)) or v is None:return v
 if isinstance(v,bpy.types.ID):return {'type':type(v).__name__,'name':v.name}
 try:return [plain(z) for z in v]
 except TypeError:return str(v)
def protected(ob):
 me=ob.data;p=ns['mesh_payload'](ob)
 for k in ['positions_local_m','positions_world_mm']:p.pop(k)
 p.update({'vertex_count':len(me.vertices),'edge_count':len(me.edges),'face_count':len(me.polygons),'loops':[[l.vertex_index,l.edge_index] for l in me.loops],
 'face_loop_ranges':[[f.loop_start,f.loop_total] for f in me.polygons],'smooth_flags':[f.use_smooth for f in me.polygons],
 'sharp_edges':[e.use_edge_sharp for e in me.edges],'custom_normal_state':me.has_custom_normals,
 'explicit_custom_normals':[list(c.vector) for c in me.corner_normals] if me.has_custom_normals else None,
 'groups':[[g.index,g.name,g.lock_weight] for g in ob.vertex_groups],
 'weights_exact_including_zero':[[[g.group,float(g.weight)] for g in v.groups] for v in me.vertices],
 'shape_key_payload':{k.name:[list(v.co) for v in k.data] for k in me.shape_keys.key_blocks} if me.shape_keys else None,
 'object_custom_properties':{k:plain(ob[k]) for k in ob.keys() if not k.startswith('AMENDMENT_')},
 'mesh_custom_properties':{k:plain(me[k]) for k in me.keys()},
 'armatures':{o.name:ns['rig_payload'](o) for o in bpy.data.objects if o.type=='ARMATURE'},
 'material_nodes':{m.name:{'diffuse':list(m.diffuse_color),'use_nodes':m.use_nodes,'nodes':[{'name':n.name,'type':n.bl_idname,'inputs':{i.identifier:plain(i.default_value) for i in n.inputs if hasattr(i,'default_value')}} for n in m.node_tree.nodes] if m.node_tree else [],'links':[[l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier] for l in m.node_tree.links] if m.node_tree else []} for m in me.materials if m}})
 return p
