from pathlib import Path
import sys,json,subprocess,hashlib
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1];C1=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance'
sys.path.insert(0,str(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'))
from PIL import Image,ImageDraw,ImageFont
ff='D:/ffmpeg/bin/ffmpeg.exe';fp='D:/ffmpeg/bin/ffprobe.exe'
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
def run(args):subprocess.run([ff,'-y','-v','error','-threads','4']+args,check=True)
def banner(path,size,texts):
 im=Image.new('RGB',size,'#351518');d=ImageDraw.Draw(im)
 for xy,txt in texts:d.text(xy,txt,font=font,fill='#fff1e7')
 im.save(path)
man=json.loads((P/'RENDER_MANIFEST.json').read_text());videos={}
banner(P/'diagnostic_banner.png',(1280,48),[((12,10),'DIAGNOSTIC_ONLY / NOT_APPROVED   |   Lightweight R1   |   Original speed 1x')])
def verify(dest,frames,fps,duration,audio):
 pr=json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-of','json',str(dest)]));v=next(s for s in pr['streams'] if s['codec_type']=='video')
 assert int(v['nb_read_frames'])==frames and abs(float(v['duration'])-duration)<.02
 aa=[s for s in pr['streams'] if s['codec_type']=='audio'];assert bool(aa)==audio
 if audio:assert abs(float(aa[0]['duration'])-duration)<.025 and float(aa[0].get('start_time',0))==0
 subprocess.run([ff,'-v','error','-i',str(dest),'-f','null','-'],check=True)
 videos[dest.name]=dict(sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),frames=frames,frame_rate=v['r_frame_rate'],duration_sec=float(v['duration']),audio_duration_sec=float(aa[0]['duration']) if aa else None,full_decode='PASS',diagnostic_only=True)
for view in man['cameras']:
 folder=P/'_frames'/view;assert len(list(folder.glob('*.png')))==357
 dest=P/f'normal_speed_{view.lower()}_NOT_APPROVED.mp4'
 run(['-framerate','60','-i',str(folder/'%04d.png'),'-i',str(C1/'piano_performance.wav'),'-i',str(P/'diagnostic_banner.png'),'-filter_complex','[0:v]pad=iw:ih+48:0:48[v0];[v0][2:v]overlay=0:0[v]','-map','[v]','-map','1:a','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t','5.95','-movflags','+faststart',str(dest)])
 verify(dest,357,60,5.95,True)
 comp=P/f'comparison_{view.lower()}_1x_NOT_APPROVED.mp4'
 banner(P/'comparison_banner.png',(1920,48),[((12,10),'SOURCE C1 | 1x'),((970,10),'NEW LIGHTWEIGHT R1 | DIAGNOSTIC_ONLY / NOT_APPROVED')])
 run(['-i',str(C1/f'normal_speed_{view.lower()}.mp4'),'-i',str(dest),'-i',str(C1/'piano_performance.wav'),'-i',str(P/'comparison_banner.png'),'-filter_complex','[0:v]scale=960:540[a];[1:v]crop=1280:720:0:48,scale=960:540[b];[a][b]hstack=inputs=2,pad=iw:ih+48:0:48[c];[c][3:v]overlay=0:0[v]','-map','[v]','-map','2:a','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t','5.95','-movflags','+faststart',str(comp)])
 verify(comp,357,60,5.95,True)
 print('VIDEO_ENCODED_AND_VERIFIED',view,flush=True)
stills=json.loads((P/'STILL_MANIFEST.json').read_text());comps=[]
for row in stills:
 crop=row['crop'];parts=[Image.open(P/'stills'/row['files'][s]).convert('RGB').crop(crop) for s in ['SOURCE','NEW']]
 w,h=parts[0].size;scale=min(2.0,780/w);wh=(round(w*scale),round(h*scale));im=Image.new('RGB',(wh[0]*2,wh[1]+82),'#21191a');d=ImageDraw.Draw(im)
 d.text((12,5),f"{row['label']} | {row['view']} | video t={row['time']:.6f}s | identical crop / scale",font=small,fill='white')
 d.text((12,32),'SOURCE C1',font=font,fill='white');d.text((wh[0]+12,32),'NEW / NOT_APPROVED',font=font,fill='#ffb3ad')
 for i,part in enumerate(parts):im.paste(part.resize(wh,Image.Resampling.LANCZOS),(i*wh[0],82))
 file=f"comparison_{row['label'].lower()}_{row['view'].lower()}.png";im.save(P/file);comps.append(dict(**row,comparison=file))
# Fixed identical crops for short 0.5x auxiliary clips. No sound at slow speed.
for label,a,b in [('EARLY',.95,1.65),('LATE',3.70,3.95),('BLACK_KEYS',2.8,3.45)]:
 view='OVERHEAD';row=next(r for r in stills if r['label']==('BLACK_73' if label=='BLACK_KEYS' else label) and r['view']==view)
 # Generous fixed crop across the full right-hand workspace for motion clips;
 # exact narrower geometry crops are reserved for static matched stills.
 x0,y0,x1,y1=520,70,1120,540;w=(x1-x0)//2*2;h=(y1-y0)//2*2
 a=round(a*60)/60;b=round(b*60)/60;count=round((b-a)*60);dur=count/30
 banner(P/'slow_banner.png',(1280,48),[((12,10),f'{label} | SOURCE C1 / NEW NOT_APPROVED | 0.5x | Silent auxiliary')])
 dest=P/f'local_{label.lower()}_05x_NOT_APPROVED.mp4'
 filt=f'[0:v]trim=start_frame={round(a*60)}:end_frame={round(b*60)},setpts=2*(PTS-STARTPTS),crop={w}:{h}:{x0}:{y0},scale=640:-2[a];[1:v]crop=1280:720:0:48,trim=start_frame={round(a*60)}:end_frame={round(b*60)},setpts=2*(PTS-STARTPTS),crop={w}:{h}:{x0}:{y0},scale=640:-2[b];[a][b]hstack=inputs=2,pad=iw:ih+48:0:48[c];[c][2:v]overlay=0:0[v]'
 run(['-i',str(C1/'normal_speed_overhead.mp4'),'-i',str(P/'normal_speed_overhead_NOT_APPROVED.mp4'),'-i',str(P/'slow_banner.png'),'-filter_complex',filt,'-map','[v]','-an','-r','30','-frames:v',str(count),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)])
 verify(dest,count,30,dur,False)
(P/'COMPARISON_MANIFEST.json').write_text(json.dumps(comps,indent=2),encoding='utf8')
(P/'VIDEO_VERIFICATION.json').write_text(json.dumps(videos,indent=2),encoding='utf8')
Image.open(P/'_frames/TEACHING/0068.png').save(P/'review_poster.png')
print('ALL_MEDIA_VERIFIED',len(videos),flush=True)
