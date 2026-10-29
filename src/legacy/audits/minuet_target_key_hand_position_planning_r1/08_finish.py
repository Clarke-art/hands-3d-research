from stage_common import *
import ast,collections,mido
tl=read(P/'PERFORMANCE_TIMELINE.json');diag=read(P/'ENGINEERING_DIAGNOSTICS.json');man=read(P/'SCENE_MANIFEST.json');videos=read(P/'VIDEO_VERIFICATION.json');audio=read(P/'KEY_AUDIO_SYNC_R1.json')
lock=read(P/'PLANNING_LOCK.json');assert all(sha(P/n)==v for n,v in lock['scripts'].items())
assert sha(P/'motion.npz')==read(P/'SCENE_IMPORT_REPAIR.json')['motion_sha256']
assert sha(SOURCE)==read(P/'INPUT_LOCK.json')['source_sha256']
original=[];tick=0;held=collections.defaultdict(collections.deque)
for msg in mido.MidiFile(SOURCE).tracks[1]:
    tick+=msg.time
    if msg.type=='note_on' and msg.velocity:held[msg.channel,msg.note].append((tick,msg.velocity))
    elif msg.type=='note_off' or msg.type=='note_on' and not msg.velocity:
        on,vel=held[msg.channel,msg.note].popleft()
        if on<4608:original.append((msg.note,on,tick,vel,msg.channel))
assert sorted(original)==sorted((n['midi_note'],n['on_tick'],n['off_tick'],n['velocity'],n['channel']) for n in tl['notes'])
for n,v in zip(tl['notes'],audio['voices']):
    assert v['midi_note']==n['midi_note'] and v['velocity']==n['velocity'] and v['hand']=='R'
    assert abs(v['note_off_sec']-n['note_off'])<1e-12
    assert abs(v['timeline_on_sec']-n['note_on'])<1e-12
dump('EVENT_AND_AUDIO_VERIFICATION.json',dict(original_midi_sha256=sha(SOURCE),
    all_original_16_notes_exact=True,note_on_count=16,note_off_count=16,
    source_ppq=384,tempo_us_per_quarter=428571,source_duration_sec=5.142852,
    original_event_pairs_velocity_channel_exact=True,presentation_lead_sec=.3,
    right_only_audio=True,voices=16,note_on_off_changed=False,all_pitch_mappings_correct=True,
    max_audio_quantization_ms=audio['audio_clock_quantization_max_ms'],pitch_within25cents=audio['pitch_within25cents'],
    hand_contact_sync='FAIL',key_retrigger_sync='FAIL_TWO_ABUTTING_G4_REPEATS',
    video_decode_pass=True,all_three_video_audio_duration_sec=5.7))
protected=read(P/'PROTECTED_INPUTS_BEFORE.json');changed=[];missing=[]
for name,digest in protected.items():
    if not Path(name).is_file():missing.append(name)
    elif sha(name)!=digest:changed.append(name)
assert not changed and not missing,(changed,missing)
dump('FROZEN_ASSET_VERIFICATION.json',dict(protected_files=len(protected),changed=changed,missing=missing,
    all_protected_hashes_unchanged=True,right_R2='HUMAN_APPROVED_FROZEN',left_R1='HUMAN_APPROVED_FROZEN',
    grand_88_key_frozen_unchanged=True,approved_static_four_unchanged=True,
    Musette_Human_acceptance_carried_forward=True,historical_engineering_limits_retained=True))
for f in P.glob('*.py'):ast.parse(f.read_text(encoding='utf8'))
result=dict(phase='MINUET_TARGET_KEY_HAND_POSITION_PLANNING_R1',stage='A',
    status='FAIL_STAGE_A_MOTION_QUALITY_NOT_QUALIFIED',human_review='PENDING',
    implementation='GENERIC_TARGET_KEY_AND_ROOT_INTERFACE_IMPLEMENTED',
    given_provisional_fingering=True,automatic_fingering=False,
    candidate_count=1,motion_generation_attempts=1,planner_restarts=0,
    performance_blend_count=1,right_root_and_joint_actions=2,key_actions=8,
    right_note_count=16,left_motion_generated=False,normal_speed_views=3,
    source_duration_sec=5.142852,video_duration_sec=5.7,
    input_events_preserved=True,frozen_assets_unchanged=True,
    alternate_pitch_set='PLANNING_ONLY_PASS_NO_SECOND_ANIMATION',
    blockers=['Visible fingertip hover on depressed white keys',
        'G5 hold contact lost during premature root return before G4',
        'Bounded independent finger adaptation cannot fulfill the prescribed common-root path',
        'Inherited key-pressure max-of-release/attack prevents full rebound in two G4 repeats'],
    no_frozen_rig_infeasibility_claim=True,no_Musette_reapproval=True,
    next_local_architecture='Contact-feasible root/digit planning over adjacent events; separate repeated-key mechanical arbitration. No infinite DIP/root tuning.',
    stop='ONE_CANDIDATE_LIMIT_REACHED_NO_SECOND_GENERATION')
dump('FINAL_STATUS.json',result)
files={f.name:dict(sha256=sha(f),bytes=f.stat().st_size) for f in P.iterdir() if f.is_file() and f.name not in ['DELIVERY_MANIFEST.json']}
dump('DELIVERY_MANIFEST.json',dict(candidate_count=1,files=files,
    frame_count_each=342,views=videos,main_review='HUMAN_REVIEW.html',status=result['status']))
print('FINAL_FAIL_SINGLE_CANDIDATE_PROTECTED',len(protected),flush=True)
