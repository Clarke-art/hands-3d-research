# STAGE5A_R2B_FEASIBILITY_ZONE_CLASSIFICATION_ERRATA — R1

**性质**：口径 / 方法勘误（classification & method errata）。
**不修改** `STAGE5A_R2B_THUMB_IP_FEASIBILITY_VOLUME.json`、
`STAGE5A_R2B_FEASIBLE_CANDIDATE_RANKING.json`、diagnosis JSON。
**不重跑**可行性搜索。

---

## 一、问题

R2B 中少数候选的**自身投影轴向**略超出正式 zone 下界：

```
正式 lower bound      = 57.333 mm
例：candidate axial   = 57.1757 mm   （低于下界 0.1573 mm）
```

但记录中被归入 zone 内。

**原因**：候选的 zone 归属继承自其**所属 axial slab level**
（slab levels = 57.333 … 74.333，全部在 zone 内），
而**未再次以 candidate 自身 projected axial 做最终 membership 判定**。

## 二、正式口径（canonical）

```
CANONICAL_ZONE_MEMBERSHIP =
  CANDIDATE_PROJECTED_AXIAL
  WITHIN
  [57.333, 74.639] mm
```

**不是：**

```
SOURCE_SLAB_LEVEL_IN_ZONE
```

## 三、量化影响

| 项 | 值 |
| --- | --- |
| candidate 总数 | 501 |
| 低于下界（min 57.1757 mm，低于 0.1573 mm） | **8** |
| 高于上界（max 74.6767 mm，高于 0.0377 mm） | **6** |
| 合计落在严格 zone 之外 | **14 / 501（2.8 %）** |
| 其中通过 clearance ≥ 3 mm 预筛 | 14（全部） |
| 其中 feasible | **0**（全部失败于 IP→TIP interior：20 样本 11–16/20） |

## 四、为什么**不推翻** no-solution 结论

口径问题使实际搜索集合：

```
slightly WIDER than the strict approved T-01 subset
```

即**多搜**了 14 个 zone 外候选，而**不是漏搜**。

```
在更宽集合内 feasible = 0
  ⇒ 其严格子集（approved T-01 subset）内 feasible = 0
```

因此 R2B 结论 `THUMB_IP_FEASIBLE_REGION = NONE_WITHIN_APPROVED_T01_REGION` **不变**。

## 五、是否需要重跑

**不需要。**

> 除非独立复核发现本项解释不成立，否则不得重跑整个 feasibility search。

本勘误已独立复核：14 个越界候选逐一确认非 feasible，且数量（14/501）不足以
影响任何统计结论。

## 六、对后续 Gate 的影响

**无**。
`THUMB_IP_TO_TIP_STRAIGHT_CHORD_CONTAINMENT = DIAGNOSTIC_ONLY`
（见 `stage5a_freeze/STAGE5A_THUMB_DISTAL_CHORD_GATE_AMENDMENT_R1.md`）不受影响；
`THUMB_IP_R = KEEP` 不变；未创建任何新 blend。
