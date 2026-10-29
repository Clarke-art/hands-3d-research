# STAGE4C_R2_NAIL_SELECTOR_AND_ORIGIN_EVIDENCE_CORRECTION

**任务**：Stage-4C R1 Human Review 后的窄修订（`REQUEST_CHANGES` 响应）
**输入（冻结）**：`stage4c/RIGHT_HAND_ENGINEERING_STAGE4C_R1.blend`
`sha256 66fa45325273f38f597f6af78bec603c471a697d6f1798b96eecc231e64bcdb6` ✓（执行前后逐字节一致）
**新 master**：`stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend`
`sha256 fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7`（2,009,735 B）
**运行时**：`D:\Blender\blender.exe`（Blender 5.1.2）

**修订范围**：仅 CON-4 nail selector、CON-6 origin evidence + errata、R2 revision。
未触碰：RSSF pose、Retopo、T-01 loops、CMC cage topology、CMC deformation、全手 UV 重展、
Production Rig、Production Skin Weight、左手镜像、animation、GLB、Three.js、Stage 5。
**CON_7_UV 未重新研究**，原样 carry forward。

---

## 0. 结论

```
STAGE4C_R2 = READY_FOR_HUMAN_REVIEW

CON_4_NAILS         = PASS_PENDING_HUMAN_REVIEW
CON_5_RSSF_REPOSE   = CARRY_FORWARD_UNCHANGED_PASS
CON_6_ORIGIN        = PASS_PENDING_HUMAN_REVIEW
CON_7_UV            = CARRY_FORWARD_PASS

CANONICAL_HAND_POSE = RSSF
HAND_BASE_TOPOLOGY  = UNCHANGED
CMC_DEFORMATION_FINAL = PENDING_STAGE6
PRODUCTION_RIG      = NOT_STARTED
STAGE5              = NOT_STARTED
STAGE4C_R1          = 保留 provenance（未覆盖、未删除、未回写）
```

---

## 1. Nail selector 根因（§十三-1）

R1 的 selector 只用了三件事：**面法向锥** + **远端骨轴向跨度** + **径向外侧比例**。
**没有 digit ownership gate，也没有 distal phalanx 空间域 gate。**

本轮先做只读诊断（`stage4c_r2/_tmp/R1_SELECTOR_DIAGNOSIS.json`），并且**完整复现了 R1 的 selector**
（`reconstruction_matches_r1 = true`，五指全中），然后量化出四条独立成因：

| # | 成因 | 实测 |
| --- | --- | --- |
| 1 | **相邻手指 nail normal 近乎平行** | index–middle 13.07°、middle–ring 11.80°、ring–little 15.24°、index–ring 24.32°。R1 的 63.3° 锥因此互相吞并：**838 个面同时落在 ≥2 个 digit 的锥内** |
| 2 | **无 ownership gate ⇒ 面集重叠** | 204 个 face 实例只覆盖 155 个唯一面 → **49 个重复归属**，10 对里 6 对相交 |
| 3 | **轴向测试只约束一个坐标 ⇒ 指根也能通过** | R1 union 到最近远端骨最远达 **64.82 mm**，其中 **46 个面 > 12 mm**（p90 = 43.55 mm）——**这正是 dorsal / thumb nail 图里指根那条浅色横带的来源** |
| 4 | **跨指误归属** | R1 union 里有 **36 个面实际属于别的 digit** |

> 结论：R1 的 `nail_side_identifiable_on_all_five_digits = true` 因为忽略重叠，**不能作为 Human Review authority**。
> 已在 `NAIL_AUDIT_R2.json.r1_authority_correction` 中作废并替换为 R2 的 gate 结果。R1 文件未改。

---

## 2. R2 selector：三道闸门（§五、§六）

```
A. DIGIT OWNERSHIP   face 必须属于其 owning digit。
                     ownership 用**整条骨链**（meta+prox+distal）判定 —— 比 brief 点名的
                     "distance to owning digit distal segment" 更强，而且是必须更强：
                     在当前对掌 RSSF 姿态下，拇指远端指节距 INDEX 指节只有 ~9 mm，
                     只用远端骨段会把食指指节的面判给拇指。
                     brief 的**字面 distal-segment 比较也同时作为一道闸门执行**。
B. DISTAL DOMAIN     轴向 ∈ [0.18, 0.80] 远端骨长；径向 > 0（背侧）；径向 ≤ 该指**实测**
                     表面包络 R_env；且径向 ≥ 0.25·R_env（外侧壳层）
C. DORSAL FACING     面法向与该指 nail normal 的锥角 cos ≥ 0.60（53°）；
                     并由相邻指仅差 ~13° 这一点决定，必须比 R1 的 0.45 更紧
web guard            距其他任一指远端骨 ≥ 4 mm
```

