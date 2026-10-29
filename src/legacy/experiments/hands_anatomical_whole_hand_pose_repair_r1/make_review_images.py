from common import *
from PIL import Image,ImageDraw,ImageFont
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
best=read(OUT/'ROUND_2_DATA.json');geo=read(OUT/'SAVED_REOPEN_MACHINE_VALIDATION.json');original=read(OUT/'BASELINE_FACTS.json')
def gap(name):return min(r['exact_clearance_mm'] for r in geo['keys'] if r['key']==name)
generated=[]
for view,title in [('OVERHEAD','正式 STAGE_C_OVERHEAD'),('SIDE_OBLIQUE','原场景侧斜视'),('AUX_INDEX_SIDE','固定辅助近侧视'),('AUX_PALM_PERSP','固定掌腕透视')]:
 canvas=Image.new('RGB',(2560,970),'#111927');d=ImageDraw.Draw(canvas)
 for i,identity in enumerate(['ORIGINAL','CURRENT_BEST']):
  im=Image.open(OUT/f'{identity}_{view}_MATCHED.png').convert('RGB');canvas.paste(im,(i*1280,65));x=i*1280+20
  d.text((x,12),f"{'原 C1' if i==0 else '本轮第二候选 · NOT_APPROVED'} | 2.600000s | {title}",font=font(26),fill='white')
  lines=(['食指 A#4 穿入 5.637124mm；零净空','整手另有 A4 0.745018mm、C#5 4.252741mm 非目标键侵入','拇指 G4 为活动目标键；左手 B3 接触保持原状'] if i==0 else [f'非目标琴键相交 0；A#4 净空 {gap("A#4"):.6f}mm',f'A4 净空 {gap("A4"):.6f}mm；C#5 净空 {gap("C#5"):.6f}mm',f'G4 接触保留；腕移 5.537mm / 朝向变化 4.123°；等待 Human 自然性审核'])
  for j,line in enumerate(lines):d.text((x,805+j*46),line,font=font(25),fill='#cad7e7' if i==0 else '#bce1d7')
 dst=OUT/f'COMPARISON_{view}.png';assert not dst.exists();canvas.save(dst);generated.append(dst.name)
# Uniform registered crop from the official overhead for index close-up.
crop=(660,95,840,300);size=(900,1025)
canvas=Image.new('RGB',(1800,1190),'#111927');d=ImageDraw.Draw(canvas)
for i,identity in enumerate(['ORIGINAL','CURRENT_BEST']):
 im=Image.open(OUT/f'{identity}_OVERHEAD_MATCHED.png').convert('RGB').crop(crop).resize(size)
 canvas.paste(im,(i*900,65));d.text((i*900+20,12),f"{'原 C1' if i==0 else '本轮第二候选 · NOT_APPROVED'} | 同俯视等倍率局部",font=font(26),fill='white')
 d.text((i*900+20,1110),'不得凭投影判断穿模；实际网格读数见完整图及 JSON',font=font(24),fill='#c6d4e8')
dst=OUT/'COMPARISON_INDEX_CLOSE.png';canvas.save(dst);generated.append(dst.name)
for view in ['OVERHEAD','AUX_INDEX_SIDE']:
 if view=='OVERHEAD':crop=(610,80,940,670);size=(660,1180)
 else:crop=None;size=(960,540)
 width=size[0]*3;height=size[1]+210;canvas=Image.new('RGB',(width,height),'#111927');d=ImageDraw.Draw(canvas)
 for i,(identity,label,q) in enumerate([('ORIGINAL','原 C1',[16.865,17.383,9.053,-13.787]),('PREVIOUS_REJECTED','前轮第三候选 · Human 已否决',[2,26,14,-24.5]),('CURRENT_BEST','本轮第二候选 · 等待 Human',[8,12,6,-12])]):
  im=Image.open(OUT/f'{identity}_{view}_MATCHED.png').convert('RGB')
  if crop:im=im.crop(crop)
  im=im.resize(size);canvas.paste(im,(i*size[0],70));x=i*size[0]+15
  d.text((x,16),label,font=font(25 if size[0]==660 else 29),fill='white')
  d.text((x,size[1]+85),f'MCP/PIP/DIP/展指：{q[0]:g}/{q[1]:g}/{q[2]:g}/{q[3]:g}°',font=font(23),fill='#cad7e7')
  d.text((x,size[1]+130),'同时间、同相机、同裁切/倍率；请判断实际轮廓',font=font(22),fill='#cad7e7')
 d.text((18,height-38),'自然性专项：不按穿入深度排名；本轮未获 Human 批准，未制作连续动画。',font=font(23),fill='#ffd08a')
 dst=OUT/f'NATURALITY_TRIPTYCH_{view}.png';canvas.save(dst);generated.append(dst.name)
save('REVIEW_IMAGE_MANIFEST.json',dict(images=[dict(path=str(OUT/n),sha256=sha(OUT/n)) for n in generated],source='Actual matched Blender renders; no model retouch, masking or camera changes between subjects.',uniform_crop_overhead=[610,80,940,670],index_crop=[660,95,840,300],previous='Human-rejected previous static pose, used only for comparison.'))
print('REVIEW_IMAGES_DONE',len(generated),flush=True)
