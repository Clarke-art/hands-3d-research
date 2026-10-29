# STAGE 2 · ROUTE C · GEOMETRY BOOTSTRAP · R1

> `production_spec/stage2_bootstrap/STAGE2_ROUTE_C_BOOTSTRAP_REPORT_R1.md`
> 项目：钢琴教学双手 3D 交互资产
> 阶段：**`STAGE2_ROUTE_C_GEOMETRY_BOOTSTRAP`**
> 日期：2026-09-28　状态：**`READY_FOR_HUMAN_REVIEW`**
>
> **执行授权**：Human Review 已完成 —— `STAGE0_ROUTE_C_R1_3_1 = APPROVED`、`CURRENT_AUTHORITY_CONSISTENCY = PASS`、
> `STAGE0 = FINAL_REFROZEN`；正式授权 `STAGE2 = START_ROUTE_C_BOOTSTRAP`。
>
> **本轮唯一目标**：`SOURCE ASSET → PROJECT WORKING COPY`（+ 完整 provenance / receipt）。
> **本轮不做任何模型工程。**

---

## 0. 本轮一句话结论

> ## ✅ `STAGE2_ROUTE_C_BOOTSTRAP = PASS`
>
> 已从 byte-frozen 官方 CC0 母文件中提取 **`Hand  - Realistic`**，建立项目正式工程工作副本
> **`RIGHT_HAND_BOOTSTRAP_C1`**（`production_spec/stage2_bootstrap/RIGHT_HAND_BOOTSTRAP_C1.blend`）。
> **几何逐字节等价**（`BOOTSTRAP_GEOMETRY_PARITY = EXACT`，网格签名与 UV 签名与源资产完全一致）。
> **官方母文件 byte-unchanged**（PRE = POST）。工作副本按设计**保留 source orientation，未做帧归一化**（归一化属 Stage 4 `CON-9`）。

---

## 1. 权威输入（锁定）

| 项 | 值 |
| --- | --- |
| 官方资产包 | **Blender Human Base Meshes v1.4.1** |
| 对象名 | **`Hand  - Realistic`**（`Hand` 与 `-` 之间**两个空格**；无尾随空格） |
| 官方母文件 | `references/licenses/blender_human_base_meshes/extracted/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend` |
| 锁定 SHA-256 | `3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137` |
| 母文件大小 | 49,420,489 bytes |
| LICENSE | **CC0** |
| 正式项目 Blender | **`D:\Blender\blender.exe`** |
| Blender Version | **5.1.2**（build hash `ec6e62d40fa9`） |

---

## 2. 官方母文件保护（BYTE-FROZEN）

| 检查 | 值 |
| --- | --- |
| `SOURCE_MASTER_HASH_PRE` | `3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137` |
| `SOURCE_MASTER_HASH_POST` | `3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137` |
| 判定 | ✅ **PRE = POST = 锁定值** |
| 母文件 mtime | **仍为 2026-09-27 20:55**（未被触碰） |
| 母文件目录 | **无 `.blend1` / 无任何新增文件** |
| 保存行为 | 母文件**全程只以 `-b` 读取**；`save_version` 置 **0**；工作副本使用 **`save_as_mainfile(copy=True)`** 写入**另一路径** |
| `SOURCE_MASTER_BYTE_UNCHANGED` | **YES** |

---

## 3. 工作副本建立

### 3.1 产出文件

| 文件 | 说明 |
| --- | --- |
| `production_spec/stage2_bootstrap/RIGHT_HAND_BOOTSTRAP_C1.blend` | **工程工作副本**（1,999,990 bytes ≈ 2.0 MB） |
| `production_spec/stage2_bootstrap/BOOTSTRAP_RECEIPT.json` | Bootstrap 收据（全字段 provenance） |
| `production_spec/stage2_bootstrap/BOOTSTRAP_VERIFICATION_INDEPENDENT.json` | 独立进程复核结果 |
| `production_spec/stage2_bootstrap/SOURCE_STRUCTURE_PROBE_R1.json` | 母文件结构只读探针（保留可审计） |
| `production_spec/stage2_bootstrap/scripts/` | 全部只读/构建脚本 |

```
working_copy_sha256        = 8fa9a5498dc5b06dc4d8fba116ebe3cedc03e4a4645921ae10df3edab805ef83
working_copy_size_bytes    = 1999990
```

