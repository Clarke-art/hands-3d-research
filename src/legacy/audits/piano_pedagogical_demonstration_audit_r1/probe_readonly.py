"""Bounded read-only evaluation; never changes or saves actions/assets."""
import bpy, json, math, sys
from pathlib import Path
import numpy as np
from mathutils import Vector
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent; ROOT=P.parents[1]
S=ROOT/'audits/minuet_stage_c_lightweight_animation_poc_r1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
man=read(S/'SCENE_MANIFEST.json'); legacy=read(ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/SCENE_MANIFEST.json')
tl=read(ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/PERFORMANCE_TIMELINE.json')
base=ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1'
markers=read(base/'FINGERTIP_CONTACT_MARKERS_R1.json')['markers'];keys=read(base/'KEYBOARD_88_KEY_TABLE_R1.json')['keys']
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False)
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
def settime(t):
 f=1+60*t;sc.frame_set(math.floor(f),subframe=f-math.floor(f));bpy.context.view_layer.update()
def verts(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();v=np.array([list(<REDACTED_EMAIL>) for x in me.vertices]);ev.to_mesh_clear();return v
rows=[]
for n in tl['notes']:
 ob=bpy.data.objects[man['mapping'][n['hand']]['mesh']];rig=bpy.data.objects[man['mapping'][n['hand']]['rig']]
 marker=markers[n['hand']][n['finger']-1];vid=marker['mesh_vertex']
 # Fixed local skin neighborhood around the established actual surface vertex.
 rest=np.array([list(v.co) for v in ob.data.vertices]);dist=np.linalg.norm(rest-rest[vid],axis=1)
 ids=np.flatnonzero(dist<=.006)
 key=keys[n['key_index']];pivot=bpy.data.objects[legacy['key_pivots'][str(n['key_index'])]]
 phases=[('prepare',max(0,n['note_on']-.08)),('on',n['note_on']),('settle',n['note_on']+.04),('hold',(n['note_on']+n['note_off'])/2),('off',n['note_off']),('release',n['note_off']+.06)]
 samples=[]
 for phase,t in phases:
  settime(t);V=verts(ob);a=pivot.rotation_euler.x;ca,sa=math.cos(a),math.sin(a);rot=np.array([[1,0,0],[0,ca,-sa],[0,sa,ca]])
  pv=np.array(key['press_pivot']);local=(V[ids]-pv)@rot+pv;mp=(V[vid]-pv)@rot+pv
  candidates=[]
  for surf in key['key_top_playable_surface']:
   inside=(local[:,0]>=surf['xmin'])&(local[:,0]<=surf['xmax'])&(local[:,1]>=surf['ymin'])&(local[:,1]<=surf['ymax'])
   for j in np.flatnonzero(inside):candidates.append((float((local[j,2]-surf['z'])*1000),int(ids[j])))
  nearest=min(candidates,key=lambda x:abs(x[0])) if candidates else None
  surface=min(key['key_top_playable_surface'],key=lambda s:np.linalg.norm(mp[:2]-np.clip(mp[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))
  samples.append(dict(phase=phase,time=t,frame=round(t*60),key_angle_rad=a,actual_skin_marker_world=V[vid].tolist(),skin_marker_gap_mm=float((mp[2]-surface['z'])*1000),skin_marker_horizontal_mm=float(np.linalg.norm(mp[:2]-np.clip(mp[:2],[surface['xmin'],surface['ymin']],[surface['xmax'],surface['ymax']]))*1000),patch_vertices_in_footprint=len(candidates),nearest_patch_vertex_gap_mm=nearest[0] if nearest else None,nearest_patch_vertex=nearest[1] if nearest else None,distal_quaternion=list(rig.pose.bones[marker['distal_frame']].rotation_quaternion)))
 rows.append(dict(note=n,skin_patch_vertex_count=len(ids),samples=samples,rig_action=rig.animation_data.action.name,key_action=pivot.animation_data.action.name))
 print('READONLY_NOTE',n['note_id'],flush=True)
(P/'SKIN_KEY_SAMPLES.json').write_text(json.dumps(dict(candidate=man,method='Saved candidate evaluated skin: fixed 6mm rest-space neighborhood; inverse actual key-pivot rotation against preserved playable surfaces. Six phases per note. No solver, no action writes, no save. Finite vertices are supporting evidence, not surface/continuous-contact proof.',rows=rows),indent=2),encoding='utf8')
