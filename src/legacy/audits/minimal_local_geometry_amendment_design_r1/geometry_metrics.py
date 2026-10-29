import sys
sys.dont_write_bytecode=True
from design import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
D=read(OUT/'GEOMETRY_AMENDMENT_CANDIDATES_R1.json');STATE=read(OUT/'CANDIDATE_EVALUATED_COORDINATES_R1.json')['states']
FULLFS=sorted(set(R['faces'])|{fi for c in D['candidates'].values() for fi,p in enumerate(F) if set(c['write_vertices']).intersection(p)})
FULLES=sorted({emap[tuple(sorted((a,b)))] for fi in FULLFS for p in [F[fi]] for a,b in zip(p,p[1:]+p[:1])})
core=R['core_vertices'];outer=R['2_ring'];n=B[:,2];x=B[:,0];y=B[:,1]
def area(v,p):return np.linalg.norm(sum((np.cross(v[p[k]]-v[p[0]],v[p[(k+1)%len(p)]]-v[p[0]]) for k in range(len(p))),np.zeros(3)))*.5
def sections(v):
 out=[]
 for angle in [0,60,120]:
  t=x*math.cos(math.radians(angle))+y*math.sin(math.radians(angle));pn=np.cross(n,t);segs=[]
  for fi in R['faces']:
   p=F[fi]
   for k in range(1,len(p)-1):
    tri=[p[0],p[k],p[k+1]];pts=[]
    for a,b in zip(tri,tri[1:]+tri[:1]):
     da=(v[a]-origin)@pn;db=(v[b]-origin)@pn
     if abs(da)<1e-9:pts.append(v[a])
     if da*db<0:pts.append(v[a]+(v[b]-v[a])*da/(da-db))
    unique=[]
    for q in pts:
     if not any(np.linalg.norm(q-z)<1e-8 for z in unique):unique.append(q)
    if len(unique)>=2:
     a,b=max(((a,b) for a in unique for b in unique),key=lambda ab:np.linalg.norm(ab[0]-ab[1]))
     segs.append({'face_id':fi,'world_mm':[a.tolist(),b.tolist()],'profile_mm':[[float((p-origin)@t),float((p-origin)@n)] for p in [a,b]]})
  out.append({'angle_degrees':angle,'direction':t.tolist(),'plane_normal':pn.tolist(),'plane_point':origin.tolist(),'segments':segs})
 return out
def quad_bowties(v):
 result=[]
 for fi in FULLFS:
  p=F[fi]
  if len(p)!=4:continue
  a=v[p]-v[p].mean(0);_,_,vt=np.linalg.svd(a);q=a@vt[:2].T
  def cross(a,b,c):
   u=b-a;w=c-a;return u[0]*w[1]-u[1]*w[0]
  def hit(a,b,c,d):return cross(a,b,c)*cross(a,b,d)<-1e-12 and cross(c,d,a)*cross(c,d,b)<-1e-12
  if hit(q[0],q[1],q[2],q[3]) or hit(q[1],q[2],q[3],q[0]):result.append(fi)
 return result
def met(v):
 q=(v-origin)@B;cf=np.linalg.lstsq(feat(q[outer]),q[outer,2],rcond=None)[0];res=q[:,2]-feat(q)@cf
 pf=np.linalg.lstsq(feat(q[outer])[:,:3],q[outer,2],rcond=None)[0];pr=q[:,2]-feat(q)[:,:3]@pf
 frozen_cf=np.linalg.lstsq(feat(Q[outer]),Q[outer,2],rcond=None)[0]
 fixed_res=q[:,2]-feat(q)@frozen_cf
 ns=[normal(v,p) for p in F];angles=[]
 for ei in FULLES:
  if len(EF[ei])!=2:continue
  deg=math.degrees(math.acos(float(np.clip(ns[EF[ei][0]]@ns[EF[ei][1]],-1,1))))
  angles.append({'edge_id':ei,'face_ids':EF[ei],'angle_deg':deg})
 return {'max_dihedral_deg':max(a['angle_deg'] for a in angles),'max_dihedral_edge':max(angles,key=lambda a:a['angle_deg']),'edge6676_angle_deg':next(a['angle_deg'] for a in angles if a['edge_id']==6676),'all_local_dihedrals':angles,'quadratic_core_depth_proxy_mm':float(max(0,-res[core].min())),'frozen_baseline_ring_reference_core_depth_proxy_mm':float(max(0,-fixed_res[core].min())),'plane_core_depth_proxy_mm':float(max(0,-pr[core].min())),'core_quadratic_residual_mm':{str(i):float(res[i]) for i in core},'core_curvature_umbrella_mm':{str(i):float((v[i]-v[list(adj[i])].mean(0))@n) for i in core},'quadratic_fit_coefficients':cf.tolist(),'local_face_area_mm2':{str(fi):float(area(v,F[fi])) for fi in FULLFS},'degenerate_native_faces':[fi for fi in FULLFS if area(v,F[fi])<1e-8],'reference_normal_reversed_faces':[fi for fi in FULLFS if ns[fi]@n<0],'projected_quad_bowties':quad_bowties(v),'local_dihedral_RMS_deg':float(np.sqrt(np.mean([a['angle_deg']**2 for a in angles]))),'core_face_area_mm2':sum(area(v,F[fi]) for fi in R['core_faces'])}
