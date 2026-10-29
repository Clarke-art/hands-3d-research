# STAGE5A_PRODUCTION_RIG_SKELETON_R1

**任务**：建立正式 Production Rig 的骨架、层级、关节位置与局部轴系（**不含 Skin Weight**）
**输入（冻结，只读）**：`production_spec/stage4_blender/stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend`
`sha256 fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7` ✓（执行前后逐字节一致）
**输出（新文件，master 未被覆盖）**：`stage5a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R1.blend`
`sha256 dd5f7265ea373579e9f77ecea2f74f0b2d0642a2bbb10795f1ddf5c17eb1486d`
**运行时**：`D:\Blender\blender.exe`（Blender 5.1.2）

---

## 0. 结论：FAIL CLOSED

```
STAGE5A                   = FAIL_CLOSED
PRODUCTION_RIG_SKELETON   = BLOCKED_ON_JOINT_LANDMARK_CORRECTION
PRODUCTION_SKIN_WEIGHT    = NOT_STARTED
RIGHT_HAND_PRODUCTION_RIG = CANDIDATE_NON_CONFORMING_EVIDENCE_ONLY
STAGE5B                   = NOT_STARTED

自动门禁 24 / 25 PASS；唯一 FAIL = JOINT_REGION_VALIDATION
```

**Blocker（按 brief §六「FAIL CLOSED 报告具体 joint，不要静默修正」处理，未做任何修正）**：

| joint | 实测 | 判定 |
| --- | --- | --- |
| `THUMB_MCP_R` | 位于拇指**网格外部**（射线奇偶 0/64），离拇指自身表面 2.446 mm，离自身最近顶点 3.082 mm | **FAIL** |
| `INDEX_MCP_R` | 位于**网格外部**（射线奇偶 0/64），离自身表面仅 0.260 mm（其余三指 MCP 为 4.75–6.14 mm 内部余量） | **FAIL** |

**非阻断观察（已记录、未修改）**：
- `THUMB_CMC_R` 在网格内部但**表面余量仅 0.174 mm** —— 它落在 Stage-4A 已批准的 CMC **表面**笼锚点上，不是深处的关节中心。
- `THUMB_TIP_R` 尖端标志点距拇指顶点 **12.078 mm**（四指对应值 0.47–4.67 mm）。

**本轮未写** APPROVED / FINAL / STAGE5B_STARTED / READY_FOR_SKINNING。

---

## 1. 冻结输入验证

```
master sha256 (执行前) = fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7
master sha256 (执行后) = fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7
MESH_VERTEX_DELTA = 0   MESH_TOPOLOGY_DELTA = 0   UV_DELTA = 0   MATERIAL_ASSIGNMENT_DELTA = 0
mesh topology signature（artifact）= 5a39668418eea1716a0fd9bc20b3d0aeda67e6a49a343b74eb3e17c339f90c1d
V = 3416   E = 6828   F = 3414   TRIS = 6828   NAIL_BED = 124 面 / HAND_SKIN = 3290 面
```

Stage5A 全程**只读** master，产物另存新路径；master 未被覆盖。

---

## 2. Binding wrist constraint 执行情况

**采用 OPTION A**（`USE_APPROVED_STAGE4C_R2_WRIST_ORIGIN`），并**同时执行 OPTION B 复核**：

```
WRIST_R head = [1.408704638, 0.022395039, 0.335847497]   ← 批准 origin，逐位一致
|WRIST_R head − Stage4B WRIST_R head| = 60.3302 mm        ← 旧 TEMP rig 位置，未使用
OPTION B 复验（radius-limited INTERIOR minimum locator，按 stage4c_finalize.py 逐式重实现，
              在冻结 master 上重跑）
  reverified_origin = [1.408704638, 0.022395039, 0.335847497]
  drift = 0.000000000 mm                                  ← 无可测漂移，未触发 FAIL CLOSED
```

因此 `WRIST_OPTION_B_REVERIFICATION = PASS`、`WRIST_HEAD_MATCH_APPROVED_ORIGIN = PASS`、
`OLD_STAGE4B_WRIST_NOT_USED = PASS`。

---

