"""Bake the sole locked result, preserving source quaternion detail and other curves."""
import sys,json,time,itertools
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement'))
from blender_local import *
def save(n,v): (OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item()),encoding='utf8')
start=time.perf_counter();man=read(C1/'SCENE_MANIFEST.json');lock=read(OUT/'STRATEGY_LOCK.json')
assert sha(man['path'])==lock['source_sha256']
res=dict(np.load(OUT/'LIGHTWEIGHT_TRAJECTORY.npz'));tl=read(C1/'PERFORMANCE_TIMELINE.json');notes=tl['notes']
dest=OUT/'STAGE_C_LIGHTWEIGHT_ANIMATION_POC_R1_DESIGN_ONLY.blend';assert not dest.exists()
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False)
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']]
source=rig.animation_data.action;source_name=source.name;slot=rig.animation_data.action_slot
digits=['INDEX','MIDDLE','RING'];names=[n for d in digits for n in c.SETUPS['R',d][0]]
paths={f'pose.bones["{n}"].rotation_quaternion' for n in names}
def fullpayload(action):
 return [dict(path=f.data_path,index=f.array_index,extrapolation=f.extrapolation,keys=[dict(co=list(k.co),interpolation=k.interpolation,handle_left=list(k.handle_left),handle_right=list(k.handle_right),handle_left_type=k.handle_left_type,handle_right_type=k.handle_right_type) for k in f.keyframe_points]) for f in curves(action)]
protected={o.name:dict(action=o.animation_data.action.name,slot=o.animation_data.action_slot.identifier,payload=fullpayload(o.animation_data.action)) for o in sc.objects if o!=rig and o.animation_data and o.animation_data.action}
untouched=[p for p in fullpayload(source) if p['path'] not in paths]
camera_before={v:dict(matrix=[list(r) for r in bpy.data.objects[n].matrix_world],ortho=bpy.data.objects[n].data.ortho_scale) for v,n in man['cameras'].items()}
def decompose(d):
 bone,_,axes,spread,_=c.SETUPS['R',d];mats=[np.array(rig.pose.bones[n].rotation_quaternion.to_matrix()) for n in bone]
 a=axes[0];a=a/np.linalg.norm(a);s=spread/np.linalg.norm(spread);v=mats[0]@a
 sp=np.arctan2(np.dot(s,np.cross(a,v)),np.dot(a,v));mats[0]=c.axisrot(-sp,s)@mats[0]
 angles=[]
 for mat,axis in zip(mats,axes):
  axis=axis/np.linalg.norm(axis);vee=np.array([mat[2,1]-mat[1,2],mat[0,2]-mat[2,0],mat[1,0]-mat[0,1]])*.5
  angles.append(np.arctan2(np.dot(axis,vee),(np.trace(mat)-1)*.5))
 return np.degrees(angles+[sp])
def correction(t):
 delta=np.array([np.interp(t,res['times'],res['correction_deg'][:,j,k]) for j in range(5) for k in range(4)]).reshape(5,4)
 for n in notes:
  if n['hand']=='R' and n['note_on']-.025<=t<=n['note_off']+.025:delta[n['finger']-1]=0
 return delta
# Keep exact source sample times; add 120 Hz and musical boundaries only when
# not within 0.5 ms of an existing sample, avoiding tiny near-duplicate spans.
times=sorted({(float(k.co.x)-1)/60 for f in curves(source) if f.data_path in paths for k in f.keyframe_points if 1<=k.co.x<=358})
for t in list(np.arange(715)/120)+[0,5.95]+[v for n in notes for v in [n['note_on'],n['note_off']]]:
 if min([abs(x-t) for x in times]+[99])>.0005:times.append(float(t))
