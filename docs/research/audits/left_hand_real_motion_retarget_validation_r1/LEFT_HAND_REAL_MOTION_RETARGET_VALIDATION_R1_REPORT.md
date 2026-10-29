# LEFT_HAND_REAL_MOTION_RETARGET_VALIDATION_R1

2026-10-07 · DESIGN_ONLY · INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY

**FINAL_STATUS = LEFT_REAL_MOTION_RETARGET_VALIDATED**（Agent validation result；**HUMAN_REVIEW_PENDING**）

固定 recording 的真实左手 track 完整存在。已使用冻结 LEFT R1 生成独立真实左手 Action，复用批准右手解剖 mapping 的镜像语义，未实施 left-specific correction。
可见预检未观察到新增系统性 axis/chain 错误或 first-web blocker；食指末端 fast bend 单独保留为 PRESENT / DEFERRED。
“VALIDATED”在此是本轮提交给 Human 的 Agent 分类，不代表 Human 已批准这段新 motion，也不等同于公制生物力学或琴键接触验证。

## Q1–Q11

| 问题 | 检查 | 回答 |
|---|---|---|
| Q1 | 同一 recording 有真实 LEFT 21-point skeleton | YES |
| Q2 | 与右手为同 recording、同11.5–18.5s timeline | YES |
| Q3 | 主要继承 approved right mapping semantics | YES |
| Q4 | 需要一次 left-specific correction | NO |
| Q5 | 完整7秒 DEFAULT_TEACHING_VIEW 可接受 | YES — Agent可见预检；最终Human待审 |
| Q6 | NORMAL_ORBIT_VIEW 可接受 | YES — Agent可见预检；最终Human待审 |
| Q7 | REASONABLE_CLOSE_VIEW 可接受 | YES — Agent可见预检；最终Human待审 |
| Q8 | first-web 保持产品可接受 | YES — 未观察到新增blocker |
| Q9 | 出现新的系统性 flip / thumb axis error / palm collapse / joint inversion / motion jump | NO — 未观察到；局部fast bend单独记录 |
| Q10 | LEFT_FINGERTIP_FAST_BEND | PRESENT / DEFERRED |
| Q11 | 最终分类 | LEFT_REAL_MOTION_RETARGET_VALIDATED |

## 真实 source qualification

recording：2024-03-04_03-46-36，PianoVAM v1.2；固定区间 11.5–18.5秒，source frames690–1110 inclusive，共421个60Hz观测，每帧21×3，缺帧0、非有限值0。

真实物理左手使用原 JSON **Right** 字段。此 recording 的 JSON 左右标签与物理手相反：既有视频 overlay780 以及本轮原视频左手叠加对照均确认 Right 对应演奏者左手。原 JSON 标签及字节未改变；没有将既有右手 motion 镜像当作真实左手。

source SHA256：`02d336c7a114b5d92be9472acfab4ba746b4e5b106cba35575fe86fd1c294035`。
MIDI context 存在；同窗口自动预测左手 fingering onset 数为26，finger labels为['1', '2', '3', '5']。
MIDI/fingering只记录上下文，未生成或修正3D姿态；没有换sample或区间。

source x向图像右、y向下（乘1080/1920作aspect校正）、z为腕相对的估计深度；相机轴为right-handed。
这是视频估计的非公制2.5D landmarks，不是标定后的真实公制3D mocap。源数据能支持本轮方向/时序retarget验证，不能独立证明精确解剖关节角、指尖落键或空间接触。

## Mapping 与成熟语义的关系

LEFT_RETARGET_MAPPING_SOURCE = MIRRORED_FROM_APPROVED_RIGHT_MAPPING

直接以AST读取既有 approved `mapping_core.py` 的校准、raw mapping和smoothed方法；未执行其旧顶层脚本，未打开或修改旧右手工程资产。
保留最终 iteration2 的规则：MCP anatomical frame和RSSF rest-space offset；PIP/DIP signed hinge；thumb独立CMC median-base frame与MCP/IP hinge；腕固定平移，仅使用相对掌向。

左右变换发生在坐标与解剖basis层面：

1. 使用实测左手点 `pL`，构造镜像坐标图 `pVirtual=J pL`，`J=diag(-1,1,1)`。这只是同一真实左手数据的坐标表示。
2. 左手proper palm basis为`PL=[radial,distal,radial×distal]`；virtual basis为`J PL K`，`K=diag(1,1,-1)`，因此palm-local vector按K转换。
3. 使用已冻结镜像平面S、proper-frame补偿H，构造只存在Python内存的virtual rest：`RestVirtual=S RestLeft H`，`H=diag(-1,1,1,1)`。没有改任何Blender骨骼或rest。
4. 运行相同approved anatomical solver；返回`BasisLeft=H BasisVirtual H`，quaternion为`(w,x,-y,-z)`。这是由反射共轭推导，不是机械复制Euler或任意反号。

对全部raw observations的矩阵共轭检查最大误差为 `1.78813934e-07`。
MCP校准、hinge axes、thumb源参考及变换矩阵保存于 LEFT_RETARGET_MAPPING_R1.json。