## 3. WRIST_R bone 定义与 PALM_REFERENCE 推导

```
WRIST_R head = 批准 origin（腕旋转中心，Stage4C R2）
WRIST_R tail = PALM_REFERENCE = 四指 MCP 关节中心（INDEX/MIDDLE/RING/LITTLE）的形心
             = [1.405533195, 0.010078979, 0.478082418]
WRIST_R length = 142.8024 mm
  （Stage-4B TEMP rig 的 WRIST_R 长度 = 201.0522 mm，未沿用其 head）
```

- tail **在掌部内部**、不在指根外部、不进拇指列、不落在前臂截断面。
- tail 与 Stage-4B 的 WRIST_R tail **完全相同**（差值 0.000e+00 m）——即 Stage-4B 的 tail 定义
  （四 MCP 形心）本身就是合理的，本轮**只修正 head**。

⚠ **需 Human Review 判断的一点（已如实上报，未自行处理）**：
`WRIST_R length = 142.80 mm`，而 Stage-4C 的 origin 审计文件把同类"腕→掌"骨长的解剖期望写为
**~65–90 mm**。批准的 origin 虽比 Stage-4B 的错误位置（201 mm）好得多，但仍显著长于该期望值。
同源观察：`wrist → mean MCP = 142.80 mm`、`wrist → 拇指 CMC 锚点 = 65.93 mm`、
`wrist → 中指尖端 = 198.44 mm`（掌/手比 0.72，解剖参考约 0.55）。
**本轮未移动 wrist**（binding 约束禁止自行改腕位）；若需改动，属 Human Review 决策。

---

## 4. 21 骨表（Production Rig）

bone-local 约定：`LOCAL_Y = head→tail`、`LOCAL_Z = dorsal-like`、`LOCAL_X = Y × Z`（lateral / 屈伸轴）。

| bone | head (m) | tail (m) | length (mm) | parent | connect | use_deform |
| --- | --- | --- | --- | --- | --- | --- |
| WRIST_R | 1.408705, 0.022395, 0.335847 | 1.405533, 0.010079, 0.478082 | 142.802 | — | — | true |
| THUMB_CMC_R | 1.448804, 0.011108, 0.393759 | 1.443062, 0.007415, 0.435889 | 42.680 | WRIST_R | false | true |
| THUMB_MCP_R | 1.443062, 0.007415, 0.435889 | 1.450861, 0.006127, 0.464001 | 29.202 | THUMB_CMC_R | true | true |
| THUMB_IP_R | 1.450861, 0.006127, 0.464001 | 1.451316, 0.010537, 0.485615 | 22.064 | THUMB_MCP_R | true | true |
| THUMB_TIP_R | 1.451316, 0.010537, 0.485615 | 1.451453, 0.011861, 0.492099 | 6.619 | THUMB_IP_R | true | **false** |
| INDEX_MCP_R | 1.445879, 0.013830, 0.479620 | 1.455229, −0.003585, 0.503314 | 30.856 | WRIST_R | false | true |
| INDEX_PIP_R | 1.455229, −0.003585, 0.503314 | 1.459105, −0.022121, 0.510946 | 20.417 | INDEX_MCP_R | true | true |
| INDEX_DIP_R | 1.459105, −0.022121, 0.510946 | 1.460983, −0.037063, 0.514026 | 15.371 | INDEX_PIP_R | true | true |
| INDEX_TIP_R | 1.460983, −0.037063, 0.514026 | 1.461546, −0.041546, 0.514949 | 4.611 | INDEX_DIP_R | true | **false** |
| MIDDLE_MCP_R | 1.416905, 0.013840, 0.482859 | 1.421529, −0.005951, 0.510629 | 34.413 | WRIST_R | false | true |
| MIDDLE_PIP_R | 1.421529, −0.005951, 0.510629 | 1.424311, −0.029810, 0.519842 | 25.727 | MIDDLE_MCP_R | true | true |
| MIDDLE_DIP_R | 1.424311, −0.029810, 0.519842 | 1.425355, −0.047430, 0.520845 | 17.679 | MIDDLE_PIP_R | true | true |
| MIDDLE_TIP_R | 1.425355, −0.047430, 0.520845 | 1.425668, −0.052716, 0.521146 | 5.304 | MIDDLE_DIP_R | true | **false** |
| RING_MCP_R | 1.394244, 0.010574, 0.479239 | 1.392641, −0.009294, 0.504846 | 32.450 | WRIST_R | false | true |
| RING_PIP_R | 1.392641, −0.009294, 0.504846 | 1.394462, −0.031272, 0.512574 | 23.369 | RING_MCP_R | true | true |
| RING_DIP_R | 1.394462, −0.031272, 0.512574 | 1.396310, −0.047095, 0.512450 | 15.931 | RING_PIP_R | true | true |
| RING_TIP_R | 1.396310, −0.047095, 0.512450 | 1.396865, −0.051842, 0.512412 | 4.779 | RING_DIP_R | true | **false** |
| LITTLE_MCP_R | 1.365105, 0.002072, 0.470611 | 1.359720, −0.012156, 0.489131 | 23.968 | WRIST_R | false | true |
| LITTLE_PIP_R | 1.359720, −0.012156, 0.489131 | 1.359665, −0.027045, 0.495908 | 16.359 | LITTLE_MCP_R | true | true |
| LITTLE_DIP_R | 1.359665, −0.027045, 0.495908 | 1.359528, −0.038467, 0.497987 | 11.611 | LITTLE_PIP_R | true | true |
| LITTLE_TIP_R | 1.359528, −0.038467, 0.497987 | 1.359487, −0.041894, 0.498610 | 3.483 | LITTLE_DIP_R | true | **false** |

