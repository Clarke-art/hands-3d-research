import sys,heapq,math
sys.dont_write_bytecode=True
from data import *
T=read(OUT/'RAW_LOCAL_COLUMN_TRACES.json')
q=src('native_thumb_anchor_evidence')['native_direction_support'];NC=np.array([q['axis_anchor_world_m']]+[q['joint_world_m'][k] for k in ['MCP','IP','TIP']])
NI=np.array(src('native_index_anchor_evidence')['native_direction_support']['joint_world_m']['MCP'])
STATES={'NATIVE':(N,NC,NI),'RSSF':(V,CHAIN,INDEX_CHAIN[0])}
def angle(a,b):return float(np.degrees(np.arccos(np.clip(unit(a)@unit(b),-1,1))))
def normals(P):
    return np.array([unit(np.cross(P[vs],np.roll(P[vs],-1,axis=0)).sum(0)) for vs in F])
def mindist(P,ids,refs):return float(np.linalg.norm(P[ids,None,:]-P[sorted(refs)][None,:,:],axis=2).min()*1000)
def nearest_axis(C,x):
    out=[]
    for a,b in zip(C[:-1],C[1:]):
        t=np.clip((x-a)@(b-a)/np.linalg.norm(b-a)**2,0,1);foot=a+t*(b-a);out.append((np.linalg.norm(x-foot),foot,unit(b-a)))
    return min(out,key=lambda t:t[0])[1:]
def angular_width(P,ids,C):
    center=P[ids].mean(0);foot,axis=nearest_axis(C,center);off=P[ids]-foot;z=unit(off[0]-axis*(off[0]@axis));x=np.cross(axis,z)
    aa=sorted((np.degrees(np.arctan2(off@x,off@z))%360).tolist());return float(360-max(np.diff(aa+[aa[0]+360])))
def local_seed_metric(P):
    # User-requested diagnostic on already traced faces only. Never a R3 field/domain.
    fs=set(F3['shared_face_ids'])|{fi for r in T['distal_non_nail']['rows'] for fi in r['face_ids']};ids={v for fi in fs for v in F[fi]};es={e for fi in fs for e in fedges(fi)}
    adj={v:[] for v in ids}
    for ei in es:
        a,b=E[ei];w=float(np.linalg.norm(P[a]-P[b])*1000);adj[a].append((b,w));adj[b].append((a,w))
    d={v:math.inf for v in ids};pq=[]
    for v in SEEDS:d[v]=0;heapq.heappush(pq,(0,v))
    while pq:
        cost,v=heapq.heappop(pq)
        if cost!=d[v]:continue
        for w,l in adj[v]:
            if cost+l<d[w]:d[w]=cost+l;heapq.heappush(pq,(d[w],w))
    assert all(math.isfinite(x) for x in d.values())
    return d,{'vertex_count':len(ids),'face_count':len(fs),'edge_count':len(es),'source_ids':sorted(SEEDS),'scope':'Diagnostic geodesic restricted to original edges of fixed F3 plus traced distal rows; no global shortest path; no ownership solve'}
