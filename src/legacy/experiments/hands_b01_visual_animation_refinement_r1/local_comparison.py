from common import *
import subprocess
begin=time.perf_counter();receipt=read(OUT/'LOCAL_RENDER_RECEIPT.json');assert receipt['frames']==51
ff='D:/ffmpeg/bin/ffmpeg.exe';fp='D:/ffmpeg/bin/ffprobe.exe';src=safe(C1/'normal_speed_overhead.mp4');wav=safe(C1/'piano_performance.wav')
READS[str(src)]=sha(src);READS[str(wav)]=sha(wav)
candidate=OUT/'B01_CANDIDATE_OVERHEAD_1X_NOT_APPROVED.mp4';comparison=OUT/'B01_BEFORE_AFTER_OVERHEAD_1X_NOT_APPROVED.mp4'
font='C\\:/Windows/Fonts/arial.ttf'
def run(args):subprocess.run([ff,'-n','-v','error','-threads','2']+args,check=True)
run(['-framerate','60','-i',str(OUT/'local_frames/%04d.png'),'-ss','0.9','-i',str(wav),'-map','0:v','-map','1:a','-frames:v','51','-t','0.85','-c:v','libx264','-crf','17','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(candidate)])
filter="[0:v]trim=start_frame=54:end_frame=105,setpts=PTS-STARTPTS,crop=640:720:480:0[a];[1:v]crop=640:720:480:0[b];[a][b]hstack=inputs=2,pad=1280:764:0:44:color=0x202020,drawtext=fontfile='"+font+"':text='ORIGINAL C1 (left) | B01 ONE EDIT (right) | 1x | NOT_APPROVED':x=12:y=12:fontsize=22:fontcolor=white[v]"
run(['-i',str(src),'-i',str(candidate),'-ss','0.9','-i',str(wav),'-filter_complex',filter,'-map','[v]','-map','2:a','-frames:v','51','-t','0.85','-c:v','libx264','-crf','17','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(comparison)])
# All local frames, chronological contact sheets for pre-QC visual inspection.
for label,select,tile in [('FIRST',"between(n,0,24)",'5x5'),('SECOND',"between(n,25,50)",'5x6')]:
    run(['-i',str(comparison),'-vf',f"select='{select}',scale=640:382,tile={tile}",'-frames:v','1',str(OUT/f'VISUAL_SEQUENCE_{label}.png')])
stats=[]
for file in [candidate,comparison]:
    meta=json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-of','json',str(file)]))
    v=next(s for s in meta['streams'] if s['codec_type']=='video');assert int(v['nb_read_frames'])==51 and v['r_frame_rate']=='60/1' and abs(float(v['duration'])-.85)<.001
    subprocess.run([ff,'-v','error','-i',str(file),'-f','null','-'],check=True)
    stats.append(dict(file=file.name,sha256=sha(file),frames=51,fps=60,duration_sec=float(v['duration']),full_decode='PASS',approval='NOT_APPROVED'))
save('LOCAL_VIDEO_RECEIPT.json',dict(seconds=time.perf_counter()-begin,files=stats,source_frame_range=[55,105],source_time=[.9,1.75],same_camera=True,same_scale=True,same_clock=True,comparison_crop_original_pixels=[480,0,640,720],complete_right_hand_in_crop=True,approval='NOT_APPROVED'))
protection('LOCAL_MEDIA_PROTECTION.json');print('LOCAL_DIAGNOSTIC_COMPARISON_READY',time.perf_counter()-begin,flush=True)
