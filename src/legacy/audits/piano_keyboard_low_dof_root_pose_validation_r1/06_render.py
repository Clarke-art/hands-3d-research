import bpy,sys,json
import numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'piano_keyboard_spatial_anchor_and_contact_validation_r1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
A=np.load(P/'model_a_evaluations.npz');old=np.load(PRE/'spatial_evaluations.npz');keys=read(P/'KEYBOARD_88_KEY_TABLE_R1.json')['keys'];ex=read(PRE/'HAND_EXTRACTION_R1.json');tl=read(P/'PERFORMANCE_TIMELINE_R1.json')
bpy.ops.wm.open_mainfile(filepath=str(P/'PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_CANDIDATE_R1.blend'),load_ui=False,use_scripts=False);sc=bpy.context.scene;obs={}
for s,c in ex['cfg'].items():
 bpy.data.objects[c['mesh']].hide_render=True
 me=bpy.data.meshes.new('REVIEW_EVALUATED_'+s);me.from_pydata(A[s+'_verts'][0].tolist(),[],ex['faces'][s]);ob=bpy.data.objects.new('REVIEW_EVALUATED_'+s,me);sc.collection.objects.link(ob);obs[s]=ob;ob.color=(.78,.53,.40,1) if s=='R' else (.40,.66,.69,1)
 for f,smooth in zip(me.polygons,ex['smooth'][s]):f.use_smooth=smooth
sc.render.resolution_x=1200;sc.render.resolution_y=660;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.display.shading.show_cavity=False;sc.display.shading.show_specular_highlight=True;sc.display.shading.shadow_intensity=.35;sc.view_settings.look='None'
jobs=[('PLAYER_A','PIANO_PLAYER_VIEW',A),('TEACHING_A','TEACHING_TOP_OBLIQUE',A),('CONTACT_A','CONTACT_CLOSE',A),('TEACHING_FIXED_REFERENCE','TEACHING_TOP_OBLIQUE',old)];preview='--preview' in sys.argv
for name,view,data in jobs:
 sc.camera=bpy.data.objects[view];out=P/'_render_frames'/name;out.mkdir(parents=True,exist_ok=True)
 for j in ([0,75,130,205] if preview else range(210)):
  sc.frame_set(j+1)
  for s,ob in obs.items():ob.data.vertices.foreach_set('co',data[s+'_verts'][j*2].astype(np.float32).ravel());ob.data.update()
  act=[n for n in tl['notes'] if n['source_on_sec']<=11.5+j/30<n['source_off_sec']];hands={n['key_index']:n['hand'] for n in act}
  for k in keys:
   s=hands.get(k['key_index']);col=(.78,.53,.40,1) if s=='R' else (.40,.66,.69,1) if s=='L' else (.82,.68,.28,1) if s=='UNKNOWN' else (.82,.80,.75,1) if k['color']=='WHITE' else (.025,.032,.045,1)
   for g in k['geometry']:bpy.data.objects[g['name']].color=col
  sc.render.filepath=str(out/f'{j:04}.png');bpy.ops.render.render(write_still=True)
 print('VIEW_COMPLETE',name,flush=True)
print('PREVIEW_COMPLETE' if preview else 'ALL_840_FRAMES_COMPLETE',flush=True)
