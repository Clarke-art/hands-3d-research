# STAGE 4A · THUMB CMC LOCAL RETOPO — R2
## `STAGE4A_CMC_TOPOLOGY_REQUIREMENT_CORRECTION_AND_LOCAL_RETOPO_R2`

> 目录：`production_spec/stage4_blender/stage4a_r2/`
> 运行时：`D:\Blender\blender.exe` **Blender 5.1.2**（build `ec6e62d40fa9`）
> 输入：`RIGHT_HAND_ENGINEERING_STAGE4A_R2_BASE.blend`（CON-1 完成 / CON-2 未施加，R2 基线）
> 本轮范围：**只做 THUMB CMC 局部拓扑**。未 re-pose，未 Rig，未 Skin Weight，未改 origin，未重展 UV，未加指甲，未镜像左手，未进入 Stage 4B。
> 日期：2026-09-28
> 授权：Human Review R2 — **OPT-A = APPROVED**

---

## 0. 结论

> ## `CON_2_THUMB_CMC_TOPOLOGY = PASS_FOR_RIG_PIPELINE`
>
> ```
> CMC_TOPOLOGY_REQUIREMENT_CORRECTION   = PASS
> T01_CMC_TUBULAR_COLLAR_REQUIREMENT    = NOT_APPLICABLE
> T04_CMC_LOCAL_MULTIAXIS_SUPPORT       = PASS
> CON_2_THUMB_CMC_TOPOLOGY              = PASS_FOR_RIG_PIPELINE
> CON_3_POLE_AUDIT                      = PASS
> CON_1_MCP_TOPOLOGY                    = PASS_NO_REGRESSION
> ASSET_FRAME_NORMALIZATION             = PASS (未触碰)
> CANONICAL_FRAME_VALIDATION            = PASS (未触碰)
> DEFORMATION_TOPOLOGY_READY_FOR_RSSF   = YES
> OPT_B_MACRO_RETOPO                    = DEFERRED_UNLESS_STAGE6_FAILS
> STAGE4A                               = PASS
> STAGE4B_RSSF_REPOSE                   = NOT_STARTED（等待 Human Review）
> ```

本轮**实际执行了**网格手术：删除 legacy CMC 三条 66 mm helical pseudo-collars 的"CON-1 完成 /
CON-2 未施加"复现基线，在其上重建 **CMC LOCAL DEFORMATION CAGE**（同心环 + 径向辐条 + 全 quad 核心）。

---

## 1. 输入保护

| 项 | 值 |
| --- | --- |
| Stage-2 冻结 bootstrap | `8fa9a5498dc5b06dc4d8fba116ebe3cedc03e4a4645921ae10df3edab805ef83`（未触碰） |
| legacy 基线 `RIGHT_HAND_ENGINEERING_STAGE4A.blend` | `5f69d1ca…cbf40`（**保留不动**，provenance） |
| R2 基线 `RIGHT_HAND_ENGINEERING_STAGE4A_R2_BASE.blend` | `afbae673ac3e1a520c5a2d6b4e56c6cdc373394876569fb36510865bef7e54a4` |
| R2 基线构建 | `scripts/stage4a_r2_base.py` = `stage4a_engineer.py` 逐字复制，仅禁用 legacy CMC helical 插入（`LEGACY_CMC_INSERT_DISABLED = True`） |

R2 基线完整性：**V=3364 / E=6724 / F=3362；100% quad；0 三角；0 n-gon；0 边界边；0 松散几何。**

---

## 2. R2 交付物

```
RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend
  sha256 = 4fa2cb6f31d8097110718e4d9cc424c30d1d2b7057c76abd93c338a5c7201039
  bytes  = 2,006,774
  （根目录与 stage4a_r2/ 内为逐字节相同副本）
```

