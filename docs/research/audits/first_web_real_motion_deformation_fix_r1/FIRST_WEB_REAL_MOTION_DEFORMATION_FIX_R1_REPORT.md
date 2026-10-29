# FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1

**VERDICT = FIRST_WEB_REAL_MOTION_FIX_LIMIT_REACHED。STOP — HUMAN REVIEW。** 已完成两次局部 weight iteration 和一个 real-motion corrective。真实 7 秒 motion 中 first-web 仍有明显硬折/缺口，F130 上缘还出现更突出的薄片状亮边。不能输出 READY_FOR_HUMAN_FINAL_DEFORMATION_APPROVAL，也不能结束右手 deformation 或进入左手阶段。

## Human 结论与保护基线

上一阶段正式 Human Q1=NONE、Q2=NOT_RUN、Q3=NO，接受 CAUSE_NOT_ISOLATED，已在 PRIOR_HUMAN_DECISION_BIND_R1.json 绑定直接用户请求。没有继续 joint isolation、PIP/DIP 拆分、更多 component combinations、ROM 或 mapping forensic。

独立候选 `RIGHT_HAND_REAL_MOTION_FIRST_WEB_FIX_CANDIDATE_R1.blend` 保持 DESIGN_ONLY / HUMAN_APPROVAL_PENDING / NOT_PRODUCTION。冻结 baseline 未覆盖，SHA256 保持 `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`。输入 axis-corrected test 仍为 `a5190adc13d39318096490f8fd2c9956d0daff457d25753fa3c216eee2027bbd`。

## 两次局部权重调整

沿用此前批准的 149 顶点 first-web 支持区，覆盖 upper-web、index radial root、thumb-index bridge 和最小 thenar transition。两轮均从同一 source 权重出发，没有扩大支持区。只重分配 WRIST_R / THUMB_CMC_R / THUMB_MCP_R / INDEX_MCP_R；保持四组总量、其余已有 influence 和区域外全部权重。没有影响整掌、整拇指、食指链或其他三指，没有 generic weight smoothing。

目标为多个真实 motion 姿态的局部 deformation displacement 连续性：相对原 wrist rigid transform 保留 rest curvature，用受约束多姿态拟合，并用五个已批准非 ZERO 姿态的实际变形顶点作软约束。训练包含五个固定 frame 和相同 7 秒 Action 的均匀取样，不做 severity census。每轮都直接渲染五个 frame、完整 210 帧两视角 motion，以及六个 regression poses。

Weight1 的真实缺口仍在，同时 INDEX_MCP_45/FULL_OPP_L3 有新尖折回退，已拒收。Weight2 加强旧姿态约束，六个状态在普通实体初判中恢复可接受，但 F130/F76 等真实 motion 硬折仍然存在。于是按照用户条件使用一个 corrective；没有第三次权重调整。

## 唯一新的 corrective

`FIRST_WEB_REAL_MOTION_CORRECTIVE_R1` 只写一个新 key 的 99 个局部顶点，全部在同一 149 顶点支持区内；Basis 写入数=0。用 F130/F76/F205/F31 的局部 posed surface rounding 位移，通过未改变的 LBS skin 逆映射并平均为一个共享 delta。目标位移限制 2.8 mm，边界淡出；没有 per-frame keys、shape library、lattice、大块 thenar 体积补偿或 topology 改写。

激活只读前序 calibrated anatomical frame 的 INDEX MCP abduction 与 THUMB CMC 相对 neutral 的 swing elevation。用现有 local quaternion 和原 calibration 的解析逆变换，生成两个内部 scalar properties，再由 2 个变量控制 key：8 个现有 quaternion scalar 输入，总共 10 个 driver variables；没有控制骨、额外 Action channels 或新的运动 solver。代码与表达式完整记录在 REAL_MOTION_CORRECTIVE_R1.json。没有复制 Euler X/Z 作为解剖分量。

实际区别依据：F130/F205/F31 key=1；F76≈0.548；F61 low-defect key=0。前序已知 low-defect F181 仅作辅助 driver 检查，key≈0.234，说明相关性有重叠，不是完美 defect classifier，也不是根因确认。六个已批准 regression poses 的新 key 均=0；旧 key/driver 完全不变。驱动接线验证时发现初始 gate 会激活 FULL_OPP_L1，在首个候选保存前加了同一 INDEX anatomical articulation 的 neutral exclusion；未改 shape delta、未创建第二个 corrective。

