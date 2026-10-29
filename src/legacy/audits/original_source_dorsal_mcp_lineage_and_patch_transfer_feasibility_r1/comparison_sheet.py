import sys
sys.dont_write_bytecode=True
from common import *
from PIL import Image,ImageDraw,ImageFont
labels=[('STAGE4C_R2','CURRENT'),('OFFICIAL_L1','OFFICIAL L1 DONOR'),('TRANSFER_PROBE','DESIGN ONLY TRANSFER PROBE')]
canvas=Image.new('RGB',(1920,732),'#edf2f6');draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
for k,(stage,title) in enumerate(labels):
 draw.text((k*640+18,15),title,fill='#203e55',font=font)
 canvas.paste(Image.open(OUT/'renders'/f'{stage}_CLOSE_FLAT.png').convert('RGB'),(k*640,52))
draw.text((18,703),'MATCHED CAMERA / SCALE / LIGHTING   |   NOT_PRODUCTION   |   NOT_APPROVED   |   STOP - HUMAN REVIEW',fill='#203e55',font=font)
canvas.save(OUT/'CURRENT_DONOR_TRANSFER_MATCHED_CLOSE.png')
print('Matched comparison sheet created; source pixels unchanged')
