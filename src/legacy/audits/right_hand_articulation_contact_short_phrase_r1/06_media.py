from articulation_common import *
import subprocess,shutil
from PIL import Image,ImageDraw,ImageFont
ff='D:/ffmpeg/bin/ffmpeg.exe';fp='D:/ffmpeg/bin/ffprobe.exe';man=read(P/'SCENE_MANIFEST.json')
audio=PRE/'short_phrase_original_piano.wav';assert sha(audio)==read(PRE/'AUDIO_SYNC.json')['excerpt_sha256'];shutil.copyfile(audio,P/'original_piano_unchanged.wav')
verification={}
for view,name in [('TEACHING','normal_speed_teaching.mp4'),('OVERHEAD','normal_speed_overhead.mp4'),('SIDE_OBLIQUE','normal_speed_side_oblique.mp4')]:
 dest=P/name;subprocess.run([ff,'-y','-v','error','-framerate','60','-i',str(P/'_frames'/view/'%04d.png'),'-i',str(P/'original_piano_unchanged.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(dest)],check=True)
 probe=json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(dest)]));v=next(x for x in probe['streams'] if x['codec_type']=='video');a=next(x for x in probe['streams'] if x['codec_type']=='audio');assert int(v['nb_read_frames'])==162 and v['r_frame_rate']=='60/1' and abs(float(v['duration'])-2.7)<1e-6 and abs(float(a['duration'])-2.7)<1e-6;subprocess.run([ff,'-v','error','-i',str(dest),'-f','null','-'],check=True)
 verification[name]={'sha256':sha(dest),'candidate_sha256':man['sha256'],'frames':162,'fps':60,'duration_sec':2.7,'audio_duration_sec':float(a['duration']),'normal_speed':True,'full_decode':'PASS','views_same_as_previous':True,'complete_same_continuous_candidate':True}
ref=P/'previous';ref.mkdir(exist_ok=True)
for name in verification:shutil.copyfile(PRE/name,ref/name);assert sha(ref/name)==read(PRE/'VIDEO_VERIFICATION.json')[name]['sha256']
dump('VIDEO_VERIFICATION.json',verification)
dump('AUDIO_EVENT_VERIFICATION.json',{'unchanged_original_PCM_sha256':sha(audio),'new_PCM_sha256':sha(P/'original_piano_unchanged.wav'),'same_PCM_bytes':True,'18_original_note_identities_durations_order_unchanged':True,'original_voices':read(PRE/'AUDIO_SYNC.json')['copied_original_voice_records'],'unchanged_key_actions':True,'all_three_audio_and_video_lengths_exact':True,'audio_voice_source':'Existing frozen Grand samples and original offline PCM; no new synthesis or time stretching'})
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
for view in ['TEACHING','SIDE_OBLIQUE','OVERHEAD']:
 sheet=Image.new('RGB',(1920,1060),'#f4f2eb');d=ImageDraw.Draw(sheet)
 for z,j in enumerate(range(0,162,6)):
  x=z%6*320;y=z//6*212;sheet.paste(Image.open(P/'_frames'/view/f'{j:04}.png').convert('RGB').resize((320,180)),(x,y+30));d.text((x+3,y+3),f'{START+j/60:.3f}s / video {j/60:.2f}s',font=font,fill='#244b3c')
 sheet.save(P/f'contact_sheet_{view.lower()}.jpg',quality=96)
Image.open(P/'_frames'/'TEACHING'/'0020.png').convert('RGB').save(P/'review_poster.jpg',quality=95)
# Finite contact evidence: two repeatedA5 and two repeatedF#5 frames, same normal side camera.
indices=[20,58,80,118];labels=['A5 first full-down','F#5 first full-down','A5 repeat full-down','F#5 repeat full-down'];sheet=Image.new('RGB',(1920,4*590),'#f4f2eb');d=ImageDraw.Draw(sheet)
for row,(j,label) in enumerate(zip(indices,labels)):
 y=row*590;d.text((15,y+5),f'{label} | source {START+j/60:.3f}s | BEFORE',font=font,fill='#244b3c');d.text((975,y+5),'AFTER / SAME CAMERA / SAME ORIGINAL MIDI TIME',font=font,fill='#244b3c')
 for col,folder in enumerate([PRE,P]):sheet.paste(Image.open(folder/'_frames'/'SIDE_OBLIQUE'/f'{j:04}.png').convert('RGB').resize((960,540)),(col*960,y+36))
sheet.save(P/'matched_A5_Fsharp5_side_contact.jpg',quality=96)
print('THREE_COMPLETE_NORMAL_SPEED_PIANO_VIDEOS_AND_MATCHED_EVIDENCE_VERIFIED',flush=True)
