"""R2-only data reflection; no weight writes, solver, sculpt, export, or promotion."""
import bpy, json, math, hashlib, sys
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[1]
R2=ROOT/'production_spec/right_hand_product_baseline_r2/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2.blend'
R1=ROOT/'production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend'
CAND=OUT/'LEFT_HAND_OFFICIAL_L1_MIRROR_CANDIDATE_R1.blend'
EXPECTED=['c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0','4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):
 (OUT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf-8')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def mat(m):return [list(r) for r in m]
def err(a,b):return float(np.max(np.abs(np.array(a)-np.array(b))))
def neutral(rig):
 for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
 bpy.context.view_layer.update()
def coords(ob):
 bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
 result=np.array([list(<REDACTED_EMAIL>) for v in me.vertices]);ev.to_mesh_clear();return result
def values(ob):return {k.name:k.value for k in ob.data.shape_keys.key_blocks if k.name!='Basis'}
def reflect(v):return np.array([list(S@Vector(p)) for p in v])
def weight_vectors(ob,names):
 W=np.zeros((len(ob.data.vertices),len(names)))
 ids={g.index:names.index(g.name) for g in ob.vertex_groups}
 for v in ob.data.vertices:
  for g in v.groups:W[v.index,ids[g.group]]=g.weight
 return W
def uv_payload(me):
 return {u.name:[{str(me.loops[i].vertex_index):list(u.data[i].uv) for i in p.loop_indices} for p in me.polygons] for u in me.uv_layers}
def bone_settings(b):return {k:getattr(b,k) for k in ['use_deform','use_connect','inherit_scale','use_inherit_rotation','use_local_location','use_relative_parent']}|{'collections':sorted(c.name for c in b.collections)}
assert [sha(R2),sha(R1)]==EXPECTED
# Existing candidate is reopened for verification, never overwritten.
bpy.ops.wm.open_mainfile(filepath=str(R2),load_ui=False,use_scripts=False)
ob=next(o for o in bpy.data.objects if o.type=='MESH');rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
neutral(rig)
assert len(ob.data.vertices)==3300 and len(rig.data.bones)==21
assert not ob.data.has_custom_normals and not len(ob.data.materials)
assert len(ob.modifiers)==1 and ob.modifiers[0].type=='ARMATURE'
assert all(not len(p.constraints) for p in rig.pose.bones)
assert not len(bpy.data.actions)
T=ob.matrix_world.copy();A=rig.matrix_world.copy();assert err(mat(A),mat(Matrix.Identity(4)))==0
wrist=rig.data.bones['WRIST_R'];origin=wrist.head_local.copy();normal=wrist.matrix_local.col[0].to_3d().normalized()
S=Matrix.Identity(4)
for i in range(3):
 for j in range(3):S[i][j]=(1 if i==j else 0)-2*normal[i]*normal[j]
S.translation=origin-S.to_3x3()@origin
H=Matrix.Diagonal(Vector((-1,1,1,1)))
D=T.inverted()@S@T
names=[b.name for b in rig.data.bones];mapping={n:n[:-2]+'_L' for n in names};leftnames=[mapping[n] for n in names]
side_dist={n:float((rig.data.bones[n].head_local-origin).dot(normal)) for n in ['THUMB_CMC_R','INDEX_MCP_R','MIDDLE_MCP_R','LITTLE_MCP_R']}
assert side_dist['THUMB_CMC_R']<0 and side_dist['INDEX_MCP_R']<0 and side_dist['LITTLE_MCP_R']>0
assert abs(normal.dot(wrist.matrix_local.col[1].to_3d()))<1e-6
assert abs(normal.dot(wrist.matrix_local.col[2].to_3d()))<1e-6
plane={'status':'PASS','MIRROR_PLANE':'WRIST rest-local X=0; plane spanned by wrist longitudinal Y and palmar/dorsal Z through WRIST head','MIRROR_SPACE':'ARMATURE_DATA (rig world identity); mesh reflection conjugated into MESH_DATA','origin_armature_m':list(origin),'normal_armature':list(normal),'equation_n_dot_p_equals':float(normal.dot(origin)),'reflection_armature_matrix':mat(S),'reflection_mesh_data_matrix':mat(D),'source_mesh_world':mat(T),'source_armature_world':mat(A),'anatomical_side_projection_m':side_dist,'reason':'Existing wrist frame supplies longitudinal and palmar/dorsal axes. Thumb/index are radial and little finger is ulnar on opposite sides. Reflection preserves these two in-plane axes and reverses radial/ulnar chirality. A single asymmetric hand has no exact self-symmetry; this is its verified anatomical bilateral construction plane, not a symmetry-fit claim.','world_X_assumed':False}
dump('CANONICAL_MIRROR_PLANE_R1.json',plane)
source_bones={b.name:{'matrix':b.matrix_local.copy(),'head':b.head_local.copy(),'tail':b.tail_local.copy(),'parent':b.parent.name if b.parent else None,'settings':bone_settings(b)} for b in rig.data.bones}
source_shapes={k.name:np.array([list(v.co) for v in k.data]) for k in ob.data.shape_keys.key_blocks}
W=weight_vectors(ob,names);source_uv=uv_payload(ob.data)
source_faces=[list(p.vertices) for p in ob.data.polygons];source_edges=[list(e.vertices) for e in ob.data.edges]
smooth=[p.use_smooth for p in ob.data.polygons];sharp=[e.use_edge_sharp for e in ob.data.edges]
source_mod={'type':ob.modifiers[0].type,'preserve_volume':ob.modifiers[0].use_deform_preserve_volume,'vertex_groups':ob.modifiers[0].use_vertex_groups,'envelopes':ob.modifiers[0].use_bone_envelopes}
source_driver=read(OUT/'SOURCE_R2_INSPECTION_R1.json')['drivers']
cases=read(ROOT/'audits/right_hand_product_baseline_r2_promotion_r1/PROMOTION_IDENTITY_R1.json')['approved_six_pose_definitions']
axis=Vector(read(ROOT/'production_spec/stage6_deformation/stage6b/STAGE6B_OPPOSITION_VECTOR_AUDIT.json')['CMC_OPPOSITION_UNIT_ROTATION']['coefficients_local_XYZ']).normalized()
reference={};basis={};refvalues={};refpose={}
for c in cases:
 neutral(rig)
 if 'bone' in c:rig.pose.bones[c['bone']].rotation_quaternion=Quaternion((1,0,0),math.radians(c['applied_rotation_deg']))
 elif 'cmc_deg' in c:
  rig.pose.bones['THUMB_CMC_R'].rotation_quaternion=Quaternion(axis,math.radians(c['cmc_deg']))
  for joint,key in [('MCP','mcp_deg'),('IP','ip_deg')]:rig.pose.bones['THUMB_'+joint+'_R'].rotation_quaternion=Quaternion((1,0,0),-math.radians(c[key]))
 bpy.context.view_layer.update();cid=c['case_id'];reference[cid]=coords(ob);basis[cid]={p.name:p.matrix_basis.copy() for p in rig.pose.bones};refpose[cid]={p.name:p.matrix.copy() for p in rig.pose.bones};refvalues[cid]=values(ob)
neutral(rig)
if not CAND.exists():
 # Reflection is baked directly into every shape coordinate, preserving vertex IDs and weights.
 for k in ob.data.shape_keys.key_blocks:
  for v in k.data:v.co=<REDACTED_EMAIL>
 for i,v in enumerate(ob.data.vertices):v.co=ob.data.shape_keys.key_blocks['Basis'].data[i].co
 ob.data.flip_normals();ob.data.update()
 # Corner UVs follow vertex identities through the necessary winding reversal.
 for u in ob.data.uv_layers:
  for p in ob.data.polygons:
   for i in p.loop_indices:u.data[i].uv=source_uv[u.name][p.index][str(ob.data.loops[i].vertex_index)]
 bpy.context.view_layer.objects.active=rig;rig.select_set(True)
 bpy.ops.object.mode_set(mode='EDIT')
 for n in names:
  b=rig.data.edit_bones[n];src=source_bones[n]
  b.head=S@src['head'];b.tail=S@src['tail'];b.align_roll(S.to_3x3()@src['matrix'].col[2].to_3d())
 bpy.ops.object.mode_set(mode='OBJECT')
 for n in names:rig.data.bones[n].name=mapping[n]
 for g in ob.vertex_groups:
  if g.name in mapping:g.name=mapping[g.name]
 for f in ob.data.shape_keys.animation_data.drivers:
  for v in f.driver.variables:
   for t in v.targets:
    if t.bone_target in mapping:t.bone_target=mapping[t.bone_target]
 ob.name='LEFT_HAND_OFFICIAL_L1_MIRROR_PRODUCT_MESH';ob.data.name='LEFT_HAND_OFFICIAL_L1_MIRROR_MESH_DATA'
 rig.name='LEFT_HAND_PRODUCTION_RIG';rig.data.name='LEFT_HAND_PRODUCTION_RIG_DATA'
 ob.data.shape_keys.name='LEFT_HAND_APPROVED_MIRRORED_CORRECTIVE_KEYS_R1'
 sc=bpy.context.scene;sc.name='LEFT_HAND_CANONICAL_MIRROR_CANDIDATE_R1'
 # Replace inherited approval labels; retain actual source identity separately.
 for owner in [sc,ob]:
  for k in list(owner.keys()):del owner[k]
  for k,v in {'PHASE':'LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1','DESIGN_ONLY':True,'NOT_PRODUCTION':True,'HUMAN_APPROVAL_PENDING':True,'HUMAN_APPROVAL':'HUMAN_REVIEW_PENDING','PRODUCT_BASELINE_STATUS':'DESIGN_ONLY / HUMAN_REVIEW_PENDING','CANONICAL_SOURCE':'RIGHT_HAND_PRODUCT_BASELINE_R2','CANONICAL_SOURCE_SHA256':EXPECTED[0],'SOURCE_IDENTITY':'Official L1 / 3300 vertices','PRODUCTION_POINTER_UPDATED':False}.items():owner[k]=v
 neutral(rig);sc.frame_set(1)
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(CAND),compress=False)
# Verify saved file, not merely the in-memory build.
bpy.ops.wm.open_mainfile(filepath=str(CAND),load_ui=False,use_scripts=False)
ob=bpy.data.objects['LEFT_HAND_OFFICIAL_L1_MIRROR_PRODUCT_MESH'];rig=bpy.data.objects['LEFT_HAND_PRODUCTION_RIG'];neutral(rig)
actualW=weight_vectors(ob,leftnames);assert np.array_equal(W,actualW)
dump('WEIGHT_FIELD_MIRROR_PARITY_R1.json',{'status':'PASS','MIRRORED_WEIGHT_FIELD_IDENTITY':'EXACT_SEMANTIC_MATCH','WEIGHT_FIELD_MIRROR_PARITY':'EXACT_SEMANTIC_MIRROR_MATCH','vertices':3300,'semantic_columns':21,'stored_deform_groups':16,'TIP_zero_columns':5,'max_abs_difference':float(np.max(np.abs(W-actualW))),'source_and_candidate_float64_vector_sha256':hashlib.sha256(W.astype('<f8').tobytes()).hexdigest(),'full_vector_exact':True,'weights_recalculated_or_written':False,'mapping':'vertex i -> i; *_R -> *_L; absent TIP groups are exact zero'})
bone_rows=[]
for n in names:
 b=rig.data.bones[mapping[n]];src=source_bones[n];expected=S@src['matrix']@H
 e=err(mat(b.matrix_local),mat(expected));assert e<5e-5,(n,e)
 assert (b.head_local-S@src['head']).length<1e-6 and (b.tail_local-S@src['tail']).length<1e-6
 assert bone_settings(b)==src['settings']
 assert (b.parent.name if b.parent else None)==mapping.get(src['parent'])
 parenterr=0
 if b.parent:
  rparent=source_bones[src['parent']]['matrix'];expectedlocal=<REDACTED_EMAIL>()@src['matrix']@H
  parenterr=err(mat(b.parent.matrix_local.inverted()@b.matrix_local),mat(expectedlocal));assert parenterr<1e-4
 bone_rows.append({'right':n,'left':b.name,'max_rest_matrix_error':e,'max_parent_space_error':parenterr,'left_rest_matrix':mat(b.matrix_local),'positive_rest_determinant':b.matrix_local.to_3x3().determinant(),'settings':bone_settings(b)})
dump('BONE_SEMANTIC_MIRROR_MAP_R1.json',{'status':'PASS','precision_note':'Blender float32 head/tail subtraction at 1.4 m origin on 5 mm TIP helpers yields up to 2.6e-5 axis-component error. Endpoints are exact reflected floats; matrix tolerance 5e-5, parent/pose 1e-4; evaluated geometry bound 0.003 mm. No weight tolerance used.','bone_count':21,'TIP_helpers_non_deform':True,'rest_rule':'L = S R H; H=diag(-1,1,1,1). Local X reverses its polar direction to retain proper handed bone frames; Y and Z reflect.','pose_rule':'B_L = H B_R H; axial rotation vector (x,y,z) -> (x,-y,-z); quaternion (w,x,y,z) -> (w,x,-y,-z)','bones':bone_rows})
assert len(ob.data.vertices)==3300 and len(ob.data.polygons)==3298
for p,r in zip(ob.data.polygons,source_faces):
 got=list(p.vertices);rev=list(reversed(r));assert any(got==rev[k:]+rev[:k] for k in range(len(rev)))
assert uv_payload(ob.data)==source_uv
assert [list(e.vertices) for e in ob.data.edges]==source_edges
assert [p.use_smooth for p in ob.data.polygons]==smooth and [e.use_edge_sharp for e in ob.data.edges]==sharp
assert len(ob.data.materials)==0 and not ob.data.has_custom_normals
assert source_mod=={'type':ob.modifiers[0].type,'preserve_volume':ob.modifiers[0].use_deform_preserve_volume,'vertex_groups':ob.modifiers[0].use_vertex_groups,'envelopes':ob.modifiers[0].use_bone_envelopes}
assert ob.modifiers[0].object==rig and ob.parent==rig and err(mat(ob.matrix_world),mat(T))<1e-6
assert all(o.matrix_world.to_3x3().determinant()>0 and min(o.scale)>0 for o in [ob,rig])
dump('VERTEX_MIRROR_MAP_R1.json',{'status':'PASS','source_sha256':EXPECTED[0],'right_to_left':list(range(3300)),'left_to_right':list(range(3300)),'vertices':3300,'faces':3298,'topology_parity':True,'face_winding_reversed':True,'UV_corner_to_vertex_identity_exact':True,'material_slots_source_and_left':0,'native_smooth_sharp_flags_exact':True,'modifier_architecture_exact':True,'negative_scale_dependency':False,'data_matrix':mat(D)})
corr=[]
for k in ob.data.shape_keys.key_blocks:
 expected=np.array([list(D@Vector(v)) for v in source_shapes[k.name]])
 actual=np.array([list(v.co) for v in k.data]);e=err(expected,actual);assert e<1e-6
 delta_source=source_shapes[k.name]-source_shapes['Basis'];delta_actual=actual-np.array([list(v.co) for v in ob.data.shape_keys.key_blocks['Basis'].data])
 de=err(delta_actual,np.array([list(D.to_3x3()@Vector(v)) for v in delta_source]));assert de<1e-6
 corr.append({'name':k.name,'coordinate_error_m':e,'delta_error_m':de})
for f,src in zip(ob.data.shape_keys.animation_data.drivers,source_driver):
 assert f.driver.expression==src['expression'] and f.data_path==src['path'] and f.driver.is_valid
 for v,sv in zip(f.driver.variables,src['variables']):
  assert v.name==sv['name'] and v.type==sv['type']
  for t,st in zip(v.targets,sv['targets']):
   assert t.id==rig and t.bone_target==mapping[st['bone_target']]
   assert t.transform_type==st['transform_type']=='ROT_X' and t.transform_space==st['transform_space']=='LOCAL_SPACE' and t.rotation_mode==st['rotation_mode']=='XYZ'
dump('CORRECTIVE_MIRROR_PARITY_R1.json',{'status':'PASS','shape_keys':corr,'driver_expression_exact':True,'driver_targets_all_left':True,'driver_ROT_X_sign':'UNCHANGED under H-conjugated proper bone frames','source_driver':source_driver,'left_targets':['THUMB_CMC_L','THUMB_MCP_L'],'no_new_corrective':True,'name_note':'Corrective suffix R1 is revision 1, not right-side bone semantics; retained intentionally.','Web_note':'Standard skin+morph. Translate this existing expression to morph weights in future Web integration; Blender drivers themselves are not glTF runtime functionality. No new Blender-only deformation dependency.'})
pose_rows=[];safety=[];leftcoords={};zero=coords(ob)
E=np.array(source_edges)
def areas(V,faces):
 return np.array([sum(np.linalg.norm(np.cross(V[f[i]]-V[f[0]],V[f[i+1]]-V[f[0]]))*.5 for i in range(1,len(f)-1)) for f in faces])
zeroareas=areas(zero,source_faces)
for c in cases:
 cid=c['case_id'];neutral(rig)
 for n in names:rig.pose.bones[mapping[n]].matrix_basis=H@basis[cid][n]@H
 V=coords(ob);leftcoords[cid]=V;expected=reflect(reference[cid]);maxmm=float(np.max(np.linalg.norm(V-expected,axis=1))*1000)
 assert maxmm<.003,(cid,maxmm)
 poseerr=max(err(mat(rig.pose.bones[mapping[n]].matrix),mat(S@refpose[cid][n]@H)) for n in names);assert poseerr<1e-4
 val=values(ob);assert all(abs(val[k]-v)<2e-5 for k,v in refvalues[cid].items()),(cid,val,refvalues[cid])
 ar=areas(V,source_faces);length=np.linalg.norm(V[E[:,0]]-V[E[:,1]],axis=1)
 row={'pose':cid,'NaN_Inf':int(np.size(V)-np.isfinite(V).sum()),'degenerate_edges':int((length<=1e-12).sum()),'gross_collapsed_faces':int(((ar<=1e-12)|(ar/zeroareas<=1e-6)).sum()),'gross_tearing_topology_change':False,'min_edge_m':float(length.min()),'min_face_area_m2':float(ar.min())}
 assert row['NaN_Inf']==row['degenerate_edges']==row['gross_collapsed_faces']==0
 neutral(rig);restore=float(np.max(np.abs(coords(ob)-zero))*1000);assert restore==0
 row['ZERO_restore_mm']=restore;row['status']='PASS';safety.append(row)
 pose_rows.append({'pose':cid,'source_definition':c,'right_to_left_basis':{n:mat(H@basis[cid][n]@H) for n in names if err(mat(basis[cid][n]),mat(Matrix.Identity(4)))>1e-8},'evaluated_mirror_max_error_mm':maxmm,'bone_pose_matrix_max_error':poseerr,'right_corrective_values':refvalues[cid],'left_corrective_values':val,'status':'PASS'})
dump('POSE_MIRROR_PARITY_R1.json',{'status':'PASS','cases_count':6,'ZERO_RSSF_is_one_of_six_approved_cases':True,'no_invented_seventh_pose':True,'right_opposition_axis':list(axis),'left_opposition_axis':[axis.x,-axis.y,-axis.z],'pose_rule':'H-conjugation, not mechanical angle-name copying','poses':pose_rows})
dump('MINIMUM_SAFETY_R1.json',{'status':'PASS','checks':safety,'obvious_penetration':'PENDING_VISIBLE_INSPECTION','hidden_crossing_or_normal_dot_census_performed':False,'Web_architecture':'mesh + 21 bones / 16 deform + 1 mirrored corrective morph; driver logic recorded for later translation','no_export':True})
dump('FINAL_ASSET_PROTECTION_R1.json',{'RIGHT_R2_UNCHANGED':sha(R2)==EXPECTED[0],'RIGHT_R1_UNCHANGED':sha(R1)==EXPECTED[1],'R2_SHA256':sha(R2),'R1_SHA256':sha(R1),'LEFT_HAND_CANDIDATE_SHA256':sha(CAND),'production_pointer_modified':False,'candidate_status':'DESIGN_ONLY / HUMAN_REVIEW_PENDING'})
# Read-only render payload from reopened candidate. All evidence cameras/scenes remain unsaved.
np.savez_compressed(OUT/'render_geometry.npz',**{f'R_{k}':v for k,v in reference.items()},**{f'L_{k}':v for k,v in leftcoords.items()})
dump('RENDER_INPUT_R1.json',{'right_faces':source_faces,'left_faces':[list(p.vertices) for p in ob.data.polygons],'smooth':smooth,'cases':[c['case_id'] for c in cases],'source_material_slots':0,'plane':plane})
print('BUILD_AND_REOPEN_PARITY_PASS',sha(CAND),flush=True)
