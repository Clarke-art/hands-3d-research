import sys,json,math,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Vector
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'))
import blender_utils as u
PRE=O.parent/'hands_c01_s1_constrained_solver_feasibility_r1';folder=O/'stills';folder.mkdir(exist_ok=True);manifest=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def curve(name,pts,col,sc):
 data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=.00027;ln=data.splines.new('POLY');ln.points.add(len(pts)-1)
 for p,q in zip(ln.points,pts):p.co=(*q,1)
 ob=bpy.data.objects.new(name,data);sc.collection.objects.link(ob);ob.color=col;return ob
for label,path,info in [('A',PRE/'S1_CONSTRAINED_DIAGNOSTIC_R1.blend',json.loads((PRE/'ACTUAL_VALIDATION_2.json').read_text())),('B',O/'S1_ANATOMY_PREPARATION_DIAGNOSTIC_R1.blend',json.loads((O/'B_ACTUAL_2.json').read_text()))]:
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[info['rig']];mesh=bpy.data.objects[info['mesh']]
 assert u.digest(u.native(mesh,rig))==u.pf['right_native_sha256']
 V,F=u.coords(mesh);snap=np.load(PRE/'ACTUAL_SKIN_2.npz' if label=='A' else O/'B_ACTUAL_SKIN_2.npz')['vertices'];assert np.max(abs(V-snap))<1e-7
 for view in ['OVERHEAD','SIDE_OBLIQUE']:
  sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.display.shading.light='STUDIO';sc.display.shading.color_type='OBJECT';sc.display.shading.show_shadows=False;sc.display.shading.show_cavity=True;sc.display.shading.cavity_type='BOTH';sc.display.shading.background_type='WORLD';sc.world.color=(.08,.08,.08)
  cam=bpy.data.objects[info['cameras'][view]];sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.34
  target=Vector(((u.c.KEYS[46]['key_center'][0]+u.c.KEYS[58]['key_center'][0])/2,-.035,.014));cam.location=target+Vector((0,0,.8) if view=='OVERHEAD' else (.11,-.48,.22));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
  overlays=[]
  def textob(body,x,y,size=.004,col=(1,.3,.08,1)):
   data=bpy.data.curves.new('REVIEW_LABEL','FONT');data.body=body;data.size=size;ob=bpy.data.objects.new('REVIEW_LABEL',data);sc.collection.objects.link(ob);ob.rotation_euler=cam.rotation_euler;ob.location=cam.matrix_world@Vector((x,y,-.38));ob.color=col;overlays.append(ob)
  textob('A: HUMAN ANATOMY FAIL | middle MCP spread -25.00 deg' if label=='A' else 'B: HUMAN PENDING | middle MCP spread -6.73 deg',-.162,.081,.005)
  textob('Cyan: MIDDLE chain | Purple: RING chain | projected actual bones',-.162,-.086,.0037,(.9,.9,.9,1))
  def project(v):
   z=cam.matrix_world.inverted()@Vector(v);z.z=-.40;return cam.matrix_world@z
  annotations=[]
  for digit,color in [('MIDDLE',(.02,1,1,1)),('RING',(.95,.05,1,1))]:
   bones=[rig.pose.bones[f'{digit}_{j}_R'] for j in ['MCP','PIP','DIP']]
   real=[<REDACTED_EMAIL> for b in bones]+[rig.matrix_world@bones[-1].tail];draw=[project(v) for v in real]
   overlays.append(curve(digit+'_PROJECTED_BONE_CHAIN',draw,color,sc))
   annotations.append(dict(digit=digit,bone_names=[b.name for b in bones],actual_world_points_m=[list(p) for p in real],overlay='Orthographic camera projection onto foreground diagnostic plane, screen-aligned; does not move bones or skin'))
   if digit=='MIDDLE':
    for ji,joint in enumerate(['MCP','PIP','DIP']):
     p=cam.matrix_world.inverted()@draw[ji];textob('MIDDLE '+joint,p.x+.002,p.y+(.002 if view=='OVERHEAD' else [-.006,.006,-.006][ji]),.0033,color)
  dest=folder/f'{label}_{view}.png';sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
  manifest.append(dict(label=label,view=view,file=str(dest),sha256=sha(dest),resolution=[1280,720],camera_world_matrix=[list(r) for r in cam.matrix_world],ortho_scale=cam.data.ortho_scale,source_blend=str(path),scene=sc.name,native_verified=True,actual_snapshot_verified=True,annotations=annotations,Human_visual='FAIL' if label=='A' else 'PENDING'))
  for ob in overlays:bpy.data.objects.remove(ob,do_unlink=True)
assert len(manifest)==4
for v in ['OVERHEAD','SIDE_OBLIQUE']:
 a=next(x for x in manifest if x['label']=='A' and x['view']==v);b=next(x for x in manifest if x['label']=='B' and x['view']==v);assert np.max(abs(np.array(a['camera_world_matrix'])-b['camera_world_matrix']))<1e-7
(O/'STILL_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
print('MATCHED_AB_STILLS',len(manifest),'NO_SOURCE_SAVE',flush=True)

