# STAGE5B_R1B 报告 · THUMB MCP / IP 窄域过渡带权重重修

- **round**：`STAGE5B_R1B_THUMB_MCP_IP_NARROW_WEIGHT_REPAIR`
- **generated**：2026-09-30
- **status**：`CANDIDATE_FOR_HUMAN_REVIEW`（**不是** `FINAL_APPROVED`）
- **scope**：**仅 SKIN WEIGHT**。未改动 mesh geometry / topology / vertex position / UV /
  material / nail face assignment / bone position / bone head-tail / roll / hierarchy /
  bone count / CMC cage / RSSF geometry / THUMB_TIP authority / distal-cap semantic /
  object origin。未 retopo。未移动 `THUMB_IP_R` / `THUMB_MCP_R` joint。
- **stage6b**：`NOT_STARTED`

---

## 一、输入 / 输出与冻结

| 角色 | 文件 | SHA-256 |
|---|---|---|
| 输入（FROZEN_PROVENANCE） | `stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend` | `c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6` |
| 输出（本轮候选） | `stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend` | `cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10` |

- 执行前 / 后 **R1A SHA-256 完全未变**（`unchanged_after = True`）。
- **R1A 仍是 Stage5B 的 `FINAL_APPROVED` master**；`stage5b_freeze/` 收据**未被触碰**，
  其中 `active_stage5b_master.sha256` 仍指向 R1A。
- `.blend` 容器字节不具备跨环境可复现性（携带会话元数据）；**同一冻结脚本连续两次运行
  产出字节相同的产物**（已实测）。真正被验证的是**载荷**：见 §六 独立后验证。

---

## 二、根因（先诊断，后修改）

`STAGE6A_R1A_THUMB_TRANSITION_ROOT_CAUSE.json`（READ-ONLY 诊断，未写入任何 blend）：

**分类 = `A_WEIGHT_TRANSITION`**（6/6 thumb case 一致）。

决定性的机制发现：

```
R1A 的纵向权重用了「单侧斜坡」：
    A_IP  = smoothstep((s - s_IP ) / (1 x MED))
    A_MCP = smoothstep((s - s_MCP) / (1 x MED)) - A_IP
=> 在关节弧长 s = s_joint 处该骨权重恰好为 0，整条过渡带完全落在关节「远端」一侧。
```

数值证据：

| 量 | 值 |
|---|---|
| `MED`（网格中位边长） | **3.888205 mm** |
| R1A 名义过渡跨度 `2 x MED` | 7.776410 mm |
| **R1A 实测 full-MCP → full-IP 弧长跨度** | **3.886146 mm ＝ 恰好 1 条网格边** |
| `TH_IP_30` 最差面 #1191 顶点弧长 | 71.882（MCP 1.000） / 75.196（IP 0.941） / 71.882（MCP 1.000） / 75.331（IP 0.965） |

即：**整个 IP 权重梯度必须由一条 3.9 mm 的网格边承担**，30°/45° 屈曲下该面被压塌。
`TH_IP_30 min face-area ratio = 0.054027`、`TH_IP_45 = 0.019443` 由此而来。

被排除的其它归因：

- **B. topology density**：拓扑为统一 100% quad，关节带可在纵向解析出 **5 个 ring**，
  只要把混合铺开就足够 —— 密度不是限制项。
- **C. pose collision**：intra-thumb 最差 pair 的纵向 ring 间隔为 0–1（同一褶皱内），
  不是远距离表面自接触。
- **D. metric artefact**：最差面 baseline 面积 1.616e-05 m²，与 patch 中位 1.544e-05 m²
  同量级，比值未被小分母放大。

诊断另确认：THUMB↔INDEX 跨指碰撞属 **姿态级**（RSSF 绑定下拇指远端与食指 MCP 最小链距
3.28 mm），**不是** weight 缺陷，本轮不作为优化目标（沿用 `POSE_CONSTRAINT_DIAGNOSTIC`）。

---

## 三、授权 region 与允许修改的 bone group

```
AUTHORISED_THUMB_REPAIR_REGION =
    ( THUMB_MCP local deformation patch
      UNION THUMB_IP local deformation patch )
    + 最多 2 个 topology ring
    限制：仅 thumb-owned 顶点
    排除并冻结：approved distal-cap 顶点 / nail semantic 顶点 / sanctioned first-web 顶点
```

| 项 | 值 |
|---|---|
| core patch union | 202 |
| 2-ring closure | 411 |
| thumb-owned 部分 | 364 |
| 冻结排除 | 88（nail 20 + first-web 21 + 其它非 thumb-owned） |
| **最终授权顶点数** | **323** |
| 授权弧长范围 | 24.513 – 87.313 mm |
| ring 外扩 | 2（未突破，**未发生 FAIL CLOSED**） |

