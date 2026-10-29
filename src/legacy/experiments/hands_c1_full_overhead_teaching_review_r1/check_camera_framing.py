import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,math,shutil,types
import numpy as np
begin=time.perf_counter();copy=OUT/'C1_READONLY_CAMERA_CHECK_COPY.blend';assert not copy.exists();shutil.copyfile(SOURCE,copy)
bpy.ops.wm.open_mainfile(filepath=str(copy),load_ui=False,use_scripts=False);assert not bpy.data.libraries
sc=bpy.data.scenes[MAN['scene']];bpy.context.window.scene=sc;cam=bpy.data.objects[MAN['cameras']['OVERHEAD']]
sc.camera=cam
assert sc.frame_start==1 and sc.frame_end==357 and sc.render.fps==60 and sc.render.fps_base==1
assert cam.data.type=='ORTHO'
for sound in bpy.data.sounds:
    if not sound.packed_file:safe(bpy.path.abspath(sound.filepath))
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file:safe(bpy.path.abspath(im.filepath))
H=types.ModuleType('frozen_helpers');p=ROOT/'experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/blender_helpers.py'
exec(compile(safe(p).read_text(encoding='utf8'),str(p),'exec'),H.__dict__)
def curves(a):return [f for layer in a.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves]
def action_digest():
    return H.digest({a.name:[dict(path=f.data_path,index=f.array_index,extrapolation=f.extrapolation,keys=[dict(co=list(k.co),interpolation=k.interpolation,left=list(k.handle_left),right=list(k.handle_right),lt=k.handle_left_type,rt=k.handle_right_type) for k in f.keyframe_points]) for f in curves(a)] for a in bpy.data.actions})
before=action_digest();native={s:H.digest(H.native(bpy.data.objects[m['mesh']],bpy.data.objects[m['rig']])) for s,m in MAN['mapping'].items()}
notes=read(C1/'PERFORMANCE_TIMELINE.json')['notes'];assert len(notes)==23 and sum(n['hand']=='R' for n in notes)==16 and sum(n['hand']=='L' for n in notes)==7
keyobs=[o for o in sc.objects if o.type=='MESH' and o.get('FROZEN_KEY_INDEX') is not None and 55-21<=o['FROZEN_KEY_INDEX']<=79-21]
rows=[];mats=[]
for frame in range(1,358):
    sc.frame_set(frame);bpy.context.view_layer.update();matrix=np.array(cam.matrix_world);mats.append(matrix)
    inv=np.linalg.inv(matrix);vf=np.array([list(v) for v in cam.data.view_frame(scene=sc)])
    lo=vf[:,:2].min(0);hi=vf[:,:2].max(0)
    def project(V):
        local=(np.c_[V,np.ones(len(V))]@inv.T)[:,:3];return (local[:,:2]-lo)/(hi-lo)
    ranges={}
    for side in ['R','L']:
        ob=bpy.data.objects[MAN['mapping'][side]['mesh']];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
        try:V=np.array([list(<REDACTED_EMAIL>) for v in me.vertices])
        finally:ev.to_mesh_clear()
        ndc=project(V);ranges[side]=dict(min=ndc.min(0),max=ndc.max(0))
    V=np.array([list(<REDACTED_EMAIL>) for o in keyobs for v in o.data.vertices]);ndc=project(V);ranges['KEY_RANGE_G3_G5']=dict(min=ndc.min(0),max=ndc.max(0))
    rows.append(dict(frame=frame,time=(frame-1)/60,ranges=ranges))
assert np.max(np.abs(np.array(mats)-mats[0]))==0
R=mats[0][:3,:3];optical=-R[:,2]/np.linalg.norm(R[:,2]);vertical_error=float(np.degrees(np.arccos(np.clip(<REDACTED_EMAIL>([0,0,-1]),-1,1))))
horizontal_error=float(np.degrees(np.arccos(np.clip(R[:,0]@np.array([1,0,0])/np.linalg.norm(R[:,0]),-1,1))))
clipped=[dict(frame=r['frame'],object=k) for r in rows for k,b in r['ranges'].items() if np.any(np.array(b['min'])<0) or np.any(np.array(b['max'])>1)]
assert not clipped and vertical_error<.01 and horizontal_error<.01
extreme_frames=sorted({rows[int(np.argmin([r['ranges'][side]['min'][a] for r in rows]))]['frame'] for side in ['R','L'] for a in [0,1]}|
                      {rows[int(np.argmax([r['ranges'][side]['max'][a] for r in rows]))]['frame'] for side in ['R','L'] for a in [0,1]})
assert before==action_digest()
assert all(H.digest(H.native(bpy.data.objects[m['mesh']],bpy.data.objects[m['rig']]))==native[s] for s,m in MAN['mapping'].items())
save('CAMERA_FRAMING_CHECK.json',dict(pass_=True,seconds=time.perf_counter()-begin,camera=cam.name,projection=cam.data.type,matrix_world=mats[0],optical_axis=optical,vertical_error_deg=vertical_error,
    keyboard_horizontal_error_deg=horizontal_error,ortho_scale=cam.data.ortho_scale,resolution_original=[sc.render.resolution_x,sc.render.resolution_y],fixed_camera_all357frames=True,
    frame_range=[1,357],presentation_duration_sec=5.95,music_on_sec=min(n['note_on'] for n in notes),last_note_off_sec=max(n['note_off'] for n in notes),notes=23,right_notes=16,left_notes=7,
    played_midi_range=[55,79],all_chromatic_keys_in_range_checked=25,clipped=clipped,extreme_frames=extreme_frames,rows=rows,all_action_payloads_unchanged=True,native_structure_unchanged=True,
    original_action_digest=before,source_sha256=sha(SOURCE),copy_sha256=sha(copy),copy_not_saved_after_camera_selection=True,no_motion_generation=True))
protect('CAMERA_INPUT_PROTECTION.json');print('TRUE_OVERHEAD_FRAMING_PASS',vertical_error,horizontal_error,extreme_frames,time.perf_counter()-begin,flush=True)
