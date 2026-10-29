# STAGE4C_RSSF_ASSET_FINALIZATION_R1

**任务**：`STAGE4C_RSSF_ASSET_FINALIZATION_R1`（关闭 CON-4 / CON-6 / CON-7）
**冻结输入**：`stage4b_rssf/RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R2.blend`
`sha256 78fc890bfa9575cd62f2ae5f55beb2eda2df7ebf565c4e346a8b5af7295bbe04` ✓（执行前后逐字节一致）
→ 冻结为 **`STAGE4B_APPROVED_RSSF_BASELINE`**，未覆盖。
**运行时**：`D:\Blender\blender.exe`（Blender 5.1.2）
**未做**：改 RSSF pose / Retopo / 改 CMC cage / 改 T-01 loops / Production Rig / Production Skin Weight / 镜像左手 / 动画 / GLB / Three.js

---

## 0. 结论

```
STAGE4C = PASS
CON_4_NAILS              = PASS
CON_5_RSSF_REPOSE        = UNCHANGED_PASS
CON_6_ORIGIN             = PASS
CON_7_UV                 = PASS_AFTER_FIX
CANONICAL_HAND_POSE      = RSSF
HAND_BASE_TOPOLOGY       = UNCHANGED
CMC_DEFORMATION_FINAL    = PENDING_STAGE6
TEMP_RSSF_RIG            = REMOVED
PRODUCTION_RIG           = NOT_STARTED
RIGHT_HAND_ENGINEERING_MASTER_CANDIDATE = READY_FOR_STAGE5_RIG
```

**交付网格**：`stage4c/RIGHT_HAND_ENGINEERING_STAGE4C_R1.blend`
`sha256 66fa45325273f38f597f6af78bec603c471a697d6f1798b96eecc231e64bcdb6`（2,009,735 B）

---

## 1. 冻结 Stage4B R2（§二）

| 项 | 值 |
| --- | --- |
| 输入 | `RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R2.blend` |
| sha256（执行前） | `78fc890bfa9575cd62f2ae5f55beb2eda2df7ebf565c4e346a8b5af7295bbe04` |
| sha256（执行后） | 同上 —— **未改写** |
| 与 `STAGE4B_RSSF_R2_STATUS.json` / `RSSF_POSE_AUDIT_R2.json` 一致 | **是** |
| 冻结名 | `STAGE4B_APPROVED_RSSF_BASELINE` |
| 新文件 | `stage4c/RIGHT_HAND_ENGINEERING_STAGE4C_R1.blend`（`save_as_mainfile(copy=True)`） |

---

## 2. CON-4 — Nails（§三）

### 方案：**per-face 材质语义**（零几何增加）

§三 要求 semi-realistic / subtle / teaching-readable，且同时要求：不改指尖体积、不做很厚的假甲、
不明显增加 tris、不破坏 DIP/TIP deformation topology。**采用材质方案可一次性满足全部四条且零风险**；
独立甲片会新增几何、增加一张需同步维护的面，因此§三「如果仅靠材质即可达到教学识别，不要无必要增加独立高模甲片」直接适用。

| 项 | 值 |
| --- | --- |
| 材质槽 | 0 = `HAND_SKIN`（3259 面）、1 = `NAIL_BED`（155 面） |
| 选择规则 | 面法向落在**该指自身 nail normal** 的 `arccos(0.45) = 63.3°` 内；轴向位于远端骨 0.15–0.82；且在径向分布的外侧 55% |
| nail normal 来源 | `lateral × 远端骨方向`，符号取朝背侧；**由 POSED 远端骨导出**，故随 RSSF 卷曲而倾斜，而不是用全局背侧去猜 |
| 几何增加 | **0** |
| tri 增加 | **0** |

| 指 | 远端骨 | nail 面数 | 轴向跨度 | nail_normal·DORSAL |
| --- | --- | --- | --- | --- |
| THUMB | `THUMB_IP_R` | 46 | 0.15–0.81 | 0.900 |
| INDEX | `INDEX_DIP_R` | 47 | 0.15–0.79 | 0.435 |
| MIDDLE | `MIDDLE_DIP_R` | 36 | 0.16–0.81 | 0.297 |
| RING | `RING_DIP_R` | 44 | 0.17–0.79 | 0.230 |
| LITTLE | `LITTLE_DIP_R` | 31 | 0.15–0.81 | 0.415 |