### 3.2 精简范围

| 项 | 源母文件 | 工作副本 |
| --- | --- | --- |
| objects | 407 | **1**（仅 `Hand  - Realistic`） |
| meshes | 227 | **1** |
| collections | 19 | **2**（`Human Base Meshes` → `Realistic`，保留资产的分类祖先链） |
| cameras | 25 | **0** |
| scenes | 1（`Scene`） | 1（`Scene`） |
| objects removed | — | **406** |
| collections removed | — | **17** |
| orphan data purged | — | meshes 226 / cameras 25 |

**保留的资产数据（未破坏）**：
`mesh`（831 v / 1,649 e / 820 p / 3,298 loops）· `UV`（`UVMap`）· **`Multires`（levels = 1，total = 1，scale 层级未动）** ·
`object data`（location / rotation / scale / dimensions / matrix_world）· 源几何 · object 自定义属性
（`M3` / `MM` / `conform_object` / `cycles`）· asset 标记。

**明确排除（已在 receipt 中记录）**：
- `realistic_hand`（**CAMERA**，是 `Hand  - Realistic` 的子对象）——非几何、非"保持该对象正常打开所必需"，故不携带；
- 其余 405 个 bundle 人体现成资产 —— 不作无意义携带。

> 🚫 未携带整个 Human Base Meshes bundle 的其他人体资产。

---

## 4. Bootstrap 一致性验证（只读字段比对）

### 4.1 同进程比对（构建后立即重新打开工作副本）

`BOOTSTRAP_GEOMETRY_PARITY = **EXACT**`

| 字段 | 源资产 | 工作副本 | 一致 |
| --- | --- | --- | --- |
| vertex count | 831 | 831 | ✅ exact |
| edge count | 1,649 | 1,649 | ✅ exact |
| face count | 820 | 820 | ✅ exact |
| loop count | 3,298 | 3,298 | ✅ exact |
| quad / ngon / tri | 819 / 1 / 1,658 | 819 / 1 / 1,658 | ✅ exact |
| UV layers | `["UVMap"]` | `["UVMap"]` | ✅ exact |
| Multires state | `levels=1, total=1, render=1, sculpt=1` | 同上 | ✅ exact |
| materials | 0 | 0 | ✅ exact |
| shape keys | none | none | ✅ exact |
| vertex groups | `[]` | `[]` | ✅ exact |
| modifiers | `[Multires]` | `[Multires]` | ✅ exact |
| dimensions | 0.15118861 × 0.06505452 × 0.28285709 | 同上（逐位相同） | ✅ exact |
| scale | `(1,1,1)` | `(1,1,1)` | ✅ exact |
| location / rotation | `(1.40478158, 0.01132820, 0.35364550)` / `(0,0,0)` | 同上 | ✅ exact |
| **matrix_world** | 单位旋转 + 平移 | 同上（16 元素逐位相同） | ✅ exact |
| **mesh topology signature (SHA-256)** | `23ca92c8475682291b589248af60f4a8cd8d48c3289965e958fb14e48d7384b5` | **相同** | ✅ exact |
| **UV signature (SHA-256)** | `c1c559e26b3ede4b1275abd278d538671b11946a58ad24707d3482590f1ab74b` | **相同** | ✅ exact |

> **网格签名** = SHA-256 over（全部顶点坐标 double · 全部边索引 · 全部面顶点索引 · 全部 loop 顶点/边索引）；
> **UV 签名** = SHA-256 over（UV 层名 + 全部 UV 坐标）。二者相同 = **拓扑与几何逐比特等价**，非"合理变化"。

### 4.2 独立进程复核（关键：排除同进程缓存影响）

在**全新 Blender 进程**中仅打开磁盘上的工作副本，重算上述全部字段：

```
INDEPENDENT_BOOTSTRAP_VERIFICATION = PASS      （12/12 项 OK）
file_object_count = 1  -> ['Hand  - Realistic']
file_mesh_count   = 1      file_camera_count = 0      file_collection_count = 2
```

---

## 5. Asset Frame 状态（本轮**不**归一化）

```
SOURCE_FRAME_STATUS        = UNNORMALIZED_BY_DESIGN
FRAME_NORMALIZATION_STAGE  = STAGE4_CON9
```

