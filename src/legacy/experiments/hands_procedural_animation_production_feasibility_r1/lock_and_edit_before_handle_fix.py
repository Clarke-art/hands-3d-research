import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_support as s
from blender_support import *
begin=time.perf_counter()
assert read(OUT/'BASELINE_PREVIEW_RECEIPT.json')['speed']==1
assert read(OUT/'BASELINE_LOCAL_PROBE.json')['rows'][3]['ring_Csharp5_depth_mm']>5
lock=dict(fragment=[START,END],target='RIGHT RING / C#5',witness_time=4.916666666666667,
          method='One fixed smoothstep MCP flexion/spread offset; no search, IK, optimizer or retries',
          delta_deg=[-7.5,0,0,-2.0],fade_in=[4.6,4.85],hold=[4.85,5.25],fade_out=[5.25,5.5],
          candidate_limit=1,modified_bones=['RING_MCP_R'],modified_channels=4,
          sample_hz=240,contact_horizontal_mm=.03,contact_gap_abs_mm=3,
          contact_pad_drift_mm=.01,nonregression_mm=.02,geometry_float_mm=.0001,
          target_core_vertex_depth_mm=.5,target_core_surface_depth_mm=.5,
          added_joint_velocity_deg_s=180,engineering_domain_deg=[[0,0,0,-25],[32,32,20,25]],
          geometric_gate='All 88 keys/139 components, all right skin, shared/mixed regions, ten digit pairs, nonincident self and cross-hand surfaces; new face-pair regressions forbidden',
          continuity='Source exact outside edit support, smoothstep correction zero value/velocity/acceleration at its endpoints; baked quaternion piecewise-linear evaluation is sampled and separately bounded by segment angular rates',
          human_naturalness='PENDING, never inferred from geometric PASS',source_sha256=sha(SOURCE))
save('STRATEGY_LOCK.json',lock)
save('ONE_ATTEMPT_STARTED.json',dict(strategy_sha256=sha(OUT/'STRATEGY_LOCK.json'),candidate_number=1,started_utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()))
copy=OUT/'C1_LOCAL_EDIT_WORKING_COPY.blend';sc,rig,mesh,left,lrig=s.open_scene(copy)
src=rig.animation_data.action;slot=rig.animation_data.action_slot.identifier
paths={'pose.bones["RING_MCP_R"].rotation_quaternion'}
unchanged=s.payload(src,paths);protected=s.protected_state(exclude_rig=True)
native={side:c.digest(c.native(ob,rg)) for side,ob,rg in [('R',mesh,rig),('L',left,lrig)]}
def smooth(u):
    u=np.clip(u,0,1);return u*u*u*(10+u*(-15+6*u))
def envelope(t):return float(smooth((t-4.6)/.25)*smooth((5.5-t)/.25))
oldcurves=[f for f in s.curves(src) if f.data_path in paths]
assert len(oldcurves)==4
ts=sorted({(float(k.co.x)-1)/60 for f in oldcurves for k in f.keyframe_points if 4.6-1e-8<=(k.co.x-1)/60<=5.5+1e-8})
for t in np.r_[np.arange(4.6,5.5+1e-9,1/120),4.6,4.85,5.25,5.5]:
    if min([abs(float(t)-v) for v in ts]+[99])>1e-6:ts.append(float(t))
ts=np.array(sorted(ts));rots=[];deltas=[];minimum_q=1e9;maximum_q=-1e9
for t in ts:
    c.settime(sc,float(t));q=s.degrees('RING');delta=np.array(lock['delta_deg'])*envelope(t);target=q+delta
    assert np.all(target>=lock['engineering_domain_deg'][0]) and np.all(target<=lock['engineering_domain_deg'][1]),('DOMAIN_STOP_NO_RETRY',t,q,target)
    old=rig.pose.bones['RING_MCP_R'].rotation_quaternion.copy()
    if envelope(t)<1e-12:quat=old
    else:
        a=c.joint_mats('R','RING',np.radians(q))[0];b=c.joint_mats('R','RING',np.radians(target))[0]
        quat=Matrix((b@<REDACTED_EMAIL>(old.to_matrix())).tolist()).to_quaternion()
        if quat.dot(old)<0:quat.negate()
    rots.append(list(quat));deltas.append(delta);minimum_q=min(minimum_q,float(target[0]));maximum_q=max(maximum_q,float(target[0]))
