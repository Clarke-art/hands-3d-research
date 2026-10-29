import json,subprocess,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;SRC=P.parent/'minuet_stage_c_lightweight_animation_poc_r1';C1=P.parent/'minuet_stage_c_r1_dual_hand_synchronized_performance'
ff='D:/ffmpeg/bin/ffmpeg.exe';fp='D:/ffmpeg/bin/ffprobe.exe';font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20);videos={}
def run(args):subprocess.run([ff,'-y','-v','error','-threads','4']+args,check=True)
def banner(name,w,text):
 im=Image.new('RGB',(w,48),'#381b20');ImageDraw.Draw(im).text((12,12),text,font=font,fill='white');im.save(P/name)
def verify(name,count,rate,duration,audio):
 path=P/name;data=json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-of','json',str(path)]));v=next(s for s in data['streams'] if s['codec_type']=='video');aa=[s for s in data['streams'] if s['codec_type']=='audio']
 assert int(v['nb_read_frames'])==count and abs(float(v['duration'])-duration)<.025 and bool(aa)==audio
 assert abs(float(v.get('start_time','0')))<.001
 if aa:assert abs(float(aa[0]['duration'])-duration)<.025
 subprocess.run([ff,'-v','error','-i',str(path),'-f','null','-'],check=True)
 videos[name]=dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),frames=count,frame_rate=v['r_frame_rate'],duration_sec=float(v['duration']),audio=audio,full_decode='PASS',label='DIAGNOSTIC_ONLY / NOT_APPROVED / FAIL_CLOSED')
manifest=json.loads((P/'RENDER_MANIFEST.json').read_text());assert manifest['candidate_sha256']==json.loads((P/'SCENE_MANIFEST.json').read_text())['sha256']
banner('new_banner.png',1280,'NEW PEDAGOGICAL REFINEMENT R1 | DIAGNOSTIC_ONLY / NOT_APPROVED | 1x')
banner('comparison_banner.png',1920,'SOURCE Lightweight R1 (left) | NEW refinement R1 (right) | NOT_APPROVED | same time / camera')
for view in ['TEACHING','OVERHEAD','SIDE_OBLIQUE']:
 name=f'normal_speed_{view.lower()}_NOT_APPROVED.mp4'
 run(['-framerate','60','-i',str(P/f'_frames/{view}/%04d.png'),'-i',str(C1/'piano_performance.wav'),'-i',str(P/'new_banner.png'),'-filter_complex','[0:v]pad=iw:ih+48:0:48[a];[a][2:v]overlay=0:0[v]','-map','[v]','-map','1:a','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t','5.95','-movflags','+faststart',str(P/name)])
 verify(name,357,60,5.95,True)
 comp=f'comparison_{view.lower()}_1x_NOT_APPROVED.mp4'
 run(['-i',str(SRC/name),'-i',str(P/name),'-i',str(C1/'piano_performance.wav'),'-i',str(P/'comparison_banner.png'),'-filter_complex','[0:v]crop=1280:720:0:48,scale=960:540[a];[1:v]crop=1280:720:0:48,scale=960:540[b];[a][b]hstack=inputs=2,pad=iw:ih+48:0:48[c];[c][3:v]overlay=0:0[v]','-map','[v]','-map','2:a','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t','5.95','-movflags','+faststart',str(P/comp)])
 verify(comp,357,60,5.95,True);print('VERIFIED',view,flush=True)
for suffix,fps,duration in [('05x',30,11.9),('025x',15,23.8)]:
 banner('slow_banner.png',1280,f'NEW REFINEMENT R1 | {suffix} SAME ORIGINAL FRAMES / SILENT | DIAGNOSTIC_ONLY / NOT_APPROVED')
 name=f'teaching_{suffix}_NOT_APPROVED.mp4'
 run(['-framerate',str(fps),'-i',str(P/'_frames/TEACHING/%04d.png'),'-i',str(P/'slow_banner.png'),'-filter_complex','[0:v]pad=iw:ih+48:0:48[a];[a][1:v]overlay=0:0[v]','-map','[v]','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-frames:v','357','-movflags','+faststart',str(P/name)])
 verify(name,357,fps,duration,False)
clips=[('B01',.95,1.65),('B02',3.65,4.02),('B03_INDEX',2.35,2.85),('B03_MIDDLE',3.92,4.22),('B03_RING',4.68,5.18)]
for label,a,b in clips:
 start=round(a*60);end=round(b*60);count=end-start;name=f'local_{label}_comparison_05x_NOT_APPROVED.mp4'
 banner('local_banner.png',1280,f'{label} | SOURCE (left) / NEW (right) | 0.5x SILENT | source video {start/60:.3f}-{end/60:.3f}s')
 filt=f'[0:v]crop=1280:720:0:48,trim=start_frame={start}:end_frame={end},setpts=2*(PTS-STARTPTS),crop=640:540:580:60,scale=640:540[a];[1:v]crop=1280:720:0:48,trim=start_frame={start}:end_frame={end},setpts=2*(PTS-STARTPTS),crop=640:540:580:60,scale=640:540[b];[a][b]hstack=inputs=2,pad=iw:ih+48:0:48[c];[c][2:v]overlay=0:0[v]'
 run(['-i',str(SRC/'normal_speed_overhead_NOT_APPROVED.mp4'),'-i',str(P/'normal_speed_overhead_NOT_APPROVED.mp4'),'-i',str(P/'local_banner.png'),'-filter_complex',filt,'-map','[v]','-an','-r','30','-frames:v',str(count),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(P/name)])
 verify(name,count,30,count/30,False)
stills=json.loads((P/'STILL_MANIFEST.json').read_text())
for row in stills:
 parts=[Image.open(P/'stills'/row['files'][s]).convert('RGB') for s in ['SOURCE','NEW']];im=Image.new('RGB',(1920,590),'#17232d');dr=ImageDraw.Draw(im);dr.text((10,8),f"{row['label']} {row['view']} | video {row['time']:.9f}s | SOURCE Lightweight / NEW NOT_APPROVED",font=font,fill='white')
 for i,part in enumerate(parts):im.paste(part.resize((960,540)),(i*960,48))
 im.save(P/f"comparison_{row['label']}_{row['view']}.jpg",quality=95)
(P/'VIDEO_VERIFICATION.json').write_text(json.dumps(videos,indent=2),encoding='utf8')
print('ALL_NEW_MEDIA_VERIFIED',len(videos),flush=True)
