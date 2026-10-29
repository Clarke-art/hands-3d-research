# audits/minuet_stage_a_r2_natural_continuous_motion

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 共享root不固定为R1的分段路径，所有五指参与连续窗口。向量化FK经3组确定性静态输入与原FK逐点对比，误差小于1e−12m。目标XY从键真实面派生，并作为受键内边界约束的通用接触变量；没有D5/G5/G4姿态分支、逐音世界坐标表或改指法。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_a_r2_natural_continuous_motion/IMPLEMENTATION_REPORT.md)

> |Q1 核心原因|先固定root再逐指追键；独立phase切换重新取中性目标、缺少导数约束；提前回迁未受持键约束；旧max压掉同键重奏。CONFIRMED/SUPPORTED/UNKNOWN见因果报告。|

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_a_r2_natural_continuous_motion/IMPLEMENTATION_REPORT.md)

## 技术路线

> 全部新增在本独立审计目录。`coordinated_motion.py` 定义共享root平移/旋转、五指关节、键内接触点及相邻事件状态；`02_generate.py` 将这些状态作为同一带状最小二乘的未知量，明确加入按真实dt计算的速度/加速度约束。195个支撑时刻、5102个未知量；一份轨迹求解内部75次评估，达到上限，未再优化。16个相邻事件静态pose仅为该次求解初始化，不是16份动态候选，也不是人工逐音拟合；生成前另有3个有限静态测试。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_a_r2_natural_continuous_motion/IMPLEMENTATION_REPORT.md)

> 原R1代码、资产、视频与报告全部保留。唯一生成前修正是移除距精确事件支撑不足4ms的冗余非事件点，记录在 `PREGENERATION_SUPPORT_CONDITIONING.json`；音乐时刻未改，修正时动态候选为0。生成后没有调整规划模块、参数或指法；没有第二求解、逐帧补丁或第二动画。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_a_r2_natural_continuous_motion/IMPLEMENTATION_REPORT.md)

## 测试结论

> 全部新增在本独立审计目录。`coordinated_motion.py` 定义共享root平移/旋转、五指关节、键内接触点及相邻事件状态；`02_generate.py` 将这些状态作为同一带状最小二乘的未知量，明确加入按真实dt计算的速度/加速度约束。195个支撑时刻、5102个未知量；一份轨迹求解内部75次评估，达到上限，未再优化。16个相邻事件静态pose仅为该次求解初始化，不是16份动态候选，也不是人工逐音拟合；生成前另有3个有限静态测试。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_a_r2_natural_continuous_motion/IMPLEMENTATION_REPORT.md)

> |Q2 是否真正联合规划|是。root三维/必要旋转、五指关节、键内接触XY与相邻状态导数共同求解，不是只换平滑函数。|

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_a_r2_natural_continuous_motion/IMPLEMENTATION_REPORT.md)

## 失败原因与证据边界

> |Q1 核心原因|先固定root再逐指追键；独立phase切换重新取中性目标、缺少导数约束；提前回迁未受持键约束；旧max压掉同键重奏。CONFIRMED/SUPPORTED/UNKNOWN见因果报告。|

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_a_r2_natural_continuous_motion/IMPLEMENTATION_REPORT.md)

> |D 最高速度原因|3.625→3.633333s中指PIP从18.885°到4.905°，8.333ms变化13.98°，−1677.6°/s。下一E5准备从3.628568s进入，上一C5释放早在3.584283s结束，短恢复尚未达到中性角，进入准备后却使用中性pad目标。该分支切换的目标不连续且缺少按dt归一化速度/加速度约束。|CONFIRMED（数值、分支与时刻对应）；逐帧独立拟合放大突变为SUPPORTED；Rig限制造成峰值未获证实|

出处：[MOTION_TRANSITION_CAUSE_ANALYSIS.md](../research/audits/minuet_stage_a_r2_natural_continuous_motion/MOTION_TRANSITION_CAUSE_ANALYSIS.md)

## 后续建议

> |C 相邻手指准备|R1仅按各指独立100ms准备，active/release优先；准备起点重新取自然q的世界pad，而非前一个实际状态；root没有当前持键和下一指准备的联合任务。|CONFIRMED|

出处：[MOTION_TRANSITION_CAUSE_ANALYSIS.md](../research/audits/minuet_stage_a_r2_natural_continuous_motion/MOTION_TRANSITION_CAUSE_ANALYSIS.md)

