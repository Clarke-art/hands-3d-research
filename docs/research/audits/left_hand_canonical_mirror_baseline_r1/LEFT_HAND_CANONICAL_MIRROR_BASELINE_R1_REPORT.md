# LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1

2026-10-07 · DESIGN_ONLY / HUMAN_REVIEW_PENDING · **READY_FOR_HUMAN_REVIEW**

唯一核心产品来源为已冻结 R2。左手候选已生成并重新打开验证，全部修改仅写入本审查目录。
机器 parity 与 Agent 对正常产品视角的可见检查通过；本报告没有代替 Human 批准，也没有更新任何 production pointer。

## Q1–Q11

| 问题 | 检查 | 回答 |
|---|---|---|
| Q1 | Canonical mirror plane / space 明确并验证 | YES |
| Q2 | 最终不存在 negative-scale runtime dependency | YES |
| Q3 | 3300 vertices / topology / UV / material mirror parity | YES |
| Q4 | 21-bone hierarchy / rest / semantic mapping parity | YES |
| Q5 | 完整 static weight field EXACT_SEMANTIC_MIRROR_MATCH | YES |
| Q6 | corrective / driver 正确镜像 | YES |
| Q7 | ZERO / RSSF 左手可见外观自然 | YES — Agent 观察；Human 待审 |
| Q8 | 六项批准姿态的镜像可见外观可接受 | YES — Agent 观察；Human 待审 |
| Q9 | 出现新的明显 bulge / flap / collapse / inside-out / thumb anomaly / first-web defect | NO — 未观察到 |
| Q10 | 右手 R2 / R1 保持原 SHA | YES |
| Q11 | 最终状态 | READY_FOR_HUMAN_REVIEW |

## 镜像平面与坐标

MIRROR_PLANE = WRIST rest-local X=0，即经过 WRIST head、由现有 WRIST rest-local Y（腕到掌/指纵向）与 Z（掌背向）张成的平面。

MIRROR_SPACE = ARMATURE_DATA；本资产 rig world matrix 为 identity。mesh 自身有旋转和平移，不能直接将 world X 作为左右轴。

平面原点（m）：`[1.3936593532562256, 0.04786719009280205, 0.36566734313964844]`。单位法线：`[-0.9800114035606384, -0.1434440314769745, 0.13784562051296234]`。
平面方程：`n · p = -1.322262672242`。
以腕坐标检查，THUMB_CMC / INDEX_MCP 位于桡侧，LITTLE_MCP 位于另一侧；法线与纵向、掌背轴正交。
这是从正式资产已有解剖框架确定的双侧构建平面。单只手本来不具备严格自对称，未声称 mesh 自身可完全对折重合。

反射矩阵为 S，mesh object matrix 为 T：mesh 与全部 shape key 坐标直接应用 `T^-1 S T`。
两对象保留正行列式和正 scale；构建过程没有使用负 object scale。面绕序翻转，UV corner 按原 face/vertex 身份恢复。

## 产品数据 parity

3300 vertices、3298 faces，vertex i ↔ vertex i。边连接、逆序后的面连接、UV 数值、原生 smooth/flat 与 sharp-edge flags、modifier 架构均验证通过。
R2 原有 material slot 数为 **0**，左手同为 0；证据图使用中性 studio 表面显示。没有新增材质、细分或修饰几何。
Official L1 身份沿 R2 继承；没有读取另一份 mesh 作为产品输入。

21 骨全部 *_R → *_L；16 deform + 5 non-deform TIP。保留 parent、connect、inherit、bone collection 与角色设置。
为保持 proper-handed rest frame，使用 `Rest_L = S Rest_R H`，其中 `H = diag(-1,1,1,1)`。
head/tail 按 S 反射；roll 使用反射后的 Z 轴对齐。local Y/Z 为反射方向，local X 额外反向以保持正行列式。
局部姿态使用 `Basis_L = H Basis_R H`，等价 quaternion `(w,x,y,z) → (w,x,-y,-z)`。
每骨 rest 与 parent-space 矩阵验证记录在 BONE_SEMANTIC_MIRROR_MAP_R1.json。

完整 3300×21 weight vectors **逐值完全相同**，差值为 0。源只有16个实际 deform groups，5个 TIP 语义列均为零，未增建或重算权重。
只改对应骨与 vertex-group 名称；没有 auto weights、harmonic solve、normalization、smoothing 或 repaint。

