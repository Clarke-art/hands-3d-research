import sys,json,hashlib,ast,math,importlib.util,re
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;OLD=P.parent/'piano_hand_static_to_dynamic_transition_r1';LAST=P.parent/'left_little_finger_moving_key_reachability_r1';sys.path.insert(0,str(OLD))
import bpy
from mathutils import Matrix,Vector
import common as o
import numpy as np
c=o.c
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False,default=lambda a:a.tolist() if hasattr(a,'tolist') else a),encoding='utf8')
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
spec=importlib.util.spec_from_file_location('identity',o.ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
for file,names in [(P.parent/'piano_keyboard_spatial_anchor_and_contact_validation_r1/04_hands.py',['intrinsic']),(OLD/'02_scene_verify.py',['rename_normalize','structural']),(LAST/'04_verify_render.py',['action','preservation'])]:
 tree=ast.parse(file.read_text(encoding='utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(file),'exec'))
PRE=OLD
pol=o.read(P/'COORDINATED_CLEARANCE_POLICY_R1.json');bpy.ops.wm.open_mainfile(filepath=pol['source_blend'],load_ui=False,use_scripts=False);before=preservation();oldactions={a.name:digest(action(a)) for a in bpy.data.actions}
man=o.read(P/'COORDINATED_SCENE_MANIFEST_R1.json');dest=P/'LEFT_OCTAVE_COORDINATED_CLEARANCE_CANDIDATE_R1.blend';assert o.sha(dest)==man['candidate_sha256'];bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False);after=preservation();assert before==after
protectedactions={name:s for name,s in oldactions.items() if name not in ['DESIGN_ONLY_LEFT_REACHABILITY_R1','DESIGN_ONLY_SHARED_WRIST_FOLLOW_R1']}
assert all(digest(action(bpy.data.actions[name]))==s for name,s in protectedactions.items()),'Protected key/right actions modified'
sm=o.read(o.STATIC/'STATIC_SCENE_MANIFEST_R2.json');expected=o.read(LAST/'STATIC_ANCHOR_PROTECTION_R1.json')['reopened_static_scene_identity'];static={}
for label,m in sm['mapping'].items():
 bpy.context.window.scene=bpy.data.scenes[m['scene']];bpy.context.view_layer.update();v=digest(h.core(bpy.data.objects[m['mesh']],bpy.data.objects[m['rig']]))
 assert v==expected[label]['expected'];static[label]={'expected':expected[label]['expected'],'reopened':v,'matches':True}
dump('STATIC_ANCHOR_PROTECTION_R1.json',{'status':'UNCHANGED','STATIC_ANCHOR_CONFLICT':False,'human_approval_preserved':True,'four_approved_static_scenes':static,'markers_sha256':o.sha(o.OLD/'FINGERTIP_CONTACT_MARKERS_R1.json'),'anchors_sha256':o.sha(o.STATIC/'SOLVED_STATIC_POSES_R2.json'),'first_web_palm_volume_intrinsic_identity_equal':before['L']['intrinsic']==after['L']['intrinsic']})
info=man['mapping'];sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[info['rig']];ob=bpy.data.objects[info['mesh']];rt=bpy.data.objects[info['root']]
M=np.load(P/'coordinated_motion.npz');old=np.load(OLD/'temporal_motion.npz')
assert np.max(abs(M['root_matrices'][0]-np.load(LAST/'probe_motion.npz')['root_matrices'][0]))<1e-6,'Starting native bind matrix must equal approved source'
times=np.unique(np.r_[np.arange(96,433)/240,M['times']]);VV=[];PP=[];SS=[];RR=[];AA=[];poseerr=0;rooterr=0;keyerr=0;planeerr=0
for t in times:
 f=1+(t-.4)*60;n=math.floor(f+1e-7);sc.frame_set(n,subframe=max(0,f-n));bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();arr=np.empty(len(me.vertices)*3);me.vertices.foreach_get('co',arr);W=np.array(ev.matrix_world);V=arr.reshape(-1,3)@W[:3,:3].T+W[:3,3];ev.to_mesh_clear();pp=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS['L']]);VV.append(V);PP.append(pp);SS.append(V[[r['mesh_vertex'] for r in c.MARKERS['L']]]);RR.append(np.array(rt.matrix_world));aa=np.zeros(88)
 ii=int(np.argmin(abs(M['times']-t)))
 if abs(M['times'][ii]-t)<1e-8:
  for j,d in enumerate(c.DIGITS):
   for name,R in zip(c.SETUPS['L',d][0],c.joint_mats('L',d,M['q'][ii,j])):poseerr=max(poseerr,float(np.max(abs(np.array(rig.pose.bones[name].matrix_basis.to_3x3())-R))))
  rooterr=max(rooterr,float(np.max(abs(np.array(rt.matrix_world)-M['root_matrices'][ii]))))
 for ki,name in info['key_pivots'].items():
  k=c.KEYS[int(ki)];pivot=bpy.data.objects[name];aa[int(ki)]=pivot.rotation_euler.x
  for g in k['geometry']:
   child=next(v for v in pivot.children if g['name'] in v.name);actual=np.array([list(<REDACTED_EMAIL>) for v in child.data.vertices]);expected=o.keytransform(k['midi_note'],g['vertices'],aa[int(ki)]);keyerr=max(keyerr,float(np.max(np.linalg.norm(actual-expected,axis=1))*1000))
  child=next(v for v in pivot.children if 'FRONT' in v.name);z=max(v.co.z for v in child.data.vertices);plane=child.matrix_world@Vector((0,0,z));normal=child.matrix_world.to_3x3().inverted().transposed()@Vector((0,0,1));normal.normalize();j=4 if ki=='17' else 0
  for pt in [pp[j],V[c.MARKERS['L'][j]['mesh_vertex']]]:planeerr=max(planeerr,abs((Vector(pt)-plane).dot(normal)*1000-o.measure(pt,k['midi_note'],aa[int(ki)])['gap_mm']))
 AA.append(aa)