**五指均可识别 nail side** ✓（每指 31–47 面，合计 155 / 3414 = 4.5%）。

**thumb nail plane 与四指的非共面关系**（§三末条）：

```
thumb_vs_index   87.98°
thumb_vs_middle  97.84°
thumb_vs_ring   102.57°
thumb_vs_little  91.14°
```

全部 > 45°，满足「合理非共面」。

**实测位置校验**：nail 面确实位于远端指节——index z 511.2–526.1 mm、y −35.3…−21.4 mm；
thumb z 457.9–482.4 mm、y 19.6…37.4 mm（背侧一侧）。

```
CON_4_NAILS = PASS
```

---

## 3. CON-6 — Origin（§四）

### ⚠ 发现一个实质性冲突，必须先说明

§四 同时给出两条要求：

1. **「优先复用：Stage4B TEMP_RIG 中已经验证的 `WRIST_R` joint centre」**
2. **「不得使用：…**前臂截断面中心** 作为替代」**

**在本资产上这两条互相冲突**，因为 Stage-4B 的 `WRIST_R` **就是**前臂截断面中心：

- Stage-4B 的运行日志原文：`WRIST_R narrowest cross-section at **−1.9 mm from the forearm cap**`
- 其 z = `0.277349 m`，而网格 bbox z-min = `0.276016 m` —— **完全重合**
- 用标记球渲染确认：`WRIST_R` 落在前臂截断边缘上（见 `_tmp/_wrist_markers_side.png`）

**第 2 条是硬性禁止（「不得使用」），第 1 条是偏好（「优先」）→ 以硬性禁止为准，未复用 `WRIST_R`。**

### 采用的定位器（可复现）

```
radius-limited INTERIOR minimum cross-section of the forearm tube
  · 轴向 = 全局 +Z（骨骼表证实：前臂 cap z=276.0 < MCP z=478.1 < 指尖 z≈527）
  · R_MAX = 45 mm —— 排除拇指列（thumb CMC 距轴 ~50 mm）
  · 排除 cut-plane band（z ≤ cap + 12 mm）—— 前臂是被切断的，其 cap ring 面积
    必然是最小值，纯全局最小**永远**落在截断面上（这正是 Stage-4B 踩的坑）
  · 指标 = 截面的凸包面积（对切片命中多少顶点不敏感）
  · 取**最靠近端**的内部局部极小（用 ±4 切片平滑后）
```

**为什么不能直接用全局最小面积**：本资产手掌是扁的（约 90 × 25 mm → 约 2090 mm²），
**比圆形的腕部（约 55 × 38 mm → 约 2110 mm²）还小**，所以纯全局最小会落到手掌里。

| 内部局部极小 | z | 面积 |
| --- | --- | --- |
| **①（= 腕，采用）** | **339.0 mm** | 2125.8 mm² |
| ②（= 掌，距 ① 97.1 mm） | 436.1 mm | 2119.0 mm² |

细化后的最小值切片：z = **335.77 mm**。

**独立交叉验证**：结果与 **Stage-3 已验收的 `wrist_narrowest_z = 0.343 m`** 相差 **7.23 mm**
（同一 basin）。
（附注：Stage-3 的 0.343 源自一个仅含 **n=8** 顶点的切片，其邻居为 n=19–27 —— 那个极小值本身是稀疏切片假象；
但它指认的高度被本轮独立方法证实。）

### 结果

| 项 | 值 |
| --- | --- |
| `ORIGIN_BEFORE` | `[1.40478158, 0.011328205, 0.353645504]` |
| `ORIGIN_AFTER` | `[1.408704638, 0.022395039, 0.335847497]` |
| `WRIST_ORIGIN` | `[1.408704638, 0.022395039, 0.335847497]`（`|Δ| = 0.000000000000 m`） |
| **`WORLD_GEOMETRY_DELTA_AFTER_ORIGIN`** | **3.725e-09 m（3.7 nm）** |
| float32 存储 epsilon | 1.47e-06 m |
| 判定 | **ZERO within float32 mesh storage precision** |

