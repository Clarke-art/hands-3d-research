from common import *
sys.path.insert(0,str(OLD/'_deps'))
import mido
assert not DEST.exists(),'ONE_NEW_DUAL_HAND_CANDIDATE_ONLY'
bindings={};notes=[]
mf=mido.MidiFile(MIDI)
tempo_events=[];raw=[];allnoteevents=[]
for tr,track in enumerate(mf.tracks):
    tick=0;held={}
    for seq,msg in enumerate(track):
        tick+=msg.time
        if msg.type=='set_tempo':tempo_events.append([tick,msg.tempo])
        if msg.type in ('note_on','note_off'):
            allnoteevents.append(dict(track=tr,sequence=seq,tick=tick,**msg.dict()))
            key=(msg.channel,msg.note)
            if msg.type=='note_on' and msg.velocity:
                assert key not in held
                held[key]=(tick,msg.velocity,seq)
            else:
                a,v,q=held.pop(key)
                if a<4608:
                    assert tick<=4608
                    raw.append(dict(track=tr,channel=msg.channel,midi_note=msg.note,on_tick=a,off_tick=tick,velocity=v,on_sequence=q,off_sequence=seq,off_type=msg.type,off_velocity=msg.velocity))
assert mf.ticks_per_beat==384 and tempo_events==[[0,428571]]
assert len(raw)==23
for side,folder in SOURCES.items():
    man=read(folder/'SCENE_MANIFEST.json');tl=read(folder/'PERFORMANCE_TIMELINE.json');state=read(folder/'FINAL_STATUS.json')
    assert sha(man['path'])==man['sha256']
    assert sha(MIDI)==tl['source_sha256']
    assert tl['fps']==60
    lead=tl['presentation_lead_sec']
    for n in tl['notes']:
        original=next(v for v in raw if all(v[k]==n[k] for k in ['channel','midi_note','on_tick','off_tick','velocity']))
        assert abs(n['note_on']-lead-n['on_tick']*428571/384/1e6)<1e-12
        assert abs(n['note_off']-lead-n['off_tick']*428571/384/1e6)<1e-12
        notes.append(dict(n,**original,source_on_sec=n['note_on']-lead,source_off_sec=n['note_off']-lead,note_on=n['note_on']-lead+LEAD,note_off=n['note_off']-lead+LEAD))
    bindings[side]=dict(manifest=man,timeline_sha256=sha(folder/'PERFORMANCE_TIMELINE.json'),motion_sha256=sha(folder/'motion.npz'),engineering_diagnostics_sha256=sha(folder/'ENGINEERING_DIAGNOSTICS.json'),lead_sec=lead,shift_frames=round((LEAD-lead)*FPS),human_status='HUMAN_VISUAL_APPROVED_WITH_ENGINEERING_WARN',approval_authority='Explicit user instruction MINUET_STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_PERFORMANCE, 2026-10-10',approval_scope='Original single-hand performance only',historical_status=state)
assert len(notes)==23 and sum(n['hand']=='R' for n in notes)==16 and sum(n['hand']=='L' for n in notes)==7
assert not {n['key_index'] for n in notes if n['hand']=='R'} & {n['key_index'] for n in notes if n['hand']=='L'}
dump('SOURCE_BINDINGS.json',bindings)
dump('PERFORMANCE_TIMELINE.json',dict(notes=sorted(notes,key=lambda x:(x['on_tick'],x['track'],x['midi_note'])),fps=FPS,presentation_lead_sec=LEAD,source_duration_sec=5.142852,presentation_duration_sec=5.95,frames=357,source_sha256=sha(MIDI),ppq=384,tempo_us_per_quarter=428571,source_tick_range=[0,4608],source_event_count=23,raw_original_events=raw,raw_note_messages=[v for v in allnoteevents if v['tick']<=4608],fingering_authority='DESIGN_PROVISIONAL_UNCHANGED'))
# Snapshot the complete current protected set plus both entire approved audit
# directories. Historical hashes are preserved as evidence, not rewritten.
files=set()
for folder in SOURCES.values():
    historical=read(folder/'PROTECTED_INPUTS_BEFORE.json')
    files.update(Path(n) for n in historical)
    files.update(p for p in folder.rglob('*') if p.is_file())
files.add(MIDI)
snapshot={str(p):sha(p) for p in sorted(files) if p.is_file()}
dump('PROTECTED_INPUTS_BEFORE.json',snapshot)
doc('APPROVED_SOURCE_BINDINGS.md','# Approved source bindings\n\nHuman approval authority: this round’s explicit user instruction. The source FINAL_STATUS files retain their older HUMAN_PENDING state and are preserved unchanged. Human acceptance is single-hand only, with engineering WARN; it does not authorize dual-hand visual PASS.\n\n'+ '\n\n'.join(f"{s}: `{b['manifest']['path']}`\n\nSHA256 `{b['manifest']['sha256']}`; scene `{b['manifest']['scene']}`; bindings `{b['manifest']['mapping']}`; motion `{b['motion_sha256']}`." for s,b in bindings.items())+f'\n\n{len(snapshot)} current protected files snapshotted; read-only Blender Action/coordinate validation follows. No solver imported.\n')
doc('SHARED_MIDI_TIMELINE.md','# Shared original MIDI clock\n\nOriginal MIDI SHA256 `'+sha(MIDI)+'`. PPQ 384; tempo 428571 µs/quarter; 3/4, four bars, ticks 0–4608, music duration 5.142852 s. All 23 original identities/pitches/channels/velocities and NOTE_ON/OFF ticks read directly from original MIDI and matched individually against the approved timelines.\n\nVerified report leads: R 0.30 s; L 0.35 s. Common preparation lead 0.35 s. `T_PRESENT = T_MUSIC + 0.35`; `F_SHARED = 1 + 60*T_PRESENT`; R Action origin shifts +3 frames; L +0 frames. No time scaling, interpolation change or musical event alteration. Actual Action curves are checked next.\n\n| ID | Hand/finger | MIDI | Channel | Velocity | ON tick | OFF tick | T_MUSIC ON | T_MUSIC OFF |\n|---|---|---|---|---|---|---|---|---|\n'+'\n'.join(f"| {n['note_id']} | {n['hand']}/{n['finger']} | {n['midi_note']} | {n['channel']} | {n['velocity']} | {n['on_tick']} | {n['off_tick']} | {n['source_on_sec']:.7f} | {n['source_off_sec']:.7f} |" for n in notes)+'\n\nAudio is synthesized once from this shared 23-note timeline using the existing Grand sample algorithm; separate source video soundtracks are not mixed. Detailed data: PERFORMANCE_TIMELINE.json.\n')
print('INPUT_IDENTITY_AND_MIDI_VERIFIED',len(snapshot),'protected files',flush=True)