def profile(rows,state,seedmetric=False):
    P,C,I=STATES[state];FN=normals(P);arc,rad,knots=project(C,P);result=[];prev=None;sd,scope=local_seed_metric(P) if seedmetric else (None,None)
    palmcue=P[794]-P[284] # proximal structural direction, not thenar ownership
    for r in rows:
        ids=r['vertex_ids'];tip=r['outgoing_vertex_ids'];ins=sorted({v for ei in r['incoming_edge_ids'] for v in E[ei]});ctr=P[ids].mean(0);outctr=P[tip].mean(0);tangent=unit(outctr-P[ins].mean(0));normal=unit(FN[r['face_ids']].sum(0));foot,axis=nearest_axis(C,ctr)
        wdir=unit(P[sorted(WEB-SEEDS)].mean(0)-ctr);idir=unit(I-ctr);naildir=unit(P[sorted(NAILS['thumb'])].mean(0)-ctr);cmcdir=unit(P[794]-ctr)
        ed={e for fi in r['face_ids'] for e in fedges(fi)};dih=[{'edge_id':e,'face_ids':EFS[e],'dihedral_normal_turn_deg':angle(FN[EFS[e][0]],FN[EFS[e][1]])} for e in sorted(ed) if len(EFS[e])==2]
        rr={**r,'coordinate_state':state,'mean_arc_mm':float(arc[tip].mean()),'outgoing_arc_min_max_mm':[float(arc[tip].min()),float(arc[tip].max())],'signed_arc_to_IP_mm':float(arc[tip].mean()-knots[2]),'signed_arc_to_MCP_mm':float(arc[tip].mean()-knots[1]),'distance_to_v284_min_mm':mindist(P,ids,{284}),'distance_to_cap37_min_vertex_mm':mindist(P,ids,CAP),'distance_to_nail_min_vertex_mm':mindist(P,ids,NAILS['thumb']),'mean_normal':normal.tolist(),'normal_turn_from_previous_row_deg':None if prev is None else angle(normal,prev),'dihedral_profile':dih,'mean_edge_dihedral_deg':float(np.mean([v['dihedral_normal_turn_deg'] for v in dih])),'sector_angular_width_deg':angular_width(P,tip,C),'frontier_separation_mm':float(np.linalg.norm(P[tip].max(0)-P[tip].min(0))*1000),'local_tube_radius_proxy_mm':float(rad[tip].mean()),'radius_proxy_definition':'Mean outgoing vertex distance to own-state thumb centerline; descriptor only, not tube-radius authority or sampling','local_tangent':tangent.tolist(),'tangent_dot_thumb_axis':float(tangent@axis),'normal_dot_web_context':float(normal@wdir),'normal_dot_index_context':float(normal@idir),'normal_dot_nail_context':float(normal@naildir),'normal_dot_CMC_context':float(normal@cmcdir),'normal_dot_proximal_palm_direction_proxy':float(normal@unit(palmcue)),'CMC_vertex794_distance_mm':mindist(P,ids,{794}),'thenar_facing_direction_proxy':cmcdir.tolist(),'palm_facing_direction_proxy':unit(palmcue).tolist(),'cue_limitations':'CMC-proximal directions describe spatial context; no independent thenar/palm ownership boundary exists here. Exact cage mask is not inferred from approximate reconstruction.','surface_face_continuous':True,'web_facing_role':'UNRESOLVED_BY_NORMALS_ALONE','circumferential_completeness':{'whole_ring_verified':r.get('known_ring_id') is not None,'known_ring_id':r.get('known_ring_id'),'beyond_known_rings':'NOT_PROVEN_BY_TWO_COLUMN_PATCH; no lateral palm expansion performed'},'shared_seed_local_edge_geodesic_mm':None if sd is None else {str(v):sd[v] for v in ids}}
        deg={v:sum(v in E[e] for e in r['outgoing_edge_ids']) for v in tip};ends=sorted(v for v,d in deg.items() if d==1)
        assert len(ends)==2
        rr['frontier_separation_mm']=float(np.linalg.norm(P[ends[0]]-P[ends[1]])*1000)
        rr['outgoing_frontier_endpoint_ids']=ends
        rr['cross_section_partial_arc_length_mm']=float(sum(np.linalg.norm(P[E[e][0]]-P[E[e][1]]) for e in r['outgoing_edge_ids'])*1000)
        rr['cross_section_arc_chord_ratio']=rr['cross_section_partial_arc_length_mm']/rr['frontier_separation_mm']
        prev=normal;result.append(rr)
    return result,scope

# Profiles start at R06, R07, R08 for MCP context, then actual opposite-edge rows.
prefix=[]
for j in [6,7,8]:
    ins=[edge(SEQ[j-1][c],SEQ[j-1][c+1]) for c in [4,5]];records=row_step(ins,STACK['rings'][j-1]['distal_face_strip'] or []);fs=[r['face_id'] for r in records]
    assert all(set(F[fi])<=set(SEQ[j-1]+SEQ[j]) for fi in fs)
    prefix.append({'row_id':f'R{j:02d}','known_ring_id':f'R{j:02d}','face_ids':fs,'vertex_ids':sorted({v for fi in fs for v in F[fi]}),'incoming_edge_ids':ins,'outgoing_edge_ids':[r['outgoing_edge'] for r in records],'outgoing_vertex_ids':[SEQ[j][c] for c in [4,5,6]],'valences':{str(SEQ[j][c]):len(ADJ[SEQ[j][c]]) for c in [4,5,6]},'cap_overlap':[],'nail_overlap':[],'event_types':[]})
