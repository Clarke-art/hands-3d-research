# audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 历史 finite local scale verdict=**PAIRWISE-DOMINATED**。10mm的 unary 为10，一条pairwise为1296，倍率129.6；1–20mm范围倍率64.8–1296。此结论指局部代价尺度，不等于每个全局能量的pairwise总和都占多数；真正的换标签取舍看 unary 差值和多条边，hard pins又是单独约束。新解不得以历史labels、边界数量或flow为目标。

出处：[NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW_R1_REPORT.md](../research/audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW_R1_REPORT.md)

## 技术路线

> U2 的设计 intent 由已记录的数学 contract 确认：报告把 unary 定义为物理测地距离，把 pairwise 定义为 TAU/3 mm；参数 JSON 明确 CAP_MAX_mm=400；前序 `_r3_geo.py` 实际返回 mm；正式 ambiguity 判据也实际将 dT/dI ×MM 后与 TAU 比较。它们共同支持共同毫米成本。仅 terminal-capacity 和复制的复算实现漏掉 m→mm 换算。此判断不是只依赖注释，也未比较哪组单位复现旧边界。记录中的设计 contract 与执行相矛盾，**historical unit bug=YES**；不声称已获 Human 批准，也不推断未记录的主观想法。

出处：[NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW_R1_REPORT.md](../research/audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW_R1_REPORT.md)

## 测试结论

> **FAIL_CLOSED**。R3 单位候选裁决为 **CORRECTED_COMMON_MM_SEMANTICS**；独立 proximal exclusive/shared extent 仍未唯一成立。没有 canonical graph、corrected radius、最终 hard-source 集合或可执行 unary input contract。Human Review 页面不生成。

出处：[NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW_R1_REPORT.md](../research/audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW_R1_REPORT.md)

> 历史 finite local scale verdict=**PAIRWISE-DOMINATED**。10mm的 unary 为10，一条pairwise为1296，倍率129.6；1–20mm范围倍率64.8–1296。此结论指局部代价尺度，不等于每个全局能量的pairwise总和都占多数；真正的换标签取舍看 unary 差值和多条边，hard pins又是单独约束。新解不得以历史labels、边界数量或flow为目标。

出处：[NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW_R1_REPORT.md](../research/audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> FIRST_WEB_21 membership保持；逐点记录native candidate、历史角色、批准的skin-weight角色、两条corrected chain距离/弧长及真实拓扑邻接。建议FW1 **SHARED_NEUTRAL_GRAPH_ONLY**。没有支持FW2独立exclusive子集的authority；FW3历史硬pin不能从权重批准推导。shared-neutral是solver输入角色，不等于要求未来二元label仍为第三类，更不能从未来label回推anatomical exclusivity。

出处：[NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW_R1_REPORT.md](../research/audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW_R1_REPORT.md)

> CMC cage geometry保持FROZEN/PASS，建议 **CAGE_GEOMETRY_PROTECTED_BUT_NOT_R3_HARD_SOURCE**；是否入图由最终domain决定，不因cage身份自动入图。全冻结mesh几何/topology/hash保护无需近似73点映射。局部deformation保护mask如果未来需要，应另依exact topology provenance确认；本轮不批准它。73点construction候选和120点unfiltered历史sphere不同；16点坐标受既有pole-neighbour smoothing影响，不把0.700591mm最近映射宣称为精确authority。旧R3仅加载/log cage，无直接cage hard-source条目。

出处：[NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW_R1_REPORT.md](../research/audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW_R1_REPORT.md)

## 原报告与关键代码

- [audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW_R1_REPORT.md](../research/audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW_R1_REPORT.md)
- [audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/finalize.py](../../src/legacy/audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/finalize.py)
- [audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/intake.py](../../src/legacy/audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/intake.py)
- [audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/static_audit.py](../../src/legacy/audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/static_audit.py)
- [audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/unit_audit.py](../../src/legacy/audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1/unit_audit.py)

## 输入、输出与大型证据

该目录原始成员 28 项；拟公开身份记录 27 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
