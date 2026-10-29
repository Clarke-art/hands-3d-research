"""Minimal static forensic figures from current numeric context; no design UI."""
import sys
sys.dont_write_bytecode=True
from common import *
import math
from PIL import Image,ImageDraw,ImageFont
G=read(OUT/'RUN_A/BOUND_GEOMETRY_CONTEXT.json')
A=read(OUT/'TRUE_CAP_STATIC_PATH_ENSEMBLE_R1.json')
B=read(OUT/'TRUE_CAP_POSED_BOUND_RECOMPUTATION_R1.json')
auth=read(OUT/'CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json')
comparison=read(OUT/'TRUE_CAP_HISTORICAL_VS_CORRECTED_COMPARISON.json')
V0=G['bind_world_m'];edges=G['edges'];faces=G['faces']
src=set(auth['source']['vertex_ids']);tgt=set(auth['target']['vertex_ids'])
c0=set(auth['target']['all_exact_boundary_endpoints']);boundary=auth['target']['exact_boundary_edge_ids']
path=A['global_shortest_path'];oldpath=comparison['historical_shortest_path']
OUT.joinpath('renders').mkdir(exist_ok=True)
def font(size,bold=False):
 file=Path('C:/Windows/Fonts')/('arialbd.ttf' if bold else 'arial.ttf')
 return ImageFont.truetype(str(file),size)
def vec(a,b):return [x-y for x,y in zip(a,b)]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def norm(a):
 l=math.sqrt(dot(a,a));return [x/l for x in a]
def panel(draw,box,coords,direction,focus,show_source=True,show_target=True,show_path=False,show_old=False,endpoint_pair=None):
 x0,y0,x1,y1=box;draw.rectangle(box,fill='#f4f6f8',outline='#cbd2da',width=2)
 n=norm(direction);right=norm(cross([0,0,1],n));up=norm(cross(n,right))
 envelope=V0+sum([G['posed_world_m'][p] for p in ['CMC_MCP_L3','FULL_OPP_L3']],[])
 framecoords=envelope if focus is None else [v for cid in [V0,coords] for i,v in enumerate(cid) if i in focus]
 xy=[(dot(v,right),dot(v,up)) for v in framecoords]
 lo=[min(x[i] for x in xy) for i in [0,1]];hi=[max(x[i] for x in xy) for i in [0,1]]
 cx,cy=(hi[0]+lo[0])/2,(hi[1]+lo[1])/2
 scale=min((x1-x0-90)/max(hi[0]-lo[0],1e-7),(y1-y0-90)/max(hi[1]-lo[1],1e-7))
 def project(v):return ((x0+x1)/2+(dot(v,right)-cx)*scale,(y0+y1)/2-(dot(v,up)-cy)*scale)
 P=[project(v) for v in coords]
 for a,b in edges:
  if focus is None or a in focus or b in focus:draw.line([P[a],P[b]],fill='#b9c2cb',width=1)
 if show_source:
  for face in auth['source']['face_ids']:
   draw.polygon([P[v] for v in faces[face]],fill='#ffd56b',outline='#dfab2c')
  for v in sorted(src):
   x,y=P[v];draw.ellipse((x-3,y-3,x+3,y+3),fill='#a57b08')
 if show_target:
  for eid in boundary:draw.line([P[v] for v in edges[eid]],fill='#22aaa3',width=3)
  for v in sorted(tgt):
   x,y=P[v];draw.ellipse((x-4,y-4,x+4,y+4),fill='#167cc2')
 if show_path:
  draw.line([P[v] for v in path['vertex_sequence']],fill='#813bd1',width=5)
 if show_old:
  draw.line([P[v] for v in oldpath['vertex_sequence']],fill='#e65b59',width=5)
 if endpoint_pair:
  selected=next(p for p in A['paths'] if [p['source_vertex'],p['target_vertex']]==endpoint_pair)
  draw.line([P[v] for v in selected['vertex_sequence']],fill='#d26b22',width=4)
 pair=endpoint_pair or ([path['source_vertex'],path['target_vertex']] if show_path else [])
 for i,v in enumerate(pair):
  x,y=P[v];color='#aa7410' if i==0 else '#076fbd'
  draw.ellipse((x-7,y-7,x+7,y+7),fill=color,outline='white',width=2)
  label='A v'+str(v) if i==0 else 'B v'+str(v)
  draw.rectangle((x+10,y-26,x+115,y-2),fill='white')
  draw.text((x+14,y-24),label,font=font(17,True),fill=color)
