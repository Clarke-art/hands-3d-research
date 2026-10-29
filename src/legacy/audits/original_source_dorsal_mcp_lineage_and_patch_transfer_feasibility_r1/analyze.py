import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np,math
S=read(OUT/'RAW_SOURCE_GEOMETRY.json')['stages'];T=read(OUT/'HISTORICAL_OPERATION_RAM_REPLAY.json');R=read(OLD/'DORSAL_MCP_DENT_ROI_R1.json');G=read(OLD/'DENT_RENDER_GEOMETRY_R1.json')
base=S['OFFICIAL_BASE'];l1=S['OFFICIAL_L1'];A=T['final_ancestry']
adj=[[] for _ in l1['local_m']]
for a,b in l1['edges']:adj[a].append(b);adj[b].append(a)
baseedge={frozenset(e):i for i,e in enumerate(base['edges'])};ancestry={};nv=len(base['local_m'])
for i in range(len(adj)):
 if i<nv:ancestry[i]={'kind':'BASE_VERTEX','vertex':i}
 else:
  originals=[j for j in adj[i] if j<nv]
  if len(originals)==2:
   assert frozenset(originals) in baseedge
   ancestry[i]={'kind':'BASE_EDGE_CHILD','edge':baseedge[frozenset(originals)],'endpoints':originals}
for i in range(nv,len(adj)):
 if i in ancestry:continue
 endpoints=set(j for e in adj[i] for j in ancestry[e]['endpoints'])
 matches=[f for f,p in enumerate(base['faces']) if set(p)==endpoints]
 assert len(matches)==1
 ancestry[i]={'kind':'BASE_FACE_CHILD','face':matches[0],'vertices':base['faces'][matches[0]]}
# Validate the entire subdivision graph against base face/corner incidence.
Ledge={e['edge']:i for i,e in ancestry.items() if e['kind']=='BASE_EDGE_CHILD'}
Lface={e['face']:i for i,e in ancestry.items() if e['kind']=='BASE_FACE_CHILD'}
def cycle(p):return min(tuple(p[k:]+p[:k]) for k in range(len(p)))
expected=[]
for fi,p in enumerate(base['faces']):
 for k,v in enumerate(p):expected.append(cycle([v,Ledge[baseedge[frozenset([v,p[(k+1)%len(p)]])]],Lface[fi],Ledge[baseedge[frozenset([p[k-1],v])]]]))
assert set(expected)=={cycle(p) for p in l1['faces']}
mapping=read(OLD/'EARLIER_STAGE4A_BASE_LOCAL_IDENTITY_R1.json')['current_to_native_vertex_ids']
core=R['core_vertices'];ids=R['vertices'];outer=R['2_ring']
rows={str(i):{'stage4a_base_vertex':mapping[str(i)],'L1_parent_weights':A[mapping[str(i)]],'base_ancestry':[{'L1_vertex':int(k),'weight':w,**ancestry[int(k)]} for k,w in A[mapping[str(i)]].items()]} for i in ids}
baseids=set()
for r in rows.values():
 for a in r['base_ancestry']:
  baseids.update([a['vertex']] if a['kind']=='BASE_VERTEX' else a.get('endpoints',a.get('vertices',[])))
l1ids=sorted({int(k) for r in rows.values() for k in r['L1_parent_weights']})
basefs=[i for i,p in enumerate(base['faces']) if set(p)&baseids];baseids=sorted({v for i in basefs for v in base['faces'][i]})
l1fs=[i for i,p in enumerate(l1['faces']) if set(p)&set(l1ids)];l1ids=sorted({v for i in l1fs for v in l1['faces'][i]})
# One rigid diagnostic transform from frozen exact ROI correspondence, also used for official sources.
ref=np.array(S['R2_PRODUCTION']['canonical_world_m'])*1000
av=np.array(S['STAGE4A_R2']['canonical_world_m'])*1000
aa=av[outer];bb=ref[outer];ac=aa.mean(0);bc=bb.mean(0);u,sv,vt=np.linalg.svd((aa-ac).T@(bb-bc));rot=u@vt
assert np.linalg.det(rot)>0
trans=bc-ac@rot
frame=G['frame'];origin=np.array(frame['origin_world_mm']);x=np.array(frame['x']);y=np.array(frame['y']);n=np.array(frame['outward']);B=np.column_stack([x,y,n])
display={};metrics={}
def normal(v,p):
 q=v[p];z=sum((np.cross(q[k],q[(k+1)%len(q)]) for k in range(len(q))),np.zeros(3));return z/max(np.linalg.norm(z),1e-15)
