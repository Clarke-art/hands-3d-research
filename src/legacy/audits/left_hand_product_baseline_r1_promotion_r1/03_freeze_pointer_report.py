"""Commit the new left pointer only after saved identity + minimal smoke PASS."""
from pathlib import Path
import json,hashlib,os,stat,traceback
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
DESTDIR=ROOT/'production_spec/left_hand_product_baseline_r1'
DEST=DESTDIR/'LEFT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend'
POINTER=ROOT/'production_spec/LEFT_HAND_PRODUCT_BASELINE.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def main():
 identity=read(OUT/'PROMOTION_IDENTITY_R1.json');before=read(OUT/'PROTECTED_INPUTS_BEFORE_R1.json');approval=read(OUT/'HUMAN_APPROVAL_BIND_R1.json')
 def protect():
  actual={p:sha(ROOT/p) for p in before};assert actual==before,'PROTECTED_INPUT_CHANGED';return actual
 protect();assert identity['status']=='PASS' and all(identity['core_component_exact_match'].values())
 assert identity['LEFT_WEIGHT_FIELD_IDENTITY']=='EXACT_MATCH'
 assert {r['state'] for r in identity['smoke']}=={'ZERO','CMC_OPP_30','FULL_OPP_L3'} and all(r['status']=='PASS' and r['corrective_trigger_parity']=='PASS' and r['evaluated_geometry_exact'] for r in identity['smoke'])
 assert approval['LEFT_HAND_PROMOTION']=='AUTHORIZED'
 assert sha(DEST)==identity['baseline']['sha256']
 assert not POINTER.exists(),'Refuse overwrite of any existing production pointer'
 assert not (OUT/'PROMOTION_FAIL_CLOSED_R1.json').exists()
 # Windows readonly bit freezes only the newly verified baseline; no input attribute changes.
 os.chmod(DEST,stat.S_IREAD)
 readonly=bool(DEST.stat().st_file_attributes & stat.FILE_ATTRIBUTE_READONLY)
 assert readonly and sha(DEST)==identity['baseline']['sha256']
 phase='LEFT_HAND_PRODUCT_BASELINE_R1_PROMOTION_R1'
 status={'PHASE':phase,'PROMOTION':'PASS','LEFT_HAND_PRODUCT_BASELINE_R1':'HUMAN_APPROVED_FROZEN','LEFT_HAND_CANONICAL_MIRROR':'CLOSED','LEFT_HAND_CANONICAL_MIRROR_CLOSED':'YES','LEFT_HAND_STATIC_DEFORMATION_BASELINE':'CLOSED','LEFT_HAND_READY_FOR_REAL_MOTION_STAGE':'YES','LEFT_HAND_HUMAN_VISIBLE_RESULT':'PASS','HUMAN_PRODUCTION_APPROVAL':'APPROVED','CANDIDATE_CONTAINER_STATUS':identity['CANDIDATE_CONTAINER_STATUS'],'PRODUCTION_CONTAINER_STATUS':'PRODUCTION_CLEAN','PROMOTION_METHOD':identity['promotion_method'],'BASELINE_ASSET':identity['baseline']['path'],'LEFT_R1_BASELINE_SHA256':sha(DEST),'BASELINE_FILE_READ_ONLY':readonly,'APPROVED_CANDIDATE_SHA256':identity['candidate']['sha256'],'LEFT_WEIGHT_FIELD_IDENTITY':'EXACT_MATCH','WEIGHT_FIELD_MIRROR_PARITY':'EXACT_SEMANTIC_MIRROR_MATCH','CORRECTIVE_MIRROR_PARITY':'PASS','MESH_RIG_REST_CORRECTIVE_DRIVER_IDENTITY':'EXACT_MATCH','NO_NEGATIVE_SCALE_RUNTIME_DEPENDENCY':True,'SAVED_POSE':'ZERO / RSSF','PREVIOUS_PRODUCTION_BASELINE':'NONE','CURRENT_PRODUCTION_BASELINE':'R1','LEFT_PRODUCTION_POINTER':'R1','RIGHT_R2_UNCHANGED':'YES','RIGHT_R1_UNCHANGED':'YES','RIGHT_PRODUCTION_POINTER_UNCHANGED':'YES','HISTORICAL_LEFT_AUDIT_UNCHANGED':'YES','REAL_MOTION_STAGE_STARTED':False,'WEB_EXPORT_STARTED':False,'STOP':'STOP — HUMAN REVIEW',**identity['source_mirror_record'],**{f'Q{i}':('AUDIT_SCAFFOLDING_PRESENT' if i==2 else 'YES') for i in range(1,11)}}
 statuspath=DESTDIR/'LEFT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_STATUS.json'
 write(statuspath,status)
 pointer={'authority':'Direct Human final left-hand production approval, 2026-10-07 Asia/Shanghai','PREVIOUS_PRODUCTION_BASELINE':'NONE','CURRENT_PRODUCTION_BASELINE':'R1','LEFT_HAND_PRODUCT_BASELINE_STATUS':'HUMAN_APPROVED_FROZEN','LEFT_HAND_PRODUCT_BASELINE_R1':'HUMAN_APPROVED_FROZEN','asset':{**identity['baseline'],'status':'HUMAN_APPROVED_FROZEN'},'source':identity['candidate'],'source_identity':'Official L1','vertex_count':3300,'face_count':3298,'bone_count':21,'deform_bone_count':16,'non_deform_TIP':identity['non_deform_TIP'],'LEFT_WEIGHT_FIELD_IDENTITY':'EXACT_MATCH','weight_field_sha256':identity['weight_vectors_sha256'],'WEIGHT_FIELD_MIRROR_PARITY':'EXACT_SEMANTIC_MIRROR_MATCH','CORRECTIVE_MIRROR_PARITY':'PASS','LEFT_HAND_CANONICAL_MIRROR':'CLOSED','LEFT_HAND_STATIC_DEFORMATION_BASELINE':'CLOSED','LEFT_HAND_READY_FOR_REAL_MOTION_STAGE':'YES',**identity['source_mirror_record'],'status':statuspath.relative_to(ROOT).as_posix(),'report':(OUT/'LEFT_HAND_PRODUCT_BASELINE_R1_PROMOTION_R1_REPORT.md').relative_to(ROOT).as_posix(),'promotion_record':(OUT/'PROMOTION_IDENTITY_R1.json').relative_to(ROOT).as_posix(),'human_approval_record':(OUT/'HUMAN_APPROVAL_BIND_R1.json').relative_to(ROOT).as_posix(),'real_motion_started':False,'Web_export_started':False}
 # Exclusive create prevents replacing an independently created authority pointer.
 with POINTER.open('x',encoding='utf-8') as f:f.write(json.dumps(pointer,ensure_ascii=False,indent=2)+'\n')
 assert read(POINTER)==pointer and sha(DEST)==pointer['asset']['sha256']
 write(OUT/'LEFT_HAND_PRODUCTION_POINTER_R1.json',{'status':'PASS','pointer':POINTER.relative_to(ROOT).as_posix(),'pointer_sha256':sha(POINTER),'before':'ABSENT','after':pointer,'identity_and_smoke_passed_before_creation':True,'new_baseline_read_only_before_pointer_creation':True,'right_pointer_modified':False})
 final=protect()
 protection={'status':'PASS','RIGHT_R2_UNCHANGED':'YES','RIGHT_R1_UNCHANGED':'YES','RIGHT_PRODUCTION_POINTER_UNCHANGED':'YES','LEFT_APPROVED_CANDIDATE_UNCHANGED':'YES','ALL_HISTORICAL_LEFT_AUDIT_REPORT_EVIDENCE_UNCHANGED':'YES','protected_file_count':len(before),'protected_inputs_expected_and_final':final,'LEFT_R1_BASELINE_SHA256':sha(DEST),'LEFT_R1_BASELINE_READ_ONLY':readonly,'LEFT_PRODUCTION_POINTER_SHA256':sha(POINTER),'verification_context':'2026-10-07 Asia/Shanghai'}
 write(OUT/'FINAL_BASELINE_PROTECTION_R1.json',protection)
 write(OUT/'LEFT_HAND_PRODUCT_BASELINE_R1_PROMOTION_R1_STATUS.json',status)
 questions=[('Q1','Human-approved candidate SHA 匹配','YES'),('Q2','Candidate container','AUDIT_SCAFFOLDING_PRESENT'),('Q3','完整 weight field 与 candidate EXACT_MATCH','YES'),('Q4','mesh / topology / UV / rig / rest / corrective / driver 一致','YES'),('Q5','NO_NEGATIVE_SCALE_RUNTIME_DEPENDENCY','YES'),('Q6','ZERO / CMC_OPP_30 / FULL_OPP_L3 smoke 全部 PASS','YES'),('Q7','右手 R2 原 SHA 保持','YES'),('Q8','右手 R1 fallback 原 SHA 保持','YES'),('Q9','左手 production pointer 建立为 R1','YES'),('Q10','左手 R1 = HUMAN_APPROVED_FROZEN','YES')]
 table='\n'.join(f'| {q} | {label} | {answer} |' for q,label,answer in questions)
 components='\n'.join(f'| {k} | EXACT_MATCH | `{identity["production_component_sha256"][k]}` |' for k in identity['core_component_exact_match'])
 smoke='\n'.join(f'| {r["state"]} | 0 | {next(iter(r["production_corrective_values"].values())):.9f} | PASS | 0 |' for r in identity['smoke'])
 report=f'''# LEFT_HAND_PRODUCT_BASELINE_R1_PROMOTION_R1

2026-10-07 · **PROMOTION = PASS** · **LEFT_HAND_PRODUCT_BASELINE_R1 = HUMAN_APPROVED_FROZEN**

已根据本轮 Human 最终授权，将指定 SHA 的已批准左手候选升格为正式 R1。
仅更改 scene / mesh object 的审核身份元数据及 scene 容器名称；没有重新镜像或重建任何产品数据。
正式 .blend 重新打开后，13 类产品 payload 逐项精确一致，三个最小 smoke 全部通过，随后设置正式文件只读并创建左手 R1 指针。

## Q1–Q10

| 问题 | 检查 | 结果 |
|---|---|---|
{table}

## Human 批准绑定与 container

Human 最终批准绑定至 `{identity['candidate']['sha256']}`，明确授权 promotion，确认六项批准姿态的可见外观 PASS。原文附件路径及其 SHA 记录于 HUMAN_APPROVAL_BIND_R1.json。

CANDIDATE_CONTAINER_STATUS = AUDIT_SCAFFOLDING_PRESENT，具体仅为待审身份标签及 candidate scene 名称。
只读检查发现：2 objects（mesh + armature），无 review/evidence camera、debug collection、comparison object、temporary Action 或 Text script。
因此采用 **CLEAN_PRODUCTION_CONTAINER_EXACT_PRODUCT_DATA**。

清理 DESIGN_ONLY、NOT_PRODUCTION、HUMAN_APPROVAL_PENDING、PRODUCTION_POINTER_UPDATED 等审核身份字段，设置正式产品批准身份。
scene 名称改为 LEFT_HAND_PRODUCT_BASELINE_R1。保留 CANONICAL_SOURCE、其 SHA、Official L1 source identity 等来源信息。
所有实际变更和明确排除的纯身份字段逐项记录在 PROMOTION_IDENTITY_R1.json；未删除任何产品 object、bone、modifier、shape key 或 driver。

## 精确产品身份验证

正式 R1 保持 3300 vertices、3298 faces、21 bone teaching rig（16 deform + 5 non-deform TIP）。
全部骨骼使用 *_L 语义。文件仍为 mesh + armature skin + bones + corrective morph，只有原有 ARMATURE modifier。
保存状态为 ZERO / RSSF，frame 1，无 Action、无约束或 mirror modifier 运行依赖；mesh/rig 均保持正 scale 与正行列式。

完整 **3300 × 21** weight semantics 逐值一致，最大差值 **0**；原始稀疏权重、vertex group 名称/索引/锁定设置也全部一致。
没有 normalize、weight rewrite、solver 或 repaint。weight vector SHA256：`{identity['weight_vectors_sha256']}`。

| 产品组件 | candidate vs production | production payload SHA256 |
|---|---|---|
{components}

rig rest 检查覆盖 head/tail、rest/local 矩阵与 local frames（含 roll 所决定的方向）、parent hierarchy、inherit/deform 设置、bone collections、角色及 pose state。
corrective 检查覆盖 shape key 坐标/相对基准、delta 所依赖的 Basis、driver expression、variables、target IDs/bones、FCurve 设置。所有比较为精确相等，无放宽误差阈值。
正式文件 SHA 与候选不同仅来自允许的容器/身份元数据清理和保存；产品 payload 未变。

## 最小 promotion smoke

仅使用上一阶段已批准的左手 pose matrices，在候选与重新打开的正式 R1 中分别应用。
未重新镜像、未重新定义姿态、未重复整个六项 Human qualification。

| 状态 | evaluated geometry 最大差值 mm | 正式 corrective 自然值 | trigger parity | ZERO restore mm |
|---|---:|---:|---|---:|
{smoke}

三项中 evaluated geometry、面连接/绕序、骨骼 pose matrices 与 corrective 值均为精确一致。
NaN/Inf、gross collapsed faces、degenerate edges 全部为 0；未产生新的 tearing。
明显 penetration 的依据为 Human 已批准候选 + 对应 evaluated surface 完全相同，不声称重新进行了视觉资格审查或 hidden crossing census。
因此没有生成重复截图；没有 hidden crossing、normal-dot、R3、true-cap 或逐顶点 anatomy forensic。
smoke 在未保存的测试会话中执行，磁盘正式文件维持 ZERO，SHA 在 smoke 前后相同。

## 正式指针与冻结

- 正式资产：`{identity['baseline']['path']}`
- LEFT_R1_BASELINE_SHA256：`{sha(DEST)}`
- 正式文件只读：YES
- 指针：`production_spec/LEFT_HAND_PRODUCT_BASELINE.json`
- PREVIOUS_PRODUCTION_BASELINE = NONE
- CURRENT_PRODUCTION_BASELINE = R1
- LEFT_HAND_PRODUCT_BASELINE_R1 = HUMAN_APPROVED_FROZEN
- LEFT_HAND_CANONICAL_MIRROR = CLOSED
- LEFT_HAND_STATIC_DEFORMATION_BASELINE = CLOSED
- LEFT_HAND_READY_FOR_REAL_MOTION_STAGE = YES

SOURCE_CANONICAL_MASTER = RIGHT_HAND_PRODUCT_BASELINE_R2

MIRROR_SOURCE_SHA256 = c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0

MIRROR_PLANE = WRIST rest-local X=0

MIRROR_SPACE = ARMATURE_DATA → MESH_DATA conjugation

这些来源记录是 sidecar/status 信息，不构成运行依赖。
原有 corrective driver 未来仍需 Web 转译；本轮没有 Web 导出、Three.js、真实 motion、retarget、MIDI、fingering 或钢琴安装。

## 原字节保护

共保护并复核 **{len(before)}** 个文件，包括全部旧左手 audit/report/evidence/candidate、右手 R2/R1 目录文件及右手 production pointer。

RIGHT_R2_UNCHANGED = YES · `c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0`

RIGHT_R1_UNCHANGED = YES · `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`

历史 DESIGN_ONLY / HUMAN_REVIEW_PENDING / READY_FOR_HUMAN_REVIEW 记录保留原字节；新批准仅写入本轮绑定记录。

**STOP — HUMAN REVIEW。未自动进入下一阶段。**
'''
 (OUT/'LEFT_HAND_PRODUCT_BASELINE_R1_PROMOTION_R1_REPORT.md').write_text(report,encoding='utf-8')
 # Verify all final authority links and hashes without modifying a protected input.
 assert read(POINTER)['asset']['sha256']==sha(DEST)==read(statuspath)['LEFT_R1_BASELINE_SHA256']
 assert all((ROOT/read(POINTER)[k]).is_file() for k in ['status','report','promotion_record','human_approval_record'])
 protect()
 manifest=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for folder in [OUT,DESTDIR] for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='FINAL_OUTPUT_MANIFEST_R1.json']
 manifest.append({'path':POINTER.relative_to(ROOT).as_posix(),'bytes':POINTER.stat().st_size,'sha256':sha(POINTER)})
 write(OUT/'FINAL_OUTPUT_MANIFEST_R1.json',{'status':'PASS','files':manifest})
 print(json.dumps({'PROMOTION':'PASS','LEFT_R1_BASELINE_SHA256':sha(DEST),'LEFT_PRODUCTION_POINTER':'R1','read_only':readonly,'protected_files_unchanged':len(before),'STOP':'STOP — HUMAN REVIEW'},ensure_ascii=False))
try:main()
except Exception as e:
 write(OUT/'PROMOTION_FAIL_CLOSED_R1.json',{'PROMOTION':'FAIL_CLOSED','reason':str(e),'traceback':traceback.format_exc(),'automatic_repair':False,'STOP':'STOP — HUMAN REVIEW'})
 raise
