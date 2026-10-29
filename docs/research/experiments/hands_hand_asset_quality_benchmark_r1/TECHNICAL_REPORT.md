# HANDS_HAND_ASSET_QUALITY_BENCHMARK_R1

结果：**NO_MEANINGFUL_QUALITY_ADVANTAGE — STOP — HUMAN REVIEW**。

本轮实测一个独立候选：Innerscene 发布、由 MakeHuman/MPFB 派生的 Posable anatomical right hand。中性俯视下，候选食指近节靠拇指侧的曲线较少出现基线那样的中段外鼓；但侧视、虎口反向观察及屈指后的结果没有共同建立明确的整体自然性优势。第一指蹼仍有可见折面。当前证据不足以用迁移成本换取这个候选，**不建议据此进入资产适配或替换**。

这是本次受限样本的视觉判断，尚未经 Human 认可；既不证明现有模型不可修复，也不证明其他外部资产没有优势。候选的指甲细节和更高三角形数量不计作两个目标病灶的修复证据。

## 真实资产与许可

| 对象 | 实际取得与选择结果 | 来源和许可 |
|---|---|---|
| C1 基线 | 读取已冻结文件中的正式右手，没有重新建模 | `audits/minuet_stage_c_r1_dual_hand_synchronized_performance/STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY.blend`，SHA256 `d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7` |
| Innerscene / MakeHuman | 已下载原始 GLB 并实际导入 Blender；唯一独立实测候选 | [发布方资产页](https://www.innerscene.com/tools/library/3d-parts/posable-anatomical-right-hand-f6098b4f)明示 CC0，作者/派生制作方为 Innerscene，上游为 MakeHuman Team / MPFB；[上游资产授权](https://static.makehumancommunity.org/about/license.html)、[MPFB 许可分界](https://github.com/makehumancommunity/mpfb2/blob/master/LICENSE.md)支持 core mesh、rig 和输出采用 CC0 |
| Blender Human Base Meshes / Dan Ulrich | 已有官方原包，但排除独立升级候选身份 | [官方分发](https://www.blender.org/download/demo-files/)为 CC0。项目已有精确网格祖先证据，当前 C1 就源自其 `Hand  - Realistic`，不能重复算一个新模型 |
| SparrowHawk / Hands Rigged | 查得 CC0，但未取得文件，不纳入视觉实测，不评价其实际质量 | [作者发布页](https://blendswap.com/blend/22269)与[下载页](https://blendswap.com/blend/22269/download)可读；下载要求登录。未登录、未注册、未绕过限制、未购买 |

没有凑出第二个模型。候选原始下载入口为 `https://www.innerscene.com/api/library/posable-anatomical-right-hand-f6098b4f/download`，原件保存在 `sources/hand-posable.glb`：506,476 bytes，SHA256 `d1705ec1317516e79deb5c5ce4ef34e69bf6315bba9025e8a7374fbd0c745f47`。实际响应地址和哈希见 `ASSET_DOWNLOAD_RECEIPT.json`。

CC0 允许商业使用、修改和分发，未要求署名，也没有禁止将衍生 GLB 交付终端的条件；保留来源是本项目的溯源做法。[CC0 条文](https://creativecommons.org/publicdomain/zero/1.0/legalcode.en)不提供权利担保，也不授予作者背书、商标或第三方人格权。发布方专门对本派生手模作了 CC0 声明；上游资产许可与软件的 GPL/AGPL 许可分别记录，没有把软件许可误套到模型。归档 HTML 和上游许可文本位于 `sources/`。

GLB 实际无图片、无外部 buffer/image URI，仅有常量色 skin 材质。其 MPFB 自定义元数据提到 jartur69 皮肤来源，但没有包含该皮肤贴图；[上游皮肤目录](https://static.makehumancommunity.org/assets/assetpacks/skins02.html)也列该皮肤为 CC0。本对标完全使用统一中性材质。

## 对齐、相机和真实几何

运行 Blender 5.1.2，独立后台 Python 实例，禁止自动执行文件内脚本。所有写入在本实验目录。原 C1 只读加载，没有保存回源文件。

基线对象为 `RIGHT_HAND_OFFICIAL_L1_PRODUCT_MESH.002`，骨架为 `RIGHT_HAND_PRODUCTION_RIG.002`。读取场景第 157 帧后，在内存副本解除骨架 Action 引用，将 pose basis 归零建立绑定中性状态；保留原有 rest data、蒙皮和 corrective driver。它**不是正式演奏 2.600 秒原姿态的截图**。随后只在内存里使用各自既有骨架摆两个最小静态姿态；不生成 Action，不迁移动作，不将外部模型绑定现有 Rig。

对齐依据真实关节头位置：腕→中指 MCP 为纵轴，食指→小指 MCP 的正交投影为横轴，中指 MCP 为原点；统一食指 MCP–PIP 骨长为基线的 32.2930145 mm。候选原骨长为 28.7180977 mm，单一缩放系数 1.1244831。没有逐顶点拟合、非均匀拉伸或轮廓优化。腕端截取长度不同，完整俯视保留这个差别，不用长腕筒评价手掌大小。

**候选原件存在反射变换**：mesh 和 armature 的世界矩阵行列式均约 −0.9840803。按腕/MCP 标志对齐后，以真实指甲几何确定的手背落在与基线相反的一面。发布方及骨名虽然写 right / `_r`，本轮不能认证这个原件已具有与当前正式右手一致的手性。对标几何仅在展示坐标中反射 Z 以统一掌背方向；未改下载原件，也未制作已解决手性问题的生产资产。此操作在四张图及 JSON 明示。展示网格的面绕序依据完整变换后的封闭体有向体积核对，双方最终朝外；没有通过反法线或背面灯光制造差别。

原生绑定姿态仍不同：统一骨长后，基线与候选的 MCP 行、指尖和拇指并不重合。没有为了匹配姿势重建骨架。食指径侧图沿共同横轴观察；两者食指骨轴尚有残余角度差，不能称为每根骨头完全相同的局部真侧投影。金色 MCP–PIP 中心线来自实际骨骼投影，只用于识别骨段，不表示皮肤编辑区域。全部皮肤保留，其他手指造成的可见遮挡没有被隐藏。

所有同名视角的两模型使用**相同相机矩阵、正交尺度、分辨率、中性材质和 studio light**，已程序核对。Workbench `paint.sl`，shadows on，cavity/specular off，无纹理、无细分或几何平滑。主证据全部为统一 Flat。整手图另外展示双方同时统一 Smooth 的同一几何，以区分表面着色；该行不作为优胜依据。最终四图只是实际 Blender 栅格渲染的等倍率排版和文字标记，没有 AI 手型或修图变形。

## 视觉观察与七项问题的回答

1. **取得什么资产、许可如何？** 上表的一项独立 CC0 候选已经实测；Blender 官方母体同源，BlendSwap 未下载，均未冒充第二项实测。
2. **食指近节谁明显更好？** `INDEX_PROXIMAL_COMPARISON.png` 中，候选俯视径侧边缘相对更连续，基线中段外鼓较显眼；但候选也有从粗指根过渡到较细骨段的收窄。侧视候选没有呈现足以消除姿态差异影响的明确优势。因此记录“局部俯视有改善迹象”，不判定跨视角明显胜出。
3. **虎口谁明显更好？** 候选连接区域更宽，拇指根体块更完整；但其食指根/掌部仍有密集三角折面，掌侧反向和展开后没有稳定、明显更自然的软组织过渡证据。不能因凹面更宽就当作原塌陷已修复。此项无明确优胜者。
4. **是否自然弯指、展开拇指？** 已实际摆姿并渲染，见下表。候选可以屈指及展开，未在这些视角观察到整块皮肤脱离或明显炸裂；这只证明该小范围 FK 操作可用。屈曲食指的根部体积、指蹼折面仍需 Human 判断。自然性、全活动范围、对掌、真实教学触键均没有通过认证。
5. **适配难点？** 骨轴、关节中心、骨长、原生姿态、命名和手性不同；目前没有现成语义一致的控制器或 corrective。现有 C1 的接触 marker、skin pad、顶点引用和 corrective 都不能按编号照搬，已有 Action 的通道/关节空间也不能直接复用。必须另行定义安全的接入机制与接触再标定，本轮未做。
6. **旧修补还是迁移成本低？** 技术推断：短期保留现有 Rig/接触/Action 的局部修补集成成本较低，但此前 Human 连续否决，达到满意外形的剩余工时没有可靠估计。迁移本候选则确定会增加骨轴映射、marker 重建、蒙皮/指蹼验证和演奏回归成本；其视觉收益又未确立，当前更不划算。无法据本轮给出“最终获批总成本”或人日承诺；这里也不授权继续旧 A/B 修补。
7. **足够建议下一轮适配吗？** 不足。当前不建议进入本候选的资产适配，更不能正式替换。请 Human 先看实际对照；保留本轮不优胜的结果，不因需要推进任务而推荐迁移。

## 原生 Rig 与静态变形实测

| 状态 | 实际执行 | 可比性和限度 |
|---|---|---|
| 绑定中性 | 两者所有 pose basis 归零，各自原生骨架/蒙皮 | 原生曲度与指列不同，并非完全相同的最终姿态 |
| 食指适度屈曲 | 名义目标 MCP/PIP/DIP 增量 20°/35°/15°，绕掌部横向轴，经过骨架/展示矩阵共轭转换到原生局部空间 | 实际 PIP、DIP 向掌侧移动已核实；因原生对象变换不同，实际局部角度也有残差，最终关节位置和张角未精确匹配 |
| 拇指展开 | 名义目标拇指根骨增加 15° 展开 | 第一指蹼确实随动；不是对掌测试，骨名 `_01` 不证明其枢轴已符合 CMC 生理位置 |

从保存的实际 pose basis 矩阵复核，基线局部旋转量为 20.000°/35.000°/15.000°，拇指 15.000°；候选为 19.250°/35.822°/15.266°，拇指 16.858°。候选原生世界变换不只是纯旋转，转换为可用局部旋转后存在上述差异。它们是可比较的适度屈曲/展开观察，**不是严格等角的变形质量试验**。不以细小姿态差异作为自然性优胜证据。

候选原件有 16 个 deform bones / 16 个蒙皮组：`hand_r` 以及 index/middle/ring/pinky/thumb 各三段。普通手指 `_01/_02/_03` 对应拟解释的 MCP/PIP/DIP 链；拇指链可作 CMC/MCP/IP 语义起点，但尚未逐项确认生理转轴。glTF 导入显示的骨尾是导入器的可视化构造，不能用它代替下一子关节头来认定骨长。

实际无 Action、shape key、corrective、driver、骨约束和控制器。任意 XYZ 可转不等于已具备有效的生理限位；发布页提到的 Blender 约束没有包含在取得的 GLB 中。16 个组覆盖所有顶点，权重和范围约 0.999999892–1.000000093，最多四个有效影响；位置重合的拆分顶点权重相同。没有修补任何权重。

基线保留的 `FIRST_WEB_OPPOSITION_CREASE_R1` 在本次三种静态输入下均为 0。**本轮没有检验它的激活区间兼容性**，也没有沿用上一实验的兼容 PASS。外部候选没有对应 corrective。

## 拓扑与工程兼容性

| 项 | 当前 C1 | Innerscene / MakeHuman | 工程含义 |
|---|---:|---:|---|
| 导入顶点 | 3,300 | 8,120 | 数量不作质量分数 |
| 原生面 / 三角形 | 3,298 quads / 6,596 tris | 12,728 triangles | 候选为 GLB 三角化交付，无法从该文件直接审阅原始 quad edge loops |
| 重合位置合并后的点数（1e−8 m 舍入） | 3,300 | 6,366 | 候选有导出拆点，不能把全部拆边当皮肤破洞 |
| 原生拓扑边界边 | 0 | 4,532 | 候选按位置虚拟焊接后为 0，未实际焊接、未更改拓扑 |
| 虚拟焊接后 >2 面共边 | 0 | 0 | 只是邻接检查，不等价于自交/可动画认证 |
| 骨骼 | 21 个，其中包含 tips；现有系统已积累动作 | 16 个全部 deform，无显式 tip bones | 外部节点不能按字符串替换现有动作通道 |
| Corrective | 现有驱动保留 | 0 | 拇指极限、MCP 屈曲体积都需要额外证据 |

三个状态均检查了非有限点、退化三角形和基础边邻接：未发现非有限点或面积趋零三角形。没有因此颁发几何安全 PASS。自交、逐面翻转、完整关节活动范围、触键净空及非目标键碰撞均 **NOT_TESTED**。没有重跑六态、23 音或整曲，因为本轮禁止实际接入。

正交俯视展示在技术上可行，候选的食指及指列也可辨认。但生产部署需要处理源文件负行列式、坐标和单位；重新核实右/左手语义；在允许的未来方案中决定保留现有 Rig 还是使用其 Rig；重建接触 marker、掌/指 pad 和指尖采样；重新定义 pose 驱动或 corrective；再验证 C1 固定姿态、A♯4 原 0.282 mm 净空及全曲动作。这些都是成本估计中的待办，**本轮未执行，也没有可继承的旧 PASS**。MIDI 音符内容可保留是语义层面的推断，不代表现有运动轨迹可直接使用。

## 证据文件与保护

- 四张核心图：`HAND_ASSET_OVERALL_COMPARISON.png`、`INDEX_PROXIMAL_COMPARISON.png`、`FIRST_WEB_COMPARISON.png`、`POSE_DEFORMATION_COMPARISON.png`。
- `HAND_ASSET_BENCHMARK_REVIEW.blend`：可打开的两模型并列中性展示；`HAND_ASSET_BENCHMARK_STATIC.blend`：三种姿态的静态真实网格快照。它们不宣称保留可驱动的演奏 Rig。
- `CANDIDATE_IMPORTED_UNALTERED.blend`：原始 GLB 导入状态，保留其原生骨架和材质；导入器产生的 Icosphere 骨显示辅助物不算皮肤，未纳入评比。
- `ALIGNMENT_AND_POSE_RECEIPT.json` 记录尺度、反射、骨骼矩阵、全部静态 pose 和实际关节坐标；`RENDER_MANIFEST.json` 记录每组相同相机和输出来源；`JOINT_PROJECTION_RECEIPT.json` 记录图上骨轴标记投影。
- `BASELINE_INVENTORY.json`、`CANDIDATE_INVENTORY.json`、`CANDIDATE_RIG_AND_SKIN_RECEIPT.json` 和 `GEOMETRY_AND_TEST_SCOPE.json` 为实际检查数据。
- `PROTECTED_SHA256_BEFORE_AFTER.json` 对本轮列入保护的 82 项输入重新哈希；下载原件另列 SHA256。所有源文件保持不变；本实验没有访问独立 piano 目录。收据不把未全面测试的历史兼容性冒充本轮通过。

**STOP — HUMAN REVIEW**
