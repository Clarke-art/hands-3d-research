from common import *
import bpy,math,itertools,types
import numpy as np
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
HELPERS=ROOT/'experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/blender_helpers.py'
c=types.ModuleType('frozen_blender_helpers');exec(compile(safe(HELPERS).read_text(encoding='utf8'),str(HELPERS),'exec'),c.__dict__)
c.DIGITS=['THUMB','INDEX','MIDDLE','RING','LITTLE'];DIGITS=c.DIGITS
c.RIG=read(OLD/'RIG_CANONICAL_PROBE_R1.json');c.MARKERS={s:read(OLD/'FINGERTIP_CONTACT_MARKERS_R1.json')['markers'][s] for s in ['R','L']}
c.SETUPS={(s,d):c.digit_setup(s,d) for s in ['R','L'] for d in DIGITS}
KEYS=read(OLD/'KEYBOARD_88_KEY_TABLE_R1.json')['keys']
ROI=read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/DIGIT_SKIN_ROI.json')
extract(ROOT/'experiments/hands_role_aware_collision_avoidance_r1/baseline_blender.py',['degrees'],globals())
def curves(action):return [f for layer in action.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves]
def payload(action,exclude=set()):
    return [dict(path=f.data_path,index=f.array_index,extrapolation=f.extrapolation,
                 keys=[dict(co=list(k.co),interpolation=k.interpolation,left=list(k.handle_left),right=list(k.handle_right),lt=k.handle_left_type,rt=k.handle_right_type) for k in f.keyframe_points])
            for f in curves(action) if f.data_path not in exclude]
def open_scene(p):
    global sc,rig,mesh,left,lrig
    bpy.ops.wm.open_mainfile(filepath=str(safe(p)),load_ui=False,use_scripts=False)
    assert not bpy.data.libraries,'LINKED_LIBRARY_FORBIDDEN'
    sc=bpy.data.scenes[MAN['scene']];bpy.context.window.scene=sc
    rig=bpy.data.objects[MAN['mapping']['R']['rig']];mesh=bpy.data.objects[MAN['mapping']['R']['mesh']]
    left=bpy.data.objects[MAN['mapping']['L']['mesh']];lrig=bpy.data.objects[MAN['mapping']['L']['rig']]
    for sound in bpy.data.sounds:
        if not sound.packed_file:safe(bpy.path.abspath(sound.filepath))
    for im in bpy.data.images:
        if im.source=='FILE' and not im.packed_file:safe(bpy.path.abspath(im.filepath))
    globals()['rig']=rig
    return sc,rig,mesh,left,lrig
def coords_tri(ob):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    try:
        me.calc_loop_triangles()
        return np.array([list(<REDACTED_EMAIL>) for v in me.vertices]),np.array([list(t.vertices) for t in me.loop_triangles],int),[list(p.vertices) for p in me.polygons]
    finally:ev.to_mesh_clear()
def keyangle(k):
    name=MAN['key_pivots'].get(str(k['key_index']))
    return bpy.data.objects[name].rotation_euler.x if name else 0.
def registered_components():
    return [(key,g,c.component_planes(g)) for key in KEYS for g in key['geometry']]
def key_local(V,key):
    pv=np.array(key['press_pivot']);return (V-pv)@c.axisrot(keyangle(key),key['press_axis'])+pv
def target_depth(V,ids,ki=52):
    key=KEYS[ki];local=key_local(V[ids],key)
    return max(float(np.maximum(0,-np.max(local@pl[:,:3].T-pl[:,3],axis=1)*1000).max()) for k,g,pl in registered_components() if k['key_index']==ki)
def protected_state(exclude_rig=False):
    return {o.name:dict(action=o.animation_data.action.name,slot=o.animation_data.action_slot.identifier,payload=c.digest(payload(o.animation_data.action)))
            for o in sc.objects if o.animation_data and o.animation_data.action and (not exclude_rig or o!=rig)}
def contact(V,key,side,finger):
    v=c.MARKERS[side][finger-1]['mesh_vertex'];p=key_local(V[[v]],key)[0]
    ss=key['key_top_playable_surface'];s=min(ss,key=lambda s:np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))
    miss=float(np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']]))*1000);gap=float(p[2]-s['z'])*1000
    inside=bool(s['xmin']<=p[0]<=s['xmax'] and s['ymin']<=p[1]<=s['ymax'])
    return dict(vertex=v,horizontal_mm=miss,gap_mm=gap,inside=inside,pass_=inside and miss<=.03 and abs(gap)<=3)
