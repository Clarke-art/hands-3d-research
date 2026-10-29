# OFFICIAL_L1_FIRST_WEB_TARGETED_DEFORMATION_FIX_R1

**READY_FOR_HUMAN_VISUAL_APPROVAL — STOP — HUMAN REVIEW**

四个原失败动作中的上缘片状尖折已在普通实体图中消退到自然可接受程度。Codex 初步可见 blocker = 0；CMC30 / L3 仍保留窄的软组织 crease 与轻微低模分面，不能理解为无折痕。最终接受与否由 Human review 决定。

| 最终字段 | 结果 |
| --- | --- |
| BASIS_GEOMETRY_CHANGED | NO |
| BASIS_VERTEX_POSITION_WRITES | 0 |
| LOCAL_WEIGHT_TUNING_VERTEX_COUNT | 149 |
| WEIGHT_ITERATION_COUNT | 2 |
| CORRECTIVE_KEY_COUNT | 1 |
| ZERO_STATUS | PASS_VISUALLY_UNCHANGED_CODEX_PRELIMINARY |
| INDEX_MCP_45_STATUS | PASS_CODEX_PRELIMINARY |
| CMC_OPP_30_STATUS | PASS_CODEX_PRELIMINARY |
| FULL_OPP_L1_STATUS | PASS_NO_REGRESSION_CODEX_PRELIMINARY |
| FULL_OPP_L2_STATUS | PASS_CODEX_PRELIMINARY |
| FULL_OPP_L3_STATUS | PASS_CODEX_PRELIMINARY |
| FIRST_WEB_HARD_FOLD_REMAINING_CASE_COUNT | 0 |
| NEW_VISIBLE_DEFECT_COUNT | 0 |
| VISIBLE_PRODUCT_BLOCKER_COUNT | 0 |
| ZERO_RESTORE | PASS |
| MACHINE_SAFETY | PASS_MINIMUM_NUMERICAL_AND_GROSS_VISIBLE_SCREEN |
| PRODUCTION_PROMOTION | NO |
| VERDICT | READY_FOR_HUMAN_VISUAL_APPROVAL |

## 局部修复

从指定输入 SHA256 `9e8b29875fc6c215ef1e0fce4f582774f10b21596835d03763edb771443b11ec` 开始。两次针对性 weight iteration 都限定同一 149 顶点支持区，只重新分配 WRIST_R / THUMB_CMC_R / THUMB_MCP_R / INDEX_MCP_R 四个已有骨骼组，保留所有其它 influence 和四组总量。通过四个失败姿态实际位移的局部曲率残差做受约束最小二乘，原权重作为软约束，边界淡出；没有重复上一轮的 generic neighbor-weight smoothing。第二次降低原权重约束系数，支持区没有扩大。两次均直接检查六状态普通实体图。

INDEX_MCP_45 的硬台阶已由权重修正消除。opposition 仍有偏锐的 crease，故停止权重调整，添加且只添加一个 `FIRST_WEB_OPPOSITION_CREASE_R1` corrective，作用于上述支持区内 82 个顶点。以 CMC30 的局部 posed surface 作小幅圆滑，再通过已有线性蒙皮逆变换写入该 shape key 的 delta；最大 posed rounding 位移 0.554024 mm。没有写 Basis，没有添加骨骼、solver 或整手修改。

仅一个 driver、两个变量：已有 THUMB_CMC_R opposition 的 bone-local Euler X 与 THUMB_MCP_R flexion。低等级 opposition 与纯 INDEX flexion 不激活。表达式：

`max(min(1,max(0,(-opp-0.37)/0.06)),min(1,max(0,(-opp-0.15)/0.15))*min(1,max(0,(-mcp-0.175)/0.175)))`

