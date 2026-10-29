from stage_common import *
import subprocess
from PIL import Image,ImageDraw,ImageFont
man=read(P/'SCENE_MANIFEST.json');tl=read(P/'PERFORMANCE_TIMELINE.json');ff='D:/ffmpeg/bin/ffmpeg.exe';fp='D:/ffmpeg/bin/ffprobe.exe';videos={}
groups=sorted(set(n['note_on'] for n in tl['notes']));on=groups[0];off=tl['notes'][-1]['note_off']
phases=[('prepare',on-.10),('chord_down',on+.04),('chord_hold',groups[1]-.15),('chord_to_A3',groups[1]+.04),
    ('B3_down',groups[2]+.04),('B3_hold_next_prepare',groups[3]-.10),('C4_down',groups[3]+.04),('C4_hold',groups[3]+.6),
    ('B3_return',groups[4]+.04),('last_hold',groups[4]+.6),('release',off+.07),('rest',man['frames']/60-1/60)]
for view in man['cameras']:
    framefolder=P/'_frames'/('OVERHEAD_FULL_HAND' if view=='OVERHEAD' and (P/'VIDEO_FRAMING_REPAIR.json').exists() else view)
    assert len(list(framefolder.glob('*.png')))==man['frames']
    dest=P/f'normal_speed_{view.lower()}.mp4'
    subprocess.run([ff,'-y','-v','error','-framerate','60','-i',str(framefolder/'%04d.png'),'-i',str(P/'piano_performance.wav'),
        '-map','0:v','-map','1:a','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(dest)],check=True)
    pr=json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-of','json',str(dest)]));v=next(s for s in pr['streams'] if s['codec_type']=='video');a=next(s for s in pr['streams'] if s['codec_type']=='audio')
    assert int(v['nb_read_frames'])==man['frames'] and v['r_frame_rate']=='60/1'
    assert abs(float(v['duration'])-man['frames']/60)<1e-6 and abs(float(a['duration'])-man['frames']/60)<.001
    subprocess.run([ff,'-v','error','-i',str(dest),'-f','null','-'],check=True)
    videos[dest.name]=dict(sha256=sha(dest),candidate_sha256=man['sha256'],frames=man['frames'],fps=60,
        duration_sec=float(v['duration']),audio_duration_sec=float(a['duration']),normal_speed=True,left_four_bar_only=True,full_decode='PASS')
    sheet=Image.new('RGB',(1920,900),'#eeeadf');d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
    for z,(label,t) in enumerate(phases):
        idx=min(man['frames']-1,round(t*60));x=z%4*480;y=z//4*300
        sheet.paste(Image.open(framefolder/f'{idx:04d}.png').convert('RGB').resize((480,270)),(x,y+30));d.text((x+3,y+3),f'{label} / video {idx/60:.3f}s',font=font,fill='#264b36')
    sheet.save(P/f'phase_sheet_{view.lower()}.jpg',quality=95)
Image.open(P/'_frames/TEACHING'/f'{round((on+.05)*60):04d}.png').convert('RGB').save(P/'review_poster.jpg',quality=95)
dump('VIDEO_VERIFICATION.json',videos);print('ONE_FULL_LEFT_STEM_THREE_COMPLETE_VIEWS',[(n,v['duration_sec']) for n,v in videos.items()],flush=True)
