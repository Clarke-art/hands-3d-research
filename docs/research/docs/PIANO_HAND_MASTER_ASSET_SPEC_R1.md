# PIANO_HAND_MASTER_ASSET_SPEC · R1

> `docs/PIANO_HAND_MASTER_ASSET_SPEC_R1.md`
> 项目：钢琴教学双手 3D 交互资产 · 第一阶段
> 版本：**R1.2（最终收口）** + **`STAGE0_ROUTE_C_AMENDMENT`（R1.3）**　基准版本：R1 / R1.1　日期：2026-09-27　状态：**PASS**
>
> **本阶段不创建 mesh、不做 Rig、不做动画。本文档只定义资产必须满足的规范。**
>
> ---
> ## 🔄 R1.3 · `STAGE0_ROUTE_C_AMENDMENT`（与资产规范相关的最小修正）
>
> 详见 `docs/STAGE0_ROUTE_C_AMENDMENT_R1.md`。
>
> - **几何来源权威变更**：主母体来源改为 **CC0 作者化基础网格**
>   （Blender Human Base Meshes v1.4.1 · `Hand  - Realistic`），不再是 Hunyuan3D 多视角重建。
> - **§11 前序门禁改写**：入口门禁由 `REFERENCE_ACQUISITION_GATE` 改为 **`ROUTE_C_SOURCE_GATE = PASS`**；
>   `REFERENCE_ACQUISITION_GATE` 降为**分支门禁**（仅 Hunyuan Multi-view fallback）。
> - **§5.1 生产策略图改写**：Route C 主路线取代 `Reference Pack → Hunyuan3D` 主链。
> - **`OFFICIAL_MULTIREZ_L1 = PERMITTED_ENGINEERING_BASE`**（见 §2.4）：
>   官方资产自带 1 级 Multires，Stage 4 可保留 / 应用 / 复制作为工程基础，**不构成新几何来源**。
> - **`CON-1`~`CON-7`** 已绑定为 **Stage 4 工程义务**（见 §2.4 / §11）。
> - ⚠ **本轮未改动**：Finger ID / 左右手镜像策略 / 21 bones / DIP 双模式 / 主流水线 Stage 5–11 / WorkBuddy 职责边界。
>
> ---
>
> **R1.1 修订内容**（详见 `docs/PHASE1_R1_1_AMENDMENT_REPORT.md`）：
> - `HR-06` = **APPROVED** → 生成范围「手 + 短前臂」，删除"固定 3–5 cm"硬性规则（§1.2）
> - `HR-08` = **APPROVED** → `ADULT_NEUTRAL`（§7.2）
> - **`DIP_ERROR_DEMO_CONFLICT` = RESOLVED** → 新增 `NORMAL_MODE` / `ERROR_DEMO_MODE` 双模式（§3.5、§4.2）
>
> **R1.2 收口内容**（详见 `docs/PHASE1_R1_2_FINAL_CLOSURE.md`）：
> - `HR-06b` / `HR-06c` = **`APPROVED_AS_TECHNICAL_RANGE`** —— 母版角度为**技术范围**，
>   **非 `STANDARD_HAND` 教学参数**（§10）
> - Stage 2 首轮输入 = **完整 8 视图**（`STAGE2_FIRST_GENERATION_INPUT` = `8_VIEWS`）
> - Stage 1 → Stage 2 之间新增 **`REFERENCE_ACQUISITION_GATE`**（§11）
> - ⚠ **本轮未改动**：Finger ID / 左右手镜像策略 / 21 bones / DIP 双模式 / 主流水线 / WorkBuddy 职责边界

---

## 0. 摘要

本规范定义 **RIGHT_HAND_MASTER** 在 **Geometry / Topology / Rig / Animation / Left-Right Strategy** 五个方面的要求，以及命名、单位、坐标系、GLB 导出与验收标准。

**生产策略（用户指定，严格遵守）**：
> 先制作并批准一个 `RIGHT_HAND_MASTER` → Blender 镜像得到 `LEFT_HAND_MASTER`。
> **不要用 AI 分别独立生成左右两只手。**

**几何来源权威（R1.3 · `STAGE0_ROUTE_C_AMENDMENT`）**：

| 字段 | 值 |
| --- | --- |
| `GEOMETRY_SOURCE_PRIMARY` | **`CC0_AUTHORED_BASE_MESH`** |
| `GEOMETRY_SOURCE_PRIMARY_ASSET` | **`BLENDER_HUMAN_BASE_MESHES_V1_4_1_HAND_REALISTIC`** |
| `GEOMETRY_SOURCE_LICENSE` | **`CC0`** |
| `GEOMETRY_SOURCE_QUALIFICATION` | **`CONDITIONAL_PASS_ACCEPTED_FOR_ENGINEERING`** |
| `PROJECT_BLENDER_RUNTIME` | **`D:\Blender\blender.exe`（Blender 5.1.2）** |

> 本规范 §1~§9 的**几何 / 拓扑 / Rig / 动画 / 导出要求全部不变**，仅**几何来源**与**入口门禁**变更（见 §11）。


---

## 1. Geometry（几何）

### 1.1 硬性要求

| ID | 要求 | 拒绝标准（Reject） |
| --- | --- | --- |
| **G-01** | **五指数量必须正确**：1 拇指 + 4 指 = 5 指，不多不少 | 多指、少指、指头融合 |
| **G-02** | **手指比例自然**：中指最长，食指与无名指接近，小指最短（2–5 指）；拇指最短且不超出食指 PIP | 五指等长；小指长于无名指；比例失真 |
| **G-03** | **拇指结构正确**：拇指**仅 2 节指骨**；CMC 为鞍状关节，根部位于腕附近而非与四指根部齐平；**拇指明显旋前**，指甲面与四指指甲面不共面 | 拇指有 3 节；拇指与四指共面（**"猿手"**）；拇指根部位置错误 |
| **G-04** | **指间不得粘连**：任意相邻两指之间存在**真实几何间隙**，指蹼（web space）为独立的膜状过渡而非实心填充 | 指缝被"缝合"成实体；指间无间隙 |
| **G-05** | **手掌结构自然**：存在掌心横弓与纵弓；大鱼际（thenar）与小鱼际（hypothenar）有合理体积 | 手掌为平板；掌弓压平 |
| **G-06** | **指尖形状正常**：指尖为圆润的锥状末端，有明确的最前端触键点；不得为平切或尖刺 | 指尖平切、塌陷、异常尖锐 |
| **G-07** | **指甲只需轻度表现**：浅浅的甲面（可有轻微隆起与边界），无需独立几何厚度 | 指甲厚重夸张；无指甲导致指尖端面无法定位触键点 |
| **G-08** | **不需要照片级皮肤细节**：不要求毛孔、细纹、汗毛 | 追求照片级细节导致面数失控 |
| **G-09** | **风格：semi-realistic / 教学型半真实** | — |
| **G-15** | **人群特征 = `ADULT_NEUTRAL`**（`HR-08` = APPROVED）：成人比例；不强调男性特征；不强调女性特征；不使用儿童手比例 | 儿童手比例；明显男性化或女性化特征（详见 `CANONICAL_HAND_POSE_SPEC_R1.md` §2.5） |
| **G-10** | 🚫 **禁止卡通手**：不得有夸张的比例、圆球状关节、简化块状手指、卡通化指甲 | 任何卡通化特征 |
| **G-11** | 🚫 **禁止明显医学解剖风**：不得暴露肌肉、肌腱、骨骼、血管；不得有剖面或半透明解剖表现 | 肌肉/骨骼可见（"解剖教学模型"观感） |
| **G-12** | **左右手不得混淆**：RIGHT_HAND_MASTER 必须是**解剖学右手** | 生成出左手（拇指在尺侧） |
| **G-13** | **皮肤表面干净**：无疤痕、痣、纹身、戒指、手表、汗毛 | 任何上述元素 |
| **G-14** | **关节区域几何连续**：在中性姿态下不得有自穿插、破面、非流形边 | 破面、自穿插、非流形几何 |

