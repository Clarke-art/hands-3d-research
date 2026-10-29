from common import *
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from html import escape
G=read(OUT/'MATCHED_ZERO_BIND_REVIEW_GEOMETRY_R1.json');J=read(OUT/'JOINT_SURFACE_REQUALIFICATION_R1.json')['all21_current_rows'];M=read(OUT/'MATCHED_RENDER_MANIFEST_R1.json');P=read(OUT/'MATCHED_NATIVE_POINT_PROJECTIONS_R1.json')['views']
fontpath='C:/Windows/Fonts/arial.ttf';font=ImageFont.truetype(fontpath,17);small=ImageFont.truetype(fontpath,14)
annotations=[]
for r in M['renders']:
 if r['path'] not in P:continue
 im=Image.open(OUT/r['path']).convert('RGB');d=ImageDraw.Draw(im);v=P[r['path']];view=r['view']
 def dot(p,c,radius=5):d.ellipse((p[0]-radius,p[1]-radius,p[0]+radius,p[1]+radius),fill=c,outline='white',width=1)
 def text(p,t,c='#0e1a27'):
  w=d.textbbox((0,0),t,font=small);box=(p[0],p[1],p[0]+w[2]+6,p[1]+21);d.rectangle(box,fill='#eef3f7');d.text((p[0]+3,p[1]+2),t,font=small,fill=c)
 def bone(n,label=None):
  b=v['bones'][n];tip='_TIP_' in n;c='#ec9e27' if tip else '#227a7a';d.line([tuple(b['head']),tuple(b['tail'])],fill=c,width=2);dot(b['head'],c)
  if label:text([b['head'][0]+6,b['head'][1]-21],label)
 if view=='JOINT_OVERVIEW':
  for i,n in enumerate(G['bones'],1):bone(n,str(i))
 elif view=='TIP_OVERVIEW':
  for n in G['bones']:
   if '_TIP_' in n:
    bone(n);p=v['bones'][n]['head'];offset={'INDEX_TIP_R':[-25,-32],'MIDDLE_TIP_R':[-45,-37],'RING_TIP_R':[10,9],'LITTLE_TIP_R':[18,-10],'THUMB_TIP_R':[10,-20]}[n]
    q=[p[0]+offset[0],p[1]+offset[1]];d.line([tuple(p),tuple(q)],fill='#ec9e27',width=1);text(q,n.replace('_R',''))
 elif view=='ROI_JOINTS':
  for p in v['approved54'].values():dot(p,'#d34c43',2)
  for n in ['RING_MCP_R','MIDDLE_MCP_R','LITTLE_MCP_R','INDEX_MCP_R']:bone(n,n.replace('_R',''))
  b=v['bones']['RING_MCP_R']['head'];q=v['RING_nearest_new'];d.line([tuple(b),tuple(q)],fill='#a43849',width=3);dot(q,'#a43849')
 elif view=='RING_MARGIN':
  bone('RING_MCP_R','RING_MCP fixed')
  q=v['RING_nearest_old'] if r['label']=='OLD_RAW' else v['RING_nearest_new'];h=v['bones']['RING_MCP_R']['head'];d.line([tuple(h),tuple(q)],fill='#ba4451',width=3);dot(q,'#ba4451')
  text([15,im.height-35],('Old 5.162971 mm' if r['label']=='OLD_RAW' else 'New 5.587251 mm')+' | 64/64 inside | T01 margin 8.875 mm')
 else:
  bone('THUMB_IP_R','IP');bone('THUMB_TIP_R','TIP non-deform');dot(v['terminal284'],'#d4454b',6)
  text([15,im.height-35],'TIP head = native terminal v284 | tail outside expected')
 out='renders/ANNOTATED_'+Path(r['path']).name;im.save(OUT/out);annotations.append({'view':view,'source':r['path'],'output':out,'projection_source':ref(OUT/'MATCHED_NATIVE_POINT_PROJECTIONS_R1.json'),'authoritative_source_geometry_or_joint_positions_modified':False})
