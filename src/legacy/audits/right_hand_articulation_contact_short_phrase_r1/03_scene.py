import bpy,sys,ast,importlib.util,re,math
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from articulation_common import *
from mathutils import Matrix,Vector
spec=importlib.util.spec_from_file_location('identity',o.ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
for file,names in [(P.parent/'piano_keyboard_spatial_anchor_and_contact_validation_r1/04_hands.py',['intrinsic']),(previous.OLD/'02_scene_verify.py',['rename_normalize','structural','linear'])]:
 tree=ast.parse(file.read_text(encoding='utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(file),'exec'))

def action_payload(a):
 rows=[]
 for layer in a.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for f in bag.fcurves:rows.append({'path':f.data_path,'index':f.array_index,'keyframes':[{'co':list(k.co),'handle_left':list(k.handle_left),'handle_right':list(k.handle_right),'interpolation':k.interpolation} for k in f.keyframe_points]})
 return rows
source=PRE/'SHORT_PHRASE_DESIGN_ONLY_R1.blend';man=read(PRE/'SCENE_MANIFEST.json');assert sha(source)==man['sha256'];dest=P/'RIGHT_HAND_ARTICULATION_CONTACT_DESIGN_ONLY_R1.blend';assert not dest.exists()
A=np.load(P/'motion.npz');OLD=np.load(PRE/'evaluated.npz');assert np.array_equal(A['times'],OLD['times'])
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc;sc.frame_set(1);bpy.context.view_layer.update()
staticmap=read(o.STATIC/'STATIC_SCENE_MANIFEST_R2.json')['mapping'];static={}
for label,info in staticmap.items():
 bpy.context.window.scene=bpy.data.scenes[info['scene']];bpy.context.view_layer.update();static[label]=digest(h.core(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]));assert static[label]==man['static_four_core_sha256'][label]
bpy.context.window.scene=sc;sc.frame_set(1);bpy.context.view_layer.update();mapping=man['mapping'];structures={}
for s,info in mapping.items():structures[s]=structural(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']])
ri=mapping['R'];rig=bpy.data.objects[ri['rig']];rt=bpy.data.objects[ri['root']];base=rt.matrix_world.copy();oldaction=rig.animation_data.action;oldactionname=oldaction.name
protectedactions={a.name:digest(action_payload(a)) for a in bpy.data.actions if a!=oldaction};protectedcameras={k:{'world':np.array(bpy.data.objects[name].matrix_world).tolist(),'ortho_scale':bpy.data.objects[name].data.ortho_scale} for k,name in man['cameras'].items()}
keygeometry={}
for k in c.KEYS:
 obs=[ob for ob in sc.objects if ob.type=='MESH' and ob.get('FROZEN_KEY_INDEX')==k['key_index']];keygeometry[str(k['key_index'])]=digest([{'vertices':[list(v.co) for v in ob.data.vertices],'faces':[list(p.vertices) for p in ob.data.polygons]} for ob in sorted(obs,key=lambda x:x.name)])
rig.animation_data_clear();rt.animation_data_clear();bpy.data.actions.remove(oldaction);rt.rotation_mode='QUATERNION';wrist=Vector(o.ANCHORS['R1']['root_xyz_m'])
for i,t in enumerate(A['times']):
 f=1+(t-START)*FPS;D=Matrix.Translation(wrist+Vector(A['R_delta'][i]))@Matrix.Rotation(math.radians(float(A['R_pitch_deg'][i])),4,'X')@Matrix.Translation(-wrist);rt.matrix_world=D@base
 for prop in ['location','rotation_quaternion']:rt.keyframe_insert(data_path=prop,frame=f)
 for j,d in enumerate(c.DIGITS):
  for name,rot in zip(c.SETUPS['R',d][0],c.joint_mats('R',d,A['R_q'][i,j])):
   b=rig.pose.bones[name];b.rotation_mode='QUATERNION';q=Matrix(rot).to_quaternion()
   if i and b.rotation_quaternion.dot(q)<0:q.negate()
   b.rotation_quaternion=q;b.keyframe_insert(data_path='rotation_quaternion',frame=f,group=d)
rig.animation_data.action.name='DESIGN_ONLY_ARTICULATION_CONTACT_RIGHT_R1';rt.animation_data.action.name='DESIGN_ONLY_ARTICULATION_COMMON_RIGHT_ROOT_R1';linear(rig);linear(rt)
sc.name='DESIGN_ONLY_RIGHT_ARTICULATION_DUAL_HAND_R1';sc['PHASE']='RIGHT_HAND_ARTICULATION_CONTACT_SHORT_PHRASE_R1';sc['DESIGN_ONLY']=True;sc['HUMAN_APPROVAL_PENDING']=True;sc['SOURCE_PREVIOUS_CANDIDATE_SHA256']=sha(source);sc.frame_set(1);sc.camera=bpy.data.objects[man['cameras']['TEACHING']];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest));bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False)
for label,info in staticmap.items():
 bpy.context.window.scene=bpy.data.scenes[info['scene']];bpy.context.view_layer.update();assert digest(h.core(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]))==static[label]
