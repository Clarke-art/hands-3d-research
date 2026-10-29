"""Final read-only output and frozen-hash verification after visual inspection."""
import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from PIL import Image
AUD=Path(__file__).resolve().parents[1];ROOT=AUD.parents[2]
def read(n):return json.loads((AUD/n).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
required=['NARROW_ANATOMICAL_EVIDENCE_REVIEW_STATUS.json','BODY_SIDE_COLLAR_ANATOMICAL_CLUSTER_AUDIT.json','MODEL_ANATOMY_CORRESPONDENCE_AUDIT.json','ANATOMICAL_SOURCE_REGISTER.json','BODY_SIDE_COLLAR_EXISTING_WEIGHT_PROVENANCE.json','FROZEN_HASH_VERIFICATION.json']
for n in required:read(n)
assert (AUD/'NARROW_ANATOMICAL_EVIDENCE_REVIEW_REPORT.md').is_file()
status=read(required[0]);cluster=read(required[1]);mapping=read(required[2]);sources=read(required[3]);provenance=read(required[4])
assert status['BRANCH']=='D' and status['Stage5B_R1F']=='NOT_CREATED'
assert len(cluster['body_vertex_ids'])==16
assert sorted(v for c in cluster['clusters'] for v in c['vertex_ids'])==cluster['body_vertex_ids']
assert len(cluster['vertices'])==16 and len(mapping['index_side_vertices'])==16
assert len(sources['sources'])==8
assert len(provenance['vertices'])==16
for p in provenance['vertices']:
    w=p['historical_vectors']
    assert w['STAGE5B_R1']==w['STAGE5B_R1A']==w['STAGE5B_R1B']
    assert all(w['STAGE5B_R1B'].get(g,0)<1e-6 for g in ['THUMB_CMC_R','THUMB_MCP_R'])
before=read('FROZEN_HASHES_BEFORE.json')
assert all(sha(ROOT/k)==h for k,h in before.items())
blends={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in ROOT.rglob('*.blend')}
assert blends=={k:h for k,h in before.items() if k.endswith('.blend')}
out=read('OUTPUT_VERIFICATION.json')
for n in out['required_figures']:
    with Image.open(AUD/'renders'/n) as im:assert im.size==(1800,1200);im.verify()
assert not (AUD/'BODY_SIDE_COLLAR_ALLOWED_GROUP_AUTHORITY_PROPOSAL.json').exists()
assert not (AUD/'renders/PROPOSED_REGIONAL_WEIGHT_AUTHORITY_MAP.png').exists()
out.update(required_reports_exist=True,visual_inspection='PASS — all seven plots inspected in contact sheet; geometry panels, point sectors, legends, all required region context and candidate/uncertainty labels checked',final_frozen_hash_check_pass=True,protected_file_count=len(before),all_workspace_blend_inventory_identical=True,conditional_authority_outputs_correctly_omitted=True)
(AUD/'OUTPUT_VERIFICATION.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
print('Final verification PASS; protected files=',len(before),'PNG=',len(out['required_figures']),'deformation=0; blend writes=0')
for k,h in before.items():
    if k.endswith('.blend') and any('/'+part+'/' in k for part in ['stage5a_r2a','stage5b_r1b','stage5b_r1e']):print(k,h)
