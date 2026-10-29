# Stage 1A · AI 多视角可行性测试结果 R1

日期：2026-09-27  
状态：`AI_MULTIVIEW_RESULT = READY_FOR_HUMAN_REVIEW`  
本轮结论：**`AI_MULTIVIEW_FEASIBILITY = FAIL`**（针对本轮内置 imagegen 的 Anchor＋参考图编辑派生路线）

## 1. 实际执行

按 `STAGE1_AI_MULTIVIEW_FEASIBILITY_PLAN_R1.md`，用内置 `image_gen` 生成 A01；因四指近伸直，使用 A01 做定向姿态编辑得到 A02；以 A02 为主参考，并逐步加入已有视角图，派生 DORSAL、PALMAR、RADIAL、ULNAR 各一张。随后执行 `AI_MULTIVIEW_QC`。四视角预检未通过，**未**继续生成 DISTAL、PROXIMAL、两张斜视图。

所有图均为 1024 × 1536 PNG 候选，仅作为本次判定证据；文件名中的 `PRECHECK` 不代表正式批准。生成依赖、提示词约束摘要见 `references/hand_r_canonical_ai/qc/GENERATION_LOG_R1.md`。

| 轮次 | 文件 | 评审 |
| --- | --- | --- |
| Anchor A01 | `references/hand_r_canonical_ai/anchor/ANCHOR_A01_REJECT_NEAR_EXTENDED.png` | 淘汰。右手、背景与五指分离基本成立，但四指从掌指到指尖看起来接近伸直，缺少可确认的 RSSF 半屈曲。 |
| Anchor A02 | `references/hand_r_canonical_ai/anchor/ANCHOR_A02_PRECHECK.png` | 可用于预检。关节屈曲较清楚，右手/五指/虎口可读；拇指离掌平面角度、前臂“短”的尺度仍需核查，不能当正式母版。 |
| DORSAL D01 | `references/hand_r_canonical_ai/candidate_views/DORSAL_D01_PRECHECK.png` | 手背和指甲可见、手别正确；相对 A02 弯曲程度减弱，指尖更趋直。 |
| PALMAR P01 | `references/hand_r_canonical_ai/candidate_views/PALMAR_P01_PRECHECK.png` | 掌心侧别和右手镜像方向看似正确；四指几乎伸直，指间张开、虎口和掌宽外形相对 A02/D01 有明显变化。它不是可信的固定 RSSF 姿态反面视角。 |
| RADIAL R01 | `references/hand_r_canonical_ai/candidate_views/RADIAL_R01_PRECHECK.png` | 拇指侧大致可读；拇指相对尺寸、指尖深度排列和弯曲趋势不能与正面图可靠闭合；侧面轮廓未提供可验证的同一几何证据。 |
| ULNAR U01 | `references/hand_r_canonical_ai/candidate_views/ULNAR_U01_PRECHECK.png` | 小指侧大致可读；可见指的弯曲程度与 R01 / P01 明显不一致，拇指后景与前臂轮廓只能作粗略侧别判断。 |

## 2. 四视角 QC 记录

等级定义：`P` 可接受、`C` 存疑、`F` 明显冲突、`NV` 无法验证。这里记录的是**跨图**判断，不是单图美观评分。

| 维度 | 评级 | 可见证据与限制 |
| --- | --- | --- |
| A 主体身份一致性 | **F** | A02/D01 有相似肤色与指甲，但 P01 的掌部外形、虎口开口、指尖形状与姿态一起重造；R01/U01 的侧面轮廓没有稳定锁定同一手指几何。不能据肤色相近断言同一只手。 |
| B 结构比例一致性 | **F** | P01 掌宽与四指根部的视觉关系相对 A02/D01 改变，拇指张开外形也变；R01 的拇指相对体量与正面图缺乏可信对应。跨正侧面的精确比例因无相机参数无法量化，但明显重造足以否定通过。 |
| C 姿态一致性 | **F** | A02 明显半屈曲，D01 较直，P01 近伸直，R01/U01 又呈不同的侧面屈曲。相机环绕不能使同一固定手的关节角实际改变；这是决定性失败。二维图也无法精确验证冻结角度数值。 |
| D 视角正确性 | **C** | DORSAL/PALMAR 表面类型可区分，正反面拇指图像侧别也大致正确；RADIAL/ULNAR 大致是对侧轮廓。缺少相机外参，无法确认严格正交或是否有额外手体旋转。后四个强制视角未测试。 |
| E 背景与光照 | **C / NV** | 浅灰背景与柔光风格基本相近；不同视角的皮肤明暗可能属于重新布光或模型再绘制。没有固定世界光源参数，`LIGHT = FIXED` 不能被证明。 |
| F Hunyuan3D 输入适配性 | **C** | 图像大体清晰、主体分离、背景干净；侧视角五指自然有遮挡，前臂截断接近图像底边，且关键几何矛盾使整套图不适合作为同一对象的多视角输入。此处只是图像适配预检，未提交 Hunyuan3D。 |

另有独立的文件体积问题：四张视角候选 PNG 合计原始 **7,164,742 bytes**，逐文件 Base64 编码后合计 **9,552,992 bytes**。四张就已高于冻结规范中的原始总量约 6 MB 工程目标和 Base64 总量 8 MB 硬约束；未来即便几何问题解决，也需先降分辨率、再考虑高质量 JPG，且保留完整八视角。此项不作为本轮主要失败理由，不能靠压缩修复姿态冲突。

**决定性比较**：A02/D01 ↔ P01 的半屈曲与张开度变化；P01 ↔ R01/U01 的关节轮廓不一致。单张图各自看起来像手，无法消除这些互相矛盾的证据。工具也没有提供共享的 3D 表示、相机位姿或固定灯光设置，故“仅移动相机”只是提示词要求，不是已实现的约束。

## 3. 判定与路线建议

四视角阶段的 A/B/C 关键项均为 `F`，依据 `STAGE1_AI_MULTIVIEW_QC_SPEC_R1.md` §4 判 `FAIL`。本轮不能将这些候选作为正式参考图包，也不能用它们替代真人拍摄图进入 Stage 2。

**不推荐继续沿用当前“单张 Anchor + 通用图像编辑逐视角派生”的路线**来制作正式包。若未来另开 AI 路线验证，应首先取得能锁定共享几何、关节姿态、相机外参和世界光照的生成/渲染机制，并从同一固定主体导出八个视角，再重复本规范的人工 QC；这属于新一轮方案，不是本轮的继续执行或批准。现有冻结 Stage 0 文档对正式采集来源的要求仍有效，本次可行性测试没有修改它们。

## 4. 文件与停止状态

- 已保存：2 张 Anchor（A01 淘汰、A02 预检）；4 张候选视角（均未批准）；1 份生成日志。
- 未生成：DISTAL、PROXIMAL、DORSAL_OBLIQUE_RADIAL、DORSAL_OBLIQUE_ULNAR；因此无正式 `8_VIEWS` 参考包。
- 未调用 Hunyuan3D；未启动 Blender；未制作 mesh、Rig、动画或 Three.js。
- 未评定或关闭 `REFERENCE_ACQUISITION_GATE`；仍需人工审核。

```text
AI_MULTIVIEW_PLAN = READY
AI_MULTIVIEW_QC_SPEC = READY
AI_MULTIVIEW_RESULT = READY_FOR_HUMAN_REVIEW
AI_MULTIVIEW_FEASIBILITY = FAIL
REFERENCE_ACQUISITION_GATE = STILL_BLOCKED
REASON = NO_APPROVED_FINAL_REFERENCE_PACK_YET
```
