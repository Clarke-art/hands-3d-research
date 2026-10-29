"""Matched source/terminal stills only; terminal state is not a candidate."""
import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement'))
from blender_local import *
man=read(C1/'SCENE_MANIFEST.json');assert sha(man['path'])==read(OUT/'STRATEGY_LOCK.json')['source_sha256']
res=dict(np.load(OUT/'TERMINAL_TRAJECTORY_EVIDENCE.npz'))
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False)
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[man['mapping']['R']['rig']]
source_action=rig.animation_data.action;source_slot=rig.animation_data.action_slot
actual=dict(np.load(OUT/'ACTUAL_TERMINAL_SKIN.npz'));mesh=bpy.data.objects[man['mapping']['R']['mesh']]
folder=OUT/'terminal_diagnostic_stills';folder.mkdir(exist_ok=True)
receipt=[]
for label,t in [('EARLY',1.133333333),('LATE',3.825)]:
    i=int(np.argmin(abs(res['times']-t)));t=float(res['times'][i])
    for state in ['SOURCE','TERMINAL_NON_CANDIDATE']:
        rig.animation_data.action=source_action;rig.animation_data.action_slot=source_slot
        settime(sc,t)
        if state!='SOURCE':
            # Render evaluates the scene clock again; detach only this in-memory
            # Action binding so it cannot overwrite the measured terminal pose.
            rig.animation_data.action=None
            for j,d in enumerate(c.DIGITS):
                for name,mat in zip(c.SETUPS['R',d][0],c.joint_mats('R',d,np.radians(res['qdeg'][i,j]))):
                    rig.pose.bones[name].rotation_quaternion=Matrix(mat.tolist()).to_quaternion()
            bpy.context.view_layer.update()
        for view,name in man['cameras'].items():
            sc.camera=bpy.data.objects[name];sc.render.filepath=str(folder/f'{label}_{state}_{view}.png')
            bpy.ops.render.render(write_still=True)
            measured=mesh_pose(mesh)[0];ai=int(np.argmin(abs(actual['times']-t)))
            expected=actual['source' if state=='SOURCE' else 'terminal'][ai]
            err=float(np.max(np.linalg.norm(measured-expected,axis=1))*1000)
            assert abs(actual['times'][ai]-t)<1e-7 and err<.03,(state,view,err)
            receipt.append(dict(scope=label,state=state,video_sec=t,camera=name,view=view,
                camera_matrix=[list(r) for r in sc.camera.matrix_world],ortho_scale=sc.camera.data.ortho_scale,
                file=sc.render.filepath,actual_render_skin_parity_mm=err))
(OUT/'TERMINAL_DIAGNOSTIC_RENDER_MANIFEST.json').write_text(json.dumps(dict(rows=receipt,
    purpose='Failure evidence only; same original source camera, scale and time; not a new playable performance',
    new_blends=0,new_actions=0,new_videos=0),indent=2),encoding='utf8')
