import sys,ast,json,hashlib,math,importlib.util,types
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Matrix,Vector,Quaternion
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];PREV=ROOT/'audits/pianovam_single_sample_right_hand_retarget_r1'
BASE=ROOT/'production_spec/left_hand_product_baseline_r1/LEFT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend'
ACTION='PIANOVAM_PHYSICAL_LEFT_MIRRORED_MAPPING_R1';TEST=OUT/'LEFT_HAND_REAL_MOTION_VALIDATION_CANDIDATE_R1.blend'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf-8')
protected=read(OUT/'PROTECTED_INPUTS_BEFORE_R1.json')
def protect():assert all(sha(ROOT/p)==s for p,s in protected.items())
protect();assert read(OUT/'LEFT_SOURCE_QUALIFICATION_R1.json')['LEFT_REAL_MOTION_SOURCE']=='VERIFIED'
spec=importlib.util.spec_from_file_location('product_identity_readers',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');identity=importlib.util.module_from_spec(spec);spec.loader.exec_module(identity)
ob,rig=identity.open_asset(BASE)
def static():
 p=identity.core(ob,rig);p.pop('pose_state');p['armature_object'].pop('animation');return p
native=static();zero,faces=identity.coords(ob)
# AST-read exact mature solver methods; no old top-level execution or old .blend loading.
source=ROOT/'audits/pianovam_retarget_local_axis_mapping_correction_r1/mapping_core.py';tree=ast.parse(source.read_text())
funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['arr','norm','frame','signed']]
klass=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Solver')
klass.body=[n for n in klass.body if isinstance(n,ast.FunctionDef) and n.name in ['__init__','raw','smoothed']]
# The ONLY loader substitutions: physical-left JSON field and a reflection of its
# coordinate chart. This uses measured LEFT observations, never a RIGHT motion track.
class LeftLoader(ast.NodeTransformer):
 def visit_Subscript(self,node):
  self.generic_visit(node)
  if isinstance(node.slice,ast.Constant) and node.slice.value=='Left':node.slice.value='Right'
  return node
init=klass.body[0];LeftLoader().visit(init)
loop=next(n for n in init.body if isinstance(n,ast.For))
loop.body.insert(1,ast.parse('p[:,0] *= -1').body[0])
module=ast.fix_missing_locations(ast.Module(body=funcs+[klass],type_ignores=[]))
(OUT/'approved_solver_with_left_source_adapter.py').write_text(ast.unparse(module)+'\n',encoding='utf-8')
exec(compile(module,'approved_solver_with_left_source_adapter','exec'),globals())
plane=read(ROOT/'audits/left_hand_canonical_mirror_baseline_r1/CANONICAL_MIRROR_PLANE_R1.json');S=Matrix(plane['reflection_armature_matrix']);H=Matrix.Diagonal(Vector((-1,1,1,1)));H3=H.to_3x3()
# A virtual coordinate representation only; real mesh/bones/rest remain untouched.
virtual_bones=[types.SimpleNamespace(name=b.name[:-2]+'_R',matrix_local=<REDACTED_EMAIL>_local@H,head_local=<REDACTED_EMAIL>_local) for b in rig.data.bones]
virtual_rig=types.SimpleNamespace(data=types.SimpleNamespace(bones=virtual_bones))
solver=Solver(None,virtual_rig,iteration=2)
sequences={b.name:[] for b in rig.data.bones if b.use_deform};rawseq={n:[] for n in sequences}
for i in range(421):
 for target,result in [(sequences,solver.smoothed(i)[0]),(rawseq,solver.raw(i)[0])]:
  for rname,q in result.items():
   n=rname[:-2]+'_L';left=Quaternion((q.w,q.x,-q.y,-q.z));left.normalize()
   if target[n] and left.dot(target[n][-1])<0:left.negate()
   target[n].append(left)
