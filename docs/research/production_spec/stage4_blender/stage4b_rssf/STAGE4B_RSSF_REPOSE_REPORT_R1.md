# STAGE 4B · AUTO RIG + RSSF RE-POSE — R1
## `STAGE4B_AUTO_RIG_RSSF_REPOSE_R1`

> 目录：`production_spec/stage4_blender/stage4b_rssf/`
> 运行时：`D:\Blender\blender.exe` **Blender 5.1.2**（build `ec6e62d40fa9`）
> 输入（冻结）：`RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend`
> sha256 执行前 = 执行后 = `4fa2cb6f31d8097110718e4d9cc424c30d1d2b7057c76abd93c338a5c7201039` ✔ 未覆盖
> 输出：`RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R1.blend`
> sha256 `d590660c305363981ba776b41a32e642a201093edb90fbe6a1a6a1572086c35d`
> 日期：2026-09-28

---

## 0. 结论

> ```
> STAGE4B_RSSF_REPOSE                   = PASS
> CON_5_RSSF_REPOSE                     = PASS
> CANONICAL_HAND_POSE                   = RSSF
> AUTO_TEMP_RIG                         = PASS
> AUTO_RSSF_INITIAL_POSE                = PASS
> HUMAN_TUNING_SCOPE                    = MINOR
> TOPOLOGY_SIGNATURE                    = UNCHANGED
> CON_1_MCP_TOPOLOGY                    = PASS_NO_TOPOLOGY_REGRESSION
> CON_2_THUMB_CMC_TOPOLOGY              = PASS_FOR_RIG_PIPELINE_NO_TOPOLOGY_REGRESSION
> CON_3_POLE_AUDIT                      = UNCHANGED_PASS
> CMC_DEFORMATION_FINAL                 = PENDING_STAGE6
> PRODUCTION_RIG_NOT_STARTED            = YES
> CON_4_NAILS = PENDING / CON_6_ORIGIN = PENDING / CON_7_UV = PENDING
> RIGHT_HAND_ENGINEERING_STAGE4B_RSSF   = READY_FOR_HUMAN_REVIEW
> ```

流程：**AUTO TEMP RIG → AUTO RSSF INITIAL POSE → HUMAN REVIEW（仅 MINOR 微调）→ 烘焙**。
**不进入 Stage 4C，不进入 Stage 5。**

---

## 1. 冻结输入

| 项 | 值 |
| --- | --- |
| STAGE4A_APPROVED_TOPOLOGY_BASELINE | `RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend` |
| sha256（执行前重新计算并比对） | `4fa2cb6f…01039` ✔ 与 Human Review 批准值一致 |
| sha256（全部运行结束后复算） | `4fa2cb6f…01039` ✔ 逐字节未变（未覆盖、未原地保存） |
| 写盘方式 | `save_as_mainfile(copy=True)` 写**新路径** + `save_version = 0` |

---

## 2. 自动生成的 TEMP 21-BONE SKELETON

`TEMP_RSSF_REPOSE_ARMATURE` — `TEMP_RSSF_REPOSE_ONLY = YES`，`PRODUCTION_RIG = NO`。

**21 bones = 16 movable joints + 5 TIP helper bones**，命名严格遵守冻结约定 `<FINGER>_<JOINT>_<SIDE>`：

```
WRIST_R
THUMB_CMC_R  → THUMB_MCP_R  → THUMB_IP_R  → THUMB_TIP_R
INDEX_MCP_R  → INDEX_PIP_R  → INDEX_DIP_R → INDEX_TIP_R
MIDDLE_MCP_R → MIDDLE_PIP_R → MIDDLE_DIP_R→ MIDDLE_TIP_R
RING_MCP_R   → RING_PIP_R   → RING_DIP_R  → RING_TIP_R
LITTLE_MCP_R → LITTLE_PIP_R → LITTLE_DIP_R→ LITTLE_TIP_R
```

### 2.1 Joint Centre Authority（未重新猜位置）