## 完整真实 motion 可见结果

同一 PianoVAM 11.5–18.5 sec、421 observations、mapping iteration2、原 quaternion smoothing、原 Action keys/timing 全部保留。每轮视频都是完整 210 帧 / 30fps / 7.000sec；另检查全部 421 观测，包含末尾 endpoint。两视角为 palmar/pianist-side close 与 first-web oblique，覆盖 web、index root、thumb root、thenar 和 palmar contour；regression 额外显示 full dorsal。

BEFORE/AFTER 相机、材质、光照、显示平滑匹配。视频中心只由 BEFORE 原 motion 得到，AFTER 原样复用；没有用重新取景藏缺口。完整帧 QC 用于画面连续性和可见质量，不重建全段 severity ranking。

| Frame | Codex 初判 |
| --- | --- |
| F130 | FAIL：明显阶梯状深折仍在，upper-web 薄片状亮边更突出 |
| F76 | 局部减轻，但硬折和内陷未消失 |
| F205 | 折线部分软化，仍有根部折边 |
| F31 | 局部软化，仍有残余折线 |
| F61 | 相对低缺陷对照保持，新 key=0 |

没有额外加入 defect frames。NEW_VISIBLE_DEFECT_COUNT=1 指一种新增/加重的局部 upper-web flap 外观；VISIBLE_FIRST_WEB_BLOCKER_COUNT=2 指持续的深折与该 flap 两种 issue，不是整段逐帧数量统计。该候选不能被当成成功修复。

## 六个 regression 与 minimum checks

ZERO/RSSF、INDEX_MCP_45、CMC_OPP_30、FULL_OPP_L1/L2/L3 的 ordinary-solid BEFORE/AFTER 初判均保持可接受；最终 Human 尚未答复。保护 thenar 主体、thumb-root 和 dorsal appearance；新 corrective 在六姿态全部 inactive。

NaN/Inf=0、collapsed face=0、degenerate edge=0，Action bone flip=0、>90° catastrophic local quaternion step=0。每次恢复候选 ZERO 的最大误差=0，ZERO_RESTORE=PASS。独立保存后重读确认 Basis、topology/vertex IDs、UV/material、21 bones/hierarchy/rest joints/roll/inherit settings/constraints/thumb chain、全部原 Action payload、原 corrective/driver 精确保持。区域外权重与区域内其它 influence 精确保持。

ZERO 的输入/候选求值差是约 0.00006749 mm 的 LBS 浮点差，Basis 坐标仍逐项精确相同；这个比较与恢复候选自身 ZERO 的 0 mm 不同。辅助“大拉伸比”提示 BEFORE 最大8、AFTER最大7，不等于实际 tearing 数量；普通两视角未见 gross tearing/gross penetration，仍保留局部 web 缺陷。MACHINE_SAFETY=PASS_MINIMUM_ONLY 不能推导产品画面通过。没有 R3/true-cap/hidden crossing/2127 edges/normal-dot/full Stage6。

FINGERTIP_ISSUE_STATUS=DEFERRED：没有修改 PIP/DIP mapping、finger rig、finger weights 或 finger corrective。动作中 fast fingertip bend 问题仍未处理。

## Human review

Q1. 完整 7 秒真实钢琴动作中，虎口缺口是否已经消失或达到自然可接受程度？ YES / NO

Q2. 本轮修复是否造成新的明显手掌 / 拇指 / 食指根部问题？ NO / YES

Q3. 此前批准的 ZERO 与代表姿态是否保持可接受？ YES / NO

Q4. 右手 deformation 是否可以结束，进入后续真实 motion / 左手阶段？ YES / NO

当前四个 Human 字段保持 null。review.html 提供两个完整 BEFORE/AFTER 视频、五个固定 frame 两视角对比、六个 AFTER regression 状态与 BEFORE 切换。

本轮修复上限已达到，不再做 weight iteration、corrective R2、更多 shape keys、mapping/指尖修复、左手或 Web export。下一步仅可在新的明确任务中重新评估 source mesh / rig deformation architecture 是否值得继续；本轮没有开始该评估。**STOP — HUMAN REVIEW。**

## 最终字段