### 1.2 面数预算

| 项目 | 目标区间 | 说明 |
| --- | --- | --- |
| 单手（含腕 + **短前臂**；`HR-06` = APPROVED） | **8,000 – 20,000 tris** | 教学级半真实；需容纳关节变形。短前臂长度**不预设固定厘米数**，按可视效果确定（FR-01~FR-05），故面数预算需按最终裁切长度复核 |
| 双手合计 | **16,000 – 40,000 tris** | — |
| 硬上限（单手） | **30,000 tris** | 超出则须人工批准 |

> **R1.1**：`HR-06` 已裁定为「手 + 短前臂」，面数预算表中"若 HR-06 选 B"的条件表述已删除。
> 因短前臂长度由视觉效果决定（不固定厘米数），**面数需在 Stage 3 Geometry Review 确定裁切长度后复核一次**。

> ⚠ **HUMAN_REVIEW_REQUIRED · HR-10**：面数预算的最终数值需结合**实际 Web 目标设备**（是否含低端移动设备 / 平板）与**同场景是否含完整键盘模型**综合裁定。上表为教学组件常见区间的技术建议，**非教学结论**。
> **下游影响**：LOD 策略、纹理分辨率、Draw Call 预算。

### 1.3 几何细节层级建议

| 区域 | 细节要求 | 理由 |
| --- | --- | --- |
| 掌指关节（MCP） | **中高**：拱顶轮廓必须清晰可辨 | `C-SH-02`；教学核心可视特征 |
| 指尖 / 指甲 | **中高**：触键点可定位 | `G-06`、单指触键动画需要精确接触点 |
| 拇指 | **高**：旋前、虎口、两节指骨必须准确 | `C-SH-03` / `G-03`；最易失败的部位 |
| 指蹼（web space） | **中**：需体现膜状过渡 | `G-04` |
| 掌心 | **中**：大小鱼际体积 | `G-05`、E-08 对比 |
| 指节中段 | **低—中**：平滑过渡即可 | 节省面数 |
| 腕 / 前臂断端 | **低**：规整断口 | 会被 UI/键盘遮挡 |

---

## 2. Topology（拓扑）

> **核心目标：后续骨骼变形正确。拓扑是为变形服务的，不是为好看服务的。**

### 2.1 硬性要求

| ID | 要求 | 说明 |
| --- | --- | --- |
| **T-01** | **指关节处必须能正常弯曲**：每个可动关节（MCP / PIP / DIP；拇指 CMC / MCP / IP）必须有**至少 3 圈环线（edge loops）**跨越关节 | 少于 3 圈会在弯曲时产生塌陷与体积丢失。业界手部 Retopo 通行做法（ArtBlast, L3‑T） |
| **T-02** | **不允许极端三角面布局破坏关节**：关节活动区域**不得**出现扇形三角面极点（pole）、五边以上的星点、或沿关节方向的密集三角化 | 三角面在关节弯曲时会产生不可预测的折痕 |
| **T-03** | **指缝区域不能严重粘连**：指蹼区域必须有足够拓扑表达膜状过渡，**不得**用共面顶点或焊接顶点把相邻指"粘"在一起 | 直接违反 `G-04`；会导致蒙皮时权重互相污染（弹 2 指带动 3 指） |
| **T-04** | **拇指根部需要足够合理的拓扑**：拇指 CMC 为鞍状关节，活动度大（屈/伸 + 外展/内收 + 旋前），根部需**放射状拓扑**以容纳多方向变形 | 拇指根部是手部拓扑最难点；拓扑不足会导致拇指旋转时掌部撕裂 |
| **T-05** | **以四边形为主**：主体布线应为四边形（quad），三角面仅允许出现在必要的收口处 | 便于 Subdivision、便于 Retopo、便于权重刷取 |
| **T-06** | **必须经过 Retopo / 拓扑工程**：不论几何来源如何（AI 生成 mesh 或 **CC0 作者化基础网格**），其面数、布线、密度分布**都不自动等于动画变形适用**，**必须**经过拓扑工程才进入 Rig | 这是流水线的既定环节（Stage 4），不是可选项。<br>⚠ R1.3：**`Hand  - Realistic` 的 base 层为"雕刻友好"密度，同样不自动满足 `T-01`** |
| **T-07** | **四指拓扑可复用**：2–5 指可采用同一套拓扑模板并按长度缩放 | 业界通行做法（ArtBlast, L3‑T）；保证一致性、降低维护成本 |
| **T-08** | **不得有非流形几何、孤立顶点、重叠面、内部面** | 导出与变形的基础要求 |
| **T-09** | **UV 不重叠、无严重拉伸**：为后续纹理烘焙与（若需要）贴图准备 | 拉伸会导致指甲、指蹼区域纹理变形 |
| **T-10** | **法线一致朝外**，无翻转面 | 镜像生成左手时法线是高频错误点 |

### 2.2 关节环线示意（每根手指）

```
        MCP                 PIP                DIP
         │                   │                  │
    ─────┼─────          ────┼─────         ────┼─────
    ─────┼─────   ...    ────┼─────  ...    ────┼─────   ← 至少 3 圈环线跨越每个关节
    ─────┼─────          ────┼─────         ────┼─────
         │                   │                  │
     近节指骨             中节指骨            远节指骨（指尖）
     (proximal)          (middle)            (distal)

  ★ 关节环线之间的间距应在弯曲侧略密、伸展侧略疏，以容纳屈曲时的压缩
```

### 2.3 拇指拓扑特殊要求

```
                      远节指骨（拇指）
                           │
                         IP 关节  ← 3 圈环线
                           │
                      近节指骨
                           │
                        MCP 关节 ← 3 圈环线
                           │
                      第 1 掌骨
                           │
              ┌──────── CMC 关节 ← 放射状拓扑（鞍状关节，多自由度）
              │              + 3 圈以上环线
        腕骨 / 掌部
        └─ 需容纳：屈/伸、外展/内收、旋前（opposition）
```

> **T-04 是本项目拓扑的最高风险点**。拇指根部拓扑不足的典型症状：拇指旋转（对掌方向）时掌侧出现撕裂或"橡皮筋"拉伸。此问题在静态评审中**看不出来**，只在 Deformation Test 阶段暴露 → 必须在流水线 Stage 6 专项测试。

---

### 2.4 Route C 拓扑工程输入（R1.3 新增）

#### 2.4.1 `OFFICIAL_MULTIREZ_L1 = PERMITTED_ENGINEERING_BASE`

> **`Hand  - Realistic` 官方资产本身自带 1 级 Multires。**