| 文件 | 内容 |
| --- | --- |
| `CMC_LOCAL_RETOPO_AUDIT_R2.json` | 机读审计（含逐项 T-04_CMC 检查、极点审计、顶点级差异证明） |
| `R2_CAGE.json` | 手术记录（盘选取、环、核心、极点滑移、逐条日志） |
| `R2_AUDIT.json` / `R2_BASE_AUDIT.json` | R2 与基线的同方法拓扑审计（含顶点坐标转储） |
| `renders/CMC_RETOPO_BEFORE_AFTER.png` | 左＝BEFORE（3 条 helical pseudo-collar 绕腕），右＝AFTER（笼体完全局部）。同一相机 |
| `renders/CMC_RETOPO_DORSAL.png` | 背侧特写：笼体 4 圈同心环 + 辐条，全部落在 ±12 mm 窗口内 |
| `renders/CMC_RETOPO_PALMAR.png` | 掌侧特写（x-ray，笼体在桡背侧故透视显示） |
| `renders/CMC_RETOPO_SIDE.png` | 侧视特写（x-ray） |
| `scripts/stage4a_r2_{base,cage,audit,render,composite,wire,probe}.py` | 全部可复现脚本 |

---

## 3. 手术设计（为什么这样建）

### 3.1 判据变更后的目标

按 R2 修正（`docs/CMC_TOPOLOGY_REQUIREMENT_CORRECTION_R1.md`），目标不是"绕掌骨的圆环"，
而是 **CMC LOCAL DEFORMATION CAGE**：围绕 CMC 旋转中心的局部 quad 笼状结构。

### 3.2 构造（保证 all-quad by design）

1. 以 CMC 表面顶点为源做 Dijkstra 测地场；
2. 取"所有顶点测地距离 ≤ R"的面集为盘，并**验证**它是欧拉示性数 = 1、
   单一简单边界环的拓扑圆盘（R = 20 mm 时：12 面 / 21 顶点 / 边界环 **16 边 = 16 顶点**）；
3. **删除盘内部，边界环逐字保留** —— 因此与 metacarpal / thenar / first web 的过渡
   与周边网格 bit-for-bit 不变（要求 C、E 由构造保证）；
4. 重建内部为：
   * **3 圈同心环**（每圈 16 顶点）+ **16 根径向辐条** → 3 × 16 = 48 个纯 band 四边面，**0 极点**；
   * **4 × 4 全 quad 网格核心** → 16 个四边面，**恰好 4 个 valence-3 角极点**；
     因 P、Q 均为偶数，网格**中心是规则 valence-4 顶点**，即 CMC 中心无极点。
5. 所有可能极点数下界由四边形网格盘的 index 恒等式
   `Σ_int(4−val) + Σ_bnd(1−val_in) = 4` 决定 —— 4 个 valence-3 角是**理论最小值**。

### 3.3 两次被否决的做法（记录在案，勿重试）

| 做法 | 结果 | 否决原因 |
| --- | --- | --- |
| 沿测地 spoke 取分数距离布环 | 环折成锯齿（最内环中位转角 **180°**，9/16 转角 > 90°） | 粗网格上相邻边界顶点的 Dijkstra 最短路互相交叉，环点失去环序 |
| `bmesh.ops.grid_fill` / 平面切割 / 调和场水平集 / 局部带 re-grid 端墙 | — | R1 已否决（n-gon / 三角） |

**最终采用：边界环向 CMC 表面点的欧氏径向收缩 + BVH 投影回原表面。**
它与边界环保持精确的 1:1 环序，四圈环的中位转角全部 ≈ 80°、最大 106°，无折叠。

### 3.4 参数

| 参数 | 值 |
| --- | --- |
| 盘半径 R | **20 mm**（测地）；边界环欧氏半径 7.50 … 15.64 mm（均值 11.60） |
| 环收缩系数 | 0.78 / 0.56 / 0.34（环均半径 8.8 / 5.9 / 3.6 mm） |
| 核心网格 | 4 × 4（P=Q=4，均偶 → 中心为规则顶点） |
| 核心朝向 | 旋转偏移按"4 个角极点远离 flexion/opposition strain path"自动选取 |
| 松弛 | 4 passes × 0.35 Laplacian，每 pass 后 BVH 投影回原表面 |
| 新增 | 57 顶点 / 64 四边面（原盘仅 12 面 → **密度 ×5.3**） |

