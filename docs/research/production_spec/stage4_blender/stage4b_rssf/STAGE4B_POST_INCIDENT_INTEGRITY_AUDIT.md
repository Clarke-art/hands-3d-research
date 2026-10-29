# STAGE4B_POST_INCIDENT_INTEGRITY_AUDIT

**任务**：`STAGE4B_POST_INCIDENT_INTEGRITY_AUDIT`（极窄只读完整性审计）
**工作区**：`<HANDS_ROOT>`
**运行时**：`D:\Blender\blender.exe`（Blender 5.1.2）
**性质**：**纯只读**。未改模型、拓扑、RSSF pose、temp rig、weights；**未删除、未移动任何文件**（唯一被修改的文件是 `scripts/stage4b_render.py`，只改输出路径规则，渲染本身未动）。

---

## 0. 结论

```
P0_DELETE_INCIDENT        = CLOSED
FORMAL_RENDER_REBUILD     = PIXEL_EXACT
CURRENT_DELIVERABLE_SET   = COMPLETE
TEMP_OUTPUT_ISOLATION     = PATCHED
GLOB_DELETE_POLICY        = PROHIBITED
STAGE4B_ARTIFACT_INTEGRITY = PASS
```

---

## 1. 冻结输入确认（§二）

| 项 | 值 |
| --- | --- |
| `RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend` sha256 | `4fa2cb6f31d8097110718e4d9cc424c30d1d2b7057c76abd93c338a5c7201039` |
| 期望值 | `4fa2cb6f31d8097110718e4d9cc424c30d1d2b7057c76abd93c338a5c7201039` |
| **MATCH** | **TRUE** |
| 本次审计是否触碰 | 否（仅读取） |

**`RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R1.blend` 当前哈希**：

| 项 | 值 |
| --- | --- |
| 路径 | `production_spec/stage4_blender/stage4b_rssf/RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R1.blend` |
| bytes | 1,988,085 |
| sha256 | `d590660c305363981ba776b41a32e642a201093edb90fbe6a1a6a1572086c35d` |
| 本次审计是否触碰 | 否（仅读取） |

同时交叉核对 `TOPOLOGY_FREEZE_AUDIT.json`：`TOPOLOGY_SIGNATURE_MATCH = true`，`PRE = POST = 5a39668418eea171…`。

---

## 2. 重建事故涉及的 4 张正式图（§三）

**scratch 目录**：`stage4b_rssf/_tmp/post_incident_rebuild/`
**未覆盖 `renders/`**（其哈希快照见 §5）。

重建输入：冻结基线 blend（BEFORE 侧）+ `…STAGE4B_RSSF_R1.blend`（AFTER 侧）+ `scripts/stage4b_render.py` + `scripts/stage4a_r2_composite.py` + `stage4b_rssf/CAMS.json`。相机规格逐字复用，BEFORE / AFTER 同相机、同尺度、同 framing。

产出：4 张 `RSSF_BEFORE_AFTER_*.png`，并额外重建了同样在事故范围内的 `RSSF_CMC_CLOSEUP.png`，以及 10 张单侧帧（供逐像素比对用）。

---

## 3. 逐图比对（§四）

比对器：`scripts/stage4b_post_incident_compare.py`。两侧都用**同一个解码器**（Blender + numpy）解码，`colorspace = Non-Color` 以避免任何色彩变换；维度另从 PNG `IHDR` 直接读出，不依赖解码器。

### 3.1 正式对比图 —— 文件字节完全相同