| 项 | 规定 |
| --- | --- |
| `OFFICIAL_MULTIREZ_L1` | **`PERMITTED_ENGINEERING_BASE`** |
| **Stage 4 允许** | **保留 / 应用 / 复制该官方已有层级**作为工程基础 |
| **这不构成** | **新几何来源**（仍属官方 CC0 资产内部既有层级） |
| ⚠ **重要** | **L1 增加环线数量 ≠ 自动满足 deformation topology** |

**实测参考（来自 `STAGE1C_C1_ASSET_QUALIFICATION_R1`）**：

| 层 | 每关节环线（四指 MCP / PIP / DIP） | 判定 |
| --- | --- | --- |
| **base** | MCP 0–1 圈 / PIP 2 圈 / DIP 2 圈；拇指 CMC = **0** | ❌ `T-01` 不满足 |
| **L1** | PIP / DIP 大部分 4–7 圈 ✅；**MCP 区部分不足**；**拇指 CMC 仍 = 0** | ⚠ 局部 `NEEDS_MINOR_RETOPO` |

> **最终是否通过 `T-01` / `T-02` / `T-04`，仍必须由 Stage 4 topology review + Stage 6 deformation test 判定。**

#### 2.4.2 `CON-1` ~ `CON-7` = Stage 4 工程义务（绑定表）

> 以下为 `STAGE1C_C1_ASSET_QUALIFICATION_R1` §11.3 的 Conditional 项，**现正式绑定为 Stage 4 义务**。

| # | 条件项 | 对应条款 | 处理阶段 |
| --- | --- | --- | --- |
| **CON-1** | 关节环线密度（MCP 区 + 拇指 CMC 局部补线） | `T-01` | **Stage 4** |
| **CON-2** | 拇指 CMC 放射状 topology 专项检查并按需修正 | `T-04` | **Stage 4**（`THUMB_CMC_TOPOLOGY_REVIEW = REQUIRED`） |
| **CON-3** | 检查极点是否落在关节弯曲区 | `T-02` | **Stage 4** |
| **CON-4** | 补轻度指甲 / 甲床表现（`G-07`） | `G-07` | **Stage 4** |
| **CON-5** | RSSF re-pose（先建 deformation topology → 再临时骨架 re-pose → 再 Retopo/Rig） | `R-09` | **Stage 4** |
| **CON-6** | origin 重设到腕关节旋转中心 | §7.1 | **Stage 4** |
| **CON-7** | UV overlap / stretch 正式验证 | `T-09` | **Stage 4** |
| **CON-8** | 左手镜像（**不在 Stage 4**） | `LR-01`~`LR-04` | **Stage 7**（右手母版获批后） |
| **CON-9** | **`ASSET_FRAME_NORMALIZATION`**（source orientation 记录 + canonical frame 记录 + 批准的 proper transform + 禁负缩放 + scale=1 + chirality 保持 `RIGHT` + canonical frame validation PASS）<br>⚠ 完成后才允许 Rig | `CANONICAL_HAND_POSE_SPEC_R1.md` §1.2.1 | **Stage 4**（🔒 R1.3.1 新增） |

> 📌 **Stage 3 不要求 `CON-1`~`CON-7` 已修完**——它们本来就是 Stage 4 的工程任务。
> Stage 3 只确认这些条件**已被正确绑定**到 Stage 4。
> 📌 **`CON-9`** 由 **R1.3.1 `ASSET_FRAME_COMPATIBILITY_AUDIT`** 引入（非 C1 Qualification 的 Conditional 项），同样绑定 **Stage 4**，且**完成后才允许进入 Stage 5 Rig**。

---

## 3. Rig（绑定）

### 3.1 骨架结构

**每只手 16 个可动关节**（与图形学界通用手部参数模型 MANO 一致：θ ∈ R⁴⁸ = 16 joints × 3 DoF），另加 5 个指尖辅助骨。

```
WRIST_R  (根骨 / 根关节)
│
├── THUMB_CMC_R ── THUMB_MCP_R ── THUMB_IP_R ── THUMB_TIP_R(辅助)
│
├── INDEX_MCP_R ── INDEX_PIP_R ── INDEX_DIP_R ── INDEX_TIP_R(辅助)
│
├── MIDDLE_MCP_R ── MIDDLE_PIP_R ── MIDDLE_DIP_R ── MIDDLE_TIP_R(辅助)
│
├── RING_MCP_R ── RING_PIP_R ── RING_DIP_R ── RING_TIP_R(辅助)
│
└── LITTLE_MCP_R ── LITTLE_PIP_R ── LITTLE_DIP_R ── LITTLE_TIP_R(辅助)
```

| 项 | 值 |
| --- | --- |
| 根骨 | `WRIST_R`（1 个） |
| 可动关节 | 15 个（5 指 × 3 关节） |
| 指尖辅助骨 | 5 个（`*_TIP_R`，**不参与蒙皮变形**，仅作为末端定位器 / Three.js 点击热区锚点） |
| 骨骼总数 | 21 个 |
| 四指关节链 | MCP → PIP → DIP（3 节指骨） |
| 拇指关节链 | CMC → MCP → IP（**2 节指骨**） |

### 3.2 骨骼命名规范（强制）

**格式**：`<FINGER>_<JOINT>_<SIDE>`

| FINGER | 含义 | **Finger ID** |
| --- | --- | --- |
| `THUMB` | 拇指 | **1** |
| `INDEX` | 食指 | **2** |
| `MIDDLE` | 中指 | **3** |
| `RING` | 无名指 | **4** |
| `LITTLE` | 小指 | **5** |

| JOINT | 含义 | 适用 |
| --- | --- | --- |
| `CMC` | 腕掌关节 | 仅 THUMB |
| `MCP` | 掌指关节 | 全部 5 指 |
| `PIP` | 近端指间关节 | 2–5 指 |
| `DIP` | 远端指间关节 | 2–5 指 |
| `IP` | 指间关节 | 仅 THUMB |
| `TIP` | 指尖辅助骨 | 全部 5 指 |

| SIDE | 含义 |
| --- | --- |
| `_R` | 右手 |
| `_L` | 左手 |

**完整骨骼清单（21 × 2 = 42 骨骼）**：

```
WRIST_R / WRIST_L

THUMB_CMC_R   THUMB_MCP_R   THUMB_IP_R   THUMB_TIP_R
INDEX_MCP_R   INDEX_PIP_R   INDEX_DIP_R  INDEX_TIP_R
MIDDLE_MCP_R  MIDDLE_PIP_R  MIDDLE_DIP_R MIDDLE_TIP_R
RING_MCP_R    RING_PIP_R    RING_DIP_R   RING_TIP_R
LITTLE_MCP_R  LITTLE_PIP_R  LITTLE_DIP_R LITTLE_TIP_R

（左手同上，_R → _L）
```

> **`C-ID-02` 落实**：Finger ID 通过骨骼名中的 `<FINGER>` 段表达，**不得**用骨骼数组下标或顶点索引隐式表达。左右手镜像后，几何上最靠近桡侧的骨骼仍必须命名为 `THUMB_*`（Finger ID 1）。

### 3.3 Rig 要求

