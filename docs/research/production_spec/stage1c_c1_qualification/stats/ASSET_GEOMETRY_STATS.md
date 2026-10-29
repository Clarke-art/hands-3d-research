# ASSET_GEOMETRY_STATS · Blender Human Base Meshes v1.4.1 · `Hand  - Realistic`

> 阶段：`STAGE1C_C1_ASSET_QUALIFICATION`
> 测量工具：Blender **4.5.9 LTS**（`blender -b` 无头，只读打开官方母文件，**未保存任何修改**）
> 原始数据：`stats/pass1_inventory.json`、`stats/asset_geometry_stats_raw.json`、`stats/asset_analysis_pass3.json`、`stats/topology_rings.json`、`stats/topology_rings_multires_l1.json`
> 日期：2026-09-27

---

## 0. 关键发现（先给结论）

| 项 | 值 |
| --- | --- |
| **实际资产名称** | **`Hand  - Realistic`**（⚠ 官方命名中 `Hand` 与 `-` 之间为**两个空格**，不是笔误） |
| 资产所属目录（Asset Catalog） | `Human Base Meshes/Realistic`（UUID `fe53c157-b313-482f-b7a3-69e260232e6f`） |
| 是否为独立资产 | ✅ 是（`Hand - Stylized ` 为另一独立资产，同包内并列） |
| 手别 | **解剖学右手**（几何手别判定见 `GEOMETRY_ANATOMY_CHECK.md` §G-12） |
| 世界坐标朝向（本文件内的约定） | 手指指向 **−Z**；**背侧 = +Y**；**掌侧 = −Y**；**拇指侧（桡侧）= +X**；前臂断端 = **+Z** |

---

## 1. ASSET_GEOMETRY_STATS（基础层，未细分）

| 指标 | 实测值 |
| --- | --- |
| objects（该资产自身） | **1** 个 mesh 对象（无骨架、无子对象、无 parent） |
| vertices | **831** |
| edges | **1,649** |
| faces | **820** |
| triangles | **0** |
| quads | **819** |
| ngons | **1**（位于前臂断端的**平盖面**；见 §4） |
| non-manifold edges | **0** |
| loose geometry（孤立顶点 / 孤立边） | **0 / 0** |
| boundary edges | **0** → **封闭网格（closed volume）** |
| signed volume | **5.369e-4 m³** |
| surface area | **0.059182 m²** |
| UV layers | **1**（`UVMap`；无 UDIM 多块，仅单块） |
| materials | **0** |
| shape keys | **0** |
| modifiers | **Multires**（`total_levels = 1`） |
| armature | **无**（该资产无 armature modifier、无 vertex groups） |
| face maps | 无（`face_maps = null`） |
| dimensions（本地 = 世界，scale = 1） | **0.151189 × 0.065055 × 0.282857 m**（15.1 × 6.5 × 28.3 cm） |
| bounding box（世界） | min `(1.3484, −0.0191, 0.1490)` → max `(1.4986, 0.0456, 0.4316)` |
| world scale | `(1.0, 1.0, 1.0)`（**未缩放，米制**） |
| origin（object origin，世界） | `(1.404782, 0.011328, 0.353646)` —— 位于**前臂中段**，**不在腕关节旋转中心**（与 `CANONICAL_HAND_POSE_SPEC_R1` §2.2 "原点建议置于腕关节旋转中心" 不一致，属需在 Stage 4 修正的项，非缺陷） |
| symmetry（自身镜像对称） | **无**：跨 X 面匹配率 **0.0**、跨 Y 面 **0.0024**、跨 Z 面 **0.0**（单只人手在自然姿态下本就不自对称，此结果符合预期） |
| 左右成对资产 | 包内**只有这一只** realistic hand（无左/右手成对资产）→ 左手必须由镜像得到（`LR-01`/`LR-02` 不受影响） |

### 1.1 multires 层级（base level 与最高现有 level，分别记录）

| level | faces | verts | corners |
| --- | --- | --- | --- |
| **base（未细分）** | **820** | **831** | 3,280 |
| **1（最高现有）** | **3,298** | **3,300** | 13,192 |

