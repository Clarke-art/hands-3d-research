from common import *
import numpy as np
from PIL import Image,ImageDraw,ImageFont
top=read(OUT/'NATIVE_TOPOLOGY.json');F=np.array(top['faces']);E=np.array(top['edges']);rows=read(OUT/'DIAGNOSTIC_RENDER_MANIFEST.json')+read(OUT/'EXACT_TRUE_SIDE_MANIFEST.json')
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
def put(im,p,t,n=25,fill='#f4f6fa'):
 ImageDraw.Draw(im).text(p,t,font=font(n),fill=fill,stroke_width=0)
def writeimg(name,im):
 dest=OUT/name;assert not dest.exists();im.convert('RGB').save(dest)
def find(ident,var,view):return next(r for r in rows if r['identity']==ident and r['variant']==var and r['view']==view)
def overlay(row,roi,wire=True,normals=False):
 im=Image.open(row['path']).convert('RGBA');lay=Image.new('RGBA',im.size);d=ImageDraw.Draw(lay);meta=read(OUT/(row['identity']+'_SNAPSHOT.json'));ids=set(meta['rois'][roi]['vertices']);pix=np.array(row['all_vertex_pixels'])
 if wire:
  for a,b in E:
   if a in ids and b in ids:d.line([tuple(pix[a]),tuple(pix[b])],fill=(35,100,130,150),width=1)
 if normals and 'face_centroid_pixels' in row:
  cen=row['face_centroid_pixels'];end=row['face_normal_end_pixels']
  for i,face in enumerate(F):
   if i%2==0 and all(v in ids for v in face):d.line([tuple(cen[i]),tuple(end[i])],fill=(0,190,210,210),width=2)
 for b in ['INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R']:
  P=row['bones'][b]['pixels'];color={'INDEX_MCP_R':'#f9ba18','INDEX_PIP_R':'#f47b29','INDEX_DIP_R':'#f04671'}[b];d.line([tuple(P[0]),tuple(P[1])],fill=color,width=5)
  x,y=P[0];d.ellipse([x-7,y-7,x+7,y+7],outline='black',fill=color,width=2)
  if 0<x<1220 and 0<y<680:d.text((x+10,y+10),b.replace('INDEX_','').replace('_R',''),font=font(23),fill=color,stroke_width=2,stroke_fill='black')
 if roi=='B':
  for v in [629,2018,2057,628,2017]:
   x,y=pix[v];d.ellipse([x-5,y-5,x+5,y+5],fill='#d400ff');d.text((x+8,y-20),'v'+str(v),font=font(19),fill='#d400ff',stroke_width=1,stroke_fill='black')
  d.line([tuple(pix[629]),tuple(pix[2018])],fill='#d400ff',width=5)
 return Image.alpha_composite(im,lay).convert('RGB')
def pair(name,a,b,title,subtitle,left='A 原C1',right='B 上轮候选 / Human已否决'):
 canvas=Image.new('RGB',(2560,886),'#17202c');canvas.paste(a,(0,100));canvas.paste(b,(1280,100));put(canvas,(24,12),title,30);put(canvas,(24,58),left,25);put(canvas,(1304,58),right,25);put(canvas,(24,828),subtitle,22);writeimg(name,canvas)
for view,label in [('OVERHEAD','正式正交俯视'),('EXACT_SOURCE_TRUE_SIDE','食指真侧视'),('WEB_CLOSE','虎口近景'),('PALM_OBLIQUE','掌部斜透视'),('WEB_REVERSE','虎口反向')]:
 a=find('ORIGINAL','NATIVE',view);b=find('REJECTED_GEOMETRY_PASS','NATIVE',view)
 assert np.allclose(a['camera_matrix'],b['camera_matrix']) and a['camera_type']==b['camera_type'] and a['ortho_scale']==b['ortho_scale']
 pair('HUMAN_NATURALITY_COMPARISON__'+view+'.png',Image.open(a['path']),Image.open(b['path']),label+' | t=2.600000s | 同机位、同投影、同倍率、完整渲染', 'C 本轮候选：未生成；诊断门槛未满足。所有诊断隔离状态均不属于修复候选。')
for roi,view in [('A','EXACT_SOURCE_TRUE_SIDE'),('B','WEB_CLOSE'),('B','WEB_REVERSE')]:
 a=find('ORIGINAL','NATIVE',view);b=find('REJECTED_GEOMETRY_PASS','NATIVE',view)
 pair(f'ANATOMICAL_ROI_DIAGNOSTIC__{roi}__{view}.png',overlay(a,roi,normals=roi=='A'),overlay(b,roi,normals=roi=='A'),f'ROI-{roi} 实际皮肤 + 实际骨轴投影 + 原生网格边', '线框及骨轴为透视叠加（含被皮肤遮挡部分）；青色短线为实际面法线。骨轴线内没有额外关节。')
