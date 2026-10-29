# STAGE6A — Deformation Harness 与隔离屈曲验证 · 阶段报告 R1

- **阶段**：`STAGE6A_DEFORMATION_HARNESS_AND_ISOLATED_FLEX_VALIDATION_R1`
- **日期**：2026-09-30（GMT+8）
- **运行环境**：Blender 5.1.2（`D:\Blender\blender.exe`），纯本地 EEVEE，无外部服务
- **输入（唯一冻结 Production Skin Master）**：`stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend`
  SHA-256 `c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6` — 执行前后**未变** ✅
- **新增 harness（TEST HARNESS COPY，非新 Production Master）**：`stage6a/RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend`
  SHA-256 `8f223c979362a8c3414b58e2467c7cda2da60f993245cc95b2a38d76c718d3ef`
- **状态结论**：`STAGE6A = READY_FOR_HUMAN_REVIEW`；`ISOLATED_FLEX_DEFORMATION = PASS_PENDING_HUMAN_REVIEW`；`STAGE6B = NOT_STARTED`

---

## 一、输入门（全部 PASS）

| 项 | 值 |
|---|---|
| Stage5B master 实际 hash | `c68e415a…c0ea6` = 冻结台账 ✅ |
| Stage5B freeze receipt | `STAGE5B = FINAL_APPROVED` ／ `PRODUCTION_SKIN_WEIGHT_STATIC = FINAL_APPROVED` ／ `STAGE5B_FREEZE = PASS` ／ `STAGE6 = READY_TO_BEGIN` ✅ |
| bone 总数 | **21**（5 TIP helper `use_deform=false` ＋ 16 deform） |
| deform vertex group | **16**，且 **无任何 `*_TIP_R` 权重组** |
| Armature modifier | `PRODUCTION_ARMATURE` → `RIGHT_HAND_PRODUCTION_RIG` ✅ |
| parent binding | `RIGHT_HAND_PRODUCTION_RIG`，world transform delta = **0.0 mm** ✅ |
| topo / UV / material | 与冻结参考**逐项相同**（V/E/F/TRIS = 3416/6828/3414/6828） |
| zero-pose baseline | max **5.967e-05 mm**（< 1e-4 硬门） ✅ |

任一不符即 FAIL CLOSED；本轮**无触发**。Stage5B master **未被覆盖**。

---

## 二、Stage6A 的性质与范围

```
STAGE6A = TECHNICAL DEFORMATION QUALIFICATION
        ≠ STANDARD_HAND 教学姿态定义
CANONICAL_HAND_POSE = RSSF（不变）
```

15° / 30° / 45° 为 **DIAGNOSTIC / STRESS-TEST 角度**，**不得**被引用为钢琴标准手型参数或
STANDARD_HAND canonical angles。

**本轮覆盖**：四指 12 个关节 ＋ `THUMB_MCP_R` ＋ `THUMB_IP_R` = **14 关节 × 3 角度 = 42 个正式 case**。
**本轮不覆盖**（留给 Stage6B / 后续）：`THUMB_CMC_R` opposition、完整 thumb opposition、
钢琴按键动作、多关节完整演奏动作。
`THUMB_CMC_R` 与 `WRIST_R` 本轮 **LOCKED_AT_BIND_POSE**（全程 0 rotation）。

---

## 三、测试装置（harness）

- 由 Stage5B master 复制；**仅新增** `STAGE6A_DIAGNOSTIC` collection（4 台测试相机 ＋ 3 盏 sun 灯）。
- 未改：joint position、bone head/tail、roll、hierarchy、bone count、vertex group、skin weight、
  parent、Armature modifier、mesh geometry、topology、UV、material、nail face、CMC cage、RSSF bind geometry。
- 允许动作仅限 `Pose Bone rotation`（bone local X）＋ 测试相机/灯光/diagnostic collection/测试脚本。
- **保存状态**：`HARNESS_FINAL_POSE = ZERO / RSSF`；重开校验所有 pose bone = identity
  （`non_identity_bones_after_reopen = []`），post-save zero delta max = **5.967e-05 mm**。
