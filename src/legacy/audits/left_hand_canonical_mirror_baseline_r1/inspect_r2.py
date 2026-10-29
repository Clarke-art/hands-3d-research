import bpy,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'production_spec/right_hand_product_baseline_r2/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2.blend'),load_ui=False,use_scripts=False)
def mat(m):return [list(r) for r in m]
out={'objects':[],'bones':[],'drivers':[],'actions':[a.name for a in bpy.data.actions]}
for o in bpy.data.objects:
 d={'name':o.name,'type':o.type,'matrix_world':mat(o.matrix_world),'parent':o.parent.name if o.parent else None,'properties':str(dict(o.items())),'constraints':[c.type for c in o.constraints]}
 if o.type=='MESH':
  d.update(vertices=len(o.data.vertices),faces=len(o.data.polygons),bounds=[list(v) for v in o.bound_box],uv=[u.name for u in o.data.uv_layers],custom_normals=o.data.has_custom_normals,modifiers=[{'name':m.name,'type':m.type,'object':getattr(getattr(m,'object',None),'name',None)} for m in o.modifiers],groups=[g.name for g in o.vertex_groups],materials=[m.name for m in o.data.materials],shapes=[{'name':k.name,'value':k.value,'vertex_group':k.vertex_group} for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else [])
  if o.data.shape_keys and o.data.shape_keys.animation_data:
   for f in o.data.shape_keys.animation_data.drivers:
    out['drivers'].append({'path':f.data_path,'expression':f.driver.expression,'variables':[{'name':v.name,'type':v.type,'targets':[{'id':getattr(t.id,'name',None),'bone_target':t.bone_target,'transform_type':t.transform_type,'transform_space':t.transform_space,'rotation_mode':t.rotation_mode,'data_path':t.data_path} for t in v.targets]} for v in f.driver.variables]})
 if o.type=='ARMATURE':
  for b in o.data.bones:
   p=o.pose.bones[b.name]
   out['bones'].append({'name':b.name,'head':list(b.head_local),'tail':list(b.tail_local),'matrix':mat(b.matrix_local),'parent':b.parent.name if b.parent else None,'deform':b.use_deform,'rotation_mode':p.rotation_mode,'constraints':[c.type for c in p.constraints],'props':str(dict(b.items()))})
 out['objects'].append(d)
(OUT/'SOURCE_R2_INSPECTION_R1.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
