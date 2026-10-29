# RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1

**FINAL_CAUSAL_RESULT = STATIC_WEIGHT_FIELD_PROBLEM_SUPPORTED**  
**STATIC_WEIGHT_ROUTE = OPEN**  
**FROZEN_FALLBACK_UNCHANGED = YES**  
**STOP — HUMAN REVIEW**

唯一 DESIGN_ONLY full-vector harmonic candidate 在两指定视角中明显去除了 F130 的主阶梯深缺口；F127/F160/F205 一致改善，F110/F176 保持自然平滑。六帧未见新增明显 bulge / flap / hard shelf / volume collapse / palm distortion。因此本轮证据支持完整 static weight field 仍可解决该 blocker，不能将其归因于已证明不足的 deformation DOF。

可见判断来自 agent 对同相机截图的逐帧评估，**Human final decision = PENDING**。正式 blocker 尚未获得 Human closure，RIGHT_HAND_DEFORMATION_CLOSED=NO。候选不是生产权重解，未 promotion；本轮之后不自动继续权重设计。

## Q1–Q9

| # | 问题 | 回答 | 证据 / 边界 |
|---|---|---|---|
|Q1 | 完整 active-bone static weight-vector field 已重构？ | YES | 8 个 active 分量在全部 164 个内部点均改变；70 边界点完整向量固定。|
|Q2 | ACTIVE_WEIGHT_BONES_IN_ROI？ | WRIST_R, THUMB_CMC_R, THUMB_MCP_R, INDEX_MCP_R, INDEX_PIP_R, INDEX_DIP_R, MIDDLE_MCP_R, RING_MCP_R | 21 骨中 16 个 use_deform=true；ROI 仅 8 个实际非零，包含很小但真实的 MIDDLE/RING contribution。|
|Q3 | 完整向量梯度实质降低？ | YES | ROI mean −17.04% / max −24.32%；主带 mean −73.77% / max −73.25%。|
|Q4 | F130 主 blocker 明显改善？ | YES | 两视角原深阶梯缺口与尖锐折带明显消失，first-web 成为连续平滑过渡；达到自然很多的门槛。|
|Q5 | F127/F160/F205 一致明显改善？ | YES | 三帧原折口/凹折均明显消失，方向一致。|
|Q6 | F110/F176 保持自然平滑？ | YES | 两保护帧继续平滑；没有用破坏它们来换取 folded frames 的改善。|
|Q7 | 新增明显 bulge/flap/shelf/collapse？ | NO | 六帧×两视角未见新增上述明显缺陷或明显 palm distortion。|
|Q8 | 结果可归因于完整 static weight field？ | YES | 唯一变量为 ROI 内部完整权重向量；mesh/rest/21 bones/Action/constraints/corrective/driver/LBS 均通过一致性复核。|
|Q9 | 最终结论？ | STATIC_WEIGHT_FIELD_PROBLEM_SUPPORTED | 现有 deformation basis 在固定 sample 与六决策帧上具备解决主 blocker 的能力；等待 Human review，不 promotion。|

## 继承的权威与实验控制

读取最近两轮 report / JSON / audit 及两个 DESIGN_ONLY candidate（只读对象与 Action 元数据，未复做其试验）。继承 LEVEL_1_TOPOLOGY_ROUTE=CLOSED 和上一轮 Human 接受的 INSUFFICIENT_EVIDENCE，不重开 retopo/subdivide/edge-flow。旧 pair probe 仅覆盖完整梯度约 9–35%，其失败不代表全向量失败。

本轮直接从 frozen fallback 构建 ONE candidate：`audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_PROBE_R1.blend`，SHA256 `0f6b24fc8d74a0fe37fb4a142169633d525db3c2ea58a440005060c137cc374d`。沿用 PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1，11.5–18.5 sec，7 sec，421 observations，同六帧。固定帧相机逐字继承 topology causal probe 的 camera JSON；baseline 图直接复用上一轮已批准图，SHA 一致，未重新渲染历史 baseline。

## Q2：完整 21 骨向量组成

rig 总数 21；16 个骨骼 use_deform=true；5 个 TIP 为 non-deform，其向量分量严格零。读取所有现有 group，不预设 bone 名称。ROI 内实际非零 influence 共 8 个：

`ACTIVE_WEIGHT_BONES_IN_ROI = ['WRIST_R', 'THUMB_CMC_R', 'THUMB_MCP_R', 'INDEX_MCP_R', 'INDEX_PIP_R', 'INDEX_DIP_R', 'MIDDLE_MCP_R', 'RING_MCP_R']`

