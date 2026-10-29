"""Read-only native payload snapshots. Explicit roll reads occur last, without save or edit setters."""
import sys
sys.dont_write_bytecode=True
from common import *
import bpy
def plain(v):
 if v is None or isinstance(v,(str,int,float,bool)):return v
 if hasattr(v,'to_dict'):return {k:plain(x) for k,x in v.to_dict().items()}
 if isinstance(v,bpy.types.ID):return {'type':v.bl_rna.identifier,'name':v.name,'library':v.library.filepath if v.library else None}
 if isinstance(v,set):return sorted(v)
 try:return [plain(x) for x in v]
 except TypeError:return {'type':v.bl_rna.identifier,'name':getattr(v,'name',None)}
def props(x,omit=()):
 return {k:plain(x[k]) for k in x.keys() if k not in omit}
def rna(x,omit=(),depth=0):
 d={}
 for p in x.bl_rna.properties:
  k=p.identifier
  if k=='rna_type' or k in omit:continue
  # Runtime/derived read-only fields are captured explicitly where they are authority.
  if p.is_readonly and k not in ('type','name'):continue
  v=getattr(x,k)
  if p.type=='COLLECTION':
   if depth>0:d[k]=[rna(z,depth=depth-1) for z in v]
  else:d[k]=plain(v)
 return d
def object_payload(o):
 return {'name':o.name,'type':o.type,'data_name':o.data.name if o.data else None,
 'settings':rna(o,omit=('dimensions','bound_box','data','modifiers','constraints','vertex_groups','material_slots','pose','animation_data','matrix_world','matrix_local','matrix_basis','matrix_parent_inverse','mode','active_material','active_material_index','active_shape_key_index','hide_viewport','hide_render')),
 'matrices':{k:plain(getattr(o,k)) for k in ('matrix_world','matrix_local','matrix_basis','matrix_parent_inverse')},
 'modifiers':[rna(m,depth=2) for m in o.modifiers],
 'constraints':[rna(c,depth=2) for c in o.constraints],
 'custom_properties':props(o),
 'animation':None if o.animation_data is None else {'settings':rna(o.animation_data),'drivers':[{'path':f.data_path,'index':f.array_index,'driver':rna(f.driver,depth=2)} for f in o.animation_data.drivers]}}
def rig_payload(o):
 return {'object':object_payload(o),'armature_name':o.data.name,'armature_settings':rna(o.data,omit=('edit_bones','bones','collections','collections_all','animation_data'),depth=0),
 'custom_properties':props(o.data),
 'bone_order':[b.name for b in o.data.bones],
 'bones':{b.name:{'head_local_m':plain(b.head_local),'tail_local_m':plain(b.tail_local),'matrix_local':plain(b.matrix_local),'matrix':plain(b.matrix),
 'head_world_m':plain(<REDACTED_EMAIL>_local),'tail_world_m':plain(<REDACTED_EMAIL>_local),
 'parent':b.parent.name if b.parent else None,'children':[c.name for c in b.children],
 'settings':rna(b,omit=('color','collections')),'color':rna(b.color),'collections':[c.name for c in b.collections],'custom_properties':props(b),
 'pose':rna(o.pose.bones[b.name],omit=('matrix','matrix_basis','matrix_channel','head','tail','length','constraints','bone','custom_shape','color'),depth=0),
 'pose_constraints':[rna(c,depth=2) for c in o.pose.bones[b.name].constraints],
 'pose_custom_properties':props(o.pose.bones[b.name])} for b in o.data.bones},
 'collections':[{'name':c.name,'parent':c.parent.name if c.parent else None,'bones':[b.name for b in c.bones],'settings':rna(c),'custom_properties':props(c)} for c in o.data.collections_all]}
