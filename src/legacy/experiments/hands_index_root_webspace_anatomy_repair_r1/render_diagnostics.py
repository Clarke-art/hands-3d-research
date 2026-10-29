import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from support import *
import support as s
from bpy_extras.object_utils import world_to_camera_view
sc,rig,mesh,left,lrig=s.open_scene(SOURCE);c.settime(sc,2.6);top=read(OUT/'NATIVE_TOPOLOGY.json');F=top['faces'];edges=np.array(top['edges'],int)
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
views={'OVERHEAD':bpy.data.objects[MAN['cameras']['OVERHEAD']]}
for name,eye,target,scale,typ in [('INDEX_TRUE_SIDE',(.015,.020,.045),(.13,.020,.035),.105,'ORTHO'),('WEB_CLOSE',(.025,-.135,.14),(.114,-.014,.030),.100,'ORTHO'),('PALM_OBLIQUE',(.33,-.30,.22),(.145,-.025,.020),.22,'PERSP'),('WEB_REVERSE',(.235,-.10,.075),(.115,-.014,.03),.10,'ORTHO')]:
 cd=bpy.data.cameras.new('DIAG_'+name);cam=bpy.data.objects.new('DIAG_'+name,cd);sc.collection.objects.link(cam);cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.type=typ;cd.ortho_scale=scale;cd.lens=55;views[name]=cam
neutral=bpy.data.materials.new('DIAGNOSTIC_NEUTRAL_ONLY');neutral.diffuse_color=(.66,.69,.72,1)
rows=[];hide_original=mesh.hide_render
def tx(V,M):return (np.c_[V,np.ones(len(V))]@np.array(M).T)[:,:3]
for identity in ['ORIGINAL','REJECTED_GEOMETRY_PASS']:
 z=np.load(OUT/(identity+'_SNAPSHOT.npz'));meta=read(OUT/(identity+'_SNAPSHOT.json'));aligned=np.load(OUT/(identity+'_ALIGNED.npz'));names=meta['bone_names']
 variants={'NATIVE':z['V'],'NEUTRAL_NO_SHADOW':z['V'],'CORRECTIVE_OFF_DIAG_ONLY':z['OFF'],'RAW_WRIST_ALIGNED_DIAG_ONLY':aligned['RAW_RIGID_WRIST'],'MCP_RIGID_A_DIAG_ONLY':aligned['RAW_RIGID_MCP']}
 for variant,V in variants.items():
  me=bpy.data.meshes.new('DIAG_READONLY_EVALUATED_GEOMETRY');me.from_pydata(V.tolist(),[],F);me.update();ob=bpy.data.objects.new('DIAG_COPY_'+identity+'_'+variant,me);sc.collection.objects.link(ob)
  # Surface data are copied from actual evaluated/basis coordinates; no edits.
  if variant=='NATIVE':
   for mat in mesh.data.materials:me.materials.append(mat)
   # Original material UVs are copied verbatim for same native appearance.
   for layer in mesh.data.uv_layers:
    target=me.uv_layers.new(name=layer.name)
    for i,d in enumerate(layer.data):target.data[i].uv=d.uv
  else:me.materials.append(neutral)
  for p,src in zip(me.polygons,mesh.data.polygons):p.use_smooth=src.use_smooth;p.material_index=src.material_index if variant=='NATIVE' else 0
  mesh.hide_render=True
  shade=sc.display.shading;shade.light='STUDIO';shade.color_type='MATERIAL';shade.show_shadows=(variant=='NATIVE');shade.show_cavity=False;shade.show_specular_highlight=False
  if variant=='NEUTRAL_NO_SHADOW':shade.light='FLAT'
  selected=list(views) if variant in ['NATIVE','NEUTRAL_NO_SHADOW'] else ['INDEX_TRUE_SIDE','WEB_CLOSE']
  for view in selected:
   cam=views[view];sc.camera=cam;name=f'{identity}__{variant}__{view}';dest=OUT/(name+'.png');assert not dest.exists();sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
   def proj(P):
    out=[]
    for p in P:
     uv=world_to_camera_view(sc,cam,Vector(p));out.append([uv.x*1280,(1-uv.y)*720])
    return out
   bone_points={}
   for bone in ['INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R','THUMB_CMC_R','THUMB_MCP_R']:
    if variant.startswith('RAW_') or variant.startswith('MCP_RIGID'):
     D=z['D'][names.index('WRIST_R' if variant.startswith('RAW_') else 'INDEX_MCP_R')];rest=np.array(meta['joints'][bone]['rest']);rig_to_mesh=np.linalg.inv(np.array(meta['mesh_world']))@np.array(meta['rig_world']);hp=rest[:3,3]
     if bone=='INDEX_MCP_R':tail=np.array(meta['joints']['INDEX_PIP_R']['rest'])[:3,3]
     elif bone=='INDEX_PIP_R':tail=np.array(meta['joints']['INDEX_DIP_R']['rest'])[:3,3]
     else:tail=hp+rest[:3,1]*.015
     P=tx(tx(np.array([hp,tail]),rig_to_mesh),D)
    else:P=np.array([meta['joints'][bone]['head_world'],meta['joints'][bone]['tail_world']])
    bone_points[bone]=dict(world=P,pixels=proj(P))
   roipixels={k:proj(V[r['vertices']]) for k,r in meta['rois'].items() if k in ['A','A_SHAFT','B']}
   rows.append(dict(identity=identity,variant=variant,view=view,path=str(dest),camera_matrix=np.array(cam.matrix_world),camera_type=cam.data.type,ortho_scale=cam.data.ortho_scale,bones=bone_points,roi_pixels=roipixels,all_vertex_pixels=proj(V)))
  mesh.hide_render=hide_original;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(me)
 # Weight falsecolor: actual unchanged weights on actual evaluated skin.
 for group in ['WRIST_R','INDEX_MCP_R','THUMB_CMC_R']:
  V=z['V'];me=bpy.data.meshes.new('DIAG_ACTUAL_WEIGHT_MAP');me.from_pydata(V.tolist(),[],F);me.update();me.materials.append(neutral);ob=bpy.data.objects.new('DIAG_WEIGHT_'+group,me);sc.collection.objects.link(ob)
  col=me.color_attributes.new(name='ACTUAL_FROZEN_WEIGHT',type='FLOAT_COLOR',domain='POINT');w=z['W'][:,names.index(group)]
  for i,t in enumerate(w):col.data[i].color=(float(t),float(.25+.3*(1-abs(2*t-1))),float(1-t),1)
  me.color_attributes.active_color=col;mesh.hide_render=True;sc.display.shading.color_type='VERTEX';sc.display.shading.light='FLAT';sc.display.shading.show_shadows=False
  for view in ['INDEX_TRUE_SIDE','WEB_CLOSE']:
   sc.camera=views[view];dest=OUT/f'{identity}__WEIGHT_{group}__{view}.png';assert not dest.exists();sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
  mesh.hide_render=hide_original;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(me)
sc.display.shading.color_type='MATERIAL';sc.display.shading.light='STUDIO';sc.display.shading.show_shadows=True;mesh.hide_render=hide_original;sc.camera=views['OVERHEAD']
rig.show_in_front=True
save('DIAGNOSTIC_RENDER_MANIFEST.json',rows);protection('DIAGNOSTIC_RENDER_INPUT_RECEIPT.json')
# Default actual original C1 state with all original deformers restored.
dest=OUT/'ANATOMICAL_DIAGNOSTIC_ONLY.blend';assert not dest.exists();bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=True)
print('DIAGNOSTIC_RENDER_COMPLETE',len(rows),flush=True)