| 图 | 尺寸（IHDR / 解码） | bytes | sha256（重建 = 现装） | 逐像素差异 | 判定 |
| --- | --- | --- | --- | --- | --- |
| `RSSF_BEFORE_AFTER_DORSAL.png` | 2414×1000 / 2414×1000×4 | 1,289,863 | `be71f049db79a7e054ee07e24b93647bce130bd14346b00b1ec65100359980e9` | **0** | **PIXEL_EXACT** |
| `RSSF_BEFORE_AFTER_PALMAR.png` | 2414×1000 / 2414×1000×4 | 1,296,250 | `52f370dda81faeeb329513c9959b39289bb24bbd762a6d8534a1005e7ae3450c` | **0** | **PIXEL_EXACT** |
| `RSSF_BEFORE_AFTER_RADIAL.png` | 2414×1000 / 2414×1000×4 | 1,118,271 | `f491431a5a4b6802edf64bdbf8bf3cde3a89361bc8424b1df2df865a1cb02b8b` | **0** | **PIXEL_EXACT** |
| `RSSF_BEFORE_AFTER_OBLIQUE.png` | 2414×1000 / 2414×1000×4 | 1,261,173 | `7c543171eae38be912c72ee52c0ae8cbdd7478e26f90731e5a16dc9aae7a5192` | **0** | **PIXEL_EXACT** |
| `RSSF_CMC_CLOSEUP.png` | 2414×1000 / 2414×1000×4 | 1,727,353 | `664b4676f6c2f05bbed809de7c823530e98590f645c2cdf591de39907ff6ea1a` | **0** | **PIXEL_EXACT** |

`file_bytes_identical = true`，`max_abs_channel_difference = 0`，差异像素数 = 0。**这 5 张图不是"看起来一样"，而是逐字节同一文件。**

### 3.2 10 张单侧帧 —— 文件哈希不同，但**像素完全相同**

| 图 | 尺寸 | bytes（两侧相同） | 逐像素差异 | max 通道差 | 判定 |
| --- | --- | --- | --- | --- | --- |
| `RSSF_BEF_{DORSAL,PALMAR,RADIAL,OBLIQUE,CMC}.png` | 1200×1000 | 654797 / 653013 / 553776 / 637472 / 858709 | **0** | 0 | **PIXEL_EXACT** |
| `RSSF_AFT_{DORSAL,PALMAR,RADIAL,OBLIQUE,CMC}.png` | 1200×1000 | 609898 / 616494 / 534540 / 589833 / 849967 | **0** | 0 | **PIXEL_EXACT** |

**哈希差异的原因已定位，不是"解释成正常"，而是逐 chunk 证明**（探针 `RSSF_BEF_DORSAL.png`）：

| chunk | 重建 | 现装 |
| --- | --- | --- |
| `tEXt` | `Date\x002026/09/28 22:15:09` | `Date\x002026/09/28 21:53:59` |
| `tEXt` | `RenderTime\x0000:00.57` | `RenderTime\x0000:00.59` |

- chunk 类型与顺序两侧完全一致；
- **`IDAT`（真正的像素负载）压缩态逐字节相同，解压后亦逐字节相同**；
- 差异仅限渲染管线写入的 PNG `tEXt` 元数据（墙钟时间与渲染耗时）。

同时这也证明渲染流水线是**确定性**的：两个不同时刻、各自独立运行，得到完全相同的像素负载。

---

## 4. 其余正式交付物只读确认（§五）

`MISSING_COUNT = 0`。

