import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
import bpy
P=Path(__file__).resolve().parent;C1=P.parent/'minuet_stage_c_lightweight_animation_poc_r1'
man=json.loads((C1/'SCENE_MANIFEST.json').read_text())
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def assets(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc;sc.frame_set(1)
 out={}
 for o in sc.objects:
  row=dict(type=o.type,data=o.data.name if o.data else None,parent=o.parent.name if o.parent else None,parent_type=o.parent_type,parent_bone=o.parent_bone,visible=not o.hide_render)
  if o.type=='MESH':
   row['vertices']=[list(v.co) for v in o.data.vertices];row['faces']=[list(f.vertices) for f in o.data.polygons]
   row['weights']=[[(g.group,g.weight) for g in v.groups] for v in o.data.vertices];row['groups']=[g.name for g in o.vertex_groups]
   row['modifiers']=[dict(name=m.name,type=m.type,object=getattr(getattr(m,'object',None),'name',None),preserve_volume=getattr(m,'use_deform_preserve_volume',None),show_render=m.show_render) for m in o.modifiers]
   if o.data.shape_keys:
    sk=o.data.shape_keys;row['shape_keys']={k.name:[list(v.co) for v in k.data] for k in sk.key_blocks}
    row['drivers']=[dict(path=d.data_path,index=d.array_index,expression=d.driver.expression,variables=[dict(name=v.name,type=v.type,targets=[dict(id=getattr(t.id,'name',None),bone=t.bone_target,path=t.data_path,transform_type=t.transform_type,space=t.transform_space) for t in v.targets]) for v in d.driver.variables]) for d in sk.animation_data.drivers] if sk.animation_data else []
  if o.type=='ARMATURE':row['bones']={b.name:dict(matrix=[list(v) for v in b.matrix_local],parent=b.parent.name if b.parent else None,use_deform=b.use_deform) for b in o.data.bones}
  if o.type=='CAMERA':row['camera']=dict(matrix=[list(v) for v in o.matrix_world],type=o.data.type,ortho=o.data.ortho_scale,lens=o.data.lens)
  out[o.name]=digest(row)
 return out
source=assets(man['path']);new=assets(P/'PIANO_PEDAGOGICAL_MOTION_REFINEMENT_R1_DESIGN_ONLY.blend')
changed=[k for k in source.keys()|new.keys() if source.get(k)!=new.get(k)]
(P/'SCENE_ASSET_IDENTITY.json').write_text(json.dumps(dict(pass_=not changed,source_object_count=len(source),candidate_object_count=len(new),changed=changed,scope='All scene object names/types/parent bindings; native mesh topology/coordinates/weights/groups, shape-key coordinates/drivers, armature rest bones, render modifiers and original cameras',source_digest=digest(source),candidate_digest=digest(new)),indent=2),encoding='utf8')
assert not changed,changed
print('SCENE_NATIVE_ASSET_IDENTITY_PASS',len(source),flush=True)
