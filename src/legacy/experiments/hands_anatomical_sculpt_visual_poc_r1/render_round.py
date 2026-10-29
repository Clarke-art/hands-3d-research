import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from sculpt_common import *
from bpy_extras.object_utils import world_to_camera_view
roundno=int(os.environ.get('SCULPT_RENDER_ROUND','1'))
diag=read(PREV/'EXACT_TRUE_SIDE_MANIFEST.json');true=next(r for r in diag if r['identity']=='ORIGINAL' and r['variant']=='NATIVE')
other=read(PREV/'DIAGNOSTIC_RENDER_MANIFEST.json');rev=next(r for r in other if r['identity']=='ORIGINAL' and r['variant']=='NATIVE' and r['view']=='WEB_REVERSE')
matched=read(POSE/'MATCHED_CAMERA_RENDER_MANIFEST.json');side=next(r for r in matched if r['identity']=='ORIGINAL' and r['view']=='AUX_INDEX_SIDE')
base=np.load(PREV/'ORIGINAL_SNAPSHOT.npz')['V']
targetA=base[np.array(PROPOSAL['regions']['A']['core_vertex_ids'])].mean(0);targetB=base[np.union1d(B,S)].mean(0)
oldroot=PARENT/'roi_approved_asset_trials_r1'
identities=[('BASE',SOURCE),('OLD_A',oldroot/'A_BASIS_CANDIDATE_2_NOT_APPROVED.blend'),('NEW_A',OUT/('A_SCULPT_ROUND_'+str(roundno)+'_NOT_APPROVED.blend')),('OLD_B',oldroot/'B1_WEIGHTS_NOT_APPROVED.blend'),('NEW_B',OUT/('B_SCULPT_ROUND_'+str(roundno)+'_NOT_APPROVED.blend'))]
records=[]
for ident,path in identities:
 sc,mesh,rig,left=open_scene(path);c.settime(sc,2.6)
 # All geometry, including the keyboard and other hand, remains visible.
 cams={'OVERHEAD':bpy.data.objects[MAN['cameras']['OVERHEAD']]}
 for view,target,rot,scale in [('A_CLOSE',targetA,np.eye(3),.067),('A_TRUE_SIDE',targetA,np.array(true['camera_matrix'])[:3,:3],.063),('B_CLOSE',targetB,np.eye(3),.063),('B_NEAR_SIDE',targetB,np.array(side['camera_matrix'])[:3,:3],.068),('B_REVERSE',targetB,np.array(rev['camera_matrix'])[:3,:3],.075)]:
  cd=bpy.data.cameras.new('SCULPT_REVIEW_'+view);cam=bpy.data.objects.new(cd.name,cd);sc.collection.objects.link(cam);m=np.eye(4);m[:3,:3]=rot;m[:3,3]=target+rot[:,2]*(.055 if view=='A_TRUE_SIDE' else .4);cam.matrix_world=Matrix(m);cd.type='ORTHO';cd.ortho_scale=scale;cd.clip_start=.0001;cams[view]=cam
 cd=bpy.data.cameras.new('SCULPT_REVIEW_A_PERSPECTIVE');cam=bpy.data.objects.new(cd.name,cd);sc.collection.objects.link(cam);cam.location=Vector(targetA+[-.075,-.045,.065]);cam.rotation_euler=(Vector(targetA)-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='PERSP';cd.lens=70;cd.clip_start=.0001;cams['A_PERSPECTIVE']=cam
 views=['OVERHEAD']+(['A_CLOSE','A_TRUE_SIDE','A_PERSPECTIVE'] if ident in ['OLD_A','NEW_A'] else ['B_CLOSE','B_NEAR_SIDE','B_REVERSE'] if ident in ['OLD_B','NEW_B'] else ['A_CLOSE','A_TRUE_SIDE','A_PERSPECTIVE','B_CLOSE','B_NEAR_SIDE','B_REVERSE'])
 for view in views:
  sc.camera=cams[view];sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1280;sc.render.resolution_y=720 if view=='OVERHEAD' else 960;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
  shade=sc.display.shading;shade.light='STUDIO';shade.color_type='OBJECT';shade.show_shadows=True;shade.show_cavity=False;shade.show_specular_highlight=False
  dest=OUT/'round_1_renders'/(ident+'__'+view+'.png') if roundno==1 else OUT/('round_'+str(roundno)+'_renders')/(ident+'__'+view+'.png')
  dest.parent.mkdir(exist_ok=True);assert not dest.exists();sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
  vv,tt,ff=coords(mesh)
  records.append({'identity':ident,'round':roundno,'source_blend':str(path),'view':view,'path':str(dest),'camera_matrix':[list(r) for r in sc.camera.matrix_world],'type':sc.camera.data.type,'ortho_scale':sc.camera.data.ortho_scale,'lens':sc.camera.data.lens,'resolution':[sc.render.resolution_x,sc.render.resolution_y],'material_object_color':list(mesh.color),'flat_flags_hash':c.digest([f.use_smooth for f in mesh.data.polygons]),'lighting':dict(light=shade.light,studio_light=shade.studio_light,rotation=shade.studiolight_rotate_z,shadows=shade.show_shadows,cavity=shade.show_cavity),'frame':sc.frame_current,'time':2.6,'hidden_model_objects_added':False})
  print('RENDERED',ident,view,flush=True)
save('ROUND_'+str(roundno)+'_RENDER_MANIFEST.json',records);protection('ROUND_'+str(roundno)+'_RENDER_INPUT_RECEIPT.json')

