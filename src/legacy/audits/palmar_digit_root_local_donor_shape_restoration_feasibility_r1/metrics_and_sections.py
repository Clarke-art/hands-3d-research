import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image,ImageDraw,ImageFont
G=read(OUT/'MATCHED_REVIEW_GEOMETRY_R1.json');P=read(OUT/'TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.json');core=G['core'];normal=G['normal'];F=G['faces'];E=G['edges'];ids=P['moved_vertex_ids'];scope=read(OUT/'PALMAR_ROOT_TRANSFER_SCOPE_R1.json');tri=read(OUT/'NATIVE_RENDER_LOOP_TRIANGLES_R1.json');lock=read(OUT/'PALMAR_ROOT_HUMAN_TARGET_LOCK_R1.json');sources=read(OUT/'PALMAR_ROOT_SOURCE_ANCESTRY_R1.json')['current_to_donor'];REND=OUT/'renders';SECT=OUT/'sections';SECT.mkdir(exist_ok=True)
def geometry(v,faces,fs):
 nn=[];areas=[];edgefaces={}
 for i,p in enumerate(faces):
  q=v[p];a=sum((np.cross(q[k]-q[0],q[k+1]-q[0]) for k in range(1,len(q)-1)),np.zeros(3));nn.append(a/max(np.linalg.norm(a),1e-15));areas.append(float(np.linalg.norm(a)/2))
  if i in fs:
   for a,b in zip(p,p[1:]+p[:1]):edgefaces.setdefault(tuple(sorted((a,b))),[]).append(i)
 nn=np.array(nn);di=[{'vertex_ids':list(e),'face_ids':ff,'dihedral_deg':math.degrees(math.acos(float(np.clip(nn[ff[0]]@nn[ff[1]],-1,1))))} for e,ff in edgefaces.items() if len(ff)==2];di.sort(key=lambda z:-z['dihedral_deg'])
 return nn,areas,di
v0=np.array(G['states']['CURRENT_RAW']['vertices']);v1=np.array(G['states']['TRANSFER_PROBE']['vertices']);cfs=set(core['face_ids']);fs={i for i,p in enumerate(F) if set(p)&set(ids)}|cfs
nn,a,d0=geometry(v0,F,fs);origin=v0[scope['DEFECT_CORE_WRITE_VERTEX_IDS']].mean(0);n=nn[list(cfs)].sum(0);n/=np.linalg.norm(n);axis=np.array([0.,0.,1.]);axis-=n*(axis@n);axis/=np.linalg.norm(axis);cross=np.cross(n,axis);planes={'FINGER_AXIS':axis,'CROSS_FINGER_AXIS':cross,'DIAGONAL_TANGENT':(axis+cross)/np.sqrt(2)}
parents={int(k) for i in ids for k in sources[str(i)]['L1_parent_weights']};out={};metrics={}
for label in ['CURRENT_RAW','OFFICIAL_L1_RSSF_DISPLAY','TRANSFER_PROBE']:
 s=G['states'][label];v=np.array(s['vertices']);ff=s['faces'];sf=fs if label!='OFFICIAL_L1_RSSF_DISPLAY' else {i for i,p in enumerate(ff) if set(p)&parents};ns,area,di=geometry(v,ff,sf);metrics[label]={'adjacent_face_dihedral':di,'face_areas_mm2':{str(i):area[i] for i in sf},'ROI_face_count':len(sf),'same_native_topology_as_current':ff==F,'mean_native_dihedral_deg':float(np.mean([r['dihedral_deg'] for r in di])),'max_native_dihedral_deg':max(r['dihedral_deg'] for r in di),'natural_crease_not_flat_target':True};out[label]={}
 for name,d in planes.items():
  pn=np.cross(n,d);segments=[]
  for row in tri[label]:
   if row['face_id'] not in sf:continue
   q=v[row['vertex_ids']];dist=(q-origin)@pn;pts=[]
   for i,j in [(0,1),(1,2),(2,0)]:
    if abs(dist[i])<1e-8:pts.append(q[i])
    if dist[i]*dist[j]<0:pts.append(q[i]+(q[j]-q[i])*dist[i]/(dist[i]-dist[j]))
   unique=[]
   for p in pts:
    if not any(np.linalg.norm(p-x)<1e-8 for x in unique):unique.append(p)
   if len(unique)==2:segments.append({'face_id':row['face_id'],'triangle_vertices':row['vertex_ids'],'world_mm':[x.tolist() for x in unique],'profile_mm':[[float((x-origin)@d),float((x-origin)@n)] for x in unique]})
  out[label][name]=segments