- 渲染全程未回写任何 `.blend`。

---

## 四、Flexion axis sign 自动资格确认（先 probe，后使用）

轴向权威：Stage5A 冻结约定 —— `LOCAL_Y` = 骨纵向、`LOCAL_Z` = dorsal-like、**`LOCAL_X` = flexion/extension 轴**。
本轮 flexion **只绕 bone local X**，未使用任何 global XYZ 猜轴。

PALMAR 方向 = `−(bone local Z)`（世界系），并与 canonical `+Y = DORSAL` 交叉校验：

| digit | bone local Z · global +Y | 与 canonical 一致 |
|---|---|---|
| INDEX | 0.6845 | ✅ |
| MIDDLE | 0.7738 | ✅ |
| RING | 0.7861 | ✅ |
| LITTLE | 0.8017 | ✅ |
| THUMB | 0.7697 | ✅ |

±5° 只读 probe（取该关节 distal tip landmark 的位移在 PALMAR 上的投影）：

| joint | +5° palmar (mm) | −5° palmar (mm) | 选定 FLEXION_SIGN |
|---|---|---|---|
| INDEX_MCP | −5.532493 | **+5.417445** | **−1** |
| INDEX_PIP | −2.825829 | **+2.710473** | **−1** |
| INDEX_DIP | −1.152840 | **+1.092133** | **−1** |
| MIDDLE_MCP | −5.944252 | **+5.739081** | **−1** |
| MIDDLE_PIP | −2.968927 | **+2.762775** | **−1** |
| MIDDLE_DIP | −1.035022 | **+0.933871** | **−1** |
| RING_MCP | −5.446843 | **+5.258104** | **−1** |
| RING_PIP | −2.641347 | **+2.452091** | **−1** |
| RING_DIP | −0.890569 | **+0.796246** | **−1** |
| LITTLE_MCP | −4.112177 | **+3.988650** | **−1** |
| LITTLE_PIP | −2.021354 | **+1.898277** | **−1** |
| LITTLE_DIP | −0.764198 | **+0.703351** | **−1** |
| THUMB_MCP | −5.030998 | **+5.108392** | **−1** |
| THUMB_IP | −2.619281 | **+2.696666** | **−1** |

两向分离充分（最小 |Δ| ≈ 0.70 mm @ LITTLE_DIP），无歧义 ⇒ `FLEXION_AXIS_SIGN_QUALIFIED = PASS`。
per-digit 签名一致：**全部 5 指 = −1**（即 flexion = 绕 local X 旋转 −angle）。
`STAGE6A_FLEXION_AXIS_SIGN_AUDIT.json`（5° probe **不计入** 42 case matrix）。

---

## 五、Local deformation patches

- **四指**：以批准 T-01 **deformation-loop 间距**（`LOOP_POSITION_axial_from_commissure_mm` 相邻差的中位数 κ）
  在批准 joint arc 两侧展开。
- **Thumb MCP / IP**：批准 joint location ＋ **拇指关节折线弧长坐标**（`APPROVED_JOINT_POLYLINE_ARC_LENGTH`）
  ± 2×网格中位边长。**未使用**任何 whole-thumb 全局表面测地坐标。

| patch | κ (mm) | 顶点数 |
|---|---|---|
| INDEX_MCP / PIP / DIP | 4.021 / 4.596 / 4.025 | 79 / 36 / 49 |
| MIDDLE_MCP / PIP / DIP | 4.441 / 5.487 / 4.535 | 73 / 41 / 42 |
| RING_MCP / PIP / DIP | 2.417 / 4.595 / 4.301 | 65 / 35 / 40 |
| LITTLE_MCP / PIP / DIP | 3.861 / 4.652 / 3.422 | 153 / 32 / 46 |
| **THUMB_MCP / IP** | 7.7764 / 7.7764 | 104 / 98 |

