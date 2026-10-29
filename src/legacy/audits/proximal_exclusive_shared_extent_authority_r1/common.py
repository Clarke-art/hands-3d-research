"""Frozen data readers and surface topology helpers; no solver imports."""
from pathlib import Path
import sys,json,hashlib
from collections import Counter
import numpy as np
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PREV=ROOT/'audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1'
REC=ROOT/'production_spec/stage5_production_rig/cap_derived_r2_r3_input_reconciliation_r1'
S5=ROOT/'production_spec/stage5_production_rig'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def packed(ids):
    ids=sorted(set(map(int,ids)))
    return {'count':len(ids),'vertex_ids':ids,'sha256':hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest()}
A=read(REC/'AUTHORITY_INPUT_VERIFICATION.json')
def src(k):return read(ROOT/A['sources'][k]['path'])
J=read(REC/'READ_ONLY_LIVE_EXTRACTION.json')
V=np.array(J['RSSF']['vertices_world_m']);N=np.array(J['NATIVE']['vertices_world_m']);E=J['RSSF']['edges'];F=J['RSSF']['faces'];NV=len(V)
ADJ=[set() for _ in range(NV)]
for a,b in E:ADJ[a].add(b);ADJ[b].add(a)
EF={tuple(sorted(e)):i for i,e in enumerate(E)};E_F=[[] for _ in E];V_F=[[] for _ in V]
for fi,vs in enumerate(F):
    for v in vs:V_F[v].append(fi)
    for a,b in zip(vs,vs[1:]+vs[:1]):E_F[EF[tuple(sorted((a,b)))]].append(fi)
CAP=set(src('cap_authority')['vertex_ids']);WEB=set(src('first_web_membership')['selected_vertices'])
NAILS={d:{v for fi in ids for v in F[fi]} for d,ids in src('nail_authority')['per_digit_faces'].items()}
NI=src('native_partition_evidence');TIPS=NI['tip_seeds']
INDEX_TUBE=set(read(REC/'CORRECTED_THUMB_TUBE_ANCHOR_CANDIDATE_AUDIT.json')['sets']['index_native_guarded_tube']['vertex_ids'])
INDEX_SOURCES=INDEX_TUBE|NAILS['index']
ANCHORS={d:read(S5/f'stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1/NATIVE_{d.upper()}_ANCHOR_SET.json') for d in ['thumb','index']}
def components(ids,adj=ADJ):
    todo=set(ids);res=[]
    while todo:
        s=min(todo);todo.remove(s);c={s};q=[s]
        while q:
            v=q.pop()
            for w in adj[v]:
                if w in todo:todo.remove(w);c.add(w);q.append(w)
        res.append(c)
    return sorted(res,key=lambda c:(-len(c),min(c)))
def component(seed,allowed):
    if seed not in allowed:return set()
    seen={seed};q=[seed]
    while q:
        v=q.pop()
        for w in ADJ[v]:
            if w in allowed and w not in seen:seen.add(w);q.append(w)
    return seen
def unit(a):return a/np.linalg.norm(a)
def projection(chain,points):
    ds=np.full(len(points),np.inf);ss=np.zeros(len(points));seg=np.zeros(len(points),int);base=0.;knots=[0.]
    for j,(a,b) in enumerate(zip(chain[:-1],chain[1:])):
        ab=b-a;l=np.linalg.norm(ab);t=np.clip((points-a)@ab/(l*l),0,1);dd=np.linalg.norm(points-(a+t[:,None]*ab),axis=1)*1000
        take=dd<ds;ds[take]=dd[take];ss[take]=base+t[take]*l*1000;seg[take]=j;base+=l*1000;knots.append(base)
    return ss,ds,seg,knots
B=J['CORRECTED']['bones']
def chain(d):
    names=[d+'_'+s+'_R' for s in (['CMC','MCP','IP'] if d=='THUMB' else ['MCP','PIP','DIP'])]
    return np.array([B[n]['head_world_m'] for n in names]+[B[names[-1]]['tail_world_m']])
CHAINS={d:chain(d.upper()) for d in ['thumb','index']}
PROJ={d:projection(c,V) for d,c in CHAINS.items()}
def surface_audit(ids):
    ids=set(ids);edges=[i for i,(a,b) in enumerate(E) if a in ids and b in ids];fs=[fi for fi,vs in enumerate(F) if set(vs)<=ids]
    support={v for fi in fs for v in F[fi]};face_edges={EF[tuple(sorted((a,b)))] for fi in fs for a,b in zip(F[fi],F[fi][1:]+F[fi][:1])}
    wires=set(edges)-face_edges;cnt=Counter(e for fi in fs for e in [EF[tuple(sorted((a,b)))] for a,b in zip(F[fi],F[fi][1:]+F[fi][:1])])
    bd={e for e,n in cnt.items() if n==1};ba={v:set() for e in bd for v in E[e]}
    for e in bd:a,b=E[e];ba[a].add(b);ba[b].add(a)
    cs=components(ids);oc=components(set(range(NV))-ids)
    holes=[c for c in oc if not c&{TIPS[d] for d in ['wrist','middle','ring','little']}]
    return {'vertices':packed(ids),'edge_count':len(edges),'face_count':len(fs),'face_ids':fs,'connected_components':len(cs),'component_sizes':[len(c) for c in cs],'non_face_supported_vertices':sorted(ids-support),'wire_only_edge_ids':sorted(wires),'wire_only_edge_endpoints':[E[e] for e in sorted(wires)],'dangling_vertices':sorted(v for v in ids if len(ADJ[v]&ids)<=1),'surface_supported':bool(ids) and not (ids-support) and not wires,'boundary_edge_ids':sorted(bd),'boundary_edge_components':[len(c) for c in components(ba,ba)] if ba else [],'boundary_non_degree2_vertices':sorted(v for v in ba if len(ba[v])!=2),'euler_characteristic':len(support)-len(face_edges)+len(fs),'enclosed_complement_candidates':[packed(c) for c in holes],'holes_interpretation':'Complement components missing all excluded digit tips and wrist are candidate holes; no solver labels involved','both_source_reachability':[{'vertices':len(c),'has_thumb_anchors':bool(c&(CAP|NAILS['thumb'])),'has_index_anchors':bool(c&INDEX_SOURCES)} for c in cs]}

if __name__=='__main__':
    assert not (OUT/'FROZEN_HASHES_BEFORE.json').exists()
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents and '.git' not in p.parts)
    ext=read(PREV/'FROZEN_HASHES_BEFORE.json')['external']
    dump('FROZEN_HASHES_BEFORE.json',{'workspace':{str(p.relative_to(ROOT)):sha(p) for p in files},'external':{p:sha(p) for p in ext}})
    for spec in A['sources'].values():assert sha(ROOT/spec['path'])==spec['sha256']
    assert sha(REC/'READ_ONLY_LIVE_EXTRACTION.json')==read(REC/'RECONCILIATION_EVIDENCE_HASH_MANIFEST_R1.json')['output_file_hashes']['READ_ONLY_LIVE_EXTRACTION.json']
    dump('INPUT_VERIFICATION.json',{'status':'PASS','frozen_source_hashes':A['sources'],'cached_geometry_extraction_sha256':sha(REC/'READ_ONLY_LIVE_EXTRACTION.json'),'extraction_source_identity_verified':True,'cost_units':'CORRECTED_COMMON_MM_SEMANTICS_CANDIDATE_PENDING_HUMAN_APPROVAL','cost_provenance_reopened':False,'workspace_files':len(files),'external_files':len(ext)})
    print('Frozen baseline:',len(files),'+',len(ext),'files; source hashes PASS.')
