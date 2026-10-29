import bpy,json,sys,numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
data=json.loads((P/'RENDER_INPUT_R1.json').read_text());V=np.load(P/'evaluated_motion.npz')['vertices'];S=Matrix(data['reflection']);SR=S.to_3x3()
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=600;sc.render.resolution_y=660;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.world=bpy.data.worlds.new('UNSAVED_REVIEW_WORLD');sc.world.color=(.10,.12,.15);sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
sh=sc.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.66,.68,.71);sh.background_type='WORLD';sh.show_cavity=False;sh.show_shadows=True;sh.shadow_intensity=0;sh.show_specular_highlight=True
cd=bpy.data.cameras.new('UNSAVED_REVIEW_CAMERA');cd.type='ORTHO';cd.clip_start=.001;cd.clip_end=10
cam=bpy.data.objects.new('UNSAVED_REVIEW_CAMERA',cd);sc.collection.objects.link(cam);sc.camera=cam
me=bpy.data.meshes.new('EVALUATED_LEFT_DISPLAY');me.from_pydata(V[0].tolist(),[],data['faces'])
for p,smooth in zip(me.polygons,data['smooth']):p.use_smooth=smooth
ob=bpy.data.objects.new('EVALUATED_LEFT_DISPLAY',me);sc.collection.objects.link(ob)
cams={};base_cam=json.loads((ROOT/'audits/right_hand_first_web_production_weight_qualification_r1/APPROVED_POSE_REGRESSION_R1.json').read_text())['poses'][0]['cameras']
for view in ['DEFAULT_TEACHING_VIEW','NORMAL_ORBIT_VIEW','REASONABLE_CLOSE_VIEW']:
 job=base_cam[view];dR=Vector(job['direction']).normalized();rightR=Vector((0,0,1)).cross(dR).normalized();upR=dR.cross(rightR).normalized();d=SR@dR;u=SR@upR;r=u.cross(d).normalized()
 # Fixed framing throughout clip; full-motion union avoids tracking cameras hiding jitter.
 if view in ['DEFAULT_TEACHING_VIEW','NORMAL_ORBIT_VIEW']:
  points=(V if view=='NORMAL_ORBIT_VIEW' else V[::10]).reshape(-1,3);axes=np.array([list(r),list(u),list(d)]);pr=points@axes.T;center=Vector(((pr.min(0)+pr.max(0))/2)@axes);extent=pr.max(0)-pr.min(0);scale=max(extent[0]*660/600,extent[1])*1.12
 else:
  center=S@Vector(job['center']);scale=.235 if view=='NORMAL_ORBIT_VIEW' else .16
 rot=Matrix((r,u,d)).transposed().to_4x4();rot.translation=center+d*.8
 cams[view]={'matrix_world':list(map(list,rot)),'ortho_scale_m':float(scale),'resolution':[600,660],'fixed_camera':True,'mirror_of_right_camera_orientation':True}
for view,job in cams.items():
 if '--orbit-only' in sys.argv and view!='NORMAL_ORBIT_VIEW':continue
 folder=P/'_render_frames'/view;folder.mkdir(parents=True,exist_ok=True);cam.matrix_world=Matrix(job['matrix_world']);cd.ortho_scale=job['ortho_scale_m']
 for j in range(210):
  me.vertices.foreach_set('co',V[j*2].astype(np.float32).ravel());me.update();sc.render.filepath=str(folder/f'{j:04}.png');bpy.ops.render.render(write_still=True)
 print('VIEW_COMPLETE',view,flush=True)
(P/'REVIEW_CAMERAS_R1.json').write_text(json.dumps(cams,indent=2),encoding='utf-8')
print('FULL_7S_THREE_VIEWS_RENDERED',flush=True)
