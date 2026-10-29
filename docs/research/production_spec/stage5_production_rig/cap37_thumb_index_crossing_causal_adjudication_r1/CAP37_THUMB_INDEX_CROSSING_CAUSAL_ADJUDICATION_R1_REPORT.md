# CAP37_THUMB_INDEX_CROSSING_CAUSAL_ADJUDICATION_R1

**READY_FOR_HUMAN_CAUSAL_ADJUDICATION — STOP / HUMAN REVIEW**

三对均裁决为 **E — VALIDATOR_SEMANTIC_ESCALATION_REQUIRES_HUMAN_ADJUDICATION**。真实 triangle crossing 已复现；尚未证明它们构成不可接受的 skin / rig / 教学形态失败。不得将 E 读作通过或已批准 pose contact。上一轮 FAIL_CLOSED 文件保持原样，本报告作为独立因果裁决附录。

## 因果结论

2×2 是保存标量权重与各自 world-space rest inverse / pose matrix 的只读 LBS 干预。骨骼命名、group order、关节头/父级、bind geometry 相同，差异只限已批准 IP/TIP slots。三候选实际 Blender modifier 与数学 kernel 的所有采样 crossing/Class 谓词一致，最大位置误差 0.000174 mm。hybrid 不作为 anatomy/skin authority 或生产候选。

| Pair / pose | BASE | K_ONLY | W_ONLY | FULL | 机械结论 | 最终资格 |
|---|---|---|---|---|---|---|
| PAIR_1225_2740 / TH_IP_30 | 无相交 | 无相交 | B | A | skin 必要；IP 轴额外升级 B→A | E |
| PAIR_1041_2735 / IDX_MCP_45 | 无相交 | 无相交 | A | A | skin 必要且足以形成此 Class A；thumb correction 非必要 | E |
| PAIR_1226_2742 / IDX_MCP_45 | 无相交 | 无相交 | A | A | skin 必要且足以形成此 Class A；thumb correction 非必要 | E |

INDEX pose 中，corrected THUMB patch 不再随 INDEX driver 运动，INDEX patch 向其靠近；TH_IP pose 中，corrected THUMB patch 能随 IP 运动。donor 没有相交不能作为其驱动正确性的证据。这里识别的是相交的机械因素，不是“权重错误”的判定。

## Onset（local-X 为负，角度列表示 flexion 大小）

0.5° 固定步进，首次阳性区间二分至 0.03125°；未创造人体允许角度。contact 为 minimum triangle distance ≤0.001 mm 的近零诊断样本，沿用 V2 footprint 数值精度；精确相交仍使用原谓词。此 contact 不代表解析精确相切角。只定位指定 pair，不代表整个两指第一次接触。

| Pair | donor | R1 exact crossing | R2 contact | R2 exact crossing | R2 V2 A |
|---|---|---|---|---|---|
| PAIR_1225_2740 | 授权范围内未观察到 | 23.15625–23.18750° | 23.15625–23.18750° | 23.15625–23.18750° | 28.93750–28.96875° |
| PAIR_1041_2735 | 授权范围内未观察到 | 33.03125–33.06250° | 33.15625–33.18750° | 33.15625–33.18750° | 33.15625–33.18750° |
| PAIR_1226_2742 | 授权范围内未观察到 | 24.68750–24.71875° | 24.75000–24.78125° | 24.75000–24.78125° | 24.75000–24.78125° |

TH_IP onset 相同；INDEX 两对 R2 onset 均略晚于 R1。A→B recovery 使此前在授权区间未发生的 pair 出现，但不能把这些诊断角度解释为人体许可边界。全采样、contact / crossing / Class A、poke、segment、局部坐标及 onset surface 图片保存在 JSON / review.html。

## 局部刚性与非刚性

| Pair / R2 | THUMB core residual RMS | INDEX core residual RMS | 运动侧 core area | 运动侧 one-ring area range | 去掉 core 非刚性残差后 |
|---|---:|---:|---:|---|---|
| PAIR_1225_2740 | 0.131353 mm | 0.000015 mm | 1.013049 | 0.981765–1.050676 | 仍有 exact crossing |
| PAIR_1041_2735 | 0.000000 mm | 0.430145 mm | 0.719338 | 0.695391–0.750883 | 仍有 exact crossing |
| PAIR_1226_2742 | 0.000000 mm | 0.632691 mm | 0.635125 | 0.599538–0.745277 | 仍有 exact crossing |

TH_IP：运动约 6.84 mm，core residual 0.131 mm，core area 约 1.013，one-ring edge 约 0.978–1.086；对侧 INDEX 近静止。INDEX：THUMB 近静止，INDEX 有真实 blend compression；两 core area 约 0.719 / 0.635，ring min edge 约 0.685 / 0.573，ring normal 在刚性旋转后最大约 6.90° / 16.92°。这些压缩与残差保留给 Human，不能称为“完全刚性”或自动正常。

三对 rigid-only best-fit surfaces 仍相交，说明局部扭坏不是相交的必要条件；此诊断不证明整体皮肤刚性、解剖合理性或视觉接受。检查范围内无坍塌、degenerate、5× edge explosion 或明显 flap 证据。两表面不是 authority-paired opposing skin，局部 tissue thickness 不可识别；surface gap / in-plane compression 不冒充厚度。

## Validator 语义差异

