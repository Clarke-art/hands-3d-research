import bpy,json,sys,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2]
paths={
 'NATIVE':'production_spec/stage4_blender/stage4a_r2/RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend',
 'RSSF':'production_spec/stage4_blender/stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend',
 'R2':'production_spec/stage5_production_rig/stage5a_r2/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2.blend',
 'R2A':'production_spec/stage5_production_rig/stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend'}
result={}
for key,rel in paths.items():
 p=ROOT/rel;h=hashlib.sha256(p.read_bytes()).hexdigest()
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False)
 ob=bpy.data.objects['Hand  - Realistic'];me=ob.data;mw=ob.matrix_world
 row={'path':rel,'sha256':h,'matrix_world':[list(x) for x in mw],'vertices_world_m':[list(<REDACTED_EMAIL>) for v in me.vertices],
 'edges':[list(e.vertices) for e in me.edges],'faces':[list(f.vertices) for f in me.polygons],
 'face_normals_world':[list((mw.to_3x3().inverted().transposed()@f.normal).normalized()) for f in me.polygons],
 'material_indices':[f.material_index for f in me.polygons]}
 rig=bpy.data.objects.get('RIGHT_HAND_PRODUCTION_RIG')
 if rig:
  row['rig_matrix_world']=[list(x) for x in rig.matrix_world]
  row['bones']={b.name:{'head_world_m':list(<REDACTED_EMAIL>_local),'tail_world_m':list(<REDACTED_EMAIL>_local),
   'head_local_m':list(b.head_local),'tail_local_m':list(b.tail_local),'matrix_local':[list(x) for x in b.matrix_local],
   'parent':b.parent.name if b.parent else None,'use_connect':b.use_connect,'use_deform':b.use_deform} for b in rig.data.bones}
  # Reading edit-bone roll only. No slot assignment and no save operation.
  bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
  for b in rig.data.edit_bones:row['bones'][b.name]['edit_roll_rad']=float(b.roll)
  bpy.ops.object.mode_set(mode='OBJECT')
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h
 result[key]=row
(OUT/'RAW_READ_ONLY_GEOMETRY_AND_BONES.json').write_text(json.dumps(result),encoding='utf-8')
print('READ_ONLY_EXTRACTION_COMPLETE', {k:len(v['vertices_world_m']) for k,v in result.items()})
