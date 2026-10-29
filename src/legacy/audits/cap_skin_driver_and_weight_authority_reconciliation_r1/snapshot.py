import json, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def inventory():
    result={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
    # Formal Human responses referenced by the authorities remain protected too.
    for folder in ('audits/human_r3_fresh_result_authority_freeze_r1','production_spec/stage5_production_rig/human_thumb_kinematic_authority_correction_r1','production_spec/stage5_production_rig/stage5b_r1e_human_cap_authority_freeze_r1'):
        for p in (ROOT/folder).glob('*.json'):
            def scan(x):
                if isinstance(x,dict):
                    for v in x.values():scan(v)
                elif isinstance(x,list):
                    for v in x:scan(v)
                elif isinstance(x,str) and x.startswith('<USER_HOME>\\Downloads\\'):
                    q=Path(x)
                    if q.is_file(): result[str(q)]=sha(q)
            scan(json.loads(p.read_text(encoding='utf-8-sig')))
    return result
if __name__=='__main__':
    p=OUT/'FROZEN_HASHES_BEFORE.json'
    assert not p.exists(), 'Refuse to replace baseline'
    data=inventory();p.write_text(json.dumps(data,indent=2),encoding='utf-8')
    print('Protected baseline:',len(data),'files')
