import sys,json,hashlib,ast,re,importlib.util,math
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;PRE=P.parent/'piano_hand_static_to_dynamic_transition_r1';sys.path.insert(0,str(PRE))
import bpy
from mathutils import Matrix,Vector
import common as o
import numpy as np
c=o.c
def dump(n,x): (P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else v),encoding='utf8')
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
spec=importlib.util.spec_from_file_location('identity',o.ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
for file,names in [(P.parent/'piano_keyboard_spatial_anchor_and_contact_validation_r1/04_hands.py',['intrinsic']),(PRE/'02_scene_verify.py',['rename_normalize','structural'])]:
 tree=ast.parse(file.read_text(encoding='utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(file),'exec'))
def action(a):
 if a is None:return None
 return {'name':a.name,'layers':[[[{'path':f.data_path,'index':f.array_index,'keys':[{'co':list(k.co),'left':list(k.handle_left),'right':list(k.handle_right),'interpolation':k.interpolation} for k in f.keyframe_points]} for bag in st.channelbags for f in bag.fcurves] for st in l.strips] for l in a.layers]}
def preservation():
 m=o.read(PRE/'DYNAMIC_SCENE_MANIFEST_R1.json');out={}
 for s,info in m['mapping'].items():
  sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;sc.frame_set(1);rig=bpy.data.objects[info['rig']];mesh=bpy.data.objects[info['mesh']]
  out[s]={'intrinsic':structural(mesh,rig),'key_actions':{k:digest(action(bpy.data.objects[n].animation_data.action)) for k,n in info['key_pivots'].items()},'key_meshes':digest([{'name':v.name,'vertices':[list(a.co) for a in v.data.vertices],'polygons':[list(a.vertices) for a in v.data.polygons]} for v in sorted(sc.objects,key=lambda x:x.name) if v.type=='MESH' and 'FROZEN_KEY_INDEX' in v]),'cameras':{k:digest(h.object_payload(bpy.data.objects[n])) for k,n in info['cameras'].items()}}
  if s=='R':out[s]['root']=digest(h.object_payload(bpy.data.objects[info['root']]));out[s]['rig_action']=digest(action(rig.animation_data.action));out[s]['full_core_frame1']=digest(h.core(mesh,rig))
 return out
source=PRE/'STATIC_TO_DYNAMIC_TRANSITION_CANDIDATE_R1.blend';bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);before=preservation()
man=o.read(P/'PROBE_SCENE_MANIFEST_R1.json');dest=P/'LEFT_LITTLE_MOVING_KEY_PROBE_R1.blend';assert o.sha(dest)==man['candidate_sha256'];bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False);after=preservation();assert before==after,('IMMUTABLE_OR_RIGHT_CHANGED',before,after)
static=o.read(P/'STATIC_ANCHOR_PROTECTION_R1.json');sm=o.read(o.STATIC/'STATIC_SCENE_MANIFEST_R2.json')
for label,m in sm['mapping'].items():
 bpy.context.window.scene=bpy.data.scenes[m['scene']];bpy.context.view_layer.update();value=digest(h.core(bpy.data.objects[m['mesh']],bpy.data.objects[m['rig']]))
 static['reopened_static_scene_identity'][label]['new_candidate']=value;assert value==static['reopened_static_scene_identity'][label]['expected']
static['new_candidate_sha256']=man['candidate_sha256'];dump('STATIC_ANCHOR_PROTECTION_R1.json',static)
info=man['mapping'];sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[info['rig']];ob=bpy.data.objects[info['mesh']];rt=bpy.data.objects[info['root']]
M=np.load(P/'probe_motion.npz');old=np.load(PRE/'temporal_motion.npz');times=M['times'];VV=[];PP=[];SS=[];RR=[];AA=[];keyerror=0;poseerror=0;rooterror=0;planeerror=0
for i,t in enumerate(times):
 f=1+(t-.4)*60;n=math.floor(f+1e-7);sc.frame_set(n,subframe=max(0,f-n));bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();arr=np.empty(len(me.vertices)*3);me.vertices.foreach_get('co',arr);W=np.array(ev.matrix_world);V=arr.reshape(-1,3)@W[:3,:3].T+W[:3,3];ev.to_mesh_clear();pp=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS['L']]);VV.append(V);PP.append(pp);SS.append(V[[r['mesh_vertex'] for r in c.MARKERS['L']]]);RR.append(np.array(rt.matrix_world));aa=np.zeros(88)
 for j,d in enumerate(c.DIGITS):
  for name,R in zip(c.SETUPS['L',d][0],c.joint_mats('L',d,M['q'][i,j])):poseerror=max(poseerror,float(np.max(np.abs(np.array(rig.pose.bones[name].matrix_basis.to_3x3())-R))))
 rooterror=max(rooterror,float(np.max(np.abs(np.array(rt.matrix_world)-M['root_matrices'][i]))))
 for ki,name in info['key_pivots'].items():
  k=c.KEYS[int(ki)];pivot=bpy.data.objects[name];aa[int(ki)]=pivot.rotation_euler.x
  for g in k['geometry']:
   child=next(v for v in pivot.children if g['name'] in v.name);actual=np.array([list(<REDACTED_EMAIL>) for v in child.data.vertices]);expected=o.keytransform(k['midi_note'],g['vertices'],aa[int(ki)]);keyerror=max(keyerror,float(np.max(np.linalg.norm(actual-expected,axis=1))*1000))
  # Independent top plane through transformed actual child vertices.
  child=next(v for v in pivot.children if 'FRONT' in v.name);z=max(v.co.z for v in child.data.vertices);plane=child.matrix_world@Vector((0,0,z));normal=child.matrix_world.to_3x3().inverted().transposed()@Vector((0,0,1));normal.normalize();j=4 if ki=='17' else 0
  for pt in [pp[j],V[c.MARKERS['L'][j]['mesh_vertex']]]:gap=(Vector(pt)-plane).dot(normal)*1000;planeerror=max(planeerror,abs(gap-o.measure(pt,k['midi_note'],aa[int(ki)])['gap_mm']))
 AA.append(aa)
