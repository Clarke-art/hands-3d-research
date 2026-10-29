# STAGE5A_R2B_STRUCTURAL_DIAGNOSIS_WORDING_ERRATA — R1

**性质**：措辞勘误（wording errata）。**不修改任何历史 diagnosis JSON**；
`stage5a_r2b/THUMB_STRAIGHT_BONE_COMPATIBILITY_DIAGNOSIS.json` 原样保留。

---

## 一、需要修正的过强表述

历史 diagnosis JSON 中记录了：

```
A_thumb_distal_mesh_curvature
  centreline_sagitta_mm       = 6.7968
  mean_section_radius_mm      = 7.9575
  sagitta_over_radius         = 0.8541
  verdict                     = "CONTRIBUTING -- PRIMARY"
```

其中 **6.7968 < 7.9575**，因此**不得**写成：

- "sagitta > radius, therefore mathematically impossible"
- "数学上必然不可能"
- 任何等价的**数学必然性**表述

## 二、正式表述（取代上述任何过强措辞）

```
STRONG CURVATURE = CONTRIBUTING PRIMARY FACTOR

R2B FEASIBILITY SEARCH =
  NO VALID STRAIGHT-CHORD SOLUTION FOUND
  IN THE SEARCHED APPROVED REGION
  AND THE EXTENDED DIAGNOSTIC BAND

结论性质 =
  EMPIRICAL_ENGINEERING_INCOMPATIBILITY_FINDING
```

**不是**：

```
FORMAL_MATHEMATICAL_IMPOSSIBILITY_PROOF
```

## 三、为什么结论仍然成立（且不需要数学必然性）

结论的支撑是**穷举式工程搜索**，不是几何定理：

1. 批准 T-01 zone 内：501 个 inside + THUMB-owned candidate，259 个 clearance ≥ 3 mm，
   **strict feasible = 0**；
2. 扩展诊断带 axial 35–100 mm：**531** 个 candidate 中，
   同时满足 MCP→IP 40/40 且 IP→TIP 40/40 的位置 = **0**；
3. 最佳折中仅 **35/40**，且位于 zone 外 11.0651 mm。

因此正确表述是「在已搜索集合内**未找到**可行解」，其性质为
**经验性工程不兼容结论**，而非形式化不可能证明。

## 四、弯曲度量的正确读法

```
sagitta 6.7968 mm  <  mean section radius 7.9575 mm   (ratio 0.8541)
```

读作：**直线弦相对中心线偏离 6.80 mm，而该处平均剖面半径仅 7.96 mm ——
弦已贴着管壁运行，因而在离散网格上必然出现局部穿出。**
这是对**观测现象**的量化解释，不是封闭形式的必然性证明。

## 五、影响范围

**无**：不改变 `THUMB_IP_R = KEEP`、不改变
`THUMB_IP_TO_TIP_STRAIGHT_CHORD_CONTAINMENT = DIAGNOSTIC_ONLY`
（见 `stage5a_freeze/STAGE5A_THUMB_DISTAL_CHORD_GATE_AMENDMENT_R1.md`），
不改变任何几何或骨架。仅修正表述强度与结论性质标签。
