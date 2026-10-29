# C-2（MakeHuman / MPFB2）轻量备选核验

> 阶段：`STAGE1C_C1_ASSET_QUALIFICATION`　日期：2026-09-27
> 按要求：**本轮不做 MakeHuman 手部的完整制作**，只做"许可 + 关键能力"的轻量核实。
> 结论前置：**因 C-1 未 FAIL（判定为 CONDITIONAL_PASS），本轮不需要继续深挖 C-2**（按人工指令 §十）。

---

## 1. 官方许可（已核实）

| 项 | 内容（官方原文） |
| --- | --- |
| 官方许可页 | `https://static.makehumancommunity.org/about/license.html` |
| **代码许可** | MakeHuman = **AGPL**；MPFB = **GPL**（原文："The source code of MPFB is shared under GPL and the source code of MakeHuman is shared under AGPL."） |
| **资产许可** | 原文："**All core assets are shared under Creative Commons, CC0.**"（并明确："you are free to do as you see fit with the asset or derivates of the assets. You do not need to pay anything, include any copyright notices nor give attribution."） |
| **导出物许可** | 官方 FAQ：导出模型为 **CC0**；"Can I sell models created with MakeHuman? **Yes.**"；"Do I need a separate commercial license...? **No**" |
| 2020 年许可澄清 | 官方 FAQ 记录：自 2020-09 起，**base mesh / targets / proxies 由 AGPL 改为 CC0 图形资产**；导出物"只包含本来就是 CC0 的内容" |
| 与本项目冲突 | **无**（与 C-1 同为 CC0 级） |
| 附带注意 | 第三方资产仓库中的用户上传资产**不适用**上述 CC0，需逐个核查（官方原文已声明） |

→ **`C2_LICENSE = CC0`（代码 AGPL/GPL 不影响交付物）**

---

## 2. 关键能力（文档级核实，**未实测**）

| 问题 | 答复 | 证据等级 |
| --- | --- | --- |
| 是否能输出**成人中性**人体？ | 可以。MakeHuman 基于"单一 androgynous（中性）基础网格"做线性插值变形，性别/年龄/体型均为滑杆参数 | 官方文档/维基描述（**未实测**） |
| 是否有**完整手指骨架**？ | 官方资料显示其基础网格含"通用骨架结构以支持姿势"，且官方曾专门展示 **hand topology 的演进**（Evolution of the hand topology）；**是否存在 5 指 × 3 骨的完整手指骨链，未在本轮实测** | ⚠ **未实测**（标记为 `TO_BE_VERIFIED_IN_C2_STAGE`） |
| hand topology 是否值得作为 C-1 备选？ | 官方明确把"通用拓扑（universal mesh）+ 手部拓扑演进"作为设计目标，方向与"可 Rig、可复用"一致；但**手部解剖精度是 MakeHuman 的公认弱项**（`SB-R2`） | 方向可信，**精度未验证** |

---

## 3. 本轮 C-2 判定

```
C2_LICENSE              = CC0            （已验证）
C2_HAND_TOPOLOGY        = NOT_VERIFIED   （本轮不深挖）
C2_ROLE                 = RETAINED_AS_ALTERNATE（保留为备选，不启动正式资格审查）
C2_FORMAL_QUALIFICATION = NOT_TRIGGERED   （因 C-1 ≠ FAIL）
```

> 触发条件（记录备查）：**仅当 C-1 最终被判 `FAIL`**，或人工在 Amendment Review 中要求双来源对比时，
> 才启动 `STAGE1C-C2_MAKEHUMAN_ASSET_QUALIFICATION`（届时需实测导出模型、检查手指骨链与手部拓扑）。
