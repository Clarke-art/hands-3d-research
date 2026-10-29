import bpy,sys,math,ast,importlib.util,re
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from stage_common import *
from mathutils import Matrix,Vector
spec=importlib.util.spec_from_file_location('identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
intrinsic_tree=ast.parse((ROOT/'audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/04_hands.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in intrinsic_tree.body if isinstance(n,ast.FunctionDef) and n.name=='intrinsic'],type_ignores=[]),'inherited_intrinsic','exec'))
tree=ast.parse((ROOT/'audits/piano_hand_static_to_dynamic_transition_r1/02_scene_verify.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['rename_normalize','structural','linear']],type_ignores=[]),'inherited_helpers','exec'))
assert sha(P/'RECOVERY_POLICY.json')==read(P/'POLICY_LOCK.json')['policy_sha256']
assert read(P/'RECOVERY_POLICY.json')['classification']=='WARN_ACCEPTABLE'
assert sha(P/'motion.npz')==read(P/'SAVED_MOTION_RECONSTRUCTION.json')['motion_sha256']
old=read(R2/'SCENE_MANIFEST.json');A=dict(np.load(P/'motion.npz'));orig=dict(np.load(R2/'motion.npz'))
assert all(np.array_equal(A[k],orig[k]) for k in A if k!='L_q')
dest=P/'STAGE_B_R3_RECOVERED_CONTACT_DESIGN_ONLY.blend';assert not dest.exists()
assert sha(old['path'])==old['sha256']
bpy.ops.wm.open_mainfile(filepath=old['path'],load_ui=False,use_scripts=False)
sm=read(o.STATIC/'STATIC_SCENE_MANIFEST_R2.json');static={}
for label,info in sm['mapping'].items():
    bpy.context.window.scene=bpy.data.scenes[info['scene']];bpy.context.view_layer.update();static[label]=digest(h.core(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]))
assert static==old['static_four_core_sha256']
sc=bpy.data.scenes[old['scene']];bpy.context.window.scene=sc;mapping=old['mapping'];rig=bpy.data.objects[mapping['rig']];mesh=bpy.data.objects[mapping['mesh']]
structure=structural(mesh,rig)
keygeometry={}
for k in c.KEYS:
    obs=[v for v in sc.objects if v.type=='MESH' and v.get('FROZEN_KEY_INDEX')==k['key_index']]
    keygeometry[str(k['key_index'])]=digest([{'v':[list(v.co) for v in ob.data.vertices],'p':[list(p.vertices) for p in ob.data.polygons]} for ob in sorted(obs,key=lambda x:x.name)])
rig.animation_data_clear()
for i,t in enumerate(A['times']):
    for j,d in enumerate(c.DIGITS):
        for name,rot in zip(c.SETUPS['L',d][0],c.joint_mats('L',d,A['L_q'][i,j])):
            b=rig.pose.bones[name];b.rotation_mode='QUATERNION';quat=Matrix(rot).to_quaternion()
            if i and b.rotation_quaternion.dot(quat)<0:quat.negate()
            b.rotation_quaternion=quat;b.keyframe_insert(data_path='rotation_quaternion',frame=1+t*60,group=d)
rig.animation_data.action.name='DESIGN_ONLY_STAGE_B_R3_SAVED_TRAJECTORY_RECOVERY_JOINTS';linear(rig)
# R2 delivered OVERHEAD uses 0.60. Copy the delivered camera, not the older
# saved scene's 0.56 scale. Teaching and side remain byte-identical transforms.
bpy.data.objects[old['cameras']['OVERHEAD']].data.ortho_scale=read(R2/'VIDEO_FRAMING_REPAIR.json')['new_ortho_scale']
cameras={view:dict(name=name,matrix_world=[list(v) for v in bpy.data.objects[name].matrix_world],ortho_scale=bpy.data.objects[name].data.ortho_scale) for view,name in old['cameras'].items()}
sc.name='STAGE_B_R3_DETERMINISTIC_RECOVERY_ONLY';sc['DESIGN_ONLY']=True;sc['HUMAN_APPROVAL_PENDING']=True;sc['REFERENCE_MOTION_PRESERVED']=True
sc.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest))
bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False)
for label,info in sm['mapping'].items():
    bpy.context.window.scene=bpy.data.scenes[info['scene']];bpy.context.view_layer.update();assert digest(h.core(bpy.data.objects[info['mesh']],bpy.data.objects[info['rig']]))==static[label]
sc=bpy.data.scenes['STAGE_B_R3_DETERMINISTIC_RECOVERY_ONLY'];bpy.context.window.scene=sc;rig=bpy.data.objects[mapping['rig']];mesh=bpy.data.objects[mapping['mesh']]
assert structural(mesh,rig)==structure
Vs=[];pads=[];skinpads=[];keyangles=[];fkerr=0;keyerr=0
for i,t in enumerate(A['times']):
    f=1+t*60;nf=math.floor(f+1e-8);sc.frame_set(nf,subframe=max(0,f-nf));bpy.context.view_layer.update();V,_=h.coords(mesh)
    pp=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS['L']])
    expected=(o.worldpads('L',A['L_q'][i])-np.array(o.ANCHORS['L1']['root_xyz_m']))@A['L_extra_rotation'][i].T+np.array(o.ANCHORS['L1']['root_xyz_m'])+A['L_delta'][i]
    fkerr=max(fkerr,float(np.max(np.linalg.norm(pp-expected,axis=1))*1000));Vs.append(V);pads.append(pp);skinpads.append(V[[r['mesh_vertex'] for r in c.MARKERS['L']]])
    aa=np.zeros(88)
    for ki,name in old['key_pivots'].items():
        pv=bpy.data.objects[name];aa[int(ki)]=pv.rotation_euler.x;k=c.KEYS[int(ki)]
        for g in k['geometry']:
            obj=next(v for v in pv.children if g['name'] in v.name);actual=np.array([list(<REDACTED_EMAIL>) for v in obj.data.vertices]);expect=o.keytransform(k['midi_note'],g['vertices'],aa[int(ki)])
            keyerr=max(keyerr,float(np.max(np.linalg.norm(actual-expect,axis=1))*1000))
    keyangles.append(aa)
