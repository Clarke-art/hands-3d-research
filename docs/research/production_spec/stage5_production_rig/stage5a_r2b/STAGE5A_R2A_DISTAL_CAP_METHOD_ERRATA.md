# STAGE5A_R2A_DISTAL_CAP_METHOD_ERRATA — R1

**性质**：文档 provenance 勘误。**不回改**任何历史文件
（`stage5a_r2a/THUMB_DISTAL_CAP_AUDIT.json`、`stage5a_r2a/FOUR_FINGER_TIP_REFERENCE.json` 原样保留）。

---

## 一、问题

R2A 正式报告 / STATUS 已经采用**一套** canonical cap authority（axis-free 测地法），
但上述两个 JSON 的部分 `method` 字段仍保留早期迭代文本
（「fitted medial distal axis + 0.5 mm slab transition / coverage ≥ 0.90」）。
两套描述**不能同时**作为 canonical authority。

## 二、唯一 canonical authority（正式声明）

```
CANONICAL_DISTAL_CAP_METHOD =
  GEODESIC_CONNECTED_CAP_FROM_DISTAL_MOST_SURFACE_REGION
```

定义（唯一，无可选参数）：

1. **D\*** = 该指自有面片顶点中、位于批准远端关节（THUMB_IP_R / *_DIP_R）远侧、
   距该关节**最远**的表面顶点。
2. **g()** = 从 D\* 出发的 **mesh 测地距离**（表面图 Dijkstra）——全程不依赖任何拟合轴向。
3. **DISTAL_CAP_PATCH** = 包含最靠近 D\* 面片的**连通** digit-owned 面片区域，
   限制为「面片最近顶点 g ≤ **9.0 mm**」。
   9.0 mm 为**已声明并校准**的测地半径：在该半径下，patch 代表点能复现四根已批准
   指尖 landmark 到其各自 D\* 的 0.3983–2.9819 mm 关系（见
   `stage5a_r2a/FOUR_FINGER_TIP_REFERENCE.json`）。非顶点百分比、非固定顶点数。
4. **CAP REPRESENTATIVE** = patch 的**面积加权质心**投影回真实表面；
   用 patch 的**测地 1-median** 交叉验证（R2A 拇指两者相差 0.347 mm）。

## 三、早期方法的状态

```
"fitted medial distal axis + 0.5 mm slab transition (coverage >= 0.90)"
        = SUPERSEDED_DIAGNOSTIC_METHOD
```

仅作为中间诊断证据保留在 `_tmp/`（`S5A_R2A_CAP_PROFILES.json`、`RINGDIAG*.json`、
`SWEEP*.json`、`PROFDIAG.json`）与历史 JSON 的叙述字段中。
**不**是 canonical authority；不得据此重算或覆盖任何已批准 landmark。

## 四、权威文件链

| 文件 | 角色 |
| --- | --- |
| `stage5a_r2a/STAGE5A_R2A_STATUS.json` | R2A 权威状态 + canonical semantic |
| `stage5a_r2a/THUMB_DISTAL_CAP_AUDIT.json` | 帽 patch 顶点/面片 ID、质心、代表点实测 |
| `stage5a_r2a/FOUR_FINGER_TIP_REFERENCE.json` | 9.0 mm 半径的校准依据（四指包络） |
| 本勘误 | 声明上述唯一 canonical method |

## 五、对已批准内容的影响

**无**。R2A `THUMB_TIP_R = [1.45281744, 0.019802358, 0.493028343]` 由 canonical method
（第 3 条）产生，本轮 Human Review 已 `KEEP`。此勘误只消除文档层面的双权威描述，
不改变任何几何、不重开任何已批准项。
