import sys,os,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];PREV=ROOT/'experiments/hands_index_root_webspace_anatomy_repair_r1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(n,x):
 content=json.dumps(x,ensure_ascii=False,indent=2,default=lambda a:a.tolist() if hasattr(a,'tolist') else a.item())
 if (OUT/n).exists():assert read(OUT/n)==json.loads(content);return
 with (OUT/n).open('x',encoding='utf8') as f:f.write(content)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def font(n):return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
def put(im,xy,s,n=24,c='#edf3f8'):ImageDraw.Draw(im).text(xy,s,font=font(n),fill=c)
def output(n,im):
 if not (OUT/n).exists():im.save(OUT/n)
 FIGURES.append(n)
FIGURES=[]
ROWS=read(OUT/'RENDER_MANIFEST.json')+read(OUT/'EXTRA_RENDER_MANIFEST.json')
if (OUT/'TRUE_SIDE_REVISED_RENDER_MANIFEST.json').exists():
 ROWS=[r for r in ROWS if not(r['view']=='TRUE_SIDE' and r['pose']=='C1_2_600000')]+read(OUT/'TRUE_SIDE_REVISED_RENDER_MANIFEST.json')
def row(k,p,v):return next(r for r in ROWS if r['candidate']==k and r['pose']==p and r['view']==v)
def image(k,p,v):return Image.open(row(k,p,v)['path']).convert('RGB')
LABEL={'BASE':'原 C1 / 未修改资产','A1':'A1 · 局部侧向轮廓收整','A2':'A2 · 局部法向形体收整','B1':'B1 · 4点 CMC→WRIST 权重','B2':'B2 · 4点临时 corrective = 1'}
state='C1_2_600000'
for prefix,kinds in [('A',['BASE','A1','A2']),('B',['BASE','B1','B2'])]:
 im=Image.new('RGB',(2700,690),'#111b29');put(im,(24,12),prefix+' | 正式正交俯视 · 原 C1 2.600000秒 · 同镜头／倍率／flat shading',32)
 for j,k in enumerate(kinds):
  put(im,(j*900+18,65),LABEL[k],25);im.paste(image(k,state,'OVERHEAD').resize((900,506)),(j*900,110))
 put(im,(22,636),'局部修补不是姿态修复；原 C1 既有穿键仍保留。所有候选均 NOT_APPROVED；未合并 A+B。',25,'#ffd492')
 output(prefix+'_OFFICIAL_OVERHEAD.png',im)
viewsA=[('A_CLOSE','食指靠虎口侧 · 局部俯视'),('TRUE_SIDE','真实网格 · 相对原 C1 骨平面真侧视')]
viewsB=[('B_CLOSE','第一指蹼下部 · 局部俯视'),('S_SIDE','侧视 · S 核心不编辑，B 邻面可变化'),('B_REVERSE','反向观察 · 不能只看最好的一面')]
for prefix,kinds,views in [('A',['BASE','A1','A2'],viewsA),('B',['BASE','B1','B2'],viewsB)]:
 h=155+len(views)*740+105;im=Image.new('RGB',(2700,h),'#111b29');put(im,(25,10),prefix+' | 原 C1 2.600000秒 · 真实 evaluated mesh 多视角比较',34)
 for j,k in enumerate(kinds):put(im,(j*900+18,63),LABEL[k],27)
 for i,(v,label) in enumerate(views):
  yy=110+i*740;put(im,(20,yy),label,25,'#bdd8e8')
  for j,k in enumerate(kinds):im.paste(image(k,state,v).resize((900,675)),(j*900,yy+40))
 put(im,(22,h-82),'实际面片保持 flat shading；没有用 smooth shading 掩盖几何。相机投影逐行完全一致。',24,'#ffd492')
 put(im,(22,h-43),'A 的旧 corrective 差分耦合仍存在；B2 为手动方法验证，没有新 driver。最终自然性待 Human。',23)
 output(prefix+'_LOCAL_MULTIVIEW.png',im)
