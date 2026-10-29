# experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 约11个直接指定的协调姿态，在起音/交接及3.60、3.67、3.708333、3.74、3.80、3.84、3.88、3.94秒设置Pose关键帧；精确Pose和曲线范围保留于两个 EDIT_LEDGER.json。关节角由人工指定，活动指目标点由一次实测指腹到声明可奏区域的刚性掌位平移直接放置，无迭代求解、IK、随机/网格搜索或大型运动规划器。实际动画为四元数/位置三次Bezier，内部控制柄平坦，直接求值后再验真实网格；不是静态回调或换帧假动画。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/TECHNICAL_REPORT.md)

## 技术路线

> 约11个直接指定的协调姿态，在起音/交接及3.60、3.67、3.708333、3.74、3.80、3.84、3.88、3.94秒设置Pose关键帧；精确Pose和曲线范围保留于两个 EDIT_LEDGER.json。关节角由人工指定，活动指目标点由一次实测指腹到声明可奏区域的刚性掌位平移直接放置，无迭代求解、IK、随机/网格搜索或大型运动规划器。实际动画为四元数/位置三次Bezier，内部控制柄平坦，直接求值后再验真实网格；不是静态回调或换帧假动画。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/TECHNICAL_REPORT.md)

> R2 2.45–2.92s另以225个原时刻复核：候选1/2最大网格差0.000611277/0.000634657mm，无名指早段关键帧控制柄payload也有变化。8个外部查询时刻的标量FCurve求值误差读数0，但不足以替代全网格和控制柄完全一致要求；严格一致检查FAIL，不能宣称此前成果在候选内部完全保持。输入R2文件本身SHA256未变。此微小非零差异及0.042mm边界泄漏均作为实现/重存保护失败保留，没有以容差改判PASS。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/TECHNICAL_REPORT.md)

## 测试结论

> |右手规定触点PASS /48|48|48|48|

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/TECHNICAL_REPORT.md)

> 精确交接候选1邻键相交0，但仍有57对两指相交；候选2交接有D5约0.367370mm、F5约0.868085mm的非法侵入及155对相交。整窗两者仍有黑键加深，不能把候选1交接单帧邻键0作为全程PASS。两候选末端3.991811833s均仍有D5约2.368mm侵入。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/TECHNICAL_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/TECHNICAL_REPORT.md](../research/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/TECHNICAL_REPORT.md)
- [experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/HUMAN_REVIEW.md](../research/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/HUMAN_REVIEW.md)
- [experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/artist_animation.py](../../src/legacy/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/artist_animation.py)
- [experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/dynamic_session.py](../../src/legacy/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/dynamic_session.py)
- [experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/final_audits.py](../../src/legacy/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/final_audits.py)
- [experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/make_delivery.py](../../src/legacy/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/make_delivery.py)
- [experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/start_mcp.py](../../src/legacy/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/start_mcp.py)
- [experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/validate_animation.py](../../src/legacy/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/validate_animation.py)

## 输入、输出与大型证据

该目录原始成员 51 项；拟公开身份记录 42 项。
- `experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/BASELINE_CONTEXT_ACTUAL.npz` → `hands-research-r1-selected-011.zip` / `payload/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/BASELINE_CONTEXT_ACTUAL.npz`
- `experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/BASELINE_CONTEXT_GEOMETRY.json` → `hands-research-r1-selected-011.zip` / `payload/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/BASELINE_CONTEXT_GEOMETRY.json`
- `experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/CANDIDATE_1_ACTUAL.npz` → `hands-research-r1-selected-011.zip` / `payload/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/CANDIDATE_1_ACTUAL.npz`
- `experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/CANDIDATE_1_NOT_APPROVED.blend` → `hands-research-r1-selected-011.zip` / `payload/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/CANDIDATE_1_NOT_APPROVED.blend`
- `experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/CANDIDATE_2_ACTUAL.npz` → `hands-research-r1-selected-011.zip` / `payload/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/CANDIDATE_2_ACTUAL.npz`
- `experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/CANDIDATE_2_NOT_APPROVED.blend` → `hands-research-r1-selected-011.zip` / `payload/experiments/hands_c1_r10_r11_dynamic_handoff_poc_r5/CANDIDATE_2_NOT_APPROVED.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
