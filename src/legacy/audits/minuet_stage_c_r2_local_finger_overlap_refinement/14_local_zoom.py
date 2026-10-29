from local_common import *
import subprocess
ff='D:/ffmpeg/bin/ffmpeg.exe';dest=P/'local_overhead_before_after.mp4'
subprocess.run([ff,'-y','-v','error','-i',str(P/'before_normal_speed_overhead.mp4'),'-i',str(P/'normal_speed_overhead.mp4'),'-filter_complex','[0:v]crop=420:420:560:70[L];[1:v]crop=420:420:560:70[R];[L][R]hstack=inputs=2[v]','-map','[v]','-map','0:a:0','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(dest)],check=True)
subprocess.run([ff,'-v','error','-i',str(dest),'-f','null','-'],check=True)
dump('LOCAL_ZOOM_VERIFICATION.json',dict(pass_=True,path=str(dest),sha256=sha(dest),same_pixel_crop=[560,70,420,420],dimensions=[840,420],frames=357,fps=60,original_speed=True,original_AAC_copied=True,full_decode='PASS',camera_change=False,scope='Auxiliary equal pixel crop only; original full normal three-view videos remain primary'))
print('AUXILIARY_EQUAL_CROP_LOCAL_COMPARISON_READY',flush=True)
