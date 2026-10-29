import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,numpy as np
from mathutils import Matrix
paths={
 'OFFICIAL':ROOT/'references/licenses/blender_human_base_meshes/extracted/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend',
 'STAGE2':ROOT/'production_spec/stage2_bootstrap/RIGHT_HAND_BOOTSTRAP_C1.blend',
 'STAGE4A_R2_BASE':ROOT/'production_spec/stage4_blender/RIGHT_HAND_ENGINEERING_STAGE4A_R2_BASE.blend',
 'STAGE4A_R2':ROOT/'production_spec/stage4_blender/stage4a_r2/RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend',
 'STAGE4B_RSSF':ROOT/'production_spec/stage4_blender/stage4b_rssf/RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R2.blend',
 'STAGE4C_R2':ROOT/'production_spec/stage4_blender/stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend',
 'R2_PRODUCTION':ROOT/'production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_r2/RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R2.blend'}
rows={}
def snap(ob,me,sourceframe=False):
 M=Matrix.Diagonal((1.,-1.,-1.)) if sourceframe else Matrix.Identity(3)
 W=ob.matrix_world
 return {'local_m':[list(v.co) for v in me.vertices],'canonical_world_m':[list(W@(<REDACTED_EMAIL>)) for v in me.vertices],
 'edges':[list(e.vertices) for e in me.edges],'faces':[list(f.vertices) for f in me.polygons],
 'smooth':[f.use_smooth for f in me.polygons],'materials':[f.material_index for f in me.polygons],
 'uv':{u.name:[list(x.uv) for x in u.data] for u in me.uv_layers},'counts':{'V':len(me.vertices),'E':len(me.edges),'F':len(me.polygons)},
 'matrix_world':[list(r) for r in W]}
for label,path in paths.items():
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 ob=bpy.data.objects['Hand  - Realistic']
 mods=[{'name':m.name,'type':m.type,**({k:getattr(m,k) for k in ['levels','total_levels','render_levels','sculpt_levels','show_viewport','show_render']} if m.type=='MULTIRES' else {})} for m in ob.modifiers]
 key='OFFICIAL_BASE' if label=='OFFICIAL' else 'STAGE2_BASE' if label=='STAGE2' else label
 rows[key]={**snap(ob,ob.data,label in ['OFFICIAL','STAGE2']),'input':{'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)},'modifiers':mods}
 if label in ['OFFICIAL','STAGE2']:
  m=next(m for m in ob.modifiers if m.type=='MULTIRES');m.levels=1
  bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();eo=ob.evaluated_get(dg);em=eo.to_mesh()
  rows['OFFICIAL_L1' if label=='OFFICIAL' else 'STAGE2_L1']={**snap(ob,em,True),'input':rows[key]['input'],'modifiers':mods,'evaluation':'Actual stored Multires L1 evaluated in memory, no modifier save/apply'};eo.to_mesh_clear()
 print(key,rows[key]['counts'],flush=True)
dump('RAW_SOURCE_GEOMETRY.json',{'stages':rows,'runtime':bpy.app.version_string,'blend_saves':0})
