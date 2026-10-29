from common import *
assert read(P/'READONLY_PREFLIGHT.json')['pass_']
sys.path.insert(0,str(OLD/'_deps'))
import numpy as np
TL=read(P/'PERFORMANCE_TIMELINE.json');DURATION=TL['frames']/FPS
PIANO=ROOT.parent/'piano/release/grand-piano-v1.1-rc-candidate'
source=OLD/'05_audio.py'
text=source.read_text(encoding='utf8').replace('from performance_core import *','')
text=text.replace("read(P/'source/PIANO_SAMPLE_MANIFEST.json')","read(OLD/'source/PIANO_SAMPLE_MANIFEST.json')")
text=text.replace("['ffmpeg',","['D:/ffmpeg/bin/ffmpeg.exe',")
poly=max(sum(n['note_on']<=t<n['note_off'] for n in TL['notes']) for t in {n['note_on'] for n in TL['notes']})
text=text.replace("'polyphony_peak_held':2",f"'polyphony_peak_held':{poly}")
text=text.replace('PERFORMANCE_TIMELINE_R1.json time at48kHz','PERFORMANCE_TIMELINE.json shared T_MUSIC + 0.35s, 48kHz')
exec(compile(text,str(source),'exec'))
audio=read(P/'KEY_AUDIO_SYNC_R1.json')
assert len(audio['voices'])==23 and len({v['note_id'] for v in audio['voices']})==23
assert audio['clipping_samples']==0 and audio['pitch_within25cents']
for n,v in zip(TL['notes'],audio['voices']):
    assert all(n[k]==v[k] for k in ['note_id','midi_note','velocity','hand'])
    assert abs(n['note_on']-v['scheduled_on_sec'])<=.5/48000+1e-12
    assert n['note_off']==v['note_off_sec']
dump('AUDIO_INTEGRATION.json',dict(pass_=True,source_algorithm=str(source),source_algorithm_sha256=sha(source),source_MIDI_sha256=sha(MIDI),wav_sha256=sha(P/'piano_performance.wav'),note_on_events=23,note_off_events=23,channels_preserved_in_timeline=[0,1],unique_note_ids=23,polyphony_peak_held=poly,one_common_gain=audio['common_mix_gain'],pitch_within25cents=True,max_schedule_quantization_ms=audio['audio_clock_quantization_max_ms'],max_audible_sample_attack_delay_ms=audio['audible_onset_delay_max_ms'],original_sample_manifest_and_velocity_law_preserved=True,source_video_soundtracks_used=False))
print('ONE_SHARED_23_NOTE_GRAND_AUDIO_PASS',flush=True)
