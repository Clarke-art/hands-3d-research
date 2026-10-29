import sys
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1];C2=ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement'
sys.path.insert(0,str(C2))
from blender_local import *
P=Path(__file__).resolve().parent
man=read(C2/'SCENE_MANIFEST.json')
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False)
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc;settime(sc,1.133333333)
out=[]
for ob in sc.objects:
    if ob.type=='MESH' and ('KEY' in ob.name):
        out.append(dict(name=ob.name,hide_render=ob.hide_render,parent=ob.parent.name if ob.parent else None,vertices=len(ob.data.vertices),bounds=[list(ob.matrix_world@Vector(p)) for p in ob.bound_box]))
(P/'KEY_OBJECTS.json').write_text(json.dumps(out,indent=2))
print('KEY_COUNT',len(out),'EXAMPLES',[(o['name'],o['parent']) for o in out if any(str(m) in o['name'] for m in [68,70,73,75])])
