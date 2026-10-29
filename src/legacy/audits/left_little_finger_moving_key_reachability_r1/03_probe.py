import sys,json,time,hashlib,math
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;PRE=P.parent/'piano_hand_static_to_dynamic_transition_r1';sys.path.insert(0,str(PRE))
import bpy
from mathutils import Matrix,Vector
import common as o
import numpy as np
sys.path.insert(0,str(P/'_deps313'))
from scipy.optimize import least_squares
c=o.c
def dump(n,x): (P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else v),encoding='utf8')
pol=o.read(P/'ROOT_FOLLOW_THROUGH_POLICY_R1.json');lock=o.read(P/'PRE_PROBE_LOCK_R1.json')
repair=o.read(P/'IMPLEMENTATION_REPAIR_R1.json')
assert o.sha(P/'ROOT_FOLLOW_THROUGH_POLICY_R1.json')==lock['policy_sha256'] and o.sha(__file__)==repair['repaired_script_sha256'] and repair['original_script_sha256']==lock['scripts_sha256']['03_probe.py']
assert not (P/'PROBE_RESULT_R1.json').exists() and not (P/'LEFT_LITTLE_MOVING_KEY_PROBE_R1.blend').exists(),'No restart or second candidate.'
source=PRE/'STATIC_TO_DYNAMIC_TRANSITION_CANDIDATE_R1.blend';assert o.sha(source)==pol['source_dynamic_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
man=o.read(PRE/'DYNAMIC_SCENE_MANIFEST_R1.json');info=man['mapping']['L'];sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc
rig=bpy.data.objects[info['rig']];ob=bpy.data.objects[info['mesh']];rt=bpy.data.objects[info['root']];base=rt.matrix_world.copy();wrist=Vector(o.ANCHORS['L1']['root_xyz_m']);rig.animation_data_clear();ctrl={k:np.array(v) for k,v in o.read(PRE/'CONTACT_AWARE_MOTION_PLAN_R1.json')['controls_radians'].items()}
targets={38:np.array(o.ANCHORS['L1']['pad_prediction_xyz_m'][4]),50:np.array(o.ANCHORS['L2']['pad_prediction_xyz_m'][0])}
extract=o.read(o.FORMAL/'FORMAL_INPUT_EXTRACTION_R1.json')['L'];rest=np.array(extract['rest_vertices_canonical']);palm=rest[:,1]<.105
patches={j:np.linalg.norm(rest-rest[c.MARKERS['L'][j]['mesh_vertex']],axis=1)<.018 for j in [0,4]}
boxes=[]
for k in c.KEYS:
 if not 21<=k['midi_note']<=61:continue
 for g in k['geometry']:
  v=np.array(g['vertices']);boxes.append((k['key_index'],v.min(0),v.max(0)))
M=np.load(PRE/'temporal_motion.npz');contact_times=[float(t) for t in M['L_times'] if any(n['note_on']-1e-8<=t<=n['note_off']+.07+1e-8 for n in o.EVENTS['L'])]
extra=[n['note_on']-.12+u*.12 for n in o.EVENTS['L'] for u in [.25,.5,.75]]+[n['note_off']+.07+u*(o.recovery_end(n)-n['note_off']-.07) for n in o.EVENTS['L'] for u in [.25,.5,.75]]
times=np.unique(contact_times+extra)
def motion(t,x):
 q,ka=o.sample('L',t,ctrl);p=ka[17]/c.KEYS[17]['press_angle_rad'];p3=ka[29]/c.KEYS[29]['press_angle_rad'];blend=np.array(x[3:]).reshape(2,4);b=(1-p3)*blend[0]+p3*blend[1];q[0]+=p*b*(o.qanchor('L1')[0]-q[0]);delta=Vector((0,float(x[2]*p/1000),float(x[0]*p/1000)));D=Matrix.Translation(wrist+delta)@Matrix.Rotation(math.radians(float(x[1]*p)),4,'X')@Matrix.Translation(-wrist)
 return q,ka,D@base
def apply(q,root):
 rt.matrix_world=root
 for j,d in enumerate(c.DIGITS):
  for name,R in zip(c.SETUPS['L',d][0],c.joint_mats('L',d,q[j])):rig.pose.bones[name].rotation_mode='QUATERNION';rig.pose.bones[name].rotation_quaternion=Matrix(R).to_quaternion()
 bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();arr=np.empty(len(me.vertices)*3);me.vertices.foreach_get('co',arr);arr=arr.reshape(-1,3);W=np.array(ev.matrix_world);V=arr@W[:3,:3].T+W[:3,3];ev.to_mesh_clear();pads=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS['L']]);return V,pads
