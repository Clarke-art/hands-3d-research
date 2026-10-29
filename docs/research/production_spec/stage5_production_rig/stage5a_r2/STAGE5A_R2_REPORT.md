# STAGE5A_R2_PRODUCTION_JOINT_LANDMARK_REQUALIFICATION

**任务**：Stage5A R1 Human Review（`REQUEST_CHANGES`）后的窄修订 —— 只重新资格确认 5 个关节位置
**冻结输入**：`stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend`
`sha256 fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7` ✓（执行前后一致）
**R1 provenance（未改）**：`stage5a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R1.blend`
`sha256 dd5f7265ea373579e9f77ecea2f74f0b2d0642a2bbb10795f1ddf5c17eb1486d` ✓
**R2 产物（新文件）**：`stage5a_r2/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2.blend`
`sha256 615367d7fab3e75431fa7171e7e82f3a655c62e29ad7ddca5509b093e9f68c81`

---

## 0. 结论

```
STAGE5A_R2                = READY_FOR_HUMAN_REVIEW
PRODUCTION_RIG_SKELETON   = PASS_PENDING_HUMAN_REVIEW
RIGHT_HAND_PRODUCTION_RIG = CANDIDATE_R2
PRODUCTION_SKIN_WEIGHT    = NOT_STARTED
STAGE5B                   = NOT_STARTED

自动门禁 32 / 32 PASS
未写 APPROVED / FINAL / READY_FOR_SKINNING / STAGE5B_STARTED
```

---

## 1. 语义修正：ASSET ORIGIN ≠ PRODUCTION WRIST JOINT

```
ASSET_OBJECT_ORIGIN            = [1.408704638, 0.022395039, 0.335847497]   （未修改，Stage4C 继续 PASS）
PRODUCTION_WRIST_JOINT_CENTER  = [1.406007767, 0.016420959, 0.358511657]
分离距离                        = 23.593 mm
与 Stage-4B 旧 WRIST_R 的距离   = 81.828 mm
```

`STAGE4C_R2_ASSET_ORIGIN` 正式定为 **FROZEN_ASSET_REFERENCE**；
`PRODUCTION_WRIST_R.head` 已 **TO_BE_ANATOMICALLY_REQUALIFIED → REQUALIFIED**。
Stage4C 的 origin 结论未被推翻，只是解除了"asset origin = skeletal wrist rotation centre"这一错误等同。

**PRODUCTION_WRIST_CENTER_METHOD（可复现，无手工点选）**

1. 前臂坐标系：`e_long` = 前臂端盖质心 → 腕区质心；`e_dorsal` = 掌平面法向；`e_lateral = e_long × e_dorsal`（正向指向拇指侧）。
2. 轴向剖面（2 mm 步长、±3 mm 切片、仅取距前臂轴 ≤45 mm 的顶点以排除拇指列），
   从已批准腕区向 distal 扫描，**扫到腕掌（CMC）层位之前停止**（不是任意偏移量）。
3. **声明式 transition 规则**：`A_ref` = 窗口近端 20% 的剖面面积中位数；
   `s_on` = 约束之后第一个面积 ≥ 1.03·A_ref 的剖面；`s_palm` = 第一个 ≥ 1.10·A_ref 的剖面；
   过渡区 = [s_on, s_palm]，其中心 `s_trans = 79.79 mm`（端盖起算）。
   - 腕部收窄（最小面积）= 54.79 mm；`s_on` = 74.79 mm；`s_palm` = 84.79 mm
   - `A_ref` = 2218.6 mm²；扫描窗口 = 38.79 … 111.78 mm
4. 关节中心 = `s_trans` 剖面的**最大间隙点**（最大内切球中心）—— **不是**最小面积点，
   全过程**未使用任何目标骨长**。

```
PRODUCTION_WRIST_CENTER = [1.406007767, 0.016420959, 0.358511657]
WRIST_R.tail (PALM_REFERENCE) = [1.414331079, 0.017137397, 0.478491724]
WRIST_ROOT_LENGTH = 120.2706 mm          （R1 before = 142.8024 mm）
```

