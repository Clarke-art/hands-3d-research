import sys
sys.dont_write_bytecode=True
import geometry as geo
from geometry import *
from PIL import Image,ImageDraw,ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
RE=read(OUT/'REVIEW_COORDINATES_R2.json');RM=read(OUT/'R2_RENDER_MANIFEST.json');M=read(OUT/'SUPPORT_DEPTH_FEASIBILITY_MATRIX_R2.json')
(OUT/'renders').mkdir(exist_ok=True);labels=list(RE['states']);sheets=[]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for pose in ['RSSF_RAW','BIND','IDX_MCP_15','IDX_MCP_30','IDX_MCP_45']:
 for mode in sorted({r['mode'] for r in RM['renders'] if r['pose']==pose}):
  frames=[r for label in labels for r in RM['renders'] if r['label']==label and r['pose']==pose and r['mode']==mode]
  if not frames:continue
  ims=[Image.open(ROOT/r['path']).convert('RGB') for r in frames];w=max(im.width for im in ims);h=max(im.height for im in ims)
  canvas=Image.new('RGB',(w*len(ims),h+52),'#f5f3ee');draw=ImageDraw.Draw(canvas)
  for j,(im,r) in enumerate(zip(ims,frames)):
   canvas.paste(im,(j*w+(w-im.width)//2,52));draw.text((j*w+12,12),r['label'].replace('_',' ')+' | '+pose,font=font,fill='#27333b');im.close()
  name=f'COMPARE_{pose}_{mode}.png';canvas.save(OUT/'renders'/name);sheets.append({'path':'renders/'+name,'mode':mode,'pose':pose,'labels':[r['label'] for r in frames]})
sets,records=nested();dep=M['first_structurally_feasible_support_depth'];pool=sets[min(5,dep+1 if dep else 5)]
domain=face_domain(pool);vertices={i for fi in domain for i in F[fi]};domain|=face_domain({j for i in vertices for j in adj[i]})
geo.R={**R,'faces':sorted(domain)};profiles={};points=[]
for label,poses in RE['states'].items():
 profiles[label]={}
 for pose,coords in poses.items():
  ss=sections(np.array(coords));profiles[label][pose]=ss
  points.extend(pt for sec in ss for seg in sec['segments'] for pt in seg['profile_mm'])
ext=np.array(points);limits=((max(-30.,float(ext[:,0].min())-.5),min(30.,float(ext[:,0].max())+.5)),(float(ext[:,1].min())-.5,float(ext[:,1].max())+.5));colors=['#aa4034','#bd9229','#197e8b','#72599d']
for pose in ['RSSF_RAW','BIND','IDX_MCP_15','IDX_MCP_30','IDX_MCP_45']:
 active=[label for label in labels if pose in profiles[label]]
 if not active:continue
 fig,axes=plt.subplots(1,3,figsize=(13,4),layout='constrained')
 for j,ax in enumerate(axes):
  for label,col in zip(active,colors):ax.add_collection(LineCollection([seg['profile_mm'] for seg in profiles[label][pose][j]['segments']],colors=col,lw=1.5,label=label,alpha=.8))
  ax.set(xlim=limits[0],ylim=limits[1],xlabel='Section distance (mm)',ylabel='Normal height (mm)',title=f'{[0,60,120][j]} degrees');ax.grid(alpha=.15);ax.set_aspect('equal',adjustable='box')
 axes[0].legend(fontsize=8);fig.suptitle(pose+' | expanded native section domain; matched planes');name=f'COMPARE_{pose}_SECTIONS.png';fig.savefig(OUT/'renders'/name,dpi=140);plt.close(fig);sheets.append({'path':'renders/'+name,'mode':'SECTIONS','pose':pose,'labels':active})
dump('R2_ACTUAL_CROSS_SECTIONS.json',{'frame':G['frame'],'native_face_domain':sorted(domain),'profiles':profiles,'not_anatomy_threshold':True})
dump('R2_REVIEW_SHEET_MANIFEST.json',{'sheets':sheets,'temporary_single_frames_directory':TEMP.relative_to(ROOT).as_posix(),'final_sheets_directory':'renders','no_deletions':True})
print('SHEETS',len(sheets))
