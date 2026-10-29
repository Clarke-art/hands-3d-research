import sys,json,time,math
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent; OLD=P.parent/'piano_hand_static_to_dynamic_transition_r1'; LAST=P.parent/'left_little_finger_moving_key_reachability_r1'
sys.path.insert(0,str(OLD));import bpy
from mathutils import Matrix,Vector
import common as o
import numpy as np
sys.path.insert(0,str(LAST/'_deps313'));from scipy.optimize import least_squares
c=o.c
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False,default=lambda a:a.tolist() if hasattr(a,'tolist') else a),encoding='utf8')
pol=o.read(P/'COORDINATED_CLEARANCE_POLICY_R1.json');lock=o.read(P/'PRE_SOLVE_LOCK_R1.json')
repair=o.read(P/'IMPLEMENTATION_REPAIR_R1.json') if (P/'IMPLEMENTATION_REPAIR_R1.json').exists() else None
assert o.sha(P/'COORDINATED_CLEARANCE_POLICY_R1.json')==lock['policy_sha256']
assert o.sha(__file__)==(repair['repaired_script_sha256'] if repair else lock['solver_script_sha256'])
if repair:assert repair['original_script_sha256']==lock['solver_script_sha256']
if (P/'ROOT_FINGER_COORDINATION_R1.json').exists():
 assert repair and repair['bind_initialization_bug_confirmed']
 assert o.sha(P/'ROOT_FINGER_COORDINATION_R1.json')==repair['invalid_coordinate_result_sha256']
 assert o.sha(P/'LEFT_OCTAVE_COORDINATED_CLEARANCE_CANDIDATE_R1.blend')==repair['invalid_coordinate_blend_sha256']
else:assert not (P/'LEFT_OCTAVE_COORDINATED_CLEARANCE_CANDIDATE_R1.blend').exists()
assert o.sha(pol['source_blend'])==pol['source_sha256']
bpy.ops.wm.open_mainfile(filepath=pol['source_blend'],load_ui=False,use_scripts=False)
info=o.read(LAST/'PROBE_SCENE_MANIFEST_R1.json')['mapping']; sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc
rig=bpy.data.objects[info['rig']];ob=bpy.data.objects[info['mesh']];rt=bpy.data.objects[info['root']]
sc.frame_set(1);bpy.context.view_layer.update();base=rt.matrix_world.copy()
expectedbase=np.load(LAST/'probe_motion.npz')['root_matrices'][0]
assert np.max(abs(np.array(base)-expectedbase))<1e-6,'Approved evaluated bind transform lost'
wrist=Vector(o.ANCHORS['L1']['root_xyz_m']);rig.animation_data_clear();rt.animation_data_clear()
ctrl0={k:np.array(v) for k,v in o.read(OLD/'CONTACT_AWARE_MOTION_PLAN_R1.json')['controls_radians'].items()}
extract=o.read(o.FORMAL/'FORMAL_INPUT_EXTRACTION_R1.json')['L'];rest=np.array(extract['rest_vertices_canonical']);palm=rest[:,1]<.105
patches={j:np.linalg.norm(rest-rest[c.MARKERS['L'][j]['mesh_vertex']],axis=1)<.018 for j in [0,4]}
boxes=[(k['key_index'],np.array(g['vertices']).min(0),np.array(g['vertices']).max(0)) for k in c.KEYS if 21<=k['midi_note']<=61 for g in k['geometry']]
M=np.load(OLD/'temporal_motion.npz');grid=np.arange(48,217)/120
extra=[n['note_on']-.12+u*.12 for n in o.EVENTS['L'] for u in [.25,.5,.75]]+[n['note_off']+.07+u*(o.recovery_end(n)-n['note_off']-.07) for n in o.EVENTS['L'] for u in [.25,.5,.75]]
times=np.unique([float(t) for t in M['L_times'] if any(n['note_on']-1e-8<=t<=n['note_off']+.07+1e-8 for n in o.EVENTS['L'])]+extra)
def motion(t,x):
 ctrl={k:v.copy() for k,v in ctrl0.items()};ctrl['L1']+=np.radians(x[4:8]);ctrl['L2']+=np.radians(x[8:12])
 q,ka=o.sample('L',t,ctrl);p=ka[17]/c.KEYS[17]['press_angle_rad'];p3=ka[29]/c.KEYS[29]['press_angle_rad'];blend=x[12:20].reshape(2,4);b=(1-p3)*blend[0]+p3*blend[1]
 q[0]+=p*b*(o.qanchor('L1')[0]-q[0]);q[1:4,:3]+=np.radians(x[20:29].reshape(3,3))*p
 delta=Vector(tuple(float(v*p/1000) for v in x[:3]));D=Matrix.Translation(wrist+delta)@Matrix.Rotation(math.radians(float(x[3]*p)),4,'X')@Matrix.Translation(-wrist)
 return q,ka,D@base
