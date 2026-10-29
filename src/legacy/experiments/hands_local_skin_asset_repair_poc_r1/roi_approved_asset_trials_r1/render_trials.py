import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from trial_common import *
from bpy_extras.object_utils import world_to_camera_view
extra=os.environ.get('TRIAL_RENDER_EXTRA')=='1'
if extra:
 ctx=read(OUT/'EXTRA_POSE_CONTEXT.json');POSES=[(ctx['label'],ctx['time'])]
diag=read(PREV/'DIAGNOSTIC_RENDER_MANIFEST.json')+read(PREV/'EXACT_TRUE_SIDE_MANIFEST.json')
def diagrow(view):return next(x for x in diag if x['identity']=='ORIGINAL' and x['variant']=='NATIVE' and x['view']==view)
true=diagrow('EXACT_SOURCE_TRUE_SIDE');rev=diagrow('WEB_REVERSE')
matched=read(POSE/'MATCHED_CAMERA_RENDER_MANIFEST.json');side=next(x for x in matched if x['identity']=='ORIGINAL' and x['view']=='AUX_INDEX_SIDE')
sc,mesh,rig,left=open_scene(SOURCE);c.settime(sc,2.6)
save(('EXTRA_' if extra else '')+'RENDER_STYLE_RECEIPT.json',{'source_engine':sc.render.engine,'source_color_type':sc.display.shading.color_type,'source_mesh_color':list(mesh.color),'flat_faces':sum(not f.use_smooth for f in mesh.data.polygons),'render_method':'Actual validated evaluated vertices copied verbatim to render-only meshes; original material slots, UVs and flat flags copied; no geometric smoothing or retouch.','projection_scope':'Same camera, render settings and pose per row for all compared candidates; local views translate to BASE ROI centers per pose. True side orientation fixed relative original C1 bone plane at 2.6s.'})
records=[]
for label,t in POSES:
 setpose(sc,rig,label,t);data=np.load(OUT/('BASE__'+label+'.npz'));base=data['V'];leftdata=data['L'];targetA=base[A].mean(0);targetB=base[np.union1d(B,S)].mean(0)
 cams={}
 for name,target,scale,mat in [('A_CLOSE',targetA,.065,np.eye(4)),('B_CLOSE',targetB,.060,np.eye(4)),('TRUE_SIDE',targetA,.060,np.array(true['camera_matrix'])),('B_REVERSE',targetB,.060,np.array(rev['camera_matrix'])),('S_SIDE',targetB,.060,np.array(side['camera_matrix']))]:
  cd=bpy.data.cameras.new('TRIAL_CAMERA_'+name);cam=bpy.data.objects.new(cd.name,cd);sc.collection.objects.link(cam);cd.type='ORTHO';cd.ortho_scale=scale
  mat=mat.copy();mat[:3,3]=target+mat[:3,2]*.4;cam.matrix_world=Matrix(mat);cams[name]=cam
 cams['OVERHEAD']=bpy.data.objects[MAN['cameras']['OVERHEAD']]
 for kind in ['BASE','A1','A2','B1','B2']:
  snap=np.load(OUT/(kind+'__'+label+'.npz'));v=snap['V'];me=bpy.data.meshes.new('EVALUATED_TRIAL_RENDER_ONLY');me.from_pydata(v.tolist(),[],F.tolist());me.update()
  for mat in mesh.data.materials:me.materials.append(mat)
  for layer in mesh.data.uv_layers:
   dest=me.uv_layers.new(name=layer.name)
   for i,uv in enumerate(layer.data):dest.data[i].uv=uv.uv
  for p,q in zip(me.polygons,mesh.data.polygons):p.use_smooth=q.use_smooth;p.material_index=q.material_index
  ob=bpy.data.objects.new('ACTUAL_EVALUATED_'+kind,me);sc.collection.objects.link(ob);ob.color=mesh.color;ob.show_wire=mesh.show_wire;ob.show_all_edges=mesh.show_all_edges
  hidden=mesh.hide_render;mesh.hide_render=True
  views=['A_CLOSE'] if kind in ['A1','A2'] else ['B_CLOSE'] if kind in ['B1','B2'] else ['A_CLOSE','B_CLOSE']
  if kind in ['BASE','B1','B2']:views+=['S_SIDE']
  if label=='C1_2_600000':
   views+=['OVERHEAD']
   views+=['TRUE_SIDE'] if kind in ['BASE','A1','A2'] else ['B_REVERSE']
   if kind=='BASE':views+=['B_REVERSE']
  for view in views:
   sc.camera=cams[view];sc.render.resolution_x=1280 if view=='OVERHEAD' else 960;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
   # Actual coarse flat shading is preserved; object color matches the source file.
   sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='OBJECT';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=False;sc.display.shading.show_specular_highlight=False
   path=OUT/'raw_renders'/(kind+'__'+label+'__'+view+'.png');path.parent.mkdir(exist_ok=True);assert not path.exists();sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)
   def proj(P):
    return [[u.x*sc.render.resolution_x,(1-u.y)*720] for p in P for u in [world_to_camera_view(sc,sc.camera,Vector(p))]]
   records.append({'candidate':kind,'pose':label,'view':view,'path':str(path),'matrix':[list(r) for r in sc.camera.matrix_world],'ortho_scale':sc.camera.data.ortho_scale,'resolution':[sc.render.resolution_x,720],'evaluated_snapshot':str(OUT/(kind+'__'+label+'.npz')),'roi_pixels':{k:proj(v[np.array(PROPOSAL['regions'][k]['core_vertex_ids'])]) for k in ['A','B','S']},'same_flat_shading':True})
   print('RENDERED',kind,label,view,flush=True)
  mesh.hide_render=hidden;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(me)
 for cam in list(cams.values()):
  if cam.name.startswith('TRIAL_CAMERA'):bpy.data.objects.remove(cam,do_unlink=True)
save(('EXTRA_' if extra else '')+'RENDER_MANIFEST.json',records);protection(('EXTRA_' if extra else '')+'RENDER_INPUT_RECEIPT.json')
