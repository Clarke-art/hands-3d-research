from common import *
import numpy as np
from PIL import Image,ImageDraw,ImageFont
top=read(OUT/'NATIVE_TOPOLOGY.json');F=np.array(top['faces'],int);E=np.array(top['edges'],int)
def tx(V,M):return (np.c_[V,np.ones(len(V))]@np.array(M).T)[:,:3]
def sections(V,T,level,ax=1,center=None):
 segments=[]
 for ti,tri in enumerate(T):
  P=V[tri];v=P[:,ax]-level
  if v.min()>0 or v.max()<0:continue
  hits=[]
  for j,k in [(0,1),(1,2),(2,0)]:
   if v[j]*v[k]<0:hits.append(P[j]+(P[k]-P[j])*(-v[j])/(v[k]-v[j]))
   elif abs(v[j])<1e-10:hits.append(P[j])
  if len(hits)>=2:
   H=np.unique(np.round(hits,10),axis=0)
   if len(H)==2:segments.append(H)
 if not segments:return dict(level=level,loops=[])
 P=np.concatenate(segments);U,inv=np.unique(np.round(P,9),axis=0,return_inverse=True);pairs=inv.reshape(-1,2);adj={i:[] for i in range(len(U))}
 for a,b in pairs:
  if a!=b:adj[int(a)].append(int(b));adj[int(b)].append(int(a))
 loops=[];seen=set()
 for start in adj:
  if start in seen:continue
  chain=[start];prev=None;cur=start
  for _ in range(len(U)+2):
   nxt=[i for i in adj[cur] if i!=prev]
   if not nxt:break
   new=nxt[0]
   if new==start:chain.append(start);break
   if new in chain:break
   chain.append(new);prev,cur=cur,new
  seen.update(chain)
  if len(chain)>3 and chain[-1]==chain[0]:
   pts=U[chain[:-1]];axes=[i for i in range(3) if i!=ax];xy=pts[:,axes];area=.5*abs(np.sum(xy[:,0]*np.roll(xy[:,1],-1)-xy[:,1]*np.roll(xy[:,0],-1)))
   loops.append(dict(points_m=pts,area_mm2=float(area*1e6),center_m=pts.mean(0),min_m=pts.min(0),max_m=pts.max(0)))
 return dict(level=level,loops=loops,segments_m=segments)
def face_normals(V):
 P=V[F];N=np.cross(P[:,1]-P[:,0],P[:,2]-P[:,0])+np.cross(P[:,2]-P[:,0],P[:,3]-P[:,0]);N/=np.maximum(1e-20,np.linalg.norm(N,axis=1))[:,None];return N
edgefaces={tuple(sorted(e)):[] for e in E}
for i,face in enumerate(F):
 for j in range(len(face)):edgefaces[tuple(sorted((int(face[j]),int(face[(j+1)%len(face)]))))].append(i)