for ident in ['ORIGINAL','REJECTED_GEOMETRY_PASS']:
 a=find(ident,'NATIVE','EXACT_SOURCE_TRUE_SIDE');b=find(ident,'MCP_RIGID_A_DIAG_ONLY','EXACT_SOURCE_TRUE_SIDE')
 pair(f'ANATOMICAL_ROI_DIAGNOSTIC__{ident}__A_FACTOR_ISOLATION.png',overlay(a,'A'),overlay(b,'A'),ident+' | 近节原始形状与实际变形的因素隔离','右侧仅为Basis随MCP刚体变换；不是合法演奏候选，其他手指位置不应作解剖/碰撞评价。',left='实际 LBS / corrective 皮肤',right='诊断：Basis + 单一MCP刚体，未修改权重')
 a=find(ident,'NATIVE','WEB_CLOSE');b=find(ident,'RAW_WRIST_ALIGNED_DIAG_ONLY','WEB_CLOSE')
 pair(f'ANATOMICAL_ROI_DIAGNOSTIC__{ident}__B_FACTOR_ISOLATION.png',overlay(a,'B'),overlay(b,'B'),ident+' | 虎口因素隔离','右侧仅为Basis随腕部刚体变换；不是修复。紫色为实际顶点ID和观测边629—2018。',left='实际 LBS / corrective 皮肤',right='诊断：Basis + 腕部刚体，所有原Action不作替换')
 for group in ['WRIST_R','INDEX_MCP_R','THUMB_CMC_R']:
  files=[OUT/f'{ident}__WEIGHT_{group}__{v}.png' for v in ['INDEX_TRUE_SIDE','WEB_CLOSE']]
  pair(f'ANATOMICAL_ROI_DIAGNOSTIC__{ident}__WEIGHTS_{group}.png',Image.open(files[0]),Image.open(files[1]),ident+' | 实际冻结权重：'+group,'蓝=0，红=1；仅诊断色图。未修改任何顶点权重。左侧为初始近似侧视，最终真侧视另见EXACT_SOURCE_TRUE_SIDE。',left='食指侧向',right='虎口近景')
# The one targeted additional read-only check: narrow first web surface,
# excluding most distal thumb; no pose sweep, no altered weights.
ef={}
for i,f in enumerate(F):
 for a,b in zip(f,np.roll(f,-1)):ef.setdefault(tuple(sorted((int(a),int(b)))),[]).append(i)
def normals(V):
 P=V[F];N=np.cross(P[:,1]-P[:,0],P[:,2]-P[:,0])+np.cross(P[:,2]-P[:,0],P[:,3]-P[:,0]);return N/np.maximum(np.linalg.norm(N,axis=1)[:,None],1e-15)
targetcheck={};ns={'np':np};extract(OUT/'analyze_rois.py',{'sections'},ns)
for ident in ['ORIGINAL','REJECTED_GEOMETRY_PASS']:
 m=read(OUT/(ident+'_SNAPSHOT.json'));z=np.load(OUT/(ident+'_SNAPSHOT.npz'));a=np.load(OUT/(ident+'_ALIGNED.npz'));C=z['C'];CW=a['C_WRIST'];W=z['W'];names=m['bone_names'];td=W[:,names.index('THUMB_MCP_R')]+W[:,names.index('THUMB_IP_R')]
 core=np.flatnonzero((C[:,0]>-.052)&(C[:,0]<-.024)&(C[:,1]>.068)&(C[:,1]<.115)&(td<.25));cs=set(core);N0=normals(C);N1=normals(CW);angles=[]
 for e,fs in ef.items():
  if len(fs)!=2 or not all(v in cs for v in e):continue
  u,v=fs;x=float(np.degrees(np.arccos(np.clip(N0[u]@N0[v],-1,1))));y=float(np.degrees(np.arccos(np.clip(N1[u]@N1[v],-1,1))));angles.append(dict(edge=e,faces=fs,raw_dihedral_deg=x,posed_dihedral_deg=y,increase_deg=y-x))
 witnesses=[]
 for v in [2057,628,2017,627,629,2018,429,1588]:
  contrib={}
  for k,n in enumerate(names):
   if W[v,k]<.001:continue
   wr=z['D'][names.index('WRIST_R')];P=np.r_[z['RV'][v],1];dv=W[v,k]*(z['D'][k]@P-wr@P)[:3];contrib[n]=dict(weight=float(W[v,k]),world_displacement_mm=dv*1000)
  witnesses.append(dict(vertex=v,raw_canonical_m=C[v],wrist_aligned_evaluated_m=CW[v],difference_mm=(CW[v]-C[v])*1000,weighted_contributions_vs_rigid_wrist=contrib))
 targetcheck[ident]=dict(roi_definition='canonical -52<x<-24mm, 68<y<115mm; THUMB_MCP+THUMB_IP weight<0.25; geometric context, not an anatomical segmentation',core_vertices=core,angles=angles,witnesses=witnesses,mean_weights={n:float(W[core,k].mean()) for k,n in enumerate(names) if W[core,k].max()>.02},sections=[dict(y_mm=y*1000,raw=ns['sections'](C,z['T'],y),posed=ns['sections'](CW,z['T'],y)) for y in [.078,.085,.095]],max_displacement_mm=float(np.linalg.norm(CW[core]-C[core],axis=1).max()*1000))
