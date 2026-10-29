# BLENDER 5.1.2 RUNTIME PARITY CHECK · R1

> `docs/BLENDER_5_1_2_RUNTIME_PARITY_CHECK_R1.md`
> 项目：钢琴教学双手 3D 交互资产
> 阶段：**`BLENDER_5_1_2_RUNTIME_PARITY_CHECK`**（极窄范围 · **READ-ONLY**）
> 日期：2026-09-27　状态：**`READY_FOR_HUMAN_REVIEW`**
>
> **本轮只回答一个问题**：`Blender 5.1.2` 能否在不改变 C1 Qualification 技术结论的前提下，作为本项目后续正式 Blender production runtime。
> **本轮不做**：重做 C1 / 重新资格审查资产 / Stage 4 / re-pose / Retopo / Rig / 修改 Stage 0。

---

## 0. 结论

> ## ✅ `BLENDER_5_1_2_RUNTIME_PARITY = PASS`
>
> 5.1.2 在**同一份官方资产**、**同一套算法**下复跑 5 项最小验证集：
> 资产发现 PASS、基础几何统计 **EXACT（26/26 字段零差异）**、Multires **PASS**、
> 拓扑环线枚举 **EXACT（base 与 L1 两份输出 JSON 逐字段 0 差异）**、渲染 **FUNCTIONAL**、
> 且**用户配置 diff = EMPTY**。
> → 推荐 `PROJECT_BLENDER_RUNTIME = D:\Blender\blender.exe`（Blender 5.1.2）。

---

## 1. 唯一指定运行时（严格按要求调用）

| 项 | 值 |
| --- | --- |
| **`BLENDER_RUNTIME`** | **`D:\Blender\blender.exe`** |
| `BLENDER_VERSION` | **5.1.2** |
| `BLENDER_BUILD` | **`ec6e62d40fa9`** |
| 调用方式 | **绝对路径**（`"/d/Blender/blender.exe" -b …`），**未使用 `where blender`** |
| 附加参数 | 所有调用均加 **`--factory-startup`**（不加载用户偏好 / 插件） |
| 是否调用 portable 4.5.9 | **否**（本轮全程未执行 4.5.9 binary） |

**Runtime banner（`evidence/runtime_banner.txt`）**：

```
Blender 5.1.2
	build date: 2026-05-19      build time: 01:37:34
	build commit date: 2026-05-18   build commit time: 13:43
	build hash: ec6e62d40fa9
	build branch: blender-v5.1-release
	build platform: Windows     build type: Release     build system: CMake
```

---

## 2. 环境只读证明（先快照 → 执行 → 再快照 → diff）

