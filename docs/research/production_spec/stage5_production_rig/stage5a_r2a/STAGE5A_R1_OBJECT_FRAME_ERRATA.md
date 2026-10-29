# STAGE5A_R1_OBJECT_FRAME_ERRATA — R1

**Provenance finding 登记 + 正式关闭**

```
STAGE5A_R1_OBJECT_FRAME_OFFSET = CLOSED_BY_R2_SUPERSESSION
```

---

## 一、缺陷（fact）

Stage5A **R1** 把 **world-space 骨骼坐标**写进了 **armature local coordinates**，
而 rig object 同时又被放在 **ASSET object origin**
`[1.408704638, 0.022395039, 0.335847497]`。

结果：R1 blend 中实际 rig 相对手**整体偏移约 1448.359 mm**
（每个骨的 `r1_effective_world_delta_mm` ≈ 1448.359，见
`stage5a_r2/STAGE5A_R2_STATUS.json → gates.FROZEN_JOINT_DRIFT.per_joint.*.r1_effective_world_delta_mm`）。

这是 **OBJECT-FRAME 缺陷，不是关节位置变化**；没有任何冻结关节位置被改动。

## 二、R1 判定

```
R1 = FAIL_CLOSED  (provenance only)
R1 不得作为 executable production rig
R1 只保留 provenance
```

## 三、R1 文件（未修改）

```
stage5a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R1.blend
sha256 dd5f7265ea373579e9f77ecea2f74f0b2d0642a2bbb10795f1ddf5c17eb1486d
```

本轮执行前后该 hash **一致**（已复核）；文件未被覆盖、未被改写。

## 四、R2 的修复方式

R2 把骨骼按 **rig 自身 object frame**（= hand mesh 的 object frame）书写：

```
bone local = world − ASSET_ORIGIN
rig.location = ASSET_ORIGIN, rotation = (0,0,0), scale = (1,1,1)
```

因此 R2 的 armature 与 hand 几何重合。
独立复核（`stage5a_r2a/R2_OBJECT_FRAME_AUDIT.json`，只读、自行相乘 `matrix_world`）：

```
R2_OBJECT_FRAME = PASS
rig 与 mesh object frame 完全一致
六个关键骨 (WRIST_R / THUMB_CMC_R / THUMB_MCP_R / THUMB_IP_R / THUMB_TIP_R / INDEX_MCP_R)
  与 STAGE5A_R2_PRODUCTION_JOINT_TABLE.json 的 world_position 最大偏差 = 2.33e-07 mm
```

## 五、影响范围

| 冻结关节位置 | 是否受影响 |
| --- | --- |
| 全部 21 个 joint 的**世界坐标语义** | 否（R1/R2 的 world 值语义一致，只是存储帧不同） |
| R1 的 **可执行性** | 是 —— R1 不可执行 |
| 派生审计（ray parity / 内部性 / 链条几何） | R1 中全部失真，R2 中已重算 |

## 六、正式状态

```
STAGE5A_R1_OBJECT_FRAME_OFFSET = CLOSED_BY_R2_SUPERSESSION
R1 blend                       : 未修改、provenance retained
R1 可执行 production rig        : 否（永久）
唯一候选                       : STAGE5A_R2A（本轮）/ R2（上一轮）
```

本勘误只做登记与关闭，不改写任何历史文件。
