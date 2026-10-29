# STAGE5B R1B / STAGE6A R1A · PROVENANCE LEDGER

- **issued under**：`STAGE5B_R1B_STAGE6A_R1A_HUMAN_APPROVAL_FREEZE_R1`
- **issued at**：2026-09-30
- **verification**：所有哈希均由磁盘实测（`sha256sum`）并写入本文件；执行前后复核一致。
- **原则**：历史文件一律保留。禁止覆盖、删除、回改任何已签发产物。

---

## 一、完整 provenance 链（磁盘实测哈希）

| 阶段 | 文件 | SHA-256 | 角色 |
|---|---|---|---|
| Stage4 | `stage4_blender/stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend` | `fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7` | FROZEN（工程几何 master） |
| Stage5A R1 | `stage5_production_rig/stage5a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R1.blend` | `dd5f7265ea373579e9f77ecea2f74f0b2d0642a2bbb10795f1ddf5c17eb1486d` | 不可执行 / provenance |
| Stage5A R2 | `stage5_production_rig/stage5a_r2/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2.blend` | `615367d7fab3e75431fa7171e7e82f3a655c62e29ad7ddca5509b093e9f68c81` | provenance |
| **Stage5A R2A** | `stage5_production_rig/stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend` | `c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845` | **FROZEN_PROVENANCE（骨架/几何权威，继续冻结）** |
| Stage5B R1 | `stage5_production_rig/stage5b_r1/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend` | `8f4c6901fdae417e3855d388f9739ebea10863f0ebdbfedf0df8d79a751c308d` | SUPERSEDED（provenance） |
| Stage5B R1A | `stage5_production_rig/stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend` | `c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6` | **FROZEN_PROVENANCE / SUPERSEDED_BY_R1B_FOR_THUMB_WEIGHTING** |
| **Stage5B R1B** | `stage5_production_rig/stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend` | `cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10` | **FINAL_APPROVED / APPROVED_STAGE5B_STATIC_SKIN_MASTER** |
| Stage6A R1 harness | `stage6_deformation/stage6a/RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend` | `8f223c979362a8c3414b58e2467c7cda2da60f993245cc95b2a38d76c718d3ef` | FROZEN_PROVENANCE（历史 TEST HARNESS） |
| **Stage6A R1A harness** | `stage6_deformation/stage6a_r1a/RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend` | `c4bb74ea116e7352064c26977a509ed1248aacbe734118e5f9c240fa24b1157b` | **FINAL_APPROVED / APPROVED_STAGE6A_ISOLATED_FLEX_TEST_HARNESS（TEST HARNESS，非 Production Master）** |

---

## 二、当前唯一有效 master

```
PRODUCTION_MASTER_GEOMETRY  = Stage5A R2A  (c4fafc56…c2845)   UNCHANGED
PRODUCTION_RIG_SKELETON     = Stage5A R2A  (c4fafc56…c2845)   UNCHANGED
PRODUCTION_SKIN_WEIGHT      = Stage5B R1B  (cec5804f…117d10)  FINAL_APPROVED
STAGE6A_TEST_HARNESS        = Stage6A R1A  (c4bb74ea…1157b)   FINAL_APPROVED (test only)
```

21 production bone / 16 deform bone / 5 TIP helper（`use_deform=false`）在整个链上未变。

---

## 三、状态语义变更（本轮）

```
Stage5B R1A : FINAL_APPROVED -> SUPERSEDED_BY_R1B_FOR_THUMB_WEIGHTING
              （仅拇指权重的权威被 R1B 取代；文件与报告全部保留）
Stage5B R1B : CANDIDATE_FOR_HUMAN_REVIEW -> FINAL_APPROVED
Stage6A R1A : READY_FOR_HUMAN_REVIEW     -> FINAL_APPROVED
```

---

## 四、冻结收据索引

```
stage5b_freeze_r1b/STAGE5B_R1B_HUMAN_APPROVAL_FREEZE_R1.md
stage5b_freeze_r1b/STAGE5B_R1B_HUMAN_APPROVAL_FREEZE_R1.json
stage5b_freeze_r1b/STAGE5B_R1B_FREEZE_VERIFICATION_R1.json
stage5b_freeze_r1b/scripts/{s5b_r1b_freeze_verify.py, s5b_r1b_repro_check.py,
                            s5b_freeze_receipts.py}

stage6a_freeze_r1a/STAGE6A_R1A_HUMAN_APPROVAL_FREEZE_R1.md
stage6a_freeze_r1a/STAGE6A_R1A_HUMAN_APPROVAL_FREEZE_R1.json
stage6a_freeze_r1a/STAGE6A_R1A_FREEZE_VERIFICATION_R1.json
```

## 五、本轮新增勘误索引

```
stage5b_r1b/STAGE5B_R1B_BLEND_REPRODUCIBILITY_ERRATA.md
stage6a_r1a/STAGE6A_R1A_METRIC_COUNT_WORDING_ERRATA.md
stage6a_r1a/STAGE6A_R1_THICKNESS_PROXY_AUTHORITY_ERRATA.md       （上一轮，继续 binding）
stage6a_r1a/STAGE6A_R1_SELF_INTERSECTION_WORDING_ERRATA.md       （上一轮，继续 binding）
```

## 六、未改动声明

本轮未修改：Stage4 / Stage5A / Stage5B R1 / R1A / R1B / Stage6A R1 / R1A 任一 `.blend`；
未修改任何历史 `.json` / `.md` / `.py`；未创建 R1C；未开始 Stage6B。

```
STAGE6B = READY_TO_BEGIN        （禁止写 STARTED）
```
