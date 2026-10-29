from common import *
import subprocess
from PIL import Image,ImageDraw,ImageFont
FF='D:/ffmpeg/bin/ffmpeg.exe';FP='D:/ffmpeg/bin/ffprobe.exe'
def run(args):
 p=subprocess.run(args,cwd=OUT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf8',errors='replace')
 if p.returncode:raise RuntimeError(p.stderr[-3000:])
 return p.stdout
font=lambda size:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)
source=C1/'normal_speed_overhead.mp4';READS[str(source)]=sha(source)
orig=OUT/'tail_original_frames';orig.mkdir(exist_ok=True)
if not (orig/'0014.png').exists():run([FF,'-v','error','-i',str(source),'-vf',r'select=between(n\,202\,216)','-vsync','0','-start_number','0',str(orig/'%04d.png')])
folder=OUT/'final_comparison_frames';folder.mkdir(exist_ok=True)
for i in range(158):
 # Preserve preliminary media and frame evidence; independent final sequence.
 dest=folder/f'{i:04d}.png';src=OUT/'comparison_frames'/f'{i:04d}.png'
 if dest.exists():assert sha(dest)==sha(src)
 else:
  with dest.open('xb') as f:f.write(src.read_bytes())
for r in read(OUT/'TAIL_RENDER_SEQUENCE.json')['frames']:
 ix=r['index'];a=Image.open(orig/f'{ix:04d}.png').convert('RGB');b=Image.open(r['path']).convert('RGB')
 canvas=Image.new('RGB',(2560,840),'#101723');canvas.paste(a,(0,86));canvas.paste(b,(1280,86));d=ImageDraw.Draw(canvas)
 for x,title in [(18,'原 C1 · ORIGINAL'),(1298,'实验 B · NOT_APPROVED')]:
  d.text((x,8),title,font=font(30),fill='white');d.text((x,49),f"窗口 B 后续回归 | 源时间 {r['time']:.6f}s | 正交俯视",font=font(22),fill='#b9cce4')
 d.text((18,811),'同源时刻并排；两段间为明确时间跳切。红色碰撞证据请见独立标注图。PARTIAL / Human Review',font=font(19),fill='#ffcf77')
 canvas.save(folder/f'{ix+158:04d}.png')
audio=OUT/'final_comparison_audio.wav';duration=173/60
filters='[0:a]atrim=start=0:end=1.366666666667,asetpts=PTS-STARTPTS[a];[0:a]atrim=start=2.1:end=3.616666666667,asetpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=0:a=1[out]'
run([FF,'-v','error','-i',str(source),'-filter_complex',filters,'-map','[out]','-c:a','pcm_s16le',str(audio)])
video=OUT/'FINAL_C1_VS_IDLE_INDEX_B_OVERHEAD_1X.mp4';slow=OUT/'FINAL_C1_VS_IDLE_INDEX_B_OVERHEAD_0_5X.mp4'
run([FF,'-v','error','-framerate','60','-start_number','0','-i',str(folder/'%04d.png'),'-i',str(audio),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-frames:v','173','-t',str(duration),'-c:a','aac','-b:a','192k','-movflags','+faststart',str(video)])
run([FF,'-v','error','-i',str(video),'-filter_complex','[0:v]setpts=2*PTS,fps=60,tpad=stop_mode=clone:stop_duration=0.033334[v];[0:a]atempo=0.5,apad[a]','-map','[v]','-map','[a]','-frames:v','346','-t',str(2*duration),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(slow)])
meta={p.name:json.loads(run([FP,'-v','error','-show_streams','-show_format','-of','json',str(p)])) for p in [video,slow]}
qc=[]
import numpy as np
for p,count,ids in [(video,173,[0,26,59,74,81,82,112,157,158,165,172]),(slow,346,[0,52,118,148,162,164,224,314,316,330,345])]:
 filt='+'.join(f'eq(n\\,{i})' for i in ids);pr=subprocess.run([FF,'-v','error','-i',str(p),'-vf','select='+filt,'-vsync','0','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE);assert pr.returncode==0
 frames=np.frombuffer(pr.stdout,np.uint8).reshape(-1,840,2560,3);assert len(frames)==len(ids)
 vals=[]
 for i,im in zip(ids,frames):
  ref=min(i if count==173 else i//2,172);arr=np.array(Image.open(folder/f'{ref:04d}.png').convert('RGB'));vals.append(dict(frame=i,reference=ref,mae=float(np.mean(abs(im.astype(float)-arr)))))
 stream=next(s for s in meta[p.name]['streams'] if s['codec_type']=='video');assert int(stream['nb_frames'])==count
 assert max(v['mae'] for v in vals)<8
 qc.append(dict(video=p.name,decoded_samples=vals,frame_count=count,pass_=True))
save('FINAL_MEDIA_QC_AND_METADATA.json',dict(videos=meta,qc=qc,sha256={p.name:sha(p) for p in [video,slow]},source_frame_ranges=[[1,82],[127,217]],source_time_ranges=[[0,1.35],[2.1,3.6]],camera='Original STAGE_C_OVERHEAD, unchanged. Full 1280x720 frames placed side by side at native scale.',audio='Trim original C1 audio with matching source frame boundaries; atempo=0.5 for slow version; final held display frame only pads cadence endpoint.'))
protection('FINAL_MEDIA_INPUT_RECEIPT.json');print('FINAL_MEDIA_DONE',flush=True)
