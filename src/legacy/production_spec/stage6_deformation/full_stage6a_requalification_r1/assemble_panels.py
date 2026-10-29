import sys
sys.dont_write_bytecode=True
from common import *
from PIL import Image,ImageDraw,ImageFont
M=read(OUT/'EVIDENCE_RENDER_MANIFEST_R1.json')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for row in M['renders']:
 p=OUT/row['path']
 if row['bind_left_posed_right']:
  stem=p.stem;left=OUT/'renders/_parts'/(stem+'_BIND.png');right=OUT/'renders/_parts'/(stem+'_POSED.png')
  if not left.exists():
   row['sha256']=sha(p);row['size']=[1280,844];continue
  with Image.open(left) as a,Image.open(right) as b:
   im=Image.new('RGB',(1280,844),'#323c49');im.paste(a,(0,44));im.paste(b,(640,44))
  d=ImageDraw.Draw(im);d.text((12,10),stem+' | BIND RSSF',font=font,fill='white');d.text((654,10),'POSED | isolated diagnostic flex',font=font,fill='white');d.line((640,44,640,844),fill='#dce1e7',width=2)
  im.save(p);left.unlink();right.unlink()
 else:
  if 'sha256' in row:continue
  with Image.open(p) as a:
   im=Image.new('RGB',(a.width,a.height+44),'#323c49');im.paste(a,(0,44))
  ImageDraw.Draw(im).text((12,10),p.stem+' | POSED FORENSIC CONTEXT',font=font,fill='white');im.save(p)
 row['sha256']=sha(p);row['size']=[1280,844]
M['panel_assembly_pending']=False;dump('EVIDENCE_RENDER_MANIFEST_R1.json',M)
# Compact visual QA sheet, retaining readable case/view labels.
sample=['IDX_MCP_15_FULL_SOLID','IDX_MCP_15_LOCAL_SOLID','IDX_MCP_30_LOCAL_PALMAR_SOLID','TH_IP_15_LOCAL_SOLID','TH_IP_45_CAP37_SOLID','TH_MCP_45_NAIL_SOLID','MID_MCP_45_FULL_SOLID','RNG_MCP_45_FULL_SOLID','LTL_MCP_45_FULL_SOLID']
sheet=Image.new('RGB',(1920,1344),'white')
for i,name in enumerate(sample):
 with Image.open(OUT/'renders'/(name+'.png')) as im:
  im.thumbnail((640,422));sheet.paste(im,((i%3)*640,(i//3)*448))
 ImageDraw.Draw(sheet).text(((i%3)*640+8,(i//3)*448+423),name,font=font,fill='#263647')
sheet.save(OUT/'renders/VISUAL_QA_CONTACT_SHEET.png')
print('ASSEMBLED',len(M['renders']),'independent matched panels')
