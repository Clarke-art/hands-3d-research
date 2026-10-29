from common import *
import subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
FF='D:/ffmpeg/bin/ffmpeg.exe';FP='D:/ffmpeg/bin/ffprobe.exe';duration=76/60
def run(args,binary=False):
 r=subprocess.run(args,cwd=OUT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if r.returncode:raise RuntimeError(r.stderr.decode('utf8',errors='replace')[-2500:])
 return r.stdout if binary else r.stdout.decode('utf8',errors='replace')
def audio(path):
 return np.frombuffer(run([FF,'-v','error','-i',str(path),'-map','0:a:0','-ac','1','-ar','48000','-f','f32le','-'],True),np.float32)
def onset(x):
 e=np.convolve(x.astype(float)**2,np.ones(240)/240,mode='valid')
 return np.flatnonzero(e>e.max()*1e-4)[0]/48000
def probe(p):return json.loads(run([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
assert read(OUT/'RENDER_DELIVERY_MANIFEST.json')['cameras_identical']
wav=safe(C1/'piano_performance.wav');READS[str(wav)]=sha(wav)
one_audio=OUT/'one_audio.wav';full_slow=OUT/'full_slow_unaligned.wav';slow_audio=OUT/'slow_audio.wav'
run([FF,'-n','-v','error','-i',str(wav),'-af',f'atrim=start=2.1:end={2.1+duration},asetpts=PTS-STARTPTS,apad,atrim=duration={duration}','-ar','48000','-c:a','pcm_s16le',str(one_audio)])
run([FF,'-n','-v','error','-i',str(wav),'-af','atempo=0.5','-ar','48000','-c:a','pcm_s16le',str(full_slow)])
original_audio=audio(wav);stretched=audio(full_slow)
delay=round((2*onset(original_audio)-onset(stretched))*48000)
assert 0<=delay<4800
run([FF,'-n','-v','error','-i',str(full_slow),'-af',f'adelay={delay}S:all=1,atrim=start=4.2:end={4.2+duration*2},asetpts=PTS-STARTPTS,apad,atrim=duration={duration*2}','-ar','48000','-c:a','pcm_s16le',str(slow_audio)])
font=lambda size:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)
outputs=[]
for kind in ['OVERHEAD','SIDE_OBLIQUE']:
 folder=OUT/(kind.lower()+'_paired_frames');folder.mkdir()
 for ix in range(76):
  canvas=Image.new('RGB',(2560,816),'#101723');d=ImageDraw.Draw(canvas);t=2.1+ix/60
  for col,(tag,title) in enumerate([('original','原 C1 / ORIGINAL'),('candidate','实验候选 2 / NOT APPROVED')]):
   im=Image.open(OUT/(tag+'_'+kind.lower()+'_frames')/f'{ix:04d}.png').convert('RGB');assert im.size==(1280,720)
   canvas.paste(im,(col*1280,64));d.text((col*1280+18,7),title,font=font(28),fill='white')
   d.text((col*1280+600,13),f't = {t:.6f} s',font=font(23),fill='#b9cce4')
  d.text((18,788),'同源时间 / 同相机 / 原始网格画面完整保留；这是未获批准的纠错实验，请结合检测报告审核。',font=font(18),fill='#ffcf77')
  canvas.save(folder/f'{ix:04d}.png')
 silent=OUT/(kind+'_1X_VIDEO_ONLY.mp4')
 run([FF,'-n','-v','error','-framerate','60','-start_number','0','-i',str(folder/'%04d.png'),'-frames:v','76','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p',str(silent)])
 video=OUT/('C1_VS_REPAIRED_OVERHEAD_1X.mp4' if kind=='OVERHEAD' else 'C1_VS_REPAIRED_SIDE_1X.mp4')
 run([FF,'-n','-v','error','-i',str(silent),'-i',str(one_audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(duration),'-movflags','+faststart',str(video)])
 outputs.append((video,76,duration,one_audio))
 if kind=='OVERHEAD':
  slow_silent=OUT/'OVERHEAD_0_5X_VIDEO_ONLY.mp4'
  run([FF,'-n','-v','error','-i',str(silent),'-vf','setpts=2*(PTS-STARTPTS),fps=60,tpad=stop_mode=clone:stop_duration=0.05','-frames:v','152','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p',str(slow_silent)])
  slow=OUT/'C1_VS_REPAIRED_OVERHEAD_0_5X.mp4'
  run([FF,'-n','-v','error','-i',str(slow_silent),'-i',str(slow_audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(duration*2),'-movflags','+faststart',str(slow)])
  outputs.append((slow,152,duration*2,slow_audio))
rows=[]
for p,n,dur,au in outputs:
 meta=probe(p);v=next(x for x in meta['streams'] if x['codec_type']=='video');a=next(x for x in meta['streams'] if x['codec_type']=='audio')
 assert int(v['nb_read_frames'])==n and v['r_frame_rate']=='60/1'
 assert abs(float(v['duration'])-dur)<.001 and abs(float(a['duration'])-dur)<.001
 assert abs(float(v['start_time']))<.001 and abs(float(a['start_time']))<.001
 run([FF,'-v','error','-i',str(p),'-f','null','-'])
 ref=audio(au);dec=audio(p);common=min(len(ref),len(dec));corr=float(np.corrcoef(ref[:common],dec[:common])[0,1]);assert corr>.98
 rows.append(dict(file=p.name,sha256=sha(p),video=v,audio=a,full_decode=True,decoded_audio_reference_correlation=corr,decoded_samples=len(dec),audio_reference_samples=len(ref)))
def grayvideo(p):
 b=run([FF,'-v','error','-i',str(p),'-map','0:v:0','-vf','scale=320:102:flags=area,format=gray','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','gray','-'],True)
 return np.frombuffer(b,np.uint8).reshape(-1,102,320)
normal=grayvideo(OUT/'C1_VS_REPAIRED_OVERHEAD_1X.mp4');slow=grayvideo(OUT/'C1_VS_REPAIRED_OVERHEAD_0_5X.mp4')
diff=np.abs(slow.astype(float)-normal[np.arange(152)//2].astype(float)).mean((1,2));assert diff.max()<2
assert normal.mean((1,2)).min()>5
# Acoustic event check on local energy-rise peaks; this does not certify all
# simultaneous voices. Use the same 5ms energy envelope in source/slow audio.
def peak_rise(x,expected):
 block=240;en=np.sqrt(np.mean(x[:len(x)//block*block].reshape(-1,block).astype(float)**2,axis=1));rise=np.diff(en)
 center=expected/.005;lo=max(0,int(center)-8);hi=min(len(rise),int(center)+8)
 return (lo+int(np.argmax(rise[lo:hi])))*.005
local=audio(one_audio);slowlocal=audio(slow_audio);eventcheck=[]
for t in [2.492855,2.921426]:
 p=peak_rise(local,t-2.1);q=peak_rise(slowlocal,2*(t-2.1));eventcheck.append(dict(event_time=t,one_peak_sec=p,slow_peak_sec=q,slow_minus_double_one_ms=(q-2*p)*1000))
contact=Image.new('RGB',(1920,1600),'#101723');draw=ImageDraw.Draw(contact)
for j,ix in enumerate([6,18,30,42,48,61]):
 col=j%3;row=j//3
 for k,tag in enumerate(['original','candidate']):
  im=Image.open(OUT/(tag+'_overhead_frames')/f'{ix:04d}.png').convert('RGB').resize((640,360))
  y=row*800+k*390+32;contact.paste(im,(col*640,y));draw.text((col*640+12,y-28),f'{tag.upper()} | t={2.1+ix/60:.3f}s',font=font(21),fill='white')
contact.save(OUT/'VIDEO_REVIEW_CONTACT_SHEET.png')
save('MEDIA_QC.json',dict(pass_=True,outputs=rows,source_WAV_sha256=sha(wav),source_frames=[127,202],first_source_time=2.1,last_source_time=3.35,one_duration=duration,slow_duration=duration*2,frame_mapping='1X frame i => source frame127+i; 0.5X frame j => 1X frame floor(j/2)',all_slow_frame_mapping_max_MAE=float(diff.max()),black_frames=0,pitch_preserving_slow_audio=True,slow_audio_method='full original waveform atempo=0.5; compensate measured first-activity latency; then trim at doubled source times',full_waveform_delay_samples=delay,full_waveform_first_onset_alignment_error_ms=(onset(stretched)+delay/48000-2*onset(original_audio))*1000,local_energy_event_checks=eventcheck,limitations='No perceptual listening claimed. Energy rise checks do not isolate each simultaneous note or prove subframe acoustic sync. Video render directly samples real saved animation at60Hz.'))
protection('MEDIA_INPUT_RECEIPT.json')
print('MEDIA_COMPLETE',json.dumps(eventcheck),flush=True)
