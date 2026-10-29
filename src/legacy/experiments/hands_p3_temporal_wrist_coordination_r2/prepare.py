from support import *
from persistence import atomic_json
sys.path.insert(0,str(OLD/'_deps'));sys.path.insert(0,str(A2))
import coordinated_motion as cm
import numpy as np,mido
assert read(O/'RESULT_PERSISTENCE_GATE.json')['RESULT_PERSISTENCE_GATE']=='PASS'
R1=ROOT/'experiments/hands_p3_whole_hand_layout_feasibility_r1'
for name in ['P3_LAYOUT_FEASIBILITY.md','TEMPORAL_AND_COLLISION_RISK.md','FINAL_RECOMMENDATION.md','solve.log','solve.py','POLICY.json','INPUT_BINDINGS.json','EXPORT_FAILURE_RECEIPT.json','INITIAL_SEED_DIAGNOSTICS.json','BLENDER_STATIC_DIAGNOSTICS.json','PROTECTION_CHECK.json']:
 p=R1/name;p.read_bytes()
orig=sorted([n for n in read(C1/'PERFORMANCE_TIMELINE.json')['notes'] if n['hand']=='R'],key=lambda n:n['note_on'])
previous=read(PREV/'CANDIDATES.json');fs=next(n for n in previous['candidates'] if n['id']=='P3')['fingers'];assert fs[8:14]==[5,1,2,3,4,5]
assert [i for i,n in enumerate(orig) if n['finger']!=fs[i]]==[9,10]
events=[dict(n,finger=fs[i]) for i,n in enumerate(orig)]
midpath=ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid'
mid=mido.MidiFile(str(midpath));tick=0;sec=0.;tempo=500000;active={};music=[]
for m in mido.merge_tracks(mid.tracks):
 sec+=mido.tick2second(m.time,mid.ticks_per_beat,tempo);tick+=m.time
 if m.type=='set_tempo':tempo=m.tempo
 if m.type=='note_on' and m.velocity>0:active[m.channel,m.note]=dict(channel=m.channel,midi_note=m.note,on_tick=tick,on_sec=sec,velocity=m.velocity)
 elif m.type=='note_off' or (m.type=='note_on' and m.velocity==0):
  n=active.pop((m.channel,m.note));n.update(off_tick=tick,off_sec=sec);music.append(n)
shift=orig[0]['note_on']-orig[0]['source_on_sec'];rows=[]
for n in orig[7:15]:
 hit=[a for a in music if all(a[k]==n[k] for k in ['channel','midi_note','on_tick','off_tick','velocity'])];assert len(hit)==1
 err=max(abs(hit[0]['on_sec']+shift-n['note_on']),abs(hit[0]['off_sec']+shift-n['note_off']));assert err<1e-10
 rows.append(dict(**n,p3_finger=fs[int(n['note_id'][1:])],midi_clock_error_sec=err))
atomic_json('EVENT_CONTEXT.json',dict(ppq=mid.ticks_per_beat,clock_shift_sec=shift,events=rows,formal_event_identity_unchanged=True))
man=read(C1/'SCENE_MANIFEST.json');assert sha(man['path'])==man['sha256']
pf=read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/RIG_PREFLIGHT.json')
co0=cm.EventCoordinator(orig,cm.DEFAULT_POLICY)
start=orig[8]['note_on']-.18;end=orig[14]['note_on']+.18
priority=np.unique(np.r_[start,end,[n['note_on']+d for n in orig[8:15] for d in [0,.035]],[n['note_off']+.04 for n in orig[7:14]]])
support=list(priority[(priority>=start)&(priority<=end)])
# Existing A2 event conditioning: prep nodes only if >=4ms from priority nodes.
for t in sorted([n['note_on']+d for n in orig[8:15] for d in [-.18,-.075]]):
 if start<t<end and min(abs(np.array(support)-t))>=.004:support.append(float(t))
controls=np.array(sorted(support));evaluation=np.unique(np.r_[controls,(controls[:-1]+controls[1:])/2])
# A finite 60Hz readback plus exact phases, no extra optimization nodes.
check=np.unique(np.r_[evaluation,np.arange(np.ceil(start*60),np.floor(end*60)+1)/60])
policy=dict(task='HANDS_P3_TEMPORAL_WRIST_COORDINATION_R2',scheme_count=1,formal_solver_calls=1,seeds=1,max_nfev=35,solver_internal_seconds=74,wrapper_solver_cap_seconds=85,total_execution_cap_seconds=180,source_method='Original A2 event support / sparse bounded least_squares / componentwise PCHIP, temporal velocity and acceleration terms',control_times_sec=controls,evaluation_times_sec=evaluation,blender_check_times_sec=check,scope_start_sec=start,scope_end_sec=end,state_dimensions=26,one_shared_root_per_time=True,root_state_per_control_time=True,first_last_states='Fixed original C1 actual full hand/root state at the exact boundaries',root_low=co0.state_low[:6],root_high=co0.state_high[:6],joint_bounds_deg=cm.B,root_domain_source='Original A2/C1 domain computed using ORIGINAL full fingering, unchanged',contact_locations='Six R08-R13 event XY pairs within existing A2 inset surfaces; R07/R14 source marker XY fixed',seed='One original C1 time-varying root and all five source joint poses; no fixed 8.70mm offset and no static seed solves',contact_horizontal_mm=.03,contact_vertical_abs_mm=3,new_key_depth_mm=.5,nonregression_mm=.02,added_joint_velocity_deg_sec=180,decomposition_tolerance_deg=.002,weights=dict(contact=6.,prepare=4.,clearance=2.,joint_neutral_prior=.055,joint_C1_prior=.055,root_rotation_prior=.20,root_C1_prior=[.015,.035,.06],velocity=[.010,.018,.028,.040]+[.020]*20,acceleration=[.00032,.00048,.00072,.00060]+[.00070]*20,added_velocity_excess=.020,contact_xy_prior=.12),geometry='Frozen native weighted skin pads + original A2 pad box and DIP/proximal-center clearance; independent full real-skin/key validation after solve',naturalness='Original narrow RSSF-relative engineering domain, original C1 and neutral priors; Human naturalness not certified',no_actions=True,no_blends=True,no_video=True,continuous_validation='Finite native readback plus analytic PCHIP parameter and velocity checks; never claim complete dynamic validation')
atomic_json('POLICY.json',policy)
atomic_json('INPUT_BINDINGS.json',dict(original_events=orig,p3_events=events,source_scene=man,static_root_base_matrix=pf['static_root_base_matrix'],full_root_rig_relation=pf['full_root_rig_relation'],base_xyz_m=pf['base_xyz_m'],native_sha256=pf['right_native_sha256']))
for p in [ROOT/'AGENTS.md',A2/'STAGE_A_R2_COORDINATED_RIGHT_DESIGN_ONLY.blend',A2/'GENERATION_POLICY.json',A2/'02_generate.py',ROOT/'audits/minuet_stage_b_r3_budget_policy_candidate_recovery_r1/STAGE_B_R3_RECOVERED_CONTACT_DESIGN_ONLY.blend',ROOT/'production_spec/right_hand_product_baseline_r2/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2.blend']:
 READS[str(p)]=sha(p)
protect();print('PREPARED',len(controls),'controls',len(evaluation),'residual times',len(check),'finite Blender checks; P3 only')
