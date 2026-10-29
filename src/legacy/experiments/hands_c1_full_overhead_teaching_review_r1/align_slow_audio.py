from common import *
import subprocess
sys.path.insert(0,str(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'))
import numpy as np
ff='D:/ffmpeg/bin/ffmpeg.exe';fp='D:/ffmpeg/bin/ffprobe.exe';begin=time.perf_counter()
qa=read(OUT/'ENCODE_QUALITY_CHECK.json');slow=OUT/'C1_FULL_OVERHEAD_0_5X.mp4';wav=safe(C1/'piano_performance.wav')
READS[str(wav)]=sha(wav)
def audio(p):return np.frombuffer(subprocess.check_output([ff,'-v','error','-i',str(p),'-map','0:a:0','-ac','1','-ar','48000','-f','f32le','-']),np.float32)
def onset(x):
    e=np.convolve(x.astype(float)**2,np.ones(240)/240,mode='valid');return float(np.flatnonzero(e>e.max()*1e-4)[0]/48000)
def end_activity(x):return float(np.flatnonzero(np.abs(x)>np.max(abs(x))*1e-3)[-1]/48000)
orig=audio(wav);old=audio(slow);delay=round((2*onset(orig)-onset(old))*48000)
assert 0<delay<4800 and end_activity(old)+delay/48000<11.9,'Do not truncate original audible tail'
diag=OUT/'SLOW_UNALIGNED_DIAGNOSTIC.mp4';assert not diag.exists();slow.rename(diag)
args=[ff,'-n','-v','error','-i',str(diag),'-i',str(wav),'-filter_complex',
      f'[1:a]atrim=duration=5.95,asetpts=PTS-STARTPTS,atempo=0.5,adelay={delay}S:all=1,apad,atrim=duration=11.9[a]',
      '-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(slow)]
subprocess.run(args,check=True)
new=audio(slow);error=(onset(new)-2*onset(orig))*1000;assert abs(error)<5
def video_hash(p):return hashlib.sha256(subprocess.check_output([ff,'-v','error','-i',str(p),'-map','0:v:0','-f','framemd5','-'])).hexdigest()
assert video_hash(diag)==video_hash(slow),'Audio alignment must not alter a single video frame'
meta=json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-of','json',str(slow)]))
v=next(s for s in meta['streams'] if s['codec_type']=='video');a=next(s for s in meta['streams'] if s['codec_type']=='audio')
assert int(v['nb_read_frames'])==714 and v['r_frame_rate']=='60/1' and float(v['duration'])==11.9 and float(a['duration'])==11.9
assert float(v['start_time'])==float(a['start_time'])==0
subprocess.run([ff,'-v','error','-i',str(slow),'-f','null','-'],check=True)
def strongest(x,lo,hi):
    block=x[round(lo*48000):round(hi*48000)].astype(float);mag=abs(np.fft.rfft(block*np.hanning(len(block)),n=65536));freq=np.fft.rfftfreq(65536,1/48000)
    mag[(freq<80)|(freq>2000)]=0;return float(freq[int(mag.argmax())])
f0=strongest(orig,.45,.65);f1=strongest(new,.9,1.3)
qa['outputs'][1]['sha256']=sha(slow);qa['outputs'][1]['video']=v;qa['outputs'][1]['audio']=a
save('FINAL_MEDIA_QA.json',dict(pass_=True,outputs=qa['outputs'],initial_encoding_seconds=qa['seconds'],audio_alignment_seconds=time.perf_counter()-begin,
    initial_activity_error_ms=qa['first_activity_slow_minus_double_original_ms'],alignment_delay_samples_48k=delay,alignment_delay_ms=delay/48,
    final_activity_error_ms=error,first_activity_original_sec=onset(orig),first_activity_final_slow_sec=onset(new),
    last_activity_before_delay_sec=end_activity(old),last_activity_after_delay_sec=end_activity(new),audible_tail_retained=True,
    slow_video_decoded_frames_identical_before_after_audio_alignment=True,one_audio_decoded_identical_to_original_C1_video=True,
    stable_opening_chord_dominant_frequency_original_Hz=f0,stable_opening_chord_dominant_frequency_slow_Hz=f1,
    stable_chord_dominant_frequency_difference_cents=float(1200*np.log2(f1/f0)),
    audio_method='atempo=0.5; compensate measured fixed onset latency with silence delay; no pitch resampling, MIDI or Action edit',command=args,
    audio_timing_limit='First-activity alignment and full-duration/source-clock checks; not independent note-by-note perceptual listening or subframe acoustic onset certification'))
protect('FINAL_MEDIA_INPUT_PROTECTION.json')
print('AUDIO_ALIGNED',delay,error,f0,f1,time.perf_counter()-begin,flush=True)
