from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;R1=P.parent/'piano_hand_four_pose_static_feasibility_r1';OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1';sys.path.insert(0,str(OLD/'_deps'))
import numpy as np
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
old=read(R1/'SOLVED_STATIC_POSES_R1.json')['poses'];new=read(P/'SOLVED_STATIC_POSES_R2.json')['poses'];oldclear=read(R1/'HAND_KEYBOARD_CLEARANCE_R1.json')['poses'];newclear=read(P/'HAND_KEYBOARD_CLEARANCE_R2.json')['poses'];oldgeo=read(R1/'STATIC_GEOMETRIC_MEASUREMENTS_R1.json');newgeo=read(P/'STATIC_GEOMETRIC_MEASUREMENTS_R2.json');policy=read(P/'STATIC_REFINEMENT_POLICY_R2.json');A=np.load(P/'evaluated_static_candidate.npz');B=np.load(R1/'evaluated_static_candidate.npz')
diff={}
for pose in new:
 p=old[pose];q=new[pose];s=q['hand'];Rold=np.array(p['root_rotation_matrix']);Rnew=np.array(q['root_rotation_matrix']);deltaR=float(np.degrees(np.arccos(np.clip((np.trace(Rold.T@Rnew)-1)/2,-1,1))));padnew=A[pose+'_pads'];padold=B[pose+'_pads'];active=q['task']['active_finger']
 bounds=[]
 for j,d in enumerate(['THUMB','INDEX','MIDDLE','RING','LITTLE']):
  typ='THUMB' if j==0 else 'LEFT_IDLE_'+d if s=='L' and j in [1,2,3] else 'LONG';lo,hi=np.array(policy['joint_increment_bounds_deg'][typ]);ang=np.array(q['joint_increments_deg'][j]);bounds.append({'digit':d,'lower_deg':lo.tolist(),'upper_deg':hi.tolist(),'near_lower_axes':np.flatnonzero(abs(ang-lo)<.05).tolist(),'near_upper_axes':np.flatnonzero(abs(ang-hi)<.05).tolist()})
 diff[pose]={'root_R1_mm':(np.array(p['root_xyz_m'])*1000).tolist(),'root_R2_mm':(np.array(q['root_xyz_m'])*1000).tolist(),'root_delta_from_R1_mm':((np.array(q['root_xyz_m'])-p['root_xyz_m'])*1000).tolist(),'root_rotation_delta_from_R1_deg':deltaR,'yaw_pitch_roll_R1_deg':p['root_yaw_pitch_roll_deg'],'yaw_pitch_roll_R2_deg':q['root_yaw_pitch_roll_deg'],'joint_R1_deg':p['joint_increments_deg'],'joint_R2_deg':q['joint_increments_deg'],'joint_delta_deg':(np.array(q['joint_increments_deg'])-p['joint_increments_deg']).tolist(),'all_pad_xyz_delta_from_R1_mm':((padnew-padold)*1000).tolist(),'active_contact_point_delta_from_R1_mm':((padnew[active-1]-padold[active-1])*1000).tolist() if active is not None else None,'joint_bound_proximity_R2':bounds,'original_contact_tolerances_unchanged':True}
left=read(P/'LEFT_OCTAVE_REFINEMENT_R2.json');left.pop('solver_bound_saturation',None);left.pop('bound_saturation_meaning',None)
left['Human_R1_naturalness']='NOT_APPROVED; too straight/splayed/tense';left['refinement_delta']={p:diff[p] for p in ['L1','L2']};left['idle_tip_pair_distances_mm']={p:{version:[float(np.linalg.norm(arr[p+'_pads'][j]-arr[p+'_pads'][j+1])*1000) for j in [1,2]] for version,arr in [('R1',B),('R2',A)]} for p in ['L1','L2']};left['left_idle_no_fake_home_targets']=True;left['R2_bound_proximity']={p:diff[p]['joint_bound_proximity_R2'] for p in ['L1','L2']};left['same_reasonable_octave_configuration']='PENDING_MATCHED_VIEW_REVIEW';left['sequence_feasibility']='UNPROVEN_NO_TRANSITION_GENERATED';dump('LEFT_OCTAVE_REFINEMENT_R2.json',left)
right=read(P/'RIGHT_NEIGHBOR_KEY_CLEARANCE_R2.json');right['refinement_delta']={p:diff[p] for p in ['R1','R2']};right['neighbor_before_after']={}
for pose in ['R1','R2']:
 right['neighbor_before_after'][pose]={}
 for midi in [75,80]:
  before=next((x for x in oldclear[pose]['key_intersections'] if x['midi']==midi),None);after=next((x for x in newclear[pose]['key_intersections'] if x['midi']==midi),None);right['neighbor_before_after'][pose][str(midi)]={'note':'D#5' if midi==75 else 'G#5','R1_vertices':before['vertices'] if before else 0,'R1_max_depth_mm':before['max_depth_mm'] if before else 0,'R2_vertices':after['vertices'] if after else 0,'R2_max_depth_mm':after['max_depth_mm'] if after else 0,'greater_than3mm_screen_zeroed':after is None}
 right['neighbor_before_after'][pose]['all_new_key_intersections']=newclear[pose]['key_intersections'];right['neighbor_before_after'][pose]['no_new_neighbor_interference_screen']=not bool(newclear[pose]['key_intersections'])
right['naturalness']='PENDING_MATCHED_VIEW_REVIEW';dump('RIGHT_NEIGHBOR_KEY_CLEARANCE_R2.json',right)
dump('BASELINE_CANDIDATE_COMPARISON_R2.json',{'pose_deltas':diff,'baseline_R1_human_approval':False,'candidate_R2_human_approval':False,'same_camera_and_scale':True,'material_unchanged':True,'joint_bounds_are_engineering_not_physiology':True})
print(json.dumps({'left_idle_tip_gaps':left['idle_tip_pair_distances_mm'],'right_neighbor':right['neighbor_before_after']},indent=2))