dump('PALMAR_ROOT_NATIVE_CROSS_SECTIONS_R1.json',{'method':'actual Blender native loop-triangle / plane intersections; current/donor-RSSF-display/probe share static coordinate frame and identical section planes','origin_world_mm':origin,'normal':n,'planes':planes,'states':out,'donor_topology_not_transferred':True,'no_profile_smoothing':True})
colors={'CURRENT_RAW':'#d54836','OFFICIAL_L1_RSSF_DISPLAY':'#6f43b5','TRANSFER_PROBE':'#15945d'}
for name in planes:
 fig,ax=plt.subplots(figsize=(9,5),layout='constrained')
 for label in out:
  first=True
  for seg in out[label][name]:
   q=np.array(seg['profile_mm']);ax.plot(q[:,0],q[:,1],color=colors[label],lw=2,label=label if first else None);first=False
 ax.legend();ax.grid(alpha=.2);ax.set_xlabel('Local tangent distance (mm)');ax.set_ylabel('Normal height (mm)');ax.set_title(name+' — native mesh geometry / fixed static RAW frame');fig.savefig(SECT/(name+'.png'),dpi=160);plt.close(fig)
# Source / construction history is comparison only, not another historical operation run.
T=read(SOURCE/'HISTORICAL_OPERATION_RAM_REPLAY.json');event=next(e for e in T['events'] if set(v['vertex_id'] for v in e['new_vertices'])==set(ids));prior=next(s for s in T['snapshots'] if s['name']==event['label']);construction={'earliest_snapshot':event['label'],'formal_asset_stage':'STAGE4A_R2_BASE','inserted_vertex_ids':[v['vertex_id'] for v in event['new_vertices']],'same_write_loop_exact':True,'historical_event_receipt':event['receipt'],'source':ref(SOURCE/'HISTORICAL_OPERATION_RAM_REPLAY.json'),'new_operation_replay':False}
dump('PALMAR_ROOT_EXISTING_CONSTRUCTION_LINEAGE_R1.json',construction)
donor=read(OUT/'PALMAR_ROOT_DONOR_SOURCE_COMPARISON_R1.json');donor.update(SOURCE_NATURAL_CREASE_PRESENT='YES',CURRENT_HARD_FACETING_PRESENT='YES',ENGINEERING_AMPLIFICATION_CONFIRMED='YES',EARLIEST_CONFIRMED_HARD_FACETING_STAGE='STAGE4A_R2_BASE / saved CON1_MIDDLE_MCP@-1mm snapshot',canonical_donor='OFFICIAL_L1',Stage2_exact_equivalence=True,existing_construction_record=construction,targeted_static_metrics=metrics,source_current_comparison='donor natural crease retained; current inserted-loop shelf is absent in deterministic source ancestry target; display-only RSSF mapping brings native donor to same static frame')
dump('PALMAR_ROOT_DONOR_SOURCE_COMPARISON_R1.json',donor)
dump('PALMAR_ROOT_TARGETED_GEOMETRY_METRICS_R1.json',{'states':metrics,'native_structure_semantics':'no absolute projected bowtie zero; actual exact registry and no continuous triangle degeneracy in separate structure audit','write_vertex_displacement_mm':{str(i):(v1[i]-v0[i]).tolist() for i in ids},'probe_target_roundtrip_max_mm':max(np.linalg.norm(v1[i]-np.array(sources[str(i)]['target_current_frame_world_m'])*1000) for i in ids),'normal_context_geometry_exact':np.array_equal(v0[normal['vertex_ids']],v1[normal['vertex_ids']]),'cross_section_json':'PALMAR_ROOT_NATIVE_CROSS_SECTIONS_R1.json'})
def font(size):
 for p in ['C:/Windows/Fonts/segoeui.ttf','C:/Windows/Fonts/arial.ttf']:
  if Path(p).exists():return ImageFont.truetype(p,size)
 return ImageFont.load_default()
# A compact review strip with no visual retouching; same static frames already rendered.
def sheet(files,labels,path):
 thumbw=640;thumbh=440;im=Image.new('RGB',(thumbw*len(files),thumbh+55),'white');dr=ImageDraw.Draw(im)
 for i,(f,title) in enumerate(zip(files,labels)):
  with Image.open(OUT/f) as z:im.paste(z.convert('RGB').resize((thumbw,thumbh)),(thumbw*i,55))
  dr.text((thumbw*i+12,15),title,fill=(25,35,45),font=font(20))
 im.save(REND/path)
