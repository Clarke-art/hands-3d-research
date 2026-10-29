import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from blender_utils import *
M=json.loads((O/'SCENE_MANIFEST.json').read_text());A=np.load(O/'motion.npz');bpy.ops.wm.open_mainfile(filepath=M['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[M['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[M['mapping']['R']['rig']];mesh=bpy.data.objects[M['mapping']['R']['mesh']]
assert digest(native(mesh,rig))==pf['right_native_sha256'];times=np.arange(I['clip_start_sec'],I['clip_end_sec'],1/240);wrist=[];angles=[];parity=[]
for t in times:
 settime(sc,float(t));p=np.array(<REDACTED_EMAIL>['WRIST_R'].head);wrist.append(p);expected=BASE+np.array([np.interp(t,A['times'],A['R_delta'][:,j]) for j in range(3)]);parity.append(float(np.linalg.norm(p-expected)*1000))
wrist=np.array(wrist);v=np.diff(wrist,axis=0)*240*1000;acc=np.diff(v,axis=0)*240
reset=[]
for t in np.linspace(I['notes'][0]['note_off']-.045,I['notes'][1]['note_on']+.035,33):
 settime(sc,float(t));V,F=coords(mesh);n=I['notes'][0];reset.append(dict(time=float(t),key_angle_rad=float(keyangles()[67-21]),thumb_contact=contact(V[c.MARKERS['R'][0]['mesh_vertex']],c.KEYS[67-21],keyangles()[67-21])))
# Additional surface-grazing check uses actual mesh triangles against actual moving key geometry.
checks=[]
for t in [2.664283999999997,2.9564260000000004,3.825,4.0278535,4.67071]:
 settime(sc,t);V,F=coords(mesh);handtree=BVHTree.FromPolygons([Vector(v) for v in V],F,epsilon=0);angles=keyangles();hits=[]
 for key in c.KEYS:
  pv=np.array(key['press_pivot']);R=c.axisrot(angles[key['key_index']],key['press_axis'])
  for j,g in enumerate(key['geometry']):
   W=(np.array(g['vertices'])-pv)@R.T+pv
   if np.any(V.max(0)<W.min(0)) or np.any(V.min(0)>W.max(0)):continue
   tr= np.asarray(g['triangles']).reshape(-1,3).tolist();kt=BVHTree.FromPolygons([Vector(v) for v in W],tr,all_triangles=True,epsilon=0);count=len(handtree.overlap(kt))
   if count:hits.append(dict(key=key['note_name'],midi=key['midi_note'],piece=j,intersecting_triangle_pairs=count))
 checks.append(dict(time=t,hand_key_triangle_surface_intersections=hits))
metric=json.loads((O/'MOTION_FEASIBILITY_METRICS.json').read_text());metric['actual_wrist_verification']=dict(samples=len(times),hz=240,actual_wrist_vs_planned_translation_max_mm=max(parity),actual_wrist_speed_peak_mm_sec=float(np.linalg.norm(v,axis=1).max()),actual_wrist_acceleration_peak_mm_sec2=float(np.linalg.norm(acc,axis=1).max()),bone='Actual WRIST_R head transformed by evaluated rig.matrix_world',not_naturalness_certificate=True);metric['repeated_G4_reset_actual_samples']=reset;metric['actual_hand_key_triangle_checks']=checks
out('MOTION_FEASIBILITY_METRICS.json',metric);print('ACTUAL_WRIST_AND_TRIANGLES_VERIFIED',max(parity),float(np.linalg.norm(v,axis=1).max()),flush=True)