| ID | 要求 |
| --- | --- |
| **R-01** | 骨骼层级必须与 §3.1 完全一致，**父子关系不可变更** |
| **R-02** | 骨骼命名 100% 符合 §3.2，**不得**使用 Blender 自动生成的 `Bone.001` 之类名称 |
| **R-03** | 每根手指拥有**完整且合理**的关节链（四指 3 关节，拇指 3 关节含 CMC） |
| **R-04** | 关节旋转轴向需按解剖学设定；**DIP 必须能独立弯曲**；**在 `NORMAL_MODE` 下 DIP joint limit 开启，禁止负向 hyperextension（过伸）**（`C-SH-05`）。错误示范所需的过伸由 `ERROR_DEMO_MODE` 承担，见 §3.5 |
| **R-05** | **DIP 与 MCP 必须能分别独立"塌陷"**以表现 E-04 / E-03 错误手型，且塌陷时几何不得穿模（`C-ERR-02`）。**该能力只在 `ERROR_DEMO_MODE` 下对学生可见**，见 §3.5 |
| **R-06** | 不要求影视级复杂 Rig（无需肌肉模拟、无需次级变形、无需修正 blendshape 体系） |
| **R-07** | **目标：教学动作稳定 + Web 性能友好** |
| **R-08** | 需提供关节角度限制（joint limits），防止出现解剖学不可能的姿态。**joint limit 按模式生效**：`NORMAL_MODE` 启用正向教学限制；`ERROR_DEMO_MODE` 允许受控放宽，见 §3.5 |
| **R-09** | 骨骼必须处于**绑定中性姿态 = `CANONICAL_HAND_POSE`（RSSF）**，而非任意姿态 |
| **R-10** | 指尖辅助骨 `*_TIP_*` 必须在 GLB 中保留（Three.js 用于点击热区锚点与指尖接触点计算） |

### 3.4 蒙皮（Skin Weight）

| ID | 要求 |
| --- | --- |
| **S-01** | 使用线性混合蒙皮（LBS），与 MANO 等业界标准管线一致，保证 GLB / Three.js 兼容 |
| **S-02** | 每个顶点的权重**必须归一化**（权重和为 1） |
| **S-03** | 每个顶点受影响骨骼数建议 ≤ 4（Web 端性能与 GLB 兼容性） |
| **S-04** | **相邻手指之间的权重不得互相污染**：弹 2 指不得带动 3 指明显位移。这是 `T-03` 在权重层的对应要求 |
| **S-05** | 关节处权重过渡需平滑，弯曲时**不得**出现体积塌陷、"糖果纸"扭转、或关节处断裂 |
| **S-06** | 拇指根部（CMC 区域）权重需能容纳多方向旋转，不得出现撕裂 |
| **S-07** | 左右手**共享 Skin Weight 逻辑**（镜像关系，见 §6） |
| **S-08** | 蒙皮必须能在 `ERROR_DEMO_MODE` 的受控过伸姿态下正常工作（DIP 反折时不塌陷、不穿模、不撕裂）。见 §3.5 |

---

### 3.5 关节模式：`NORMAL_MODE` / `ERROR_DEMO_MODE`（R1.1 新增）

> ## ✅ `DIP_ERROR_DEMO_CONFLICT` = **RESOLVED**

#### 3.5.1 R1 中存在的逻辑冲突

R1 的 R-04 与 R-05 存在**表面矛盾**：

| 条款 | 要求 |
| --- | --- |
| **R-04** | DIP **禁止**负向 hyperextension（这是正常教学的必要约束：`C-SH-05`） |
| **R-05** | DIP **必须能塌陷 / 反折**以演示错误手型 E-04「折指」（`C-ERR-02`） |

若不做区分，这两条要么互相抵消（错误示范做不出来），要么导致学生在自由交互中把手指随意反折（教学上不可接受）。

#### 3.5.2 解法：双模式

同一个 Rig、同一套蒙皮，**通过模式切换区分用途**。模式是**运行时状态**，不是两套资产。

| | **`NORMAL_MODE`**（默认） | **`ERROR_DEMO_MODE`** |
| --- | --- | --- |
| **用途** | 正常教学：标准手型、单指触键、自由交互观察 | 错误手型教学：演示 E-04「折指」等错误 |
| **DIP joint limit** | ✅ **开启**，**禁止负向 hyperextension** | ⚠ **受控放宽**，允许展示 `ERR_COLLAPSED_DIP` |
| **谁可进入** | 学生（默认状态） | **仅由教学流程触发**，学生不可自由进入 |
| **学生自由度** | 自由旋转/缩放/点击手指 | 🚫 **禁止学生在普通自由交互状态下把 DIP 随意反折** |
| **运行时切换** | 默认 | 由 WorkBuddy 在 Three.js 层按教学内容切换；退出错误示范后**必须回到 `NORMAL_MODE`** |

#### 3.5.3 `ERR_COLLAPSED_DIP` 的三种实现路径（任选其一，须在 Stage 8 前确定）

| 路径 | 做法 | 优点 | 代价 |
| --- | --- | --- | --- |
| **P-1 专门 Pose** ⭐ | 预置一个 `ERR_COLLAPSED_DIP` 静态 Pose（烘焙好的姿态），播放时直接切换 | 最简单；无需运行时改 limit；蒙皮结果可预先验证；Web 性能最好 | 只能展示**一个预设程度**的塌陷，不可调 |
| **P-2 受控临时 override** | 进入 `ERROR_DEMO_MODE` 时临时放宽 DIP 关节限制，退出时恢复 | 可动态调节塌陷程度；可与其他姿态组合 | 需要运行时状态管理；须保证退出时**必定恢复**（否则学生会看到能随便折的手） |
| **P-3 corrective deformation** | 用 corrective blendshape / 形变修正直接表现塌陷几何 | 几何表现最可控、最好看 | 需要额外的形变制作工作量；增加资产复杂度 |

> **推荐 P-1（专门 Pose）**，理由：教学上只需要演示"这个错误长什么样"，一个预设程度足够；
> 且 P-1 不触碰 `NORMAL_MODE` 的 limit，**从架构上就不可能让学生自由反折 DIP**——这是最安全的方案。
> 若教学方需要"可调节的塌陷程度"或"多个塌陷等级"，再升级到 P-2。
> **最终选择由人工在 Stage 8 前裁定。**

#### 3.5.4 硬性约束（无论选哪条路径都必须遵守）

| ID | 约束 |
| --- | --- |
| **DM-01** | 🚫 **禁止学生在普通自由交互状态下把 DIP 随意反折。** `NORMAL_MODE` 下 DIP 负向过伸必须被 limit 阻止。 |
| **DM-02** | `ERROR_DEMO_MODE` **只能由教学流程触发**（例如点击"错误示范：折指"按钮 / 播放对应动画），不得由学生的自由拖拽、自由交互进入。 |
| **DM-03** | 退出错误示范后，**必须回到 `NORMAL_MODE`**，且 DIP 恢复正向姿态。 |
| **DM-04** | 错误示范必须有**明确的 UI 标识**（标注这是"错误示范"，且可与标准手型对比），避免学生误学。 |
| **DM-05** | `ERROR_DEMO_MODE` 下的 DIP 反折程度须由**教学方确认**，不得由 WorkBuddy 臆测。 |
| **DM-06** | 两种模式共享**同一个 mesh 与同一套 Rig**（`C-ERR-01`），不得为错误示范另建模型。 |

#### 3.5.5 WorkBuddy 侧的实现责任

> WorkBuddy 负责在 Three.js 层实现模式切换与 UI 标识（§3.5.4 DM-01~DM-04 的运行层部分），
> **但不负责**决定反折程度（DM-05，教学方决定）与选择实现路径（3.5.3，人工裁定）。

