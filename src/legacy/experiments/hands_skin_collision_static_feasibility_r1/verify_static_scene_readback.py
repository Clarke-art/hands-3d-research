import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
import bpy
O=Path(__file__).resolve().parent;F=json.loads((O/'STATIC_POSE_FEASIBILITY.json').read_text());bpy.ops.wm.open_mainfile(filepath=F['diagnostic_blend'],load_ui=False,use_scripts=False)
rows=[]
for test in F['tests']:
 for attempt in test['attempts']:
  sc=bpy.data.scenes[attempt['scene']];animated=[o.name for o in sc.objects if o.animation_data and o.animation_data.action];assert not animated,(sc.name,animated);rows.append(dict(scene=sc.name,bound_object_actions=0,static_only=True))
(O/'DIAGNOSTIC_BLEND_READBACK.json').write_text(json.dumps(dict(scenes=rows,new_keyframes_inserted=0,source_animation_datablocks_only_as_unbound_reference=True),indent=2)+'\n',encoding='utf8');print('STATIC_BLEND_READBACK_PASS',len(rows))
