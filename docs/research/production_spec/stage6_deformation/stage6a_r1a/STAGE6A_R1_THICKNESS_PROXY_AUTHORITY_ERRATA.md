# STAGE6A_R1_THICKNESS_PROXY_AUTHORITY_ERRATA

- **stage**: STAGE6A_FORMAL_ERRATA
- **issued under**: STAGE5B_R1B_THUMB_MCP_IP_NARROW_WEIGHT_REPAIR + STAGE6A_R1A_ISOLATED_FLEX_REQUALIFICATION
- **issued at**: 2026-09-30
- **supersedes (for future rounds only)**: the deformation-authority status of the Stage6A R1
  local thickness ray-cast proxy
- **historical files**: **NOT edited** (see §6)

---

## 一、勘误缘起

Human Review 在对 Stage6A R1 的裁决中指出：Stage6A R1 使用的 **local thickness ray-cast
proxy** 在**凹面 / 折叠区域**（尤其 MCP 谷底、45° 全屈的掌侧褶皱）明显不稳定 ——
既可能给出极小值，也可能给出数百倍乃至数千倍的异常值。

正式勘误如下。

---

## 二、原始方法（Stage6A R1，`s6a_run_cases.py::thickness_proxy`）

对 patch 采样顶点 `v`：

1. 求 `v` 到该指 **chain polyline** 的最近点 `q`，方向 `dw = normalize(q - v)`（即大致**向轴心/内侧**）；
2. 把起点沿 `dw` 外推 `5e-7 m`（0.5 µm）避开自身面片；
3. 用 `ob.ray_cast` 沿 `dw` 打一条射线，`distance = 0.5 m`；
4. 首次命中距离即为该点的 "thickness"；
5. `thickness_ratio = t_case / t_bind`。

---

## 三、不稳定性证据（来自现有 `STAGE6A_PINCH_COLLAPSE_AUDIT.json`，未回改）

### 3.1 动态范围达 5 个数量级

| 指标 | 最小 | 最大 |
|---|---|---|
| `min_local_thickness_proxy_mm` | **0.000549**（IDX_MCP_45） | **16.078711**（MID_PIP_15） |
| `thickness_ratio_min` | **1.5e-05**（LTL_MCP_30） | **0.987011**（RNG_PIP_15） |

一个"厚度"量在同一个模型、同一批关节上跨 5 个数量级，本身即说明它不是一个稳定几何量。

### 3.2 **对角度的非单调性**（决定性反证）

同一关节、同一采样点集，仅改变屈曲角：

| case | thickness_ratio_min |
|---|---|
| LTL_MCP_15 | 1.6e-05 |
| LTL_MCP_30 | **1.5e-05** ← 比 45° 更"薄" |
| LTL_MCP_45 | 0.1095 |
| MID_MCP_15 | 0.02507 |
| MID_MCP_30 | **2.8e-05** ← 比 15° 与 45° 都薄 |
| MID_MCP_45 | 0.2006 |

如果该 proxy 真的度量"背-掌向实体厚度"，它必须**随屈曲角单调下降**。
实测**非单调** ⇒ 它度量的是**射线首次命中的偶然性**，而非厚度。

### 3.3 失效机制

在凹面 / 折叠区，射线沿"指向指链轴的向内方向"发射，首次命中可能是：

- **(a)** 已经闭合的褶皱近侧壁 → 距离 ≈ 0（产生"厚度 ≈ 0"的假 collapse 读数）；
- **(b)** **相邻手指**的表面（RSSF 绑定位姿下拇指-食指最小链距仅 3.28 mm，掌心各指谷底同样贴近）；
- **(c)** 掠射自命中（grazing hit）。

三者都与"背面-掌面实体厚度"无关。

---

## 四、正式定位

```
LOCAL_THICKNESS_PROXY = DIAGNOSTIC_ONLY
```

- **不得**再把 `IDX_MCP thickness ≈ 0`（或任何 case 的 `thickness_ratio_min ≈ 0`）
  **单独**作为**真实 collapse 的硬证据**。
- 该量可以继续被计算和记录，但只作为**辅助线索**，其单点极小值**不构成**任何 PASS/FAIL 判据。

---

## 五、Deformation authority 优先级（binding，本勘误生效后）

```
1. actual mesh visual evidence            （HR 同机位渲染目视）
2. face-area strain                       （min / p05 / median / p95 的 face-area ratio）
3. edge strain                            （min edge ratio / max edge stretch）
4. self-intersection                      （新增相交面对 + penetration proxy）
5. local surface-area / contour behaviour （patch 局部面积比、contour 行为）
6. thickness proxy                        = DIAGNOSTIC ONLY
```

**推论**：本轮 STAGE6A_R1A 的候选接受逻辑**完全不使用** thickness proxy，只使用
第 2–5 项（见 `STAGE6A_R1A_THUMB_WEIGHT_CANDIDATE_RANKING.json` 的
`objective` 与 `acceptance` 字段）。

---

## 六、历史文件处理

以下文件**保持原样，不回改**（provenance）：

```
stage6_deformation/stage6a/STAGE6A_PINCH_COLLAPSE_AUDIT.json
stage6_deformation/stage6a/STAGE6A_REPORT_R1.md          （§十三 表与脚注）
stage6_deformation/stage6a/STAGE6A_THUMB_DISTAL_AUDIT.json
stage6_deformation/stage6a/scripts/s6a_run_cases.py      （thickness_proxy 实现保留）
```

历史报告中"distal thickness ratio min"等列**继续有效**，但按本勘误降级为
`DIAGNOSTIC_ONLY`；凡引用这些列的后续文件，必须同时引用本勘误。

---

## 七、对本轮的影响

- Stage6A R1A 的 `TH_IP_30 / TH_IP_45 / TH_MCP_45` 修复目标**不再包含**
  任何 thickness proxy 指标。
- 「TH_IP 内侧褶皱是否真的闭合」这一类判断，改为由 **face-area strain + intra-thumb
  self-intersection + HR 目视**三者共同承担。
- `THUMB_DISTAL` / `NAIL` 的判据亦不依赖 thickness proxy。

---

## 八、状态

```
STAGE6A_R1_THICKNESS_PROXY_AUTHORITY = DIAGNOSTIC_ONLY   （本勘误生效）
DEFORMATION_AUTHORITY_PRIORITY       = 见 §五
HISTORICAL_R1_FILES                  = UNCHANGED
```
