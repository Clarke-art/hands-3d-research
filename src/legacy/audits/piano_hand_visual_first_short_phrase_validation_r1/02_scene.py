import bpy,sys,ast,importlib.util,re,math
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from phrase_common import *
from mathutils import Matrix,Vector
spec=importlib.util.spec_from_file_location('identity',o.ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
for file,names in [(P.parent/'piano_keyboard_spatial_anchor_and_contact_validation_r1/04_hands.py',['intrinsic']),(OLD/'02_scene_verify.py',['rename_normalize','structural','linear'])]:
 tree=ast.parse(file.read_text(encoding='utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(file),'exec'))
source=o.STATIC/'STATIC_POSTURE_REFINED_CANDIDATE_R2.blend';sm=read(o.STATIC/'STATIC_SCENE_MANIFEST_R2.json');dest=P/'SHORT_PHRASE_DESIGN_ONLY_R1.blend';assert not dest.exists();assert sha(source)==sm['candidate_sha256']
A=np.load(P/'motion.npz');bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
static={};originalstructure={}
for pose,info in sm['mapping'].items():
 bpy.context.window.scene=bpy.data.scenes[info['scene']];bpy.context.view_layer.update();static[pose]=digest(h.core(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]))
for s,pose in [('L','L1'),('R','R1')]:
 info=sm['mapping'][pose];bpy.context.window.scene=bpy.data.scenes[info['scene']];originalstructure[s]=structural(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']])

def clone(pose):
 info=sm['mapping'][pose];source_scene=bpy.data.scenes[info['scene']];bpy.context.window.scene=source_scene
 for ob in source_scene.objects:ob['PHRASE_COPY_TOKEN']=ob.name
 bpy.ops.scene.new(type='FULL_COPY');sc=bpy.context.scene;copied={v['PHRASE_COPY_TOKEN']:v for v in sc.objects if 'PHRASE_COPY_TOKEN' in v}
 for ob in list(source_scene.objects)+list(sc.objects):
  if 'PHRASE_COPY_TOKEN' in ob:del ob['PHRASE_COPY_TOKEN']
 return sc,copied,info
sc,L,li=clone('L1');sc.name='DESIGN_ONLY_DUAL_HAND_SHORT_PHRASE_R1'
rs,R,ri=clone('R1');selected=[R[ri[k]] for k in ['root','rig','mesh']]
for ob in selected:sc.collection.objects.link(ob)
for ob in list(rs.objects):
 if ob not in selected:bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.scenes.remove(rs);bpy.context.window.scene=sc
mapping={s:{k:copies[info[k]].name for k in ['root','rig','mesh']} for s,copies,info in [('L',L,li),('R',R,ri)]}
structure={};rootbases={}
for s,info in mapping.items():
 rig=bpy.data.objects[info['rig']];ob=bpy.data.objects[info['mesh']];rt=bpy.data.objects[info['root']];bpy.context.view_layer.update();rootbases[s]=rt.matrix_world.copy();structure[s]=structural(ob,rig);assert structure[s]==originalstructure[s],('CLONE_IDENTITY_CHANGED',s)
 rig.animation_data_clear();rt.animation_data_clear();rt.rotation_mode='QUATERNION'
 for i,t in enumerate(A['times']):
  f=1+(t-START)*FPS
  if s=='L':
   wrist=Vector(o.ANCHORS['L1']['root_xyz_m']);delta=Vector(A['L_delta'][i]);D=Matrix.Translation(wrist+delta)@Matrix.Rotation(math.radians(float(A['L_pitch_deg'][i])),4,'X')@Matrix.Translation(-wrist);rt.matrix_world=D@rootbases[s]
   for prop in ['location','rotation_quaternion']:rt.keyframe_insert(data_path=prop,frame=f)
  for j,d in enumerate(c.DIGITS):
   for name,rot in zip(c.SETUPS[s,d][0],c.joint_mats(s,d,A[s+'_q'][i,j])):
    b=rig.pose.bones[name];b.rotation_mode='QUATERNION';quat=Matrix(rot).to_quaternion()
    if i and b.rotation_quaternion.dot(quat)<0:quat.negate()
    b.rotation_quaternion=quat;b.keyframe_insert(data_path='rotation_quaternion',frame=f,group=d)
 rig.animation_data.action.name='DESIGN_ONLY_SHORT_PHRASE_'+s;linear(rig)
 if s=='L':rt.animation_data.action.name='DESIGN_ONLY_SHORT_PHRASE_SHARED_LEFT_ROOT';linear(rt)
keygeometry={};pivotmap={}
for k in c.KEYS:
 obs=[v for v in sc.objects if v.type=='MESH' and v.get('FROZEN_KEY_INDEX')==k['key_index']];assert len(obs)==len(k['geometry']);keygeometry[str(k['key_index'])]=digest([{'vertices':[list(v.co) for v in ob.data.vertices],'faces':[list(p.vertices) for p in ob.data.polygons]} for ob in sorted(obs,key=lambda x:x.name)])
 for ob in obs:ob.color=(.86,.85,.80,1) if k['color']=='WHITE' else (.025,.028,.032,1)
 if not any(n['key_index']==k['key_index'] for n in TL['notes']):continue
 pivot=bpy.data.objects.new('DESIGN_ONLY_SHORT_PHRASE_KEY_'+str(k['midi_note']),None);sc.collection.objects.link(pivot);pivot.location=k['press_pivot'];pivot['MIDI_NOTE']=k['midi_note']
 for ob in obs:
  world=ob.matrix_world.copy();ob.parent=pivot;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=Matrix.Translation(-Vector(k['press_pivot']))@world
 for i,t in enumerate(A['times']):pivot.rotation_euler.x=float(A['key_angles'][i,k['key_index']]);pivot.keyframe_insert(data_path='rotation_euler',index=0,frame=1+(t-START)*FPS)
 pivot.animation_data.action.name='DESIGN_ONLY_SHORT_PHRASE_KEY_'+str(k['midi_note']);linear(pivot);pivotmap[str(k['key_index'])]=pivot.name
# Reframe the existing review cameras to show both hands. No hidden camera selection.
cameras={};configs={'TEACHING':((-.015,-.60,.67),(-.015,.014,.012),.80),'SIDE_OBLIQUE':((.06,-.63,.30),(-.015,.025,.004),.80),'OVERHEAD':((-.015,.005,.82),(-.015,.005,0),.80)}
for name,(eye,target,scale) in configs.items():
 data=bpy.data.cameras.new('SHORT_PHRASE_'+name);data.type='ORTHO';data.ortho_scale=scale;data.clip_start=.001;data.clip_end=10;ob=bpy.data.objects.new('SHORT_PHRASE_'+name,data);sc.collection.objects.link(ob);ob.location=eye;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();cameras[name]=ob.name
sc['DESIGN_ONLY']=True;sc['HUMAN_APPROVAL_PENDING']=True;sc['PHASE']='PIANO_HAND_VISUAL_FIRST_SHORT_PHRASE_VALIDATION_R1';sc['TIMEBASE']='frame1=source presentation 0.4s;60fps';sc.render.fps=FPS;sc.frame_start=1;sc.frame_end=round((END-START)*FPS);sc.camera=bpy.data.objects[cameras['TEACHING']];sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.frame_set(1)
# Preserve approved static scenes verbatim; transient identity normalization restored their state.
for pose,info in sm['mapping'].items():
 bpy.context.window.scene=bpy.data.scenes[info['scene']];bpy.context.view_layer.update();assert digest(h.core(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]))==static[pose],('STATIC_CHANGED_BEFORE_SAVE',pose)
bpy.context.window.scene=sc;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest));bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False)
for pose,info in sm['mapping'].items():
 bpy.context.window.scene=bpy.data.scenes[info['scene']];bpy.context.view_layer.update();assert digest(h.core(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]))==static[pose],('STATIC_CHANGED_REOPEN',pose)
