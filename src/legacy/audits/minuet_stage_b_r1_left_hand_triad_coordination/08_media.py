from stage_common import *
import subprocess
from PIL import Image,ImageDraw,ImageFont
man=read(P/'SCENE_MANIFEST.json');ff='D:/ffmpeg/bin/ffmpeg.exe';fp='D:/ffmpeg/bin/ffprobe.exe';verification={}
notes=read(P/'PERFORMANCE_TIMELINE.json')['notes'];on=notes[0]['note_on'];off=notes[0]['note_off']
phases=[('prepare',on-.10),('touch',on),('down',on+.04),('hold',on+.4),('off',off),('return',off+.07),('recover',off+.25),('rest',man['frames']/60-1/60)]
for view in man['cameras']:
    assert len(list((P/'_frames'/view).glob('*.png')))==man['frames']
    dest=P/f'normal_speed_{view.lower()}.mp4'
    subprocess.run([ff,'-y','-v','error','-framerate','60','-i',str(P/'_frames'/view/'%04d.png'),'-i',str(P/'piano_performance.wav'),
        '-map','0:v','-map','1:a','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(dest)],check=True)
    probe=json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(dest)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert int(v['nb_read_frames'])==man['frames'] and v['r_frame_rate']=='60/1'
    assert abs(float(v['duration'])-man['frames']/60)<1e-6 and abs(float(a['duration'])-man['frames']/60)<.001
    subprocess.run([ff,'-v','error','-i',str(dest),'-f','null','-'],check=True)
    verification[dest.name]=dict(sha256=sha(dest),candidate_sha256=man['sha256'],frames=man['frames'],fps=60,
        duration_sec=float(v['duration']),audio_duration_sec=float(a['duration']),normal_speed=True,left_triad_only=True,full_decode='PASS')
    sheet=Image.new('RGB',(1920,600),'#ece9df');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    for z,(label,t) in enumerate(phases):
        idx=min(man['frames']-1,round(t*60));x=z%4*480;y=z//4*300
        sheet.paste(Image.open(P/'_frames'/view/f'{idx:04d}.png').convert('RGB').resize((480,270)),(x,y+30))
        draw.text((x+4,y+3),f'{label} | video {idx/60:.3f}s',font=font,fill='#244936')
    sheet.save(P/f'phase_sheet_{view.lower()}.jpg',quality=95)
idx=round((on+.05)*60);Image.open(P/'_frames'/ 'TEACHING'/f'{idx:04d}.png').convert('RGB').save(P/'review_poster.jpg',quality=95)
dump('VIDEO_VERIFICATION.json',verification)
print('ONE_LEFT_TRIAD_THREE_COMPLETE_VIEWS',[(n,v['duration_sec']) for n,v in verification.items()],flush=True)
