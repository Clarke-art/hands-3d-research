import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'G4_E5_NATURAL_BRIDGE_DESIGN_PROVISIONAL_R2.blend'),load_ui=False,use_scripts=False)
b=json.loads((O/'ACTION_BINDINGS.json').read_text());sc=bpy.data.scenes[b['scene']];bpy.context.window.scene=sc
m=json.loads((O/'SKIN_MODEL_META.json').read_text());keys=m['key_table'];target=Vector(((keys[46]['key_center'][0]+keys[58]['key_center'][0])/2,-.035,.014))
sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100
sc.display.shading.light='STUDIO';sc.display.shading.color_type='OBJECT';sc.display.shading.show_shadows=False;sc.display.shading.show_cavity=True;sc.display.shading.background_type='WORLD';sc.world.color=(.075,.075,.075)

for ob in sc.objects:
 if ob.type=='MESH':
  ki=ob.get('FROZEN_KEY_INDEX')
  ob.color=((.055,.055,.065,1) if keys[int(ki)]['color']=='BLACK' else (.85,.85,.84,1)) if ki is not None else (.38,.40,.43,1)
bpy.data.objects[b['mesh']].color=(.72,.43,.24,1)
sc.render.image_settings.file_format='PNG';sc.render.use_stamp=True;sc.render.use_stamp_note=True;sc.render.use_stamp_time=False;sc.render.use_stamp_date=False;sc.render.use_stamp_frame=False;sc.render.use_stamp_filename=False;sc.render.use_stamp_camera=False;sc.render.stamp_font_size=18;sc.render.stamp_foreground=(1,1,1,1);sc.render.stamp_background=(0,0,0,.9)
shots=[('BRIDGE_START_OVERHEAD',2.527855,'OVERHEAD','B2 START | G4 held | DESIGN_PROVISIONAL'),('EXCHANGE_OVERHEAD',2.921426,'OVERHEAD','EXACT MIDI EXCHANGE | G4 LOST / E5 DEEP INTRUSION | FAIL'),('EXCHANGE_SIDE_OBLIQUE',2.921426,'SIDE_OBLIQUE','EXACT MIDI EXCHANGE | COLLISION FAILURE | DESIGN_PROVISIONAL'),('PLUS35MS_OVERHEAD',2.956426,'OVERHEAD','E5 ON +35 ms | local contact PASS does not validate ON')]
out=[]
for name,t,v,label in shots:
 frame=1+60*t;sc.frame_set(math.floor(frame),subframe=frame-math.floor(frame));cam=bpy.data.objects[b['cameras'][v]];cam.animation_data_clear();cam.constraints.clear();cam.parent=None;cam.location=target+Vector((0,0,.8) if v=='OVERHEAD' else (.11,-.48,.22));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.46;sc.camera=cam;sc.render.stamp_note_text=label;sc.render.filepath=str(O/'stills'/f'{name}.png');bpy.ops.render.render(write_still=True);out.append(dict(file=sc.render.filepath,time=t,view=v,resolution=[1280,720],label=label))
(O/'BRIDGE_STILL_MANIFEST.json').write_text(json.dumps(out,indent=2)+'\n');print('FOUR_FAILURE_REVIEW_STILLS_COMPLETE')
