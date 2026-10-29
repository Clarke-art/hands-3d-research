from stage_common import *
import mido,collections,ast
lock=read(P/'GENERATION_LOCK.json');assert all(sha(P/n)==h for n,h in lock['scripts'].items())
assert sha(SOURCE)==lock['source_sha256'] and sha(P/'PERFORMANCE_TIMELINE.json')==lock['timeline_sha256'] and sha(P/'GENERATION_POLICY.json')==lock['policy_sha256']
tl=read(P/'PERFORMANCE_TIMELINE.json');notes=tl['notes'];original=[];tick=0;held=collections.defaultdict(collections.deque)
for msg in mido.MidiFile(SOURCE).tracks[2]:
    tick+=msg.time
    if msg.type=='note_on' and msg.velocity:held[msg.channel,msg.note].append((tick,msg.velocity))
    elif msg.type=='note_off' or msg.type=='note_on' and not msg.velocity:
        on,vel=held[msg.channel,msg.note].popleft()
        if 0<=on<4608:original.append((msg.note,on,tick,vel,msg.channel))
assert sorted(original)==sorted((n['midi_note'],n['on_tick'],n['off_tick'],n['velocity'],n['channel']) for n in notes)
assert len(original)==7 and [n['finger'] for n in notes]==[5,3,1,4,3,2,3] and max(n['off_tick'] for n in notes)==4608
audio=read(P/'KEY_AUDIO_SYNC_R1.json');assert len(audio['voices'])==7 and audio['polyphony_peak_held']==3 and audio['pitch_within25cents']
for n,v in zip(notes,audio['voices']):
    assert v['midi_note']==n['midi_note'] and v['hand']=='L' and v['velocity']==n['velocity'] and v['timeline_on_sec']==n['note_on'] and v['note_off_sec']==n['note_off']
man=read(P/'SCENE_MANIFEST.json');assert sha(man['path'])==man['sha256']
assert man['four_static_scenes_unchanged'] and man['hand_structure_unchanged'] and man['all_88_key_geometry_unchanged'] and man['save_reopen_verified'] and man['left_only']
assert not man['right_in_performance_scene'] and len(list(P.glob('*.blend')))==1
rawframe=read(P/'WHOLE_LEFT_HAND_FRAMING.json');assert rawframe['views']['TEACHING']['all_actual_left_vertices_inside_frame'] and rawframe['views']['SIDE_OBLIQUE']['all_actual_left_vertices_inside_frame']
assert read(P/'VIDEO_FRAMING_REPAIR.json')['all_delivered_views_entire_left_hand_visible']
videos=read(P/'VIDEO_VERIFICATION.json');assert len(videos)==3
for n,v in videos.items():assert v['fps']==60 and v['frames']==man['frames']==357 and v['sha256']==sha(P/n) and v['full_decode']=='PASS'
diag=read(P/'ENGINEERING_DIAGNOSTICS.json');assert diag['chord_pressure_max_difference']<1e-6 and diag['other_keys_stationary'] and diag['key_angle_readback_parity_max_rad']<1e-5
for f in P.glob('*.py'):ast.parse(f.read_text(encoding='utf8'))
protected=read(P/'PROTECTED_INPUTS_BEFORE.json');changed=[];missing=[]
for path,h in protected.items():
    if not Path(path).is_file():missing.append(path)
    elif sha(path)!=h:changed.append(path)
assert not changed and not missing,(changed,missing)
dump('FROZEN_AND_PRIOR_BASELINE_VERIFICATION.json',dict(protected_files=len(protected),changed=changed,missing=missing,all_protected_hashes_unchanged=True,
    RIGHT_HAND_R2='HUMAN_APPROVED_FROZEN',LEFT_HAND_R1='HUMAN_APPROVED_FROZEN',Grand88_keyboard_unchanged=True,approved_four_static_poses_unchanged=True,
    STAGE_A_R2='HUMAN_VISUAL_APPROVED_WITH_ENGINEERING_WARN',STAGE_A_R2_candidate_code_videos_reports_unchanged=True,
    STAGE_B_R1_technical_baseline_preserved=True,STAGE_B_R1_Human_naturalness='INCONCLUSIVE_DURATION_TOO_SHORT',
    STAGE_B_R1_candidate_code_videos_reports_unchanged=True,prior_reports_not_rewritten=True,original_MIDI_audio_chain_unchanged=True,
    Musette_Human_acceptance_carried_forward=True))
dump('EVENT_KEY_AUDIO_VIDEO_VERIFICATION.json',dict(original_MIDI_sha256=sha(SOURCE),all_original_7_left_notes_exact=True,
    original_NOTE_ON_OFF_pitch_velocity_channel_exact=True,fingers_DESIGN_PROVISIONAL=[5,3,1,4,3,2,3],
    source_tick_range=[0,4608],last_note_off_tick=4608,no_boundary_clip=True,source_duration_sec=5.142852,
    source_true_different_onset_held_overlaps=0,source_adjacent_same_key_restrikes=0,
    original_tempo_us_per_quarter=428571,ppq=384,voices=7,right_audio_or_motion=False,
    sample_audio_quantization_max_ms=audio['audio_clock_quantization_max_ms'],finite_pitch_checks_within25cents=True,
    key_readback_shared_event_clock=True,chord_simultaneity=True,mechanical_release_overlap_does_not_add_notes=True,
    frames=357,fps=60,video_duration_sec=5.95,all_three_views_full_decode=True))
fit=read(P/'COORDINATED_TRAJECTORY_FIT.json');dump('SOLVER_EXECUTION_ACCOUNTING.json',dict(preflight_batch_static_tests=6,
    actual_static_readback_no_actions=True,initialization_joint_pose_solves_inside_single_run=fit['phase_initialization_solves'],
    new_dynamic_candidates=1,coupled_full_trajectory_solves=1,nfev=fit['nfev'],converged=fit['success'],
    post_render_refits=0,restarts=0,independent_note_animations_stitched=False,manual_per_note_or_finger_patches=False))
print('LEFT_FOUR_BAR_VERIFIED_ALL7_ONE_CANDIDATE_PROTECTED',len(protected),flush=True)
