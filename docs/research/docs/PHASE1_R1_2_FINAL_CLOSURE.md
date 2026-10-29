# PIANO_HAND_PHASE1 · R1.2 最终收口报告

> `docs/PHASE1_R1_2_FINAL_CLOSURE.md`
> 项目：钢琴教学双手 3D 交互资产 · 第一阶段
> 版本：**R1.2（最终收口）**　基准：R1 / R1.1　日期：2026-09-27
> 性质：**极窄收口** —— 不重新研究、不扩大范围、不进入 Stage 1

---

## 1. R1.2 修改范围

| 项 | 说明 |
| --- | --- |
| **性质** | Stage 0 / Phase 1 的最终规范收口 |
| **✅ 做了** | 8 视图首轮提交规则、6/8 MB 规则修正、光照原则修正、`HR-06b` / `HR-06c` / `HR-09` 裁定、`REFERENCE_GAP-02` 重新定义、新增 `REFERENCE_ACQUISITION_GATE`、`GATE 1` 判定、Stage 0 冻结 |
| **🚫 没做** | 未重新研究、未扩大范围、未进入 Stage 1、未采集图片、未调用混元 3D、未创建 mesh、未制作 Rig、未制作动画、未进行 Three.js 开发 |
| **未修改的文件** | `docs/PIANO_HAND_PEDAGOGY_RESEARCH_R1.md`（教学研究正文**未动**） |
| **已修改的文件** | `CANONICAL_HAND_POSE_SPEC_R1.md` · `MULTIVIEW_REFERENCE_PACK_SPEC_R1.md` · `PIANO_HAND_MASTER_ASSET_SPEC_R1.md` · `PIANO_HAND_PRODUCTION_PIPELINE_R1.md` · `REFERENCE_MANIFEST_R1.json` |

### 明确保持不变（不得重新设计）

| # | 保持不变项 |
| --- | --- |
| 1 | **Finger ID**：1 = THUMB / 2 = INDEX / 3 = MIDDLE / 4 = RING / 5 = LITTLE，左右手语义一致 |
| 2 | **RIGHT_HAND_MASTER → LEFT_HAND_MASTER**：先完成并批准右手，再在 Blender 镜像得左手；**禁止**分别用 AI 独立生成左右手 |
| 3 | **21 bones / hand**：16 个可动关节 + 5 个 TIP 辅助骨 |
| 4 | **DIP 双模式机制**：`NORMAL_MODE` / `ERROR_DEMO_MODE`；`DIP_ERROR_DEMO_CONFLICT` = RESOLVED |
| 5 | **主流水线**：Stage 0 → 11 完整保留，**未重构**；仅新增 Stage 1 → Stage 2 之间的 `REFERENCE_ACQUISITION_GATE` |
| 6 | **WorkBuddy 职责边界**：完全不变 |

---

## 2. 8 视图首轮提交规则

> ## ✅ `STAGE2_FIRST_GENERATION_INPUT` = **`8_VIEWS`**
>
> **Stage 2 第一次 Geometry 生成，就必须提交完整 8 视图。**

### 已删除的旧表述

| 🚫 已删除 |
| --- |
| ~~"首轮只提交 6 个强制视角"~~ |
| ~~"6 强制 + 2 建议"~~ |
| ~~"斜视角后续补充"~~ |
| ~~"第 7、8 视角为补充/建议视角"~~ |
| ~~"最后削减补充视角（7、8）"~~ |

### 映射（唯一权威，不得更改）

| # | 本项目视角 | `ViewType` |
| --- | --- | --- |
| 1 | DORSAL | `front` ⭐ 必填 |
| 2 | PALMAR | `back` |
| 3 | RADIAL | `right` |
| 4 | ULNAR | `left` |
| 5 | DISTAL | `top` |
| 6 | PROXIMAL | `bottom` |
| 7 | DORSAL_OBLIQUE_RADIAL | `right_front` |
| 8 | DORSAL_OBLIQUE_ULNAR | `left_front` |

