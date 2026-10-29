import sys,math,json,hashlib,ast,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Matrix,Vector,Quaternion
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PREV=ROOT/'audits/pianovam_single_sample_right_hand_retarget_r1';AB=ROOT/'audits/pianovam_first_web_corrective_ab_isolation_r1'
BASE=ROOT/'production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend';OLD=PREV/'RIGHT_HAND_PIANO_MOTION_TEST_R1.blend'
BASE_SHA='4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2';OLD_SHA='43e8e2854aa24c74053830118ea6d939fc56af4efb450bf0098a7bd99838dae8'
spec=importlib.util.spec_from_file_location('approved_helpers',ROOT/'audits/official_l1_first_web_targeted_deformation_fix_r1/common.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.old.lib.OUT=OUT
node=next(n for n in ast.parse((BASE.parent/'freeze_baseline.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='shape_payload');exec(compile(ast.Module(body=[node],type_ignores=[]),'shape_payload','exec'))
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def arr(mat):return [list(row) for row in mat]
def norm(v):return Vector(v).normalized()
def frame(y,x):
 y=norm(y);x=Vector(x)-y*Vector(x).dot(y);x.normalize();z=x.cross(y).normalized();return Matrix((x,y,z)).transposed()
def signed(a,b,h):
 a=norm(a);b=norm(b);h=norm(h);return math.atan2(a.cross(b).dot(h),a.dot(b))
def deg(v):return [math.degrees(float(x)) for x in v]
class Solver:
 def __init__(self,ob,rig,iteration=1):
  self.ob=ob;self.rig=rig;self.iteration=iteration
  src=ROOT/'references/piano_motion/pianovam_sample_r1/Handskeleton/2024-03-04_03-46-36.json';acq=read(PREV/'PIANOVAM_SINGLE_SAMPLE_ACQUISITION_R1_STATUS.json');expected=next(f['sha256'] for f in acq['files'] if f['remote_path'].startswith('Handskeleton/'));assert sha(src)==expected
  data=read(src);self.points=[];self.palms=[];self.local=[]
  for f in range(690,1111):
   p=np.array(data[str(f)]['Left'],dtype=float);assert p.shape==(21,3);p[:,1]*=1080/1920;P=frame(Vector(p[9]-p[0]),Vector(p[5]-p[17]));self.points.append(p);self.palms.append(P);self.local.append(np.array([(P.transposed()@Vector(v-p[0]))[:] for v in p]))
  self.local=np.array(self.local);self.rest={b.name:b.matrix_local.to_3x3().normalized() for b in rig.data.bones};self.y={n:R@Vector((0,1,0)) for n,R in self.rest.items()}
  p={b.name:b.head_local for b in rig.data.bones};self.R=frame(p['MIDDLE_MCP_R']-p['WRIST_R'],p['INDEX_MCP_R']-p['LITTLE_MCP_R']);self.bridge=<REDACTED_EMAIL>[0].transposed();self.rad=self.R@Vector((1,0,0));self.normal=self.R@Vector((0,0,1));self.distal=self.R@Vector((0,1,0))
  self.anatom={};self.hinges={};self.calibration={};self.digits=[('INDEX',5),('MIDDLE',9),('RING',13),('LITTLE',17)]
  for digit,start in self.digits:
   n=digit+'_MCP_R';A=frame(self.y[n],self.rad);self.anatom[n]=A;self.calibration[n]=A.transposed()@self.rest[n]
   h=A@Vector((1,0,0))
   for j in ['PIP','DIP']:
    n=digit+'_'+j+'_R';hh=(h-self.y[n]*h.dot(self.y[n])).normalized();self.hinges[n]=self.rest[n].transposed()@hh
  # Thumb has a distinct base and metacarpal frame. Neutral source CMC orientation is
  # wrist->CMC projected onto the palm, measured from this same window's base landmarks.
  # It is a structural base reference, not a selected performance pose or angle clamp.
  anchor=np.median(self.local[:,1,:2]-self.local[:,0,:2],axis=0);self.thumb_neutral=norm((anchor[0],anchor[1],0))
  if iteration==2:
   dirs=self.local[:,2]-self.local[:,1];dirs/=np.linalg.norm(dirs,axis=1)[:,None];self.thumb_neutral=norm(np.median(dirs,axis=0))
  self.thumb_src_rest=frame(self.thumb_neutral,(0,0,1))
  self.thumb_anatom=frame(self.y['THUMB_CMC_R'],self.normal);self.thumb_roll_offset=self.thumb_anatom.transposed()@self.rest['THUMB_CMC_R']
  h=self.thumb_anatom@Vector((1,0,0))
  for j in ['MCP','IP']:
   n='THUMB_'+j+'_R';hh=(h-self.y[n]*h.dot(self.y[n])).normalized();self.hinges[n]=self.rest[n].transposed()@hh
  self.source_sha=expected;self.cache={}
 def raw(self,i):
  if i in self.cache:return self.cache[i]
  L=self.local[i];D=<REDACTED_EMAIL>[i]@self.palms[0].transposed()@self.bridge.transposed();world={};qs={};components={}
  world['WRIST_R']=<REDACTED_EMAIL>['WRIST_R'];qs['WRIST_R']=(self.rest['WRIST_R'].transposed()@world['WRIST_R']).to_quaternion()
  for digit,s in self.digits:
   d=norm(L[s+1]-L[s]);n=digit+'_MCP_R'
   # Palm radial vector anchors the digit plane. Rest anatomical zero is explicitly
   # calibrated to the frozen bent/spread RSSF bone frame, instead of replacing it
   # with an absolute straight image-space segment direction.
   S=frame(d,(1,0,0));A=self.anatom[n];target=D@A@<REDACTED_EMAIL>[n]
   predicted=world['WRIST_R']@self.rest['WRIST_R'].transposed()@self.rest[n];q=(predicted.transposed()@target).to_quaternion();qs[n]=q;world[n]=target
   flex=math.atan2(d.z,math.hypot(d.x,d.y));abd=math.atan2(d.x,d.y)
   components[n]={'source_flexion_rad':flex,'source_abduction_rad':abd,'source_flexion_deg':math.degrees(flex),'source_abduction_deg':math.degrees(abd),'source_plane_anchor':'palm radial projected perpendicular to first phalanx','rig_anatomical_rest_frame':arr(A),'rig_local_flexion_axis':list(self.rest[n].transposed()@(A@Vector((1,0,0)))),'rig_local_positive_abduction_axis':list(self.rest[n].transposed()@(-(A@Vector((0,0,1)))))}
   for j,joint in [(1,'PIP'),(2,'DIP')]:
    parent=n;n=digit+'_'+joint+'_R';a=norm(L[s+j]-L[s+j-1]);b=norm(L[s+j+1]-L[s+j]);h=norm(Vector((1,0,0))-a*a.x);bend=signed(a,b,h)
    q=Quaternion(self.hinges[n],bend);qs[n]=q;pred=world[parent]@self.rest[parent].transposed()@self.rest[n];world[n]=<REDACTED_EMAIL>_matrix();components[n]={'source_signed_hinge_bend_rad':bend,'source_signed_hinge_bend_deg':math.degrees(bend),'rig_local_hinge_axis':list(self.hinges[n]),'source_out_of_digit_plane_component':float(b.dot(h))}
  # Thumb swing is measured in its own wrist/CMC base frame; thumb MCP/IP bending
  # uses the plane spanned by consecutive thumb segments, anchored to palm normal.
  a=norm(L[2]-L[1]);b=norm(L[3]-L[2]);plane=a.cross(b);plane_mag=plane.length
  anchor=norm(Vector((0,0,1))-a*a.z)
  reliable=plane_mag>math.sin(math.radians(10)) and abs(norm(plane).dot(anchor))>.7
  # Preserve calibrated rest twist: the thumb-plane normal diagnoses hinge geometry,
  # but is not copied as a noisy CMC axial twist.
  T=frame(a,(0,0,1));delta=self.thumb_src_rest.transposed()@T;target=<REDACTED_EMAIL>_anatom@<REDACTED_EMAIL>_roll_offset
  n='THUMB_CMC_R';predicted=world['WRIST_R']@self.rest['WRIST_R'].transposed()@self.rest[n];qs[n]=(predicted.transposed()@target).to_quaternion();world[n]=target
  swing=self.thumb_neutral.rotation_difference(a);components[n]={'source_base_neutral_direction':list(self.thumb_neutral),'source_CMC_direction':list(a),'source_swing_quaternion':list(swing),'source_in_palm_swing_rad':math.atan2(a.x,a.y)-math.atan2(self.thumb_neutral.x,self.thumb_neutral.y),'source_out_of_palm_flexion_rad':math.atan2(a.z,math.hypot(a.x,a.y)),'thumb_plane_normal':list(norm(plane)) if plane_mag>1e-7 else None,'thumb_plane_reliable_for_bend_diagnostic':reliable,'CMC_axial_twist_copied':False}
  for u,joint in [(2,'MCP'),(3,'IP')]:
   parent=n;n='THUMB_'+joint+'_R';a=norm(L[u]-L[u-1]);b=norm(L[u+1]-L[u]);h=norm(Vector((0,0,1))-a*a.z);bend=signed(a,b,h);qs[n]=Quaternion(self.hinges[n],bend);pred=world[parent]@self.rest[parent].transposed()@self.rest[n];world[n]=pred@qs[n].to_matrix();components[n]={'source_signed_hinge_bend_rad':bend,'source_signed_hinge_bend_deg':math.degrees(bend),'rig_local_hinge_axis':list(self.hinges[n]),'thumb_plane_anchor':'palm normal projected perpendicular to parent segment','out_of_thumb_plane_component':float(b.dot(h))}
  for q in qs.values():q.normalize()
  self.cache[i]=(qs,components);return self.cache[i]
 def smoothed(self,i):
  seq=[self.raw(max(0,i-1))[0],self.raw(i)[0],self.raw(min(420,i+1))[0]];out={}
  for n,q in seq[1].items():
   neighbors=[s[n].copy() for s in seq]
   for p in neighbors:
    if p.dot(q)<0:p.negate()
   v=[sum(w*p[k] for w,p in zip([.25,.5,.25],neighbors)) for k in range(4)];s=Quaternion(v);s.normalize();out[n]=s
  return out,self.raw(i)[1]
 def apply(self,qs):
  self.rig.animation_data.action=None;m.reset_pose(self.rig)
  for n,q in qs.items():self.rig.pose.bones[n].rotation_quaternion=q
  bpy.context.view_layer.update()
 def audit(self):
  normals=[p@Vector((0,0,1)) for p in self.palms];dists=[p@Vector((0,1,0)) for p in self.palms];rads=[p@Vector((1,0,0)) for p in self.palms]
  steps=lambda vs:[math.degrees(a.angle(b)) for a,b in zip(vs,vs[1:])]
  bones={}
  for b in self.rig.data.bones:
   rel=b.parent.matrix_local.inverted()@b.matrix_local if b.parent else b.matrix_local
   y=(self.R.transposed()@self.y[b.name]);bones[b.name]={'head_armature':list(b.head_local),'tail_armature':list(b.tail_local),'rest_matrix_armature':arr(b.matrix_local),'parent_relative_rest_matrix':arr(rel),'bone_local_axes_in_armature':{a:list(self.rest[b.name]@v) for a,v in [('X',Vector((1,0,0))),('Y_PRIMARY',Vector((0,1,0))),('Z',Vector((0,0,1)))]},'rest_primary_in_palm_frame':list(y),'rest_primary_palm_elevation_deg':math.degrees(math.atan2(y.z,math.hypot(y.x,y.y))),'rest_primary_palm_splay_deg':math.degrees(math.atan2(y.x,y.y)),'use_deform':b.use_deform,'parent':b.parent.name if b.parent else None,'inherit_rotation':b.use_inherit_rotation,'inherit_scale':b.inherit_scale}
  return {'SOURCE_MOTION':'PIANOVAM_SAME_11_5_18_5_WINDOW','source_sha256':self.source_sha,'source_frame_range':[690,1110],'observation_count':421,'source_field':'Left (video-verified physical right, original labels unchanged)','source_coordinate_system':{'x':'image right','y':'image down, aspect corrected *1080/1920','z':'relative depth positive away from camera; not metric','handedness':'RIGHT_HANDED_CAMERA_X_RIGHT_Y_DOWN_Z_FORWARD','euler_primary':False},'palm_local':{'X':'radial: INDEX_MCP-LITTLE_MCP orthogonalized to distal','Y':'distal: MIDDLE_MCP-WRIST','Z':'X cross Y, geometric palmar-away-camera for this right hand','construction':'Gram-Schmidt, determinant +1; no temporal sign forcing or smoothing','basis_determinant_range':[min(p.determinant() for p in self.palms),max(p.determinant() for p in self.palms)],'normal_sign_flip_count':sum(a.dot(b)<0 for a,b in zip(normals,normals[1:])),'radial_sign_flip_count':sum(a.dot(b)<0 for a,b in zip(rads,rads[1:])),'distal_sign_flip_count':sum(a.dot(b)<0 for a,b in zip(dists,dists[1:])),'normal_max_step_deg':max(steps(normals)),'radial_max_step_deg':max(steps(rads)),'distal_max_step_deg':max(steps(dists))},'rig':{'object_world_matrix':arr(self.rig.matrix_world),'mesh_world_matrix':arr(self.ob.matrix_world),'armature_linear_determinant':self.rig.matrix_world.to_3x3().determinant(),'palm_basis_armature':arr(self.R),'palm_radial_armature':list(self.rad),'palm_distal_armature':list(self.distal),'palm_palmar_normal_armature':list(self.normal),'bones':bones},'conversion_chain':'world orientation to armature via inverse armature object rotation; parent predicted = parent pose * inverse(parent rest) * bone rest; local basis = inverse(predicted)*desired. Native parent conversion cross-checked with Blender PoseBone.convert_local_to_pose in dry run. No scale/translation changes.','old_method_explanation':'Absolute palm-local first-phalanx direction was aligned to a curved/spread RSSF rest bone. Thus source flexion can be smaller than the rest built-in palmar elevation and produce a positive local X delta. Positive local Euler X alone was not proof of a reversed source normal or wrong local-matrix multiplication. Old minimal direction-only alignment also leaves MCP plane/twist underconstrained and permits PIP/DIP off-hinge motion.','new_rest_calibration':'Source anatomical neutral axes map to the existing rig anatomical REST axes. Source flexion/abduction are joint articulation relative to neutral palm frame; intrinsic rig rest curvature/splay and roll are retained as rest offset. No angle/sign clamp and no old representative fixture is used by solver.','wrist_mode':'B_FIXED_TRANSLATION_SOURCE_PALM_ORIENTATION','smoothing':'Unchanged one symmetric quaternion 3-tap [.25,.5,.25] at source60fps, sign alignment and normalization; no frame flip hidden by smoothing.'}