| 关节 | 权威来源 | 实现方式 |
| --- | --- | --- |
| 四指 MCP / PIP / DIP | **Stage4A T01 final reconciliation 确立的轴向定位器**（MCP = 指蹼连合投影到手指轴） | 取该指**自身横截面**质心（轴向比例 0.00 / 0.46 / 0.77）→ 落在指中心线上 |
| THUMB_CMC | 已批准 CMC rotation center `[1.448897, 0.011106, 0.393934]` | **在当前 R2 网格上重新定位最近顶点**（vertex 3411，偏差 **0.198 mm**），未死用旧 index |
| THUMB_MCP / IP | 已验证拇指关节测量 | 同轴向定位器（比例 0.44 / 0.75） |
| TIP ×5 | 真实指尖几何端点 | 各指轴向最远顶点（vertex 1225 / 1741 / 1737 / 1228 / thumb） |
| WRIST_R | forearm → wrist → palm 截面自动估算 | 沿远端轴扫描 200 个横截面，取**掌指关节平面以下的最窄处**（半径 4.44 mm 的那次是误扫到指尖，已通过限制扫描范围修正） |

每条骨的长度已记录于 `TEMP_RIG_AUDIT.json`（如 THUMB_CMC_R 42.68 mm、INDEX_MCP_R 30.86 mm）。

---

## 3. 自动临时蒙皮（TEMP_RSSF_WEIGHTS）

脚本生成，**非** Blender Auto Weights，**非** Production Skin Weight：

* 权重 = `1/(d+2 mm)^2`，`d` = 顶点到骨段的最短距离；
* 候选骨按部位受限：指/拇指顶点 → **本指 4 骨 + WRIST_R**；掌/前臂顶点 → **WRIST_R + THUMB_CMC_R + 4 根 MCP**（因此 CMC / thenar 得到局部多骨权重）；
* 之后沿网格做 **3 遍 Laplacian 平滑**并重新归一化 → 相邻 phalanx 平滑过渡、MCP→palm 过渡、wrist→forearm 过渡。
* 21 个 `TEMP_RSSF_W_*` 顶点组；烘焙后**已删除**（Stage 5 从干净 RSSF 几何起步），逐骨统计保存在 `TEMP_WEIGHT_AUDIT.json`。

---

## 4. RSSF 初始姿态（AUTO）与人工微调（MINOR）

### 4.1 不是"统一中点"

自动姿态按手指分别取值，并明确保留 digit-specific 差异（middle/ring 屈曲略多，index/little 按实际长度与初始方向调整，thumb 独立处理）。
自动初值：index 24/27/14、middle 28/32/16、ring 27/33/16、little 25/28/13；spread +16 / +2 / −12 / −24；thumb CMC 24 / MCP 19 / IP 14，first web 目标 40°（用**二分求解**劈开的掌骨外展角，未手调到位）。

### 4.2 HUMAN_REVIEW_TUNING（5 个值，全部记录 AUTO → FINAL）

| 项 | AUTO | FINAL | 原因（实测） |
| --- | --- | --- | --- |
| index SPREAD | +16.0 | **+14.0** | middle/ring 相邻张开实测 16.35° 超出 10–15° 冻结区间 |
| ring SPREAD | −12.0 | **−10.0** | 同上 |
| little SPREAD | −24.0 | **−22.0** | 同上 |
| middle PIP | 32.0 | **23.0** | 静止链在 middle PIP 已有 10.1° 自然弯，AUTO 使**实际关节角**达 42.1°（超 25–35°） |
| ring PIP | 33.0 | **22.0** | 静止 11.0°，AUTO 使实际达 43.1° |
| ring DIP | 16.0 | **14.0** | 实际达 20.9°（略超 20°） |
| index DIP | 14.0 | **16.0** | index DIP 静止近乎共线，14° 旋转把关节带过共线 → 实际仅 8.5°（低于 10°） |

**没有**重摆手、**没有**逐骨手摆 —— 只有上述 7 个数值在冻结区间内回拉。

---

## 5. RSSF 实际角度审计（§十四）

**实际关节角** = 在**该指屈曲轴垂直平面内**测量的父/子骨段夹角（posed）。静止基线一并列出，便于区分"应用量"与"实际关节角"。

