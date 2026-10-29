from common import *
sys.path.insert(0,str(OLD/'_deps'))
import mido
midi=safe(ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid');timeline=read(C1/'PERFORMANCE_TIMELINE.json');assert sha(midi)==timeline['source_sha256']
mf=mido.MidiFile(str(midi));raw=[];tempo=[]
for trackno,track in enumerate(mf.tracks):
    tick=0;held={}
    for seq,msg in enumerate(track):
        tick+=msg.time
        if msg.type=='set_tempo':tempo.append([tick,msg.tempo])
        if msg.type in ('note_on','note_off'):
            k=(msg.channel,msg.note)
            if msg.type=='note_on' and msg.velocity:held[k]=(tick,msg.velocity)
            else:
                on,vel=held.pop(k)
                if on<4608:raw.append(dict(track=trackno,channel=msg.channel,midi_note=msg.note,on_tick=on,off_tick=tick,velocity=vel))
assert mf.ticks_per_beat==384 and tempo==[[0,428571]] and len(raw)==23
for n in NOTES:
    assert sum(all(r[k]==n[k] for k in ['track','channel','midi_note','on_tick','off_tick','velocity']) for r in raw)==1
    assert abs(n['note_on']-.35-n['on_tick']*428571/384/1e6)<1e-12
    assert abs(n['note_off']-.35-n['off_tick']*428571/384/1e6)<1e-12
source=read(ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion/PERFORMANCE_TIMELINE.json')['notes']
right=[n for n in NOTES if n['hand']=='R'];assert len(right)==16
for n in right:
    a=next(v for v in source if v['note_id']==n['note_id']);assert all(n[k]==a[k] for k in ['midi_note','key_index','finger','on_tick','off_tick'])
save('FORMAL_MIDI_AND_FINGERING_MAPPING.json',dict(pass_=True,midi_path=str(midi),midi_sha256=sha(midi),all_23_events_match_raw=True,right_16_match_frozen_source_fingering=True,fingering_authority=timeline['fingering_authority'],raw_events=raw))
protection('MIDI_INPUT_SHA_RECEIPT.json');print('MIDI_AND_FINGERING_PASS')