# Verify conjugation at the rotation-matrix level for every raw observation.
conjugation=max(max(abs((<REDACTED_EMAIL>(i)[0][n[:-2]+'_R'].to_matrix()@H3)[r][c]-rawseq[n][i].to_matrix()[r][c]) for r in range(3) for c in range(3)) for i in range(421) for n in rawseq)
assert conjugation<2e-6
calibration={n[:-2]+'_L':{'virtual_right_anatomical_frame':[list(r) for r in a],'virtual_right_rest_offset':[list(r) for r in solver.calibration[n]]} for n,a in solver.anatom.items()}
dump('LEFT_RETARGET_MAPPING_R1.json',{'LEFT_RETARGET_MAPPING_SOURCE':'MIRRORED_FROM_APPROVED_RIGHT_MAPPING','approved_source':source.relative_to(ROOT).as_posix(),'approved_source_sha256':sha(source),'approved_solver_iteration':2,'methods_reused':['__init__ calibration','raw anatomical mapping','smoothed quaternion temporal treatment'],'source_loader_only_changes':['JSON physical LEFT=Right','camera chart reflection J=diag(-1,1,1) applied to actual LEFT observations'],'no_right_motion_used':True,'coordinate_derivation':'Measured left camera points pL -> virtual right chart J pL. If PL=[radial,distal,radial cross distal], Pvirtual=J PL K with K=diag(1,1,-1); palm-local vectors map by K. Canonical rest virtual right = S RestL H, H=diag(-1,1,1,1). Apply exact approved mapping, then BasisL=H BasisVirtual H. This changes coordinate charts, not source motion or asset.','reflection_armature':list(map(list,S)),'local_H':list(map(list,H)),'matrix_conjugation_max_error':conjugation,'MCP_calibration':calibration,'hinges_virtual_right_local':{n[:-2]+'_L':list(h) for n,h in solver.hinges.items()},'thumb_neutral_from_actual_left_window_median':list(solver.thumb_neutral),'thumb_mapping':'Approved iteration2 window-median CMC direction, palm-normal thumb frame, transported frozen rest offset; MCP/IP signed hinges. No CMC noisy axial twist.','smoothing_kernel':[.25,.5,.25],'source_hz':60,'interpolation':'LINEAR quaternion component keys at half-frame positions; normalized by Blender evaluation','wrist':'Fixed canonical translation, source palm orientation relative to first observation','MAPPING_CORRECTION_COUNT':0,'asset_geometry_rest_weights_corrective_edits':False})
rig.animation_data_create();action=bpy.data.actions.new(ACTION);action.use_fake_user=True;rig.animation_data.action=action
for k,v in {'SOURCE_RECORDING_ID':'2024-03-04_03-46-36','SOURCE_FIELD':'Right (physical LEFT, video verified)','SOURCE_WINDOW':'11.5-18.5sec','USAGE_SCOPE':'INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY','LICENSE':'CC BY-NC-SA 4.0','DESIGN_ONLY':True,'HUMAN_APPROVAL_PENDING':True,'DO_NOT_PROMOTE_DATASET_MOTION_TO_COMMERCIAL_PRODUCT':True,'MAPPING_SOURCE':'MIRRORED_FROM_APPROVED_RIGHT_MAPPING','MAPPING_CORRECTION_COUNT':0}.items():action[k]=v
for n,seq in sequences.items():
 p=rig.pose.bones[n];assert p.rotation_mode=='QUATERNION'
 for i,q in enumerate(seq):p.rotation_quaternion=q;p.keyframe_insert(data_path='rotation_quaternion',frame=1+i/2,group=n)
for layer in action.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:
   for f in bag.fcurves:
    for k in f.keyframe_points:k.interpolation='LINEAR'