> ⚠ 与选路阶段网页描述的差异（**以实际文件为准**）：
> 网页/文档曾称 realistic 资产带"multi-resolution details"。**实际文件核验**：该 hand 资产的 Multires 修饰器
> **只有 1 级**（`total_levels = 1`），并非多级细节堆叠。因此**不能假设"高模细节已存在"**；
> 母版的表面细节需在 Stage 4 由人工造型提供。
>
> 但 **1 级 multires 对拓扑密度有实质意义**：它把指关节处的环线密度**翻倍**（见 `TOPOLOGY_CHECK.md` §T-01）。

---

## 2. 尺度核验（现实尺度对照）

| 区段 | 实测（世界 z 方向） | 长度 |
| --- | --- | --- |
| 中指指尖（z 最小） | z = 0.1490 | — |
| 腕部最窄处（wrist） | z ≈ 0.335 ~ 0.345（截面单连通、宽度最小） | — |
| 前臂断端（z 最大） | z = 0.4316 | — |
| **手（腕 → 中指尖）** | 0.335 → 0.149 | **≈ 0.186 m（18.6 cm）** |
| **前臂（腕 → 断端）** | 0.335 → 0.4316 | **≈ 0.097 m（9.7 cm）** |
| 手 + 前臂总长 | — | 0.283 m（28.3 cm） |

> 18.6 cm 的腕—中指尖长度落在**成人**区间（成年男性均值约 19 cm、女性约 17.5 cm）。
> → **尺度上属成人手**，非儿童手比例（对 `G-15` 有利）。**scale = 1.0，无需单位换算。**

---

## 3. 各指实测（来自 slice-blob 跟踪，`stats/asset_analysis_pass3.json`）

| 指 | 指尖 z | 与手掌合流处 z（≈MCP 区） | 指长（沿 z） | 指尖 x（均值） |
| --- | --- | --- | --- | --- |
| THUMB（拇指） | 0.241 | 0.292（CMC 区） | 0.0775 m | 1.485 |
| INDEX（食指） | 0.164 | 0.240 | 0.0837 m | 1.457 |
| MIDDLE（中指） | **0.149（最长）** | 0.230 | 0.0870 m | 1.4225 |
| RING（无名指） | 0.160 | 0.231 | 0.0768 m | 1.3925 |
| LITTLE（小指） | **0.188（最短）** | 0.258 | 0.0779 m | 1.3575 |

**指长排序：中指 > 食指 > 小指 ≈ 无名指 > 拇指**（无名指与小指按指尖 z 计基本并列，按 MCP→指尖计无名指略长）
→ 与解剖学常规一致（中指最长、小指最短、拇指最短）。

---

## 4. 前臂断端结构（影响 Stage 4 处理，记录事实）

- 前臂在 z = 0.4316 处**平切收口**，切面由**唯一的一个 ngon** 封闭（即 §1 中的 1 个 ngon）。
- 该 ngon 位于**完全不变形的平板区域**（前臂断端），**不在任何关节活动区**。
  → 对 `T-05`（四边形为主）与 `T-08`（无非流形/孤立顶点/内部面）**不构成问题**；
  → 但它意味着**前臂不是天然"断口"而是封闭盖面**：若后续需要把前臂延长/接续，需先处理该盖面。
  → 本资产**不自带任何前臂延长几何**（判定见 `RSSF_POSE_DELTA_AND_FOREARM.md`）。

---

## 5. 证据文件索引

| 内容 | 文件 |
| --- | --- |
| 包内对象/资产元数据完整清点 | `stats/pass1_inventory.json` |
| 基础层几何统计 + 对称性 + multires 逐级 | `stats/asset_geometry_stats_raw.json` |
| 切片/指追踪原始输出 | `stats/asset_analysis_pass3.json` |
| 环线（edge loop）枚举（base 层） | `stats/topology_rings.json`（实际写入者为 pass9） |
| 环线（edge loop）枚举（multires L1） | `stats/topology_rings_multires_l1.json` |
| 8 视角证据渲染 | `renders/EVIDENCE_*.png` |
| 线框证据（含关节近景） | `wireframes/WIREFRAME_*.png` |
| 执行脚本（可复现） | `scripts/pass1_inventory.py` … `scripts/pass12_knuckles.py`、`scripts/render_one.py`、`scripts/render_all.sh` |

**状态：`ASSET_GEOMETRY_STATS = COMPLETE`**
