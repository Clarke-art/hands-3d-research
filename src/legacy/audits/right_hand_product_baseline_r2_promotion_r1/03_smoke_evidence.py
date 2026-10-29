from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
import json
OUT=Path(__file__).resolve().parent
def font(n,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),n)
cv=Image.new('RGB',(1920,2930),'#101b27');d=ImageDraw.Draw(cv)
d.text((20,15),'R2 PROMOTION SMOKE | EXACT APPROVED DEFORMATION DATA',font=font(31,True),fill='#e4eef7')
d.text((20,63),'Approved candidate LEFT / clean R2 RIGHT | ZERO / F130 / FULL_OPP_L3 only | no requalification',font=font(23),fill='#a9bfd2')
checks=[]
for row,state in enumerate(['ZERO','F130','FULL_OPP_L3']):
    images=[]
    for col,label in enumerate(['APPROVED_CANDIDATE','R2']):
        im=Image.open(OUT/'smoke_renders'/f'{label}__{state}__REASONABLE_CLOSE_VIEW.png').convert('RGB');images.append(im)
        x=col*960;y=110+row*940
        d.text((x+12,y+8),state+' | '+label,font=font(25,True),fill='#e4eef7')
        cv.paste(im,(x,y+40))
    assert ImageChops.difference(images[0],images[1]).getbbox() is None,state
    checks.append({'state':state,'matched_neutral_product_view_pixels_exact':True})
cv.save(OUT/'EVIDENCE_PROMOTION_SMOKE_R1.png')
(OUT/'SMOKE_VISIBLE_COMPARISON_R1.json').write_text(json.dumps({'status':'PASS','scope':'Three minimal states only; native evaluated positions and matched pixels are identical','checks':checks,'full_qualification_repeated':False},indent=2)+'\n',encoding='utf-8')
print('MINIMAL_SMOKE_EXACT_3_STATES')