def apply(q,root):
 rt.matrix_world=root
 for j,d in enumerate(c.DIGITS):
  for name,R in zip(c.SETUPS['L',d][0],c.joint_mats('L',d,q[j])):
   b=rig.pose.bones[name];b.rotation_mode='QUATERNION';b.rotation_quaternion=Matrix(R).to_quaternion()
 bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();arr=np.empty(len(me.vertices)*3);me.vertices.foreach_get('co',arr);W=np.array(ev.matrix_world);V=arr.reshape(-1,3)@W[:3,:3].T+W[:3,3];ev.to_mesh_clear()
 pads=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS['L']]);return V,pads
def contact_residual(pt,n,angle):
 midi=n['midi_note'];j=n['finger']-1;anchor=o.ANCHORS['L1' if j==4 else 'L2']['pad_prediction_xyz_m'][j];p=angle/c.KEYS[n['key_index']]['press_angle_rad'];v=o.keytransform(midi,pt,angle,True)
 # Allowed migration window is intersected with the genuine playable patch.
 choices=[]
 for surf in c.KEYS[n['key_index']]['key_top_playable_surface']:
  lower=np.maximum([surf['xmin'],surf['ymin']],np.array(anchor[:2])-np.array([.002,.005])*p);upper=np.minimum([surf['xmax'],surf['ymax']],np.array(anchor[:2])+np.array([.002,.005])*p)
  if np.all(lower<=upper):
   dxy=v[:2]-np.clip(v[:2],lower,upper);choices.append(np.r_[dxy,v[2]-surf['z']-.0005])
 assert choices
 return min(choices,key=lambda r:np.linalg.norm(r))*1000
calls=0;start=time.monotonic();last=start;w=pol['solver']['weights'];limits=pol['continuity']
def excess(v,b,weight):return (np.maximum(np.abs(v)-b,0)*weight).ravel()
def residual(x):
 global calls,last
 calls+=1;out=[];cache={}
 for t in times:
  q,ka,root=motion(t,x);sig=(q.tobytes(),np.array(root).tobytes())
  if sig not in cache:cache[sig]=apply(q,root)
  V,pads=cache[sig];active=[]
  for n in o.EVENTS['L']:
   if n['note_on']-1e-8<=t<n['note_off']-1e-8:
    j=n['finger']-1;k=n['key_index'];out.extend(contact_residual(pads[j],n,ka[k])*w['fixed_contact_mm']);out.extend(contact_residual(V[c.MARKERS['L'][j]['mesh_vertex']],n,ka[k])*w['skin_contact_mm'])
   if n['note_on']-1e-8<=t<=o.recovery_end(n)+1e-8:active.append((n['key_index'],patches[n['finger']-1]))
  pen=np.zeros(len(V))
  for k,lo,hi in boxes:
   VV=o.keytransform(k+21,V,ka[k],True) if ka[k] else V;d=np.abs(VV-(lo+hi)/2)-(hi-lo)/2;sdf=np.linalg.norm(np.maximum(d,0),axis=1)+np.minimum(np.max(d,axis=1),0);margin=np.where(palm,.005,.002)
   for own,patch in active:
    if own==k:margin=margin.copy();margin[patch]=0
   pen=np.maximum(pen,margin-sdf)
  out.extend(np.maximum(pen,0)*1000*w['clearance_mm'])
 qs=[];xyz=[];ang=[]
 for t in grid:
  q,ka,root=motion(t,x);qs.append(np.degrees(q));p=ka[17]/c.KEYS[17]['press_angle_rad'];xyz.append(x[:3]*p);ang.append(x[3]*p)
 qs=np.array(qs);xyz=np.array(xyz);ang=np.array(ang)
 for values,scale,vl,al,vw,aw in [(qs,120,limits['joint_velocity_deg_sec'],limits['joint_acceleration_deg_sec2'],.05,.0005),(xyz,120,limits['root_velocity_mm_sec'],limits['root_acceleration_mm_sec2'],.05,.0005),(ang,120,limits['root_angular_velocity_deg_sec'],limits['root_angular_acceleration_deg_sec2'],.05,.0005)]:
  v=np.diff(values,axis=0)*scale;a=np.diff(v,axis=0)*scale
  if values is xyz:v=np.linalg.norm(v,axis=1);a=np.linalg.norm(a,axis=1)
  out.extend(excess(v,vl,vw));out.extend(excess(a,al,aw))
 out.extend(x[4:12]*w['active_offset_deg']);out.extend(x[20:]*w['idle_delta_deg'])
 if time.monotonic()-last>20:print('ONE_COORDINATED_SOLVE',calls,'elapsed',round(time.monotonic()-start,1),flush=True);last=time.monotonic()
 return np.array(out)