smoothing直接复用60Hz quaternion三点`[0.25,0.5,0.25]`，邻居符号对齐并normalize；边界重复端点，后续quaternion符号连续，half-frame LINEAR keys。
没有新增滤波、调参、限角或二次smoothing。**MAPPING_CORRECTION_COUNT = 0**。

## Action 与产品隔离

Action：`PIANOVAM_PHYSICAL_LEFT_MIRRORED_MAPPING_R1`。
候选：`LEFT_HAND_REAL_MOTION_VALIDATION_CANDIDATE_R1.blend`。
候选SHA256：`c356c3d223f9f0853b3451d93a2cdc4a0212805b72a7aea3bc829d084f41665d`。

16个deform bones、64条quaternion FCurves，各421keys；5个TIP helpers无独立通道，腕无translation/scale keys。
30fps输出210帧、精确7秒；最后一个source endpoint18.5s保留在Blender frame211，而视频最后显示帧为18.4667s，视频持续至18.5s。
重新打开候选后验证全部421个evaluated geometry与保存前完全一致。

正式mesh coordinates、vertex order、topology/winding、UV、shading、完整weights、rig/rest/hierarchy、corrective geometry与driver均保持原样。
所有source-derived缓存、Action和证据只在本audit目录；正式左手baseline仍为原SHA、ZERO/RSSF、无测试Action运行依赖。

## 产品可见检查与范围

完整7秒三产品视角视频已生成并在审查页播放核验到7.000秒；另提供固定时间轴的真实左手视频+landmarks对照。
Agent可见判断依据为覆盖前/中/后时段的产品视角、source对照及16.5–17.0s的一组局部连续帧；不将这些观察表述为最终Human全片批准或逐帧穷尽证明。

DEFAULT_TEACHING_VIEW保留整体腕、掌、五指；NORMAL_ORBIT_VIEW按左手全motion范围固定取景，扩展过一次相机范围以避免末端出框；REASONABLE_CLOSE_VIEW聚焦first-web/thenar/指根，非forensic macro。相机方向按正式S反射，未复制错误的右手位置。取景调整不计为mapping correction。

观察到的掌体积、腕过渡与拇指运动方向基本可信；未发现新的系统性反折、整条finger chain翻转、thumb axis方向错误、明显掌塌陷、first-web裂开、flap、shelf或明显穿透。
**LEFT_FINGERTIP_FAST_BEND = PRESENT / DEFERRED**。食指末端在16.5–17.0s附近可见较快屈伸变化；单独记录、不修复。现有视频估计深度无法唯一判定这是实动还是landmark估计噪声，不据此重开axis或surface设计。

**FIRST_WEB_STATUS = ACCEPTABLE_NO_NEW_VISIBLE_BLOCKER_OBSERVED**。
本段421观测中的corrective自然值始终为0，driver及targets保持原样。因此本段未观察到first-web新增blocker，但不能声称测试了corrective的active range或扩大了已批准deformation envelope。

最低机器保护：421观测NaN/Inf=0、gross collapse=0、degenerate edges=0；拓扑始终一致，ZERO restore最大误差0mm。
明显penetration与surface接受度由可见证据预检记录，机器检查不作为Human PASS。没有hidden crossing、normal-dot、R3、true-cap、2127-edge或anatomy forensic。

## 交付与许可

- [review.html](../../../../examples/historical/audits/left_hand_real_motion_retarget_validation_r1/review.html)：完整播放、慢放、三视角/真实source对照切换。
- [三视角完整7秒](../../../artifacts/087520c577d578a61351.md)
- [真实左手同步对照](../../../artifacts/b6f09a72c029d08a60c5.md)
- [EARLY](../../../artifacts/4408577b8565205b8c77.md)、[MID](../../../artifacts/05cedb3f5b39bc5848cc.md)、[LATE](../../../artifacts/9438e05acb81dee8a36a.md)
- [单一区间连续帧](../../../artifacts/999b2f8cb46a3ab492ab.md)：fast bend观察记录，不是blocker ranking。

PianoVAM v1.2，Kim, Yonghyun; Park, Junhyung; Bae, Joonhyung; Kim, Kirak; Kwon, Taegyun; Lerch, Alexander; Nam, Juhan，ISMIR2025。
Source: https://huggingface.co/datasets/PianoVAM/PianoVAM_v1
License: CC BY-NC-SA4.0 https://creativecommons.org/licenses/by-nc-sa/4.0/
USAGE_SCOPE = INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY。
本次motion adaptation保留该署名与许可。修改包括固定窗口提取、左手解剖坐标映射、原有三点smoothing、产品渲染和视频叠加。source-derived motion不得直接promote至商业产品。

## 正式资产保护与停止

LEFT_R1_UNCHANGED = YES · `54307bb199a75a5e684c29d346de9ca6bf2f8e7696911d9d69c57559516ad1a7`

RIGHT_R2_UNCHANGED = YES · `c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0`

RIGHT_R1_UNCHANGED = YES · `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`

全部1513个受保护输入hash一致，两正式pointer未改动，右手approved mapping与Action未改动。
未进入双手、Web/glTF/Three.js、MIDI/fingering系统、钢琴安装或promotion。

**STOP — HUMAN REVIEW。**
