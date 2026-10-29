R4 几何设计已按 FAIL_CLOSED_R4_GEOMETRY_DESIGN 停止，Human 合格候选为 0，推荐写入顶点为 0。所有几何变动仅存于本目录独立诊断数组与临时场景；生产未 APPLY、未保存任何 blend。

主因：A_NONLINEAR_SOLVER_NONCONVERGENCE。本策略没有收敛到自然浅而连续的 dorsal MCP valley。末轮满步的既有 component 总长度连续证书未解决；缩短试步新增了 source component / fan membership，全部拒绝。分别记录 F_NUMERICAL_CCD_UNRESOLVED 和局部 C_BASELINE_CONTACT_COMPONENT_CONFLICT，不将某一方向失败推成全局约束冲突。E_TARGET_CONTOUR_CONFLICT 表示该诊断终点仍未达目标，而非证明目标在整个位置空间不可行。

POSITION_ONLY_ROUTE = OPEN_NOT_QUALIFIED。TOPOLOGY_EVIDENCE = NOT_FOUND。TOPOLOGY_CHANGE_REQUIRED = NOT_PROVED。RET0PO = NO。停止等待 Human 审阅，不自动改拓扑或换轨。

| 项目 | 结果 |
|---|---|
| Solver formulation | COUPLED_NONLINEAR_TRUST_REGION_FEATURE_AWARE_CONSTRAINED_DESCENT |
| Support | S4，111 顶点，333 world XYZ 自由度 |
| Normal / tangents | 法向与两个切向共同求解；同一个位移、梯度、弯曲度量 |
| Feature re-identification | 每个 nonlinear iteration 更新有限端点、closest simplex、source feature / component 范围 |
| Continuous certification | 43 / 43 接受步均完整认证，坐标 SHA 链核对通过；没有五采样安全推断 |
| Negative controls | 16 / 16 PASS，与冻结对照名称一致 |
| Qualified Human candidates | 0；R4-A 未创建，R4-B 不进入，R4-C 不允许 |
| Candidate actual writes / max / mean / RMS / P95 | 0 / N/A / N/A / N/A / N/A |
| Candidate visual / boundary / four smoke | N/A；没有完整候选 |
| Recommended candidate / write count | NONE / 0 |
| Production drift | 0 |

目标函数共同包含基于冻结周围表面的相对 dent 修正、6676 和 core 原生法向 progression、同手健康 reference 和周围 continuation、位置位移、一阶梯度、二阶弯曲、外环 falloff 和边界 progression。健康参考的 normal progression 95 分位为 35.963353°，hinge soft goal 为 50.963353°，仅是形状先验，不是 anatomy threshold。没有复制绝对深度、宽度、曲率，也没有 normal-only、分轴独立或通用 fairing 替代。

各位置试步以真实有限 simplex 接触语义检查。共同 native edge / vertex / internal fan diagonal 合法零距；边外越界、正面积共面重叠、新非邻接交点、路径 fan rank 丢失均拒绝。source 真实接触本身不是目标或自动 FAIL；实际 component 的 fan membership、端点 feature、直径、总交段长度、共面面积不得新增或增大。最终没有固定 barycentric / world-point 等式；早期等式试探只作为代数诊断保留，绝非不可行证明。所有计算容差声明为 COMPUTATIONAL_GEOMETRY_TOLERANCE，不是 anatomy clearance。

连续步证书以输入 binary64 的精确有理数表示构造移动 volume、旋转分离平面、有限三角形 / 共同顶点 cone separation、完整 oriented matroid signs、persistent coplanar rank-3 charts，以及实际 edge-plane 交点的有理函数。Bernstein 符号与递归细分覆盖整段参数区间。共同边 rotating volume 和 opposite-ray certificate 区分合法共享 simplex 与边外重叠。source contact 端点 feature 用精确 barycentric 多项式保持；component diameter 和 total curve length 用有理平方不等式 / Bernstein bound 连续限制，允许内部 fan 长度重新分配。任何不能认证的区间均拒绝。原生 vertex cycle 和连续 material simplex frame 固定，world-normal hemisphere 只是图表诊断，不能独自判定真实反转；数值 swept area minima 仅作补充。

