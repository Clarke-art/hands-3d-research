import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from blender_local import *
from mathutils import Quaternion
assert not DEST.exists()
policy=read(P/'LOCAL_CORRECTION_POLICY.json');assert sha(P/'LOCAL_CORRECTION_POLICY.json')==read(P/'LOCAL_CORRECTION_POLICY_LOCK.json')['policy_sha256']
v=read(P/'IN_MEMORY_VALIDATION.json');bad=v['local_bad_samples'];dump('LOCKED_RESIDUAL_SUMMARY.json',dict(count=len(bad),first_video_sec=min(r['presentation_sec'] for r in bad),last_video_sec=max(r['presentation_sec'] for r in bad),max_triangle_pairs=max(r['intersecting_patch_triangle_pairs'] for r in bad),metrics=v['metrics'],parameter_changes=0,second_motion_solve=False,exact_zero_intersection_gate='FAILED_RETAINED',actual_scope='Normal-view inspection of same locked correction only; no retuning or second candidate.'))
man=read(C1/'SCENE_MANIFEST.json');bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']];bone=rig.pose.bones['RING_MCP_R'];axis=Vector(c.SETUPS['R','RING'][3]);original=rig.animation_data.action;roi=read(P/'LOCAL_SKIN_ROI_WITH_NEIGHBOR.json')
for t in [.9,1.05,1.1125,1.133333333,1.15,1.20,1.40,1.80,1.95,2.1]:
    settime(sc,t);saved={b.name:b.rotation_quaternion.copy() for b in rig.pose.bones};rig.animation_data.action=None
    for phase in ['BEFORE','AFTER']:
        for name,q in saved.items():rig.pose.bones[name].rotation_quaternion=q
        if phase=='AFTER':
            start,end=policy['presentation_support_sec'];a,b=policy['plateau_sec'];delta=policy['maximum_delta_deg']
            if t<=start or t>=end:delta=0
            elif t<a:u=(t-start)/(a-start);delta*=u**3*(10-15*u+6*u*u)
            elif t>b:u=(end-t)/(end-b);delta*=u**3*(10-15*u+6*u*u)
            bone.rotation_quaternion=Quaternion(axis,math.radians(delta))@saved[bone.name]
        bpy.context.view_layer.update()
        for view,name in man['cameras'].items():
            sc.camera=bpy.data.objects[name];folder=P/'locked_preview';folder.mkdir(exist_ok=True);sc.render.filepath=str(folder/f'{phase}_{view}_{round(t*240):04d}.png');bpy.ops.render.render(write_still=True)
    rig.animation_data.action=original
print('SAME_LOCKED_CORRECTION_VISIBLE_RESIDUAL_EVIDENCE_READY',flush=True)