`STAGE6A_LOCAL_PATCH_TABLE.json`

---

## 六、执行协议与 zero restore（硬 Gate）

每个 case 严格按：`RESET ALL POSE BONES → 验证 zero state → 只应用目标关节 rotation → depsgraph evaluate →
采集 metrics → （渲染）→ RESET TO BIND → 再次验证 restore`。
**从不**在前一 pose 上累积 rotation。

| 项 | 值 |
|---|---|
| pre-case zero max delta | **5.967e-05 mm** |
| post-case restore max delta（42 case 最大） | **5.967e-05 mm** |
| 硬门 | 1e-4 mm |
| 结论 | `ZERO_RESTORE_AFTER_EACH_CASE = PASS` |

restore 后的 evaluated mesh 与 Stage5B frozen zero-pose baseline **float-equivalent 一致**。
`STAGE6A_ZERO_RESTORE_AUDIT.json`（含每 case pre/post 记录与 bone pose reset 状态）。
harness 保存态另经重开校验 = `ZERO / RSSF`。

---

## 七、硬机器 blocker（§十四）

| A. NaN / Inf 顶点 | **0** |
| B. collapsed face（area ≤ 1e-12 m² 或 ratio ≤ 1e-6） | **0** |
| degenerate edge（≤ 1e-12 m） | **0** |
| D. mesh vertex count / topology | 42/42 case **unchanged** |
| C. new severe self-intersection | 见 §八（**非 0，全部升级 Human Review**） |
| E. non-target finger shaft | 见 §九（**PASS**） |
| F. forearm 被拖动 | 见 §十（**PASS**） |
| G. nail / distal cap 脱离 | 见 §十四/§十五（**未脱离**） |

无 catastrophic failure。**blockers = 0**。

---

## 八、自交分解（§十四 C）

绑定姿态本身已有 **59** 个相交面对（RSSF 下拇指尖已贴在食指上），全部作为 baseline 扣除。
新相交面对 = case 集合 − baseline 集合（共享顶点者排除）：

| metric | 值 |
|---|---|
| 42 case 新增相交面对总数 | **909** |
| 其中 intra-target-digit（本指折痕自接触） | **279** |
| 其中 target-vs-other-digit（姿态接触） | **404** |
| 其中 other-vs-other | 226 |
| 穿透深度 > 0.5 mm 的对数 | **454** |
| **新增相交 = 0 的 case** | **27 / 42** |

非零 case 全部集中在 **THUMB（MCP / IP）与 INDEX_MCP** —— 即 **在 RSSF 绑定姿态下本就相互接触的
两根手指**。原因是几何性的：冻结姿态里拇指远端指骨与食指 MCP 段最小链距仅 **3.28 mm**，
任何超过数度的拇指屈曲都会把拇指压进食指；45° 诊断角因此产生**姿态级互穿**，
**不可归因于 skin weight**。

| case | new | intra | vs_other | other | max depth (mm) |
|---|---|---|---|---|---|
| TH_MCP_45 | 222 | 79 | 84 | 59 | 3.951 |
| TH_MCP_30 | 171 | 49 | 67 | 55 | 2.309 |
| TH_IP_45 | 159 | 51 | 71 | 37 | 2.359 |
| TH_MCP_15 | 119 | 33 | 58 | 28 | 2.303 |
| TH_IP_30 | 113 | 35 | 52 | 26 | 1.979 |
| IDX_MCP_45 | 46 | 5 | 32 | 9 | 1.300 |
| IDX_MCP_30 | 38 | 6 | 27 | 5 | 1.304 |
| TH_IP_15 | 18 | 13 | 5 | 0 | 2.094 |

```
NEW_SEVERE_SELF_INTERSECTION =
  PASS_WITH_HUMAN_REVIEW（intra-digit 折痕 279 ／ 跨指接触 404 ／ >0.5 mm 454）
```

