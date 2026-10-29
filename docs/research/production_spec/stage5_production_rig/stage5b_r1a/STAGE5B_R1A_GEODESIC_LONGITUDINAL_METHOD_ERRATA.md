# STAGE5B_R1A_GEODESIC_LONGITUDINAL_METHOD_ERRATA

**性质**：ERRATA sidecar（方法学勘误）。**不回改**任何历史文件。
**本轮**：纯只读测量 + 文档。未修改任何 blend、未修改任何权重。
**证据来源**：`stage5b_r1a/STAGE5B_R1A_THUMB_WEIGHT_ROOT_CAUSE_AUDIT.json`
→ 键 `geodesic_coordinate_rejection`（R1A 只读根因审计，在改权重之前产出）
**冻结输入**：`stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend`
SHA-256 `c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845`

---

## 零、正式结论（binding）

```
GLOBAL_THUMB_LONGITUDINAL_COORDINATE  = APPROVED_JOINT_POLYLINE_ARC_LENGTH
FORBIDDEN                             = GLOBAL_SURFACE_GEODESIC_FROM_DISTAL_TIP
LOCAL_DISTAL_CAP_GEODESIC_9MM         = REMAINS_APPROVED
```

两句话必须同时成立、不得互相推翻：

- **禁用**：以“从拇指最远端顶点出发的**全局**表面测地距离”作为整根拇指的纵向坐标。
- **保留**：Stage5A 已批准的
  `GEODESIC_CONNECTED_CAP_FROM_DISTAL_MOST_SURFACE_REGION`（**局部** 9 mm 测地远端 cap patch）继续有效。

---

## 一、现象

在当前 mesh 上，`geodesic distance from the thumb distal-most vertex (D* = v2189)`
**沿拇指方向不单调**，因此不能承担“整指纵向坐标”的职责。

| 顶点 | 身份 | 空间（欧氏）关系 | 表面测地距离（自 D\*） |
|---|---|---|---|
| **v2189** | 拇指最远端顶点 D\*、R2A 批准 distal-cap 成员 | 0（种子） | **0.000 mm** |
| v1076 | R2A 批准 distal-cap patch 的**代表点**（geodesic 1-median） | 距 cap 代表点 0.258 mm（几乎同点） | **8.938 mm** |
| **v284** | R1 时代 THUMB_TIP 地标所在顶点 | 与 v1076 空间相距 **12.027 mm** | **174.705 mm** |
| 拇指指甲板 22 个顶点（全部） | material_index == 1 且 face 质心属拇指 | 距 D\* 8–30 mm | **152.313 – 175.279 mm** |
| 拇指指甲近端 border | v1383 / v2740 | 距 D\* 约 20–30 mm | **163.169 / 169.358 mm** |

补充计数（同一证据）：

```
#{ v : geodesic_from_D* > 120 mm  AND  lateral distance to thumb chain < 15 mm } = 287
```

即：**约 287 个“空间上就贴在拇指上”的顶点，其表面测地距离超过 120 mm**。

---

## 二、诊断

```
FOLD / SHEET TOPOLOGY
  ⇒ GLOBAL_SURFACE_PATH_DISCONTINUITY
```

- v1076 与 v284 空间仅 12.027 mm 之隔，表面测地却相差 165.767 mm ⇒ 两者之间存在
  **表面折痕 / 片层结构**，最短表面路径必须绕行（ridge → 折返），而非横穿。
- 指尖 `max_geo` 与关节层级自洽性一并失效——测地层级出现**非物理排序**：

| 关节（诊断量） | 自 D\* 的表面测地距离 |
|---|---|
| THUMB_IP_R | **164.485 mm** |
| THUMB_MCP_R | **118.099 mm** |
| THUMB_CMC_R | **130.470 mm** |
| WRIST_R | 278.744 mm |
| THUMB_TIP_R（R1 时代地标） | 174.705 mm |

  真实解剖顺序应为 `IP < MCP < CMC < WRIST`；实测为
  `MCP(118.10) < CMC(130.47) < IP(164.48)` —— **IP 反而最远**，完全不成立。

- 结论：该坐标在**拇指自有表面范围内**就不能作为“距指尖多远”的单调度量，
  更不可能作为跨区域（拇指→掌→腕）的纵向坐标。

### 与 R1 的关系（损害评估）