times=np.array(sorted(times));rots={n:[] for n in names};bound_clamps=0
for t in times:
 settime(sc,float(t));delta=correction(t)
 for j in [1,2,3]:
  d=c.DIGITS[j];q=decompose(d);lo,hi=c.bounds(d);target=np.clip(q+delta[j],np.degrees(lo),np.degrees(hi))
  if np.max(abs(target-q-delta[j]))>1e-5:bound_clamps+=1
  before=c.joint_mats('R',d,np.radians(q));after=c.joint_mats('R',d,np.radians(target))
  for n,a,b in zip(c.SETUPS['R',d][0],before,after):
   old=rig.pose.bones[n].rotation_quaternion.copy()
   quat=old if np.max(abs(delta[j]))<1e-10 else Matrix((b@<REDACTED_EMAIL>(old.to_matrix())).tolist()).to_quaternion()
   if rots[n] and np.dot(rots[n][-1],list(quat))<0:quat.negate()
   rots[n].append(list(quat))
new=source.copy();new.name='DESIGN_ONLY_LIGHTWEIGHT_R1_RIGHT_JOINTS_NOT_APPROVED'
rig.animation_data.action=new;rig.animation_data.action_slot=new.slots[slot.identifier]
for f in curves(new):
 if f.data_path not in paths:continue
 n=f.data_path.split('"')[1];values=np.array(rots[n])[:,f.array_index]
 f.keyframe_points.clear()
 f.keyframe_points.add(len(times));f.keyframe_points.foreach_set('co',np.column_stack((1+60*times,values)).ravel())
 for k in f.keyframe_points:k.interpolation='LINEAR'
 f.update()
assert [p for p in fullpayload(new) if p['path'] not in paths]==untouched
sc['REVIEW_STATUS']='DIAGNOSTIC_ONLY / NOT_APPROVED';sc['METHOD']='CONTACT_GUIDED_LIGHTWEIGHT_ANIMATION'
sc.frame_set(1);sc.camera=bpy.data.objects[man['cameras']['TEACHING']]
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
save('BAKE_RECEIPT.json',dict(seconds=time.perf_counter()-start,samples=len(times),changed_bones=names,changed_curves=36,unchanged_other_curves=True,bound_clamp_samples=bound_clamps,candidate_path=str(dest),candidate_sha256=sha(dest),source_sha256=sha(man['path']),candidate_action=new.name))
bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False)
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']]
if source_name not in bpy.data.actions:
 with bpy.data.libraries.load(man['path'],link=False) as (available,loaded):loaded.actions=[source_name]