```
PRODUCTION_BONE_COUNT = 21     BONE_NAME_SET_EXACT = PASS     HIERARCHY_EXACT = PASS
TIP_HELPER_COUNT = 5           TIP_USE_DEFORM_FALSE = PASS     DEFORM_BONE_COUNT = 16
JOINT_CHAIN_CONTINUITY = PASS（每链 head/tail 严格重合，max gap < 1e-9 mm）
无 control / IK / pole / mechanism / palm helper / twist / mirror bone，无左手骨架
WRIST_R → 5 个 digit root：parented but NOT connected（未为迎合 Blender 连接规则而移动关节中心）
```

### TIP helper 规则（确定性，已记录）

```
TIP_FRACTION = 0.30
TIP.tail = TIP.head + normalise(远端指骨方向) × 0.30 × (远端指骨长度)
```
由于 `TIP.head == 远端指骨.tail`，TIP helper 与远端指骨**严格共线**（角度 0.00°），
不会突然折向；且 `use_deform = false`。

---

## 5. 局部轴 / roll 审计

**确定性规则（不使用 Blender 默认 roll）**：`edit_bone.align_roll(dorsal_reference)`。

per-digit dorsal reference（来自**当前批准的** RSSF 网格，非全局猜测）：

| 部位 | dorsal reference（world） | 来源 |
| --- | --- | --- |
| thumb | (0.631289, 0.775319, −0.018839) | 该指自身 nail plane（NAIL_AUDIT_R2 批准甲面集的面法向均值） |
| index | (0.283415, 0.025267, 0.958664) | 同上 |
| middle | (−0.030993, 0.004625, 0.999509) | 同上 |
| ring | (−0.000005, −0.038838, 0.999246) | 同上 |
| little | (−0.331073, 0.054303, 0.942041) | 同上 |
| wrist | (−0.153714, 0.984849, 0.080280) | **掌平面法向**（腕 origin + 四 MCP 中心张成的平面；符号由"屈曲手指体在掌侧"确定） |

> 说明：拇指**未**使用任何全局 DORSAL，只用其自身甲面；腕部**不能**用四指 dorsal 均值
> ——那些方向与腕骨轴（腕→掌）几乎平行（|dot| ≈ 0.995），`align_roll` 会退化、roll 不稳定。
> 实测：改用掌平面法向后，wrist→CHAIN 的局部 +Z 夹角由 82.7° 降到 47.3°，整链连续。

