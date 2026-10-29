from stage_common import *
import ast
# Reuse the existing frozen-sample PCM adapter verbatim apart from its input/output
# directory/timebase bindings and accurate one-hand scope metadata.
source=OLD/'05_audio.py';text=source.read_text(encoding='utf8')
text=text.replace('from performance_core import *',"from stage_common import *\nTL=read(P/'PERFORMANCE_TIMELINE.json');DURATION=read(P/'SCENE_MANIFEST.json')['frames']/60;FPS=60;PIANO=c.PIANO")
text=text.replace("read(P/'source/PIANO_SAMPLE_MANIFEST.json')","read(OLD/'source/PIANO_SAMPLE_MANIFEST.json')")
text=text.replace("['ffmpeg',","['D:/ffmpeg/bin/ffmpeg.exe',")
text=text.replace("'polyphony_peak_held':2","'polyphony_peak_held':1")
exec(compile(text,str(source),'exec'))
dump('AUDIO_ADAPTER_REUSE.json',dict(source_file=str(source),source_sha256=sha(source),
    original_midi_sha256=sha(SOURCE),voices=16,right_only=True,
    unchanged_sample_mapping=True,unchanged_PCM_algorithm=True,tempo_changed=False,
    original_MIDI_rewritten=False,NOTE_ON_OFF_preserved=True))
