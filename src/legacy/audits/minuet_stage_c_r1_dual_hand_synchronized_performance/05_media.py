from common import *
import subprocess,shutil
from PIL import Image,ImageDraw,ImageFont
man=read(P/'SCENE_MANIFEST.json');assert read(P/'RENDER_MANIFEST.json')['candidate_sha256']==man['sha256']
ff='D:/ffmpeg/bin/ffmpeg.exe';fp='D:/ffmpeg/bin/ffprobe.exe';videos={}
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
tl=read(P/'PERFORMANCE_TIMELINE.json')
phases=[('Preparation',.20),('D5 + G3/B3/D4',.39),('G4 melody + chord',.82),('B4 + A3',1.25),('D5 + B3',1.70),('G4 first repeat',2.54),('E5 + C4',3.05),('F#5 + C4',4.02),('G5 + B3',4.28),('Octave return G4',4.70),('G4 second repeat',5.08),('Release',5.62)]
for view in man['cameras']:
    folder=P/'_frames'/view;assert len(list(folder.glob('*.png')))==357
    dest=P/f'normal_speed_{view.lower()}.mp4'
    subprocess.run([ff,'-y','-v','error','-framerate','60','-i',str(folder/'%04d.png'),'-i',str(P/'piano_performance.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(dest)],check=True)
    pr=json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-of','json',str(dest)]));v=next(s for s in pr['streams'] if s['codec_type']=='video');a=next(s for s in pr['streams'] if s['codec_type']=='audio')
    assert int(v['nb_read_frames'])==357 and v['r_frame_rate']=='60/1' and abs(float(v['duration'])-5.95)<1e-6 and abs(float(a['duration'])-5.95)<.001
    subprocess.run([ff,'-v','error','-i',str(dest),'-f','null','-'],check=True)
    videos[dest.name]=dict(sha256=sha(dest),candidate_sha256=man['sha256'],frames=357,fps=60,video_duration_sec=float(v['duration']),audio_duration_sec=float(a['duration']),audio_start_sec=float(a.get('start_time',0)),video_start_sec=float(v.get('start_time',0)),full_decode='PASS',normal_speed=True,two_hands_in_one_real_scene=True)
    sheet=Image.new('RGB',(1920,900),'#ece8de');d=ImageDraw.Draw(sheet)
    for i,(name,t) in enumerate(phases):
        idx=round(t*60);x=(i%4)*480;y=(i//4)*300
        sheet.paste(Image.open(folder/f'{idx:04d}.png').convert('RGB').resize((480,270)),(x,y+30))
        d.text((x+4,y+4),f'{name} / {t-LEAD:.3f}s music',font=font,fill='#183d36')
    sheet.save(P/f'phase_sheet_{view.lower()}.jpg',quality=95)
Image.open(P/'_frames/TEACHING/0024.png').convert('RGB').save(P/'review_poster.jpg',quality=95)
dump('VIDEO_VERIFICATION.json',videos)
print('THREE_FULL_ORIGINAL_SPEED_DUAL_HAND_VIDEOS_PASS',flush=True)