按 §三十三「0 **或全部明确 Human Review**」执行：**全部逐 case 列出**（`STAGE6A_SELF_INTERSECTION_AUDIT.json`），
最终形态判断权交 Human Review。**未**将姿态接触当作 skinning 缺陷，**未**伪报为 0。

---

## 九、Cross-digit 一致性（§十八）—— 按权重的权威口径

为避免“口径含糊”，本轮用**权重本身**判定：

- `CLEAN(d)` = 归属为 digit d 且权重向量**不含任何外来指骨组**的顶点。
- `SANCTIONED(d)` = 归属为 d 但携带外来指骨组的顶点（= Stage5B 已批准的 **sanctioned cross blend**，
  主要是 first-web root blend）。

| metric | 值 |
|---|---|
| **NON_TARGET_CLEAN_VERTEX_MOTION_MAX（42 case 最大）** | **5.967e-05 mm** ＝ harness 浮点噪声底 |
| blocker 阈值 | 1e-3 mm（= 17× 噪声底） |
| 结论 | `NON_TARGET_DIGIT_SHAFT_CONTAMINATION = PASS` |
| SANCTIONED_CROSS_BLEND_MOTION_MAX（对照诊断） | 4.462 mm（授权首蹼根混合按设计工作） |

即：**任何权重纯属自身指列的顶点，在其它指孤立屈曲下位移不超过浮点噪声**；
所有跨指运动都被**逐点归因到 Stage5B 已批准的 first-web root blend**（该混合在 Stage5B
`CROSS_DIGIT_WEIGHT_LEAK_AUDIT_R1A.json` 中已登记为 `SANCTIONED_first_web_root_blend`）。

`STAGE6A_CROSS_DIGIT_DEFORM_AUDIT.json`

---

## 十、Forearm 稳定性（§十九）

`WRIST_R` 本轮锁定。552 个前臂顶点（腕关节 head 近端侧）在 42 case 中最大位移
= **7.451e-06 mm** ⇒ `FOREARM_STABILITY = PASS`（float-equivalent zero）。
未出现 finger flex 拉动前臂。

---

## 十一、Fingertip trajectory（§二十）

14/14 关节的 tip landmark **palmar 分量随角度单调递增**（`TIP_TRAJECTORY_MONOTONIC = PASS`）：

| joint | 15° | 30° | 45° | mono |
|---|---|---|---|---|
| INDEX_MCP / PIP / DIP | 15.74 / 7.70 / 3.06 | 29.38 / 13.85 / 5.37 | 39.99 / 18.02 / 6.77 | ✅ |
| MIDDLE_MCP / PIP / DIP | 16.43 / 7.59 / 2.47 | 29.90 / 12.81 / 3.87 | 39.50 / 15.32 / 4.10 | ✅ |
| RING_MCP / PIP / DIP | 15.05 / 6.72 / 2.08 | 27.38 / 11.28 / 3.18 | 36.16 / 13.38 / 3.21 | ✅ |
| LITTLE_MCP / PIP / DIP | 11.48 / 5.27 / 1.91 | 21.06 / 9.08 / 3.14 | 28.11 / 11.16 / 3.61 | ✅ |
| **THUMB_MCP / IP** | 15.40 / 8.24 | 30.45 / 16.61 | 44.11 / 24.54 | ✅ |

无 30° 相对 15° 反向弹回的情形。`STAGE6A_TIP_TRAJECTORY_AUDIT.json`（含 world 位置与位移分量）。

---

## 十二、局部应变（DIAGNOSTIC，§十六）

> **不设**任何人造人体科学阈值（未硬编码 1.2 / 1.5 / 2.0）。仅“趋近 0 的 face area”或“爆炸性离群”
> 作为 blocker；本轮 blocker 命中数 = **0**（最小 face-area ratio = 0.019 > 1e-6）。

