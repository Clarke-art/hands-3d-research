import bpy,sys,ast,importlib.util
from mathutils import Matrix,Vector,Quaternion
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
locked();A=np.load(P/'model_a_evaluations.npz');old=np.load(PRE/'spatial_evaluations.npz');sol=read(P/'MODEL_A_SOLUTION_R1.json')
bpy.ops.wm.open_mainfile(filepath=str(PRE/'PIANO_KEYBOARD_SPATIAL_ANCHOR_VALIDATION_CANDIDATE_R1.blend'),load_ui=False,use_scripts=False);sc=bpy.context.scene
sp=importlib.util.spec_from_file_location('identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
for file,fn in [(ROOT/'audits/pianovam_first_web_corrective_ab_isolation_r1/isolate.py','action_payload'),(PRE/'04_hands.py','intrinsic')]:
 tree=ast.parse(file.read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fn],type_ignores=[]),fn,'exec'))
def linear(ob):
 for l in ob.animation_data.action.layers:
  for s in l.strips:
   for b in s.channelbags:
    for f in b.fcurves:
     for k in f.keyframe_points:k.interpolation='LINEAR'
for side,c in ex['cfg'].items():
 rig=bpy.data.objects[c['rig']];assert digest(action_payload(rig.animation_data.action))==ex['action_hashes'][side];root=rig.parent;assert root.name=='AUDIT_ONLY_KEYBOARD_ROOT_'+side
 previous_action=root.animation_data.action;assert not previous_action.name.startswith('PIANOVAM');root.animation_data_clear();bpy.data.actions.remove(previous_action)
 root.name='AUDIT_ONLY_LOW_DOF_ROOT_'+side;Q=np.array(ex['frames'][side]['rotation']);w=np.array(ex['frames'][side]['native_wrist']);last=None
 for i in range(N):
  R=A[side+'_rotation'][i]@Q;q=Matrix(R).to_quaternion()
  if last is not None and q.dot(last)<0:q.negate()
  root.rotation_quaternion=q;root.location=A[side+'_roots'][i]-R@w;root.keyframe_insert(data_path='location',frame=1+i*.5);root.keyframe_insert(data_path='rotation_quaternion',frame=1+i*.5);last=q.copy()
 linear(root);root['MODEL']='A_XYZ_YAW';root['translation_only_dynamic']=False;root['PRODUCT_SPATIALIZATION_NOT_MOCAP']=True
sc['PHASE']='PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_R1';sc['STATUS']='MODEL_A_FAILED_PENDING_HUMAN_REVIEW';sc['MODEL_B']='NOT_RUN_GATE_NOT_MET';sc['USAGE_SCOPE']='INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY';sc['NOT_PRODUCTION']=True
# Cameras frame the union of OLD and NEW for truly matched comparison.
points=np.concatenate([dataset[s+'_verts'].reshape(-1,3) for dataset in [A,old] for s in ['R','L']]);cameras={}
for name in ['PIANO_PLAYER_VIEW','TEACHING_TOP_OBLIQUE','CONTACT_CLOSE']:
 cam=bpy.data.objects[name];pts=points
 if name=='PIANO_PLAYER_VIEW':pts=np.concatenate([pts,np.array([v for k in keys for g in k['geometry'] for v in g['vertices']])])
 axes=np.array(cam.matrix_world.to_3x3());pr=(pts-np.array(cam.location))@axes;scale=max(np.ptp(pr[:,0]),np.ptp(pr[:,1])*1200/660)*1.12;cam.data.ortho_scale=float(scale);shift=np.array([.5*(pr[:,0].min()+pr[:,0].max()),.5*(pr[:,1].min()+pr[:,1].max()),0]);cam.location=np.array(cam.location)+axes@shift;bpy.context.view_layer.update();cameras[name]={'matrix_world':[list(r) for r in cam.matrix_world],'ortho_scale':float(scale),'framing':'FULL_421_OLD_NEW_UNION','resolution':[1200,660]}
