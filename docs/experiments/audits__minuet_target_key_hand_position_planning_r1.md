# audits/minuet_target_key_hand_position_planning_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 全部新增文件位于本审计目录。`target_key_planner.py` 增加真实键几何定位、按候选指号的共同掌位分段、连续root轨迹与运动键面目标；`02_generate.py` 局部复用既有FK/关节轴，用固定策略生成连续目标适配；`03_scene.py` 克隆批准R1场景并烘焙两个右手Action与8个目标键Action；音频复用现有Grand采样链。未改现有正式运动入口、原键/声runtime、冻结blend、mesh、rest、weights、drivers、键网格或静态姿态。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_target_key_hand_position_planning_r1/IMPLEMENTATION_REPORT.md)

> |1 新目标键自动定位|定位接口PASS；实际触键FAIL|8音高均从真实键表定位，包含F♯5；不是逐音坐标。多个白键触键不达标。|

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_target_key_hand_position_planning_r1/IMPLEMENTATION_REPORT.md)

## 技术路线

> **交付状态：通用接口已实现，Stage A动态质量 FAIL。** 一份右手短句候选和三个原速视角已经生成；不提升为产品演奏入口，不宣称自动指法规划。达到ONE NEW CANDIDATE ONLY后停止，不无限调参。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_target_key_hand_position_planning_r1/IMPLEMENTATION_REPORT.md)

> 全部新增文件位于本审计目录。`target_key_planner.py` 增加真实键几何定位、按候选指号的共同掌位分段、连续root轨迹与运动键面目标；`02_generate.py` 局部复用既有FK/关节轴，用固定策略生成连续目标适配；`03_scene.py` 克隆批准R1场景并烘焙两个右手Action与8个目标键Action；音频复用现有Grand采样链。未改现有正式运动入口、原键/声runtime、冻结blend、mesh、rest、weights、drivers、键网格或静态姿态。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_target_key_hand_position_planning_r1/IMPLEMENTATION_REPORT.md)

## 测试结论

> **交付状态：通用接口已实现，Stage A动态质量 FAIL。** 一份右手短句候选和三个原速视角已经生成；不提升为产品演奏入口，不宣称自动指法规划。达到ONE NEW CANDIDATE ONLY后停止，不无限调参。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_target_key_hand_position_planning_r1/IMPLEMENTATION_REPORT.md)

> |1 新目标键自动定位|定位接口PASS；实际触键FAIL|8音高均从真实键表定位，包含F♯5；不是逐音坐标。多个白键触键不达标。|

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_target_key_hand_position_planning_r1/IMPLEMENTATION_REPORT.md)

## 失败原因与证据边界

> 工程门槛筛出12/16音符在某些采样接触失败；少数轻微不可见差异可WARN，但明确可见D5/G5阻断。只用32个代表性skin点的有限接触邻域/掌部屏幕：最大采样穿入约5.68毫米（R10期间E5），不是完整三角碰撞或逐顶点forensic结论，不进行按点修补。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_target_key_hand_position_planning_r1/IMPLEMENTATION_REPORT.md)

> 有限回读诊断：D5小指持键最大间隙约9.4毫米；G5最大竖直间隙约21.5毫米、水平出界约17.9毫米；全部16音符中12个至少有采样未满足原工程接触门槛。某些4毫米误差是否明显可由Human判断，但D5与G5的可见悬空已经足以阻断，无须把所有微小误差都升格。

出处：[HUMAN_VISIBLE_REVIEW.md](../research/audits/minuet_target_key_hand_position_planning_r1/HUMAN_VISIBLE_REVIEW.md)

## 后续建议

> 下一步局部架构修改应将“中性pad区间→固定root→独立指节”改为相邻事件窗口中的root与指节联合可达约束，显式检查下沉目标与跨界释放/接近条件。并独立定义同键重触的机械阶段仲裁，保留MIDI音乐事件。该建议不要求重建Rig、完整IK架构、物理引擎或手部资产；本轮不执行第二动态候选。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_target_key_hand_position_planning_r1/IMPLEMENTATION_REPORT.md)