| 交付物 | bytes | sha256 |
| --- | --- | --- |
| `RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R1.blend` | 1,988,085 | `d590660c305363981ba776b41a32e642a201093edb90fbe6a1a6a1572086c35d` |
| `STAGE4B_RSSF_REPOSE_REPORT_R1.md` | 12,907 | `89a7addc83d8e2c66250a16c799cd0f8df8cb06f2d0251bdf40a11f34997cf94` |
| `RSSF_POSE_AUDIT.json` | 4,252 | `7ffdcbe6b01b1804ef45eb639db4034c1a1b4783317fd1c71572de702f178c75` |
| `TEMP_RIG_AUDIT.json` | 8,691 | `c0a3008bbcf27a6c82b211f6fcae661a7ced2adad861660a764968a474d570f1` |
| `TOPOLOGY_FREEZE_AUDIT.json` | 837 | `96e131196b97cb3e2c9727dd4226c5a851da06b5ab61b09aaee2089944919cd4` |
| `TEMP_WEIGHT_AUDIT.json` | 1,986 | `99ca38c326825e6a257de83d95381b0dbb38008edd8e4b7416e626ef96e4a703` |
| `RSSF_DEFORM_CHECK.json` | 2,533 | `302f84965791e41de61ba2f58ad0f407092d5fce031ce83673538e47ed762753` |
| `RSSF_RUN.json` | 14,256 | `8c7a3fe3f9733e1cf7bdcfb9f1e6b04debb7c91bc326d883f6bfb5aafc42fdd6` |
| `CAMS.json` | 728 | `24785e2f10cf907f9484a1637fa7aea567a2ab140ed13168a87ca9d85940d17a` |
| `RSSF_CMC_CLOSEUP.png` | 1,727,353 | `664b4676f6c2f05bbed809de7c823530e98590f645c2cdf591de39907ff6ea1a` |
| `RSSF_SKELETON_OVERLAY.png` | 632,300 | `ffd76b6964588d99061ebc71a59cf2e00c3a57b0086dd7f7d0ae4845f6a2180a` |
| `RSSF_BEFORE_AFTER_DORSAL.png` | 1,289,863 | `be71f049db79a7e054ee07e24b93647bce130bd14346b00b1ec65100359980e9` |
| `RSSF_BEFORE_AFTER_PALMAR.png` | 1,296,250 | `52f370dda81faeeb329513c9959b39289bb24bbd762a6d8534a1005e7ae3450c` |
| `RSSF_BEFORE_AFTER_RADIAL.png` | 1,118,271 | `f491431a5a4b6802edf64bdbf8bf3cde3a89361bc8424b1df2df865a1cb02b8b` |
| `RSSF_BEFORE_AFTER_OBLIQUE.png` | 1,261,173 | `7c543171eae38be912c72ee52c0ae8cbdd7478e26f90731e5a16dc9aae7a5192` |

### `renders/` 未被本次审计改动

审计开始时对 `renders/` 全部 16 个文件做了哈希快照，审计结束后重新计算：

- 文件数 before / after：16 / 16
- **逐字节相同：TRUE**（`changed_files = []`）

即：本轮**只往 `_tmp/` 写**，`renders/` 一个字节都没变。

---

## 5. 渲染输出规则修复（§六）

只修改了 `scripts/stage4b_render.py`（sha256 `02347b516dbcee9139bb7c480a553da75b51bc8f8e7475f3406e14fb0521bca8`）。**渲染逻辑、相机、分辨率、AA、配光一律未动**，只改输出路径规则。

```
TEMP_RENDER_OUTPUT_DIR  = stage4b_rssf/_tmp/
    单侧帧                : _tmp/RSSF_BEF_*.png , _tmp/RSSF_AFT_*.png
    临时 overlay / probe  : _tmp/

FINAL_RENDER_OUTPUT_DIR = stage4b_rssf/renders/
    只允许: RSSF_BEFORE_AFTER_{DORSAL,PALMAR,RADIAL,OBLIQUE}.png
            RSSF_CMC_CLOSEUP.png
            RSSF_SKELETON_OVERLAY.png
```

### 关键设计：**白名单**，不是前缀规则

事故的根因是前缀判定 `RSSF_BEFORE_*` 同时命中交付物 `RSSF_BEFORE_AFTER_*` —— **任何前缀规则都无法区分这两个名字**。因此改为**按目标目录做精确文件名白名单**：不在白名单内的名字一律硬拒，并在报错里点名事故本身。

同时加入：

- 单侧帧**只**写 TEMP，永不写 FINAL；
- `TEMP == FINAL` → 硬拒；
- `TEMP` 的目录名是 `renders` → 硬拒；
- 脚本**不含任何删除动作**（无 unlink、无 glob 删除、无递归删除、无前缀通配删除）。

### 负向测试（实测）

