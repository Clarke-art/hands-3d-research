import dynamic_session as w
from dynamic_session import *

def shifted_wrist(delta):
 b=w.rig.pose.bones['WRIST_R'];M=<REDACTED_EMAIL>;M.translation+=Vector(delta);b.matrix=w.rig.matrix_world.inverted()@M;bpy.context.view_layer.update()
def place_pad(d,key,x,y,gap_mm):
 # One direct rigid palm placement from the measured pad to a declared spot.
 # No joint solving, iterations, angle search, or generated motion planner.
 V=s.coords_tri(w.mesh)[0];pad=V[c.MARKERS['R'][DIGITS.index(d)]['mesh_vertex']]
 target=np.array([x,y,key['key_top_playable_surface'][0]['z']+gap_mm*.001]);pv=np.array(key['press_pivot'])
 target=(target-pv)@c.axisrot(s.keyangle(key),key['press_axis']).T+pv
 shifted_wrist(target-pad)

def patch_curves(action,old,samples,paths,lo,hi):
 oldmap={(f.data_path,f.array_index):f for f in s.curves(old)}
 newmap={(f.data_path,f.array_index):f for f in s.curves(action)}
 for path in paths:
  dim=3 if path.endswith('.location') else 4
  bone=path.split('"')[1];prop=path.rsplit('.',1)[1]
  for ai in range(dim):
   f=newmap[path,ai];of=oldmap[path,ai]
   # Exact de Casteljau splitting preserves the original exterior polynomial.
   def split_at(frame):
    pts=f.keyframe_points
    exact=next((k for k in pts if abs(k.co.x-frame)<1e-5),None)
    if exact:return exact
    left=next((k for k in reversed(list(pts)) if k.co.x<frame),None)
    right=next((k for k in pts if k.co.x>frame),None)
    if left is None or right is None:
     assert f.extrapolation=='CONSTANT'
     value=f.evaluate(frame);k=pts.insert(frame,value,options={'FAST'});k.interpolation='BEZIER';k.handle_left_type='FREE';k.handle_right_type='FREE';k.handle_left=(frame-.1,value);k.handle_right=(frame+.1,value);f.update()
     return next(k for k in pts if abs(k.co.x-frame)<1e-5)
    if left.interpolation in ['LINEAR','CONSTANT']:
     value=f.evaluate(frame);interp=left.interpolation;k=pts.insert(frame,value,options={'FAST'});k.interpolation=interp;k.handle_left_type='FREE';k.handle_right_type='FREE';k.handle_left=(frame-.1,value);k.handle_right=(frame+.1,value);f.update()
     return next(k for k in pts if abs(k.co.x-frame)<1e-5)
    P=np.array([left.co,left.handle_right,right.handle_left,right.co],float)
    low,high=0.,1.
    for _ in range(55):
     u=(low+high)/2;q=(1-u)**3*P[0]+3*(1-u)**2*u*P[1]+3*(1-u)*u*u*P[2]+u**3*P[3]
     if q[0]<frame:low=u
     else:high=u
    u=(low+high)/2;P01=(1-u)*P[0]+u*P[1];P12=(1-u)*P[1]+u*P[2];P23=(1-u)*P[2]+u*P[3];P012=(1-u)*P01+u*P12;P123=(1-u)*P12+u*P23;P0123=(1-u)*P012+u*P123
    lframe=float(left.co.x);rframe=float(right.co.x)
    left.handle_right_type='FREE';left.handle_right=P01
    right.handle_left_type='FREE';right.handle_left=P23
    k=pts.insert(frame,P0123[1],options={'FAST'});k.interpolation='BEZIER';k.handle_left_type='FREE';k.handle_right_type='FREE';k.handle_left=P012;k.handle_right=P123;f.update()
    return next(k for k in pts if abs(k.co.x-frame)<1e-5)
   kl=split_at(1+60*lo);kr=split_at(1+60*hi)
   boundary_left=np.array(kl.handle_left);boundary_right=np.array(kr.handle_right)
   for j in reversed(range(len(f.keyframe_points))):
    x=f.keyframe_points[j].co.x
    if 1+60*lo+1e-5<x<1+60*hi-1e-5:f.keyframe_points.remove(f.keyframe_points[j],fast=True)
   for row in samples:
    frame=1+60*row['time'];p=row['pose'][bone];value=p['location' if prop=='location' else 'quaternion'][ai]
    f.keyframe_points.insert(frame,value,options={'FAST'})
   f.update();pts=[k for k in f.keyframe_points if 1+60*lo-1e-5<=k.co.x<=1+60*hi+1e-5]
   for j,k in enumerate(pts):
    k.interpolation='BEZIER';k.handle_left_type='FREE';k.handle_right_type='FREE'
    if j>0:
     dt=(k.co.x-pts[j-1].co.x)/3;k.handle_left=(k.co.x-dt,k.co.y)
    if j+1<len(pts):
     dt=(pts[j+1].co.x-k.co.x)/3;k.handle_right=(k.co.x+dt,k.co.y)
   pts[0].handle_left=boundary_left;pts[-1].handle_right=boundary_right
   f.update()

