from common import *
import subprocess
from PIL import Image,ImageDraw,ImageFont
R1=ROOT/'experiments/hands_c1_dynamic_artist_correction_poc_r1'
v=read(R1/'CANDIDATE_2_FIXED_VALIDATION.json');reg=read(R1/'REGRESSION_DETAILS.json');ledger=read(R1/'CANDIDATE_2_FIXED_EDIT_LEDGER.json')
selected=[r for r in v['rows'] if r['illegal'] and 2.45<=r['time']<=2.92]
save('R1_EXISTING_EVIDENCE_READ.json',dict(summary=v['summary'],target_illegal_rows=selected,regressions=reg,ledger=ledger))
for view,name in [('OVERHEAD','C1_VS_REPAIRED_OVERHEAD_1X.mp4'),('SIDE','C1_VS_REPAIRED_SIDE_1X.mp4')]:
 folder=OUT/('review_'+view.lower());folder.mkdir()
 src=safe(R1/name);READS[str(src)]=sha(src)
 subprocess.run(['D:/ffmpeg/bin/ffmpeg.exe','-n','-v','error','-i',str(src),'-map','0:v:0','-fps_mode','passthrough',str(folder/'%03d.png')],check=True)
 indices=[41,47,49,57,59,62];sheet=Image.new('RGB',(2560,1320),'#101723');d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',25)
 for i,ix in enumerate(indices):
  x=(i%2)*1280;y=(i//2)*440
  im=Image.open(folder/f'{ix+1:03d}.png').convert('RGB').resize((1280,408));sheet.paste(im,(x,y+32));d.text((x+12,y+1),f'R1 VIDEO / {view} / t={2.1+ix/60:.6f}s',font=font,fill='white')
 sheet.save(OUT/f'R1_VIDEO_EXIT_REVIEW_{view}.png')
protection('EXISTING_VIDEO_INPUT_RECEIPT.json')
print('EXISTING_VIDEO_REVIEW_READY',len(selected),len(reg['key_depth_regressions_over_0_02mm']))
