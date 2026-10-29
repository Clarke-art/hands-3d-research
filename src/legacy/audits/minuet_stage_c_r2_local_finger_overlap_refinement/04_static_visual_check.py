import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from blender_local import *
from mathutils import Quaternion
assert not DEST.exists() and not (P/'LOCAL_CORRECTION_POLICY_LOCK.json').exists()
fit=read(P/'STATIC_FEASIBILITY.json');choice=next(r for r in fit['rows'] if r['ring_MCP_spread_delta_deg']==-6)
assert choice['target_patch_pair_sum']==0 and choice['neighbor_patch_pair_sum']==0 and choice['maximum_active_skin_gap_mm']<3 and choice['maximum_active_skin_horizontal_mm']==0
man=read(C1/'SCENE_MANIFEST.json');bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
rig=bpy.data.objects[man['mapping']['R']['rig']];bone=rig.pose.bones['RING_MCP_R'];axis=Vector(c.SETUPS['R','RING'][3]);original=rig.animation_data.action
for t in [1.05,1.40,1.80]:
    settime(sc,t);saved={b.name:b.rotation_quaternion.copy() for b in rig.pose.bones};rig.animation_data.action=None
    for phase in ['BEFORE','AFTER']:
        for name,q in saved.items():rig.pose.bones[name].rotation_quaternion=q
        if phase=='AFTER':bone.rotation_quaternion=Quaternion(axis,math.radians(-6))@saved[bone.name]
        bpy.context.view_layer.update()
        for view,name in man['cameras'].items():
            sc.camera=bpy.data.objects[name];folder=P/'static_visual';folder.mkdir(exist_ok=True);sc.render.filepath=str(folder/f'{phase}_{view}_{round(t*60):04d}.png');bpy.ops.render.render(write_still=True)
    rig.animation_data.action=original
print('FINITE_STATIC_VISUALS_READY_NO_ANIMATED_CANDIDATE',flush=True)