> **8 个视角地位完全平等，全部为强制。**
> 🚫 **不得无故删除** `top` / `bottom` / `left_front` / `right_front`。

### 总量超限处理顺序（不可颠倒）

```
   ①  先降低分辨率      （2048 → 1536 → 1024）
        ↓ 仍超限
   ②  再改为高质量 JPG   （质量 ≥ 92）
        ↓ 仍超限
   ③  才考虑其他合规手段
```

> 🚫 **优先保留完整 8 视图，不得首先通过减少视角来解决总量问题。**

---

## 3. 6 MB / 8 MB 规则修正

> ⚠ **此前表述有误，已全部更正。**

### 正确规则

| 项 | 规则 | 性质 |
| --- | --- | --- |
| **`BASE64_ENCODED_TOTAL` ≤ 8 MB** | Base64 编码后的实际总量**必须 ≤ 8 MB** | 🔴 **腾讯官方硬约束** |
| **`RAW_IMAGE_TOTAL_TARGET` 约 ≤ 6 MB** | 原始图片总量**目标**约 ≤ 6 MB | 🟡 **工程侧建议值**（非官方硬上限） |

**为什么是"约 6 MB"**：Base64 编码约产生 **30% 体积膨胀**。
8 MB ÷ 1.3 ≈ 6.15 MB，工程上取"约 6 MB"作为目标值。

### 写法纪律

| | 写法 |
| --- | --- |
| ✅ 正确 | `BASE64_ENCODED_TOTAL <= 8 MB`（硬约束） |
| ✅ 正确 | `RAW_IMAGE_TOTAL_TARGET <= approximately 6 MB`（建议目标） |
| 🚫 **禁止** | ~~"base64 编码后总量 ≤ 6 MB"~~ |
| 🚫 **禁止** | 把"约 6 MB"写成官方硬上限 |

> **📌 若使用非 Base64 传输方式**：仍以**腾讯接口实际请求限制**为权威，不得把"约 6 MB"误写成官方硬上限。

### 检查清单中必须分别存在

- [x] **`RAW_IMAGE_TOTAL_TARGET` <= ~6 MB**
- [x] **`BASE64_ENCODED_TOTAL` <= 8 MB**

（已写入 `MULTIVIEW_REFERENCE_PACK_SPEC_R1.md` §3.1.1 与 §7 D 段；`REFERENCE_MANIFEST_R1.json` 的 `image_size_rule`）

---

## 4. HAND / LIGHT / CAMERA 最终采集原则

> ## 🔑 `LIGHTING_RULE` = **`HAND_FIXED_LIGHT_FIXED_CAMERA_MOVES`**

```
        HAND   = FIXED
        LIGHT  = FIXED
        CAMERA = MOVES
```

| 项 | 含义 |
| --- | --- |
| **`HAND = FIXED`** | 真人右手在整个 8 视图采集过程中保持**同一个 `CANONICAL_HAND_POSE`**，不得翻转、转动、重新摆放 |
| **`CAMERA = MOVES`** | 通过改变**相机观察机位**获得 8 个视图 |
| **`LIGHT = FIXED`** | 整个采集过程中：**灯位不变 / 光照方向不变 / 光照强度不变 / 色温不变 / 柔光环境不变** |

### 🚫 已废弃

> **"光源随相机同步移动"** 作为推荐方案 —— **已废弃（R1.2）**。
>
> 理由：光源跟随相机移动意味着每个机位光照方向都不同，这恰恰**破坏**了多视角重建要求的光照一致性。
> 正确解法是让光照环境**本身各向同性**，这样相机移到任何机位，手上的受光状态都不变 ——
> 这也正是 `LIGHT = FIXED` 与 `CAMERA = MOVES` 并不矛盾的原因。

### ✅ 正式推荐的光照方案

1. **固定的环绕式柔光环境**
2. **柔光帐**
3. **大面积漫射光**
4. 尽量减少**方向性明显的硬光**
5. 避免**强镜面高光**
6. 避免**硬阴影进入指缝**

### 多相机同步采集的定位（澄清）

