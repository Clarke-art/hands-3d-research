# experiments/hands_role_aware_collision_avoidance_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 精确窗口长**0.788571秒**。F♯5后35ms完整下行落在窗口内；窗口结束仍为F♯5持键，不能把结束处当全手无任务。本轮未修复B01/B03，也未认证窗口外的F♯5释放。`正式范围`（链接见原报告）

出处：[BASELINE_AND_CAUSE.md](../research/experiments/hands_role_aware_collision_avoidance_r1/BASELINE_AND_CAUSE.md)

> 1. **为什么交叉？** 上行D5→E5使用4→3，原中/无名指相向横展和远端曲度将真实skin带入同一空间；接触点正确与关节曲线平滑没有保证独立指体分离。原A2任务只约束pad/关节代理，没有对应的连续指间避让通道。既有R4/root及轻量修正失败记录支持这一机制缺口，但没有证明蒙皮权重错误或冻结Rig不可行。

出处：[BASELINE_AND_CAUSE.md](../research/experiments/hands_role_aware_collision_avoidance_r1/BASELINE_AND_CAUSE.md)

## 技术路线

> 本轮读取AGENTS.md及三份路线复盘，使用原C1，不使用C01或G4→E5实验动作。C1 SHA256仍为`d8e0f5a…e51a7`；正式MIDI、23音指法和事件身份均保持。通过实际MIDI的tempo/tick独立换算核对46个事件时刻，最大误差低于1e-10秒，未以报告近似时间生成输入。`MIDI精确时钟`（链接见原报告）

出处：[BASELINE_AND_CAUSE.md](../research/experiments/hands_role_aware_collision_avoidance_r1/BASELINE_AND_CAUSE.md)

> - 前方准备点采用可奏面相对纵深30%及键中心，由事件和几何推导，不是音名角度补丁；但此单一前方策略未验证能容纳非拇指逆序交接。

出处：[BASELINE_AND_CAUSE.md](../research/experiments/hands_role_aware_collision_avoidance_r1/BASELINE_AND_CAUSE.md)

## 测试结论

> **FAIL — STOP — HUMAN REVIEW**

出处：[BASELINE_AND_CAUSE.md](../research/experiments/hands_role_aware_collision_avoidance_r1/BASELINE_AND_CAUSE.md)

> **HANDS_ROLE_AWARE_COLLISION_AVOIDANCE_R1：FAIL，失败发生在生成前预检。动态候选0；没有新Action、Blend或视频。**

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_collision_avoidance_r1/FINAL_HUMAN_REVIEW.md)

## 失败原因与证据边界

> `原因与覆盖边界`（链接见原报告）

出处：[BASELINE_AND_CAUSE.md](../research/experiments/hands_role_aware_collision_avoidance_r1/BASELINE_AND_CAUSE.md)

> 没有动态候选，故**新旧教学1×／俯视／侧斜对照、新原速自然度判断全部NOT_RUN**，不使用静态点或旧视频冒充新演奏。Human可审核失败原因和路线取舍；当前没有可供接受的新自然动作。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_collision_avoidance_r1/FINAL_HUMAN_REVIEW.md)

## 后续建议

> | 无名指下一F♯5准备窗开始 | 3.8128535 |

出处：[BASELINE_AND_CAUSE.md](../research/experiments/hands_role_aware_collision_avoidance_r1/BASELINE_AND_CAUSE.md)

> 若Human仍选择继续此小机制，下一项应是**接触左极限连续的释放/准备任务目标**：在OFF处保留原接触位置，利用现有A2释放包络连续过渡到一个有限避让门户，再与下一PREPARING通道合并。门户高度应由真实局部冲突见证决定，而非附近最高键面加整段最大半径；用更贴合远端形状的分段包络降低假不可行，但仍须真实skin验收。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_collision_avoidance_r1/FINAL_HUMAN_REVIEW.md)

## 原报告与关键代码

- [experiments/hands_role_aware_collision_avoidance_r1/BASELINE_AND_CAUSE.md](../research/experiments/hands_role_aware_collision_avoidance_r1/BASELINE_AND_CAUSE.md)
- [experiments/hands_role_aware_collision_avoidance_r1/FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_collision_avoidance_r1/FINAL_HUMAN_REVIEW.md)
- [experiments/hands_role_aware_collision_avoidance_r1/ROLE_AWARE_PLANNER_RESULT.md](../research/experiments/hands_role_aware_collision_avoidance_r1/ROLE_AWARE_PLANNER_RESULT.md)
- [experiments/hands_role_aware_collision_avoidance_r1/anchor_blender.py](../../src/legacy/experiments/hands_role_aware_collision_avoidance_r1/anchor_blender.py)
- [experiments/hands_role_aware_collision_avoidance_r1/baseline_blender.py](../../src/legacy/experiments/hands_role_aware_collision_avoidance_r1/baseline_blender.py)
- [experiments/hands_role_aware_collision_avoidance_r1/check_coordinate_adapter.py](../../src/legacy/experiments/hands_role_aware_collision_avoidance_r1/check_coordinate_adapter.py)
- [experiments/hands_role_aware_collision_avoidance_r1/prepare.py](../../src/legacy/experiments/hands_role_aware_collision_avoidance_r1/prepare.py)
- [experiments/hands_role_aware_collision_avoidance_r1/role_planner.py](../../src/legacy/experiments/hands_role_aware_collision_avoidance_r1/role_planner.py)
- [experiments/hands_role_aware_collision_avoidance_r1/runtime.py](../../src/legacy/experiments/hands_role_aware_collision_avoidance_r1/runtime.py)
- [experiments/hands_role_aware_collision_avoidance_r1/verify_static_blender.py](../../src/legacy/experiments/hands_role_aware_collision_avoidance_r1/verify_static_blender.py)
- [experiments/hands_role_aware_collision_avoidance_r1/verify_timing_and_close.py](../../src/legacy/experiments/hands_role_aware_collision_avoidance_r1/verify_timing_and_close.py)

## 输入、输出与大型证据

该目录原始成员 47 项；拟公开身份记录 36 项。
- `experiments/hands_role_aware_collision_avoidance_r1/BASELINE_ACTUAL.npz` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_role_aware_collision_avoidance_r1/BASELINE_ACTUAL.npz`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
