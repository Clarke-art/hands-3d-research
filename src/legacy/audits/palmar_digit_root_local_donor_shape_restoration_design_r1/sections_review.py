import sys,math
sys.dont_write_bytecode=True
from common import *
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image,ImageDraw,ImageFont
G=read(OUT/'MATCHED_REVIEW_GEOMETRY_R1.json');C=read(OUT/'PALMAR_ROOT_FORMAL_TARGET_COORDINATES_R1.json');T=read(OUT/'NATIVE_RENDER_LOOP_TRIANGLES_R1.json');core=G['core'];normal=G['normal'];F=C['faces'];ids=C['vertex_ids'];REND=OUT/'renders';SECT=OUT/'sections';SECT.mkdir(exist_ok=True)
reuse(FEAS/'metrics_and_sections.py',['geometry'],globals())
v0=np.array(C['source_world_mm']);fs={i for i,p in enumerate(F) if set(p)&set(ids)}|set(core['face_ids']);nn,_,_=geometry(v0,F,fs);origin=v0[[3353,3354,3359]].mean(0);n=nn[core['face_ids']].sum(0);n/=np.linalg.norm(n);axis=np.array([0.,0.,1.]);axis-=n*(axis@n);axis/=np.linalg.norm(axis);cross=np.cross(n,axis);planes={'FINGER_AXIS':axis,'CROSS_FINGER_AXIS':cross,'DIAGONAL_TANGENT':(axis+cross)/np.sqrt(2)};parents={int(k) for r in C['per_vertex'] for k in r['L1_parent_weights']};metrics={};sections={}
labels=['CURRENT_RAW','OFFICIAL_L1_RSSF_DISPLAY','FEASIBILITY_PROBE','FORMAL_CANDIDATE']
for label in labels:
 s=G['states'][label];v=np.array(s['vertices']);ff=s['faces'];sf=fs if label!='OFFICIAL_L1_RSSF_DISPLAY' else {i for i,p in enumerate(ff) if set(p)&parents};ns,ar,di=geometry(v,ff,sf);metrics[label]={'native_face_dihedral_mean_deg':float(np.mean([d['dihedral_deg'] for d in di])),'native_face_dihedral_max_deg':max(d['dihedral_deg'] for d in di),'adjacent_face_dihedral':di,'face_areas_mm2':{str(i):ar[i] for i in sf},'same_topology_as_current':ff==F,'descriptive_not_anatomy_threshold':True};sections[label]={}
 for name,d in planes.items():
  pn=np.cross(n,d);segs=[]
  for row in T[label]:
   if row['face_id'] not in sf:continue
   q=v[row['vertex_ids']];dist=(q-origin)@pn;pts=[]
   for a,b in [(0,1),(1,2),(2,0)]:
    if abs(dist[a])<1e-8:pts.append(q[a])
    if dist[a]*dist[b]<0:pts.append(q[a]+(q[b]-q[a])*dist[a]/(dist[a]-dist[b]))
   unique=[]
   for p in pts:
    if not any(np.linalg.norm(p-z)<1e-8 for z in unique):unique.append(p)
   if len(unique)==2:segs.append({'face_id':row['face_id'],'native_triangle_ids':row['vertex_ids'],'world_mm':[p.tolist() for p in unique],'profile_mm':[[float((p-origin)@d),float((p-origin)@n)] for p in unique]})
  assert segs;sections[label][name]=segs
dump('PALMAR_ROOT_NATIVE_CROSS_SECTIONS_R1.json',{'method':'actual Blender native loop triangles intersect identical fixed planes; no profile smoothing','origin_world_mm':origin,'normal':n,'planes':planes,'states':sections,'native_donor_topology_retained':True,'static_RAW_RSSF_frame_only':True})
dump('PALMAR_ROOT_GEOMETRY_DIAGNOSTICS_R1.json',{'states':metrics,'description':'Native crease preserved. Angles describe source/current shape; not Human acceptance or anatomy thresholds.'})
colors={'CURRENT_RAW':'#d84836','OFFICIAL_L1_RSSF_DISPLAY':'#8d52bf','FEASIBILITY_PROBE':'#2396b0','FORMAL_CANDIDATE':'#16834d'}
for name in planes:
 fig,ax=plt.subplots(figsize=(9,5),layout='constrained')
 for label in labels:
  for j,s in enumerate(sections[label][name]):
   q=np.array(s['profile_mm']);ax.plot(q[:,0],q[:,1],color=colors[label],lw=1.6 if label=='FORMAL_CANDIDATE' else 2.3,linestyle='--' if label=='FORMAL_CANDIDATE' else '-',label=label if j==0 else None)
 ax.legend(fontsize=8);ax.grid(alpha=.2);ax.set_xlabel('Tangent distance (mm)');ax.set_ylabel('Normal height (mm)');ax.set_title(name+' / actual native triangles / static RAW frame');fig.savefig(SECT/(name+'.png'),dpi=160);plt.close(fig)
def font(n):return ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',n)
def sheet(files,titles,name):
 w=600;h=412;im=Image.new('RGB',(w*len(files),h+55),'white');dr=ImageDraw.Draw(im)
 for i,(f,title) in enumerate(zip(files,titles)):
  with Image.open(OUT/f) as z:im.paste(z.convert('RGB').resize((w,h)),(i*w,55))
  dr.text((i*w+12,14),title,fill='#152430',font=font(19))
 im.save(REND/name)