Stage6A 使用 bind BVH subtraction、旧 centroid ownership 与 centroid-plane proxy，将 target–other digit 归为 pose contact / Human Review；硬 gate 主要抓 NaN、collapse、degenerate 等。R1C V2 使用 exact triangle test、footprint-constrained vertex-plane poke 与 bind facet mean，Class A 条件是相交且 poke / facet ≥1。两代 proxy 不同，0.5 mm practical visibility 与 V2 ratio 也不是同一阈值。Stage6A_R1B 使用 R1C skin，不得混称本轮 R1B donor。

V2 poke 取落在对侧 footprint 内的顶点到平面的绝对距离；它不是实体厚度、体积穿入深度或最小分离位移。在 INDEX 两对首次 Class A 阳性处，交线仅 0.000104 / 0.001203 mm，poke 已约 3.901 / 4.967 mm。算法可按定义给出 A，却不能凭这个量独立判定教学可见失败。R1C 历史明显失败还包含 flap / 10–24× strain 与实景证据，不能把它的结论泛化成所有 Class A 自动失败。本轮未改任何 classifier/threshold。

## corrected R1 → R2

**R2 DID NOT INTRODUCE THE BLOCKER。** 三对来自 corrected recovery，R2 新增为 0。未确认实质形态失败恶化；不声称每个数值都不增。

| Pair | terminal poke Δ (R2−R1) | terminal segment Δ | INDEX core residual RMS Δ |
|---|---:|---:|---:|
| PAIR_1225_2740 | +0.000000000 mm | +0.000000000 mm | +0.000000000 mm |
| PAIR_1041_2735 | -0.001604179 mm | -0.028065178 mm | +0.004036300 mm |
| PAIR_1226_2742 | -0.002344139 mm | +0.010062475 mm | +0.000988423 mm |

1226/2742 segment 约增加 0.010 mm；INDEX core residual 分别增加约 0.0040 / 0.0010 mm。逐项保留，不设任意容差抹去。机器与匹配图未确认这些变化造成实质失败恶化，最终 visual severity 仍待 Human。

## 必须输出的计数

```json
{
  "HISTORICAL_R1B_PAIR_COUNT": 0,
  "CORRECTED_R1_PAIR_COUNT": 3,
  "R2_PAIR_COUNT": 3,
  "CORRECTED_RECOVERY_INTRODUCED_PAIR_COUNT": 3,
  "R2_INCREMENTAL_INTRODUCED_PAIR_COUNT": 0,
  "R2_WORSENED_PAIR_COUNT": 0,
  "KINEMATIC_CAUSAL_COUNT": 0,
  "SKIN_CAUSAL_COUNT": 0,
  "POSE_CONTACT_ONLY_COUNT": 0,
  "MIXED_CAUSAL_COUNT": 0,
  "VALIDATOR_SEMANTIC_ADJUDICATION_COUNT": 3,
  "VISIBLE_TEACHING_DEFECT_COUNT": null,
  "VISIBLE_TEACHING_DEFECT_COUNT_STATUS": "UNDETERMINED_PENDING_HUMAN_REVIEW",
  "VISIBLE_GROSS_LOCAL_SKIN_DEFECT_CONFIRMED_COUNT": 0,
  "GEOMETRIC_SKIN_NECESSARY_PAIR_COUNT": 3,
  "GEOMETRIC_KINEMATIC_NECESSARY_FOR_EXACT_CROSSING_COUNT": 0,
  "GEOMETRIC_KINEMATIC_NECESSARY_FOR_CLASS_A_COUNT": 1,
  "R2_POSITIVE_SEGMENT_DELTA_PAIR_COUNT": 1,
  "R2_POSITIVE_CORE_RESIDUAL_DELTA_PAIR_COUNT": 2,
  "PRODUCTION_DRIFT": 0,
  "PAIR_1225_2740_CAUSE": "VALIDATOR_SEMANTIC_ESCALATION_REQUIRES_HUMAN_ADJUDICATION",
  "PAIR_1041_2735_CAUSE": "VALIDATOR_SEMANTIC_ESCALATION_REQUIRES_HUMAN_ADJUDICATION",
  "PAIR_1226_2742_CAUSE": "VALIDATOR_SEMANTIC_ESCALATION_REQUIRES_HUMAN_ADJUDICATION"
}
```

KINEMATIC / SKIN / MIXED_CAUSAL_COUNT 是最终 B/C/D“失败”分类计数，均 0 confirmed，不否认 skin 对三对几何的必要性。VISIBLE_TEACHING_DEFECT_COUNT = null（待 Human），不能伪造 0。R2_WORSENED_PAIR_COUNT = 0 confirmed，不能读作视觉已批准或所有 scalar identity。

## Human evidence 与冻结验证

66 张 matched PNG：三候选、三对、full hand / thumb-index close / plain solid / wire / isolated pair / real plane section，加 onset 同角度比较。相同 pose、camera、light、scale；plain solid 没有 forensic color 遮盖。软件 flat shading 用于几何 Human evidence，不能代表最终教学产品材质/视角。

新结果仅位于本轮目录。生产文件、旧 qualification、其他 fixtures 的历史结果不改不重测。独立 clean reopen 与全历史 hash 比较见 PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json。

**NEXT = READY_FOR_HUMAN_CAUSAL_ADJUDICATION；STOP — HUMAN REVIEW。** 无 remediation、scope/kinematic amendment、Stage6/R3 rerun 或 promotion authority。
