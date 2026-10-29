# PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1

本轮 Codex 初判：**CAUSE_NOT_ISOLATED**；`PRIMARY_TRIGGER_COMPONENT = NOT_ISOLATED_TO_TESTED_JOINT_COMPONENTS`。A–D 均未明显消除缺口，只有少数帧的小改善。不能据此确认 combined-motion skin sensitivity，也没有新的 source anatomical semantics 违规证据。**STOP — HUMAN REVIEW**。

## 绑定与选帧

上一阶段 Human Q1=NO、Q2=YES、Q3=REJECT，`RETARGET_AXIS_MAPPING_PARTIAL_CAUSE=HUMAN_CONFIRMED` 已单独绑定，未改写历史审核记录。冻结右手保持 `HUMAN_APPROVED_FROZEN`。

使用原 axis-corrected test、Action `PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1`、相同 PianoVAM 11.5–18.5 sec / 421 observations。从已有 iteration-2 NEW close sheet 中选 F130（MOST_SEVERE）、F76/F205（SEVERE）、F31（MODERATE），F61 为相对 low-defect control。上述标签是残余 NEW 的相对可见严重度，未照搬旧 retarget 的严重度，也未重做全段 census；F61 仍有浅折痕，未宣称完全正常。

## 临时隔离方法

只在未保存的 Blender 运行时 pose 上测试。前序 mapping_core.py 原样只读导入，iteration=2。A/B 从 Solver.raw 内部已有 source flexion/abduction 读值，重建相同 `frame(direction, palm radial)`，通过原 anatomical rest frame / roll calibration 映射；仅目标 flexion 或 abduction 恢复 0。冻结 RSSF rest 的内建弯曲、张开与 roll 仍保留。没有 Euler X/Z 清零。

C 恢复整个独立映射的 thumb CMC swing/opposition stance 到前序 iteration-2 median CMC→MCP calibrated-neutral。原 CMC 未复制可观测性不足的 axial twist，因此这里将 in-plane swing 和相对 neutral 的 out-of-plane stance 一起恢复；neutral 的绝对 elevation 并非强行设为 0。Thumb MCP/IP local hinge bends 全部保持。D 只把 thumb MCP signed anatomical hinge bend 恢复 0。

每个 OFF 均在原来的 i−1/i/i+1 source observations 上处理目标分量，再使用原 quaternion sign alignment、[.25,.5,.25] 和 normalization。其余骨骼 local quaternion、location、scale、rotation mode 完全复制 saved corrected Action 的实际值。Quaternion 平滑非线性，目标骨的四个 quaternion 系数可同时改变；这不表示额外修改另一解剖分量，也不新增平滑。每帧 saved Action 与原 Solver.smoothed 的 quaternion 数值在 1e−6 内一致。

既有 corrective/driver 始终自然求值，未静音或覆盖；本轮所选 A–D 中自然 corrective 值均为 0。正式 Action 数据不变，运行时只临时分离 Action binding 后写目标 pose；每次测试立即重新绑定并校验 evaluated mesh 精确恢复。未保存任何 .blend。

## 两视角结果

每帧 BASELINE + A/B/C/D，固定同一 Palmar/Thenar Close 和 First-Web Oblique 相机、960×880、光照、clay 材质和显示平滑，共 50 张 matched renders。显示副本只用于未保存的诊断 scene，没有改动资产 mesh。

| Frame | Role | INDEX ABD OFF | INDEX FLEX OFF | THUMB CMC SWING OFF | THUMB MCP FLEX OFF |
| --- | --- | --- | --- | --- | --- |
| 130 | MOST_SEVERE | NO_EFFECT | NO_EFFECT | NO_EFFECT | NO_EFFECT |
| 76 | SEVERE | SMALL_IMPROVEMENT | NO_EFFECT | NO_EFFECT | NO_EFFECT |
| 205 | SEVERE | NO_EFFECT | NO_EFFECT | SMALL_IMPROVEMENT | NO_EFFECT |
| 31 | MODERATE | SMALL_IMPROVEMENT | NO_EFFECT | NO_EFFECT | NO_EFFECT |
| 61 | CONTROL | NO_EFFECT | NO_EFFECT | NO_EFFECT | NO_EFFECT |

F130 的阶梯状深折线在所有 OFF 中保留。A 在 F76/F31 掌側只有稍浅的局部折线，斜视凹角仍在。C 在 F205 缩短部分折线，但尖角和凹折保留；thumb 改变位置不能直接等同缺陷消除。D 主要改变 thumb 远段姿态，first-web 根部缺口仍在。没有 CLEAR_IMPROVEMENT 或接近消失的单项。

**COMBINED_TEST_RUN=NO**：A 与 C 均未表现明显贡献，未满足用户规定的组合测试前提。E 的因果效应未知，不能把 NOT_RUN 当成 NO_EFFECT，不能声称已证实或排除 combined-motion skin sensitivity。不继续拆其他关节、PIP/DIP 或几十种组合。

## 辅助记录与保护检查

