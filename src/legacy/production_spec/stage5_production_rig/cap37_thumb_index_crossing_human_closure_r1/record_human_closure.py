"""Record the explicit user Human decision; hash-only verification, no deformation run."""
import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
S5=ROOT/'production_spec/stage5_production_rig'
CAUSAL=S5/'cap37_thumb_index_crossing_causal_adjudication_r1'
TARGET=S5/'cap_fixture_static_validation_and_targeted_deformation_r1'
R2=S5/'targeted_rig_and_skin_data_rebuild_r2/RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R2.blend'
EXPECTED='adf757aeace8a0d69070b94f102b9bef9eb99da9847dd7a5639c4c2c3799dde9'
VECTOR='1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55'
PHASE='CAP_FIXTURE_STATIC_VALIDATION_AND_TARGETED_DEFORMATION_R1'
MACHINE='VALIDATOR_SEMANTIC_ESCALATION_REQUIRES_HUMAN_ADJUDICATION'
DISPOSITION='ACCEPTED_NON_BLOCKING_DIAGNOSTIC_CONTACT'
PASS='PASS_WITH_HUMAN_ACCEPTED_NON_BLOCKING_DIAGNOSTIC_CONTACT'
NEXT='TRUE_CAP_BOUND_RECOMPUTE_AFTER_DEPENDENCY_RECONCILIATION'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def inventory():return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
def write(name,d):
 with (OUT/name).open('x',encoding='utf-8') as f:f.write(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n' if isinstance(d,dict) else d)
def ref(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}

assert not (OUT/'TARGETED_DEFORMATION_HUMAN_CLOSURE_R1.json').exists(),'Closure already exists; do not overwrite.'
before=inventory();write('HISTORICAL_HASHES_BEFORE.json',before)
ts=read(TARGET/(PHASE+'_STATUS.json'));cs=read(CAUSAL/'CAP37_THUMB_INDEX_CROSSING_CAUSAL_ADJUDICATION_R1_STATUS.json')
prior_verify=read(CAUSAL/'PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json')
matrix=read(CAUSAL/'THREE_PAIR_CAUSAL_MATRIX.json')
assert ts['TARGETED_DEFORMATION_VERDICT']=='FAIL_CLOSED_TARGETED_DEFORMATION'
assert cs['verdict']=='READY_FOR_HUMAN_CAUSAL_ADJUDICATION'
assert prior_verify['PRODUCTION_DRIFT']==0 and prior_verify['R2_vector_sha256']==VECTOR
assert sha(R2)==EXPECTED
pairs=[('PAIR_1225_2740','TH_IP_30',[1225,2740]),('PAIR_1041_2735','IDX_MCP_45',[1041,2735]),('PAIR_1226_2742','IDX_MCP_45',[1226,2742])]
assert {r['pair_id'] for r in matrix['rows']}=={p[0] for p in pairs}
assert all(r['cause']==MACHINE for r in matrix['rows'])
sources={k:ref(p) for k,p in {
 'historical_targeted_report':TARGET/(PHASE+'_REPORT.md'),
 'historical_targeted_status':TARGET/(PHASE+'_STATUS.json'),
 'historical_causal_report':CAUSAL/'CAP37_THUMB_INDEX_CROSSING_CAUSAL_ADJUDICATION_R1_REPORT.md',
 'historical_causal_status':CAUSAL/'CAP37_THUMB_INDEX_CROSSING_CAUSAL_ADJUDICATION_R1_STATUS.json',
 'machine_causal_matrix':CAUSAL/'THREE_PAIR_CAUSAL_MATRIX.json',
 'matched_visual_evidence_manifest':CAUSAL/'VISUAL_EVIDENCE_MANIFEST.json',
 'historical_production_verification':CAUSAL/'PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',
 'R2_candidate':R2}.items()}
decision={'HUMAN_CAUSAL_ADJUDICATION':'APPROVED',**{p[0]:DISPOSITION for p in pairs},'VISIBLE_TEACHING_DEFECT_COUNT':0,'VISIBLE_GROSS_LOCAL_SKIN_DEFECT_COUNT':0,'SKIN_REMEDIATION_REQUIRED':'NO','KINEMATIC_REMEDIATION_REQUIRED':'NO','SCOPE_EXPANSION_REQUIRED':'NO','R2_INTRODUCED_BLOCKER':'NO','R2_WORSENED_BLOCKER':'NO','R2_INCREMENTAL_INTRODUCED_PAIR_COUNT':0,'R2_WORSENED_PAIR_COUNT':0,'PRODUCTION_DRIFT':0}
for p,_,_ in pairs:decision[p+'_HUMAN_DISPOSITION']=DISPOSITION
provenance={'authority':'Explicit Human decision supplied by the user in this conversation','recorded_at_utc':datetime.now(timezone.utc).isoformat(),'review_performed_by':'Human user','review_evidence':['full-hand plain solid','thumb-index close plain solid','local surface plain solid','historical donor vs corrected R1 vs R2 matched evidence'],'observations_not_seen':['visible surface break','visible flap','visible spike','visible inversion','visible teaching-level penetration defect','gross local skin failure'],'scope':'Only the three specified diagnostic pose / face-pairs and closure of the targeted-deformation blocker.'}
pair_records=[{'pair_id':p,'pose':pose,'face_pair':faces,'machine_causal_classification_retained':MACHINE,'machine_confirmed_triangle_crossing_retained':True,'HUMAN_DISPOSITION':DISPOSITION,'visible_teaching_defect':False,'visible_gross_local_skin_defect':False} for p,pose,faces in pairs]
human={'artifact':'CAP37_THUMB_INDEX_CROSSING_HUMAN_ADJUDICATION_R1','artifact_type':'Independent additive Human approval record','provenance':provenance,**decision,'pairs':pair_records,'semantic_rule':'machine-confirmed geometric crossing != product-level visible teaching defect','machine_conclusions_unchanged':True,'historical_machine_unknown_visibility_counts_unchanged':True,'geometry_facts_retained':True,'sources':sources,'NEXT':NEXT,'NEXT_EXECUTED':False,'STOP':True,'production_promotion_or_freeze_authorized':False,'scope_or_anatomy_authority_amended':False}
write('CAP37_THUMB_INDEX_CROSSING_HUMAN_ADJUDICATION_R1.json',human)
human_text='''# CAP37_THUMB_INDEX_CROSSING_HUMAN_ADJUDICATION_R1

**HUMAN_CAUSAL_ADJUDICATION = APPROVED**

本独立记录依据用户在当前对话明确提供的 Human 裁决。Human 已审阅 full-hand plain solid、thumb-index close plain solid、local surface plain solid，以及 historical donor / corrected R1 / R2 的匹配证据。

| Pair | Pose | Human disposition |
|---|---|---|
| PAIR_1225_2740 | TH_IP_30 | ACCEPTED_NON_BLOCKING_DIAGNOSTIC_CONTACT |
| PAIR_1041_2735 | IDX_MCP_45 | ACCEPTED_NON_BLOCKING_DIAGNOSTIC_CONTACT |
| PAIR_1226_2742 | IDX_MCP_45 | ACCEPTED_NON_BLOCKING_DIAGNOSTIC_CONTACT |

三对真实 triangle crossing 作为几何事实保留。原 machine-level 分类 `VALIDATOR_SEMANTIC_ESCALATION_REQUIRES_HUMAN_ADJUDICATION` 保留，不改写为 POSE_CONTACT_ONLY、无相交或机器通过。

Human 在完整手、两指近景和局部实体表面中未观察到需要修复的可见教学形态缺陷；未观察到 visible surface break / flap / spike / inversion / teaching-level penetration defect / gross local skin failure。

`machine-confirmed geometric crossing ≠ product-level visible teaching defect`。Human 接受这三对作为 NON_BLOCKING_DIAGNOSTIC_CONTACT。

```json
'''+json.dumps(decision,ensure_ascii=False,indent=2)+'''
```

这些 0 是本次 Human 观察结论；旧报告中的 pending / null 仍按历史原样保留。R1→R2 的细小测量差异同样保留；Human 确认新增 crossing = 0、实质恶化 = 0。

审批仅关闭这三对的 targeted-deformation blocker；不提供 skin/rig remediation、scope expansion、R3 rerun、生产 promotion/freeze 或下一阶段执行授权。

机器证据：[causal report](../cap37_thumb_index_crossing_causal_adjudication_r1/CAP37_THUMB_INDEX_CROSSING_CAUSAL_ADJUDICATION_R1_REPORT.md) · [matched review](../cap37_thumb_index_crossing_causal_adjudication_r1/review.html)。精确来源哈希见同名 JSON；全历史与生产文件保护验证见 `PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json`。

**NEXT = TRUE_CAP_BOUND_RECOMPUTE_AFTER_DEPENDENCY_RECONCILIATION（只记录，未执行）。STOP。**
'''
write('CAP37_THUMB_INDEX_CROSSING_HUMAN_ADJUDICATION_R1.md',human_text)
qualified={'CAP37':{'machine_crossing_facts':'RETAINED','machine_causal_classification':MACHINE,'Human disposition':DISPOSITION,'visible_teaching_defect_count':0},'old cap9':'PASS / previously qualified','FIRST_WEB':'PASS / previously qualified','fresh R3 transition/collar':'PASS / previously qualified','edge5879':'PASS / previously qualified','16 inherited debt':'STATIC_QUALIFICATION_DEBT_WITHOUT_TRUE_DEFORMATION_FAILURE'}
closure={'artifact':'TARGETED_DEFORMATION_HUMAN_CLOSURE_R1','artifact_type':'Independent additive recovery closure; historical status files are not overwritten','recovery_phase':PHASE,'historical_phase_verdict_retained':ts['TARGETED_DEFORMATION_VERDICT'],'historical_causal_verdict_retained':cs['verdict'],'effective_recovery_status':PASS,PHASE:PASS,**decision,'targeted_blocker_closed':True,'closure_basis':ref(OUT/'CAP37_THUMB_INDEX_CROSSING_HUMAN_ADJUDICATION_R1.json'),'previously_qualified_items_carried_without_retest':qualified,'prior_fixture_pending_labels_in_historical_files_retained':True,'sources':sources,'NEXT':NEXT,'NEXT_EXECUTED':False,'STOP':True,'activities_executed':['Record explicit Human decision','Create independent additive closure artifacts','Read-only byte/hash verification'],'activities_not_executed':['bound recompute','Stage6A','Stage6B','skin/rig remediation','scope expansion','R3 rerun','production mutation','promotion/freeze'],'retested_items':[],'production_candidate_sha256':EXPECTED,'production_vector_sha256':VECTOR,'production_vector_verification_basis':'Current candidate byte hash equals the previously independently reopened candidate hash; no new weight/deformation test.'}
write('TARGETED_DEFORMATION_HUMAN_CLOSURE_R1.json',closure)
write('TARGETED_DEFORMATION_HUMAN_CLOSURE_R1.md','''# TARGETED_DEFORMATION_HUMAN_CLOSURE_R1

**CAP_FIXTURE_STATIC_VALIDATION_AND_TARGETED_DEFORMATION_R1 = PASS_WITH_HUMAN_ACCEPTED_NON_BLOCKING_DIAGNOSTIC_CONTACT**

本独立 closure 依据 [Human approval](CAP37_THUMB_INDEX_CROSSING_HUMAN_ADJUDICATION_R1.md) 关闭 targeted-deformation recovery blocker。有效 recovery 状态采用上面的 Human closure；旧 targeted report/status 的 `FAIL_CLOSED_TARGETED_DEFORMATION` 和旧 causal report/status 的 `READY_FOR_HUMAN_CAUSAL_ADJUDICATION` 原样保留，体现历史时点，不被覆盖。

三对 CAP37 machine-confirmed crossing facts 和 `VALIDATOR_SEMANTIC_ESCALATION_REQUIRES_HUMAN_ADJUDICATION` 分类保留。Human 批准三对 `ACCEPTED_NON_BLOCKING_DIAGNOSTIC_CONTACT`，visible teaching defect count = 0，visible gross local skin defect count = 0。

| 项目 | Closure 保留结果 | 本轮重测 |
|---|---|---|
| old cap9 | PASS / previously qualified | 无 |
| FIRST_WEB | PASS / previously qualified | 无 |
| fresh R3 transition/collar | PASS / previously qualified | 无 |
| edge5879 | PASS / previously qualified | 无 |
| 16 inherited debt | STATIC_QUALIFICATION_DEBT_WITHOUT_TRUE_DEFORMATION_FAILURE | 无 |

上述 closure 表依据用户本次明确指令沿用已关闭结果；旧文件的 pending 标签同样保留。静态资格 debt 仍保留，不声称已经消除。

SKIN_REMEDIATION_REQUIRED = NO；KINEMATIC_REMEDIATION_REQUIRED = NO；SCOPE_EXPANSION_REQUIRED = NO；R2_INTRODUCED_BLOCKER = NO；R2_WORSENED_BLOCKER = NO。

PRODUCTION_DRIFT = 0。当前 R2 byte SHA256 仍为 `'''+EXPECTED+'''`。既有独立 clean-reopen 权重 vector SHA256 为 `'''+VECTOR+'''`，由相同 candidate 字节哈希与历史证据承接；本轮只做只读哈希核对，没有重新测试 deformation 或修改生产数据。

R2 candidate、weights、geometry、topology、bones、joints、RSSF、cap37、corrected kinematics、R3 authority、FIRST_WEB 和所有历史 report/status 未改变。详细核对见 `PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json`。本 closure 不等于完整 Stage6A/Stage6B requalification 或生产 promotion/freeze。

**NEXT = TRUE_CAP_BOUND_RECOMPUTE_AFTER_DEPENDENCY_RECONCILIATION。只记录阶段名称，本轮未执行。STOP。**
''')
after=inventory();diff=[p for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)]
assert not diff,diff
assert sha(R2)==EXPECTED
assert read(TARGET/(PHASE+'_STATUS.json'))==ts and read(CAUSAL/'CAP37_THUMB_INDEX_CROSSING_CAUSAL_ADJUDICATION_R1_STATUS.json')==cs
for filename in ['CAP37_THUMB_INDEX_CROSSING_HUMAN_ADJUDICATION_R1.json','TARGETED_DEFORMATION_HUMAN_CLOSURE_R1.json']:
 d=read(OUT/filename)
 assert all(d[k]==v for k,v in decision.items()) and not d['NEXT_EXECUTED'] and d['STOP']
