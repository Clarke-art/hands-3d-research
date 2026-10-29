import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
PREV=OUT.parent/'thumb_frozen_web_partial_circumference_frontier_authority_r1'
sys.path.insert(0,str(PREV))
from local_data import N,V,E,F,ADJ,VF,EF,EFS,FADJ,CAP,WEB,SEEDS,NAILS,NAILF,CHAIN,INDEX_CHAIN,ARC,DIST,KNOTS,J,A,ROOT,REC,read,sha,unit,project,components,surface,src,np
def dump(name,value):(OUT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
STACK=read(PREV/'THUMB_PROXIMAL_RING_STACK_R1.json');SEQ=[r['vertex_sequence'] for r in STACK['rings']]
F3=read(PREV/'LOCAL_DIAGNOSTIC_STRIP_SETS.json')['F3']
def edge(a,b):return EF[tuple(sorted((a,b)))]
def fedges(fi):
    vs=F[fi];return [edge(a,b) for a,b in zip(vs,vs[1:]+vs[:1])]
def row_step(incoming,last):
    records=[]
    for ei in incoming:
        fs=sorted(set(EFS[ei])-set(last));r={'incoming_edge':ei,'candidate_face_ids':fs,'unique_quad':len(fs)==1 and len(F[fs[0]])==4}
        if r['unique_quad']:
            fi=fs[0];opp=[e for e in fedges(fi) if not set(E[e])&set(E[ei])];assert len(opp)==1
            r.update(face_id=fi,vertex_ids=F[fi],outgoing_edge=opp[0])
        records.append(r)
    return records
if __name__=='__main__':
    assert not (OUT/'FROZEN_HASHES_BEFORE.json').exists()
    before={'workspace':{str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and OUT not in p.parents and '.git' not in p.parts},'external':{p:sha(p) for p in read(PREV/'FROZEN_HASHES_BEFORE.json')['external']}}
    request=r'<USER_HOME>\.codex\attachments\3f5177e3-1a85-4a91-8aa9-4970999a12d0\已粘贴的文本.txt'
    before['external'][request]=sha(request);dump('FROZEN_HASHES_BEFORE.json',before)
    for group,h in read(PREV/'OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json')['files'].items():assert sha(PREV/group)==h
    for key in ['cap_authority','corrected_rig','kinematic_authority','kinematic_application','Stage4C_geometry','native_geometry','nail_authority','first_web_membership','first_web_human_approval','CMC_cage_source','CMC_cage_construction','native_thumb_anchor_evidence','native_index_anchor_evidence']:
        s=A['sources'][key];assert sha(ROOT/s['path'])==s['sha256']
    dump('INPUT_VERIFICATION.json',{'status':'PASS','prior_audit_output_manifest_verified':True,'source_manifest':str((REC/'AUTHORITY_INPUT_VERIFICATION.json').relative_to(ROOT)),'historical_labels_loaded':False,'scope':'Only opposite-edge continuation of F3 local face columns; event-adjacent controls; no global domain or solver work','workspace_files':len(before['workspace']),'external_files':len(before['external'])})
    print('Frozen',len(before['workspace']),'+',len(before['external']),'files')