save('TARGETED_READONLY_WEB_CHECK.json',dict(check_count=1,pose_edits=0,states=targetcheck))
# Reproducible plots, not generated or retouched anatomy.
os.environ['MPLCONFIGDIR']=str(OUT/'matplotlib_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'Microsoft YaHei','font.size':11})
analysis=read(OUT/'ROI_GEOMETRY_AND_WEIGHT_ANALYSIS.json');fig,axes=plt.subplots(2,2,figsize=(14,9));color={'ORIGINAL':'#df7441','REJECTED_GEOMETRY_PASS':'#297bc1'}
for ident in color:
 st=analysis[ident]['stations'];x=np.array([r['fraction'] for r in st]);dors=[r['posed']['max_m'][2]*1000 for r in st];area=[r['posed']['area_mm2'] for r in st];axes[0,0].plot(x,dors,'o-',c=color[ident],label=ident);axes[0,1].plot(x,area,'o-',c=color[ident],label=ident)
st=analysis['ORIGINAL']['stations'];axes[0,0].plot(x,[r['raw']['max_m'][2]*1000 for r in st],'k--',label='Basis / 原始形状');axes[0,1].plot(x,[r['raw']['area_mm2'] for r in st],'k--',label='Basis')
axes[0,0].set(title='近节截面背侧极值：MCP局部系',ylabel='局部 z (mm)',xlabel='MCP→PIP 长度比例');axes[0,1].set(title='闭合截面积（实际三角面截线）',ylabel='mm²',xlabel='MCP→PIP 长度比例')
for name in ['WRIST_R','INDEX_MCP_R','INDEX_PIP_R']:
 axes[1,0].plot(x,[r['mean_weights'].get(name,0) for r in st],'o-',label=name)
axes[1,0].set(title='近节局部采样带实际平均权重',ylabel='权重',xlabel='MCP→PIP 长度比例',ylim=(0,1))
for ident in color:
 sec=analysis[ident]['stations'][4]['posed'];P=np.array(sec['points_m']);P=np.r_[P,P[:1]];axes[1,1].plot(P[:,0]*1000,P[:,2]*1000,c=color[ident],label=ident)
sec=st[4]['raw'];P=np.array(sec['points_m']);P=np.r_[P,P[:1]];axes[1,1].plot(P[:,0]*1000,P[:,2]*1000,'k--',label='Basis');axes[1,1].set(title='MCP→PIP 50%截面；同一局部系',xlabel='局部 x (mm)',ylabel='局部 z (mm)');axes[1,1].axis('equal')
for ax in axes.ravel():ax.grid(alpha=.2);ax.legend(fontsize=8)
fig.suptitle('ROI-A 几何与权重证据 | 描述值不是人体自然性标准；不设毫米级合格阈值');fig.tight_layout();dest=OUT/'ANATOMICAL_ROI_DIAGNOSTIC__A_SECTIONS_WEIGHTS.png';assert not dest.exists();fig.savefig(dest,dpi=140);plt.close(fig)
fig,axes=plt.subplots(1,3,figsize=(15,6))
for k,y in enumerate([78,85,95]):
 ax=axes[k]
 for ident in color:
  sec=targetcheck[ident]['sections'][k]['posed']
  for seg in sec['segments_m']:
   P=np.array(seg)*1000;ax.plot(P[:,0],P[:,2],c=color[ident],linewidth=1.2)
 for seg in targetcheck['ORIGINAL']['sections'][k]['raw']['segments_m']:
  P=np.array(seg)*1000;ax.plot(P[:,0],P[:,2],'k--',linewidth=.9)
 ax.set(title=f'腕部对齐：canonical y={y}mm',xlim=(-58,-15),ylim=(-35,15),xlabel='canonical x (mm)',ylabel='canonical z (mm)');ax.set_aspect('equal');ax.grid(alpha=.2)
fig.suptitle('ROI-B 实际网格切线 | 黑虚线Basis，橙C1，蓝Human否决候选 | 非独立软组织体积测量');fig.tight_layout();dest=OUT/'ANATOMICAL_ROI_DIAGNOSTIC__B_SECTIONS.png';assert not dest.exists();fig.savefig(dest,dpi=150);plt.close(fig)
protection('PACKAGING_INPUT_RECEIPT.json');print('EVIDENCE_PACKAGED',flush=True)
