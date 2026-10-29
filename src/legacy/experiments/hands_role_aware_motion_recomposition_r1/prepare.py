from model import *
from persistence import atomic_json,atomic_record,load_record
import mido
from scipy.interpolate import PchipInterpolator
SOURCEDIR=ROOT/'experiments/hands_reusable_motion_representation_feasibility_r1'
I=read(SOURCEDIR/'INPUT_BINDINGS.json')
for p in [ROOT/'AGENTS.md',ROOT/'audits/hands_role_decomposed_motion_reuse_review_r1/FINAL_TECHNICAL_DECISION.md',SOURCEDIR/'MOTION_PRIMITIVE_DESIGN.md',SOURCEDIR/'RETARGET_AND_GEOMETRY_VALIDATION.md',SOURCEDIR/'FINAL_HUMAN_REVIEW.md',A2/'coordinated_motion.py',A2/'02_generate.py',ROOT/'audits/minuet_target_key_hand_position_planning_r1/02_generate.py']:
 p.read_bytes()
raw,_=load_record_from=None,None
with np.load(SOURCEDIR/'SOURCE_AUDIT_SAMPLES.npz',allow_pickle=False) as a:S={k:a[k] for k in a.files if k!='metadata_utf8'}
source=I['source'];target=I['target'];shift=target[0]['note_on']-source[0]['note_on']
assert all(abs(t['note_on']-s['note_on']-shift)<1e-10 and abs(t['note_off']-s['note_off']-shift)<1e-10 for s,t in zip(source,target))
events=read(C1/'PERFORMANCE_TIMELINE.json')['notes'];right=sorted([n for n in events if n['hand']=='R'],key=lambda n:n['note_on'])
midpath=ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid';mid=mido.MidiFile(str(midpath));tick=0;sec=0.;tempo=500000;active={};music=[]
for m in mido.merge_tracks(mid.tracks):
 sec+=mido.tick2second(m.time,mid.ticks_per_beat,tempo);tick+=m.time
 if m.type=='set_tempo':tempo=m.tempo
 if m.type=='note_on' and m.velocity>0:active[m.channel,m.note]=dict(channel=m.channel,midi_note=m.note,on_tick=tick,on_sec=sec,velocity=m.velocity)
 elif m.type=='note_off' or (m.type=='note_on' and m.velocity==0):
  n=active.pop((m.channel,m.note));n.update(off_tick=tick,off_sec=sec);music.append(n)
for n in I['source_context']+I['target_context']:
 hit=[x for x in music if all(x[k]==n[k] for k in ['channel','midi_note','on_tick','off_tick','velocity'])];assert len(hit)==1
 assert max(abs(hit[0]['on_sec']+.35-n['note_on']),abs(hit[0]['off_sec']+.35-n['note_off']))<1e-10
