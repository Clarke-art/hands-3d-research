# audits/pianovam_first_web_joint_contribution_isolation_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 只在未保存的 Blender 运行时 pose 上测试。前序 mapping_core.py 原样只读导入，iteration=2。A/B 从 Solver.raw 内部已有 source flexion/abduction 读值，重建相同 `frame(direction, palm radial)`，通过原 anatomical rest frame / roll calibration 映射；仅目标 flexion 或 abduction 恢复 0。冻结 RSSF rest 的内建弯曲、张开与 roll 仍保留。没有 Euler X/Z 清零。

出处：[PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1_REPORT.md](../research/audits/pianovam_first_web_joint_contribution_isolation_r1/PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1_REPORT.md)

> 每个 OFF 均在原来的 i−1/i/i+1 source observations 上处理目标分量，再使用原 quaternion sign alignment、[.25,.5,.25] 和 normalization。其余骨骼 local quaternion、location、scale、rotation mode 完全复制 saved corrected Action 的实际值。Quaternion 平滑非线性，目标骨的四个 quaternion 系数可同时改变；这不表示额外修改另一解剖分量，也不新增平滑。每帧 saved Action 与原 Solver.smoothed 的 quaternion 数值在 1e−6 内一致。

出处：[PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1_REPORT.md](../research/audits/pianovam_first_web_joint_contribution_isolation_r1/PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1_REPORT.md)

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [finalize.py](../../src/legacy/audits/pianovam_first_web_joint_contribution_isolation_r1/finalize.py)
- [inspection_previews.py](../../src/legacy/audits/pianovam_first_web_joint_contribution_isolation_r1/inspection_previews.py)
- [isolate.py](../../src/legacy/audits/pianovam_first_web_joint_contribution_isolation_r1/isolate.py)
- [verify_protection.py](../../src/legacy/audits/pianovam_first_web_joint_contribution_isolation_r1/verify_protection.py)

## 测试结论

> 上一阶段 Human Q1=NO、Q2=YES、Q3=REJECT，`RETARGET_AXIS_MAPPING_PARTIAL_CAUSE=HUMAN_CONFIRMED` 已单独绑定，未改写历史审核记录。冻结右手保持 `HUMAN_APPROVED_FROZEN`。

出处：[PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1_REPORT.md](../research/audits/pianovam_first_web_joint_contribution_isolation_r1/PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1_REPORT.md)

>   "MACHINE_CHECK": "PASS",

出处：[PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1_REPORT.md](../research/audits/pianovam_first_web_joint_contribution_isolation_r1/PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 本轮没有进行 weights/mesh/Basis/rig/mapping/source/Action/corrective/driver 修复，没有换 sample、左手或 Web export。停在本轮 Human 审核；下一阶段也未自动启动。

出处：[PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1_REPORT.md](../research/audits/pianovam_first_web_joint_contribution_isolation_r1/PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1_REPORT.md)

## 原报告与关键代码

- [audits/pianovam_first_web_joint_contribution_isolation_r1/PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1_REPORT.md](../research/audits/pianovam_first_web_joint_contribution_isolation_r1/PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1_REPORT.md)
- [audits/pianovam_first_web_joint_contribution_isolation_r1/finalize.py](../../src/legacy/audits/pianovam_first_web_joint_contribution_isolation_r1/finalize.py)
- [audits/pianovam_first_web_joint_contribution_isolation_r1/inspection_previews.py](../../src/legacy/audits/pianovam_first_web_joint_contribution_isolation_r1/inspection_previews.py)
- [audits/pianovam_first_web_joint_contribution_isolation_r1/isolate.py](../../src/legacy/audits/pianovam_first_web_joint_contribution_isolation_r1/isolate.py)
- [audits/pianovam_first_web_joint_contribution_isolation_r1/verify_protection.py](../../src/legacy/audits/pianovam_first_web_joint_contribution_isolation_r1/verify_protection.py)

## 输入、输出与大型证据

该目录原始成员 74 项；拟公开身份记录 5 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