---

## 4. Animation（动画）

> **本阶段只定义动画需求，不制作任何动画。**

### 4.1 必须支持的 Pose / Animation 清单

| 名称 | 类型 | 说明 | 时长建议 | 循环 |
| --- | --- | --- | --- | --- |
| `RELAXED` | Pose（静态） | 自然放松手型。定义取自"手臂自然下垂时手的天然形状"（`C-SH-01`） | 单帧 | — |
| `PIANO_READY` | Pose（静态） | 预备触键姿态：手置于键上方，尚未触键 | 单帧 | — |
| `STANDARD_HAND` | Pose（静态） | **标准钢琴手型**（教学核心） | 单帧 | — |
| `FINGER_1_PRESS` | Clip | 1 指（拇指）触键 | 约 0.8–1.2 s | 否（单次） |
| `FINGER_2_PRESS` | Clip | 2 指（食指）触键 | 约 0.8–1.2 s | 否 |
| `FINGER_3_PRESS` | Clip | 3 指（中指）触键 | 约 0.8–1.2 s | 否 |
| `FINGER_4_PRESS` | Clip | 4 指（无名指）触键 | 约 0.8–1.2 s | 否 |
| `FINGER_5_PRESS` | Clip | 5 指（小指）触键 | 约 0.8–1.2 s | 否 |
| `AUTO_DEMO_01` | Clip | 标准手型自动示范 | 待定 | 是 |

### 4.2 变形测试姿态（Deformation Test Poses，非交付内容）

| 名称 | 模式 | 用途 |
| --- | --- | --- |
| `DEFORM_TEST_FIST` | `NORMAL_MODE` 量程内 | 完全握拳 → 测试最大屈曲时关节是否塌陷 |
| `DEFORM_TEST_EXTEND` | `NORMAL_MODE` 量程内 | 五指完全伸直 → 测试最大伸展时是否有过伸与撕裂 |
| `DEFORM_TEST_SPREAD` | `NORMAL_MODE` 量程内 | 五指最大张开 → 测试指蹼与掌部拓扑 |
| `DEFORM_TEST_THUMB_OPPOSE` | `NORMAL_MODE` 量程内 | 拇指对掌（最大旋前）→ 测试拇指 CMC 拓扑（`T-04` 最高风险点） |
| `DEFORM_TEST_ERR_COLLAPSED_MCP` | `ERROR_DEMO_MODE` | 掌指关节塌陷 → 验证 E-03 可行性 |
| `DEFORM_TEST_ERR_COLLAPSED_DIP` | `ERROR_DEMO_MODE` | 第一关节塌陷（折指）→ 验证 E-04 可行性 |

> **R1.1 说明（解决与 R-04 的逻辑冲突）**：
> - 前 4 项在 **`NORMAL_MODE` 关节量程内**执行，用于验证正常教学动作的变形质量。
> - 后 2 项在 **`ERROR_DEMO_MODE`** 下执行，属于**受控的错误示范量程**，用于验证错误对比是否可做。
> - **二者不再冲突**：`NORMAL_MODE` 下 DIP 仍严格禁止过伸（R-04）；过伸只在 `ERROR_DEMO_MODE` 的受控量程中出现（R-05）。
>   详见 §3.5。
> - 测试姿态本身用于流水线 Stage 6 的**几何/权重验收**，**不作为教材内容交付**。

### 4.3 动画通用规范

| 项 | 规定 |
| --- | --- |
| 帧率 | **30 fps** |
| 时间单位 | 秒 |
| 曲线 | 缓入缓出（ease-in / ease-out），避免线性机械感 |
| 命名 | 严格使用 §4.1 的大写下划线命名，**左右手同名**（前缀/后缀区分手别，见 §6） |
| 根骨 | 动画**不得**移动根骨 `WRIST_*` 的位置（除非该动画本身设计为手部整体位移，如 `C-SH-07` 的掌部对齐调整） |
| 手腕伴随调整 | `FINGER_n_PRESS` 必须包含手腕/掌部的**轻微伴随位移与对齐调整**（`C-SH-06`、`C-SH-07`） |
| 指尖接触 | `FINGER_n_PRESS` 下键时，指定指尖必须**到达键面接触平面**并下沉约 **10 mm**（标准钢琴键下沉深度，**待人工核实**） |

### 4.4 阻塞项

> ⚠ **`STANDARD_HAND` 的具体关节角度、`FINGER_n_PRESS` 的抬指高度与幅度，均依赖以下未决事项，本阶段不定义数值**：
> - `HR-01`（Lhevinne vs Taubman：弯曲程度与触键部位）
> - `HR-02`（手腕具体高度）
> - `HR-03`（是否主动抬指、抬多高）
> - `REFERENCE_GAP-04`（手型量化角度数值缺失）
>
> 在人工裁定前，**不得**由 WorkBuddy 臆测这些数值。

---

## 5. Left / Right Hand Strategy（左右手策略）

### 5.1 生产策略（强制 · R1.3 修订）

```
        ┌──────────────────────────────────────────────────┐
        │  CC0 Authoritative Base Mesh                      │
        │  《Hand  - Realistic》Human Base Meshes v1.4.1     │
        └───────────────────┬──────────────────────────────┘
                            ▼  （ROUTE_C_SOURCE_GATE = PASS）
                Stage 2 · Geometry Bootstrap
                → RIGHT_HAND_BOOTSTRAP_C1 工作副本
                            ▼
                  Stage 3 · Geometry Review（人工）  🚦 GATE 2
                  → RIGHT_HAND_ENGINEERING_CANDIDATE
                            ▼
                  Stage 4 · Blender Engineering
                  （Topology Patch / RSSF Re-pose / 指甲 / origin / UV）
                            ▼
                  Stage 5 · Rig（按 §3 规范）
                            ▼
                  Stage 6 · Deformation Test  🚦 GATE 3
                            ▼
              ✅ RIGHT_HAND_MASTER 批准
                            ▼
                  Blender 镜像（X 轴）
                            ▼
              ✅ LEFT_HAND_MASTER 批准
                            ▼
                  Stage 8 · Animation

  ── 旁支（非阻塞）──────────────────────────────────────
  真人 8 Views → Validation / Texture Reference
  Hunyuan3D    → 仅人工触发（Multi-view fallback 受 REFERENCE_ACQUISITION_GATE 约束）
```


### 5.2 硬性规则

| ID | 规则 |
| --- | --- |
| **LR-01** | 🚫 **不要分别用 AI 独立生成左右两只手** |
| **LR-02** | 必须先制作并**人工批准** `RIGHT_HAND_MASTER`，**之后**才镜像得到 `LEFT_HAND_MASTER` |
| **LR-03** | 镜像在 Blender 中完成，**不得**通过 Three.js 的 `scale.x = -1` 之类的运行时负缩放实现（会破坏法线、光照、蒙皮与射线检测） |
| **LR-04** | 镜像后**必须**应用变换（Apply Scale）并**重算法线** |

### 5.3 左右手必须共享的内容

| 项目 | 要求 |
| --- | --- |
| **拓扑结构** | 顶点数、面数、UV 布局、顶点顺序**完全一致**（镜像对应） |
| **Rig 结构** | 骨骼层级、父子关系、命名**完全一致**（仅 `_R` / `_L` 后缀不同） |
| **Skin Weight 逻辑** | 权重分配**镜像对应**（顶点 i 在手 R 与手 L 上受同名骨骼的影响权重相同） |
| **Finger ID** | 语义一致：1=THUMB、2=INDEX、3=MIDDLE、4=RING、5=LITTLE |
| **动作命名规则** | 同名（如 `STANDARD_HAND`），通过手别命名空间区分（见 §6.2） |