assert fkerr<.03 and keyerr<.03
for k in c.KEYS:
    obs=[v for v in sc.objects if v.type=='MESH' and v.get('FROZEN_KEY_INDEX')==k['key_index']]
    assert keygeometry[str(k['key_index'])]==digest([{'v':[list(v.co) for v in ob.data.vertices],'p':[list(p.vertices) for p in ob.data.polygons]} for ob in sorted(obs,key=lambda x:x.name)])
np.savez_compressed(P/'evaluated.npz',times=A['times'],L_verts=Vs,L_pads=pads,L_skin_pads=skinpads,key_angles=keyangles)
dump('SCENE_MANIFEST.json',dict(path=str(dest),sha256=sha(dest),scene=sc.name,mapping=mapping,cameras=old['cameras'],camera_parameters=cameras,key_pivots=old['key_pivots'],static_four_core_sha256=static,four_static_scenes_unchanged=True,hand_structure_unchanged=True,all_88_key_geometry_unchanged=True,original_root_and_key_actions_retained=True,right_in_performance_scene=False,candidate_count=1,save_reopen_verified=True,actual_pad_vs_FK_max_mm=fkerr,actual_key_world_parity_max_mm=keyerr,key_angle_parity_max_rad=float(np.max(abs(np.array(keyangles)-A['key_angles']))),frames=sc.frame_end,render_engine=sc.render.engine))
print('SINGLE_R3_SCENE_SAVED_REOPENED_SKIN_READBACK',fkerr,keyerr,flush=True)

dump("RECOVERY_ATTEMPT.json",dict(attempt=1,status="BLENDER_SAVED_REOPENED_READBACK_VERIFIED",NEW_SOLVER_CALLS=0,candidate_count=1,source_guard_sha256=read(P/"POLICY_LOCK.json")["source_guard_sha256"],Blender_candidate_saved=True))
