import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from support import *
import support as s
from bpy_extras.object_utils import world_to_camera_view
sc,rig,mesh,left,lrig=s.open_scene(SOURCE);c.settime(sc,2.6)
top=read(OUT/'NATIVE_TOPOLOGY.json');meta0=read(OUT/'ORIGINAL_SNAPSHOT.json');j=meta0['joints']
h=np.array(j['INDEX_MCP_R']['head_world']);p=np.array(j['INDEX_PIP_R']['head_world']);d=np.array(j['INDEX_DIP_R']['head_world'])
normal=np.cross(p-h,d-p);normal/=np.linalg.norm(normal);target=(h+p)/2
cd=bpy.data.cameras.new('DIAG_EXACT_SOURCE_INDEX_SAGITTAL');cam=bpy.data.objects.new(cd.name,cd);sc.collection.objects.link(cam)
cam.location=target+.055*normal;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=.105;cd.clip_start=.0001;sc.camera=cam
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
neutral=bpy.data.materials.new('DIAG_SAME_LIGHT_NEUTRAL');neutral.diffuse_color=(.66,.69,.72,1)
rows=[]
for identity in ['ORIGINAL','REJECTED_GEOMETRY_PASS']:
 z=np.load(OUT/(identity+'_SNAPSHOT.npz'));a=np.load(OUT/(identity+'_ALIGNED.npz'));meta=read(OUT/(identity+'_SNAPSHOT.json'))
 for variant,V in [('NATIVE',z['V']),('NEUTRAL_STUDIO_NO_SHADOW',z['V']),('CORRECTIVE_OFF_DIAG_ONLY',z['OFF']),('MCP_RIGID_A_DIAG_ONLY',a['RAW_RIGID_MCP'])]:
  me=bpy.data.meshes.new('DIAG_EXACT_SURFACE');me.from_pydata(V.tolist(),[],top['faces']);me.update();ob=bpy.data.objects.new(me.name,me);sc.collection.objects.link(ob)
  if variant=='NATIVE':
   for mat in mesh.data.materials:me.materials.append(mat)
  else:me.materials.append(neutral)
  shade=sc.display.shading;shade.color_type='MATERIAL';shade.light='STUDIO';shade.show_shadows=False;shade.show_cavity=False;shade.show_specular_highlight=False
  mesh.hide_render=True;dest=OUT/f'{identity}__{variant}__EXACT_SOURCE_TRUE_SIDE.png';assert not dest.exists();sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
  def proj(P):
   return [[q.x*1280,(1-q.y)*720] for q in [world_to_camera_view(sc,cam,Vector(v)) for v in P]]
  bones={b:dict(world=[meta['joints'][b]['head_world'],meta['joints'][b]['tail_world']],pixels=proj([meta['joints'][b]['head_world'],meta['joints'][b]['tail_world']])) for b in ['INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R']}
  # Rigid diagnostic uses rest axes transformed by the same rigid MCP matrix.
  if variant=='MCP_RIGID_A_DIAG_ONLY':
   D=z['D'][meta['bone_names'].index('INDEX_MCP_R')];rm=np.linalg.inv(np.array(meta['mesh_world']))@np.array(meta['rig_world'])
   for b in bones:
    M=np.array(meta['joints'][b]['rest']);end=('INDEX_PIP_R' if b=='INDEX_MCP_R' else 'INDEX_DIP_R' if b=='INDEX_PIP_R' else None)
    R=np.array([M[:3,3],np.array(meta['joints'][end]['rest'])[:3,3] if end else M[:3,3]+M[:3,1]*.015]);P=(np.c_[R,np.ones(2)]@(D@rm).T)[:,:3];bones[b]=dict(world=P,pixels=proj(P))
  P=V[np.array(top['faces'])];cent=P.mean(1);N=np.cross(P[:,1]-P[:,0],P[:,2]-P[:,0])+np.cross(P[:,2]-P[:,0],P[:,3]-P[:,0]);N/=np.maximum(np.linalg.norm(N,axis=1)[:,None],1e-15)
  rows.append(dict(identity=identity,variant=variant,view='EXACT_SOURCE_TRUE_SIDE',path=str(dest),camera_matrix=np.array(cam.matrix_world),camera_type='ORTHO',ortho_scale=cd.ortho_scale,bones=bones,all_vertex_pixels=proj(V),face_centroid_pixels=proj(cent),face_normal_end_pixels=proj(cent+.0015*N),source_sagittal_normal=normal))
  mesh.hide_render=False;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(me)
save('EXACT_TRUE_SIDE_MANIFEST.json',rows)
sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']];rig.show_in_front=True;sc.display.shading.show_shadows=True
dest=OUT/'ANATOMICAL_DIAGNOSTIC_WITH_TRUE_SIDE.blend';assert not dest.exists();bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=True)
protection('TRUE_SIDE_INPUT_RECEIPT.json')
print('EXACT_TRUE_SIDE_COMPLETE',flush=True)