dist={};prox={};scopes={}
for state in STATES:
    dist[state],scopes[state]=profile(T['distal_non_nail']['rows'],state,True)
    prox[state],_=profile(prefix+T['proximal']['rows'],state)
dump('DISTAL_NON_NAIL_LONGITUDINAL_PROFILE.json',{'states':dist,'distance_units':'mm','normal_units':'unit vector / angles degrees','local_metric_scope':scopes,'row_rule':'Opposite-edge face continuation, one non-nail column; no arbitrary paths','full_R3_distance_field_computed':False,'first_conflict_row':'D05','first_conflict_face':1227,'first_conflict_cap_vertices':[298,1454]})
dump('PROXIMAL_SHARED_STRIP_LONGITUDINAL_PROFILE.json',{'states':prox,'distance_units':'mm','topology_trace_only_columns':2,'lateral_expansion':False,'whole_palm_role_search':False,'note':'S3 topology-only traversal is a negative control. Later rows are NOT proposed shared support. Local geometric events may occur earlier; topology continuation is not semantic persistence.','first_topology_event':T['proximal']['first_structural_or_authority_event']})

# Left/right identity from original edge/face incidence, not images.
side=[]
for name,c,fi,other in [('LEFT',4,1177,5),('RIGHT',6,1176,5)]:
    v=SEQ[0][c];inner=SEQ[0][other];rowedge=edge(v,inner);outrec=row_step([rowedge],STACK['rings'][0]['proximal_face_strip'])[0];vs=F[fi];outer=next(w for w in vs if w in ADJ[v] and w!=inner)
    rr={'frontier':name,'column_provenance':c,'R00_vertex':v,'existing_frontier_edge_ids':F3[name.lower()+'_frontier_edge_ids'],'R00_sector_end_edge':rowedge,'first_continuation_face':fi,'face_vertex_ids':vs,'boundary_continuation_edge':edge(v,outer),'incident_face_ids':EFS[edge(v,outer)],'nail_overlap':sorted(set(vs)&NAILS['thumb']),'cap_overlap':sorted(set(vs)&CAP),'identity':'NAIL_FACING_SIDE' if set(vs)&NAILS['thumb'] else 'NON_NAIL_SIDE','states':{}}
    for state,(P,C,I) in STATES.items():
        FN=normals(P);rr['states'][state]={'nail_distance_min_vertex_mm':mindist(P,vs,NAILS['thumb']),'cap_distance_min_vertex_mm':mindist(P,vs,CAP),'mean_normal':FN[fi].tolist(),'frontier_local_tangent':unit(P[outer]-P[v]).tolist(),'frontier_vertex_world_m':P[v].tolist()}
    side.append(rr)
dump('DISTAL_FRONTIER_SIDE_IDENTITY_R1.json',{'status':'RESOLVED_TOPOLOGICAL_SIDE_IDENTITY','sides':side,'nail_side_hard_constraint':{'status':'RESOLVED','side':'LEFT','stop_before_face':1177,'excluded_nail_vertex':304,'mechanism':'AUTHORITY_CONFLICT_TERMINATION','constraint_does_not_stop_other_side':True},'asymmetric_taper_allowed':True})
print(json.dumps({'distal':{k:[(r['row_id'],r['face_ids'],round(r['normal_dot_web_context'],3),round(r['normal_turn_from_previous_row_deg'] or 0,2),round(r['distance_to_cap37_min_vertex_mm'],3)) for r in v] for k,v in dist.items()},'proximal_first12':{k:[(r['row_id'],round(r['mean_arc_mm'],3),round(r['tangent_dot_thumb_axis'],3),round(r['local_tube_radius_proxy_mm'],3)) for r in v[:15]] for k,v in prox.items()}},indent=2))
