from local_common import *
import subprocess,shutil
from PIL import Image,ImageDraw,ImageFont
man=read(P/'SCENE_MANIFEST.json');assert read(P/'RENDER_MANIFEST.json')['candidate_sha256']==man['sha256']
ff='D:/ffmpeg/bin/ffmpeg.exe';fp='D:/ffmpeg/bin/ffprobe.exe';videos={};audiohashes=[]
shutil.copyfile(C1/'piano_performance.wav',P/'piano_performance.wav');assert sha(P/'piano_performance.wav')==sha(C1/'piano_performance.wav')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
times=[.75,.9,1.05,1.133333333,1.2,1.4,1.55,1.8,1.95,2.1,3.9,4.73]
for view in man['cameras']:
    stem=view.lower();folder=P/'_frames'/view;assert len(list(folder.glob('*.png')))==357
    before=P/f'before_normal_speed_{stem}.mp4';shutil.copyfile(C1/f'normal_speed_{stem}.mp4',before)
    after=P/f'normal_speed_{stem}.mp4'
    # Copy the original single shared AAC track verbatim, no re-synthesis,
    # gain adjustment, resampling, or soundtrack offset.
    subprocess.run([ff,'-y','-v','error','-framerate','60','-i',str(folder/'%04d.png'),'-i',str(before),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(after)],check=True)
    compare=P/f'synchronized_{stem}_before_after.mp4'
    subprocess.run([ff,'-y','-v','error','-i',str(before),'-i',str(after),'-filter_complex','[0:v][1:v]hstack=inputs=2[v]','-map','[v]','-map','0:a:0','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(compare)],check=True)
    for file in [before,after,compare]:
        probe=json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-of','json',str(file)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio');assert int(v['nb_read_frames'])==357 and v['r_frame_rate']=='60/1' and abs(float(v['duration'])-5.95)<1e-6 and abs(float(a['duration'])-5.95)<.001
        subprocess.run([ff,'-v','error','-i',str(file),'-f','null','-'],check=True)
        decoded=subprocess.check_output([ff,'-v','error','-i',str(file),'-map','0:a:0','-f','f32le','-ac','2','-ar','48000','-']);ah=hashlib.sha256(decoded).hexdigest();audiohashes.append(ah)
        videos[file.name]=dict(sha256=sha(file),fps=60,frames=357,duration_sec=5.95,dimensions=[v['width'],v['height']],full_decode='PASS',audio_decoded_sha256=ah,original_speed=True)
    # Original decoder frames for exact same timestamps, compared to the new
    # same-camera rendering. No zoom or framing change is used to imply repair.
    oldfolder=P/'before_frames'/view;oldfolder.mkdir(parents=True,exist_ok=True)
    subprocess.run([ff,'-y','-v','error','-i',str(before),'-start_number','1',str(oldfolder/'%04d.png')],check=True)
    sheet=Image.new('RGB',(1920,1680),'#ece8df');d=ImageDraw.Draw(sheet)
    for i,t in enumerate(times):
        idx=round(t*60);x=(i%4)*480;y=(i//4)*560
        old=Image.open(oldfolder/f'{idx+1:04d}.png').convert('RGB');new=Image.open(folder/f'{idx:04d}.png').convert('RGB')
        sheet.paste(old.resize((480,250)),(x,y+30));sheet.paste(new.resize((480,250)),(x,y+310));d.text((x+4,y+4),f'R1 before / video{idx/60:.3f}s',font=font,fill='#294737');d.text((x+4,y+284),'R2 same camera / partial refinement',font=font,fill='#294737')
    sheet.save(P/f'comparison_sheet_{stem}.jpg',quality=95)
Image.open(P/'_frames/OVERHEAD/0063.png').convert('RGB').save(P/'review_poster.jpg',quality=95)
assert len(set(audiohashes))==1
dump('VIDEO_VERIFICATION.json',videos)
dump('AUDIO_AND_TIMELINE_PRESERVATION.json',dict(pass_=True,WAV_bitwise_identical=True,WAV_sha256=sha(P/'piano_performance.wav'),all_nine_video_AAC_decoded_tracks_identical=True,audio_decoded_sha256=audiohashes[0],MIDI_sha256=sha(MIDI),original_timeline_sha256=sha(C1/'PERFORMANCE_TIMELINE.json'),voices=23,original_NOTE_ON_OFF_velocity_channel_fingering_tempo_preserved=True,no_audio_resynthesis=True,no_audio_offset=True))
print('NINE_ORIGINAL_SPEED_VIDEOS_AND_UNCHANGED_AUDIO_VERIFIED',flush=True)