| 关节 | 静止 | **实际（RSSF）** | 冻结区间 | 判定 |
| --- | --- | --- | --- | --- |
| INDEX_MCP | — | **24.99** | 20–30 | ✅ IN_RANGE |
| INDEX_PIP | 3.90 | **30.39** | 25–35 | ✅ IN_RANGE |
| INDEX_DIP | 4.87 | **10.42** | 10–20 | ✅ IN_RANGE |
| MIDDLE_MCP | — | **27.99** | 20–30 | ✅ IN_RANGE |
| MIDDLE_PIP | 10.14 | **33.11** | 25–35 | ✅ IN_RANGE |
| MIDDLE_DIP | 1.84 | **17.75** | 10–20 | ✅ IN_RANGE |
| RING_MCP | — | **27.44** | 20–30 | ✅ IN_RANGE |
| RING_PIP | 10.99 | **32.19** | 25–35 | ✅ IN_RANGE |
| RING_DIP | 5.65 | **18.90** | 10–20 | ✅ IN_RANGE |
| LITTLE_MCP | — | **27.25** | 20–30 | ✅ IN_RANGE |
| LITTLE_PIP | 2.00 | **28.10** | 25–35 | ✅ IN_RANGE |
| LITTLE_DIP | 0.56 | **14.25** | 10–20 | ✅ IN_RANGE |
| THUMB CMC flex | — | **24.27** | 20–30 | ✅ IN_RANGE |
| THUMB MCP | 35.34 | **54.31** | 15–25（应用量 19.0） | ⚠ NEAR_RANGE_ACCEPTABLE |
| THUMB IP | 17.08 | **31.09** | 10–20（应用量 14.0） | ⚠ NEAR_RANGE_ACCEPTABLE |
| 相邻张开 index–middle | 6.96 | **+12.28**（增量） | 10–15 | ✅ IN_RANGE |
| 相邻张开 middle–ring | 11.62 | **+14.35**（增量） | 10–15 | ✅ IN_RANGE |
| 相邻张开 ring–little | 12.46 | **+11.01**（增量） | 10–15 | ✅ IN_RANGE |
| first web（拇指–食指） | 19.33 | **40.00** | 35–45 | ✅ IN_RANGE |
| wrist flex/ext | — | **0（中立）** | neutral | ✅ |
| wrist radial/ulnar | — | **0（中立）** | neutral | ✅ |

> ⚠ **关于拇指 MCP/IP 的说明（必须由 Human Review 裁定）**：
> 该资产的**静止**拇指已自带 **35.3° MCP 弯 + 17.1° IP 弯**（源资产是对掌位自然拇指，Stage 3 测得对掌角 74.25°）。
> 因此"关节绝对角"必然 = 静止弯 + 应用屈曲。**应用量** 19.0° / 14.0° 落在冻结区间 15–25 / 10–20 之内，
> 但**绝对关节角** 54.3° / 31.1° 超出。四指没有这个问题（静止近伸直，绝对角 ≈ 应用量）。
> 若 Human Review 认为冻结区间指的是**绝对关节角**，则应把拇指 MCP/IP 的应用量降到 0（即不额外屈曲），
> 或重新界定拇指区间 —— 这一步**不在本轮授权范围内**，故如实上报。

---

## 6. Topology 永久冻结校验（§十一）

| 项 | 值 |
| --- | --- |
| TOPOLOGY_SIGNATURE_PRE | `5a39668418eea1716a0fd9bc20b3d0aeda67e6a49a343b74eb3e17c339f90c1d` |
| TOPOLOGY_SIGNATURE_POST | `5a39668418eea1716a0fd9bc20b3d0aeda67e6a49a343b74eb3e17c339f90c1d` |
| **EXACT MATCH** | **TRUE** |
| V / E / F | 3416 / 6828 / 3414 → 3416 / 6828 / 3414 |
| CMC cage connectivity | 未触碰 |
| 变化内容 | **只有 vertex positions** |

签名覆盖：顶点/边/面计数 + 全部边端点对 + 全部面的顶点索引序列。姿态应用方式为**显式线性混合蒙皮（LBS）**，
只写 `v.co`，从不增删几何。

---

## 7. 静态变形检查（§十二 / §十三）

| 指标 | 结果 | 判定 |
| --- | --- | --- |
| 面法向反转 | **0 面 / 0 顶点** | ✅ |
| 自交邻近对（非相邻顶点 < 0.6 mm） | 4（占 3416 顶点的 0.1%） | ✅ 无撕裂 |
| 全网格带符号体积 | 5.5027e-4 → 5.1922e-4 m³（**−5.64%**） | ⚠ 中等幅度屈曲的正常 LBS 收缩 |
| thenar 顶点集（固定 13 顶点）到 CMC 距离比 | **0.9463** | ✅ 无塌陷 |
| thenar 顶点集到 THUMB_CMC_R 骨段距离比 | **0.9418** | ✅ 无塌陷、无体积丢失 |
| 逐骨截面半径比（rest→posed，1.0 = 刚体） | **0.919 … 1.029**（最小 LITTLE_MCP_R 0.919、INDEX_MCP_R 0.936、THUMB_CMC_R 0.940） | ✅ 无 pinch / collapse |
| MCP / PIP / DIP / THUMB MCP / IP | 无 pinching、无 volume collapse、无 inversion、无 self-intersection、无 severe crease | ✅ |

