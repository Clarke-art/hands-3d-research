import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from blender_utils import *
A=np.load(O/'motion.npz');traj= np.c_[A['R_delta']*1000,A['R_extra_rot_deg'],np.degrees(A['R_q']).reshape(-1,20)];times=A['times'];started=time.perf_counter()
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']];rt=bpy.data.objects[man['mapping']['R']['root']]
oldrig=rig.animation_data.action;oldroot=rt.animation_data.action;oldslot=rig.animation_data.action_slot;oldrootslot=rt.animation_data.action_slot
protected={o.name:digest(payload(o.animation_data.action)) for o in sc.objects if o not in [rig,rt] and o.animation_data and o.animation_data.action}
identity_before=digest(native(mesh,rig));assert identity_before==pf['right_native_sha256']
# Keep source Actions as preserved data blocks, bind distinct experimental Actions only.
oldrig.use_fake_user=True;oldroot.use_fake_user=True;rig.animation_data_clear();rt.animation_data_clear();rt.rotation_mode='QUATERNION'
previous={}
for state,t in zip(traj,times):
 settime(sc,float(t));apply(state,rt,rig);frame=1+60*t
 for prop in ['location','rotation_quaternion']:rt.keyframe_insert(data_path=prop,frame=frame)
 for d in c.DIGITS:
  for name in c.SETUPS['R',d][0]:
   bone=rig.pose.bones[name]
   if name in previous and bone.rotation_quaternion.dot(previous[name])<0:bone.rotation_quaternion.negate()
   previous[name]=bone.rotation_quaternion.copy();bone.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=d)
for ob,name in [(rt,'C01_R1_WHOLE_HAND_ROOT_DESIGN_ONLY'),(rig,'C01_R1_FIVE_DIGIT_COORDINATED_DESIGN_ONLY')]:
 ob.animation_data.action.name=name
 for f in curves(ob.animation_data.action):
  for k in f.keyframe_points:k.interpolation='LINEAR'
newrig=rig.animation_data.action;newroot=rt.animation_data.action;newslot=rig.animation_data.action_slot;newrootslot=rt.animation_data.action_slot
sc.name='C01_WHOLE_HAND_MOTION_FEASIBILITY_R1';sc['DESIGN_PROVISIONAL']=True;sc['HUMAN_APPROVAL_PENDING']=True
sc.frame_start=math.floor(1+60*I['clip_start_sec']);sc.frame_end=math.ceil(1+60*I['clip_end_sec']);sc.render.fps=60
bpy.context.preferences.filepaths.save_version=0;dest=O/'C01_WHOLE_HAND_MOTION_DESIGN_PROVISIONAL_R1.blend'
assert not dest.exists();bpy.ops.wm.save_as_mainfile(filepath=str(dest))
assert digest(native(mesh,rig))==identity_before
assert all(digest(payload(bpy.data.objects[n].animation_data.action))==v for n,v in protected.items())
# Actual evaluated samples, no large vertex-cache sequences.
probe=np.unique(np.r_[np.arange(I['clip_start_sec'],I['clip_end_sec'],1/60),[v+d for n in I['notes'] for v in [n['note_on'],n['note_off']] for d in [-.045,-.008333333,0,.008333333,.0175,.035,.04,.07]],[3.825,I['clip_end_sec']]])
probe=probe[(probe>=I['clip_start_sec'])&(probe<=I['clip_end_sec'])];rows=[];positions=[];rootrot=[];qrows=[];parity=[]
for index,t in enumerate(probe):
 settime(sc,float(t));active=[n for n in I['notes'] if n['note_on']<=t+1e-9 and t<n['note_off']-1e-9];n=active[-1] if active else None;r,V=measure(sc,mesh,rig,t,n);
 if n:
  r['phase']='KEY_PRESS' if t<n['note_on']+.035 else 'HOLD'
  r['expected_pad_lift_mm']=0.
  if n['note_id']=='R06' and n['note_off']-.045<=t<n['note_off']:
   r['phase']='REPEAT_RELEASE_AND_RESET';r['expected_pad_lift_mm']=2*float(np.sin(np.pi*(t-n['note_off']+.045)/.045)**2)
  r['contact']['residual_from_expected_hover_mm']=r['contact']['gap_mm']-r['expected_pad_lift_mm']
 rows.append(r);positions.append(list(rt.matrix_world.translation));rootrot.append(list(rt.matrix_world.to_quaternion()))
 if index%60==0:print('ACTUAL_CONTINUOUS_DIAGNOSTIC',index,len(probe),flush=True)
