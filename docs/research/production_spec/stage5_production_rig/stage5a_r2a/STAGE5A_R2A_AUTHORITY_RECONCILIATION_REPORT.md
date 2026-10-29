# STAGE5A_R2A — THUMB TIP AUTHORITY RECONCILIATION · REPORT R1

**状态** `STAGE5A_R2A = READY_FOR_HUMAN_REVIEW`（本报告不写 APPROVED / FINAL / READY_FOR_SKINNING / STAGE5B_STARTED）

**分支** `BRANCH_B`（THUMB_TIP_R_ONLY_REQUALIFICATION）
**新产物** `stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend`
sha256 `c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845`

---

## 一、本轮关闭的三件事

| # | 事项 | 结果 |
| --- | --- | --- |
| 1 | THUMB_TIP_R 权威统一 | **DONE** — 唯一 canonical semantic 已建立，R2 点不满足 → Branch B |
| 2 | INDEX_MCP 0.000 vs −1.5157 矛盾 | **DONE** — STATUS 为唯一权威；报告值为 STALE |
| 3 | STAGE5A_R1_OBJECT_FRAME_OFFSET | **DONE** — CLOSED_BY_R2_SUPERSESSION |

## 二、冻结输入（执行前后逐字节一致，已复核）

| 输入 | sha256 |
| --- | --- |
| Stage4C master | `fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7` |
| Stage5A R1 | `dd5f7265ea373579e9f77ecea2f74f0b2d0642a2bbb10795f1ddf5c17eb1486d` |
| Stage5A R2 | `615367d7fab3e75431fa7171e7e82f3a655c62e29ad7ddca5509b093e9f68c81` |

三者**均未被修改**；R1 / R2 未覆盖。

## 三、Canonical THUMB_TIP semantic（本轮正式建立）

```
THUMB_TIP_R = STABLE DISTAL-CAP SURFACE LANDMARK
```

它**不是**：最远单个 vertex / 任意 apex vertex / 指甲中心 / 骨头真实末端 / 为满足某个 mm threshold 调出的点。
它**是**：拇指远端帽 patch 上能稳定代表 fingertip centre 的表面 landmark。
`APEX_VERTEX_DISTANCE = DIAGNOSTIC_ONLY`；`5 mm gate` 与 `8 mm gate` 均**移除**；只存在一套 canonical 规则。

## 四、Distal-cap patch 定义（可复现、无手工点击、无顶点百分比）

1. **D\*** = 该指远端最靠外的表面顶点：取该指自有面片顶点中、位于批准远端关节（THUMB_IP / *_DIP）远侧、且距该关节最远者。
2. **g()** = 从 D\* 出发的 **mesh 测地距离**（表面图 Dijkstra）——全程**不依赖任何拟合轴向**。
3. **DISTAL_CAP_PATCH** = 包含最靠近 D\* 面片的连通 digit-owned 面片区域，限制为「最近顶点测地距离 ≤ 9.0 mm」的面片。
4. **CAP REPRESENTATIVE** = patch 的**面积加权质心投影回真实表面**；用 patch 的**测地 1-median** 交叉验证。

**9.0 mm 的来历（已声明并校准，非拍脑袋）**：在该半径下，patch 代表点能复现四根已批准指尖 landmark 到其各自 D\* 的 0.40–2.98 mm 关系（见 `FOUR_FINGER_TIP_REFERENCE.json`）。整轮**未使用**「top 5% / top 10% / 固定 N 个顶点」。
**敏感性**：7 / 9 / 12 mm 三档重跑，判定不变（R2 点始终不在帽内）。

**拇指帽实测**：4 面 / 9 顶点，面积 83.21 mm²，D\* = v2189 `[1.450257778, 0.018083785, 0.49866727]`（距 IP 36.675 mm），质心 `[1.452646017, 0.019510806, 0.49294889]`，帽内 0 个指甲面。
⚠ 拇指末端壳在 9 mm 测地半径内只有 **4 个 quad**，而四指各有 48–51 个 —— 拇指帽的网格密度约为四指的 1/12，这正是「单顶点 apex 会被量化数 mm」的根因。