### 5.4 镜像后必须专项检查（高频错误点）

| # | 检查项 | 典型症状 |
| --- | --- | --- |
| 1 | **法线朝向** | 手看起来"内翻"、光照发黑 |
| 2 | **负缩放残留** | Three.js 中蒙皮错乱、包围盒异常、射线检测失效 |
| 3 | **蒙皮权重镜像正确性** | 弹 2 指时 3 指跟着动 |
| 4 | **动画曲线 X 轴旋转取反** | 手指往反方向弯 |
| 5 | **拇指位置** | 左手拇指应在**桡侧**（右手拇指的镜像侧）；两拇指相对朝向中央 C（`C-ID-04`） |
| 6 | **Finger ID 映射** | 左手几何上最靠桡侧的仍是 `THUMB`（ID 1），**不得**因镜像变成 `LITTLE` |
| 7 | **拓扑缠绕方向** | 面片索引缠绕反转导致背面剔除错误 |

> ✅ **`C-ID-04` 校验口诀**：把左右手并排放在键盘前，**两个拇指必须彼此相对、朝向中央 C**。若不相对，说明镜像或手别判定有误。这是**首要人工检查项**。

---

## 6. 命名与组织规范

### 6.1 资产命名

| 资产 | 名称 |
| --- | --- |
| 右手母版 | `RIGHT_HAND_MASTER` |
| 左手母版 | `LEFT_HAND_MASTER` |
| 右手 GLB | `hand_right_master.glb` |
| 左手 GLB | `hand_left_master.glb` |
| 合并导出（可选） | `piano_hands_master.glb` |

### 6.2 骨骼命名空间

- 右手：`WRIST_R`, `THUMB_MCP_R`, …（见 §3.2）
- 左手：`WRIST_L`, `THUMB_MCP_L`, …
- **若双手合并在一个 GLB 中**，必须保证骨骼名全局唯一（正是 `_R` / `_L` 后缀的作用）

### 6.3 动画命名与手别

| 方式 | 示例 | 说明 |
| --- | --- | --- |
| 同名 + 手别命名空间（推荐） | `RIGHT/STANDARD_HAND`、`LEFT/STANDARD_HAND` | 动作名一致，便于代码统一调用 |
| 或后缀式 | `STANDARD_HAND_R`、`STANDARD_HAND_L` | 备选 |

> **推荐第一种**：WorkBuddy 在 Three.js 层只需按手别切换命名空间，动作名保持一致，减少出错面。

---

## 7. 单位、坐标系与键面对齐

### 7.1 单位与轴向

| 项 | 规定 |
| --- | --- |
| **单位** | **米（m）**，1 unit = 1 m |
| **轴向** | 右手系，**Y-up**（Three.js 标准） |
| **Asset Frame** | 见 `CANONICAL_HAND_POSE_SPEC_R1.md` §1.2：+X 桡侧、+Y 掌背、+Z 指尖方向 |
| **原点** | 腕关节旋转中心 |
| **缩放** | 导出时 scale = 1，**禁止**非均匀缩放 |
| **旋转** | 建议导出前应用全部旋转（rotation = 0），避免运行时额外变换 |

### 7.2 尺度参考值（待人工确认）

| 项 | 参考值 | 状态 |
| --- | --- | --- |
| 成人手长（腕横纹 → 中指尖） | 约 **0.19 m** | ⚠ 待确认。`HR-08` 已裁定为 `ADULT_NEUTRAL`，故本项按**成人中性手**取值，不因人群特征再变 |
| 标准钢琴白键宽 | 约 **23.5 mm** | ⚠ 待确认 |
| 标准钢琴键下沉深度 | 约 **10 mm** | ⚠ 待确认 |

> ⚠ **HUMAN_REVIEW_REQUIRED · HR-11**：上述尺度数值需人工核实。这些数值直接决定 3D 手与（未来）键盘模型的比例关系，若错误会导致教学演示失真。

### 7.3 键面接触平面（Key Surface Plane）

由于生成阶段不引入琴键（`REFERENCE_GAP-06`），需**独立定义**键面接触平面：

| 项 | 建议定义 |
| --- | --- |
| 名称 | `KEY_SURFACE_PLANE` |
| 定义 | 白键上表面所在的水平面 |
| 在 Asset Frame 中的约定 | 由 Blender 工程阶段标定：使 `STANDARD_HAND` 姿态下五个指尖恰好落在该平面上 |
| 交付形式 | 在资产规范附录或 Blender 工程文件中记录**标定数值**（从腕部原点到该平面的偏移） |

> ⚠ **HUMAN_REVIEW_REQUIRED · HR-12**：键面接触平面的标定方式与数值需人工确认（依赖 `HR-01` / `HR-02` 确定的 `STANDARD_HAND`，而后者尚未裁定）。
> **下游影响**：Three.js 中手与键盘的相对摆放、单指触键动画的终点判定。

---

## 8. GLB 导出规范

| 项 | 规定 |
| --- | --- |
| 格式 | **glTF 2.0 Binary（.glb）** |
| 单位 | 米，scale = 1 |
| 轴向 | Y-up |
| 材质 | glTF PBR（ metallicRoughness ）；教学型半真实材质 |
| 纹理 | 若使用，建议 **1024 × 1024**（单手）或 **2048**（若需指节细节）；**需与面数预算一并人工确认** |
| 骨骼 | 必须导出（Skinned Mesh + Joints），**不得**塌陷为静态网格 |
| 指尖辅助骨 | **必须保留** |
| 动画 | 以 glTF Animation Clip 导出，命名符合 §4.1 |
| 压缩 | 视需要使用 Draco（**注意**：Draco 压缩骨骼动画需验证 Three.js 端兼容性） |
| 校验 | 导出后必须在 Three.js 或 glTF Viewer 中验证：骨骼层级、蒙皮、动画播放、指尖骨存在 |

---

## 9. 验收清单（Acceptance Checklist）

### A. Geometry
- [ ] 五指数量正确（G-01）
- [ ] 手指比例自然（G-02）
- [ ] 拇指 2 节指骨、明显旋前、根部位置正确，非"猿手"（G-03）
- [ ] 指间无粘连，指蹼为膜状过渡（G-04）
- [ ] 掌弓存在，大小鱼际体积合理（G-05）
- [ ] 指尖形状正常，有明确触键点（G-06）
- [ ] 指甲轻度表现（G-07）
- [ ] 风格为 semi-realistic 教学型；**非卡通、非医学解剖风**（G-09 / G-10 / G-11）
- [ ] 确认为解剖学右手（G-12）
- [ ] **`ADULT_NEUTRAL` 符合性**：成人比例、不强调性别特征、非儿童手比例（G-15 / `HR-08`）
- [ ] **手 + 短前臂**已包含，且足以表达「前臂—手腕—手掌」方向与连续关系（`HR-06` FR-02 / FR-03）
- [ ] 面数在预算内，且已按最终前臂裁切长度复核（HR-10）