本轮六个状态的 key value：ZERO = 0；INDEX_MCP_45 = 0；CMC_OPP_30 = 1；FULL_OPP_L1 = 0；FULL_OPP_L2 = 0.973056；FULL_OPP_L3 = 1。阈值采用弧度，复用原骨骼局部轴；没有增加控制骨或自定义属性网络。retarget 时需保留原骨骼动作语义，本轮不执行 retarget。

## 保留与最低检查

Basis / topology / UV / 材质 / 21 骨骼层级、joint head-tail 与 rest matrix / transforms / Armature modifier 全部逐项不变；区域外所有权重逐项不变，区域内其它 influence 不变。Basis shape key 与输入坐标逐项相同。ZERO 的 before/after 求值最大差 0.000134845732 mm，为权重重分配引入的浮点误差，实体图视觉一致；各姿态恢复本 candidate ZERO 的误差均为 0 mm。这两个比较的基准不同。

只复测 ZERO、INDEX_MCP_45、CMC_OPP_30、FULL_OPP_L1/L2/L3 共六状态。NaN/Inf、collapsed face、degenerate edge、gross severe stretch 均为 0；gross tearing / gross penetration 的普通实体图可见筛查为 0。没有进行 hidden crossing census、normal-dot、true-cap、R3 或完整 Stage6 矩阵。最低机器检查不替代人眼审查。

输入 candidate、Official donor、corrected rig 与 production weight donor 的 SHA256 均保持原记录。不覆盖 production asset。

## 交付

[review.html](../../../artifacts/08da8c4a37ad5061514a.md)：仅六个状态，每组 BEFORE / AFTER 普通掌侧 full view 与 first-web close；可展开背侧 full / grazing 辅助视图。48 张同机位原始实体图，所有原生面保留，无 cavity、无 cast shadow。评审选项均为空，不替人类选择。Human 结果可下载本地 JSON，绑定本 candidate SHA256。

DESIGN_ONLY candidate：[RIGHT_HAND_OFFICIAL_L1_FIRST_WEB_TUNED_DESIGN_ONLY_R1.blend](../../../artifacts/133fc296c8845dd7f7de.md)，保存姿态 ZERO，SHA256 `783a1b8fe414298cb442aa94d72161a3b2f3d5a95c39a341a6885e943e6dea1b`。

[保存重开与最低检查](../../../../examples/historical/audits/official_l1_first_web_targeted_deformation_fix_r1/PRESERVATION_AND_MINIMUM_SAFETY_R1.json)、[权重第1轮](../../../../examples/historical/audits/official_l1_first_web_targeted_deformation_fix_r1/WEIGHT_ITERATION_1.json)、[权重第2轮](../../../../examples/historical/audits/official_l1_first_web_targeted_deformation_fix_r1/WEIGHT_ITERATION_2.json)、[一个 corrective 与 driver](../../../../examples/historical/audits/official_l1_first_web_targeted_deformation_fix_r1/CORRECTIVE_KEY_R1.json)、[同机位渲染清单](../../../../examples/historical/audits/official_l1_first_web_targeted_deformation_fix_r1/MATCHED_RENDER_MANIFEST_R1.json)、[Codex 初步可见筛查](../../../../examples/historical/audits/official_l1_first_web_targeted_deformation_fix_r1/PRELIMINARY_VISIBLE_SCREEN_R1.json)、[输入与 production 保留](../../../../examples/historical/audits/official_l1_first_web_targeted_deformation_fix_r1/INPUT_AND_PRODUCTION_PROTECTION_R1.json)。

浏览器核对：48/48 原始实体图载入成功，六个 Human 选项均未预填，下载按钮在未完成评审时禁用。[页面核对记录](../../../../examples/historical/audits/official_l1_first_web_targeted_deformation_fix_r1/BROWSER_REVIEW_VERIFICATION_R1.json)。

[CMC30 同机位 before / after 与空白 Human review](../../../artifacts/45fae16adbacbcdc3571.md)

**PRODUCTION_PROMOTION = NO. STOP — HUMAN REVIEW.**