JOINT_COMPONENT_VALUES_R1.json 记录每帧每条件原分量、neutralized 分量、实际 baseline/diagnostic local quaternion、三个原邻近观测的 landmark digest 和原 anatomical components。数值只供重现，不做 ROM/医学角度判断。MACHINE_CHECK_R1.json 记录所有未测试 local channels 精确一致、同相机、同 source/frame/mapping/smoothing、同 mesh/Basis/weights/rest/joint layout/roll/hierarchy/corrective/driver、全部 Action payload hash 一致和每次精确 restore。

冻结 baseline SHA256 仍为 `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`；motion test SHA256 仍为 `a5190adc13d39318096490f8fd2c9956d0daff457d25753fa3c216eee2027bbd`。原 mapping_core.py 与四个 sample 文件 hash 均前后相同。未运行 R3、true-cap、hidden crossing、normal-dot、Stage6 或 2127 edges。

FINGERTIP_OBSERVATION = 所选静帧中 INDEX MCP OFF 只改变食指整链姿态、PIP/DIP local bend 保持不变，未重新评估 fast bend，也未开启修复。

## Human review（本轮尚未回答）

Q1. 哪一个单独 component OFF 对虎口缺口改善最明显？ INDEX_MCP_ABDUCTION / INDEX_MCP_FLEXION / THUMB_CMC_SWING / THUMB_MCP_FLEXION / NONE

Q2. 是否只有 INDEX_MCP + THUMB_CMC 组合隔离后才明显恢复？ YES / NO / NOT_RUN

Q3. 是否已经足以定位为 combined-motion skin deformation 问题？ YES / NO

review.html 提供 frame/condition 下拉，以及每个条件两个视角与相同帧 BASELINE 对照、Codex preliminary effect。所有本轮 Human 字段保持 null。OFF 仅用于 causal isolation，不表示真实钢琴动作应为零；不推断 index 不应外展或 thumb opposition 错误。

本轮没有进行 weights/mesh/Basis/rig/mapping/source/Action/corrective/driver 修复，没有换 sample、左手或 Web export。停在本轮 Human 审核；下一阶段也未自动启动。

## 最终字段

```json
{
  "PHASE": "PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1",
  "SOURCE_ACTION": "PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1",
  "SOURCE_MOTION_CHANGED": "NO",
  "SELECTED_DEFECT_FRAME_COUNT": 4,
  "CONTROL_FRAME_COUNT": 1,
  "INDEX_MCP_ABDUCTION_EFFECT": "SMALL_IMPROVEMENT",
  "INDEX_MCP_FLEXION_EFFECT": "NO_EFFECT",
  "THUMB_CMC_SWING_EFFECT": "SMALL_IMPROVEMENT",
  "THUMB_MCP_FLEXION_EFFECT": "NO_EFFECT",
  "COMBINED_TEST_RUN": "NO",
  "COMBINED_EFFECT": "NOT_RUN",
  "PRIMARY_TRIGGER_COMPONENT": "NOT_ISOLATED_TO_TESTED_JOINT_COMPONENTS",
  "COMBINED_MOTION_SKIN_SENSITIVITY": "NOT_ESTABLISHED",
  "RETARGET_COMPONENT_INTERPRETATION_STILL_SUSPECT": "NO_NEW_SEMANTIC_EVIDENCE",
  "FINGERTIP_OBSERVATION": "所选静帧中 INDEX MCP OFF 只改变食指整链姿态、PIP/DIP local bend 保持不变，未重新评估 fast bend，也未开启修复。",
  "BASELINE_MODIFIED": "NO",
  "MESH_MODIFIED": "NO",
  "WEIGHTS_MODIFIED": "NO",
  "RIG_MODIFIED": "NO",
  "CORRECTIVE_MODIFIED": "NO",
  "DRIVER_MODIFIED": "NO",
  "ACTION_MODIFIED": "NO",
  "MAPPING_IMPLEMENTATION_MODIFIED": "NO",
  "SMOOTHING_MODIFIED": "NO",
  "PRIMARY_CAUSE_CLASSIFICATION": "CAUSE_NOT_ISOLATED",
  "VERDICT": "CAUSE_NOT_ISOLATED_PENDING_HUMAN_REVIEW",
  "STOP": "HUMAN REVIEW",
  "classification_authority": "Codex preliminary; no current Human answers recorded",
  "HUMAN_Q1": null,
  "HUMAN_Q2": null,
  "HUMAN_Q3": null,
  "MACHINE_CHECK": "PASS",
  "baseline_sha256": "4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2",
  "motion_test_sha256": "a5190adc13d39318096490f8fd2c9956d0daff457d25753fa3c216eee2027bbd",
  "same_source_window_seconds": [
    11.5,
    18.5
  ],
  "source_observation_count": 421,
  "render_count": 50,
  "no_blend_saved": true,
  "skin_repair_started": false,
  "PRODUCTION_PROMOTION": "NO",
  "USAGE_SCOPE": "INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY",
  "LICENSE": "CC BY-NC-SA 4.0"
}
```
