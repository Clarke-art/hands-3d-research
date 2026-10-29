import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
G=read(OUT/'DIAGNOSTIC_RENDER_GEOMETRY_R1.json');triangles=read(OUT/'NATIVE_DISPLAY_LOOP_TRIANGLES_R1.json');roi=G['roi'];fr=G['frame'];origin=np.array(fr['origin_world_mm']);n=np.array(fr['normal']);ax=np.array(fr['finger_axis_tangent']);cx=np.array(fr['cross_finger_tangent'])
REND=OUT/'renders';SECT=OUT/'sections';SECT.mkdir(exist_ok=True)
planes={'FINGER_AXIS':ax,'CROSS_FINGER_AXIS':cx,'DIAGONAL_TANGENT':(ax+cx)/np.sqrt(2)}
states=['OFFICIAL_L1','STAGE2_L1','STAGE4A_R2_BASE','STAGE4A_R2','STAGE4B_RSSF','PRE_DONOR_STAGE4C_RAW','CURRENT_R2_RAW','CURRENT_R2_ZERO','IDX_MCP_15','IDX_MCP_30','TH_IP_15'];out={};origins={}
mapping=read(OUT/'PALMAR_IRREGULARITY_SOURCE_DONOR_COMPARISON_R1.json')['candidate_current_to_source'];seed=G['faces'][fr['seed_face_id']]
for label in states:
 src=G['source_states'].get(label);v=np.array(src['positions_mm'] if src else G['states'][label]);ids=set(src['roi_faces'] if src else roi['2_ring_faces']);out[label]={}
 anchor=origin.copy()
 if src:
  if label=='STAGE4A_R2_BASE':anchor=np.mean([v[mapping[str(i)]['stage4a_base_vertex']] for i in seed],axis=0)
  else:anchor=np.mean([sum((v[int(j)]*w for j,w in mapping[str(i)]['L1_parent_weights'].items()),np.zeros(3)) for i in seed],axis=0)
 origins[label]=anchor.tolist()
 for name,d in planes.items():
  pn=np.cross(n,d);segs=[]
  for row in triangles[label]:
   if row['face_id'] not in ids:continue
   vv=v[row['vertex_ids']];dist=(vv-anchor)@pn;pts=[]
   for i,j in [(0,1),(1,2),(2,0)]:
    if abs(dist[i])<1e-8:pts.append(vv[i])
    if dist[i]*dist[j]<0:pts.append(vv[i]+(vv[j]-vv[i])*dist[i]/(dist[i]-dist[j]))
   unique=[]
   for q in pts:
    if not any(np.linalg.norm(q-z)<1e-8 for z in unique):unique.append(q)
   if len(unique)==2:segs.append({'face_id':row['face_id'],'triangle_vertex_ids':row['vertex_ids'],'world_mm':[q.tolist() for q in unique],'profile_mm':[[float((q-anchor)@d),float((q-anchor)@n)] for q in unique]})
  out[label][name]=segs
dump('PALMAR_IRREGULARITY_NATIVE_CROSS_SECTIONS_R1.json',{'method':'plane intersections with actual Blender 5.1 display loop triangles on unmodified native face cycles and frozen coordinates','origin_world_mm':origin,'physical_ancestry_matched_origins_per_state_mm':origins,'normal':n,'planes':planes,'registration_caveat':'source topology and fixed rigid diagnostic fit differ; donor and base sections anchored on same seed-face ancestry, current RAW/ZERO/POSED share fixed RAW origin; donor offset is not a defect metric','states':out,'actual_geometry_not_shading':True})
colors={'OFFICIAL_L1':'#7d46c1','STAGE2_L1':'#ada2c4','STAGE4A_R2_BASE':'#b57938','STAGE4A_R2':'#994422','STAGE4B_RSSF':'#444444','PRE_DONOR_STAGE4C_RAW':'#999999','CURRENT_R2_RAW':'#148247','CURRENT_R2_ZERO':'#079bab','IDX_MCP_15':'#ef9c17','IDX_MCP_30':'#e83c38','TH_IP_15':'#2e6cc4'}
for name in planes:
 fig,axs=plt.subplots(1,2,figsize=(15,5.3),layout='constrained')
 for a,labels,title in [(axs[0],['CURRENT_R2_RAW','CURRENT_R2_ZERO','IDX_MCP_30','TH_IP_15'],'RAW / ZERO / saved poses'),(axs[1],['OFFICIAL_L1','STAGE2_L1','STAGE4A_R2_BASE','STAGE4B_RSSF','CURRENT_R2_RAW'],'Native geometry lineage (fixed registration)')]:
  for label in labels:
   first=True
   for seg in out[label][name]:
    q=np.array(seg['profile_mm']);a.plot(q[:,0],q[:,1],color=colors[label],lw=1.8,label=label if first else None,alpha=.85);first=False
  a.set_title(title);a.set_xlabel('Local tangent distance (mm)');a.set_ylabel('Normal height (mm)');a.set_xlim(-18,18);a.grid(alpha=.2);a.legend(fontsize=8)
 fig.suptitle(name+' — actual native triangle/plane intersection, no interpolation smoothing');fig.savefig(SECT/(name+'.png'),dpi=140);plt.close(fig)