`R_env`（各指远端指节实测表面包络半径）：thumb 11.14 / index 7.64 / middle 7.80 /
ring 7.15 / little 6.75 mm —— 是**测出来的**，不是调参，因此细的 little 指自动收紧。

**disjoint 是结构性的**：每个面只有一个 owner，所以五个集合在构造上就不可能相交；
10 组 pairwise intersection 仍逐对计算并上报作为证据。

**材质方案保留**：brief 规定"除非能证明 material-only 在当前 topology 上无法形成合理教学语义"才可换成独立甲片。
R2 重新验证后发现：加上三道闸门后，material-only 在五指上都形成了干净的单一甲片、
0 重叠、0 泄漏 —— **不存在支持改用独立高模甲片的证据**，故保留 material-only（零几何、零 tri）。

---

## 3. R1 → R2 face ownership 差异（§十三-2）

| 指标 | R1 | R2 |
| --- | --- | --- |
| face 实例数 | 204 | **124** |
| 唯一面数（union） | 155 | **124** |
| 重复归属 | **49** | **0** |
| 相交的 digit 对 | 6 / 10 | **0 / 10** |
| >12 mm 远离远端骨的面 | 46 | **0** |
| 掌侧泄漏 | —（未检查） | **0** |
| web 泄漏 | —（未检查） | **0** |
| 每个 digit 的连通分量 | —（未检查） | **1** |

面级变化：**保留 70** 个 R1 面、**丢弃 85** 个（越界/跨指/指根）、**新增 54** 个（同一甲片的正确补足）。

---

## 4. 五指最终 face count 与几何（§十三-3）

| digit | faces | distal bone | axial 归一化 | bbox extent (mm) | 到自身骨距离 (mm) | 到竞争指距离 (mm) |
| --- | --- | --- | --- | --- | --- | --- |
| THUMB | **12** | `THUMB_IP_R` | 0.20–0.73 | 5.6 × 3.6 × 12.1 | 4.81–9.45 | 48.84–… |
| INDEX | **29** | `INDEX_DIP_R` | 0.18–0.79 | 10.2 × 9.2 × 3.1 | 3.09–6.84 | ≥ 32.21 |
| MIDDLE | **35** | `MIDDLE_DIP_R` | 0.20–0.76 | 12.6 × 10.0 × 3.4 | 5.73–8.32 | ≥ 26.67 |
| RING | **25** | `RING_DIP_R` | 0.29–0.80 | 12.2 × 8.6 × 3.3 | 5.65–6.96 | ≥ 24.13 |
| LITTLE | **23** | `LITTLE_DIP_R` | 0.20–0.79 | 7.9 × 6.8 × 3.7 | 3.32–6.18 | ≥ 32.55 |
| **合计** | **124** | | | | | |

`NAIL_CONNECTED_COMPONENTS_PER_DIGIT` = `{thumb: [12], index: [29], middle: [35], ring: [25], little: [23]}`
→ **每指恰好 1 个连续甲片，无碎片、无 speck 丢弃**（speck 规则未触发）。

**THUMB 从 R1 的 46 面降到 12 面**是本轮最显著的收缩——R1 的 46 面里包含了大量指根/掌侧/跨指面；
12 面是拇指**远端指节背侧**的真实甲床范围。指令明确"不要为了保留 R1 的 31–47 faces 而扩大错误区域"，故按实测收紧。

---

## 5. 10 组 pairwise intersection（§十三-4）

| pair | 交集 | pair | 交集 |
| --- | --- | --- | --- |
| thumb × index | **0** | index × little | **0** |
| thumb × middle | **0** | middle × ring | **0** |
| thumb × ring | **0** | middle × little | **0** |
| thumb × little | **0** | ring × little | **0** |
| index × middle | **0** | — | — |

```
NAIL_FACE_SET_DISJOINT        = PASS
NAIL_FACE_OVERLAP_COUNT_TOTAL = 0
```

---

## 6. Leakage 与其它 gate（§十三-5）