> 没有进行参数搜索、改指、逐音手修或第二候选。下一步应修改接触可达约束下的root/关节联合规划与同键重触仲裁，不能继续无限调root/DIP。

出处：[HUMAN_VISIBLE_REVIEW.md](../research/audits/minuet_target_key_hand_position_planning_r1/HUMAN_VISIBLE_REVIEW.md)

## 原报告与关键代码

- [audits/minuet_target_key_hand_position_planning_r1/IMPLEMENTATION_REPORT.md](../research/audits/minuet_target_key_hand_position_planning_r1/IMPLEMENTATION_REPORT.md)
- [audits/minuet_target_key_hand_position_planning_r1/HUMAN_VISIBLE_REVIEW.md](../research/audits/minuet_target_key_hand_position_planning_r1/HUMAN_VISIBLE_REVIEW.md)
- [audits/minuet_target_key_hand_position_planning_r1/FINGERING_AND_EVENT_SCOPE.md](../research/audits/minuet_target_key_hand_position_planning_r1/FINGERING_AND_EVENT_SCOPE.md)
- [audits/minuet_target_key_hand_position_planning_r1/TARGET_KEY_PLANNING_DESIGN.md](../research/audits/minuet_target_key_hand_position_planning_r1/TARGET_KEY_PLANNING_DESIGN.md)
- [audits/minuet_target_key_hand_position_planning_r1/00_scope.py](../../src/legacy/audits/minuet_target_key_hand_position_planning_r1/00_scope.py)
- [audits/minuet_target_key_hand_position_planning_r1/01_plan.py](../../src/legacy/audits/minuet_target_key_hand_position_planning_r1/01_plan.py)
- [audits/minuet_target_key_hand_position_planning_r1/02_generate.py](../../src/legacy/audits/minuet_target_key_hand_position_planning_r1/02_generate.py)
- [audits/minuet_target_key_hand_position_planning_r1/03_scene.py](../../src/legacy/audits/minuet_target_key_hand_position_planning_r1/03_scene.py)
- [audits/minuet_target_key_hand_position_planning_r1/04_diagnostics.py](../../src/legacy/audits/minuet_target_key_hand_position_planning_r1/04_diagnostics.py)
- [audits/minuet_target_key_hand_position_planning_r1/05_render.py](../../src/legacy/audits/minuet_target_key_hand_position_planning_r1/05_render.py)
- [audits/minuet_target_key_hand_position_planning_r1/06_audio.py](../../src/legacy/audits/minuet_target_key_hand_position_planning_r1/06_audio.py)
- [audits/minuet_target_key_hand_position_planning_r1/07_media.py](../../src/legacy/audits/minuet_target_key_hand_position_planning_r1/07_media.py)
- [audits/minuet_target_key_hand_position_planning_r1/08_finish.py](../../src/legacy/audits/minuet_target_key_hand_position_planning_r1/08_finish.py)
- [audits/minuet_target_key_hand_position_planning_r1/09_interface_checks.py](../../src/legacy/audits/minuet_target_key_hand_position_planning_r1/09_interface_checks.py)
- [audits/minuet_target_key_hand_position_planning_r1/scene_import_repair.py](../../src/legacy/audits/minuet_target_key_hand_position_planning_r1/scene_import_repair.py)
- [audits/minuet_target_key_hand_position_planning_r1/stage_common.py](../../src/legacy/audits/minuet_target_key_hand_position_planning_r1/stage_common.py)

## 输入、输出与大型证据

该目录原始成员 60 项；拟公开身份记录 44 项。
- `audits/minuet_target_key_hand_position_planning_r1/evaluated.npz` → `hands-research-r1-selected-004.zip` / `payload/audits/minuet_target_key_hand_position_planning_r1/evaluated.npz`
- `audits/minuet_target_key_hand_position_planning_r1/STAGE_A_RIGHT_TARGET_KEY_DESIGN_PROVISIONAL_R1.blend` → `hands-research-r1-selected-004.zip` / `payload/audits/minuet_target_key_hand_position_planning_r1/STAGE_A_RIGHT_TARGET_KEY_DESIGN_PROVISIONAL_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