| 用例 | 结果 |
| --- | --- |
| `TEMP == FINAL == renders/` | **REFUSED** — `temp_dir == final_dir` |
| 往 `renders/` 写 `RSSF_BEF_DORSAL.png` | **REFUSED** — `prefix 'RSSF_BEF_'` |
| 往 `renders/` 写 `RSSF_AFT_DORSAL.png` | **REFUSED** — `prefix 'RSSF_AFT_'` |
| 往 `renders/` 写 `RSSF_BEFORE_DORSAL.png` | **REFUSED** — `prefix 'RSSF_BEFORE_'` |
| 往 `renders/` 写 `RSSF_AFTER_DORSAL.png` | **REFUSED** — `prefix 'RSSF_AFTER_'` |

（测试方式：把脚本中**实际发布的**护栏代码原样抽出执行，不是另写一份模拟逻辑。`RSSF_CMC_CLOSEUP.png` / `RSSF_BEFORE_AFTER_DORSAL.png` / `RSSF_SKELETON_OVERLAY.png` 三个交付名正确放行。）

### 正向复现（修补后完整走一遍）

`stage4b_rssf/_tmp/post_patch_check/`：FINAL 目录**只收到 5 个交付物**，TEMP 目录收到 10 张单侧帧；与 `renders/` 比对 **15/15 PIXEL_EXACT**，其中 5 张正式图 **`file_bytes_identical = true`**。

即：修补没有改变任何一个输出像素，只是改变了它们落盘的位置。

---

## 6. LEGACY_TEMP_LOCATION（§七）

`renders/` 中现存 10 个单侧帧先**保留原位**：

```
状态    : KEEP_IN_PLACE_UNTIL_HUMAN_REVIEW
目录    : production_spec/stage4_blender/stage4b_rssf/renders/
数量    : 10
文件    : RSSF_BEF_{DORSAL,PALMAR,RADIAL,OBLIQUE,CMC}.png
          RSSF_AFT_{DORSAL,PALMAR,RADIAL,OBLIQUE,CMC}.png
```

**只标记，未移动、未删除。** 标记落在三处：本报告、`STAGE4B_POST_INCIDENT_INTEGRITY_AUDIT.json` 的 `legacy_temp_location`、以及 `_tmp/LEGACY_TEMP_LOCATION.json`。它们不是交付物；Human Review 后再决定是否移入 `_tmp/`。

---

## 7. 本轮新增 / 修改的文件

**新增（全部在 `_tmp/` 或审计产物位置）**

```
stage4b_rssf/STAGE4B_POST_INCIDENT_INTEGRITY_AUDIT.md       (本报告)
stage4b_rssf/STAGE4B_POST_INCIDENT_INTEGRITY_AUDIT.json     (机读)
stage4b_rssf/_tmp/LEGACY_TEMP_LOCATION.json
stage4b_rssf/_tmp/renders_pre_state.json
stage4b_rssf/_tmp/deliverable_inventory.json
stage4b_rssf/_tmp/compare_pairs.json / compare_result.json
stage4b_rssf/_tmp/compare_pairs_post_patch.json / compare_result_post_patch.json
stage4b_rssf/_tmp/post_incident_rebuild/     (15 张重建图)
stage4b_rssf/_tmp/post_patch_check/          (15 张修补后脚本产出)
scripts/stage4b_post_incident_compare.py
scripts/stage4b_post_incident_audit_json.py
```

**修改（1 个，只改输出路径规则）**

```
scripts/stage4b_render.py    sha256 02347b516dbcee9139bb7c480a553da75b51bc8f8e7475f3406e14fb0521bca8
```

**未删除、未移动：任何文件。**

---

## 8. 状态（§八）

```
P0_DELETE_INCIDENT         = CLOSED
FORMAL_RENDER_REBUILD      = PIXEL_EXACT
CURRENT_DELIVERABLE_SET    = COMPLETE
TEMP_OUTPUT_ISOLATION      = PATCHED
GLOB_DELETE_POLICY         = PROHIBITED
STAGE4B_ARTIFACT_INTEGRITY = PASS
```

**已停止。未进入 Stage4C。等待 Human Review。**
