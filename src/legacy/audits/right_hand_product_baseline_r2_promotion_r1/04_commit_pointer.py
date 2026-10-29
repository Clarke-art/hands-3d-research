"""Commit only after exact identity and smoke PASS. Preserve exact old pointer for rollback."""
from pathlib import Path
import json,hashlib,os,copy
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PHASE='RIGHT_HAND_PRODUCT_BASELINE_R2_PROMOTION_R1'
POINTER=ROOT/'production_spec/RIGHT_HAND_PRODUCT_BASELINE.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
I=read(OUT/'PROMOTION_IDENTITY_R1.json');C=read(OUT/'CANDIDATE_CONTAINER_INSPECTION_R1.json');S=read(OUT/'SMOKE_VISIBLE_COMPARISON_R1.json')
assert I['status']=='PASS' and I['WEIGHT_FIELD_IDENTITY']=='EXACT_MATCH' and all(I['core_component_exact_match'].values()) and S['status']=='PASS'
assert I['R2_CONTAINER_STATUS']=='PRODUCTION_CLEAN' and all(x['status']=='PASS' for x in I['smoke_checks'])
assert sha(POINTER)==C['production_pointer_before_sha256']
for path,expected in C['protected_inputs_before'].items():assert sha(ROOT/path)==expected,path
assert sha(ROOT/I['R2_baseline']['path'])==I['R2_baseline']['sha256']
request=Path('<USER_HOME>/.codex/attachments/0400bd0c-c4cf-459d-8b81-785cb38f9bc4/已粘贴的文本.txt')
QUAL=ROOT/'audits/right_hand_first_web_production_weight_qualification_r1'
q=read(QUAL/'RIGHT_HAND_FIRST_WEB_PRODUCTION_WEIGHT_QUALIFICATION_R1_STATUS.json')
assert q['PRODUCTION_QUALIFICATION']=='PASS' and q['candidate_sha256']==I['approved_candidate']['actual_sha256']
approval={'PHASE':PHASE,'authority':'Direct current Human final production approval and promotion instruction, supplied through pasted task attachment','request_path':str(request),'request_sha256':sha(request),'approval_date_client_timezone':'2026-10-07 Asia/Shanghai','RIGHT_HAND_FIRST_WEB_PRODUCTION_WEIGHT_QUALIFICATION_R1':'HUMAN_APPROVED','HUMAN_PRODUCTION_APPROVAL':'APPROVED','FIRST_WEB_HUMAN_VISIBLE_BLOCKER':'CLOSED','NEW_HUMAN_VISIBLE_REGRESSION':'NO','PRODUCTION_PROMOTION':'AUTHORIZED','approved_candidate':I['approved_candidate'],'human_reviewed_video':{'path':(QUAL/'product_7s_matched_reasonable_close_view.mp4').relative_to(ROOT).as_posix(),'sha256':sha(QUAL/'product_7s_matched_reasonable_close_view.mp4')},'human_reviewed_qualification_report':{'path':(QUAL/'RIGHT_HAND_FIRST_WEB_PRODUCTION_WEIGHT_QUALIFICATION_R1_REPORT.md').relative_to(ROOT).as_posix(),'sha256':sha(QUAL/'RIGHT_HAND_FIRST_WEB_PRODUCTION_WEIGHT_QUALIFICATION_R1_REPORT.md')},'scope':'Exact approved deformation state only. No weight/mesh/rig/Action/corrective/driver modification; no left hand or Web export.','prior_pending_history_preserved':True}
dump(OUT/'HUMAN_APPROVAL_BIND_R1.json',approval)
# Independent byte-exact backup of the old pointer, with no change to historical files.
old_bytes=POINTER.read_bytes();(OUT/'PRODUCTION_POINTER_BEFORE_R1.json').write_bytes(old_bytes)
assert sha(OUT/'PRODUCTION_POINTER_BEFORE_R1.json')==C['production_pointer_before_sha256']
old=read(POINTER);new=copy.deepcopy(old)
new.update({
 'authority':'Direct Human final production approval and R2 promotion request, 2026-10-07',
 'CURRENT_PRODUCTION_BASELINE':'R2','PREVIOUS_PRODUCTION_BASELINE':'R1',
 'RIGHT_HAND_PRODUCT_BASELINE_STATUS':'HUMAN_APPROVED_FROZEN',
 'RIGHT_HAND_PRODUCT_BASELINE_R2':'HUMAN_APPROVED_FROZEN','RIGHT_HAND_PRODUCT_BASELINE_R1':'HISTORICAL_FROZEN_FALLBACK',
 'asset':I['R2_baseline'].copy(),'source':{'path':I['approved_candidate']['path'],'sha256':I['approved_candidate']['actual_sha256']},
 'historical_frozen_fallback':{'path':old['asset']['path'],'sha256':old['asset']['sha256'],'status':'HISTORICAL_FROZEN_FALLBACK','permanent_retention':True,'rollback_available':True},
 'mesh':'Official L1, 3300 vertices, 3298 faces','bone_count':21,'deform_bone_count':16,'non_deform_TIP':I['TIP_non_deform'],
 'WEIGHT_FIELD_IDENTITY':'EXACT_MATCH_APPROVED_FULL_VECTOR_STATIC_FIELD','weight_field_sha256':I['weight_field_sha256'],
 'FIRST_WEB_HUMAN_VISIBLE_BLOCKER':'CLOSED','RIGHT_HAND_DEFORMATION':'CLOSED','RIGHT_HAND_DEFORMATION_CLOSED':'YES',
 'STATIC_WEIGHT_FIELD_PROBLEM':'RESOLVED_IN_R2','RIGHT_HAND_READY_FOR_LEFT_HAND_STAGE':'YES',
 'HUMAN_PRODUCTION_APPROVAL':'APPROVED','PRODUCTION_PROMOTION':'COMPLETE',
 'motion_gate':'PASS_HUMAN_APPROVED_PRODUCTION_WEIGHT_QUALIFICATION_R1',
 'left_hand_and_Web_gate':'WAIT_FOR_NEXT_HUMAN_STAGE_AUTHORIZATION',
 'LEFT_HAND_STARTED':False,'WEB_EXPORT_STARTED':False,'PIANOVAM_RUNTIME_DEPENDENCY':False,
 'qualification_evidence':{'phase':'RIGHT_HAND_FIRST_WEB_PRODUCTION_WEIGHT_QUALIFICATION_R1','status':'HUMAN_APPROVED','report':approval['human_reviewed_qualification_report']['path'],'video':approval['human_reviewed_video']['path']},
 'promotion_record':(OUT/'PROMOTION_IDENTITY_R1.json').relative_to(ROOT).as_posix(),
 'human_approval_record':(OUT/'HUMAN_APPROVAL_BIND_R1.json').relative_to(ROOT).as_posix(),
 'report':(OUT/(PHASE+'_REPORT.md')).relative_to(ROOT).as_posix(),
 'status':'production_spec/right_hand_product_baseline_r2/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2_STATUS.json',
 'historical_assets_deleted_or_overwritten':False})