result={};font=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
for identity in ['ORIGINAL','REJECTED_GEOMETRY_PASS']:
 meta=read(OUT/(identity+'_SNAPSHOT.json'));z=np.load(OUT/(identity+'_SNAPSHOT.npz'));names=meta['bone_names'];D=z['D'];world=z['V'];RV=z['RV'];can=np.array(meta['canonical_from_rig']);mw=np.array(meta['mesh_world']);rw=np.array(meta['rig_world']);mesh_to_can=<REDACTED_EMAIL>(rw)@mw
 wr=D[names.index('WRIST_R')];mc=D[names.index('INDEX_MCP_R')]
 Cw=tx(tx(world,np.linalg.inv(wr)),mesh_to_can);Cm=tx(tx(world,np.linalg.inv(mc)),mesh_to_can)
 rest_mcp=np.array(meta['joints']['INDEX_MCP_R']['rest']);mesh_to_bone=np.linalg.inv(rest_mcp)@np.linalg.inv(rw)@mw
 raw_local=tx(RV,mesh_to_bone);posed_local=tx(tx(world,np.linalg.inv(mc)),mesh_to_bone)
 A=np.array(meta['rois']['A']['vertices']);AS=np.array(meta['rois']['A_SHAFT']['vertices']);B=np.array(meta['rois']['B']['vertices']);W=z['W'];AL=z['ALONG'];R=z['RADIUS'];L=meta['index_proximal_length_mm']/1000
 rawN=face_normals(z['C']);poseN=face_normals(Cw);edge_rows=[]
 for e,ff in edgefaces.items():
  if len(ff)!=2 or not all(v in set(A) for v in e):continue
  a,b=ff;rawang=float(np.degrees(np.arccos(np.clip(rawN[a]@rawN[b],-1,1))));posang=float(np.degrees(np.arccos(np.clip(poseN[a]@poseN[b],-1,1))));weightL1=float(abs(W[e[0]]-W[e[1]]).sum())
  edge_rows.append(dict(edge=e,faces=ff,mean_fraction=float(AL[list(e)].mean()/L),raw_dihedral_deg=rawang,posed_dihedral_deg=posang,weight_vector_L1=weightL1))
 core_edges=[r for r in edge_rows if .2<=r['mean_fraction']<=.8]
 stations=[];section_profiles=[]
 for f in [.1,.2,.3,.4,.5,.6,.7,.8,.9]:
  band=np.flatnonzero((abs(AL/L-f)<.075)&(R<.012));weightmean={names[i]:float(W[band,i].mean()) for i in range(len(names)) if len(band) and W[band,i].max()>.01}
  row=dict(fraction=f,vertices=band,mean_weights=weightmean,raw=None,posed=None)
  for label,VV in [('raw',raw_local),('posed',posed_local)]:
   sec=sections(VV,z['T'],f*L)
   nearby=[q for q in sec['loops'] if np.linalg.norm(q['center_m'][[0,2]])<.012 and q['area_mm2']<600]
   chosen=min(nearby,key=lambda q:np.linalg.norm(q['center_m'][[0,2]])) if nearby else None
   row[label]=chosen;section_profiles.append(dict(label=label,fraction=f,section=sec))
  stations.append(row)
 # Per-vertex LBS displacement decomposition relative to a rigid MCP or wrist.
 contribA={};contribB={}
 for j,name in enumerate(names):
  VA=tx(RV,D[j])-tx(RV,mc);VB=tx(RV,D[j])-tx(RV,wr)
  contribA[name]=float(np.linalg.norm(W[A,j,None]*VA[A],axis=1).max()*1000)
  contribB[name]=float(np.linalg.norm(W[B,j,None]*VB[B],axis=1).max()*1000)
 # Actual web cross sections in wrist-aligned canonical frame; entire contour,
 # not a claim of anatomical soft-tissue volume.
 websecs=[]
 for y in [.070,.090,.110]:websecs.append(dict(y_m=y,raw=sections(z['C'],z['T'],y),posed=sections(Cw,z['T'],y)))
 np.savez_compressed(OUT/(identity+'_ALIGNED.npz'),C_WRIST=Cw,C_MCP=Cm,RAW_LOCAL=raw_local,POSED_LOCAL=posed_local,RAW_RIGID_MCP=tx(RV,mc),RAW_RIGID_WRIST=tx(RV,wr))
 result[identity]=dict(stations=stations,section_profiles=section_profiles,A_native_edges=edge_rows,A_midshaft_top_dihedrals=sorted(core_edges,key=lambda r:-r['raw_dihedral_deg'])[:12],A_lbs_difference_from_rigid_mcp_max_mm=float(np.linalg.norm((world-tx(RV,mc))[A],axis=1).max()*1000),A_shaft_lbs_difference_from_rigid_mcp_max_mm=float(np.linalg.norm((world-tx(RV,mc))[AS],axis=1).max()*1000),B_difference_from_rigid_wrist_max_mm=float(np.linalg.norm((world-tx(RV,wr))[B],axis=1).max()*1000),A_weighted_contributions_max_mm=contribA,B_weighted_contributions_max_mm=contribB,web_sections=websecs,ROIs=meta['rois'])
 print(identity,'A midshaft raw edges',[(r['edge'],round(r['mean_fraction'],3),round(r['raw_dihedral_deg'],2),round(r['posed_dihedral_deg'],2)) for r in result[identity]['A_midshaft_top_dihedrals'][:5]],flush=True)
 print('SECTIONS',[(round(r['fraction'],1),None if r['raw'] is None else round(r['raw']['area_mm2'],2),None if r['posed'] is None else round(r['posed']['area_mm2'],2),r['mean_weights']) for r in stations],flush=True)
save('ROI_GEOMETRY_AND_WEIGHT_ANALYSIS.json',result)
protection('ANALYSIS_INPUT_RECEIPT.json')