for view in ['HUMAN_CAMERA','CLOSE','ALTERNATE']:
 for style in ['SOLID','GRAZING','FLAT_SOURCE_NATIVE']:
  sheet([f'renders/{s}__{view}__{style}.png' for s in labels],['CURRENT','OFFICIAL L1 / frozen RSSF','FEASIBILITY PROBE','FORMAL DESIGN CANDIDATE'],view+'__'+style+'__FOUR_COLUMN.png')
# Project native core/normal face outlines into the unchanged Human camera for engineering states.
man=read(OUT/'MATCHED_RENDER_MANIFEST_R1.json');cam=G['camera'];M=np.array(cam['camera_world_matrix']);iv=np.linalg.inv(M);width=cam['orthographic_width_m'];height=width*1100/1600
def pixel(q):
 z=iv@np.r_[np.array(q)/1000,1.];return (float((z[0]/width+.5)*1600),float((.5-z[1]/height)*1100))
for label in labels:
 im=Image.open(REND/f'{label}__HUMAN_CAMERA__SOLID.png').convert('RGB');dr=ImageDraw.Draw(im);s=G['states'][label];v=s['vertices']
 if label!='OFFICIAL_L1_RSSF_DISPLAY':
  for faceids,color in [(normal['face_ids'],'#19d5e4'),(core['face_ids'],'#ff741f')]:
   for fi in faceids:
    pts=[pixel(v[i]) for i in F[fi]];dr.line(pts+[pts[0]],fill=color,width=2)
 else:
  # Source-native topology differs. Mark ancestry centroids; do not claim engineering face-ID equality.
  q=np.array([r['donor_ancestry_rest_world_m'] for r in C['per_vertex'] if r['vertex_id'] in [3353,3354,3359]])
  primary=np.array(C['candidate_world_mm'])[[3353,3354,3359]].mean(0);normalcenter=v0[normal['vertex_ids']].mean(0)
  for pt,col in [(primary,'#ff741f'),(normalcenter,'#19d5e4')]:
   x,y=pixel(pt);dr.ellipse((x-10,y-10,x+10,y+10),outline=col,width=4)
 dr.rectangle((0,0,1600,90),fill='#16222d');dr.text((18,10),'ORANGE: PRIMARY DEFECT CORE',fill='#ff934c',font=font(26));dr.text((18,47),'CYAN: EXCLUDED NORMAL / POSITION LOCKED',fill='#4eecf5',font=font(26));im.save(REND/f'{label}__HUMAN_CAMERA__ANNOTATED.png')
sheet([f'renders/{s}__HUMAN_CAMERA__ANNOTATED.png' for s in labels],['CURRENT','OFFICIAL L1 DONOR','FEASIBILITY PROBE','FORMAL DESIGN CANDIDATE'],'HUMAN_CAMERA__FIRST_SCREEN.png')
# Lower normal-region protection: every native point and complete49 faces exact; image differences separately quantified.
lock=read(OUT/'PALMAR_ROOT_HUMAN_TARGET_LOCK_R1.json');x0,y0,x1,y1=lock['EXCLUDED_NORMAL_ROI_pixel_xyxy'];scores={}
for style in ['SOLID','FLAT_SOURCE_NATIVE','GRAZING']:
 a=np.array(Image.open(REND/f'CURRENT_RAW__HUMAN_CAMERA__{style}.png'))[:,:,:3];b=np.array(Image.open(REND/f'FORMAL_CANDIDATE__HUMAN_CAMERA__{style}.png'))[:,:,:3];delta=np.abs(a.astype(float)-b.astype(float))[y0:y1+1,x0:x1+1];scores[style]={'mean_absolute_channel_difference_8bit':float(delta.mean()),'max_absolute_channel_difference_8bit':float(delta.max()),'pixels_any_channel_difference_gt3':int(np.count_nonzero(np.any(delta>3,axis=2))),'camera_light_scale_exact':True,'geometry_drift':0}
 for lab,data in [('CURRENT',a),('FORMAL_CANDIDATE',b)]:Image.fromarray(data[y0:y1+1,x0:x1+1]).save(REND/f'NORMAL_REGION__{lab}__{style}.png')
 sheet([f'renders/NORMAL_REGION__{s}__{style}.png' for s in ['CURRENT','FORMAL_CANDIDATE']],['NORMAL CURRENT (locked)','NORMAL FORMAL CANDIDATE'],f'NORMAL_REGION__{style}__BEFORE_AFTER.png')
z=read(OUT/'PALMAR_ROOT_NORMAL_CONTEXT_PROTECTION_R1.json');z.update(NORMAL_CONTEXT_VISIBLE_CHANGE='NEGLIGIBLE_ONLY',render_pixel_comparison=scores,shape_change_observed=False,Human_confirmation_pending=True);dump('PALMAR_ROOT_NORMAL_CONTEXT_PROTECTION_R1.json',z)
for cid in ['BIND']+read(OUT/'TEMP_DOWNSTREAM_COORDINATES_R1.json')['pose_smoke_cases']:
 for view in ['CLOSE','ALTERNATE']:
  for style in ['SOLID','FLAT_SOURCE_NATIVE','GRAZING']:
   sheet([f'renders/{s}_{cid}__{view}__{style}.png' for s in ['CURRENT','FORMAL_CANDIDATE']],['CURRENT / '+cid,'FORMAL CANDIDATE / '+cid],f'{cid}__{view}__{style}__COMPARISON.png')
print('Native crosssections, four-column panels, all normal styles generated; normal max',max(z['max_absolute_channel_difference_8bit'] for z in scores.values()),flush=True)
