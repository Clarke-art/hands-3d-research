# STAGE4B_RSSF_POSE_SEMANTIC_CORRECTION_R2

**任务**：`STAGE4B_RSSF_POSE_SEMANTIC_CORRECTION_R2`（RSSF 姿态语义修正）
**冻结输入**：`RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend`
`sha256 4fa2cb6f31d8097110718e4d9cc424c30d1d2b7057c76abd93c338a5c7201039` ✓（执行前后一致）
**运行时**：`D:\Blender\blender.exe`（Blender 5.1.2）
**原则**：从冻结 Stage-4A 基线**重新生成**，未在已 bake 的 R1 geometry 上叠加修正。R1 产物原样保留作 provenance。

---

## 0. 结论

```
STAGE4B_RSSF_REPOSE_R2              = PASS
CON_5_RSSF_REPOSE                   = PASS
CANONICAL_HAND_POSE                 = RSSF
VALIDATION_SEMANTICS                = FINAL_ABSOLUTE_ANGLE
HUMAN_TUNING_SCOPE                  = NONE
TOPOLOGY_SIGNATURE                  = UNCHANGED
CMC_DEFORMATION_FINAL               = PENDING_STAGE6
RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R2 = READY_FOR_HUMAN_REVIEW
```

**全部 21 项 FINAL ABSOLUTE 指标 = IN_TECHNICAL_RANGE；OUT_OF_RANGE = 0。**

---

## 1. 语义修正：技术范围一律解释为 FINAL ABSOLUTE POSE（§二）

从本轮起，所有 RSSF 技术范围统一约束 **最终绝对关节角 / 绝对邻指夹角**：

- 不使用 `delta from source`；
- 不使用 `applied rotation`；
- applied rotation 只作诊断字段。

**做法**：新增 `VALIDATION_SEMANTICS = FINAL_ABSOLUTE_ANGLE`，并把机读审计拆成三组**明确分离**的字段：

| 字段 | 含义 | 是否作验收依据 |
| --- | --- | --- |
| `AUTO_RSSF_INITIAL_VALUES` | 自动求解器输出（applied rotation + 目标），**非 null** | 否（记录） |
| `APPLIED_ROTATION_VALUES` | 逐骨 local rotation 幅值，`acos((trace-1)/2)` | **否，仅诊断** |
| `FINAL_ABSOLUTE_POSE_VALUES` | 最终姿态的**绝对角**，逐项带 range 与 status | **是（唯一权威）** |

另加 `validation_authority = FINAL_ABSOLUTE_POSE_VALUES`、`diagnostic_only = [APPLIED_ROTATION_VALUES, change_deg, rest_deg]`。

---

## 2. R1 → R2 修正内容（§四、§五）

### 2.1 邻指 spread（原判据错误地用了 CHANGE）

| 项 | R1 绝对角 | R2 绝对角 | 冻结范围 | 状态 |
| --- | --- | --- | --- | --- |
| INDEX–MIDDLE | 19.24° | **12.00°** | 10–15° | IN_TECHNICAL_RANGE |
| MIDDLE–RING | 25.97° | **13.00°** | 10–15° | IN_TECHNICAL_RANGE |
| RING–LITTLE | 23.47° | **12.00°** | 10–15° | IN_TECHNICAL_RANGE |

三组**不是**同一个值（12 / 13 / 12），是自动求解成自然轻度扇形，不是机械等分，也不是 display-hand fan。

自动求解出的 applied spread：`index +4.758° / middle 0.000° / ring +0.974° / little +0.444°`。
（R1 是 `+14 / +2 / −10 / −22` —— 差分才是超额部分的来源。）

### 2.2 Thumb（原判据错误地用了 applied rotation）

| 项 | source/rest | R1 绝对角 | R2 绝对角 | 冻结范围 | R2 applied |
| --- | --- | --- | --- | --- | --- |
| THUMB CMC | — | 24.27° | **27.70°** | 20–30° | CMC_FLEX 24.0°（未改） |
| THUMB MCP | 35.34° | 54.31° | **22.00°** | 15–25° | **−13.182°（EXTENSION）** |
| THUMB IP | 17.08° | 31.09° | **17.84°** | 10–20° | **0.000°（不动）** |
| first web | 19.33° | 40.00° | **40.00°** | 35–45° | CMC_ABDUCT +9.435° |

- **THUMB MCP**：静止已带 35.34° 自然弯，范围是 15–25°，因此需要**相对 source 做 EXTENSION**。R1 反而加了 +19° flexion → 54.31°。R2 自动求解为 **−13.182°** → 22.00°。
- **THUMB IP**：rest 17.08° 已落在范围内（且落在优选的 15–19° 子区间）→ **不再加 14°**，applied = 0。
  注意：**最终绝对读数是 17.84°，不是 17.08°**。测量平面在世界空间固定，CMC 外展施加后读数会有小幅移动；报告与机读字段都使用**实测的 17.84°**，不使用假设值。
