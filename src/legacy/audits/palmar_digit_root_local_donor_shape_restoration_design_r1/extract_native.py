import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
from mathutils import Matrix
assert sha(CURRENT)==EXPECTED_CURRENT
prov=payload_helpers(globals())
bpy.ops.wm.open_mainfile(filepath=str(CURRENT),load_ui=False,use_scripts=False)
s=snapshot();assert not s['protected']['groups'] and not s['protected']['rigs']
assert s['protected']['mesh']['counts']==[3416,6828,3414]
dump('CURRENT_STAGE4C_NATIVE_SNAPSHOT_R1.json',s)
old=read(SOURCE/'RAW_SOURCE_GEOMETRY.json')['stages'];stages={}
for label in ['OFFICIAL_L1','STAGE2_L1','STAGE4A_R2_BASE','STAGE4A_R2']:
 path=ROOT/old[label]['input']['path'];assert sha(path)==old[label]['input']['sha256']
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);ob=bpy.data.objects['Hand  - Realistic'];me=ob.data;eo=None
 if label.endswith('L1'):
  next(m for m in ob.modifiers if m.type=='MULTIRES').levels=1
  bpy.context.view_layer.update();eo=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=eo.to_mesh()
 orient=Matrix.Diagonal((1.,-1.,-1.)) if label.endswith('L1') else Matrix.Identity(3)
 row={'local_m':[list(v.co) for v in me.vertices],'canonical_world_m':[list(ob.matrix_world@(<REDACTED_EMAIL>)) for v in me.vertices],'edges':[list(e.vertices) for e in me.edges],'faces':[list(p.vertices) for p in me.polygons],'smooth':[p.use_smooth for p in me.polygons],'materials':[p.material_index for p in me.polygons],'matrix_world':[list(r) for r in ob.matrix_world],'input':ref(path)}
 for k in row:
  if k!='input':assert row[k]==old[label][k],(label,k,'saved witness differs')
 stages[label]=row
 if eo:eo.to_mesh_clear()
 assert sha(path)==row['input']['sha256']
 print('Read-only independent actual source extraction',label,flush=True)
assert all(stages['OFFICIAL_L1'][k]==stages['STAGE2_L1'][k] for k in ['local_m','canonical_world_m','edges','faces'])
dump('INDEPENDENT_DONOR_HISTORICAL_NATIVE_INPUTS_R1.json',{'stages':stages,'canonical_donor':'OFFICIAL_L1','Stage2_equivalence_witness_only':True,'source_blend_saves':0,'runtime':bpy.app.version_string,'payload_helper_AST':prov})
