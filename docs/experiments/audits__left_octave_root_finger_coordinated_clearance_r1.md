# audits/left_octave_root_finger_coordinated_clearance_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 实现bug修复：近零参数的相对差分被Blender float32吞掉，root侧移、小指和三闲置指几何导数为零。只读DERIVATIVE_PRECISION_CHECK_R1.json实际复现。首次启动在结果/blend生成前中止；仅改为有界绝对差分，保持原政策SHA、范围、目标、权重、seed与max_nfev。修复启动不是第二候选，未比较选优。完整记录见IMPLEMENTATION_REPAIR_R1.json。

出处：[LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT.md](../research/audits/left_octave_root_finger_coordinated_clearance_r1/LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT.md)

> 实现bug修复补充：第一次差分修复后的输出使用了未激活静态场景的单位root矩阵，丢失原生绑定。首帧与来源正确矩阵最大元素差1.980873823，画面手部离开视野，故无效且不用于候选选优。修复改为已求值的来源动态场景frame1 root，并在求解前及保存重开时断言与来源矩阵相同。两个无效实现启动完整记录于IMPLEMENTATION_REPAIR_R1.json；只保留一份最终候选路径，政策/seed/范围/目标/权重/max_nfev不变，未生成第二套运动方案。

出处：[LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT.md](../research/audits/left_octave_root_finger_coordinated_clearance_r1/LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT.md)

## 技术路线

> 继承 root-path conflict / supported、contact-clearance tradeoff / confirmed、left dynamic not-approved。没有重新求解或覆盖历史证据。先锁定唯一政策及脚本 SHA；一个 29 参数联合运动问题，覆盖 D2→D3→D2 全段原时间轴，没有 root 后补或逐指局部补丁。

出处：[LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT.md](../research/audits/left_octave_root_finger_coordinated_clearance_r1/LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT.md)

> 政策 SHA `f6b56554716e0b34c27ad761cc8bd4833729530f0bc24b891f8c2e3eedd250ff`。XYZ 偏移范围 x±2、y[-5,0]、z[-3.5,0]mm；腕部仅继承 world-X pitch[-2,0]°，yaw/roll不变。x自由度是本轮求解前声明的有限工程假设：已有E2侧面浅退出距离支持测试侧向避让，同时主动指在真实键面中补偿。未根据结果扩域。小指/拇指继承RSSＦ工程域及锚点±12°、压力上界0.5°余量；闲置三指分别仅允许批准曲度±4°，base spread保持。所有范围不是人体生理极限。

出处：[LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT.md](../research/audits/left_octave_root_finger_coordinated_clearance_r1/LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT.md)

## 测试结论

> **FINAL_STATUS = COORDINATED_CLEARANCE_FAIL_CLOSED**。一个完整共享 root＋主动指＋闲置指协调候选；Human approval=false。

出处：[LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT.md](../research/audits/left_octave_root_finger_coordinated_clearance_r1/LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT.md)

> |n01 / D2小指|3.524178|3.541024|FAIL|

出处：[LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT.md](../research/audits/left_octave_root_finger_coordinated_clearance_r1/LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/left_octave_root_finger_coordinated_clearance_r1/LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT.md](../research/audits/left_octave_root_finger_coordinated_clearance_r1/LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT.md)
- [audits/left_octave_root_finger_coordinated_clearance_r1/00_lock.py](../../src/legacy/audits/left_octave_root_finger_coordinated_clearance_r1/00_lock.py)
- [audits/left_octave_root_finger_coordinated_clearance_r1/01_coordinate.py](../../src/legacy/audits/left_octave_root_finger_coordinated_clearance_r1/01_coordinate.py)
- [audits/left_octave_root_finger_coordinated_clearance_r1/02_verify_render.py](../../src/legacy/audits/left_octave_root_finger_coordinated_clearance_r1/02_verify_render.py)
- [audits/left_octave_root_finger_coordinated_clearance_r1/03_measure.py](../../src/legacy/audits/left_octave_root_finger_coordinated_clearance_r1/03_measure.py)
- [audits/left_octave_root_finger_coordinated_clearance_r1/04_media.py](../../src/legacy/audits/left_octave_root_finger_coordinated_clearance_r1/04_media.py)
- [audits/left_octave_root_finger_coordinated_clearance_r1/05_finish.py](../../src/legacy/audits/left_octave_root_finger_coordinated_clearance_r1/05_finish.py)
- [audits/left_octave_root_finger_coordinated_clearance_r1/check_derivative_precision.py](../../src/legacy/audits/left_octave_root_finger_coordinated_clearance_r1/check_derivative_precision.py)
- [audits/left_octave_root_finger_coordinated_clearance_r1/prepare_review_checks.py](../../src/legacy/audits/left_octave_root_finger_coordinated_clearance_r1/prepare_review_checks.py)
- [audits/left_octave_root_finger_coordinated_clearance_r1/record_bind_repair.py](../../src/legacy/audits/left_octave_root_finger_coordinated_clearance_r1/record_bind_repair.py)
- [audits/left_octave_root_finger_coordinated_clearance_r1/record_implementation_repair.py](../../src/legacy/audits/left_octave_root_finger_coordinated_clearance_r1/record_implementation_repair.py)
- [audits/left_octave_root_finger_coordinated_clearance_r1/record_visual_precheck.py](../../src/legacy/audits/left_octave_root_finger_coordinated_clearance_r1/record_visual_precheck.py)

## 输入、输出与大型证据

该目录原始成员 64 项；拟公开身份记录 53 项。
- `audits/left_octave_root_finger_coordinated_clearance_r1/evaluated_coordinated.npz` → `hands-research-r1-selected-001-r1a.zip` / `payload/audits/left_octave_root_finger_coordinated_clearance_r1/evaluated_coordinated.npz`
- `audits/left_octave_root_finger_coordinated_clearance_r1/LEFT_OCTAVE_COORDINATED_CLEARANCE_CANDIDATE_R1.blend` → `hands-research-r1-selected-001-r1a.zip` / `payload/audits/left_octave_root_finger_coordinated_clearance_r1/LEFT_OCTAVE_COORDINATED_CLEARANCE_CANDIDATE_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
