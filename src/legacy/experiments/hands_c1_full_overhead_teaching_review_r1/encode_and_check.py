from common import *
import subprocess,wave
sys.path.insert(0,str(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'))
import numpy as np
begin=time.perf_counter();assert read(OUT/'CAMERA_FRAMING_CHECK.json')['pass_']
ff='D:/ffmpeg/bin/ffmpeg.exe';fp='D:/ffmpeg/bin/ffprobe.exe';src=safe(C1/'normal_speed_overhead.mp4');wav=safe(C1/'piano_performance.wav')
READS[str(src)]=sha(src);READS[str(wav)]=sha(wav)
legacy=read(C1/'MUX_AUDIO_CLOCK_VERIFICATION.json');assert sha(wav)==legacy['reference_WAV_sha256']
commands=[]
def run(args):
    commands.append(args);subprocess.run([ff,'-n','-v','error','-threads','2']+args,check=True)
def probe(p):return json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
def decode_video(p):
    raw=subprocess.check_output([ff,'-v','error','-i',str(p),'-map','0:v:0','-vf','scale=160:90:flags=area,format=gray','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','gray','-'])
    return np.frombuffer(raw,np.uint8).reshape(-1,90,160)
def decode_audio(p):
    raw=subprocess.check_output([ff,'-v','error','-i',str(p),'-map','0:a:0','-ac','1','-ar','48000','-f','f32le','-'])
    return np.frombuffer(raw,np.float32)
one=OUT/'C1_FULL_OVERHEAD_1X.mp4';slow=OUT/'C1_FULL_OVERHEAD_0_5X.mp4'
assert not one.exists() and not slow.exists()
run(['-i',str(src),'-map','0:v:0','-map','0:a:0','-vf','scale=1920:1080:flags=lanczos','-frames:v','357','-fps_mode','passthrough',
     '-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(one)])
run(['-i',str(src),'-i',str(wav),'-filter_complex',
     '[0:v]scale=1920:1080:flags=lanczos,setpts=2*(PTS-STARTPTS),fps=60,tpad=stop_mode=clone:stop_duration=0.05,trim=duration=11.9[v];[1:a]atrim=duration=5.95,asetpts=PTS-STARTPTS,atempo=0.5,apad,atrim=duration=11.9[a]',
     '-map','[v]','-map','[a]','-frames:v','714','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(slow)])
stats=[]
original=decode_video(src);assert len(original)==357
for p,count,duration,indices in [(one,357,5.95,np.arange(357)),(slow,714,11.9,np.arange(714)//2)]:
    meta=probe(p);v=next(s for s in meta['streams'] if s['codec_type']=='video');a=next(s for s in meta['streams'] if s['codec_type']=='audio')
    assert int(v['nb_read_frames'])==count and v['r_frame_rate']=='60/1' and v['width']==1920 and v['height']==1080
    assert abs(float(v['duration'])-duration)<.001 and abs(float(a['duration'])-duration)<.025 and abs(float(v['start_time']))<.001 and abs(float(a['start_time']))<.001
    subprocess.run([ff,'-v','error','-i',str(p),'-f','null','-'],check=True)
    images=decode_video(p);diff=np.abs(images.astype(float)-original[indices].astype(float)).mean(axis=(1,2))
    black=np.flatnonzero(images.mean((1,2))<5);assert not len(black) and diff.max()<2
    stats.append(dict(file=p.name,sha256=sha(p),video=v,audio=a,full_decode='PASS',source_frame_mapping='i' if count==357 else 'floor(i/2)',
                      mapping_frame_mean_absolute_error_max=float(diff.max()),mapping_frame_mean_absolute_error_average=float(diff.mean()),black_frames=black,
                      all_original357_frames_retained=True,upscale_from=[1280,720],native_render_resolution=[1280,720],output_resolution=[1920,1080]))
aud_src=decode_audio(src);aud_one=decode_audio(one);assert np.array_equal(aud_src,aud_one)
orig=decode_audio(wav);stretched=decode_audio(slow)
def onset(x):
    # Detect first waveform activity well above AAC/silence noise, with the same
    # relative threshold; this is a limited timing check, not 23-note recognition.
    e=np.convolve(x.astype(float)**2,np.ones(240)/240,mode='valid')
    return float(np.flatnonzero(e>e.max()*1e-4)[0]/48000)
orig_on=onset(orig);slow_on=onset(stretched)
save('ENCODE_QUALITY_CHECK.json',dict(pass_=True,seconds=time.perf_counter()-begin,outputs=stats,commands=commands,one_audio_decoded_identical_to_original_C1_video=True,
     source_video_sha256=sha(src),source_WAV_sha256=sha(wav),source_WAV_legacy_lag_samples=legacy['per_video']['normal_speed_overhead.mp4']['best_lag_samples_48k'],
     slow_audio_filter='atempo=0.5 (pitch preserving), padded/truncated only to full 11.9-second presentation container',
     first_activity_original_sec=orig_on,first_activity_slow_sec=slow_on,first_activity_slow_minus_double_original_ms=(slow_on-2*orig_on)*1000,
     slow_audio_peak=float(np.max(abs(stretched))),audio_sample_rate=48000,scope='Source identity and deterministic frame/time mapping; no motion/geometry safety claim; perceptual listening is not claimed'))
protect('MEDIA_INPUT_PROTECTION.json')
print('FULL_VIDEOS_ENCODED_CHECKED',json.dumps(dict(seconds=time.perf_counter()-begin,slow_audio_first_activity_error_ms=(slow_on-2*orig_on)*1000,frame_errors=[s['mapping_frame_mean_absolute_error_max'] for s in stats])),flush=True)
