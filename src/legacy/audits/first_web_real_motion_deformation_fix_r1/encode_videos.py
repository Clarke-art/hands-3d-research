import sys,json,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent
tag=sys.argv[1] if len(sys.argv)>1 else 'WEIGHT_1'
ffmpeg='D:/ffmpeg/bin/ffmpeg.exe'
ffprobe='D:/ffmpeg/bin/ffprobe.exe'
records=[]
for v in ['PALMAR_MOTION','OBLIQUE_MOTION']:
    for label in ['BEFORE',tag]:
        dst=OUT/f'{label.lower()}_{v.lower()}.mp4'
        if label!='BEFORE' or not dst.exists():
            pattern=OUT/(label.lower()+'_motion')/f'{label}__F%03d__{v}.png'
            subprocess.run([ffmpeg,'-y','-loglevel','error','-framerate','30','-start_number','1','-i',str(pattern),'-frames:v','210','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dst)],check=True)
        meta=json.loads(subprocess.check_output([ffprobe,'-v','error','-show_entries','stream=width,height,nb_frames,r_frame_rate:format=duration','-of','json',str(dst)]))
        assert float(meta['format']['duration'])==7 and meta['streams'][0]['nb_frames']=='210'
        records.append({'file':dst.name,'metadata':meta})
    name=('review_before_after.mp4' if v=='PALMAR_MOTION' else 'review_before_after_oblique.mp4') if tag=='FINAL' else f'{tag.lower()}_before_after_{v.lower()}.mp4'
    dst=OUT/name
    # Left BEFORE, right AFTER. Labels remain in the video when downloaded independently.
    filt="[0:v][1:v]hstack=inputs=2,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='BEFORE':x=12:y=12:fontcolor=white:fontsize=22:box=1:boxcolor=black@0.6,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='AFTER':x=652:y=12:fontcolor=white:fontsize=22:box=1:boxcolor=black@0.6[v]"
    subprocess.run([ffmpeg,'-y','-loglevel','error','-i',str(OUT/f'before_{v.lower()}.mp4'),'-i',str(OUT/f'{tag.lower()}_{v.lower()}.mp4'),'-filter_complex',filt,'-map','[v]','-frames:v','210','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dst)],check=True)
    meta=json.loads(subprocess.check_output([ffprobe,'-v','error','-show_entries','stream=width,height,nb_frames,r_frame_rate:format=duration','-of','json',str(dst)]))
    assert float(meta['format']['duration'])==7 and meta['streams'][0]['nb_frames']=='210'
    records.append({'file':name,'metadata':meta})
(OUT/f'{tag}_VIDEO_VERIFICATION_R1.json').write_text(json.dumps({'status':'PASS','videos':records},indent=2),encoding='utf-8')
print('VIDEOS_READY',tag)