多相机同步**仍可作为优选方案**，但其**主要价值是减少真人手随时间发生的姿态漂移**（时间维度），
**不是为了让光源跟随相机**。

> **无论单相机还是多相机**：
> `HAND = FIXED` / `LIGHT = FIXED` / `CAMERA VIEWPOINTS = MULTIPLE`。
> **LIGHT 不跟随 CAMERA 移动。**

### RK-14（重写）

| | 内容 |
| --- | --- |
| **ID** | `RK-14`（R1.2 重写） |
| **风险** | **多视角采集过程中光照环境发生变化** |
| **风险来源** | 灯位变化 / 光源强度变化 / 色温变化 / 环境光变化 / **户外自然光变化** / **拍摄时间过长导致光线漂移** |
| **缓解** | ① 使用**固定室内拍摄环境**；② 使用**固定柔光帐 / 大面积漫射光**；③ **8 视图期间灯位、强度、色温不变**；④ **避免自然光作为主要光源**；⑤ 多相机同步可**减少拍摄时间**，但**不改变 `LIGHT = FIXED` 原则** |

---

## 5. `HR-06b` 裁定

> ## ✅ `HR-06b` = **`APPROVED_AS_TECHNICAL_RANGE`**

**主题**：母版手**相邻指间张开角**。
**采用**：**约 10–15°**。

### 必须明确这不是什么

🚫 **这不是钢琴 `STANDARD_HAND` 的教学角度。**
它只是 **`CANONICAL_HAND_POSE` / Hunyuan3D 多视角重建 / Rig neutral pose** 所使用的**技术范围**。

### 技术目的

- 保证指间存在**可见间隙**；
- 降低**指缝粘连**；
- 降低**侧视角遮挡**；
- 又**不过度拉伸指蹼**。

### 使用纪律

| | |
| --- | --- |
| 🚫 **不要锁成单一数值** | 不要求"所有手必须正好 12°"之类**假精确** |
| ✅ **正确含义** | 大致处于 10–15° 技术范围，**以视觉上五指分离清晰、指蹼不过度拉伸为实际判据** |

**→ `HR-06b` 不再阻塞 Stage 1。**

---

## 6. `HR-06c` 裁定

> ## ✅ `HR-06c` = **`APPROVED_AS_TECHNICAL_RANGE`**

**主题**：`CANONICAL_HAND_POSE` 母版姿态中的 **MCP / PIP / DIP 屈曲角**。
**采用**：**MCP 约 20–30° / PIP 约 25–35° / DIP 约 10–20°**。

### 只用于

- `CANONICAL_HAND_POSE` / **RSSF**
- **Hunyuan3D 母版生成**
- **Rig neutral pose**

### 🚫 不得用于

- 定义**标准钢琴手型**；
- 定义**学生正确触键姿势**；
- 代替 **`HR-01` / `HR-02` / `REFERENCE_GAP-04`**。

> **`STANDARD_HAND` 的具体角度，仍然必须由后续教学依据与人工裁定决定。**

### 为什么必须区分

Rig 的 neutral pose 处于**关节活动范围中段**时蒙皮最稳定；
而 `STANDARD_HAND` 是**功能姿态**，接近屈曲一端。**两者本来就应该不同。**
（已写入 `PIANO_HAND_MASTER_ASSET_SPEC_R1.md` §10.1）

**→ `HR-06c` 不再阻塞 Stage 1。**

---

## 7. `HR-09` 裁定

> ## ✅ `HR-09` = **`OPTIONAL_NON_BLOCKING`**

**主题**：是否使用开源 CC0 手部模型正交渲染图作为一致性校验基准。

| | 内容 |
| --- | --- |
| **✅ 允许用途** | 真手多视角**几何比例辅助校验** / **视角尺度一致性**检查 / **姿态漂移辅助比对** / 作为**内部 QC 参考** |
| **🚫 禁止用途** | 不得**代替真人参考图** / 不得作为 **Hunyuan3D 正式生成输入** / 不得作为**解剖学最终权威** / **不得因为没有 CC0 校验模型而阻塞 Stage 1** |

