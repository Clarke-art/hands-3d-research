import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
bpy.ops.wm.open_mainfile(filepath=str(CAND),load_ui=False,use_scripts=False)
ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
mw=rig.matrix_world
bones={}
for b in rig.data.bones:
 bones[b.name]={'head_world_mm':list((<REDACTED_EMAIL>_local)*1000),'tail_world_mm':list((<REDACTED_EMAIL>_local)*1000),'frame_world':[(mw.to_3x3()@b.matrix_local.to_3x3().col[j]).normalized()[:] for j in range(3)],'parent':b.parent.name if b.parent else None,'use_connect':b.use_connect,'use_deform':b.use_deform}
dump('FROZEN_RIG_FRAME_EXTRACTION_R3.json',{'source':ref(CAND),'bone_count':len(bones),'bones':bones,'geometry_source':ref(ROOT/'production_spec/stage4_blender/stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend'),'read_only':True,'production_saves':0,'UV_hash':digest([[list(e.uv) for e in uv.data] for uv in ob.data.uv_layers]),'materials':[m.name for m in ob.data.materials],'material_assignment':[p.material_index for p in ob.data.polygons],'face_smooth':[p.use_smooth for p in ob.data.polygons],'has_custom_normals':ob.data.has_custom_normals,'edges_sharp':[e.use_edge_sharp for e in ob.data.edges]})
print('FRAMES_EXTRACTED',len(bones),flush=True)