每 patch 记录 edge length ratio、face area ratio、local surface area ratio、joint-band width change、
local bbox、vertex displacement max/mean。45° 摘要（min / max）：

| joint | edge ratio | face area ratio | patch disp max (mm) |
|---|---|---|---|
| INDEX_MCP | 0.490 / 3.173 | 0.387 / 2.039 | 6.030 |
| INDEX_PIP | 0.481 / 1.324 | 0.489 / 1.318 | 3.063 |
| INDEX_DIP | 0.379 / 1.264 | 0.389 / 1.264 | 5.090 |
| MIDDLE_MCP | 0.761 / 1.578 | 0.663 / 1.558 | 9.065 |
| MIDDLE_PIP | 0.530 / 1.305 | 0.533 / 1.302 | 4.893 |
| MIDDLE_DIP | 0.408 / 1.270 | 0.419 / 1.264 | 3.932 |
| RING_MCP | 0.845 / 1.708 | 0.838 / 1.422 | 5.444 |
| RING_PIP | 0.530 / 1.325 | 0.537 / 1.316 | 4.322 |
| RING_DIP | 0.378 / 1.239 | 0.387 / 1.231 | 3.693 |
| LITTLE_MCP | 0.734 / 1.626 | 0.790 / 1.576 | 9.343 |
| LITTLE_PIP | 0.541 / 1.296 | 0.544 / 1.283 | 2.739 |
| LITTLE_DIP | 0.357 / 1.219 | 0.349 / 1.215 | 3.337 |
| **THUMB_MCP** | 0.421 / 3.016 | **0.194** / 3.029 | 15.811 |
| **THUMB_IP** | 0.286 / 3.128 | **0.019** / 2.663 | 11.481 |

`STAGE6A_LOCAL_STRAIN_AUDIT.json`（含 p05 / median / p95 分布）。

---

## 十三、Pinching / Collapse（§十七）

- **内侧面压缩**（patch 内 min edge ratio）与 **外侧面拉伸**（max edge ratio）已逐 case 记录。
- **Local thickness proxy**：自 patch 顶点沿指向指链轴方向 ray-cast 到对侧表面的距离比（bind vs case）。

45° 最薄的 6 个 case：

| case | thickness ratio min | inner compression | outer stretch |
|---|---|---|---|
| **IDX_MCP_45** | **0.0001** | 0.490 | 3.173 |
| RING_MCP_45 | 0.0007 | 0.845 | 1.708 |
| **TH_IP_45** | **0.0008** | **0.286** | 3.128 |
| LITTLE_MCP_45 | 0.1095 | 0.734 | 1.626 |
| TH_MCP_45 | 0.1341 | 0.421 | 3.016 |
| MID_MCP_45 | 0.2006 | 0.761 | 1.578 |

**机器值仅作诊断**；最终形态判断（pinching / 教学可读性 / 自然轮廓）归 Human Review。
**注意**：单点 thickness ratio ≈ 0 说明该处内外表面在采样射线上几乎贴合（弯曲内侧褶皱闭合），
这是 45° 全屈下的**内侧褶皱压缩**现象；是否可接受由 HR 判定。
`STAGE6A_PINCH_COLLAPSE_AUDIT.json`

---

## 十四、指甲形变（§二十一）

| digit | nail 顶点数 | 45° nail area ratio | 45° nail 平均位移 (mm) |
|---|---|---|---|
| INDEX | 43 | 1.000366 (MCP) / 1.003654 (PIP) / **1.091956** (DIP) | 44.80 / 21.50 / 5.69 |
| MIDDLE | 50 | 0.999920 / 1.000306 / **1.087463** | 51.27 / 26.91 / 6.89 |
| RING | 38 | 1.000111 / 1.000685 / **1.085096** | 47.86 / 25.03 / 6.83 |
| LITTLE | 36 | 1.000267 / 1.014542 / **1.095004** | 34.18 / 16.76 / 4.00 |
| **THUMB** | 22 | 1.000352 (MCP) / **1.108746** (IP) | 27.98 / 7.97 |