- **THUMB CMC**：applied `CMC_FLEX` **未改（24.0°）**；绝对读数 24.27° → 27.70° 是因为 first web 求解出的 CMC_ABDUCT 从 R1 的 +1.14° 变成 **+9.435°**（见 §3 的耦合说明）。仍在 20–30°。

### 2.3 四指 flexion（按指令保持不变）

applied flexion **一字未改**（index 24/27/16、middle 28/23/16、ring 27/22/14、little 25/28/13）。
但 spread 修正会产生**必要的小连带变化**（测量平面的投影效应），逐项如下：

| 关节 | R1 绝对 | R2 绝对 | Δ | 冻结范围 |
| --- | --- | --- | --- | --- |
| INDEX MCP / PIP / DIP | 24.99 / 30.39 / 10.42 | 24.09 / 30.77 / 10.95 | −0.90 / +0.38 / +0.53 | 20–30 / 25–35 / 10–20 |
| MIDDLE MCP / PIP / DIP | 27.99 / 33.11 / 17.75 | 27.95 / 33.14 / 17.84 | −0.04 / +0.03 / +0.09 | 同上 |
| RING MCP / PIP / DIP | 27.44 / 32.19 / 18.90 | 26.71 / 33.06 / 19.70 | −0.73 / +0.87 / +0.80 | 同上 |
| LITTLE MCP / PIP / DIP | 27.25 / 28.10 / 14.25 | 24.94 / 30.03 / 13.53 | −2.31 / +1.93 / −0.72 | 同上 |

**全部 Δ ≤ 2.31°，全部仍在冻结范围内。**

---

## 3. 一处必须说明的耦合：first web → CMC abduction

`first web` 的测量对象是「第一掌骨方向」与「食指近节方向」之间的角。
R2 把食指 spread 从 +14° 降到 +4.758°，食指方向随之转向，**该夹角随之变小**。
要把 web 保持在冻结的 40°（R1 已是 40°，指令要求保持），就必须由 **CMC 外展**补偿：

```
CMC_ABDUCT:  R1 +1.14°  ->  R2 +9.435°   (web 40.00° 保持)
```

这是本轮唯一的跨项连带，已在 `R1_TO_R2_CORRECTION` 中记录。若不补偿，web 会掉出 35–45° 区间。

---

## 4. 逐项验收（§十二）—— 全部 IN_TECHNICAL_RANGE

```
ADJACENT_SPREAD_INDEX_MIDDLE   12.00   [10,15]   IN_TECHNICAL_RANGE
ADJACENT_SPREAD_MIDDLE_RING    13.00   [10,15]   IN_TECHNICAL_RANGE
ADJACENT_SPREAD_RING_LITTLE    12.00   [10,15]   IN_TECHNICAL_RANGE
FIRST_WEB                      40.00   [35,45]   IN_TECHNICAL_RANGE
INDEX_MCP / PIP / DIP    24.09 / 30.77 / 10.95   IN_TECHNICAL_RANGE
MIDDLE_MCP / PIP / DIP   27.95 / 33.14 / 17.84   IN_TECHNICAL_RANGE
RING_MCP / PIP / DIP     26.71 / 33.06 / 19.70   IN_TECHNICAL_RANGE
LITTLE_MCP / PIP / DIP   24.94 / 30.03 / 13.53   IN_TECHNICAL_RANGE
THUMB_CMC                      27.70   [20,30]   IN_TECHNICAL_RANGE
THUMB_MCP                      22.00   [15,25]   IN_TECHNICAL_RANGE
THUMB_IP                       17.84   [10,20]   IN_TECHNICAL_RANGE
WRIST_flex_ext / radial_ulnar   0.00   neutral   IN_TECHNICAL_RANGE
```

`21 items | not strictly in range: 0 | out of range: 0`

---

## 5. Human tuning（§七）— 机器/报告一致性

```
AUTO_RSSF_R2_VALUE  ->  FINAL_R2_VALUE
TUNING_DIFF.count   =  0
TUNING_DIFF.items   =  []
HUMAN_TUNING_SCOPE  =  NONE
```

自动解**一次就全部落进冻结区间**，因此没有做人工微调。
`TUNING_DIFF` 由程序对 `AUTO_RSSF_INITIAL_VALUES` 与 `FINAL_RSSF_VALUES` 做 **dotted-path 全量 diff** 得出，**不是手写数字**——因此上一轮「写 MINOR（3 项）实际改了 7 项」这类机读/报告不一致在本轮结构上不可能再发生。

---

## 6. 冻结项核对（§九）

```
TOPOLOGY_SIGNATURE_PRE = POST = 5a39668418eea1716a0fd9bc20b3d0aeda67e6a49a343b74eb3e17c339f90c1d
TOPOLOGY_SIGNATURE_MATCH = True
V 3416 -> 3416 | E 6828 -> 6828 | F 3414 -> 3414   （只有顶点位置改变）
TOPOLOGY_SIGNATURE = UNCHANGED
CMC cage topology  = UNCHANGED
TEMP rig semantic skeleton = 同一 21 骨定义（16 可动 + 5 TIP）
PRODUCTION_RIG_NOT_STARTED = YES   TEMP_RSSF_REPOSE_ONLY = YES
input sha256 before = after = 4fa2cb6f…01039   （冻结输入未被改写）
```