refinement=read(ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/STATIC_REFINEMENT_POLICY_R2.json')
B=np.array([refinement['joint_increment_bounds_deg']['THUMB' if j==0 else 'LONG'] for j in range(5)])
neutral=np.array(read(ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/SOLVED_STATIC_POSES_R2.json')['poses']['R1']['joint_increments_deg'])
pf=read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/RIG_PREFLIGHT.json')
primitive_xy=[];fractions=[];contacts=[]
for event in I['source_context']:
 ix=int(np.argmin(abs(S['times']-(event['note_on']+.035))));p=S['vertices'][ix,PADIDS[event['finger']-1]];key=KEYS[event['key_index']];pv=np.array(key['press_pivot']);local=rot(-S['key_angles'][ix,event['key_index']],key['press_axis'])@(p-pv)+pv;s=key['key_top_playable_surface'][0];loxy,hixy=inset(key);xy=np.clip(local[:2]*1000,loxy,hixy)
 primitive_xy.append(xy);fractions.append((xy-loxy)/(hixy-loxy))
 contacts.append(dict(source_event=event['note_id'],finger=event['finger'],preferred_key_local_xy_mm=xy,source_gap_mm=float((local[2]-s['z'])*1000)))
policy=dict(task='HANDS_ROLE_AWARE_MOTION_RECOMPOSITION_R1',representation='Event phase, single shared wrist-relative curve, RSSF-relative five-digit posture priors, actual active skin-pad contact features',source_count=1,target_count=1,source_witness_times=[1.7,2.0,2.0625],source_precheck_batches=1,source_local_variables=6,source_local_meaning='Four source active-digit engineering angles + two existing inset-key contact coordinates; all other digits and rig world fixed',source_local_max_nfev=45,local_contact_weight=6.,local_body_clearance_weight=2.,local_joint_prior=.055,local_xy_prior=.12,contact_horizontal_mm=.03,contact_vertical_abs_mm=3.,wrong_key_depth_mm=.5,nonregression_mm=.02,joint_bounds_deg=B,added_joint_velocity_deg_s=180,source_complete_collision_free_required=False,target_joint_trace_generation_input=False,target_boundary_conditions_only=True,numerical_limit_seconds=180,outer_parameters=[dict(name='shared_wrist_Y_mm',low=-8,high=8),dict(name='shared_wrist_Z_mm',low=-5,high=5),dict(name='first_active_PIP_deg',low=-4,high=4),dict(name='second_active_PIP_deg',low=-4,high=4),dict(name='middle_idle_MCP_deg',low=0,high=8),dict(name='index_idle_MCP_deg',low=0,high=8),dict(name='thumb_idle_CMC_deg',low=0,high=5),dict(name='first_release_MCP_deg',low=0,high=8)],outer_max_nfev=18,role_contact_max_nfev=12,no_seed_search=True,no_retuning=True,no_second_candidate=True)
atomic_json('POLICY.json',policy)
atomic_json('INPUT_BINDINGS.json',dict(source=source,target=target,source_context=I['source_context'],target_context=I['target_context'],right_events=right,all_events=events,scene=I['source_scene'],native_sha256=I['native_sha256'],phase_clock_shift_sec=shift,source_window_sec=[float(S['times'][0]),float(S['times'][-1])],target_window_sec=[float(S['times'][0]+shift),float(S['times'][-1]+shift)],base_xyz_m=pf['base_xyz_m'],static_root_base_matrix=pf['static_root_base_matrix'],full_root_rig_relation=pf['full_root_rig_relation'],neutral_q_deg=neutral))
atomic_record('SOURCE_FEATURES.npz',dict(times=S['times'],phase_times=S['times']-source[0]['note_on'],q_prior=S['qdeg'],wrist_relative_world=S['rig_world'],skin_pads=S['vertices'][:,PADIDS],key_angles=S['key_angles'],preferred_xy_mm=primitive_xy,preferred_xy_fraction=fractions),dict(record_type='ROLE_PRIMITIVE_FROM_SOURCE_ONLY',source_sha256=I['source_scene']['sha256'],source_contact_features=contacts,idle_raw_curves_may_not_be_copied_to_target=True,source_has_documented_geometry_defects=True,target_joint_samples=0))
# Independent FK, known contact and persistence checks BEFORE any solver call.
errors=[]
for t in policy['source_witness_times']:
 ix=int(np.argmin(abs(S['times']-t)));assert abs(S['times'][ix]-t)<1e-10
 V=native(S['qdeg'][ix],S['rig_world'][ix])[0];err=float(np.linalg.norm(V-S['vertices'][ix],axis=1).max()*1000);assert err<.01;errors.append(err)
event=source[-1];ix=int(np.argmin(abs(S['times']-2.0)));preferred=np.array(primitive_xy[2]);seed,low,high,fun,ids=local_fit_inputs(S['qdeg'][ix],S['rig_world'][ix],S['key_angles'][ix],event,preferred,policy);r=fun(seed);assert np.isfinite(r).all()
atomic_record('INPUT_GATE_KNOWN_STATE.npz',dict(x=seed,fun=r),dict(record_type='PRESERIALIZATION_TEST_NO_SOLVE'));back,_=load_record('INPUT_GATE_KNOWN_STATE.npz');assert np.array_equal(back['x'],seed)
atomic_json('INPUT_GATE.json',dict(pass_=True,full_source_native_LBS_errors_mm=errors,local_residual_finite=True,persistence_roundtrip=True,target_joint_trace_not_read=True,formal_solver_calls=0,policy_sha256=sha(O/'POLICY.json')))
for p in [Path(I['source_scene']['path']),midpath,ROOT/'AGENTS.md',ROOT/'production_spec/right_hand_product_baseline_r2/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2.blend']:
 READS[str(p)]=sha(p)
protect();print('FEATURE_EXTRACTION_AND_INPUT_GATE PASS; source only, three local witnesses locked')