def sections(v,F,fs):
 out={}
 for ang in [0,60,120]:
  d=x*math.cos(math.radians(ang))+y*math.sin(math.radians(ang));pn=np.cross(n,d);segs=[]
  for fi in fs:
   p=F[fi]
   for k in range(1,len(p)-1):
    tri=[p[0],p[k],p[k+1]];pts=[]
    for a,b in zip(tri,tri[1:]+tri[:1]):
     da=(v[a]-origin)@pn;db=(v[b]-origin)@pn
     if abs(da)<1e-8:pts.append(v[a])
     if da*db<0:pts.append(v[a]+(v[b]-v[a])*da/(da-db))
    if len(pts)>=2:segs.append({'face':fi,'world_mm':[pts[0].tolist(),pts[1].tolist()],'profile_mm':[[float((p-origin)@d),float((p-origin)@n)] for p in pts[:2]]})
  out[str(ang)]=segs
 return out
def sampled_profile(q,F,fs):
 grid=np.array([(a,b) for a in np.linspace(-9,9,37) for b in np.linspace(-9,9,37)]);values=[[] for _ in grid]
 for fi in fs:
  p=F[fi]
  for k in range(1,len(p)-1):
   tri=q[[p[0],p[k],p[k+1]]];m=np.column_stack([tri[1,:2]-tri[0,:2],tri[2,:2]-tri[0,:2]])
   if abs(np.linalg.det(m))<1e-10:continue
   uv=(grid-tri[0,:2])@np.linalg.inv(m).T
   for j in np.where((uv[:,0]>=-1e-7)&(uv[:,1]>=-1e-7)&(uv.sum(1)<=1+1e-7))[0]:
    values[j].append(float(tri[0,2]+uv[j]@(tri[1:,2]-tri[0,2])))
 return [{'xy_mm':p.tolist(),'outward_mm':max(v) if v else None,'layer_count':len(set(round(z,6) for z in v))} for p,v in zip(grid,values)]
for label in ['OFFICIAL_BASE','OFFICIAL_L1','STAGE2_L1','STAGE4A_R2_BASE','STAGE4A_R2','STAGE4B_RSSF','STAGE4C_R2','R2_PRODUCTION']:
 s=S[label];v=np.array(s['canonical_world_m'])*1000
 if label in ['OFFICIAL_BASE','OFFICIAL_L1','STAGE2_L1','STAGE4A_R2_BASE','STAGE4A_R2']:v=v@rot+trans
 F=s['faces'];roiids=baseids if label=='OFFICIAL_BASE' else l1ids if label in ['OFFICIAL_L1','STAGE2_L1'] else ids
 fs=basefs if label=='OFFICIAL_BASE' else l1fs if label in ['OFFICIAL_L1','STAGE2_L1'] else R['faces']
 q=(v-origin)@B;fn={i:normal(v,F[i]) for i in fs};ef={}
 for fi in fs:
  p=F[fi]
  for a,b in zip(p,p[1:]+p[:1]):ef.setdefault(tuple(sorted([a,b])),[]).append(fi)
 dih=[{'vertices':list(e),'faces':f,'degrees':math.degrees(math.acos(float(np.clip(fn[f[0]]@fn[f[1]],-1,1))))} for e,f in ef.items() if len(f)==2]
 samples=sampled_profile(q,F,fs);valid=[z for z in samples if z['outward_mm'] is not None];ring=[z for z in valid if 6<=np.linalg.norm(z['xy_mm'])<=9];inside=[z for z in valid if np.linalg.norm(z['xy_mm'])<=4]
 def features(p):a,b=p;return [1,a,b,a*a,a*b,b*b]
 coef=np.linalg.lstsq(np.array([features(z['xy_mm']) for z in ring]),[z['outward_mm'] for z in ring],rcond=None)[0]
 residual=[{'xy_mm':z['xy_mm'],'residual_mm':float(z['outward_mm']-np.array(features(z['xy_mm']))@coef)} for z in inside]
 umbrella=[]
 ad={i:[] for i in roiids}
 for a,b in s['edges']:
  if a in ad:ad[a].append(b)
  if b in ad:ad[b].append(a)
 for i in roiids:
  if ad[i]:umbrella.append({'vertex':i,'signed_normal_umbrella_mm':float((v[i]-v[ad[i]].mean(0))@n)})
 metrics[label]={'common_grid_valley_depth_proxy_mm':max(0.,-min(z['residual_mm'] for z in residual)),'common_grid_ring_quadratic':coef.tolist(),'sampled_profiles':samples,'core_residuals':residual,'max_local_dihedral_deg':max(z['degrees'] for z in dih),'edge_facet_normal_progression':dih,'curvature_umbrella_proxy':umbrella,'cross_sections':sections(v,F,fs),'silhouette_profile':{'camera_direction':R['camera']['direction'],'ROI_projected_vertices_mm':q[roiids].tolist(),'native_edges':[list(e) for e in ef]},'physical_ROI_selection':'Exact subdivision graph ancestry and historical split edge interpolation; no screenshot inference','comparative_only':True,'anatomical_threshold':None}
 display[label]={'world_mm':v.tolist(),'faces':F,'smooth':s['smooth'],'roi_vertices':roiids,'roi_faces':fs,'sections':metrics[label]['cross_sections']}
 print(label,'depth',round(metrics[label]['common_grid_valley_depth_proxy_mm'],4),'dihedral',round(metrics[label]['max_local_dihedral_deg'],3))