允许**重新分配**的组（仅此 4 个）：`WRIST_R`、`THUMB_CMC_R`、`THUMB_MCP_R`、`THUMB_IP_R`。
**禁止**改动：`INDEX_*`、`MIDDLE_*`、`RING_*`、`LITTLE_*`（本轮**逐顶点 0 漂移**，见 §五）。

---

## 四、候选搜索与选定

方法：**确定性局部权重重建**，纵向坐标一律使用
`APPROVED_JOINT_POLYLINE_ARC_LENGTH`（**未**使用 `GLOBAL_SURFACE_GEODESIC_FROM_DISTAL_TIP`）。
**无任何逐顶点自由参数**。

候选族（全局可复现参数）：

```
form      : centered | onesided
W_IP      : IP 过渡半宽（单位 MED）
W_MCP     : MCP 过渡半宽（单位 MED）
W_BASE    : CMC/WRIST base 过渡半宽（单位 MED）
shift_IP  : IP 斜坡中心偏移（单位 MED）
shift_MCP : MCP 斜坡中心偏移（单位 MED）
profile   : smoothstep | quintic | cosine
```

**关节居中（joint-centred）形式**：

```
u     = prof(0.5 + (s - s_IP  - shift_IP ) / (2*W_IP ))
vbase = 1 - prof(0.5 + (s - s_MCP - shift_MCP) / (2*W_BASE))
A_IP  = u ,  A_BASE = vbase ,  A_MCP = clamp(1 - u - vbase)

`form = onesided` 精确复现 R1A 原式 —— 用作引擎校验。
```

**引擎校验（关键前置门）**：

| 校验 | 结果 |
|---|---|
| R1A 参数复算权重最大漂移 | `2.879e-08`（float32 存储分辨率内） |
| float32 精确不一致数 | **0** |
| **R1A 配置复算指标 vs Stage6A R1 实测** | **EXACT**（6 case × 4 指标 × intra 计数全等） |

**扫描规模**：Stage A 288 + Stage B 87 = **375 个候选**，全部记录于
`stage6a_r1a/STAGE6A_R1A_THUMB_WEIGHT_CANDIDATE_RANKING.json`。

**接受逻辑（baseline-relative，绝不引入新的人体平均阈值）**：

```
A. TH_IP_30 / TH_IP_45 min face-area ratio 严格优于 R1
B. TH_IP_30 / TH_IP_45 face-area p05       严格优于 R1
C. TH_IP_30 / TH_IP_45 max edge stretch    不得增加
D. TH_IP_30 / TH_IP_45 intra-thumb 自交    不得增加
E. TH_MCP_45  在 face-area / edge-stretch / intra-thumb 上不得整体退化
F. 不得牺牲 15° / 30°
硬门：NaN/Inf=0、collapsed face=0、degenerate edge=0、topology delta=0、
      unweighted vertex=0、max influences<=4、normalization PASS、
      non-target clean drift 处于噪声底
```

**筛选结果**：375 中 **172** 满足 A–F + 全部硬门；其中 **91** 个四项必需改善均 ≥ **+25%**
（"清晰 Pareto 改善"门槛）。**0 个**候选能在全部受限 case 上同时不退化 `min_edge_ratio`
—— 这是一条**真实的单目标代价**，已在 §七 如实列出。

### 选中候选

```
form = centered
W_IP = 5.0 x MED = 19.4410 mm 半宽   (full span 38.882 mm)
W_MCP = 1.0 x MED = 3.8882 mm 半宽
W_BASE = 3.0 x MED = 11.6646 mm 半宽 (full span 23.329 mm)
shift_IP = 0.0 , shift_MCP = 0.0
profile = quintic
```

过渡剖面（IP / MCP / BASE 权重 vs 弧长）：

| arc (mm) | R1A (IP, MCP, BASE) | R1B (IP, MCP, BASE) |
|---|---|---|
| 27.7 | 0.0000, 0.0000, 1.0000 | 0.0000, 0.0000, 1.0000 |
| 42.7 （MCP 关节） | 0.0000, 0.0000, 1.0000 | 0.0000, **0.5000**, 0.5000 |
| 57.3 | 0.0000, 1.0000, 0.0000 | 0.0159, 0.9841, 0.0000 |
| 64.9 | 0.0000, 1.0000, 0.0000 | 0.1905, 0.8095, 0.0000 |
| 71.9 （IP 关节） | **0.0000**, 1.0000, 0.0000 | **0.5000**, 0.5000, 0.0000 |
| 78.9 | 1.0000, 0.0000, 0.0000 | 0.8095, 0.1905, 0.0000 |
| 93.9 （TIP） | 1.0000, 0.0000, 0.0000 | 1.0000, 0.0000, 0.0000 |

