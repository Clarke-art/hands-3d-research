import sys
sys.dont_write_bytecode=True
import json,heapq
from pathlib import Path
import numpy as np
out=Path(__file__).resolve().parents[1];root=out.parents[2]
data=json.loads((out/'_tmp/static_mesh_states.json').read_text());state=data['R2_SELECTOR_STATE'];v=np.array(state['vertices_world_m']);f=state['faces'];e=state['edges']
jf=json.loads((root/'production_spec/stage4_blender/stage4c_r2/STAGE4B_R2_JOINT_FRAME.json').read_text())['bones'];oa=json.loads((root/'production_spec/stage4_blender/stage4c_r2/ORIGIN_AUDIT_R2.json').read_text())
segments={'THUMB':['CMC','MCP','IP'],'INDEX':['MCP','PIP','DIP'],'MIDDLE':['MCP','PIP','DIP'],'RING':['MCP','PIP','DIP'],'LITTLE':['MCP','PIP','DIP']}
chains={n:[jf[n+'_'+ss[0]+'_R']['head']]+[jf[n+'_'+s+'_R']['tail'] for s in ss] for n,ss in segments.items()};chains['wrist']=[oa['WRIST_ORIGIN'],jf['WRIST_R']['tail']]
centers=np.array([v[vs].mean(0) for vs in f])
def poly_dist(points,chain):
    ds=[]
    for a,b in zip(chain,chain[1:]):
        a=np.array(a);b=np.array(b);d=b-a;t=np.clip(((points-a)@d)/(d@d),0,1)
        ds.append(np.linalg.norm(points-a-t[:,None]*d,axis=1))
    return np.min(ds,axis=0)
distances={n:poly_dist(centers,ch) for n,ch in chains.items()};names=list(chains);owner=[names[i] for i in np.argmin(np.array(list(distances.values())),axis=0)]
own=[i for i,n in enumerate(owner) if n=='THUMB'];domain=sorted({i for fi in own for i in f[fi]});P=np.array(jf['THUMB_IP_R']['head']);T=np.array(jf['THUMB_TIP_R']['head']);axis=(T-P)/np.linalg.norm(T-P)
candidates=[i for i in domain if (v[i]-P)@axis>0];seed=max(candidates,key=lambda i:np.linalg.norm(v[i]-P))
adj=[[] for _ in v];fadj=[set() for _ in f];ef={}
for a,b in e:
    l=float(np.linalg.norm(v[a]-v[b]));adj[a].append((b,l));adj[b].append((a,l))
for fi,vs in enumerate(f):
    for a,b in zip(vs,vs[1:]+vs[:1]):ef.setdefault(tuple(sorted([a,b])),[]).append(fi)
for fs in ef.values():
    for a in fs:fadj[a].update(set(fs)-{a})
g=np.full(len(v),np.inf);g[seed]=0.;q=[(0.,seed)];pred={}
while q:
    cost,a=heapq.heappop(q)
    if cost>g[a]+1e-15:continue
    for b,l in adj[a]:
        if cost+l<g[b]-1e-15:g[b]=cost+l;pred[b]=a;heapq.heappush(q,(g[b],b))
eligible={fi for fi in own if min(g[a] for a in f[fi])<=.009};near=min(own,key=lambda fi:np.linalg.norm(centers[fi]-v[seed]));eligible.add(near);selected=set();stack=[near]
while stack:
    a=stack.pop()
    if a in selected or a not in eligible:continue
    selected.add(a);stack.extend(fadj[a]-selected)
selverts=sorted({a for fi in selected for a in f[fi]});approved=json.loads((out.parent/'stage5a_r2a/THUMB_DISTAL_CAP_AUDIT.json').read_text())
print('REPRO seed',seed,'faces',sorted(selected),'verts',selverts,'matches',selverts==approved['thumb_cap_vertex_ids'])
rows=[]
for fi in sorted(selected):
    rows.append({'face_id':fi,'vertices':f[fi],'owner':owner[fi],'chain_distances_mm':{n:float(ds[fi]*1000) for n,ds in distances.items()},'vertex_geodesics_mm':{str(i):float(g[i]*1000) for i in f[fi]},'min_geodesic_mm':float(min(g[i] for i in f[fi])*1000)})
path=[2192]
while path[-1]!=seed:path.append(pred[path[-1]])
result={'seed':seed,'candidate_domain_vertex_ids':domain,'distal_candidate_vertex_ids':candidates,'owned_face_ids':own,'selected_face_ids':sorted(selected),'selected_vertex_ids':selverts,'exact_approved_cap_reproduced':selverts==approved['thumb_cap_vertex_ids'] and sorted(selected)==approved['thumb_cap_face_ids'],'seed_to_v2192_path':path[::-1],'v2192_geodesic_mm':float(g[2192]*1000),'selected_faces':rows,'head_IP':P.tolist(),'head_TIP':T.tolist(),'axis':axis.tolist(),'all_face_owners':owner,'all_chain_distances_mm':{n:(ds*1000).tolist() for n,ds in distances.items()}}
(out/'_tmp/selector_reproduction.json').write_text(json.dumps(result),encoding='utf8')
