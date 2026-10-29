# NARROW_ANATOMICAL_EVIDENCE_REVIEW

结论：**Branch D — ANATOMICAL_CORRESPONDENCE = UNRESOLVED**。
下一候选：**MANUAL_ANATOMICAL_REFERENCE_REVIEW**。完成本轮后 STOP，等待 Human Review。

这 16 点在模型中确实绕食指近节管形成周向环，而非单一虎口/拇指基部表面片。可提出“食指近节表面组织”的强候选对应；但未完成真实虎口边界、皮纹或皮下附着点的配准，也没有对应位置的原生 CMC/MCP 分离皮肤位移证据。因此整圈及局部新 thumb authority 均未获支持。本轮的 UNRESOLVED 不表示已证明 thumb coupling 为零，也不表示 R1B 的具体权重已经被解剖学验证。

## 精确对象与静态定位

Body-side IDs：2153, 2155, 2157, 2159, 2161, 2163, 2166, 2169, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203。
INDEX-side IDs：689, 692, 693, 696, 698, 699, 702, 704, 2156, 2160, 2164, 2167, 2170, 2172, 2174, 2176。
Exact cut-set = 16 edges；C0/C1/C2 = 32/32/32。

从 Stage4A R2（pre-RSSF）到 R1、R1A、R1B，3416 顶点及 3414 面的顶点顺序完全相同，允许追踪同一 ID；只读取静态数据，没有运行 deformation。定位不是从 R3 THUMB、THUMB_DISTAL 或旧 INDEX_ROOT 标签推出。Stage4A R2 的 canonical frame 为右手、+X 桡侧、+Y 背侧、+Z 远端；Stage2 源轴不同，未混用。pre-RSSF 精确环 PCA 平面与面积加权法线决定周向簇；current live MCP→PIP 轴独立检查。当前法线跨过扇区边界的点在逐点 JSON 中标注，簇不是组织学分割。

当前 body 点沿 INDEX MCP→PIP 的轴投影在 **0.628–0.730**，该骨段长 31.508 mm。“index-root”作为宽泛历史术语不够精确，环实际位于近节管向 PIP 的一段。每点记录背/掌/桡/尺位置、两份法线、live thumb CMC/MCP、index MCP/PIP 距离、WEB/CAP/thenar proxy 欧氏/图/边长测地距离及邻面。骨点只作描述，不作组织许可。closest skeletal landmark 也不等于 closest skin attachment。

## 四个可复现候选簇

| 簇 | 数量与 IDs | 候选真实表面角色 | 证据与限制 |
|---|---|---|---|
| DORSAL | 4：2153, 2169, 3196, 3203 | Dorsal index proximal-phalanx integument; local digital gliding/wrinkle apparatus candidate, not a registered PIP crease | S4, S6, S8，LEVEL_B；精确附着及 thumb driver 未决 |
| PALMAR | 5：2157, 2161, 2163, 3198, 3201 | Volar index proximal-phalanx skin/fat with local fascial tether and adaptation candidate; not proven thenar anchor | S4, S5，LEVEL_B；精确附着及 thumb driver 未决 |
| RADIAL | 3：2159, 3197, 3200 | Radial index proximal-phalanx lateral integument; possible commissure-facing extension remains unregistered | S3, S4, S7，LEVEL_B；精确附着及 thumb driver 未决 |
| ULNAR | 4：2155, 2166, 3199, 3202 | Ulnar index proximal-phalanx lateral integument; local digital cutaneous anchoring candidate | S4, S5，LEVEL_B；精确附着及 thumb driver 未决 |

簇的区域身份 confidence = MEDIUM；模型坐标定位 confidence = HIGH；具体组织插入点和 CMC/MCP authority = UNRESOLVED。不会把皮肤顶点命名为某条韧带本体。

## 窄范围文献证据与对应缺口

