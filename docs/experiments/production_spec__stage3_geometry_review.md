# production_spec/stage3_geometry_review

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> > 其中 ring/little 的次序取决于各指 MCP 的 z 取值。本轮采用的是**可肉眼验证的远端伸达顺序**（指端 z），

出处：[GEOMETRY_REVIEW_REPORT_R1.md](../research/production_spec/stage3_geometry_review/GEOMETRY_REVIEW_REPORT_R1.md)

> | 层级 | faces | tris（估） | 相对 8k–20k 目标 | 相对 30k 硬上限 |

出处：[GEOMETRY_REVIEW_REPORT_R1.md](../research/production_spec/stage3_geometry_review/GEOMETRY_REVIEW_REPORT_R1.md)

## 技术路线

> > 阶段：**`STAGE3_ROUTE_C_GEOMETRY_REVIEW`　门禁：`GATE_2`**

出处：[GEOMETRY_REVIEW_REPORT_R1.md](../research/production_spec/stage3_geometry_review/GEOMETRY_REVIEW_REPORT_R1.md)

> > **执行授权**：`STAGE2_ROUTE_C_BOOTSTRAP = APPROVED`；`STAGE3 = AUTHORIZED_TO_START`。

出处：[GEOMETRY_REVIEW_REPORT_R1.md](../research/production_spec/stage3_geometry_review/GEOMETRY_REVIEW_REPORT_R1.md)

## 测试结论

> > 日期：2026-09-28　状态：**`READY_FOR_HUMAN_REVIEW`**

出处：[GEOMETRY_REVIEW_REPORT_R1.md](../research/production_spec/stage3_geometry_review/GEOMETRY_REVIEW_REPORT_R1.md)

> > ## ✅ `STAGE3_GEOMETRY_REVIEW = PASS` → `GATE2 = PASS` → `RIGHT_HAND_ENGINEERING_CANDIDATE = APPROVED`

出处：[GEOMETRY_REVIEW_REPORT_R1.md](../research/production_spec/stage3_geometry_review/GEOMETRY_REVIEW_REPORT_R1.md)

## 失败原因与证据边界

> > 未出现的结构性缺陷（解剖错误 / 手性错误 / 掌心拇指指蹼不可用 / 前臂不适合 / 需从零重建 / bootstrap 与 C1 不一致 / provenance 失效）**一项都不成立**。

出处：[GEOMETRY_REVIEW_REPORT_R1.md](../research/production_spec/stage3_geometry_review/GEOMETRY_REVIEW_REPORT_R1.md)

> | provenance 失效 | 母文件 byte-unchanged；receipt + 独立复核齐备 | ❌ 不成立 |

出处：[GEOMETRY_REVIEW_REPORT_R1.md](../research/production_spec/stage3_geometry_review/GEOMETRY_REVIEW_REPORT_R1.md)

## 后续建议

> | 是否因早期规范提过"短前臂"而机械裁短 | 🚫 **未裁短**（本轮禁止裁切，亦未建议裁切） |

出处：[GEOMETRY_REVIEW_REPORT_R1.md](../research/production_spec/stage3_geometry_review/GEOMETRY_REVIEW_REPORT_R1.md)

> → **不建议 `SHORTEN_IN_STAGE4`**；`TARGET_FOREARM_LENGTH = CURRENT_SOURCE_LENGTH = 0.0886 m`。

出处：[GEOMETRY_REVIEW_REPORT_R1.md](../research/production_spec/stage3_geometry_review/GEOMETRY_REVIEW_REPORT_R1.md)

## 原报告与关键代码

- [production_spec/stage3_geometry_review/GEOMETRY_REVIEW_REPORT_R1.md](../research/production_spec/stage3_geometry_review/GEOMETRY_REVIEW_REPORT_R1.md)
- [production_spec/stage3_geometry_review/scripts/geometry_review_measure.py](../../src/legacy/production_spec/stage3_geometry_review/scripts/geometry_review_measure.py)
- [production_spec/stage3_geometry_review/scripts/render_review_view.py](../../src/legacy/production_spec/stage3_geometry_review/scripts/render_review_view.py)

## 输入、输出与大型证据

该目录原始成员 8 项；拟公开身份记录 8 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
