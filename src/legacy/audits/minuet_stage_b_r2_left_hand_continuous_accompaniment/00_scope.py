from stage_common import *
import mido,collections,csv,re
assert not (P/'INPUT_LOCK.json').exists()
assert sha(SOURCE)=='fd87a6673e18104047842a1c858d2c9d8eb9ad845d7a8fa46e3664b17642cb75'
m=mido.MidiFile(SOURCE);notes=[];meta=[];controls=[];names={}
for ti,tr in enumerate(m.tracks):
    tick=0;held=collections.defaultdict(collections.deque)
    for msg in tr:
        tick+=msg.time
        if msg.is_meta:
            meta.append(dict(track=ti,tick=tick,**msg.dict()))
            if msg.type=='track_name':names[ti]=msg.name
        elif msg.type=='control_change':controls.append(dict(track=ti,tick=tick,**msg.dict()))
        elif msg.type=='note_on' and msg.velocity:held[msg.channel,msg.note].append((tick,msg.velocity))
        elif msg.type=='note_off' or msg.type=='note_on' and not msg.velocity:
            on,vel=held[msg.channel,msg.note].popleft()
            if ti==2 and 0<=on<4608:notes.append(dict(track=ti,channel=msg.channel,midi_note=msg.note,on_tick=on,off_tick=tick,velocity=vel))
    assert all(not v for v in held.values())
assert m.ticks_per_beat==384 and names[2]=='two:'
assert [(x['tick'],x['tempo']) for x in meta if x['type']=='set_tempo']==[(0,428571)]
assert [(x['tick'],x['numerator'],x['denominator']) for x in meta if x['type']=='time_signature']==[(0,3,4)]
notes.sort(key=lambda n:(n['on_tick'],n['midi_note']))
assert [(n['midi_note'],n['on_tick'],n['off_tick']) for n in notes]==[(55,0,768),(59,0,768),(62,0,768),(57,768,1152),(59,1152,2304),(60,2304,3456),(59,3456,4608)]
fingers=[5,3,1,4,3,2,3];lead=.35;duration=4608/384*428571/1e6
for i,(n,finger) in enumerate(zip(notes,fingers)):
    key=c.KEYS[n['midi_note']-21];n.update(note_id=f'L{i:02d}',hand='L',finger=finger,key_index=n['midi_note']-21,
        note_name=key['note_name'],key_color=key['color'],measure=1+n['on_tick']//1152,
        note_on=lead+n['on_tick']/384*428571/1e6,note_off=lead+n['off_tick']/384*428571/1e6,
        duration_ticks=n['off_tick']-n['on_tick'],source_on_sec=n['on_tick']/384*428571/1e6,source_off_sec=n['off_tick']/384*428571/1e6)
assert all(n['off_tick']<=4608 for n in notes) and max(n['off_tick'] for n in notes)==4608
groups=[]
for tick in sorted(set(n['on_tick'] for n in notes)):
    ns=[n for n in notes if n['on_tick']==tick];groups.append(dict(on_tick=tick,source_on_sec=ns[0]['source_on_sec'],
        note_ids=[n['note_id'] for n in ns],notes=[n['note_name'] for n in ns],fingers=[n['finger'] for n in ns],
        type='CHORD' if len(ns)>1 else 'SINGLE',off_ticks=[n['off_tick'] for n in ns]))
overlaps=[dict(previous=a['note_id'],next=b['note_id'],overlap_ticks=a['off_tick']-b['on_tick']) for i,a in enumerate(notes) for b in notes[i+1:] if a['on_tick']<b['on_tick']<a['off_tick']]
repeats=[dict(previous=a['note_id'],next=b['note_id'],gap_ticks=b['on_tick']-a['off_tick'],adjacent_same_key_restrike=False)
    for i,a in enumerate(notes) for b in notes[i+1:] if a['midi_note']==b['midi_note']]
score=SOURCE.with_suffix('.ly');leftvoice=score.read_text(encoding='utf8').split('voicetwo =')[1]
assert not re.search(r'\\finger\b|-[1-5](?!\d)',leftvoice)
dump('PERFORMANCE_TIMELINE.json',dict(notes=notes,fps=60,planning_hz=120,presentation_lead_sec=lead,
    source_duration_sec=duration,presentation_duration_sec=lead+duration+.45,source_sha256=sha(SOURCE),
    source_track=2,ppq=384,tempo_us_per_quarter=428571,time_signature=[3,4],source_tick_range=[0,4608],
    right_motion_generated=False,audio_scope='ALL_ORIGINAL_LEFT_NOTES_FIRST4_BARS',fingering_authority='DESIGN_PROVISIONAL'))
dump('LEFT_FOUR_BAR_SCOPE_VERIFICATION.json',dict(note_count=len(notes),note_on_count=len(notes),note_off_count=len(notes),
    groups=groups,musical_peak_polyphony=3,chord_groups=1,double_note_groups=0,single_note_groups=4,
    different_onset_held_overlaps=overlaps,adjacent_same_key_restrikes=[],pitch_revisits=repeats,
    pitch_range=[55,62],five_finger_position='G3,A3,B3,C4,D4 =5,4,3,2,1',required_register_reposition=False,
    hand_position_claim='All notes fit one provisional five-finger span; wrist adaptations may occur, not a demonstrated large register shift.',
    last_NOTE_OFF_tick=4608,no_boundary_clip=True,source_duration_sec=duration,
    source_printed_fingering=False,controls=controls,score_sha256=sha(score)))
with (P/'ORIGINAL_LEFT_EVENTS_FIRST4.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(notes[0]));w.writeheader();w.writerows(notes)
protected=read(B1/'PROTECTED_INPUTS_BEFORE.json');protected={p:sha(p) for p in protected if Path(p).is_file()}
for folder in [A2,B1]:
    for f in folder.rglob('*'):
        if f.is_file():protected[str(f)]=sha(f)
dump('PROTECTED_INPUTS_BEFORE.json',protected)
dump('HUMAN_AUTHORITY_BIND.json',dict(source='Direct Human Stage B R2 request',
    STAGE_A_R2='HUMAN_VISUAL_APPROVED_WITH_ENGINEERING_WARN',STAGE_B_R1_HUMAN_NATURALNESS='INCONCLUSIVE_DURATION_TOO_SHORT',
    B1_technical_results_retained=['THREE_FINGER_CONTACT_PASS','SHARED_ROOT_FINGER_COORDINATION_PASS','CHORD_TIMING_PASS','ENGINEERING_WARN'],
    B1_Human_visual_PASS_not_claimed=True,prior_files_not_rewritten=True,all_frozen_baselines_preserved=True,
    ONE_NEW_DYNAMIC_CANDIDATE_ONLY=True,no_dual_hand_stage=True))
dump('INPUT_LOCK.json',dict(source_sha256=sha(SOURCE),timeline_sha256=sha(P/'PERFORMANCE_TIMELINE.json'),
    source_tick_range=[0,4608],fingers=fingers,fingering_authority='DESIGN_PROVISIONAL',
    first_triad_fingers_preserved=[5,3,1],rationale='Continue left G3-D4 five-finger layout: A3 ring4, B3 middle3, C4 index2; B3 revisited by3. No post-render change.',
    candidate_limit=1,committed_before_motion=True))
print('LEFT_FOUR_BAR_SCOPE',[(n['note_name'],n['finger'],n['on_tick'],n['off_tick']) for n in notes],duration,'overlaps',overlaps,'protected',len(protected),flush=True)
