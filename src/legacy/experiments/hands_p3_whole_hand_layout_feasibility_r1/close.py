from support import *
sys.path.insert(0,str(OLD/'_deps'));import numpy as np
I=read(O/'INPUT_BINDINGS.json');P=read(O/'POLICY.json');D=read(O/'BLENDER_STATIC_DIAGNOSTICS.json');A=dict(np.load(O/'INITIAL_SEED_LAYOUTS.npz'))
times=A['times'];q=A['states'][:,6:].reshape(-1,5,4);delta=q-A['qsource'];sr=A['source_roots'];r=A['states'][0,:6]
pf=read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/RIG_PREFLIGHT.json');base=np.array(pf['base_xyz_m']);static=np.array(I['static_root_base_matrix']);relation=np.array(pf['full_root_rig_relation'])
from scipy.spatial.transform import Rotation
def root_of_world(world):
 C=np.array(world)@np.linalg.inv(relation)@np.linalg.inv(static);pos=C[:3,:3]@base+C[:3,3]
 return np.r_[(pos-base)*1000,Rotation.from_matrix(C[:3,:3]).as_euler('xyz',degrees=True)]
steps=[]
for k in range(len(times)-1):
 dt=times[k+1]-times[k];dq=float(np.max(abs(delta[k+1]-delta[k])));dr=sr[k+1]-sr[k]
 steps.append(dict(start=P['phase_labels'][k],end=P['phase_labels'][k+1],available_sec=float(dt),same_initial_seed_added_joint_delta_deg=dq,conditional_min_sec_at180_added_deg_s=dq/180,source_C1_root_endpoint_translation_mm=float(np.linalg.norm(dr[:3])),source_C1_root_endpoint_mean_speed_mm_s=float(np.linalg.norm(dr[:3]))/dt,source_C1_max_root_rotation_component_delta_deg=float(abs(dr[3:]).max())))
boundary=[]
for c0 in D['boundary_context']:
 root=root_of_world(c0['rig_world']);boundary.append(dict(event=c0['event'],time=c0['time'],C1_root_xyz_mm=(base+root[:3]/1000)*1000,initial_seed_translation_distance_mm=float(np.linalg.norm(r[:3]-root[:3])),initial_seed_max_rotation_component_distance_deg=float(abs(r[3:]-root[3:]).max())))
jointchange=float(np.max(abs(delta)))
notes=I['p3_events'];n08=notes[8];n09=notes[9];n10=notes[10];n13=notes[13];n14=notes[14]
timing=dict(R08_hold_sec=n08['note_off']-n08['note_on'],R08_press_sec=.035,R08_after_press_available_sec=n08['note_off']-n08['note_on']-.035,C1_prepare_sec=.18,C1_near_approach_sec=.075,C1_release_follow_sec=.04,R08_OFF_to_R09_ON_sec=n09['note_on']-n08['note_off'],R09_OFF_to_R10_ON_sec=n10['note_on']-n09['note_off'],R09_hold_sec=n09['note_off']-n09['note_on'],R10_R11_R12_hold_sec=[n['note_off']-n['note_on'] for n in notes[10:13]],R13_hold_sec=n13['note_off']-n13['note_on'],R13_OFF_to_R14_ON_sec=n14['note_on']-n13['note_off'])
dump('TEMPORAL_EVIDENCE.json',dict(clock=timing,source_root_low=P['root_low'],source_root_high=P['root_high'],initial_seed_root_parameter=r,root_xyz_mm=(base+r[:3]/1000)*1000,source_phase_roots_A2_parameters=sr,initial_seed_vs_C1_root_translation_mm=np.linalg.norm(sr[:,:3]-r[:3],axis=1),initial_seed_max_joint_change_from_source_deg=jointchange,phase_endpoint_checks=steps,boundary_context=boundary,hard_added_joint_velocity_deg_sec=180,root_hard_velocity_limit='NOT_REGISTERED_IN_A2_POLICY; soft regularizers and observed reference speeds are not hard caps',valid_path_endpoint_lower_bound_available=False,reason='No accepted terminal layout or legal preparation interval was retained; same initial seed violates contacts and geometry'))
summary=[]
for old,new in zip(D['source'],D['initial_seed']):
 active=[c for c in new['contacts'] if c['phase']=='HOLD_OR_PRESS'];release=[c for c in new['contacts'] if c['phase']=='RELEASE_FOLLOW']
 summary.append(dict(label=new['label'],active_contacts=active,release_follow_diagnostics=release,skin_pairs=sum(new['finger_intersection_pairs'].values()),source_skin_pairs=sum(old['finger_intersection_pairs'].values()),source_wrong_key_depth_mm=old['max_wrong_or_inactive_depth_mm'],initial_wrong_key_depth_mm=new['max_wrong_or_inactive_depth_mm'],new_pointwise_depth_regressions=new['new_vertex_depth_regression_count'],black_key_witnesses=[w for w in new['wrong_or_inactive_key_depth_witnesses'] if w['color']=='BLACK'],max_LBS_parity_mm=new['native_LBS_pad_parity_mm']))
dump('STATIC_COMPARISON_SUMMARY.json',dict(rows=summary,initial_seed_only=True,optimizer_terminal_not_available=True))
protect();before=read(O/'PROTECTED_BEFORE.json');after={p:sha(p) for p in before};changed=[p for p in before if before[p]!=after[p]]
dump('PROTECTION_CHECK.json',dict(referenced_files_checked=len(before),all_unchanged=not changed,changed=changed,before=before,after=after,independent_piano_access='FORBIDDEN; Python audit hook rejects access; C1 embedded 88-key scene only, no linked libraries',new_actions=0,new_blends=0,new_videos=0,formal_fingering_unchanged=True,historical_concurrent_FAIL='Retained; narrow current SHA check does not supersede historical FAIL',path_migration=0,solver_attempts=1,solver_restarts=0))
assert not changed
dump('FINAL_STATUS.json',dict(task='HANDS_P3_WHOLE_HAND_LAYOUT_FEASIBILITY_R1',status='INCONCLUSIVE',reason='Sole optimizer terminal state lost at post-solve export; retained initial shared-root layout fails contact/geometry. No legal coordinated layout or transition certified.',dynamic_authorization_recommended=False,global_unreachability_claim=False,continuous_performance_pass=False,optimizer_calls=1,optimizer_restarts=0,next_stage_started=False,stop='STOP — HUMAN REVIEW'))
print('ROOT_INITIAL_MM',((base+r[:3]/1000)*1000).tolist());print('ROOT_ROTATION_DEG',r[3:].tolist());print('INITIAL_JOINT_CHANGE_FROM_C1_DEG',jointchange);print('BOUNDARIES',boundary);print('PROTECTED',len(before),'unchanged');print('STATUS INCONCLUSIVE')
