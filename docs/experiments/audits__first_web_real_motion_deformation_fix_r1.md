# audits/first_web_real_motion_deformation_fix_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 目标为多个真实 motion 姿态的局部 deformation displacement 连续性：相对原 wrist rigid transform 保留 rest curvature，用受约束多姿态拟合，并用五个已批准非 ZERO 姿态的实际变形顶点作软约束。训练包含五个固定 frame 和相同 7 秒 Action 的均匀取样，不做 severity census。每轮都直接渲染五个 frame、完整 210 帧两视角 motion，以及六个 regression poses。

出处：[FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1_REPORT.md](../research/audits/first_web_real_motion_deformation_fix_r1/FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1_REPORT.md)

> `FIRST_WEB_REAL_MOTION_CORRECTIVE_R1` 只写一个新 key 的 99 个局部顶点，全部在同一 149 顶点支持区内；Basis 写入数=0。用 F130/F76/F205/F31 的局部 posed surface rounding 位移，通过未改变的 LBS skin 逆映射并平均为一个共享 delta。目标位移限制 2.8 mm，边界淡出；没有 per-frame keys、shape library、lattice、大块 thenar 体积补偿或 topology 改写。

出处：[FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1_REPORT.md](../research/audits/first_web_real_motion_deformation_fix_r1/FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1_REPORT.md)

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [add_real_motion_corrective.py](../../src/legacy/audits/first_web_real_motion_deformation_fix_r1/add_real_motion_corrective.py)
- [common.py](../../src/legacy/audits/first_web_real_motion_deformation_fix_r1/common.py)
- [deliver.py](../../src/legacy/audits/first_web_real_motion_deformation_fix_r1/deliver.py)
- [encode_videos.py](../../src/legacy/audits/first_web_real_motion_deformation_fix_r1/encode_videos.py)
- [evaluate_candidate.py](../../src/legacy/audits/first_web_real_motion_deformation_fix_r1/evaluate_candidate.py)

## 测试结论

> Weight1 的真实缺口仍在，同时 INDEX_MCP_45/FULL_OPP_L3 有新尖折回退，已拒收。Weight2 加强旧姿态约束，六个状态在普通实体初判中恢复可接受，但 F130/F76 等真实 motion 硬折仍然存在。于是按照用户条件使用一个 corrective；没有第三次权重调整。

出处：[FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1_REPORT.md](../research/audits/first_web_real_motion_deformation_fix_r1/FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1_REPORT.md)

> | F130 | FAIL：明显阶梯状深折仍在，upper-web 薄片状亮边更突出 |

出处：[FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1_REPORT.md](../research/audits/first_web_real_motion_deformation_fix_r1/FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1_REPORT.md)

## 失败原因与证据边界

> 实际区别依据：F130/F205/F31 key=1；F76≈0.548；F61 low-defect key=0。前序已知 low-defect F181 仅作辅助 driver 检查，key≈0.234，说明相关性有重叠，不是完美 defect classifier，也不是根因确认。六个已批准 regression poses 的新 key 均=0；旧 key/driver 完全不变。驱动接线验证时发现初始 gate 会激活 FULL_OPP_L1，在首个候选保存前加了同一 INDEX anatomical articulation 的 neutral exclusion；未改 shape delta、未创建第二个 corrective。

出处：[FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1_REPORT.md](../research/audits/first_web_real_motion_deformation_fix_r1/FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1_REPORT.md)

## 后续建议

> Q4. 右手 deformation 是否可以结束，进入后续真实 motion / 左手阶段？ YES / NO

出处：[FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1_REPORT.md](../research/audits/first_web_real_motion_deformation_fix_r1/FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1_REPORT.md)

> 本轮修复上限已达到，不再做 weight iteration、corrective R2、更多 shape keys、mapping/指尖修复、左手或 Web export。下一步仅可在新的明确任务中重新评估 source mesh / rig deformation architecture 是否值得继续；本轮没有开始该评估。**STOP — HUMAN REVIEW。**

出处：[FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1_REPORT.md](../research/audits/first_web_real_motion_deformation_fix_r1/FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1_REPORT.md)

## 原报告与关键代码

- [audits/first_web_real_motion_deformation_fix_r1/FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1_REPORT.md](../research/audits/first_web_real_motion_deformation_fix_r1/FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1_REPORT.md)
- [audits/first_web_real_motion_deformation_fix_r1/add_real_motion_corrective.py](../../src/legacy/audits/first_web_real_motion_deformation_fix_r1/add_real_motion_corrective.py)
- [audits/first_web_real_motion_deformation_fix_r1/common.py](../../src/legacy/audits/first_web_real_motion_deformation_fix_r1/common.py)
- [audits/first_web_real_motion_deformation_fix_r1/deliver.py](../../src/legacy/audits/first_web_real_motion_deformation_fix_r1/deliver.py)
- [audits/first_web_real_motion_deformation_fix_r1/encode_videos.py](../../src/legacy/audits/first_web_real_motion_deformation_fix_r1/encode_videos.py)
- [audits/first_web_real_motion_deformation_fix_r1/evaluate_candidate.py](../../src/legacy/audits/first_web_real_motion_deformation_fix_r1/evaluate_candidate.py)
- [audits/first_web_real_motion_deformation_fix_r1/inspect_region.py](../../src/legacy/audits/first_web_real_motion_deformation_fix_r1/inspect_region.py)
- [audits/first_web_real_motion_deformation_fix_r1/make_previews.py](../../src/legacy/audits/first_web_real_motion_deformation_fix_r1/make_previews.py)
- [audits/first_web_real_motion_deformation_fix_r1/show_weight_support.py](../../src/legacy/audits/first_web_real_motion_deformation_fix_r1/show_weight_support.py)
- [audits/first_web_real_motion_deformation_fix_r1/verify_final.py](../../src/legacy/audits/first_web_real_motion_deformation_fix_r1/verify_final.py)
- [audits/first_web_real_motion_deformation_fix_r1/weight_iteration.py](../../src/legacy/audits/first_web_real_motion_deformation_fix_r1/weight_iteration.py)

## 输入、输出与大型证据

该目录原始成员 1069 项；拟公开身份记录 12 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