| Bone | ROI 非零顶点数 | ROI mean weight | ROI max weight |
|---|---:|---:|---:|
| WRIST_R | 222 | 0.59606748 | 1.00000000 |
| THUMB_CMC_R | 201 | 0.23371411 | 1.00000000 |
| THUMB_MCP_R | 176 | 0.01900601 | 0.13878439 |
| INDEX_MCP_R | 193 | 0.13775886 | 0.80396777 |
| INDEX_PIP_R | 70 | 0.00674704 | 0.12259352 |
| INDEX_DIP_R | 70 | 0.00643497 | 0.12240475 |
| MIDDLE_MCP_R | 15 | 0.00026885 | 0.02170279 |
| RING_MCP_R | 3 | 0.00000269 | 0.00031088 |

MIDDLE_MCP_R 与 RING_MCP_R 贡献很小但实际存在，因此保留参与，未做 support thresholding；ROI 完全无贡献的其余骨骼未加入。完整 baseline/candidate 21 分量逐点存于 FULL_VECTOR_FIELD_DEFINITION_R1.json。

上一轮 WRIST/THUMB pair 在继承 F130 主带 8 边上占完整 endpoint-vector L1 差的 **9.45%–35.18%**。其余主要 INDEX 项本轮参与同一求解，未再固定。pair 逐边占比仍附在梯度 JSON，未重复 sensitivity sweep。

## 唯一 candidate 的数学定义

沿用既有 ROI：234 节点 / 431 原网格边 / 70 原外边界 / 164 内部点，未扩大到整手。对全部 8 active 分量共同求解：

`L_II W_I = -L_IB W_B`；`c_uv = 1 / 原 Basis 世界系 rest-edge-length`。

正 conductance 的同一 mesh-edge graph Laplacian 对每个 bone 完全一致。boundary 每分量固定 baseline 值；没有 strength、iteration 参数、目标帧拟合、优化器、painting、support pruning 或第二 candidate。固定边界使每列唯一；非负边界配合离散 maximum principle 保持非负；所有列共用算子使常数 partition-of-unity 被保持。只对内部约 10⁻⁸ 的浮点 sum 误差做 numerical normalization。

- solve 最大 absolute residual = 4.55e-13；normalization 最大单分量改变量 = 1.35e-08。
- 最小 weight = 0；全网格 weight sum 范围 = [0.9999999404, 1.0000000596]。
- ROI 外与 boundary 全部数值逐分量完全一致；inactive 分量也完全一致，保存后重新打开复核通过。
- 8 个 active 分量每个均在 164/164 free 点改变，不是名义 full-vector、实际 pair。
- mesh coordinates / edges / faces / Basis / UV / native shading flags / 21 bones / rest matrices / constraints / drivers / original corrective / modifiers / Action 均一致；保持 LBS。
- 新 bone / helper / cage / corrective / DQS 均为零。既有 corrective 六帧自然值都为 0.0，未强制切换。

## Q3：干预验证（在渲染前完成；SECONDARY EVIDENCE）

完整 gradient = `Σ_b |w_b(v) − w_b(u)| / 原 rest-edge-length_mm`，单位 L1/mm。

| 区域 | mean before | mean after | median before | median after | max before | max after | mean 降幅 |
|---|---:|---:|---:|---:|---:|---:|---:|
| ROI overall | 0.03626607 | 0.03008728 | 0.02624033 | 0.02716930 | 0.16024949 | 0.12127637 | 17.04% |
| Human-visible 8-edge band | 0.13427408 | 0.03522320 | 0.13939412 | 0.03779743 | 0.16024949 | 0.04287099 | 73.77% |

主带 max 下降 73.25%；ROI max 下降 24.32%。weighted Dirichlet energy `1489.605960 → 1035.627891`，下降 30.48%。全部原边与预选主带沿用，未按结果重新挑选。

| Bone | ROI mean before → after | ROI max before → after | Band mean before → after | Band max before → after |
|---|---:|---:|---:|---:|
| WRIST_R | 0.01359767 → 0.01242427 | 0.06641448 → 0.06063819 | 0.01337487 → 0.01110189 | 0.02628767 → 0.01494575 |
| THUMB_CMC_R | 0.00952616 → 0.00990312 | 0.06434934 → 0.06063819 | 0.02496015 → 0.01689270 | 0.03415769 → 0.02085391 |
| THUMB_MCP_R | 0.00224846 → 0.00051352 | 0.03512940 → 0.00983533 | 0.00427170 → 0.00035522 | 0.01221712 → 0.00058158 |
| INDEX_MCP_R | 0.00778465 → 0.00677897 | 0.05135155 → 0.03805084 | 0.03676244 → 0.00672216 | 0.05135155 → 0.00892195 |
| INDEX_PIP_R | 0.00152876 → 0.00019176 | 0.03431292 → 0.00334137 | 0.02749996 → 0.00006802 | 0.03431292 → 0.00010564 |
| INDEX_DIP_R | 0.00149934 → 0.00016482 | 0.03426009 → 0.00331958 | 0.02740496 → 0.00005116 | 0.03426009 → 0.00009647 |
| MIDDLE_MCP_R | 0.00008024 → 0.00010941 | 0.00539325 → 0.00409781 | 0.00000000 → 0.00003172 | 0.00000000 → 0.00008588 |
| RING_MCP_R | 0.00000080 → 0.00000141 | 0.00007725 → 0.00005715 | 0.00000000 → 0.00000032 | 0.00000000 → 0.00000093 |

