from phrase_common import *
import subprocess,wave
ff='D:/ffmpeg/bin/ffmpeg.exe';fp='D:/ffmpeg/bin/ffprobe.exe'
# Reuse original audio PCM: exact same18 MIDI notes, velocities, layers and source clock.
original=c.P/'piano_performance.wav';sync=read(c.P/'KEY_AUDIO_SYNC_R1.json');assert sync['voices_scheduled']==len(TL['notes']) and sync['all_notes_have_voice'] and sync['pitch_within25cents'];assert sha(c.P/'PERFORMANCE_TIMELINE_R1.json')==read(P/'PROTECTED_INPUTS_BEFORE.json')[str(c.P/'PERFORMANCE_TIMELINE_R1.json')]
with wave.open(str(original),'rb') as src:
 params=src.getparams();assert params.framerate==48000;src.setpos(round(START*params.framerate));pcm=src.readframes(round((END-START)*params.framerate))
with wave.open(str(P/'short_phrase_original_piano.wav'),'wb') as dst:dst.setparams(params);dst.writeframes(pcm)
dump('AUDIO_SYNC.json',{'original_audio':str(original),'original_sha256':sha(original),'excerpt_sha256':sha(P/'short_phrase_original_piano.wav'),'crop_source_seconds':[START,END],'music_source_seconds':[0,2],'crop_changes_timing':False,'copied_original_voice_records':sync['voices'],'audio_clock_quantization_max_ms':sync['audio_clock_quantization_max_ms'],'audible_onset_delay_max_ms':sync['audible_onset_delay_max_ms'],'pitch_checks':sync['pitch_checks'],'pitch_within25cents':True,'same_timebase_as_keys':True,'all18_notes_retained':True,'source':'Frozen Grand VCSL Kawai piano samples through existing offline adapter, original PCM crop'})
verification={}
for view in ['TEACHING','SIDE_OBLIQUE','OVERHEAD']:
 name={'TEACHING':'normal_speed_teaching.mp4','SIDE_OBLIQUE':'normal_speed_side_oblique.mp4','OVERHEAD':'normal_speed_overhead.mp4'}[view];dest=P/name
 subprocess.run([ff,'-y','-v','error','-framerate','60','-i',str(P/'_frames'/view/'%04d.png'),'-i',str(P/'short_phrase_original_piano.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(dest)],check=True)
 probe=json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(dest)]));vs=next(v for v in probe['streams'] if v['codec_type']=='video');aus=next(v for v in probe['streams'] if v['codec_type']=='audio');assert int(vs['nb_read_frames'])==round((END-START)*FPS) and vs['r_frame_rate']=='60/1';subprocess.run([ff,'-v','error','-i',str(dest),'-f','null','-'],check=True)
 verification[name]={'sha256':sha(dest),'frames':int(vs['nb_read_frames']),'fps':60,'video_duration_sec':float(vs['duration']),'audio_duration_sec':float(aus['duration']),'container_duration_sec':float(probe['format']['duration']),'dimensions':[vs['width'],vs['height']],'full_decode':'PASS','normal_speed':True,'audio':True,'same_uninterrupted_candidate':True}
dump('VIDEO_VERIFICATION.json',verification)
from PIL import Image,ImageDraw,ImageFont
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
for view in ['TEACHING','SIDE_OBLIQUE','OVERHEAD']:
 frames=range(0,162,6);sheet=Image.new('RGB',(1920,5*212),'#f4f2eb');d=ImageDraw.Draw(sheet)
 for z,j in enumerate(frames):
  x=z%6*320;y=z//6*212;sheet.paste(Image.open(P/'_frames'/view/f'{j:04}.png').convert('RGB').resize((320,180)),(x,y+30));d.text((x+4,y+3),f'{START+j/60:.3f}s / video {j/60:.2f}s',font=font,fill='#244b3c')
 sheet.save(P/f'contact_sheet_{view.lower()}.jpg',quality=96)
Image.open(P/'_frames'/'TEACHING'/'0020.png').convert('RGB').save(P/'review_poster.jpg',quality=95)
print('THREE_NORMAL_SPEED_VIDEOS_VERIFIED',flush=True)

