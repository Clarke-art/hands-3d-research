from common import *
import numpy as np
from PIL import Image,ImageDraw,ImageFont
G=read(OUT/'MATCHED_ZERO_BIND_REVIEW_GEOMETRY_R1.json');D=read(OUT/'CLEAN_REOPEN_NATIVE_PAYLOADS_R1.json');B=read(OUT/'BIND_ZERO_GEOMETRY_REVALIDATION_AFTER_PALMAR_R1.json')
design=ROOT/'audits/palmar_digit_root_local_donor_shape_restoration_design_r1'
normal=read(design/'PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json')['vertex_ids']
dorsal=read(ROOT/'audits/local_donor_shape_transfer_amendment_design_r1/FORMAL_DONOR_TRANSFER_WRITE_SET_R1.json')['vertex_ids']
V=np.array(G['stages']['R2_RAW']['world_m']);Z=np.array(G['stages']['R2_BIND_ZERO']['world_m']);F=G['faces']
support={}
for name,ids in [('palmar16',IDS),('normal69',normal),('dorsal54',dorsal)]:
 assert len(ids)=={'palmar16':16,'normal69':69,'dorsal54':54}[name]
 assert all(D['R2']['coordinates_local_m'][i]==D['STAGE4']['coordinates_local_m'][i] for i in ids)
 roi=[i for i,f in enumerate(F) if set(f)&set(ids)];areas=[]
 for fi in roi:
  f=F[fi]
  for k in range(1,len(f)-1):
   vv=[f[0],f[k],f[k+1]];a=V[vv];z=Z[vv];na=np.cross(a[1]-a[0],a[2]-a[0]);nz=np.cross(z[1]-z[0],z[2]-z[0]);aa=np.linalg.norm(na);az=np.linalg.norm(nz)
   areas.append({'native_face':fi,'triangle_vertex_ids':vv,'raw_area_mm2':float(aa*.5e6),'zero_area_mm2':float(az*.5e6),'zero_to_raw_area_ratio':float(az/aa),'orientation_dot':float(na@nz)})
 assert all(a['zero_area_mm2']>0 and a['orientation_dot']>0 for a in areas)
 assert all(B['all3416_delta_mm'][i]<=B['recovered_existing_tolerance_mm'] for i in ids)
 support[name]={'status':'PASS','native_ids':ids,'raw_match_latest_Stage4C_exact':True,'zero_max_displacement_mm':max(B['all3416_delta_mm'][i] for i in ids),'formal_zero_gate_mm':B['recovered_existing_tolerance_mm'],'zero_out_of_tolerance_count':0,'incident_native_face_ids':roi,'triangles':areas,'zero_area_count':0,'orientation_reversal_count':0,'area_ratio_min':min(a['zero_to_raw_area_ratio'] for a in areas),'area_ratio_max':max(a['zero_to_raw_area_ratio'] for a in areas),'new_area_ratio_threshold':False,'classification':'ZERO contour numerical support; no static skin continuity or nonzero pose qualification'}
 support[name]['old_to_new_raw_coords_changed_count']=sum(D['OLD_R2']['coordinates_local_m'][i]!=D['R2']['coordinates_local_m'][i] for i in ids)
dump('ZERO_BIND_PROTECTED_SURFACE_NUMERICAL_SUPPORT_R1.json',support)
# Fresh native ID consistency only on both actual reopened Stage5 topologies.
current=ROOT/'production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/LOCKED_CURRENT9_ROWS_R1.json'
rows=read(current)['rows'];overlap={}
for key in ('CORRECTED','R2'):
 s=D[key];adj=[set() for _ in s['coordinates_local_m']]
 for _,(a,b) in s['protected']['mesh']['edges']:adj[a].add(b);adj[b].add(a)
 w=set(IDS);one=w|{j for i in w for j in adj[i]};two=one|{j for i in one for j in adj[i]};wf={i for i,f in s['protected']['mesh']['faces'] if set(f)&w}
 result=[{'pair_id':r['pair_id'],'case_id':r['case_id'],'direct_vertex_overlap':sorted(w&set(r['vertex_ids'])),'changed_face_overlap':sorted(wf&set(r['face_ids'])),'1ring_overlap':sorted(one&set(r['vertex_ids'])),'2ring_overlap':sorted(two&set(r['vertex_ids']))} for r in rows]
 counts=[sum(bool(r['direct_vertex_overlap'] or r['changed_face_overlap']) for r in result),sum(bool(r['1ring_overlap']) for r in result),sum(bool(r['2ring_overlap']) for r in result)]
 assert counts==[0,0,0]
 overlap[key]={'counts_direct_1ring_2ring':counts,'rows':result}
