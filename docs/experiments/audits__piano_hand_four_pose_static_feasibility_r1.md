# audits/piano_hand_four_pose_static_feasibility_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> |姿态|任务|固定 pad 垂直差|实际皮肤 pad 差|可奏区域|分类|

出处：[PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md](../research/audits/piano_hand_four_pose_static_feasibility_r1/PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md)

## 技术路线

> 求解前锁定 `STATIC_POSTURE_POLICY_R1.json`（链接见原报告），SHA256 `d289ec7eb9089bfde1bd18958e0dcc321e5c0cd24c89e2e9c0a627e4344cec61`；锁同时记录求解脚本 SHA。工程 bounds 未根据结果放宽，既有 3mm/2mm 接触容差不变。正向 flex + 基部 spread 从已经弯曲的 RSSF rest 增量设置，不称为人体生理极限。左手闲置三指强 prior、较小增量边界，避免统一伸直/钩爪。两手每对共享一个 XYZ/yaw/pitch/roll 变换，使用现有21骨旋转；没有新 helper bone、逐顶点修改、scale 或 corrective。

出处：[PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md](../research/audits/piano_hand_four_pose_static_feasibility_r1/PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md)

> 一套政策内对左/右共享-root 的两姿态各联合求解一次，共一个四姿态候选。两次求解分别 50 / 18 evaluations 收敛，初始化各1次、重启0次、参数 sweep0次。蒙皮 proxy 来自冻结现有权重，用于计划；最终接触/净空来自保存后重新打开的实际 Blender 皮肤，未复用旧动态 IK。

出处：[PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md](../research/audits/piano_hand_four_pose_static_feasibility_r1/PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md)

## 测试结论

> **FINAL_STATUS = STATIC_FEASIBILITY_PARTIAL**。本轮已按 Human 新授权真实生成一个包含四个静态场景的候选，不再用外部视频缺失阻止实验。L1/L2 为 PASS_CANDIDATE，等待 Human 自然度审核；R1/R2 为 FAIL_CLEARANCE，右手食指/无名指邻黑键风险保留。全部正式资产保持不变。

出处：[PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md](../research/audits/piano_hand_four_pose_static_feasibility_r1/PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md)

> |L1|小指 D2 / 拇指 D3 准备|0.586mm|0.601mm|inside|PASS_CANDIDATE|

出处：[PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md](../research/audits/piano_hand_four_pose_static_feasibility_r1/PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md)

## 失败原因与证据边界

> 技术阻断 NONE；IK_SOLVER_FAILURE 未观察（两次联合解收敛）；当前归因是单次固定姿态/代理净空政策的限制，保留左手边界饱和与右手邻键风险。**GEOMETRY_LIMIT 未证明**，没有必须重建正式 hand mesh/rig 的证据。不再调参或生成第二候选。

出处：[PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md](../research/audits/piano_hand_four_pose_static_feasibility_r1/PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md)

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/piano_hand_four_pose_static_feasibility_r1/PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md](../research/audits/piano_hand_four_pose_static_feasibility_r1/PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md)
- [audits/piano_hand_four_pose_static_feasibility_r1/00_extract.py](../../src/legacy/audits/piano_hand_four_pose_static_feasibility_r1/00_extract.py)
- [audits/piano_hand_four_pose_static_feasibility_r1/01_policy.py](../../src/legacy/audits/piano_hand_four_pose_static_feasibility_r1/01_policy.py)
- [audits/piano_hand_four_pose_static_feasibility_r1/02_solve.py](../../src/legacy/audits/piano_hand_four_pose_static_feasibility_r1/02_solve.py)
- [audits/piano_hand_four_pose_static_feasibility_r1/03_scene.py](../../src/legacy/audits/piano_hand_four_pose_static_feasibility_r1/03_scene.py)
- [audits/piano_hand_four_pose_static_feasibility_r1/04_render.py](../../src/legacy/audits/piano_hand_four_pose_static_feasibility_r1/04_render.py)
- [audits/piano_hand_four_pose_static_feasibility_r1/05_measure.py](../../src/legacy/audits/piano_hand_four_pose_static_feasibility_r1/05_measure.py)
- [audits/piano_hand_four_pose_static_feasibility_r1/06_finish.py](../../src/legacy/audits/piano_hand_four_pose_static_feasibility_r1/06_finish.py)
- [audits/piano_hand_four_pose_static_feasibility_r1/07_review.py](../../src/legacy/audits/piano_hand_four_pose_static_feasibility_r1/07_review.py)
- [audits/piano_hand_four_pose_static_feasibility_r1/09_verify.py](../../src/legacy/audits/piano_hand_four_pose_static_feasibility_r1/09_verify.py)

## 输入、输出与大型证据

该目录原始成员 51 项；拟公开身份记录 50 项。
- `audits/piano_hand_four_pose_static_feasibility_r1/STATIC_POSTURE_CANDIDATE_R1.blend` → `hands-research-r1-selected-006.zip` / `payload/audits/piano_hand_four_pose_static_feasibility_r1/STATIC_POSTURE_CANDIDATE_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
