# STAGE6B_R1A · SEAM REPAIR DECISION MATRIX

**轮次**：`STAGE6B_R1A_THUMB_INDEX_SEAM_TOPOLOGY_PROVENANCE_AUDIT`（READ-ONLY）
**供** Human Review 决策使用。**本文件不授权执行任何修复。**

---

## 1. 判定输入

```
CLASS_A (ANATOMIC_FIRST_WEB_TRANSITION)          =  6
CLASS_B (SEMANTIC_OWNERSHIP_MISCLASSIFICATION)   = 61
CLASS_C (ANATOMICALLY_INVALID_CROSS_LINK)        =  0
CLASS_D (AMBIGUOUS)                              =  0
                                        A+B+C+D  = 67   ✅ 无漏边
```

关键事实（全部为直接实测）：

1. **67 / 67** 条边都是**真实、流形、光滑**的内部网格边；**0** 条 bridge-like；**0** 条 near-coincident。
2. **67 / 67** 条边的两个端点用**真实网格测地线**判定落在**同一根手指**上（39 双侧 INDEX / 28 双侧 THUMB）。
3. **0** 条是真正跨指边界 → **CLASS_C = 0**。
4. 拇指尖 ↔ 食指尖 网格测地距离 = **201.70 mm** → 手部解剖结构正常，**不存在**“拇指末节直接连到食指”的非法连接。
5. 边界图为 **25 个互不相连碎片**（度直方图 `{1:54, 2:34, 3:4}`），
   且**每个端点 1-ring 都是混合标签**（0 个孤立标签岛）→ 典型“近似等距最近链测试随机翻面”特征。
6. 67 条边在 **S4A_CANDIDATE**（CC0 表面 + Multirez L1）即已存在；
   **0 / 67** 落在 Stage4A R2 CMC 手术 25.08 mm 约束半径内，**0** 触及 CMC cage patch。
7. CC0 bootstrap 与 Stage4A R2 表面 **median 0.0006 mm** 重合（刚体 180° about X）→ 同一表面、同一姿态。
8. 拇指片 ↔ 食指片最小间距：源姿态 10.86 mm → RSSF 前 **5.05 mm** → **RSSF R2 后 0.2465 mm**（≈20× 收缩）。

---

## 2. 决策分支（§27）

| 条件 | 是否成立 | 结论 |
|---|---|---|
| `CLASS_C > 0` → `LOCAL_SEAM_TOPOLOGY_REPAIR` | **否** | 不适用 |
| `CLASS_C = 0 且 CLASS_B > 0` → `SEMANTIC_OWNERSHIP_AUDIT_CORRECTION` | **是** | ✅ **命中** |
| 主要为 `CLASS_A` → 回到 pose path / contact constraint 诊断 | **否**（A 仅 6/67 = 8.96%） | 不适用但**保留为附带约束**（见 §4） |

### ✅ 推荐下一候选路径

```
NEXT_CANDIDATE =
    SEMANTIC_OWNERSHIP_AUDIT_CORRECTION
PENDING_HUMAN_AUTHORIZATION
```

**内容（仅描述，未执行）**：修正拇指 / 食指归属权威 ——
在 RSSF 接触带内用**网格真实的测地归属**（或等价的连通性权威）替代**纯空间最近链距离**，
使该带内顶点得到与其真实手指一致的 digit ownership **与** skin weight。

---

## 3. 明确**不**推荐的路径及其理由

| 路径 | 判定 | 理由 |
|---|---|---|
| `LOCAL_SEAM_TOPOLOGY_REPAIR`（剪边 / retopo） | **不推荐** | `CLASS_C = 0`；67 条边全部是合法连续皮肤的内部边，剪断会破坏真实手部表面 |
| 重开 CMC cage / `OPT-B THENAR/PALM MACRO RETOPO` | **不推荐** | `0 / 67` 边落在 CMC 手术半径内；CMC cage 已通过动态资格 |
| 直接改权重以消除 thumb ↔ index 接触 | **不推荐** | 接触是 RSSF 姿态的固有属性，不是权重缺陷（Stage6A 已冻结为 `POSE_CONSTRAINT_DIAGNOSTIC`） |
| 修改 joint / bone / roll / RSSF | **禁止** | 超出本线授权 |

> **`RETOPO_REQUIRED` 不得写入任何文件** —— CLASS_C 未被证明。

---

## 4. 必须与主路径一并处理的附带约束

1. **`CLASS_A`（6 条）** → 正式记录 **`DO_NOT_CUT_CLASS_A`**：
   位于拇指基底 / 第一指蹼连续皮肤带，任何后续修正都不得破坏该区域连续性。
2. **深穿透** → `THUMB_INDEX_DEEP_PENETRATION = SEPARATE_PENDING_STAGE6B_RETEST`
   （max penetration proxy **4.177 mm**）。**修 seam / 改 ownership 并不等于 Stage6B 自动通过**；
   修复后**必须重跑 Stage6B contact progression**。
3. **Stage5B region audit 影响** → R1A / R1B 的授权区域与 changed 集合都是由 `own_r1a` 派生的；
   接触带内顶点同时带**错误 digit 标签**与**错误 bind 权重**（例：拇指面片顶点带 `INDEX_MCP_R`）。
   → 若 HR 授权 ownership correction，需同时评估其对 Stage5B region audit 的回溯影响。

---

## 5. 现行状态（本文件不改变）

```
STAGE6B_R1A_SEAM_PROVENANCE = READY_FOR_HUMAN_REVIEW
STAGE6B                     = REMAINS_FAIL_CLOSED
CMC_CAGE_DYNAMIC_QUALIFICATION = PASS
T04_CMC                     = PASS_FOR_CURRENT_STAGE6B_RANGE
CMC_DEFORMATION_FINAL       = PENDING
DEFORMATION_FINAL           = PENDING
TOPOLOGY_REPAIR             = NOT_STARTED
OWNERSHIP_CORRECTION        = NOT_STARTED
STAGE6B_RETEST              = NOT_STARTED
```

**STOP —— 等待 Human Review 授权。**
