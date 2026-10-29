import exit_session as w
from geometry import *
import geometry as g
def point(f,t):return next(k for k in f.keyframe_points if abs(k.co.x-(1+60*t))<1e-4)
def flatten(k,left=True,right=True):
 k.handle_left_type='FREE';k.handle_right_type='FREE'
 if left:k.handle_left.y=k.co.y
 if right:k.handle_right.y=k.co.y
def build(number=1):
 assert number in [1,2]
 rig=w.rig;sc=w.sc
 old=w.OLD_ACTION;rig.animation_data.action=old
 action=old.copy();action.name=f'R2_EXIT_LOCAL_{number}_NOT_APPROVED';rig.animation_data.action=action
 source=bpy.data.actions.get('DESIGN_ONLY_STAGE_C_R_rig')
 if source is None:
  # Read only the original C1 Action datablock, never its scene or assets.
  with bpy.data.libraries.load(str(safe(SOURCE)),link=False) as (data_from,data_to):
   assert 'DESIGN_ONLY_STAGE_C_R_rig' in data_from.actions
   data_to.actions=['DESIGN_ONLY_STAGE_C_R_rig']
  source=data_to.actions[0]
 orig={(f.data_path,f.array_index):f for f in s.curves(source)}
 before={(f.data_path,f.array_index):f for f in s.curves(old)}
 changed=[]
 # Actual direct wrist translation: local axis conversion of world -X 1mm.
 c.settime(sc,2.92);b=rig.pose.bones['WRIST_R'];M=<REDACTED_EMAIL>
 loc0=rig.convert_space(pose_bone=b,matrix=M,from_space='WORLD',to_space='LOCAL').translation
 loc1=rig.convert_space(pose_bone=b,matrix=Matrix.Translation(Vector((-.001,0,0)))@M,from_space='WORLD',to_space='LOCAL').translation
 locY=rig.convert_space(pose_bone=b,matrix=Matrix.Translation(Vector((0,-.001,0)))@M,from_space='WORLD',to_space='LOCAL').translation
 delta=np.array(loc1-loc0);deltaY=np.array(locY-loc0)
 times=[2.68,2.78,2.86,2.921426,3.02,3.12]
 offsets=[0,.30,1.10,1.10,0,0] # millimetres world -X; no vertical lift.
 back=[0,0,0,0,0,0]
 if number==2:
  # Second and final local design: diagonally retreat from the thumb/A4
  # corner, retain small rearward translation through the finger handoff.
  offsets=[0,.20,.80,.80,0,0]
  back=[0,.30,1.20,1.20,1.20,0]
 offset_vectors=[delta*x+deltaY*y for x,y in zip(offsets,back)]
 for f in s.curves(action):
  path=f.data_path
  if path=='pose.bones["WRIST_R"].location':
   for i,t in enumerate(times):
    k=point(f,t);d=offset_vectors[i][f.array_index]
    left=np.array(k.handle_left);right=np.array(k.handle_right);co=np.array(k.co)
    if i==0 or i>=len(times)-2 or (i>0 and np.array_equal(offset_vectors[i-1],offset_vectors[i])) or (i<len(times)-1 and np.array_equal(offset_vectors[i+1],offset_vectors[i])):slope=0.
    else:slope=(offset_vectors[i+1][f.array_index]-offset_vectors[i-1][f.array_index])/(60*(times[i+1]-times[i-1]))
    k.co.y+=float(d);k.handle_left=(left[0],left[1]+d+slope*(left[0]-co[0]));k.handle_right=(right[0],right[1]+d+slope*(right[0]-co[0]))
   changed.append((path,f.array_index))
  if 'WRIST_R' in path:
   for t in [3.02,3.12]:flatten(point(f,t))
   if (path,f.array_index) not in changed:changed.append((path,f.array_index))
  if any(f'"{d}_{j}_R"' in path for d in ['INDEX','MIDDLE'] for j in ['MCP','PIP','DIP']):
   # Flat plateau retains authored pose and eliminates unintended reversal.
   for t in [2.86,2.921426]:flatten(point(f,t))
   join=1+60*3.02;prev=1+60*2.921426;of=orig[path,f.array_index]
   value=of.evaluate(join);slope=(of.evaluate(join+.001)-of.evaluate(join))/.001
   for ix in reversed(range(len(f.keyframe_points))):
    if f.keyframe_points[ix].co.x>=join-1e-4:f.keyframe_points.remove(f.keyframe_points[ix],fast=True)
   for ok in of.keyframe_points:
    if ok.co.x>join+1e-4:
     k=f.keyframe_points.insert(ok.co.x,ok.co.y,options={'FAST'});k.interpolation=ok.interpolation;k.handle_left_type=ok.handle_left_type;k.handle_right_type=ok.handle_right_type
   k=f.keyframe_points.insert(join,value,options={'FAST'});f.update();k=point(f,3.02)
   k.interpolation='LINEAR';k.handle_left_type='FREE';k.handle_right_type='FREE'
   k.handle_left=(join-(join-prev)/3,value-slope*(join-prev)/3)
   k.handle_right=(join+.1,value+slope*.1)
   changed.append((path,f.array_index))
  f.update()
 for f in s.curves(action):
  of=before[f.data_path,f.array_index]
  for t in [0.,2.1,2.45,2.6,2.68,3.1201,3.35,5.5]:
   assert abs(f.evaluate(1+60*t)-of.evaluate(1+60*t))<1e-6,(f.data_path,t)
 assert w.OTHER_ACTIONS==s.protected_state(True)
 assert w.NATIVE=={a:c.digest(c.native(o,r)) for a,o,r in [('R',w.mesh,rig),('L',w.left,w.lrig)]}
 c.settime(sc,2.6);sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']]
 dest=OUT/f'EXIT_CANDIDATE_{number}_NOT_APPROVED.blend';assert not dest.exists();bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=True)
 save(f'CANDIDATE_{number}_EDIT_LEDGER.json',dict(candidate=str(dest),sha256=sha(dest),edited_channels=changed,scope=[2.68,3.12],world_minus_X_offsets_mm=dict(zip(map(str,times),offsets)),world_minus_Y_offsets_mm=dict(zip(map(str,times),back)),local_delta_per_mm=delta,local_delta_back_per_mm=deltaY,return_to_original_C1_finger_curves_at=3.02,plateau_handles_flat_at=[2.86,2.921426],wrist_exit_handles_flat_at=[3.02,3.12],earlier_curves_unchanged=True,notes_and_other_actions_unchanged=True,native_unchanged=True))
 print('R2_CANDIDATE_BUILT',number,flush=True)
