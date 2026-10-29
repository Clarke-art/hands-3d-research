# audits/minuet_stage_b_r1_left_hand_triad_coordination

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> **READY_FOR_HUMAN_REVIEW · STOP — HUMAN REVIEW。** 真正新增同手多目标同时接触任务，原三音、原时值及DESIGN_PROVISIONAL指法不变；自然度Human待审。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r1_left_hand_triad_coordination/IMPLEMENTATION_REPORT.md)

> 所有新增文件在本独立目录。`left_chord_motion.py` 是Stage A R2联合规划模块的受控适配：使用左手自身rest/轴/marker/root及L1/L2自然关节参考；显式并发目标集合和同指重叠冲突校验；三指静态与动态目标均在共同root问题中成立；两闲指使用既有左手idle域；释放覆盖70ms并增加渐进恢复及首尾准备约束。没有镜像右手轨迹、固定原D2/D3目标或修改任何Rig结构。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r1_left_hand_triad_coordination/IMPLEMENTATION_REPORT.md)

## 技术路线

> `03_generate.py` 复用Stage A带状状态/接触/速度/加速度求解，将全部同时任务一起初始化和求解。31个支撑、812未知量、233输出采样；一次联合动态轨迹求解在19次评估后成功终止。8个通用阶段初值均联合所有当时手指，不是三段单指动画。3个静态预检及未保存Blender静态回读发生在动态候选前，0个静态Action/0保存blend。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r1_left_hand_triad_coordination/IMPLEMENTATION_REPORT.md)

> `07_audio.py` 使用既有冻结Grand映射、音量/velocity、pitchRatio、NOTE_OFF release与PCM方法，仅绑定本三音输入。3voices，没有改MIDI或声音事件。三原速媒体全解码通过；三根键使用相同原事件压力，非目标键不动。完整左手所有实际顶点跨233采样均在正常三视角内。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r1_left_hand_triad_coordination/IMPLEMENTATION_REPORT.md)

## 测试结论

> `03_generate.py` 复用Stage A带状状态/接触/速度/加速度求解，将全部同时任务一起初始化和求解。31个支撑、812未知量、233输出采样；一次联合动态轨迹求解在19次评估后成功终止。8个通用阶段初值均联合所有当时手指，不是三段单指动画。3个静态预检及未保存Blender静态回读发生在动态候选前，0个静态Action/0保存blend。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r1_left_hand_triad_coordination/IMPLEMENTATION_REPORT.md)

> |Q5 三指都达键吗|技术检查支持：三主动skin marker均在目标可奏区域，最大间隙约1.51/0.87/1.47mm，且各有独立关节按压与真实下沉位移；自然视觉结论仍待Human。|

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r1_left_hand_triad_coordination/IMPLEMENTATION_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 生成前修正过CLI3.12 SciPy与Blender3.13FK读取的导入边界，未改求解参数。后续修正过新审核服务继承的旧端口，使用8872；这是交付服务，不改变候选/音频。Stage A R2任何文件都未改。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r1_left_hand_triad_coordination/IMPLEMENTATION_REPORT.md)

> |Q12 进入下一阶段吗|本实例技术结果支持后续讨论，但当前等待Human实际观看后决定；本轮没有启动左手连续伴奏、双手或完整Stage B。|

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r1_left_hand_triad_coordination/IMPLEMENTATION_REPORT.md)

## 原报告与关键代码