tmp=OUT/'_tmp';tmp.mkdir(exist_ok=True)
staged=tmp/'RIGHT_HAND_PRODUCT_BASELINE_R2_POINTER.json';dump(staged,new)
assert read(staged)==new and sha(POINTER)==C['production_pointer_before_sha256']
os.replace(staged,POINTER)
assert read(POINTER)==new and sha(ROOT/new['asset']['path'])==new['asset']['sha256']
assert sha(ROOT/new['historical_frozen_fallback']['path'])==new['historical_frozen_fallback']['sha256']
dump(OUT/'PRODUCTION_POINTER_UPDATE_R1.json',{'PHASE':PHASE,'status':'PASS','pointer_path':POINTER.relative_to(ROOT).as_posix(),'PREVIOUS_PRODUCTION_BASELINE':'R1','CURRENT_PRODUCTION_BASELINE':'R2','identity_and_smoke_verified_before_update':True,'before_sha256':C['production_pointer_before_sha256'],'after_sha256':sha(POINTER),'before':old,'after':new,'old_pointer_byte_exact_backup':'PRODUCTION_POINTER_BEFORE_R1.json','R1_role':'HISTORICAL_FROZEN_FALLBACK','R1_permanently_retained':True,'new_asset_sha_matches':True,'promotion_authority':'HUMAN_APPROVAL_BIND_R1.json','atomic_replace_used':True})
print('PRODUCTION_POINTER_COMMITTED_R1_TO_R2',new['asset']['sha256'],flush=True)
