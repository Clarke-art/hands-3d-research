import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_support as s
from blender_support import *
begin=time.perf_counter();base=read(OUT/'BASELINE_B01_ACTUAL.json')
# Authored phase poses, chosen from ORIGINAL C1 observation, not LW1 angles.
anchors=[
 [.9,[0,0,0,0],[0,0,0,0]],
 [1.027142,[-.8,1.6,-.8,1.2],[-1.5,2.5,-1,-3]],
 [1.1333333333333333,[-1.2,2.4,-1.2,2.2],[-2.5,4.5,-2,-5.5]],
 [1.207142,[-.4,.8,0,1],[-2.5,4.5,-2,-5.5]],
 [1.3,[-.4,.8,0,1],[-1.5,3,-1,-4.5]],
 [1.4214275,[-.4,.8,0,1],[-.6,1.2,0,-4.5]],
 [1.4614275,[-.5,1,-.5,1.8],[-.6,1.2,0,-3]],
 [1.55,[0,-.6,.6,1],[-.4,.8,0,-1.5]],
 [1.635713,[0,0,0,0],[-.2,.4,0,-.5]],
 [1.705713,[0,0,0,0],[0,0,0,0]]]
lock=dict(strategy='One authored multi-joint phase-pose increment, quintic interpolation over original C1; no pose search/IK/optimization',
 support=[.9,1.705713],review_window=[.9,1.75],core=[1.1,1.4214275],anchors=anchors,anchor_columns=['time','MIDDLE_MCP_PIP_DIP_spread_delta_deg','RING_MCP_PIP_DIP_spread_delta_deg'],
 bones=['MIDDLE_MCP_R','MIDDLE_PIP_R','MIDDLE_DIP_R','RING_MCP_R','RING_PIP_R','RING_DIP_R'],bake_hz=240,candidate_limit=1,
 original_C1_sha256=sha(SOURCE),contact_horizontal_mm=.03,contact_gap_abs_mm=3,nonregression_mm=.02,added_joint_velocity_deg_s=180,
 domain_tolerance_deg=.002,geometry_numerical_mm=.0001,
 target_gate='No middle/ring actual face intersections in primary B01 core; no new target face pairs relative to C1 at other times; full other-region nonregression',
 safety='Actual active skin contact and original domain; no new other key penetration, shared/web regression, nonincident self or crosshand face pairs',
 final_product='Human visual acceptance required; historical B02/B03 not repaired',
 render_policy='Local NOT_APPROVED diagnostic first; full 23-note candidate video only if machine gates pass')
save('STRATEGY_LOCK.json',lock);save('ONE_EDIT_STARTED.json',dict(candidate_number=1,strategy_sha256=sha(OUT/'STRATEGY_LOCK.json')))
sc,rig,mesh,left,lrig=s.open_scene(OUT/'C1_B01_ORIGINAL_EDITING_COPY.blend')
source=rig.animation_data.action;slot=rig.animation_data.action_slot.identifier
paths={f'pose.bones["{n}"].rotation_quaternion' for n in lock['bones']}
protected=s.protected_state(exclude_rig=True);untouched=s.payload(source,paths)
oldcurves=[f for f in s.curves(source) if f.data_path in paths];assert len(oldcurves)==24
a,b=lock['support'];fa,fb=1+60*a,1+60*b
ts=sorted({(float(k.co.x)-1)/60 for f in oldcurves for k in f.keyframe_points if fa-1e-5<=k.co.x<=fb+1e-5})
for t in np.r_[np.arange(a,b,1/240),[p[0] for p in anchors],a,b]:
    if min([abs(float(t)-v) for v in ts]+[99])>1e-6:ts.append(float(t))
ts=np.array(sorted(ts));ats=np.array([p[0] for p in anchors]);ads=np.array([[p[1],p[2]] for p in anchors])
def correction(t):
    if t<=a or t>=b:return np.zeros((2,4))
    ix=np.clip(np.searchsorted(ats,t,side='right')-1,0,len(ats)-2);u=(t-ats[ix])/(ats[ix+1]-ats[ix]);u=u**3*(10+u*(-15+6*u))
    return ads[ix]+u*(ads[ix+1]-ads[ix])
