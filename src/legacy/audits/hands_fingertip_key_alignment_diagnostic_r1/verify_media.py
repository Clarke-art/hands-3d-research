from common import *
import subprocess
import numpy as np
from PIL import Image
FF='D:/ffmpeg/bin/ffmpeg.exe';source=safe(C1/'normal_speed_overhead.mp4');dest=OUT/'C1_OVERHEAD_ALIGNMENT_DIAGNOSTIC_1X.mp4'
def decoder(path):return subprocess.Popen([FF,'-v','error','-i',str(path),'-map','0:v:0','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
a=decoder(source);b=decoder(dest);rows=[];still_errors=[]
stills={67:'01_INDEX_ACTIVE_A4',79:'02_MIDDLE_ACTIVE_B4',208:'03_MIDDLE_ACTIVE_C5',27:'04_INDEX_IDLE_GSHARP',157:'05_INDEX_IDLE_ASHARP',86:'06_C1_B01_HANDOFF'}
for i in range(1,358):
    aa=a.stdout.read(1280*720*3);bb=b.stdout.read(1280*720*3);assert len(aa)==len(bb)==1280*720*3
    av=np.frombuffer(aa,np.uint8).reshape(720,1280,3);bv=np.frombuffer(bb,np.uint8).reshape(720,1280,3)
    # All annotation is outside this left-hand scene region. This checks the
    # original frame sequence was retained, not just a matching container clock.
    diff=np.abs(av[38:655,:590].astype(float)-bv[38:655,:590]);rows.append(dict(frame=i,unannotated_region_mae=float(diff.mean()),scene_mean=float(bv[38:655].mean())))
    if i in stills:
        raw=np.asarray(Image.open(OUT/'raw_stills'/(stills[i]+'.png')).convert('RGB'));still_errors.append(dict(frame=i,still=stills[i],full_native_render_to_original_video_mae=float(np.abs(av.astype(float)-raw).mean())))
assert a.stdout.read(1)==b.stdout.read(1)==b'';a.stdout.close();b.stdout.close();assert a.wait()==b.wait()==0
assert max(r['unannotated_region_mae'] for r in rows)<3 and min(r['scene_mean'] for r in rows)>20
assert max(r['full_native_render_to_original_video_mae'] for r in still_errors)<3
save('FRAME_SEQUENCE_AND_NATIVE_RENDER_CHECK.json',dict(pass_=True,frames=357,max_unannotated_region_mae=max(r['unannotated_region_mae'] for r in rows),native_still_checks=still_errors,frame_checks=rows,no_black_frames=True,frame_sequence_preserved=True,limitation='Pixel comparison confirms original visual sequence outside diagnostic overlays; natural held frames are retained. Not a contact/safety PASS.'))
protection('MEDIA_SEQUENCE_SHA_RECEIPT.json')