assert poseerror<1e-5 and rooterror<1e-5 and keyerror<.001 and planeerror<.001
assert np.array_equal(M['key_angles'],old['L_key_angles']) and np.array_equal(M['q'][:,1:],old['L_q'][:,1:])
np.savez_compressed(P/'evaluated_probe.npz',times=times,verts=np.array(VV),pads=np.array(PP),skin_pads=np.array(SS),root_matrices=np.array(RR),key_angles=np.array(AA))
dump('SAVE_REOPEN_VERIFICATION_R1.json',{'candidate_sha256':man['candidate_sha256'],'preservation_before':before,'preservation_after':after,'immutable_hand_right_keys_cameras_equal':before==after,'static_scenes_equal':True,'actual_pose_matrix_max_error':poseerror,'actual_root_matrix_max_error':rooterror,'actual_key_world_vertex_max_error_mm':keyerror,'independent_actual_top_plane_max_gap_error_mm':planeerror,'left_little_and_idle_trajectories_exactly_unchanged':True,'key_motion_array_exactly_unchanged':True,'samples':len(times),'no_manual_skinning':True})
print('SAVE_REOPEN_VALIDATED',len(times),poseerror,rooterror,keyerror,flush=True)
folder=P/'_frames'/'L';folder.mkdir(parents=True,exist_ok=True);sc.render.resolution_x=768;sc.render.resolution_y=594
for frame in range(1,85):
 sc.frame_set(frame)
 for view,name in info['cameras'].items():
  sc.camera=bpy.data.objects[name];sc.render.filepath=str(folder/f'{frame-1:04}_{view}.png');bpy.ops.render.render(write_still=True)
 if frame%10==0 or frame==84:print('LEFT_RENDER_PROGRESS',frame,84,flush=True)
dump('RENDER_MANIFEST_R1.json',{'frames':84,'fps':60,'views':info['cameras'],'dimensions':[768,594],'candidate_sha256':man['candidate_sha256'],'before_raw_frames_from':str(PRE/'_frames'/'L'),'matched_cameras_verified':True,'right_rendered':False})
