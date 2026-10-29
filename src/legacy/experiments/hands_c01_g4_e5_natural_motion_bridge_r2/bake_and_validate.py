import sys,json,time,math,ast
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Matrix,Vector
O=Path(__file__).resolve().parent;ROOT=O.parent/'hands';sys.path.insert(0,str(O));sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'))
from geometry_detector import *
from triangle_distance import *
import blender_utils as u
source=(O/'extract_anatomy.py').read_text(encoding='utf-8-sig');tree=ast.parse(source);exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['unit','angle','matrix','coords','signed_rot']],type_ignores=[]),'actual_joint_recovery','exec'))
P=json.loads((O/'POLICY_LOCK.json').read_text());M=P['source_action_scene'];TRACK=np.load(O/'ACTION_TRACKS.npz');START=2.527855;EX=2.921426;FULL=2.956426;END=3.349997
ES=json.loads((O/'ENDPOINT_SOLVE_2.json').read_text());Q0=np.array(ES['reference_q_R1']);Q1=np.array(ES['reference_q_R2']);ACTIVE=np.array(ES['active_flex_anchor'])
dest=O/'G4_E5_NATURAL_BRIDGE_DESIGN_PROVISIONAL_R2.blend'
expected=json.loads((O/'PREFLIGHT_AND_ENDPOINT_DIAGNOSIS.json').read_text())['original_action_payloads']
if not dest.exists():
 bpy.ops.wm.open_mainfile(filepath=M['path'],load_ui=False,use_scripts=False);source_scene=bpy.data.scenes[M['scene']];bpy.context.window.scene=source_scene;u.settime(source_scene,START)
 for ob in source_scene.objects:ob['NATURAL_BRIDGE_SOURCE_ID']=ob.name
 bpy.ops.scene.new(type='FULL_COPY');sc=bpy.context.scene;sc.name='G4_E5_NATURAL_BRIDGE_DESIGN_PROVISIONAL_R2';cp={ob['NATURAL_BRIDGE_SOURCE_ID']:ob for ob in sc.objects if 'NATURAL_BRIDGE_SOURCE_ID' in ob}
 for ob in list(source_scene.objects)+list(sc.objects):
  if 'NATURAL_BRIDGE_SOURCE_ID' in ob:del ob['NATURAL_BRIDGE_SOURCE_ID']
 rig=cp[M['mapping']['R']['rig']];mesh=cp[M['mapping']['R']['mesh']];rt=cp[M['mapping']['R']['root']]
 assert u.digest(u.native(mesh,rig))==u.pf['right_native_sha256']
 for ob in [rig,rt]:
  if ob.animation_data and ob.animation_data.action:ob.animation_data.action.use_fake_user=True
  ob.animation_data_clear()
 # Keep inherited left hand static and out of diagnostic renders; no new left-hand Action.
 for key in ['rig','root']:
  lob=cp[M['mapping']['L'][key]]
  if lob.animation_data:lob.animation_data_clear()
 cp[M['mapping']['L']['mesh']].hide_render=True
 rt.rotation_mode='QUATERNION'
 names=TRACK['bone_names'].tolist()
 for i,t in enumerate(TRACK['times']):
  frame=1+60*float(t);rt.location=TRACK['root_location'][i];rt.rotation_quaternion=TRACK['root_quat'][i]
  for prop in ['location','rotation_quaternion']:rt.keyframe_insert(data_path=prop,frame=frame)
  for j,n in enumerate(names):
   pb=rig.pose.bones[n];pb.rotation_mode='QUATERNION';pb.rotation_quaternion=TRACK['bone_quat'][i,j];pb.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=n.split('_')[0])
 derivs={}
 for ob,label in [(rt,'R2_NATURAL_BRIDGE_ROOT_DESIGN_PROVISIONAL'),(rig,'R2_NATURAL_BRIDGE_JOINTS_DESIGN_PROVISIONAL')]:
  ob.animation_data.action.name=label
  for fc in u.curves(ob.animation_data.action):
   if ob==rt:dv=TRACK['root_location_derivative'][:,fc.array_index] if fc.data_path=='location' else TRACK['root_quat_derivative'][:,fc.array_index]
   else:
    n=fc.data_path.split('"')[1];dv=TRACK['bone_quat_derivative'][:,names.index(n),fc.array_index]
   # keyframe_insert merges very close event +/-100us keys; populate RNA directly.
   if ob==rt:values=TRACK['root_location'][:,fc.array_index] if fc.data_path=='location' else TRACK['root_quat'][:,fc.array_index]
   else:values=TRACK['bone_quat'][:,names.index(n),fc.array_index]
   fc.keyframe_points.clear();fc.keyframe_points.add(len(TRACK['times']))
   for ii,kp in enumerate(fc.keyframe_points):kp.co=(1+60*float(TRACK['times'][ii]),float(values[ii]))
   pts=fc.keyframe_points
   assert len(pts)==len(TRACK['times'])
   for i,k in enumerate(pts):
    k.interpolation='BEZIER';k.handle_left_type='FREE';k.handle_right_type='FREE'
    left=(float(k.co.x)-float(pts[i-1].co.x))/3 if i>0 else (float(pts[1].co.x)-float(k.co.x))/3
    right=(float(pts[i+1].co.x)-float(k.co.x))/3 if i+1<len(pts) else left
    slope=float(dv[i])/60
    k.handle_left=(k.co.x-left,k.co.y-slope*left);k.handle_right=(k.co.x+right,k.co.y+slope*right)
 sc.frame_start=math.ceil(1+60*START);sc.frame_end=math.floor(1+60*END);sc.render.fps=60
 sc['DESIGN_PROVISIONAL']=True;sc['HUMAN_APPROVAL_PENDING']=True;sc['BRIDGE_START_SEC']=START;sc['BRIDGE_END_SEC']=END
 assert all((u.digest(u.payload(cp[n].animation_data.action)) if cp[n].animation_data and cp[n].animation_data.action else None)==expected[str(i)] for i,n in u.man['key_pivots'].items())
 bind=dict(scene=sc.name,rig=rig.name,mesh=mesh.name,root=rt.name,objects={n:ob.name for n,ob in cp.items()},cameras={v:cp[n].name for v,n in M['cameras'].items()},new_actions=[rt.animation_data.action.name,rig.animation_data.action.name],interval=[START,END],clock_offset=.35,original_key_action_payloads=expected,only_one_candidate=True)
 (O/'ACTION_BINDINGS.json').write_text(json.dumps(bind,indent=2)+'\n',encoding='utf8');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest))
bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False);bind=json.loads((O/'ACTION_BINDINGS.json').read_text());sc=bpy.data.scenes[bind['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[bind['rig']];mesh=bpy.data.objects[bind['mesh']];rt=bpy.data.objects[bind['root']];cp={n:bpy.data.objects[v] for n,v in bind['objects'].items()}
assert u.digest(u.native(mesh,rig))==u.pf['right_native_sha256']
assert all((u.digest(u.payload(cp[n].animation_data.action)) if cp[n].animation_data and cp[n].animation_data.action else None)==expected[str(i)] for i,n in u.man['key_pivots'].items())
def keyangles():
 a=np.zeros(88)
 for i,n in u.man['key_pivots'].items():a[int(i)]=cp[n].rotation_euler.x
 return a
def recover():
 result=[];error=0;quats=[]
 for d in u.c.DIGITS:
  names,rels,axes,spread,pad=u.c.SETUPS['R',d];vals=[]
  for j,n in enumerate(names):
   R=np.array([list(r) for r in rig.pose.bones[n].matrix_basis])[:3,:3];A,sv,Bt=np.linalg.svd(R);R=A@Bt;ax=np.array(axes[j]);sp=np.array(spread)
   if j==0:ss=angle(ax,R@ax,sp);ff=signed_rot(u.c.axisrot(-np.radians(ss),sp)@R,ax);rec=u.c.axisrot(np.radians(ss),sp)@u.c.axisrot(np.radians(ff),ax)
   else:ss=0.;ff=signed_rot(R,ax);rec=u.c.axisrot(np.radians(ff),ax)
   vals.append(ff);error=max(error,float(np.linalg.norm(R-rec)));quats.append(list(rig.pose.bones[n].rotation_quaternion))
  vals.append(angle(np.array(axes[0]),np.array([list(r) for r in rig.pose.bones[names[0]].matrix_basis])[:3,:3]@np.array(axes[0]),np.array(spread)));result.append(vals)
 return np.array(result),error,np.array(quats)
def strict(V,key,a,f):
 p=keylocal(V,key,a);patch=set(META['pad_patches'][f-1]);count=0
 for ti in np.flatnonzero(LABEL==f-1):
  if not all(int(v) in patch for v in TR[ti]):continue
  for s in key['key_top_playable_surface']:
   poly=list(p[TR[ti]])
   for ax,lim,sgn in [(0,s['xmin'],-1),(0,s['xmax'],1),(1,s['ymin'],-1),(1,s['ymax'],1)]:poly=clip(poly,ax,lim,sgn) if poly else []
   if poly:
    zs=[q[2]-s['z'] for q in poly]
    if min(zs)<=0<=max(zs):count+=1
 return count
def true_contact(ct,ss):return bool(ss>0 and ct['top_surface_crossing_triangles']>0 and ct['near_contact_projected_area_mm2']>0)
cache={}
def measure(t):
 key=round(float(t),12)
 if key in cache:return cache[key]
 u.settime(sc,float(t));V,F=u.coords(mesh);a=keyangles();target=67 if t<EX else 76;m=detect(V,a,dict(midi=target,finger=1 if target==67 else 3))
 cG=contact_metric(V,KEYS[46],a[46],1);cE=contact_metric(V,KEYS[55],a[55],3);sg=strict(V,KEYS[46],a[46],1);se=strict(V,KEYS[55],a[55],3)
 q,off,quats=recover();lam=(q[2,3]-Q0[2,3])/(Q1[2,3]-Q0[2,3]);ref=(1-lam)*Q0[1:]+lam*Q1[1:];delta=ACTIVE-ref[1,:3];alpha=float(np.dot(q[2,:3]-ref[1,:3],delta)/max(np.dot(delta,delta),1e-20));ref[1,:3]=(1-alpha)*ref[1,:3]+alpha*ACTIVE;fam=float(np.max(abs(q[1:]-ref)))
 jgate=(-1e-4<=lam<=1+1e-4 and -1e-4<=alpha<=1+1e-4 and fam<=.001 and off<=1e-5 and np.all(q[0]>=np.array([0,0,0,-35])-1e-4) and np.all(q[0]<=np.array([25,25,18,35])+1e-4))
 mr=next(p for p in m['self_skin'] if p['digits']==['MIDDLE','RING'])
 ex=exact_clearance(V,TR,np.flatnonzero(LABEL==2),np.flatnonzero(LABEL==3),META['topological_vertex_neighbors'],max(mr['minimum_gap_sampled_mm']/1000+1e-10,.0000001)) if not mr['true_nonadjacent_triangle_pair_count'] else dict(distance_mm=0.,reason='actual intersections')
 held=true_contact(cG,sg) and cG['pad_horizontal_outside_mm']<=1e-5 and abs(cG['pad_gap_mm'])<=3
 strike=true_contact(cE,se) and cE['pad_horizontal_outside_mm']<=1e-5 and abs(cE['pad_gap_mm'])<=3
 requiredG=t<=EX+1e-10;requiredE=t>=EX-1e-10
 contactpass=(not requiredG or held) and (not requiredE or strike)
 geometry=m['target_key_max_depth_mm']<=.25 and m['wrong_key_or_nonpulp_max_depth_mm']<=.25 and m['nonadjacent_self_triangle_pairs']==0
 wrist=list(<REDACTED_EMAIL>['WRIST_R'].head)
 row=dict(time=float(t),music_time=float(t-.35),phase='G4_HOLD_PREPARE' if t<EX else 'EXACT_EXCHANGE' if abs(t-EX)<1e-10 else 'E5_KEY_DESCENT' if t<FULL else 'E5_HOLD',G4_contact_raw=cG,E5_contact_raw=cE,G4_strict_crossing_faces=sg,E5_strict_crossing_faces=se,G4_hold=held,E5_contact=strike,G4_required=requiredG,E5_required=requiredE,contact_timing_gate=contactpass,geometry_gate=geometry,joint_gate=bool(jgate),actual_geometry=m,middle_ring_exact_clearance=ex,joint_controls_deg=q.tolist(),joint_basis_quaternions=quats.tolist(),reference_lambda=float(lam),active_flex_alpha=alpha,reference_residual_deg=fam,off_axis_rotation_error=off,root_world_position_m=list(rt.matrix_world.translation),root_world_quaternion=list(rt.matrix_world.to_quaternion()),wrist_world_position_m=wrist,G4_angle_rad=float(a[46]),E5_angle_rad=float(a[55]),root_relative_Z_mm=float((rt.matrix_world.translation.z-u.BASE[2])*1000))
 cache[key]=row;return row
base=np.arange(START,END,1/120);events=[START,EX,FULL,END];near=[v+d for v in [EX,FULL] for d in [-.004,-.001,-.0001,0,.0001,.001,.004] if START<=v+d<=END];primary=np.unique(np.r_[base,events,TRACK['times'],near]);rows=[]
startcheck=time.monotonic()
for i,t in enumerate(primary):
 rows.append(measure(float(t)))
 if i%20==0:print('ACTUAL_BRIDGE_SAMPLE',i,len(primary),'seconds',round(time.monotonic()-startcheck,2),flush=True)
# Focus additional samples on the twelve most risky intervals; no endless density expansion.
scored=[]
for a,b in zip(rows[:-1],rows[1:]):
 score=max(a['actual_geometry']['wrong_key_or_nonpulp_max_depth_mm'],b['actual_geometry']['wrong_key_or_nonpulp_max_depth_mm'])/.25+5*(not a['contact_timing_gate'] or not b['contact_timing_gate'])+max(a['actual_geometry']['nonadjacent_self_triangle_pairs'],b['actual_geometry']['nonadjacent_self_triangle_pairs'])
 if score>0:scored.append((score,a['time'],b['time']))
adaptive=[]
for score,a,b in sorted(scored,reverse=True)[:12]:
 adaptive.extend([a+(b-a)*f for f in [.25,.5,.75]])
for t in adaptive:measure(float(t))
rows=sorted(cache.values(),key=lambda r:r['time']);uniform=[measure(float(t)) for t in base];TT=np.array([r['time'] for r in uniform]);WP=np.array([r['wrist_world_position_m'] for r in uniform])*1000;RP=np.array([r['root_world_position_m'] for r in uniform])*1000;QQ=np.array([r['joint_controls_deg'] for r in uniform]);velocity=np.gradient(WP,TT,axis=0,edge_order=2);acc=np.gradient(velocity,TT,axis=0,edge_order=2);rootv=np.gradient(RP,TT,axis=0,edge_order=2);jv=np.gradient(QQ,TT,axis=0,edge_order=2)
fails=[r for r in rows if not(r['contact_timing_gate'] and r['geometry_gate'] and r['joint_gate'])]
loss=[r['time'] for r in rows if r['G4_required'] and not r['G4_hold']];ec=[r['time'] for r in rows if r['E5_contact']];gc=[r['time'] for r in rows if r['G4_hold']]
gaps=[r['middle_ring_exact_clearance']['distance_mm'] for r in rows if r['middle_ring_exact_clearance'].get('distance_mm') is not None]
critical={str(t):measure(t) for t in events};allpass=not fails
maxrootjump=0.;maxqjump=0.
for ob in [rt,rig]:
 for fc in u.curves(ob.animation_data.action):
  for k in fc.keyframe_points:
   dxl=k.co.x-k.handle_left.x;dxr=k.handle_right.x-k.co.x
   if abs(dxl)<1e-8 or abs(dxr)<1e-8:continue
   jump=abs((k.co.y-k.handle_left.y)/dxl-(k.handle_right.y-k.co.y)/dxr)*60
   if ob==rt and fc.data_path=='location':maxrootjump=max(maxrootjump,jump*1000)
   else:maxqjump=max(maxqjump,jump)
kin=dict(derivative_method='Finite differences of actual uniform120Hz wrist/world and recovered rest-relative joint controls; not clinical absolute angles',wrist_speed_peak_mm_s=float(np.linalg.norm(velocity,axis=1).max()),wrist_acceleration_peak_mm_s2=float(np.linalg.norm(acc,axis=1).max()),root_speed_peak_mm_s=float(np.linalg.norm(rootv,axis=1).max()),joint_control_velocity_peak_deg_s=float(np.max(abs(jv))),per_finger_joint_control_velocity_peak_deg_s={d:np.max(abs(jv[:,j]),axis=0).tolist() for j,d in enumerate(DIGITS)},actual_component_C1_float32_root_slope_jump_mm_s=maxrootjump,actual_quaternion_component_slope_jump_per_s=maxqjump,no_clinical_comfort_speed_limit_claim=True)
out=dict(status='BRIDGE_TECHNICAL_PASS_HUMAN_PENDING' if allpass else 'BRIDGE_MOTION_PARTIAL',authority='DESIGN_PROVISIONAL',actual_action_generated=True,scene=sc.name,blend=str(dest),new_actions=bind['new_actions'],candidate_count=1,optimizer=json.loads((O/'ONE_BRIDGE_SOLVE.json').read_text()),dynamic_all_sample_gates=allpass,can_render_video=allpass,validation=dict(base_Hz=120,primary_count=len(primary),adaptive_count=len(adaptive),unique_actual_sample_count=len(rows),exact_event_boundaries=events,finite_sampling_not_continuous_time_collision_proof=True),rows=rows,critical_times=critical,G4_first_hold_loss_time=loss[0] if loss else None,G4_last_observed_contact=gc[-1] if gc else None,E5_first_observed_contact_time=ec[0] if ec else None,E5_contact_early_relative_ON_sec=EX-ec[0] if ec else None,maximum_target_depth_mm=max(r['actual_geometry']['target_key_max_depth_mm'] for r in rows),maximum_non_target_depth_mm=max(r['actual_geometry']['wrong_key_or_nonpulp_max_depth_mm'] for r in rows),maximum_nonadjacent_crossing_pairs=max(r['actual_geometry']['nonadjacent_self_triangle_pairs'] for r in rows),middle_ring_min_exact_mm=min(gaps) if gaps else None,failed_samples=len(fails),joint_failed_samples=sum(not r['joint_gate'] for r in rows),kinematics=kin,original_key_action_payloads_unchanged=True,native_frozen_identity_verified=u.digest(u.native(mesh,rig))==u.pf['right_native_sha256'],entry_R05_R06_R07_hand_context='NOT_VALIDATED: only original key Action context inspected, no entrance animation generated',music_time_offset_sec=.35,clip=[START,END],Human_review='PENDING',natural_reference_limit='Active flexion family remains provisional; no clinical maximum/comfortable-ROM interpretation',check_seconds=time.monotonic()-startcheck)
assert out['native_frozen_identity_verified']
(O/'ACTUAL_ACTION_VALIDATION.json').write_text(json.dumps(out,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')
print('ACTUAL_ACTION_RESULT',out['status'],'samples',len(rows),'failed',len(fails),'G4loss',out['G4_first_hold_loss_time'],'E5first',out['E5_first_observed_contact_time'],'wrong',out['maximum_non_target_depth_mm'],'self',out['maximum_nonadjacent_crossing_pairs'],flush=True)