sc=bpy.data.scenes['DESIGN_ONLY_DUAL_HAND_SHORT_PHRASE_R1'];bpy.context.window.scene=sc
arrays={'times':A['times']};poseerr=0;keyerr=0;fkerr={'L':0,'R':0};keyangles=[]
for s,info in mapping.items():arrays[s+'_verts']=[];arrays[s+'_pads']=[];arrays[s+'_skin_pads']=[];arrays[s+'_root_matrices']=[]
for i,t in enumerate(A['times']):
 f=1+(t-START)*FPS;nf=math.floor(f+1e-7);sc.frame_set(nf,subframe=max(0,f-nf));bpy.context.view_layer.update()
 for s,info in mapping.items():
  rig=bpy.data.objects[info['rig']];ob=bpy.data.objects[info['mesh']];rt=bpy.data.objects[info['root']];V,_=h.coords(ob);pp=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS[s]])
  arrays[s+'_verts'].append(V);arrays[s+'_pads'].append(pp);arrays[s+'_skin_pads'].append(V[[r['mesh_vertex'] for r in c.MARKERS[s]]]);arrays[s+'_root_matrices'].append(np.array(rt.matrix_world))
  expected=o.worldpads(s,A[s+'_q'][i])
  if s=='L':
   wrist=Vector(o.ANCHORS['L1']['root_xyz_m']);D=Matrix.Translation(wrist+Vector(A['L_delta'][i]))@Matrix.Rotation(math.radians(float(A['L_pitch_deg'][i])),4,'X')@Matrix.Translation(-wrist);DD=np.array(D);expected=expected@DD[:3,:3].T+DD[:3,3]
  fkerr[s]=max(fkerr[s],float(np.max(np.linalg.norm(pp-expected,axis=1))*1000))
  for j,d in enumerate(c.DIGITS):
   for name,rot in zip(c.SETUPS[s,d][0],c.joint_mats(s,d,A[s+'_q'][i,j])):poseerr=max(poseerr,float(np.max(abs(np.array(rig.pose.bones[name].matrix_basis.to_3x3())-rot))))
 aa=np.zeros(88)
 for ki,name in pivotmap.items():
  pivot=bpy.data.objects[name];aa[int(ki)]=pivot.rotation_euler.x;k=c.KEYS[int(ki)]
  for g in k['geometry']:
   ob=next(v for v in pivot.children if g['name'] in v.name);actual=np.array([list(<REDACTED_EMAIL>) for v in ob.data.vertices]);expected=o.keytransform(k['midi_note'],g['vertices'],aa[int(ki)]);keyerr=max(keyerr,float(np.max(np.linalg.norm(actual-expected,axis=1))*1000))
 keyangles.append(aa)
