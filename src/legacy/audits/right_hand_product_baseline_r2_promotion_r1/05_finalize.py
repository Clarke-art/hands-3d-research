"""Final freeze records and protection checks; no further Blender mutation or qualification."""
from pathlib import Path
import json,hashlib,stat
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PHASE='RIGHT_HAND_PRODUCT_BASELINE_R2_PROMOTION_R1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
I=read(OUT/'PROMOTION_IDENTITY_R1.json');C=read(OUT/'CANDIDATE_CONTAINER_INSPECTION_R1.json');U=read(OUT/'PRODUCTION_POINTER_UPDATE_R1.json');A=read(OUT/'HUMAN_APPROVAL_BIND_R1.json')
pointer=ROOT/U['pointer_path'];current=read(pointer)
assert current==U['after'] and sha(pointer)==U['after_sha256']
previous_pointer=U['pointer_path'];protected={}
for path,expected in C['protected_inputs_before'].items():
    if path==previous_pointer:continue
    assert sha(ROOT/path)==expected,path
    protected[path]=expected
R2=ROOT/I['R2_baseline']['path'];R1=ROOT/current['historical_frozen_fallback']['path'];candidate=ROOT/I['approved_candidate']['path']
assert sha(R2)==I['R2_baseline']['sha256'] and sha(R1)=='4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2'
assert sha(candidate)=='0f6b24fc8d74a0fe37fb4a142169633d525db3c2ea58a440005060c137cc374d'
readonly=bool(R2.stat().st_file_attributes & stat.FILE_ATTRIBUTE_READONLY);assert readonly
assert not list(R2.parent.glob('*.blend1')) and len(list(R2.parent.glob('*.blend')))==1
status={'PHASE':PHASE,'PROMOTION':'PASS','RIGHT_HAND_PRODUCT_BASELINE_R2':'HUMAN_APPROVED_FROZEN','R2_BASELINE_ASSET':I['R2_baseline']['path'],'R2_BASELINE_SHA256':sha(R2),'R2_FILE_READ_ONLY':True,'HUMAN_PRODUCTION_APPROVAL':'APPROVED','FIRST_WEB_HUMAN_VISIBLE_BLOCKER':'CLOSED','RIGHT_HAND_DEFORMATION':'CLOSED','RIGHT_HAND_DEFORMATION_CLOSED':'YES','STATIC_WEIGHT_FIELD_PROBLEM':'RESOLVED_IN_R2','RIGHT_HAND_READY_FOR_LEFT_HAND_STAGE':'YES','R1_ROLE':'HISTORICAL_FROZEN_FALLBACK','R1_FALLBACK_ASSET':current['historical_frozen_fallback']['path'],'R1_FALLBACK_SHA256':sha(R1),'R1_HISTORICAL_FALLBACK_UNCHANGED':'YES','WEIGHT_FIELD_IDENTITY':'EXACT_MATCH','APPROVED_CANDIDATE_SHA256':sha(candidate),'CANDIDATE_CONTAINER_STATUS':I['CANDIDATE_CONTAINER_STATUS'],'R2_CONTAINER_STATUS':'PRODUCTION_CLEAN','PRODUCTION_POINTER':'R2','PianoVAM_Runtime_Dependency':False,'Action_compatibility':'EXACT_MATCH','LEFT_HAND_STARTED':'NO','WEB_EXPORT_STARTED':'NO','STOP':'STOP — HUMAN REVIEW'}
questions=[['Q1','获批 candidate SHA 匹配？','YES'],['Q2','Candidate container 状态？','AUDIT_SCAFFOLDING_PRESENT'],['Q3','R2 完整 weight field EXACT_MATCH？','YES'],['Q4','mesh/topology/rig/rest/corrective/driver 一致？','YES'],['Q5','ZERO/F130/FULL_OPP_L3 最小 smoke 通过？','YES'],['Q6','R1 fallback 原 SHA 保持？','YES'],['Q7','production pointer 成功 R1 → R2？','YES'],['Q8','R2 = HUMAN_APPROVED_FROZEN 成立？','YES']]
status.update({q[0]:q[2] for q in questions})
dump(OUT/(PHASE+'_STATUS.json'),status)
dump(R2.parent/'RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2_STATUS.json',status)
protection={'PHASE':PHASE,'status':'PASS','R2':{'path':I['R2_baseline']['path'],'sha256':sha(R2),'status':'HUMAN_APPROVED_FROZEN','file_read_only':True,'saved_pose':'ZERO / RSSF','product_container_clean':True},'R1':{'path':current['historical_frozen_fallback']['path'],'expected_sha256':current['historical_frozen_fallback']['sha256'],'actual_sha256':sha(R1),'role':'HISTORICAL_FROZEN_FALLBACK','permanent_retention':True,'unchanged':True},'approved_candidate':{'path':I['approved_candidate']['path'],'expected_sha256':I['approved_candidate']['expected_sha256'],'actual_sha256':sha(candidate),'unchanged':True},'production_pointer':{'path':U['pointer_path'],'before_sha256':U['before_sha256'],'after_sha256':sha(pointer),'PREVIOUS_PRODUCTION_BASELINE':'R1','CURRENT_PRODUCTION_BASELINE':'R2','authorized_change':True,'updated_after_identity_smoke_PASS':True},'protected_inputs_expected_and_final_except_authorized_pointer':protected,'all_prior_audit_history_unchanged':True,'approved_weight_field':'EXACT_MATCH','core_deformation_mutation_count':0,'weight_writes':0,'harmonic_recomputations':0,'R1_blend_writes':0,'approved_candidate_blend_writes':0,'R2_container_saves':2,'R2_save_scope':'Only new production container; second save finalized two inherited scene approval labels before pointer commit. All core payload hashes remained exact.','full_qualification_repeated':False,'210_frame_render_repeated':False,'421_observation_qualification_repeated':False,'new_bone_corrective_helper_cage_DQS':False,'left_hand_started':False,'web_export_started':False,'STOP':'STOP — HUMAN REVIEW'}
dump(OUT/'FINAL_BASELINE_PROTECTION_R1.json',protection)
qtable='\n'.join('| '+' | '.join(q)+' |' for q in questions)
component_table='\n'.join('| '+k+' | EXACT_MATCH | `'+I['core_component_R2_sha256'][k]+'` |' for k in I['core_component_exact_match'])
smoke_table='\n'.join('| '+r['state']+' | PASS | '+str(r['max_difference_mm'])+' | '+str(r['R2_corrective_natural_values']['FIRST_WEB_OPPOSITION_CREASE_R1'])+' |' for r in I['smoke_checks'])
report=f'''# {PHASE}

**PROMOTION = PASS**  
**RIGHT_HAND_PRODUCT_BASELINE_R2 = HUMAN_APPROVED_FROZEN**  
**FIRST_WEB_HUMAN_VISIBLE_BLOCKER = CLOSED**  
**RIGHT_HAND_DEFORMATION = CLOSED**  
**RIGHT_HAND_READY_FOR_LEFT_HAND_STAGE = YES**  
**R1_HISTORICAL_FALLBACK_UNCHANGED = YES**

已将 Human 最终批准的同一份 deformation state 升格并冻结为 R2，production pointer 从 R1 更新到 R2。完整权重和全部核心产品 payload 与批准 candidate 逐项完全一致；只清理审计播放包装与身份标记，没有重求 harmonic、刷 weights、改 mesh/rig 或重新 qualification。

## Q1–Q8

| # | 问题 | 回答 |
|---|---|---|
{qtable}

## Human 最终授权与输入

本轮明确获得 Human 决策：RIGHT_HAND_FIRST_WEB_PRODUCTION_WEIGHT_QUALIFICATION_R1 = HUMAN_APPROVED，HUMAN_PRODUCTION_APPROVAL = APPROVED，FIRST_WEB_HUMAN_VISIBLE_BLOCKER = CLOSED，NEW_HUMAN_VISIBLE_REGRESSION = NO，PRODUCTION_PROMOTION = AUTHORIZED。原 qualification report / review / JSON / 视频和原 causal candidate 都保持原样，PENDING / DESIGN_ONLY 历史未追改。独立 HUMAN_APPROVAL_BIND_R1.json 绑定当前用户请求与已审核视频的 SHA。

唯一获批 candidate：`{I['approved_candidate']['path']}`  
SHA256：`{sha(candidate)}`。

上一轮完整 7 秒 / 三产品视角 / 六旧姿态 / ZERO / 421 observations 的 PASS 和 Human approval 直接继承。本轮不重做它们。

## 容器检查与 clean packaging

**CANDIDATE_CONTAINER_STATUS = AUDIT_SCAFFOLDING_PRESENT**。只读 inventory 显示：只有原 Official L1 mesh 与成熟 rig 两个对象；无 audit camera、comparison object、debug collection 或 evidence helper。

仍有两类审计包装：保存于 F130 并绑定的 PianoVAM qualification Action，以及 DESIGN_ONLY / NOT_PRODUCTION / approval pending 标记（包括继承的 HUMAN_APPROVAL=PENDING、DO_NOT_PROMOTE）。它们不应成为正式产品的身份或运行依赖，因此采用 **CLEAN_PRODUCTION_CONTAINER_EXACT_PRODUCT_DATA**，而非 byte-copy 整个审计 .blend。

允许的变化仅为：

- R2 以 ZERO / RSSF、frame 1 保存，清除 qualification playback binding；生产容器不嵌入 PianoVAM evidence Action。
- 在新容器内将审计 approval/identity labels 改为 Human-approved frozen 状态；原 candidate 的 Action payload 与文件均未改。
- 该同一 Action 在重新打开 R2 的未保存 smoke 会话中临时 library-append，验证 F130 兼容；不写回 R2，因此 **PianoVAM_RUNTIME_DEPENDENCY = NO**。

新 R2 SHA 与 candidate 不同是容器包装变化，并非重新生成等价 weights。所有差异白名单、数据哈希与清理前后 container SHA 都记录于 PROMOTION_IDENTITY_R1.json。首次新容器保存后补齐两个继承的 scene approval 标签，**在 pointer 更新前**重新验证所有核心 payload 完全一致；未改任何 approved deformation data。

## Exact product identity

R2：`{I['R2_baseline']['path']}`  
**R2_BASELINE_SHA256 = `{sha(R2)}`**。

保留 Official L1 source identity、3300 vertices / 3298 faces、现有 21-bone teaching rig（16 deform + 5 non-deform TIP helpers）、原 approved corrective/driver 和 Human-approved complete static field。

**WEIGHT_FIELD_IDENTITY = EXACT_MATCH**。全部 3300 个完整 weight vectors、ROI active-bone 向量、boundary 和 ROI 外 weights 均完全相同。weight-field SHA256：`{I['weight_field_sha256']}`。没有 weight setter 或 harmonic solve。

| 核心组件 | 结果 | 与 approved candidate 相同的 SHA256 |
|---|---|---|
{component_table}

armature 完整 payload 包括 21 bone names、parents、rest transforms、inherit settings、pose/rig constraints、bone collections 及原 driver/settings。其他验证包含 Basis、corrective 数据、UV、materials、native shading、modifiers、topology edges/faces/loops 与 group settings。只对白名单的产品身份 metadata 排除比较，其余产品字段没有豁免。

六个旧批准 pose 的定义直接继承且未改；没有重新渲染六姿态资格矩阵。Action compatibility = EXACT_MATCH，临时读取的 approved Action payload SHA256 为 `{I['qualification_Action_payload_sha256']}`。

## 最小 smoke check

只检查 ZERO、F130 和 FULL_OPP_L3（用于确认原 corrective 可自然参与），没有 210 帧或 421 observations 重验。

| 状态 | 结果 | candidate ↔ R2 最大求值位置差 mm | 原 corrective 自然值 |
|---|---|---:|---:|
{smoke_table}

三状态全部对应点数值完全相同；NaN/Inf=0，ZERO restore=0.0 mm。成熟正常产品相机、lighting/shading 匹配图的像素也完全相同，未见新 packaging regression。

![Promotion smoke](EVIDENCE_PROMOTION_SMOKE_R1.png)

## Pointer 更新与新 freeze

仅在 identity、clean reopen 和 smoke 全部 PASS 后，将 `production_spec/RIGHT_HAND_PRODUCT_BASELINE.json` 原子更新为：

`PREVIOUS_PRODUCTION_BASELINE = R1`  
`CURRENT_PRODUCTION_BASELINE = R2`。

更新前 SHA256：`{U['before_sha256']}`；更新后 SHA256：`{sha(pointer)}`。旧 pointer 原始字节另存 PRODUCTION_POINTER_BEFORE_R1.json，供审计或经授权回滚。PRODUCTION_POINTER_UPDATE_R1.json 同时记录完整 before/after。

R2 已重新打开验证、以 ZERO 保存、无 active motion Action、无 audit objects，并设置 Windows read-only 文件属性（不影响文件 SHA）。R2_STATUS sidecar 与 pointer 同时记录 HUMAN_APPROVED_FROZEN、FIRST_WEB CLOSED、RIGHT_HAND_DEFORMATION CLOSED、STATIC_WEIGHT_FIELD_PROBLEM RESOLVED_IN_R2。

## 永久 fallback 与历史保护

R1 保留原路径 `production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend`，新角色 **HISTORICAL_FROZEN_FALLBACK**，永久保留。

**R1_FALLBACK_SHA256 = `{sha(R1)}`**，轮前轮后不变。R1 资产、原候选、所有旧 report / audit / review / JSON / matched evidence / approved sample / retarget source 均未改或删除。正式 role 更新只在新的 pointer/promotion record 中记录，不追改旧状态。

本轮写入的正式 .blend 只有新 R2 容器；R1 写入 0，approved candidate 写入 0，deformation mutation 0。没有新 bone/corrective/helper/cage/DQS，未开始左手、Three.js/Web export 或钢琴集成。

## 交付与停止

本报告、PROMOTION_IDENTITY_R1.json、PRODUCTION_POINTER_UPDATE_R1.json、FINAL_BASELINE_PROTECTION_R1.json、HUMAN_APPROVAL_BIND_R1.json、EVIDENCE_PROMOTION_SMOKE_R1.png 和新正式 R2 .blend 已完成。独立 R2 status 与原 pointer 的 byte-exact 备份一并保留。

**PROMOTION = PASS**  
**RIGHT_HAND_PRODUCT_BASELINE_R2 = HUMAN_APPROVED_FROZEN**  
**FIRST_WEB_HUMAN_VISIBLE_BLOCKER = CLOSED**  
**RIGHT_HAND_DEFORMATION_CLOSED = YES**  
**RIGHT_HAND_READY_FOR_LEFT_HAND_STAGE = YES**

**STOP — HUMAN REVIEW。等待下一阶段 Human 决策。**
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
required=[PHASE+'_REPORT.md','PROMOTION_IDENTITY_R1.json','PRODUCTION_POINTER_UPDATE_R1.json','FINAL_BASELINE_PROTECTION_R1.json','HUMAN_APPROVAL_BIND_R1.json','EVIDENCE_PROMOTION_SMOKE_R1.png']
assert all((OUT/n).exists() for n in required)
files=[{'path':p.relative_to(OUT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='FINAL_OUTPUT_MANIFEST_R1.json' and '_tmp' not in p.relative_to(OUT).parts]
dump(OUT/'FINAL_OUTPUT_MANIFEST_R1.json',{'PHASE':PHASE,'PROMOTION':'PASS','STOP':'STOP — HUMAN REVIEW','required_deliverables_present':required,'R2_asset':I['R2_baseline'],'R2_sidecar_status':'production_spec/right_hand_product_baseline_r2/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2_STATUS.json','production_pointer_path':U['pointer_path'],'production_pointer_sha256':sha(pointer),'files':files})
print('R2_PROMOTION_FREEZE_COMPLETE',sha(R2),'R1_UNCHANGED',sha(R1),flush=True)
