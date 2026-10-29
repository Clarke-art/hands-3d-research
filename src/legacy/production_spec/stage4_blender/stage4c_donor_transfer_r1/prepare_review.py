import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np,math
from html import escape
from PIL import Image,ImageDraw,ImageFont
C=read(OUT/'APPLICATION_NATIVE_GEOMETRY_R1.json');G=read(DESIGN/'FORMAL_MATCHED_REVIEW_GEOMETRY_R1.json');frame=G['frame'];origin=np.array(frame['origin_world_mm']);x=np.array(frame['x']);y=np.array(frame['y']);n=np.array(frame['outward'])
labels=['SOURCE_STAGE4C_R2','APPROVED_FORMAL_CANDIDATE','APPLIED_NEW_STAGE4C_REVISION'];titles=['Source Stage4C_R2','Human-approved candidate','Applied new Stage4C revision']
base=G['stages']['CURRENT_STAGE4C_R2'];stages={k:{**base,'world_mm':v,'faces':C['faces'],'smooth_flags':C['smooth_flags']} for k,v in zip(labels,[C['source_world_mm'],C['approved_candidate_world_mm'],C['application_world_mm']])}
provenance=reuse(DESIGN/'prepare_visuals.py',['sections'],globals())
for k,s in stages.items():s['sections']=sections(np.array(s['world_mm']),s['faces'],s['roi_faces'])
assert stages[labels[1]]['sections']==stages[labels[2]]['sections']
dump('APPLICATION_MATCHED_REVIEW_GEOMETRY_R1.json',{'stages':stages,'frame':frame,'camera':G['camera'],'shape_authority':'Actual saved/reopened application native coordinates; approved candidate actual reopened coordinates; source captured from actual frozen blend.','Human_approved_design_applied_exactly':True,'production_promoted':False})
Q={'stages':{k:s['sections'] for k,s in stages.items()},'meaning':'Native plane/triangle sections at common0/60/120deg physical planes with native face IDs; approved/application sections exactly identical.','section_function_AST':provenance,'source_native_topology':ref(SOURCE)}
dump('APPLICATION_NATIVE_SECTIONS_R1.json',Q)
(OUT/'sections').mkdir(exist_ok=True)
reuse(DESIGN/'deliver.py',['plot'],globals())
for a in [0,60,120]:
 plot(a,[[(k,t,'#303b42')] for k,t in zip(labels,titles)],f'THREE_NATIVE_SECTIONS_{a}.svg')
 plot(a,[[('APPROVED_FORMAL_CANDIDATE','Human-approved formal candidate','#a24a37'),('APPLIED_NEW_STAGE4C_REVISION','Applied new Stage4C revision','#24597f')]],f'APPROVED_APPLIED_OVERLAY_{a}.svg')
# Derive the matched display-only renderer; it never edits any saved blend.
src=(DESIGN/'render.py').read_text(encoding='utf-8-sig')
src=src.replace("FORMAL_MATCHED_REVIEW_GEOMETRY_R1.json","APPLICATION_MATCHED_REVIEW_GEOMETRY_R1.json").replace("FORMAL_MATCHED_RENDER_MANIFEST_R1.json","APPLICATION_MATCHED_RENDER_MANIFEST_R1.json")
src=src.replace("primary=['CURRENT_STAGE4C_R2','OFFICIAL_L1_DONOR','TEMPORARY_FEASIBILITY_PROBE','FORMAL_AMENDMENT_CANDIDATE']","primary=['SOURCE_STAGE4C_R2','APPROVED_FORMAL_CANDIDATE','APPLIED_NEW_STAGE4C_REVISION']")
src=src.replace("'design_display_only':True","'application_display_only':True").replace("Four-column plain solid","Three-column plain solid").replace('FORMAL_RENDER','APPLICATION_RENDER')
# Omit unused feasibility smoke branch entirely to make the STOP scope concrete.
start=src.index("if '--' in sys.argv");end=src.index('for view in views:',start);src=src[:start]+src[end:]
(OUT/'render_application.py').write_text(src,encoding='utf-8')
dump('APPLICATION_RENDERER_PROVENANCE_R1.json',{'source_renderer':ref(DESIGN/'render.py'),'source_matched_frame':ref(DESIGN/'FORMAL_MATCHED_REVIEW_GEOMETRY_R1.json'),'adaptation':'Three actual source/approved/application labels + actual reopened geometry, new output names; original exact camera/lighting/display recipe retained; smoke branch omitted; no geometry modeling or saved-blend edits.','generated_renderer':ref(OUT/'render_application.py')})
print('Actual source / approved / applied matched review geometry and exact native sections prepared')