dump('MATCHED_CAMERA_POLICY_R1.json',cameras);sc.frame_set(1);dest=P/'PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_CANDIDATE_R1.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest));bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False)
errs={s:[] for s in ['R','L']};paderrs={s:[] for s in ['R','L']};marker=read(P/'FINGERTIP_CONTACT_MARKERS_R1.json')['markers'];pose_cache={s:[] for s in ['R','L']}
for i in range(N):
 bpy.context.scene.frame_set(1+i//2,subframe=(i%2)*.5)
 for s,c in ex['cfg'].items():
  v,_=h.coords(bpy.data.objects[c['mesh']]);errs[s].append(float(np.max(np.abs(v-A[s+'_verts'][i]))*1000))
  for r in marker[s]:paderrs[s].append(float(np.linalg.norm(np.array(bpy.data.objects['VIRTUAL_PAD_'+s+'_'+r['digit']].matrix_world.translation)-A[s+'_pads'][i,r['finger']-1])*1000))
identity={};safety={}
for s,c in ex['cfg'].items():
 rig=bpy.data.objects[c['rig']];ob=bpy.data.objects[c['mesh']];actual=digest(action_payload(rig.animation_data.action));assert actual==ex['action_hashes'][s];assert max(errs[s])<.005 and max(paderrs[s])<.005
 rig.parent=None;rig.animation_data.action=None;h.neutral(rig);zero,F=h.coords(ob);current=digest(intrinsic(ob,rig));assert current==read(PRE/'STATIC_COMPONENT_DIGESTS_R1.json')[s]
 Q=np.array(ex['frames'][s]['rotation']);w=np.array(ex['frames'][s]['native_wrist']);zero=(zero-w)@Q.T;local=np.load(PRE/'hand_motion_canonical.npz')[s+'_verts'];edges=np.array([list(e.vertices) for e in ob.data.edges]);length=np.linalg.norm(local[:,edges[:,0]]-local[:,edges[:,1]],axis=2);length0=np.linalg.norm(zero[edges[:,0]]-zero[edges[:,1]],axis=1);tri=np.array([[f[0],f[j],f[j+1]] for f in F for j in range(1,len(f)-1)]);areas=np.linalg.norm(np.cross(local[:,tri[:,1]]-local[:,tri[:,0]],local[:,tri[:,2]]-local[:,tri[:,0]]),axis=2)*.5;extent=np.linalg.norm(np.ptp(local,axis=1),axis=1)
 safety[s]={'NaN_Inf':int((~np.isfinite(A[s+'_verts'])).sum()),'gross_collapse':int((extent<np.linalg.norm(np.ptp(zero,axis=0))*.2).sum()),'degenerate_edges':int((length<1e-8).sum()),'degenerate_triangles':int((areas<1e-14).sum()),'gross_tearing_over10x':int((length/length0>10).sum()),'ZERO_restore':'intrinsic full component digest MATCH after removing audit root and detaching Action','saved_reopened_421_geometry_max_error_mm':max(errs[s]),'saved_reopened_marker_max_error_mm':max(paderrs[s])}
 assert all(safety[s][k]==0 for k in ['NaN_Inf','gross_collapse','degenerate_edges','degenerate_triangles','gross_tearing_over10x'])
 identity[s]={'expected_action_sha256':ex['action_hashes'][s],'saved_reopened_action_sha256':actual,'identity':'MATCHED','static_component_digest':current,'mesh_weights_rest_driver_corrective_identity':'MATCHED','internal_action_mutations':0,'external_layer_only':True}
dump('ACTION_IDENTITY_R1.json',{'hands':identity,'candidate_sha256':sha(dest),'saved_reopened':True,'all421_evaluations_verified':True});dump('MINIMUM_SAFETY_R1.json',{'structural_safety':'PASS','spatial_contact_safety':'NOT_CLEARED','hands':safety,'no_hidden_crossing_normal_dot_anatomy_audit':True,'root_continuity':read(P/'MODEL_A_RESULT_R1.json')['machine_gates']['continuity']});print('CANDIDATE_VERIFIED',flush=True)
