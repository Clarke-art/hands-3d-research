from stage_common import *
source=OLD/'05_audio.py';text=source.read_text(encoding='utf8')
text=text.replace('from performance_core import *',"from stage_common import *\nTL=read(P/'PERFORMANCE_TIMELINE.json');DURATION=read(P/'SCENE_MANIFEST.json')['frames']/60;FPS=60;PIANO=c.PIANO")
text=text.replace("read(P/'source/PIANO_SAMPLE_MANIFEST.json')","read(OLD/'source/PIANO_SAMPLE_MANIFEST.json')")
text=text.replace("['ffmpeg',","['D:/ffmpeg/bin/ffmpeg.exe',")
text=text.replace("'polyphony_peak_held':2","'polyphony_peak_held':3")
exec(compile(text,str(source),'exec'))
dump('AUDIO_ADAPTER_REUSE.json',dict(source_file=str(source),source_sha256=sha(source),original_MIDI_sha256=sha(SOURCE),
    voices=len(TL['notes']),left_only=True,unchanged_Grand_sample_mapping=True,unchanged_PCM_algorithm=True,
    original_NOTE_ON_OFF_and_velocity_preserved=True,no_other_notes_or_repetition_added=True,
    original_MIDI_rewritten=False,source_music_duration_sec=read(P/'PERFORMANCE_TIMELINE.json')['source_duration_sec']))
