import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from trial_common import *
from bpy_extras.object_utils import world_to_camera_view
rows=read(PREV/'EXACT_TRUE_SIDE_MANIFEST.json');ref=next(r for r in rows if r['identity']=='ORIGINAL' and r['variant']=='NATIVE');rot=np.array(ref['camera_matrix'])[:3,:3]
sc,mesh,rig,left=open_scene(SOURCE);c.settime(sc,2.6);base=np.load(OUT/'BASE__C1_2_600000.npz')['V'];target=base[A].mean(0)
cd=bpy.data.cameras.new('TRUE_SIDE_CLOSE_ORIGIN');cam=bpy.data.objects.new(cd.name,cd);sc.collection.objects.link(cam);mat=np.eye(4);mat[:3,:3]=rot;mat[:3,3]=target+.055*rot[:,2];cam.matrix_world=Matrix(mat);cd.type='ORTHO';cd.ortho_scale=.060;cd.clip_start=.0001;sc.camera=cam
out=[]
for kind in ['BASE','A1','A2']:
 v=np.load(OUT/(kind+'__C1_2_600000.npz'))['V'];me=bpy.data.meshes.new('ACTUAL_EVALUATED_TRUE_SIDE');me.from_pydata(v.tolist(),[],F.tolist());me.update()
 for m in mesh.data.materials:me.materials.append(m)
 for p,q in zip(me.polygons,mesh.data.polygons):p.use_smooth=q.use_smooth;p.material_index=q.material_index
 ob=bpy.data.objects.new('RENDER_'+kind,me);sc.collection.objects.link(ob);ob.color=mesh.color;mesh.hide_render=True
 sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=960;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';shade=sc.display.shading;shade.light='STUDIO';shade.color_type='OBJECT';shade.show_shadows=True;shade.show_cavity=False;shade.show_specular_highlight=False
 path=OUT/'raw_renders'/(kind+'__C1_2_600000__TRUE_SIDE_NEAR.png');assert not path.exists();sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 out.append({'candidate':kind,'pose':'C1_2_600000','view':'TRUE_SIDE','path':str(path),'matrix':[list(r) for r in cam.matrix_world],'ortho_scale':.06,'resolution':[960,720],'clip_start':.0001,'reason':'Same bone-plane orientation; place orthographic camera 55mm from local target as original true-side diagnostic, instead of behind foreground key geometry. No object hidden except original right hand replaced by exact evaluated copy.','evaluated_snapshot':str(OUT/(kind+'__C1_2_600000.npz')),'same_flat_shading':True})
 mesh.hide_render=False;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(me)
save('TRUE_SIDE_REVISED_RENDER_MANIFEST.json',out);protection('TRUE_SIDE_REVISED_INPUT_RECEIPT.json')