> 若后续找到合适且授权清晰的 CC0 模型，可以使用。
> **如果没有，不影响 Stage 1。**

---

## 8. `REFERENCE_GAP-02` 新定义

> ## 🔄 `REFERENCE_GAP-02` = **`REFERENCE_SOURCE_TO_BE_ACQUIRED_IN_STAGE1`**

| 项 | 内容 |
| --- | --- |
| **内容** | 尚未实际获得满足要求的：**同一只 `ADULT_NEUTRAL` 解剖学右手 + 同一 `CANONICAL_HAND_POSE` + 完整 8 视图 + 合法授权** 的参考图包 |
| **🚫 不阻塞** | ① Stage 0 完成　② Phase 1 冻结　③ **Stage 1 启动** |
| **🔴 必须阻塞** | **Stage 1 → Stage 2** |

### 为什么改判

> **Stage 1 本身的任务，就是去采集 / 获取 / 授权这些参考素材。**
> 因此这个问题不应继续定义为"阻塞 Stage 1 启动"。
> **不要把"尚未拍摄参考图"继续解释成 Stage 0 研究失败。**

**正确阶段状态**：`STAGE0 = COMPLETE` / `STAGE1 = READY_TO_START`。
**但 Stage 1 → Stage 2 仍由 `REFERENCE_ACQUISITION_GATE` 严格控制。**

---

## 9. `REFERENCE_ACQUISITION_GATE` 定义

> ## 🔒 位置：**Stage 1 → Stage 2**
> **只有以下 12 项全部满足 → `REFERENCE_ACQUISITION_GATE` = `PASS` → 才允许进入 Stage 2。**
> **否则：`Stage 2` = `BLOCKED`。**

| # | 条件 |
| --- | --- |
| **1** | 已获得同一只 **`ADULT_NEUTRAL` 解剖学右手** |
| **2** | 全部 8 张来自**同一只手、同一次采集会话、同一个 `CANONICAL_HAND_POSE`** |
| **3** | 采集原则 **`HAND = FIXED` / `LIGHT = FIXED` / `CAMERA = MOVES`** 已实际遵守 |
| **4** | **完整 8 视图存在**：DORSAL / PALMAR / RADIAL / ULNAR / DISTAL / PROXIMAL / DORSAL_OBLIQUE_RADIAL / DORSAL_OBLIQUE_ULNAR |
| **5** | **手悬空** —— 掌部、手指、指尖没有：接触桌面 / 接触琴键 / 接触支架 / 被支撑压平掌弓 |
| **6** | **短前臂存在**，足以表达**前臂—手腕—手掌**方向与连续关系 |
| **7** | 8 张图完成**一致性 QC**：姿态一致 / 手指张开一致 / 掌宽比例一致 / 指长比例一致 / 拇指旋前一致 / 无明显时间漂移 |
| **8** | 若使用单相机环绕：**`DORSAL_PRE` / `DORSAL_POST` 漂移校验 PASS** |
| **9** | **授权完成**：至少存在 `LICENSES.md`，并明确——模特授权 / 图片使用权 / **商业数字教材使用范围** / **是否允许修改与 AI 3D 生成** |
| **10** | **图片技术参数 PASS**：`RAW_IMAGE_TOTAL_TARGET` ≤ ~6 MB；`BASE64_ENCODED_TOTAL` ≤ 8 MB |
| **11** | **Hunyuan3D 3.1 `ViewType` 映射检查 PASS** |
| **12** | **`MULTIVIEW_REFERENCE_PACK_SPEC` Pre-flight Checklist 全部 PASS** |

### 🚫 严禁为了赶进度

- 拼不同人的手
- 拼不同姿态
- 用左手补右手
- 用 AI 图片补真人视角
- 用 CC0 模型图代替正式真人输入
- 缺视角也强行提交

（对应风险登记册新增 **RK-17**）

---

## 10. `GATE 1` 最终状态

> ## ✅ `GATE 1` = **`PASS`**

