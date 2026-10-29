"""Read-only local ring evidence. No historical ownership labels or solver code."""
import sys,json,hashlib
from pathlib import Path
from collections import Counter
import numpy as np
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PREV=ROOT/'audits/proximal_exclusive_shared_extent_authority_r1'
REC=ROOT/'production_spec/stage5_production_rig/cap_derived_r2_r3_input_reconciliation_r1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def unit(v):return v/np.linalg.norm(v)
def pack(ids):return {'count':len(set(ids)),'vertex_ids':sorted(set(map(int,ids)))}
A=read(REC/'AUTHORITY_INPUT_VERIFICATION.json')
def src(k):return read(ROOT/A['sources'][k]['path'])
J=read(REC/'READ_ONLY_LIVE_EXTRACTION.json');N=np.array(J['NATIVE']['vertices_world_m']);V=np.array(J['RSSF']['vertices_world_m']);E=J['RSSF']['edges'];F=J['RSSF']['faces'];NV=len(V)
ADJ=[set() for _ in V];VF=[[] for _ in V];EF={tuple(sorted(e)):i for i,e in enumerate(E)};EFS=[[] for _ in E]
for a,b in E:ADJ[a].add(b);ADJ[b].add(a)
for fi,vs in enumerate(F):
    for v in vs:VF[v].append(fi)
    for a,b in zip(vs,vs[1:]+vs[:1]):EFS[EF[tuple(sorted((a,b)))]].append(fi)
FADJ=[set() for _ in F]
for fs in EFS:
    for a in fs:FADJ[a].update(set(fs)-{a})
CAP=set(src('cap_authority')['vertex_ids']);WEB=set(src('first_web_membership')['selected_vertices']);SEEDS={1396,1399,1402,2774}
NAILF=src('nail_authority')['per_digit_faces'];NAILS={d:{v for fi in ids for v in F[fi]} for d,ids in NAILF.items()}
B=J['CORRECTED']['bones'];CHAIN=np.array([B['THUMB_'+s+'_R']['head_world_m'] for s in ['CMC','MCP','IP']]+[B['THUMB_IP_R']['tail_world_m']]);INDEX_CHAIN=np.array([B['INDEX_'+s+'_R']['head_world_m'] for s in ['MCP','PIP','DIP']]+[B['INDEX_DIP_R']['tail_world_m']])
def project(C,P):
    ds=np.full(len(P),np.inf);ss=np.zeros(len(P));ks=[0.];base=0.
    for a,b in zip(C[:-1],C[1:]):
        ab=b-a;l=np.linalg.norm(ab);t=np.clip((P-a)@ab/(l*l),0,1);dd=np.linalg.norm(P-(a+t[:,None]*ab),axis=1)*1000;take=dd<ds
        ds[take]=dd[take];ss[take]=base+t[take]*l*1000;base+=l*1000;ks.append(base)
    return ss,ds,ks
ARC,DIST,KNOTS=project(CHAIN,V)
RAW=read(PREV/'THUMB_BRANCH_CONTINUITY_AUDIT.json')['true_topological_rings']['rings']
def components(ids,adj=ADJ):
    todo=set(ids);res=[]
    while todo:
        seed=min(todo);todo.remove(seed);c={seed};q=[seed]
        while q:
            v=q.pop()
            for w in adj[v]:
                if w in todo:todo.remove(w);c.add(w);q.append(w)
        res.append(c)
    return sorted(res,key=lambda c:(-len(c),min(c)))
def grow(ids,k):
    s=set(ids);front=s.copy()
    for _ in range(k):front={w for v in front for w in ADJ[v]}-s;s|=front
    return s
def surface(ids):
    ids=set(ids);es={ei for ei,(a,b) in enumerate(E) if a in ids and b in ids};fs={fi for fi,vs in enumerate(F) if set(vs)<=ids};fv={v for fi in fs for v in F[fi]};fes={EF[tuple(sorted((a,b)))] for fi in fs for a,b in zip(F[fi],F[fi][1:]+F[fi][:1])}
    return {'vertex_count':len(ids),'edge_count':len(es),'face_count':len(fs),'face_ids':sorted(fs),'non_face_supported_vertex_ids':sorted(ids-fv),'wire_only_edge_ids':sorted(es-fes),'dangling_vertex_ids':sorted(v for v in ids if len(ADJ[v]&ids)<=1),'connected_components':len(components(ids)),'surface_supported':bool(ids) and ids==fv and es==fes}
if __name__=='__main__':
    assert not (OUT/'FROZEN_HASHES_BEFORE.json').exists()
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents and '.git' not in p.parts)
    ext=read(PREV/'FROZEN_HASHES_BEFORE.json')['external']
    dump('FROZEN_HASHES_BEFORE.json',{'workspace':{str(p.relative_to(ROOT)):sha(p) for p in files},'external':{p:sha(p) for p in ext}})
    for spec in A['sources'].values():assert sha(ROOT/spec['path'])==spec['sha256']
    assert sha(REC/'READ_ONLY_LIVE_EXTRACTION.json')==read(REC/'RECONCILIATION_EVIDENCE_HASH_MANIFEST_R1.json')['output_file_hashes']['READ_ONLY_LIVE_EXTRACTION.json']
    dump('INPUT_VERIFICATION.json',{'status':'PASS','sources':A['sources'],'previous_ring_audit_sha256':sha(PREV/'THUMB_BRANCH_CONTINUITY_AUDIT.json'),'seed_ids':sorted(SEEDS),'seed_membership_in_frozen21_valid':SEEDS<=WEB,'cap37_and_web21_and_nail_membership_reopened':False,'cost_unit_authority':'CORRECTED_COMMON_MM_SEMANTICS_CANDIDATE_PENDING_HUMAN_APPROVAL','local_scope':'9 existing closed thumb rings; immediate1/2-ring endpoint face neighborhoods only','historical_R2_R3_labels_loaded':False,'workspace_files':len(files),'external_files':len(ext)})
    print('Frozen baseline',len(files),'+',len(ext),'files; input verification PASS.')
