import sys,json,hashlib,ast,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
import bpy,numpy as np
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parent;ROOT=P.parents[1];R1=P.parent/'piano_hand_four_pose_static_feasibility_r1';OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1'
sys.path.insert(0,str(OLD));import performance_core as c
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
sp=importlib.util.spec_from_file_location('identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
tree=ast.parse((P.parent/'piano_keyboard_spatial_anchor_and_contact_validation_r1/04_hands.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='intrinsic'],type_ignores=[]),'intrinsic','exec'))
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def normalized_identity(ob,rig,info):
 parent=rig.parent;world=rig.matrix_world.copy();basis={b.name:b.matrix_basis.copy() for b in rig.pose.bones};color=list(ob.color);tag=ob.get('STATIC_POSE');ob.color=info['original_color'];del ob['STATIC_POSE'];rig.parent=None;rig.matrix_world=Matrix.Identity(4);h.neutral(rig);value=digest(intrinsic(ob,rig));rig.parent=parent;rig.matrix_world=world
 for name,m in basis.items():rig.pose.bones[name].matrix_basis=m
 ob.color=color;ob['STATIC_POSE']=tag;bpy.context.view_layer.update();return value
def cameras(info):
 return {v:{'matrix_world':[list(r) for r in bpy.data.objects[n].matrix_world],'type':bpy.data.objects[n].data.type,'ortho_scale':bpy.data.objects[n].data.ortho_scale,'clip_start':bpy.data.objects[n].data.clip_start,'clip_end':bpy.data.objects[n].data.clip_end} for v,n in info['cameras'].items()}
sol=read(P/'SOLVED_STATIC_POSES_R2.json');policy=read(P/'STATIC_REFINEMENT_POLICY_R2.json');source=R1/'STATIC_POSTURE_CANDIDATE_R1.blend';assert sha(source)==policy['source_candidate_sha256'];assert sha(P/'STATIC_REFINEMENT_POLICY_R2.json')==sol['policy_sha256'];oldman=read(R1/'STATIC_SCENE_MANIFEST_R1.json');mapping=oldman['mapping'];dest=P/'STATIC_POSTURE_REFINED_CANDIDATE_R2.blend';assert not dest.exists()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);before={};camera_before={}
for pose,info in mapping.items():
 sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[info['rig']];ob=bpy.data.objects[info['mesh']];root=bpy.data.objects[info['root']];bpy.context.view_layer.update()
 before[pose]=normalized_identity(ob,rig,info);assert before[pose]==info['source_intrinsic_at_import'];camera_before[pose]=cameras(info)
 row=sol['poses'][pose];root.matrix_world=Matrix.Translation(Vector(row['root_xyz_m']))@Matrix(row['root_rotation_matrix']).to_4x4()@Matrix(c.RIG[info['hand']]['native_to_canonical']);rig.matrix_basis=Matrix.Identity(4)
 q=np.radians(row['joint_increments_deg'])
 for j,d in enumerate(c.DIGITS):
  for name,r in zip(c.SETUPS[info['hand'],d][0],c.joint_mats(info['hand'],d,q[j])):rig.pose.bones[name].rotation_mode='QUATERNION';rig.pose.bones[name].rotation_quaternion=Matrix(r).to_quaternion()
 sc['PHASE']='PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2';sc['POLICY_SHA256']=sol['policy_sha256'];sc['SOURCE_R1_SHA256']=policy['source_candidate_sha256'];bpy.context.view_layer.update()
bpy.context.window.scene=bpy.data.scenes[mapping['L1']['scene']];assert len(bpy.data.actions)==0;bpy.ops.wm.save_as_mainfile(filepath=str(dest));bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False)
arrays={};out={};identities={};camera_after={}
for pose,info in mapping.items():
 sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[info['rig']];ob=bpy.data.objects[info['mesh']];root=bpy.data.objects[info['root']];s=info['hand'];bpy.context.view_layer.update();V,F=h.coords(ob);pads=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS[s]]);skin=np.array([V[r['mesh_vertex']] for r in c.MARKERS[s]]);pred=np.array(sol['poses'][pose]['pad_prediction_xyz_m']);err=float(np.max(np.linalg.norm(pads-pred,axis=1))*1000);assert err<.03
 out[pose]={'pad_xyz_m':pads.tolist(),'skin_pad_xyz_m':skin.tolist(),'FK_saved_reopened_max_error_mm':err,'skin_rigid_pad_drift_mm':(np.linalg.norm(skin-pads,axis=1)*1000).tolist(),'evaluated_vertices':len(V),'bone_count':len(rig.data.bones),'shape_key_values':h.values(ob),'root_scale_singular_values':np.linalg.svd(np.array(root.matrix_world)[:3,:3],compute_uv=False).tolist()}
 arrays[pose+'_verts']=V;arrays[pose+'_pads']=pads;arrays[pose+'_skin_pads']=skin;camera_after[pose]=cameras(info);ident=normalized_identity(ob,rig,info);identities[pose]={'before':before[pose],'after':ident,'matches':ident==before[pose]};assert identities[pose]['matches'];assert camera_after[pose]==camera_before[pose]
np.savez_compressed(P/'evaluated_static_candidate.npz',**arrays)
dump('STATIC_SCENE_MANIFEST_R2.json',{'candidate_path':str(dest),'candidate_sha256':sha(dest),'source_R1_sha256':sha(source),'policy_sha256':sol['policy_sha256'],'mapping':mapping,'readback':out,'intrinsic_identity':identities,'camera_before':camera_before,'camera_after':camera_after,'same_camera_same_framing':True,'keyboard_rebuilt':False,'material_changes':False,'candidate_count':1,'static_scene_count':4,'new_action_count':0,'save_reopen_verified':True,'in_memory_identity_reset_not_saved':True})
print('R2_SAVED_REOPENED_SAME_CAMERA',json.dumps({p:{'FK_error_mm':o['FK_saved_reopened_max_error_mm'],'skin_drift_max_mm':max(o['skin_rigid_pad_drift_mm'])} for p,o in out.items()}),flush=True)
