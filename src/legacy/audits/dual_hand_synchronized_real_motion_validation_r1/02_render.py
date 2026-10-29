import bpy,json,sys,numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
data=json.loads((P/'RENDER_INPUT_R1.json').read_text());V=np.load(P/'evaluated_dual_motion.npz')
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.world=bpy.data.worlds.new('UNSAVED_REVIEW_WORLD');sc.world.color=(.10,.12,.15);sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
sh=sc.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.66,.68,.71);sh.background_type='WORLD';sh.show_cavity=False;sh.show_shadows=True;sh.shadow_intensity=0;sh.show_specular_highlight=True
cd=bpy.data.cameras.new('REVIEW_CAMERA');cd.type='ORTHO';cd.clip_start=.001;cd.clip_end=10;cam=bpy.data.objects.new('REVIEW_CAMERA',cd);sc.collection.objects.link(cam);sc.camera=cam
obs={}
for side in ['L','R']:
 me=bpy.data.meshes.new('EVALUATED_'+side);me.from_pydata(V[side][0].tolist(),[],data['faces'][side])
 for poly,smooth in zip(me.polygons,data['smooth'][side]):poly.use_smooth=smooth
 ob=bpy.data.objects.new('EVALUATED_'+side,me);sc.collection.objects.link(ob);obs[side]=ob
S=Matrix(json.loads((ROOT/'audits/left_hand_real_motion_retarget_validation_r1/RENDER_INPUT_R1.json').read_text())['reflection']).to_3x3()
d=Vector((-.38,-.924,.018)).normalized();r=Vector((0,0,1)).cross(d).normalized();u=d.cross(r).normalized()
jobs={'DUAL_TEACHING_VIEW':{'sides':['L','R'],'axes':[r,u,d],'resolution':[1200,660]}}
for side in ['R','L']:
 d=Vector((.19980031,-.93906146,.27972043)).normalized();r=Vector((0,0,1)).cross(d).normalized();u=d.cross(r).normalized()
 if side=='L':d=S@d;u=S@u;r=u.cross(d).normalized()
 jobs[side+'_DETAIL_VIEW']={'sides':[side],'axes':[r,u,d],'resolution':[600,660]}
cameras={}
for view,job in jobs.items():
 axes=np.array([list(x) for x in job['axes']]);points=np.concatenate([V[s].reshape(-1,3) for s in job['sides']]);proj=points@axes.T;extent=np.ptp(proj,axis=0);center=Vector(((proj.min(0)+proj.max(0))*.5)@axes);w,height=job['resolution'];scale=max(extent[0]*max(w,height)/w,extent[1]*max(w,height)/height)*1.13
 r,u,d=job['axes'];rot=Matrix((r,u,d)).transposed().to_4x4();rot.translation=center+d*.8;cam.matrix_world=rot;cd.ortho_scale=scale;sc.render.resolution_x=w;sc.render.resolution_y=height
 for s,ob in obs.items():ob.hide_render=s not in job['sides']
 cameras[view]={'matrix_world':[list(x) for x in rot],'scale':float(scale),'resolution':[w,height],'fixed_camera':True,'framing':'FULL_421_OBSERVATION_UNION','native_smooth_flags':True}
 folder=P/'_render_frames'/view;folder.mkdir(parents=True,exist_ok=True)
 for j in range(210):
  for s in job['sides']:obs[s].data.vertices.foreach_set('co',V[s][j*2].astype(np.float32).ravel());obs[s].data.update()
  sc.render.filepath=str(folder/f'{j:04}.png');bpy.ops.render.render(write_still=True)
 print('VIEW_COMPLETE',view,flush=True)
(P/'REVIEW_CAMERAS_R1.json').write_text(json.dumps(cameras,indent=2),encoding='utf-8')