def figure(name,title,subtitle,coords,kind,endpoint_pair=None):
 im=Image.new('RGB',(1800,1050),'white');d=ImageDraw.Draw(im)
 d.text((36,24),title,font=font(30,True),fill='#202a36')
 d.text((36,73),subtitle,font=font(19),fill='#506071')
 focus=src|c0|set(path['vertex_sequence'])
 if kind=='old':focus |=set(oldpath['vertex_sequence'])
 # Fixed pair context uses complete current path for the maximizing endpoint pair.
 if endpoint_pair:
  row=next(p for p in A['paths'] if [p['source_vertex'],p['target_vertex']]==endpoint_pair)
  focus |=set(row['vertex_sequence'])
 for box,direction in [((35,120,882,902),(0,-1,.6)),((918,120,1765,902),(-.65,-.5,.7))]:
  panel(d,box,coords,direction,focus if kind!='cap' else None,
   show_source=kind!='target',show_target=kind!='cap',show_path=kind in ['path','old','posed'],show_old=kind=='old',endpoint_pair=endpoint_pair)
 d.text((36,926),'Yellow = frozen cap37 | Blue = INDEX-side exact targets | Teal = fresh20 boundary',font=font(20),fill='#243647')
 legend='Purple = global shortest bind path | Orange = maximizing bound pair fixed-path context' if kind=='posed' else 'Purple = corrected global shortest bind path | Red = historical path, comparison only'
 d.text((36,958),legend,font=font(20),fill='#243647')
 d.text((36,997),'Forensic geometry context only. No anatomy review, weight assignment or deformation qualification.',font=font(18),fill='#647283')
 p=OUT/'renders'/name;im.save(p);return p
files=[]
files.append(figure('BIND_FROZEN_CAP37.png','Bind-space canonical cap37: 37 vertices / 25 faces','Only frozen cap37 is the source authority; no legacy cap selector or REP.',V0,'cap'))
files.append(figure('BIND_CURRENT_EXACT_TARGET_COLLAR.png','Current exact target: 19 INDEX endpoints from frozen fresh20 boundary','38 boundary endpoints; collar/transition neighborhoods and proximal stop are separate roles.',V0,'target'))
files.append(figure('BIND_GLOBAL_SHORTEST_PATH.png','Corrected global shortest path: v1380 to v2035','24 native mesh edges | bind path length = %.9f mm'%path['total_path_length_mm'],V0,'path'))
files.append(figure('BIND_HISTORICAL_VS_CORRECTED_PATH.png','Historical vs corrected shortest pair on unchanged geometry','Red: old v2192-v704, INVALIDATED true-cap interpretation | Purple: current v1380-v2035.',V0,'old'))
for pose in ['CMC_MCP_L3','FULL_OPP_L3']:
 worst=B['per_pose'][pose]['max_over_complete_703_pairs']
 files.append(figure(pose+'_BOUND_ENDPOINT_PATH_CONTEXT.png',pose+': actual corrected R2 endpoint/path context','Maximum full703 bound = %.9f | A v%d / B v%d | purple is retained global shortest bind path'%(worst['strict_lower_bound'],worst['source_vertex'],worst['target_vertex']),G['posed_world_m'][pose],'posed',[worst['source_vertex'],worst['target_vertex']]))
sheet=Image.new('RGB',(1500,882),'#dfe4ea')
for i,p in enumerate(files):
 with Image.open(p) as im:
  im.thumbnail((500,294));sheet.paste(im,((i%3)*500,(i//3)*441))
 # add a readable filename below each miniature
 d=ImageDraw.Draw(sheet);d.text(((i%3)*500+12,(i//3)*441+310),p.name,font=font(16),fill='#243647')
sheet.save(OUT/'renders/FORENSIC_CONTACT_SHEET.png')
dump('FORENSIC_RENDER_MANIFEST.json',{'purpose':'Minimal endpoint sanity evidence; not Human anatomy review, new design UI or qualification.','render_count':len(files),'renders':[{**ref(p),'image_size':[1800,1050]} for p in files],'contact_sheet':ref(OUT/'renders/FORENSIC_CONTACT_SHEET.png'),'pose_positions':'Actual read-only R2 evaluation from RUN_A','shared_framing':'Pose-context panels retain common bind/opposition envelope for selected frozen endpoints/path vertices.'})
print('Six minimal forensic figures + contact sheet created.')
