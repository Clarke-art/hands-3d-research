# audits/right_hand_lbs_vs_dqs_real_motion_ab_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> A_LBS / B_DQS 的对象变换完全一致，mesh / UV / 顶点索引 / weights / materials / Key datablock / approved driver 均共享或逐项一致。Rest armature datablock 共享，两份 pose rig 使用同一个 Action。B 的 Armature target 绑定到其等价 rig；归一化 target 身份后，全部 modifier RNA 设置和顺序只差 Preserve Volume。驱动目标保留原 A rig，未改 driver：所有 421 个观察点和六个姿态均逐骨确认 A/B pose matrices 完全一致，因此共享 corrective 的自然求值对 A/B 相同。测试中不应独立改变其中一份 pose rig。Blender 中两份测试对象位于同一位置，单独查看时可用 Outliner 隐藏另一份 mesh；审核渲染从各自 evaluated mesh 生成。

出处：[RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md](../research/audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md)

> 按照请求在此停止。不推广、修改正式基线或尝试 hybrid。若 Human 确认此路线无价值，后续 architecture rebuild assessment 需要新的独立任务；本轮不执行。

出处：[RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md](../research/audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md)

## 技术路线

> 按照请求在此停止。不推广、修改正式基线或尝试 hybrid。若 Human 确认此路线无价值，后续 architecture rebuild assessment 需要新的独立任务；本轮不执行。

出处：[RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md](../research/audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md)

## 测试结论

> 预分类：**DQS_WORSE**。当前步骤结束于 **STOP — HUMAN REVIEW**。此结论为代理的普通实体视图判断，四项 Human 答案未填写，PRODUCTION_PROMOTION = NO。

出处：[RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md](../research/audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md)

> 最低机器安全：两组 421 个观测点 + 六姿态 NaN/Inf = 0、collapsed face = 0、degenerate edge = 0、ZERO restore = PASS。普通实体视图 gross visible tearing = 0（代理检查，非 hidden forensic 证明）。未执行 volume integral、strain/crossing/normal-dot census、R3、true-cap、2127 edges 或 Stage6 重验。DQS_NEW_VISIBLE_DEFECT_COUNT = 1 表示一个问题类型：更加突出的片状虎口折边，不表示异常帧计数。指尖问题仍 DEFERRED。

出处：[RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md](../research/audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md)

## 失败原因与证据边界

> DQS 在部分动作帧明显减轻 LBS 的小阶梯凹折，但 F130 仍有大的角状折口，虎口桥面更鼓起，形成更宽且突出的片状折边。按本轮“明显 first-web distortion / 更差”的分类规则，优先归 DQS_WORSE。局部变平的收益已保留在下面的逐帧说明中；不能据此认定 DQS 完全无效，也不能认定 LBS 体积损失是唯一或主要根因。纯 Preserve Volume 开关没有使这段动作达到自然可接受程度。

出处：[RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md](../research/audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md)

## 后续建议

> 按照请求在此停止。不推广、修改正式基线或尝试 hybrid。若 Human 确认此路线无价值，后续 architecture rebuild assessment 需要新的独立任务；本轮不执行。

出处：[RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md](../research/audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md)

## 原报告与关键代码

- [audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md](../research/audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md)
- [audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/build_ab.py](../../src/legacy/audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/build_ab.py)
- [audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/common.py](../../src/legacy/audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/common.py)
- [audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/deliver.py](../../src/legacy/audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/deliver.py)
- [audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/evaluate_ab.py](../../src/legacy/audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/evaluate_ab.py)
- [audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/finalize.py](../../src/legacy/audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/finalize.py)
- [audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/make_media.py](../../src/legacy/audits/right_hand_lbs_vs_dqs_real_motion_ab_r1/make_media.py)

## 输入、输出与大型证据

该目录原始成员 979 项；拟公开身份记录 8 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