---

## 4. 静态验收（§八 逐条）

| # | 要求 | 实测 | 判定 |
| --- | --- | --- | --- |
| 1 | locality 明确 | 全部 73 个笼顶点距 CMC ≤ 15.64 mm（R = 20 mm 球外 **0** 个）；最外环轴向跨度 22.99 mm | ✅ |
| 2 | 形状保持 | 对原表面偏差 **max 0.0001 mm**（每个新顶点都落在原表面上）；边界环逐字未动 | ✅ |
| 3 | all-quad | quads=3414 / tris=**0** / ngons=**0** | ✅ |
| 4 | edge density 足够 | 盘内 12 面 → 64 面（×5.3）；环边长 1.5 … 7.6 mm，局部网格边长 5.9 mm | ✅ |
| 5 | pole 路径合理 | 见 §5 | ✅ |
| 6 | first web / thenar 保持 | 修改区全部顶点距 CMC ≤ 25.1 mm；形状偏差 ≈ 0；边界环未动 | ✅ |
| 7 | 无 helical pseudo-collar | 三圈环轴向跨度 **22.99 / 16.56 / 10.02 mm**，全部 < 40 mm；winding 判据已按修正**不再适用** | ✅ |
| — | 流形 / 松散 | 非流形边 **0**；边界边 **0**；>2 面边 **0**；松散顶点/边 **0** | ✅ |
| — | 法向一致 | 笼内相邻面法向不一致对 **0**；64 面全部与原表面法向同向 | ✅ |

---

## 5. CON-3 pole audit（重跑）

### 5.1 CMC 邻域（≤ 25 mm 欧氏）内的极点

| | 极点数 | flexion midline 上 | opposition path 上 |
| --- | --- | --- | --- |
| **R2 基线（修正前）** | 2 | **2** | 0 |
| **R2 交付** | 18 | **0** | **0** |

⇒ 本轮把 CMC 邻域内**原本就在屈曲中线上的 2 个极点**一并滑出了 strain path。

宽窗口（25 mm 轴向）下剩余的 2 个 flexion-midline 极点位于 **v107（距 CMC 99.0 mm）** 与
**v566（96.8 mm）** —— 是手上其它部位的历史极点，**在授权修改范围之外**，本轮不处理。

### 5.2 CMC core（|轴向| ≤ 6 mm）内的极点

7 个，全部为笼体自身结构极点（4 个核心网格角 + 3 个接缝极点），
法向与背/掌中线的夹角 **48° … 118°**，无一落在屈曲中线（≤45°）或对掌路径（掌侧≤62° 且 桡侧≤75°）上。

### 5.3 极点滑移（允许的 "少量 pole reposition"）

6 个顶点、累计位移 ≤ **0.9 mm**、单步 0.9 mm、累计上限 4.0 mm；每次滑移后 BVH 投影回原表面。
⚠ 过程中曾发现滑移的轴向窗口会误伤远处顶点（一次跑出 103 mm 外的改动），已加
**双重作用域护栏**（欧氏 ≤ R×1.05 且轴向 ≤ 25 mm）后消除 —— 最终顶点级差异证明见 §6。

### 5.4 全手极点

基线 83 → R2 **99**（v3 62 / v5 36 / other 1）。增量为笼体结构极点，全部位于 CMC 邻域且远离 strain path。

```
CON_3_POLE_AUDIT = PASS
```

---

## 6. 无回归证明（顶点级）

以顶点世界坐标集合精确对比基线与交付：

