# audits/palmar_thenar_source_shape_restoration_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> Official Hand - Realistic 的 actual stored Multires L1 本轮只读求值，原生坐标与 faces 和既有已验证 snapshot 精确一致。采用已验证、与 Stage2 等价的 official L1；不替换整手、不转入 source topology。

出处：[PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_REPORT.md](../research/audits/palmar_thenar_source_shape_restoration_r1/PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_REPORT.md)

> | FULL_OPP_L2 | NEW_VISIBLE_PROBLEM | 增加的静态体积在虎口基底形成更突出的硬折角 / 压挤凹槽，position-only 尚未达到自然形变目标。 |

出处：[PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_REPORT.md](../research/audits/palmar_thenar_source_shape_restoration_r1/PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_REPORT.md)

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [common.py](../../src/legacy/audits/palmar_thenar_source_shape_restoration_r1/common.py)
- [deliver.py](../../src/legacy/audits/palmar_thenar_source_shape_restoration_r1/deliver.py)
- [make_inspection_sheets.py](../../src/legacy/audits/palmar_thenar_source_shape_restoration_r1/make_inspection_sheets.py)
- [prepare_and_preview.py](../../src/legacy/audits/palmar_thenar_source_shape_restoration_r1/prepare_and_preview.py)
- [save_and_smoke.py](../../src/legacy/audits/palmar_thenar_source_shape_restoration_r1/save_and_smoke.py)

## 测试结论

> ZERO 的虎口下方斜面、大鱼际上缘和拇指根掌侧连接更饱满，保持原 first-web 开口和 crease。L1 的静态改善仍可见。L2/L3 在同一冻结权重下，虎口 floor 出现更突出的硬折角 / 局部压挤凹槽。因此本轮**不判 READY_FOR_HUMAN_APPROVAL，也不判 Stage6B final PASS**。最低 catastrophic 机器门通过不代表局部形变产品外观通过。

出处：[PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_REPORT.md](../research/audits/palmar_thenar_source_shape_restoration_r1/PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_REPORT.md)

> `ZERO_SHAPE_PASS = YES` 是 Codex 初步静态判断，最终 Human 尚未批准。`OPPOSITION_VOLUME_PRESERVATION_FAIL = YES` 指 L2/L3 的局部上缘 / floor 压挤外观；下部 thenar mass 仍在，不等于全块大鱼际消失，也未证明权重是唯一根因。

出处：[PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_REPORT.md](../research/audits/palmar_thenar_source_shape_restoration_r1/PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_REPORT.md)

## 失败原因与证据边界

> `ZERO_SHAPE_PASS = YES` 是 Codex 初步静态判断，最终 Human 尚未批准。`OPPOSITION_VOLUME_PRESERVATION_FAIL = YES` 指 L2/L3 的局部上缘 / floor 压挤外观；下部 thenar mass 仍在，不等于全块大鱼际消失，也未证明权重是唯一根因。

出处：[PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_REPORT.md](../research/audits/palmar_thenar_source_shape_restoration_r1/PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_REPORT.md)

> 这是一种由 source 轮廓和体积引导、适配 RSSF 的产品恢复，不是逐毫米复制原始中性 donor。没有进行 anatomy、根因、CMC-axis、retopo 或 topology-correspondence 研究。

出处：[PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_REPORT.md](../research/audits/palmar_thenar_source_shape_restoration_r1/PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_REPORT.md)

## 后续建议

> 共三版内存静态预览。前两版在虎口基底引入硬折面，未保存成 blend，未进入 opposition smoke。第三版通过 donor profile field 插值、轴向保留与 distal transition 解决静态新折面，选为唯一正式 design candidate。Candidate blend 只保存一次，且在 ZERO；后续 pose 全部在内存，最后 RESET ZERO，未保存 posed blend。

出处：[PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_REPORT.md](../research/audits/palmar_thenar_source_shape_restoration_r1/PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_REPORT.md)

## 原报告与关键代码

- [audits/palmar_thenar_source_shape_restoration_r1/PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_REPORT.md](../research/audits/palmar_thenar_source_shape_restoration_r1/PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_REPORT.md)
- [audits/palmar_thenar_source_shape_restoration_r1/common.py](../../src/legacy/audits/palmar_thenar_source_shape_restoration_r1/common.py)
- [audits/palmar_thenar_source_shape_restoration_r1/deliver.py](../../src/legacy/audits/palmar_thenar_source_shape_restoration_r1/deliver.py)
- [audits/palmar_thenar_source_shape_restoration_r1/make_inspection_sheets.py](../../src/legacy/audits/palmar_thenar_source_shape_restoration_r1/make_inspection_sheets.py)
- [audits/palmar_thenar_source_shape_restoration_r1/prepare_and_preview.py](../../src/legacy/audits/palmar_thenar_source_shape_restoration_r1/prepare_and_preview.py)
- [audits/palmar_thenar_source_shape_restoration_r1/save_and_smoke.py](../../src/legacy/audits/palmar_thenar_source_shape_restoration_r1/save_and_smoke.py)

## 输入、输出与大型证据

该目录原始成员 113 项；拟公开身份记录 109 项。
- `audits/palmar_thenar_source_shape_restoration_r1/RIGHT_HAND_STAGE5B_PALMAR_THENAR_RESTORATION_CANDIDATE_R1.blend` → `hands-research-r1-selected-006.zip` / `payload/audits/palmar_thenar_source_shape_restoration_r1/RIGHT_HAND_STAGE5B_PALMAR_THENAR_RESTORATION_CANDIDATE_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
