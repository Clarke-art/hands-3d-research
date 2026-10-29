"""Record qualification, not promotion. All original assets remain byte-identical."""
from pathlib import Path
import json,hashlib
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
I=read('CANDIDATE_IDENTITY_R1.json');S=read('FULL_MOTION_MINIMUM_SAFETY_R1.json');R=read('APPROVED_POSE_REGRESSION_R1.json');V=read('VIDEO_VERIFICATION_R1.json');C=read('CONTACT_SHEET_DEFINITION_R1.json')
assert I['CANDIDATE_WEIGHT_FIELD_IDENTITY']=='MATCHED' and all(v==0 for v in S['maxima'].values())
before=I['protected_inputs_before']
for path,expected in before.items():assert sha(ROOT/path)==expected,path
PHASE=I['PHASE']
pose_findings={
 'ZERO':'批准 RSSF 外形保持；三产品视角匹配对照没有肉眼外形变化。',
 'INDEX_MCP_45':'食指根弯折与 first-web 连接保持可接受；没有 candidate 新增明显 shelf、flap 或 palm collapse。',
 'CMC_OPP_30':'拇指根与 thenar 在批准 opposition 姿态下保持可接受；既有 corrective 自然求值 1.0，baseline 与 candidate 相同。',
 'FULL_OPP_L1':'轻度复合 opposition 保持自然；没有可见新凹陷或 first-web 打开。',
 'FULL_OPP_L2':'较强 opposition 的掌侧体积和 thumb/index 过渡保持可接受，未见新明显表面问题。',
 'FULL_OPP_L3':'最强旧批准 opposition 保持原可接受外观，没有新增 flap、hard shelf 或 thenar collapse。'}
for row in R['poses']:
    row['human_visible_result']='YES_ACCEPTABLE_NO_NEW_VISIBLE_REGRESSION'
    row['agent_visible_findings']=pose_findings[row['pose']]
R['human_visible_result']='YES_ALL_SIX_ACCEPTABLE';R['human_production_approval']='PENDING';R['assessment_scope']='Matched ordinary three-product-view renders; no hidden forensic gates'
dump('APPROVED_POSE_REGRESSION_R1.json',R)
S['status']='PASS';S['human_visible_screen_pending']=False
S['visible_gross_tearing']='NONE_NEW_OBSERVED';S['visible_obvious_penetration']='NONE_NEW_GROSS_OBSERVED'
S['visible_assessment_scope']='Product videos and temporal scans + six matched approved poses. Not exhaustive hidden collision certification.'
dump('FULL_MOTION_MINIMUM_SAFETY_R1.json',S)
questions=[
 ['Q1','Candidate weight-field identity 与上一轮完全一致？','YES'],
 ['Q2','完整 7 秒 DEFAULT_TEACHING_VIEW 可接受？','YES'],
 ['Q3','完整 7 秒 NORMAL_ORBIT_VIEW 可接受？','YES'],
 ['Q4','完整 7 秒 REASONABLE_CLOSE_VIEW 可接受？','YES'],
 ['Q5','完整 motion 中原 first-web blocker 保持解决？','YES'],
 ['Q6','出现新的明显 bulge/flap/shelf/collapse/volume distortion/motion jump？','NO'],
 ['Q7','六个旧 Human-approved 姿态全部可接受？','YES'],
 ['Q8','ZERO / RSSF 保持批准外形？','YES'],
 ['Q9','421 observations 最低机器保护通过？','YES'],
 ['Q10','最终资格结论','PASS']]
