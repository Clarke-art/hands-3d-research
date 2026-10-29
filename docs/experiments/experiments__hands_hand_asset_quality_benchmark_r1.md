# experiments/hands_hand_asset_quality_benchmark_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 这是本次受限样本的视觉判断，尚未经 Human 认可；既不证明现有模型不可修复，也不证明其他外部资产没有优势。候选的指甲细节和更高三角形数量不计作两个目标病灶的修复证据。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_hand_asset_quality_benchmark_r1/TECHNICAL_REPORT.md)

> CC0 允许商业使用、修改和分发，未要求署名，也没有禁止将衍生 GLB 交付终端的条件；保留来源是本项目的溯源做法。`CC0 条文`（链接见原报告）不提供权利担保，也不授予作者背书、商标或第三方人格权。发布方专门对本派生手模作了 CC0 声明；上游资产许可与软件的 GPL/AGPL 许可分别记录，没有把软件许可误套到模型。归档 HTML 和上游许可文本位于 `sources/`。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_hand_asset_quality_benchmark_r1/TECHNICAL_REPORT.md)

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [acquire.py](../../src/legacy/experiments/hands_hand_asset_quality_benchmark_r1/acquire.py)
- [build_benchmark.py](../../src/legacy/experiments/hands_hand_asset_quality_benchmark_r1/build_benchmark.py)
- [compose_review.py](../../src/legacy/experiments/hands_hand_asset_quality_benchmark_r1/compose_review.py)
- [finalize.py](../../src/legacy/experiments/hands_hand_asset_quality_benchmark_r1/finalize.py)
- [inspect_models.py](../../src/legacy/experiments/hands_hand_asset_quality_benchmark_r1/inspect_models.py)

## 测试结论

> 基线对象为 `RIGHT_HAND_OFFICIAL_L1_PRODUCT_MESH.002`，骨架为 `RIGHT_HAND_PRODUCTION_RIG.002`。读取场景第 157 帧后，在内存副本解除骨架 Action 引用，将 pose basis 归零建立绑定中性状态；保留原有 rest data、蒙皮和 corrective driver。它**不是正式演奏 2.600 秒原姿态的截图**。随后只在内存里使用各自既有骨架摆两个最小静态姿态；不生成 Action，不迁移动作，不将外部模型绑定现有 Rig。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_hand_asset_quality_benchmark_r1/TECHNICAL_REPORT.md)

> | 状态 | 实际执行 | 可比性和限度 |

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_hand_asset_quality_benchmark_r1/TECHNICAL_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 本轮实测一个独立候选：Innerscene 发布、由 MakeHuman/MPFB 派生的 Posable anatomical right hand。中性俯视下，候选食指近节靠拇指侧的曲线较少出现基线那样的中段外鼓；但侧视、虎口反向观察及屈指后的结果没有共同建立明确的整体自然性优势。第一指蹼仍有可见折面。当前证据不足以用迁移成本换取这个候选，**不建议据此进入资产适配或替换**。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_hand_asset_quality_benchmark_r1/TECHNICAL_REPORT.md)

> 7. **足够建议下一轮适配吗？** 不足。当前不建议进入本候选的资产适配，更不能正式替换。请 Human 先看实际对照；保留本轮不优胜的结果，不因需要推进任务而推荐迁移。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_hand_asset_quality_benchmark_r1/TECHNICAL_REPORT.md)

## 原报告与关键代码

- [experiments/hands_hand_asset_quality_benchmark_r1/TECHNICAL_REPORT.md](../research/experiments/hands_hand_asset_quality_benchmark_r1/TECHNICAL_REPORT.md)
- [experiments/hands_hand_asset_quality_benchmark_r1/HUMAN_REVIEW.md](../research/experiments/hands_hand_asset_quality_benchmark_r1/HUMAN_REVIEW.md)
- [experiments/hands_hand_asset_quality_benchmark_r1/acquire.py](../../src/legacy/experiments/hands_hand_asset_quality_benchmark_r1/acquire.py)
- [experiments/hands_hand_asset_quality_benchmark_r1/build_benchmark.py](../../src/legacy/experiments/hands_hand_asset_quality_benchmark_r1/build_benchmark.py)
- [experiments/hands_hand_asset_quality_benchmark_r1/compose_review.py](../../src/legacy/experiments/hands_hand_asset_quality_benchmark_r1/compose_review.py)
- [experiments/hands_hand_asset_quality_benchmark_r1/finalize.py](../../src/legacy/experiments/hands_hand_asset_quality_benchmark_r1/finalize.py)
- [experiments/hands_hand_asset_quality_benchmark_r1/inspect_models.py](../../src/legacy/experiments/hands_hand_asset_quality_benchmark_r1/inspect_models.py)
- [experiments/hands_hand_asset_quality_benchmark_r1/prepare.py](../../src/legacy/experiments/hands_hand_asset_quality_benchmark_r1/prepare.py)
- [experiments/hands_hand_asset_quality_benchmark_r1/preview_reverse.py](../../src/legacy/experiments/hands_hand_asset_quality_benchmark_r1/preview_reverse.py)
- [experiments/hands_hand_asset_quality_benchmark_r1/render_comparisons.py](../../src/legacy/experiments/hands_hand_asset_quality_benchmark_r1/render_comparisons.py)
- [experiments/hands_hand_asset_quality_benchmark_r1/rig_receipt.py](../../src/legacy/experiments/hands_hand_asset_quality_benchmark_r1/rig_receipt.py)
- [experiments/hands_hand_asset_quality_benchmark_r1/verify_geometry.py](../../src/legacy/experiments/hands_hand_asset_quality_benchmark_r1/verify_geometry.py)

## 输入、输出与大型证据

该目录原始成员 98 项；拟公开身份记录 73 项。
- `experiments/hands_hand_asset_quality_benchmark_r1/CANDIDATE_IMPORTED_UNALTERED.blend` → `hands-research-r1-selected-012.zip` / `payload/experiments/hands_hand_asset_quality_benchmark_r1/CANDIDATE_IMPORTED_UNALTERED.blend`
- `experiments/hands_hand_asset_quality_benchmark_r1/HAND_ASSET_BENCHMARK_REVIEW.blend` → `hands-research-r1-selected-012.zip` / `payload/experiments/hands_hand_asset_quality_benchmark_r1/HAND_ASSET_BENCHMARK_REVIEW.blend`
- `experiments/hands_hand_asset_quality_benchmark_r1/HAND_ASSET_BENCHMARK_STATIC.blend` → `hands-research-r1-selected-012.zip` / `payload/experiments/hands_hand_asset_quality_benchmark_r1/HAND_ASSET_BENCHMARK_STATIC.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
