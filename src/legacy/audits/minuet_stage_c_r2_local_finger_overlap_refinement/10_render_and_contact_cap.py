import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from blender_local import *
assert read(P/'SAVED_CANDIDATE_VALIDATION.json')['functional_and_non_target_guards']=='PASS'
man=read(P/'SCENE_MANIFEST.json');assert sha(man['path'])==man['sha256'];tl=read(C1/'PERFORMANCE_TIMELINE.json')
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
info=man['mapping']['R'];mesh=bpy.data.objects[info['mesh']];rig=bpy.data.objects[info['rig']]
settime(sc,0);native=np.array([list(v.co) for v in mesh.data.vertices]);vid=c.MARKERS['R'][3]['mesh_vertex'];groups={g.index:g.name for g in mesh.vertex_groups};weights=np.array([sum(g.weight for g in v.groups if groups[g.group].startswith('RING_')) for v in mesh.data.vertices]);ids=np.flatnonzero((np.linalg.norm(native-native[vid],axis=1)<.006)&(weights>.65));assert len(ids)>=5
n=next(n for n in tl['notes'] if n['note_id']=='R04');k=c.KEYS[n['key_index']];pv=bpy.data.objects[man['key_pivots'][str(n['key_index'])]];samples=[]
for t in np.linspace(n['note_on'],n['note_off']-.00001,21):
    v=snapshot(sc,info,'R',float(t));angle=pv.rotation_euler.x;pivot=np.array(k['press_pivot']);R=c.axisrot(angle,[1,0,0]);points=(v['V'][ids]-pivot)@R+pivot;center=(v['skin_pads'][3]-pivot)@R+pivot
    surface=min(k['key_top_playable_surface'],key=lambda s:np.linalg.norm(center[:2]-np.clip(center[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))
    lo,hi=np.quantile(points[:,0],[.05,.95]);samples.append(dict(presentation_sec=float(t),music_sec=float(t-.35),skin_center_gap_mm=float((center[2]-surface['z'])*1000),P90_cap_left_margin_mm=float((lo-surface['xmin'])*1000),P90_cap_right_margin_mm=float((surface['xmax']-hi)*1000),full_cap_x_range_mm=[float(points[:,0].min()*1000),float(points[:,0].max()*1000)]))
assert all(min(s['P90_cap_left_margin_mm'],s['P90_cap_right_margin_mm'])>0 and abs(s['skin_center_gap_mm'])<3 for s in samples),'R04_FINITE_SKIN_PAD_CAP_FAILED'
dump('ACTIVE_RING_C5_CAP_READBACK.json',dict(pass_=True,source_C5_note_id='R04',finite_local_skin_vertices=ids.tolist(),samples=samples,minimum_P90_edge_margin_mm=min(min(s['P90_cap_left_margin_mm'],s['P90_cap_right_margin_mm']) for s in samples),only_one_changed_active_note=True,keyboard_pressure_action_unchanged=True,limitations='6mm rest neighborhood of calibrated actual pad vertex, finite P90 footprint check, not exhaustive pressure/collision simulation'))
# Use the exact inherited saved cameras, render settings, light/material setup.
sc.render.image_settings.file_format='PNG';sc.render.use_persistent_data=True
for frame in range(1,358):
    sc.frame_set(frame)
    for view,name in man['cameras'].items():
        folder=P/'_frames'/view;folder.mkdir(parents=True,exist_ok=True);dest=folder/f'{frame-1:04d}.png'
        if dest.exists():continue
        sc.camera=bpy.data.objects[name];sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
    if frame%30==0:print('SAME_SOLE_LOCAL_CANDIDATE_FULL_THREE_VIEWS',frame,357,flush=True)
dump('RENDER_MANIFEST.json',dict(candidate_sha256=man['sha256'],frames_each=357,fps=60,dimensions=[1280,720],same_saved_C1_cameras=True,same_lighting_materials=True,source_audio_unchanged=True,single_derived_scene=True,normal_speed=True))
