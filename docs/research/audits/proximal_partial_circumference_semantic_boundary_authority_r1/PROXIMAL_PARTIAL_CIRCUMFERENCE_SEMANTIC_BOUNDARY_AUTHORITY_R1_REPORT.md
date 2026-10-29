# PROXIMAL_PARTIAL_CIRCUMFERENCE_SEMANTIC_BOUNDARY_AUTHORITY_R1

最终状态：**MACHINE_EVIDENCE_EXHAUSTED_HUMAN_ADJUDICATION_REQUIRED**。机器唯一候选为 NONE；在指定局部、真实拓扑与批准参考范围内，十张 exact face 的 anatomical role 仍为 AMBIGUOUS。NEXT = HUMAN_PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_ADJUDICATION；等待 Human 导出的 JSON，STOP。

## 范围与判定

只分析 P02–P06 的十张指定 face、直接 incident fans，以及每行一个 distal/proximal guard。P01/P07 仅为 guard context。五行直接 fan 的并集为 28 张原始 quad；每行直接 fan 为 12 张。全手坐标仅供视图定位，不计算全掌 role map，不沿链延伸，不加入第四条边界。

| 行 | Exact face IDs | 最终 exact role | 已有描述性支持与剩余缺口 |
|---|---|---|---|
| P02 | 1372 / 1375 | AMBIGUOUS | 成对 lanes、横向条带和 frozen web 方向提供 digit-web compatibility；两状态的主导 thumb wrapping 身份没有解剖注册。 |
| P03 | 1373 / 1374 | AMBIGUOUS | digit-web 支持与 morphology transition 并存；不能将转向自动升格为 broader-interface onset。 |
| P04 | 1368 / 1371 | AMBIGUOUS | 两 lane 连续存在，邻接 fan 没有独立批准的 broader sheet 身份。 |
| P05 | 1369 / 1370 | AMBIGUOUS | 既有 per-face 描述性场混合；normal sign 或极值不能裁定 anatomical role。 |
| P06 | 1378 / 1377 | AMBIGUOUS | post-reversal 只作已有描述，缺少正向 broader-interface 证明。 |

此表的 AMBIGUOUS 是逐面 anatomy authority 结论，不否认前轮的几何描述或 digit-web compatibility。JSON 逐面回答 thumb-local digit、web-facing flank、partial-circumference sector、broader palm/metacarpal/thenar interface 及其证据来源，并保留每面顶点、边、incident fan 和 immediate row。

P02 early control = FAIL，含义是主导 digit-web organization **未获机器认证**，不是已证实其属于 broader interface。本轮采用放宽后的新规则：允许 broader influence；没有将“无法排除 broader influence”本身当作失败原因。P06 late control = FAIL，因为正向 broader-interface 证据未建立，不能用“不像 digit”或 post-reversal 替代。

## Surface flow 与正向 broader 证据

LOCAL_SURFACE_FLOW_R1.json 保存 native/RSSF 每张 focus face 的原始面法向、incoming/outgoing transverse vector、面内 longitudinal tangent、沿真实 shared edge 的最小旋转搬运及 ordered vertex fans。搬运只连接原始相邻面；验证旋转正交、det=+1、法向与切向搬运一致。法向和切向用于表面组织描述，不产生 ownership 或阈值排名。

原始两 lanes 到所有固定 rows 仍成对连通。直接 fans 均为规则 quad continuation，没有独立批准的 thenar/palm sheet role 标签。每行检查五项正向 broader 条件：停止 thumb wrapping、跨越更宽掌/掌骨表面、两 lane 不再成对 digit-sector、fan 转入共享 sheet、独立 anatomical reference 证明该关系。没有一行同时取得所需正向证明。几何 pairing 的存在也不反向证明必然属于 digit。

部分 circumference 不要求闭合 ring；本轮明确审查 transverse wrapping、longitudinal branch、normal-field organization、frozen-web sector 关系和 broader-sheet 排除/主导组织。没有用完美圆柱或完整闭环作为必要条件。既有 widening 和 reversal 只保留出处，不计算任何新 scalar extrema，不用它们推荐 A/B/C。

## 三个固定候选

| Option | 固定边界 | 顶点对 | Exact face transitions | Role change proven | Too early / too late |
|---|---|---|---|---|---|
| A STOP_AFTER_P03 | e1375 / e1374 | [1518,293] / [386,1518] | 1373→1368 / 1374→1371 | NO | UNRESOLVED / UNRESOLVED |
| B STOP_AFTER_P04 | e4666 / e4668 | [1444,2822] / [1520,2822] | 1368→1369 / 1371→1370 | NO | UNRESOLVED / UNRESOLVED |
| C STOP_AFTER_P05 | e1376 / e1377 | [294,1519] / [1519,385] | 1369→1378 / 1370→1377 | NO | UNRESOLVED / UNRESOLVED |

三条均未被排除，均未证明 distal digit-web → proximal broader interface 的精确角色变化。D = KEEP_UNRESOLVED 不建立新的边界。机器证据在用户指定的局部 authority 问题上已用尽；一般 anatomical context 足够开展有范围的 Human review，因此不选择 INSUFFICIENT_ANATOMICAL_REFERENCE。

