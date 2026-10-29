from common import *
import numpy as np
from PIL import Image,ImageDraw,ImageFont
FONT='C:/Windows/Fonts/msyh.ttc';font=lambda n:ImageFont.truetype(FONT,n)
GREEN='#35e38a';CYAN='#00e5ff';GOLD='#ffda57';RED='#ff485d';PINK='#ff73e7';WHITE='#eeeeee'
geo=read(OUT/'ANATOMICAL_SAMPLES_AND_METHOD.json');M=np.array(geo['camera_matrix']);W=geo['orthographic_scale'];H=W*720/1280
keys=read(OLD/'KEYBOARD_88_KEY_TABLE_R1.json')['keys'];deep=read(OUT/'INDEX_BLACK_KEY_REAL_GEOMETRY.json')
extract(OUT/'make_media.py',['px','hull','cross','dash','seam','annotate'],globals())
r=read(OUT/'NINTH_STILL_PROJECTION.json');im=annotate(Image.open(r['raw_path']),r);d=ImageDraw.Draw(im)
k=next(k for k in keys if k['note_name']=='D#5');a=k['key_top_playable_surface'][0]
d.line([px(a['xmin'],a['ymin']),px(a['xmax'],a['ymin']),px(a['xmax'],a['ymax']),px(a['xmin'],a['ymax']),px(a['xmin'],a['ymin'])],fill=RED,width=2)
dr=read(OUT/'MIDDLE_ACTIVE_NEIGHBOR_BLACK_DEEP.json')[1];c=max(dr['triangle_certificates'],key=lambda a:a['lower_mm']);p=c['witness_world_m'];cross(d,px(p[0],p[1]),RED,7,2)
out=Image.new('RGB',(1920,1080),'#141b24');out.paste(im,(0,64));out.paste(im.crop((610,80,910,400)).resize((600,640),Image.Resampling.LANCZOS),(1300,80));d=ImageDraw.Draw(out)
d.text((22,16),f"DIAGNOSTIC_ONLY | ORIGINAL_C1 | t={r['time']:.6f}s | R3 ACTIVE E5",font=font(25),fill=WHITE)
lines=['中指按E5时：pad接触PASS，但手指皮肤穿入相邻D#5。','实际三角面内部深度1.341mm；红十字为面内见证点。','顶点深度仅0.518mm，说明仅看顶点还会低估面内侵入。']
for i,t in enumerate(lines):d.text((26,810+i*38),t,font=font(24),fill=WHITE)
for i,(t,col) in enumerate([('青：真实skin pad / 绿：E5合法面',CYAN),('黄：末端皮肤点 / 白：末端包络',GOLD),('红框：D#5 / 红十字：真实侵入',RED)]):d.text((1110,810+i*42),t,font=font(22),fill=col)
d.text((1310,736),'同一正俯视画面局部放大 2×',font=font(22),fill=WHITE)
d.text((26,957),f"triangle {c['triangle_index']} vertices {c['vertices']} | witness XYZ (mm): "+', '.join(f'{v*1000:.3f}' for v in p),font=font(21),fill='#bec8d7')
d.text((26,997),'所有标记均由原相机投影；未改变动作、键体或验收标准。DIAGNOSTIC_ONLY',font=font(22),fill='#bec8d7')
dest=OUT/'09_MIDDLE_ACTIVE_E5_DIAGNOSTIC_ONLY.png';assert not dest.exists();out.save(dest)
save('NINTH_IMAGE_RECEIPT.json',dict(path=str(dest),sha256=sha(dest),surface_witness_world_m=p,surface_witness_pixel=px(p[0],p[1]),triangle=c))
