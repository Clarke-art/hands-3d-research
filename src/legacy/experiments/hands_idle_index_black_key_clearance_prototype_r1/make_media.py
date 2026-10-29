from common import *
import subprocess
from PIL import Image,ImageDraw,ImageFont
FF='D:/ffmpeg/bin/ffmpeg.exe';FP='D:/ffmpeg/bin/ffprobe.exe'
def run(args):
 r=subprocess.run(args,cwd=OUT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf8',errors='replace')
 if r.returncode:raise RuntimeError(r.stderr[-4000:])
 return r.stdout
font=lambda size:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)
source=C1/'normal_speed_overhead.mp4';READS[str(source)]=sha(source)
orig=OUT/'original_video_frames';orig.mkdir(exist_ok=False)
run([FF,'-v','error','-i',str(source),'-vf',r'select=between(n\,0\,81)+between(n\,126\,201)','-vsync','0','-start_number','0',str(orig/'%04d.png')])
seq=read(OUT/'RENDER_SEQUENCE.json');folder=OUT/'comparison_frames';folder.mkdir(exist_ok=False)
for r in seq['frames']:
 ix=r['index'];a=Image.open(orig/f'{ix:04d}.png').convert('RGB');b=Image.open(r['path']).convert('RGB');assert a.size==b.size==(1280,720)
 canvas=Image.new('RGB',(2560,840),'#101723');canvas.paste(a,(0,86));canvas.paste(b,(1280,86));d=ImageDraw.Draw(canvas)
 for x,title in [(18,'原 C1 · ORIGINAL'),(1298,'实验 B · NOT_APPROVED')]:
  d.text((x,8),title,font=font(30),fill='#ffffff');d.text((x,49),f"{'窗口 A + A4 准备/触键' if ix<82 else '窗口 B + 前后过渡'} | 源时间 {r['time']:.6f}s | 正交俯视",font=font(22),fill='#b9cce4')
 d.text((18,811),'同源时刻并排；两段间为明确时间跳切。红色碰撞证据请见独立标注图。PARTIAL / Human Review',font=font(19),fill='#ffcf77')
 canvas.save(folder/f'{ix:04d}.png')
audio=OUT/'comparison_audio.wav'
filters='[0:a]atrim=start=0:end=1.366666666667,asetpts=PTS-STARTPTS[a];[0:a]atrim=start=2.1:end=3.366666666667,asetpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=0:a=1[out]'
run([FF,'-v','error','-i',str(source),'-filter_complex',filters,'-map','[out]','-c:a','pcm_s16le',str(audio)])
video=OUT/'C1_VS_IDLE_INDEX_B_OVERHEAD_1X.mp4'
run([FF,'-v','error','-framerate','60','-start_number','0','-i',str(folder/'%04d.png'),'-i',str(audio),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',str(video)])
slow=OUT/'C1_VS_IDLE_INDEX_B_OVERHEAD_0_5X.mp4'
run([FF,'-v','error','-i',str(video),'-filter_complex','[0:v]setpts=2*PTS[v];[0:a]atempo=0.5[a]','-map','[v]','-map','[a]','-r','60','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(slow)])
stills=read(OUT/'STILL_GEOMETRY_PROJECTIONS.json')
for label in ['A','B']:
 panel=Image.new('RGB',(2560,1120),'#101723');d=ImageDraw.Draw(panel)
 for col,identity in enumerate(['ORIGINAL_C1','CANDIDATE_B']):
  r=next(r for r in stills if r['label']==label and r['identity']==identity);im=Image.open(r['path']).convert('RGB');draw=ImageDraw.Draw(im);w=max(r['witnesses'],key=lambda x:x['depth_mm']);px,py=w['pixel']
  draw.ellipse((px-9,py-9,px+9,py+9),outline='#ff334f',width=3);draw.line([(px+10,py),(px+70,py-40)],fill='#ff334f',width=2);draw.text((px+72,py-60),f"{w['key']} {w['depth_mm']:.3f}mm",font=font(22),fill='#ff334f')
  x=col*1280;panel.paste(im,(x,72));d.text((x+18,10),f"{identity} | t={r['time']:.6f}s | IDLE INDEX",font=font(29),fill='white')
  crop=im.crop((int(px)-100,int(py)-100,int(px)+100,int(py)+100)).resize((280,280));panel.paste(crop,(x+18,811))
  lines=[f"碰撞键：{w['key']}",f"真实三角面穿入深度：{w['depth_mm']:.6f} mm",'几何关系：仍相交；净空为 0 mm',f"皮肤三角形顶点：{w['triangle']}",'红圈为三维内部见证点的相机投影；','可被琴键遮挡，不表示该点裸露可见。','下方仅为同一正俯视画面局部放大。']
  for j,line in enumerate(lines):d.text((x+320,815+j*37),line,font=font(23),fill='#ff9b9b' if j<3 else '#c4d2e5')
 panel.save(OUT/f'{label}_BEFORE_AFTER_GEOMETRY.png')
meta={}
for p in [video,slow]:
 meta[p.name]=json.loads(run([FP,'-v','error','-show_streams','-show_format','-of','json',str(p)]))
save('MEDIA_METADATA.json',dict(videos=meta,frames=len(seq['frames']),source_frame_ranges=[[1,82],[127,202]],source_time_ranges=[[0,81/60],[2.1,201/60]],source_sha256=sha(source),sha256={p.name:sha(p) for p in [video,slow,OUT/'A_BEFORE_AFTER_GEOMETRY.png',OUT/'B_BEFORE_AFTER_GEOMETRY.png']},audio='Original C1 audio trimmed with identical shot boundaries; half-speed uses atempo=0.5'))
protection('MEDIA_INPUT_RECEIPT.json');print('MEDIA_DONE',flush=True)