S1 为第一虎口形态原始论文；本轮可访问的 primary 索引内容不足以核查详细边界，明确降为 LEVEL_C，不能凭题名转成模型定位证据。[Zhu 等，2024](https://pubmed.ncbi.nlm.nih.gov/39084025/)

S3 的供区描述从食指 MCP 桡背侧朝背侧虎口延伸，说明真实界面并不由工程 WEB 标签封闭定义。但移植皮瓣供区是邻域参考，不能将更远端近节管整圈或其桡侧直接认定为原生虎口组织；对本模型的推断为 LEVEL_B。[Sano 等，2012](https://pubmed.ncbi.nlm.nih.gov/22471263/)

S4 的新鲜标本为小/环/中指，另有 Thiel 动态标本；显示侧方指皮肤的锚定与滑移关系。S5 则说明掌侧皮肤脂肪的局部筋膜网络随指屈曲改变方向。它们支持食指同源区域的候选角色（LEVEL_B），没有直接研究本食指虎口或 thumb motion，也不能证明模型上的韧带插入点。[Cleland 研究](https://pubmed.ncbi.nlm.nih.gov/24305724/)、[Grayson 研究](https://pubmed.ncbi.nlm.nih.gov/30170887/)

S6 提供 PIP 背侧皮纹附着的邻域证据；本环位于 PIP 近侧，未与真实皮纹配准，不能冒称位于 PIP wrinkle ligament 插入点。[Law 与 McGrouther，1984](https://pubmed.ncbi.nlm.nih.gov/6512362/)

S7 直接研究真实第一虎口挛缩松解后的功能：外展改善和对掌功能并不完全等价。LEVEL_A 只适用于真实 web 的功能关系，不能分离本位置 CMC 与 MCP 的原生皮肤驱动，也没有该模型注册。[Masden 与 Higgins，2011](https://pubmed.ncbi.nlm.nih.gov/22379438/)

S2 的血供交通仅为 vascular continuity（用于本变形问题是 LEVEL_C）；手术可移动的供区不等于完整皮肤原来的运动牵引。S8 的皮肤标记被动运动问题也提醒骨运动不是局部皮肤驱动身份的直接观测。[Pagliei 等，2003](https://www.sciencedirect.com/science/article/abs/pii/S026676810200298X)、[Nataraj 与 Li，2013](https://pubmed.ncbi.nlm.nih.gov/23775305/)

本轮注册 8 项原始研究：LEVEL_A=1、LEVEL_B=4、LEVEL_C=3；**直接注册 exact collar 并给出 driver authority 的来源数=0**。S1 可访问内容受限，已在 register 记载。无外部插图被复制进资产；commercial-use relevance = N/A。

## first web、thenar 与组织连续性

first-web correspondence：**UNRESOLVED**。模型已批准 WEB 是工程语义片，真实 commissure 可有延伸。10–16 graph edges 与无 direct adjacency 仅描述模型拓扑；既不能直接否定延伸，也不能因距离近就肯定。桡侧簇最值得人工配准，但目前不是 SUPPORTED shared cluster。

thenar correspondence：**NOT ESTABLISHED**。模型 thenar 仅有历史 arc/ownership proxy，不存在注册的人体边界；本环周向覆盖食指近节表面，不能当成 thenar/palm anchor 的已证身份。检索到的证据没有量化原生 thenar→此环在 thumb opposition、CMC opposition 或 thumb MCP flex 下的位移传递。

ANATOMICAL CONTINUITY 是可连续的区域布局；VASCULAR CONTINUITY 是血管通路；FASCIAL CONTINUITY 是筋膜附着/连续网络；SKIN MOBILITY 是皮肤可滑移或调整；DEFORMATION COUPLING 需要对应位置随指定关节动作的实际运动关系。前四者不能自动推出第五者，更不能推出某个 production 权重值。

CMC cross-region evidence：真实 web 对掌功能为 LEVEL_A，传递到候选桡侧模型位置最多 LEVEL_B 且未注册；**exact collar CMC authority = UNRESOLVED**。
MCP cross-region evidence：相邻手术供区为 LEVEL_B、血供为 LEVEL_C；没有原生 thumb MCP flex 对本环皮肤的独立测量；**exact collar MCP authority = UNRESOLVED**。两关节没有合并推定。

## 独立权重 provenance 审查

16 点 R1→R1A→R1B 的完整权重向量逐项完全相同，均由 INDEX_MCP_R 主导。初始 R1 脚本 line 111 使用 nearest-chain ownership，lines 295–317 设置语义/距离白名单，lines 321–365 以纵向/横向 Gaussian 场及 guard/归一化分配。源 bootstrap receipt 记录无 armature、无 vertex groups。因此它是可追溯的工程生成和继承，不能当作解剖测量。没有重跑旧算法。

独立模型几何及 LEVEL_B 文献使“食指近节表面组织”合理；但这只能支持区域 association，不能验证 R1B INDEX_MCP 的具体数值或证明所有 thumb transmission 必为零。旧权重可能不完全正确，也不能反推 thumb influence 正确。

R3 ownership 仍是 HUMAN_APPROVED 的 surface-domain identity；不能据此把其 THUMB 身份变成 skin driver identity。INDEX-side 16 点是同一食指管界面 counterpart，缺少新的对应运动证据，继续 **NO NEW THUMB AUTHORITY**。数值 sensitivity 需求不作为本轮解剖证据。

## Authority 与分支

整圈 thumb coupling supported = NO；partial regional coupling supported = NO（未获支持，不代表已证明生理 coupling 不存在）。CMC/MCP 新组许可均未授予。本轮不生成有条件的 allowed-group proposal 或 authority map，避免产生已批准区域的印象。没有提出 production 百分比、衰减方向或 anchor solver。

THUMB_IP_R 与 INDEX_DIP_R 不得作为未来新 collar authority；这不改写冻结历史向量或宣称其极小旧 residue 不存在。Approved distal cap 继续 THUMB_IP_R=1.0，approved first-web 继续既有四组并禁止 IP，未重开。

选择 D 而非 C：模型表面定位强烈支持 index integument 候选，但真实 commissure margin 和皮肤附着点未注册；缺少独立动态证据，不应将强区域候选升级成“已证明 index-only/stationary”或“已证明零 thumb coupling”。下一轮仅在用户授权后可人工将真实右手背/掌/桡侧图像及 MCP/PIP 皮纹、commissure margin 配准到 ID；如确认 shared patch，再寻找可区分 CMC/MCP 的原生皮肤运动证据。

## 输出与冻结验证

必需的 7 张 PNG 已生成，模型↔人体图逐项展示 body 16、INDEX 16、WEB、thumb CMC/MCP、index MCP、thenar proxy、cap、cut-set；人体对应写作候选，未伪造配准参考。逐点/逐簇定位、来源、confidence、冲突与 full vector provenance 在 JSON 可审计。

保护的 303 个既有文件全部 SHA-256 before=after，包括 R2A、R1B、R1E、R3 evidence、feasibility audit、上一轮 endpoint audit 及所有 workspace blend。全 blend inventory 相同，无新增/删除。WEIGHT/GEOMETRY/TOPOLOGY/BONE/JOINT DELTA 均为 0，BLEND_FILES_WRITTEN=0。

冻结 production master=R1B；R1E 仍 fail-closed candidate；R1F=NOT_CREATED。R3 exact collar 与 CMC cage PASS 为既有资格继承，本轮未重新测试。Pose/deformation runs=0；Stage6A/B/C=0；retopo=0。

**STOP — WAITING FOR HUMAN REVIEW**。
