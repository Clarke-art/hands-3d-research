from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
P=Path(__file__).resolve().parent
cases=json.loads((P/'RENDER_INPUT_R1.json').read_text())['cases']
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
def plate(name,title,rows,views,w=600):
 h=round(650*w/600);cols=len(views)*2;header=100;rh=h+45
 im=Image.new('RGB',(w*cols,header+rh*len(rows)), '#101b27');d=ImageDraw.Draw(im)
 d.text((18,12),title,font=font(26,True),fill='#e8eef7')
 d.text((18,52),'R2 RIGHT / LEFT CANDIDATE | reflected cameras | native face shading | HUMAN REVIEW PENDING',font=font(18),fill='#adc1d3')
 for ri,c in enumerate(rows):
  for vi,v in enumerate(views):
   for si,side in enumerate(['R','L']):
    x=(vi*2+si)*w;y=header+ri*rh
    d.text((x+12,y+9),f'{c} | {v} | '+('RIGHT R2' if side=='R' else 'LEFT'),font=font(17,True),fill='#e8eef7')
    tile=Image.open(P/'_render_tiles'/f'{c}__{v}__{side}.png').convert('RGB').resize((w,h),Image.Resampling.LANCZOS)
    im.paste(tile,(x,y+45))
 im.save(P/name)
plate('EVIDENCE_ZERO_RIGHT_VS_LEFT_R1.png','ZERO / RSSF - CANONICAL MIRROR', ['ZERO'],['PALMAR','DORSAL','FIRST_WEB'],400)
plate('EVIDENCE_MIRROR_POSE_REGRESSION_R1.png','SIX APPROVED CASES - PALMAR + DORSAL',cases,['PALMAR','DORSAL'],450)
plate('EVIDENCE_FIRST_WEB_MIRROR_R1.png','SIX APPROVED CASES - FIRST WEB',cases,['FIRST_WEB'],600)
for case in cases:
 plate('_render_tiles/'+case+'__REVIEW_PAIR.png',case+' - THREE PRODUCT VIEWS',[case],['PALMAR','DORSAL','FIRST_WEB'],400)
print('THREE_EVIDENCE_PLATES_COMPLETE')
