from performance_core import *
from PIL import Image,ImageDraw,ImageFont
import subprocess,wave
from scipy.signal import correlate,correlation_lags
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22);bold=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',27)
def compose(j):
 im=Image.open(P/'_frames'/f'{j:04}.png').convert('RGB');im.load();d=ImageDraw.Draw(im);d.rectangle((0,0,1600,92),fill='#14202b');d.text((24,8),'MUSETTE / BWV Anh.126 / MEASURES 1-2',font=bold,fill='#eef4fa');d.text((24,48),'ONE PROCEDURAL CANDIDATE / MOTION & CONTACT NOT VALIDATED',font=font,fill='#ffc48d');d.text((1260,18),f'{j/FPS:.3f} / {DURATION:.3f}s',font=font,fill='#eef4fa')
 t=j/FPS;act=[n for n in TL['notes'] if n['note_on']<=t<n['note_off']]
 def line(s):return ' + '.join(KEYS[n['key_index']]['note_name']+f" / finger {n['finger']}" for n in act if n['hand']==s) or 'prepare / release'
 d.rectangle((0,830,1600,900),fill='#14202b');d.text((24,842),'LEFT  '+line('L'),font=bold,fill='#eef4fa');d.text((865,842),'RIGHT  '+line('R'),font=bold,fill='#eef4fa');return im
out=P/'product_midi_dual_hand_with_audio.mp4'
enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1600x900','-framerate',str(FPS),'-i','-','-i',str(P/'piano_performance.wav'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-t',str(DURATION),'-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
for j in range(round(DURATION*FPS)):enc.stdin.write(compose(j).tobytes())
enc.stdin.close();assert enc.wait()==0
compose(67).save(P/'review_poster.jpg',quality=94)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(out)]));v=next(x for x in probe['streams'] if x['codec_type']=='video');a=next(x for x in probe['streams'] if x['codec_type']=='audio');assert int(v['nb_read_frames'])==204;assert a['codec_name']=='aac';assert abs(float(probe['format']['duration'])-DURATION)<.03
decoded=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(out),'-vn','-f','f32le','-ac','2','-ar','48000','-']),dtype='<f4').reshape(-1,2)
with wave.open(str(P/'piano_performance.wav'),'rb') as w:ref=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2)/32768
x=decoded.mean(axis=1);y=ref.mean(axis=1);c=correlate(x,y,method='fft');lag=int(correlation_lags(len(x),len(y))[np.argmax(c)]);rms=float(np.sqrt(np.mean(decoded**2)));assert rms>.001;assert abs(lag)<=480
sync=read(P/'KEY_AUDIO_SYNC_R1.json');sync.update({'audio_status':'PASS','mp4_audio_track':True,'mp4_audio_rms':rms,'decoded_aac_vs_pcm_lag_samples':lag,'decoded_aac_vs_pcm_lag_ms':lag/48,'mux_note':'AAC priming handled by container; decoded cross-correlation compares final delivery to same-clock PCM.','PRODUCT_DEMO_PASS':False});dump('KEY_AUDIO_SYNC_R1.json',sync)
dump('VIDEO_VERIFICATION_R1.json',{'status':'PASS_MEDIA_STRUCTURE','duration_sec':DURATION,'frames':204,'fps':60,'audio_present':True,'audio_not_silent':True,'decoded_audio_rms':rms,'AAC_PCM_lag_ms':lag/48,'probe':probe,'motion_quality':'NOT_PASSED'})
qa=P/'_qa';qa.mkdir(exist_ok=True)
for part in range(4):
 sheet=Image.new('RGB',(1600,6*192),'#14202b');d=ImageDraw.Draw(sheet)
 for k in range(51):
  j=part*51+k;row=k//9;col=k%9;sheet.paste(Image.open(P/'_frames'/f'{j:04}.png').resize((176,99)),(col*177,row*192+30));d.text((col*177+2,row*192+4),f'{j/FPS:.3f}s',font=font,fill='white')
 sheet.save(qa/f'all_frames_{part+1}.jpg',quality=93)
print('MEDIA_VERIFIED',rms,'lag_ms',lag/48,flush=True)