不声称每个指标或每个 bone 均下降：ROI median 略升，THUMB_CMC mean 上升 3.96%，微小 MIDDLE/RING 项因谐波传播会增加支持，但没有人为添加全无贡献骨骼。固定 boundary 仍保留原陡变；高应变主带的主要 INDEX 梯度已明显减少。这与上一轮只改 pair 的因果隔离缺口不同。

过程透明说明：构建脚本曾加入 Human 未要求的“ROI 与 band mean 都 ≥20%”软件 gate，输出 NO。**首次渲染前**检查真实数据后撤销这个额外 gate：ROI 17.04% / max 24.32%、主带 73.77%、所有 8 列实改与 energy 下降已经构成有效干预，并非 gradient 基本不变。原 log 和修正理由保留在 PRE_RENDER_MANIPULATION_ASSESSMENT_R1.json；没有改候选、边界、算子、weights 或参数。这一判断完全先于可见结果。

[完整向量梯度](../../../artifacts/0f55edf8bb0332c67731.md)

## Q4–Q7：Human-visible 主结果

同 camera / pose / frame / neutral Workbench lighting / material / smooth display shading。baseline LEFT，candidate RIGHT；未经 pixel difference、strain 或 distance 分数代替视觉判据。

| 帧 | 匹配两视角的可见结果 |
|---|---|
| F110 | 两视角保持自然平滑。原斜向凹线趋于平顺，未见新增明显 bulge/flap/shelf 或掌面塌陷。 |
| F127 | 两视角原 first-web 阶梯状折口明显消失，连续过渡更自然；改善方向与 F130 一致。 |
| F130 | 两视角原深阶梯缺口与尖锐折带明显消失，first-web 成为连续平滑过渡；达到自然很多的门槛。 |
| F160 | 原斜向深凹折带明显消失；两视角均呈平滑过渡。 |
| F176 | 恢复帧两视角保持平滑，无新增明显 flap/硬台阶或体积塌陷。 |
| F205 | 原对角折口与锯齿深折明显消失；两视角一致改善，拇指根部仍自然连接。 |

[F130 对照](../../../artifacts/ac3fc70c382561d790f2.md)

[六帧对照](../../../artifacts/495b2bc2cc9cc4f61696.md)

候选可以看到 first-web 原来被拉开的阶梯深折被连续曲面替代，既不只是锯齿减少，也不只是浅一点。静态 rest shape 完全不变；运动中表面变化源于完整 weights。无新明显 palm distortion。此处只评估六帧×两视角可见表面，不宣称完整 motion 的所有角度已获得生产质量认可。

## 次级位移与最低保护

F130 对应 ROI 点最大位移 24.515 mm，候选局部 max edge-length ratio=1.765；仅作干预确实影响曲面的佐证，不作为 PASS 条件。六帧完整数值位于 PROBE_MEASUREMENTS_R1.json。421 observations 检查包含最后端点 F211：`i=0..420 → source 690+i → frame 1+i//2, subframe=(i%2)/2`。没有改 sample 或 retarget。

NaN/Inf=0、gross collapsed faces=0、degenerate edges=0，ZERO restore=0.000000 mm。candidate 与 baseline 的 ZERO 求值浮点差最大 0.000136778 mm；原生坐标逐项一致。连接拓扑不变，六决策帧未见明显新增 tearing/penetration。未运行 hidden crossing census、normal-dot、R3、true-cap、2127-edge 或逐顶点 anatomy forensic；不将普通视图判断冒充 exhaustive collision proof。

## 资产保护与停止

Frozen fallback SHA256 轮前轮后均为 `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`，**FROZEN_FALLBACK_UNCHANGED=YES**。所有前两轮 durable audit / report / JSON / candidate / raster 和 protected source/sample/pointer 哈希结束一致。仅本轮 audit 内一份 .blend；未移动 production pointer、未 promotion、未正式 weight rebuild、未开始左手或 Web export。

**STATIC_WEIGHT_ROUTE = OPEN**。本轮证明 existing static field 具有解决当前六帧主 blocker 的能力；production-quality weight solution 的设计需下一轮 Human 决策。`DEFORMATION_DOF_LIMIT_SUPPORTED` 本轮不成立，不自动进入新 bone / helper / cage / PSD / RBF / muscle / new rig。

交付：本报告、review.html、唯一 DESIGN_ONLY .blend、三张指定 EVIDENCE PNG、FULL_VECTOR_FIELD_DEFINITION_R1.json、FULL_VECTOR_GRADIENT_R1.json、PROBE_MEASUREMENTS_R1.json、FINAL_ASSET_PROTECTION_R1.json，以及小量可复现脚本和判读记录。

**STOP — HUMAN REVIEW。等待 Human 决策。**
