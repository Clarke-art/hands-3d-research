# experiments/hands_anatomical_whole_hand_pose_repair_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 本轮从原 C1 独立副本出发，经 **2 轮** Blender MCP 直接摆姿，得到仅针对 **2.600000s** 的静态候选。独立重新打开后，右手对全部非目标琴键未检出非法相交，原关节域及当前两手活动接触保持；Codex 初步认为轮廓较前轮被否决候选合理，可以交 Human 判断。**没有 Human 自然性批准，没有正式教学动画批准，没有连续动画。** 未使用剩余轮次继续刷指标。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_anatomical_whole_hand_pose_repair_r1/TECHNICAL_REPORT.md)

> 补读 `Practising the Piano 教学公开页`（链接见原报告） 的关节支撑与腕部活动说明，仅采用定性观察原则，未把八度练习转成当前任务的角度处方。Hoffman 页面本轮未能取到正文，不作新增证据。来源、当地文件和限制详见 `REFERENCE_BASIS.md`（链接见原报告）。PianoVAM 为 Kim et al., ISMIR 2025，CC BY-NC-SA 4.0，仅内部非商业定性验证，没有复制数据集动作或晋升产品资产。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_anatomical_whole_hand_pose_repair_r1/TECHNICAL_REPORT.md)

## 技术路线

> 第2轮保持**同样的食指局部姿态**，基于共有掌位与黑键前沿的关系，直接将整手后收4mm，并绕拇指附近作世界 X +1°、Y −4° 的小幅联合旋转。它是人工选择的单次刚体摆放操作，不是保持接触的迭代求解器。活动 pad 允许在原合法 G4 键面内移动，随后实测验收，没有改 marker、键面或接触容差。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_anatomical_whole_hand_pose_repair_r1/TECHNICAL_REPORT.md)

> 所有新增内容仅写本隔离目录。独立 piano 目录没有访问、扫描、读取、运行或间接跟随。原 C1、正式 MIDI、23音时钟/冻结指法、历史候选与全部保护输入不改。当前两轮姿态都从原C1直接编辑；前轮第三候选仅后置读取作自然性对照，没有作为起点。未开发求解器或自动纠错Agent。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_anatomical_whole_hand_pose_repair_r1/TECHNICAL_REPORT.md)

## 测试结论

> **STATIC_PASS_PENDING_HUMAN — STOP — HUMAN REVIEW**。2026-10-15 23:43:07 +08:00。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_anatomical_whole_hand_pose_repair_r1/TECHNICAL_REPORT.md)

> 原食指局部增量 MCP/PIP/DIP/展指约 16.865/17.383/9.053/−13.787°。沿用冻结 Rig 定义的现有屈伸与展指轴；完整局部轴、原掌腕矩阵、各 MCP 点及真实变形数据保留在 `BASELINE_FACTS.json`（链接见原报告）。原共享掌位下，活动拇指 G4、食指 IDLE 的状态已核对；左手此刻中指 B3 ACTIVE。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_anatomical_whole_hand_pose_repair_r1/TECHNICAL_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 5. **能否进入下一轮动画？** 当前证据足够交Human进行静态自然性审核，**不足以直接开做动画**。必须先取得Human对这组实际俯视/侧视图片的明确认可，再另行授权进入/保持/退出关键帧任务；静态无碰撞不推出动态安全。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_anatomical_whole_hand_pose_repair_r1/TECHNICAL_REPORT.md)

## 原报告与关键代码

- [experiments/hands_anatomical_whole_hand_pose_repair_r1/TECHNICAL_REPORT.md](../research/experiments/hands_anatomical_whole_hand_pose_repair_r1/TECHNICAL_REPORT.md)
- [experiments/hands_anatomical_whole_hand_pose_repair_r1/HUMAN_REVIEW.md](../research/experiments/hands_anatomical_whole_hand_pose_repair_r1/HUMAN_REVIEW.md)
- [experiments/hands_anatomical_whole_hand_pose_repair_r1/REFERENCE_BASIS.md](../research/experiments/hands_anatomical_whole_hand_pose_repair_r1/REFERENCE_BASIS.md)
- [experiments/hands_anatomical_whole_hand_pose_repair_r1/common.py](../../src/legacy/experiments/hands_anatomical_whole_hand_pose_repair_r1/common.py)
- [experiments/hands_anatomical_whole_hand_pose_repair_r1/editing.py](../../src/legacy/experiments/hands_anatomical_whole_hand_pose_repair_r1/editing.py)
- [experiments/hands_anatomical_whole_hand_pose_repair_r1/finalize.py](../../src/legacy/experiments/hands_anatomical_whole_hand_pose_repair_r1/finalize.py)
- [experiments/hands_anatomical_whole_hand_pose_repair_r1/geometry.py](../../src/legacy/experiments/hands_anatomical_whole_hand_pose_repair_r1/geometry.py)
- [experiments/hands_anatomical_whole_hand_pose_repair_r1/make_review_images.py](../../src/legacy/experiments/hands_anatomical_whole_hand_pose_repair_r1/make_review_images.py)
- [experiments/hands_anatomical_whole_hand_pose_repair_r1/run_stage.py](../../src/legacy/experiments/hands_anatomical_whole_hand_pose_repair_r1/run_stage.py)
- [experiments/hands_anatomical_whole_hand_pose_repair_r1/session.py](../../src/legacy/experiments/hands_anatomical_whole_hand_pose_repair_r1/session.py)
- [experiments/hands_anatomical_whole_hand_pose_repair_r1/support.py](../../src/legacy/experiments/hands_anatomical_whole_hand_pose_repair_r1/support.py)
- [experiments/hands_anatomical_whole_hand_pose_repair_r1/verify_and_compare.py](../../src/legacy/experiments/hands_anatomical_whole_hand_pose_repair_r1/verify_and_compare.py)

## 输入、输出与大型证据

该目录原始成员 73 项；拟公开身份记录 68 项。
- `experiments/hands_anatomical_whole_hand_pose_repair_r1/ORIGINAL_C1_ISOLATED_NOT_APPROVED.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_anatomical_whole_hand_pose_repair_r1/ORIGINAL_C1_ISOLATED_NOT_APPROVED.blend`
- `experiments/hands_anatomical_whole_hand_pose_repair_r1/ROUND_1_STATIC_NOT_APPROVED.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_anatomical_whole_hand_pose_repair_r1/ROUND_1_STATIC_NOT_APPROVED.blend`
- `experiments/hands_anatomical_whole_hand_pose_repair_r1/ROUND_2_STATIC_NOT_APPROVED.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_anatomical_whole_hand_pose_repair_r1/ROUND_2_STATIC_NOT_APPROVED.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
