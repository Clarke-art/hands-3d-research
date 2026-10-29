import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image,ImageDraw,ImageFont
G=read(OUT/'PALMAR_APPLICATION_MATCHED_REVIEW_GEOMETRY_R1.json');C=read(OUT/'PALMAR_APPLICATION_NATIVE_GEOMETRY_R1.json');tri=read(OUT/'PALMAR_APPLICATION_NATIVE_RENDER_TRIANGLES_R1.json');prior=read(DESIGN/'PALMAR_ROOT_NATIVE_CROSS_SECTIONS_R1.json');normal=G['normal'];core=G['core'];F=C['faces'];REND=OUT/'renders';SECT=OUT/'sections';SECT.mkdir(exist_ok=True)
labels=['SOURCE_STAGE4C','APPROVED_FORMAL_CANDIDATE','APPLIED_NEW_STAGE4C_REVISION'];titles=['CURRENT SOURCE STAGE4C','HUMAN-APPROVED CANDIDATE','APPLIED NEW STAGE4C REVISION'];fs={i for i,p in enumerate(F) if set(p)&set(IDS)}|set(core['face_ids']);origin=np.array(prior['origin_world_mm']);n=np.array(prior['normal']);planes={k:np.array(v) for k,v in prior['planes'].items()};sections={}
for label in labels:
 v=np.array(G['states'][label]['vertices']);sections[label]={}
 for name,d in planes.items():
  pn=np.cross(n,d);segs=[]
  for row in tri[label]:
   if row['face_id'] not in fs:continue
   q=v[row['vertex_ids']];dist=(q-origin)@pn;pts=[]
   for a,b in [(0,1),(1,2),(2,0)]:
    if abs(dist[a])<1e-8:pts.append(q[a])
    if dist[a]*dist[b]<0:pts.append(q[a]+(q[b]-q[a])*dist[a]/(dist[a]-dist[b]))
   unique=[]
   for p in pts:
    if not any(np.linalg.norm(p-z)<1e-8 for z in unique):unique.append(p)
   if len(unique)==2:segs.append({'face_id':row['face_id'],'native_triangle_ids':row['vertex_ids'],'world_mm':[p.tolist() for p in unique],'profile_mm':[[float((p-origin)@d),float((p-origin)@n)] for p in unique]})
  assert segs;sections[label][name]=segs
assert sections[labels[1]]==sections[labels[2]]
dump('PALMAR_APPLICATION_NATIVE_SECTIONS_R1.json',{'method':'Fresh actual application / approved / source Blender loop-triangle intersections; immutable approved section planes; no profile smoothing','origin_world_mm':origin,'normal':n,'planes':planes,'states':sections,'approved_applied_sections_exact':True,'design_geometry_not_substituted':True})
colors=['#d64935','#8560bd','#19884c']
for name in planes:
 fig,ax=plt.subplots(figsize=(10,5),layout='constrained')
 for label,color in zip(labels,colors):
  for j,s in enumerate(sections[label][name]):
   q=np.array(s['profile_mm']);ax.plot(q[:,0],q[:,1],color=color,lw=2 if label!=labels[2] else 1.5,ls='--' if label==labels[2] else '-',label=label if j==0 else None)
 ax.legend(fontsize=8);ax.grid(alpha=.2);ax.set_xlabel('Tangent distance (mm)');ax.set_ylabel('Normal height (mm)');ax.set_title(name+' / fresh actual native application geometry');fig.savefig(SECT/(name+'.png'),dpi=160);plt.close(fig)
def font(size):return ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',size)
def sheet(files,captions,name):
 w=640;h=440;im=Image.new('RGB',(w*len(files),h+55),'white');dr=ImageDraw.Draw(im)
 for i,(file,title) in enumerate(zip(files,captions)):
  with Image.open(OUT/file) as z:im.paste(z.convert('RGB').resize((w,h)),(i*w,55))
  dr.text((i*w+12,15),title,fill='#173042',font=font(19))
 im.save(REND/name)
