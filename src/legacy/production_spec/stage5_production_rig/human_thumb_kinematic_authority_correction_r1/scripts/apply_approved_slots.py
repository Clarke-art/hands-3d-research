import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
AUTH=read(OUT/'THUMB_DISTAL_IP_TIP_KINEMATIC_CORRECTION_AUTHORITY_R1.json')
INPUT=ROOT/AUTH['input_rig_path'];OUTPUT=ROOT/AUTH['corrected_rig_path'];S=AUTH['slots'];ALLOWED={'THUMB_IP_R.tail','THUMB_IP_R.roll','THUMB_TIP_R.head','THUMB_TIP_R.tail','THUMB_TIP_R.roll'}
assert not OUTPUT.exists() and sha(INPUT)==AUTH['input_rig_sha256']
assert AUTH['status']=='HUMAN_APPROVED'
def canon(d):return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
assert canon({k:v for k,v in AUTH.items() if k!='combined_authority_hash'})==AUTH['combined_authority_hash']
bpy.ops.wm.open_mainfile(filepath=str(INPUT),load_ui=False)
rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];mesh=bpy.data.objects['Hand  - Realistic'];original_active=bpy.context.view_layer.objects.active
selection={o.name:o.select_get() for o in bpy.context.view_layer.objects}
def snapshot():
 bones={}
 for b in rig.data.bones:
  bones[b.name]={'head_local_m':list(b.head_local),'tail_local_m':list(b.tail_local),'head_world_m':list(<REDACTED_EMAIL>_local),'tail_world_m':list(<REDACTED_EMAIL>_local),'matrix_local':[list(r) for r in b.matrix_local],
  'parent':b.parent.name if b.parent else None,'use_connect':bool(b.use_connect),'use_deform':bool(b.use_deform),'inherit_scale':b.inherit_scale,'use_inherit_rotation':b.use_inherit_rotation,'use_local_location':b.use_local_location,
  'collections':sorted(c.name for c in b.collections),'custom_properties':{k:str(b[k]) for k in b.keys()},'pose_location':list(rig.pose.bones[b.name].location),'pose_rotation_mode':rig.pose.bones[b.name].rotation_mode,
  'pose_rotation_quaternion':list(rig.pose.bones[b.name].rotation_quaternion),'pose_rotation_euler':list(rig.pose.bones[b.name].rotation_euler),'pose_scale':list(rig.pose.bones[b.name].scale)}
 m=mesh.data
 geo={'vertices_local_m':[list(v.co) for v in m.vertices],'edges':[list(e.vertices) for e in m.edges],'faces':[list(p.vertices) for p in m.polygons],
 'vertex_groups':[g.name for g in mesh.vertex_groups],'weights':[[[g.group,g.weight] for g in v.groups] for v in m.vertices],'UV':{l.name:[list(u.uv) for u in l.data] for l in m.uv_layers},'material_assignment':[p.material_index for p in m.polygons],
 'materials':[mat.name if mat else None for mat in m.materials],'smooth_flags':[p.use_smooth for p in m.polygons],
 'shape_keys':{k.name:[list(p.co) for p in k.data] for k in m.shape_keys.key_blocks} if m.shape_keys else {},'mesh_parent':mesh.parent.name if mesh.parent else None,'modifiers':[[mo.name,mo.type] for mo in mesh.modifiers]}
 return {'bones':bones,'rig_matrix_world':[list(r) for r in rig.matrix_world],'rig_location':list(rig.location),'rig_rotation_euler':list(rig.rotation_euler),'rig_scale':list(rig.scale),
 'mesh_matrix_world':[list(r) for r in mesh.matrix_world],'object_transforms':{o.name:[list(r) for r in o.matrix_world] for o in bpy.data.objects},'geometry':geo,'geometry_signature':canon(geo),'runtime':bpy.app.version_string}
BEFORE=snapshot()
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
E=rig.data.edit_bones
edit_before={b.name:{'head':list(b.head),'tail':list(b.tail),'roll':float(b.roll),'parent':b.parent.name if b.parent else None,'use_connect':b.use_connect,'use_deform':b.use_deform} for b in E}
for n,r in edit_before.items():BEFORE['bones'][n]['roll_rad']=r['roll'];BEFORE['bones'][n]['roll_deg']=math.degrees(r['roll'])
assert edit_before['THUMB_IP_R']['head']==S['THUMB_IP_R.head']['armature_local_m']
# These are the ONLY bone slot assignments in this script.
E['THUMB_IP_R'].tail=Vector(S['THUMB_IP_R.tail']['armature_local_m'])
E['THUMB_IP_R'].roll=S['THUMB_IP_R.roll']['value']
E['THUMB_TIP_R'].head=Vector(S['THUMB_TIP_R.head']['armature_local_m'])
E['THUMB_TIP_R'].tail=Vector(S['THUMB_TIP_R.tail']['armature_local_m'])
E['THUMB_TIP_R'].roll=S['THUMB_TIP_R.roll']['value']
edit_after={b.name:{'head':list(b.head),'tail':list(b.tail),'roll':float(b.roll),'parent':b.parent.name if b.parent else None,'use_connect':b.use_connect,'use_deform':b.use_deform} for b in E}
unauthorized_edit=[]
for n,a in edit_after.items():
 for k,v in a.items():
  if n+'.'+k not in ALLOWED and v!=edit_before[n][k]:unauthorized_edit.append({'bone':n,'slot':k,'before':edit_before[n][k],'after':v})