dump('JOINT_ANNOTATION_EVIDENCE_MANIFEST_R1.json',{'annotations':annotations,'note':'Exact world points projected for audit: teal deform head/axis, gold non-deform helper, red approved54 or native terminal. Lines and markers are image overlay, not source geometry.'})
labels=['STAGE4_RAW','R2_RAW','R2_BIND_ZERO'];titles=['Stage4C approved raw','Stage5B R2 raw','Stage5B R2 bind ZERO']
# Inspection sheet for the requested three-column matched contour comparison.
sheet=Image.new('RGB',(1920,4*682),'#eef2f5');d=ImageDraw.Draw(sheet)
views=[('CLOSE','FLAT'),('CLOSE','SOURCE_NATIVE'),('GRAZING','SOURCE_NATIVE'),('SIDE','FLAT')]
for row,(view,shade) in enumerate(views):
 for col,(label,title) in enumerate(zip(labels,titles)):
  im=Image.open(OUT/f'renders/{label}_{view}_{shade}.png').convert('RGB');sheet.paste(im,(col*640,row*682+42));d.text((col*640+12,row*682+9),title+' | '+view+' / '+shade,font=font,fill='#132a40')
sheet.save(OUT/'MATCHED_RAW_BIND_CONTOUR_INSPECTION_R1.png')

# Actual native triangle/plane sections, reusing only approved scientific plotting functions.
previous=read(APP/'APPLICATION_MATCHED_REVIEW_GEOMETRY_R1.json');roi=previous['stages']['APPLIED_NEW_STAGE4C_REVISION']['roi_faces'];frame=G['frame']
origin=np.array(frame['origin_world_mm']);x=np.array(frame['x']);y=np.array(frame['y']);n=np.array(frame['outward'])
design=ROOT/'audits/local_donor_shape_transfer_amendment_design_r1'
reused=reuse(design/'prepare_visuals.py',['sections'],globals())
Q={'stages':{k:sections(np.array(s['world_m'])*1000,G['faces'],roi) for k,s in G['stages'].items()}}
assert Q['stages']['STAGE4_RAW']==Q['stages']['R2_RAW']
dump('RAW_BIND_NATIVE_SECTION_COMPARISON_R1.json',{'section_source':reused,'physical_frame':frame,**Q})
(OUT/'sections').mkdir(exist_ok=True)
reuse(design/'deliver.py',['plot'],globals())
for a in (0,60,120):
 plot(a,[[(k,t,'#303b42')] for k,t in zip(labels,titles)],f'MATCHED_ZERO_BIND_SECTIONS_{a}.svg')
 plot(a,[[('R2_RAW','Raw','#c25542'),('R2_BIND_ZERO','Bind ZERO','#246899')]],f'RAW_BIND_OVERLAY_{a}.svg')
Vraw=np.array(G['stages']['R2_RAW']['world_m']);Vbind=np.array(G['stages']['R2_BIND_ZERO']['world_m']);areas=[]
for fi in roi:
 p=G['faces'][fi]
 for t in range(1,len(p)-1):
  ids=[p[0],p[t],p[t+1]];a,b=Vraw[ids],Vbind[ids];na=np.cross(a[1]-a[0],a[2]-a[0]);nb=np.cross(b[1]-b[0],b[2]-b[0]);aa=np.linalg.norm(na)*.5*1e6;ab=np.linalg.norm(nb)*.5*1e6
  areas.append({'native_face':fi,'triangle_vertex_ids':ids,'raw_area_mm2':float(aa),'bind_area_mm2':float(ab),'ratio':float(ab/aa),'orientation_dot':float(na@nb)})
assert all(a['bind_area_mm2']>0 and a['orientation_dot']>0 for a in areas)
dump('DORSAL_MCP_BIND_ZERO_NUMERICAL_CONTOUR_SUPPORT_R1.json',{'status':'PASS','geometry_authority':ref(FILES['STAGE4']),'raw_full_coordinate_exact':True,'raw_to_bind_gate':ref(OUT/'BIND_ZERO_GEOMETRY_REVALIDATION_R1.json'),'ROI_native_face_ids':roi,'ROI_native_triangle_count':len(areas),'zero_area_triangle_count':sum(a['bind_area_mm2']==0 for a in areas),'zero_bind_triangle_orientation_reversal_count':sum(a['orientation_dot']<=0 for a in areas),'minimum_bind_to_raw_triangle_area_ratio':min(a['ratio'] for a in areas),'maximum_bind_to_raw_triangle_area_ratio':max(a['ratio'] for a in areas),'triangles':areas,'classification':'Zero/bind local contour support only; not static skin continuity or posed deformation qualification'})
print('VISUAL PREPARED 18 renders / 6 native sections / overlays / inspection sheet')