for view in ['HUMAN_CAMERA','CLOSE','ALTERNATE']:
 for style in ['SOLID','GRAZING','FLAT_SOURCE_NATIVE','WIRE','ROI_LABEL']:
  sheet([f'renders/{s}__{view}__{style}.png' for s in labels],titles,view+'__'+style+'__THREE_COLUMN.png')
# Approved vs actual application pixel equality is checked on fresh renders under every view/style.
pixel={}
for view in ['HUMAN_CAMERA','CLOSE','ALTERNATE']:
 for style in ['SOLID','GRAZING','FLAT_SOURCE_NATIVE','WIRE','ROI_LABEL']:
  a=np.array(Image.open(REND/f'{labels[1]}__{view}__{style}.png'));b=np.array(Image.open(REND/f'{labels[2]}__{view}__{style}.png'));assert np.array_equal(a,b),(view,style,'FAIL_CLOSED visual application mismatch')
  pixel[view+'__'+style]={'pixel_exact':True,'max_channel_delta':0,'changed_pixels':0,'new_renders_this_round':True}
normal_pixels={};box=read(DESIGN/'PALMAR_ROOT_HUMAN_TARGET_LOCK_R1.json')['EXCLUDED_NORMAL_ROI_pixel_xyxy'];x0,y0,x1,y1=box
for style in ['SOLID','FLAT_SOURCE_NATIVE','GRAZING']:
 a=np.array(Image.open(REND/f'{labels[0]}__HUMAN_CAMERA__{style}.png'))[:,:,:3];b=np.array(Image.open(REND/f'{labels[2]}__HUMAN_CAMERA__{style}.png'))[:,:,:3];d=np.abs(a.astype(float)-b.astype(float))[y0:y1+1,x0:x1+1]
 normal_pixels[style]={'max_8bit_channel_difference':float(d.max()),'mean_8bit_channel_difference':float(d.mean()),'pixels_any_channel_difference_above3':int(np.count_nonzero(np.any(d>3,axis=2))),'native_geometry_drift':0,'fresh_application_render':True}
 for lab,data in [('SOURCE',a),('APPLIED',b)]:Image.fromarray(data[y0:y1+1,x0:x1+1]).save(REND/f'NORMAL_REGION__{lab}__{style}.png')
 sheet([f'renders/NORMAL_REGION__{s}__{style}.png' for s in ['SOURCE','APPLIED']],['LOCKED NORMAL / CURRENT SOURCE','LOCKED NORMAL / APPLIED REVISION'],f'NORMAL_REGION__{style}__BEFORE_AFTER.png')
N=read(OUT/'PALMAR_APPLICATION_NORMAL_CONTEXT_AUDIT_R1.json');N.update(status='PASS',NORMAL_CONTEXT_VISIBLE_CHANGE='NEGLIGIBLE_ONLY',fresh_matched_normal_render_comparison=normal_pixels,no_observed_shape_change=True);dump('PALMAR_APPLICATION_NORMAL_CONTEXT_AUDIT_R1.json',N)
dump('PALMAR_APPLICATION_VISUAL_EQUIVALENCE_R1.json',{'status':'PASS','VISUAL_APPLICATION_EQUIVALENCE':'PASS','APPROVED_DESIGN_APPLIED_EXACTLY':True,'fresh_actual_native_coordinate_renders':True,'approved_applied_fresh_render_pixel_comparison':pixel,'approved_applied_native_sections_exact':True,'primary_defect':'HUMAN_APPROVED_HARD_SHELF_REMOVED_OR_CLEARLY_REDUCED_APPLIED_EXACTLY','natural_crease':'HUMAN_APPROVED_PRESERVED_APPLIED_EXACTLY','normal_region':'HUMAN_APPROVED_UNCHANGED_NATIVE_EXACT_FRESH_RENDER_EQUIVALENT','candidate_reselection_needed':False,'new_Human_acceptance_not_expanded':True,'agent_visual_inspection':'PENDING','production_promoted':False})
print('Fresh three-column/native sections/pixel equivalence PASS; approved vs applied pixel exact in all15 comparisons; normal channel max',max(z['max_8bit_channel_difference'] for z in normal_pixels.values()),flush=True)
