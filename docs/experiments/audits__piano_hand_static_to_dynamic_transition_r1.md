# audits/piano_hand_static_to_dynamic_transition_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 技术路线

> 实现错误修复：第一次保存的琴键父平移未正确抵消，已只读记录于 CONFIRMED_CODE_ERROR_R1.json；修复为显式逆pivot局部变换。第一次属性数组复制错误也已修复。动作NPZ/事前政策/优化control points完全不变，没有重跑solver或生成第二套轨迹。修复后实际运动键世界顶点逐120Hz与原规则最大差小于0.00002mm；旧错误画面已替换，所有最终素材绑定修复后唯一blend SHA。

出处：[PIANO_HAND_STATIC_TO_DYNAMIC_TRANSITION_R1_REPORT.md](../research/audits/piano_hand_static_to_dynamic_transition_r1/PIANO_HAND_STATIC_TO_DYNAMIC_TRANSITION_R1_REPORT.md)

## 测试结论

> **FINAL_STATUS = STATIC_TO_DYNAMIC_TRANSITION_FAIL_CLOSED**。这是 Agent 候选提交判断；动态 Human 批准仍为 false。

出处：[PIANO_HAND_STATIC_TO_DYNAMIC_TRANSITION_R1_REPORT.md](../research/audits/piano_hand_static_to_dynamic_transition_r1/PIANO_HAND_STATIC_TO_DYNAMIC_TRANSITION_R1_REPORT.md)

> R2 静态候选 SHA `18359b1c2c6e8abaa1a4444f342e7672a1f1fda35d96cc95146bc8d1161b551c`；唯一动态候选 SHA `664a0702637e7c3d7aef6b4ba260d8b464f87c9704aa2d4b56b8492d01492284`。四个原静态场景完整保留且保存重开内部状态完全一致。当前用户明确的静态 Human 批准覆盖旧报告 HUMAN_PENDING，只用于动作参考，不 Promotion。

出处：[PIANO_HAND_STATIC_TO_DYNAMIC_TRANSITION_R1_REPORT.md](../research/audits/piano_hand_static_to_dynamic_transition_r1/PIANO_HAND_STATIC_TO_DYNAMIC_TRANSITION_R1_REPORT.md)

## 失败原因与证据边界

> 本候选的明确阻断：左手小指两次D2按键起音端点合格，但下沉/持键/回弹阶段固定pad最高7.672mm、实际皮肤最高7.689mm，正常近景可见手指未持续跟随键面，属于已批准接触在动态阶段的重大可见回退。左拇指D3全过程接触通过（最大约1.000mm）；右中指F#5全过程接触通过（最大约0.710mm）。不能用右手成功抵消左手失败。

出处：[PIANO_HAND_STATIC_TO_DYNAMIC_TRANSITION_R1_REPORT.md](../research/audits/piano_hand_static_to_dynamic_transition_r1/PIANO_HAND_STATIC_TO_DYNAMIC_TRANSITION_R1_REPORT.md)

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/piano_hand_static_to_dynamic_transition_r1/PIANO_HAND_STATIC_TO_DYNAMIC_TRANSITION_R1_REPORT.md](../research/audits/piano_hand_static_to_dynamic_transition_r1/PIANO_HAND_STATIC_TO_DYNAMIC_TRANSITION_R1_REPORT.md)
- [audits/piano_hand_static_to_dynamic_transition_r1/00_lock.py](../../src/legacy/audits/piano_hand_static_to_dynamic_transition_r1/00_lock.py)
- [audits/piano_hand_static_to_dynamic_transition_r1/01_plan.py](../../src/legacy/audits/piano_hand_static_to_dynamic_transition_r1/01_plan.py)
- [audits/piano_hand_static_to_dynamic_transition_r1/02_scene_verify.py](../../src/legacy/audits/piano_hand_static_to_dynamic_transition_r1/02_scene_verify.py)
- [audits/piano_hand_static_to_dynamic_transition_r1/03_measure.py](../../src/legacy/audits/piano_hand_static_to_dynamic_transition_r1/03_measure.py)
- [audits/piano_hand_static_to_dynamic_transition_r1/04_render.py](../../src/legacy/audits/piano_hand_static_to_dynamic_transition_r1/04_render.py)
- [audits/piano_hand_static_to_dynamic_transition_r1/05_media.py](../../src/legacy/audits/piano_hand_static_to_dynamic_transition_r1/05_media.py)
- [audits/piano_hand_static_to_dynamic_transition_r1/06_finish.py](../../src/legacy/audits/piano_hand_static_to_dynamic_transition_r1/06_finish.py)
- [audits/piano_hand_static_to_dynamic_transition_r1/common.py](../../src/legacy/audits/piano_hand_static_to_dynamic_transition_r1/common.py)
- [audits/piano_hand_static_to_dynamic_transition_r1/probe_key_transform.py](../../src/legacy/audits/piano_hand_static_to_dynamic_transition_r1/probe_key_transform.py)
- [audits/piano_hand_static_to_dynamic_transition_r1/record_precheck.py](../../src/legacy/audits/piano_hand_static_to_dynamic_transition_r1/record_precheck.py)

## 输入、输出与大型证据

该目录原始成员 51 项；拟公开身份记录 49 项。
- `audits/piano_hand_static_to_dynamic_transition_r1/evaluated_temporal_candidate.npz` → `hands-research-r1-selected-006.zip` / `payload/audits/piano_hand_static_to_dynamic_transition_r1/evaluated_temporal_candidate.npz`
- `audits/piano_hand_static_to_dynamic_transition_r1/EVIDENCE_DYNAMIC_CONTACT_R1.png` → `hands-research-r1-selected-006.zip` / `payload/audits/piano_hand_static_to_dynamic_transition_r1/EVIDENCE_DYNAMIC_CONTACT_R1.png`
- `audits/piano_hand_static_to_dynamic_transition_r1/EVIDENCE_STATIC_ANCHOR_VS_DYNAMIC_R1.png` → `hands-research-r1-selected-006.zip` / `payload/audits/piano_hand_static_to_dynamic_transition_r1/EVIDENCE_STATIC_ANCHOR_VS_DYNAMIC_R1.png`
- `audits/piano_hand_static_to_dynamic_transition_r1/L_review_poster.jpg` → `hands-research-r1-selected-006.zip` / `payload/audits/piano_hand_static_to_dynamic_transition_r1/L_review_poster.jpg`
- `audits/piano_hand_static_to_dynamic_transition_r1/STATIC_TO_DYNAMIC_TRANSITION_CANDIDATE_R1.blend` → `hands-research-r1-selected-006.zip` / `payload/audits/piano_hand_static_to_dynamic_transition_r1/STATIC_TO_DYNAMIC_TRANSITION_CANDIDATE_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