s=pol['solver'];lower=np.array(s['bounds_lower']);upper=np.array(s['bounds_upper'])
def jacobian(x):
 # Absolute parameter steps are required for Blender float32 geometry near zero.
 baseline=residual(x);columns=[];steps=np.array(repair['absolute_difference_steps'] if repair else [.02]*3+[.03]*9+[.003]*8+[.03]*9)
 for j,h in enumerate(steps):
  step=h if x[j]+h<=upper[j] else -h
  step=min(step,upper[j]-x[j]) if step>0 else max(step,lower[j]-x[j])
  assert abs(step)>1e-10
  shifted=x.copy();shifted[j]+=step;columns.append((residual(shifted)-baseline)/step)
 return np.column_stack(columns)
fit=least_squares(residual,np.array(s['seed']),jac=jacobian,bounds=(lower,upper),max_nfev=s['max_nfev'],xtol=s['xtol'],ftol=s['ftol'],gtol=s['gtol'])
assert np.isfinite(fit.x).all()
dump('ROOT_FINGER_COORDINATION_R1.json',{'planner':pol['planner'],'x':fit.x,'success':bool(fit.success),'nfev':int(fit.nfev),'calls':calls,'cost':float(fit.cost),'message':fit.message,'elapsed_sec':time.monotonic()-start,'policy_sha256':lock['policy_sha256'],'script_sha256':o.sha(__file__),'candidate_count':1,'restarts':0,'implementation_bug_restart':repair is not None,'shared_root_count':1,'jointly_optimized':['root_XYZ_pitch','LITTLE_four_pressure_offsets','THUMB_four_pressure_offsets_eight_preparation_coefficients','INDEX_MIDDLE_RING_nine_bounded_flexion_offsets'],'no_post_smoothing':True,'no_per_frame_IK':True,'collocation_count':len(times),'engineering_verification':'PENDING','naturalness':'HUMAN_PENDING'})
print('SOLE_COORDINATED_FIT_FINISHED',fit.x.tolist(),flush=True)
def linear(obj):
 for layer in obj.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for f in bag.fcurves:
     for k in f.keyframe_points:k.interpolation='LINEAR'
Q=[];roots=[]
for i,t in enumerate(M['L_times']):
 q,ka,root=motion(float(t),fit.x);Q.append(q);roots.append(np.array(root));f=1+(t-.4)*60;rt.matrix_world=root;rt.rotation_mode='QUATERNION'
 for data in ['location','rotation_quaternion']:rt.keyframe_insert(data_path=data,frame=f)
 for j,d in enumerate(c.DIGITS):
  for name,R in zip(c.SETUPS['L',d][0],c.joint_mats('L',d,q[j])):
   b=rig.pose.bones[name];quat=Matrix(R).to_quaternion()
   if i and b.rotation_quaternion.dot(quat)<0:quat.negate()
   b.rotation_quaternion=quat;b.keyframe_insert(data_path='rotation_quaternion',frame=f,group=d)
rig.animation_data.action.name='DESIGN_ONLY_COORDINATED_LEFT_FINGERS_R1';rt.animation_data.action.name='DESIGN_ONLY_COORDINATED_SHARED_ROOT_R1';linear(rig);linear(rt)
sc['PHASE']=pol['phase'];sc['DESIGN_ONLY']=True;sc['HUMAN_APPROVAL_PENDING']=True;sc['POLICY_SHA256']=lock['policy_sha256'];sc.frame_set(1)
dest=P/'LEFT_OCTAVE_COORDINATED_CLEARANCE_CANDIDATE_R1.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest))
np.savez_compressed(P/'coordinated_motion.npz',times=M['L_times'],q=Q,root_matrices=roots,key_angles=M['L_key_angles'])
dump('COORDINATED_SCENE_MANIFEST_R1.json',{'candidate_sha256':o.sha(dest),'mapping':info,'source_sha256':pol['source_sha256'],'policy_sha256':lock['policy_sha256'],'right_new_actions':0,'original_key_actions_untouched':True})
print('SOLE_COORDINATED_CANDIDATE_SAVED',flush=True)