**WRIST_R.tail 重新验证**：四 MCP 形心本身**并不在网格内部**（射线奇偶 0/64，距表面仅 0.0417 mm
—— 它在掌背皮肤上）。R2 因此把它**重新推导**为"掌内 medial 点"：通过四 MCP 形心、垂直于掌长轴的平面内
取 1.5×R_env(index) 球内的最大间隙点 →

```
PALM_REFERENCE(R2) = [1.414331079, 0.017137397, 0.478491724]
  ray parity = 64/64（内部）  表面余量 = 7.685 mm
  位于新 WRIST head 的 distal 方向 118.87 mm 处
  与腕骨轴夹角 = 8.75°（= 合理的 root 方向）
  距拇指列 37.70 mm（不在拇指列内）
```

**Sanity check（不作为目标）**：`wrist → mean MCP = 120.0 mm`；项目此前引用的解剖参考 65–90 mm。
该项按 brief 只作 SANITY 报告，**未用于放置关节、未为命中数字调骨长**。

---

## 2. 五个重新资格确认的关节（前后对照）

| joint | R1 位置 | R2 位置 | shift | R2 表面余量 | 奇偶 | 依据 |
| --- | --- | --- | --- | --- | --- | --- |
| WRIST_R | 1.408704638 / 0.022395039 / 0.335847497 | 1.406007767 / 0.016420959 / 0.358511657 | **23.593 mm** | 18.901 mm | 64/64 | 腕掌过渡区剖面最大间隙点 |
| INDEX_MCP_R | 1.445879102 / 0.013830277 / 0.479620308 | 1.442374706 / 0.017366245 / 0.483602315 | **6.375 mm** | 5.867 mm | 64/64 | 保留 T-01 轴向平面，求该剖面内最大间隙点 |
| THUMB_CMC_R | 1.448804379 / 0.011108357 / 0.393759280 | 1.440895081 / 0.001219887 / 0.391814500 | **12.811 mm** | 0.174 → **12.000 mm** | 64/64 | 批准 CMC 笼区域内的 thenar/第一掌骨 medial 点 |
| THUMB_MCP_R | 1.443062305 / 0.007415419 / 0.435889333 | 1.454060912 / 0.001536575 / 0.436873049 | **12.510 mm** | −2.446（外部）→ **9.484 mm** | 0/64 → **64/64** | 批准 T-01 轴向区内的拇指管 medial 点 |
| THUMB_TIP_R | 1.451316237 / 0.010537470 / 0.485614926 | 1.456466794 / 0.018134484 / 0.487595350 | **9.390 mm** | 0.0022 mm | 64/64 | 指尖 landmark 重定（见 §4） |
| THUMB_IP_R | 1.450860858 / 0.006127121 / 0.464001149 | **完全相同** | **0.000000 mm** | 6.217 mm | 64/64 | CARRY_FORWARD（未移动） |

### INDEX_MCP_R

```
AXIAL_DELTA_FROM_APPROVED_T01 = 0.000 mm   （R2 点构造上就落在批准 T-01 轴向平面内）
R2 独立佐证：沿 R1 点局部表面法向的内部弦 medial 点 → 与 R2 相差 2.078 mm
```
未机械 inward offset；中心由该剖面的**最大内切球中心**求出（`search ball = 1.15 × R_env(index) = 8.79 mm`）。

### THUMB_CMC_R

```
CMC_SURFACE_ANCHOR        = [1.441702724, 0.015799001, 0.392542213]（Stage-4A R2 顶点 794）
CMC_PRODUCTION_CENTER     = [1.440895081, 0.001219887, 0.391814500]
SURFACE_CLEARANCE BEFORE  = 0.1739 mm
SURFACE_CLEARANCE AFTER   = 12.0003 mm
DISTANCE_TO_CAGE_ANCHOR   = 14.620 mm  ≤  批准 cage locality 半径 15.64 mm
CMC_INSIDE_APPROVED_REGION = true
```
CMC cage / topology / retopo **全部未动**；**未**宣称 CMC deformation PASS
（最终权威仍是 `STAGE6_DEFORM_TEST_THUMB_OPPOSE`）。
方法：在笼锚点所在轴向平面内、以锚点为心的批准区域内求最大间隙点（1.15×R_env(thumb) = 12.81 mm 搜索球）。

