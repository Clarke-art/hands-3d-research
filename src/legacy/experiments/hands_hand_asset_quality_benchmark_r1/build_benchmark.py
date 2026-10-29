import bpy,sys,os,json,math,hashlib
from pathlib import Path
import numpy as np
from mathutils import Matrix,Vector,Quaternion
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];os.environ.update(TEMP=str(OUT),TMP=str(OUT))
def save(n,x):
 with (OUT/n).open('w',encoding='utf8') as f:json.dump(x,f,indent=2,ensure_ascii=False,default=lambda v:v.item() if hasattr(v,'item') else str(v))
def point(m,v):return np.array(m@Vector(v))
def unit(a):return a/np.linalg.norm(a)
def evaluated(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
 v=np.array([list(<REDACTED_EMAIL>) for v in me.vertices]);f=[list(p.vertices) for p in me.polygons];ev.to_mesh_clear();return v,f
def frame(j):
 y=unit(j['middle']-j['wrist']);x=j['little']-j['index'];x=unit(x-y*np.dot(x,y));z=unit(np.cross(x,y));return np.stack([x,y,z],axis=1)
def worldjoints(rig,names):return {k:point(rig.matrix_world,rig.data.bones[n].head_local) for k,n in names.items()}
records={};payload={}
for ident in ['C1','MAKEHUMAN']:
 if ident=='C1':
  p=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY.blend'
  bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
  sc=bpy.data.scenes['STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY'];bpy.context.window.scene=sc;sc.frame_set(157)
  mesh=bpy.data.objects['RIGHT_HAND_OFFICIAL_L1_PRODUCT_MESH.002'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG.002']
  names=dict(wrist='WRIST_R',index='INDEX_MCP_R',pip='INDEX_PIP_R',dip='INDEX_DIP_R',middle='MIDDLE_MCP_R',little='LITTLE_MCP_R',thumb='THUMB_CMC_R',thumb_mcp='THUMB_MCP_R')
  flexnames=['INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R'];thumbname='THUMB_CMC_R'
 else:
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(OUT/'sources/hand-posable.glb'),import_pack_images=True)
  mesh=bpy.data.objects['Avery | anatomical body'];rig=bpy.data.objects['Avery | anatomical body.rig']
  names=dict(wrist='hand_r',index='index_01_r',pip='index_02_r',dip='index_03_r',middle='middle_01_r',little='pinky_01_r',thumb='thumb_01_r',thumb_mcp='thumb_02_r')
  flexnames=['index_01_r','index_02_r','index_03_r'];thumbname='thumb_01_r'
 assert not bpy.data.libraries
 rig.animation_data_clear();rig.data.pose_position='POSE'
 j=worldjoints(rig,names);basis=frame(j);origin=j['middle'];length=np.linalg.norm(j['pip']-j['index'])
 dorsal_sign=1 if ident=='C1' else -1
 basis[:,2]*=dorsal_sign
 if ident=='C1':target_length=length
 scale=target_length/length
 jc={k:((v-origin)@basis*scale) for k,v in j.items()}
 records[ident]=dict(source=str(p) if ident=='C1' else 'sources/hand-posable.glb',scale=scale,index_proximal_source_mm=length*1000,origin_world=origin.tolist(),basis_world=basis.tolist(),basis_determinant=float(np.linalg.det(basis)),display_reflection_only=ident!='C1',handedness_evidence='Candidate nail geometry lies on opposite signed side of wrist/MCP frame relative to baseline; native source says right. Display Z reflected only, not certified native right hand.' if ident!='C1' else 'Project formal right hand authority preserved.',joints_normalized_m={k:v.tolist() for k,v in jc.items()},alignment='Palm frame: Y wrist to middle MCP; X projected index-to-little MCP; origin middle MCP; ONE uniform scale matching index MCP-PIP length. Candidate ONLY: Z reflection for dorsal correspondence, explicitly disclosed. No vertex fitting or rebind.',states={})
 payload[ident]={}
 for state in ['NEUTRAL','INDEX_FLEX','THUMB_SPREAD']:
  for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
  if state=='INDEX_FLEX':
   for n,a in zip(flexnames,[20,35,15]):
    pb=rig.pose.bones[n];a_world=(<REDACTED_EMAIL>_local).to_3x3()
    worldrot=Matrix.Rotation(math.radians(-a*dorsal_sign),3,Vector(basis[:,0]))
    pb.rotation_mode='XYZ';pb.rotation_euler=(a_world.inverted()@worldrot@a_world).to_euler('XYZ')
  if state=='THUMB_SPREAD':
   pb=rig.pose.bones[thumbname]
   # Thumb points radially: negative rotation around dorsal axis opens it from the fingers.
   a_world=(<REDACTED_EMAIL>_local).to_3x3()
   worldrot=Matrix.Rotation(math.radians(15*dorsal_sign),3,Vector(basis[:,2]))
   pb.rotation_mode='XYZ';pb.rotation_euler=(a_world.inverted()@worldrot@a_world).to_euler('XYZ')
  bpy.context.view_layer.update()
  v,f=evaluated(mesh);v=(v-origin)@basis*scale
  # Account for BOTH native object reflection and display reflection. Normalize
  # baked render winding by actual enclosed signed volume, never by name alone.
  volume=sum(np.dot(v[face[0]],np.cross(v[face[i]],v[face[i+1]])) for face in f for i in range(1,len(face)-1))/6
  if volume<0:f=[list(reversed(face)) for face in f]
  payload[ident][state]=(v,f)
  np.savez(OUT/(ident+'__'+state+'.npz'),V=v,F=np.array(f,dtype=object))
  records[ident]['states'][state]=dict(vertices=len(v),faces=len(f),baked_winding_reversed_for_outward_normals=bool(volume<0),outward_signed_volume_m3=abs(float(volume)),bounds_m=[v.min(0).tolist(),v.max(0).tolist()],pose_basis={pb.name:[list(row) for row in pb.matrix_basis] for pb in rig.pose.bones},pose_joints_normalized_m={k:((point(rig.matrix_world,rig.pose.bones[n].head)-origin)@basis*scale).tolist() for k,n in names.items()},shape_keys={k.name:k.value for k in mesh.data.shape_keys.key_blocks} if mesh.data.shape_keys else {},geometric_digest=hashlib.sha256(v.tobytes()).hexdigest())
 save('ALIGNMENT_AND_POSE_RECEIPT.json',records)
print('EXTRACTION_COMPLETE',flush=True)
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
sc.world=bpy.data.worlds.new('Shared neutral background')
sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
sh=sc.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='MATERIAL';sh.single_color=(.64,.64,.64);sh.show_shadows=True;sh.show_cavity=False;sh.show_specular_highlight=False;sh.background_type='WORLD';sc.world.color=(.055,.065,.08)
sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.view_settings.exposure=0;sc.view_settings.gamma=1
mat=bpy.data.materials.new('SHARED_NEUTRAL_NO_TEXTURE');mat.diffuse_color=(.64,.64,.64,1)
objects={}
for ident in payload:
 objects[ident]={}
 for state,(v,f) in payload[ident].items():
  me=bpy.data.meshes.new(ident+'__'+state);me.from_pydata(v.tolist(),[],f);me.update();ob=bpy.data.objects.new(me.name,me);sc.collection.objects.link(ob);me.materials.append(mat);objects[ident][state]=ob
cd=bpy.data.cameras.new('BENCHMARK_ORTHO');cam=bpy.data.objects.new(cd.name,cd);sc.collection.objects.link(cam);sc.camera=cam;cd.type='ORTHO';cd.clip_start=.0001;cd.clip_end=10
for ob in sc.objects:
 if ob.type=='MESH':ob.hide_render=True
ob=objects['C1']['NEUTRAL'];ob.hide_render=False
cam.location=(0,.0,.5);cam.rotation_euler=(0,0,0);cd.ortho_scale=.26;sc.render.resolution_x=800;sc.render.resolution_y=1000
for ident in objects:
 for x in objects.values():
  for o in x.values():o.hide_render=True
 objects[ident]['NEUTRAL'].hide_render=False
 sc.render.filepath=str(OUT/('PREVIEW_'+ident+'.png'));bpy.ops.render.render(write_still=True)
save('RENDER_SETTINGS.json',dict(engine=sc.render.engine,lighting='paint.sl studio, shadows on; cavity/specular OFF',material=list(mat.diffuse_color),texture=False,view_transform=sc.view_settings.view_transform,projection='ORTHOGRAPHIC',pose_comparability='Independent native binds, same applied angle increments, NOT anatomically identical poses. No transferred animation.'))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'HAND_ASSET_BENCHMARK_STATIC.blend'),check_existing=False)
print('PREVIEW_READY',flush=True)
