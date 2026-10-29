from local_common import *
sys.path.insert(0,str(OLD/'_deps'))
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import subprocess,shutil
rows=read(P/'OVERLAP_TIMES_AND_GEOMETRY.json')['rows'];bad=[r for r in rows if r['intersecting_patch_triangle_pairs']]
print('INTERSECTED_FRAME_RANGE',bad[0]['frame'] if bad else None,bad[-1]['frame'] if bad else None,'COUNT',len(bad))
for f in [1,19,37,49,61,64,73,85,97,109,121,133,145,157,169,181,193,199]:
    r=rows[f-1];print('FRAME',f,'VIDEO',r['presentation_sec'],'MUSIC',r['music_sec'],'PAIRS',r['intersecting_patch_triangle_pairs'],'DIST',r['nearest_sampled_patch_distance_mm'],'PHASE',r['phases'])
nums=dict(np.load(P/'source_numeric.npz'))
for t in [.6,.8,1.,1.1,1.2,1.4,1.6,1.8,2.,2.2,2.5,2.8,3.]:
    i=np.argmin(abs(nums['times']-t));print('Q',t,'MIDDLE',nums['qdeg'][i,2].tolist(),'RING',nums['qdeg'][i,3].tolist())
for view in ['OVERHEAD','TEACHING','SIDE_OBLIQUE']:
    folder=P/'diagnostic_frames'/view
    subprocess.run(['D:/ffmpeg/bin/ffmpeg.exe','-y','-v','error','-i',str(C1/f'normal_speed_{view.lower()}.mp4'),'-vf',"select='between(n,91,198)'",'-fps_mode','passthrough','-start_number','91',str(folder/'%04d.png')],check=True)
    sheet=Image.new('RGB',(1600,1200),'#eeeade');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    for i,f in enumerate([90,96,102,108,114,120,132,144,156,168,180,192]):
        img=Image.open(folder/f'{f:04d}.png').convert('RGB').crop((550,70,1050,490)).resize((400,340));x=i%4*400;y=i//4*400;sheet.paste(img,(x,y+40));draw.text((x+4,y+4),f'frame{f+1} video{f/60:.3f}s / music{f/60-.35:.3f}s',font=font,fill='#173d32')
    sheet.save(P/f'diagnostic_right_{view.lower()}_1p5_3p2.jpg',quality=95)
arrow=Path('<USER_HOME>/AppData/Local/Temp/codex-clipboard-4d1a87e8-4d76-453f-844f-6b538c8369d7.png')
shutil.copyfile(arrow,P/'HUMAN_ARROW_REFERENCE.png')
receipt=read(P/'HUMAN_AUTHORITY_RECEIPT.json');receipt.update(arrow_screenshot_received=True,arrow_reference_sha256=sha(arrow),human_time_range_presentation_sec=[1,3]);dump('HUMAN_AUTHORITY_RECEIPT.json',receipt)