### THUMB_MCP_R

```
R1 outside mesh 2.446 mm  →  R2 inside, clearance 9.4841 mm, ray parity 64/64
T-01 axial delta = +4.588 mm   （批准 zone ±9.614 mm）
独立佐证：法向内部弦 medial 点 → 与 R2 相差 1.915 mm
```
未使用"旧点 + 内向法向"；中心来自批准轴向平面内的拇指剖面最大间隙点。

---

## 3. THUMB_TIP_R —— 重新资格确认后的 fingertip landmark

R1 的 landmark 距真正拇指 apex **12.078 mm**，Human Review 判 NOT ACCEPTED。

**R2 定义（可复现、不依赖单个顶点）**

1. 候选集 = 拇指**严格归属**的表面采样点（**顶点 ∪ 面心**，因此粗网格的指尖帽不能量化结果），
   且位于 `THUMB_IP` 骨段周围**实测远端指骨包络 R_env(thumb) = 11.14 mm** 之内
   （与已批准 nail selector 用同一包络）。管域限制是必需的：不加它，距 IP 关节最远的手指点会落到腕掌区。
2. landmark = 候选集中**从 THUMB_IP 关节起算最远、且其直线在每一个内部采样点都位于拇指内部**的点
   （候选按距离降序尝试，第 9 个通过）。

```
THUMB_TIP_R.head(R2) = [1.456466794, 0.018134484, 0.487595350]
到拇指 apex 顶点距离  = 12.078 → 6.967 mm
到拇指自身表面        = 0.0022 mm（体表点，与四指已批准的 landmark 同类）
shift = 9.390 mm
TIP helper tail 仍按 0.30 × 前段远端指骨长度沿 distal tangent 延伸；use_deform = false
```

---

## 4. THUMB chain 最终几何（`STAGE5A_R2_THUMB_CHAIN_AUDIT.json`）

| 段 | 长度 | 与上段夹角 | 内部采样 | T-01 轴向跨度 | length/axial |
| --- | --- | --- | --- | --- | --- |
| CMC → MCP | 46.9437 mm | — | 14/14 内部 | — | — |
| MCP → IP | 27.6992 mm | 24.664° | 14/14 内部 | 27.274 mm | 1.016 |
| IP → TIP | 27.0608 mm | 25.375° | 14/14 内部 | 21.995 mm | 1.230 |

```
THUMB_CMC_TO_MCP_LENGTH_REASONABLE = true
THUMB_MCP_TO_IP_LENGTH_REASONABLE  = true
THUMB_IP_TO_TIP_LENGTH_REASONABLE  = true
THUMB_CHAIN_GEOMETRY               = PASS
```
判据（**不硬编码任何人体平均长度**）：每段长度必须 ≥ 其已批准 T-01 轴向跨度且 ≤ 1.6×
（投影只会缩短），相邻段夹角 ≤ 60°，且拇指 IP→TIP 的内部采样通过率必须 **不低于**
四个已获批准手指 DIP→TIP 段的实测最小值（自校准对照：四指实测 1.000，拇指 R2 实测 1.000）。
`THUMB_IP_R` 的 **head 完全未变**（delta 0.000000 mm）；其 tail（= fingertip landmark）
按链条关系必然随 `THUMB_TIP_R` 更新——这是 brief 允许的 representation 重算，不是关节移动。

---

## 5. 冻结关节零漂移（`STAGE5A_R2_FROZEN_JOINT_DRIFT_AUDIT.json`）

```
authorized to change : WRIST_R / INDEX_MCP_R / THUMB_CMC_R / THUMB_MCP_R / THUMB_TIP_R (+ 两个 tail 重算)
FROZEN_JOINT_DRIFT   = 0     （15 个未授权关节，head 逐位一致）
max frozen head delta = 3.725e-06 mm      tolerance = 1.0e-04 mm
tolerance reason      = float32-equivalent（两个 blend 的作者意图同源，残差只是浮点存储/往返）
```
即：INDEX_PIP/DIP/TIP、MIDDLE_*、RING_*、LITTLE_*、以及 THUMB_IP 的**关节位置零漂移**。