def build_one():
 w.reset();sc,rig=w.sc,w.rig;old=w.BASE_ACTION
 # First authored design: keep R4's separated R10 preparation, move the ring
 # left within D5 while middle rolls over a raised proximal arch to E5.
 table=[
  # time, ring MCP/PIP/DIP/spread, middle MCP/PIP/DIP/spread, anchor
  (w.A,[9,1,2,-3],[10,12,13,-7],'RING'),
  (3.60,[19,1,1,1],[2,6,6,-5],'RING'),
  (3.67,[23,1,1,8],[1,5,6,-5],'RING'),
  (3.708333333333333,[23,1,1,14],[1,12,10,-10],'RING'),
  (3.74,[23,1,1,20],[1,22,14,-17],'RING'),
  (w.H,[23,1,1,23],[2,28,16,-20],'RING'),
  (3.80,[16,2,2,18],[8,26,16,-18],'MIDDLE'),
  (3.84,[7,3,3,12],[16,22,14,-12],'MIDDLE'),
  (3.88,[3,2,2,8],[22,16,10,-8],'MIDDLE'),
  (3.94,[3,1,1,-3],[25,22,13,0],'MIDDLE'),
 ]
 lo=w.A;hi=w.B
 samples=[];measurements=[]
 for t,rq,mq,anchor in table:
  rig.animation_data.action=old;c.settime(sc,t)
  w.qset('RING',rq);w.qset('MIDDLE',mq)
  # Idle index slightly straighter avoids black-key tip intrusion as palm moves.
  w.qset('INDEX',[6,8,5,-12])
  key=KEYS[w.R10['key_index'] if anchor=='RING' else w.R11['key_index']]
  place_pad(anchor,key,.1915 if anchor=='RING' else .2155,.024,.7)
  row,V,L=w.measure(t);samples.append(dict(time=t,pose=w.pose(),anchor=anchor));measurements.append(row)
 # Closed temporal support: no edits in R09 or R12 formal performance.
 for t in [lo,hi]:
  rig.animation_data.action=old;c.settime(sc,t)
  p=dict(time=t,pose=w.pose(),anchor='original_exact_boundary')
  if t==lo:samples[0]=p
  else:samples.append(p)
 paths=['pose.bones["WRIST_R"].location']+[f'pose.bones["{d}_{j}_R"].rotation_quaternion' for d in ['INDEX','MIDDLE','RING'] for j in ['MCP','PIP','DIP']]
 action=old.copy();action.name='R5_ARTIST_HANDOFF_CANDIDATE_1_NOT_APPROVED';rig.animation_data.action=action
 patch_curves(action,old,samples,paths,lo,hi)
 c.settime(sc,w.H);sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']]
 dest=OUT/'CANDIDATE_1_NOT_APPROVED.blend';assert not dest.exists();bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=True)
 save('CANDIDATE_1_EDIT_LEDGER.json',dict(candidate=str(dest),scope=[lo,hi],paths=paths,samples=samples,authored_pose_checks=measurements,method='Ten directly specified coordinating poses, one measured-pad rigid palm placement per pose; actual quaternion/location FCurves use cubic Bezier flat interior handles. Exterior curves split exactly; exact R09/R12 boundary values retained. No solver or pose/angle search. R4 references not fixed templates.',purpose='Ring D5 hold; raised middle preparation with separate curl; ring release into R12 preparation; avoid idle index black keys.',candidate_count=1,original_other_actions_unchanged=OTHER_ACTIONS==s.protected_state(True)))
 print('CANDIDATE_1_AUTHORED',flush=True)

