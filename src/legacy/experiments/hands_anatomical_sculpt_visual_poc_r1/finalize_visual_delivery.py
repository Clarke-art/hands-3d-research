import sys,json,hashlib,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(n,o):
 with (OUT/n).open('x',encoding='utf8') as f:json.dump(o,f,ensure_ascii=False,indent=2)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def font(n):return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
def text(im,p,s,n=25,c='#edf2f8'):ImageDraw.Draw(im).text(p,s,font=font(n),fill=c)
rows=read(OUT/'ROUND_2_RENDER_MANIFEST.json')
status={'A':'VISUAL_DISTORTION','B':'VISUAL_NO_MEANINGFUL_IMPROVEMENT'}
reasons={'A':'侧缘变化可见，但残留收腰／新的分段折点；未达到合理、自然的骨段皮肤轮廓。','B':'局部填充存在，但未形成足够清楚、可信的第一指蹼自然形体改善；S仍独立保留。'}
for region,ident,views in [('A',['BASE','OLD_A','NEW_A'],['OVERHEAD','A_CLOSE','A_TRUE_SIDE','A_PERSPECTIVE']),('B',['BASE','OLD_B','NEW_B'],['OVERHEAD','B_CLOSE','B_NEAR_SIDE','B_REVERSE'])]:
 src=OUT/(region+'_SCULPT_ROUND_2_NOT_APPROVED.blend');dest=OUT/(region+'_SCULPT_NOT_APPROVED.blend');assert not dest.exists()
 with dest.open('xb') as f:
  with src.open('rb') as r:shutil.copyfileobj(r,f)
 assert sha(src)==sha(dest)
 canvas=Image.new('RGB',(2880,3280),'#111b29');text(canvas,(25,15),region+' | 人体自然形态直接雕塑 · 原C1 2.600000秒 · 最终限定候选',34)
 for j,label in enumerate(['原C1 · 未修改','上轮A2 · Human已否决' if region=='A' else '上轮B1 · Human已否决','本轮第2轮 · 独立shape key = 1']):text(canvas,(j*960+20,75),label,26)
 y=125
 for view in views:
  label={'OVERHEAD':'正式正交俯视','A_CLOSE':'局部高清俯视 · 食指近节侧缘','A_TRUE_SIDE':'原C1骨平面真侧视 · 真实皮肤','A_PERSPECTIVE':'局部透视 · 保留软组织上下文','B_CLOSE':'局部高清俯视 · 第一指蹼下部','B_NEAR_SIDE':'虎口近侧视 · S核心及保护邻域保持固定','B_REVERSE':'反向观察 · 真实皮肤连续性'}[view]
  text(canvas,(22,y),label,24,'#bdd4e3');y+=40;height=540 if view=='OVERHEAD' else 720
  rr=[next(r for r in rows if r['identity']==i and r['view']==view) for i in ident]
  for attr in ['camera_matrix','type','ortho_scale','lens','resolution','material_object_color','flat_flags_hash','lighting']:assert all(r[attr]==rr[0][attr] for r in rr),attr
  for j,r in enumerate(rr):canvas.paste(Image.open(r['path']).convert('RGB').resize((960,height),Image.Resampling.LANCZOS),(j*960,y))
  y+=height+28
 text(canvas,(25,3104),status[region]+' — '+reasons[region],24,'#ffd492')
 text(canvas,(25,3151),'同时间／相机／光照／材质／倍率；原flat shading；无遮挡皮肤，没有隐藏模型或改变姿态。',24)
 text(canvas,(25,3194),'两轮已结束；手动key不是自动触发机制。有限安全检查不等于自然性或全曲验收通过。',23)
 text(canvas,(25,3233),'STOP — HUMAN REVIEW',26,'#ffd492')
 output=OUT/(region+'_SCULPT_HUMAN_REVIEW.png');assert not output.exists();canvas.save(output)
save('FINAL_SELECTION_AND_VISUAL_ASSESSMENT.json',{'task':'HANDS_ANATOMICAL_SCULPT_VISUAL_POC_R1','per_region':{r:{'result':status[r],'codex_visual_observation':reasons[r],'selected_round':2,'substantive_rounds_executed':2,'candidate':r+'_SCULPT_NOT_APPROVED.blend','source_round_file':r+'_SCULPT_ROUND_2_NOT_APPROVED.blend','source_and_delivery_bytes_identical':True,'human_approved':False} for r in ['A','B']},'no_success_inferred_from_displacement':True,'further_sculpt_performed':False,'A_B_combined':False,'stop':'STOP — HUMAN REVIEW'})
print('2 actual selected blends and 2 final visual panels created')

