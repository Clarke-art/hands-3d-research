import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Vector
O=Path(__file__).resolve().parent;PREV=O.parent/'hands_c01_whole_hand_motion_feasibility_r1';sys.path.insert(0,str(O));sys.path.insert(0,str(PREV));import blender_utils as u
F=json.loads((O/'STATIC_POSE_FEASIBILITY.json').read_text());R={x['test']:x for x in F['tests']};selected=json.loads((O/'SELECTED_STATIC_SCENES.json').read_text());selected={x['scene']:x for x in selected};P=json.loads((O/'POLICY_LOCK.json').read_text());bpy.ops.wm.open_mainfile(filepath=F['diagnostic_blend'],load_ui=False,use_scripts=False)
folder=O/'stills';folder.mkdir(exist_ok=True);manifest=[]
plan=[('INITIAL','OVERHEAD'),('S1','OVERHEAD'),('S1','SIDE_OBLIQUE'),('S2','SIDE_OBLIQUE')]
for label,view in plan:
 if label=='INITIAL':
  sc=bpy.data.scenes[P['source_action_scene']['scene']];bpy.context.window.scene=sc;u.settime(sc,1.914284);info=P['source_action_scene'];rig=bpy.data.objects[info['mapping']['R']['rig']];mesh=bpy.data.objects[info['mapping']['R']['mesh']];midi=70;ctext='C01 INITIAL - FAIL: INDEX / A#4; RING / C#5'
  source=json.loads((O/'SOURCE_POSE_COLLISION_DIAGNOSES.json').read_text());measurement=next(x['measurement'] for x in source if x['label']=='C01_INITIAL');cams=info['cameras']
 else:
  choice=selected[R[label]['selected_scene']];sc=bpy.data.scenes[choice['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[choice['rig']];mesh=bpy.data.objects[choice['mesh']];midi=R[label]['midi'];measurement=choice['actual_geometry'];cams=choice['cameras'];status=R[label]['status'];ctext=f'{label}: MIDI {midi}, FINGER {R[label]["finger"]} -- '+('STATIC SCREEN PASS, HUMAN PENDING' if status=='PASS_STATIC_SCREEN_HUMAN_PENDING' else 'PRECONDITION NOT MET, EXPLORATORY ONLY' if label=='S5' else f'FAIL: TARGET DEPTH {measurement["target_key_max_depth_mm"]:.3f} mm')
 assert u.digest(u.native(mesh,rig))==u.pf['right_native_sha256']
 sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.display.shading.light='STUDIO';sc.display.shading.color_type='OBJECT';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=True;sc.display.shading.cavity_type='BOTH';sc.display.shading.background_type='WORLD';sc.world.color=(.08,.08,.08)
 cam=bpy.data.objects[cams[view]];sc.camera=cam;cam.data.ortho_scale=.34;target=Vector(((u.c.KEYS[67-21]['key_center'][0]+u.c.KEYS[79-21]['key_center'][0])/2,-.035,.014));cam.location=target+Vector((0,0,.8) if view=='OVERHEAD' else (.11,-.48,.22));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 bpy.context.view_layer.update();overlays=[]
 font=bpy.data.curves.new('DIAGNOSTIC_TEXT','FONT');font.body=ctext;font.size=.009;obj=bpy.data.objects.new('DIAGNOSTIC_LABEL',font);sc.collection.objects.link(obj);obj.rotation_euler=cam.rotation_euler;obj.location=cam.matrix_world@Vector((-.28,.147,-.42));obj.color=(1,.25,.15,1) if label in ['INITIAL','S1'] else (.1,.75,.35,1);overlays.append(obj)
 if label in ['INITIAL','S1']:
  candidates=[(h,w) for h in measurement['key_hits'] for w in h.get('triangle_interior_witnesses',[]) if w['inside_depth_mm']>.25]
  candidates=sorted(candidates,key=lambda x:x[1]['inside_depth_mm'],reverse=True)[:2]
  for h,w in candidates:
   point=Vector(w['world_point_m']);bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.0013,location=point+Vector((0,0,.015)));dot=bpy.context.object;dot.name='COLLISION_MARKER_OFFSET_4MM';dot.color=(1,.03,.02,1);overlays.append(dot)
   curve=bpy.data.curves.new('COLLISION_CONNECTOR','CURVE');curve.dimensions='3D';curve.bevel_depth=.00025;line=curve.splines.new('POLY');line.points.add(1);line.points[0].co=(*point,1);line.points[1].co=(*(point+Vector((0,0,.015))),1);ob=bpy.data.objects.new('COLLISION_WITNESS_LINE',curve);sc.collection.objects.link(ob);ob.color=(1,.03,.02,1);overlays.append(ob)
 file=folder/f'{label}_{view}.png';sc.render.filepath=str(file);bpy.ops.render.render(write_still=True);manifest.append(dict(file=str(file),test=label,view=view,caption=ctext,scene=sc.name,actual_static_mesh=True,collision_marker_offset_mm=15 if label in ['INITIAL','S1'] else 0,overlay_only_not_in_solver=True))
 for ob in overlays:bpy.data.objects.remove(ob,do_unlink=True)
existing=json.loads((O/'STILL_MANIFEST.json').read_text());updated={(x['test'],x['view']):x for x in existing if x['test']!='S5'};updated.update({(x['test'],x['view']):x for x in manifest});manifest=list(updated.values())
(O/'STILL_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8');print('STATIC_STILLS_ONLY',len(manifest),flush=True)