POSES=[('NEUTRAL_REST','原Rig中性 / REST'),('C1_0_433333','C1 0.433333秒'),('C1_1_100000','C1 1.100000秒 / ACTIVE A4'),('C1_2_600000','C1 2.600000秒'),('FIXED_GEOMETRY_PASS','历史固定几何PASS / 自然性未批准'),('C1_CORRECTIVE_ACTIVE','C1 0.885714秒 / 旧corrective=0.942')]
def multi(prefix,kinds,view,title):
 cellw=760;cellh=550;header=120;footer=100;im=Image.new('RGB',(cellw*3,header+6*cellh+footer),'#111b29');put(im,(20,10),title,32)
 for j,k in enumerate(kinds):put(im,(j*cellw+18,63),LABEL[k],24)
 for i,(p,lab) in enumerate(POSES):
  y=header+i*cellh;put(im,(18,y+2),lab,22,'#bdd8e8')
  for j,k in enumerate(kinds):
   # Identical crop and scaling for all cells; no shape retouch.
   pic=image(k,p,view).crop((100,135,860,605));im.paste(pic,(j*cellw,y+35))
  if prefix=='A':
   note='激活旧corrective时，A效果被抵消约94%；不是新碰撞。' if p=='C1_CORRECTIVE_ACTIVE' else '基线既有缺陷保留；此行未发现新增碰撞或触键回退。'
  elif prefix=='B':note='B1 中性姿态位移=0；B2 本轮所有姿态均手动设为1，未形成自动触发。' if p=='NEUTRAL_REST' else 'S核心顶点误差=0；未发现新增碰撞，局部饱满度仍待Human判断。'
  else:note='S核心几何完全不变；邻近B面片变化不等于解决S的独立异常。'
  put(im,(20,y+cellh-27),note,19,'#d3dce6')
 put(im,(20,header+6*cellh+18),'同一行使用同一 BASE 相机、姿态与倍率；各姿态只平移局部镜头到基线ROI中心。',22)
 put(im,(20,header+6*cellh+55),'没有新动作、姿态修正或组合资产；六种实际状态均逐一检查。',22,'#ffd492')
 output(prefix+'_MULTIPOSE.png',im)
multi('A',['BASE','A1','A2'],'A_CLOSE','A | 六种状态 · 局部轮廓比较')
multi('B',['BASE','B1','B2'],'B_CLOSE','B | 六种状态 · 第一指蹼比较')
multi('S',['BASE','B1','B2'],'S_SIDE','S | 六种状态 · 独立侧视观察，核心禁止编辑')
# Geometry facts accompany the images; these are descriptive, not an anatomical score.
top=read(PREV/'NATIVE_TOPOLOGY.json');F=np.array(top['faces']);E=np.array(top['edges'])
def normals(v):
 p=v[F];fn=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0])+np.cross(p[:,2]-p[:,0],p[:,3]-p[:,0]);n=np.zeros_like(v)
 for j in range(4):np.add.at(n,F[:,j],fn)
 return n/np.linalg.norm(n,axis=1)[:,None]
summary={}
for k in ['BASE','A1','A2','B1','B2']:
 rec={}
 for p,_ in POSES:
  v=np.load(OUT/(k+'__'+p+'.npz'))['V'];n=normals(v);i=1376;nei=sorted({int(b) if a==i else int(a) for a,b in E if a==i or b==i});normal_lap=float((v[nei].mean(0)-v[i])@n[i]*1000)
  data=read(OUT/(k+'__'+p+'.json'));rec[p]={'v1376_signed_one_ring_normal_residual_mm':normal_lap,'geometry_regression':data.get('geometry_regression',False),'max_skin_shift_mm':data.get('max_skin_shift_mm',0),'shape_values':data['shape_values']}
 summary[k]=rec
save('DESCRIPTIVE_SHAPE_COMPARISON.json',summary)
for view,kinds in [('OVERHEAD',['BASE','A1','A2','B1','B2']),('A_CLOSE',['BASE','A1','A2']),('B_CLOSE',['BASE','B1','B2']),('TRUE_SIDE',['BASE','A1','A2']),('S_SIDE',['BASE','B1','B2']),('B_REVERSE',['BASE','B1','B2'])]:
 for p,_ in POSES:
  rows=[r for r in ROWS if r['pose']==p and r['view']==view and r['candidate'] in kinds]
  if rows:
   assert all(r['matrix']==rows[0]['matrix'] and r['ortho_scale']==rows[0]['ortho_scale'] and r['resolution']==rows[0]['resolution'] for r in rows)
save('CORE_REVIEW_IMAGE_MANIFEST.json',{'core_image_count':len(FIGURES),'images':[dict(path=str(OUT/n),sha256=sha(OUT/n)) for n in FIGURES],'same_camera_projection_verified':True,'image_retouch':False})
print(json.dumps({'core_images':FIGURES,'B_residual_2_6':{k:summary[k]['C1_2_600000']['v1376_signed_one_ring_normal_residual_mm'] for k in ['BASE','B1','B2']}},ensure_ascii=False))
