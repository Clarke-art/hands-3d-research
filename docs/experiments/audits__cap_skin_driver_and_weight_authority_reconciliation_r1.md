# audits/cap_skin_driver_and_weight_authority_reconciliation_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 技术路线

> R3 authority canonical SHA256 `361f4f25201f5810830dc1bfc4bd2cf19db908aef8945801a63bfd2829197ff0`、membership SHA256 `f57483723e90cc34e0551bf70fac00c7c8cb789dbad5d0e248018fdaddd3741d`均精确匹配。冻结 graph 962/1881、THUMB/INDEX 498/464、boundary20、ambiguity21、CLASS_A6/6、FIRST_WEB7/14且hardpins0、old9 INDEX9且hardrole0、cap37与INDEX145 hard sources均保留。读取旧 field/validator 仅为绑定证据，未运行相关求解或 validator。

出处：[CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md](../research/audits/cap_skin_driver_and_weight_authority_reconciliation_r1/CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md)

> 未来candidate采用4组INDEX+WRIST simplex约束harmonic reconstruction；edge系数MED/length，geometry inverse-square bone-distance prior系数0.01，fixed valid local vectors为Dirichlet pins，按sorted IDs实现唯一convex问题。0.01为本轮明确提交Human审核的deterministic prior strength，不冒称历史批准参数。此优化未运行；所有cap9旧THUMB保护/override退休。需通过native INDEX continuity、outer seams、crater/spike以及targeted deformation检查。

出处：[CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md](../research/audits/cap_skin_driver_and_weight_authority_reconciliation_r1/CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md)

## 测试结论

> 本轮形成可供 Human 审批的 deterministic skin authority/rebuild plan。主要 authority 全部 RESOLVED，状态仍为 PENDING_HUMAN_APPROVAL。没有生成新权重向量，没有重建 skin、保存 blend、修改 geometry/rig、重跑 R3 或运行 Stage6。

出处：[CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md](../research/audits/cap_skin_driver_and_weight_authority_reconciliation_r1/CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md)

> first-web允许bones的slots全部不变且IP禁止，因此IP距离变化本身不要求改21点的vectors；其中1点需要重建、其余20点定向复验。CMC cage geometry FROZEN/PASS；exact skin mask未在本轮新冻结，仅geometry locality/protection context，不从R3创建mask。

出处：[CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md](../research/audits/cap_skin_driver_and_weight_authority_reconciliation_r1/CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md)

## 失败原因与证据边界

> 静态逐vertex比较old R2A与corrected deform-chain nearest segment、raw/clamped mu、arc、normalized longitudinal、distance/radius-normalized location。共同radius尺度沿用历史R1B诊断值。material阈值：distance或arc≥0.5MED，mu/normalized longitudinal≥0.05，radius-normalized≥0.1，或nearest segment改变；必须同时有active thumb distal field支持。全mesh numerical changes与active skin影响分开记录，不能因远处投影变化判全mesh失效。normalized longitudinal分母变化单独作为诊断，不是本规则使用的毫米arc，不能单独触发重建。active affected 163点。IP roll carriers即使距离变化小仍需定向复验，距离审计不证明旋转deformation合格。

出处：[CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md](../research/audits/cap_skin_driver_and_weight_authority_reconciliation_r1/CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md)

> R1C/D/E实际保存delta及其cap-derived repair scope作为复验原因保留，不导入失败candidate向量。safe vectors也必须在获批后的新corrected bind上完成zero-pose/regression确认；SAFE_REUSE是exact vector eligibility，不是新资产已通过deformation。

出处：[CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md](../research/audits/cap_skin_driver_and_weight_authority_reconciliation_r1/CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md)

## 后续建议

> 每项authority状态RESOLVED指规则可执行；candidate static/deformation仍NOT_RUN，DEFORMATION_VALIDATION_REQUIRED可以进入获批后的候选重建，不再增加解剖逐点研究。Review七问仅审批driver/INDEX修正/shared wrapper/reuse-envelope/edge/ownership guard/下一候选重建。全部YES才批准TARGETED_RIG_AND_SKIN_DATA_REBUILD_AFTER_APPROVAL_R1；不会自动执行、不批准Stage6/production promotion。

出处：[CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md](../research/audits/cap_skin_driver_and_weight_authority_reconciliation_r1/CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md)

## 原报告与关键代码

- [audits/cap_skin_driver_and_weight_authority_reconciliation_r1/CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md](../research/audits/cap_skin_driver_and_weight_authority_reconciliation_r1/CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md)
- [audits/cap_skin_driver_and_weight_authority_reconciliation_r1/extract_read_only.py](../../src/legacy/audits/cap_skin_driver_and_weight_authority_reconciliation_r1/extract_read_only.py)
- [audits/cap_skin_driver_and_weight_authority_reconciliation_r1/make_review.py](../../src/legacy/audits/cap_skin_driver_and_weight_authority_reconciliation_r1/make_review.py)
- [audits/cap_skin_driver_and_weight_authority_reconciliation_r1/reconcile.py](../../src/legacy/audits/cap_skin_driver_and_weight_authority_reconciliation_r1/reconcile.py)
- [audits/cap_skin_driver_and_weight_authority_reconciliation_r1/snapshot.py](../../src/legacy/audits/cap_skin_driver_and_weight_authority_reconciliation_r1/snapshot.py)
- [audits/cap_skin_driver_and_weight_authority_reconciliation_r1/verify.py](../../src/legacy/audits/cap_skin_driver_and_weight_authority_reconciliation_r1/verify.py)

## 输入、输出与大型证据

该目录原始成员 44 项；拟公开身份记录 43 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
