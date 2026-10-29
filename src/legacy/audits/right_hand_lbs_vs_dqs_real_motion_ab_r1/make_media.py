import json, subprocess
from pathlib import Path
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent
FRAMES=[130,76,205,31,61]
for f in FRAMES:
    cv=Image.new('RGB',(1280,1830),(21,28,35));d=ImageDraw.Draw(cv)
    for y,v in enumerate(['FIRST_WEB_CLOSE','PALMAR_THENAR_CLOSE','FIRST_WEB_OBLIQUE']):
        for x,label in enumerate(['LBS','DQS']):
            im=Image.open(OUT/(label.lower()+'_selected')/f'{label}__F{f:03}__{v}.png').convert('RGB');im.thumbnail((640,586))
            cv.paste(im,(x*640,y*610+24));d.text((x*640+6,y*610+5),f'{label} F{f} {v}',fill='white')
    cv.save(OUT/f'AB_F{f:03}_PREVIEW.png')
for v in ['PALMAR_FULL','THENAR_CLOSE','DORSAL_FULL','FIRST_WEB_CLOSE']:
    cv=Image.new('RGB',(1440,1500),(21,28,35));d=ImageDraw.Draw(cv)
    for j,c in enumerate(['ZERO','INDEX_MCP_45','CMC_OPP_30','FULL_OPP_L1','FULL_OPP_L2','FULL_OPP_L3']):
        for k,label in enumerate(['LBS','DQS']):
            im=Image.open(OUT/(label.lower()+'_regression')/f'{label}__{c}__{v}.png').convert('RGB');im.thumbnail((360,476))
            x=(j%2)*720+k*360;y=(j//2)*500
            cv.paste(im,(x,y+24));d.text((x+4,y+5),f'{label} {c}',fill='white')
    cv.save(OUT/f'AB_REGRESSION_{v}_PREVIEW.png')
for s in range(7):
    cv=Image.new('RGB',(1800,1520),(21,28,35));d=ImageDraw.Draw(cv)
    for j,f in enumerate(range(s*30+1,s*30+31)):
        x=(j%3)*600;y=(j//3)*152
        for k,(label,v) in enumerate([(l,v) for l in ['LBS','DQS'] for v in ['PALMAR_MOTION','OBLIQUE_MOTION']]):
            im=Image.open(OUT/(label.lower()+'_motion')/f'{label}__F{f:03}__{v}.png').convert('RGB');im.thumbnail((150,128))
            cv.paste(im,(x+k*150,y+20))
        d.text((x+4,y+2),f'F{f:03} LBS P/O | DQS P/O',fill='white')
    cv.save(OUT/f'AB_FULL_MOTION_QC_{s+1}.png')
records=[]
for v,name in [('PALMAR_MOTION','review_lbs_vs_dqs_palmar.mp4'),('OBLIQUE_MOTION','review_lbs_vs_dqs_first_web.mp4')]:
    for label in ['LBS','DQS']:
        dst=OUT/f'{label.lower()}_{v.lower()}.mp4'
        subprocess.run(['D:/ffmpeg/bin/ffmpeg.exe','-y','-loglevel','error','-framerate','30','-start_number','1','-i',str(OUT/(label.lower()+'_motion')/f'{label}__F%03d__{v}.png'),'-frames:v','210','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dst)],check=True)
    filt="[0:v][1:v]hstack=inputs=2,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='LBS':x=12:y=12:fontcolor=white:fontsize=22:box=1:boxcolor=black@0.6,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='DQS / Preserve Volume':x=652:y=12:fontcolor=white:fontsize=22:box=1:boxcolor=black@0.6[v]"
    subprocess.run(['D:/ffmpeg/bin/ffmpeg.exe','-y','-loglevel','error','-i',str(OUT/f'lbs_{v.lower()}.mp4'),'-i',str(OUT/f'dqs_{v.lower()}.mp4'),'-filter_complex',filt,'-map','[v]','-frames:v','210','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/name)],check=True)
    for name2 in [name,f'lbs_{v.lower()}.mp4',f'dqs_{v.lower()}.mp4']:
        meta=json.loads(subprocess.check_output(['D:/ffmpeg/bin/ffprobe.exe','-v','error','-show_entries','stream=width,height,nb_frames,r_frame_rate:format=duration','-of','json',str(OUT/name2)]))
        assert float(meta['format']['duration'])==7 and meta['streams'][0]['nb_frames']=='210'
        records.append({'file':name2,'metadata':meta})
(OUT/'VIDEO_VERIFICATION_R1.json').write_text(json.dumps({'status':'PASS','videos':records},indent=2),encoding='utf-8')
print('AB_MEDIA_READY')