```
NAIL_FACE_OWNER_DISTANCE_TEST         = PASS   (violations 0)
NAIL_DISTAL_DOMAIN_TEST               = PASS   (violations 0)
NAIL_PALMAR_LEAKAGE                   = 0
NAIL_WEBSPACE_LEAKAGE                 = 0
NAIL_FACES_FURTHER_THAN_12MM_FROM_ANY_DISTAL_BONE = 0
NAIL_CONNECTED_COMPONENTS_PER_DIGIT   = 每指 1 个
```

对照 R1：指根浅色横带（46 个 >12 mm 的面）**已完全消失**。

---

## 7. Origin errata（§七、§十三-6）

**未重新寻找 origin。** R2 master 以 origin delta = **0.0 m** 保存，数值与 R1 approved candidate 一致：

```
WRIST_ORIGIN = [1.408704638, 0.022395039, 0.335847497]
ORIGIN_BEFORE = [1.40478158, 0.011328205, 0.353645504]
origin delta vs R1 = 0.0 m
```

### ERRATA（R2 侧新增，R1 文件原样不动）

`ERRATA_ID = STAGE4C_R1_ORIGIN_STAGE3_DELTA_WORDING`

R1 的矛盾原文（三处，均已定位）：

| 文件 | 字段 | 问题 |
| --- | --- | --- |
| `stage4c/ORIGIN_AUDIT.json` | `note` | 写着 "…reproduces the already-accepted Stage-3 wrist level **to <1 mm**"，与同文件 `delta_to_stage3_mm = 7.23` **直接冲突** |
| `stage4c/ORIGIN_AUDIT.json` | `reproduces_stage3_wrist_narrowest_z` | 字段**名**暗示"复现"，其值 0.343 其实是 Stage-3 的**水平高度**，不是达成的一致性 |
| `stage4c/STAGE4C_RUN.json` | `CON_6_origin.note` | 同一句 "<1 mm" |

**修正后的正式表述**：

> **difference to the Stage-3 accepted wrist level = 7.23 mm**
> （同一解剖 basin；两个定位器是相互独立的方法，**并不**达到亚毫米一致）

R1 文件**未修改**；其 sha256 已记录在 `ORIGIN_AUDIT_R2.json.ERRATA.r1_file_hashes` 以便核验。

### Stage4B finding 继续传递

```
STAGE4B_WRIST_R_LOCATOR_DEFECT = OPEN -- FOR STAGE 5
STAGE 5 不得继承 Stage-4B 的 WRIST_R 位置（该点在 z=0.277349 m，即前臂截断面；
其"腕→掌心"骨长 201 mm，解剖上应为 ~65–90 mm）。
不影响 Stage-4B 的 RSSF 关节角验收（全部在手指上测量）。
```

---

## 8. 冻结项验证（§十）

```
VERTEX POSITION max delta        = 0.000e+00 m      (必须为 0)  PASS
UV max delta                     = 0.000e+00                    PASS
origin delta vs R1               = 0.000e+00 m                  PASS
TOPOLOGY_SIGNATURE_PRE = POST    = 5a396684…90c1d               PASS
  V = 3416   E = 6828   F = 3414（全部 quad）
TOTAL_RIGHT_HAND_TRIS            = 6828                         PASS
armatures present                = []                           PASS
vertex groups                    = []                           PASS
R1 file sha256 before = after    = 66fa4532…4bcdb6              PASS
```

变更仅限 **face material assignment**（`NAIL_BED` 155 → 124 面）；顶点位置、边/面拓扑、
UV、世界几何、origin 全部不变。

---

## 9. 正式 Human Review 证据图（§十三-8）

```
stage4c_r2/renders/STAGE4C_R2_DORSAL.png                  材质背侧（指根横带已消失）
stage4c_r2/renders/STAGE4C_R2_PALMAR.png                  材质掌侧
stage4c_r2/renders/STAGE4C_R2_FINGERTIPS.png              四指甲片特写（沿 nail normal）
stage4c_r2/renders/STAGE4C_R2_THUMB_NAIL.png              拇指指甲特写
stage4c_r2/renders/STAGE4C_R2_NAIL_MASK_DORSAL.png        每指 diagnostic color（背侧，brief 指定）
stage4c_r2/renders/STAGE4C_R2_NAIL_MASK_NAILVIEW.png      每指 diagnostic color（正对甲片）
stage4c_r2/renders/STAGE4C_R2_NAIL_MASK_THUMBVIEW.png     拇指 diagnostic color
stage4c_r2/renders/STAGE4C_R2_ORIGIN_SIDE.png             origin 证据（带标注）
stage4c_r2/renders/STAGE4C_R2_ORIGIN_DORSAL_OBLIQUE.png   origin 证据（腕部上下文）
```

