from pathlib import Path
import hashlib,json,sys
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
PREV=ROOT/'production_spec/stage5_production_rig/cap_derived_r2_r3_input_reconciliation_r1'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def dump(n,d): (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
if __name__=='__main__':
    assert not (OUT/'FROZEN_HASHES_BEFORE.json').exists()
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents and '.git' not in p.parts)
    ext=read(PREV/'FROZEN_HASHES_BEFORE.json')['external']
    dump('FROZEN_HASHES_BEFORE.json',{'workspace':{str(p.relative_to(ROOT)):sha(p) for p in files},'external':{p:sha(Path(p)) for p in ext}})
    a=read(PREV/'AUTHORITY_INPUT_VERIFICATION.json')
    for v in a['sources'].values(): assert sha(ROOT/v['path'])==v['sha256'],v['path']
    manifest=read(PREV/'RECONCILIATION_EVIDENCE_HASH_MANIFEST_R1.json')
    dump('SOURCE_INPUT_VERIFICATION.json',{'status':'PASS','sources':a['sources'],'previous_manifest_sha256':sha(PREV/'RECONCILIATION_EVIDENCE_HASH_MANIFEST_R1.json'),'read_only_extraction_sha256':sha(PREV/'READ_ONLY_LIVE_EXTRACTION.json'),'cap_and_kinematic_decisions':'PRESERVED_NOT_READJUDICATED','existing_files':len(files),'external_files':len(ext)})
    print('Frozen baseline:',len(files),'workspace files;',len(ext),'external files. Source hashes PASS.')
