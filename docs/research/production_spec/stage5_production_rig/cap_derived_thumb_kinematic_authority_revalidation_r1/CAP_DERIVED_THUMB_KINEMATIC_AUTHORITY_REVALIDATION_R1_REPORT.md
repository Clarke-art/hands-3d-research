# CAP_DERIVED_THUMB_KINEMATIC_AUTHORITY_REVALIDATION_R1

THUMB_KINEMATIC_AUTHORITY = **CORRECTION_REQUIRED_PENDING_HUMAN_REVIEW**。本轮仅建立 JSON 候选和可视证据，未应用。

## Authority 与执行边界

首先重新序列化冻结 authority payload 并实算 SHA256：`c81dd96d6925ed402cdf0ba44c148d7a78c2c60640fe23fb6247fb729f346cc8`，HUMAN_APPROVED_FROZEN，37 vertices / 25 faces。cap37 是 surface membership authority；它不是 bone endpoint rule。未运行 cap selector。OLD_CAP9 和旧 REP 仅作为污染 provenance 的审计对象，不能作为 anatomical authority。

以 frozen Stage4C_R2 原始 RSSF mesh 为几何输入（hash `fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7`）。native→RSSF→R2→R2A 的全量 ordered polygons 和 edge endpoint IDs 完全一致；RSSF→R2A 世界坐标逐值相同。没有读取 stale STAGE4B_R2_JOINT_FRAME.json 的数值来形成候选，也没有把当前冻结状态、旧 labels/weights、strict-bound 或 Stage6 当证明。

## 六个 slot 的裁决

| Slot | Verdict | Position Δ mm | Roll-coordinate Δ deg |
|---|---|---:|---:|
| THUMB_IP_R.head | REVALIDATED_UNCHANGED | 0.000000 | — |
| THUMB_IP_R.tail | CHANGE_REQUIRED | 12.027053 | — |
| THUMB_IP_R.roll | CHANGE_REQUIRED | — | 0.456707 |
| THUMB_TIP_R.head | CHANGE_REQUIRED | 12.027053 | — |
| THUMB_TIP_R.tail | CHANGE_REQUIRED | 15.635184 | — |
| THUMB_TIP_R.roll | CHANGE_REQUIRED | — | 0.456625 |

两个 bone 的 axis angular delta 最大 **13.933852°**；whole-frame rotation 另列 JSON。最大 position delta **15.635184 mm** 出现在 TIP tail。最大 Blender edit-roll coordinate delta **0.456707°**；平行运输后的 twist delta **1.964041°**，这是另一种 frame 对比量，不能混称相同 roll 指标。

## Provenance 与独立 IP 重验

IP head 从 Stage4B native axial locator 的 posed frame 经 R1/R2 H(IP) 继承；R2A build L245–260 没有写它。源码与 R2/R2A 实际骨数据逐项匹配，旧 REP 对 head 无直接或间接依赖。IP tail / TIP head 直接依赖 REP；TIP tail 直接用 REP 和历史 P 计算；两处 align_roll 通过纵轴间接依赖 REP。详细 current world/local 数值及行号见 `THUMB_IP_TIP_KINEMATIC_SLOT_PROVENANCE.json` 和带源码摘录/hash 的 `SOURCE_EVIDENCE_INDEX.json`。

独立重算沿用 approved axial method：native terminal/root identities 映射到 RSSF；当前 mesh edge 长度求几何路径，取 0.25–0.55 functional-length band 估计轴，root 投影作为 anchor，IP 在 axial fraction 0.75、±3 mm 截面内求中心。独立 native 分支身份重新核对；这不是 R2/R3 ownership 求解。true edge loops 使用原批准的 face-cyclic opposite-edge / valence-4 traversal 函数，遇 pole 停止；当前局部找到 4 条支持路径，其中 3 个闭合环和 1 条开口支撑弧，开口没有伪称闭合环。

当前 IP head `[1.450860857963562, 0.006127120926976204, 0.4640011489391327]` m；独立 section center `[1.4514000869932628, 0.005238577812200501, 0.4635959565639496]` m；差 **1.115553 mm**（轴向 0.584312 mm，横向 0.950283 mm）。±2–4 mm 带宽敏感性对应中心距当前点 **0.708066–2.004535 mm**；native 原 IP 截面顶点映射到 RSSF 后中心距当前点 **0.708066 mm**。当前 head 在 native thumb 截面内，surface clearance 6.220 mm，16/16 径向射线命中，左右半径不对称量不高于独立中心。环在轴向跨过该 head。

因此 IP head **REVALIDATED_UNCHANGED**，confidence **MEDIUM_HIGH_GEOMETRIC**。这不是“数值恰好等于重新求出的 centroid”；该方法提供有厚度的几何 joint section，无法从皮肤唯一观测内部骨关节的亚毫米中心。保留 current 的依据是独立截面、环和 native-mapped section 支持其位置，不是最小改动、冻结状态或减少 downstream drift。

## terminal landmark、候选与 rig 语义

native v284 = `[1.49774169921875, -0.013108416460454464, 0.46520325541496277]` m；同一 vertex identity 在 RSSF = `[1.4514825344085693, 0.010474493727087975, 0.48555445671081543]` m。映射是 baked nonrigid repose 后的同 ID 取值，不是直接复用 native XYZ，也没有假设全局刚性变换。

生产 contract 明确 TIP 是 non-deform fingertip helper：head 表示 terminal surface landmark，与 deform IP tail 共点；tail 是 `head + 0.30*(head-IP.head)` 的显示/方向延伸。IP tail 不是另一处 anatomical joint。故独立 v284 terminal evidence 与这个已存在的 surface endpoint convention 相容；它不是由 TIP 名称推断，也不是把 cap37 centroid 或 boundary center 硬套为骨点。v284 在 frozen cap37 内仅作 surface-envelope 交叉佐证。TIP tail 留在表面外是该 helper 规则的预期。