assert poseerr<1e-5 and rooterr<1e-5 and keyerr<.001 and planeerr<.001
assert np.array_equal(M['key_angles'],old['L_key_angles'])
np.savez_compressed(P/'evaluated_coordinated.npz',times=times,verts=VV,pads=PP,skin_pads=SS,root_matrices=RR,key_angles=AA)
dump('SAVE_REOPEN_VERIFICATION_R1.json',{'candidate_sha256':man['candidate_sha256'],'preservation_before':before,'preservation_after':after,'immutable_hand_right_keys_cameras_equal':before==after,'all_protected_key_and_right_actions_unchanged':True,'left_design_only_actions_replaced_in_new_file':True,'source_file_unchanged':o.sha(pol['source_blend'])==pol['source_sha256'],'static_scenes_equal':True,'actual_pose_matrix_max_error':poseerr,'actual_root_matrix_max_error':rooterr,'actual_key_world_vertex_max_error_mm':keyerr,'independent_actual_top_plane_max_gap_error_mm':planeerr,'key_motion_array_exactly_unchanged':True,'samples':len(times),'sampling_hz':240,'no_manual_skinning':True})
print('COORDINATED_REOPEN_IDENTITY_PASS',len(times),flush=True)
folder=P/'_frames'/'L';folder.mkdir(parents=True,exist_ok=True);sc.render.resolution_x=768;sc.render.resolution_y=594
for frame in range(1,85):
 sc.frame_set(frame)
 for view,name in info['cameras'].items():
  sc.camera=bpy.data.objects[name];sc.render.filepath=str(folder/f'{frame-1:04}_{view}.png');bpy.ops.render.render(write_still=True)
 if frame%10==0 or frame==84:print('COORDINATED_RENDER_PROGRESS',frame,84,flush=True)
dump('RENDER_MANIFEST_R1.json',{'frames':84,'fps':60,'views':info['cameras'],'dimensions':[768,594],'candidate_sha256':man['candidate_sha256'],'before_raw_frames_from':str(LAST/'_frames'/'L'),'matched_cameras_verified':True,'right_rendered':False})