## 五、四指自校准（只读，四指未动、未重新验收）

| 指 landmark 是否在自家帽 patch | 到帽代表点 (mm) | 到 D\* (mm) | 表面距 (mm) | DIP→TIP 内部 |
| --- | --- | --- | --- | --- |
| index ✓ | 4.2591 | 0.4704 | 0.2540 | 20/20 |
| middle ✓ | 1.1297 | 0.4377 | 0.2419 | 20/20 |
| ring ✓ | 1.5633 | 0.3983 | 0.2321 | 20/20 |
| little ✓ | 4.1552 | 2.9819 | 0.2135 | 20/20 |

**经验包络**：到帽代表点 1.13–4.26 mm；到 D\* 0.40–2.98 mm；四者全部在自家帽 patch 内。

## 六、R2 点判定 → Branch B

| 指标 | R2 点 | 四指包络 | 判定 |
| --- | --- | --- | --- |
| 在拇指帽 patch 内 | **否**（最近面 f385 ∉ {356,357,389,390}） | 四指全部为真 | FAIL |
| 到帽代表点 | **6.7540 mm** | 1.13–4.26 mm | 超出 |
| 到 D\* (v2189) | **12.6942 mm** | 0.40–2.98 mm | 超出约 4.3× |
| 测地距 D\* | 17.5928 mm | — | — |
| 表面距 | 0.0022 mm ✓ | 0.21–0.25 mm | OK |
| 归属 | THUMB ✓ | — | OK |
| IP→TIP 内部 | 20/20 ✓ | 1.0 | OK |

（对照：R1 点距 D\* 15.1139 mm —— 当初被判 NOT ACCEPTED；R2 点 12.6942 mm，改进有限。）

## 七、新 R2A THUMB_TIP

```
R2A THUMB_TIP_R.head = [1.45281744, 0.019802358, 0.493028343]   (= 拇指帽 patch 面积加权质心投影)
shift from R2        = 6.754 mm
到 D\* (v2189)        = 6.4267 mm
到帽质心             = 0.3474 mm
测地距 D\*           = 8.9385 mm
交叉验证             = 测地 1-median v1076 [1.452778339, 0.019757092, 0.493278891]（相距 0.347 mm）
```

**仅修改三个槽位**：`THUMB_TIP_R.head` / `THUMB_TIP_R.tail`（TIP_FRACTION 0.30 重算）/ `THUMB_IP_R.tail`。
`THUMB_IP_R.head` **0 漂移**；其余 20 个 joint head **0 漂移**（max = 0.0 mm）。
Mesh vertex delta 9.31e-07 mm；topology / UV / material delta = 0；无 parent / modifier / vertex groups。

**门禁**：`THUMB_TIP_ON_DISTAL_CAP_PATCH = PASS`；`THUMB_TIP_SURFACE_DISTANCE = PASS (0.0 mm)`；`THUMB_TIP_OWNER = PASS (THUMB)`；`THUMB_TIP_NOT_SINGLE_VERTEX_ARTIFACT = PASS`。

## 八、⚠ 必须由 Human Review 裁决的残差

```
THUMB_IP_TO_TIP_INTERIOR = 14/20   （t = 0.37 / 0.41 / 0.45 / 0.49 / 0.53 / 0.57 处出网格）
```

**根因**：冻结的 `THUMB_IP_R.head` 无法用一条完全位于网格内部的直线弦「看见」拇指远端帽——拇指远端指骨弯曲，**帽内每一点**都过不了严格 20/20 内部测试；帽内唯一 20/20 的采样点（v1074，距 IP 27.280 mm）距 D\* 仍有 12.71 mm，与被否决的 R2 点相当。
**对照**：四根已批准手指的 DIP→TIP 均为 20/20。
**未修复原因**：修复需要移动 `THUMB_IP_R.head`，本轮禁止（brief §18）。
**因此该门禁没有被静默放过**，保持 OPEN，交 Human Review。

