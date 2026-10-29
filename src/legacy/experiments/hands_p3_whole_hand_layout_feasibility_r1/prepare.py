from support import *
sys.path.insert(0,str(OLD/'_deps'));sys.path.insert(0,str(A2))
import coordinated_motion as cm
import numpy as np, mido
tl=read(C1/'PERFORMANCE_TIMELINE.json');orig=sorted([n for n in tl['notes'] if n['hand']=='R'],key=lambda n:n['note_on'])
candidates=read(PREV/'CANDIDATES.json');p3=next(n for n in candidates['candidates'] if n['id']=='P3')['fingers']
assert [i for i,(a,b) in enumerate(zip([n['finger'] for n in orig],p3)) if a!=b]==[9,10]
assert p3[8:14]==[5,1,2,3,4,5]
midpath=ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid'
mid=mido.MidiFile(str(midpath));tick=0;sec=0.;tempo=500000;active={};music=[]
for m in mido.merge_tracks(mid.tracks):
 sec+=mido.tick2second(m.time,mid.ticks_per_beat,tempo);tick+=m.time
 if m.type=='set_tempo':tempo=m.tempo
 if m.type=='note_on' and m.velocity>0:active[m.channel,m.note]=dict(channel=m.channel,midi_note=m.note,on_tick=tick,on_sec=sec,velocity=m.velocity)
 elif m.type=='note_off' or (m.type=='note_on' and m.velocity==0):
  n=active.pop((m.channel,m.note));n.update(off_tick=tick,off_sec=sec);music.append(n)
shift=orig[0]['note_on']-orig[0]['source_on_sec'];checks=[]
for n in orig[7:15]:
 matches=[a for a in music if all(a[k]==n[k] for k in ['channel','midi_note','on_tick','off_tick','velocity'])];assert len(matches)==1
 a=matches[0];err=max(abs(a['on_sec']+shift-n['note_on']),abs(a['off_sec']+shift-n['note_off']));assert err<1e-10
 checks.append(dict(**n,p3_finger=p3[int(n['note_id'][1:])],midi_clock_error_sec=err))
dump('EVENT_CONTEXT.json',dict(ppq=mid.ticks_per_beat,presentation_shift_sec=shift,events=checks,original_timing_unchanged=True))
events=[dict(n,finger=p3[i]) for i,n in enumerate(orig)]
origco=cm.EventCoordinator(orig,cm.DEFAULT_POLICY);co=cm.EventCoordinator(events,cm.DEFAULT_POLICY)
manifest=read(C1/'SCENE_MANIFEST.json');assert sha(Path(manifest['path']))==manifest['sha256']
critical=[C1/'STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY.blend',A2/'STAGE_A_R2_COORDINATED_RIGHT_DESIGN_ONLY.blend',ROOT/'audits/minuet_stage_b_r3_budget_policy_candidate_recovery_r1/STAGE_B_R3_RECOVERED_CONTACT_DESIGN_ONLY.blend',ROOT/'production_spec/right_hand_product_baseline_r2/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2.blend',ROOT/'AGENTS.md']
for p in critical:READS[str(p)]=sha(p)
pf=read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/RIG_PREFLIGHT.json')
assert np.max(np.abs(cm.BASE-pf['base_xyz_m']))<1e-9
times=[orig[8]['note_on']+.035,orig[9]['note_on']-.18,orig[9]['note_on']-.075,orig[9]['note_on'],orig[9]['note_on']+.035,orig[10]['note_on'],orig[10]['note_on']+.035,orig[11]['note_on']+.035,orig[12]['note_on']+.035,orig[13]['note_on']+.035]
labels=['R08_DEPRESSED','R08_PREP_START','R08_THUMB_NEAR','R09_ON_HANDOFF','R09_DEPRESSED','R10_ON_HANDOFF','R10_DEPRESSED','R11_DEPRESSED','R12_DEPRESSED','R13_DEPRESSED']
policy=dict(task='HANDS_P3_WHOLE_HAND_LAYOUT_FEASIBILITY_R1',batch_limit=1,solver_calls=1,max_nfev=45,solver_wall_cap_seconds=65,total_execution_cap_seconds=180,root_common_across_all_10_phases=True,root_bounds=origco.state_low[:6].tolist()+origco.state_high[:6].tolist(),root_low=origco.state_low[:6],root_high=origco.state_high[:6],joint_bounds_deg=cm.B,source='Original A2/C1 EventCoordinator bounds using ORIGINAL fingers; no P3-derived domain enlargement',contact_horizontal_mm=.03,contact_vertical_abs_mm=3,new_key_depth_mm=.5,nonregression_mm=.02,added_joint_velocity_deg_sec=180,phase_times_sec=times,phase_labels=labels,one_deterministic_seed='median original C1 root; original C1 joint poses at same times',contact_locations='A2 original inset surface bounds, six event coordinates shared across phases',no_trajectory=True,no_actions=True,no_domain_relaxation=True,geometry_proxy='Existing A2 pad box clearance and joint center prior; native frozen weighted skin pad for contacts',naturalness='A2 neutral + same-phase original C1 joint prior; exact original tighter bounds',temporal='Sparse phase soft velocity from original A2; endpoint lower bound on added correction; no path certificate')
dump('POLICY.json',policy);dump('INPUT_BINDINGS.json',dict(original_events=orig,p3_events=events,source_scene=manifest,static_root_base_matrix=pf['static_root_base_matrix'],native_sha256=pf['right_native_sha256']))
dump('POLICY_LOCK.json',dict(policy_sha256=sha(O/'POLICY.json'),locked_before_solve=True))
protect();print('PREPARED',len(times),'phases; original musical events exact; original narrow bounds retained')
