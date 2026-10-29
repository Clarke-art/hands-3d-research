import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Vector
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'))
import blender_utils as u
P=json.loads((O/'POLICY_LOCK.json').read_text());M=P['source_action_scene']
K=np.array([2.527855,2.72,2.86,2.921426,2.956426,3.14,3.349997])
times=sorted(set(K.tolist()+[float(a+(b-a)*w) for a,b in zip(K[:-1],K[1:]) for w in [.25,.5,.75]]+[2.921326,2.921526,2.956326,2.956526]))
bpy.ops.wm.open_mainfile(filepath=M['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[M['scene']];bpy.context.window.scene=sc;ang=[]
for t in times:u.settime(sc,t);ang.append(u.keyangles())
np.savez_compressed(O/'MOTION_COLLOCATION_KEYS.npz',knots=K,times=times,key_angles=ang)
plan=dict(one_trajectory_only=True,knots=K.tolist(),geometry_collocation_times=times,clock_offset=.35,held_G4_until=2.921426,E5_contact_required_from=2.921426,E5_Action_full_press=2.956426,validation_Hz=120,adaptive_near_contact=True,interpolation='PCHIP-limited cubic Hermite, clamped zero velocity at bridge start/end; joint/root scalar tracks C1',start_fixed='B2 exact verified state',end_fixed='verified natural E5 endpoint at E5 OFF, still depressed under original Action',internal_states='root, thumb, reference lambda, coordinated middle flex alpha jointly solved; no separate finger fixes',contact_proxy='Clipped complete pulp; material/plane collision activity witnesses; final independent full Blender triangles mandatory',active_reference_confidence='Provisional active hinge flex family, reviewed spread unchanged; not clinical ROM',numerical_budget_seconds=280,maximum_restarts=0,video_requires_full_dynamic_gate=True)
(O/'MOTION_DESIGN_LOCK.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Two low-cost endpoint previews within the total six-still cap.
info=json.loads((O/'ENDPOINT_ACTUAL_2.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(O/'E5_ENDPOINT_2_DIAGNOSTIC.blend'),load_ui=False,use_scripts=False);sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;folder=O/'stills';folder.mkdir(exist_ok=True);manifest=[]
for view in ['OVERHEAD','SIDE_OBLIQUE']:
 sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.display.shading.light='STUDIO';sc.display.shading.color_type='OBJECT';sc.display.shading.show_shadows=False;sc.display.shading.show_cavity=True;sc.display.shading.cavity_type='BOTH';sc.display.shading.background_type='WORLD';sc.world.color=(.08,.08,.08)
 cam=bpy.data.objects[info['cameras'][view]];sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.34;target=Vector(((u.c.KEYS[46]['key_center'][0]+u.c.KEYS[58]['key_center'][0])/2,-.035,.014));cam.location=target+Vector((0,0,.8) if view=='OVERHEAD' else (.11,-.48,.22));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
 data=bpy.data.curves.new('ENDPOINT_LABEL','FONT');data.body='E5 endpoint: +35 ms / PROVISIONAL ACTIVE FLEX / HUMAN PENDING';data.size=.0046;ob=bpy.data.objects.new('ENDPOINT_LABEL',data);sc.collection.objects.link(ob);ob.rotation_euler=cam.rotation_euler;ob.location=cam.matrix_world@Vector((-.162,.081,-.38));ob.color=(1,.3,.1,1)
 file=folder/f'ENDPOINT_{view}.png';sc.render.filepath=str(file);bpy.ops.render.render(write_still=True);manifest.append(dict(file=str(file),time=2.956426,view=view,resolution=[1280,720],purpose='endpoint visual risk check, not dynamic proof'));bpy.data.objects.remove(ob,do_unlink=True)
(O/'ENDPOINT_STILL_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
print('MOTION_COLLOCATION_KEYS_EXACT',len(times),'ENDPOINT_STILLS',len(manifest),flush=True)
