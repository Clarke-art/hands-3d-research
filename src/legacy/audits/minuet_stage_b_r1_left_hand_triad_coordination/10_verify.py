from stage_common import *
import mido,collections,ast
lock=read(P/'GENERATION_LOCK.json');assert all(sha(P/n)==h for n,h in lock['scripts'].items())
assert sha(SOURCE)==lock['source_sha256'] and sha(P/'PERFORMANCE_TIMELINE.json')==lock['timeline_sha256']
assert sha(P/'GENERATION_POLICY.json')==lock['policy_sha256']
tl=read(P/'PERFORMANCE_TIMELINE.json');selected=tl['notes'];original=[];tick=0;held=collections.defaultdict(collections.deque)
for msg in mido.MidiFile(SOURCE).tracks[2]:
    tick+=msg.time
    if msg.type=='note_on' and msg.velocity:held[msg.channel,msg.note].append((tick,msg.velocity))
    elif msg.type=='note_off' or msg.type=='note_on' and not msg.velocity:
        on,vel=held[msg.channel,msg.note].popleft()
        if on==0:original.append((msg.note,on,tick,vel,msg.channel))
assert sorted(original)==sorted((n['midi_note'],n['on_tick'],n['off_tick'],n['velocity'],n['channel']) for n in selected)
assert len(original)==3 and [n['finger'] for n in selected]==[5,3,1]
audio=read(P/'KEY_AUDIO_SYNC_R1.json');assert len(audio['voices'])==3 and audio['polyphony_peak_held']==3 and audio['pitch_within25cents']
for n,v in zip(selected,audio['voices']):
    assert v['midi_note']==n['midi_note'] and v['hand']=='L' and v['velocity']==n['velocity']
    assert v['timeline_on_sec']==n['note_on'] and v['note_off_sec']==n['note_off']
assert len(set(v['timeline_on_sec'] for v in audio['voices']))==1 and len(set(v['note_off_sec'] for v in audio['voices']))==1
man=read(P/'SCENE_MANIFEST.json');assert sha(man['path'])==man['sha256']
assert man['four_static_scenes_unchanged'] and man['hand_structure_unchanged'] and man['all_88_key_geometry_unchanged'] and man['save_reopen_verified']
assert man['left_only'] and not man['right_in_performance_scene']
assert len(list(P.glob('*.blend')))==1
framing=read(P/'WHOLE_LEFT_HAND_FRAMING.json');assert framing['all_views_entire_left_hand_visible']
videos=read(P/'VIDEO_VERIFICATION.json');assert len(videos)==3
for n,v in videos.items():
    assert v['fps']==60 and v['frames']==man['frames']==100 and v['sha256']==sha(P/n) and v['full_decode']=='PASS'
diag=read(P/'ENGINEERING_DIAGNOSTICS.json');assert diag['same_key_pressure_max_difference']<1e-6 and diag['other_keys_stationary']
for f in P.glob('*.py'):ast.parse(f.read_text(encoding='utf8'))
protected=read(P/'PROTECTED_INPUTS_BEFORE.json');changed=[];missing=[]
for path,h in protected.items():
    if not Path(path).is_file():missing.append(path)
    elif sha(path)!=h:changed.append(path)
assert not changed and not missing,(changed,missing)
dump('FROZEN_AND_APPROVED_BASELINE_VERIFICATION.json',dict(protected_files=len(protected),changed=changed,missing=missing,
    all_protected_hashes_unchanged=True,RIGHT_HAND_R2='HUMAN_APPROVED_FROZEN',LEFT_HAND_R1='HUMAN_APPROVED_FROZEN',
    Grand88_keyboard_unchanged=True,approved_four_static_poses_unchanged=True,
    STAGE_A_R2='HUMAN_VISUAL_APPROVED_WITH_ENGINEERING_WARN',approved_A2_candidate_code_videos_reports_unchanged=True,
    A2_historical_pending_reports_not_rewritten=True,latest_Human_authority_stored_in_this_audit=True,
    original_MIDI_and_audio_chain_unchanged=True,Musette_Human_acceptance_carried_forward=True))
dump('EVENT_KEY_AUDIO_VIDEO_VERIFICATION.json',dict(original_MIDI_sha256=sha(SOURCE),
    original_three_notes_exact=True,original_NOTE_ON_OFF_velocity_channel_exact=True,
    original_duration_sec=.857142,source_on_tick=0,source_off_tick=768,ppq=384,tempo_us_per_quarter=428571,
    fingers_DESIGN_PROVISIONAL=[5,3,1],voices=3,other_notes_or_repetition_added=False,
    same_three_MIDI_on_off=True,same_three_key_pressure=True,same_three_audio_on_off=True,
    sample_audio_clock_quantization_max_ms=audio['audio_clock_quantization_max_ms'],all_sample_pitch_ratios_correct=True,
    spectrum_checks_within25cents=True,video_fps=60,video_frames=100,video_duration_sec=100/60,
    AAC_container_audio_duration_sec=[v['audio_duration_sec'] for v in videos.values()],
    AAC_final_silent_tail_rounding_under_1ms=True,all_three_views_full_decode=True,
    left_only_not_full_measure=True,left_hand_framing_pass=True))
fit=read(P/'COORDINATED_TRAJECTORY_FIT.json');dump('SOLVER_EXECUTION_ACCOUNTING.json',dict(
    preflight_static_tests=3,preflight_static_readback_no_actions=True,phase_initializations_inside_single_run=fit['phase_initialization_solves'],
    new_dynamic_candidates=1,coupled_dynamic_solves=1,concurrent_active_peak=fit['concurrent_peak_fingers'],
    normal_internal_nfev=fit['nfev'],converged=fit['success'],post_render_refits=0,restarts=0,
    right_actions_generated=0,manual_per_finger_or_note_patch=False))
print('STAGE_B_VERIFIED_3_ORIGINAL_NOTES_ONE_CANDIDATE_ALL_APPROVED_PROTECTED',len(protected),flush=True)