sc=bpy.data.scenes['DESIGN_ONLY_RIGHT_ARTICULATION_DUAL_HAND_R1'];bpy.context.window.scene=sc
assert all(digest(action_payload(bpy.data.actions[name]))==hh for name,hh in protectedactions.items())
assert protectedcameras=={k:{'world':np.array(bpy.data.objects[name].matrix_world).tolist(),'ortho_scale':bpy.data.objects[name].data.ortho_scale} for k,name in man['cameras'].items()}
arrays={'times':A['times']};keyangles=[];poseerr=0;keyerr=0;rightFK=0;leftdiff=0
for s in ['L','R']:
 for suffix in ['verts','pads','skin_pads','root_matrices']:arrays[s+'_'+suffix]=[]
for i,t in enumerate(A['times']):
 f=1+(t-START)*FPS;nf=math.floor(f+1e-7);sc.frame_set(nf,subframe=max(0,f-nf));bpy.context.view_layer.update()
 for s,info in mapping.items():
  rr=bpy.data.objects[info['rig']];ob=bpy.data.objects[info['mesh']];root=bpy.data.objects[info['root']];V,_=h.coords(ob);pp=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS[s]]);arrays[s+'_verts'].append(V);arrays[s+'_pads'].append(pp);arrays[s+'_skin_pads'].append(V[[r['mesh_vertex'] for r in c.MARKERS[s]]]);arrays[s+'_root_matrices'].append(np.array(root.matrix_world))
  if s=='L':leftdiff=max(leftdiff,float(np.max(np.linalg.norm(V-OLD['L_verts'][i],axis=1))*1000))
  else:
   expected=o.worldpads('R',A['R_q'][i]);D=Matrix.Translation(wrist+Vector(A['R_delta'][i]))@Matrix.Rotation(math.radians(float(A['R_pitch_deg'][i])),4,'X')@Matrix.Translation(-wrist);DD=np.array(D);expected=expected@DD[:3,:3].T+DD[:3,3];rightFK=max(rightFK,float(np.max(np.linalg.norm(expected-pp,axis=1))*1000))
  for j,d in enumerate(c.DIGITS):
   for name,rot in zip(c.SETUPS[s,d][0],c.joint_mats(s,d,A[s+'_q'][i,j])):poseerr=max(poseerr,float(np.max(abs(np.array(rr.pose.bones[name].matrix_basis.to_3x3())-rot))))
 aa=np.zeros(88)
 for ki,name in man['key_pivots'].items():
  pv=bpy.data.objects[name];aa[int(ki)]=pv.rotation_euler.x;k=c.KEYS[int(ki)]
  for g in k['geometry']:
   ob=next(v for v in pv.children if g['name'] in v.name);actual=np.array([list(<REDACTED_EMAIL>) for v in ob.data.vertices]);expected=previous.o.keytransform(k['midi_note'],g['vertices'],aa[int(ki)]);keyerr=max(keyerr,float(np.max(np.linalg.norm(actual-expected,axis=1))*1000))
 keyangles.append(aa)
assert poseerr<1e-5 and keyerr<.03 and rightFK<.03 and leftdiff<1e-6,('READBACK_PARITY_FAILED',poseerr,keyerr,rightFK,leftdiff)
arrays['key_angles']=keyangles;np.savez_compressed(P/'evaluated.npz',**arrays)
for s,info in mapping.items():assert structural(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']])==structures[s]
for k in c.KEYS:
 obs=[ob for ob in sc.objects if ob.type=='MESH' and ob.get('FROZEN_KEY_INDEX')==k['key_index']];assert keygeometry[str(k['key_index'])]==digest([{'vertices':[list(v.co) for v in ob.data.vertices],'faces':[list(p.vertices) for p in ob.data.polygons]} for ob in sorted(obs,key=lambda x:x.name)])
dump('SCENE_MANIFEST.json',{'path':str(dest),'sha256':sha(dest),'previous_candidate_sha256':man['sha256'],'scene':sc.name,'mapping':mapping,'cameras':man['cameras'],'key_pivots':man['key_pivots'],'static_four_core_sha256':static,'four_static_scenes_unchanged':True,'hand_structure_unchanged':True,'all_88_key_geometry_unchanged':True,'all_left_key_actions_exact_unchanged':True,'all_camera_transforms_exact_unchanged':True,'left_actual_geometry_max_difference_mm':leftdiff,'right_actual_pad_vs_FK_max_mm':rightFK,'actual_joint_rotation_parity_max':poseerr,'actual_key_world_parity_max_mm':keyerr,'key_angle_parity_max_rad':float(np.max(abs(np.array(keyangles)-A['key_angles']))),'candidate_count':1,'save_reopen_verified':True,'evaluated_samples':len(A['times']),'render_engine':sc.render.engine,'only_right_nonfrozen_actions_changed':True})
print('NEW_SINGLE_CANDIDATE_REOPEN_VERIFIED_LEFT_KEY_ACTIONS_IDENTICAL',leftdiff,rightFK,flush=True)
