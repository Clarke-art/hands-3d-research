import dynamic_artist as w
from geometry import *
import geometry as g
def build(number=1):
 assert number in [1,2]
 rig=w.rig;sc=w.sc
 rig.animation_data.action=w.BASE_ACTION
 c.settime(sc,2.2)
 rig.pose.bones['WRIST_R'].matrix=w.W0
 action=w.BASE_ACTION.copy();action.name=f'DYNAMIC_ARTIST_CANDIDATE_{number}_NOT_APPROVED'
 rig.animation_data.action=action
 slot=rig.animation_data.action_slot
 bag=next(b for l in action.layers for st in l.strips for b in st.channelbags if b.slot_handle==slot.handle)
 static=read(OUT/'STATIC_B_STATIC_CHECK.json')
 wrist=rig.pose.bones['WRIST_R']
 wrist.rotation_mode='QUATERNION'
 # Independently chosen sparse animator poses. Preserve the original baked
 # curves outside this bounded span, including all original key coordinates.
 times=[2.2,2.30,2.42,2.60,2.68,2.78,2.86,2.921426,3.02,3.12]
 wrist_weights=[0,.35,1,1,1,.7,.25,0,0,0]
 index_weights=[0,.35,1,1,1,1,1,1,.6,0]
 middle_weights=[0,0,0,0,0,.5,1,1,.6,0]
 index_target=[10,15,8,-12]
 if number==2:
  # Final bounded animation attempt: soften distal curl while retaining MCP,
  # and let wrist release overlap the E5 preparation at small residual weight.
  index_target=[10,10,5,-12]
  wrist_weights=[0,.35,1,1,1,.85,.55,.15,0,0]
 def smooth_curve(f,values,tangent=None):
  for t,v in zip(times,values):
   fr=1+60*t
   old=next((k for k in f.keyframe_points if abs(k.co.x-fr)<1e-5),None)
   k=old or f.keyframe_points.insert(fr,float(v),options={'FAST'})
   k.co=(fr,float(v))
  f.update()
  points=[next(k for k in f.keyframe_points if abs(k.co.x-(1+60*t))<1e-4) for t in times]
  for i,k in enumerate(points):
   k.interpolation='BEZIER';k.handle_left_type='FREE';k.handle_right_type='FREE'
   slope=0. if i in [0,len(points)-1] else (values[i+1]-values[i-1])/(60*(times[i+1]-times[i-1]))
   if tangent and i in [0,len(points)-1]:slope=tangent[0 if i==0 else 1]
   dl=(k.co.x-points[i-1].co.x)/3 if i else (points[1].co.x-k.co.x)/3
   dr=(points[i+1].co.x-k.co.x)/3 if i<len(points)-1 else dl
   k.handle_left=(k.co.x-dl,k.co.y-dl*slope);k.handle_right=(k.co.x+dr,k.co.y+dr*slope)
  f.update()
 def edit_digit(d,target,weights):
  for j,name in enumerate(c.SETUPS['R',d][0]):
   targetq=Matrix(c.joint_mats('R',d,np.radians(target))[j].tolist()).to_quaternion()
   path=f'pose.bones["{name}"].rotation_quaternion'
   fs=sorted([f for f in s.curves(action) if f.data_path==path],key=lambda f:f.array_index)
   orig=[[f.evaluate(1+60*t) for f in fs] for t in times]
   vals=[]
   for q,weight in zip(orig,weights):
    from mathutils import Quaternion
    vals.append(list(Quaternion(q).slerp(targetq,weight)))
   for ix,f in enumerate(fs):
    a,b=1+60*times[0],1+60*times[-1]
    tangent=[(f.evaluate(a)-f.evaluate(a-.001))/.001,(f.evaluate(b+.001)-f.evaluate(b))/.001]
    # RNA keyframe wrappers reference a mutable contiguous buffer. Remove by
    # descending index so earlier removals cannot invalidate later wrappers.
    outside_before=[(tuple(k.co),k.interpolation,tuple(k.handle_left),tuple(k.handle_right)) for k in f.keyframe_points if k.co.x<a-1e-5 or k.co.x>b+1e-5]
    for ki in reversed(range(len(f.keyframe_points))):
     if a-1e-5<=f.keyframe_points[ki].co.x<=b+1e-5:f.keyframe_points.remove(f.keyframe_points[ki],fast=True)
    f.update()
    smooth_curve(f,[q[ix] for q in vals],tangent)
    outside_after=[(tuple(k.co),k.interpolation,tuple(k.handle_left),tuple(k.handle_right)) for k in f.keyframe_points if k.co.x<a-1e-5 or k.co.x>b+1e-5]
    assert [r[:2] for r in outside_before]==[r[:2] for r in outside_after],'OUTSIDE_KEY_VALUE_MUTATION'
    assert all(r[1]=='LINEAR' for r in outside_before),'REVIEW_NONLINEAR_OUTSIDE_HANDLES'
 edit_digit('INDEX',index_target,index_weights)
 edit_digit('MIDDLE',[0,4,3,float(w.Q0['MIDDLE'][3])],middle_weights)
 from mathutils import Quaternion
 WQ=Quaternion(static['wrist_quaternion']);WL=np.array(static['wrist_location'])
 original_loc=list(wrist.location);original_q=list(wrist.rotation_quaternion)
 for path,vals in [('location',[list(WL*a) for a in wrist_weights]),('rotation_quaternion',[list(Quaternion((1,0,0,0)).slerp(WQ,a)) for a in wrist_weights])]:
  for ix in range(len(vals[0])):
   f=bag.fcurves.new(f'pose.bones["WRIST_R"].{path}',index=ix)
   smooth_curve(f,[v[ix] for v in vals])
 c.settime(sc,2.6);sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']]
 dest=OUT/f'CANDIDATE_{number}_IMPLEMENTATION_FIXED_NOT_APPROVED.blend';assert not dest.exists()
 bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=True)
 paths={f'pose.bones["{n}"].rotation_quaternion' for d in ['INDEX','MIDDLE'] for n in c.SETUPS['R',d][0]}|{f'pose.bones["WRIST_R"].{p}' for p in ['rotation_quaternion','location']}
 assert c.digest(s.payload(action,paths))==c.digest(s.payload(w.BASE_ACTION,paths))
 save(f'CANDIDATE_{number}_FIXED_EDIT_LEDGER.json',dict(candidate=str(dest),times=times,wrist_weights=wrist_weights,index_target=index_target,index_weights=index_weights,middle_weights=middle_weights,edited_paths=sorted(paths),unchanged_other_rig_curves=True,protected_actions=w.PROTECTED,native=w.NATIVE,original_wrist_location=original_loc,original_wrist_quaternion=original_q,sparse_keys_per_channel=len(times),retained_original_outside=True,implementation_repair='remove RNA points by descending index; initial files retained as invalid diagnostics, same two authored animation designs'))
 print('BUILT',dest)