calls=0;start=time.monotonic();last=start
def residual(x):
 global calls,last
 calls+=1;out=[];cache={}
 for t in times:
  q,ka,root=motion(t,x);signature=(q.tobytes(),np.array(root).tobytes(),ka.tobytes())
  if signature not in cache:cache[signature]=apply(q,root)
  V,pads=cache[signature];active=[]
  for n in o.EVENTS['L']:
   if n['note_on']-1e-8<=t<=n['note_off']+.07+1e-8:
    j=n['finger']-1;k=n['key_index'];target=o.keytransform(n['midi_note'],targets[n['midi_note']],ka[k]);out.extend((pads[j]-target)*1000*10);out.extend((V[c.MARKERS['L'][j]['mesh_vertex']]-target)*1000*6);active.append((k,patches[j]))
  pen=np.zeros(len(V))
  for k,lo,hi in boxes:
   VV=o.keytransform(k+21,V,ka[k],True) if ka[k] else V;d=np.abs(VV-(lo+hi)/2)-(hi-lo)/2;sdf=np.linalg.norm(np.maximum(d,0),axis=1)+np.minimum(np.max(d,axis=1),0);margin=np.where(palm,.005,.002)
   for own,patch in active:
    if own==k:margin=margin.copy();margin[patch]=0
   pen=np.maximum(pen,margin-sdf)
  out.extend(np.maximum(pen,0)*1000*2)
 if time.monotonic()-last>20:print('ONE_PROBE_SOLVING',calls,'elapsed_sec',round(time.monotonic()-start,1),flush=True);last=time.monotonic()
 return np.array(out)
s=pol['solver'];fit=least_squares(residual,np.array(s['seed']),bounds=(s['bounds_lower'],s['bounds_upper']),max_nfev=s['max_nfev'],diff_step=s['diff_step'],xtol=s['xtol'],ftol=s['ftol'],gtol=s['gtol'])
assert np.isfinite(fit.x).all()
dump('PROBE_RESULT_R1.json',{'x':fit.x,'success':bool(fit.success),'cost':float(fit.cost),'nfev':int(fit.nfev),'calls':calls,'message':fit.message,'elapsed_sec':time.monotonic()-start,'candidate_count':1,'restarts':0,'policy_sha256':lock['policy_sha256'],'collocation_count':len(times),'actual_geometry_used':True,'full_candidate_acceptance':'NOT_YET_MEASURED'})
print('SOLE_FIT_FINISHED',fit.x.tolist(),'cost',fit.cost,flush=True)
def linear(obj):
 for layer in obj.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for f in bag.fcurves:
     for k in f.keyframe_points:k.interpolation='LINEAR'
# Preserve original action data blocks/right scene; create left rig/root actions only.
Q=[];roots=[]
for i,t in enumerate(M['L_times']):
 q,ka,root=motion(float(t),fit.x);Q.append(q);roots.append(np.array(root));f=1+(t-.4)*60;rt.matrix_world=root;rt.rotation_mode='QUATERNION'
 for data in ['location','rotation_quaternion']:rt.keyframe_insert(data_path=data,frame=f)
 for j,d in enumerate(c.DIGITS):
  for n,R in zip(c.SETUPS['L',d][0],c.joint_mats('L',d,q[j])):
   b=rig.pose.bones[n];quat=Matrix(R).to_quaternion()
   if i and b.rotation_quaternion.dot(quat)<0:quat.negate()
   b.rotation_quaternion=quat;b.keyframe_insert(data_path='rotation_quaternion',frame=f,group=d)
rig.animation_data.action.name='DESIGN_ONLY_LEFT_REACHABILITY_R1';rt.animation_data.action.name='DESIGN_ONLY_SHARED_WRIST_FOLLOW_R1';linear(rig);linear(rt)
sc['PHASE']='LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1';sc['DESIGN_ONLY']=True;sc['HUMAN_APPROVAL_PENDING']=True;sc['POLICY_SHA256']=lock['policy_sha256'];sc.frame_set(1)
dest=P/'LEFT_LITTLE_MOVING_KEY_PROBE_R1.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest))
np.savez_compressed(P/'probe_motion.npz',times=M['L_times'],q=np.array(Q),root_matrices=np.array(roots),key_angles=M['L_key_angles'])
dump('PROBE_SCENE_MANIFEST_R1.json',{'candidate_sha256':o.sha(dest),'mapping':info,'source_sha256':o.sha(source),'policy_sha256':lock['policy_sha256'],'action_count':len(bpy.data.actions),'right_new_actions':0,'original_key_actions_untouched':True})
print('SOLE_CANDIDATE_SAVED',flush=True)