scene=bpy.context.scene;scene.name='LEFT_REAL_MOTION_VALIDATION_DESIGN_ONLY';scene.frame_start=1;scene.frame_end=210;scene.render.fps=30;scene.render.fps_base=1
for k in list(scene.keys()):del scene[k]
for k,v in {'PHASE':'LEFT_HAND_REAL_MOTION_RETARGET_VALIDATION_R1','DESIGN_ONLY':True,'HUMAN_APPROVAL_PENDING':True,'USAGE_SCOPE':'INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY','PRODUCTION_PROMOTION':'NO'}.items():scene[k]=v
E=np.array([list(e.vertices) for e in ob.data.edges]);tri=np.array([[f[0],f[j],f[j+1]] for f in faces for j in range(1,len(f)-1)]);faceid=np.array([fi for fi,f in enumerate(faces) for j in range(1,len(f)-1)])
def areas(v):return np.bincount(faceid,weights=np.linalg.norm(np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]]),axis=1)*.5,minlength=len(faces))
A0=areas(zero);evaluated=[];corrective=[];bad=[];dirs={n:[] for n in sequences}
for i in range(421):
 scene.frame_set(1+i//2,subframe=(i%2)*.5);v,f=identity.coords(ob);assert f==faces;ar=areas(v);el=np.linalg.norm(v[E[:,0]]-v[E[:,1]],axis=1)
 counts=[int(np.size(v)-np.isfinite(v).sum()),int(((ar<=1e-12)|(ar/A0<=1e-6)).sum()),int((el<=1e-12).sum())]
 if any(counts):bad.append({'observation':i,'NaN_Inf_collapse_degenerate':counts})
 evaluated.append(v);corrective.append(identity.values(ob))
 for n in dirs:dirs[n].append(rig.pose.bones[n].matrix.to_3x3()@Vector((0,1,0)))
rig.animation_data.action=None;identity.neutral(rig);restore=float(np.max(np.abs(identity.coords(ob)[0]-zero))*1000);assert restore==0 and static()==native
rig.animation_data.action=action;scene.frame_set(1);bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(TEST),compress=False)
ob,rig=identity.open_asset(TEST);rig.animation_data.action=None;identity.neutral(rig);assert static()==native;assert np.array_equal(identity.coords(ob)[0],zero)
# Leave saved file as motion; reopen validation itself is not saved.
steps={n:[math.degrees(a.rotation_difference(b).angle) for a,b in zip(qs,qs[1:])] for n,qs in sequences.items()};directionsteps={n:[math.degrees(a.angle(b)) for a,b in zip(vs,vs[1:])] for n,vs in dirs.items()}
dump('LEFT_REAL_MOTION_ACTION_R1.json',{'action':ACTION,'candidate':TEST.relative_to(ROOT).as_posix(),'candidate_sha256':sha(TEST),'DESIGN_ONLY':True,'observations':421,'source_frames':[690,1110],'keys_per_quaternion_channel':421,'animated_bones':16,'TIP_animation_channels':0,'wrist_translation_keys':0,'scene_fps':30,'render_frame_count':210,'duration_seconds':7,'source_endpoint_key':211,'MAPPING_CORRECTION_COUNT':0,'corrective_values':corrective,'max_local_step_deg_by_bone':{n:max(s) for n,s in steps.items()},'max_world_direction_step_deg_by_bone':{n:max(s) for n,s in directionsteps.items()},'product_static_payload_exact_after_save_reopen':True,'USAGE_SCOPE':'INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY','license':'CC BY-NC-SA 4.0'})
dump('MINIMUM_SAFETY_R1.json',{'machine_status':'PASS' if not bad else 'FAIL','frames_checked':421,'bad_observations':bad,'NaN_Inf':sum(r['NaN_Inf_collapse_degenerate'][0] for r in bad),'gross_collapse':sum(r['NaN_Inf_collapse_degenerate'][1] for r in bad),'degenerate_edges':sum(r['NaN_Inf_collapse_degenerate'][2] for r in bad),'topology_tearing':'NO_TOPOLOGY_CHANGE','ZERO_restore_mm':restore,'static_mesh_weights_rig_rest_UV_shading_corrective_driver_exact':True,'visible_penetration':'PENDING_PRODUCT_VIDEO_REVIEW','machine_metrics_do_not_imply_Human_PASS':True})
np.savez_compressed(OUT/'evaluated_motion.npz',vertices=np.array(evaluated),zero=zero)
dump('RENDER_INPUT_R1.json',{'faces':faces,'smooth':[p.use_smooth for p in ob.data.polygons],'reflection':list(map(list,S)),'native_source':'LEFT R1 unchanged; rendering actual evaluated Action geometry'})
protect();print('LEFT_ACTION_CREATED',ACTION,'minimum_safety',not bad,'ZERO',restore,flush=True)