metrics={};profiles={};baseline_saved=read(S6/'full_stage6a_requalification_r1/POSED_COORDINATES_R1.json')['positions_world_m']
for label,poses in STATE.items():
 metrics[label]={};profiles[label]={}
 for pose,rawv in poses.items():
  v=np.array(rawv);m=met(v)
  if label=='CURRENT' and pose!='RSSF_RAW':m['saved_fullStage6A_coord_max_delta_mm']=float(np.linalg.norm(v-np.array(baseline_saved[pose])*1000,axis=1).max())
  if label!='CURRENT':
   b=metrics['CURRENT'][pose];m['introduced_degenerate_faces']=sorted(set(m['degenerate_native_faces'])-set(b['degenerate_native_faces']));m['introduced_reference_normal_reversed_faces']=sorted(set(m['reference_normal_reversed_faces'])-set(b['reference_normal_reversed_faces']));m['corrected_preexisting_reference_reversed_faces']=sorted(set(b['reference_normal_reversed_faces'])-set(m['reference_normal_reversed_faces']));m['introduced_projected_quad_bowties']=sorted(set(m['projected_quad_bowties'])-set(b['projected_quad_bowties']))
  metrics[label][pose]=m;profiles[label][pose]=sections(v)
 # Float actual write/influence only. No all-ROI write assumption.
 if label!='CURRENT':
  ids=D['candidates'][label]['write_vertices'];bind=np.array(poses['BIND'])
  for pose in ['IDX_MCP_15','IDX_MCP_30','IDX_MCP_45']:
   v=np.array(poses[pose]);metrics[label][pose]['write_set_pose_displacement_from_bind_max_mm']=float(np.max(np.linalg.norm(v[ids]-bind[ids],axis=1)));metrics[label][pose]['core_pose_displacement_from_bind_max_mm']=float(np.max(np.linalg.norm(v[core]-bind[core],axis=1)))
dump('CANDIDATE_LOCAL_GEOMETRY_METRICS_R1.json',{'method':'Same diagnosis frame and actual0/60/120degree sections; plane/quadratic ring residual proxies, not biological acceptance gates. All candidate incident faces plus diagnosis faces share one comparison domain. Normal direction reversing alone relative to baseline is not inversion: previously folded faces are corrected; new reference-reversed faces and bowties are separately checked.','comparison_face_ids':FULLFS,'comparison_edge_ids':FULLES,'metrics':metrics,'topology_gate':{'vertex_count':len(V),'edge_count':len(E),'face_count':len(F),'all_native_edges_have_2_faces':all(len(f)==2 for f in EF)}})
dump('CANDIDATE_ACTUAL_CROSS_SECTIONS_R1.json',{'frame':frame,'face_domain':R['faces'],'native_quad_fan_triangulation':True,'profiles':profiles})
ext=np.array([p for poses in profiles.values() for ss in poses.values() for sec in ss for seg in sec['segments'] for p in seg['profile_mm']]);limits=((ext[:,0].min()-.5,ext[:,0].max()+.5),(ext[:,1].min()-.5,ext[:,1].max()+.5))
for label,poses in profiles.items():
 for pose,ss in poses.items():
  fig,axs=plt.subplots(1,3,figsize=(12,3.4),layout='constrained')
  for ax,sec in zip(axs,ss):
   ax.add_collection(LineCollection([seg['profile_mm'] for seg in sec['segments']],colors='#237094',lw=1.7));ax.axvline(0,c='#a44',lw=.5);ax.axhline(0,c='#999',lw=.5)
   ax.set(xlim=limits[0],ylim=limits[1],xlabel='Distance in section (mm)',ylabel='Normal height (mm)',title=f"{sec['angle_degrees']} deg");ax.grid(alpha=.15);ax.set_aspect('equal',adjustable='box')
  fig.suptitle(label+' / '+pose+' | measured mesh sections; fixed axes',fontsize=11);fig.savefig(OUT/'renders'/f'{label}_{pose}_SECTIONS.png',dpi=130);plt.close(fig)
fig,axs=plt.subplots(1,3,figsize=(12,3.8),layout='constrained')
for ax,j in zip(axs,range(3)):
 for label,col in [('CURRENT','#9a3934'),('A','#7573a5'),('B','#ba8b20'),('C','#22856f')]:
  ax.add_collection(LineCollection([seg['profile_mm'] for seg in profiles[label]['BIND'][j]['segments']],colors=col,lw=1.5,label=label,alpha=.8))
 ax.set(xlim=limits[0],ylim=limits[1],xlabel='Distance in section (mm)',ylabel='Normal height (mm)',title=f'{[0,60,120][j]} deg');ax.grid(alpha=.15);ax.set_aspect('equal',adjustable='box')
axs[0].legend(fontsize=9);fig.suptitle('CURRENT / A / B / C | same actual mesh section planes; no threshold');fig.savefig(OUT/'renders'/'CANDIDATE_SECTION_OVERLAY.png',dpi=150);plt.close(fig)
print('METRICS',json.dumps({k:{'max':v['BIND']['max_dihedral_deg'],'edge6676':v['BIND']['edge6676_angle_deg'],'depth':v['BIND']['quadratic_core_depth_proxy_mm'],'new_reversed':v['BIND'].get('introduced_reference_normal_reversed_faces',[]),'new_bowtie':v['BIND'].get('introduced_projected_quad_bowties',[])} for k,v in metrics.items()},indent=2))