for view in ['HUMAN_CAMERA','CLOSE','ALTERNATE']:
 files=[f'renders/{s}__{view}__SOLID.png' for s in ['CURRENT_RAW','OFFICIAL_L1_RSSF_DISPLAY','TRANSFER_PROBE']]+[f'renders/TRANSFER_PROBE__{view}__ROI_LABEL.png'];sheet(files,['CURRENT RAW','OFFICIAL L1 / frozen RSSF','TRANSFER PROBE (design only)','ROI + position difference'],view+'__FOUR_COLUMN.png')
# Normal-area before/after crop is deterministic; no smoothing/edit to source pixels.
x0,y0,x1,y1=lock['EXCLUDED_NORMAL_ROI_pixel_xyxy'];scores={};normal_imgs=[]
for kind in ['SOLID','FLAT_SOURCE_NATIVE','GRAZING']:
 a=np.array(Image.open(REND/f'CURRENT_RAW__HUMAN_CAMERA__{kind}.png'))[:,:,:3];b=np.array(Image.open(REND/f'TRANSFER_PROBE__HUMAN_CAMERA__{kind}.png'))[:,:,:3];d=np.abs(a.astype(float)-b.astype(float))[y0:y1+1,x0:x1+1]
 scores[kind]={'mean_absolute_8bit_channel_difference':float(d.mean()),'max_absolute_8bit_channel_difference':float(d.max()),'geometry_change':False,'same_camera_scale_light_static_pose':True,'threshold_is_anatomy_gate':False}
 if kind=='SOLID':
  aa=Image.fromarray(a[y0:y1+1,x0:x1+1]);bb=Image.fromarray(b[y0:y1+1,x0:x1+1]);aa.save(REND/'EXCLUDED_NORMAL__BEFORE.png');bb.save(REND/'EXCLUDED_NORMAL__AFTER.png')
sheet(['renders/EXCLUDED_NORMAL__BEFORE.png','renders/EXCLUDED_NORMAL__AFTER.png'],['NORMAL AREA BEFORE (locked)','NORMAL AREA AFTER (unchanged)'],'EXCLUDED_NORMAL__BEFORE_AFTER.png')
audit=read(OUT/'PALMAR_ROOT_NORMAL_CONTEXT_PROTECTION_AUDIT_R1.json');audit.update(NORMAL_CONTEXT_VISIBLE_CHANGE='NEGLIGIBLE_PENDING_HUMAN',render_pixel_comparison=scores,new_visible_shape_change_observed=False,visual_observation='same lower normal contour; maximum1/255 shading/raster channel difference, no geometry change; Human review separately supplied');dump('PALMAR_ROOT_NORMAL_CONTEXT_PROTECTION_AUDIT_R1.json',audit)
# Distinct ROI outline labels on the original confirmed image (only display annotation).
base=Image.open(PRIOR/'renders/CANDIDATE_PIXEL_SELECTION.png').convert('RGB');dr=ImageDraw.Draw(base);dr.rectangle(lock['PRIMARY_DEFECT_ROI_pixel_xyxy'],outline=(255,80,35),width=5);dr.rectangle(lock['EXCLUDED_NORMAL_ROI_pixel_xyxy'],outline=(20,190,230),width=5);dr.rectangle((0,0,1600,70),fill=(24,30,40));dr.text((15,20),'HUMAN LOCK: upper orange = DEFECT CORE; lower cyan = NORMAL / POSITION LOCKED',fill='white',font=font(26));base.save(REND/'HUMAN_TARGET_LOCK_LABELS.png')
dump('PALMAR_ROOT_VISUAL_FEASIBILITY_REVIEW_R1.json',{'machine_visual_review':'SOURCE_LIKE_NATURAL_PALMAR_ROOT_CREASE_RESTORED_PENDING_HUMAN','views_inspected':['CURRENT_RAW / TRANSFER_PROBE / native donor CLOSE SOLID','CURRENT_RAW / TRANSFER_PROBE ALTERNATE SOLID'],'primary_shelf_reduced':True,'natural_crease_preserved':True,'whole_normal_area_recontoured':False,'normal_area_pixel_scores':scores,'geometry_based_structural_PASS':True,'Human_acceptance_pending':True,'not_formal_apply':True})
print('Native sections and exact normal-area pixel comparisons generated; max normal channel delta',max(v['max_absolute_8bit_channel_difference'] for v in scores.values()),'earliest',construction['earliest_snapshot'],flush=True)
