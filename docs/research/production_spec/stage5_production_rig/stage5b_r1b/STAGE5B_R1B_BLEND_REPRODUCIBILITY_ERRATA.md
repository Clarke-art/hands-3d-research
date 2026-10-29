# STAGE5B_R1B_BLEND_REPRODUCIBILITY_ERRATA

- **stage**: STAGE5B_R1B_FORMAL_ERRATA
- **issued under**: STAGE5B_R1B_STAGE6A_R1A_HUMAN_APPROVAL_FREEZE_R1
- **issued at**: 2026-09-30
- **subject**: `.blend` container byte reproducibility of the approved Stage5B R1B master
- **historical files**: **NOT edited** — `stage5b_r1b/STAGE5B_R1B_STATUS.json` keeps its original
  `blend_container_byte_reproducible` field untouched (see §六)

---

## 一、勘误缘起

`STAGE5B_R1B_STATUS.json` 中写有：

```
"output_r1b": { ..., "blend_container_byte_reproducible": false, ... }
```

而后继执行记录又出现「固定 build script 下最终 R1B hash 可稳定复现」的说法。
两者表面上冲突。**不得凭摘要直接改结论**，本轮做了一次最小只读/重建可重复性核验。

---

## 二、本轮核验方法（只读 + 仅写 `_tmp/`）

1. 用**未经修改的冻结** build 脚本
   `stage5b_r1b/scripts/s5b_r1b_build.py`，
   同一输入（冻结 R1A `c68e415a…c0ea6` + 已批准候选参数）、
   同一 Blender runtime（`D:\Blender\blender.exe` **5.1.2**），
   把副本重新生成到 **`stage5b_r1b/_tmp/rebuild/`**。
   **approved R1B master 从未被覆盖**（核验后哈希仍为 `cec5804f…`）。
2. 同一临时路径**连续重建两次**，比较两次产物。
3. 对 approved master 与临时副本做**逐字节差异定位**与**语义载荷逐字段比较**
   （顶点坐标、拓扑、UV、材质索引、vertex group 权重、骨骼表、object matrix、绑定位姿）。

---

## 三、核验结果

### 3.1 同一输出路径 → 字节确定

```
两次连续重建（同一 _tmp/rebuild 路径）：
  8cb6bd46e0354367b8156c4277e9741095194c9e15147b2fd5ff77bafafd5c9c
  8cb6bd46e0354367b8156c4277e9741095194c9e15147b2fd5ff77bafafd5c9c   ← byte-identical
```

### 3.2 不同输出路径 → 字节不同，但差异极小且**非语义**

| 项 | 值 |
|---|---|
| approved master | `cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10` |
| 临时副本 | `8cb6bd46e0354367b8156c4277e9741095194c9e15147b2fd5ff77bafafd5c9c` |
| 文件大小 | 2 296 143 B（**两者完全相同**） |
| 差异字节数 | **36 / 2 296 143**（0.0016 %） |
| 差异位置 | 全部位于 Blender DNA `DATA` 块内 |
| 差异性质 | **全部 36 B 都落在 8 字节槽位中，且高 40 位相同的成对地址值（内部指针 / 数据块顺序字段）** |

即：差异是**容器内部指针值**，不是任何几何、权重或绑定数据。

### 3.3 语义载荷逐字段比较 → **全部一致**

| 载荷字段 | 结果 |
|---|---|
| `V` / `E` / `F` / `TRIS` | IDENTICAL |
| `vertex_coords_sha`（世界坐标） | IDENTICAL |
| `topology_sha` | IDENTICAL |
| `uv_sha` | IDENTICAL |
| `material_index_sha` / `materials` | IDENTICAL |
| **`weights_sha`（3416 顶点 × 16 组，逐组逐顶点）** | **IDENTICAL** |
| `max_influences` | IDENTICAL（4） |
| `vertex_groups` | IDENTICAL |
| `bone_table_sha` / `bone_count` | IDENTICAL（21） |
| `object_matrix_sha` / `parent` / `armature_modifier` | IDENTICAL |
| `pose_all_identity`（保存态 = ZERO / RSSF） | IDENTICAL |

---

## 四、正式结论（binding）

```
BLEND_CONTAINER_BYTE_REPRODUCIBILITY = NOT_GUARANTEED
REPRODUCIBLE_UNDER_FIXED_OUTPUT_PATH  = TRUE
SEMANTIC_PAYLOAD_REPRODUCIBILITY      = PASS
CAUSE_OF_BYTE_DIFFERENCE              = INTERNAL_DNA_POINTER_VALUES_ONLY
```

- `.blend` 容器字节**不保证**跨输出路径/环境可复现：Blender 在保存时写入内部内存地址
  与数据块顺序，随文件路径与分配布局变化。
- 在**固定输出路径**下，同一冻结脚本 + 同一输入 + 同一 runtime 的重建产物**字节确定**。
- 无论容器字节如何，**语义载荷确定且可复现**（§3.3 全部字段一致）。
- 因此记录在案的 R1B SHA-256 应理解为**该已签发产物的身份标识**，
  其**内容**的可复现性依据是语义载荷比较，而非容器字节。

---

## 五、对 Stage5B / Stage6A 的影响

- **无功能影响**。R1B 冻结所依据的验证链（作者化权重场复算 float32 精确一致、
  冻结集零漂移、max influences ≤ 4、normalization PASS、zero-pose bind PASS、
  42/42 case、四指位移差 0.000e+00 mm）**全部与容器字节无关**。
- `TH_MCP_45 min_edge_residual` 的分类 `ACCEPTED_NON_BLOCKING_FOR_STAGE6A` 不受影响。

---

## 六、历史文件处理

```
stage5b_r1b/STAGE5B_R1B_STATUS.json           不回改（含原 blend_container_byte_reproducible 字段）
stage5b_r1b/STAGE5B_R1B_REPORT.md              不回改
stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend   已批准 master，未覆盖
```

后续任何引用 R1B 可重复性的文档，必须同时引用本勘误。
本勘误的完整机器可读证据：
`stage5b_r1b/_tmp/R1B_BLEND_REPRODUCIBILITY_CHECK.json`。

---

## 七、状态

```
BLEND_BUILD_REPRODUCIBILITY = REPRODUCIBLE_UNDER_FROZEN_BUILD_SCRIPT_AND_RUNTIME
                              （固定输出路径条件下；跨路径字节不保证）
ERROR_TAXONOMY              = CONTAINER_METADATA_ONLY，非数据错误
```