```
BONE_LOCAL_FRAME_ORTHONORMAL = PASS
  每骨 |X| = |Y| = |Z| = 1（1e-7 内）、X·Y = Y·Z = X·Z = 0、X = Y × Z（右手系）
BONE_ROLL_CONTINUITY = PASS（max 47.345 deg，容差 60 deg）
  逐链局部 +Z 相邻夹角：
    thumb  47.35 → 16.33 → 3.26 → 0.02
    index  32.80 → 31.00 → 11.25 → 0.00
    middle 32.25 → 32.90 → 17.63 → 0.00
    ring   35.53 → 33.24 → 19.77 → 0.02
    little 29.30 → 30.45 → 13.20 → 0.00
BONE_ROLL_180_FLIPS = 0
BONE_LENGTH_NONZERO = PASS
```

⚠ 注意：`EditBone.roll` 的**原始数值**（−172°…+170°）在本资产上不具可比性（它取决于骨方向与
Blender roll 参考的关系）；**roll 连续性必须看局部 +Z 夹角**，即上表。

---

## 6. Joint region validation（唯一 FAIL 门）

**判定标准（先声明后执行）**：

1. **关节标志点**（16 个非 TIP 骨）必须**严格位于网格内部** —— 判据 = **射线奇偶**
   （64 条准随机方向的全网格穿透计数；黄金标准，不依赖法向也不依赖面归属）。
2. **指尖标志点**（5 个 TIP helper head）按定义就是体表尖端点 ⇒ 判据 = 到**本指**表面
   ≤ 1.0 mm 且距**本指**顶点 ≤ 15 mm。
3. 8 个四指 PIP/DIP 关节另加**轴向交叉验证**：与 Stage-4A 已批准的 T-01 关节层位比较，
   |Δ| ≤ 该关节的 T-01 zone 半宽。
4. 腕：批准 origin + Option B 复验（drift = 0）。
5. 拇指 CMC：批准的 CMC deformation cage 区域（锚点顶点 794，胶囊盘半径 R = 20 mm）。

| joint | 判定 | 射线奇偶 | 至自身表面 (mm) | 至自身顶点 (mm) | T-01 轴向 Δ (mm) | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| WRIST_R | PASS | 64/64 | 15.768 | — | — | 批准 origin；Option B drift 0 |
| THUMB_CMC_R | PASS | 64/64 | 0.174 | — | — | ⚠ 表面余量 0.174 mm（见 observation） |
| **THUMB_MCP_R** | **FAIL** | **0/64** | 2.446 | 3.082 | 3.267 | **在网格外部** |
| THUMB_IP_R | PASS | 64/64 | 6.217 | — | 4.315 | |
| THUMB_TIP_R | PASS | 64/64 | 0.112 | 0.188 | — | ⚠ 距顶点 12.078 mm |
| **INDEX_MCP_R** | **FAIL** | **0/64** | 0.260 | 1.863 | 0.000 | **在网格外部**（其余三指 MCP 有 4.75–6.14 mm 内部余量） |
| INDEX_PIP_R | PASS | 64/64 | 6.103 | — | −1.360 | |
| INDEX_DIP_R | PASS | 64/64 | 5.068 | — | −1.920 | |
| INDEX_TIP_R | PASS | 0/64 | 0.232 | 0.470 | — | 指尖点（定义上在表面） |
| MIDDLE_MCP_R | PASS | 64/64 | 6.137 | — | 0.000 | |
| MIDDLE_PIP_R | PASS | 64/64 | 6.625 | — | −3.637 | |
| MIDDLE_DIP_R | PASS | 64/64 | 5.966 | — | −2.218 | |
| MIDDLE_TIP_R | PASS | 0/64 | 0.242 | 0.439 | — | |
| RING_MCP_R | PASS | 64/64 | 5.163 | — | 0.000 | |
| RING_PIP_R | PASS | 64/64 | 6.212 | — | −2.584 | |
| RING_DIP_R | PASS | 64/64 | 5.086 | — | −1.548 | |
| RING_TIP_R | PASS | 0/64 | 0.232 | 0.398 | — | |
| LITTLE_MCP_R | PASS | 64/64 | 4.750 | — | 0.000 | |
| LITTLE_PIP_R | PASS | 64/64 | 5.132 | — | −1.334 | |
| LITTLE_DIP_R | PASS | 64/64 | 4.001 | — | −1.445 | |
| LITTLE_TIP_R | PASS | 0/64 | 0.214 | 0.476 | — | |

