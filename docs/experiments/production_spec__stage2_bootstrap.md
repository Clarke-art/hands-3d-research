# production_spec/stage2_bootstrap

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> > **本轮唯一目标**：`SOURCE ASSET → PROJECT WORKING COPY`（+ 完整 provenance / receipt）。

出处：[STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md](../research/production_spec/stage2_bootstrap/STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md)

> 目标对象的 mesh / UV / Multires / object data / 变换**逐比特未变**（已由签名证明）。

出处：[STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md](../research/production_spec/stage2_bootstrap/STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md)

## 技术路线

> > `production_spec/stage2_bootstrap/STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md`

出处：[STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md](../research/production_spec/stage2_bootstrap/STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md)

> > 阶段：**`STAGE2_ROUTE_C_GEOMETRY_BOOTSTRAP`**

出处：[STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md](../research/production_spec/stage2_bootstrap/STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md)

## 测试结论

> > 日期：2026-09-28　状态：**`READY_FOR_HUMAN_REVIEW`**

出处：[STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md](../research/production_spec/stage2_bootstrap/STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md)

> > **执行授权**：Human Review 已完成 —— `STAGE0_ROUTE_C_R1_3_1 = APPROVED`、`CURRENT_AUTHORITY_CONSISTENCY = PASS`、

出处：[STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md](../research/production_spec/stage2_bootstrap/STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md)

## 失败原因与证据边界

> | 原因 | `CON-9 ASSET_FRAME_NORMALIZATION` **属于 Stage 4**；Stage 2 禁止修改 geometry |

出处：[STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md](../research/production_spec/stage2_bootstrap/STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md)

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [production_spec/stage2_bootstrap/STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md](../research/production_spec/stage2_bootstrap/STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md)
- [production_spec/stage2_bootstrap/scripts/bootstrap_right_hand_c1.py](../../src/legacy/production_spec/stage2_bootstrap/scripts/bootstrap_right_hand_c1.py)
- [production_spec/stage2_bootstrap/scripts/probe_structure.py](../../src/legacy/production_spec/stage2_bootstrap/scripts/probe_structure.py)
- [production_spec/stage2_bootstrap/scripts/verify_parity.py](../../src/legacy/production_spec/stage2_bootstrap/scripts/verify_parity.py)

## 输入、输出与大型证据

该目录原始成员 8 项；拟公开身份记录 8 项。
- `production_spec/stage2_bootstrap/RIGHT_HAND_BOOTSTRAP_C1.blend` → `hands-research-r1-selected-014.zip` / `payload/production_spec/stage2_bootstrap/RIGHT_HAND_BOOTSTRAP_C1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