assert not unauthorized_edit,unauthorized_edit
bpy.ops.object.mode_set(mode='OBJECT')
AFTER=snapshot()
for n,r in edit_after.items():AFTER['bones'][n]['roll_rad']=r['roll'];AFTER['bones'][n]['roll_deg']=math.degrees(r['roll'])
protected=['rig_matrix_world','rig_location','rig_rotation_euler','rig_scale','mesh_matrix_world','object_transforms','geometry']
assert all(BEFORE[k]==AFTER[k] for k in protected)
unauthorized_object=[]
for n,a in AFTER['bones'].items():
 for k,v in a.items():
  slot={'head_local_m':'head','head_world_m':'head','tail_local_m':'tail','tail_world_m':'tail','roll_rad':'roll','roll_deg':'roll','matrix_local':'frame'}.get(k,k)
  if slot=='frame' and n in ['THUMB_IP_R','THUMB_TIP_R']:continue
  if n+'.'+slot not in ALLOWED and v!=BEFORE['bones'][n][k]:unauthorized_object.append({'bone':n,'property':k,'before':BEFORE['bones'][n][k],'after':v})
dump('PRE_SAVE_SLOT_SCOPE_VERIFICATION.json',{'authorized_edit_slot_changes':sorted(ALLOWED),'unauthorized_edit_changes':unauthorized_edit,'unauthorized_object_changes':unauthorized_object,'protected_mesh_and_objects_equal':True,'edit_before':edit_before,'edit_after':edit_after})
if unauthorized_object:
 print('FAIL_CLOSED: object-mode roundtrip changed unrelated data; no blend saved',json.dumps(unauthorized_object)[:6000]);raise RuntimeError('Unapproved object-mode drift')
for o in bpy.context.view_layer.objects:o.select_set(selection[o.name])
bpy.context.view_layer.objects.active=original_active
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT),copy=True,compress=False)
output_sha=sha(OUTPUT)
assert sha(INPUT)==AUTH['input_rig_sha256']
bpy.ops.wm.open_mainfile(filepath=str(OUTPUT),load_ui=False)
rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];mesh=bpy.data.objects['Hand  - Realistic'];SAVED=snapshot()
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for b in rig.data.edit_bones:SAVED['bones'][b.name]['roll_rad']=float(b.roll);SAVED['bones'][b.name]['roll_deg']=math.degrees(b.roll)
# No further bone assignment; no second save.
bpy.ops.object.mode_set(mode='OBJECT')
assert SAVED==AFTER,'saved/reloaded data differ'
assert sha(OUTPUT)==output_sha
dump('RIG_BEFORE_AFTER_FULL_SNAPSHOTS.json',{'before':BEFORE,'after_saved_reloaded':SAVED,'input_rig_sha256':AUTH['input_rig_sha256'],'output_rig_sha256':output_sha,'authority_combined_hash':AUTH['combined_authority_hash']})
rows=[]
for name in ['THUMB_IP_R','THUMB_TIP_R']:
 for slot in ['head','tail','roll']:
  r={'slot':name+'.'+slot,'changed_authorized':name+'.'+slot in ALLOWED}
  if slot=='roll':
   r.update(before_rad=BEFORE['bones'][name]['roll_rad'],after_rad=SAVED['bones'][name]['roll_rad'],approved_rad=S[name+'.roll']['value']);r['delta_deg']=math.degrees((r['after_rad']-r['before_rad']+math.pi)%(2*math.pi)-math.pi);r['approval_storage_error_deg']=math.degrees(r['after_rad']-r['approved_rad'])
  else:
   r.update(before_world_m=BEFORE['bones'][name][slot+'_world_m'],after_world_m=SAVED['bones'][name][slot+'_world_m'],before_local_m=BEFORE['bones'][name][slot+'_local_m'],after_local_m=SAVED['bones'][name][slot+'_local_m'],approved_world_m=S[name+'.'+slot]['world_m'],approved_local_m=S[name+'.'+slot]['armature_local_m'])
   r['delta_mm']=(Vector(r['after_world_m'])-Vector(r['before_world_m'])).length*1000;r['approval_storage_error_mm']=math.sqrt(sum((a-b)**2 for a,b in zip(r['after_world_m'],r['approved_world_m'])))*1000
  rows.append(r)
dump('THUMB_KINEMATIC_BEFORE_AFTER_SLOT_VALUES.json',{'slots':rows,'input_rig_path':AUTH['input_rig_path'],'input_rig_sha256':AUTH['input_rig_sha256'],'output_rig_path':AUTH['corrected_rig_path'],'output_rig_sha256':output_sha,'saved_reload_exact_match':True,'BLEND_FILES_WRITTEN':1})
print('APPROVED_FIVE_SLOTS_APPLIED_AND_SAVED_RELOAD_VERIFIED',output_sha)
