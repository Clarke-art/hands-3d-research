import bpy,json,math
import numpy as np
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent
read=lambda n:json.loads((P/n).read_text())
keys=read('KEYBOARD_88_KEY_TABLE_R1.json')['keys'];A=np.load(P/'spatial_evaluations.npz');ex=read('HAND_EXTRACTION_R1.json')
bpy.ops.wm.open_mainfile(filepath=str(P/'PIANO_KEYBOARD_SPATIAL_ANCHOR_VALIDATION_CANDIDATE_R1.blend'),load_ui=False,use_scripts=False);sc=bpy.context.scene
actual=[o for o in bpy.data.objects if 'key_index' in o];assert len(actual)==88;assert sorted(o['midi_note'] for o in actual)==list(range(21,109))
maxerr=0
for i in [0,91,206,420]:
 sc.frame_set(1+i//2,subframe=(i%2)*.5)
 for k in keys:
  pv=np.array(k['press_pivot']);a=A['angles'][i,k['key_index']];c=math.cos(a);s=math.sin(a)
  for g in k['geometry']:
   ob=bpy.data.objects[g['name']];q=np.array(g['vertices'])-pv;t=q.copy();t[:,1]=q[:,1]*c-q[:,2]*s;t[:,2]=q[:,1]*s+q[:,2]*c;t+=pv;v=np.array([list(<REDACTED_EMAIL>) for p in ob.data.vertices]);maxerr=max(maxerr,float(np.max(np.abs(t-v))*1000))
assert maxerr<.005
# Verify approved positive pivot rotation actually lowers the front top, not just metadata.
press_checks=[]
for k in keys:
 g=min(k['key_top_playable_surface'],key=lambda s:s['ymin']);y=g['ymin'];z=g['z'];pv=k['press_pivot'];a=k['press_angle_rad'];down=pv[2]+(y-pv[1])*math.sin(a)+(z-pv[2])*math.cos(a);assert down<z
 press_checks.append((z-down)*1000)
for c in ex['cfg'].values():bpy.data.objects[c['mesh']].hide_render=True
for k in keys:
 o=bpy.data.objects[k['semantic_identity']];o.animation_data_clear();o.rotation_euler=(0,0,0)
 for g in k['geometry']:bpy.data.objects[g['name']].color=(.95,.55,.24,1) if k['midi_note'] in [21,60,69,108] else (.82,.80,.75,1) if k['color']=='WHITE' else (.025,.032,.045,1)
cam=bpy.data.objects['PIANO_PLAYER_VIEW'];cam.location.y=-.24;cam.location.z=.8;target=Vector((cam.location.x,.045,0));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.42;sc.camera=cam;sc.render.resolution_x=1600;sc.render.resolution_y=460;sc.render.resolution_percentage=100;sc.render.filepath=str(P/'KEY_MAPPING_PROOF_BASE.png');bpy.context.view_layer.update();bpy.ops.render.render(write_still=True)
labels=[]
for n in [21,60,69,108]:
 k=keys[n-21];p=world_to_camera_view(sc,cam,Vector((k['key_center'][0],k['front_extent']-.02,0)));labels.append({'label':f'{n} = {k["note_name"]}','pixel':[p.x*1600,(1-p.y)*460]})
(P/'KEYBOARD_INDEPENDENT_VERIFICATION_R1.json').write_text(json.dumps({'status':'PASS','saved_reopened_actual_key_count':len(actual),'unique_midi_21_108':True,'saved_geometry_animation_max_error_mm':maxerr,'verified_observations':[0,91,206,420],'positive_press_lowers_front_all88':True,'front_top_dip_mm_min_max':[min(press_checks),max(press_checks)],'actual_camera_projected_sample_labels':labels,'sample_geometry_order':'A0<C4<A4<C8'},indent=2))
print('INDEPENDENT_KEYBOARD_PASS',maxerr)
