"""Check only the selected ROI across earlier changed whole-mesh topology.
Accept an earlier match only with unique exact coordinates AND matching face cycles.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,numpy as np
R=read(OUT/'DORSAL_MCP_DENT_ROI_R1.json');L=read(OUT/'LINEAGE_RAW_READONLY_EXTRACTION.json')
path=ROOT/'production_spec/stage4_blender/RIGHT_HAND_ENGINEERING_STAGE4A_R2_BASE.blend'
bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
ob=bpy.data.objects['Hand  - Realistic'];V=np.asarray([list(<REDACTED_EMAIL>) for v in ob.data.vertices]);F=[list(f.vertices) for f in ob.data.polygons]
A=np.asarray(L['stages']['STAGE4A_R2_FROZEN']['raw_world_m']);mapping={};unresolved=[]
for i in R['vertices']:
 eq=np.where(np.all(V==A[i],axis=1))[0].tolist()
 if len(eq)==1:mapping[i]=eq[0]
 else:unresolved.append({'current_vertex_id':i,'exact_coordinate_matches':eq})
def cycle(p):
 # Preserve winding; allow only cyclic indexing, not reversal.
 return min(tuple(p[k:]+p[:k]) for k in range(len(p)))
native={cycle(p):fi for fi,p in enumerate(F)};fm={};missing=[]
for fi in R['faces']:
 p=L['topology']['faces'][fi]
 if not all(i in mapping for i in p):missing.append(fi);continue
 key=cycle([mapping[i] for i in p])
 if key in native:fm[fi]=native[key]
 else:missing.append(fi)
ok=not unresolved and not missing
dump('EARLIER_STAGE4A_BASE_LOCAL_IDENTITY_R1.json',{'status':'PASS_EXACT_LOCAL_VERTEX_AND_FACE_IDENTITY' if ok else 'UNRESOLVED_NO_EARLIER_IDENTITY_ASSUMED','input':ref(path),'whole_mesh_vertex_count':len(V),'current_mesh_vertex_count':len(A),'same_whole_mesh_topology':False,'mapping_basis':'Unique exactly equal world coordinates for all52 ROI vertices, plus equal oriented native face cycles for all36 ROI faces. Native face identity is independently verified; global index mapping is not assumed.','current_to_native_vertex_ids':{str(k):v for k,v in mapping.items()},'current_to_native_face_ids':{str(k):v for k,v in fm.items()},'unresolved_vertices':unresolved,'missing_faces':missing,'max_confirmed_ROI_coordinate_difference_mm':0 if ok else None,'earlier_ROI_geometry_matches_rendered_Stage4A_R2_exactly':ok,'armature_count':sum(m.type=='ARMATURE' for m in ob.modifiers),'blend_save_count':0,'scope_expansion':'Only one earlier engineering baseline selected ROI, not a historical qualification suite.'})
print('EARLIER_LOCAL_IDENTITY',ok,'vertices',len(mapping),'faces',len(fm),'unresolved',unresolved[:3],missing[:3])