| 检查对象 | 方法 | 结果 |
| --- | --- | --- |
| `%APPDATA%\Blender Foundation\Blender\5.1\`（**全量文件**） | 执行前 / 执行后 各记录 `路径 + 大小 + mtime`，`diff` | **`USER_CONFIG_DIFF = EMPTY`**（21 个文件，前后完全一致，见 `evidence/userconfig_pre.txt` / `userconfig_post.txt` / `userconfig_diff.txt`） |
| 上述目录下的**子目录** | 前后快照 diff | `DIRS_DIFF = EMPTY` |
| `D:\Blender\`（Blender 安装，前两级） | 前后快照 diff | `BLENDER_INSTALL_DIFF = EMPTY`（`evidence/dblender_pre.txt` / `dblender_post.txt`） |
| **官方母文件**（`.blend`） | SHA-256 复核 | `3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137` → **与上一轮基线完全一致，未被修改** |
| portable 4.5.9（`…\.workbuddy\binaries\blender\`） | 查找是否有本次时段被改动的文件 | **无**（未删除、未修改） |
| 上一轮 C1 原始统计文件（`stage1c_c1_qualification/stats/*.json`） | 时间戳核对 | 仍为上一轮（21:00–21:19），**未被本轮覆盖**（本轮全部写入 `runtime_parity/` 独立目录） |
| `.blend` 保存行为 | 全程未调用任何保存 API | 无任何 `.blend` 被写出 |

> **未做**：未修改用户偏好 / addons / extensions / PATH / 注册表；未覆盖 Blender 安装；未卸载 portable 4.5.9。

---

## 3. 复用同一份官方 C1 资产（未重新下载、未换版本、未换文件）

| 项 | 值 |
| --- | --- |
| 资产包 | Human Base Meshes **v1.4.1**（上一轮已获取并留档） |
| 母文件 | `references/licenses/blender_human_base_meshes/extracted/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend` |
| 大小 / SHA-256 | **49,420,489 B** / **`3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137`**（与上一轮一致） |
| 目标资产名 | **`Hand  - Realistic`**（`Hand` 与 `-` 之间**两个空格**） |

---

## 4. TEST 1 · ASSET DISCOVERY

| 项 | 4.5.9（上一轮基线） | **5.1.2（本轮）** | 一致 |
| --- | --- | --- | :-: |
| object found | YES | **YES** | ✅ |
| type | MESH | **MESH** | ✅ |
| asset | YES | **YES** | ✅ |
| asset catalog | `fe53c157-b313-482f-b7a3-69e260232e6f` | **`fe53c157-b313-482f-b7a3-69e260232e6f`** | ✅ |
| mesh name | `Hand  - Realistic` | **`Hand  - Realistic`** | ✅ |

```
TEST1 = PASS
```

---

## 5. TEST 2 · BASE GEOMETRY STATS（字段级逐项对比）

| 字段 | 4.5.9 | **5.1.2** | 判定 |
| --- | --- | --- | :-: |
| vertices | 831 | **831** | ✅ |
| edges | 1649 | **1649** | ✅ |
| faces | 820 | **820** | ✅ |
| triangles | 0 | **0** | ✅ |
| quads | 819 | **819** | ✅ |
| ngons | 1 | **1** | ✅ |
| non-manifold edges | 0 | **0** | ✅ |
| boundary edges | 0 | **0** | ✅ |
| loose verts / edges | 0 / 0 | **0 / 0** | ✅ |
| closed manifold | True | **True** | ✅ |
| UV layers | 1（`UVMap`） | **1（`UVMap`）** | ✅ |
| materials | 0 | **0** | ✅ |
| armature | none | **none** | ✅ |
| vertex groups | 0 | **0** | ✅ |
| shape keys | 0 | **0** | ✅ |
| modifiers | Multires | **Multires** | ✅ |
| scale | [1,1,1] | **[1,1,1]** | ✅ |
| dimensions | 0.151189 × 0.065055 × 0.282857 | **完全相同** | ✅ |
| world bbox min / max | (1.348449, −0.019137, 0.148758) / (1.499637, 0.045918, 0.431615) | **完全相同** | ✅ |
| origin (world) | (1.404782, 0.011328, 0.353646) | **完全相同** | ✅ |
| signed volume | 5.369e-4 m³ | **5.369e-4 m³** | ✅ |
| surface area | 0.059182 m² | **0.059182 m²** | ✅ |

```
BASE_GEOMETRY_PARITY = PASS (EXACT_MATCH)
mismatch_count = 0 / 26 字段
未出现任何需要解释的差异字段
```

---

## 6. TEST 3 · MULTIRES

| 项 | 4.5.9 | **5.1.2** | 判定 |
| --- | --- | --- | :-: |
| Multires modifier 存在 | 是 | **是** | ✅ |
| `total_levels` | 1 | **1** | ✅ |
| `levels`(viewport) | 1 | **1** | ✅ |
| `render_levels` | 1 | **1** | ✅ |
| `sculpt_levels` | 1 | **1** | ✅ |
| L1 faces | 3,298 | **3,298** | ✅ |
| L1 verts | 3,300 | **3,300** | ✅ |
| L1 corners | 13,192 | **13,192** | ✅ |

```
MULTIRES_PARITY = PASS
```

---

## 7. TEST 4 · TOPOLOGY EDGE LOOP PARITY

### 7.1 脚本复用方式（透明记录）

- **算法、阈值、窗口定义、指轴定义、环线分类逻辑一律未改动**：`align < 0.45`、关节窗口 `min(11 mm, 12% 指长)`、五条指轴 `SEG`、`joints` 定义均逐字节相同（校验输出：`marker both=True`）。
- 唯一改动 = **输出路径重定向**（避免覆盖上一轮 C1 基线 JSON）：
  - `pass9_edge_loops.py`：**changed_lines = 2**（仅 `with open(...)` 一行）
  - `pass10_multires_loops.py`：**changed_lines = 2**（同上）
- 因 Blender 5.1 **没有出现 API 差异**，脚本**无需任何兼容性修改**即可运行。

### 7.2 结果对照（逐指逐关节环线计数）

**base 层**

| 指 | 环线总数 4.5.9 → 5.1.2 | MCP | PIP | DIP | 拇指 IP / MCP_T / CMC |
| --- | :-: | :-: | :-: | :-: | :-: |
| THUMB | 7 → **7** | 2 → **2** | — | — | IP 2 → **2** / MCP_T 2 → **2** / **CMC 0 → 0** |
| INDEX | 9 → **9** | 1 → **1** | 2 → **2** | 2 → **2** | — |
| MIDDLE | 8 → **8** | 1 → **1** | 2 → **2** | 2 → **2** | — |
| RING | 8 → **8** | 1 → **1** | 2 → **2** | 2 → **2** | — |
| LITTLE | 8 → **8** | 0 → **0** | 2 → **2** | 2 → **2** | — |

**multires L1**

| 指 | 环线总数 4.5.9 → 5.1.2 | MCP | PIP | DIP | 拇指 IP / MCP_T / CMC |
| --- | :-: | :-: | :-: | :-: | :-: |
| THUMB | 19 → **19** | MCP_T 2 → **2** | — | — | IP 4 → **4** / **CMC 0 → 0** |
| INDEX | 24 → **24** | 2 → **2** | 5 → **5** | 7 → **7** | — |
| MIDDLE | 24 → **24** | 5 → **5** | 4 → **4** | 5 → **5** | — |
| RING | 24 → **24** | 5 → **5** | 4 → **4** | 7 → **7** | — |
| LITTLE | 22 → **22** | 0 → **0** | 4 → **4** | 6 → **6** | — |

### 7.3 严格 diff

| 对比 | 差异数 |
| --- | :-: |
| `topology_rings.json`（base） 逐字段深比对 | **0** |
| `topology_rings_multires_l1.json`（L1） 逐字段深比对 | **0** |

> 比对为**深度递归**（含每个关节的 `world` 坐标、每条环线的轴向位置 `t`、`median_gap`、`ring_n_edges`、`gaps` 列表等全部字段，数值容差 `1e-9`）。
> 详见 `evidence/topology_parity_report.txt`。

```
TOPOLOGY_PARITY = EXACT   (total diffs = 0)
```

→ 与上一轮 C1 基线**完全一致**：base 各关节 0–2 圈、L1 的 PIP/DIP 4–7 圈、MCP 区部分不足、**THUMB CMC = 0**。
→ **`C1_TOPOLOGY = CONDITIONAL_PASS` 这一结论不因 runtime 改变而改变。**

---

## 8. TEST 5 · MINIMAL RENDER SMOKE

| 输出 | 说明 | 结果 |
| --- | --- | --- |
| `renders/EVIDENCE_DORSAL_5_1.png` | 背侧（相机 +Y），solid | ✅ 生成，模型正常可见，**背侧朝向与 4.5.9 一致**（拇指在画面左侧） |
| `renders/EVIDENCE_PALMAR_5_1.png` | 掌侧（相机 −Y），solid | ✅ 生成，**掌侧朝向一致**（拇指在画面右侧，可见大鱼际/掌心凹） |
| `renders/WIREFRAME_THUMB_CMC_5_1.png` | 拇指 CMC 近景线框 | ✅ 生成，线框拓扑可见 |

- Workbench 着色属性在 5.1.2 下**全部可用**：`engine / light / color_type / single_color / show_cavity / background_type / render_aa / use_boundary / use_even_offset` → `SHADING_UNAVAILABLE = []`。
- `scene.display.shading.light='FLAT' | 'STUDIO'`、Wireframe 修饰器（`use_replace = True` 默认）均正常。

### 8.1 一处"看起来像差异"的现象 → 已查清，**不是差异**

初次目视时，5.1.2 的线框图看着像"深色底"，4.5.9 的证据图看着像"浅色底"。
**逐字节解码 PNG 后确认**：两张图（以及全部 4.5.9 证据图）**背景 alpha 均为 0（透明）**——
因为母文件存有 `scene.render.film_transparent = True`、输出为 **PNG RGBA**，两个 runtime 行为**完全一致**；
"深/浅底"只是**图片查看器对透明区域的合成差异**，与实际渲染无关。

→ **结论：不存在背景/着色差异。** 本轮亦未要求 pixel-identical，不同版本的抗锯齿差异不构成 FAIL。

```
RENDER_RUNTIME = FUNCTIONAL
```

---

## 9. 差异清单（诚实列出）

| # | 差异 | 类别 | 影响 |
| --- | --- | --- | --- |
| — | **无实质差异** | — | — |
| 注 1 | 3 张 smoke 图的文件名不同（`*_5_1.png`） | 命名 | 无 |
| 注 2 | 文件字节大小与 4.5.9 版本不完全相同 | PNG 压缩/抗锯齿差异 | 无（不要求 pixel-identical） |
| 注 3 | 线性编码等 build flags 不同（5.1 vs 4.5 分支） | 版本固有 | 无（几何/拓扑结果证明无影响） |

> 按人工指令 §八：**未出现影响 C1 结论的差异**，因此不降级为 `CONDITIONAL_PASS`；
> 也不存在"只有 API / 渲染差异"的情形（连渲染差异都未成立）→ **判定 `PASS`**。

---

## 10. 运行时推荐与 provenance 处理

```
PROJECT_BLENDER_RUNTIME_RECOMMENDATION = D:\Blender\blender.exe      (Blender 5.1.2, build ec6e62d40fa9)
```

**推荐理由**（按要求）：这是**用户原有的正式 MSI 安装**（非 WorkBuddy 私有副本）、版本更新（5.1 > 4.5）、
已有正常配置环境（`%APPDATA%\Blender Foundation\Blender\5.1\` 含 userpref / addons / extensions）、
且本轮已实测其对本项目的资产与算法**完全等价**。

**portable 4.5.9 的处理（按 §九）**：

| 项 | 处理 |
| --- | --- |
| `<USER_HOME>\.workbuddy\binaries\blender\blender-4.5.9-windows-x64\` | **保留未动**，角色 = **`C1_QUALIFICATION_REPRO_RUNTIME`** |
| 是否删除 / 修改 | **否** |
| 历史 provenance | **不得篡改**：`C1_ASSET_QUALIFICATION` 的复现 runtime 仍记录为 **Blender 4.5.9 LTS (build 8bf95cbd38d1)** |

---

## 11. 对 C1 结论的处理（本轮不重新裁定）

| 项 | 结果 |
| --- | --- |
| `C1_ASSET_QUALIFICATION` | **`UNCHANGED_CONDITIONAL_PASS`** |
| `C1_GEOMETRY` | **`UNCHANGED_PASS`** |
| `C1_TOPOLOGY` | **`UNCHANGED_CONDITIONAL_PASS`** |
| 是否出现会改变资产技术事实的差异 | **否** |
| 是否重新裁定资格 | **否**（本轮无重裁权限，亦无重裁必要） |

---

## 12. 本轮未做（合规确认）

- 🚫 未 re-pose / 未加骨架 / 未 Retopo / 未补 MCP·CMC 环线 / 未加指甲 / 未调 UV / 未改 origin
- 🚫 未保存任何 `.blend`（无新母版）
- 🚫 未制作左手
- 🚫 未调用 Hunyuan3D
- 🚫 未进入 Three.js
- 🚫 未修改 Stage 0（`STAGE0 = FROZEN`、`STAGE2 = BLOCKED`）
- 🚫 未重新下载资产、未更换资产版本、未更换文件
- 🚫 未卸载 / 未修改 portable 4.5.9，未修改 PATH / 注册表 / Blender 配置
- 🚫 未进入 `STAGE0_ROUTE_C_AMENDMENT`
- ✅ 已完成：5 项最小验证集（asset discovery / base geometry / multires / topology / render smoke）＋ 只读性前后 diff ＋ 运行时推荐

---

## 13. 证据目录

```
production_spec/runtime_parity/blender_5_1_2/
├── evidence/
│   ├── runtime_banner.txt                     ← 5.1.2 版本/构建信息
│   ├── parity_stats.json                      ← TEST 1/2/3 原始输出
│   ├── topology_rings_5_1_2.json              ← TEST 4 base 层（5.1.2）
│   ├── topology_rings_multires_l1_5_1_2.json  ← TEST 4 L1（5.1.2）
│   ├── topology_parity_report.txt             ← 逐字段 diff + 逐指逐关节对照
│   ├── pass9_stdout_5_1_2.txt / pass10_stdout_5_1_2.txt
│   ├── userconfig_pre.txt / userconfig_post.txt / userconfig_diff.txt
│   ├── userconfig_pre_dirs.txt / userconfig_post_dirs.txt / userconfig_dirs_diff.txt
│   ├── dblender_pre.txt / dblender_post.txt / dblender_diff.txt
│   ├── localcache_post.txt
│   └── diag/ (bg_FLAT_WORLD.png, bg_STUDIO_WORLD.png, bg_FLAT_THEME.png)
├── renders/  (EVIDENCE_DORSAL_5_1.png, EVIDENCE_PALMAR_5_1.png, WIREFRAME_THUMB_CMC_5_1.png)
└── scripts/  (parity_stats.py, pass9_edge_loops.py, pass10_multires_loops.py,
               render_parity_5_1.py, diag_*.py)
```

---

## 14. 最终状态输出

```
BLENDER_5_1_2_RUNTIME            = DISCOVERED            (D:\Blender\blender.exe, 5.1.2, ec6e62d40fa9)

BLENDER_5_1_2_RUNTIME_PARITY     = PASS
BASE_GEOMETRY_PARITY             = PASS   (EXACT_MATCH, 26/26 字段零差异)
MULTIRES_PARITY                  = PASS   (total_levels=1; L1 3298 faces / 3300 verts 完全一致)
TOPOLOGY_PARITY                  = EXACT  (base + L1 两份输出逐字段 0 差异)
RENDER_RUNTIME                   = FUNCTIONAL
USER_CONFIG_DIFF                 = EMPTY

C1_ASSET_QUALIFICATION           = UNCHANGED_CONDITIONAL_PASS
C1_GEOMETRY                      = UNCHANGED_PASS
C1_TOPOLOGY                      = UNCHANGED_CONDITIONAL_PASS

PROJECT_BLENDER_RUNTIME_RECOMMENDATION = D:\Blender\blender.exe

C1_QUALIFICATION_REPRO_RUNTIME   = RETAINED (Blender 4.5.9 LTS, 未删除未修改)
C1_PROVENANCE                    = 保持记录为 Blender 4.5.9 LTS（不篡改历史）

STAGE0                           = FROZEN
STAGE2                           = BLOCKED
```

**等待 Human Review。本轮在此停止，不进入 `STAGE0_ROUTE_C_AMENDMENT`。**

**文档状态：`READY_FOR_HUMAN_REVIEW`**
