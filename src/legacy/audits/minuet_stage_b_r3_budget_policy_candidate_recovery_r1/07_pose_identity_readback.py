"""Read reopened candidate joint matrices and original root. Never save blend."""
import bpy,sys,math
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from stage_common import *
man=read(P/'SCENE_MANIFEST.json');A=dict(np.load(P/'motion.npz'));before=sha(man['path']);assert before==man['sha256']
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[man['mapping']['rig']];root=bpy.data.objects[man['mapping']['root']]
maxerr=0.;roots=[];camera_values={v:dict(matrix=[list(r) for r in bpy.data.objects[n].matrix_world],scale=bpy.data.objects[n].data.ortho_scale) for v,n in man['cameras'].items()}
for i,t in enumerate(A['times']):
    f=1+t*60;nf=math.floor(f+1e-8);sc.frame_set(nf,subframe=max(0,f-nf));bpy.context.view_layer.update();roots.append(np.array(root.matrix_world))
    for j,d in enumerate(c.DIGITS):
        expected=c.joint_mats('L',d,A['L_q'][i,j])
        for name,r in zip(c.SETUPS['L',d][0],expected):
            actual=np.array(rig.pose.bones[name].matrix_basis.to_3x3());maxerr=max(maxerr,float(np.max(abs(actual-r))))
old=read(R2/'SCENE_MANIFEST.json');bpy.ops.wm.open_mainfile(filepath=old['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[old['scene']];bpy.context.window.scene=sc;oldroot=bpy.data.objects[old['mapping']['root']];rooterr=0.;camera_checks=[]
for i,t in enumerate(A['times']):
    f=1+t*60;nf=math.floor(f+1e-8);sc.frame_set(nf,subframe=max(0,f-nf));bpy.context.view_layer.update();rooterr=max(rooterr,float(np.max(abs(np.array(oldroot.matrix_world)-roots[i]))))
for v,n in old['cameras'].items():
    oldcam=bpy.data.objects[n];expectedscale=read(R2/'VIDEO_FRAMING_REPAIR.json')['new_ortho_scale'] if v=='OVERHEAD' else oldcam.data.ortho_scale
    camera_checks.append(dict(view=v,matrix_error=float(np.max(abs(np.array(camera_values[v]['matrix'])-np.array(oldcam.matrix_world)))),scale_error=abs(camera_values[v]['scale']-expectedscale)))
assert maxerr<1e-5 and rooterr<1e-8 and all(x['matrix_error']<1e-8 and x['scale_error']<1e-6 for x in camera_checks)
assert sha(man['path'])==before
dump('FULL_POSE_AND_CAMERA_IDENTITY.json',dict(samples=len(A['times']),all15_joint_bone_matrices_cover_20_DOF=True,actual_matrix_basis_vs_saved_numeric_max_abs=maxerr,actual_root_matrix_vs_R2_max_abs=rooterr,cameras_match_R2_delivered_views=camera_checks,candidate_sha256_unchanged=before,read_only_reopen=True,NEW_SOLVER_CALLS=0,pass_=True))
print('READ_ONLY_ALL20_DOF_ROOT_CAMERA_IDENTITY_PASS',maxerr,rooterr,flush=True)