候选唯一采用映射后的 v284 terminal 与保留的已独立重验 IP head；本轮没有新的 endpoint selector 或“最接近 current”评分。候选中所有 6 项均有数值、confidence、evidence basis。surface tip 身份 confidence HIGH；它的 kinematic adoption 仍待 Human review。

## roll、静态 gates 与局限

独立 frame 先以重算 IP center→v284 为纵轴，再从批准 nail face normals 建 dorsal cue；palmar 取反，radial/ulnar 通过 native away-from-index 方向及 IP surface half-ring IDs 映射佐证。候选在 head 得到独立支持后使用 retained head→v284 轴。没有先拟合当前 R2A。+Y 为 distal，+Z 为 nail dorsal 的正交投影，+X=Y×Z；在本几何里 +X 对应 ulnar cue。

current roll 对它自己旧纵轴仍符合 nail projection rule，但该纵轴指向污染 endpoint，因此不能保持旧数字。重新计算的 frame determinant +1，dorsal projection norm 0.988285，无 axis degeneracy、roll ambiguity 或 180° flip；IP→TIP twist=0。MCP→IP 的平行运输 twist 见 roll JSON，MCP 只作 continuity check，不反过来决定 candidate dorsal。

当前 IP→旧 TIP 段 native-thumb oriented-surface static gate 为 **13/20 inside**，候选为 **20/20 inside**；current TIP head 离独立 terminal 12.027 mm，不能由新 terminal evidence 支持。current distal chain anatomically plausible = **NO**；候选 static plausible = **YES**。两条 helper extension 均在 skin 外，不把 non-deform helper 外露误报为 deform-bone 穿皮。没有 chain reversal 或 parent-child inversion；两处连接间隙 current/candidate 均为 0。

这些是 rest geometry 的局部静态 gates；最近 oriented thumb surface 的符号不冒充全局 volumetric proof，20 个采样也不冒充连续 chord 的严格证明。未执行动态 deformation、ownership 重算或 skin qualification。

## 下游输入预览

**R2/R3 input change expected = YES**，但必须区分实现：R2 默认 seed 由显式 cap vertex mean 决定，单改骨不自动更新其 seed/domain；旧 `ref AC` 也是单独输入。未来 cap/reference reconciliation 才会改变那条路径。R3 LIVE_CHAIN 直接读取 IP tail，候选必然改变 tube segment 输入，并影响 strong predicate 的 distance/arc；继而可能改变 dT、hard pins、mincut、closure。没有计算新 predicate 集合、dT、cut 或标签，具体边界变动保持未知。纯 roll 或单独 TIP helper tail 不直接改变静态 segment distance。

**Stage5B field change expected = YES**：R1 live BH/BT→segment distance→L0B radius→raw mu→weight vector 路径受 IP tail 影响。R1 的 POLY/XIJ/arc_of 却读取历史 jf，修改 blend 并不会自动修复该字段；R1A 有同类混合输入；R1D/R1E live arc 的末段则会改变。两个 impact JSON 给出 constructor / validator 的行号和依赖。没有生成新 weight vector，也没有重判 first-web、CMC cage、nail authority、R3 ownership 或 cap weight driver。

## Human gate 与冻结保护

`THUMB_KINEMATIC_HUMAN_REVIEW.html` 只展示 current vs proposed distal IP/TIP correction、6 slot 数值/差值和 8 张 PNG，不把整只 skeleton 重新提交。candidate 尚未写入任何 blend。unaffected hierarchy/origin 的独立来源和 R2/R2A 实值对比在 `UNAFFECTED_UPSTREAM_PROVENANCE.json`。

保护清单与最终 before/after SHA256 比对在 `FROZEN_HASHES_BEFORE.json`、`PROTECTED_STATE_VERIFICATION.json`。所有历史 Stage4C、Stage5A/B、R3、Stage6、canonical authority 与 Human responses 均保持不变。本轮所有实际 geometry/topology/bone/joint/weight delta 为 0；R2/R3/Stage6 runs 为 0。

## 最终逐项回答

1. THUMB_IP_R.head = REVALIDATED_UNCHANGED
2. THUMB_IP_R.tail = CHANGE_REQUIRED
3. THUMB_IP_R.roll = CHANGE_REQUIRED
4. THUMB_TIP_R.head = CHANGE_REQUIRED
5. THUMB_TIP_R.tail = CHANGE_REQUIRED
6. THUMB_TIP_R.roll = CHANGE_REQUIRED
7. current cap-derived REP authority = NO
8. independent thumb IP landmark confidence = MEDIUM_HIGH_GEOMETRIC; submillimeter osseous center not established
9. independent terminal tip landmark confidence = HIGH; frozen native v284 identity mapped exactly to RSSF
10. maximum position delta mm = 15.635183545981327
11. maximum axis delta deg = 13.933852284203642
12. maximum roll delta deg = 0.4567074290420726
13. current chain anatomically plausible = NO (local distal chain)
14. corrected candidate required = YES
15. Human review required = YES
16. R2/R3 input change expected = YES; direct R3 change, R2 default seed separately cap-driven
17. Stage5B field change expected = YES
18. unaffected hierarchy/origin preserved = YES
19. cap37 membership unchanged = YES
20. R3 run count = 0
21. Stage6 run count = 0
22. BLEND_FILES_WRITTEN = 0
23. NEXT = HUMAN_THUMB_KINEMATIC_AUTHORITY_CORRECTION
24. STOP = YES
