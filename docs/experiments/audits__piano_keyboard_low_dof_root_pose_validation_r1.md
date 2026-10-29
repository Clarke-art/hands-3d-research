# audits/piano_keyboard_low_dof_root_pose_validation_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 技术路线

> |Q1 上一轮 fixed-orientation model 保持 REJECTED？|YES；仅重放原缓存作对照，没有重新求解。|

出处：[PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_R1_REPORT.md](../research/audits/piano_keyboard_low_dof_root_pose_validation_r1/PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_R1_REPORT.md)

> |Q2 MODEL A = XYZ + YAW 是否执行？|YES；完整 421 observations，全局单次求解。|

出处：[PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_R1_REPORT.md](../research/audits/piano_keyboard_low_dof_root_pose_validation_r1/PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_R1_REPORT.md)

## 测试结论

> 本状态针对本轮 MODEL A 候选安装：手掌放置和整体自然度未过关，不能用“只是预测指法不准”放行。它不证明所有合法 root orientation 都失败；源数据、指法和拟合误差的因果占比仍未隔离。

出处：[PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_R1_REPORT.md](../research/audits/piano_keyboard_low_dof_root_pose_validation_r1/PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_R1_REPORT.md)

> MODEL A 不通过；MODEL B 未达到合法启动条件，未执行。没有 MODEL C、第二轮参数 sweep 或 finger correction。不能把 `SOURCE_2_5D_OR_CONTACT_PRECISION_LIMIT` 的名称当作因果结论：它只是“粗略覆盖可行、严格接触不可行”的待解释残差。当前也不满足 C 类“root 本身已经合理”的前提，因此不以 EVIDENCE_LIMITED 状态暗示安装已成功。B 类在本报告中的结论边界是当前候选仍然阻塞；**未证实失败主要来自源/指法，也未证明排除了它们**。

出处：[PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_R1_REPORT.md](../research/audits/piano_keyboard_low_dof_root_pose_validation_r1/PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/piano_keyboard_low_dof_root_pose_validation_r1/PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_R1_REPORT.md](../research/audits/piano_keyboard_low_dof_root_pose_validation_r1/PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_R1_REPORT.md)
- [audits/piano_keyboard_low_dof_root_pose_validation_r1/01_inherit_and_probe.py](../../src/legacy/audits/piano_keyboard_low_dof_root_pose_validation_r1/01_inherit_and_probe.py)
- [audits/piano_keyboard_low_dof_root_pose_validation_r1/02_lock_policy.py](../../src/legacy/audits/piano_keyboard_low_dof_root_pose_validation_r1/02_lock_policy.py)
- [audits/piano_keyboard_low_dof_root_pose_validation_r1/03_solve.py](../../src/legacy/audits/piano_keyboard_low_dof_root_pose_validation_r1/03_solve.py)
- [audits/piano_keyboard_low_dof_root_pose_validation_r1/04_evaluate.py](../../src/legacy/audits/piano_keyboard_low_dof_root_pose_validation_r1/04_evaluate.py)
- [audits/piano_keyboard_low_dof_root_pose_validation_r1/05_candidate.py](../../src/legacy/audits/piano_keyboard_low_dof_root_pose_validation_r1/05_candidate.py)
- [audits/piano_keyboard_low_dof_root_pose_validation_r1/06_render.py](../../src/legacy/audits/piano_keyboard_low_dof_root_pose_validation_r1/06_render.py)
- [audits/piano_keyboard_low_dof_root_pose_validation_r1/07_media.py](../../src/legacy/audits/piano_keyboard_low_dof_root_pose_validation_r1/07_media.py)
- [audits/piano_keyboard_low_dof_root_pose_validation_r1/08_finalize.py](../../src/legacy/audits/piano_keyboard_low_dof_root_pose_validation_r1/08_finalize.py)
- [audits/piano_keyboard_low_dof_root_pose_validation_r1/common.py](../../src/legacy/audits/piano_keyboard_low_dof_root_pose_validation_r1/common.py)

## 输入、输出与大型证据

该目录原始成员 67 项；拟公开身份记录 56 项。
- `audits/piano_keyboard_low_dof_root_pose_validation_r1/KEY_CLUSTER_PLACEMENT_METRIC_R1.json` → `hands-research-r1-selected-006.zip` / `payload/audits/piano_keyboard_low_dof_root_pose_validation_r1/KEY_CLUSTER_PLACEMENT_METRIC_R1.json`
- `audits/piano_keyboard_low_dof_root_pose_validation_r1/model_a_evaluations.npz` → `hands-research-r1-selected-006.zip` / `payload/audits/piano_keyboard_low_dof_root_pose_validation_r1/model_a_evaluations.npz`
- `audits/piano_keyboard_low_dof_root_pose_validation_r1/MODEL_A_KEY_CLUSTER_PLACEMENT_METRIC_R1.json` → `hands-research-r1-selected-006.zip` / `payload/audits/piano_keyboard_low_dof_root_pose_validation_r1/MODEL_A_KEY_CLUSTER_PLACEMENT_METRIC_R1.json`
- `audits/piano_keyboard_low_dof_root_pose_validation_r1/PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_CANDIDATE_R1.blend` → `hands-research-r1-selected-006.zip` / `payload/audits/piano_keyboard_low_dof_root_pose_validation_r1/PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_CANDIDATE_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