**结论**：Stage-4B R2 的候选关节帧对**四指 12 个关节 + THUMB_IP + WRIST** 是合格的
（全部在网格内、全部落在批准 T-01 层位内、轴向偏差 ≤ 3.64 mm），
但 **THUMB_MCP 与 INDEX_MCP 不合格**。

```
JOINT_REGION_VALIDATION = FAIL      failures = [THUMB_MCP_R, INDEX_MCP_R]
CMC_JOINT_IN_APPROVED_REGION = PASS（奇偶 64/64，距笼锚点 8.598 mm ≤ R 20 mm）
```

### 关于 T-01 环质心做法的更正（方法与工具层面）

本轮**放弃**了用 `T01_FINAL_AUDIT.json` 的 `_verts` 计算关节环质心的做法：
该字段是被截断的环行走前缀（例：31 边环只记录 7–11 个顶点），据此算出的"环质心"是**一段弧**
的质心而非整环质心，会把 THUMB_MCP 的径向偏差伪造成 11.8 mm。
已改用**批准 T-01 的轴向层位**（`joint_axial_center_mm` / `zone_half_width_mm`，完整且权威）
做交叉验证，并以**射线奇偶**做内外部裁决。

---

## 7. 自动门禁汇总（24 PASS / 1 FAIL）

```
PASS  PRODUCTION_BONE_COUNT = 21          PASS  BONE_NAME_SET_EXACT
PASS  HIERARCHY_EXACT                     PASS  TIP_HELPER_COUNT = 5
PASS  TIP_USE_DEFORM_FALSE                PASS  DEFORM_BONE_COUNT = 16
PASS  WRIST_HEAD_MATCH_APPROVED_ORIGIN    PASS  OLD_STAGE4B_WRIST_NOT_USED (60.330 mm)
PASS  JOINT_CHAIN_CONTINUITY              FAIL  JOINT_REGION_VALIDATION
PASS  CMC_JOINT_IN_APPROVED_REGION        PASS  BONE_LENGTH_NONZERO
PASS  BONE_LOCAL_FRAME_ORTHONORMAL        PASS  BONE_ROLL_CONTINUITY (max 47.345°)
PASS  BONE_ROLL_180_FLIPS = 0             PASS  NEGATIVE_SCALE = 0
PASS  MESH_VERTEX_DELTA = 0               PASS  MESH_TOPOLOGY_DELTA = 0
PASS  UV_DELTA = 0                        PASS  MATERIAL_ASSIGNMENT_DELTA = 0
PASS  MESH_PARENT = NONE                  PASS  ARMATURE_MODIFIER = NONE
PASS  VERTEX_GROUPS = NONE                PASS  PRODUCTION_SKIN_WEIGHT = NOT_STARTED
PASS  WRIST_OPTION_B_REVERIFICATION (drift 0.000000000 mm)
```

---

## 8. Rig object transform

```
name            = RIGHT_HAND_PRODUCTION_RIG
data            = RIGHT_HAND_PRODUCTION_RIG_DATA（display_type = OCTAHEDRAL, show_names = True）
location        = [1.408704638, 0.022395039, 0.335847497]   ← 与 hand mesh 相同的 object frame
rotation_euler  = [0, 0, 0]
scale           = [1, 1, 1]
NEGATIVE_SCALE  = 0

Stage5A 未 parent mesh / 未加 Armature modifier / 未建 vertex group / 未做任何 skin weight
```

---

## 9. 正式 Human Review 证据图（9 张）