---

## 6. ⚠ 在 R2 期间发现的 Stage5A R1 遗留缺陷（R1 文件未动）

```
id = STAGE5A_R1_OBJECT_FRAME_OFFSET
```
R1 把骨骼坐标按 **world 值**写入，同时把 armature object 放在 ASSET object origin 上，
因此 R1 骨架在场景中整体偏离手部 **1448.359 mm**（正好一个 origin 向量）。
R1 的局部数值自洽（自审与渲染都以局部值显示），但**该 blend 里的骨架与手并不重合**。
R2 改为在 rig 自身的 object frame（= 手 mesh 的 object frame）中写入骨骼，
因此 R2 骨架与手几何重合。R1 blend **未被修改**（sha256 仍为 dd5f7265…）。

---

## 7. 局部轴 / roll

R1 的方法保留（`LOCAL_Y = head→tail`，`LOCAL_Z` = 投影后的 digit-local dorsal-like，`LOCAL_X = Y×Z`），
但**所有骨骼的 roll 都在 R2 重新 `align_roll` 计算，未复制任何 R1 数值**。

```
BONE_LOCAL_FRAME_ORTHONORMAL = PASS（每骨 |X|=|Y|=|Z|=1、正交、X = Y×Z，1e-5）
BONE_ROLL_CONTINUITY         = PASS（相邻局部 +Z 最大夹角 47.208°，容差 60°）
BONE_ROLL_180_FLIPS          = 0
```

---

## 8. 全部门禁（32 / 32 PASS）

```
PRODUCTION_BONE_COUNT = 21                BONE_NAME_SET_EXACT            HIERARCHY_EXACT
ASSET_ORIGIN_UNCHANGED                    PRODUCTION_WRIST_DECOUPLED_FROM_ASSET_ORIGIN
PRODUCTION_WRIST_INSIDE_MESH              PRODUCTION_WRIST_NOT_FOREARM_CAP
PRODUCTION_WRIST_NOT_PALM_CENTRE          WRIST_ROOT_LENGTH_SANITY_REPORTED = YES
INDEX_MCP_INSIDE                          INDEX_MCP_T01_AXIAL_REGION
THUMB_CMC_INSIDE                          THUMB_CMC_IN_APPROVED_CAGE_REGION
THUMB_CMC_NOT_SURFACE_ANCHOR_ONLY         THUMB_MCP_INSIDE
THUMB_MCP_T01_AXIAL_REGION                THUMB_IP_CARRY_FORWARD_VALID
THUMB_TIP_APEX_ALIGNMENT                  THUMB_CHAIN_GEOMETRY
JOINT_REGION_VALIDATION                   FROZEN_JOINT_DRIFT = 0
BONE_LOCAL_FRAME_ORTHONORMAL              BONE_ROLL_CONTINUITY
BONE_ROLL_180_FLIPS = 0                   MESH_VERTEX_DELTA = 0
MESH_TOPOLOGY_DELTA = 0                   UV_DELTA = 0
MATERIAL_ASSIGNMENT_DELTA = 0             MESH_PARENT = NONE
ARMATURE_MODIFIER = NONE                  VERTEX_GROUPS = NONE
PRODUCTION_SKIN_WEIGHT = NOT_STARTED
```

---

## 9. 冻结验证

```
Stage4C master  before = fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7
                after  = fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7  ✅
Stage5A R1      before = dd5f7265ea373579e9f77ecea2f74f0b2d0642a2bbb10795f1ddf5c17eb1486d
                after  = dd5f7265ea373579e9f77ecea2f74f0b2d0642a2bbb10795f1ddf5c17eb1486d  ✅
Stage5A R2 candidate   = 615367d7fab3e75431fa7171e7e82f3a655c62e29ad7ddca5509b093e9f68c81
mesh topology signature（artifact）= 5a39668418eea1716a0fd9bc20b3d0aeda67e6a49a343b74eb3e17c339f90c1d
V = 3416  E = 6828  F = 3414  TRIS = 6828   NAIL_BED 124 面 / HAND_SKIN 3290 面
rig object location = [1.408704638, 0.022395039, 0.335847497]（= ASSET origin，未改）
rig object rotation = [0,0,0]   scale = [1,1,1]
```