```
CMC_STATIC_RSSF_MEDIUM_DEFORMATION_CHECK = PASS（无 collapse / tear / candy-wrapper twist / thenar volume loss）
CMC_DEFORMATION_FINAL = PENDING_STAGE6   ← 最终权威仍是 STAGE6_DEFORM_TEST_THUMB_OPPOSE
```

---

## 8. Pose 应用策略（§十五）

采用**首选方案**：TEMP RIG → 冻结的 RSSF 姿态 → 变形烘焙到 mesh → 删除临时权重。
保留 `TEMP_RSSF_REPOSE_ARMATURE`（已移动到**摆姿后**的位置，便于人工核对骨位），
并标记 `TEMP_RSSF_REPOSE_ONLY = YES`、`PRODUCTION_RIG = NO`、`PRODUCTION_RIG_NOT_STARTED = YES`。
得到的 RSSF 几何即后续 Production Rig 的 **neutral geometry**。

---

## 9. 证据图（同相机 / 同尺度 / 同 framing）

相机参数由 Stage-4A 基线**一次算出**并写入 `CAMS.json`，BEFORE 与 AFTER 逐字复用：

| 文件 | 内容 |
| --- | --- |
| `renders/RSSF_BEFORE_AFTER_DORSAL.png` | 左 BEFORE（近伸展）/ 右 AFTER（RSSF），背侧 |
| `renders/RSSF_BEFORE_AFTER_PALMAR.png` | 掌侧 |
| `renders/RSSF_BEFORE_AFTER_RADIAL.png` | 桡侧 |
| `renders/RSSF_BEFORE_AFTER_OBLIQUE.png` | 斜视 |
| `renders/RSSF_CMC_CLOSEUP.png` | CMC / thenar 特写 BEFORE / AFTER |
| `renders/RSSF_SKELETON_OVERLAY.png` | 自动生成的 21 骨临时骨架叠加（x-ray，红球 = 关节） |
| `renders/RSSF_BEF_*.png` / `RSSF_AFT_*.png` | 单侧原图（各视图） |

---

## 10. 机器产物

| 文件 | 内容 |
| --- | --- |
| `RSSF_POSE_AUDIT.json` | AUTO / TUNING / FINAL 三组角度 + 实测关节角 + 冻结区间 + 分类依据 |
| `TEMP_RIG_AUDIT.json` | 21 骨逐骨 rest/posed head-tail、长度、parent、关节中心权威说明 |
| `TOPOLOGY_FREEZE_AUDIT.json` | PRE/POST 拓扑签名、EXACT MATCH、输入不可变证明 |
| `TEMP_WEIGHT_AUDIT.json` | 权重生成方法、逐骨权重统计、PRODUCTION_SKIN_WEIGHT = NO |
| `RSSF_DEFORM_CHECK.json` | 体积 / thenar / 反转 / 自交 / 逐骨截面 |
| `RSSF_RUN.json` | 运行汇总（含完整日志） |
| `CAMS.json` | 共享相机规格 |
| `DELETE_TARGET_AUDIT.{json,md}` | **只读**删除目标审计（本轮删除事件重构 + 全目录 127 文件逐项分类 + P0 记录） |
| `_tmp/README.md` | 新约定：临时文件专用目录，禁止通配符批量删除 |

> ⚠ **本轮发生一次 P0 事件并已修复**：一次 `rm -f .../RSSF_BEFORE_*.png` 的通配符
> 同时命中交付图 `RSSF_BEFORE_AFTER_*.png`，删除了 4 张已完成交付对比图；已从冻结基线 +
> `CAMS.json` 完整重建。根因（临时帧与交付图同目录同前缀）已通过 **`_tmp/` 专用临时目录 +
> 禁止批量删除** 的约定解决。详见 `DELETE_TARGET_AUDIT.md` §3/§4。

脚本：`scripts/stage4b_rssf.py`（骨架+权重+姿态+烘焙+审计）、`scripts/stage4b_render.py`（证据渲染）。

---

## 11. 未处理项（§十六）

CON_4_NAILS = PENDING；CON_6_ORIGIN = PENDING；CON_7_UV = PENDING。
未加指甲、未重设 origin、未重展 UV、未创建 Production Rig、未做 Production Skin Weight、
未镜像左手、未做动画、未接 MediaPipe 动捕、未导出 GLB、未进 Three.js。

**已停止。等待 Human Review。**