S4 为主支持。S3 仅提供包含关系与范围证据；S5 仅用于周围 / 边界审阅，没有出现必须扩展 S4 的 boundary conflict。没有自动 S5 优化或构建 S6。search pool 不等于写入 authority。

下表是未合格求解终点，不能作为候选或写入清单。其普通实体图片仍保留深凹与尖折，视觉 FAIL_TARGET_CONTOUR，不标 PASS_PENDING_HUMAN。

| 诊断指标 | 当前基线 | 未达标终点 |
|---|---:|---:|
| Fixed surrounding depth mm | 1.546239168 | 1.401673383 |
| 6676 angle ° | 178.227633924 | 168.902047144 |
| 6675 angle ° | 27.929196939 | 26.167871693 |
| 6602 angle ° | 25.668912224 | 26.292593037 |

未合格诊断实际非零位移 111 顶点；max 0.347393528 mm，mean 0.024565426 mm，RMS 0.059682287 mm，P95 0.133410107 mm，boundary displacement gradient max 0.004961386。逐顶点 before / after / delta 和法切分量在 R4_UNQUALIFIED_DIAGNOSTIC_WRITE_SET.json，明确不可选、不可 APPLY。

终点及所有接受步的 source 固定 chart 检查没有新增投影 flags，2771 / 3332 / 3351 三个已有 flags 不要求绝对清零，无显著 projection-overlap 增长。它们的原生 fan 非零面积、对边实际 3D gap 和内部 fan exact contact 分别记录。3351 的独立旧真实 contacts 2784/3351（0.539691 mm）、2787/3351（0.541564 mm）及其所有顶点不动，不能混淆为 projection-only。

2182/3330 实际 common edge 79/955 的零距保留合法，边外与共面面积继续严格限制。2181/3329 保留 NONADJACENT_TRUE_COLLISION。204/207 旧 nonadjacent gap 0.024319952 mm 已 before / after 监视，但不是唯一 contact。整个 affected-incident 与 whole-mesh broadphase 的 source component catalog 为 10 个真实接触家族 / 10 components；没有新 components、没有 feature expansion、没有整体范围扩大。所有 closest-feature 和 component 逐项 before / after 在 R4_BASELINE_CONTACT_COMPONENT_AUDIT.json。

未合格终点新增 true self intersection、off-shared component、positive-area coplanar overlap、material-path reversal、degenerate face 和旧 contact worsening 均为 0。native manifold incidence、V3416 / E6828 / F3414 以及 native cycles 不变；boundary 审计覆盖所有 moved incident edges、write boundary 与第一层 fixed-fixed 外环，未出现新 screen fold。boundary 人工 PASS 未设定，不能用这个数值 screen 代替 natural contour 审阅。

四个临时 BIND_RSSF、IDX_MCP_15 / 30 / 45 smoke 均 NOT_RUN_NO_QUALIFIED_CANDIDATE，符合“完整候选后再 smoke”的顺序。Full42、Stage6B、ownership R3、skin rebuild、promotion 均未进行。INCIDENTAL_STAGE6A_CONTACT_DELTA = NOT_MEASURED_NO_R4_POSE_SMOKE；旧 FullStage6A FAIL / 9 severe crossings 独立保留，没有重分类或用于优化。

review.html 第一屏为普通原始 Human 相机下 CURRENT / R1-C FAILED / R2-S5 FAILED / R4-A unavailable。之后为 dorsal、close、grazing、side、silhouette、wire 与边界参考。未合格诊断另列且明确禁选，之后提供 0° / 60° / 120° 原生截面与健康参考，彩色 forensics 放在最后。无合格 B，所以无 B 选择入口。

生产、旧阶段报告、旧临时场景和旧参考 bytes 的 3326 文件 SHA256 前后清单已完整核对并通过。所有新文件都在当前 R4 目录，UV / material / normal flag / custom normal / weights / bones / joints / RSSF 没有生产变更。最终 no-drift 证据见 PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json。

NEXT = STOP_HUMAN_REVIEW_NO_APPLY。Human 本轮仅审阅失败证据；没有可供 HUMAN_SELECT_R4 的合格方案。
