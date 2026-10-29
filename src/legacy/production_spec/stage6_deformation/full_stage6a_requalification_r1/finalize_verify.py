import sys
sys.dont_write_bytecode=True
from common import *
import re
from PIL import Image
baseline=read(OUT/'HISTORICAL_HASHES_BEFORE.json');current=inventory()
changed=[{'path':p,'before':h,'after':current.get(p)} for p,h in baseline.items() if current.get(p)!=h]
unexpected=sorted(set(current)-set(baseline))
protection={'status':'PASS' if not changed and not unexpected else 'FAIL_CLOSED','protected_preexisting_file_count':len(baseline),'modified_or_deleted_preexisting_file_count':len(changed),'modified_or_deleted':changed,'new_files_outside_authorized_round_directory':unexpected,'production_input':ref(CAND),'production_candidate_hash_matches_expected':sha(CAND)==EXPECTED_CAND,'all_writes_confined_to':'production_spec/stage6_deformation/full_stage6a_requalification_r1','weights_geometry_topology_UV_materials_rest_bones_authorities_receipts_and_history_preserved':not changed and not unexpected,'PRODUCTION_DRIFT':len(changed)+len(unexpected)}
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',protection)
assert protection['status']=='PASS' and protection['production_candidate_hash_matches_expected'],protection
status=read(OUT/'FULL_STAGE6A_REQUALIFICATION_R1_STATUS.json');status['PRODUCTION_DRIFT']=0
status['PROTECTED_PREEXISTING_FILE_COUNT']=len(baseline)
dump('FULL_STAGE6A_REQUALIFICATION_R1_STATUS.json',status)
report=OUT/'FULL_STAGE6A_REQUALIFICATION_R1_REPORT.md'
txt=report.read_text(encoding='utf-8').replace('| PRODUCTION_DRIFT | PENDING_FINAL_HASH_VERIFICATION |','| PRODUCTION_DRIFT | 0 |')
txt+='\nFinal protection verification: all %d preexisting files retain exact SHA256; no writes outside this new round directory. The saved zero/RSSF harness reopened with an identical complete R2 mesh/rig/weight payload. Independent fresh-process reproduction matched all42 posed coordinate arrays and all12 severe/accepted exact-pair numeric records exactly.\n'%len(baseline)
report.write_text(txt,encoding='utf-8')
M=read(OUT/'EVIDENCE_RENDER_MANIFEST_R1.json');assert not M['panel_assembly_pending']
for r in M['renders']:
 p=OUT/r['path'];assert sha(p)==r['sha256']
 with Image.open(p) as im:assert list(im.size)==r['size'];im.verify()
page=(OUT/'review.html').read_text(encoding='utf-8')
links=re.findall(r'(?:src|href)="([^"]+)"',page)
missing=sorted({p for p in links if not p.startswith(('http:','https:','#')) and not (OUT/p).is_file()})
assert not missing,missing
assert page.count('<article ')==42 and page.count('data-angle="45"')==14
checks={'status':'PASS','formal_case_cards':42,'max_angle_cards':14,'image_count':len(M['renders']),'all_image_hashes_and_PNG_decodes_verified':True,'all_review_local_links_valid':True,'blocker_case_cards':page.count('data-state="BLOCKER"'),'independent_reproduction':read(OUT/'INDEPENDENT_REPRODUCTION_VERIFICATION_R1.json')['status'],'harness_reopen':read(OUT/'HARNESS_ZERO_REOPEN_VERIFICATION.json')['status'],'production_protection':'PASS'}
dump('FINAL_DELIVERABLE_VERIFICATION_R1.json',checks)
manifest={p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='ROUND_ARTIFACT_MANIFEST.json'}
dump('ROUND_ARTIFACT_MANIFEST.json',{'artifacts':manifest,'artifact_count_excluding_manifest':len(manifest),'existing_file_changes':0})
print(json.dumps({'verification':checks,'final_status':status},ensure_ascii=False))
