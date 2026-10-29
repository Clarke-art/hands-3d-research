from common import *
import subprocess
import numpy as np
from PIL import Image
FF='D:/ffmpeg/bin/ffmpeg.exe';seq=read(OUT/'RENDER_SEQUENCE.json')['frames'];results=[]
for name,count,indices in [('C1_VS_IDLE_INDEX_B_OVERHEAD_1X.mp4',158,[0,26,48,59,74,81,82,112,130,157]),('C1_VS_IDLE_INDEX_B_OVERHEAD_0_5X.mp4',316,[0,52,96,118,148,162,164,224,260,314])]:
 select='+'.join(f'eq(n\\,{i})' for i in indices)
 proc=subprocess.run([FF,'-v','error','-i',str(OUT/name),'-vf','select='+select,'-vsync','0','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 assert proc.returncode==0,proc.stderr
 frames=np.frombuffer(proc.stdout,np.uint8).reshape(-1,840,2560,3);assert len(frames)==len(indices)
 qc=[]
 for ix,im in zip(indices,frames):
  src=ix if count==158 else ix//2;ref=np.array(Image.open(OUT/'comparison_frames'/f'{src:04d}.png').convert('RGB'))
  mae=float(np.mean(abs(im.astype(float)-ref)))
  qc.append(dict(frame=ix,reference=src,mae_255=mae,mean=float(im.mean()),std=float(im.std())))
  if count==158 and ix in [26,74,112,157]:Image.fromarray(im).save(OUT/f'VIDEO_QC_{ix:03d}.png')
 results.append(dict(video=name,expected_frames=count,checks=qc,pass_=all(r['mae_255']<8 and r['std']>10 for r in qc)))
save('MEDIA_VISUAL_QC.json',dict(results=results,pass_=all(r['pass_'] for r in results),method='Decode sampled frames from both videos and compare to exact side-by-side PNG source; preserves frame order/time labels and verifies no blank at shot boundary or transitions.'))
print('MEDIA_QC',[(r['video'],r['pass_'],max(x['mae_255'] for x in r['checks'])) for r in results],flush=True)