new=rig.animation_data.action;newslot=rig.animation_data.action_slot;source=bpy.data.actions[source_name]
def bind(action):rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[newslot.identifier]
preserved=all(dict(action=bpy.data.objects[n].animation_data.action.name,slot=bpy.data.objects[n].animation_data.action_slot.identifier,payload=fullpayload(bpy.data.objects[n].animation_data.action))==v for n,v in protected.items())
assert preserved
assert [p for p in fullpayload(new) if p['path'] not in paths]==untouched
camera_after={v:dict(matrix=[list(r) for r in bpy.data.objects[n].matrix_world],ortho=bpy.data.objects[n].data.ortho_scale) for v,n in man['cameras'].items()}
assert camera_after==camera_before
rois=read(ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/LOCAL_SKIN_ROI.json')
keys=[k for k in c.KEYS if k['color'].upper()=='BLACK' and 64<=k['midi_note']<=82]
def spatial(V,t):
 trees={d:BVHTree.FromPolygons([Vector(v) for v in V],rois[d]['faces'],epsilon=0) for d in ['INDEX','MIDDLE','RING','LITTLE']}
 pairs={a+'_'+b:len(trees[a].overlap(trees[b])) for a,b in [('INDEX','MIDDLE'),('MIDDLE','RING'),('RING','LITTLE')]}
 hits=[]
 for d in digits:
  points=V[rois[d]['vertices']]
  for key in keys:
   pivot=np.array(key['press_pivot']);ang=bpy.data.objects[man['key_pivots'][str(key['key_index'])]].rotation_euler.x if str(key['key_index']) in man['key_pivots'] else 0
   local=(points-pivot)@c.axisrot(ang,[1,0,0])+pivot
   depth=max(float(np.minimum(local-np.min(g['vertices'],axis=0),np.max(g['vertices'],axis=0)-local).min(1).max()*1000) for g in key['geometry'])
   if depth>.02:hits.append(dict(digit=d,key=key['note_name'],midi=key['midi_note'],depth_mm=depth))
 return dict(pair_intersections=pairs,black_hits=hits)
probe=np.unique(np.r_[np.arange(358)/60,[n[k] for n in notes for k in ['note_on','note_off']],1.133333333,3.825])
rows=[];sourceqs=[];newqs=[];active_delta=[];bounds=[];padrows=[];snapshots={}
for i,t in enumerate(probe):
 states={}
 for state,action in [('source',source),('new',new)]:
  bind(action);settime(sc,float(t));V=mesh_pose(mesh)[0];q=np.array([decompose(d) for d in c.DIGITS])
  (sourceqs if state=='source' else newqs).append(q)
  states[state]=dict(V=V,q=q,spatial=spatial(V,t))
  if state=='new':
   for j,d in enumerate(c.DIGITS):
    lo,hi=c.bounds(d);bounds.append(float(max(np.max(np.degrees(lo)-q[j]),np.max(q[j]-np.degrees(hi)),0)))
 for n in notes:
  if n['hand']=='R' and n['note_on']-1e-7<=t<=n['note_off']+1e-7:
   j=n['finger']-1;v=c.MARKERS['R'][j]['mesh_vertex'];change=float(np.linalg.norm(states['new']['V'][v]-states['source']['V'][v])*1000);active_delta.append(change)
   key=c.KEYS[n['key_index']];ang=bpy.data.objects[man['key_pivots'][str(n['key_index'])]].rotation_euler.x
   padrows.append(dict(time=float(t),note=n['note_id'],source=contact(states['source']['V'][v],key,ang),new=contact(states['new']['V'][v],key,ang),pad_change_mm=change))
 rows.append(dict(time=float(t),source=states['source']['spatial'],new=states['new']['spatial']))
 if abs(t-1.133333333)<1e-7 or abs(t-3.825)<1e-7:snapshots[str(float(t))]={s:x['V'].tolist() for s,x in states.items()}
 if i%90==0:print('BAKED_ACTUAL_VALIDATE',i,len(probe),flush=True)
qnew=np.array(newqs);qsource=np.array(sourceqs)
uniform=np.array([np.argmin(abs(probe-t)) for t in np.arange(358)/60]);velnew=np.diff(qnew[uniform],axis=0)*60;velold=np.diff(qsource[uniform],axis=0)*60
severity=max(bounds);padmax=max(active_delta);added=float(np.max(abs(velnew-velold)))
basic=preserved and severity<.002 and padmax<.25 and added<180
save('ACTUAL_VALIDATION.json',dict(rows=rows,active_pads=padrows,protected_actions_unchanged=preserved,unmodified_rig_curves_exact=True,cameras_unchanged=True,engineering_max_violation_deg=severity,active_pad_change_max_mm=padmax,peak_joint_velocity_source_deg_sec=float(np.max(abs(velold))),peak_joint_velocity_new_deg_sec=float(np.max(abs(velnew))),added_velocity_max_deg_sec=added,basic_engineering_music_pass=basic,limits=dict(float_decomposition_tolerance_deg=.002,active_source_pad_drift_mm=.25,added_velocity_deg_sec=180),sampling='60Hz whole phrase plus note boundaries and historical exact probes; local actual distal skin BVHs and raised key bodies',limitations='Finite diagnostic samples, not continuous collision proof; no full 88-key all-mesh audit'))
np.savez_compressed(OUT/'BAKED_ANGLE_SAMPLES.npz',times=probe,source=qsource,new=qnew)
save('VISUAL_PROBE_SKIN.json',snapshots)
bind(new)
assert basic,dict(joint=severity,pad=padmax,added_velocity=added)
save('SCENE_MANIFEST.json',dict(path=str(dest),sha256=sha(dest),scene=sc.name,mapping=man['mapping'],cameras=man['cameras'],frames=357,fps=60,diagnostic_only=True))
print('BASIC_ENGINEERING_MUSIC_PASS',padmax,severity,added,flush=True)