write('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',{'status':'PASS','PRODUCTION_DRIFT':0,'method':'Read-only full workspace byte/hash comparison excluding only this new closure directory; R2 hash checked against frozen expected hash. No Blender execution or deformation retest.','historical_file_count':len(before),'all_historical_files_byte_hash_unchanged':True,'added_deleted_changed_outside_closure_directory':diff,'historical_targeted_and_causal_reports_statuses_unchanged':True,'R2_sha256':sha(R2),'R2_vector_sha256_carried_from_prior_independent_live_reopen':VECTOR,'R2_byte_identity_preserves_prior_verified_vector':True,'prior_live_reopen_evidence':sources['historical_production_verification'],'production_writes':0,'deformation_runs':0,'bound_recomputations':0,'NEXT_EXECUTED':False,'STOP':True})
write('CLOSURE_ARTIFACT_HASH_MANIFEST.json',{p.name:sha(p) for p in OUT.iterdir() if p.is_file()})
print(json.dumps({'HUMAN_CAUSAL_ADJUDICATION':'APPROVED','effective_recovery_status':PASS,'historical_files_unchanged':len(before),'PRODUCTION_DRIFT':0,'NEXT':NEXT,'NEXT_EXECUTED':False,'STOP':True},ensure_ascii=False,indent=2))