| 判定依据 | 状态 |
| --- | --- |
| 研究已完成 | ✅ |
| `CANONICAL_HAND_POSE` 已定义 | ✅ |
| 多视角方法学已定义 | ✅ |
| HY-3D-3.1 八视图基线已确认 | ✅ |
| `HR-06` 已批准 | ✅ |
| `HR-08` 已批准 | ✅ |
| `HR-07` 已解决 | ✅ |
| `HR-06b` / `HR-06c` 已批准为技术范围 | ✅ |
| `HR-09` 已降为 `OPTIONAL_NON_BLOCKING` | ✅ |
| 参考图从哪里来 = Stage 1 的执行任务 | ✅ 不构成 Stage 0 失败 |

**→ `GATE 1` = PASS。Stage 0 完成，可以进入 Stage 1。**

---

## 11. Stage 0 Freeze 状态

> ## 🔒 `STAGE0` = **`FROZEN`**

| 项 | 状态 |
| --- | --- |
| **Stage 0** | ✅ **COMPLETE** / 🔒 **FROZEN** |
| **冻结内容** | 教学研究 · 母版姿态规范 · 多视角规范 · 资产规范 · 流水线 · 参考清单 |
| **未做** | 未建 mesh、未生成、未绑定、未动画、未编码、未采集图片 |

**冻结后的产出清单（8 份）**：

| # | 文件 |
| --- | --- |
| 1 | `docs/PIANO_HAND_PEDAGOGY_RESEARCH_R1.md`（**未修改**） |
| 2 | `docs/CANONICAL_HAND_POSE_SPEC_R1.md` |
| 3 | `docs/MULTIVIEW_REFERENCE_PACK_SPEC_R1.md` |
| 4 | `docs/PIANO_HAND_MASTER_ASSET_SPEC_R1.md` |
| 5 | `docs/PIANO_HAND_PRODUCTION_PIPELINE_R1.md` |
| 6 | `reference_manifest/REFERENCE_MANIFEST_R1.json` |
| 7 | `docs/PHASE1_R1_1_AMENDMENT_REPORT.md` |
| 8 | `docs/PHASE1_R1_2_FINAL_CLOSURE.md`（本文件） |

---

## 12. 下一阶段允许做什么 / 禁止做什么

### ✅ Stage 1 允许

| # | 允许 |
| --- | --- |
| 1 | **开始真人右手多视角采集**（悬臂固定前臂末端、手悬空、相机绕手移动到 8 机位） |
| 2 | 搭建固定环绕柔光环境（柔光帐 / 大面积漫射） |
| 3 | 选择多相机同步或单相机快速环绕（后者须做 `DORSAL_PRE` / `DORSAL_POST` 漂移校验） |
| 4 | 办理模特授权、图片使用权、**商业数字教材使用范围**、**是否允许修改与 AI 3D 生成** |
| 5 | 编写 `LICENSES.md` |
| 6 | 执行一致性 QC 并产出 `CONSISTENCY_REPORT.md` |
| 7 | （可选）使用 CC0 模型正交图作**内部 QC 参考**（不得作生成输入） |
| 8 | 实测两个总量数值：原始总量 vs ~6 MB 目标；Base64 编码后 vs 8 MB 硬约束 |
| 9 | 在 Stage 1 → Stage 2 处执行 `REFERENCE_ACQUISITION_GATE` 12 项检查 |

### 🚫 Stage 1 禁止

| # | 禁止 |
| --- | --- |
| 1 | 🚫 **拼不同人的手** |
| 2 | 🚫 **拼不同姿态** |
| 3 | 🚫 **用左手补右手** |
| 4 | 🚫 **用 AI 图片补真人视角** |
| 5 | 🚫 **用 CC0 模型图代替正式真人输入** |
| 6 | 🚫 **缺视角强行提交** |
| 7 | 🚫 翻转 / 转动 / 重新摆放手（违反 `HAND = FIXED`） |
| 8 | 🚫 光源随相机移动（违反 `LIGHT = FIXED`） |
| 9 | 🚫 让手部接触实体平面、压平掌弓 |
| 10 | 🚫 未通过 `REFERENCE_ACQUISITION_GATE` 就调用 Hunyuan3D |
| 11 | 🚫 创建 mesh / 制作 Rig / 制作动画 / 进行 Three.js 开发（属 Stage 4 之后） |

