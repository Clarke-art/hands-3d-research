"""Static, read-only P02--P06 evidence extraction. Never imports prior analysis code."""
import sys
sys.dont_write_bytecode = True
import json, hashlib
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
PREV = OUT.parent / 'thumb_shared_strip_longitudinal_stop_rule_authority_r1'
REC = ROOT / 'production_spec/stage5_production_rig/cap_derived_r2_r3_input_reconciliation_r1'
NAME = 'NARROW_PROXIMAL_WEB_TO_PALM_TRANSITION_AUTHORITY_R1'
ROWS = ['P02', 'P03', 'P04', 'P05', 'P06']
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n, d): (OUT/n).write_text(json.dumps(d, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf8')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576), b''): h.update(b)
    return h.hexdigest()
def inventory():
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and OUT not in p.parents and '.git' not in p.parts}
def unit(x):
    x=np.asarray(x, dtype=float); l=np.linalg.norm(x)
    assert l>1e-14
    return x/l
def angle(a,b): return float(np.degrees(np.arccos(np.clip(unit(a)@unit(b),-1,1))))

if not (OUT/'FROZEN_HASHES_BEFORE.json').exists():
    ext=list(read(PREV/'FROZEN_HASHES_AFTER.json')['external'])
    ext.append(r'<USER_HOME>\.codex\attachments\9e43acf6-4c34-4aad-bcbc-514da4387dfa\已粘贴的文本.txt')
    dump('FROZEN_HASHES_BEFORE.json', {'workspace':inventory(), 'external':{p:sha(p) for p in sorted(set(ext))}})

# Verify provenance by hashes without consulting historical role/weight content.
checks=[]
def ck(n,v):
    assert v,n
    checks.append({'name':n,'passed':True})
for p,h in read(PREV/'OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json')['files'].items(): ck('previous evidence hash: '+p,sha(PREV/p)==h)
authority=read(REC/'AUTHORITY_INPUT_VERIFICATION.json')
sourcekeys=['cap_authority','corrected_rig','kinematic_authority','kinematic_application','Stage4C_geometry','native_geometry','nail_authority','first_web_membership','first_web_human_approval','CMC_cage_source','CMC_cage_construction','native_thumb_anchor_evidence']
for k in sourcekeys:
    s=authority['sources'][k];ck('frozen source hash: '+k,sha(ROOT/s['path'])==s['sha256'])
ck('frozen extraction hash',sha(REC/'READ_ONLY_LIVE_EXTRACTION.json')==read(REC/'RECONCILIATION_EVIDENCE_HASH_MANIFEST_R1.json')['output_file_hashes']['READ_ONLY_LIVE_EXTRACTION.json'])
j=read(REC/'READ_ONLY_LIVE_EXTRACTION.json')
E=j['RSSF']['edges']; F=j['RSSF']['faces']; ck('native/RSSF exact stable topology',j['NATIVE']['edges']==E and j['NATIVE']['faces']==F)
ef={tuple(sorted(e)):i for i,e in enumerate(E)}
vf={}; efs={}; ve={}
for ei,(a,b) in enumerate(E):
    ve.setdefault(a,[]).append(ei);ve.setdefault(b,[]).append(ei)
for fi,vs in enumerate(F):
    for v in vs: vf.setdefault(v,[]).append(fi)
    for a,b in zip(vs,vs[1:]+vs[:1]): efs.setdefault(ef[tuple(sorted((a,b)))],[]).append(fi)
def fedges(fi):
    vs=F[fi]; return [ef[tuple(sorted((a,b)))] for a,b in zip(vs,vs[1:]+vs[:1])]
def local_fan(v):
    fs=vf[v];adj={f:sorted({g for e in fedges(f) if v in E[e] for g in efs[e] if g!=f}) for f in fs}
    assert all(len(a)==2 for a in adj.values())
    first=min(fs);order=[first];previous=None;current=first
    for _ in range(len(fs)-1):
        nxt=next(g for g in adj[current] if g!=previous)
        assert nxt not in order
        order.append(nxt);previous,current=current,nxt
    assert first in adj[current]
    return {'cyclic_face_ids':order,'cyclic_shared_edge_ids':[next(e for e in set(fedges(a))&set(fedges(b)) if v in E[e]) for a,b in zip(order,order[1:]+order[:1])],'closed_fan':True,'orientation':'deterministic arbitrary cycle orientation; no anatomical label'}
trace=read(PREV/'RAW_LOCAL_COLUMN_TRACES.json')
rows=[r for r in trace['proximal']['rows'] if r['row_id'] in ROWS]
del trace
ck('exact allowed rows', [r['row_id'] for r in rows]==ROWS)
ck('exact allowed face pairs',[r['face_ids'] for r in rows]==[[1372,1375],[1373,1374],[1368,1371],[1369,1370],[1378,1377]])
prior=read(PREV/'PROXIMAL_SHARED_STRIP_LONGITUDINAL_PROFILE.json')
prior={s:{r['row_id']:r for r in prior['states'][s] if r['row_id'] in ROWS} for s in ['NATIVE','RSSF']}
ids=sorted({v for r in rows for v in r['vertex_ids']})
focus=sorted({f for r in rows for f in r['face_ids']})
neighbours=sorted({f for v in ids for f in vf[v]})
normal_faces=sorted({f for v in ids for f in vf[v]})
q=read(ROOT/authority['sources']['native_thumb_anchor_evidence']['path'])['native_direction_support']
NC=np.array([q['axis_anchor_world_m']]+[q['joint_world_m'][k] for k in ['MCP','IP','TIP']])
b=j['CORRECTED']['bones']
RC=np.array([b['THUMB_'+s+'_R']['head_world_m'] for s in ['CMC','MCP','IP']]+[b['THUMB_IP_R']['tail_world_m']])
states={'NATIVE':(np.array(j['NATIVE']['vertices_world_m']),NC),'RSSF':(np.array(j['RSSF']['vertices_world_m']),RC)}
def section(edges):
    mid=set(E[edges[0]])&set(E[edges[1]]);assert len(mid)==1
    m=next(iter(mid));return [next(v for v in E[edges[0]] if v!=m),m,next(v for v in E[edges[1]] if v!=m)]
def chain_context(C,x):
    candidates=[]
    for i,(a,b) in enumerate(zip(C[:-1],C[1:])):
        ab=b-a;t=float(np.clip((x-a)@ab/(ab@ab),0,1));foot=a+t*ab
        candidates.append((float(np.linalg.norm(x-foot)),i,t,foot,unit(ab)))
    _,i,t,foot,axis=min(candidates,key=lambda a:a[0])
    return i,t,foot,axis

patch={'name':'PROXIMAL_TRANSITION_LOCAL_PATCH_R1','row_ids':ROWS,'focus_face_ids':focus,'focus_vertex_ids':ids,'direct_incident_face_ids':neighbours,'scope':'Fixed ten faces and their direct vertex-incident neighbourhood; no recursive traversal and no P07+ trace. MCP/CMC/chain are structural references only.','units':{'positions':'world metres','distances':'millimetres','angles':'degrees'},'normal_method':'Newell polygon area vector in world coordinates; vertex normal = normalized sum of direct incident polygon area vectors (computed diagnostic, not cached Blender split normals).','states':{},'topology':{'vertices':{str(v):{'edge_ids':ve[v],'incident_face_ids':vf[v],'valence':len(ve[v]),'local_ordered_face_fan':local_fan(v)} for v in ids},'edges':{str(e):{'vertex_ids':E[e],'incident_face_ids':efs[e]} for e in sorted({e for f in focus for e in fedges(f)})},'faces':{str(f):{'vertex_ids':F[f],'edge_ids':fedges(f)} for f in neighbours}},'cue_limitations':'Palmar and thenar anatomical normal bases are not frozen in this patch. CMC direction and neighbour normals are proxies, never ownership sources. No full circumference inferred.'}
for state,(P,C) in states.items():
    area={f:np.cross(P[F[f]],np.roll(P[F[f]],-1,axis=0)).sum(0) for f in normal_faces}
    fn={f:unit(a) for f,a in area.items()}
    vn={v:unit(sum((area[f] for f in vf[v]),np.zeros(3))) for v in ids}
    rr=[]
    for r in rows:
        n=r['row_id'];ins=section(r['incoming_edge_ids']);outs=section(r['outgoing_edge_ids']);ctr=P[r['vertex_ids']].mean(0)
        incoming=P[ins].mean(0);outgoing=P[outs].mean(0);L=unit(outgoing-incoming);N=unit(sum((area[f] for f in r['face_ids']),np.zeros(3)))
        T=unit((P[outs[-1]]-P[outs[0]])+(P[ins[-1]]-P[ins[0]]))
        # Tangent-projected orthonormal frame, with signed L x T normal handedness.
        LP=unit(L-N*(L@N));TP=unit(np.cross(N,LP)); TP=TP if TP@T>=0 else -TP
        i,t,foot,axis=chain_context(C,ctr)
        rv=ctr-foot; radial=unit(rv-axis*(rv@axis));circ=unit(np.cross(axis,radial))
        flank=sorted({f for v in r['vertex_ids'] for f in vf[v]}-set(focus))
        flankn=unit(sum((area[f] for f in flank),np.zeros(3)))
        av=prior[state][n]
        front={}
        for name,sec in [('incoming',ins),('outgoing',outs)]:
            chord=float(np.linalg.norm(P[sec[-1]]-P[sec[0]])*1000)
            arc=float(sum(np.linalg.norm(P[a]-P[b]) for a,b in zip(sec[:-1],sec[1:]))*1000)
            front[name]={'ordered_vertex_ids':sec,'left_position_world_m':P[sec[0]].tolist(),'middle_position_world_m':P[sec[1]].tolist(),'right_position_world_m':P[sec[2]].tolist(),'chord_width_mm':chord,'partial_arc_width_mm':arc,'arc_chord_ratio':arc/chord,'transverse_vector':unit(P[sec[-1]]-P[sec[0]]).tolist()}
        lanes=[]
        for lane in range(2):
            a=unit(P[outs[lane]]-P[ins[lane]]); z=unit(P[outs[lane+1]]-P[ins[lane+1]])
            fi=r['face_ids'][lane];fc=P[F[fi]].mean(0);_,_,ffoot,faxis=chain_context(C,fc);frad=unit((fc-ffoot)-faxis*((fc-ffoot)@faxis))
            lanes.append({'face_id':fi,'left_frontier_edge_id':ef[tuple(sorted((ins[lane],outs[lane])))],'right_frontier_edge_id':ef[tuple(sorted((ins[lane+1],outs[lane+1])))],'incoming_edge_id':r['incoming_edge_ids'][lane],'outgoing_edge_id':r['outgoing_edge_ids'][lane],'face_normal':fn[fi].tolist(),'normal_dot_own_face_centroid_radial':float(fn[fi]@frad),'own_face_centroid_radial_direction':frad.tolist(),'side_tangent_turn_deg':angle(a,z)})
        pervertex=[]
        for v in r['vertex_ids']:
            vi,vt,vfoot,vaxis=chain_context(C,P[v]); vr=unit((P[v]-vfoot)-vaxis*((P[v]-vfoot)@vaxis))
            pervertex.append({'vertex_id':v,'normal':vn[v].tolist(),'normal_dot_chain_radial':float(vn[v]@vr),'normal_dot_chain_axis':float(vn[v]@vaxis)})
        rr.append({'row_id':n,'face_ids':r['face_ids'],'vertex_ids':r['vertex_ids'],'edge_ids':sorted({e for f in r['face_ids'] for e in fedges(f)}),'incoming_edge_ids':r['incoming_edge_ids'],'outgoing_edge_ids':r['outgoing_edge_ids'],'centre_world_m':ctr.tolist(),'frontiers':front,'left_frontier_edge_id':ef[tuple(sorted((ins[0],outs[0])))],'right_frontier_edge_id':ef[tuple(sorted((ins[-1],outs[-1])))],'lanes':lanes,'vertex_normals':pervertex,'frame':{'longitudinal':L.tolist(),'transverse':T.tolist(),'surface_normal':N.tolist(),'orthonormal_longitudinal':LP.tolist(),'orthonormal_transverse':TP.tolist(),'L_cross_T_dot_normal':float(unit(np.cross(L,T))@N),'longitudinal_dot_thumb_axis':float(L@axis),'transverse_dot_circumferential':float(T@circ),'transverse_dot_thumb_axis':float(T@axis),'normal_dot_chain_radial':float(N@radial),'normal_dot_thumb_axis':float(N@axis),'normal_dot_circumferential':float(N@circ)},'thumb_chain_relation':{'chain_points_world_m':C.tolist(),'nearest_segment_index':i,'nearest_segment_fraction':t,'axis_vector':axis.tolist(),'radial_direction_only':radial.tolist(),'circumferential_direction':circ.tolist(),'incoming_to_outgoing_axis_displacement_mm':float((outgoing-incoming)@axis*1000),'inherited_outgoing_chain_arc_delta_to_MCP_mm':av['signed_arc_to_MCP_mm']},'MCP_relation':{'reference_world_m':C[1].tolist(),'centre_offset_world_m':(ctr-C[1]).tolist(),'centre_distance_mm':float(np.linalg.norm(ctr-C[1])*1000),'not_stop_rule':True},'CMC_relation':{'reference_world_m':C[0].tolist(),'centre_distance_mm':float(np.linalg.norm(ctr-C[0])*1000),'centre_direction':unit(C[0]-ctr).tolist(),'normal_dot_CMC_direction':float(N@unit(C[0]-ctr)),'ownership_hard_source':False},'surface_cues':{'inherited_web_facing_dot':av['normal_dot_web_context'],'inherited_proximal_palm_proxy_dot':av['normal_dot_proximal_palm_direction_proxy'],'inherited_thenar_direction_proxy':av['thenar_facing_direction_proxy'],'local_flank_face_ids':flank,'local_flank_mean_normal':flankn.tolist(),'normal_dot_local_flank_normal':float(N@flankn),'face_pair_normal_turn_deg':angle(*[fn[f] for f in r['face_ids']]),'semantic_palmar_basis':'UNAVAILABLE','semantic_thenar_basis':'UNAVAILABLE'},'topology_auxiliary':{'valences':{str(v):len(ve[v]) for v in r['vertex_ids']},'incident_face_fans':{str(v):vf[v] for v in r['vertex_ids']},'one_hop_neighbor_count':len({f for v in r['vertex_ids'] for f in vf[v]}),'neighbor_quads':all(len(F[f])==4 for v in r['vertex_ids'] for f in vf[v])}})
    for k,r in enumerate(rr):
        prev=rr[k-1] if k else None;nxt=rr[k+1] if k<len(rr)-1 else None
        r['incoming_row_tangent']=None if prev is None else prev['frame']['longitudinal']
        r['outgoing_row_tangent']=None if nxt is None else nxt['frame']['longitudinal']
        r['turn_from_previous_row_deg']=None if prev is None else angle(prev['frame']['longitudinal'],r['frame']['longitudinal'])
        r['normal_turn_from_previous_row_deg']=None if prev is None else angle(prev['frame']['surface_normal'],r['frame']['surface_normal'])
        r['outgoing_width_relative_change_from_previous']=None if prev is None else r['frontiers']['outgoing']['chord_width_mm']/prev['frontiers']['outgoing']['chord_width_mm']-1
        r['within_row_width_relative_change']=r['frontiers']['outgoing']['chord_width_mm']/r['frontiers']['incoming']['chord_width_mm']-1
    patch['states'][state]={'rows':rr,'vertex_positions_world_m':{str(v):P[v].tolist() for v in sorted({v for f in neighbours for v in F[f]})},'face_normals':{str(f):fn[f].tolist() for f in neighbours},'vertex_normals':{str(v):vn[v].tolist() for v in ids},'chain_reference_provenance':'Independent native frozen anchor evidence' if state=='NATIVE' else 'Human-approved corrected extracted live thumb chain'}
dump('PROXIMAL_TRANSITION_LOCAL_PATCH_R1.json',patch)
dump('INPUT_VERIFICATION.json',{'status':'PASS','checks':checks,'legacy_ownership_labels_consulted':False,'weights_consulted':False,'previous_scripts_imported_or_executed':False,'scope_face_ids':focus,'focus_vertex_count':len(ids),'direct_incident_face_count':len(neighbours),'new_chain_radius_or_tube_anchor_computation':False,'read_only_extraction_source':str((REC/'READ_ONLY_LIVE_EXTRACTION.json').relative_to(ROOT))})
for s in patch['states']:
    print(s)
    for r in patch['states'][s]['rows']:
        fr=r['frame'];c=r['surface_cues']; w=r['frontiers']['outgoing']
        print(r['row_id'], 'width',round(w['chord_width_mm'],3),'arc/chord',round(w['arc_chord_ratio'],4),'L.axis',round(fr['longitudinal_dot_thumb_axis'],4),'T.circ',round(fr['transverse_dot_circumferential'],4),'T.axis',round(fr['transverse_dot_thumb_axis'],4),'N.radial',round(fr['normal_dot_chain_radial'],4),'N.axis',round(fr['normal_dot_thumb_axis'],4),'web',round(c['inherited_web_facing_dot'],4),'palm',round(c['inherited_proximal_palm_proxy_dot'],4),'flank',round(c['normal_dot_local_flank_normal'],4),'turn',r['turn_from_previous_row_deg'],'normalturn',r['normal_turn_from_previous_row_deg'],'valence',list(r['topology_auxiliary']['valences'].values()))
print('Boundary alternatives',[(r['row_id'],r['outgoing_edge_ids']) for r in rows[1:4]])