| 项 | 值 |
| --- | --- |
| 基线顶点 | 3364 |
| 交付顶点 | 3416 |
| 保持原位不变 | **3334** |
| 被删除 | 30（盘内 5 个孤立顶点 + 25 个被滑移/松弛的顶点） |
| 新增 | 82（57 个笼顶点 + 25 个滑移后的新位置） |
| 被删顶点距 CMC 最大 | **25.05 mm** |
| 新增顶点距 CMC 最大 | **25.10 mm** |

⇒ **每个基线顶点要么原位不动、要么被删除，且所有改动都落在 CMC 25.1 mm 半径内。**
笼外网格逐比特不变，因此任何针对笼外区域的计数方式下 CON-1 都不可能回归。

同方法重跑全部 15 关节环线审计：

```
little  LITTLE_MCP=3, LITTLE_PIP=5, LITTLE_DIP=4
ring    RING_MCP=1, RING_PIP=4, RING_DIP=4
middle  MIDDLE_MCP=2, MIDDLE_PIP=3, MIDDLE_DIP=4
index   INDEX_MCP=2, INDEX_PIP=4, INDEX_DIP=4
thumb   THUMB_CMC=1, THUMB_MCP=4, THUMB_IP=4
REGRESSION vs baseline: 0 joint(s) changed
```

> 说明：此"重检法"（对最终网格重新做横向分量检测）对 MCP 区计出的数值低于
> `stage4a/JOINT_LOOP_AUDIT.json` 的记法（该记法 = L1 既有环 + 已插入且落入 band 的环，
> 两者口径不同，本轮**未改变**该记法也未重插任何 MCP 环线）。
> 由于笼外网格逐比特不变，**两种口径下 CON-1 都同样地"与基线完全一致"**，
> 故 `CON_1_MCP_TOPOLOGY = PASS_NO_REGRESSION`。

```
CON_1_MCP_TOPOLOGY = PASS_NO_REGRESSION
```

---

## 7. 未触发 STOP 条款

§七 规定：若必须扩大到整个 palm 或大范围 thenar 才能成立，须输出
`CMC_LOCAL_RET0PO_SCOPE = ESCALATES_TO_MACRO_RETOPO` 并停止。

本轮修改区域：以 CMC 为心 **≤ 25.1 mm** 半径（掌宽 ~80 mm），未触及整个 palm、
未触及 first web（虎口距 CMC 远大于 25 mm）、未触及手背大面积。

```
CMC_LOCAL_RET0PO_SCOPE = LOCAL_CMC_THENAR_NEIGHBOURHOOD (<= 25.1 mm)   -- 未升级
```

---

## 8. 最终状态

```
STAGE4A_CMC_TOPOLOGY_REQUIREMENT_CORRECTION_AND_LOCAL_RETOPO_R2 = COMPLETE

CMC_TOPOLOGY_REQUIREMENT_CORRECTION   = PASS
T01_CMC_TUBULAR_COLLAR_REQUIREMENT    = NOT_APPLICABLE
T04_CMC_LOCAL_MULTIAXIS_SUPPORT       = PASS
CON_2_THUMB_CMC_TOPOLOGY              = PASS_FOR_RIG_PIPELINE
CON_3_POLE_AUDIT                      = PASS
CON_1_MCP_TOPOLOGY                    = PASS_NO_REGRESSION
CON_4_NAILS / CON_5_RSSF_REPOSE / CON_6_ORIGIN / CON_7_UV = PENDING（未执行）
ASSET_FRAME_NORMALIZATION             = PASS（未触碰）
DEFORMATION_TOPOLOGY_READY_FOR_RSSF   = YES
OPT_B_MACRO_RETOPO                    = DEFERRED_UNLESS_STAGE6_FAILS
STAGE4A                               = PASS
STAGE4B_RSSF_REPOSE                   = NOT_STARTED

FINAL_CMC_DEFORMATION_AUTHORITY       = STAGE6_DEFORM_TEST_THUMB_OPPOSE
```

**未开始 RSSF re-pose，未进入 Stage 4B。等待 Human Review。**

**文档状态：`READY_FOR_HUMAN_REVIEW`**
