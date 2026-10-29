# STAGE5A_R2_INDEX_MCP_NUMERIC_ERRATA — R1

**性质**：勘误（errata）。**不修改**任何历史 R2 报告 / JSON；历史文件保持原样作为 provenance。

---

## 一、矛盾

| 来源 | 写法 | 值 |
| --- | --- | --- |
| `stage5a_r2/STAGE5A_R2_REPORT.md` §INDEX_MCP_R | `AXIAL_DELTA_FROM_APPROVED_T01` | **0.000 mm** |
| `stage5a_r2/STAGE5A_R2_STATUS.json` `gates.INDEX_MCP_T01_AXIAL_REGION` | `measured_axial_mm` / `delta_mm` | **−1.5157 mm** |
| 同上 | `t01_axial_mm` = 0.0，`zone_half_width_mm` = 9.364 | PASS |

## 二、独立复核（从 `RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2.blend` 重算，只读）

两个数字用的是**同一个原点**（批准的 Stage4B `INDEX_MCP_R.head = [1.445879102, 0.013830277, 0.479620308]`）、**同一个参考值 0.0**，差别只在**轴**：

| 轴 | 定义 | R2 点读数 |
| --- | --- | --- |
| A. MCP→TIP 弦 | 单位向量 `(INDEX_TIP_R.head − INDEX_MCP_R.head)`（均为冻结 Stage4B landmark） | **−1.5157 mm** |
| B. 近节指骨轴 | `(INDEX_PIP_R.head − INDEX_MCP_R.head)` | **−0.000008 mm** |

两轴夹角 **19.2607°**。
R2 的 INDEX_MCP 中心是在「过 R1 landmark、垂直于**B 轴**的平面内」搜索得到的 —— 所以沿 **B 轴**的偏移**按构造就是 0**；它不是一次测量，而是构造陈述。沿 **A 轴**才是对 R2 点的真实、可复现测量。

补充：R2 点相对批准点的总位移为 6.375 mm（−1.5157 mm 是其轴向分量）。

## 三、唯一权威来源（本轮正式指定）

```
文件  : stage5a_r2/STAGE5A_R2_STATUS.json
路径  : gates.INDEX_MCP_T01_AXIAL_REGION.measured_axial_mm
数值  : -1.5157 mm
规则  : INDEX_MCP axial authority
        = (R2 INDEX_MCP − 批准 INDEX_MCP) 在
          unit(INDEX_TIP_R.head − INDEX_MCP_R.head) 上的分量
        （两端点均为冻结 Stage4B landmark，因此该规则只依赖 R2 blend 即可复现，
          与被 re-pose 的网格无关）
```

**被取代的表述**：`STAGE5A_R2_REPORT.md` 中 `AXIAL_DELTA_FROM_APPROVED_T01 = 0.000 mm`
→ 判定为 **STALE PRE-FINAL MEASUREMENT**（实为另一轴上的构造陈述，非 T-01 轴向测量）。

## 四、几何结论（不变）

`|−1.5157| ≤ 9.364 mm` → `INDEX_MCP_T01_AXIAL_REGION = PASS`。
**INDEX_MCP geometry PASS 不变**；本次勘误只修正「哪一个数字是权威」，
不改变任何关节位置，不重开 INDEX_MCP 几何（brief §3 / §18）。

## 五、复核证据

`stage5a_r2a/_tmp/S5A_R2A_INDEX_MCP_RECON.json`（由 `stage5a_r2a/scripts/s5a_r2a_audit.py` 只读生成，
输入 sha256 = `615367d7fab3e75431fa7171e7e82f3a655c62e29ad7ddca5509b093e9f68c81`，执行前后一致）。