矩阵手法（正确性说明）：origin 即 `matrix_world.translation`，故「把原点到腕」= **替换平移、保留旋转/缩放**：
`B = (MW 的 3×3, translation = WRIST_ORIGIN)`，`v' = B⁻¹ · MW · v`。
（首版误用 `B = T(WRIST_ORIGIN) @ MW`，会把腕向量**加到**原平移上 → 原点跑到 2.81 m，已修正并重跑。）

**跨文件独立复核**（分别加载 R2 与 4C，逐顶点比较 world 坐标）：

```
objects   R2 = [Hand  - Realistic, TEMP_RSSF_REPOSE_ARMATURE]  ->  4C = [Hand  - Realistic]
verts     3416 -> 3416
max world delta = 3.80e-09 m   (float32 存储舍入，非几何改变)
```

未改变 world-space 几何、RSSF pose、canonical orientation。

```
CON_6_ORIGIN = PASS
```

### 🔺 需 Human Review 知晓的发现

```
FINDING ID : STAGE4B_WRIST_R_LOCATOR_DEFECT
```

Stage-4B 骨架的 `WRIST_R` 与其 201 mm 的「腕→掌心」骨在解剖上是错的（腕被放在前臂截断面上）。
**这不影响 Stage-4B 已通过的 RSSF 验收**（关节角全部在手指上测量），但它意味着
Stage-5 Rig 不得直接沿用该骨架的腕骨位置。已记入 `ORIGIN_AUDIT.json` 的 `P0_STYLE_FINDING`。

---

## 4. CON-7 — UV（§五）

### 只读审计（BEFORE）

| 指标 | 值 |
| --- | --- |
| UV layer 数 | 1（`UVMap`） |
| **missing / zero-area UV faces** | **64 / 64** |
| flipped UV triangles | 0（winding 一致：3350 正 / 0 负） |
| island 数 | 3 |
| overlap | 0.000000（无重叠） |
| stretch（UV 面积份额 ÷ 3D 面积份额） | p05 0.281 / 中位 0.903 / p95 1.931 / max 5.903 |
| texel density（4096²） | 中位 106.6 px/cm，max/min = 7.73 |

**诊断**：现有 UVMap **除 64 个面完全没有 UV 外是完整的**。这 64 个面**恰好**是
Stage-4A R2 建立的 CMC deformation cage（3 圈同心环 × 16 + 4×4 核心 = 48 + 16 = 64），
当时从未展 UV。其余方面（翻转 / 重叠 / 缠绕）全部正常。

→ 因此 **不得**无理由重展整只手；但 64 个面未定义 UV 时确实无法支撑
semi-realistic hand material + subtle nails，故 **必须做局部修正**。

### 局部修正（AFTER）

```
方法 : 把这 64 个面按它们自身的平均法向做平面投影，缩放进 0.16 的 UV 方块，
       再用 512×512 占用扫描 + 4 格 padding 找到空闲区域落位（实际落于 u=0.000, v=0.018）
范围 : 仅这 64 个面。UV 是 per-loop 属性 —— 未触碰任何邻面、顶点、多边形；手的其余部分未重展。
```

| 指标 | BEFORE | AFTER |
| --- | --- | --- |
| missing UV faces | 64 | **0** |
| zero-area UV faces | 64 | **0** |
| flipped | 0 | **0** |
| island 数 | 3 | 3 |
| overlap | 0.000000 | **0.000000** |
| texel max/min | 7.73 | 7.73 |

`intentional overlap`：**无**（修正前后均为 0，未引入）。
Topology 影响：**无**。

```
CON_7_UV = PASS_AFTER_FIX
```

---

## 5. TEMP RSSF Rig 处理（§六）

**先确认 RSSF geometry 不依赖这些对象**：

```json
{"mesh_parent": null, "mesh_modifiers": [], "mesh_constraints": [],
 "mesh_has_animation_data": false, "mesh_vertex_groups": []}
```

RSSF 已 bake 进 mesh（Stage-4B 用显式 LBS 施加，未建立 armature parent / modifier / constraint），
故断言通过后才删除。

**逐对象精确删除**（无 glob、无递归）：

```
removed : TEMP_RSSF_REPOSE_ARMATURE  (armature data 同名)
  flag TEMP_RSSF_REPOSE_ONLY = YES ; PRODUCTION_RIG = NO
removed_count = 1
geometry after TEMP-rig removal: max world delta 0.000000000 m
```

