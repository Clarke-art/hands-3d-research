from stage_common import *
import mido, collections, csv, re
assert not (P/'INPUT_LOCK.json').exists(), 'Inputs already committed'
assert sha(SOURCE) == 'fd87a6673e18104047842a1c858d2c9d8eb9ad845d7a8fa46e3664b17642cb75'
m = mido.MidiFile(SOURCE); notes=[]; meta=[]
for ti, tr in enumerate(m.tracks):
    tick=0; held=collections.defaultdict(collections.deque)
    for msg in tr:
        tick += msg.time
        if msg.is_meta: meta.append(dict(track=ti, tick=tick, **msg.dict()))
        elif msg.type=='note_on' and msg.velocity:
            held[msg.channel,msg.note].append((tick,msg.velocity))
        elif msg.type=='note_off' or msg.type=='note_on' and not msg.velocity:
            on,vel=held[msg.channel,msg.note].popleft()
            if ti==1 and on<4608:
                assert tick<=4608
                notes.append(dict(midi_note=msg.note, channel=msg.channel, on_tick=on, off_tick=tick, velocity=vel))
    assert all(not v for v in held.values())
assert m.ticks_per_beat==384
assert [(x['tick'],x['tempo']) for x in meta if x['type']=='set_tempo']==[(0,428571)]
assert [(x['tick'],x['numerator'],x['denominator']) for x in meta if x['type']=='time_signature']==[(0,3,4)]
assert next(x['name'] for x in meta if x['type']=='track_name' and x['track']==1)=='one:'
notes.sort(key=lambda x:x['on_tick'])
# Given music-level fingering, committed BEFORE any solve or visual result.
# Five-finger G position; E5 fifth then C5 third; release/reposition during
# ascending E5/F#5/G5; octave return by thumb. No pose coordinates here.
fingers=[5,1,2,3,4, 5,1,1, 5,3,4,3,4, 5,1,1]
expected=[74,67,69,71,72,74,67,67,76,72,74,76,78,79,67,67]
assert [x['midi_note'] for x in notes]==expected and len(notes)==16
LEAD=.3; END=LEAD+4608/384*428571/1e6+.25
for i,(n,f) in enumerate(zip(notes,fingers)):
    n.update(note_id=f'R{i:02d}',hand='R',finger=f,key_index=n['midi_note']-21,
        measure=1+n['on_tick']//1152,note_on=LEAD+n['on_tick']/384*428571/1e6,
        note_off=LEAD+n['off_tick']/384*428571/1e6)
    k=c.KEYS[n['key_index']]; assert k['midi_note']==n['midi_note']
    n.update(note_name=k['note_name'],key_color=k['color'])
assert all(a['off_tick']<=b['on_tick'] for a,b in zip(notes,notes[1:]))
voice=SCORE.read_text(encoding='utf8').split('voiceone =')[1].split('voicetwo =')[0]
assert not re.search(r'\\finger\b|-[1-5](?!\d)',voice)
timeline=dict(notes=notes, fps=60, planning_hz=120, presentation_lead_sec=LEAD,
    source_duration_sec=5.142852, presentation_duration_sec=END, source_sha256=sha(SOURCE),
    source_tick_range=[0,4608], ppq=384, tempo_us_per_quarter=428571,
    left_motion_generated=False, right_note_count=16, source_note_events_unmodified=True,
    fingering_authority='DESIGN_PROVISIONAL_GIVEN_INPUT_NOT_AUTOMATIC_FINGERING')
dump('PERFORMANCE_TIMELINE.json',timeline)
with (P/'ORIGINAL_RIGHT_EVENTS_FIRST4.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(notes[0]));w.writeheader();w.writerows(notes)
prior=read(ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/PROTECTED_INPUTS_BEFORE.json')
protected={p:sha(p) for p in prior if Path(p).is_file()}
for folder in [ROOT/'audits/minuet_in_g_longer_phrase_validation_r1',
               ROOT/'audits/right_hand_articulation_contact_short_phrase_r1']:
    for p in folder.rglob('*'):
        if p.is_file(): protected[str(p)]=sha(p)
for name in ['RIGHT_HAND_PRODUCT_BASELINE.json','LEFT_HAND_PRODUCT_BASELINE.json']:
    ptr=ROOT/'production_spec'/name; v=read(ptr); asset=ROOT/v['asset']['path']
    assert sha(asset)==v['asset']['sha256']; protected[str(ptr)]=sha(ptr);protected[str(asset)]=sha(asset)
dump('PROTECTED_INPUTS_BEFORE.json',protected)
dump('INPUT_LOCK.json',dict(source_sha256=sha(SOURCE),score_sha256=sha(SCORE),
    timeline_sha256=sha(P/'PERFORMANCE_TIMELINE.json'), fingers=fingers,
    source_printed_fingering=False, source_track=1, source_bars=[1,4],
    candidate_limit=1, input_committed_before_motion=True,
    rationale='G-position first two bars; E5=5,C5=3,D5=4 then E5=3/F#5=4/G5=5 permits register reposition; G4=1 octave return. Provisional and not teacher-approved. No post-render refingering.'))
print('INPUT_LOCKED', [(n['note_name'],n['finger'],n['on_tick'],n['off_tick']) for n in notes], 'protected',len(protected))