## Anatomy reference 的来源与限制

采用批准 corrected kinematic distal direction、批准 thumb nail dorsal、frozen FIRST_WEB21 四 seeds 与既有真实 strip、批准 RSSF MCP/CMC，以及独立 Stage4C wrist reference。旧 Stage4B cut-plane wrist 不作为此参考。方向轴均不等于 palm normal。既有 strip 是几何上下文，不是新增角色批准；CMC cage 不作为 hard ownership 来源。

Native 没有独立批准的 corrected MCP/CMC 位置注册。本页通过相同 frozen nail 顶点 IDs 的刚性方向拟合搬运 approved corrected distal orientation，拟合 RMS = 0.144503 mm；只搬运方向，不声称 native MCP/CMC 位置。精确 approved joint markers 出现在 RSSF companion。该限制在页面与 JSON 均可见。侧名是 thumb-local nail/web reference side，不是全掌表面标签。

先检查本地参考：AI canonical 图片和未注册模型缩略图不能作为真实 anatomy。采用已有 Sciencia58 真实手外观照片：背侧使用 male_both_sides 的右手 dorsal panel，掌侧使用 Hand female 5；CC BY-SA 4.0 授权和来源链接保留。照片为其他手，landmark registration 仍待 Human，不将其位置转换为本模型 face ID。来源：[Hand male both sides](https://commons.wikimedia.org/wiki/File:Hand_male_both_sides.jpg)、[Hand female 5](https://commons.wikimedia.org/wiki/File:Hand_female_5.jpg)。

仅补做一次针对 first-web/MCP/thenar 的来源查阅。Kapandji 的 indexed English abstract 支持 first-web 功能涉及 trapeziometacarpal、肌筋膜、web integument 与 thenar aponeurotic system，不能给出本 asset 的离散边界。[Functional anatomy of the first web space, 1986](https://pubmed.ncbi.nlm.nih.gov/3767503/)。2024 cadaver study 的 indexed abstract excerpt 支持外观形态不对称和 palmar-abduction 参考姿态相关；不能把 chain 当作完美圆柱或确定 A/B/C。[Measurement and observation of the first web space based on morphology and clinical applications](https://pubmed.ncbi.nlm.nih.gov/39084025/)。查阅日 2026-10-03；PubMed 直接访问遇 CAPTCHA，未绕过，未查 full text。术后 WashU 图片未作为正常 anatomy authority，也未嵌入重分发。

## Human Review 与验证

交付 PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_HUMAN_REVIEW.html：自包含、无 CDN，支持本地离线打开。native/RSSF 两个 viewer 可拖动、缩放、切换 palmar/dorsal/radial/ulnar、局部/冻结 context、IDs 和 flow。附九张科学图：三边界总览、A/B/C closeups、P02/P06 controls、两状态四视角和 frozen landmarks。

A/B/C/D 为真实可选 radio，均未预选；Q1/Q2/Q4/Q5 均为空，Notes 可填写，Q3 自动绑定原始 edges 和 face transitions。导出 JSON 具有 review_id、selected_option、Q1–Q5、notes、timestamp。D 导出 null 边界并保持未决。批准 A/B/C 需要 Q1/Q2/Q4 全为 YES。导出不应用 authority、不修改 production，不延伸角色或自动启动 solver。批准范围仅为 proximal semantic stop。

使用 computer-use 浏览器流程验证。空答复被阻止，A/B/C 的 Q3 IDs 与固定边对一致，D/UNRESOLVED 实际生成 JSON。浏览器 download-event 捕获 API 超时，但实际下载文件在本机 Downloads 中找到，并逐字段与浏览器预览完全相同；QA_DOWNLOAD_VERIFICATION_R1.json 记录其哈希。测试文件名及 response_kind 均明确为 AUTOMATED_UI_VALIDATION_NOT_HUMAN，approved_for_boundary_authority=false，不能作为 Human decision。正式页面已恢复无测试参数和空白答案，Human response count = 0。

页面第一次运行的 newline-escape JS 语法错误已通过 raw HTML template 修复，重新加载后双 viewer、表单与导出均运行。21 项 response logic 检查覆盖三边对、D/null、空答复、无效第四候选、矛盾批准、timestamp、Unicode 和生成 HTML 的 JS 解析；另有 216 项静态/拓扑/搬运/冻结一致性验证通过。浏览器截图记录空白选项与导出控件。

## 冻结与停止

既有 1840 个 workspace 文件与 9 个外部输入文件全部 before == after；新增 workspace 文件仅位于本轮 audit 目录。所有既有 Stage4、Stage5、corrected rig、cap37、FIRST_WEB21、nail、CMC cage、distal stop evidence、R2/R3、Stage6、Human responses 均字节相同。WEIGHT/GEOMETRY/TOPOLOGY/BONE/JOINT_DELTA 全为 0；R2/R3/skin/Stage6 runs = 0；BLEND_FILES_WRITTEN = 0。

NEXT = HUMAN_PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_ADJUDICATION。等待 Human 导出 JSON；不再进入 scalar audit。STOP = YES。