assert poseerr<1e-5 and keyerr<.03 and max(fkerr.values())<.03,('PLAYBACK_PARITY_FAILED',poseerr,keyerr,fkerr)
arrays['key_angles']=keyangles;np.savez_compressed(P/'evaluated.npz',**arrays)
for s,info in mapping.items():assert structural(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']])==structure[s],('FROZEN_STRUCTURE_CHANGED',s)
for k in c.KEYS:
 obs=[v for v in sc.objects if v.type=='MESH' and v.get('FROZEN_KEY_INDEX')==k['key_index']];assert keygeometry[str(k['key_index'])]==digest([{'vertices':[list(v.co) for v in ob.data.vertices],'faces':[list(p.vertices) for p in ob.data.polygons]} for ob in sorted(obs,key=lambda x:x.name)])
dump('SCENE_MANIFEST.json',{'path':str(dest),'sha256':sha(dest),'scene':sc.name,'mapping':mapping,'cameras':cameras,'key_pivots':pivotmap,'static_four_core_sha256':static,'four_static_scenes_unchanged':True,'hand_structure_unchanged':True,'all_88_key_geometry_unchanged':True,'bone_count':{s:len(bpy.data.objects[v['rig']].data.bones) for s,v in mapping.items()},'actual_pad_vs_FK_max_mm':fkerr,'actual_joint_rotation_parity_max':poseerr,'actual_key_world_parity_max_mm':keyerr,'key_angle_parity_max_rad':float(np.max(abs(np.array(keyangles)-A['key_angles']))),'candidate_count':1,'save_reopen_verified':True,'evaluated_samples':len(A['times']),'render_engine':sc.render.engine,'saved_mutations':'Only new DESIGN_ONLY actions, external root motion, display cameras and object key colors in copied scene'})
print('ONE_DUAL_HAND_SCENE_SAVED_REOPEN_VERIFIED',sc.render.engine,fkerr,flush=True)