status={'PHASE':PHASE,**{q[0]:q[2] for q in questions},'PRODUCTION_QUALIFICATION':'PASS','FIRST_WEB_BLOCKER_STATUS':'CANDIDATE_RESOLVED_PENDING_HUMAN_PROMOTION','NEW_HUMAN_VISIBLE_REGRESSION':'NO','PRODUCTION_CANDIDATE_READY':'YES','PRODUCTION_CANDIDATE':'READY_FOR_HUMAN_APPROVAL','qualification_readiness':'READY_FOR_HUMAN_PRODUCTION_APPROVAL','CANDIDATE_WEIGHT_FIELD_IDENTITY':'MATCHED','FROZEN_FALLBACK_UNCHANGED':'YES','candidate_path':I['candidate_path'],'candidate_sha256':I['candidate_actual_sha256'],'candidate_file_status':'DESIGN_ONLY_UNMODIFIED','new_candidate_count':0,'blend_files_written':0,'production_pointer_moved':False,'promotion':False,'RIGHT_HAND_DEFORMATION_CLOSED':'NO_PENDING_HUMAN_PRODUCTION_APPROVAL','LEFT_HAND_START':'NO','WEB_EXPORT_START':'NO','human_production_approval':'PENDING','WORKFLOW_STATUS':'STOP_HUMAN_REVIEW','STATIC_WEIGHT_ROUTE':'OPEN','LEVEL_1_TOPOLOGY_ROUTE':'CLOSED','DEFORMATION_DOF_REBUILD':'NOT_REQUIRED_FOR_CURRENT_BLOCKER'}
dump(PHASE+'_STATUS.json',status)
dump('VISIBLE_PRODUCT_REVIEW_R1.json',{'PHASE':PHASE,'PRODUCTION_QUALIFICATION':'PASS','observer':'Agent review; Human production approval remains pending','evidence_basis':['Complete 7s three-product-view video','Existing baseline vs same candidate matched orbit and close videos','Four temporal contact sheets, 48 selected timestamps spanning early/mid/problem-zone/late','Six approved poses × three mature product directions, baseline/candidate matched','ZERO three-view evidence'], 'temporal_scope_note':'Product playback with visual sampling and contact-sheet scan; not 421 independent Human judgments. All 421 observations receive only minimum machine checks.','reviewed_contact_sheets':C['sheets'],'DEFAULT_TEACHING_VIEW':'YES_ACCEPTABLE','NORMAL_ORBIT_VIEW':'YES_ACCEPTABLE','REASONABLE_CLOSE_VIEW':'YES_ACCEPTABLE','original_deep_stepped_first_web_blocker':'NOT_SEEN_RETURNING','new_visible_bulge_flap_shelf_collapse_volume_pumping_sliding_softening_jump':'NONE_NEW_OBSERVED','thumb_root_thenar_index_root_palm_volume_thumb_index_connection_other_digit_roots':'No obvious new defect identified in product evidence','suspect_interval_found':False,'expanded_suspect_interval':None,'pose_findings':pose_findings,'no_repair_performed':True,'human_final_production_decision':'PENDING'})
fallback=ROOT/'production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend'
protection={'PHASE':PHASE,'status':'PASS','FROZEN_FALLBACK_UNCHANGED':'YES','frozen_fallback_actual_sha256':sha(fallback),'frozen_fallback_expected_sha256':'4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2','frozen_fallback_status':'PROTECTED_FROZEN_FALLBACK','candidate_path':I['candidate_path'],'candidate_original_sha256':I['candidate_expected_sha256'],'candidate_final_sha256':sha(ROOT/I['candidate_path']),'CANDIDATE_WEIGHT_FIELD_IDENTITY':'MATCHED','candidate_weights_Basis_topology_rest_bones_Action_corrective_driver_unchanged':True,'ROI_outside_and_boundary_weights_unchanged':True,'prior_audit_report_review_JSON_candidate_matched_evidence_unchanged':True,'protected_inputs_expected_and_final':before,'blend_files_written':[],'new_candidate_count':0,'new_harmonic_solution':False,'weight_design_or_tuning':False,'production_pointer_moved':False,'promotion':False,'left_hand_started':False,'web_export_started':False,'new_bone_corrective_helper_cage_DQS':False,'forbidden_forensic_performed':False,'WORKFLOW_STATUS':'STOP_HUMAN_REVIEW'}
assert protection['candidate_final_sha256']==I['candidate_expected_sha256'] and protection['frozen_fallback_actual_sha256']==protection['frozen_fallback_expected_sha256']
dump('FINAL_ASSET_PROTECTION_R1.json',protection)
qtable='\n'.join('| '+' | '.join(q)+' |' for q in questions)
pose_table='\n'.join('| '+row['pose']+' | YES | '+pose_findings[row['pose']]+' | '+str(row['candidate_corrective_natural_values']['FIRST_WEB_OPPOSITION_CREASE_R1'])+' |' for row in R['poses'])
contact_table='\n'.join('| '+row['segment']+' | '+', '.join('F'+str(f) for f in row['frames'])+' | ['+row['path']+']('+row['path']+') |' for row in C['sheets'])
report=f'''# {PHASE}

**PRODUCTION_QUALIFICATION = PASS**  
**FIRST_WEB_BLOCKER_STATUS = CANDIDATE_RESOLVED_PENDING_HUMAN_PROMOTION**  
**NEW_HUMAN_VISIBLE_REGRESSION = NO**  
**PRODUCTION_CANDIDATE_READY = YES**  
**FROZEN_FALLBACK_UNCHANGED = YES**

本轮只读验证上一轮同一份成功的 full-vector candidate。固定完整 7 秒 motion 的三种成熟产品视角、六个旧 Human-approved 代表姿态及 ZERO 对照没有显示新的明显产品可见回退；first-web 主深阶梯缺口在时间扫描及视频产品证据中未见再次打开。候选具备 **READY_FOR_HUMAN_PRODUCTION_APPROVAL / READY_FOR_HUMAN_APPROVAL** 资格，仍为 DESIGN_ONLY，Human production approval / promotion = PENDING。

## Q1–Q10

| # | 问题 | 回答 |
|---|---|---|
{qtable}

## 继承 Human 决策与同一 candidate 身份

Human 已接受 RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1 = HUMAN_APPROVED、STATIC_WEIGHT_FIELD_PROBLEM = CAUSALLY_SUPPORTED。STATIC_WEIGHT_ROUTE=OPEN，LEVEL_1_TOPOLOGY_ROUTE=CLOSED，DEFORMATION_DOF_REBUILD=NOT_REQUIRED_FOR_CURRENT_BLOCKER。批准记录只写本轮 HUMAN_APPROVAL_BIND_R1.json；原报告 / pending 历史状态均保持字节原样，不追改历史。

读取并继承上一轮 report、review、JSON、matched evidence、DESIGN_ONLY .blend 和 frozen fallback。没有重新研究成因、重新求 harmonic、刷 weights、改 ROI/boundary/Laplacian、人工微调、optimization/sweep 或新 candidate。

唯一 qualification 输入仍为 `{I['candidate_path']}`。文件 SHA256 `{I['candidate_actual_sha256']}`，轮前、求值后、结束一致。保存于上一阶段的每个完整 ROI weight-vector 与本轮读取值逐分量完全一致，ROI 外和 boundary 与 frozen baseline 完全一致；native geometry / topology / Basis / UV / rest / 21 bones / modifiers / constraints / drivers / 原 corrective / Action 一致。

**CANDIDATE_WEIGHT_FIELD_IDENTITY = MATCHED**。本轮 .blend 写入数 = 0；候选文件未另存、未改元数据。生产候选 readiness 是本轮报告状态，不是写回资产或 production pointer 的 promotion。

## 完整 motion 与成熟产品相机

仍使用 PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1，11.5–18.5 sec，7 sec，421 observations。30fps 视频由 F1–210 组成，210 个整数帧全部渲染三产品视角；机器 observation 包含半帧与最终 F211 端点：`i=0..420 → source 690+i → frame 1+i//2 + (i%2)/2`。未换 sample、Action 或 retarget。

相机逐帧直接复用 `audits/right_hand_first_web_product_impact_go_no_go_r1/PRODUCT_VIEW_OBSERVATION_R1.json` 的完全匹配成熟定义。方向 / center / scale / resolution 均相同，candidate 不重新自适应取景。Workbench lighting / shadow intensity 0 / neutral clay / smooth display shading 同原 baseline 产品证据。

| View | 原成熟方向 | ortho_scale | 产品目的 |
|---|---|---:|---|
| DEFAULT_TEACHING_VIEW | −0.38183954, −0.92405248, 0.0180442 | 0.42 m | 整手及腕的正常教学观察 |
| NORMAL_ORBIT_VIEW | 0.19980031, −0.93906146, 0.27972043 | 0.22 m | 正常旋转观察 palm / roots |
| REASONABLE_CLOSE_VIEW | 同 NORMAL_ORBIT_VIEW | 0.115 m | 合理产品近景，不是 forensic macro |

三份视频均 7.000 sec / 210 frames / 30fps / H.264，可在 review.html 完整播放、慢放、逐帧及切换视角：

- [product_7s_candidate_three_views.mp4](product_7s_candidate_three_views.mp4)：candidate 完整三视角，2880×900；review 可单独显示各视角。
- [product_7s_matched_normal_orbit_view.mp4](product_7s_matched_normal_orbit_view.mp4)：baseline LEFT / candidate RIGHT，1920×900。
- [product_7s_matched_reasonable_close_view.mp4](product_7s_matched_reasonable_close_view.mp4)：同上，合理近景。

baseline 直接使用既有完全匹配 product videos，保护其原哈希，没有重生成 baseline motion 素材。匹配视频只做同步并排排版；candidate 权重与 motion 均不变。

## Human-visible 产品审核

审核依据为完整视频产品时间轴、视频实际播放抽样观察与四段接触表，以及六旧姿态匹配图。**不是对 421 个 observation 逐一作 Human 判读**；421 次是最低机器检查。contact sheets 为 48 个跨时间点，时间点包含问题生长、原 peak、恢复和 late recurrence，不止原六帧。原 first-web 主带没有从深折变成另一种明显 bulge/flap/shelf/collapse；未识别需要展开的可疑区间。

| 产品检查 | 可见结果 |
|---|---|
| Teaching whole hand | 动作及整体轮廓保持可接受；未见新明显 palm volume collapse 或其他指根异常 |
| Normal orbit | thumb root / thenar / index root / thumb-index 连接连续；未见新明显 hard shelf 或 flap |
| Reasonable close | 原深阶梯缺口在 problem zone 保持消失；恢复与 late recurrence 中保持连续可信 |
| 新缺陷类型 | 没有观察到新增明显 bulge、flap、shelf、collapse、volume pumping、skin sliding 感、异常软化、不自然深凹或突然表面跳变 |

此结论是在给定 sample、成熟产品视角与指定旧姿态中的产品资格判断；没有将 machine PASS 替代可见质量，也没有扩张成所有未来动作/角度的数学保证。最终生产接受仍由 Human 判断。

| 时间段 | 接触表时间点 | 文件 |
|---|---|---|
{contact_table}

## 六个旧批准姿态回归与 ZERO

逐项复用既有 approved case 定义，不改角度、局部轴或 corrective。基线和 candidate 使用同一套三产品相机；每个姿态中心由 baseline evaluated hand/web bbox 按原 .45/.55 产品 framing 规则设置，方向 / scale / resolution 不变。candidate 不单独重取景。全 6×3×2 对照源图可由 review 的 pose/view 控件查看；两张总证据避免重复截图。

| Pose | 可接受 | 可见判读 | 原 corrective 自然值，两资产相同 |
|---|---|---|---:|
{pose_table}

![Approved pose regression](EVIDENCE_APPROVED_POSE_REGRESSION_R1.png)

![ZERO / RSSF](EVIDENCE_ZERO_R1.png)

ZERO 批准外形保持；native Basis / rest 坐标和 topology 逐项完全一致。ZERO evaluated 最大浮点差仅 {I['ZERO_baseline_candidate_evaluated_max_mm']:.9f} mm，肉眼外形不变，不能据此阻塞正常产品。所有旧姿态回到 ZERO 后 restore=0.000000 mm。既有 corrective 在 CMC_OPP_30 / L2 / L3 仍按原 driver 自然参与，baseline 与 candidate 值相同，没有强制开关或新增机制。

## 最低机器保护与资产保护

421 observations：NaN/Inf=0，gross collapsed faces=0，catastrophic zero-length edges=0；ZERO restore=PASS，最大差 0.0 mm。旧姿态相同最低检查通过。gross tearing 与明显 penetration 使用普通产品证据可见检查，未观察到 candidate 新增的明显产品故障；没有 hidden collision 认证或已禁止的法证指标。

未执行 hidden crossing / normal-dot / R3 / true-cap / 2127-edge / 逐顶点 anatomy proof。没有进入 repair、causal diagnosis 或 weight design。

Frozen fallback SHA256 轮前轮后均为 `{protection['frozen_fallback_actual_sha256']}`，PROTECTED_FROZEN_FALLBACK 状态保持。上一阶段候选 `{I['candidate_actual_sha256']}` 和全部上一阶段 durable audit / report / review / JSON / matched evidence，以及生产 pointer / Action / retarget / sample 输入均哈希不变，详见 FINAL_ASSET_PROTECTION_R1.json。

**未 promotion，未覆盖 fallback，未移动 production pointer，未开始左手或 Web export。** 没有 new bone/corrective/helper/cage/DQS，也没有新的 .blend candidate。

## 停止

**PRODUCTION_QUALIFICATION = PASS**  
**PRODUCTION_CANDIDATE = READY_FOR_HUMAN_APPROVAL**  
**FIRST_WEB_BLOCKER_STATUS = CANDIDATE_RESOLVED_PENDING_HUMAN_PROMOTION**

交付已包括完整三产品视角视频、两匹配 A/B 视频、四时间扫描表、六旧姿态与 ZERO 证据、identity/safety/pose regression/protection JSON 和 review.html。候选仍保留在上一轮原路径，文件未改变。

**STOP — HUMAN REVIEW。等待 Human 生产批准与 promotion 决策。**
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
print('QUALIFICATION_PASS_SAME_CANDIDATE_NO_PROMOTION',flush=True)
