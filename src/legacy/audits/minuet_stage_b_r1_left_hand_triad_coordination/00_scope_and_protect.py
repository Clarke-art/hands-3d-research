from stage_common import *
import mido,collections,csv,re
assert not (P/'INPUT_LOCK.json').exists()
assert sha(SOURCE)=='fd87a6673e18104047842a1c858d2c9d8eb9ad845d7a8fa46e3664b17642cb75'
m=mido.MidiFile(SOURCE);allnotes=[];meta=[];names={}
for ti,tr in enumerate(m.tracks):
    tick=0;held=collections.defaultdict(collections.deque)
    for msg in tr:
        tick+=msg.time
        if msg.is_meta:
            meta.append(dict(track=ti,tick=tick,**msg.dict()))
            if msg.type=='track_name':names[ti]=msg.name
        elif msg.type=='note_on' and msg.velocity:held[msg.channel,msg.note].append((tick,msg.velocity))
        elif msg.type=='note_off' or msg.type=='note_on' and not msg.velocity:
            on,vel=held[msg.channel,msg.note].popleft();allnotes.append(dict(track=ti,channel=msg.channel,midi_note=msg.note,on_tick=on,off_tick=tick,velocity=vel))
    assert all(not v for v in held.values())
assert m.ticks_per_beat==384 and names[2]=='two:'
assert [(x['tick'],x['tempo']) for x in meta if x['type']=='set_tempo']==[(0,428571)]
assert [(x['tick'],x['numerator'],x['denominator']) for x in meta if x['type']=='time_signature']==[(0,3,4)]
selected=sorted([n for n in allnotes if n['track']==2 and n['on_tick']==0],key=lambda n:n['midi_note'])
assert [n['midi_note'] for n in selected]==[55,59,62]
assert {n['off_tick'] for n in selected}=={768}
lead=.35;duration=768/384*428571/1e6
for i,(n,finger) in enumerate(zip(selected,[5,3,1])):
    k=c.KEYS[n['midi_note']-21];assert k['midi_note']==n['midi_note']
    n.update(note_id=f'L{i:02d}',hand='L',finger=finger,key_index=n['midi_note']-21,
        note_name=k['note_name'],key_color=k['color'],note_on=lead+n['on_tick']/384*428571/1e6,
        note_off=lead+n['off_tick']/384*428571/1e6)
overlaps=[n for n in allnotes if n not in selected and n['on_tick']<768 and n['off_tick']>0]
# selected now has extra fields, so exclude by identity of the three raw events.
overlaps=[n for n in overlaps if not (n['track']==2 and n['on_tick']==0 and n['midi_note'] in [55,59,62])]
score=SOURCE.with_suffix('.ly');leftvoice=score.read_text(encoding='utf8').split('voicetwo =')[1]
assert not re.search(r'\\finger\b|-[1-5](?!\d)',leftvoice)
timeline=dict(notes=selected,fps=60,planning_hz=120,presentation_lead_sec=lead,
    source_duration_sec=duration,presentation_duration_sec=lead+duration+.45,
    source_sha256=sha(SOURCE),source_track=2,source_track_name=names[2],ppq=384,
    tempo_us_per_quarter=428571,time_signature=[3,4],scope='ONLY_ORIGINAL_OPENING_LEFT_TRIAD',
    full_measure_performance=False,right_motion_generated=False,audio_scope='THREE_SELECTED_LEFT_NOTES_ONLY',
    simultaneous_note_on=True,simultaneous_note_off=True,fingering_authority='DESIGN_PROVISIONAL')
dump('PERFORMANCE_TIMELINE.json',timeline)
dump('SOURCE_TRIAD_EVENT_VERIFICATION.json',dict(original_file=str(SOURCE),original_sha256=sha(SOURCE),
    selected=selected,source_duration_sec=duration,all_three_on_tick=0,all_three_off_tick=768,
    all_three_same_on_off=True,other_events_overlapping_in_original_source=overlaps,
    other_left_events_during_hold=[],other_events_in_demo=[],source_printed_fingering=False,score_sha256=sha(score)))
with (P/'ORIGINAL_LEFT_TRIAD_EVENTS.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(selected[0]));w.writeheader();w.writerows(selected)
protected=read(A2/'PROTECTED_INPUTS_BEFORE.json');protected={p:sha(p) for p in protected if Path(p).is_file()}
for f in A2.rglob('*'):
    if f.is_file():protected[str(f)]=sha(f)
for name in ['RIGHT_HAND_PRODUCT_BASELINE.json','LEFT_HAND_PRODUCT_BASELINE.json']:
    ptr=ROOT/'production_spec'/name;v=read(ptr);asset=ROOT/v['asset']['path'];assert sha(asset)==v['asset']['sha256']
    protected[str(ptr)]=sha(ptr);protected[str(asset)]=sha(asset)
dump('PROTECTED_INPUTS_BEFORE.json',protected)
dump('HUMAN_AUTHORITY_BIND.json',dict(source='Direct Human Stage B request',
    STAGE_A_R2='HUMAN_VISUAL_APPROVED_WITH_ENGINEERING_WARN',
    approved_scope='First4 bars /16 right notes, amateur piano teaching demonstration',
    retained_warns=['root high acceleration','solver max evaluations without convergence','finite geometry WARN'],
    Stage_A_original_files_not_rewritten=True,not_generalization_approval=True,
    frozen_right_R2=True,frozen_left_R1=True,Grand88_frozen=True,approved_four_static_poses=True,
    Musette_Human_acceptance_carried_forward=True,ONE_NEW_DYNAMIC_CANDIDATE_ONLY=True))
dump('INPUT_LOCK.json',dict(source_sha256=sha(SOURCE),timeline_sha256=sha(P/'PERFORMANCE_TIMELINE.json'),
    score_sha256=sha(score),fingers_by_selected_note=[5,3,1],fingering_status='DESIGN_PROVISIONAL',
    committed_before_motion=True,candidate_limit=1,isolated_original_chord_not_full_measure=True))
print('TRIAD_INPUT_LOCK',[(n['note_name'],n['finger'],n['channel'],n['on_tick'],n['off_tick']) for n in selected],duration,'SOURCE_OTHER_OVERLAPS',overlaps,'protected',len(protected),flush=True)
