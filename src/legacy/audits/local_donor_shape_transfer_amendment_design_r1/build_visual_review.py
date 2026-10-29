import sys
sys.dont_write_bytecode=True
from common import *
from PIL import Image,ImageDraw,ImageFont
LABELS=['CURRENT_STAGE4C_R2','OFFICIAL_L1_DONOR','TEMPORARY_FEASIBILITY_PROBE','FORMAL_AMENDMENT_CANDIDATE']
SMOKE=['FORMAL_AMENDMENT_CANDIDATE','TEMP_BIND','TEMP_IDX_MCP_15','TEMP_IDX_MCP_30','TEMP_IDX_MCP_45']
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
def sheet(labels,views,name,shade='FLAT',size=640):
 result=Image.new('RGB',(len(labels)*size,len(views)*(size+55)),(238,238,238));d=ImageDraw.Draw(result)
 for row,v in enumerate(views):
  for col,s in enumerate(labels):
   im=Image.open(OUT/f'renders/{s}_{v}_{shade}.png').convert('RGB')
   if im.size!=(size,size):im.thumbnail((size,size))
   x=col*size;y=row*(size+55);small=font
   for px in range(19,8,-1):
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',px)
    if d.textlength(s,font=small)<size-20:break
   d.text((x+10,y+4),s,font=small,fill='#222222');d.text((x+10,y+28),v+' | DESIGN REVIEW',font=small,fill='#555555');result.paste(im,(x,y+55))
 result.save(OUT/name)
sheet(LABELS,['CLOSE'],'FOUR_COLUMN_SOLID_REVIEW_R1.png')
sheet(LABELS,['GRAZING','SIDE','FULL_DORSAL','SILHOUETTE','WIRE'],'PRIMARY_VISUAL_INSPECTION_SHEET_R1.png',size=320)
sheet(SMOKE,['CLOSE','GRAZING','SIDE','FULL_DORSAL','WIRE'],'BIND_IDX_VISUAL_INSPECTION_SHEET_R1.png',size=320)
print('Plain-solid four-column review and matched inspection sheets generated')