链条其余指标：CMC→MCP 46.9437 mm（20/20）；MCP→IP 27.6992 mm（20/20，1.0156×）；IP→TIP 32.1468 mm（14/20，1.4616× ≤ 1.6 ✓）；折角 18.5929° ≤ 60° ✓。

## 九、INDEX_MCP 数字权威（独立复核）

从 R2 blend + 批准 T-01 authority 独立重算：

| 轴 | 值 |
| --- | --- |
| index MCP→TIP 弦（冻结 Stage4B landmark） | **−1.5157 mm** |
| index 近节指骨轴 | −0.000008 mm（构造上为 0，两轴夹角 19.26°） |
| T-01 zone | ±9.364 mm → **两者都 PASS，INDEX_MCP geometry PASS 不变** |

**唯一权威来源** = `stage5a_r2/STAGE5A_R2_STATUS.json → gates.INDEX_MCP_T01_AXIAL_REGION.measured_axial_mm = −1.5157 mm`。
R2 报告的 `AXIAL_DELTA_FROM_APPROVED_T01 = 0.000 mm` = **STALE**（它是「R2 点落在与其正交平面内」这一**构造陈述**，不是测量）。
详见 `STAGE5A_R2_INDEX_MCP_NUMERIC_ERRATA.md`（历史 R2 报告/JSON 均未改动）。

## 十、R1 object-frame provenance 关闭

`STAGE5A_R1_OBJECT_FRAME_OFFSET`：R1 把 world 坐标写进 armature local，同时 rig object 又放在 ASSET origin → 实际 rig 相对手整体偏移 **1448.359 mm**。
正式状态：**CLOSED_BY_R2_SUPERSESSION**。R1 blend 未修改、provenance 保留、不再作为可执行 production rig。
详见 `STAGE5A_R1_OBJECT_FRAME_ERRATA.md`。

## 十一、R2 object frame 复核（独立从 blend 读取）

`R2_OBJECT_FRAME = PASS`。rig object 与 hand mesh 的 matrix_world 完全一致（identity rotation + ASSET origin）；六个关键骨（WRIST_R / THUMB_CMC_R / THUMB_MCP_R / THUMB_IP_R / THUMB_TIP_R / INDEX_MCP_R）的 `matrix_world @ head_local` 与 joint table 逐一对齐，**最大偏差 2.33e-07 mm**。审计自行相乘，不复用任何 render-script 变换。→ `R2_OBJECT_FRAME_AUDIT.json`。

## 十二、禁止项核对

本轮**未做**：Stage5B / skin weight / vertex groups / mesh parenting / Armature modifier / IK / constraints / animation / GLB / Three.js / 左手 / Stage6 / retopo / CMC cage / T-01 topology / RSSF / nails / UV / 拇指网格改动 / `THUMB_IP_R.head`。

## 十三、产物清单

```
stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend   c4fafc56…c2845
stage5a_r2a/STAGE5A_R2A_AUTHORITY_RECONCILIATION_REPORT.md（本文件）
stage5a_r2a/STAGE5A_R2A_STATUS.json
stage5a_r2a/THUMB_DISTAL_CAP_AUDIT.json
stage5a_r2a/FOUR_FINGER_TIP_REFERENCE.json
stage5a_r2a/R2_OBJECT_FRAME_AUDIT.json
stage5a_r2a/STAGE5A_R2_INDEX_MCP_NUMERIC_ERRATA.md
stage5a_r2a/STAGE5A_R1_OBJECT_FRAME_ERRATA.md
stage5a_r2a/renders/STAGE5A_R2A_THUMB_DISTAL_CAP_AUTHORITY.png
stage5a_r2a/renders/STAGE5A_R2A_THUMB_TIP_SIDE.png
stage5a_r2a/renders/STAGE5A_R2A_THUMB_TIP_DORSAL.png
stage5a_r2a/scripts/*.py        （全部只读审计 + 唯一 R2A 构建）
stage5a_r2a/_tmp/*.json         （过程证据）
```

## 十四、停止点

到此停止。**不进入 Stage5B。** 等待 Human Review 对第八节残差（THUMB_IP_TO_TIP_INTERIOR）的裁决。