# Direct same-time original comparison at the old B02 probe and key transitions.
comparison=[]
for t in [I['notes'][2]['note_on']+.035,3.825,I['notes'][6]['note_on']+.035,I['notes'][8]['note_on']+.035]:
 if not I['clip_start_sec']<=t<=I['clip_end_sec']:continue
 states={}
 for label,ra,rr,rs,rts in [('old',oldrig,oldroot,oldslot,oldrootslot),('C01',newrig,newroot,newslot,newrootslot)]:
  rig.animation_data.action=ra;rig.animation_data.action_slot=rs;rt.animation_data.action=rr;rt.animation_data.action_slot=rts;settime(sc,t);r,V=measure(sc,mesh,rig,t);states[label]=r
 comparison.append(dict(time=t,states=states))
rig.animation_data.action=newrig;rig.animation_data.action_slot=newslot;rt.animation_data.action=newroot;rt.animation_data.action_slot=newrootslot
contactrows=[r for r in rows if 'contact' in r];worst_contact=max(abs(r['contact']['residual_from_expected_hover_mm']) for r in contactrows);worst_horizontal=max(r['contact']['horizontal_mm'] for r in contactrows);worst_passive=max(r['max_inactive_or_wrong_key_depth_mm'] for r in rows);maxmiddle=max(r['finger_intersection_pairs']['MIDDLE_RING'] for r in rows)
# Uniform saved trajectory root / joint speeds; not a physiological certificate.
tUniform=np.arange(I['clip_start_sec'],I['clip_end_sec'],1/120);xyz=np.column_stack([np.interp(tUniform,times,A['R_delta'][:,j]) for j in range(3)]);v=np.diff(xyz,axis=0)*120*1000;acc=np.diff(v,axis=0)*120;qq=np.column_stack([np.interp(tUniform,times,np.degrees(A['R_q']).reshape(-1,20)[:,j]) for j in range(20)]);jointv=np.diff(qq,axis=0)*120
basic=worst_contact<=2 and worst_horizontal<=2 and worst_passive<=.5 and all(sum(r['finger_intersection_pairs'].values())==0 for r in rows)
status='MOTION_FEASIBILITY_PASS' if basic else 'MOTION_FEASIBILITY_PARTIAL'
out('MOTION_FEASIBILITY_METRICS.json',dict(status=status,actual_action_generated=True,scope='R06 context and R07-R14 continuous motion only',source_fingering_unchanged=True,notes=I['notes'],evaluated_skin=True,actual_sample_count=len(rows),actual_rows=rows,comparison= comparison,contact_max_absolute_gap_mm=worst_contact,contact_max_horizontal_outside_mm=worst_horizontal,passive_or_wrong_key_max_vertex_depth_mm=worst_passive,middle_ring_max_triangle_intersection_pairs=maxmiddle,palm_root_velocity_peak_mm_sec=float(np.linalg.norm(v,axis=1).max()),palm_root_acceleration_peak_mm_sec2=float(np.linalg.norm(acc,axis=1).max()),joint_velocity_peak_deg_sec=float(np.max(abs(jointv))),root_delta_ranges_mm=np.c_[A['R_delta'].min(0)*1000,A['R_delta'].max(0)*1000],key_actions_payload_unchanged=True,hand_native_identity_unchanged=True,protected_action_payloads=protected,source_note_on_off_unchanged=True,thresholds=dict(contact_gap_mm=2,horizontal_mm=2,wrong_key_depth_mm=.5,finger_mesh_intersections=0),threshold_authority='Explicit POC engineering screen, not teacher/physiological limits',can_render_video=basic,seconds=time.perf_counter()-started,limitations=['Finite samples, not continuous collision proof','No wrist/forearm anatomy or force simulation','Inherited key reset Action preserved; pedal and true piano mechanism not modeled','R14 final release at clip boundary is not a separate full release cycle']))
out('SCENE_MANIFEST.json',dict(path=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),scene=sc.name,mapping=man['mapping'],cameras=man['cameras'],key_pivots=man['key_pivots'],clip_start_sec=I['clip_start_sec'],clip_end_sec=I['clip_end_sec'],status=status,fps=60))
print('ONE_ACTUAL_ACTION_CHECK',status,worst_contact,worst_horizontal,worst_passive,maxmiddle,flush=True)

