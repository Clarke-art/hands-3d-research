import sys,ast,importlib.util,json,re
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
import bpy
from mathutils import Matrix,Vector
from common import *
spec=importlib.util.spec_from_file_location('identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
tree=ast.parse((P.parent/'piano_keyboard_spatial_anchor_and_contact_validation_r1/04_hands.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='intrinsic'],type_ignores=[]),'intrinsic','exec'))
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def rename_normalize(v):
 if isinstance(v,str):return re.sub(r'\.\d{3}$','',v)
 if isinstance(v,list):return [rename_normalize(x) for x in v]
 if isinstance(v,dict):return {k:rename_normalize(x) for k,x in v.items()}
 return v
def structural(ob,rig):
 parent=rig.parent;rigbasis=rig.matrix_basis.copy();pose_state={b.name:{n:list(getattr(b,n)) for n in ['location','rotation_euler','rotation_quaternion','rotation_axis_angle','scale']} for b in rig.pose.bones};action=rig.animation_data.action if rig.animation_data else None;slot=rig.animation_data.action_slot if rig.animation_data else None
 if rig.animation_data:rig.animation_data.action=None
 rig.parent=None;rig.matrix_world=Matrix.Identity(4);h.neutral(rig);value=rename_normalize(intrinsic(ob,rig))
 value['mesh_object']['props'].pop('STATIC_POSE',None)
 rig.parent=parent;rig.matrix_basis=rigbasis
 for name,values in pose_state.items():
  for n,v in values.items():setattr(rig.pose.bones[name],n,v)
 if action:rig.animation_data.action=action;rig.animation_data.action_slot=slot
 bpy.context.view_layer.update();return digest(value)
def linear(ob):
 for l in ob.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for f in bag.fcurves:
     for k in f.keyframe_points:k.interpolation='LINEAR'
def settime(sc,t,s):
 f=1+(t-WINDOWS[s][0])*60;sc.frame_set(int(f+1e-8),subframe=max(0,f-int(f+1e-8)))
plan=read(P/'CONTACT_AWARE_MOTION_PLAN_R1.json');A=np.load(P/'temporal_motion.npz');source=STATIC/'STATIC_POSTURE_REFINED_CANDIDATE_R2.blend';sm=read(STATIC/'STATIC_SCENE_MANIFEST_R2.json');dest=P/'STATIC_TO_DYNAMIC_TRANSITION_CANDIDATE_R1.blend'
repair=read(P/'CONFIRMED_CODE_ERROR_R1.json') if (P/'CONFIRMED_CODE_ERROR_R1.json').exists() else None
if dest.exists():assert repair and sha(dest)==repair['candidate_before_fix_sha256'] and sha(P/'temporal_motion.npz')==repair['motion_sha256'],'Only confirmed implementation repair of identical motion allowed.'
assert sha(source)==sm['candidate_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
staticbefore={};mapping={};structure={};keyboard={}
for pose,info in sm['mapping'].items():
 bpy.context.window.scene=bpy.data.scenes[info['scene']];bpy.context.view_layer.update();staticbefore[pose]=digest(h.core(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]))
for s,pose in [('L','L1'),('R','R1')]:
 info=sm['mapping'][pose];source_scene=bpy.data.scenes[info['scene']];bpy.context.window.scene=source_scene
 for ob in source_scene.objects:ob['COPY_TOKEN_TRANSITION']=ob.name
 bpy.ops.scene.new(type='FULL_COPY');sc=bpy.context.scene;sc.name='DYNAMIC_LEFT_OCTAVE_R1' if s=='L' else 'DYNAMIC_RIGHT_FSHARP_R1';copies={o['COPY_TOKEN_TRANSITION']:o for o in sc.objects if 'COPY_TOKEN_TRANSITION' in o}
 for ob in source_scene.objects:del ob['COPY_TOKEN_TRANSITION']
 for ob in sc.objects:
  if 'COPY_TOKEN_TRANSITION' in ob:del ob['COPY_TOKEN_TRANSITION']
 rig=copies[info['rig']];mesh=copies[info['mesh']];rt=copies[info['root']]
 clone_identity=structural(mesh,rig);bpy.context.window.scene=source_scene;original_identity=structural(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]);assert clone_identity==original_identity,('COPY_INTRINSIC_CHANGED',s,clone_identity,original_identity)
 bpy.context.window.scene=sc;structure[s]={'source_normalized_intrinsic_sha256':original_identity,'copy_before_action_sha256':clone_identity}
 sc['PHASE']='PIANO_HAND_STATIC_TO_DYNAMIC_TRANSITION_R1';sc['DESIGN_ONLY']=True;sc['HUMAN_APPROVAL_PENDING']=True;sc['SOURCE_STATIC_R2_SHA256']=sha(source);sc['POLICY_SHA256']=plan['policy_sha256'];sc['TIMEBASE']='frame1=window_start; exact original timeline seconds;60fps sampled at120Hz';sc['NO_DYNAMIC_TRANSITION_CLAIM']=False;sc.render.fps=60;sc.frame_start=1;sc.frame_end=int(np.ceil((WINDOWS[s][1]-WINDOWS[s][0])*60));sc.camera=copies[info['cameras']['TEACHING_TOP']]
 rig.animation_data_clear()
 for i,t in enumerate(A[s+'_times']):
  f=1+(t-WINDOWS[s][0])*60
  for j,d in enumerate(c.DIGITS):
   for name,r in zip(c.SETUPS[s,d][0],c.joint_mats(s,d,A[s+'_q'][i,j])):
    b=rig.pose.bones[name];b.rotation_mode='QUATERNION';quat=Matrix(r).to_quaternion()
    if i and b.rotation_quaternion.dot(quat)<0:quat.negate()
    b.rotation_quaternion=quat;b.keyframe_insert(data_path='rotation_quaternion',frame=f,group=d)
 rig.animation_data.action.name='DESIGN_ONLY_TEMPORAL_'+s+'_R1';linear(rig)
 pivotmap={};keygeometry={}
 for k in c.KEYS:
  keyobs=[o for o in sc.objects if o.get('FROZEN_KEY_INDEX')==k['key_index']]
  assert len(keyobs)==len(k['geometry']);keygeometry[k['key_index']]=digest([{'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons]} for o in sorted(keyobs,key=lambda x:x.name)])
  if not any(n['key_index']==k['key_index'] for n in EVENTS[s]):continue
  pivot=bpy.data.objects.new('DESIGN_ONLY_MOVING_KEY_'+s+'_'+str(k['midi_note']),None);sc.collection.objects.link(pivot);pivot.location=k['press_pivot'];pivot['MIDI_NOTE']=k['midi_note'];pivot['FROZEN_KEY_INDEX']=k['key_index'];pivot['INHERITED_KEY_RULE']='35ms down/70ms return'
  for o in keyobs:
   world=o.matrix_world.copy();o.parent=pivot;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Translation(-Vector(k['press_pivot']))@world
   o.color=(.38,.62,.64,1) if k['color']=='WHITE' else (.025,.10,.12,1)
  for i,t in enumerate(A[s+'_times']):pivot.rotation_euler.x=float(A[s+'_key_angles'][i,k['key_index']]);pivot.keyframe_insert(data_path='rotation_euler',index=0,frame=1+(t-WINDOWS[s][0])*60)
  pivot.animation_data.action.name='DESIGN_ONLY_KEY_'+s+'_'+str(k['midi_note'])+'_R1';linear(pivot);pivotmap[str(k['key_index'])]=pivot.name
 for row in c.MARKERS[s]:
  marker=bpy.data.objects.new('CONTACT_PAD_'+s+'_'+row['digit'],None);sc.collection.objects.link(marker);marker.parent=rig;marker.parent_type='BONE';marker.parent_bone=row['distal_frame'];marker.location=Vector(row['local_pad_point'])-Vector((0,rig.data.bones[row['distal_frame']].length,0));marker.empty_display_size=.002;marker['AUDIT_ONLY']=True
 mapping[s]={'scene':sc.name,'rig':rig.name,'mesh':mesh.name,'root':rt.name,'cameras':{v:copies[n].name for v,n in info['cameras'].items()},'key_pivots':pivotmap,'window':WINDOWS[s],'source_scene':source_scene.name};keyboard[s]=keygeometry
 settime(sc,WINDOWS[s][0],s)
bpy.context.window.scene=bpy.data.scenes[mapping['L']['scene']];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest));bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False)
arrays={};readback={};staticmatch={};keymatches={}
for pose,info in sm['mapping'].items():
 bpy.context.window.scene=bpy.data.scenes[info['scene']];bpy.context.view_layer.update();now=digest(h.core(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]));staticmatch[pose]={'source':staticbefore[pose],'saved':now,'matches':now==staticbefore[pose]};assert staticmatch[pose]['matches']
for s,info in mapping.items():
 sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[info['rig']];ob=bpy.data.objects[info['mesh']];verts=[];pads=[];skins=[];errors=[];actualangles=[];world_key_error=0
 for i,t in enumerate(A[s+'_times']):
  settime(sc,float(t),s);V,_=h.coords(ob);pp=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS[s]]);sp=V[[r['mesh_vertex'] for r in c.MARKERS[s]]];verts.append(V);pads.append(pp);skins.append(sp);errors.append(float(np.max(np.linalg.norm(pp-A[s+'_pads'][i],axis=1))*1000));aa=np.zeros(88)
  for k,name in info['key_pivots'].items():
   key=c.KEYS[int(k)];pivot=bpy.data.objects[name];aa[int(k)]=pivot.rotation_euler.x
   for g in key['geometry']:
    child=next(o for o in pivot.children if g['name'] in o.name);actual=np.array([list(<REDACTED_EMAIL>) for v in child.data.vertices]);expected=keytransform(key['midi_note'],g['vertices'],aa[int(k)]);err=float(np.max(np.linalg.norm(actual-expected,axis=1))*1000);world_key_error=max(world_key_error,err)
  assert world_key_error<.03,('ACTUAL_KEY_TRANSFORM_MISMATCH',s,t,world_key_error)
  actualangles.append(aa)
 structure[s]['copy_after_save_reopen_reset_sha256']=structural(ob,rig);structure[s]['matches']=structure[s]['copy_before_action_sha256']==structure[s]['copy_after_save_reopen_reset_sha256'];assert structure[s]['matches'];assert max(errors)<.03
 km=[]
 for k in c.KEYS:
  keyobs=[o for o in sc.objects if o.type=='MESH' and o.get('FROZEN_KEY_INDEX')==k['key_index']];value=digest([{'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons]} for o in sorted(keyobs,key=lambda x:x.name)]);assert value==keyboard[s][k['key_index']];km.append(value)
 arrays[s+'_verts']=np.array(verts);arrays[s+'_pads']=np.array(pads);arrays[s+'_skin_pads']=np.array(skins);arrays[s+'_times']=A[s+'_times'];arrays[s+'_key_angles']=np.array(actualangles);keymatches[s]={'unchanged_key_mesh_count':len(km),'actual_key_angle_parity_max_rad':float(np.max(np.abs(arrays[s+'_key_angles']-A[s+'_key_angles']))),'actual_moving_key_world_vertex_parity_max_mm':world_key_error}
 readback[s]={'FK_saved_reopened_max_error_mm':max(errors),'skin_pad_drift_max_mm':float(np.max(np.linalg.norm(np.array(skins)-pads,axis=2))*1000),'bone_count':len(rig.data.bones),'vertices':len(ob.data.vertices),'samples':len(verts),'root_motion_mm':0}
 print('SAVE_REOPEN_SEQUENCE_VERIFIED',s,json.dumps(readback[s]),flush=True)
np.savez_compressed(P/'evaluated_temporal_candidate.npz',**arrays)
dump('DYNAMIC_SCENE_MANIFEST_R1.json',{'candidate_sha256':sha(dest),'source_candidate_sha256':sha(source),'mapping':mapping,'static_anchor_scene_identity':staticmatch,'immutable_hand_structure':structure,'key_geometry_identity':keymatches,'readback':readback,'action_count':len(bpy.data.actions),'save_reopen_verified':True,'verification_reset_not_saved':True})
print('SOLE_BLENDER_CANDIDATE_SAVED_VERIFIED',flush=True)
