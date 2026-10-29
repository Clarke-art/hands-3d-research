# audits/left_hand_canonical_mirror_baseline_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 现有 Blender driver 的 expression 以后仍需转译成 Web morph 权重；本轮验证其镜像 parity，没有声称 driver 可直接随 glTF 工作，也没有进行 Web 导出或实现。

出处：[LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1_REPORT.md](../research/audits/left_hand_canonical_mirror_baseline_r1/LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1_REPORT.md)

## 技术路线

> 现有 Blender driver 的 expression 以后仍需转译成 Web morph 权重；本轮验证其镜像 parity，没有声称 driver 可直接随 glTF 工作，也没有进行 Web 导出或实现。

出处：[LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1_REPORT.md](../research/audits/left_hand_canonical_mirror_baseline_r1/LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1_REPORT.md)

## 测试结论

> | Q11 | 最终状态 | READY_FOR_HUMAN_REVIEW |

出处：[LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1_REPORT.md](../research/audits/left_hand_canonical_mirror_baseline_r1/LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1_REPORT.md)

> | ZERO | 0.000722190 | 0.000000000 | 0.000000000 | PASS |

出处：[LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1_REPORT.md](../research/audits/left_hand_canonical_mirror_baseline_r1/LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/left_hand_canonical_mirror_baseline_r1/LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1_REPORT.md](../research/audits/left_hand_canonical_mirror_baseline_r1/LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1_REPORT.md)
- [audits/left_hand_canonical_mirror_baseline_r1/build_verify.py](../../src/legacy/audits/left_hand_canonical_mirror_baseline_r1/build_verify.py)
- [audits/left_hand_canonical_mirror_baseline_r1/check_precision.py](../../src/legacy/audits/left_hand_canonical_mirror_baseline_r1/check_precision.py)
- [audits/left_hand_canonical_mirror_baseline_r1/compose_evidence.py](../../src/legacy/audits/left_hand_canonical_mirror_baseline_r1/compose_evidence.py)
- [audits/left_hand_canonical_mirror_baseline_r1/finalize_review.py](../../src/legacy/audits/left_hand_canonical_mirror_baseline_r1/finalize_review.py)
- [audits/left_hand_canonical_mirror_baseline_r1/inspect_r2.py](../../src/legacy/audits/left_hand_canonical_mirror_baseline_r1/inspect_r2.py)
- [audits/left_hand_canonical_mirror_baseline_r1/render_review.py](../../src/legacy/audits/left_hand_canonical_mirror_baseline_r1/render_review.py)

## 输入、输出与大型证据

该目录原始成员 71 项；拟公开身份记录 69 项。
- `audits/left_hand_canonical_mirror_baseline_r1/EVIDENCE_FIRST_WEB_MIRROR_R1.png` → `hands-research-r1-selected-001-r1a.zip` / `payload/audits/left_hand_canonical_mirror_baseline_r1/EVIDENCE_FIRST_WEB_MIRROR_R1.png`
- `audits/left_hand_canonical_mirror_baseline_r1/EVIDENCE_MIRROR_POSE_REGRESSION_R1.png` → `hands-research-r1-selected-001-r1a.zip` / `payload/audits/left_hand_canonical_mirror_baseline_r1/EVIDENCE_MIRROR_POSE_REGRESSION_R1.png`
- `audits/left_hand_canonical_mirror_baseline_r1/EVIDENCE_ZERO_RIGHT_VS_LEFT_R1.png` → `hands-research-r1-selected-001-r1a.zip` / `payload/audits/left_hand_canonical_mirror_baseline_r1/EVIDENCE_ZERO_RIGHT_VS_LEFT_R1.png`
- `audits/left_hand_canonical_mirror_baseline_r1/LEFT_HAND_OFFICIAL_L1_MIRROR_CANDIDATE_R1.blend` → `hands-research-r1-selected-001-r1a.zip` / `payload/audits/left_hand_canonical_mirror_baseline_r1/LEFT_HAND_OFFICIAL_L1_MIRROR_CANDIDATE_R1.blend`
- `audits/left_hand_canonical_mirror_baseline_r1/_render_tiles/CMC_OPP_30__DORSAL__L.png` → `hands-research-r1-selected-001-r1a.zip` / `payload/audits/left_hand_canonical_mirror_baseline_r1/_render_tiles/CMC_OPP_30__DORSAL__L.png`
- `audits/left_hand_canonical_mirror_baseline_r1/_render_tiles/CMC_OPP_30__DORSAL__R.png` → `hands-research-r1-selected-001-r1a.zip` / `payload/audits/left_hand_canonical_mirror_baseline_r1/_render_tiles/CMC_OPP_30__DORSAL__R.png`
- `audits/left_hand_canonical_mirror_baseline_r1/_render_tiles/CMC_OPP_30__FIRST_WEB__L.png` → `hands-research-r1-selected-001-r1a.zip` / `payload/audits/left_hand_canonical_mirror_baseline_r1/_render_tiles/CMC_OPP_30__FIRST_WEB__L.png`
- `audits/left_hand_canonical_mirror_baseline_r1/_render_tiles/CMC_OPP_30__FIRST_WEB__R.png` → `hands-research-r1-selected-001-r1a.zip` / `payload/audits/left_hand_canonical_mirror_baseline_r1/_render_tiles/CMC_OPP_30__FIRST_WEB__R.png`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
