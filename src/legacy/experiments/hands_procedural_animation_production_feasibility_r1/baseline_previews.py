from common import *
import subprocess
begin=time.perf_counter();files=[]
for view in ['teaching','side_oblique']:
    src=safe(C1/f'normal_speed_{view}.mp4');READS[str(src)]=sha(src)
    dst=OUT/f'before_C1_{view}_1x.mp4';assert not dst.exists()
    args=['D:/ffmpeg/bin/ffmpeg.exe','-n','-v','error','-threads','2','-i',str(src),'-filter_complex',
          '[0:v]trim=start_frame=264:end_frame=336,setpts=PTS-STARTPTS[v];[0:a]atrim=start=4.4:end=5.6,asetpts=PTS-STARTPTS[a]',
          '-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(dst)]
    subprocess.run(args,check=True)
    meta=json.loads(subprocess.check_output(['D:/ffmpeg/bin/ffprobe.exe','-v','error','-count_frames','-show_streams','-of','json',str(dst)]))
    v=next(s for s in meta['streams'] if s['codec_type']=='video')
    assert int(v['nb_read_frames'])==72 and v['r_frame_rate']=='60/1' and abs(float(v['duration'])-1.2)<.001
    subprocess.run(['D:/ffmpeg/bin/ffmpeg.exe','-v','error','-i',str(dst),'-f','null','-'],check=True)
    files.append(dict(file=dst.name,sha256=sha(dst),video=v,source_sha256=sha(src)))
save('BASELINE_PREVIEW_RECEIPT.json',dict(seconds=time.perf_counter()-begin,files=files,source_start=START,source_end=END,speed=1,frames=72))
protection('BASELINE_MEDIA_PROTECTION.json')
print('BEFORE_PREVIEWS_READY',time.perf_counter()-begin,flush=True)