```
stage5a/renders/STAGE5A_RIG_DORSAL.png                  mesh 半透明 + 21 骨，颜色按指区分
stage5a/renders/STAGE5A_RIG_PALMAR.png
stage5a/renders/STAGE5A_RIG_RADIAL.png
stage5a/renders/STAGE5A_RIG_ULNAR.png
stage5a/renders/STAGE5A_RIG_DORSAL_OBLIQUE.png
stage5a/renders/STAGE5A_RIG_WRIST_CLOSEUP.png           同时显示：Production WRIST_R（蓝球 + 蓝条）
                                                        + 批准 Stage4C wrist 参考平面（蓝条）
                                                        + 前臂截断面（红条）
                                                        + LEGACY_STAGE4B_WRIST_R（黑球，标注 DO NOT USE）
stage5a/renders/STAGE5A_RIG_THUMB_CMC_CLOSEUP.png        CMC 关节 + 批准笼区域（锚点顶点 794 + R = 15.64 mm 欧氏 cage）
stage5a/renders/STAGE5A_RIG_FINGERS_JOINT_CLOSEUP.png    MCP/PIP/DIP 关节球与骨，按指标注
stage5a/renders/STAGE5A_RIG_LABELLED.png                 21 骨名称双列排布，全部可核对
```

临时文件仅写 `stage5a/_tmp/`；正式图仅写 `stage5a/renders/`；全程**未使用** glob / recursive /
prefix wildcard 删除，未移动既有文件。

---

## 10. 产物清单

```
stage5a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R1.blend
stage5a/STAGE5A_PRODUCTION_RIG_REPORT_R1.md          （本报告）
stage5a/STAGE5A_STATUS.json                          机读状态 + 全部门禁 + mesh 签名
stage5a/STAGE5A_RIG_AUDIT.json                       同内容（审计入口）
stage5a/STAGE5A_PRODUCTION_JOINT_TABLE.json          21 关节表（含 authority / validation_method / status）
stage5a/STAGE5A_BONE_FRAME_AUDIT.json                逐骨 head/tail/length/roll/local XYZ + 轴向/roll 门禁
stage5a/renders/*.png                                9 张正式图
stage5a/_tmp/S5A_INPUT_FORENSICS.json                只读取证：解剖比例 / 截面剖面 / 关节初判
stage5a/_tmp/S5A_JOINT_FRAME_PROVENANCE.json         冻结 Stage-4B provenance 的 rest vs posed 对照
stage5a/_tmp/S5A_OWNERSHIP_DIAG.json                 ownership 基准的关节局部验证
stage5a/_tmp/S5A_THUMB_SEARCH.json                   拇指 CMC/MCP/TIP 严格归属复核
stage5a/_tmp/S5A_PARITY.json                         21 点射线奇偶裁决
stage5a/_tmp/S5A_GEOMETRY_DIAG.json                  T-01 环半径与局部表面诊断
stage5a/_tmp/S5A_WRIST_REVERIFY.json                 Option B 腕复验明细
stage5a/_tmp/S5A_BUILD_LOG.json                      构建日志（骨表 / dorsal / sha256）
stage5a/scripts/stage5a_{probe,probe_frame_provenance,diag,diag2,diag3,diag4_parity,build,audit,render}.py
```

---

## 11. 供 Human Review 裁决的三点

1. **THUMB_MCP_R / INDEX_MCP_R 不合格**（在网格外部）。需要 Human 决定：
   (a) 授权一次**关节中心修正**（窄范围、只改这两个 joint，并重跑本审计），或
   (b) 退回 Stage-4B 关节帧来源另作处理。
   **本轮未自行修正，按 brief 停在 FAIL CLOSED。**
2. **THUMB_CMC_R 表面余量仅 0.174 mm** —— 它落在 Stage-4A 批准的 CMC **表面**笼锚点上。
   按 brief 的 CMC 规则这属"位于已批准 cage 有效区域"⇒ PASS；但作为 Production Rig 的
   CMC 关节中心是否足够深，请 Human 判断。
3. **WRIST_R length = 142.80 mm** vs Stage-4C 自己引用的解剖期望 ~65–90 mm。
   本轮**未移动 wrist**（binding 约束）。若需变更，属 Human 决策。

```
STAGE5A = FAIL_CLOSED          STAGE5B = NOT_STARTED
RIGHT_HAND_PRODUCTION_RIG = CANDIDATE_NON_CONFORMING_EVIDENCE_ONLY

已停止。未创建 Production Skin Weight，未进入 Stage 5B。
```