rots={n:[] for n in lock['bones']};pose_rows=[];largest_domain=0
for t in ts:
    c.settime(sc,float(t));delta=correction(t);qs=[];targets=[]
    for index,d in enumerate(['MIDDLE','RING']):
        q=s.degrees(d);target=q+delta[index];bounds=np.array(base['frozen_domains'][DIGITS.index(d)])
        violation=float(max(0,np.max(bounds[0]-target),np.max(target-bounds[1])));largest_domain=max(largest_domain,violation)
        before=c.joint_mats('R',d,np.radians(q));after=c.joint_mats('R',d,np.radians(target))
        for name,x,y in zip(c.SETUPS['R',d][0],before,after):
            old=rig.pose.bones[name].rotation_quaternion.copy()
            quat=old if np.max(abs(delta[index]))<1e-12 else Matrix((y@<REDACTED_EMAIL>(old.to_matrix())).tolist()).to_quaternion()
            if quat.dot(old)<0:quat.negate()
            rots[name].append(list(quat))
        qs.append(q);targets.append(target)
    if min(abs(t-x) for x in ats)<1e-6:pose_rows.append(dict(time=t,source_qdeg=qs,target_qdeg=targets,delta_deg=delta))
# Preserve and diagnose any domain defect; never hide it with in-loop pose clamping.
new=source.copy();new.name='B01_ONE_MULTIJOIN_PHASE_EDIT_NOT_APPROVED';new.use_fake_user=True;source.use_fake_user=True
rig.animation_data.action=new;rig.animation_data.action_slot=new.slots[slot]
outside={ (f.data_path,f.array_index):[(list(k.co),k.interpolation) for k in f.keyframe_points if k.co.x<fa-1e-5 or k.co.x>fb+1e-5] for f in oldcurves}
for f in s.curves(new):
    if f.data_path not in paths:continue
    name=f.data_path.split('"')[1]
    for k in list(f.keyframe_points):
        if fa-1e-5<=k.co.x<=fb+1e-5:f.keyframe_points.remove(k,fast=True)
    for t,quat in zip(ts,rots[name]):
        k=f.keyframe_points.insert(1+60*float(t),quat[f.array_index],options={'FAST'});k.interpolation='LINEAR'
    f.update()
    assert [(list(k.co),k.interpolation) for k in f.keyframe_points if k.co.x<fa-1e-5 or k.co.x>fb+1e-5]==outside[f.data_path,f.array_index]
assert s.payload(new,paths)==untouched and s.protected_state(exclude_rig=True)==protected
assert all(c.digest(c.native(ob,rg))==base['native_structure'][side] for side,ob,rg in [('R',mesh,rig),('L',left,lrig)])
sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']];sc.frame_start=55;sc.frame_end=105;sc.frame_preview_start=55;sc.frame_preview_end=105;sc.use_preview_range=True
for scene in bpy.data.scenes:scene.render.filepath=str(OUT/'render_output'/scene.name/'frame_')
sc['STATUS']='B01 ONE CANDIDATE / NOT_APPROVED';sc['OPTIMIZER_CALLS']=0;sc['EDITED_BONES']=', '.join(lock['bones'])
c.settime(sc,1.1333333333333333);bpy.context.preferences.filepaths.save_version=0
dest=OUT/'B01_MULTIJOIN_SINGLE_CANDIDATE_NOT_APPROVED.blend';assert not dest.exists();bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=False)
save('EDIT_RECEIPT.json',dict(seconds=time.perf_counter()-begin,candidate_path=str(dest),candidate_sha256=sha(dest),source_action=source.name,source_slot=slot,candidate_action=new.name,
 bones=lock['bones'],curves=24,samples=len(ts),pose_rows=pose_rows,largest_prebake_domain_violation_deg=largest_domain,protected_actions=protected,native_structure=base['native_structure'],
 other_curves_exact=True,outside_key_values_and_interpolation_exact=True,optimizer_calls=0,candidates=1,parameter_retries=0))
protection('EDIT_PROTECTION.json');print('ONE_MULTIJOIN_EDIT_SAVED',len(ts),largest_domain,time.perf_counter()-begin,flush=True)
