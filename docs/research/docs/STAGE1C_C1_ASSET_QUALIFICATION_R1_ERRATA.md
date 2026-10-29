# STAGE 1C · C-1 · ERRATA SIDECAR

> `docs/STAGE1C_C1_ASSET_QUALIFICATION_R1_ERRATA.md`
> 对象历史文档：`docs/STAGE1C_C1_ASSET_QUALIFICATION_R1.md`（**该历史文件保持原样，未做任何修改**）
> 关联证据：`production_spec/stage1c_c1_qualification/stats/GEOMETRY_ANATOMY_CHECK.md`（**同样保持原样，未做任何修改**）
> 日期：2026-09-28　状态：**`READY_FOR_HUMAN_REVIEW`**

---

## 0. 勘误标识

```
ERRATA_ID          = C1_Y_AXIS_ANATOMICAL_LABEL_REVERSAL
APPLIES_TO         = docs/STAGE1C_C1_ASSET_QUALIFICATION_R1.md
                     production_spec/stage1c_c1_qualification/stats/GEOMETRY_ANATOMY_CHECK.md
MODE               = SIDECAR_ONLY（历史文件 byte-unchanged，勘误不写入历史文件）
```

---

## 1. 原记录 vs 正式更正

| 轴 / 量 | 原记录（历史） | **正式更正（权威）** |
| --- | --- | --- |
| `DORSAL`（手背法向） | `+Y` | **`-Y`** |
| `PALMAR`（掌心法向） | `-Y` | **`+Y`** |
| `DISTAL`（手指方向） | `-Z` | `-Z` — **unchanged** |
| `RADIAL`（拇指侧） | `+X` | `+X` — **unchanged** |
| `HAND_CHIRALITY` | `RIGHT` | `RIGHT` — **unchanged** |

```
原记录：
    DORSAL = +Y
    PALMAR = -Y

正式更正：
    DORSAL = -Y
    PALMAR = +Y
    DISTAL = -Z    unchanged
    RADIAL = +X    unchanged
    HAND_CHIRALITY = RIGHT    unchanged
```

---

## 2. `SOURCE_TO_CANONICAL_TRANSFORM`（正式）

```
SOURCE_TO_CANONICAL_TRANSFORM =
    diag(1, -1, -1)  =  Rx(180°)

det   = +1      （proper rotation；无负缩放 / 无镜像 / 无反射）
scale = 1       （归一化后）
```

---

## 3. 权威依据

| 依据 | 路径 |
| --- | --- |
| R1.3.1 收口报告 | `docs/STAGE0_ROUTE_C_R1_3_1_FINAL_CLOSURE.md` |
| 数学审计正式结论 | `production_spec/stage0_r1_3_1_frame_audit/raw/ASSET_FRAME_COMPATIBILITY_AUDIT_RESULT.json` |
| 只读原始证据 | `production_spec/stage0_r1_3_1_frame_audit/raw/*.json` |
| 只读审计脚本 | `production_spec/stage0_r1_3_1_frame_audit/scripts/*.py` |
| 冻结后的帧定义 | `docs/CANONICAL_HAND_POSE_SPEC_R1.md` §1.2.1 |

---

## 4. 效力范围声明

```
THIS ERRATA DOES NOT MODIFY THE HISTORICAL C1 QUALIFICATION RESULT.

C1_ASSET_QUALIFICATION = UNCHANGED_CONDITIONAL_PASS
```

- 本勘误**只更正 Y 轴的解剖学命名标签**，以及由该标签派生的视角命名语义
  （`EVIDENCE_DORSAL_*`（相机 +Y）实为**掌侧**视图；`EVIDENCE_PALMAR_*`（相机 −Y）实为**背侧**视图；
  相机位置描述本身无误）。
- 本勘误**不改变**任何几何 / 拓扑 / 姿态 / 授权判定结论：
  `C1_GEOMETRY = PASS`、`C1_TOPOLOGY = CONDITIONAL_PASS`、`C1_FOREARM = PASS`、
  `C1_RSSF_REPOSE = MODERATE`、`C1_ASSET_QUALIFICATION = CONDITIONAL_PASS` 全部**不变**。
- 本勘误**不改变** `RIGHT_HAND` 结论（更正后 `(D × R) · DORSAL = +1` → 右手，与 C1 `G-12` 一致）。
- 本勘误**不改变** `ROUTE_C_SOURCE_GATE = PASS`，**不影响** Stage 2 可启动性。
- 历史证据 PNG / JSON / 统计输出 / Stage1A / Stage1B / Stage1C 原始报告**一律未修改**。

---

## 5. 历史不可变性

```
C1_HISTORY_IMMUTABLE = YES
```

- `docs/STAGE1C_C1_ASSET_QUALIFICATION_R1.md` —— **未修改**（含未追加任何更正框 / 更正标记 / 勘误章节）；
- `production_spec/stage1c_c1_qualification/stats/GEOMETRY_ANATOMY_CHECK.md` —— **未修改**（同上）；
- 勘误的**唯一载体** = 本 sidecar + `docs/STAGE0_ROUTE_C_R1_3_1_FINAL_CLOSURE.md`。

### 5.1 字节级校验记录（供后续审计复用）

| 文件 | 大小（bytes） | SHA-256（恢复后稳定值） | 与 R1.3.1 修改前目录清单一致？ |
| --- | --- | --- | --- |
| `docs/STAGE1C_C1_ASSET_QUALIFICATION_R1.md` | **30563** | `a04d5f9c1d9ba3bdd0c0efe11afc842059458fb76c4a2237a6b8dd9c7129fa7d` | ✅ 一致（30563） |
| `production_spec/stage1c_c1_qualification/stats/GEOMETRY_ANATOMY_CHECK.md` | **9208** | `6f23f0699c67f40a1ae2ad940f457cfb7e36936a21abca09f1ab7b426c525f63` | ✅ 一致（9208） |

**内容 = byte-exact 恢复**；两条 R1.3.1 更正标记计数均为 **0**。

> ⚠ **诚实记录（元数据层）**：恢复操作使这两个文件的 **mtime 变为 2026-09-28**。
> **文件内容与原状逐字节相同**；mtime 变化本身是"曾发生恢复操作"的诚实痕迹，**未回拨时间戳**（回拨时间戳会掩盖 provenance）。
> 恢复过程脚本：`production_spec/stage0_r1_3_1_frame_audit/scripts/restore_history.py`、`restore_history_fix.py`；
> 卫生扫描：`production_spec/stage0_r1_3_1_frame_audit/scripts/historical_provenance_hygiene_scan.py`。

**文档状态：`READY_FOR_HUMAN_REVIEW`**
