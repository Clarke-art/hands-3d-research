import sys
sys.dont_write_bytecode=True
from common import *
from PIL import Image,ImageDraw,ImageFont
labels=['SOURCE_STAGE4C_R2','APPROVED_FORMAL_CANDIDATE','APPLIED_NEW_STAGE4C_REVISION']
def sheet(views,name,size):
 canvas=Image.new('RGB',(3*size,len(views)*(size+55)),(238,238,238));d=ImageDraw.Draw(canvas)
 for row,v in enumerate(views):
  for col,l in enumerate(labels):
   im=Image.open(OUT/f'renders/{l}_{v}_FLAT.png').convert('RGB')
   if im.size!=(size,size):im.thumbnail((size,size))
   for px in range(19,8,-1):
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',px)
    if d.textlength(l,font=font)<size-20:break
   x=col*size;y=row*(size+55);d.text((x+10,y+4),l,font=font,fill='#222');d.text((x+10,y+28),v+' | APPLICATION / NOT PROMOTED',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',min(14,max(9,px-2))),fill='#555');canvas.paste(im,(x,y+55))
 canvas.save(OUT/name)
sheet(['CLOSE'],'THREE_COLUMN_APPLICATION_SOLID_R1.png',640)
sheet(['GRAZING','SIDE','FULL_DORSAL','SILHOUETTE','WIRE'],'APPLICATION_VISUAL_INSPECTION_SHEET_R1.png',400)
print('Application three-column plain-solid and full matched inspection sheet generated')
