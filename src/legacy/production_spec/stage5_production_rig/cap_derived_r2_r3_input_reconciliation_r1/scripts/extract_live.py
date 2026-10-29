import bpy,json,sys,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2]
J=json.loads((OUT/'AUTHORITY_INPUT_VERIFICATION.json').read_text(encoding='utf-8'));R={}
for key,source in [('CORRECTED','corrected_rig'),('RSSF','Stage4C_geometry'),('NATIVE','native_geometry')]:
 spec=J['sources'][source];p=ROOT/spec['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==spec['sha256']
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False);o=bpy.data.objects['Hand  - Realistic'];m=o.data
 r={'source':spec,'matrix_world':[list(x) for x in o.matrix_world],'vertices_world_m':[list(<REDACTED_EMAIL>) for v in m.vertices],'vertices_local_m':[list(v.co) for v in m.vertices],
 'edges':[list(e.vertices) for e in m.edges],'faces':[list(f.vertices) for f in m.polygons],'material_indices':[f.material_index for f in m.polygons]}
 if key=='CORRECTED':
  rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];r['rig_matrix_world']=[list(x) for x in rig.matrix_world]
  r['bones']={b.name:{'head_world_m':list(<REDACTED_EMAIL>_local),'tail_world_m':list(<REDACTED_EMAIL>_local),'head_local_m':list(b.head_local),'tail_local_m':list(b.tail_local),'matrix_local':[list(x) for x in b.matrix_local],'parent':b.parent.name if b.parent else None,'connect':b.use_connect,'deform':b.use_deform} for b in rig.data.bones}
  bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
  for b in rig.data.edit_bones:r['bones'][b.name]['roll_rad']=float(b.roll)
  bpy.ops.object.mode_set(mode='OBJECT')
 assert hashlib.sha256(p.read_bytes()).hexdigest()==spec['sha256'];R[key]=r
(OUT/'READ_ONLY_LIVE_EXTRACTION.json').write_text(json.dumps(R),encoding='utf-8')
print('EXTRACTED corrected rig + RSSF + native, READ ONLY, no save')