| 项 | 值 |
| --- | --- |
| source asset orientation（R1.3.1 勘误后） | `RADIAL = +X` / **`DORSAL = -Y`** / **`PALMAR = +Y`** / `DISTAL = -Z` |
| canonical target frame | `+X = RADIAL` / `+Y = DORSAL` / `+Z = DISTAL` |
| `SOURCE_TO_CANONICAL_TRANSFORM` | `diag(1,-1,-1)` = `Rx(180°)`，`det = +1` |
| 本轮是否执行该变换 | **否**（`executed_in_stage2 = false`） |
| 原因 | `CON-9 ASSET_FRAME_NORMALIZATION` **属于 Stage 4**；Stage 2 禁止修改 geometry |

> ✅ `RIGHT_HAND_BOOTSTRAP_C1` **继续保存 source orientation**，已在 receipt 中显式记录。

---

## 6. Stage 2 禁止事项 —— 合规声明

本轮**未**执行（`GEOMETRY_OPS_PERFORMED = NONE_PERFORMED`）：

- 🚫 Apply Multires　🚫 新增 Subdivision　🚫 Retopo　🚫 补 MCP / CMC 环线
- 🚫 删除 / 新增顶点　🚫 RSSF re-pose　🚫 创建临时骨架
- 🚫 Rig　🚫 Skin Weight　🚫 加指甲　🚫 改 UV　🚫 改 origin　🚫 裁前臂
- 🚫 镜像左手　🚫 动画　🚫 Hunyuan3D　🚫 Three.js
- 🚫 直接保存官方母文件
- 🚫 **未自动进入 Stage 3**

```
GEOMETRY_MODIFIED  = NO
MULTIRES_APPLIED   = NO
REPOSE_PERFORMED   = NO
RETOPO_PERFORMED   = NO
RIG_CREATED        = NO
```

**注**：对象层面的"删除其他 406 个对象 / 17 个集合 + 孤儿数据清理"**不属于几何操作** ——
目标对象的 mesh / UV / Multires / object data / 变换**逐比特未变**（已由签名证明）。

---

## 7. Bootstrap Receipt 字段清单（`BOOTSTRAP_RECEIPT.json`）

`asset_name` · `source_bundle_version` · `source_parent_file` · `source_parent_sha256` · `license` ·
`bootstrap_runtime_path` · `bootstrap_runtime_version` ·
`source_vertex_count` · `source_edge_count` · `source_face_count` · `source_multires_levels` ·
`source_uv_layers` · `source_material_count` · `source_armature_state` · `source_shape_key_state` ·
`source_orientation` · `canonical_target_orientation` · `source_to_canonical_transform` ·
`frame_normalization_status` · `working_copy_path` · `working_copy_sha256` · `created_at`

外加：`source_loop_count` / `quad_count` / `ngon_count` / `triangle_count` / `source_dimensions` / `source_scale` /
`source_location` / `source_collection_path` / `source_custom_props` / **`source_mesh_signature_sha256`** /
**`source_uv_signature_sha256`** / `working_copy_size_bytes` / `reduction`（精简明细）/ `parity_detail`（逐字段比对）。

```
SOURCE_MASTER_BYTE_UNCHANGED = YES
GEOMETRY_MODIFIED  = NO
MULTIRES_APPLIED   = NO
REPOSE_PERFORMED   = NO
RETOPO_PERFORMED   = NO
RIG_CREATED        = NO
```

---

## 8. Stage 2 输出状态

```
STAGE2_ROUTE_C_BOOTSTRAP        = PASS

RIGHT_HAND_BOOTSTRAP_C1         = CREATED
SOURCE_MASTER_BYTE_UNCHANGED    = YES
BOOTSTRAP_GEOMETRY_PARITY       = EXACT

SOURCE_FRAME_STATUS             = UNNORMALIZED_BY_DESIGN
CON_9_ASSET_FRAME_NORMALIZATION = PENDING_STAGE4

C1_ASSET_QUALIFICATION          = UNCHANGED_CONDITIONAL_PASS
```

---

## 9. 停止条件 / 最终状态

**完成 Bootstrap 后立即停止。未自动执行 Stage 3。**

```
STAGE2  = COMPLETE
RIGHT_HAND_BOOTSTRAP_C1 = READY_FOR_GEOMETRY_REVIEW
STAGE3  = READY_FOR_HUMAN_REVIEW
```

**等待 Human Review。**

**文档状态：`READY_FOR_HUMAN_REVIEW`**