new=src.copy();new.name='EXPERIMENT_C_RING_MCP_SINGLE_EDIT_NOT_APPROVED'
new.use_fake_user=True;src.use_fake_user=True
rig.animation_data.action=new;rig.animation_data.action_slot=new.slots[slot]
outside_before={f.array_index:[dict(co=list(k.co),left=list(k.handle_left),right=list(k.handle_right),interpolation=k.interpolation,lt=k.handle_left_type,rt=k.handle_right_type) for k in f.keyframe_points if k.co.x<277-1e-5 or k.co.x>331+1e-5] for f in oldcurves}
for f in s.curves(new):
    if f.data_path not in paths:continue
    for k in list(f.keyframe_points):
        if 277-1e-5<=k.co.x<=331+1e-5:f.keyframe_points.remove(k,fast=True)
    for t,quat in zip(ts,rots):
        k=f.keyframe_points.insert(1+60*float(t),quat[f.array_index],options={'FAST'});k.interpolation='LINEAR'
    f.update()
outside_after={f.array_index:[dict(co=list(k.co),left=list(k.handle_left),right=list(k.handle_right),interpolation=k.interpolation,lt=k.handle_left_type,rt=k.handle_right_type) for k in f.keyframe_points if k.co.x<277-1e-5 or k.co.x>331+1e-5] for f in s.curves(new) if f.data_path in paths}
assert outside_before==outside_after,'OUTSIDE_CURVE_PAYLOAD_CHANGED'
assert s.payload(new,paths)==unchanged and s.protected_state(exclude_rig=True)==protected
assert all(c.digest(c.native(ob,rg))==native[side] for side,ob,rg in [('R',mesh,rig),('L',left,lrig)])
sc['EXPERIMENT_STATUS']='ONE_CANDIDATE_UNVALIDATED_NOT_APPROVED';sc['EXPERIMENT_TARGET']='RING / C#5 only'
sc['EXPERIMENT_WINDOW']='4.4-5.6 sec display';sc['OPTIMIZER_CALLS']=0
sc.frame_start=265;sc.frame_end=336;sc.frame_preview_start=265;sc.frame_preview_end=336;sc.use_preview_range=True
sc.camera=bpy.data.objects[MAN['cameras']['TEACHING']];c.settime(sc,4.916666666666667)
bpy.context.preferences.filepaths.save_version=0
dest=OUT/'C_RING_SINGLE_CANDIDATE_NOT_APPROVED.blend';assert not dest.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=False)
save('EDIT_RECEIPT.json',dict(seconds=time.perf_counter()-begin,candidate_path=str(dest),candidate_sha256=sha(dest),source_action=src.name,source_slot=slot,candidate_action=new.name,
     baked_samples=len(ts),changed_bones=['RING_MCP_R'],changed_curves=4,other_curves_exact=True,other_actions_exact=True,outside_modified_curves_exact=True,
     native_structure=native,protected_actions=protected,target_min_MCP_deg=minimum_q,target_max_MCP_deg=maximum_q,
     analytical_added_flexion_peak_deg_s=7.5*1.875/.25,analytical_added_spread_peak_deg_s=2*1.875/.25,
     solver_calls=0,candidates=1,parameter_retries=0))
protection('EDIT_PROTECTION.json')
print('SINGLE_EDIT_SAVED',len(ts),minimum_q,maximum_q,time.perf_counter()-begin,flush=True)
