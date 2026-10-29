import sys
sys.dont_write_bytecode=True
from reference_features import *
from PIL import Image,ImageDraw,ImageFont
re=read(OUT/'REVIEW_COORDINATES_R3.json');rm=read(OUT/'R3_RENDER_MANIFEST.json');font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);big=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25);renders=OUT/'renders';renders.mkdir(exist_ok=True);sheets=[]
sets,records=nested()
def sheet(name,frames,placeholder=False):
 ims=[Image.open(ROOT/r['path']).convert('RGB') for r in frames];w=max(im.width for im in ims);h=max(im.height for im in ims);cols=len(ims)+(2 if placeholder else 0);canvas=Image.new('RGB',(w*cols,h+72),'#f5f3ee');draw=ImageDraw.Draw(canvas)
 for j,(im,r) in enumerate(zip(ims,frames)):
  canvas.paste(im,(j*w+(w-im.width)//2,72));draw.text((j*w+12,12),r['label'].replace('_',' '),font=font,fill='#253840');draw.text((j*w+12,39),'DESIGN ONLY | '+r['mode'],font=font,fill='#63727a');im.close()
 if placeholder:
  for j,label in [(len(ims),'R3-A'),(len(ims)+1,'R3-B')]:
   draw.rectangle((j*w+12,90,(j+1)*w-12,h+55),fill='#e9e5df');draw.text((j*w+30,130),label,font=big,fill='#404d51');draw.text((j*w+30,175),'NO QUALIFIED CANDIDATE',font=font,fill='#884d3a');draw.text((j*w+30,215),'Not selectable. No application.',font=font,fill='#606b70')
 canvas.save(renders/name);sheets.append({'path':'renders/'+name,'labels':[r['label'] for r in frames],'placeholder_columns':placeholder})
main=['CURRENT','R1C_FAILED_REFERENCE','R2S5_FAILED_REFERENCE'];failed=['R3_A_FAILED_S5_WITNESS','R3_B_FAILED_S5_WITNESS'];refs=['REFERENCE_1','REFERENCE_2']
for mode in ['HUMAN_CAMERA','DORSAL_WHOLE','CLOSE','GRAZING','FLAT','WIRE','SILHOUETTE','ANGLE_2','SIDE_2','BOUNDARY_6675','BOUNDARY_6602']:
 frames=[r for lab in main for r in rm['renders'] if r['label']==lab and r['mode']==mode and r['pose']=='RSSF_RAW'];sheet('COMPARE_'+mode+'.png',frames,mode=='HUMAN_CAMERA')
for mode in ['CLOSE','GRAZING','WIRE','SILHOUETTE','ANGLE_2','SIDE_2']:
 frames=[r for lab in ['CURRENT']+refs for r in rm['renders'] if r['label']==lab and r['mode']==mode and r['pose']=='RSSF_RAW'];sheet('HEALTHY_REFERENCE_'+mode+'.png',frames)
 frames=[r for lab in ['CURRENT']+failed for r in rm['renders'] if r['label']==lab and r['mode']==mode and r['pose']=='RSSF_RAW'];sheet('FAILED_SOLVE_'+mode+'.png',frames)
domain=sorted(face_domain(sets[5]));profiles={lab:native_sections(np.array(re['states'][lab]['RSSF_RAW']),domain,origin,B) for lab in main+failed};dump('R3_ACTUAL_CROSS_SECTIONS.json',{'native_face_domain':domain,'frame':G['frame'],'states':profiles,'angles_deg':[0,60,120],'not_anatomy_threshold':True})
for subset,title,name in [(main,'CURRENT / historical failed references','COMPARE_SECTIONS.png'),(['CURRENT']+failed,'Current / R3 S5 failed solve witnesses (not candidates)','FAILED_SOLVE_SECTIONS.png')]:
 fig,axes=plt.subplots(1,3,figsize=(13,4),layout='constrained')
 for j,ax in enumerate(axes):
  for lab,col in zip(subset,['#944634','#b99b27','#236e82']):ax.add_collection(LineCollection([s['profile_mm'] for s in profiles[lab][j]['segments']],colors=col,lw=1.4,label=lab))
  ax.set(xlim=(-14,14),ylim=(-5,7),title=f'{[0,60,120][j]} degrees',xlabel='Section distance (mm)',ylabel='Dorsal normal height (mm)');ax.grid(alpha=.15);ax.set_aspect('equal')
 axes[0].legend(fontsize=6);fig.suptitle(title+' | matched native sections');fig.savefig(renders/name,dpi=150);plt.close(fig);sheets.append({'path':'renders/'+name,'labels':subset})
fig=plt.figure(figsize=(12,4.5),layout='constrained')
for j,lab in enumerate(['CURRENT']+failed):
 ax=fig.add_subplot(1,3,j+1,projection='3d');q=(np.array(re['states'][lab]['RSSF_RAW'])-origin)@B
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 for fi,col in [(2182,'#2f8498'),(3330,'#bb5144')]:
  ax.add_collection3d(Poly3DCollection([q[F[fi]]],facecolor=col,edgecolor=col,alpha=.45))
  for i in F[fi]:ax.text(*q[i],str(i),fontsize=7)
 ax.set(xlim=(-5,2),ylim=(-5,2),zlim=(-2,2),title=lab);ax.set_box_aspect((7,7,4));ax.view_init(elev=22,azim=-40)
fig.suptitle('2182/3330: legal shared edge79/955; off-edge contacts are forbidden');fig.savefig(renders/'ADJACENT_CONTACT_FORENSIC.png',dpi=150);plt.close(fig)
dump('R3_REVIEW_SHEET_MANIFEST.json',{'sheets':sheets,'first_screen':'Original Human camera plain solid, CURRENT/R1-C/R2-S5 plus explicit unavailable R3 placeholders.','failed_witnesses_not_selectable':failed,'temporary_single_frames':TEMP.relative_to(ROOT).as_posix(),'final_evidence_directory':'renders','no_deletions':True})
print('REVIEW SHEETS',len(sheets))
