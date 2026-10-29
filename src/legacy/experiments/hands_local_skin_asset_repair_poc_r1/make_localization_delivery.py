import sys,os,json,hashlib,re
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PREV=ROOT/'experiments/hands_index_root_webspace_anatomy_repair_r1'
def safe(p):
 p=Path(p).absolute()
 assert p.is_relative_to(ROOT),'OUTSIDE_HANDS'
 assert not any(a.is_symlink() or a.is_junction() for a in [p,*p.parents] if a.is_relative_to(ROOT)),'REPARSE'
 assert p.resolve().is_relative_to(ROOT)
 return p
def guard(event,args):
 if event not in ['open','os.mkdir','os.remove','os.rename'] or not args or not isinstance(args[0],(str,bytes,os.PathLike)):return
 p=Path(os.fsdecode(args[0])).absolute()
 assert '/3d interactive components/piano' not in p.as_posix().lower(),'PIANO_FORBIDDEN'
 writing=event!='open'
 if event=='open':
  mode,flags=args[1:3];writing=(isinstance(mode,str) and any(x in mode for x in 'wax+')) or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
 if writing:assert p.is_relative_to(OUT),'WRITE_OUTSIDE_EXPERIMENT'
sys.addaudithook(guard)
def load(p):return json.loads(safe(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with safe(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(name,obj):
 with (OUT/name).open('x',encoding='utf8') as f:json.dump(obj,f,ensure_ascii=False,indent=2)
def md(name,s):
 with (OUT/name).open('x',encoding='utf8') as f:f.write(s)
protected=load(PREV/'PROTECTED_SHA256_BEFORE_AFTER.json')['files']
inputs={r['path']:sha(r['path']) for r in protected}
assert all(inputs[r['path']]==r['after'] for r in protected),'HISTORICAL_INPUT_CHANGED'
extra=['DIAGNOSTIC_RENDER_MANIFEST.json','EXACT_TRUE_SIDE_MANIFEST.json','NATIVE_TOPOLOGY.json','ORIGINAL_SNAPSHOT.json','REJECTED_GEOMETRY_PASS_SNAPSHOT.json','ANATOMICAL_CAUSE_REPORT.md','ANATOMICAL_DIAGNOSTIC_WITH_TRUE_SIDE.blend']
idents=['ORIGINAL','REJECTED_GEOMETRY_PASS'];views=['OVERHEAD','EXACT_SOURCE_TRUE_SIDE','WEB_REVERSE']
extra += [f'{i}__NATIVE__{v}.png' for i in idents for v in views]
for n in extra:inputs[str(PREV/n)]=sha(PREV/n)
inputs[str(PREV/'PROTECTED_SHA256_BEFORE_AFTER.json')]=sha(PREV/'PROTECTED_SHA256_BEFORE_AFTER.json')
save('PROTECTED_BEFORE.json',dict(files=[dict(path=k,sha256=v) for k,v in inputs.items()]))
import numpy as np
from PIL import Image,ImageDraw,ImageFont
rows=load(PREV/'DIAGNOSTIC_RENDER_MANIFEST.json')+load(PREV/'EXACT_TRUE_SIDE_MANIFEST.json');top=load(PREV/'NATIVE_TOPOLOGY.json');E=np.array(top['edges']);F=np.array(top['faces'])
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
def text(im,xy,s,size=22,color='#f3f5f8'):ImageDraw.Draw(im).text(xy,s,font=font(size),fill=color)
canvas=Image.new('RGB',(2400,1670),'#17202c')
text(canvas,(26,12),'需要Human定位：食指靠虎口侧轮廓 / 虎口根部面片',34)
text(canvas,(26,60),'仅复用已有真实Blender渲染；所有网格、姿态、光照均未编辑。无Human红箭头原图，当前无已确认编辑ROI。',23)
paneldefs=[('OVERHEAD',(600,90,960,640),432,660),('EXACT_SOURCE_TRUE_SIDE',(0,0,1280,720),984,660),('WEB_REVERSE',(0,0,1280,720),984,660)]
maps=[]
for row,ident in enumerate(idents):
 text(canvas,(26,110+row*720),('上排 A：原C1' if row==0 else '下排 B：上轮固定几何PASS姿态，Human自然性已否决')+' | 2.600000秒',26)
 xbase=0
 for col,(view,crop,width,height) in enumerate(paneldefs):
  meta=next(r for r in rows if r['identity']==ident and r['variant']=='NATIVE' and r['view']==view)
  title=['正式正交俯视（右手局部裁切）','食指真侧视（相对原C1骨平面）','虎口反向'][col];panelno=row*3+col+1
  panel=Image.new('RGB',(width,height),'#212c39');text(panel,(12,8),f'P{panelno} {title}',21)
  original=Image.open(meta['path']).convert('RGBA');lay=Image.new('RGBA',original.size);d=ImageDraw.Draw(lay)
  m=load(PREV/(ident+'_SNAPSHOT.json'));ctx=set(m['rois']['A']['vertices'])|set(m['rois']['B']['vertices']);P=np.array(meta['all_vertex_pixels'])
  for a,b in E:
   if a in ctx and b in ctx:d.line([tuple(P[a]),tuple(P[b])],fill=(0,110,160,80),width=1)
  for name in ['INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R']:
   points=meta['bones'][name]['pixels'];d.line([tuple(points[0]),tuple(points[1])],fill=(250,185,20,220),width=3)
   xx,yy=points[0];d.ellipse((xx-5,yy-5,xx+5,yy+5),fill=(250,185,20,240))
  for v in [629,2018]:
   xx,yy=P[v];d.ellipse((xx-6,yy-6,xx+6,yy+6),fill=(210,0,240,255));d.text((xx+9,yy),f'v{v}',font=font(22),fill=(210,0,240,255),stroke_width=1,stroke_fill='black')
  actual=Image.alpha_composite(original,lay).convert('RGB').crop(crop)
  scale=min(width/actual.width,(height-58)/actual.height);sz=(round(actual.width*scale),round(actual.height*scale));actual=actual.resize(sz,Image.Resampling.LANCZOS);x=(width-sz[0])//2;y=50;panel.paste(actual,(x,y));dd=ImageDraw.Draw(panel)
  for k in range(7):
   gx=x+round(k*sz[0]/6);dd.line((gx,y,gx,y+sz[1]),fill='#6d8194',width=1)
  for k in range(5):
   gy=y+round(k*sz[1]/4);dd.line((x,gy,x+sz[0],gy),fill='#6d8194',width=1)
  for rr in range(4):
   for cc in range(6):
    gx=x+round(cc*sz[0]/6)+5;gy=y+round(rr*sz[1]/4)+3;dd.text((gx,gy),chr(65+cc)+str(rr+1),font=font(18),fill='white',stroke_width=1,stroke_fill='#263543')
  canvas.paste(panel,(xbase,155+row*720));maps.append(dict(panel=f'P{panelno}',identity=ident,view=view,source=meta['path'],source_crop=crop,scale=scale,canvas_origin=[xbase+x,155+row*720+y],grid=[6,4],camera_matrix=meta['camera_matrix'],reference_vertices=[629,2018],confirmed_edit_roi=False));xbase+=width
text(canvas,(22,1606),'请在P编号/格号内标出ROI-A与ROI-B的具体折线和编辑边界；青线=历史诊断上下文，黄线=骨轴，紫点=参考顶点。',23)
text(canvas,(22,1640),'所有叠加均为X-ray参考，可能包含遮挡面；不是Human原箭头，也不是已确认的修补范围。上下排各视角采用相同相机、倍率和裁切。',21)
imagepath=OUT/'HUMAN_ROI_LOCALIZATION_REQUIRED.png';assert not imagepath.exists();canvas.save(imagepath)
edge=[629,2018];faceids=[i for i,f in enumerate(F) if any(set([int(f[k]),int(f[(k+1)%4])])==set(edge) for k in range(4))]
save('LOCALIZATION_MAP.json',dict(status='UNCONFIRMED',original_human_red_arrow_available=False,reference_edge=edge,reference_native_faces=faceids,reference_face_vertices={str(i):F[i].tolist() for i in faceids},reference_is_edit_target=False,confirmed_ROI_A=None,confirmed_ROI_B=None,panels=maps,editing_performed=False))
link=lambda n:f'<<HANDS_ROOT>/experiments/hands_local_skin_asset_repair_poc_r1/{n}>'
md('TECHNICAL_REPORT.md',f'''# HANDS_LOCAL_SKIN_ASSET_REPAIR_POC_R1

结果：**INSUFFICIENT_EVIDENCE**。最终状态：**STOP — HUMAN REVIEW**。

阶段1停止：本轮明确要求先核对Human原始红箭头，并规定“如果不能准确对应，输出一张可供Human定位的标注图并停止，不得自行猜测要修的面片”。当前可访问的本会话5个任务回合均为文字请求，没有Human图像内容；已知上一轮及前轮文本附件目录也只有已粘贴的文本。未找到可核对的原始红箭头截图，不能确认截图视角、指向表面或编辑边界。本次没有对整个文件系统或其他会话开展无目标扫描。

已重新读取hands/AGENTS.md。用户本轮授权隔离资产实验，未授予对冻结资产的修改权；同时编辑前的目标确认门槛尚未满足。没有把历史ROI-A背侧拱形或边629—2018自动当成本轮编辑目标。

## 实际执行

- Blender MCP只读确认当前打开的是上一轮`ANATOMICAL_DIAGNOSTIC_WITH_TRUE_SIDE.blend`，帧157=2.600000秒，左右手各3300顶点、3298面。相关corrective当前值0。
- 复用上一轮实际骨轴、原生线框及相机投影数据；本轮仅输出一张定位图，没有新增批量渲染，没有编辑模型或动作。
- 图上上排是原C1，下排是上轮固定几何PASS姿态；后者仍为Human自然性否决状态，不能作为正确解剖模板。
- 每排展示正式正交俯视右手局部、原C1骨平面真侧视、虎口反向。上下排各视角相机、倍率、裁切一致。真侧视是相对原C1定义；候选不分别旋转取得更好看角度。
- P1～P6和A1～F4为定位网格。青色线为宽的历史诊断上下文（含背面遮挡边），不是本轮编辑ROI边界。黄线为实际骨轴投影。紫色v629/v2018只作参考；相邻原生面ID为{faceids}，它们不自动成为待修面片。
- `LOCALIZATION_MAP.json`记录源图、相机、裁切、缩放、参考顶点和面ID，且明确confirmed_ROI_A/B为null。

## 实验与回归状态

| 项目 | 状态 |
|---|---|
| A最小Basis修补 | NOT_RUN；0个版本 |
| B1局部权重 | NOT_RUN；0个版本 |
| B2局部corrective | NOT_RUN；0个版本 |
| 多姿态资产回归 | NOT_RUN；没有修改后资产 |
| 固定PASS姿态全手键碰撞、接触、自交回归 | NOT_RUN；不得复用旧PASS冒充本轮结果 |
| 候选Blend | 无；不制作无修改或未定位资产冒充修补候选 |
| 正式C1/冻结Rig/权重/Basis/corrective/时序/琴键 | 未修改 |

这不是任何方法的实验性失败，也不是已证明资产不可修。当前缺少的是准确编辑目标，而不是隔离实验的授权。

## 六个必答问题

1. 最小Basis能否明显改善？**未验证**，ROI-A尚不能与Human红箭头准确对应。
2. 虎口更适合权重还是corrective？**未验证**，没有B1/B2修改或方法比较结果；不根据旧折面夹角选择方法。
3. 哪种方法能保留其他代表性手型？**未知**，没有实验资产或多姿态回归结果。
4. 是否影响触键、碰撞与原演奏动作？**本轮没有资产修改，未引入修改**；但没有“修改后资产”的安全PASS证据。
5. 两处是否需分别修？**尚未证明**；现有证据不支持合并为同一缺陷。后续按授权使用独立A/B副本做单因素验证。
6. 是否足以批准正式修订？**NO**。本轮不足以支持正式资产修订，也没有可批准候选；已有隔离原型授权无需重复申请，只需先补齐准确目标。

## 证据与保护

唯一新增图片：[定位图]({link('HUMAN_ROI_LOCALIZATION_REQUIRED.png')})。原始Blender渲染和诊断数据仍保留在上一轮目录，没有覆盖。保护输入前后SHA256见`PROTECTED_SHA256_BEFORE_AFTER.json`，包括原C1、冻结原始资产、MIDI/指法/时钟/Action相关历史输入及本次使用的图像/网格数据。独立piano目录未访问。所有新文件都位于本轮目录。
''')
md('HUMAN_REVIEW.md',f'''# STOP — HUMAN REVIEW

**INSUFFICIENT_EVIDENCE。未编辑任何资产，A/B实验与回归均未启动。**

本轮任务第三节要求准确对应Human原始红箭头后才允许编辑；无法对应时必须输出定位图并停止。目前可见会话与已知附件中没有该红箭头原图，不能把历史背侧ROI直接当作食指靠虎口侧目标。

请在这张图上标明两处问题的具体轮廓/面片及边界，或补充原始红箭头图供对应：

[打开唯一定位图]({link('HUMAN_ROI_LOCALIZATION_REQUIRED.png')})

上排原C1，下排上轮固定姿态（Human已否决自然性）。可用“ROI-A在P编号/格号……，沿……轮廓；ROI-B在……”定位。图上历史青色线框不是拟编辑边界，紫色顶点只是参考；请勿将整块线框默认视为需修区域。

需要Human判断的是准确编辑区域，不是重新批准已经授权的隔离实验。本轮没有修补候选、没有通过结论，不需要批准正式资产。核对目标后才能进行独立A/B修补与多姿态回归。

- [技术报告及六个必答问题]({link('TECHNICAL_REPORT.md')})
- [顶点/面与相机定位数据]({link('LOCALIZATION_MAP.json')})
- [保护SHA256前后收据]({link('PROTECTED_SHA256_BEFORE_AFTER.json')})
''')
receipt=[dict(path=k,before=v,after=sha(k),unchanged=sha(k)==v) for k,v in inputs.items()]
assert all(r['unchanged'] for r in receipt)
save('PROTECTED_SHA256_BEFORE_AFTER.json',dict(all_unchanged=True,files=receipt,count=len(receipt),piano_access=False))
with Image.open(imagepath) as im:im.verify()
save('RESULT.json',dict(result='INSUFFICIENT_EVIDENCE',final_state='STOP — HUMAN REVIEW',stop_reason='User section 3 requires matching original Human red-arrow screenshot before editing; original image is not present in accessible evidence.',confirmed_ROI_A=None,confirmed_ROI_B=None,asset_edits=0,pose_edits=0,candidates=[],regression='NOT_RUN',new_images=1,protected_files=len(receipt),all_protected_unchanged=True))
save('DELIVERY_SHA256.json',dict(files=[dict(path=str(p),sha256=sha(p)) for p in OUT.iterdir() if p.is_file() and p.name!='DELIVERY_SHA256.json']))
print(json.dumps(dict(result='INSUFFICIENT_EVIDENCE',images=1,protected=len(receipt),reference_faces=faceids,edits=0),ensure_ascii=False))