- nail patch **随对应 distal phalanx 连续变形**；无脱离、无翻转、无崩坏。
- 拓扑不变 ⇒ nail patch 连通性未被破坏。
- 面积比在 DIP/IP 屈曲下上升 ~9 %（远端指骨表面被轻微拉伸），属**轻微**范围；
  `NAIL_DEFORMATION = PASS_PENDING_HUMAN_REVIEW`（本轮**不要求** nail 保持刚性平板）。
`STAGE6A_NAIL_DEFORM_AUDIT.json`

---

## 十五、Thumb distal 特殊审计（§二十二）

Authority = R2A 批准的 distal-cap semantic（`GEODESIC_CONNECTED_CAP_FROM_DISTAL_MOST_SURFACE_REGION`, 9 mm）。
**未使用** IP→TIP straight chord full containment 作为 FAIL gate（Stage5A 例外继续 binding）。

| case | cap area ratio | cap 位移 max (mm) | IP crease min edge ratio | distal thickness ratio min |
|---|---|---|---|---|
| TH_MCP_45 | 1.0004 | 49.029 | 0.421 | 0.1341 |
| **TH_IP_45** | **1.0001** | 28.061 | **0.286** | **0.0008** |

- distal-cap **面积几乎不变**（1.0001–1.0004）⇒ 无明显压缩/膨胀；无折叠、无翻转。
- IP 屈曲的折痕集中在 IP crease（min edge ratio 0.286 @45°），远端帽本体稳定。
- 未出现“向 first web 异常变形”的证据（跨指运动全部归因到 sanctioned first-web blend）。
- `THUMB_DISTAL_DEFORMATION = PASS_PENDING_HUMAN_REVIEW`（形态最终判断归 HR）。

---

## 十六、四指 MCP / PIP / DIP 与 Thumb MCP / IP 结果

- **四指（36 case）**：NaN/折叠 = 0；topology 不变；前臂不动；非目标指 clean 顶点不动；
  tip trajectory 14/14 单调；patch 位移随角度单调增长；face area ratio 最低 0.349（LITTLE_DIP_45）。
  仅 INDEX_MCP 出现跨指姿态接触（因它参与 first web，且绑定位姿下拇指贴在其上）。
- **THUMB_MCP（3 case）**：patch disp 5.39 / 10.69 / 15.81 mm；area ratio min 0.194 @45°；
  未影响 CMC（locked）与前臂；四指 clean 顶点位移 ≤ 5.967e-05 mm。
- **THUMB_IP（3 case）**：patch disp 3.92 / 7.77 / 11.48 mm；area ratio min **0.019** @45°；
  远端 cap 面积比 1.0001；tip palmar 单调 8.24 → 16.61 → 24.54 mm。

---

## 十七、失败 case 与归因

**无 FAIL case。** 无 blocker。以下为需 HR 关注的**非阻断**诊断项及其归因：

| 现象 | 归因（§三十二 分类） |
|---|---|
| THUMB（MCP/IP）与 INDEX_MCP 在 45° 出现姿态级互穿（404 对跨指） | **几何约束**：RSSF 绑定位姿下拇指远端与食指 MCP 段最小链距 3.28 mm。**不是** weight 缺陷 |
| 45° 内侧折痕压缩（TH_IP face area ratio 0.019；IDX_MCP thickness ratio 0.0001） | **A. WEIGHT_TRANSITION_FAILURE** 的候选（1 网格边宽的过渡带在 45° 全屈下压缩剧烈）→ 交 HR 判定是否需要收敛角度或调整过渡带宽 |
| THUMB_MCP/IP 的 outer stretch 达 3.0–3.1× | 同上，属**内侧压缩/外侧拉伸**的配对现象 |
| INDEX 根部 24 个顶点在 THUMB_MCP 屈曲下位移 ≤ 1.33 mm | **D 的 sanctioned 分支**：Stage5B 已批准的 first-web root blend（`SANCTIONED_CROSS_BLEND`） |

