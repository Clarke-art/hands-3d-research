import sys,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;roundno=int(sys.argv[1]) if len(sys.argv)>1 else 1
rows=json.loads((OUT/('ROUND_'+str(roundno)+'_RENDER_MANIFEST.json')).read_text(encoding='utf8'))
def font(n):return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
def text(im,p,s,n=26,c='#edf2f8'):ImageDraw.Draw(im).text(p,s,font=font(n),fill=c)
def row(i,v):return next(r for r in rows if r['identity']==i and r['view']==v)
for region,ident,views in [('A',['BASE','OLD_A','NEW_A'],['OVERHEAD','A_CLOSE','A_TRUE_SIDE','A_PERSPECTIVE']),('B',['BASE','OLD_B','NEW_B'],['OVERHEAD','B_CLOSE','B_NEAR_SIDE','B_REVERSE'])]:
 canvas=Image.new('RGB',(2880,3160),'#111b29')
 text(canvas,(25,15),region+' | 人体自然形态直接雕塑 · 原C1 2.600000秒 · 第'+str(roundno)+'轮',36)
 for j,label in enumerate(['原C1 · 未修改','上轮A2 · Human已否决' if region=='A' else '上轮B1 · Human已否决','本轮独立雕塑 key = 1 · 未批准']):text(canvas,(j*960+20,75),label,26)
 y=125
 for view in views:
  label={'OVERHEAD':'正式正交俯视','A_CLOSE':'局部高清俯视 · 食指近节侧缘','A_TRUE_SIDE':'原C1骨平面真侧视 · 真实皮肤','A_PERSPECTIVE':'局部透视 · 保留软组织厚度','B_CLOSE':'局部高清俯视 · 第一指蹼下部','B_NEAR_SIDE':'虎口近侧视 · S核心与保护邻域固定','B_REVERSE':'反向观察 · 真实皮肤连续性'}[view]
  text(canvas,(22,y),label,24,'#bdd4e3');y+=40
  height=540 if view=='OVERHEAD' else 720
  selected=[row(i,view) for i in ident]
  for attr in ['camera_matrix','type','ortho_scale','lens','resolution','material_object_color','flat_flags_hash','lighting']:
   assert all(r[attr]==selected[0][attr] for r in selected),attr
  for j,r in enumerate(selected):
   im=Image.open(r['path']).convert('RGB').resize((960,height),Image.Resampling.LANCZOS);canvas.paste(im,(j*960,y))
  y+=height+28
 text(canvas,(25,3048),'同时间、相机、光照、材质、倍率；保持原flat shading。没有隐藏手或琴键，没有改变姿态。',25,'#ffd492')
 text(canvas,(25,3094),'新shape key只在隔离副本中手动启用；不代表自动触发、完整动画验收或Human自然性批准。',23)
 dest=OUT/('ROUND_'+str(roundno)+'_'+region+'_VISUAL_REVIEW.png');assert not dest.exists();canvas.save(dest)
print('visual panels ready',roundno)