- [audits/minuet_stage_b_r1_left_hand_triad_coordination/IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r1_left_hand_triad_coordination/IMPLEMENTATION_REPORT.md)
- [audits/minuet_stage_b_r1_left_hand_triad_coordination/LEFT_HAND_MULTI_CONTACT_FEASIBILITY.md](../research/audits/minuet_stage_b_r1_left_hand_triad_coordination/LEFT_HAND_MULTI_CONTACT_FEASIBILITY.md)
- [audits/minuet_stage_b_r1_left_hand_triad_coordination/LEFT_TRIAD_MIDI_AND_FINGERING.md](../research/audits/minuet_stage_b_r1_left_hand_triad_coordination/LEFT_TRIAD_MIDI_AND_FINGERING.md)
- [audits/minuet_stage_b_r1_left_hand_triad_coordination/TRIAD_CONTACT_AND_NATURALNESS_REVIEW.md](../research/audits/minuet_stage_b_r1_left_hand_triad_coordination/TRIAD_CONTACT_AND_NATURALNESS_REVIEW.md)
- [audits/minuet_stage_b_r1_left_hand_triad_coordination/LEFT_TRIAD_COORDINATED_PLANNING_DESIGN.md](../research/audits/minuet_stage_b_r1_left_hand_triad_coordination/LEFT_TRIAD_COORDINATED_PLANNING_DESIGN.md)
- [audits/minuet_stage_b_r1_left_hand_triad_coordination/00_scope_and_protect.py](../../src/legacy/audits/minuet_stage_b_r1_left_hand_triad_coordination/00_scope_and_protect.py)
- [audits/minuet_stage_b_r1_left_hand_triad_coordination/01_feasibility.py](../../src/legacy/audits/minuet_stage_b_r1_left_hand_triad_coordination/01_feasibility.py)
- [audits/minuet_stage_b_r1_left_hand_triad_coordination/02_static_readback.py](../../src/legacy/audits/minuet_stage_b_r1_left_hand_triad_coordination/02_static_readback.py)
- [audits/minuet_stage_b_r1_left_hand_triad_coordination/03_generate.py](../../src/legacy/audits/minuet_stage_b_r1_left_hand_triad_coordination/03_generate.py)
- [audits/minuet_stage_b_r1_left_hand_triad_coordination/04_scene.py](../../src/legacy/audits/minuet_stage_b_r1_left_hand_triad_coordination/04_scene.py)
- [audits/minuet_stage_b_r1_left_hand_triad_coordination/05_diagnostics.py](../../src/legacy/audits/minuet_stage_b_r1_left_hand_triad_coordination/05_diagnostics.py)
- [audits/minuet_stage_b_r1_left_hand_triad_coordination/06_render.py](../../src/legacy/audits/minuet_stage_b_r1_left_hand_triad_coordination/06_render.py)
- [audits/minuet_stage_b_r1_left_hand_triad_coordination/07_audio.py](../../src/legacy/audits/minuet_stage_b_r1_left_hand_triad_coordination/07_audio.py)
- [audits/minuet_stage_b_r1_left_hand_triad_coordination/08_media.py](../../src/legacy/audits/minuet_stage_b_r1_left_hand_triad_coordination/08_media.py)
- [audits/minuet_stage_b_r1_left_hand_triad_coordination/09_framing_verify.py](../../src/legacy/audits/minuet_stage_b_r1_left_hand_triad_coordination/09_framing_verify.py)
- [audits/minuet_stage_b_r1_left_hand_triad_coordination/10_verify.py](../../src/legacy/audits/minuet_stage_b_r1_left_hand_triad_coordination/10_verify.py)
- [audits/minuet_stage_b_r1_left_hand_triad_coordination/11_finish.py](../../src/legacy/audits/minuet_stage_b_r1_left_hand_triad_coordination/11_finish.py)

## 输入、输出与大型证据

该目录原始成员 78 项；拟公开身份记录 66 项。
- `audits/minuet_stage_b_r1_left_hand_triad_coordination/evaluated.npz` → `hands-research-r1-selected-002.zip` / `payload/audits/minuet_stage_b_r1_left_hand_triad_coordination/evaluated.npz`
- `audits/minuet_stage_b_r1_left_hand_triad_coordination/STAGE_B_LEFT_TRIAD_DESIGN_ONLY_R1.blend` → `hands-research-r1-selected-002.zip` / `payload/audits/minuet_stage_b_r1_left_hand_triad_coordination/STAGE_B_LEFT_TRIAD_DESIGN_ONLY_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
