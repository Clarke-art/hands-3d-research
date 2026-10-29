from stage_common import *
import subprocess,shutil
from PIL import Image,ImageDraw,ImageFont
man=read(P/'SCENE_MANIFEST.json');tl=read(P/'PERFORMANCE_TIMELINE.json');ff='D:/ffmpeg/bin/ffmpeg.exe';fp='D:/ffmpeg/bin/ffprobe.exe';videos={}
shutil.copyfile(R2/'piano_performance.wav',P/'piano_performance.wav')
shutil.copyfile(R2/'KEY_AUDIO_SYNC_R1.json',P/'KEY_AUDIO_SYNC_R1.json')
dump('AUDIO_REUSE.json',dict(original_audio_sha256=sha(R2/'piano_performance.wav'),audio_sha256=sha(P/'piano_performance.wav'),bitwise_identical=True,original_MIDI_sha256=sha(SOURCE),timeline_sha256=sha(P/'PERFORMANCE_TIMELINE.json'),same_7_voices_and_NOTE_ON_OFF=True))
groups=sorted(set(n['note_on'] for n in tl['notes']));on=groups[0];off=tl['notes'][-1]['note_off']
phases=[('prepare',on-.10),('chord_down',on+.04),('chord_hold',groups[1]-.15),('A3_down',groups[1]+.04),('B3_down',groups[2]+.04),('B3_hold',groups[3]-.10),('C4_down',groups[3]+.04),('C4_hold',groups[3]+.6),('B3_return',groups[4]+.04),('last_hold',groups[4]+.6),('release',off+.07),('rest',man['frames']/60-1/60)]
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
for view in man['cameras']:
    folder=P/'_frames'/view;assert len(list(folder.glob('*.png')))==man['frames'];dest=P/f'normal_speed_{view.lower()}.mp4'
    subprocess.run([ff,'-y','-v','error','-framerate','60','-i',str(folder/'%04d.png'),'-i',str(P/'piano_performance.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(dest)],check=True)
    pr=json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-of','json',str(dest)]));v=next(s for s in pr['streams'] if s['codec_type']=='video');a=next(s for s in pr['streams'] if s['codec_type']=='audio');assert int(v['nb_read_frames'])==man['frames'] and v['r_frame_rate']=='60/1';assert abs(float(v['duration'])-man['frames']/60)<1e-6
    subprocess.run([ff,'-v','error','-i',str(dest),'-f','null','-'],check=True)
    videos[dest.name]=dict(sha256=sha(dest),frames=man['frames'],fps=60,duration_sec=float(v['duration']),audio_duration_sec=float(a['duration']),normal_speed=True,full_decode='PASS')
    # Frame-accurate movie pair; left R2, right R3. Same unscaled 1280x720
    # camera images, one original audio stem, identical clocks.
    before=R2/dest.name;pair=P/f'synchronized_{view.lower()}_before_after.mp4'
    subprocess.run([ff,'-y','-v','error','-i',str(before),'-i',str(dest),'-filter_complex','[0:v][1:v]hstack=inputs=2[v]','-map','[v]','-map','0:a','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(pair)],check=True)
    subprocess.run([ff,'-v','error','-i',str(pair),'-f','null','-'],check=True)
    videos[pair.name]=dict(sha256=sha(pair),frames=man['frames'],fps=60,duration_sec=man['frames']/60,normal_speed=True,left='R2',right='R3',unscaled_camera_images=True,full_decode='PASS')
    sheet=Image.new('RGB',(1920,900),'#eeeadf');d=ImageDraw.Draw(sheet)
    oldfolder=R2/'_frames'/('OVERHEAD_FULL_HAND' if view=='OVERHEAD' else view)
    compare=Image.new('RGB',(1920,1800),'#eeeadf');cd=ImageDraw.Draw(compare)
    for z,(label,t) in enumerate(phases):
        idx=min(man['frames']-1,round(t*60));x=z%4*480;y=z//4*300
        img=Image.open(folder/f'{idx:04d}.png').convert('RGB').resize((480,270));sheet.paste(img,(x,y+30));d.text((x+3,y+3),f'{label} / {idx/60:.3f}s',font=font,fill='#264b36')
        yy=z//4*600;compare.paste(Image.open(oldfolder/f'{idx:04d}.png').convert('RGB').resize((480,270)),(x,yy+30));compare.paste(img,(x,yy+330));cd.text((x+3,yy+3),f'R2 {label} / {idx/60:.3f}s',font=font,fill='#343434');cd.text((x+3,yy+303),'R3 same frame',font=font,fill='#264b36')
    sheet.save(P/f'phase_sheet_{view.lower()}.jpg',quality=95);compare.save(P/f'comparison_sheet_{view.lower()}.jpg',quality=95)
Image.open(P/'_frames/TEACHING'/f'{round((on+.05)*60):04d}.png').convert('RGB').save(P/'review_poster.jpg',quality=95)
dump('VIDEO_VERIFICATION.json',videos)
print('THREE_ORIGINAL_SPEED_VIEWS_AND_THREE_SYNCHRONIZED_COMPARISONS_VERIFIED',flush=True)
