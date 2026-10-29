import sys,json,shutil
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;LATEST=P.parent/'left_little_finger_moving_key_reachability_r1';sys.path.insert(0,str(P.parent/'piano_hand_static_to_dynamic_transition_r1'));import common as o
from PIL import Image,ImageDraw,ImageFont
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20);bold=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',31)
views=['TEACHING_TOP','SIDE_OBLIQUE','REASONABLE_CLOSE'];names=['TEACHING TOP VIEW','SIDE OBLIQUE','REASONABLE CLOSE'];(P/'_frames_A').mkdir(exist_ok=True)
for frame in [20,21,22]:
 for view in views:shutil.copyfile(LATEST/'_frames'/'L'/f'{frame:04}_{view}.png',P/'_frames_A'/f'{frame:04}_{view}.png')
def panel(im,y,state,frame,label):
 d=ImageDraw.Draw(im);d.text((20,y+5),label,font=font,fill='#244938')
 for j,(view,name) in enumerate(zip(views,names)):
  d.text((j*768+20,y+42),name,font=small,fill='#617465');im.paste(Image.open(P/f'_frames_{state}'/f'{frame:04}_{view}.png').convert('RGB'),(j*768,y+75))
a=Image.new('RGB',(2304,2270),'#f5f3ed');d=ImageDraw.Draw(a);d.text((24,16),'E2 / F#2 | 当前真实候选 · 三张连续60fps帧 · 未放大局部',font=bold,fill='#244938')
for row,frame in enumerate([20,21,22]):panel(a,75+row*685,'A',frame,f'A · MIDI {.4+frame/60:.6f}s · D2 下沉末段 / 持键')
d.text((24,2145),'E2：D2右邻白键，小指末节侧面；F#2：中指与无名指之间黑键，两指末节侧面。',font=font,fill='#244938');d.text((24,2190),'几何穿入已证实；常规画面未确认明显大面积穿键。标注位于画外，未覆盖真实形状。',font=font,fill='#617465');a.save(P/'EVIDENCE_E2_FSHARP2_CONFLICT_R1.png')
b=Image.new('RGB',(2304,1575),'#f5f3ed');d=ImageDraw.Draw(b);d.text((24,16),'同一时刻 / 同一相机 / 同一指关节 Action | 仅隔离外部 root',font=bold,fill='#244938');panel(b,75,'A',21,'A · 0.750s · 保存的动态root：E2 8顶点 / F#2 9顶点 · D2 skin gap 2.969mm');panel(b,765,'B',21,'B · 0.750s · 静态root反事实：E2 / F#2 命中均0 · D2 skin gap 7.689mm')
d.text((24,1460),'B仅为未保存的诊断评估，不是新候选或修复。root恢复净空，同时丢失D2接触。',font=font,fill='#244938');d.text((24,1505),'D3完整接触区间最大gap：A 1.983mm → B 6.653mm；0.750s时D3尚非主动接触。',font=font,fill='#617465');b.save(P/'EVIDENCE_ROOT_COUNTERFACTUAL_R1.png')
out={n:{'sha256':o.sha(P/n),'size':Image.open(P/n).size} for n in ['EVIDENCE_E2_FSHARP2_CONFLICT_R1.png','EVIDENCE_ROOT_COUNTERFACTUAL_R1.png']};(P/'EVIDENCE_MANIFEST_R1.json').write_text(json.dumps({'images':out,'whole_frames_only':True,'macro_crops':0,'overlays_on_geometry':False,'new_videos':0,'source_render_manifest_sha256':o.sha(P/'DIAGNOSTIC_RENDER_MANIFEST_R1.json')},indent=2),encoding='utf8');print('TWO_DIAGNOSTIC_EVIDENCE_IMAGES_READY')
