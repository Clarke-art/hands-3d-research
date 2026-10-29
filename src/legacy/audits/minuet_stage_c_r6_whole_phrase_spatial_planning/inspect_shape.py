import sys,json
from pathlib import Path
import bpy,numpy as np
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
man=json.loads((P.parent/'minuet_stage_c_r1_dual_hand_synchronized_performance/SCENE_MANIFEST.json').read_text())
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False)
ob=bpy.data.objects[man['mapping']['R']['mesh']];sk=ob.data.shape_keys
rows=[]
for k in sk.key_blocks:
    rows.append(dict(name=k.name,mute=k.mute,vertex_group=k.vertex_group,
        max_delta_m=max((v.co-r.co).length for v,r in zip(k.data,k.relative_key.data))))
drivers=[]
for f in sk.animation_data.drivers:
    drivers.append(dict(path=f.data_path,expression=f.driver.expression,variables=[dict(name=v.name,type=v.type,targets=[dict(bone=t.bone_target,transform_type=t.transform_type,transform_space=t.transform_space,data_path=t.data_path) for t in v.targets]) for v in f.driver.variables]))
(P/'SHAPE_DRIVER_READONLY.json').write_text(json.dumps(dict(keys=rows,drivers=drivers),indent=2))
np.savez_compressed(P/'SHAPE_DELTA.npz',delta=np.array([list(v.co-r.co) for v,r in zip(sk.key_blocks[1].data,sk.key_blocks[1].relative_key.data)]))
print('SHAPE_METADATA',rows,drivers,flush=True)