---

## 10. 正式 Human Review 证据图（10 张，`stage5a_r2/renders/`）

```
STAGE5A_R2_RIG_DORSAL.png                    STAGE5A_R2_RIG_PALMAR.png
STAGE5A_R2_RIG_DORSAL_OBLIQUE.png
STAGE5A_R2_WRIST_BEFORE_AFTER.png            同时显示：ASSET OBJECT ORIGIN / R1 WRIST_R / R2 PRODUCTION WRIST_R
                                             / 前臂截断面 / PALM REFERENCE，
                                             并明确标注 "ASSET ORIGIN != PRODUCTION WRIST JOINT"
STAGE5A_R2_INDEX_MCP_BEFORE_AFTER.png        R1 红点（皮肤外 0.26 mm）/ R2 橙点（剖面 medial 中心）
STAGE5A_R2_THUMB_CHAIN_BEFORE_AFTER.png      R1 thumb 链（灰诊断）/ R2 thumb 链（橙生产候选）/ THUMB_IP
STAGE5A_R2_THUMB_CMC_CLOSEUP.png             CMC 关节 + Stage-4A 批准笼区域球
STAGE5A_R2_THUMB_MCP_CLOSEUP.png             MCP 关节前后对照
STAGE5A_R2_THUMB_TIP_CLOSEUP.png             指尖 landmark 前后对照
STAGE5A_R2_LABELLED.png                      21 骨名称双列可核对
```
before / after 语义：**R1 = 灰色 diagnostic marker**，**R2 = 橙色 production candidate**。
临时文件只写 `stage5a_r2/_tmp/`；正式图只写 `stage5a_r2/renders/`；
全程未使用 glob / recursive / prefix wildcard 删除。

---

## 11. 产物清单

```
stage5a_r2/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2.blend
stage5a_r2/STAGE5A_R2_REPORT.md                          （本报告）
stage5a_r2/STAGE5A_R2_STATUS.json                        32 门禁 + 判定 + mesh 签名
stage5a_r2/STAGE5A_R2_JOINT_AUDIT.json                   同内容（审计入口）
stage5a_r2/STAGE5A_R2_PRODUCTION_JOINT_TABLE.json        21 关节：世界位置 / 依据 / 验证方法 / 状态 / R1 对照
stage5a_r2/STAGE5A_R2_BONE_FRAME_AUDIT.json              逐骨 head/tail/roll/local XYZ + 正交与 roll 门禁
stage5a_r2/STAGE5A_R2_THUMB_CHAIN_AUDIT.json             CMC/MCP/IP/TIP + 三段几何 + 自校准对照
stage5a_r2/STAGE5A_R2_WRIST_PROFILE.json                 WRIST_CANDIDATE_PROFILE（逐剖面全部量 + 候选评分）
stage5a_r2/STAGE5A_R2_FROZEN_JOINT_DRIFT_AUDIT.json      冻结关节漂移审计
stage5a_r2/renders/*.png                                 10 张正式图
stage5a_r2/_tmp/                                         全部只读取证（候选点、诊断、构建日志）
stage5a_r2/scripts/stage5a_r2_{candidates,diag,diag2,build,audit,render}.py
```

---

## 12. 本轮禁止事项（均未执行）

Skin Weight / automatic weights / vertex groups / mesh parenting / Armature modifier /
controllers / IK / constraints / animation / MediaPipe retarget / 左手 / GLB / Three.js /
Stage6 deformation test；**亦未**重做 Retopo / CMC cage / T-01 topology / RSSF pose / Nails / UV。

```
STAGE5A_R2 = READY_FOR_HUMAN_REVIEW        STAGE5B = NOT_STARTED
已停止。等待 Human Review。
```
