# experiments/hands_blender_artist_pose_repair_poc_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 3. 静态门槛失败，按任务要求停止阶段2。自然嵌入原 C1 的能力本轮未验证，不能回答“已做到”。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_blender_artist_pose_repair_poc_r1/TECHNICAL_REPORT.md)

> 3. 静态门槛失败，按任务要求停止阶段2。自然嵌入原 C1 的能力本轮未验证，不能回答“已做到”。

出处：[TECHNICAL_REPORT_PRE_LABEL_QC.md](../research/experiments/hands_blender_artist_pose_repair_poc_r1/TECHNICAL_REPORT_PRE_LABEL_QC.md)

## 技术路线

> 使用已配置 Blender MCP 的 `execute_blender_code` 实际操作当前 Blender。先将原 C1 另存到本隔离目录，再直接给 `INDEX_MCP_R`、`INDEX_PIP_R`、`INDEX_DIP_R` 的 `rotation_quaternion` 赋值并在原时间 2.600000s（frame 157）插入静态姿态关键帧。MCP 的实际骨骼读数及真实 Blender 渲染确认操作落地。Python 仅用于把人工选定的关节姿态写入现有骨骼，并检查网格；没有运动求解器、随机/网格搜索或自动角度生成器。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_blender_artist_pose_repair_poc_r1/TECHNICAL_REPORT.md)

> 4. 相对原 C1，单时刻深度减少约 `89.83%`；相对上一轮固定策略在同一时刻的 `1.761794mm`，再减少约 `67.45%`。新增证据是观察驱动的合法展指与关节弧度编辑能够进一步减轻碰撞，并保持当前 G4 接触；这只是静态改善，仍不是成功清障。未载入或复用上轮候选姿态，也没有对上轮动画作优劣泛化结论。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_blender_artist_pose_repair_poc_r1/TECHNICAL_REPORT.md)

## 测试结论

> **PARTIAL — STOP — HUMAN REVIEW**。2026-10-15 22:46:09 +08:00。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_blender_artist_pose_repair_poc_r1/TECHNICAL_REPORT.md)

> 2.600000s 右手拇指 G4：真实 pad 保持面内、gap `0.437994014mm`、pad 位移 **0mm**，接触 PASS。当前其他活动音的真实接触也逐项记录在 `SAVED_REOPEN_STATIC_VALIDATION.json`（链接见原报告）。掌/root、腕及其他手指动画路径摘要保持，左手变形皮肤变化为 0。食指动作经冻结混合权重传到拇指 ROI 的最大皮肤位移 `0.717469mm`；这些变动面已参与检测，不能把“拇指骨没动”当作所有拇指皮肤绝对不变。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_blender_artist_pose_repair_poc_r1/TECHNICAL_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 工作循环是原俯视/侧视观察 → 一次直接摆姿 → 真正模型渲染 → mesh/BVH/三角面读数 → 下一轮观察修正。原场景侧斜视对食指内侧遮挡较多，另建固定辅助近侧视相机，原 C1 与候选采用相同位置/投影。正式 STAGE_C_OVERHEAD 和原侧斜视相机保持不变，所有对象可见性未改。保存后另用现有 Blender Python API 后台进程独立重新打开候选，验证不是只改变内存或绘制示意图。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_blender_artist_pose_repair_poc_r1/TECHNICAL_REPORT.md)

> 工作循环是原俯视/侧视观察 → 一次直接摆姿 → 真正模型渲染 → mesh/BVH/三角面读数 → 下一轮观察修正。原场景侧斜视对食指内侧遮挡较多，另建固定辅助近侧视相机，原 C1 与候选采用相同位置/投影。正式 STAGE_C_OVERHEAD 和原侧斜视相机保持不变，所有对象可见性未改。保存后另用现有 Blender Python API 后台进程独立重新打开候选，验证不是只改变内存或绘制示意图。

出处：[TECHNICAL_REPORT_PRE_LABEL_QC.md](../research/experiments/hands_blender_artist_pose_repair_poc_r1/TECHNICAL_REPORT_PRE_LABEL_QC.md)

## 原报告与关键代码

- [experiments/hands_blender_artist_pose_repair_poc_r1/TECHNICAL_REPORT.md](../research/experiments/hands_blender_artist_pose_repair_poc_r1/TECHNICAL_REPORT.md)
- [experiments/hands_blender_artist_pose_repair_poc_r1/TECHNICAL_REPORT_PRE_LABEL_QC.md](../research/experiments/hands_blender_artist_pose_repair_poc_r1/TECHNICAL_REPORT_PRE_LABEL_QC.md)
- [experiments/hands_blender_artist_pose_repair_poc_r1/HUMAN_REVIEW.md](../research/experiments/hands_blender_artist_pose_repair_poc_r1/HUMAN_REVIEW.md)
- [experiments/hands_blender_artist_pose_repair_poc_r1/artist_session.py](../../src/legacy/experiments/hands_blender_artist_pose_repair_poc_r1/artist_session.py)
- [experiments/hands_blender_artist_pose_repair_poc_r1/artist_tools.py](../../src/legacy/experiments/hands_blender_artist_pose_repair_poc_r1/artist_tools.py)
- [experiments/hands_blender_artist_pose_repair_poc_r1/aux_views.py](../../src/legacy/experiments/hands_blender_artist_pose_repair_poc_r1/aux_views.py)
- [experiments/hands_blender_artist_pose_repair_poc_r1/deliver_static.py](../../src/legacy/experiments/hands_blender_artist_pose_repair_poc_r1/deliver_static.py)
- [experiments/hands_blender_artist_pose_repair_poc_r1/reopen_static.py](../../src/legacy/experiments/hands_blender_artist_pose_repair_poc_r1/reopen_static.py)

## 输入、输出与大型证据

该目录原始成员 67 项；拟公开身份记录 57 项。
- `experiments/hands_blender_artist_pose_repair_poc_r1/C1_ARTIST_WORKING_COPY_NOT_APPROVED.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_blender_artist_pose_repair_poc_r1/C1_ARTIST_WORKING_COPY_NOT_APPROVED.blend`
- `experiments/hands_blender_artist_pose_repair_poc_r1/ROUND_1_APPLIED_STATIC_NOT_APPROVED.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_blender_artist_pose_repair_poc_r1/ROUND_1_APPLIED_STATIC_NOT_APPROVED.blend`
- `experiments/hands_blender_artist_pose_repair_poc_r1/ROUND_1_STATIC_NOT_APPROVED.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_blender_artist_pose_repair_poc_r1/ROUND_1_STATIC_NOT_APPROVED.blend`
- `experiments/hands_blender_artist_pose_repair_poc_r1/ROUND_2_STATIC_NOT_APPROVED.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_blender_artist_pose_repair_poc_r1/ROUND_2_STATIC_NOT_APPROVED.blend`
- `experiments/hands_blender_artist_pose_repair_poc_r1/ROUND_3_STATIC_NOT_APPROVED.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_blender_artist_pose_repair_poc_r1/ROUND_3_STATIC_NOT_APPROVED.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