> **⚠ 本轮（R1.2）停止后，在完成 Human Review 之前，上述"允许"项也不得启动。**

---

## 13. 最终状态输出

```
HR_06B                      = APPROVED_AS_TECHNICAL_RANGE
HR_06C                      = APPROVED_AS_TECHNICAL_RANGE
HR_09                       = OPTIONAL_NON_BLOCKING

MULTIVIEW_FIRST_PASS        = 8_VIEWS

LIGHTING_RULE               = HAND_FIXED_LIGHT_FIXED_CAMERA_MOVES

IMAGE_SIZE_RULE             = RAW_APPROX_6MB / BASE64_ENCODED_MAX_8MB

REFERENCE_GAP_02            = REFERENCE_SOURCE_TO_BE_ACQUIRED_IN_STAGE1

GATE_1                      = PASS

REFERENCE_ACQUISITION_GATE  = REQUIRED_BETWEEN_STAGE1_AND_STAGE2

PIANO_HAND_PHASE1_R1_2      = PASS

STAGE0                      = FROZEN

STAGE1                      = READY_TO_START
```

### 已批准项汇总（不重开）

| ID | 状态 |
| --- | --- |
| `HR-06` | **APPROVED**（手 + 短前臂） |
| `HR-06b` | **APPROVED_AS_TECHNICAL_RANGE**（约 10–15°） |
| `HR-06c` | **APPROVED_AS_TECHNICAL_RANGE**（MCP 20–30° / PIP 25–35° / DIP 10–20°） |
| `HR-07` | **RESOLVED**（`HAND` / `LIGHT` / `CAMERA` 三固定 + 移动原则） |
| `HR-08` | **APPROVED**（`ADULT_NEUTRAL`） |
| `HR-09` | **OPTIONAL_NON_BLOCKING** |
| `REFERENCE_GAP-01` | **CLOSED**（HY-3D-3.1） |
| `REFERENCE_GAP-05` | **CLOSED**（`ADULT_NEUTRAL`） |
| `DIP_ERROR_DEMO_CONFLICT` | **RESOLVED**（双模式） |

### 仍 OPEN（但**不阻塞 Stage 1**）

| ID | 事项 | 阻塞于 |
| --- | --- | --- |
| `HR-01` | 手指弯曲程度与触键部位（Lhevinne vs Taubman） | Stage 8 |
| `HR-02` | 手腕具体高度 | Stage 8 |
| `HR-03` | 是否主动抬指、抬多高 | Stage 8 |
| `HR-04` | "手腕水平"的表述与可视化方式 | 教学文案 |
| `HR-05` | 错误手型对比优先级；E-02 阈值 | 错误对比资产 |
| `HR-10` | 面数预算最终数值 | Stage 4 / 11 |
| `HR-11` | 尺度参考值 | Stage 4 / 11 |
| `HR-12` | 键面接触平面标定 | Stage 4 / 11 |
| `HR-13` | `ERR_COLLAPSED_DIP` 实现路径 | Stage 8 |
| `HR-14` | DIP 反折程度 | Stage 8 |
| `REFERENCE_GAP-03` | 院校官方教材未获取 | 教学背书 |
| `REFERENCE_GAP-04` | 手型量化角度数值缺失 | Stage 8 |
| `REFERENCE_GAP-06` | 键面参照 / 键宽 / 键下沉深度 | Stage 11 |

---

## 14. 停止条件

**R1.2 收口完成，立即停止。**

本轮**未**进行且**不得**进行：

- 🚫 开始拍摄
- 🚫 搜索或下载参考图
- 🚫 调用 Hunyuan3D
- 🚫 创建 mesh
- 🚫 打开 Blender 建模
- 🚫 制作 Rig
- 🚫 制作动画
- 🚫 开始 Three.js

**等待 Human Review。**