**未**自动修权重、**未**改区域、**未**移 bone、**未** retopo（§三十一）。Stage5A 骨架保持冻结。

---

## 十八、自动 Gate（§三十三）

```
FLEXION_AXIS_SIGN_QUALIFIED          = PASS
FORMAL_CASE_COUNT                    = 42
ZERO_RESTORE_AFTER_EACH_CASE         = PASS          (max 5.967e-05 mm < 1e-4)
NAN_INF_DEFORM                       = 0
COLLAPSED_FACES                      = 0
NEW_SEVERE_SELF_INTERSECTION         = PASS_WITH_HUMAN_REVIEW
                                       (intra-digit 279 / cross-digit contact 404 / >0.5mm 454)
FOREARM_STABILITY                    = PASS          (max 7.451e-06 mm)
NON_TARGET_DIGIT_SHAFT_CONTAMINATION = PASS          (clean-vertex max 5.967e-05 mm)
TIP_TRAJECTORY_MONOTONIC             = PASS          (14/14)
NAIL_DEFORMATION                     = PASS_PENDING_HUMAN_REVIEW
THUMB_DISTAL_DEFORMATION             = PASS_PENDING_HUMAN_REVIEW
TOPOLOGY_UNCHANGED_ALL_CASES         = true
HARNESS_FINAL_POSE                   = ZERO / RSSF   (5.967e-05 mm)
MASTER_HASH_UNCHANGED                = true
HARNESS_HASH_UNCHANGED               = true
blockers                             = 0
```

> **不伪造机器 PASS**（§三十四）：subtle pinching、教学可读性、自然指形轮廓、nail 形状质量、
> 折痕质量、体积保持、解剖合理性 —— **全部保留 Human Review 权威**。
> 本报告**不宣称** `DEFORMATION_FINAL = PASS`。

---

## 十九、渲染证据（§二十八 / §二十九 / §三十）

- 14 张 max-angle（45°）证据：`STAGE6A_{INDEX|MIDDLE|RING|LITTLE}_{MCP|PIP|DIP}_45.png`、
  `STAGE6A_THUMB_{MCP|IP}_45.png`
- 额外：`STAGE6A_FOUR_FINGER_OVERVIEW.png`（四指代表关节**分别**展示，2×2，未叠加到同一 mesh pose）、
  `STAGE6A_THUMB_MCP_CLOSEUP.png`、`STAGE6A_THUMB_IP_CLOSEUP.png`、`STAGE6A_BIND_RESTORE_PROOF.png`
- **before/after 规范**：代表性图在同一帧内渲染两个网格副本（左 = 冻结 bind，右 = 45° test），
  使用**相同相机 / 灯光 / 材质 / 比例**；未通过换相机掩盖形变。

---

## 二十、哈希复核与产物

| 文件 | SHA-256 | before = after |
|---|---|---|
| Stage5B master `RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend` | `c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6` | ✅ |
| Stage6A harness `RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend` | `8f223c979362a8c3414b58e2467c7cda2da60f993245cc95b2a38d76c718d3ef` | ✅ |

产物清单见 `STAGE6A_STATUS.json` 与 §二十一。

---

## 二十一、停止点

`STAGE6A = READY_FOR_HUMAN_REVIEW`；`ISOLATED_FLEX_DEFORMATION = PASS_PENDING_HUMAN_REVIEW`；
`STAGE6B = NOT_STARTED`。

**未**开始 Stage6B；**未**测 CMC opposition / 完整 thumb opposition / 钢琴按键 / 多关节演奏动作；
**未**写 `APPROVED` / `FINAL` / `CMC_OPPOSITION_PASS` / `READY_FOR_RELEASE`。
等待 Human Review。
