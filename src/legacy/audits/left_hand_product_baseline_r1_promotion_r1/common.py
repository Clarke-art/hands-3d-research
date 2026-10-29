"""Read-only identity and smoke helpers. No mesh, rest, weight or driver writers."""
import sys,json,hashlib,math
from pathlib import Path
sys.dont_write_bytecode=True
import bpy
import numpy as np
from mathutils import Matrix
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
HISTORY=ROOT/'audits/left_hand_canonical_mirror_baseline_r1'
CAND=HISTORY/'LEFT_HAND_OFFICIAL_L1_MIRROR_CANDIDATE_R1.blend'
DESTDIR=ROOT/'production_spec/left_hand_product_baseline_r1'
DEST=DESTDIR/'LEFT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend'
POINTER=ROOT/'production_spec/LEFT_HAND_PRODUCT_BASELINE.json'
RIGHT_POINTER=ROOT/'production_spec/RIGHT_HAND_PRODUCT_BASELINE.json'
EXPECTED_CAND='c31190de326c5af44baf876f4066a130c8a9fef42d6c71c0071de5f63f0f2750'
RIGHTS={ROOT/'production_spec/right_hand_product_baseline_r2/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2.blend':'c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0',ROOT/'production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend':'4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2'}
PHASE='LEFT_HAND_PRODUCT_BASELINE_R1_PROMOTION_R1'
AUDIT_KEYS={'PHASE','DESIGN_ONLY','NOT_PRODUCTION','HUMAN_APPROVAL_PENDING','HUMAN_APPROVAL','PRODUCT_BASELINE_STATUS','PRODUCTION_POINTER_UPDATED','PRODUCT_BASELINE_SOURCE_SHA256','PRODUCTION_PROMOTION'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def plain(v):
 if v is None or isinstance(v,(str,bool,int)):return v
 if isinstance(v,float):return v if math.isfinite(v) else str(v)
 if isinstance(v,bpy.types.ID):return {'ID_type':v.bl_rna.identifier,'name':v.name,'library':v.library.filepath if v.library else None}
 if hasattr(v,'to_dict'):return {k:plain(x) for k,x in v.to_dict().items()}
 if hasattr(v,'to_list'):return plain(v.to_list())
 return [plain(x) for x in v]
def dump(n,v):
 (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf-8')
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def props(o,exclude=()):return {k:plain(v) for k,v in o.items() if k not in exclude}
def scalars(o,exclude=()):
 result={}
 for p in o.bl_rna.properties:
  k=p.identifier
  if k in exclude or k=='rna_type':continue
  if p.type in {'BOOLEAN','INT','FLOAT','STRING','ENUM'}:result[k]=plain(getattr(o,k))
 return result
def chosen(o,keys):return {k:plain(getattr(o,k)) for k in keys}
def mat(m):return [list(r) for r in m]
def animation(a):
 if a is None:return None
 return {'action':plain(a.action),'use_nla':a.use_nla,'nla_tracks':len(a.nla_tracks),'drivers':[driver(f) for f in a.drivers]}
def driver(f):return {'settings':scalars(f,('is_valid',)),'driver':scalars(f.driver,('is_valid',)),'variables':[{'settings':scalars(v),'targets':[scalars(t)|{'id':plain(t.id)} for t in v.targets]} for v in f.driver.variables],'modifiers':[scalars(m) for m in f.modifiers],'keyframes':[scalars(k) for k in f.keyframe_points]}
def object_payload(o,exclude=()):
 return {'name':o.name,'data':plain(o.data),'props':props(o,exclude),'state':chosen(o,['location','rotation_mode','rotation_euler','rotation_quaternion','rotation_axis_angle','scale','delta_location','delta_rotation_euler','delta_rotation_quaternion','delta_scale','matrix_world','matrix_basis','matrix_local','matrix_parent_inverse','parent_type','parent_bone','hide_render','hide_viewport','hide_select','display_type','show_in_front','color']),'parent':plain(o.parent),'constraints':[scalars(c) for c in o.constraints],'animation':animation(o.animation_data),'collections':sorted(c.name for c in o.users_collection)}
def weights(ob,rig):
 names=[b.name for b in rig.data.bones];W=np.zeros((len(ob.data.vertices),len(names)),dtype='<f8');groups={g.index:names.index(g.name) for g in ob.vertex_groups}
 for v in ob.data.vertices:
  for g in v.groups:W[v.index,groups[g.group]]=g.weight
 return W
def core(ob,rig):
 me=ob.data;keys=me.shape_keys
 return {
 'mesh_object':object_payload(ob,AUDIT_KEYS),
 'armature_object':object_payload(rig),
 'mesh_identity':{'name':me.name,'props':props(me),'vertex_count':len(me.vertices),'face_count':len(me.polygons),'settings':chosen(me,['use_mirror_x','use_mirror_y','use_mirror_z','use_mirror_topology','use_auto_texspace','texspace_location','texspace_size'])},
 'coordinates_vertex_order':[[v.index,list(v.co)] for v in me.vertices],
 'topology_face_winding':{'edges':[list(e.vertices) for e in me.edges],'loops':[[l.vertex_index,l.edge_index] for l in me.loops],'polygons':[[list(p.vertices),p.loop_start,p.loop_total] for p in me.polygons]},
 'UV':[{'settings':scalars(u),'coords':[list(d.uv) for d in u.data]} for u in me.uv_layers],
 'native_shading':{'smooth':[p.use_smooth for p in me.polygons],'sharp_edges':[e.use_edge_sharp for e in me.edges],'material_indices':[p.material_index for p in me.polygons],'custom_normals':me.has_custom_normals,'corner_normals':[list(n.vector) for n in me.corner_normals],'materials':[plain(m) for m in me.materials]},
 'attributes':[{'name':a.name,'type':a.data_type,'domain':a.domain,'data':[scalars(v) for v in a.data]} for a in me.attributes],
 'groups_and_weights':{'groups':[scalars(g) for g in ob.vertex_groups],'stored_sparse_vectors':[[[g.group,g.weight] for g in v.groups] for v in me.vertices],'semantic_columns':[b.name for b in rig.data.bones],'complete_3300x21':weights(ob,rig).tolist()},
 'modifiers':[{'settings':scalars(m,('execution_time',)),'object':plain(getattr(m,'object',None))} for m in ob.modifiers],
 'rig_rest_and_semantics':{'name':rig.data.name,'props':props(rig.data),'settings':chosen(rig.data,['pose_position','display_type','show_names','show_axes','axes_position','show_bone_custom_shapes']),'collections':[{'name':c.name,'settings':scalars(c),'props':props(c),'bones':[b.name for b in c.bones]} for c in rig.data.collections_all],'bones':[{'settings':scalars(b),'props':props(b),'parent':b.parent.name if b.parent else None,'head':list(b.head_local),'tail':list(b.tail_local),'rest_matrix':mat(b.matrix_local),'local_matrix':mat(b.matrix),'collections':[c.name for c in b.collections],'color':scalars(b.color)|{'custom':scalars(b.color.custom)}} for b in rig.data.bones]},
 'pose_state':{'settings':scalars(rig.pose),'bones':[{'name':p.name,'settings':scalars(p),'props':props(p),'matrix_basis':mat(p.matrix_basis),'matrix':mat(p.matrix),'constraints':[scalars(c) for c in p.constraints],'custom_shape':plain(p.custom_shape),'color':scalars(p.color)|{'custom':scalars(p.color.custom)}} for p in rig.pose.bones]},
 'corrective_geometry_and_driver':{'name':keys.name,'settings':chosen(keys,['use_relative','eval_time']),'props':props(keys),'blocks':[{'settings':scalars(k),'relative_key':k.relative_key.name,'data':[list(v.co) for v in k.data]} for k in keys.key_blocks],'animation':animation(keys.animation_data)},
 }
def open_asset(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);bpy.context.view_layer.update()
 return bpy.data.objects['LEFT_HAND_OFFICIAL_L1_MIRROR_PRODUCT_MESH'],bpy.data.objects['LEFT_HAND_PRODUCTION_RIG']
def neutral(rig):
 for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
 bpy.context.view_layer.update()
def is_zero(rig):return all(np.array_equal(np.array(p.matrix_basis),np.eye(4)) for p in rig.pose.bones)
def coords(ob):
 bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
 V=np.array([list(<REDACTED_EMAIL>) for v in me.vertices]);F=[list(p.vertices) for p in me.polygons];ev.to_mesh_clear();return V,F
def values(ob):return {k.name:k.value for k in ob.data.shape_keys.key_blocks if k.name!='Basis'}
def apply_smoke(rig,state):
 neutral(rig)
 row=next(p for p in read(HISTORY/'POSE_MIRROR_PARITY_R1.json')['poses'] if p['pose']==state)
 # Reuse already-qualified LEFT matrices, do not recompute a mirror or a pose definition.
 for right_name,basis in row['right_to_left_basis'].items():rig.pose.bones[right_name[:-2]+'_L'].matrix_basis=Matrix(basis)
 bpy.context.view_layer.update()
def validate_protected(expected):
 failures=[p for p,s in expected.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=s]
 assert not failures,('PROTECTED_INPUT_CHANGED',failures)
def protected():
 result={p.relative_to(ROOT).as_posix():sha(p) for p in HISTORY.rglob('*') if p.is_file()}
 for folder in [ROOT/'production_spec/right_hand_product_baseline_r2',ROOT/'production_spec/right_hand_product_baseline_r1']:
  for p in folder.rglob('*'):
   if p.is_file():result[p.relative_to(ROOT).as_posix()]=sha(p)
 result[RIGHT_POINTER.relative_to(ROOT).as_posix()]=sha(RIGHT_POINTER)
 return result