未做：Retopo / 改 CMC cage / 加指甲 / 改 UV / 改 origin / Production Rig / 镜像左手 / 动画。

---

## 7. 静态变形检查 R2（§十）

| 指标 | R1 | R2 | 判定 |
| --- | --- | --- | --- |
| flipped faces / vertices | 0 / 0 | **0 / 0** | PASS |
| self-intersection proximity pairs (<0.6 mm, 非邻接) | 4 | **3** | 无严重自交 |
| signed volume Δ | −5.642% | **−3.642%** | 无塌陷 |
| thenar 厚度（到 CMC / 到拇指骨，固定顶点集） | 0.946 / 0.942 | **1.036 / 1.066** | 无 thenar 塌陷 |
| 最小逐骨截面比（1.0 = 刚性） | 0.919 | **0.925** | 无 pinch / collapse |

逐骨截面比全部落在 0.925–1.029；无 MCP/PIP/DIP collapse、无 thenar collapse、无 first-web 变形。

```
CMC_DEFORMATION_FINAL = PENDING_STAGE6
FINAL_CMC_DEFORMATION_AUTHORITY = STAGE6_DEFORM_TEST_THUMB_OPPOSE
```

本轮仅为 **STATIC RSSF MEDIUM-DEFORMATION CHECK**，不宣称最终功能通过。

---

## 8. 证据图（§十一）— 与 R1 同相机（同一 `CAMS.json`）

```
renders/RSSF_R2_BEFORE_AFTER_DORSAL.png
renders/RSSF_R2_BEFORE_AFTER_PALMAR.png
renders/RSSF_R2_BEFORE_AFTER_RADIAL.png
renders/RSSF_R2_BEFORE_AFTER_OBLIQUE.png
renders/RSSF_R2_CMC_CLOSEUP.png
```

BEFORE = 冻结 Stage-4A 基线；AFTER = R2 RSSF 姿态。同相机、同尺度、同 framing。

**临时单侧帧只写 `stage4b_rssf/_tmp/r2/`，未写入 `renders/`。**
新增交付名已显式加入 `scripts/stage4b_render.py` 的**精确文件名白名单**（`FINAL_ALLOWED`），护栏未被放宽成模式匹配。

**视觉核对**：
- 邻指间距：R2 明显收拢，R1 的 display-hand fan 已消除；
- ring / little：无外翻过度；
- thumb：MCP 从 54.31° 降到 22.00°、IP 从 31.09° 降到 17.84°，**过度蜷曲已消除**；
- 掌弓保持；四指呈柔和连续弧线；无 claw、无 grasp、无 robotic 等角姿态。

像素级佐证：R2 AFTER 与 R1 AFTER 帧在 OBLIQUE 视角有 212,729 个像素不同（≈18%），DORSAL 231,279 个——姿态确实改变，不是渲染缓存。

---

## 9. 产物清单

```
stage4b_rssf/RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R2.blend   sha256 78fc890bfa9575cd62f2ae5f55beb2eda2df7ebf565c4e346a8b5af7295bbe04
  1,988,085 B（两次独立运行哈希一致 → 可复现）
stage4b_rssf/STAGE4B_RSSF_REPOSE_REPORT_R2.md               (本报告)
stage4b_rssf/RSSF_POSE_AUDIT_R2.json                        (三组分离 + VALIDATION_SEMANTICS)
stage4b_rssf/RSSF_DEFORM_CHECK_R2.json
stage4b_rssf/TEMP_RIG_AUDIT_R2.json
stage4b_rssf/TEMP_WEIGHT_AUDIT_R2.json
stage4b_rssf/TOPOLOGY_FREEZE_AUDIT_R2.json
stage4b_rssf/RSSF_RUN_R2.json                               (含完整日志)
stage4b_rssf/renders/RSSF_R2_{BEFORE_AFTER_*,CMC_CLOSEUP}.png
scripts/stage4b_rssf_r2.py                                  (R2 管线，可逐字节复现)
```

**R1 产物全部保留未改动**：`RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R1.blend`（`d590660c…c35d`）及其审计与证据图。

---

## 10. 最终状态（§十二）

```
STAGE4B_RSSF_REPOSE_R2 = PASS
CON_5_RSSF_REPOSE = PASS
CANONICAL_HAND_POSE = RSSF
VALIDATION_SEMANTICS = FINAL_ABSOLUTE_ANGLE
HUMAN_TUNING_SCOPE = NONE
TOPOLOGY_SIGNATURE = UNCHANGED
CMC_DEFORMATION_FINAL = PENDING_STAGE6
RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R2 = READY_FOR_HUMAN_REVIEW
```

**已停止。未进入 Stage4C。未进入 Stage5。等待 Human Review。**