R1 的 `s5b_r1_bind.py` **定义了** `GEO[D] = dij(DSTAR[D])` 与 `gval(D, p)`，
但**守卫与权重公式从未调用**（实际使用的是 `arc_of()` 关节折线弧长）。
因此该缺陷**未在 R1 造成损害**，但它是 R1A 必须显式排除的方法学陷阱。

---

## 三、采用的替代坐标（已冻结）

```
THUMB_LONGITUDINAL_AUTHORITY = APPROVED_JOINT_POLYLINE_ARC_LENGTH
POLYLINE = THUMB_CMC_R.head -> THUMB_CMC_R.tail(=MCP) -> THUMB_MCP_R.tail(=IP) -> THUMB_TIP_R.head
XIJ（mm）= [0.0(CMC head), 42.6796(MCP joint), 71.8815(IP joint), 93.9454(TIP landmark)]
```

理由：

1. **单调**：沿已批准运动学轴的投影，天然从根部到指尖递增；
2. **贴合 authority**：与 Stage5A 冻结的 21-bone 关节系一致（bone = KINEMATIC CONTROL AXIS）；
3. **复现批准范围**：IP 段 71.8815 → 93.9454 mm（= 22.0639 mm）与 R2A 批准的
   `distal_joint_to_landmark = 22.0608 mm` 一致；
4. **姿态无关的确定性**：不依赖表面拓扑细节。

R1A 全部纵向量（`W_IP / W_MCP / W_CMC / W_BASE` 的 joint-local transition）均建立在该坐标上。

---

## 四、明确不构成本勘误的推翻对象

```
LOCAL_DISTAL_CAP_GEODESIC_9MM = REMAINS_APPROVED
```

- Stage5A `STAGE5A_HUMAN_APPROVAL_FREEZE_R1.md` §五 确立的
  `CANONICAL_DISTAL_CAP_METHOD = GEODESIC_CONNECTED_CAP_FROM_DISTAL_MOST_SURFACE_REGION`
  （D\* → mesh geodesic → connected digit-owned cap → **9.0 mm** calibrated radius
  → area-weighted centroid projected to surface → geodesic 1-median cross-check）
  **继续有效**，本轮**不重开、不降级、不改写**。
- 原因是适用范围不同：
  * 局部方法只在 **9 mm 半径**内做“连通球冠 + 代表点”，
    D\* 邻域内测地路径正常（cap patch 的最大内测地 18.1458 mm，patch 内外一致）；
  * 全局方法要求**整指单调**，被折痕/片层破坏。
- 因此 **"global 不可用" ≠ "local cap 不可用"**，不得据本勘误推翻 R2A 远端 cap 权威、
  不得重算 THUMB_TIP_R、不得改动 `distal_most_vertex / rep_vertex / cap patch` 任何成员。

| 用途 | Authority | 状态 |
|---|---|---|
| 整根拇指纵向参数（权重分区、joint transition） | `APPROVED_JOINT_POLYLINE_ARC_LENGTH` | 本轮冻结 |
| 拇指远端 cap patch（9 mm 测地连通球冠） | `GEODESIC_CONNECTED_CAP_FROM_DISTAL_MOST_SURFACE_REGION` | **继续有效（Stage5A 已批准）** |
| （弃用）全局表面测地纵向坐标 | `GLOBAL_SURFACE_GEODESIC_FROM_DISTAL_TIP` | **FORBIDDEN** |

---

## 五、对后续阶段的约束

1. **Stage6 / 后续任何权重轮**：不得引入 `GLOBAL_SURFACE_GEODESIC_FROM_DISTAL_TIP`
   作为指列纵向坐标；如需纵向量，一律使用已批准关节折线弧长。
2. 若将来网格拓扑改变（re-topo / 合并 seam），该禁令可在**新的只读复测**后重新评估——
   复测至少需证明 `IP < MCP < CMC < WRIST` 的测地层级单调性成立。
3. 本勘误**不改变** Stage5A 的
   `THUMB_IP_TO_TIP_STRAIGHT_CHORD_CONTAINMENT = DIAGNOSTIC_ONLY` 例外与四指 containment gate。

---

## 六、产物

```
stage5b_r1a/STAGE5B_R1A_GEODESIC_LONGITUDINAL_METHOD_ERRATA.md   （本文件）
stage5b_r1a/STAGE5B_R1A_THUMB_WEIGHT_ROOT_CAUSE_AUDIT.json
    → geodesic_coordinate_rejection                              （只读实测证据）
```