Basis 和现有 corrective geometry/delta 都按相同 vertex map 反射。corrective 名称中的 R1 是版本号，保留该名称并非保留右手骨语义。
现有 expression 保持不变；opp / mcp targets 改为 THUMB_CMC_L / THUMB_MCP_L。由于该 proper-frame 选择保持 local ROT_X 符号，expression 无需人为反号。
自然触发值在六项姿态中与右手匹配，没有新 sculpt 或 left-only corrective。

## 六项批准姿态

R2 批准集本身就是六项：ZERO/RSSF 是其中一项。未把 ZERO 另加一次，也未杜撰第七项。
回归定义只读取 R2 promotion 中的批准六项和其已使用的 opposition 轴；没有载入旧 R1 或旧工程 mesh 作为输入。
右 opposition 轴 `[-0.8687883019447327, -0.25, -0.42744219303131104]`；左等价轴 `[-0.8687883019447327, 0.25, 0.42744219303131104]`。
INDEX MCP 的 local-X -45°保持；THUMB MCP/IP 屈曲 local-X 符号保持。CMC 的混合轴按 H-conjugation 镜像。

| 姿态 | evaluated mirror 最大误差 mm | 右 corrective | 左 corrective | parity |
|---|---:|---:|---:|---|
| ZERO | 0.000722190 | 0.000000000 | 0.000000000 | PASS |
| INDEX_MCP_45 | 0.000725009 | 0.000000000 | 0.000000000 | PASS |
| CMC_OPP_30 | 0.000890151 | 1.000000000 | 1.000000000 | PASS |
| FULL_OPP_L1 | 0.000722190 | 0.000000000 | 0.000000000 | PASS |
| FULL_OPP_L2 | 0.000752569 | 0.973056197 | 0.973056555 | PASS |
| FULL_OPP_L3 | 0.000722190 | 1.000000000 | 1.000000000 | PASS |

最大 evaluated geometry 误差 **0.000890151 mm**。仅 float32 坐标/矩阵序列化与 Blender rest-axis 重建误差。
短 TIP 骨位于约 1.4 m 坐标偏移，端点相减会放大方向的浮点误差：端点仍为精确反射 float，最大 rest matrix 分量误差为 2.56001949e-05。
初始 3e-6 matrix 分量阈值因此触发过；只读核实端点后，验证界限记录为 rest 5e-5、parent/pose 1e-4，最终几何严格小于 0.003 mm。
没有为了通过验证修改骨骼或权重；候选文件自首次写出后未被重写。

每项 NaN/Inf、gross collapsed faces、degenerate edges 为 0；拓扑不变且几何与右手镜像匹配，无新增 tearing。六次 ZERO restore 误差均为 0。
Agent 检查六项 × 三视角，未观察到新增明显 penetration、flap、bulge、塌陷、inside-out、拇指方向或骨轴异常。
原生 L1 面感与右手一致，未以显示平滑掩盖。此为正常可见产品检查，不是 hidden-crossing / normal-dot / forensic 分析。

## Human 证据与后续边界

- [review.html](../../../../examples/historical/audits/left_hand_canonical_mirror_baseline_r1/review.html)：逐姿态、逐视角切换左右对照。
- [ZERO/RSSF](../../../artifacts/aac7d10653f58c1e5e2a.md)
- [六项掌侧/背侧](../../../artifacts/28426e6af27e062091b6.md)
- [六项 first-web](../../../artifacts/afe4b7d65e805b988f71.md)
- [左手候选](../../../artifacts/2d53c5ec96da8483bdef.md)

候选保留 mesh + skin + bones + corrective morph 标准结构，无 constraint、lattice、cage、自定义 deformation node 或负 scale 运行依赖。
现有 Blender driver 的 expression 以后仍需转译成 Web morph 权重；本轮验证其镜像 parity，没有声称 driver 可直接随 glTF 工作，也没有进行 Web 导出或实现。
未开始真实左手 motion、双手 motion、MIDI、fingering、钢琴安装或 promotion。

## 资产保护

LEFT_HAND_CANDIDATE_SHA256 = `c31190de326c5af44baf876f4066a130c8a9fef42d6c71c0071de5f63f0f2750`

RIGHT_R2_UNCHANGED = YES · `c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0`

RIGHT_R1_UNCHANGED = YES · `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`

WEIGHT_FIELD_MIRROR_PARITY = EXACT_SEMANTIC_MIRROR_MATCH

CORRECTIVE_MIRROR_PARITY = PASS

HUMAN_VISIBLE_RESULT = AGENT_VISIBLE_PASS / HUMAN_REVIEW_PENDING

FINAL_STATUS = READY_FOR_HUMAN_REVIEW

**STOP — HUMAN REVIEW。等待 Human 决策。**
