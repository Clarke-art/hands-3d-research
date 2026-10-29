import sys
sys.dont_write_bytecode=True
from local_data import *
raw=sorted(RAW,key=lambda r:-float(ARC[r['vertex_ids']].mean()))
assert len(raw)==9
def cyclic(r):
    vs=set(r['vertex_ids']);adj={v:set() for v in vs}
    for ei in r['edge_ids']:
        a,b=E[ei];adj[a].add(b);adj[b].add(a)
    assert all(len(x)==2 for x in adj.values())
    start=min(vs);seq=[start];prev=start;now=min(adj[start])
    while now!=start:
        seq.append(now);nxt=next(iter(adj[now]-{prev}));prev,now=now,nxt
    assert len(seq)==len(vs)
    return seq
ordered=[cyclic(raw[0])];pairs=[]
for j,(a,b) in enumerate(zip(raw[:-1],raw[1:])):
    sa=set(a['vertex_ids']);sb=set(b['vertex_ids']);fs=[fi for fi,vs in enumerate(F) if set(vs)<=sa|sb and len(set(vs)&sa)==2 and len(set(vs)&sb)==2]
    edges=[ei for ei,(u,v) in enumerate(E) if (u in sa and v in sb) or (u in sb and v in sa)]
    mp={v:sorted(ADJ[v]&sb) for v in sa};unique=all(len(v)==1 for v in mp.values()) and len({v[0] for v in mp.values()})==len(sb)
    assert unique and len(fs)==16 and len(edges)==16
    order=[mp[v][0] for v in ordered[-1]];assert all(tuple(sorted((u,v))) in EF for u,v in zip(order,order[1:]+order[:1]))
    ordered.append(order)
    pair={'distal_ring':f'R{j:02d}','proximal_ring':f'R{j+1:02d}','face_ids':fs,'longitudinal_edge_ids':edges,'vertex_correspondence':[{'circumferential_index':i,'distal_vertex':v,'proximal_vertex':mp[v][0],'longitudinal_edge_id':EF[tuple(sorted((v,mp[v][0])))],'supporting_face_ids':sorted(set(VF[v])&set(VF[mp[v][0]])&set(fs))} for i,v in enumerate(ordered[-2])],'one_to_one':unique,'strip_face_components':len(components(fs,FADJ)),'closed_quad_annulus':len(fs)==16 and all(len(F[fi])==4 for fi in fs),'angle_matching_used':False}
    pairs.append(pair)
rings=[]
for j,(r,seq) in enumerate(zip(raw,ordered)):
    av=ARC[seq]
    rings.append({'ring_id':f'R{j:02d}','order_distal_to_proximal':j,'vertex_sequence':seq,'edge_sequence':[EF[tuple(sorted((a,b)))] for a,b in zip(seq,seq[1:]+seq[:1])],'circumferential_order_definition':'R00 starts at minimum vertex ID, follows lower-ID first neighbor only as coordinate convention; subsequent rings mapped exclusively through real longitudinal edges and quad face strips. This indexing grants no role.','axial_min_max_mm':[float(av.min()),float(av.max())],'axial_mean_mm':float(av.mean()),'distance_to_IP_signed_arc_mm':[float(x-KNOTS[2]) for x in av],'distance_to_MCP_signed_arc_mm':[float(x-KNOTS[1]) for x in av],'known_shared_vertices':[v for v in seq if v in WEB],'known_shared_indices':[i for i,v in enumerate(seq) if v in WEB],'distal_face_strip':pairs[j-1]['face_ids'] if j else None,'proximal_face_strip':pairs[j]['face_ids'] if j<8 else None,'ring_completeness':{'closed':True,'vertices':len(seq),'edges':len(seq),'all_valence4':all(len(ADJ[v])==4 for v in seq)},'distance_to_IP_euclidean_mm':{str(v):float(np.linalg.norm(V[v]-CHAIN[2])*1000) for v in seq},'distance_to_MCP_euclidean_mm':{str(v):float(np.linalg.norm(V[v]-CHAIN[1])*1000) for v in seq}})
stackverts={v for seq in ordered for v in seq};stackfaces={fi for p in pairs for fi in p['face_ids']}
dump('THUMB_PROXIMAL_RING_STACK_R1.json',{'status':'TOPOLOGY_RESOLVED_ROLE_FRONTIER_UNRESOLVED','ring_count':9,'rings':rings,'vertex_set':pack(stackverts),'face_ids':sorted(stackfaces),'axial_space':'Corrected live THUMB chain arc in frozen RSSF world geometry, mm','MCP_arc_mm':KNOTS[1],'IP_arc_mm':KNOTS[2],'native_RSSF_stable_vertex_identity':J['NATIVE']['edges']==E and J['NATIVE']['faces']==F,'full_ring_exclusive_assumption':False})
dump('THUMB_RING_TO_RING_CORRESPONDENCE.json',{'status':'RESOLVED_TOPOLOGICAL_CORRESPONDENCE','pairs':pairs,'same_mapping_native_RSSF':True,'topology_only':True,'nearest_angle_matching':False,'global_domain_recomputed':False})
# Exact seed-to-seed / frozen-web connections in 1/2-hop context, not region dilation.
seedrows=[]
for v in sorted(SEEDS):
    j=next(j for j,seq in enumerate(ordered) if v in seq);i=ordered[j].index(v);one=grow({v},1)-{v};two=grow({v},2)-one-{v}
    mappings=[]
    for k in [j-1,j+1]:
        if 0<=k<9:mappings.append({'ring':rings[k]['ring_id'],'vertex_id':ordered[k][i],'edge_id':EF[tuple(sorted((v,ordered[k][i])))],'face_ids':sorted(set(VF[v])&set(VF[ordered[k][i]]))})
    local=grow({v},2);connections=[]
    for w in sorted((WEB-{v})&local):
        if w in ADJ[v]:paths=[[v,w]]
        else:paths=[[v,x,w] for x in sorted(ADJ[v]&ADJ[w])]
        connections.append({'frozen_web_vertex':w,'all_minimum_1_or_2_hop_paths':paths,'edge_chain_not_membership_extension':True})
    seedrows.append({'vertex_id':v,'ring_id':rings[j]['ring_id'],'circumferential_index':i,'neighbor_ring_mappings':mappings,'incident_faces':VF[v],'frozen_web_provenance':A['sources']['first_web_membership'],'one_ring_vertex_ids':sorted(one),'two_ring_vertex_ids':sorted(two),'other_frozen_web_connections_within_two_hops':connections,'known_shared':True,'neighbors_auto_shared':False})
dump('FROZEN_WEB_SEED_CONTEXT_AUDIT.json',{'status':'PROVENANCE_VALID','frozen_web21':pack(WEB),'seeds':seedrows,'web21_on_stack':sorted(WEB&stackverts),'other17_outside_stack':sorted(WEB-stackverts),'all_seed_ids_verified':SEEDS<=WEB,'first_web_membership_changed':False})
print(json.dumps({'rings':[(r['ring_id'],r['axial_mean_mm'],r['vertex_sequence'],r['known_shared_indices']) for r in rings],'face_strips':[(p['distal_ring'],len(p['face_ids'])) for p in pairs],'seeds':[(r['vertex_id'],r['circumferential_index']) for r in seedrows]},indent=2))
