from common import *
import subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R1=ROOT/'experiments/hands_c1_dynamic_artist_correction_poc_r1'
FF='D:/ffmpeg/bin/ffmpeg.exe';FP='D:/ffmpeg/bin/ffprobe.exe';duration=76/60
assert read(OUT/'RENDER_MANIFEST.json')['camera_exact_match']
oldqa=read(R1/'MEDIA_QC.json')
def run(args):
 r=subprocess.run(args,cwd=OUT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if r.returncode:raise RuntimeError(r.stderr.decode('utf8',errors='replace')[-2500:])
 return r.stdout
def audio(path):return np.frombuffer(run([FF,'-v','error','-i',str(path),'-map','0:a:0','-ac','1','-ar','48000','-f','f32le','-']),np.float32)
refs={1:safe(R1/'one_audio.wav'),.5:safe(R1/'slow_audio.wav')}
for p in refs.values():READS[str(p)]=sha(p)
font=lambda size:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)
outputs=[]
for kind in ['OVERHEAD','SIDE_OBLIQUE']:
 folder=OUT/(kind.lower()+'_paired_frames');folder.mkdir()
 for ix in range(76):
  canvas=Image.new('RGB',(2560,816),'#101723');d=ImageDraw.Draw(canvas);t=2.1+ix/60
  for col,(root,tag,title) in enumerate([(R1,'original','原 C1 / ORIGINAL'),(OUT,'candidate','R2 退出修正 2 / NOT APPROVED')]):
   p=safe(root/(tag+'_'+kind.lower()+'_frames')/f'{ix:04d}.png');im=Image.open(p).convert('RGB');assert im.size==(1280,720)
   canvas.paste(im,(col*1280,64));d.text((col*1280+18,7),title,font=font(28),fill='white');d.text((col*1280+650,13),f't = {t:.6f} s',font=font(23),fill='#b9cce4')
  d.text((18,788),'同源时间 / 同正式相机 / 实际模型画面完整保留；R2 局部退出修正实验，未获教学用途批准。',font=font(18),fill='#ffcf77');canvas.save(folder/f'{ix:04d}.png')
 silent=OUT/(kind+'_1X_VIDEO_ONLY.mp4')
 run([FF,'-n','-v','error','-framerate','60','-i',str(folder/'%04d.png'),'-frames:v','76','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p',str(silent)])
 speeds=[(1,silent,76,duration)]
 if kind=='OVERHEAD':
  ss=OUT/'OVERHEAD_0_5X_VIDEO_ONLY.mp4';run([FF,'-n','-v','error','-i',str(silent),'-vf','setpts=2*(PTS-STARTPTS),fps=60,tpad=stop_mode=clone:stop_duration=0.05','-frames:v','152','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p',str(ss)]);speeds.append((.5,ss,152,duration*2))
 for speed,src,count,dur in speeds:
  name='C1_VS_EXIT_CORRECTED_'+('OVERHEAD' if kind=='OVERHEAD' else 'SIDE')+('_1X.mp4' if speed==1 else '_0_5X.mp4');dest=OUT/name
  run([FF,'-n','-v','error','-i',str(src),'-i',str(refs[speed]),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(dur),'-movflags','+faststart',str(dest)])
  meta=json.loads(run([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(dest)]));v=next(s for s in meta['streams'] if s['codec_type']=='video');a=next(s for s in meta['streams'] if s['codec_type']=='audio')
  assert int(v['nb_read_frames'])==count and v['r_frame_rate']=='60/1' and abs(float(v['duration'])-dur)<.001 and abs(float(a['duration'])-dur)<.001
  assert float(v['start_time'])==float(a['start_time'])==0
  run([FF,'-v','error','-i',str(dest),'-f','null','-']);ref=audio(refs[speed]);got=audio(dest);n=min(len(ref),len(got));corr=float(np.corrcoef(ref[:n],got[:n])[0,1]);assert corr>.98
  outputs.append(dict(file=name,sha256=sha(dest),video=v,audio=a,full_decode=True,audio_reference_correlation=corr))
def images(path):
 raw=run([FF,'-v','error','-i',str(path),'-vf','scale=320:102:flags=area,format=gray','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','gray','-']);return np.frombuffer(raw,np.uint8).reshape(-1,102,320)
one=images(OUT/'C1_VS_EXIT_CORRECTED_OVERHEAD_1X.mp4');slow=images(OUT/'C1_VS_EXIT_CORRECTED_OVERHEAD_0_5X.mp4')
diff=np.abs(slow.astype(float)-one[np.arange(152)//2].astype(float)).mean((1,2));assert diff.max()<2 and one.mean((1,2)).min()>5
sheet=Image.new('RGB',(2560,1320),'#101723');d=ImageDraw.Draw(sheet)
for j,ix in enumerate([35,41,47,49,57,62]):
 x=(j%2)*1280;y=(j//2)*440;im=Image.open(OUT/'overhead_paired_frames'/f'{ix:04d}.png').convert('RGB').resize((1280,408));sheet.paste(im,(x,y+32));d.text((x+12,y+1),f'C1 / R2 | t={2.1+ix/60:.6f}s',font=font(25),fill='white')
sheet.save(OUT/'VIDEO_REVIEW_CONTACT_SHEET.png')
save('MEDIA_QC.json',dict(pass_=True,outputs=outputs,frames=[76,152],fps=60,source_frame_range=[127,202],source_time_range=[2.1,3.35],one_duration=duration,slow_duration=duration*2,slow_frame_mapping='floor(j/2)',slow_mapping_max_MAE=float(diff.max()),black_frames=0,audio_sources={str(k):dict(path=str(p),sha256=sha(p)) for k,p in refs.items()},audio_reused_from_frozen_R1_without_timing_changes=True,pitch_preserving_slow=True,prior_audio_timing_checks=oldqa['local_energy_event_checks'],audio_limit='The same pitch-preserving R1 waveforms retain measured local energy-rise timing deviations of15/20ms. Duration and waveform identity verified anew; no perceptual listening or all-note subframe acoustic certification claimed.'))
protection('MEDIA_INPUT_RECEIPT.json');print('R2_MEDIA_COMPLETE',flush=True)
