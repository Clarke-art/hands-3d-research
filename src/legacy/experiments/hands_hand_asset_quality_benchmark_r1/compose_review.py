from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
OUT=Path(__file__).resolve().parent
fontpath=r'C:\Windows\Fonts\msyh.ttc'
def font(n):return ImageFont.truetype(fontpath,n)
cols=['C1 · 正式冻结右手基线','Innerscene / MakeHuman · CC0 候选']
projections={(r['identity'],r['view']):r['points_pixels'] for r in json.loads((OUT/'JOINT_PROJECTION_RECEIPT.json').read_text())}
def compose(name,title,rows,foot):
 W=1660;pad=20;tilew=800;h=155+sum(55+round(Image.open(OUT/'renders'/('C1__'+v+'.png')).height*800/Image.open(OUT/'renders'/('C1__'+v+'.png')).width) for v,t in rows)+110
 im=Image.new('RGB',(W,h),(17,25,39));d=ImageDraw.Draw(im)
 d.text((20,15),title,font=font(31),fill='white')
 d.text((20,60),'同组相同相机、物理尺度、灯光和无纹理中性材质；候选作展示镜像，未修改下载源文件。',font=font(21),fill=(190,208,230))
 for i,c in enumerate(cols):d.text((pad+i*(tilew+20),105),c,font=font(25),fill=(118,219,230) if i else (238,213,151))
 y=155
 for v,t in rows:
  d.text((20,y+9),t,font=font(23),fill=(230,235,244));y+=55
  for i,ident in enumerate(['C1','MAKEHUMAN']):
   tile=Image.open(OUT/'renders'/(ident+'__'+v+'.png')).convert('RGB')
   if v.startswith('INDEX_'):
    td=ImageDraw.Draw(tile);pts=projections[ident,v]
    td.line([tuple(pts['MCP']),tuple(pts['PIP'])],fill=(250,210,90),width=2)
    for lab,(px,py) in pts.items():
     td.ellipse((px-5,py-5,px+5,py+5),fill=(250,210,90),outline=(20,20,20),width=1)
     td.text((px+9,py-20),lab,font=font(19),fill=(255,225,130),stroke_width=2,stroke_fill=(25,30,40))
   # Same exact scale factor for both members, no adaptive fit/crop.
   if tile.width!=tilew:tile=tile.resize((tilew,round(tile.height*tilew/tile.width)),Image.Resampling.LANCZOS)
   im.paste(tile,(pad+i*(tilew+20),y))
  y+=tile.height
 for i,s in enumerate(foot):d.text((20,y+18+i*29),s,font=font(20),fill=(202,215,230))
 im.save(OUT/name)
compose('HAND_ASSET_OVERALL_COMPARISON.png','整手正交俯视 · 真实网格对标',[
 ('OVERALL_FLAT','1  中性绑定姿态 / Flat：完整手部和腕端；两者食指近节骨长统一为 32.293 mm。'),
 ('OVERALL_SMOOTH','2  同一网格 / 双方统一 Smooth：仅检视着色，几何与第 1 行完全相同。')],
 ['腕端截取长度不同，禁止用腕长评价手掌比例。统一 Smooth 不构成质量通过证据。','候选发布名为右手，但源文件含反射变换；本图先统一掌背方向，仅作视觉对标。'])
compose('INDEX_PROXIMAL_COMPARISON.png','食指 MCP–PIP · 虎口侧轮廓',[
 ('INDEX_OVERHEAD','1  中性姿态正交俯视 / Flat：重点看食指靠拇指一侧的连续轮廓。'),
 ('INDEX_SIDE','2  同一中性姿态 / 径侧正交观察：看骨段厚度、弧度和指根转折。')],
 ['金色点/线为真实骨骼 MCP–PIP 中心轴投影，用于辨认骨段，不是编辑范围。','全部皮肤保留，无几何平滑或纹理修饰；两模型绑定姿态仍有差异。'])
compose('FIRST_WEB_COMPARISON.png','第一指蹼与指根 · 多角度真实皮肤',[
 ('WEB_DORSAL_OBLIQUE','1  中性姿态 / 手背近侧：虎口凹面、食指根部和掌部连接。'),
 ('WEB_PALMAR_REVERSE','2  同一中性姿态 / 掌侧反向：查看相反表面的厚度和三角折面。'),
 ('WEB_SPREAD','3  拇指根展开 / 名义目标 15°：观察指蹼随动；原生变换不同，实际角度见报告。')],
 ['核心判断来自 Flat 几何；不因三角形更多或指甲更细就判定自然性更好。','本轮没有修改、绑定或迁移任何皮肤、权重和动作。'])
compose('POSE_DEFORMATION_COMPARISON.png','三种静态姿态 · 现有 Rig 实测',[
 ('POSE_NEUTRAL','1  两者原生绑定中性姿态 / 同一斜向相机，Flat。'),
 ('POSE_INDEX_FLEX','2  食指屈曲名义目标 20° / 35° / 15°；原生变换不同，实际角度见报告。'),
 ('POSE_THUMB_SPREAD','3  拇指根展开名义目标 15°；未验证 CMC 生理活动范围，不是动作迁移。')],
 ['实际静态变形已执行；原生骨轴与绑定姿态不同，未严格匹配最终关节位置。','自动演奏、接触 marker、键碰撞、corrective 多姿态、连续动画兼容性：NOT_TESTED。'])
print('FOUR_REVIEW_PANELS_READY')
