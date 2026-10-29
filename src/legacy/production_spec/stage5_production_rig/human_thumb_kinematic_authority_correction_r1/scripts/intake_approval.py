from pathlib import Path
import json,hashlib,sys,datetime
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2];PRIOR=OUT.parent/'cap_derived_thumb_kinematic_authority_revalidation_r1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def combined(d):return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
assert not (OUT/'RIGHT_HAND_STAGE5A_PRODUCTION_RIG_THUMB_KINEMATIC_CORRECTED_R1.blend').exists()
checks=[];oldmanifest=read(PRIOR/'OUTPUT_VERIFICATION.json')
for n in ['KINEMATIC_CANDIDATE_R1.json','RAW_READ_ONLY_GEOMETRY_AND_BONES.json','GEOMETRIC_EVIDENCE_COMPUTATION.json','STATIC_GEOMETRY_GATES_AND_FRAME_METRICS.json']:
 p=PRIOR/n;h=sha(p);assert h==oldmanifest['output_hashes'][n];checks.append({'path':str(p.relative_to(ROOT)),'sha256':h,'matches_prior_review_manifest':True})
cap_path=OUT.parent/'stage5b_r1e_human_cap_authority_freeze_r1/THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1.json';cap=read(cap_path)
assert combined({k:v for k,v in cap.items() if k!='combined_authority_hash'})==cap['combined_authority_hash']=='c81dd96d6925ed402cdf0ba44c148d7a78c2c60640fe23fb6247fb729f346cc8'
assert cap['status']=='HUMAN_APPROVED_FROZEN' and len(cap['vertex_ids'])==37 and len(cap['face_ids'])==25
input_rig=OUT.parent/'stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend';h=sha(input_rig);assert h=='c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845'
cand=read(PRIOR/'KINEMATIC_CANDIDATE_R1.json');allowed=['THUMB_IP_R.tail','THUMB_IP_R.roll','THUMB_TIP_R.head','THUMB_TIP_R.tail','THUMB_TIP_R.roll']
assert {n for n,s in cand['slots'].items() if s['classification']=='CHANGE_REQUIRED'}==set(allowed)
assert cand['slots']['THUMB_IP_R.head']['classification']=='REVALIDATED_UNCHANGED'
decision={'record_id':'HUMAN_THUMB_KINEMATIC_APPROVAL_R1','source_type':'DIRECT_USER_MESSAGE_IN_CURRENT_CODEX_CHAT','source_client_date':'2026-10-03','source_timezone':'Asia/Shanghai','source_copy':'HUMAN_DECISION_SOURCE_R1.txt','source_copy_sha256':sha(OUT/'HUMAN_DECISION_SOURCE_R1.txt'),'source_copy_note':'UTF-8 transcription of the received Human message; hash covers this saved transcription, not a transport-level chat signature.','overall_decision':'THUMB_KINEMATIC_AUTHORITY_CORRECTION = HUMAN_APPROVED','scope':'thumb distal IP/TIP kinematic authority only','slot_decisions':{n:('KEEP CURRENT / REVALIDATED_UNCHANGED' if n=='THUMB_IP_R.head' else 'APPROVE CORRECTED CANDIDATE') for n in cand['slots']},'candidate_id':cand['candidate_id'],'candidate_path':str((PRIOR/'KINEMATIC_CANDIDATE_R1.json').relative_to(ROOT)),'candidate_sha256':sha(PRIOR/'KINEMATIC_CANDIDATE_R1.json'),'authorized_slot_writes':allowed,'scope_exclusions':['R2','R3','skin weights','Stage5B','Stage6A','Stage6B','strict-bound results'],'forbidden_runs':['R2','R3','skin rebuild','Stage6'],'R1F_creation_authorized':False,'NEXT':'CAP_DERIVED_R2_R3_INPUT_RECONCILIATION_R1','STOP_AFTER_COMPLETION':True}
decision['combined_approval_hash']=combined(decision);dump('HUMAN_THUMB_KINEMATIC_APPROVAL_R1.json',decision)
authority={'authority_id':'THUMB_DISTAL_IP_TIP_KINEMATIC_CORRECTION_AUTHORITY_R1','status':'HUMAN_APPROVED','authority_scope':'six thumb distal IP/TIP slots: retained IP head plus five approved corrections','human_approval_record':'HUMAN_THUMB_KINEMATIC_APPROVAL_R1.json','human_approval_combined_hash':decision['combined_approval_hash'],'approved_candidate_path':decision['candidate_path'],'approved_candidate_sha256':decision['candidate_sha256'],'coordinate_contract':cand['units'],'slots':cand['slots'],'slot_application_rule':'Copy the five approved slot values exactly; preserve IP head bitwise; no geometric refit or selector rerun. Float32 storage rounding is measured separately from authority value.','supersedes':'R2A old cap-derived distal endpoint/roll authority only; historical artifacts remain frozen','old_cap_REP_authority':'SUPERSEDED_CONTAMINATED; NOT_AUTHORITY','cap37_combined_authority_hash':cap['combined_authority_hash'],'cap37_semantics':'SURFACE MEMBERSHIP ONLY; unchanged','input_rig_path':str(input_rig.relative_to(ROOT)),'input_rig_sha256':h,'corrected_rig_path':str((OUT/'RIGHT_HAND_STAGE5A_PRODUCTION_RIG_THUMB_KINEMATIC_CORRECTED_R1.blend').relative_to(ROOT)),'corrected_rig_scope':'New skeleton-only derivative for these approved slots; downstream consumers remain unreconciled','scope_exclusions':decision['scope_exclusions'],'NEXT':decision['NEXT']}
authority['combined_authority_hash']=combined(authority);dump('THUMB_DISTAL_IP_TIP_KINEMATIC_CORRECTION_AUTHORITY_R1.json',authority)
protected=read(PRIOR/'FROZEN_HASHES_BEFORE.json')['external']
files=[p for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents and '.git' not in p.parts]
dump('FROZEN_HASHES_BEFORE.json',{'workspace':{str(p.relative_to(ROOT)):sha(p) for p in files},'external':{p:sha(Path(p)) for p in protected}})
dump('APPROVAL_INPUT_VERIFICATION.json',{'candidate_and_evidence_checks':checks,'source_rig_sha256':h,'cap37_verified':True,'cap37_vertices':37,'cap37_faces':25,'protected_workspace_file_count':len(files),'protected_external_file_count':len(protected),'approval_record_hash':sha(OUT/'HUMAN_THUMB_KINEMATIC_APPROVAL_R1.json'),'authority_record_hash':sha(OUT/'THUMB_DISTAL_IP_TIP_KINEMATIC_CORRECTION_AUTHORITY_R1.json')})
print('APPROVAL_AND_AUTHORITY_RECORDED; protected',len(files),'workspace files +',len(protected),'external inputs')