### B. Topology
- [ ] 每个关节 ≥ 3 圈环线（T-01）
- [ ] 关节区无极端三角面布局（T-02）
- [ ] 指缝拓扑独立，无焊接粘连（T-03）
- [ ] 拇指根部放射状拓扑充分（T-04）
- [ ] 四边形为主（T-05）
- [ ] 已完成 Retopo（T-06）
- [ ] 无非流形几何 / 孤立顶点 / 重叠面（T-08）
- [ ] UV 无重叠、无严重拉伸（T-09）
- [ ] 法线一致朝外（T-10）

### C. Rig
- [ ] 骨骼层级与 §3.1 一致（R-01）
- [ ] 骨骼命名 100% 符合 §3.2（R-02）
- [ ] 每指完整关节链（R-03）
- [ ] DIP 可独立弯曲，且 **`NORMAL_MODE` 下禁止过伸**（R-04 / §3.5）
- [ ] MCP / DIP 可分别独立塌陷且不穿模，**且该能力仅在 `ERROR_DEMO_MODE` 下对学生可见**（R-05 / §3.5）
- [ ] **双模式机制已实现**：`NORMAL_MODE` 为默认；`ERROR_DEMO_MODE` 只能由教学流程触发；退出后必定恢复（DM-01~DM-04）
- [ ] **学生无法在普通自由交互状态下随意反折 DIP**（DM-01）
- [ ] 错误示范有明确的 UI 标识（DM-04）
- [ ] 绑定中性姿态 = CANONICAL_HAND_POSE（R-09）
- [ ] 权重归一化，每顶点 ≤ 4 骨骼（S-02 / S-03）
- [ ] 相邻指权重无污染（S-04）
- [ ] 关节弯曲无塌陷 / 扭转 / 断裂（S-05）
- [ ] 拇指 CMC 多方向旋转无撕裂（S-06）
- [ ] `ERROR_DEMO_MODE` 受控过伸下蒙皮正常（S-08）
- [ ] 全部 6 项 Deformation Test 通过；前 4 项在 `NORMAL_MODE` 量程内，后 2 项在 `ERROR_DEMO_MODE` 下（§4.2）

### D. Animation
- [ ] 9 项 Pose / Clip 全部存在且命名正确（§4.1）
- [ ] 30 fps，缓入缓出（§4.3）
- [ ] `FINGER_n_PRESS` 含手腕/掌部伴随调整（C-SH-06）
- [ ] 弹 1 指 vs 弹 5 指时掌部水平位置有可见差异（C-SH-07）
- [ ] 指尖到达键面接触平面（HR-12）

### E. Left/Right
- [ ] 左手由右手镜像得到，非独立生成（LR-01 / LR-02）
- [ ] 右手先经人工批准（LR-02）
- [ ] 拓扑 / Rig / 权重逻辑 / Finger ID / 动作命名共享（§5.3）
- [ ] 镜像后 7 项专项检查全部通过（§5.4）
- [ ] **两拇指相对朝向中央 C**（C-ID-04）

### F. Export
- [ ] glTF 2.0 Binary（.glb）
- [ ] 单位为米，Y-up，scale = 1
- [ ] 骨骼与蒙皮已导出
- [ ] 指尖辅助骨保留
- [ ] Three.js 端验证通过

---

## 10. `HUMAN_REVIEW_REQUIRED` 汇总（本文档）

| ID | 事项 | 状态（R1.2） | 结论 |
| --- | --- | --- | --- |
| **HR-06** | 生成范围：仅手 / 手+短前臂 / 手+完整前臂 | ✅ **APPROVED** | **手 + 短前臂**；删除"固定 3–5 cm"硬性规则，改为 FR-01~FR-05 原则 |
| **HR-06b** | 母版手相邻指间张开角 | ✅ **`APPROVED_AS_TECHNICAL_RANGE`** | **约 10–15°**。技术范围，非 `STANDARD_HAND` 教学角度；不锁单一数值（母版规范 §3.1） |
| **HR-06c** | `CANONICAL_HAND_POSE` 的 MCP / PIP / DIP 屈曲角 | ✅ **`APPROVED_AS_TECHNICAL_RANGE`** | **MCP 约 20–30° / PIP 约 25–35° / DIP 约 10–20°**。仅用于 RSSF / 母版生成 / Rig neutral pose（母版规范 §3.2） |
| **HR-08** | 母版人群特征（成人/儿童/性别） | ✅ **APPROVED** | **`ADULT_NEUTRAL`**（G-15 / 母版规范 §2.5） |
| **HR-09** | CC0 手部模型正交渲染图作一致性校验基准 | ✅ **`OPTIONAL_NON_BLOCKING`** | 可作内部 QC 参考；**不得代替真人参考图**、**不得作 Hunyuan3D 正式输入**；没有不阻塞 Stage 1。<br>⚠ **R1.3 语义澄清**：`HR-09` 限制的是 **"CC0 MODEL RENDERED IMAGES 作为 Hunyuan input"**，**不是**"CC0 3D ASSET 本身不能作为母体"。<br>Route C 使用的是 **CC0 3D geometry asset**，不是 **CC0 model screenshot → Hunyuan input** → **`HR-09` 与 Route C 无逻辑冲突**（详见修订文档 §11） |
| **HR-10** | 面数预算最终数值（结合目标设备与是否含键盘） | ⏳ 仍待人工确认 | 单手 8k–20k tris（需在确定前臂裁切长度后复核） |
| **HR-11** | 尺度参考值（手长、键宽、键下沉深度） | ⏳ 仍待人工确认 | 0.19 m / 23.5 mm / 10 mm（待核实） |
| **HR-12** | 键面接触平面的标定方式与数值 | ⏳ 仍待人工确认 | 由 STANDARD_HAND 反标 |

### R1.1 新增待裁定项（仍 OPEN）

| ID | 事项 | 状态 | 说明 |
| --- | --- | --- | --- |
| **HR-13** | `ERR_COLLAPSED_DIP` 的实现路径（P-1 专门 Pose / P-2 受控 override / P-3 corrective deformation） | ⏳ **待人工裁定**（Stage 8 前） | 推荐 **P-1**。见 §3.5.3 |
| **HR-14** | `ERROR_DEMO_MODE` 下 DIP 反折的具体程度 | ⏳ **待教学方确认** | 不得由 WorkBuddy 臆测（DM-05） |

> 另：`HR-01` / `HR-02` / `HR-03` / `REFERENCE_GAP-04` 阻塞 **`STANDARD_HAND` 与 `FINGER_n_PRESS` 的具体数值**，见 §4.4。
> **`DIP_ERROR_DEMO_CONFLICT` = RESOLVED**（§3.5）：R-04 与 R-05 的冲突已由 `NORMAL_MODE` / `ERROR_DEMO_MODE` 双模式消解。

### 10.1 ⚠ 技术范围 vs 教学参数（R1.2 重要区分）

> **`HR-06b` / `HR-06c` 批准的是"技术范围"，不是"教学参数"。**

| | 技术范围（`HR-06b` / `HR-06c`） | 教学参数（`STANDARD_HAND`） |
| --- | --- | --- |
| **用于** | `CANONICAL_HAND_POSE` / RSSF 母版生成<br>Hunyuan3D 多视角重建<br>**Rig neutral pose** | 标准钢琴手型<br>学生正确触键姿势 |
| **数值** | 张开约 10–15°<br>MCP 约 20–30° / PIP 约 25–35° / DIP 约 10–20° | **仍未确定** |
| **决定者** | 技术推导 + 人工批准（已完成） | **教学依据 + 人工裁定**（待 `HR-01` / `HR-02` / `REFERENCE_GAP-04`） |
| **可否互换** | 🚫 **不得**用技术范围定义 `STANDARD_HAND` | 🚫 **不得**用 `STANDARD_HAND` 需求反改母版姿态 |