```json
{
  "PHASE": "FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1",
  "SOURCE_BASELINE_SHA256": "4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2",
  "SOURCE_ACTION": "PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1",
  "SOURCE_MOTION_CHANGED": "NO",
  "BASIS_GEOMETRY_CHANGED": "NO",
  "BASIS_VERTEX_POSITION_WRITES": 0,
  "LOCAL_WEIGHT_REGION_VERTEX_COUNT": 149,
  "WEIGHT_ITERATION_COUNT": 2,
  "NEW_CORRECTIVE_COUNT": 1,
  "CORRECTIVE_REQUIRED": "YES_WEIGHTS_INSUFFICIENT",
  "REAL_7S_FIRST_WEB_STATUS": "FAIL_VISIBLE_BLOCKER_REMAINS",
  "F130_STATUS": "FAIL_DEEP_STEPPED_FOLD_AND_UPPER_WEB_FLAP",
  "F76_STATUS": "PARTIAL_IMPROVEMENT_RESIDUAL_HARD_CREASE",
  "F205_STATUS": "PARTIAL_IMPROVEMENT_RESIDUAL_WEB_FOLD",
  "F31_STATUS": "PARTIAL_IMPROVEMENT_RESIDUAL_CREASE",
  "ZERO_REGRESSION": "PRELIMINARY_ACCEPTABLE_HUMAN_PENDING",
  "INDEX_MCP_45_REGRESSION": "PRELIMINARY_ACCEPTABLE_HUMAN_PENDING",
  "CMC_OPP_30_REGRESSION": "PRELIMINARY_ACCEPTABLE_HUMAN_PENDING",
  "FULL_OPP_L1_REGRESSION": "PRELIMINARY_ACCEPTABLE_HUMAN_PENDING",
  "FULL_OPP_L2_REGRESSION": "PRELIMINARY_ACCEPTABLE_HUMAN_PENDING",
  "FULL_OPP_L3_REGRESSION": "PRELIMINARY_ACCEPTABLE_HUMAN_PENDING",
  "NEW_VISIBLE_DEFECT_COUNT": 1,
  "new_visible_defect_note": "F130 upper-web thin bright slit/flap is more prominent after corrective; counted as one localized visible issue type, not a frame census.",
  "VISIBLE_FIRST_WEB_BLOCKER_COUNT": 2,
  "blocker_count_scope": "Two issue types: persistent deep stepped folds and the newly prominent upper-web flap. Not a full-segment severity census.",
  "FINGERTIP_ISSUE_STATUS": "DEFERRED",
  "ZERO_RESTORE": "PASS",
  "MACHINE_SAFETY": "PASS_MINIMUM_ONLY",
  "NaN_Inf": 0,
  "collapsed_face": 0,
  "degenerate_edge": 0,
  "gross_tearing_visible": 0,
  "gross_penetration_visible": 0,
  "bone_flip": 0,
  "catastrophic_motion_jump": 0,
  "machine_scope": "Minimum finite/area/length/restore/action-continuity checks plus ordinary visible gross screen; product first-web failure remains. No hidden crossing, R3, true-cap, 2127-edge or normal-dot audit.",
  "FROZEN_BASELINE_OVERWRITTEN": "NO",
  "PRODUCTION_PROMOTION": "NO",
  "ASSET_STATUS": "DESIGN_ONLY_HUMAN_APPROVAL_PENDING_NOT_PRODUCTION",
  "VERDICT": "FIRST_WEB_REAL_MOTION_FIX_LIMIT_REACHED",
  "STOP": "HUMAN REVIEW",
  "candidate": {
    "path": "audits/first_web_real_motion_deformation_fix_r1/RIGHT_HAND_REAL_MOTION_FIRST_WEB_FIX_CANDIDATE_R1.blend",
    "sha256": "c93fc9b068b5704b79c2c0aa2ff185540b06ca2830e36f956770fa5fdcb4f352"
  },
  "prior_Human_decision": {
    "Q1": "NONE",
    "Q2": "NOT_RUN",
    "Q3": "NO",
    "PRIMARY_CAUSE_CLASSIFICATION": "CAUSE_NOT_ISOLATED"
  },
  "HUMAN_Q1": null,
  "HUMAN_Q2": null,
  "HUMAN_Q3": null,
  "HUMAN_Q4": null,
  "same_source_window_sec": [
    11.5,
    18.5
  ],
  "source_observations": 421,
  "video_frames": 210,
  "video_duration_sec": 7,
  "USAGE_SCOPE": "INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY",
  "LICENSE": "CC BY-NC-SA 4.0",
  "further_patch_iteration_started": false,
  "left_hand_started": false,
  "web_export": false
}
```
