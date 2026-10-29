from pathlib import Path
import sys,json,hashlib,heapq,ast
import numpy as np
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2];S4=ROOT/'production_spec/stage4_blender';S5=OUT.parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def enc(v):
 if isinstance(v,np.ndarray):return v.tolist()
 if isinstance(v,np.generic):return v.item()
 raise TypeError(type(v))
def dump(n,d):(OUT/n).write_text(json.dumps(d,default=enc,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def unit(v):return v/np.linalg.norm(v)
def angle(a,b):return float(np.degrees(np.arccos(np.clip(unit(a)@unit(b),-1,1))))
D=read(OUT/'RAW_READ_ONLY_GEOMETRY_AND_BONES.json');A=read(S5/'stage5b_r1e_human_cap_authority_freeze_r1/THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1.json')
N=np.array(D['NATIVE']['vertices_world_m']);V=np.array(D['RSSF']['vertices_world_m']);F=D['RSSF']['faces'];E=D['RSSF']['edges']
assert D['RSSF']['sha256']=='fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7'
assert D['NATIVE']['sha256']==A['native_geometry_hash']
for k in ['NATIVE','R2','R2A']:assert D[k]['edges']==E and D[k]['faces']==F
assert np.max(np.abs(V-np.array(D['R2A']['vertices_world_m'])))==0
part=read(S5/'stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1/_tmp/native_independent_partition.json')
ids=np.array([i for i,l in enumerate(part['labels']) if l=='thumb']);root=part['thumb_root_vertex']
assert part['tip_seeds']['thumb']==284
def dij(v,seed):
 adj=[[] for _ in v]
 for a,b in E:
  l=float(np.linalg.norm(v[a]-v[b]));adj[a].append((b,l));adj[b].append((a,l))
 ds=np.full(len(v),np.inf);ds[seed]=0;q=[(0.,seed)]
 while q:
  c,a=heapq.heappop(q)
  if c>ds[a]+1e-15:continue
  for b,l in adj[a]:
   if c+l<ds[b]-1e-16:ds[b]=c+l;heapq.heappush(q,(c+l,b))
 return ds
# Reconfirm branch partition from native tip identities; this is NOT an R2/R3 ownership run.
names=list(part['tip_seeds']);native_ds={n:dij(N,s) for n,s in part['tip_seeds'].items()}
labels=[names[i] for i in np.argmin(np.array([native_ds[n] for n in names]),axis=0)]
assert labels==part['labels']
def locator(v,ds):
 L=ds[root];band=ids[(ds[ids]>=.25*L)&(ds[ids]<=.55*L)];ax=unit(v[284]-v[band].mean(0));anchor=v[284]+ax*((v[root]-v[284])@ax);length=float((v[284]-anchor)@ax)
 def section(frac,half=.003):
  sel=ids[np.abs((v[ids]-anchor)@ax-length*frac)<=half]
  if len(sel)<6:sel=ids[np.abs((v[ids]-anchor)@ax-length*frac)<=half*3]
  return {'fraction':frac,'half_width_mm':half*1000,'vertex_ids':sel,'center_world_m':v[sel].mean(0)}
 return {'axis':ax,'anchor_world_m':anchor,'axial_length_mm':length*1000,'functional_length_mm':L*1000,'axis_band_vertex_ids':band,'IP':section(.75),'MCP':section(.44),'sections':[section(float(f)) for f in np.linspace(.55,.95,9)],'sensitivity':[section(.75,h) for h in [.002,.0025,.003,.0035,.004]]}
native=locator(N,native_ds['thumb']);rssf=locator(V,dij(V,284))
H=np.array(D['R2A']['bones']['THUMB_IP_R']['head_world_m']);TIP=V[284];axis=unit(TIP-H)
nail=read(S4/'stage4c_r2/NAIL_AUDIT_R2.json')['per_digit_faces']['thumb'];nids=sorted({v for fi in nail for v in F[fi]});norm=np.array(D['RSSF']['face_normals_world'])[nail]
dorsal=unit(norm.sum(0));z=unit(dorsal-axis*(dorsal@axis));x=unit(np.cross(axis,z));frame=np.column_stack([x,axis,z])
nc=V[nids].mean(0);_,ns,nvt=np.linalg.svd(V[nids]-nc);plane=nvt[-1]
if plane@dorsal<0:plane=-plane
# Native radial cue = away from native index branch, projected into independent section.
na=unit(N[284]-native['IP']['center_world_m']);nn=unit(np.array(D['NATIVE']['face_normals_world'])[nail].sum(0));nx=unit(np.cross(na,unit(nn-na*(nn@na))))
away=N[284]-N[part['tip_seeds']['index']];radial_sign=1 if nx@away>0 else -1
ringids=np.array(native['IP']['vertex_ids']);offset=(N[ringids]-N[ringids].mean(0))@(nx*radial_sign)
radial_ids=ringids[offset>0];ulnar_ids=ringids[offset<0];radial_cue=unit(V[radial_ids].mean(0)-V[ulnar_ids].mean(0))
# Execute only the approved topology walk definitions, never the old script body/selectors.
source=S4/'scripts/stage4a_t01_edgeloop.py';tree=ast.parse(source.read_text());funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['vcycle','opposite_at','walk']]
incident={i:[] for i in range(len(V))};edge_v={i:tuple(e) for i,e in enumerate(E)};edge_key={tuple(sorted(e)):i for i,e in enumerate(E)};link={}
for i,(a,b) in enumerate(E):incident[a].append(i);incident[b].append(i)
for vs in F:
 for j,v in enumerate(vs):
  ep=edge_key[tuple(sorted([vs[j-1],v]))];en=edge_key[tuple(sorted([v,vs[(j+1)%len(vs)]]))]
  link.setdefault((v,ep),set()).add(en);link.setdefault((v,en),set()).add(ep)
env={'incident':incident,'edge_v':edge_v,'link':link,'VCYC':{}};exec(compile(ast.Module(body=funcs,type_ignores=[]),str(source),'exec'),env)
loops=[];seen=set();axis0=rssf['axis'];anchor=rssf['anchor_world_m'];target=rssf['axial_length_mm']*.75
for ei,(a,b) in enumerate(E):
 f,sf,vf,kf=env['walk'](ei,a);bw,sb,vb,kb=env['walk'](ei,b);edges=sorted(set(f+bw));key=tuple(edges)
 if key in seen:continue
 seen.add(key);vs=sorted({v for e in edges for v in E[e]})
 if len(edges)<8 or len(set(vs)&set(ids))/len(vs)<.55:continue
 points=V[vs];c=points.mean(0);av=(points-anchor)@axis0*1000;align=np.mean([abs(unit(V[E[e][1]]-V[E[e][0]])@axis0) for e in edges])
 u=unit(np.cross(axis0,dorsal));w=np.cross(axis0,u);theta=np.sort(np.arctan2((points-c)@w,(points-c)@u));coverage=1-np.max(np.diff(np.r_[theta,theta[0]+2*np.pi]))/(2*np.pi)
 if align>=.45 or coverage<.60 or abs(av.mean()-target)>8:continue
 loops.append({'edge_ids':edges,'vertex_ids':vs,'closed':sf==sb=='closed','stops':[{'status':sf,'vertex':vf,'valence':kf},{'status':sb,'vertex':vb,'valence':kb}],'axis_alignment':align,'coverage':coverage,'center_world_m':c,'axial_mm':av.mean(),'axial_span_mm':np.ptp(av),'distance_to_current_head_mm':np.linalg.norm(c-H)*1000})
loops.sort(key=lambda r:r['axial_mm'])
cap=V[A['vertex_ids']];ct=cap.mean(0)
candidate={'THUMB_IP_R':{'head_world_m':H,'tail_world_m':TIP,'frame_XYZ':frame},'THUMB_TIP_R':{'head_world_m':TIP,'tail_world_m':TIP+.3*(TIP-H),'frame_XYZ':frame}}
out={'mapping':{'method':'identity i -> i; exact entire edge endpoint and ordered polygon arrays equal NATIVE/RSSF/R2/R2A; world XYZ read separately from each immutable mesh','native_v284_world_m':N[284],'rssf_v284_world_m':TIP,'displacement_mm':np.linalg.norm(TIP-N[284])*1000,'rigid_transform_used':False,'native_to_RSSF':'nonrigid baked repose; no single global affine transform claimed'},
 'native_locator':native,'RSSF_locator':rssf,'native_IP_section_mapped_center_world_m':V[native['IP']['vertex_ids']].mean(0),'IP_current_head_world_m':H,'IP_locator_delta_mm':np.linalg.norm(H-rssf['IP']['center_world_m'])*1000,
 'native_domain_vertex_ids':ids,'root_vertex':root,'IP_true_edge_loops':loops,
 'dorsal_cue':dorsal,'nail_face_ids':nail,'nail_vertex_ids':nids,'nail_plane':{'center_world_m':nc,'normal':plane,'singular_values_m':ns,'normal_difference_deg':angle(plane,dorsal),'axis_to_plane_deg':90-angle(axis,plane)},
 'radial_cue':radial_cue,'radial_vertex_ids':radial_ids,'ulnar_vertex_ids':ulnar_ids,'frame_X_points':('RADIAL' if x@radial_cue>0 else 'ULNAR'),'radial_evidence':'native anatomical away-from-index sign + native IP surface half-ring IDs mapped unchanged to RSSF; qualitative cue, not new region authority',
 'candidate':candidate,'cap_envelope':{'surface_center_world_m':ct,'longitudinal_range_relative_IP_mm':[(cap-H)@axis*1000][0][[np.argmin((cap-H)@axis),np.argmax((cap-H)@axis)]],'centroid_used_as_endpoint':False,'membership_authority_only':True},
 'nail_projection_norm':np.linalg.norm(dorsal-axis*(dorsal@axis)),'geometric_axis_independent_locator_to_tip':unit(TIP-rssf['IP']['center_world_m'])}
dump('GEOMETRIC_EVIDENCE_COMPUTATION.json',out)
print('IP locator delta mm',out['IP_locator_delta_mm'],'loops',[(l['closed'],len(l['edge_ids']),l['distance_to_current_head_mm']) for l in loops])
print('sensitivity delta mm',[float(np.linalg.norm(H[slice(None)]-r['center_world_m'])*1000) for r in rssf['sensitivity']]);print('tip delta mm',np.linalg.norm(TIP-np.array(D['R2A']['bones']['THUMB_TIP_R']['head_world_m']))*1000)
print('nail axis projection',out['nail_projection_norm'],'frame X',out['frame_X_points'])