def build_two():
 w.reset();sc,rig=w.sc,w.rig;old=w.BASE_ACTION
 # Final, different routing: flex ring at PIP/IP, carry middle through at MCP;
 # move ring to front D5 and clear/release it earlier AFTER the exact OFF.
 table=[
  (w.A,None,None,None),
  (3.60,[12,12,8,1],[2,6,6,-5],'RING'),
  (3.67,[6,20,12,8],[1,5,6,-5],'RING'),
  (3.708333333333333,[3,25,14,14],[2,4,4,-10],'RING'),
  (3.74,[1,28,16,20],[4,2,2,-18],'RING'),
  (w.H,[1,28,16,23],[7,1,1,-23],'RING'),
  (3.80,[1,15,10,10],[9,2,2,-19],'MIDDLE'),
  (3.84,[1,8,5,3],[17,10,7,-12],'MIDDLE'),
  (3.88,[3,2,2,0],[22,16,10,-8],'MIDDLE'),
  (3.94,[3,1,1,-3],[25,22,13,0],'MIDDLE'),
  (w.B,None,None,None),
 ]
 samples=[];measurements=[]
 for t,rq,mq,anchor in table:
  rig.animation_data.action=old;c.settime(sc,t)
  if anchor:
   w.qset('RING',rq);w.qset('MIDDLE',mq);w.qset('INDEX',[6,8,5,-12])
   key=KEYS[w.R10['key_index'] if anchor=='RING' else w.R11['key_index']]
   # Ring contact is slightly right of D5 centre with room for whole-finger skin.
   place_pad(anchor,key,.1935 if anchor=='RING' else .2155,.018 if anchor=='RING' else .024,.7)
  row,V,L=w.measure(t);samples.append(dict(time=t,pose=w.pose(),anchor=anchor or 'original_exact_boundary'));measurements.append(row)
 paths=['pose.bones["WRIST_R"].location']+[f'pose.bones["{d}_{j}_R"].rotation_quaternion' for d in ['INDEX','MIDDLE','RING'] for j in ['MCP','PIP','DIP']]
 action=old.copy();action.name='R5_ARTIST_HANDOFF_CANDIDATE_2_NOT_APPROVED';rig.animation_data.action=action
 patch_curves(action,old,samples,paths,w.A,w.B)
 c.settime(sc,w.H);sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']]
 dest=OUT/'CANDIDATE_2_NOT_APPROVED.blend';assert not dest.exists();bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=True)
 save('CANDIDATE_2_EDIT_LEDGER.json',dict(candidate=str(dest),scope=[w.A,w.B],paths=paths,samples=samples,authored_pose_checks=measurements,method='Second and final direct-animation design. Reverse middle/ring flex distribution, more-front D5 contact, ring lifts/uncurls after OFF rather than staying crossed. No solver, search or extra candidate. Same exact temporal support/exterior protection as candidate1.',purpose='Attempt distinct vertical routing of middle/ring and faster post-OFF ring clearance; retain R12 formal pose and timing.',candidate_count=2,original_other_actions_unchanged=OTHER_ACTIONS==s.protected_state(True)))
 print('CANDIDATE_2_AUTHORED_FINAL_ATTEMPT',flush=True)
