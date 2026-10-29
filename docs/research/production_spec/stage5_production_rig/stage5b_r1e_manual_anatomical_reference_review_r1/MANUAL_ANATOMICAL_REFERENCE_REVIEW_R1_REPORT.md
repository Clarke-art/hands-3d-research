# MANUAL_ANATOMICAL_REFERENCE_REVIEW_R1

本轮仅 anatomical registration。**最终 Branch D：MANUAL_REGISTRATION_REQUIRED**，状态 **PENDING_HUMAN_REGISTRATION**。已制作本地双栏/SVG 标注审阅页、A–E 真实参考图包、五个冻结 R1B 视图及 3-edge path 检查图。没有替 Human 注册点或推导 weight authority。

## 优先发现

Body 16 模型表面仍是食指近节管周向环的强候选，沿当前 engineered INDEX MCP→PIP 投影 0.628–0.730。其候选位置在 MCP 表面/皮纹远侧、PIP 皮纹近侧；照片 skin crease 不与骨关节中心完全重合，故此为候选关系。4 簇保持背侧4、掌侧5、桡侧3、尺侧4。桡侧不能仅凭朝向虎口被注册为 first web。逐点候选、照片可见表面线索及限制记录在 JSON。

**v2192 的解剖对应存在可见冲突。** 在 pre-RSSF native geometry，它与 v703、v2169、v704 连续沿食指管表面排列；不像独立拇指分支的末端。当前 contact pose 中它距 engineered thumb-tip endpoint 6.428 mm；这个接近不能反证 native surface identity。v2169 在原始表面是背桡侧食指近节候选，并非已证明 shared interface。所有 cap authority 保持冻结，不由本次观察撤销。

## 3-edge path：视觉与拓扑分开

重算全 CAP→INDEX collar 的 edge-length shortest path：**v2192→v703→v2169→v704**。三个现有边长为 4.540557, 4.387491, 4.236569 mm，总长 **13.1646179 mm**；对应 pre-RSSF 总长 12.7149155 mm。每边均有两个 incident faces，没有新桥接边/裂缝/非流形证据；路径与 approved WEB 无交集。

sanity 检查选 **C：region/semantic correspondence anomaly**，限定为“冻结 cap 的工程名字与 native 模型位置不一致的可见冲突”，不是宣称模型有破损拓扑。它看起来是沿同一食指管的普通连续路径，不能称为已证明的 thumb distal cap→first-web 合理解剖捷径。总体人体对应仍待 Human，因此全局最终分支保持 D，未强行使用 A/B 或注册为真实 shared patch。

## 真实照片与手性筛选

A 采用 Sciencia58 原始双图中的右手背侧部分；B 采用同作者另一张右手掌侧。D 为 A 的开放虎口 viewport，E 为 B 的 index proximal closeup viewport；只是展示窗口，未改原像素。C 为 Charles A. Goldfarb / Washington University 的术后虎口斜视实拍，用作补充；其瘢痕、遮挡、laterality 未在来源明说和非正常 native margin 的限制均显示。没有把它当正常虎口边界标准。

参考来源：[Sciencia58 背侧双图](https://commons.wikimedia.org/wiki/File:Hand_male_both_sides.jpg)、[Sciencia58 掌侧照片](https://commons.wikimedia.org/wiki/File:Hand_female_5.jpg)、[Washington University 斜视实拍](https://congenitalhand.wustl.edu/2020/08/tight-first-webspace/)。A/B 原图许可证 CC BY-SA 4.0，页面保留署名/来源/许可证。C 仅为本地研究参考，未建立再分发许可。

另有两张标题声称 right hand 的图与可见手性冲突，已明确排除，未镜像造出右手。主参考是外观正常的成人照片，没有临床健康筛查数据，也不是该模型的原始扫描对象。

## 可见 landmarks

在原图独立 SVG 层标出 INDEX MCP 的表面 knuckle/皮纹候选、PIP 可见皮纹、近节表面、commissure margin、thumb MCP 表面轮廓、CMC broad approximate region、thenar eminence、dorsal/palmar first web。没有把隐藏骨中心、韧带或肌肉插入点标成照片直接可见结构。C 的被遮挡 landmarks 未补画成确定位置。

模型显示 body16、INDEX16、exact16 edges、live INDEX MCP/PIP、thumb CMC/MCP、approved WEB/CAP。5 个 PNG 均有全局上下文和局部近景；v2169 在背、掌、桡和斜视有红圈。pre-RSSF 切换保留同 ID 原生形状，不错误复用 current engineered joint frame。

## Review 页

打开 `MANUAL_REGISTRATION_REVIEW.html`。默认双栏真实参考↔模型，支持切换5视图及路径、R1B/pre-RSSF、landmarks、ID、4簇显示。背侧/掌侧/掌侧近景可启用 INDEX MCP/PIP 两点轴对齐的 opacity overlay；它只是一项可人工修正的二维 similarity hypothesis。匹配两点不意味着其它 landmarks 正确，也不是非刚性配准。斜视/虎口/路径以及 pre-RSSF 自动关闭 overlay，避免错误外观。

Human 的五个问题已经放在页尾，逐簇也可记录候选/未决。答复可导出 JSON，仅本地保存，不改生产文件，不自动修改 authority。默认答复均“未判断”，本轮 Human answers=0。

## 冻结与停止

1340 个既有 production_spec/docs 文件 SHA-256 before=after；包含 R2A/R1B/R1E、R3 evidence、feasibility、endpoint authority 和 narrow anatomy 各轮输出。WEIGHT/GEOMETRY/TOPOLOGY/BONE/JOINT DELTA=0；BLEND_FILES_WRITTEN=0；R1F_CREATED=false。未跑 deformation、Stage6 或 retopo，未提出生产权重数值。

**STOP — WAITING FOR HUMAN REVIEW**。
