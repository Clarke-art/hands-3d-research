# audits/right_hand_first_web_foundational_rebuild_target_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 本轮目的不是重建，而是确定重建到哪一层。结论：要真正消除 first-web Human-visible blocker，

出处：[RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md](../research/audits/right_hand_first_web_foundational_rebuild_target_r1/RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md)

## 技术路线

>   **其数据未用于任何结论**，改用不依赖 skinning 复现的实测方法

出处：[RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md](../research/audits/right_hand_first_web_foundational_rebuild_target_r1/RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md)

> | `ROUTE_A_RECONCILIATION_R1.json` | 与 POC A 失败的调和测量 |

出处：[RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md](../research/audits/right_hand_first_web_foundational_rebuild_target_r1/RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md)

## 测试结论

> 本轮目的不是重建，而是确定重建到哪一层。结论：要真正消除 first-web Human-visible blocker，

出处：[RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md](../research/audits/right_hand_first_web_foundational_rebuild_target_r1/RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md)

> | 帧 | 状态 | 静止边长中位数 | 差分离散 max | >2× 边数 | 判定 |

出处：[RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md](../research/audits/right_hand_first_web_foundational_rebuild_target_r1/RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md)

## 失败原因与证据边界

> 原因是 POC A 的均匀 N×N 中点细分把局部边长中位数只从 4.05 mm 降到 3.80 mm（约 1.07 倍），

出处：[RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md](../research/audits/right_hand_first_web_foundational_rebuild_target_r1/RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md)

> 是局部承载被突破，不是整个变形模型失效。B/C 两条 POC（helper bone、local cage）失败也不构成

出处：[RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md](../research/audits/right_hand_first_web_foundational_rebuild_target_r1/RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md)

## 后续建议

> | Q7 | 下一轮是否值得正式实施该 level | **YES** |

出处：[RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md](../research/audits/right_hand_first_web_foundational_rebuild_target_r1/RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md)

> 若下一轮正式实施 LEVEL 1，第一个动作应当是**先做一次真正改变 edge flow 方向的

出处：[RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md](../research/audits/right_hand_first_web_foundational_rebuild_target_r1/RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md)

## 原报告与关键代码

- [audits/right_hand_first_web_foundational_rebuild_target_r1/RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md](../research/audits/right_hand_first_web_foundational_rebuild_target_r1/RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md)
- [audits/right_hand_first_web_foundational_rebuild_target_r1/common.py](../../src/legacy/audits/right_hand_first_web_foundational_rebuild_target_r1/common.py)
- [audits/right_hand_first_web_foundational_rebuild_target_r1/diagnose_attribution.py](../../src/legacy/audits/right_hand_first_web_foundational_rebuild_target_r1/diagnose_attribution.py)
- [audits/right_hand_first_web_foundational_rebuild_target_r1/diagnose_flow_vs_density.py](../../src/legacy/audits/right_hand_first_web_foundational_rebuild_target_r1/diagnose_flow_vs_density.py)
- [audits/right_hand_first_web_foundational_rebuild_target_r1/diagnose_rigid_fit.py](../../src/legacy/audits/right_hand_first_web_foundational_rebuild_target_r1/diagnose_rigid_fit.py)
- [audits/right_hand_first_web_foundational_rebuild_target_r1/diagnose_route_a_reconcile.py](../../src/legacy/audits/right_hand_first_web_foundational_rebuild_target_r1/diagnose_route_a_reconcile.py)
- [audits/right_hand_first_web_foundational_rebuild_target_r1/diagnose_structure.py](../../src/legacy/audits/right_hand_first_web_foundational_rebuild_target_r1/diagnose_structure.py)
- [audits/right_hand_first_web_foundational_rebuild_target_r1/diagnose_visible_crease.py](../../src/legacy/audits/right_hand_first_web_foundational_rebuild_target_r1/diagnose_visible_crease.py)
- [audits/right_hand_first_web_foundational_rebuild_target_r1/diagnose_weight_field.py](../../src/legacy/audits/right_hand_first_web_foundational_rebuild_target_r1/diagnose_weight_field.py)
- [audits/right_hand_first_web_foundational_rebuild_target_r1/make_evidence.py](../../src/legacy/audits/right_hand_first_web_foundational_rebuild_target_r1/make_evidence.py)
- [audits/right_hand_first_web_foundational_rebuild_target_r1/verify_protection.py](../../src/legacy/audits/right_hand_first_web_foundational_rebuild_target_r1/verify_protection.py)

## 输入、输出与大型证据

该目录原始成员 29 项；拟公开身份记录 22 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
