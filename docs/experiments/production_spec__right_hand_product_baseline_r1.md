# production_spec/right_hand_product_baseline_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 技术路线

> 当前产品资产权威指针：`production_spec/RIGHT_HAND_PRODUCT_BASELINE.json`（链接见原报告）。新的路线说明：`RIGHT_HAND_PRODUCT_BASELINE_AUTHORITY_R1.md`（链接见原报告）。此前 3416 顶点 engineering mesh 降为 LEGACY_ENGINEERING_REFERENCE_ONLY。历史文件没有删除或覆盖。

出处：[RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_REPORT.md](../research/production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_REPORT.md)

## 测试结论

> **RIGHT_HAND_PRODUCT_BASELINE = PASS / HUMAN_APPROVED_FROZEN**

出处：[RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_REPORT.md](../research/production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_REPORT.md)

> Human 明确批准上一阶段六个状态，原 first-web 尖折已消除，ZERO 与 INDEX 正常，opposition L1/L2/L3 可接受。当前独立 asset 完整保留该已批准的网格、21 骨骼、权重、UV/材质及 first-web corrective/driver。没有新增 geometry、weight 或 corrective 修改。

出处：[RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_REPORT.md](../research/production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> **基线冻结成功；真实钢琴 motion 检查单独 BLOCKED。STOP — MOTION SOURCE NOT FOUND。下一步只记录为专门寻找现成手部 motion source。**

出处：[RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_REPORT.md](../research/production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_REPORT.md)

## 原报告与关键代码

- [production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_REPORT.md](../research/production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_REPORT.md)
- [production_spec/right_hand_product_baseline_r1/finalize_baseline.py](../../src/legacy/production_spec/right_hand_product_baseline_r1/finalize_baseline.py)
- [production_spec/right_hand_product_baseline_r1/freeze_baseline.py](../../src/legacy/production_spec/right_hand_product_baseline_r1/freeze_baseline.py)
- [production_spec/right_hand_product_baseline_r1/inspect_motion_libraries.py](../../src/legacy/production_spec/right_hand_product_baseline_r1/inspect_motion_libraries.py)

## 输入、输出与大型证据

该目录原始成员 16 项；拟公开身份记录 13 项。
- `production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend` → `hands-research-r1-selected-014.zip` / `payload/production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend`
- `production_spec/right_hand_product_baseline_r1/renders/BASELINE__ZERO__DORSAL_FULL.png` → `hands-research-r1-selected-014.zip` / `payload/production_spec/right_hand_product_baseline_r1/renders/BASELINE__ZERO__DORSAL_FULL.png`
- `production_spec/right_hand_product_baseline_r1/renders/BASELINE__ZERO__PALMAR_FULL.png` → `hands-research-r1-selected-014.zip` / `payload/production_spec/right_hand_product_baseline_r1/renders/BASELINE__ZERO__PALMAR_FULL.png`
- `production_spec/right_hand_product_baseline_r1/renders/BASELINE__ZERO__THENAR_CLOSE.png` → `hands-research-r1-selected-014.zip` / `payload/production_spec/right_hand_product_baseline_r1/renders/BASELINE__ZERO__THENAR_CLOSE.png`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
