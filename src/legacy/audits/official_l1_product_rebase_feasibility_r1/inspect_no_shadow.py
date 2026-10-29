import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
G=read(OUT/'STATIC_BIND_AND_REBASE_R1.json')
ob,rig=open_candidate();renderer=Renderer(G['cameras'],'no_cast_shadow_preview')
print('SHADOW_SETTING_AVAILABLE',hasattr(renderer.sc.display.shading,'shadow_intensity'),flush=True)
renderer.sc.display.shading.shadow_intensity=0.
for c in cases():
    if c['case_id'] not in ['INDEX_MCP_45','THUMB_MCP_45','CMC_OPP_30','FULL_OPP_L3']:continue
    apply_case(rig,c);V,F=evaluate(ob,ob.matrix_world)
    renderer.draw('REBASED',c['case_id'],V,F,['THUMB_WEB_OBLIQUE','THENAR_CLOSE'] if c['case_id']!='INDEX_MCP_45' else ['FINGER_ROOTS_CLOSE'])
renderer.dispose();reset_pose(rig)
print('NO_SHADOW_VISIBLE_PREVIEW_READY',flush=True)