```
TEMP_RSSF_RIG = REMOVED        (provenance 仍完整保留在 STAGE4B_APPROVED_RSSF_BASELINE 中)
PRODUCTION_RIG = NOT_STARTED
```

---

## 6. 拓扑冻结与面数（§七、§八）

采用**材料式 nail** → §七 适用「`TOPOLOGY_SIGNATURE = EXACT_STAGE4B_R2`」：

```
TOPOLOGY_SIGNATURE_PRE  = 5a39668418eea1716a0fd9bc20b3d0aeda67e6a49a343b74eb3e17c339f90c1d
TOPOLOGY_SIGNATURE_POST = 5a39668418eea1716a0fd9bc20b3d0aeda67e6a49a343b74eb3e17c339f90c1d
TOPOLOGY_SIGNATURE_MATCH = True
V 3416 / E 6828 / F 3414（全部 quad）
HAND_BASE_TOPOLOGY_SIGNATURE = UNCHANGED
```

| 面数 | 值 |
| --- | --- |
| `HAND_BASE_TRIS` | **6,828** |
| `NAIL_ADDED_TRIS` | **0** |
| `TOTAL_RIGHT_HAND_TRIS` | **6,828** |
| 目标 | 8k–20k |
| 硬上限 | 30k |

当前略低于 8k。按§八「当前略低于 8k 不是必须为了数字补面，不得为了达到 8k 人为增加无意义几何」
→ **未补面**。

---

## 7. 证据（§九）

```
renders/STAGE4C_DORSAL.png         整手背侧（材质着色）
renders/STAGE4C_PALMAR.png         整手掌侧
renders/STAGE4C_FINGERTIPS.png     四指指甲特写（沿 nail normal 观看，plate 正对镜头）
renders/STAGE4C_THUMB_NAIL.png     拇指指甲特写
renders/STAGE4C_UV_LAYOUT.png      UV 布局（灰 = 主体，绿 = nail 区，橙 = 本次修复的 64 面）
```

未重做完整 8-view pack（按§九）。
渲染使用 `WORKBENCH + MATERIAL` 着色，nail 语义可见。
**临时/诊断图只写 `stage4c/_tmp/`**（腕部标记图、nail-only 诊断、探针 JSON）。

---

## 8. 产物（§十）

```
stage4c/RIGHT_HAND_ENGINEERING_STAGE4C_R1.blend            66fa4532…4bcdb6（2,009,735 B）
stage4c/STAGE4C_FINALIZATION_REPORT_R1.md                  (本报告)
stage4c/NAIL_AUDIT.json
stage4c/ORIGIN_AUDIT.json
stage4c/UV_AUDIT.json
stage4c/STAGE4C_STATUS.json
stage4c/STAGE4C_RUN.json                                   (完整日志)
stage4c/renders/*.png                                      (5 张)
stage4c/_tmp/                                              (探针 / 诊断 / scratch)
scripts/stage4c_probe.py / stage4c_wrist_probe.py / stage4c_finalize.py
scripts/stage4c_render.py / stage4c_audits.py
```

`STAGE4B_APPROVED_RSSF_BASELINE` 未被覆盖；Stage4B R1、R2 全部产物未改动。

---

## 9. 状态（§十一）

```
STAGE4C = PASS
CON_4_NAILS = PASS
CON_5_RSSF_REPOSE = UNCHANGED_PASS
CON_6_ORIGIN = PASS
CON_7_UV = PASS_AFTER_FIX

CANONICAL_HAND_POSE = RSSF
HAND_BASE_TOPOLOGY = UNCHANGED
CMC_DEFORMATION_FINAL = PENDING_STAGE6
TEMP_RSSF_RIG = REMOVED
PRODUCTION_RIG = NOT_STARTED
RIGHT_HAND_ENGINEERING_MASTER_CANDIDATE = READY_FOR_STAGE5_RIG
```

**待 Human Review 知晓**：`STAGE4B_WRIST_R_LOCATOR_DEFECT`（Stage-4B 骨架腕位错误；
本轮 origin 未采用该值，改用解剖学腕旋转中心）。

**已停止。未进入 Stage5。等待 Human Review。**
