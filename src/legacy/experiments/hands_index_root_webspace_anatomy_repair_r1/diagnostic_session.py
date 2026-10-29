import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import support as s
from support import *
PREV=ROOT/'experiments/hands_anatomical_whole_hand_pose_repair_r1/ROUND_2_STATIC_NOT_APPROVED.blend'
for r in read(ROOT/'experiments/hands_anatomical_whole_hand_pose_repair_r1/PROTECTED_SHA256_BEFORE_AFTER.json')['files']:READS[r['path']]=sha(r['path'])
for p in [PREV,ROOT/'audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_REPORT.md',ROOT/'audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md',ROOT/'audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_CAUSAL_DIAGNOSIS_R1_REPORT.md']:
 READS[str(p)]=sha(p)
save('PROTECTED_BEFORE.json',dict(files=[dict(path=p,sha256=h) for p,h in READS.items()]))
def transform(V,M):return (np.c_[V,np.ones(len(V))]@np.array(M).T)[:,:3]
def snapshot(identity,path,reuse=False):
 global sc,rig,mesh,left,lrig
 sc,rig,mesh,left,lrig=s.open_scene(path,reuse_loaded=reuse);c.settime(sc,2.6)
 V,T,F=s.coords_tri(mesh);RV=np.array([list(v.co) for v in mesh.data.vertices]);rig_RV=transform(RV,rig.matrix_world.inverted()@mesh.matrix_world)
 can=np.array(c.RIG['R']['bones']['INDEX_MCP_R']['matrix'])@np.linalg.inv(np.array(rig.data.bones['INDEX_MCP_R'].matrix_local));C=transform(rig_RV,can)
 mcp=rig.data.bones['INDEX_MCP_R'];pip=rig.data.bones['INDEX_PIP_R'];dip=rig.data.bones['INDEX_DIP_R'];root=np.array(mcp.head_local);axis=np.array(pip.head_local)-root;length=np.linalg.norm(axis);axis/=length
 along=(rig_RV-root)@axis;rad=np.linalg.norm(rig_RV-root-along[:,None]*axis,axis=1)
 A=np.flatnonzero((along>=-.012)&(along<=length+.004)&(rad<.014));shaft=np.flatnonzero((along>=.15*length)&(along<=.85*length)&(rad<.012))
 B=np.flatnonzero((C[:,0]>=-.065)&(C[:,0]<=-.018)&(C[:,1]>=.040)&(C[:,1]<=.126)&(C[:,2]>=-.05)&(C[:,2]<=.02))
 ids=np.union1d(A,B);rois=dict(A=A,A_SHAFT=shaft,B=B);bone_names=[b.name for b in rig.data.bones if b.use_deform]
 W=np.zeros((len(RV),len(bone_names)))
 for v in mesh.data.vertices:
  for vg in v.groups:
   name=mesh.vertex_groups[vg.group].name
   if name in bone_names:W[v.index,bone_names.index(name)]=vg.weight
 keys=mesh.data.shape_keys;keyrows=[];inputRV=RV.copy()
 if keys:
  inputRV=np.array([list(v.co) for v in keys.key_blocks[0].data])
  for k in keys.key_blocks:
   delta=np.array([list(v.co) for v in k.data])-np.array([list(v.co) for v in k.relative_key.data]);value=k.value
   if k!=keys.key_blocks[0]:inputRV+=value*delta
   keyrows.append(dict(name=k.name,value=value,mute=k.mute,relative_key=k.relative_key.name,max_delta_mm=float(np.linalg.norm(delta,axis=1).max()*1000),roi_A_max_delta_mm=float(np.linalg.norm(delta[A],axis=1).max()*1000),roi_B_max_delta_mm=float(np.linalg.norm(delta[B],axis=1).max()*1000)))
 driverrows=[]
 if keys and keys.animation_data:
  for f in keys.animation_data.drivers:driverrows.append(dict(path=f.data_path,mute=f.mute,expression=f.driver.expression,valid=f.driver.is_valid,variables=[dict(name=v.name,type=v.type,targets=[dict(bone=t.bone_target,space=t.transform_space,transform=t.transform_type,path=t.data_path) for t in v.targets]) for v in f.driver.variables]))
 # Diagnostic-only deformation isolation on a private mesh datablock.
 original_data=mesh.data;private=original_data.copy();mesh.data=private;bpy.context.view_layer.update()
 if private.shape_keys:
  if private.shape_keys.animation_data:
   for f in private.shape_keys.animation_data.drivers:f.mute=True
  for k in private.shape_keys.key_blocks:
   if k!=private.shape_keys.key_blocks[0]:k.value=0
 bpy.context.view_layer.update();OFF,_,_=s.coords_tri(mesh)
 arm=[m for m in mesh.modifiers if m.type=='ARMATURE'];modstate=[(m,m.show_viewport,m.show_render) for m in arm]
 for m,_,_ in modstate:m.show_viewport=False;m.show_render=False
 bpy.context.view_layer.update();RAW,_,_=s.coords_tri(mesh)
 for m,vp,rd in modstate:m.show_viewport=vp;m.show_render=rd
 mesh.data=original_data;bpy.context.view_layer.update();RESTORED,_,_=s.coords_tri(mesh);assert np.array_equal(V,RESTORED)
 bpy.data.meshes.remove(private)
 matrices=[];pred=np.zeros_like(V);pred_off=np.zeros_like(V)
 for j,name in enumerate(bone_names):
  D=<REDACTED_EMAIL>[name]<REDACTED_EMAIL>[name].matrix_local.inverted()@rig.matrix_world.inverted()@mesh.matrix_world;matrices.append(np.array(D));pred+=W[:,j,None]*transform(inputRV,D);pred_off+=W[:,j,None]*transform(RV,D)
 joints={name:dict(rest=np.array(rig.data.bones[name].matrix_local),pose=np.array(rig.pose.bones[name].matrix),head_world=list(<REDACTED_EMAIL>[name].head),tail_world=list(<REDACTED_EMAIL>[name].tail),quaternion=list(rig.pose.bones[name].rotation_quaternion)) for name in ['WRIST_R','INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R','THUMB_CMC_R','THUMB_MCP_R','THUMB_IP_R','MIDDLE_MCP_R']}
 stats=dict(identity=identity,path=str(path),vertices=len(V),triangles=len(T),native_digest=c.digest(c.native(mesh,rig)),qdeg={d:s.degrees(d) for d in DIGITS},bone_names=bone_names,joints=joints,shape_keys=keyrows,drivers=driverrows,modifiers=[dict(name=m.name,type=m.type,preserve_volume=getattr(m,'use_deform_preserve_volume',None),vertex_groups=getattr(m,'use_vertex_groups',None),envelopes=getattr(m,'use_bone_envelopes',None)) for m in mesh.modifiers],rois={k:dict(count=len(v),vertices=v) for k,v in rois.items()},index_proximal_length_mm=float(length*1000),corrective_off_max_mm=float(np.linalg.norm(V-OFF,axis=1).max()*1000),corrective_off_A_mm=float(np.linalg.norm((V-OFF)[A],axis=1).max()*1000),corrective_off_B_mm=float(np.linalg.norm((V-OFF)[B],axis=1).max()*1000),lbs_prediction_max_mm=float(np.linalg.norm(V-pred,axis=1).max()*1000),lbs_off_prediction_max_mm=float(np.linalg.norm(OFF-pred_off,axis=1).max()*1000),weight_sum_range=[float(W.sum(1).min()),float(W.sum(1).max())],restore_error_mm=0.,mesh_world=np.array(mesh.matrix_world),rig_world=np.array(rig.matrix_world),canonical_from_rig=can,flat_faces=sum(not p.use_smooth for p in mesh.data.polygons),custom_normals=mesh.data.has_custom_normals)
 save(identity+'_SNAPSHOT.json',stats);np.savez_compressed(OUT/(identity+'_SNAPSHOT.npz'),V=V,T=T,RV=RV,RIG_RV=rig_RV,C=C,OFF=OFF,RAW=RAW,W=W,D=np.array(matrices),PRED=pred,PRED_OFF=pred_off,ALONG=along,RADIUS=rad)
 protection(identity+'_INPUT_RECEIPT.json')
 print('SNAPSHOT',identity,json.dumps({k:stats[k] for k in ['vertices','triangles','corrective_off_max_mm','lbs_prediction_max_mm','lbs_off_prediction_max_mm','flat_faces','custom_normals','index_proximal_length_mm']},ensure_ascii=False),'ROI_COUNTS',{k:len(v) for k,v in rois.items()},'SHAPES',[(r['name'],r['value']) for r in keyrows],flush=True)
 return stats
original=snapshot('ORIGINAL',SOURCE,True)
dest=OUT/'ORIGINAL_C1_DIAGNOSTIC_ONLY.blend';assert not dest.exists();bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=True)