> **为什么必须区分**：Rig 的 neutral pose 处于关节活动范围中段时蒙皮最稳定；
> 而 `STANDARD_HAND` 是功能姿态，接近屈曲一端。**两者本来就应该不同。**

---

## 11. 前序门禁（R1.3 改写）

本资产规范的实施，前置于 **Stage 2（`GEOMETRY BOOTSTRAP`）**。

### 11.1 主路线入口门禁：`ROUTE_C_SOURCE_GATE`

| 项 | 说明 |
| --- | --- |
| **门禁名** | **`ROUTE_C_SOURCE_GATE`** |
| **位置** | **Stage 0 之后 · Stage 2 之前** |
| **作用** | 控制 **Route C geometry bootstrap 是否可以启动** |
| **结果** | ✅ **`PASS`** —— 允许创建 Route C 工程工作副本 |
| **🚫 不表示** | `RIGHT_HAND_MASTER` 已批准 / Topology 已完成 / Rig 可以开始 |
| **详细定义** | 见 `docs/PIANO_HAND_PRODUCTION_PIPELINE_R1.md` §1 与 `docs/STAGE0_ROUTE_C_AMENDMENT_R1.md` §12 |

### 11.2 `REFERENCE_ACQUISITION_GATE` = **`CONDITIONAL_BRANCH_GATE`**（R1.3 重定义）

| 项 | 说明 |
| --- | --- |
| **门禁类型** | **`CONDITIONAL_BRANCH_GATE`** |
| **适用范围** | **仅 `HUNYUAN3D_MULTIVIEW_FALLBACK`** |
| **对 Route C** | **`NOT_APPLICABLE_TO_ROUTE_C`**（**不是 `PASS`**——它没有被绕过，而是不适用） |
| **12 项条件** | **完整保留，不得删除**；仅改变 scope / applicability。fallback 一旦启用即逐条恢复强制力 |
| **详细定义** | 见 `docs/PIANO_HAND_PRODUCTION_PIPELINE_R1.md` §1 与 `docs/MULTIVIEW_REFERENCE_PACK_SPEC_R1.md` §7 |

> 🚫 **在 Hunyuan Multi-view 分支上严禁**为了进入生成阶段而：拼不同人的手、拼不同姿态、用左手补右手、
> 用 AI 图片补真人视角、**用 CC0 模型图代替正式真人输入**、缺视角强行提交。
>
> ⚠ **R1.3 澄清**：上述最后一条约束的是 **"CC0 模型渲染图作为 Hunyuan input"**，
> **不是**"CC0 3D 资产本身不能作为母体"。Route C 使用的是 **CC0 3D geometry asset**，
> 不是 **CC0 model screenshot → Hunyuan input**。因此 **`HR-09` 与 Route C 不存在逻辑冲突**（见 `HR-09` 条目与修订文档 §11）。


---

## 12. 本阶段禁止事项（重申）

本阶段**未**进行且**不得**进行：创建 hand mesh、Blender 建模/雕刻、混元 3D 生成、Rig、Skin Weight、动画、Three.js、HTML UI、钢琴键盘开发、自动进入下一阶段。

本文档**只定义规范，不产出资产**。

> **⚠ R1.3 附加禁止**（`STAGE0_ROUTE_C_AMENDMENT` 本轮）：创建 C1 working mesh、修改官方母文件、应用 Multires、
> 补 topology、re-pose、加指甲、改 UV、改 origin、镜像左手、删除 portable Blender 4.5.9、修改用户 Blender 5.1 配置、
> **自动进入 Stage 2**。详见 `docs/PIANO_HAND_PRODUCTION_PIPELINE_R1.md` §7.1。


---

## 13. 当前权威状态（R1.3 对齐）

> 本节仅为**状态声明**，用于与其余冻结文件保持一致；**不改变任何已批准的技术决策**。

| 冻结事实 | 值 |
| --- | --- |
| `GEOMETRY_SOURCE_PRIMARY` | **`CC0_AUTHORED_BASE_MESH`** |
| `GEOMETRY_SOURCE_PRIMARY_ASSET` | **`BLENDER_HUMAN_BASE_MESHES_V1_4_1_HAND_REALISTIC`** |
| `GEOMETRY_SOURCE_LICENSE` | **`CC0`** |
| `GEOMETRY_SOURCE_QUALIFICATION` | **`CONDITIONAL_PASS_ACCEPTED_FOR_ENGINEERING`** |
| `OFFICIAL_MULTIREZ_L1` | **`PERMITTED_ENGINEERING_BASE`**（§2.4.1） |
| `PROJECT_BLENDER_RUNTIME` | **`D:\Blender\blender.exe`（Blender 5.1.2）** |
| `C1_QUALIFICATION_REPRO_RUNTIME` | **`BLENDER_4_5_9_LTS`**（历史复现，永久区分） |
| `ROUTE_C_SOURCE_GATE` | ✅ **PASS** |
| `MULTIVIEW_FIRST_PASS` | **`8_VIEWS`**（⚠ 仅 Hunyuan 分支） |
| `ALL_8_VIEWS` | **`REQUIRED`**（⚠ 仅 Hunyuan Multi-view 分支） |
| `LIGHTING_RULE` | **`HAND_FIXED_LIGHT_FIXED_CAMERA_MOVES`**（采集侧；仅可选参考分支，见多视角规范 §2.3 / §5） |
| `REAL_HUMAN_8VIEW_REFERENCE` | **`OPTIONAL_NON_BLOCKING_FOR_ROUTE_C`** |
| `REFERENCE_GAP_02` | **`REFERENCE_SOURCE_TO_BE_ACQUIRED_IN_STAGE1`**（⚠ 仅 Hunyuan Multi-view 分支） |
| `REFERENCE_GAP_02_DOES_NOT_BLOCK_STAGE1` | **YES** |
| `REFERENCE_ACQUISITION_GATE` | **`CONDITIONAL_BRANCH_GATE`**（仅 Hunyuan Multi-view；Route C 下 = `NOT_APPLICABLE_TO_ROUTE_C`；见 §11） |
| `HUNYUAN3D_ROLE` | **`OPTIONAL_FALLBACK_EXPERIMENT`** |
| `ROUTE_B_EXECUTION` | **`DEFERRED`** |
| `2D_IMAGEGEN_MULTIVIEW_ROUTE` | **`REJECTED_BASELINE`** |
| `GATE_1` | **PASS**（历史判定，保留） |
| `STAGE0` | **`REFROZEN_AFTER_ROUTE_C_AMENDMENT`** |
| `STAGE1` | **`OPTIONAL_NON_BLOCKING`**（旁支 A） |
| `STAGE2` | **`READY_TO_START_ROUTE_C_BOOTSTRAP`** |

---

**文档状态：PASS（R1.3 · `STAGE0_ROUTE_C_AMENDMENT` 完成）**　**`STAGE0 = REFROZEN`**　**`STAGE2 = READY_TO_START_ROUTE_C_BOOTSTRAP`**