# Direct algebra of the saved case, without bpy pose setters/evaluations.
nat=read(NATIVE);rb=nat['protected']['rigs']['RIGHT_HAND_PRODUCTION_RIG'];bones=rb['bones'];mw=np.array(rb['object']['matrices']['matrix_world']);weights=nat['positive_weight_vectors'];raw=np.array(G['states']['CURRENT_R2_RAW'])/1000;cases=read(FRESH/'FULL_STAGE6A_CASE_MATRIX_R1.json')['cases'];driver=read(OUT/'PALMAR_IRREGULARITY_SKIN_DRIVER_DIAGNOSTIC_R1.json');evidence={}
for cid in CASES:
 c=next(x for x in cases if x['case_id']==cid);bn=c['bone'];desc={bn};todo=[bn]
 while todo:
  b=todo.pop()
  for ch in bones[b]['children']:desc.add(ch);todo.append(ch)
 angle=math.radians(c['applied_rotation_deg']);r=np.eye(4);r[1:3,1:3]=[[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]];bmat=np.array(bones[bn]['matrix_local']);tm=mw@bmat@<REDACTED_EMAIL>(bmat)@np.linalg.inv(mw)
 rotated=(np.column_stack([raw,np.ones(len(raw))])@tm.T)[:,:3];ws=np.array([sum(w.get(k,0) for k in desc) for w in weights]);pred=raw+(rotated-raw)*ws[:,None];saved=np.array(G['states'][cid])/1000;err=np.linalg.norm(pred-saved,axis=1)*1000
 evidence[cid]={'bone':bn,'applied_rotation_degrees':c['applied_rotation_deg'],'descendant_driver_groups':sorted(desc),'prediction':'single saved joint local-X rigid transform weighted by exact descendant support; armature preserve volume disabled','saved_case_reconstruction_max_ROI_error_mm':float(err[roi['vertices']].max()),'saved_case_reconstruction_max_whole_mesh_error_mm':float(err.max()),'ROI_support_mass':{str(i):float(ws[i]) for i in roi['vertices']},'zero_support_vertices':sum(ws[i]==0 for i in roi['vertices']),'partial_support_vertices':sum(0<ws[i]<1 for i in roi['vertices']),'full_support_vertices':sum(ws[i]>=1-1e-6 for i in roi['vertices']),'arithmetic_only_not_pose_application':True}
driver['saved_case_LBS_reconstruction']=evidence;driver['candidate_attribution']='Actual limited IDX change is reconstructed by existing linear blend skinning and frozen joint transform; TH_IP has zero support in candidate ROI. Baseline triangular ridge already exists at raw. No rig transform defect established.';dump('PALMAR_IRREGULARITY_SKIN_DRIVER_DIAGNOSTIC_R1.json',driver)
# Pixel evidence selection overlay and candidate silhouette comparisons (display artifacts only).
src=Image.open(PREP/'renders/IDX_MCP_30__LOCAL_ALTERNATE.png').convert('RGB');dr=ImageDraw.Draw(src)
for box in roi['pixel_rectangles_xyxy']:dr.rectangle(box,outline=(255,180,20),width=4)
dr.rectangle((0,0,1600,62),fill=(25,30,40));dr.text((20,20),'PROVISIONAL CANDIDATE ONLY - Human screenshot absent - pixel raycast ROI',fill='white');src.save(REND/'CANDIDATE_PIXEL_SELECTION.png')
# ROI silhouette in camera projection: exterior edges of visible ROI face patch, not the complete hand outline.
camera=np.array(G['camera_source']['camera']['camera_world_matrix']);right=camera[:3,0];up=camera[:3,1];center=camera[:3,3]*1000
boundary=[]
for fi in roi['visible_hit_faces']:
 p=G['faces'][fi]
 for a,b in zip(p,p[1:]+p[:1]):
  key=tuple(sorted((a,b)))
  if key in boundary:boundary.remove(key)
  else:boundary.append(key)
fig,axs=plt.subplots(1,2,figsize=(12,5),layout='constrained');deviations={}
rawmm=np.array(G['states']['CURRENT_R2_RAW'])
for aa,view in zip(axs,[np.column_stack([right,up]),np.column_stack([cx,n])]):
 for label in ['CURRENT_R2_RAW','CURRENT_R2_ZERO','IDX_MCP_30','TH_IP_15']:
  v=np.array(G['states'][label]);q=(v-origin)@view;first=True
  for a,b in boundary:aa.plot(q[[a,b],0],q[[a,b],1],color=colors[label],label=label if first else None,lw=1.2);first=False
  deviations[label]=float(np.linalg.norm(((v-rawmm)@view)[roi['vertices']],axis=1).max())
 aa.axis('equal');aa.grid(alpha=.2);aa.legend(fontsize=8);aa.set_xlabel('Projected mm');aa.set_ylabel('Projected mm')
axs[0].set_title('ROI boundary in candidate camera');axs[1].set_title('ROI tangent / normal projection');fig.suptitle('ROI boundary displacement, not whole-hand silhouette');fig.savefig(SECT/'ROI_BOUNDARY_PROJECTION.png',dpi=140);plt.close(fig)
dump('PALMAR_IRREGULARITY_SILHOUETTE_DIAGNOSTIC_R1.json',{'scope':'visible ROI patch boundary only; whole-hand mask renders supplied separately','boundary_edges':boundary,'last_projection_max_displacement_mm':deviations,'no_product_threshold':True})
print('Sections / saved-case algebra complete; max ROI reconstruction errors mm',{k:v['saved_case_reconstruction_max_ROI_error_mm'] for k,v in evidence.items()},flush=True)
