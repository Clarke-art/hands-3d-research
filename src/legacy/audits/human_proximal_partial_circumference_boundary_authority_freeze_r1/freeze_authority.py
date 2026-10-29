"""Freeze one Human-approved boundary. Read-only history; no geometry/solver work."""
import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
RUN='HUMAN_PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_AUTHORITY_FREEZE_R1'
AUTH='PROXIMAL_PARTIAL_CIRCUMFERENCE_SEMANTIC_BOUNDARY_AUTHORITY_R1'
REVIEW='PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_HUMAN_REVIEW_R1'
NEXT='R3_RECOVERY_INPUT_CONTRACT_FINALIZATION_R1'
HUMAN=Path(r'<USER_HOME>\Downloads\PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_HUMAN_REVIEW_R1_RESPONSE_2026-10-03T09-05-56-031Z.json')
PRIOR=ROOT/'audits/proximal_partial_circumference_semantic_boundary_authority_r1'
def unique_pairs(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise ValueError('duplicate JSON key: '+k)
  d[k]=v
 return d
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'),object_pairs_hook=unique_pairs)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(name,data):(OUT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
def canonical(data):return json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf8')
def inventory():return {str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and OUT not in p.parents and '.git' not in p.parts}
def exactly(actual,expected):
 if type(actual) is not type(expected):return False
 if isinstance(expected,list):return len(actual)==len(expected) and all(exactly(a,b) for a,b in zip(actual,expected))
 if isinstance(expected,dict):return actual.keys()==expected.keys() and all(exactly(actual[k],v) for k,v in expected.items())
 return actual==expected
checks=[]
def ck(name,passed,actual=None):
 checks.append({'name':name,'passed':bool(passed),'actual':actual})
def require_all():
 if any(not c['passed'] for c in checks):
  dump('HUMAN_RESPONSE_VERIFICATION_R1.json',{'verified':False,'status':'FAIL_CLOSED','checks':checks,'freeze_permitted':False})
  dump(RUN+'_STATUS.json',{'status':'FAIL_CLOSED','Human_response_verified':False,'freeze_performed':False,'NEXT':None,'STOP':True})
  raise SystemExit('FAIL_CLOSED: no authority freeze permitted; inspect verification output.')

ext=set(read(PRIOR/'FROZEN_HASHES_AFTER.json')['external'])
ext.add(str(HUMAN));ext.add(r'<USER_HOME>\.codex\attachments\41454178-5d22-45f5-928e-9c4cfa90559a\已粘贴的文本.txt')
baseline={'workspace':inventory(),'external':{p:sha(p) for p in sorted(ext)}}
if not (OUT/'FROZEN_HASHES_BEFORE.json').exists():dump('FROZEN_HASHES_BEFORE.json',baseline)
before=read(OUT/'FROZEN_HASHES_BEFORE.json')
ck('existing frozen baseline matches invocation',before==baseline)
try:human=read(HUMAN)
except (ValueError,OSError) as e:
 ck('Human JSON readable, valid and duplicate-free',False,str(e));require_all()
required={'review_id':REVIEW,'authority_id':AUTH,'selected_option':'B','Q1_P02_digit_web_acceptable':'YES','Q2_P06_broader_interface_acceptable':'YES','Q4_native_RSSF_context_acceptable':'YES','Q5_approve_for_boundary_authority':'APPROVE_BOUNDARY_ONLY','approved_for_boundary_authority':True,'authority_scope':'THUMB_SHARED_STRIP_PROXIMAL_SEMANTIC_STOP_ONLY','response_kind':'HUMAN_ANATOMICAL_ADJUDICATION_RESPONSE','validation_mode':False,'applies_production_changes':False,'frozen_membership_changes':False,'automatic_role_extension':False,'automatic_solver_execution':False,'first_web_hard_pin_count':0}
for k,v in required.items():ck('Human '+k,exactly(human.get(k),v),human.get(k))
boundary={'option':'B','stop':'STOP_AFTER_P04','distal_row':'P04','proximal_row':'P05','left_boundary_edge_id':4666,'right_boundary_edge_id':4668,'boundary_vertex_ids':[[1444,2822],[1520,2822]],'incident_face_transitions':[[1368,1369],[1371,1370]]}
for k,v in boundary.items():ck('Human Q3 '+k,exactly(human.get('Q3_selected_boundary',{}).get(k),v),human.get('Q3_selected_boundary',{}).get(k))
ck('Human notes preserved as text',isinstance(human.get('notes'),str) and len(human['notes'])>0)
try:datetime.fromisoformat(human['timestamp'].replace('Z','+00:00'));stamp_ok=True
except (ValueError,KeyError,TypeError):stamp_ok=False
ck('Human timestamp valid',stamp_ok,human.get('timestamp'))
require_all()
human_hash=sha(HUMAN)
specs=[
 ('thumb_frozen_web_partial_circumference_frontier_authority_r1','THUMB_FROZEN_WEB_PARTIAL_CIRCUMFERENCE_FRONTIER_AUTHORITY_R1','Frozen seeds and original columns4–6 diagnostic context; historical FAIL_CLOSED, no extension approval.'),
 ('thumb_shared_strip_longitudinal_stop_rule_authority_r1','THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY_R1','Existing distal hard-stop conflict evidence and longitudinal strip IDs; retain prior candidate/evidence status.'),
 ('narrow_proximal_web_to_palm_transition_authority_r1','NARROW_PROXIMAL_WEB_TO_PALM_TRANSITION_AUTHORITY_R1','Fixed three proximal alternatives and local transition evidence; historical FAIL_CLOSED remains unchanged.'),
 ('proximal_partial_circumference_semantic_boundary_authority_r1',AUTH,'Exact-face evidence and Human review; machine NONE/exhausted YES retained, not machine-proved B.')]
chain=[];statuses=[]
for i,(directory,authority,role) in enumerate(specs,1):
 source=ROOT/'audits'/directory;sp=source/(authority+'_STATUS.json');st=read(sp);statuses.append(st)
 manifest=source/'OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json'
 for name,digest in read(manifest)['files'].items():ck('historical manifest '+directory+'/'+name,sha(source/name)==digest)
 chain.append({'order':i,'authority_id':authority,'path':str(sp),'workspace_relative_path':str(sp.relative_to(ROOT)),'hash':sha(sp),'hash_algorithm':'SHA-256','status':st.get('status',st.get('authority_status')),'role_in_final_authority':role,'supporting_artifacts':[{'path':str(source/(authority+'_REPORT.md')),'hash':sha(source/(authority+'_REPORT.md'))},{'path':str(manifest),'hash':sha(manifest)}]})
machine=statuses[-1]
ck('historical machine unique candidate NONE',machine['machine_unique_candidate']=='NONE')
ck('historical machine evidence exhausted YES',machine['machine_evidence_exhausted']=='YES')
selected=next(c for c in read(PRIOR/'THREE_BOUNDARY_ROLE_CHANGE_COMPARISON.json')['candidates'] if c['option']=='B')
ck('Human boundary matches frozen Option B evidence',selected['stop']==boundary['stop'] and selected['row_pair']==['P04','P05'] and [e['edge_id'] for e in selected['boundary_edges']]==[4666,4668] and [e['vertex_ids'] for e in selected['boundary_edges']]==boundary['boundary_vertex_ids'] and [[e['before_face_id'],e['after_face_id']] for e in selected['boundary_edges']]==boundary['incident_face_transitions'])
ck('B not relabeled machine-proved',selected['ROLE_CHANGE_PROVEN'] is False)
require_all()
chain.append({'order':5,'authority_id':AUTH,'review_id':REVIEW,'path':str(HUMAN),'hash':human_hash,'hash_algorithm':'SHA-256','status':'HUMAN_APPROVED_BOUNDARY_ONLY','selected_option':'B','stop':'STOP_AFTER_P04','human_timestamp':human['timestamp'],'role_in_final_authority':'Sole Human adjudication input and direct approval basis for this proximal semantic boundary.'})
provenance={'authority_id':AUTH,'items':chain,'sole_Human_approval_input':str(HUMAN),'historical_evidence_is_not_new_Human_approval':True,'machine_unique_candidate':'NONE','machine_evidence_exhausted':'YES','human_selected_option':'B','machine_proved_B':False}
dump('PROXIMAL_BOUNDARY_AUTHORITY_PROVENANCE_CHAIN.json',provenance)
chain_hash=sha(OUT/'PROXIMAL_BOUNDARY_AUTHORITY_PROVENANCE_CHAIN.json')
distal=statuses[1]
distal_retained={'source_path':chain[1]['path'],'source_hash':chain[1]['hash'],'nail_side_stop':distal['distal_nail_side_stop'],'nail_side_rule':'STOP_BEFORE_FACE1177_NAIL_V304','non_nail_stop':distal['distal_non_nail_stop'],'non_nail_final_row':distal['distal_non_nail_final_row'],'non_nail_last_safe_faces':distal['distal_non_nail_last_safe_faces'],'next_forbidden_face':distal['distal_non_nail_first_forbidden_face'],'cap37_conflict_vertex_ids':distal['distal_non_nail_cap_conflict_ids'],'status_treatment':'PRIOR_EVIDENCE_OR_CANDIDATE_UNCHANGED','upgraded_to_new_Human_frozen_authority':False,'positive_shared_role_approval':False}
excluded=['lateral frontier','shared-role extension','four-role global map','tube radius','thumb strong anchors','R3 graph','R3 unary','skin weights','Stage6','CORRECTED_MM cost authority']
authority={'authority_id':AUTH,'status':'HUMAN_APPROVED_FROZEN','authority_type':'BOUNDARY_AUTHORITY','selected_option':'B',**{k:v for k,v in boundary.items() if k!='option'},'authority_scope':required['authority_scope'],'LAST_ACCEPTED_DIGIT_WEB_SIDE':'P04','FIRST_ACCEPTED_BROADER_INTERFACE_SIDE':'P05','PROXIMAL_STOP':'FROZEN','human_response_path':str(HUMAN),'human_response_hash':human_hash,'human_review_id':REVIEW,'human_timestamp':human['timestamp'],'human_notes':human['notes'],'provenance_chain_hash':chain_hash,'native_RSSF_context_accepted':True,'P02_digit_web_control_Human_accepted':True,'P06_broader_interface_control_Human_accepted':True,'machine_unique_candidate':'NONE','machine_evidence_exhausted':'YES','machine_proved_B':False,'first_web_membership_changed':False,'first_web_hard_pin_count':0,'cap37_changed':False,'nail_changed':False,'automatic_role_extension':False,'automatic_solver_execution':False,'applies_production_changes':False,'FULL_ROLE_MAP_AUTHORITY':False,'all_P04_vertices_THUMB_EXCLUSIVE':False,'all_P05_vertices_SHARED_NEUTRAL':False,'whole_palm_role_determined':False,'LATERAL_FRONTIER':'UNRESOLVED','ROLE_EXTENSION':'NOT_YET_FORMED','FOUR_ROLE_MAP':'UNRESOLVED','R3':'NOT_RUN','excluded_from_approval':excluded,'distal_authority_retained':distal_retained}
payload=canonical(authority);combined_hash=hashlib.sha256(payload).hexdigest()
trigger={'record_id':'DOWNSTREAM_LATERAL_FRONTIER_TRIGGER','record_status':'ROUTE_REVISED_BY_LATEST_USER_MESSAGE','NEXT':NEXT,'execute_now':False,'automatic_solver_execution':False,'STOP_after_this_freeze':True,'previous_next':'NARROW_THUMB_SHARED_SECTOR_LATERAL_FRONTIER_CONFIRMATION_R1','independent_lateral_face_authority_audit_will_start':False,'lateral_frontier_anatomical_authority_status':'UNRESOLVED','proximal_boundary_authority_path':str(OUT/(AUTH+'.json')),'proximal_boundary_authority_hash':combined_hash,'proximal_stop':'STOP_AFTER_P04','boundary':['P04','P05'],'distal_stop_evidence':distal_retained,'conservative_engineering_transition_band':{'existing_columns':[4,5,6],'intended_next_contract_role':'SHARED_NEUTRAL_TRANSITION_BAND','basis':'LATEST_EXPLICIT_USER_ROUTE_REVISION','usage_status':'RECORD_FOR_NEXT_INPUT_CONTRACT_ONLY','anatomical_FIRST_WEB_membership':False,'FIRST_WEB21_membership_changes':False,'THUMB_hard_pin':False,'INDEX_hard_pin':False,'hard_pin_count':0,'anatomical_lateral_frontier_approved':False,'formal_shared_role_extension_generated':False,'new_vertex_or_face_role_map_generated':False},'next_contract_scope':['corrected kinematics','cap37','Human-approved P04/P05 proximal stop','existing distal hard-stop evidence','conservative shared-neutral transition band','INDEX sources','nail/cage wrappers','CORRECTED_MM cost semantics'],'contract_generated_this_run':False,'cost_authority_approved_this_run':False,'R3_recompute_run_this_run':False,'no_reopening_proximal_stop':True,'authorization_source':'Latest user message: 重要路线修订; supersedes older lateral-frontier NEXT, not the Human boundary scope.'}
dump('DOWNSTREAM_LATERAL_FRONTIER_TRIGGER.json',trigger)
dump('ROUTE_REVISION_R1.json',{'authority_source':'LATEST_DIRECT_USER_MESSAGE','NEXT':NEXT,'independent_lateral_authority_audit':'DO_NOT_START','columns4_to6':'CONSERVATIVE_ENGINEERING_SHARED_NEUTRAL_TRANSITION_BAND_FOR_NEXT_INPUT_CONTRACT','anatomical_membership_change':False,'hard_pins':0,'role_extension_created':False,'automatic_next_execution':False,'STOP':True})
after={'workspace':inventory(),'external':{p:sha(p) for p in before['external']}}
ck('all existing workspace and external files before == after',before==after)
ck('Human bytes unchanged after verification',sha(HUMAN)==human_hash)
require_all()
dump('FROZEN_HASHES_AFTER.json',after)
protection={'before_equals_after':True,'workspace_file_count':len(before['workspace']),'external_file_count':len(before['external']),'changed_files':[],'removed_files':[],'added_outside_new_audit_directory':[],'historical_files_modified':False,'blend_files_modified':False,'BLEND_FILES_WRITTEN':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'R2_runs':0,'R3_runs':0,'Stage6_runs':0,'scope':'Every pre-existing workspace file except .git and all inherited external Human/reference inputs plus this exact response and request attachment. No scripts or solvers from history imported/executed.'}
dump('FROZEN_HASH_VERIFICATION_R1.json',protection)
# Commit the frozen boundary only after every response/provenance/protection check passed.
dump(AUTH+'.json',authority)
(OUT/'PROXIMAL_BOUNDARY_AUTHORITY_CANONICAL.json').write_bytes(payload)
ck('canonical serialization is deterministic UTF8 sorted keys',canonical(read(OUT/(AUTH+'.json')))==payload)
ck('combined authority hash reproducible from canonical bytes',sha(OUT/'PROXIMAL_BOUNDARY_AUTHORITY_CANONICAL.json')==combined_hash)
require_all()
dump('PROXIMAL_BOUNDARY_AUTHORITY_HASH.json',{'authority_id':AUTH,'algorithm':'SHA-256','canonicalization':'JSON UTF-8; recursively sorted object keys; compact separators comma/colon; ensure_ascii=false; allow_nan=false; no BOM; no trailing newline. Array order retained.','canonical_payload_path':str(OUT/'PROXIMAL_BOUNDARY_AUTHORITY_CANONICAL.json'),'canonical_payload_size_bytes':len(payload),'combined_authority_hash':combined_hash,'authority_file_path':str(OUT/(AUTH+'.json')),'authority_file_hash':sha(OUT/(AUTH+'.json')),'human_response_path':str(HUMAN),'human_response_hash':human_hash,'human_response_hash_basis':'Raw original file bytes, not reserialized JSON','provenance_chain_hash':chain_hash,'hash_embedded_in_payload':False})
dump('HUMAN_RESPONSE_VERIFICATION_R1.json',{'verified':True,'freeze_permitted':True,'Human_response_path':str(HUMAN),'Human_response_hash':human_hash,'check_count':len(checks),'checks':checks,'notes_preserved_verbatim':True,'no_other_Human_response_used_to_select_boundary':True})
status={'run':RUN,'authority_id':AUTH,'status':'HUMAN_APPROVED_FROZEN','Human_response_verified':'YES','selected_option':'B','PROXIMAL_STOP':'STOP_AFTER_P04','proximal_stop_authority_state':'FROZEN','BOUNDARY':['P04','P05'],'distal_row':'P04','proximal_row':'P05','LEFT_EDGE':4666,'RIGHT_EDGE':4668,'incident_face_transitions':boundary['incident_face_transitions'],'authority_scope':required['authority_scope'],'human_response_hash':human_hash,'combined_authority_hash':combined_hash,'machine_unique_candidate':'NONE','machine_evidence_exhausted':'YES','machine_proved_B':False,'FIRST_WEB21_changed':'NO','cap37_changed':'NO','nail_changed':'NO','first_web_hard_pin_count':0,'role_extension_generated':'NO','ROLE_EXTENSION':'NOT_YET_FORMED','LATERAL_FRONTIER':'UNRESOLVED','FOUR_ROLE_MAP':'UNRESOLVED','R3':'NOT_RUN','CORRECTED_COMMON_MM_SEMANTICS':machine['CORRECTED_COMMON_MM_SEMANTICS'],'distal_authority_upgraded':False,'conservative_columns4_to6_route_recorded':True,'input_contract_generated':False,'independent_lateral_audit_started':False,'frozen_protection':protection,'NEXT':NEXT,'automatic_next_execution':False,'STOP':True}
dump(RUN+'_STATUS.json',status)
report=f'''# {RUN}

Human response verified = YES。Option B 的 proximal semantic boundary 已建立为 **HUMAN_APPROVED_FROZEN**：STOP_AFTER_P04，P04 / P05，e4666 / e4668；面转换 1368→1369、1371→1370。这是 Human boundary authority，不是 full role map authority。

唯一 Human input：`{HUMAN}`。逐字段、逐类型验证 review/authority IDs、B、Q1/Q2/Q4 YES、Q3 原始边对/顶点/面转换、Q5 APPROVE_BOUNDARY_ONLY、批准布尔值与全部 scope/禁止自动执行字段。JSON 重复键被拒绝；timestamp 有效；Human notes 原文保留。共 {len(checks)} 项 response、历史 manifest、来源一致性及冻结检查通过。

Human response SHA-256：`{human_hash}`。combined authority SHA-256：`{combined_hash}`。PROXIMAL_BOUNDARY_AUTHORITY_HASH.json 记录原始 response 字节 hash、provenance chain hash、pretty authority 文件 hash 和 canonical serialization 规则。canonical payload 为 UTF-8、递归 sort_keys、紧凑 separators、无 BOM/末尾换行；保留数组顺序。combined hash 覆盖全部 authority payload（包括 Human approval、边界、scope、notes、禁令和 provenance hash），不自包含该 hash。

Human 接受 P04 侧仍可作为 digit-web / partial-circumference side、P05 侧开始作为 broader shared-interface context，供后续 shared-strip assembly 使用。未把 P04 所有顶点赋为 THUMB_EXCLUSIVE，也未把 P05 所有顶点赋为 SHARED_NEUTRAL，未建立整个 palm role。P02/P06 接受来自 Human adjudication；历史 machine unique candidate=NONE、machine evidence exhausted=YES、machine proved B=false 原样保留，历史 role map 未改写。

正式五项 provenance chain：frozen web partial-circumference frontier → longitudinal stop evidence → narrow proximal transition evidence → exact-face semantic boundary review → 本次原始 Human response。每项记录 path、SHA-256、历史 status、role in final authority，历史 supporting reports/manifests 同时绑定。四个历史输出 manifests 均校验一致；没有导入或执行历史脚本。

FIRST_WEB21 membership 不变，hard pin count=0；cap37、nail、corrected rig、CMC cage 均受保护。Human notes 排除的 lateral frontier、shared-role extension、four-role global map、tube radius、thumb strong anchors、R3 graph/unary、skin weights、Stage6、CORRECTED_MM cost authority 均未升级。LATERAL_FRONTIER=UNRESOLVED，ROLE_EXTENSION=NOT_YET_FORMED，FOUR_ROLE_MAP=UNRESOLVED，R3=NOT_RUN；CORRECTED_COMMON_MM_SEMANTICS 保持 {machine['CORRECTED_COMMON_MM_SEMANTICS']}。

distal 仅保留既有 evidence/status：nail-side stop=RESOLVED，在 face1177/nail v304 前停止；non-nail 为 D04/face1226，下一面1227触及 cap37 v298/v1454，其状态仍是 {distal['distal_non_nail_stop']}。本轮不升级成新的 Human frozen distal authority，也不把 conflict stop evidence 当作 positive shared-role approval。

最新用户路线修订覆盖旧 NEXT。不再启动 lateral frontier 的独立逐面 authority 审计。columns4–6 仅记录为下一轮使用的 conservative engineering SHARED_NEUTRAL transition band，其身份不等于 anatomical FIRST_WEB membership，不是 THUMB/INDEX hard pin；本轮未生成 band role map 或正式 role extension。DOWNSTREAM_LATERAL_FRONTIER_TRIGGER.json 保留原要求的文件名，但其内容明确采用修订路线且 execute_now=false。

唯一 NEXT = **{NEXT}**。下一轮目标：收束 corrected kinematics、cap37、Human-approved P04/P05 proximal stop、已有 distal hard-stop evidence、conservative shared-neutral band、INDEX sources、nail/cage wrappers 与 CORRECTED_MM cost semantics，形成一次性的 R3 recompute input contract。本轮未生成该 contract，未执行 R3，也没有重新研究 proximal stop。

既有 {len(before['workspace'])} 个 workspace 文件、{len(before['external'])} 个外部来源文件全部 before hash == after hash；任何历史 Human response、audit、.blend、Stage4/5、R2/R3、Stage6 均未修改。本轮新增 workspace 文件只在本 audit 目录。BLEND_FILES_WRITTEN=0；WEIGHT/GEOMETRY/TOPOLOGY/BONE/JOINT_DELTA=0；R2/R3/Stage6 runs=0。

完成本次 Human authority freeze，STOP=YES。不得自动开始任何下游任务。
'''
(OUT/(RUN+'_REPORT.md')).write_text(report,encoding='utf8')
dump('OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json',{'scope':'This new freeze directory only; manifest excludes itself.','files':{str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json'}})
print(json.dumps({'Human_response_verified':'YES','status':status['status'],'human_response_hash':human_hash,'combined_authority_hash':combined_hash,'checks':len(checks),'frozen_workspace_files':len(before['workspace']),'frozen_external_files':len(before['external']),'NEXT':NEXT,'STOP':True},indent=2))
