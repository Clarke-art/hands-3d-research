# HUMAN_CAP_AUTHORITY_REVIEW_REPORT

执行：HUMAN_CAP_AUTHORITY_CORRECTION_R1。状态：**STOP — WAITING_FOR_HUMAN_CAP_AUTHORITY_REVIEW**。

只生成 Human 审阅材料。候选 **NATIVE_THUMB_DISTAL_CAP_CANDIDATE_R1** 仍为 PENDING_HUMAN_REVIEW，human_decision=null，未登记新的 membership authority。

## 输入与显示

独立候选原清单逐 ID 保持：48 vertices / 33 faces，seed v284；native THUMB-only induced graph；继承的 9 mm min-corner convention。与旧 cap9 无交集。旧 cap9：151, 158, 1061, 1074, 1076, 2189, 2192, 2569, 2577，已证明全部 INDEX_SURFACE，CURRENT_APPROVED_CAP_9=CONTAMINATED；本轮只作红色错误对照。

源候选 SHA256：`531fd2740ded03db59b5b740288c1fa1bd5c5e403bb865c00475b337be7f5ba3`。
native blend：`production_spec\stage4_blender\stage4a_r2\RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend`；SHA256：`4fa2cb6f31d8097110718e4d9cc424c30d1d2b7057c76abd93c338a5c7201039`。复用独立 audit 保存的 native world coordinates/topology，直接核对源 blend 哈希；没有重新保存 blend、求姿态或运行 Blender。nail mask 使用 Stage4C_R2 approved 12-face region：[64, 65, 68, 71, 1036, 1037, 1038, 1039, 1040, 1216, 1218, 1219]，映回不变 face IDs。IP `[1.4839419489321501, -0.01135163952636978, 0.44807723553284357]` 是继承的 native 工程估计；tip direction `[0.6254420158152934, -0.07962188330745959, 0.7761975525286561]` 为 IP→v284，不创建 joint/bone authority。

六个 PNG：DORSAL、PALMAR、RADIAL、ULNAR、THUMB_SIDE、THUMB_TIP_CLOSEUP，均只画 native/pre-RSSF；每图同时提供完整手上下文、thumb distal closeup、旧错误 cap9 食指局部，并显示候选绿色点/半透明面、红 cap9、橙 seed、紫 nail、IP、tip direction、candidate boundary。灰色表面作深度测试；全部彩色证据使用明确标注的 X-ray 投影，包括隐藏面，不能将隐藏投影当可见表面贴合。DORSAL=-Y、PALMAR=+Y、RADIAL=+X、ULNAR=-X；thumb side 和 tip axial basis 见 NATIVE_VIEW_METADATA.json。

## Geodesic expansion

**20 个候选点自身 geodesic ≤9 mm；28 个自身 >9 mm，由 min-corner face expansion 纳入。最大 15.894139 mm。48 点并非全部在 9 mm 内。**

计算仅用于这份候选的审阅 audit，不改变已存在 membership。测地距离使用 native world edge length mm 和独立 THUMB-only graph。tip distance 为 native 到 seed v284 的 Euclidean distance；vertex 和 face-corner geodesic 单独列出，未把 face centroid Euclidean distance 写成 surface geodesic。

| vertex ID | geodesic mm | tip Euclidean mm | nail | boundary |
| --- | ---: | ---: | --- | --- |
| 37 | 10.564231 | 7.452503 | True | True |
| 39 | 13.007251 | 11.437322 | False | True |
| 44 | 10.146097 | 7.429877 | False | True |
| 339 | 11.230029 | 8.373723 | False | True |
| 340 | 9.229549 | 8.822127 | False | True |
| 341 | 10.737414 | 7.582981 | False | True |
| 881 | 13.380550 | 9.603806 | True | True |
| 882 | 15.894139 | 11.951136 | True | True |
| 886 | 15.070941 | 11.681947 | False | True |
| 889 | 12.668048 | 9.446134 | False | True |
| 1339 | 12.221454 | 10.824092 | False | True |
| 1340 | 9.491394 | 7.528835 | False | True |
| 1342 | 11.622694 | 10.687649 | False | True |
| 1344 | 9.230463 | 7.522461 | False | True |
| 1378 | 12.113992 | 8.981770 | False | True |
| 1380 | 11.612442 | 8.802831 | False | True |
| 1450 | 9.494644 | 7.874057 | False | True |
| 1452 | 11.430130 | 9.136100 | False | True |
| 1453 | 14.550214 | 10.813822 | False | True |
| 1454 | 12.028306 | 8.239720 | False | True |
| 2496 | 11.750221 | 8.331070 | True | True |
| 2499 | 11.266322 | 8.388501 | False | True |
| 2740 | 13.177649 | 10.401411 | True | True |
| 2743 | 12.432023 | 10.128142 | False | True |
| 2785 | 13.276937 | 10.961913 | False | True |
| 2790 | 13.354509 | 11.160404 | False | True |
| 2965 | 9.425637 | 7.235391 | False | True |
| 2966 | 9.479503 | 7.034807 | False | True |

## Boundary audit

全部 48 vertex rows / 33 face rows 含原始 ID、geodesic、native branch、nail membership、tip distance、boundary membership。记录 selected-face boundary edges、外侧 native faces、geodesic shortest paths 和每个扩展点的 admitting face / ≤9 mm corner。边界：28 edges / 28 vertices / 16 boundary faces / 1 closed loop(s)；selected-edge incidence >2：0。闭环检查只说明候选拓扑，解剖边界是否合理留给 Human Q5。

## Human questions

Q1. v284 是否视觉上位于真实 native thumb terminal tip？
Q2. 48-vertex candidate 是否整体位于 thumb distal cap？
Q3. candidate 是否明显侵入 thumb middle/proximal surface？
Q4. candidate 是否遗漏明显 distal-cap surface？
Q5. 当前 33-face boundary 是否视觉合理？
Q6. 是否批准 NATIVE_THUMB_DISTAL_CAP_CANDIDATE_R1 作为新的 cap membership authority？

Q1–Q5：YES / NO / UNRESOLVED；Q6：APPROVE / APPROVE_WITH_BOUNDARY_REVIEW / REJECT / UNRESOLVED。页面不预选答案，不自动判定。浏览器只在 Human 操作后生成可下载答案；不会提交网络或更新 production authority。

## 冻结

1451 个既有 workspace 文件逐文件 SHA256 before==after（全部既有 production/docs/reference/旧审阅和审计文件，另含全部 BLEND）。新增材料只在本审阅目录。完整 before/after 见 FROZEN_HASH_VERIFICATION.json。

BLEND_FILES_WRITTEN=0；WEIGHT_DELTA=0；GEOMETRY_DELTA=0；TOPOLOGY_DELTA=0；BONE_DELTA=0；JOINT_DELTA=0。cap/R3 未修改；R3_runs=0；R1F_CREATED=false；Stage6_runs=0；strict_bound_recomputations=0；retopo=false。

**STOP。未自动应用新的 cap membership authority。**
