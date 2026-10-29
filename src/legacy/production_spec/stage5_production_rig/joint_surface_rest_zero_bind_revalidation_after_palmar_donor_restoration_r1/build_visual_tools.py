from common import *
source=(APP/'render_application.py').read_text(encoding='utf-8')
head='''import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,numpy as np
from mathutils import Vector,Matrix
G=read(OUT/'MATCHED_ZERO_BIND_REVIEW_GEOMETRY_R1.json')
B=read(OUT/'CLEAN_REOPEN_NATIVE_PAYLOADS_R1.json')['R2']
assert read(OUT/'PHASE_MACHINE_RESULT_R1.json')['BIND_ZERO']=='PASS'
DESIGN=ROOT/'audits/palmar_digit_root_local_donor_shape_restoration_design_r1'
lock=read(DESIGN/'PALMAR_ROOT_HUMAN_TARGET_LOCK_R1.json');core=read(DESIGN/'PALMAR_ROOT_DEFECT_CORE_R1.json');normal=read(DESIGN/'PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json')
NAT=B['protected']['mesh'];F=G['faces'];E=[e[1] for e in NAT['edges']];cfs=set(core['face_ids']);nfs=set(normal['face_ids']);ids=core['visible_upper_box_hit_vertex_ids']
P={'baseline_world_mm':[[x*1000 for x in v] for v in G['stages']['STAGE4_RAW']['world_m']],'moved_vertex_ids':IDS}
states={k:{'vertices':[[x*1000 for x in v] for v in s['world_m']],'faces':F,'smooth':NAT['smooth_flags'],'material_indices':NAT['face_material_indices']} for k,s in G['stages'].items()}
'''
body=source[source.index('bpy.ops.wm.read_factory_settings'):source.index("for view in ['HUMAN_CAMERA','CLOSE','ALTERNATE']:")]
body=body.replace("['SOURCE_STAGE4C','APPLIED_NEW_STAGE4C_REVISION']","['STAGE4_RAW','R2_RAW']")
body=body.replace("'STATIC_RAW_CURRENT_RSSF_ONLY'","'MEASURED_RAW_OR_ACTUAL_EVALUATED_ZERO; NO_POSE_SETTERS_IN_RENDERER'")
body=body.replace("'PALMAR_APPLICATION_MATCHED_RENDER_MANIFEST_R1.json'","'PALMAR_BIND_ZERO_MATCHED_RENDER_MANIFEST_R1.json'")
tail="""
for view,kind in [('HUMAN_CAMERA','SOLID'),('CLOSE','SOLID'),('ALTERNATE','SOLID'),('CLOSE','GRAZING'),('CLOSE','FLAT_SOURCE_NATIVE'),('CLOSE','WIRE')]:
 for st in states:render(st,kind,view)
dump('PALMAR_BIND_ZERO_NATIVE_RENDER_TRIANGLES_R1.json',tris)
print('PALMAR THREE-COLUMN MATCHED RENDERS',len(records),'NO SAVES')
"""
(OUT/'render_palmar.py').write_text(head+body+tail,encoding='utf-8')
# Reuse prior passed dorsal sentinel display setup and render function only.
dorsal=(PRIOR/'render_evidence.py').read_text(encoding='utf-8')
end=dorsal.index('if not overview_only:')
dorsal=dorsal[:end]
dorsal=dorsal.replace("G=read(OUT/'MATCHED_ZERO_BIND_REVIEW_GEOMETRY_R1.json');frame=G['frame']", "G=read(OUT/'MATCHED_ZERO_BIND_REVIEW_GEOMETRY_R1.json');D=read(ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_r1/APPLICATION_MATCHED_REVIEW_GEOMETRY_R1.json');G['camera']=D['camera'];frame=D['frame']")
dorsal=dorsal.replace('MATCHED_RENDER_MANIFEST_R1.json','DORSAL_BIND_ZERO_MATCHED_RENDER_MANIFEST_R1.json')
dorsal=dorsal.replace("view=='GRAZING'", "'GRAZING' in view")
dorsal+='''\nfor view,shade,direction in [('CLOSE','FLAT',human),('CLOSE','SOURCE_NATIVE',human),('GRAZING','SOURCE_NATIVE',human)]:
 for label in G['stages']:render(label,'DORSAL_'+view,shade,origin,direction,.028)
'''
(OUT/'render_dorsal.py').write_text(dorsal,encoding='utf-8')
print('Render adapters derived from existing approved matched camera workflows; only display meshes.')
