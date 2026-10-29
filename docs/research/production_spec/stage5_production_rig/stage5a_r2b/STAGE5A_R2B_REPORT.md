# STAGE5A_R2B — THUMB_IP FEASIBILITY AND CHAIN CLOSURE · REPORT R1

**状态** `STAGE5A_R2B = FAIL_CLOSED_FOR_HUMAN_REVIEW`（Branch B）
`THUMB_IP_FEASIBLE_REGION = NONE_WITHIN_APPROVED_T01_REGION`
`ACTIVE_PRODUCTION_RIG_CANDIDATE = STAGE5A_R2A`（未变）
**未创建任何新 blend。未进入 Stage5B。**

---

## 一、本轮回答的核心问题

> 在批准的 THUMB_IP T-01 joint region 内，是否存在一个 Production THUMB_IP joint centre，
> 能同时满足：joint 在 thumb mesh 内部、仍在批准 T-01 region、有合理内部 clearance、
> MCP→IP 与 IP→TIP 两条直线 bone segment 都完整位于 thumb volume 内、长度/折角合理、
> 且不动 CMC / MCP / TIP / mesh？

**答案：不存在。** 并且在一个**远超**批准区域的诊断带（axial 35–100 mm）内也不存在。

## 二、恢复并使用的 THUMB_IP T-01 authority（未重新发明）

| 项 | 值 |
| --- | --- |
| 来源 | `stage4a_t01/T01_FINAL_AUDIT.json → OTHER_T01_JOINTS.THUMB_IP` |
| locator | `AXIAL -- joint centre = the web commissure projected on the finger axis` |
| **approved axial centre** | **65.986 mm** |
| **zone half width** | **±8.653 mm** → zone = [57.333, 74.639] mm |
| 轴向定义 | `unit(THUMB_TIP_R.head − THUMB_CMC_R.head)`（冻结 Stage4B 帧），原点 = 同帧 `THUMB_CMC_R.head` |
| T-01 axial span | MCP→IP 27.274 mm；IP→TIP 21.995 mm |

该约定**与已通过的 THUMB_MCP T-01 gate 完全相同**（同法重算 THUMB_MCP = 43.300 mm，与
`STAGE5A_R2_STATUS.json` 逐位一致），因此是「恢复」而非新发明。

**当前 R2A IP** axial = **70.3014 mm** → T-01 delta = **+4.3154 mm**（在 zone 内，PASS）。
即：**当前 IP 本来就在批准区域内**——问题不在区域边界。

## 三、搜索 volume 与 candidate 总数

- 35 个 axial slab（0.5 mm 步长，覆盖整个 zone）；
- 每 slab：thumb 自有面片顶点（±1.2 mm slab、radial ≤ 1.3×R_env = 14.48 mm）→ 剖面质心
  + 极坐标内点网格（0.25 / 0.50 / 0.75 × r95 × 8 方向）；
- 约束：签名最近面内测（prefilter）+ 64 向 ray parity（strict）；最近面 owner 必须 = THUMB；
- **candidate 总数 = 501**（inside + THUMB-owned）；clearance ≥ 3 mm 后 **259**。

## 四、Feasible candidate 数量 = **0**

| 阶段 | 数量 |
| --- | --- |
| inside + THUMB-owned | 501 |
| clearance ≥ 3.0 mm | 259 |
| 快筛（两条 segment 20-sample 全内部） | 0 |
| **STRICT 64-ray parity（20 与 40 sample）** | **0** |

**5. best / selected candidate** — 无可选项。近可解者如下：

| 位置 | axial | T-01 delta | MCP→IP | IP→TIP | 最小 margin | 距当前 IP |
| --- | --- | --- | --- | --- | --- | --- |
| **R2A 当前 IP**（冻结） | 70.3014 | +4.3154 | **40/40** | **31/40** | 0.0096 mm | 0 |
| zone 内最优 | 61.6619 | −4.3241 | **40/40** | **36/40** | 0.2232 mm | 15.95 mm |
| IP→TIP 单项最优（仍在 zone） | 57.8307 | −8.1553 | **20/40** | **40/40** | 0.2581 mm | 27.82 mm |
| 综合最优（**zone 外** 11.07 mm） | 46.2679 | −19.7181 | **40/40** | **35/40** | 0.0789 mm | 25.55 mm |

（以上全部为 64 向 ray parity 的 strict 读数；20/40 样本两套均已测。）

关键结论：**IP→TIP 单独能到 40/40 的位置，MCP→IP 掉到 20/40；MCP→IP 能 40/40 的位置，
IP→TIP 最多 35/40。二者从未同时成立。**