def material_payload(m):
 if m is None:return None
 tree=m.node_tree
 return {'name':m.name,'settings':rna(m,omit=('node_tree','animation_data'),depth=0),'custom_properties':props(m),
 'nodes':[{'type':n.bl_idname,'settings':rna(n,omit=('inputs','outputs','internal_links'),depth=1),'custom_properties':props(n),
 'inputs':[{'identifier':s.identifier,'settings':rna(s,depth=0)} for s in n.inputs],
 'outputs':[{'identifier':s.identifier,'settings':rna(s,depth=0)} for s in n.outputs]} for n in tree.nodes] if tree else [],
 'links':[[l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier] for l in tree.links] if tree else []}
def snapshot():
 candidates=[o for o in bpy.data.objects if o.type=='MESH' and len(o.data.vertices)==3416]
 assert len(candidates)==1,[o.name for o in candidates]
 o=candidates[0];me=o.data
 names={g.index:g.name for g in o.vertex_groups}
 obj=object_payload(o)
 # Only newly introduced metadata keys are excluded. Every pre-existing key is retained.
 obj['custom_properties']={k:v for k,v in obj['custom_properties'].items() if not k.startswith('GEOMETRY_PROPAGATION_')}
 mesh={'name':me.name,'counts':[len(me.vertices),len(me.edges),len(me.polygons)],
 'vertex_ids':[v.index for v in me.vertices],'edges':[[e.index,list(e.vertices)] for e in me.edges],
 'faces':[[f.index,list(f.vertices)] for f in me.polygons],'loops':[[l.index,l.vertex_index,l.edge_index] for l in me.loops],
 'face_loop_ranges':[[f.loop_start,f.loop_total] for f in me.polygons],
 'smooth_flags':[f.use_smooth for f in me.polygons],'sharp_edges':[e.use_edge_sharp for e in me.edges],
 'face_material_indices':[f.material_index for f in me.polygons],
 'UV_layers':[{'name':u.name,'active':u.active,'active_render':u.active_render,'active_clone':u.active_clone,'coords':[plain(v.uv) for v in u.data]} for u in me.uv_layers],
 'material_slots':[[s.link,s.material.name if s.material else None] for s in o.material_slots],
 'materials':[material_payload(m) for m in me.materials],
 'custom_normal_state':me.has_custom_normals,'explicit_custom_normals':[plain(n.vector) for n in me.corner_normals] if me.has_custom_normals else None,
 'attributes':[{'name':a.name,'type':a.data_type,'domain':a.domain,'values':[rna(v) for v in a.data]} for a in me.attributes if a.name!='position'],
 'shape_keys':None if me.shape_keys is None else {'settings':rna(me.shape_keys),'blocks':[{'settings':rna(k,omit=('data',)),'coords':[plain(v.co) for v in k.data]} for k in me.shape_keys.key_blocks]},
 'settings':rna(me,omit=('vertices','edges','loops','polygons','attributes','uv_layers','vertex_colors','materials','shape_keys','animation_data'),depth=0),
 'custom_properties':props(me)}
 protected={'mesh':mesh,'object':obj,'groups':[[g.index,g.name,g.lock_weight] for g in o.vertex_groups],
 'weights_exact_including_zero':[[[g.group,float(g.weight)] for g in v.groups] for v in me.vertices],
 'rigs':{r.name:rig_payload(r) for r in bpy.data.objects if r.type=='ARMATURE'},
 'other_objects':{x.name:object_payload(x) for x in bpy.data.objects if x!=o and x.type!='ARMATURE'}}
 return {'object_name':o.name,'coordinates_local_m':[plain(v.co) for v in me.vertices],
 'coordinates_world_m':[plain(<REDACTED_EMAIL>) for v in me.vertices],
 'protected':protected,'positive_weight_vectors':[{names[g.group]:float(g.weight) for g in v.groups if g.weight>0} for v in me.vertices]}
def read_rolls_last():
 """Enter EDIT only to read native EditBone.roll; no setters, exit, or save afterwards."""
 rigs=[o for o in bpy.data.objects if o.type=='ARMATURE']
 assert len(rigs)<=1
 if not rigs:return {}
 rig=rigs[0]
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.object.mode_set(mode='EDIT')
 return {rig.name:{b.name:float(b.roll) for b in rig.data.edit_bones}}
def load(p):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