> |D 最高速度原因|3.625→3.633333s中指PIP从18.885°到4.905°，8.333ms变化13.98°，−1677.6°/s。下一E5准备从3.628568s进入，上一C5释放早在3.584283s结束，短恢复尚未达到中性角，进入准备后却使用中性pad目标。该分支切换的目标不连续且缺少按dt归一化速度/加速度约束。|CONFIRMED（数值、分支与时刻对应）；逐帧独立拟合放大突变为SUPPORTED；Rig限制造成峰值未获证实|

出处：[MOTION_TRANSITION_CAUSE_ANALYSIS.md](../research/audits/minuet_stage_a_r2_natural_continuous_motion/MOTION_TRANSITION_CAUSE_ANALYSIS.md)

## 原报告与关键代码

- [audits/minuet_stage_a_r2_natural_continuous_motion/IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_a_r2_natural_continuous_motion/IMPLEMENTATION_REPORT.md)
- [audits/minuet_stage_a_r2_natural_continuous_motion/MOTION_TRANSITION_CAUSE_ANALYSIS.md](../research/audits/minuet_stage_a_r2_natural_continuous_motion/MOTION_TRANSITION_CAUSE_ANALYSIS.md)
- [audits/minuet_stage_a_r2_natural_continuous_motion/COORDINATED_MOTION_DESIGN.md](../research/audits/minuet_stage_a_r2_natural_continuous_motion/COORDINATED_MOTION_DESIGN.md)
- [audits/minuet_stage_a_r2_natural_continuous_motion/BEFORE_AFTER_MOTION_REVIEW.md](../research/audits/minuet_stage_a_r2_natural_continuous_motion/BEFORE_AFTER_MOTION_REVIEW.md)
- [audits/minuet_stage_a_r2_natural_continuous_motion/00_cause.py](../../src/legacy/audits/minuet_stage_a_r2_natural_continuous_motion/00_cause.py)
- [audits/minuet_stage_a_r2_natural_continuous_motion/01_preflight.py](../../src/legacy/audits/minuet_stage_a_r2_natural_continuous_motion/01_preflight.py)
- [audits/minuet_stage_a_r2_natural_continuous_motion/02_generate.py](../../src/legacy/audits/minuet_stage_a_r2_natural_continuous_motion/02_generate.py)
- [audits/minuet_stage_a_r2_natural_continuous_motion/03_scene.py](../../src/legacy/audits/minuet_stage_a_r2_natural_continuous_motion/03_scene.py)
- [audits/minuet_stage_a_r2_natural_continuous_motion/04_diagnostics.py](../../src/legacy/audits/minuet_stage_a_r2_natural_continuous_motion/04_diagnostics.py)
- [audits/minuet_stage_a_r2_natural_continuous_motion/05_render.py](../../src/legacy/audits/minuet_stage_a_r2_natural_continuous_motion/05_render.py)
- [audits/minuet_stage_a_r2_natural_continuous_motion/07_media.py](../../src/legacy/audits/minuet_stage_a_r2_natural_continuous_motion/07_media.py)
- [audits/minuet_stage_a_r2_natural_continuous_motion/08_comparison_media.py](../../src/legacy/audits/minuet_stage_a_r2_natural_continuous_motion/08_comparison_media.py)
- [audits/minuet_stage_a_r2_natural_continuous_motion/09_verification.py](../../src/legacy/audits/minuet_stage_a_r2_natural_continuous_motion/09_verification.py)
- [audits/minuet_stage_a_r2_natural_continuous_motion/10_camera_verify.py](../../src/legacy/audits/minuet_stage_a_r2_natural_continuous_motion/10_camera_verify.py)
- [audits/minuet_stage_a_r2_natural_continuous_motion/11_finish.py](../../src/legacy/audits/minuet_stage_a_r2_natural_continuous_motion/11_finish.py)
- [audits/minuet_stage_a_r2_natural_continuous_motion/coordinated_motion.py](../../src/legacy/audits/minuet_stage_a_r2_natural_continuous_motion/coordinated_motion.py)

## 输入、输出与大型证据

该目录原始成员 82 项；拟公开身份记录 70 项。
- `audits/minuet_stage_a_r2_natural_continuous_motion/evaluated.npz` → `hands-research-r1-selected-002.zip` / `payload/audits/minuet_stage_a_r2_natural_continuous_motion/evaluated.npz`
- `audits/minuet_stage_a_r2_natural_continuous_motion/STAGE_A_R2_COORDINATED_RIGHT_DESIGN_ONLY.blend` → `hands-research-r1-selected-002.zip` / `payload/audits/minuet_stage_a_r2_natural_continuous_motion/STAGE_A_R2_COORDINATED_RIGHT_DESIGN_ONLY.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
