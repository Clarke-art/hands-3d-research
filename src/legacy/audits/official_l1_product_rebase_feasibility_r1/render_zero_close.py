import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
G=read(OUT/'STATIC_BIND_AND_REBASE_R1.json')
r=Renderer(G['cameras'],'final_renders')
r.sc.display.shading.shadow_intensity=0.
r.draw('REBASED','ZERO',[Vector(v) for v in G['rebased_zero_world_m']],[tuple(f) for f in G['faces']],['FINGER_ROOTS_CLOSE'])
r.dispose()
dump('ZERO_CLOSE_DISPLAY_MANIFEST_R1.json',{'renders':r.records,'display_only':True,'asset_opened_or_saved':False})
