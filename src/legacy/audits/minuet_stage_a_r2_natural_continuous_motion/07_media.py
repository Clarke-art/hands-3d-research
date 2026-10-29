from stage_common import *
import subprocess
from PIL import Image,ImageDraw,ImageFont
man=read(P/'SCENE_MANIFEST.json');ff='D:/ffmpeg/bin/ffmpeg.exe';fp='D:/ffmpeg/bin/ffprobe.exe';verification={}
for view in man['cameras']:
    files=list((P/'_frames'/view).glob('*.png'));assert len(files)==man['frames']
    dest=P/f'normal_speed_{view.lower()}.mp4'
    subprocess.run([ff,'-y','-v','error','-framerate','60','-i',str(P/'_frames'/view/'%04d.png'),
        '-i',str(P/'piano_performance.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-crf','18',
        '-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(dest)],check=True)
    probe=json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(dest)]))
    v=next(x for x in probe['streams'] if x['codec_type']=='video');a=next(x for x in probe['streams'] if x['codec_type']=='audio')
    assert int(v['nb_read_frames'])==man['frames'] and v['r_frame_rate']=='60/1'
    assert abs(float(v['duration'])-man['frames']/60)<1e-6 and abs(float(a['duration'])-man['frames']/60)<.001
    subprocess.run([ff,'-v','error','-i',str(dest),'-f','null','-'],check=True)
    verification[dest.name]=dict(sha256=sha(dest),candidate_sha256=man['sha256'],frames=man['frames'],
        fps=60,duration_sec=float(v['duration']),audio_duration_sec=float(a['duration']),
        normal_speed=True,right_only=True,full_decode='PASS')
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
    ns=read(P/'PERFORMANCE_TIMELINE.json')['notes'];sheet=Image.new('RGB',(1920,960),'#eeeade');draw=ImageDraw.Draw(sheet)
    for j,n in enumerate(ns):
        idx=round((n['note_on']+.06)*60);x=j%4*480;y=j//4*240
        sheet.paste(Image.open(P/'_frames'/view/f'{idx:04}.png').convert('RGB').resize((480,210)),(x,y+30))
        draw.text((x+4,y+3),f"{n['note_id']} {n['note_name']} / finger {n['finger']} / {idx/60:.3f}s",font=font,fill='#223d34')
    sheet.save(P/f'contact_sheet_{view.lower()}.jpg',quality=94)
Image.open(P/'_frames/TEACHING/0021.png').convert('RGB').save(P/'review_poster.jpg',quality=95)
dump('VIDEO_VERIFICATION.json',verification)
print('THREE_VIEWS_OF_ONE_CANDIDATE',[(n,v['duration_sec']) for n,v in verification.items()])