## 六、结构冲突诊断（Branch B，§13）

| 成因 | 量化 | 判定 |
| --- | --- | --- |
| **A. 拇指远端网格弯曲** | 远端指骨中心线相对直线弦的 **sagitta = 6.7968 mm**，而平均剖面半径仅 **7.9575 mm**（比值 0.854） | **主要成因** |
| **B. THUMB_IP T-01 region 位置** | 当前 IP 在 zone 内 +4.315 mm；综合最优位置在 zone 外 **11.0651 mm** —— 即使放宽 zone 也无解 | **非主因** |
| **C. 直线单骨表示** | 一根直骨无法跟随弯曲的远端指骨；IP→TIP 弦长 32.15 mm、折角 18.59° | 参与成因 |
| **D. 粗糙拇指拓扑** | IP 远侧仅 166 面 / 217 顶点；边长中位数 3.77 mm、最大 11.39 mm | 次要成因 |

诊断文件：`THUMB_STRAIGHT_BONE_COMPATIBILITY_DIAGNOSIS.json`（DIAGNOSIS ONLY，
其中 zone 外位置**未被批准**，仅供 Human Review 理解冲突结构）。

## 七、冻结确认

- R2A `THUMB_TIP_R.head = [1.45281744, 0.019802358, 0.493028343]` —— **未移动、未回滚**
  （未退回 R2 / R1 tip）。
- `THUMB_CMC_R` / `THUMB_MCP_R.head` / `WRIST_R` / `INDEX_MCP_R` / 四指 —— 未动。
- **本轮零修改**：未创建 blend、未改 roll/local frame、未改 mesh / topology / CMC cage / RSSF。
- 四份冻结 blend 执行前后 hash 一致（见 STATUS `frozen_inputs_unchanged`）。

## 八、Distal-cap canonical method 勘误（§15 顺带关闭）

`STAGE5A_R2A_DISTAL_CAP_METHOD_ERRATA.md` 已新增，正式声明唯一 authority：

```
CANONICAL_DISTAL_CAP_METHOD = GEODESIC_CONNECTED_CAP_FROM_DISTAL_MOST_SURFACE_REGION
  D* → mesh geodesic → connected digit-owned cap → 9.0 mm calibrated radius
  → cap representative = 面积加权质心投影回表面（测地 1-median 交叉验证）
早期 "fitted medial distal axis + 0.5 mm slab transition" = SUPERSEDED_DIAGNOSTIC_METHOD
```

历史文件未回改。R2A tip 由 canonical method 产生，`KEEP` 不受影响。

## 九、证据图

- `renders/STAGE5A_R2B_THUMB_IP_FEASIBILITY_MAP.png` — 整个被搜 T-01 region、501 点 candidate cloud、
  失败候选、zone 内最优（黄，36/40）、IP→TIP 40/40 位置（青，MCP→IP 仅 20/40）、
  综合最优（品红，zone 外）、当前 IP（红）、MCP（灰）、TIP（绿）。
- `renders/STAGE5A_R2B_THUMB_CHAIN_BEFORE_AFTER.png`
- `renders/STAGE5A_R2B_THUMB_IP_CLOSEUP.png`

## 十、产物清单

```
stage5a_r2b/STAGE5A_R2B_REPORT.md                       （本文件）
stage5a_r2b/STAGE5A_R2B_STATUS.json
stage5a_r2b/STAGE5A_R2B_THUMB_IP_FEASIBILITY_VOLUME.json
stage5a_r2b/STAGE5A_R2B_FEASIBLE_CANDIDATE_RANKING.json
stage5a_r2b/THUMB_STRAIGHT_BONE_COMPATIBILITY_DIAGNOSIS.json
stage5a_r2b/STAGE5A_R2A_DISTAL_CAP_METHOD_ERRATA.md
stage5a_r2b/renders/*.png   (3)
stage5a_r2b/scripts/*.py    (4：feasibility / diagnosis / verify / render)
stage5a_r2b/_tmp/*.json     （S5A_R2B_STRICT_VERIFY.json 等）
```

## 十一、停止点

到此停止。**未创建 R2B blend；未进入 Stage5B。**
`ACTIVE_PRODUCTION_RIG_CANDIDATE = STAGE5A_R2A`。等待 Human Review 裁决：
- 是否接受「straight single-bone IP→TIP 在当前拇指网格上无解」这一结构结论；
- 后续路径（例如 distal phalanx 辅助表示、或 THUMB_IP_R.head 的重新授权）须由 Human Review 另行授权。