dump('DONOR_TO_CURRENT_TOPOLOGY_CORRESPONDENCE_R1.json',{'status':'PASS_EXACT_ANCESTRY_FOR_FROZEN_ROI','multires_graph_validation':'Every L1 oriented child face cycle equals subdivision of the recorded base face/corner incidence','L1_to_base_ancestry':{str(i):a for i,a in ancestry.items()},'current_ROI_to_source':rows,'RAM_replay_exact_historical_match':True,'current_center_955_base_ancestry':ancestry[955],'new_support_vertices':'Actual historical parent edge weights before plane projection, not nearest surface','rigid_display_registration':{'rotation_row':rot.tolist(),'translation_mm':trans.tolist(),'scale':1,'outer_RMS_mm':float(np.sqrt(np.mean(np.sum((aa@rot+trans-bb)**2,axis=1))))},'mapping_scope':'Frozen Human ROI; no claim for remote CMC engineering vertices','projection_used_for_correspondence':False})
dump('DENT_SOURCE_LINEAGE_METRICS_R1.json',{'method':'Matched physical 0.5mm tangent-plane sampling; radius<=4mm core and 6..9mm fit ring are comparative sampling windows, not transfer scope or anatomy gates. Native facets, actual triangle sections, signed umbrella, local silhouette. Different tessellations retain native metrics.','frame':frame,'stages':metrics})
dump('REVIEW_GEOMETRY.json',{'frame':frame,'stages':display,'camera':R['camera']})
receipt=read(ROOT/'production_spec/stage2_bootstrap/BOOTSTRAP_RECEIPT.json')
dump('SOURCE_GEOMETRY_LINEAGE_R1.json',{'stages':{k:{'counts':s['counts'],'input':s['input'],'modifiers':s['modifiers']} for k,s in S.items()},'bootstrap_base_coordinate_topology_UV_parity':all(S['OFFICIAL_BASE'][k]==S['STAGE2_BASE'][k] for k in ['local_m','faces','edges','uv']),'bootstrap_evaluated_L1_exact_parity':all(S['OFFICIAL_L1'][k]==S['STAGE2_L1'][k] for k in ['local_m','faces','edges','uv']),'receipt_source_hash_verified':receipt['source_parent_sha256']==S['OFFICIAL_BASE']['input']['sha256'],'receipt_bootstrap_hash_verified':receipt['working_copy_sha256']==S['STAGE2_BASE']['input']['sha256'],'lineage':['OFFICIAL_BASE + stored official Multires L1 displacement','STAGE2 exact isolated base + unapplied Multires L1','STAGE4A_R2_BASE: bake actual official Multires L1; CON9 Rx180 mesh-data rotation; four CON1 subdivide-and-plane-project loops; CON3 pole relocation with neighbor smoothing','STAGE4A_R2: CMC engineering; frozen ROI exact native geometry identity','STAGE4B_RSSF: baked temporary rig deformation, topology frozen','STAGE4C_R2: UV/nail/material/origin finalization','R2 production: rig/weights rebuild; raw surface inherited'],'geometry_layer_selected_at_Stage2':'Neither baked base nor baked L1: base cage plus preserved enabled Multires L1 modifier','geometry_layer_selected_at_Stage4A':'Actual evaluated official L1 baked into mesh','historical_RAM_replay_exact_final_match':True})