关键差异：**R1A 在 IP 关节处 IP 权重为 0（单侧）**；R1B 在关节处为 **0.5**，并把混合
铺展到 52.441 – 91.323 mm。

---

## 五、改动统计与 no-drift 证明

| 项 | 值 |
|---|---|
| 授权顶点 | 323 |
| **实际改动顶点** | **319** |
| 授权但未改 | 4 |
| 重建的组 | `WRIST_R`、`THUMB_CMC_R`、`THUMB_MCP_R`、`THUMB_IP_R` |

**逐字节冻结证明**（全部 = `0.000e+00`）：

| 集合 | 漂移 |
|---|---|
| 四指 + INDEX 全部冻结组（全网格） | `0.0` |
| **sanctioned FIRST_WEB cross blend（逐顶点）** | `0.0` |
| nail semantic 顶点 | `0.0` |
| approved distal-cap 顶点 | `0.0` |
| 授权区外全部顶点 | `0.0` |
| central palm | `0.0` |

结构门（全 PASS）：group set 完全一致 / topology 一致 / material 一致 / UV 一致 /
顶点坐标一致 / bone count 21 / deform bone 16 / tip helper 5 / 骨骼全属性一致 /
parent binding / armature modifier。

硬门：`max influences = 4`、`normalization = PASS`、`unweighted vertex = 0`、
`zero-pose bind max = 5.967e-05 mm`（float32 噪声底，硬门 1e-4）。

---

## 六、独立后验证（独立进程，不信任 build 自报）

`s5b_r1b_verify.py` 从**冻结 R1A master + 记录参数**重新推导候选权重，再打开落盘的 R1B
逐组比较：

| 校验 | 结果 |
|---|---|
| 载荷 vs 落盘文件的 float32 不一致数 | **0** |
| 最大绝对差 | `0.000e+00` |
| 四指/INDEX 组漂移 | `0.0` |
| FIRST_WEB / nail / distal-cap / 区外 漂移 | `0.0` |
| 结构门 / 保存位姿 = ZERO\|RSSF | 全 PASS |

`PAYLOAD_ENCODES_ACCEPTED_CANDIDATE = True`。

---

## 七、残余项（交 Human Review）

```
TH_MCP_45 min_edge_ratio :  R1 = 0.421283  ->  R1B = 0.219223
```

这是在六个 thumb case 的**全部记录指标中唯一一项劣于 Stage6A R1 的指标**
（掌侧内表面在 45° 单纯 MCP 屈曲下的压缩）。事实陈述：

- 扫描族内 **375 个候选无一能同时不退化全部受限 case 的 `min_edge_ratio`**；
- 该 case 的 **max edge stretch 完全未变（3.016385）**，**face-area ratio 与 p05 均改善**
  （0.193672→0.297893，0.523736→0.580019），**intra-thumb 自交减少**（79→74）；
- 主观可见程度与是否可接受，**归 Human Review**，本轮**不自行判定 PASS**。

---

## 八、状态

```
STAGE5B_R1A              = FROZEN_PROVENANCE（仍是 FINAL_APPROVED master）
STAGE5B_R1B              = CANDIDATE_FOR_HUMAN_REVIEW
STAGE6A_R1A              = READY_FOR_HUMAN_REVIEW（见 STAGE6A_R1A_REPORT.md）
THUMB_MCP_TRANSITION     = IMPROVED_PENDING_HUMAN_REVIEW
THUMB_IP_TRANSITION      = IMPROVED_PENDING_HUMAN_REVIEW
DEFORMATION_FINAL        = NOT_SET_PENDING_HUMAN_REVIEW
STAGE6B                  = NOT_STARTED
```

## 九、本轮产物

```
stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend
stage5b_r1b/STAGE5B_R1B_STATUS.json
stage5b_r1b/STAGE5B_R1B_WEIGHT_DELTA_AUDIT.json
stage5b_r1b/STAGE5B_R1B_PROTECTED_WEIGHT_DRIFT_AUDIT.json
stage5b_r1b/STAGE5B_R1B_TOPOLOGY_DRIFT.json
stage5b_r1b/STAGE5B_R1B_ZERO_POSE_BIND_AUDIT.json
stage5b_r1b/STAGE5B_R1B_VERTEX_INFLUENCE_AUDIT.json
stage5b_r1b/STAGE5B_R1B_POSTSAVE_SELF_PROOF.json
stage5b_r1b/_tmp/R1B_REGIONS.json
stage5b_r1b/scripts/{r1b_common.py, s5b_r1b_build.py, s5b_r1b_verify.py}
```