**关于 mask**：brief 指定的 dorsal 视图是本轮证明**否定命题**的视图 —— 它显示所有诊断色
只出现在指尖，**指根、web、掌侧全无颜色**。但半屈姿态下甲片与背侧轴成 ~64°，
该视图无法读出**形状**，因此额外加了两张正对甲片的 mask 视图
（`NAIL_MASK_NAILVIEW` / `NAIL_MASK_THUMBVIEW`），使"五个区域互不交叉"可以被肉眼直接确认。
额外图不改变 brief 指定的那张，也不改 master（master 仍是统一 `NAIL_BED`）。

**关于 origin 证据图**：`STAGE4C_R2_ORIGIN_SIDE.png` 用 X-ray 显示
**蓝色**（WRIST_ORIGIN，交付值）与**黑色**（Stage-4B WRIST_R，错误值）两个标记
**相距 ~58 mm、清晰不同**，并各自标注名称；腕部轮廓保持可见（未被标注遮挡）。
`STAGE4C_R2_ORIGIN_DORSAL_OBLIQUE.png` 显示蓝条位于**腕部收窄处**，
其上方可见 thenar / 拇指基座、下方可见前臂截断面红条 —— 证明 origin 不是 forearm cap、
不是 palm centre、也不是拇指列。

**临时图仅写入 `stage4c_r2/_tmp/`**；正式图在 `stage4c_r2/renders/`。
全程未使用 glob / recursive / prefix wildcard 删除。

---

## 10. 新 master（§十三-7）

```
stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend
sha256 fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7
2,009,735 B
（R1 master 66fa45325273f38f597f6af78bec603c471a697d6f1798b96eecc231e64bcdb6，未改动）
```

产物清单：

```
stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend
stage4c_r2/STAGE4C_R2_FINALIZATION_REPORT.md      (本报告)
stage4c_r2/STAGE4C_R2_STATUS.json
stage4c_r2/NAIL_AUDIT_R2.json
stage4c_r2/ORIGIN_AUDIT_R2.json
stage4c_r2/STAGE4C_R2_RUN.json                    (完整日志)
stage4c_r2/STAGE4B_R2_JOINT_FRAME.json            (从冻结 Stage-4B provenance 只读提取的 21 骨测量帧)
stage4c_r2/renders/*.png                          (9 张正式图)
stage4c_r2/_tmp/                                  (诊断 / 探针 / 无标注版 scratch)
scripts/stage4c_r2_{selector,frame,diag,probe,finalize,render,audits}.py
```

**R2 master 不含 armature，也不在运行时依赖 TEMP rig**：骨位信息以
`STAGE4B_R2_JOINT_FRAME.json`（从冻结 Stage-4B provenance 只读提取）作为测量帧存在，
TEMP rig 未被恢复、未被保存进 R2 master。

---

## 11. 最终状态（§十三-9）

```
STAGE4C_R2 = READY_FOR_HUMAN_REVIEW

CON_4_NAILS              = PASS_PENDING_HUMAN_REVIEW
CON_5_RSSF_REPOSE        = CARRY_FORWARD_UNCHANGED_PASS
CON_6_ORIGIN             = PASS_PENDING_HUMAN_REVIEW
CON_7_UV                 = CARRY_FORWARD_PASS
CANONICAL_HAND_POSE      = RSSF
HAND_BASE_TOPOLOGY       = UNCHANGED
CMC_DEFORMATION_FINAL    = PENDING_STAGE6
PRODUCTION_RIG           = NOT_STARTED
STAGE5                   = NOT_STARTED
```

**未写** APPROVED / FINAL / READY_FOR_STAGE5_RIG。

**待 Human Review 关注**：
1. `STAGE4B_WRIST_R_LOCATOR_DEFECT`（OPEN，对 Stage 5 有约束力）
2. `STAGE4C_R1_ORIGIN_STAGE3_DELTA_WORDING`（已由 errata 关闭，R1 文件未动）
3. thumb 甲片由 R1 的 46 面收紧到 12 面 —— 请确认其**视觉比例**是否可接受（本轮按实测收紧，
   未为保留 R1 数量而扩大区域）

**已停止。未进入 Stage 5。等待 Human Review。**