response=Path('<USER_HOME>/Downloads/CURRENT_FULL_STAGE6A_CROSSING_HUMAN_RESPONSE_R1.json')
dump('CURRENT9_HOLD_AND_OVERLAP_RECHECK_R1.json',{'status':'PASS','CURRENT9_DIRECT_OVERLAP':0,'CURRENT9_1RING_OVERLAP':0,'CURRENT9_2RING_OVERLAP':0,'CURRENT9_HUMAN_RESPONSE':'HOLD_NOT_CLOSED','paths':overlap,'frozen_rows':ref(current),'prior_hold_receipt':ref(PROP/'CURRENT9_RESPONSE_STATE_BEFORE.json'),'external_response':ref(response) if response.is_file() else None,'external_response_missing_if_null_not_reconstructed':True,'answer_writes':0,'closure_generated':False,'acceptance_expansion':False,'scope':'native ID consistency only; no crossing or deformation qualification'})
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
labels=['STAGE4_RAW','R2_RAW','R2_BIND_ZERO'];titles=['Latest Stage4C RAW','New Stage5B RAW','Actual Stage5B evaluated ZERO']
groups={'PALMAR_SOLID_INSPECTION_R1.png':[('HUMAN_CAMERA','SOLID'),('CLOSE','SOLID'),('ALTERNATE','SOLID')],'PALMAR_DETAIL_INSPECTION_R1.png':[('CLOSE','GRAZING'),('CLOSE','FLAT_SOURCE_NATIVE'),('CLOSE','WIRE')],'DORSAL_SENTINEL_INSPECTION_R1.png':[('DORSAL_CLOSE','FLAT'),('DORSAL_CLOSE','SOURCE_NATIVE'),('DORSAL_GRAZING','SOURCE_NATIVE')]}
comparisons=[]
for filename,views in groups.items():
 dims=(720,495) if filename.startswith('PALMAR') else (640,640)
 sheet=Image.new('RGB',(dims[0]*3,(dims[1]+42)*len(views)),'#e7edf2');draw=ImageDraw.Draw(sheet)
 for row,(view,kind) in enumerate(views):
  images=[]
  for col,(label,title) in enumerate(zip(labels,titles)):
   fn=f'{label}__{view}__{kind}.png' if filename.startswith('PALMAR') else f'{label}_{view}_{kind}.png'
   im=Image.open(OUT/'renders'/fn).convert('RGB');images.append(np.array(im).astype(np.int16));sheet.paste(im.resize(dims,Image.Resampling.LANCZOS),(col*dims[0],row*(dims[1]+42)+42));draw.text((col*dims[0]+8,row*(dims[1]+42)+8),title+' | '+view+' / '+kind,font=font,fill='#163047')
  comparisons.append({'view':view,'kind':kind,'Stage4C_vs_Stage5B_raw_pixel_exact':bool(np.array_equal(images[0],images[1])),'raw_zero_RGB_scalar_changed_count':int(np.count_nonzero(images[1]-images[2])),'raw_zero_RGB_mean_absolute_difference':float(np.abs(images[1]-images[2]).mean()),'raw_zero_RGB_max_scalar_difference':int(np.abs(images[1]-images[2]).max())})
 sheet.save(OUT/filename)
dump('MATCHED_RENDER_PIXEL_SUPPORT_R1.json',{'rows':comparisons,'classification':'supplemental matched camera pixel evidence; not a new qualification threshold'})
print('normal69 / dorsal54 / palmar16 bind-zero numerical support; both current9 overlaps 0/0/0; three contact sheets ready')
