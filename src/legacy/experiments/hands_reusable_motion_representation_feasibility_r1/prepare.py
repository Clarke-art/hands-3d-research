from support import *
from persistence import atomic_json
sys.path.insert(0,str(OLD/'_deps'));sys.path.insert(0,str(A2))
import coordinated_motion as cm
import numpy as np,mido
HIST=ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance'
for p in [ROOT/'AGENTS.md',ROOT/'experiments/hands_p3_temporal_wrist_coordination_r2/FINAL_HUMAN_REVIEW.md',HIST/'RIGHT_HAND_OVERLAP_AND_BLACK_KEY_DIAGNOSIS.md',HIST/'R1_LOCAL_GEOMETRY.json',HIST/'R1_BLACK_SUMMARY.json',HIST/'WITNESS_SOURCE_PARITY_AND_CONTACT.json',ROOT/'audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/FINAL_ANSWERS.md',ROOT/'audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/SPATIAL_CONFLICT_ROOT_CAUSE_ANALYSIS.md',A2/'02_generate.py',A2/'GENERATION_POLICY.json',A2/'ENGINEERING_DIAGNOSTICS.json',C1/'R_approved_reference.npz']:
 p.read_bytes()
authority=read(ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement/HUMAN_AUTHORITY_RECEIPT.json')
tl=read(C1/'PERFORMANCE_TIMELINE.json');right=sorted([n for n in tl['notes'] if n['hand']=='R'],key=lambda n:n['note_on'])
# Event IDs are experiment selectors only, never rules in a motion generator.
source=[right[4],right[5]];target=[right[12],right[13]]
assert [n['finger'] for n in source]==[4,5] and [n['finger'] for n in target]==[4,5]
mid=mido.MidiFile(str(ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid'))
tick=0;sec=0.;tempo=500000;active={};music=[]
for m in mido.merge_tracks(mid.tracks):
 sec+=mido.tick2second(m.time,mid.ticks_per_beat,tempo);tick+=m.time
 if m.type=='set_tempo':tempo=m.tempo
 if m.type=='note_on' and m.velocity>0:active[m.channel,m.note]=dict(channel=m.channel,midi_note=m.note,on_tick=tick,on_sec=sec,velocity=m.velocity)
 elif m.type=='note_off' or (m.type=='note_on' and m.velocity==0):
  n=active.pop((m.channel,m.note));n.update(off_tick=tick,off_sec=sec);music.append(n)
shift=right[0]['note_on']-right[0]['source_on_sec'];checks=[]
for n in right[3:7]+right[11:15]:
 hit=[a for a in music if all(a[k]==n[k] for k in ['channel','midi_note','on_tick','off_tick','velocity'])];assert len(hit)==1
 err=max(abs(hit[0]['on_sec']+shift-n['note_on']),abs(hit[0]['off_sec']+shift-n['note_off']));assert err<1e-10
 checks.append(dict(**n,midi_clock_error_sec=err))
man=read(C1/'SCENE_MANIFEST.json');assert sha(man['path'])==man['sha256']==authority['source_candidate_sha256']
pf=read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/RIG_PREFLIGHT.json')
start=source[0]['note_on']-.18;end=source[-1]['note_off']+.07
uniform=np.arange(np.ceil(start*240),np.floor(end*240)+1)/240
phases=[n[p]+d for n in right[3:7] for p in ['note_on','note_off'] for d in [-.18,-.075,0,.0175,.035,.04,.07]]
times=np.unique(np.r_[start,end,uniform,phases]);times=times[(times>=start)&(times<=end)]
co=cm.EventCoordinator(right,cm.DEFAULT_POLICY)
policy=dict(task='HANDS_REUSABLE_MOTION_REPRESENTATION_FEASIBILITY_R1',source_event_ids=[n['note_id'] for n in source],target_event_ids=[n['note_id'] for n in target],representation_count=1,source_count=1,target_count=1,local_contact_correction_sets_max=1,dynamic_candidates_max=1,numerical_execution_limit_seconds=120,source_window_sec=[start,end],source_core_sec=[source[0]['note_on'],source[-1]['note_off']],source_audit_times=times,source_audit_sampling='240Hz + exact event/phase times, with preceding and following active notes',source_acceptance='All source core ACTIVE pad contacts must pass; real finger skin intersections or non-owned key penetration >0.5mm constitute source rejection. Context risks recorded separately. Overall Human acceptance is not a local defect waiver.',contact_horizontal_mm=.03,contact_vertical_abs_mm=3,key_depth_mm=.5,nonregression_mm=.02,added_joint_velocity_deg_sec=180,joint_bounds_deg=cm.B,root_low=co.state_low[:6],root_high=co.state_high[:6],decomposition_tolerance_deg=.002,source_failure_action='STOP; no donor substitution, motion primitive extraction, target retargeting, local IK, candidate or video',planned_representation='Event phase + key-frame-relative shared wrist residual + RSSF-relative five-digit posture curves; NOT IMPLEMENTED unless source gate passes',per_note_tables_prohibited=True,no_P3_B02_optimizer=True,no_external_motion_data=True)
atomic_json('POLICY.json',policy);atomic_json('POLICY_LOCK.json',dict(policy_sha256=sha(O/'POLICY.json'),locked_before_source_audit=True))
atomic_json('INPUT_BINDINGS.json',dict(source=source,target=target,source_context=right[3:7],target_context=right[11:15],right_events=right,all_events=tl['notes'],source_scene=man,native_sha256=pf['right_native_sha256'],human_authority=authority,formal_event_checks=checks,midi_clock_shift_sec=shift))
for p in [A2/'STAGE_A_R2_COORDINATED_RIGHT_DESIGN_ONLY.blend',ROOT/'production_spec/right_hand_product_baseline_r2/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2.blend']:
 READS[str(p)]=sha(p)
protect();print('ONE DONOR / ONE TARGET LOCKED; source gate first,',len(times),'temporal samples')
