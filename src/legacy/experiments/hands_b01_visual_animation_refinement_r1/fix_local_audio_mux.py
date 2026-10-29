from common import *
import subprocess
sys.path.insert(0,str(OLD/'_deps'))
import numpy as np
begin=time.perf_counter();ff='D:/ffmpeg/bin/ffmpeg.exe';fp='D:/ffmpeg/bin/ffprobe.exe';wav=safe(C1/'piano_performance.wav');READS[str(wav)]=sha(wav)
oldreceipt=read(OUT/'LOCAL_VIDEO_RECEIPT.json');files=[]
def video_hash(p):return hashlib.sha256(subprocess.check_output([ff,'-v','error','-i',str(p),'-map','0:v:0','-f','framemd5','-'])).hexdigest()
def audio(p):return np.frombuffer(subprocess.check_output([ff,'-v','error','-i',str(p),'-map','0:a:0','-ac','1','-ar','48000','-f','f32le','-']),np.float32)
reference=audio(wav)[43200:84000];decoded=[]
for row in oldreceipt['files']:
    target=OUT/row['file'];assert sha(target)==row['sha256']
    diag=target.with_name(target.stem+'_SHORT_AUDIO_DIAGNOSTIC.mp4');assert not diag.exists();target.rename(diag)
    command=[ff,'-n','-v','error','-i',str(diag),'-i',str(wav),'-filter_complex','[1:a]atrim=start=0.9:end=1.75,asetpts=PTS-STARTPTS[a]',
        '-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-t','0.85','-movflags','+faststart',str(target)]
    subprocess.run(command,check=True)
    assert video_hash(target)==video_hash(diag)
    meta=json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-of','json',str(target)]))
    v=next(s for s in meta['streams'] if s['codec_type']=='video');a=next(s for s in meta['streams'] if s['codec_type']=='audio')
    assert int(v['nb_read_frames'])==51 and float(v['duration'])==.85 and float(a['duration'])==.85 and float(v['start_time'])==float(a['start_time'])==0
    subprocess.run([ff,'-v','error','-i',str(target),'-f','null','-'],check=True)
    au=audio(target);decoded.append(au);corr=float(np.corrcoef(au[:len(reference)],reference)[0,1]);assert corr>.995
    files.append(dict(file=target.name,sha256=sha(target),frames=51,fps=60,duration_sec=.85,audio_duration_sec=.85,audio_start=0,video_start=0,
        full_decode='PASS',approval='NOT_APPROVED',video_frames_unchanged_by_mux=True,source_audio_reference_sec=[.9,1.75],source_WAV_zero_lag_correlation=corr,command=command))
assert np.array_equal(decoded[0],decoded[1])
save('FINAL_LOCAL_VIDEO_RECEIPT.json',dict(seconds=time.perf_counter()-begin,files=files,source_frame_range=[55,105],source_time=[.9,1.75],same_camera=True,same_scale=True,same_clock=True,
    comparison_crop_original_pixels=[480,0,640,720],complete_right_hand_in_crop=True,approval='NOT_APPROVED',
    original_short_audio_bug='Initial -frames:v output ended audio after one AAC packet; remuxed exact unchanged video with explicit full original WAV interval',
    old_short_audio_diagnostics_preserved=True,both_final_audio_tracks_identical=True))
protection('FINAL_LOCAL_MEDIA_PROTECTION.json');print('LOCAL_AUDIO_MUX_FIXED',time.perf_counter()-begin,[x['source_WAV_zero_lag_correlation'] for x in files],flush=True)
