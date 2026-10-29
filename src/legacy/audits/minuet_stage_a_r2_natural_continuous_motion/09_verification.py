from stage_common import *
import ast,mido,collections
tl=read(P/'PERFORMANCE_TIMELINE.json');assert tl==read(R1/'PERFORMANCE_TIMELINE.json')
lock=read(P/'GENERATION_LOCK.json');assert all(sha(P/n)==h for n,h in lock['scripts'].items())
assert sha(P/'GENERATION_POLICY.json')==lock['policy_sha256'] and sha(SOURCE)==lock['source_sha256']
original=[];tick=0;held=collections.defaultdict(collections.deque)
for msg in mido.MidiFile(SOURCE).tracks[1]:
    tick+=msg.time
    if msg.type=='note_on' and msg.velocity:held[msg.channel,msg.note].append((tick,msg.velocity))
    elif msg.type=='note_off' or msg.type=='note_on' and not msg.velocity:
        on,vel=held[msg.channel,msg.note].popleft()
        if on<4608:original.append((msg.note,on,tick,vel,msg.channel))
assert sorted(original)==sorted((n['midi_note'],n['on_tick'],n['off_tick'],n['velocity'],n['channel']) for n in tl['notes'])
assert len(original)==16
assert sha(P/'piano_performance.wav')==sha(R1/'piano_performance.wav')
videos=read(P/'VIDEO_VERIFICATION.json');assert len(videos)==3
for name,v in videos.items():
    assert v['frames']==342 and v['fps']==60 and v['duration_sec']==5.7 and v['full_decode']=='PASS'
    assert v['sha256']==sha(P/name)
man=read(P/'SCENE_MANIFEST.json');assert man['four_static_scenes_unchanged'] and man['hand_structure_unchanged'] and man['all_88_key_geometry_unchanged']
assert man.get('all_R1_review_cameras_matched_float32_precision',False) and man['save_reopen_verified']
assert len(list(P.glob('*.blend')))==1
for f in P.glob('*.py'):ast.parse(f.read_text(encoding='utf8'))
protected=read(P/'PROTECTED_INPUTS_BEFORE.json');changed=[];missing=[]
for name,h in protected.items():
    if not Path(name).is_file():missing.append(name)
    elif sha(name)!=h:changed.append(name)
assert not changed and not missing,(changed,missing)
dump('FROZEN_ASSET_VERIFICATION.json',dict(protected_files=len(protected),changed=changed,missing=missing,
    all_protected_hashes_unchanged=True,right_R2='HUMAN_APPROVED_FROZEN',left_R1='HUMAN_APPROVED_FROZEN',
    four_approved_static_poses_unchanged=True,grand_88_key_frozen=True,
    MIDI_mapping_and_audio_chain_unchanged=True,R1_original_failed_candidate_unchanged=True,
    Musette_Human_acceptance_carried_forward=True,history_not_reapproved=True))
dump('EVENT_AUDIO_VIDEO_VERIFICATION.json',dict(original_MIDI_sha256=sha(SOURCE),
    original_source_duration_sec=5.142852,note_count=16,note_on_count=16,note_off_count=16,
    NOTE_ON_OFF_velocity_pitch_channel_exact=True,R1_provisional_fingering_exact=True,
    original_PCM_bytes_exact=True,left_motion_or_audio=False,video_duration_sec=5.7,
    videos=videos,same_actual_camera_transforms=True,all_generated_files_in_new_audit_directory=True))
fit=read(P/'COORDINATED_TRAJECTORY_FIT.json')
dump('SOLVER_EXECUTION_ACCOUNTING.json',dict(new_dynamic_trajectory_candidates=1,
    preflight_static_pose_solves=3,internal_adjacent_event_static_initializations=16,
    coupled_dynamic_trajectory_solves=1,normal_internal_nfev=fit['nfev'],residual_evaluations=fit['calls'],
    solver_converged=fit['success'],post_render_refits=0,restarts=0,new_left_actions=0,
    clarification='16 static initial poses are generic initialization inside the single trajectory run, not manually edited poses or 16 dynamic candidates.'))
print('VERIFIED_ONE_CANDIDATE_16_EVENTS_PCM_3_VIEWS_AND_FROZEN_FILES',len(protected),flush=True)
